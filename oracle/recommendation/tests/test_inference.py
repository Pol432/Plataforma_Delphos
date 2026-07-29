"""
Tests del wrapper de inferencia Wide&Deep.

Qué se valida aquí:
  * que la featurización reproduce la del entrenamiento (test de paridad
    contra muestras reales del dataset y sus vectores de skills),
  * la forma y los rangos de lo que entra al modelo,
  * que los skills fuera de vocabulario se descartan Y se reportan,
  * la forma de MatchingOutput.

Qué NO se valida: que el número coincida con la heurística del backend. Son
modelos distintos; esa comparación no significaría nada.

Los tests que necesitan MindSpore se saltan solos: el framework sólo tiene
wheels hasta Python 3.11 y esta máquina corre 3.13.
"""
import numpy as np
import pytest

from inference import (
    DEFAULT_THRESHOLD,
    EDUCATION_ALIASES,
    FALLBACK_EDUCATION_LEVEL,
    FALLBACK_FIELD_OF_STUDY,
    N_CONTINUOUS,
    N_SKILL_SLOTS,
    MatchingInput,
    MatchingOutput,
    SimulationFeatures,
    UserFeatures,
    WideDeepFeaturizer,
    WideDeepRecommender,
    _difficulty_alignment,
    _jaccard_from_vectors,
)

try:  # pragma: no cover - depende del entorno
    import mindspore  # noqa: F401

    HAS_MINDSPORE = True
except ImportError:  # pragma: no cover
    HAS_MINDSPORE = False

needs_mindspore = pytest.mark.skipif(
    not HAS_MINDSPORE, reason="MindSpore no instalado (no hay wheel para Python 3.13)"
)


@pytest.fixture(scope="module")
def featurizer():
    return WideDeepFeaturizer()


@pytest.fixture
def sample_input():
    """Perfil técnico contra una simulación STEM, todo dentro de vocabulario."""
    return MatchingInput(
        user_features=UserFeatures(
            user_skill_ids=[6, 9, 13, 14],
            education_level="Bachelor's",
            field_of_study="Computer Science",
            analytical_score=90,
            creative_score=30,
            social_score=25,
            linguistic_score=40,
            hands_on_score=70,
        ),
        simulation_features=SimulationFeatures(
            simulation_id="sim_data_scientist",
            simulation_categoria="STEM",
            simulation_nivel_dificultad="Upper-Intermediate",
            simulation_duracion_horas=9.9,
            simulation_industria="Technology",
            simulation_skill_ids=[6, 9, 13],
        ),
    )


# ---------------------------------------------------------------------------
# Layout y carga de artefactos
# ---------------------------------------------------------------------------

class TestLayout:
    def test_config_matches_trained_checkpoint(self, featurizer):
        assert featurizer.field_size == 115
        assert featurizer.vocab_size == 148
        assert featurizer.cont_base_id == 38
        assert featurizer.skill_base_id == 44
        assert featurizer.sim_skill_base == 96

    def test_categorical_vocab_matches_encoders(self, featurizer):
        sizes = [len(featurizer.encoders[n].classes_) for n in featurizer.CATEGORICAL_ORDER]
        assert sizes == featurizer.cat_vocab_sizes == [4, 13, 8, 5, 8]

    def test_offsets_are_cumulative(self, featurizer):
        expected = np.cumsum([0] + featurizer.cat_vocab_sizes[:-1]).tolist()
        assert featurizer.cat_offsets == expected

    def test_skill_catalog_has_52_entries(self, featurizer):
        assert featurizer.n_skills == N_SKILL_SLOTS


# ---------------------------------------------------------------------------
# Forma de los tensores
# ---------------------------------------------------------------------------

class TestFeaturizationShape:
    def test_shapes_and_dtypes(self, featurizer, sample_input):
        ids, vals, _ = featurizer.featurize(sample_input)
        assert ids.shape == (115,)
        assert vals.shape == (115,)
        assert ids.dtype == np.int32
        assert vals.dtype == np.float32

    def test_ids_within_vocabulary(self, featurizer, sample_input):
        ids, _, _ = featurizer.featurize(sample_input)
        assert ids.min() >= 0
        assert ids.max() < featurizer.vocab_size

    def test_id_blocks_are_in_the_trained_order(self, featurizer, sample_input):
        ids, _, _ = featurizer.featurize(sample_input)
        # 5 categóricas, cada una dentro de su rango de offset
        for i, offset in enumerate(featurizer.cat_offsets):
            assert offset <= ids[i] < offset + featurizer.cat_vocab_sizes[i]
        # 6 continuas con IDs fijos consecutivos
        np.testing.assert_array_equal(
            ids[5:11], np.arange(featurizer.cont_base_id, featurizer.cont_base_id + N_CONTINUOUS)
        )
        # 52 + 52 slots de skill
        np.testing.assert_array_equal(
            ids[11:63], np.arange(featurizer.skill_base_id, featurizer.skill_base_id + 52)
        )
        np.testing.assert_array_equal(
            ids[63:115], np.arange(featurizer.sim_skill_base, featurizer.sim_skill_base + 52)
        )

    def test_categorical_weights_are_one(self, featurizer, sample_input):
        _, vals, _ = featurizer.featurize(sample_input)
        np.testing.assert_array_equal(vals[:5], np.ones(5, dtype=np.float32))

    def test_continuous_normalisation(self, featurizer, sample_input):
        _, vals, _ = featurizer.featurize(sample_input)
        np.testing.assert_allclose(
            vals[5:11],
            np.array([0.90, 0.30, 0.25, 0.40, 0.70, 9.9 / 20.0], dtype=np.float32),
            rtol=1e-6,
        )

    def test_skill_blocks_are_binary(self, featurizer, sample_input):
        _, vals, _ = featurizer.featurize(sample_input)
        skills = vals[11:]
        assert set(np.unique(skills)).issubset({0.0, 1.0})


# ---------------------------------------------------------------------------
# Mapeo de skills — posición = skill_id - 1
# ---------------------------------------------------------------------------

class TestSkillMapping:
    def test_skill_id_maps_to_position_minus_one(self, featurizer, sample_input):
        _, vals, _ = featurizer.featurize(sample_input)
        user_block = vals[11:63]
        assert list(np.nonzero(user_block)[0]) == [5, 8, 12, 13]  # ids 6, 9, 13, 14

    def test_boundary_ids(self, featurizer, sample_input):
        sample_input.user_features.user_skill_ids = [1, 52]
        _, vals, report = featurizer.featurize(sample_input)
        user_block = vals[11:63]
        assert list(np.nonzero(user_block)[0]) == [0, 51]
        assert report.oov_user_skill_ids == []

    def test_duplicate_ids_do_not_double_count(self, featurizer, sample_input):
        sample_input.user_features.user_skill_ids = [6, 6, 6]
        _, vals, _ = featurizer.featurize(sample_input)
        assert vals[11:63].sum() == 1.0

    def test_empty_skill_list_is_valid(self, featurizer, sample_input):
        sample_input.user_features.user_skill_ids = []
        _, vals, report = featurizer.featurize(sample_input)
        assert vals[11:63].sum() == 0.0
        assert report.n_user_skills_in_vocab == 0


# ---------------------------------------------------------------------------
# Skills fuera de vocabulario (la decisión: descartar Y reportar)
# ---------------------------------------------------------------------------

class TestOutOfVocabularySkills:
    def test_synthetic_ids_are_dropped(self, featurizer, sample_input):
        sample_input.user_features.user_skill_ids = [6, 1004, 1015]
        _, vals, _ = featurizer.featurize(sample_input)
        assert list(np.nonzero(vals[11:63])[0]) == [5]

    def test_synthetic_ids_are_reported(self, featurizer, sample_input):
        sample_input.user_features.user_skill_ids = [6, 1004, 1015]
        _, _, report = featurizer.featurize(sample_input)
        assert report.oov_user_skill_ids == [1004, 1015]
        assert report.n_user_skills_in_vocab == 1
        assert not report.is_clean

    def test_simulation_oov_reported_separately(self, featurizer, sample_input):
        sample_input.simulation_features.simulation_skill_ids = [1000, 1001]
        _, vals, report = featurizer.featurize(sample_input)
        assert vals[63:].sum() == 0.0
        assert report.oov_simulation_skill_ids == [1000, 1001]
        assert report.oov_user_skill_ids == []

    def test_ux_designer_case_produces_valid_tensors(self, featurizer, sample_input):
        """
        sim_ux_designer tiene sus 5 skills fuera de vocabulario. Debe seguir
        produciendo tensores válidos, puntuados sólo por el resto de features.
        """
        sample_input.simulation_features.simulation_skill_ids = [1004, 1009, 1013, 1015, 1014]
        sample_input.simulation_features.simulation_categoria = "Design"
        ids, vals, report = featurizer.featurize(sample_input)
        assert ids.shape == (115,) and vals.shape == (115,)
        assert ids.max() < featurizer.vocab_size
        assert vals[63:].sum() == 0.0
        assert len(report.oov_simulation_skill_ids) == 5

    def test_clean_input_reports_clean(self, featurizer, sample_input):
        _, _, report = featurizer.featurize(sample_input)
        assert report.is_clean


# ---------------------------------------------------------------------------
# Categóricas del usuario fuera de vocabulario
# ---------------------------------------------------------------------------

class TestCategoricalFallbacks:
    def test_doctorate_maps_to_phd(self, featurizer, sample_input):
        sample_input.user_features.education_level = "Doctorate"
        ids, _, report = featurizer.featurize(sample_input)
        phd_code = featurizer._class_index["education_level"]["PhD"]
        assert ids[0] == phd_code + featurizer.cat_offsets[0]
        assert report.substituted_education_level == "PhD"

    @pytest.mark.parametrize("raw", ["Associate's", "Bootcamp"])
    def test_aliased_levels_land_in_vocabulary(self, featurizer, sample_input, raw):
        sample_input.user_features.education_level = raw
        ids, _, report = featurizer.featurize(sample_input)
        assert report.substituted_education_level == EDUCATION_ALIASES[raw]
        assert 0 <= ids[0] < featurizer.cat_vocab_sizes[0]

    def test_unknown_education_falls_back(self, featurizer, sample_input):
        sample_input.user_features.education_level = "Nanodegree Galáctico"
        _, _, report = featurizer.featurize(sample_input)
        assert report.substituted_education_level == FALLBACK_EDUCATION_LEVEL

    def test_unknown_field_of_study_falls_back(self, featurizer, sample_input):
        sample_input.user_features.field_of_study = "Astrobiología Aplicada"
        ids, _, report = featurizer.featurize(sample_input)
        assert report.substituted_field_of_study == FALLBACK_FIELD_OF_STUDY
        offset = featurizer.cat_offsets[1]
        assert offset <= ids[1] < offset + featurizer.cat_vocab_sizes[1]

    def test_enum_like_values_are_accepted(self, featurizer, sample_input):
        """Los schemas del backend pasan Enums str, no strings pelados."""

        class FakeEnum:
            value = "STEM"

        sample_input.simulation_features.simulation_categoria = FakeEnum()
        ids, _, report = featurizer.featurize(sample_input)
        assert report.is_clean
        offset = featurizer.cat_offsets[2]
        assert offset <= ids[2] < offset + featurizer.cat_vocab_sizes[2]

    def test_unknown_simulation_category_raises(self, featurizer, sample_input):
        """
        Las categóricas de simulación vienen del catálogo y están siempre en
        vocabulario. Si llega una desconocida es un bug, no un caso a absorber.
        """
        sample_input.simulation_features.simulation_categoria = "Astrología"
        with pytest.raises(ValueError, match="fuera del vocabulario"):
            featurizer.featurize(sample_input)


# ---------------------------------------------------------------------------
# Paridad con el entrenamiento
# ---------------------------------------------------------------------------

class TestTrainingParity:
    """
    El test que de verdad importa: featurizar muestras reales del dataset de
    entrenamiento y comparar contra los tensores que el entrenamiento habría
    producido, reconstruidos desde las columnas codificadas y los vectores .npy.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def training_sample():
        pd = pytest.importorskip("pandas")
        root = WideDeepFeaturizer().root
        processed = root / "data" / "processed"
        df = pd.read_csv(processed / "unified_training_dataset_v3.csv")
        user_vecs = np.load(processed / "user_skill_vectors.npy")
        sim_vecs = np.load(processed / "simulation_skill_vectors.npy")
        return df, user_vecs, sim_vecs

    @pytest.mark.parametrize("row_index", [0, 1, 500, 9000, 18500])
    def test_featurization_matches_training(self, featurizer, training_sample, row_index):
        df, user_vecs, sim_vecs = training_sample
        row = df.iloc[row_index]

        # Los skill_ids se reconstruyen desde el vector de entrenamiento
        # (posición + 1), que es la fuente de verdad de lo que vio el modelo.
        user_ids = [int(p) + 1 for p in np.nonzero(user_vecs[row_index])[0]]
        sim_ids = [int(p) + 1 for p in np.nonzero(sim_vecs[row_index])[0]]

        item = MatchingInput(
            user_features=UserFeatures(
                user_skill_ids=user_ids,
                education_level=row.education_level,
                field_of_study=row.field_of_study,
                analytical_score=int(row.analytical_score),
                creative_score=int(row.creative_score),
                social_score=int(row.social_score),
                linguistic_score=int(row.linguistic_score),
                hands_on_score=int(row.hands_on_score),
            ),
            simulation_features=SimulationFeatures(
                simulation_id=row.simulation_id,
                simulation_categoria=row.simulation_categoria,
                simulation_nivel_dificultad=row.simulation_nivel_dificultad,
                simulation_duracion_horas=float(row.simulation_duracion_horas),
                simulation_industria=row.simulation_industria,
                simulation_skill_ids=sim_ids,
            ),
        )
        ids, vals, report = featurizer.featurize(item)

        # Las columnas *_encoded del dataset son exactamente lo que el
        # entrenamiento metió en el modelo.
        expected_cat = np.array(
            [
                int(row.education_level_encoded) + featurizer.cat_offsets[0],
                int(row.field_of_study_encoded) + featurizer.cat_offsets[1],
                int(row.simulation_categoria_encoded) + featurizer.cat_offsets[2],
                int(row.simulation_nivel_dificultad_encoded) + featurizer.cat_offsets[3],
                int(row.simulation_industria_encoded) + featurizer.cat_offsets[4],
            ],
            dtype=np.int32,
        )
        np.testing.assert_array_equal(ids[:5], expected_cat)

        expected_cont = np.array(
            [
                row.analytical_score / 100.0,
                row.creative_score / 100.0,
                row.social_score / 100.0,
                row.linguistic_score / 100.0,
                row.hands_on_score / 100.0,
                row.simulation_duracion_horas / 20.0,
            ],
            dtype=np.float32,
        )
        np.testing.assert_allclose(vals[5:11], expected_cont, rtol=1e-6)

        np.testing.assert_array_equal(vals[11:63], user_vecs[row_index].astype(np.float32))
        np.testing.assert_array_equal(vals[63:115], sim_vecs[row_index].astype(np.float32))
        assert report.is_clean, "una fila real del entrenamiento no debería requerir sustituciones"


# ---------------------------------------------------------------------------
# Lotes
# ---------------------------------------------------------------------------

class TestBatchFeaturization:
    def test_batch_shapes(self, featurizer, sample_input):
        ids, vals, reports = featurizer.featurize_batch([sample_input] * 7)
        assert ids.shape == (7, 115)
        assert vals.shape == (7, 115)
        assert len(reports) == 7

    def test_empty_batch(self, featurizer):
        ids, vals, reports = featurizer.featurize_batch([])
        assert ids.shape == (0, 115)
        assert reports == []

    def test_batch_matches_individual(self, featurizer, sample_input):
        single_ids, single_vals, _ = featurizer.featurize(sample_input)
        batch_ids, batch_vals, _ = featurizer.featurize_batch([sample_input])
        np.testing.assert_array_equal(batch_ids[0], single_ids)
        np.testing.assert_array_equal(batch_vals[0], single_vals)


# ---------------------------------------------------------------------------
# Diagnósticos descriptivos
# ---------------------------------------------------------------------------

class TestDiagnostics:
    def test_jaccard_identical_vectors(self):
        v = np.array([1, 0, 1, 1], dtype=np.float32)
        assert _jaccard_from_vectors(v, v) == 1.0

    def test_jaccard_disjoint(self):
        a = np.array([1, 0, 0], dtype=np.float32)
        b = np.array([0, 1, 1], dtype=np.float32)
        assert _jaccard_from_vectors(a, b) == 0.0

    def test_jaccard_empty_is_zero_not_nan(self):
        z = np.zeros(4, dtype=np.float32)
        assert _jaccard_from_vectors(z, z) == 0.0

    def test_jaccard_partial(self):
        a = np.array([1, 1, 0, 0], dtype=np.float32)
        b = np.array([1, 0, 1, 0], dtype=np.float32)
        assert _jaccard_from_vectors(a, b) == pytest.approx(1 / 3)

    def test_difficulty_alignment_bounds(self):
        assert 0.0 <= _difficulty_alignment(0, "Expert") <= 1.0
        assert 0.0 <= _difficulty_alignment(100, "Beginner") <= 1.0

    def test_difficulty_alignment_rewards_match(self):
        aligned = _difficulty_alignment(100, "Expert")
        misaligned = _difficulty_alignment(0, "Expert")
        assert aligned > misaligned

    def test_unknown_difficulty_is_zero(self):
        assert _difficulty_alignment(50, "Imposible") == 0.0


# ---------------------------------------------------------------------------
# Contrato de salida
# ---------------------------------------------------------------------------

class TestOutputContract:
    def test_matching_output_field_names_match_backend(self):
        """
        Los nombres deben coincidir con app.schemas.ml.MatchingOutput o el
        backend no podrá construir su respuesta desde este objeto.
        """
        expected = {
            "label",
            "engagement_probability",
            "skill_overlap_score",
            "difficulty_match_score",
            "confidence_interval",
        }
        assert set(MatchingOutput.__dataclass_fields__) == expected

    def test_threshold_is_the_checkpoint_one(self):
        assert DEFAULT_THRESHOLD == 0.65

    def test_recommender_exposes_predict_signature(self):
        for name in ("predict", "predict_many", "predict_verbose"):
            assert callable(getattr(WideDeepRecommender, name))


# ---------------------------------------------------------------------------
# Extremo a extremo (requiere MindSpore)
# ---------------------------------------------------------------------------

@needs_mindspore
class TestModelInference:
    @pytest.fixture(scope="class")
    def recommender(self):
        return WideDeepRecommender.load(batch_size=8)

    def test_predict_returns_matching_output(self, recommender, sample_input):
        out = recommender.predict(sample_input)
        assert isinstance(out, MatchingOutput)
        assert out.label in (0, 1)
        assert 0.0 <= out.engagement_probability <= 1.0
        assert 0.0 <= out.skill_overlap_score <= 1.0
        assert 0.0 <= out.difficulty_match_score <= 1.0
        assert out.confidence_interval is None

    def test_label_follows_threshold(self, recommender, sample_input):
        out = recommender.predict(sample_input)
        assert out.label == (1 if out.engagement_probability >= recommender.threshold else 0)

    def test_batch_padding_does_not_change_results(self, recommender, sample_input):
        """Un lote que no llena el batch congelado debe dar lo mismo que uno solo."""
        single = recommender.predict(sample_input)
        batch = recommender.predict_many([sample_input] * 3)
        assert len(batch) == 3
        for item in batch:
            assert item.engagement_probability == pytest.approx(
                single.engagement_probability, abs=1e-5
            )

    def test_verbose_reports_oov(self, recommender, sample_input):
        sample_input.user_features.user_skill_ids = [6, 1004]
        _, report = recommender.predict_verbose(sample_input)
        assert report.oov_user_skill_ids == [1004]

    def test_empty_batch_returns_empty(self, recommender):
        assert recommender.predict_many([]) == []

    def test_probability_is_not_rounded(self, recommender, sample_input):
        """
        Redondear a 4 decimales colapsaba el 65% del split de test a 0.0 exacto.
        La probabilidad debe conservar la precisión de float32.
        """
        out = recommender.predict(sample_input)
        p = out.engagement_probability
        assert p == pytest.approx(float(np.float32(p)), abs=0)

    def test_logits_available_for_ranking(self, recommender, sample_input):
        outs, logits = recommender.predict_many_with_logits([sample_input])
        assert len(outs) == len(logits) == 1
        assert isinstance(logits[0], float)

    def test_saturated_candidates_are_still_ordered(self, recommender):
        """
        El caso que motivó el cambio: candidatos cuya probabilidad satura a 0.0
        deben seguir quedando ordenados de forma determinista.

        El desempate lo hacen los diagnósticos, no el logit — medido, el logit
        ordena peor que al azar en esa región (AUC 0.2129 sobre el test).
        """
        base = dict(
            education_level="High School",
            field_of_study="Arts",
            analytical_score=5,
            creative_score=5,
            social_score=5,
            linguistic_score=5,
            hands_on_score=5,
        )
        candidates = [
            MatchingInput(
                user_features=UserFeatures(user_skill_ids=[], **base),
                simulation_features=SimulationFeatures(
                    simulation_id=f"sim_{i}",
                    simulation_categoria="STEM",
                    simulation_nivel_dificultad=level,
                    simulation_duracion_horas=duration,
                    simulation_industria="Technology",
                    simulation_skill_ids=[i + 1],
                ),
            )
            for i, (level, duration) in enumerate(
                [("Expert", 20.0), ("Beginner", 3.0), ("Advanced", 12.0)]
            )
        ]
        ranked = recommender.rank_candidates(candidates)
        assert len(ranked) == len(candidates)
        # Orden total y determinista, sin importar cuánto sature la probabilidad
        assert sorted(i for i, _ in ranked) == list(range(len(candidates)))
        keys = [
            (o.engagement_probability, o.skill_overlap_score, o.difficulty_match_score)
            for _, o in ranked
        ]
        assert keys == sorted(keys, reverse=True)
        # Y es estable: dos llamadas dan el mismo orden
        assert [i for i, _ in ranked] == [
            i for i, _ in recommender.rank_candidates(candidates)
        ]

    def test_logit_and_probability_are_consistent(self, recommender, sample_input):
        """probabilidad = sigmoid(logit), salvo underflow."""
        outs, logits = recommender.predict_many_with_logits([sample_input])
        expected = 1.0 / (1.0 + np.exp(-np.float64(logits[0])))
        assert outs[0].engagement_probability == pytest.approx(expected, abs=1e-5)
