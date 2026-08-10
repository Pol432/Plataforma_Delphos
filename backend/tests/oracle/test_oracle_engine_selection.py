"""
Selección de motor y fallback de /api/v1/oracle/recommend.

Qué se valida aquí:
  * que el contrato JSON no cambia según qué motor responda,
  * que `engine` refleja el motor real (si no, un fallback silencioso sería
    indistinguible de un modelo funcionando),
  * que se cae al heurístico ante fallo de carga, excepción o scores
    degenerados — en vez de romper la petición,
  * que `ORACLE_ENGINE=heuristic` ni siquiera intenta cargar el modelo.

No requiere MindSpore: el modelo se sustituye por dobles. Los tests que sí
ejercitan el checkpoint real viven en oracle/recommendation/tests/.
"""
import uuid

import pytest

from app.services import oracle_engine


@pytest.fixture
def auth_headers(client):
    """Registra un usuario y devuelve su cabecera Bearer (patrón de tests/catalogs)."""
    uid = uuid.uuid4().hex[:6]
    user = {
        "username": f"oracle_{uid}",
        "email": f"oracle_{uid}@test.com",
        "password": "Password123!",
        "full_name": "Oracle Tester",
    }
    registration = client.post("/api/v1/register", json=user)
    assert registration.status_code == 201, registration.text

    login = client.post(
        "/api/v1/token",
        data={"username": user["username"], "password": user["password"]},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture(autouse=True)
def _clean_engine_state(monkeypatch):
    """Cada test arranca sin modelo cacheado y sin ORACLE_ENGINE heredado."""
    monkeypatch.delenv("ORACLE_ENGINE", raising=False)
    oracle_engine.reset_cache()
    yield
    oracle_engine.reset_cache()


class _FakeOutput:
    def __init__(self, prob):
        self.engagement_probability = prob


class _FakeRecommender:
    """Doble del WideDeepRecommender: sólo implementa `rank_candidates`."""

    def __init__(self, probabilities=None, raises=None):
        self.probabilities = probabilities
        self.raises = raises
        self.calls = 0

    def rank_candidates(self, inputs):
        self.calls += 1
        if self.raises is not None:
            raise self.raises
        probs = self.probabilities or [1.0 / (i + 1) for i in range(len(inputs))]
        order = sorted(range(len(inputs)), key=lambda i: probs[i], reverse=True)
        return [(i, _FakeOutput(probs[i])) for i in order]


def _use(monkeypatch, recommender):
    monkeypatch.setattr(oracle_engine, "get_recommender", lambda force=False: recommender)


# ---------------------------------------------------------------------------
# Modos
# ---------------------------------------------------------------------------

class TestModes:
    def test_default_mode_is_auto(self):
        assert oracle_engine.get_mode() == oracle_engine.MODE_AUTO

    @pytest.mark.parametrize("value", ["auto", "heuristic", "widedeep"])
    def test_valid_modes(self, monkeypatch, value):
        monkeypatch.setenv("ORACLE_ENGINE", value)
        assert oracle_engine.get_mode() == value

    def test_mode_is_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("ORACLE_ENGINE", "  HeUrIsTiC ")
        assert oracle_engine.get_mode() == oracle_engine.MODE_HEURISTIC

    def test_unknown_mode_falls_back_to_auto(self, monkeypatch):
        monkeypatch.setenv("ORACLE_ENGINE", "turbo")
        assert oracle_engine.get_mode() == oracle_engine.MODE_AUTO

    def test_heuristic_mode_never_touches_the_model(self, monkeypatch):
        """El kill switch tiene que apagar el modelo, no sólo ignorar su salida."""
        def _explode(force=False):
            raise AssertionError("no debería intentar cargar el modelo")

        monkeypatch.setenv("ORACLE_ENGINE", "heuristic")
        monkeypatch.setattr(oracle_engine, "get_recommender", _explode)
        assert oracle_engine.model_ranking([object(), object()]) is None


# ---------------------------------------------------------------------------
# Detección de degeneración
# ---------------------------------------------------------------------------

class TestIsDegenerate:
    def test_normal_spread_is_fine(self):
        assert oracle_engine.is_degenerate([0.9, 0.5, 0.1]) is None

    def test_all_identical_is_degenerate(self):
        reason = oracle_engine.is_degenerate([0.42] * 64)
        assert reason and "mismo score" in reason

    def test_all_zero_is_degenerate(self):
        reason = oracle_engine.is_degenerate([0.0] * 64)
        assert reason is not None

    def test_all_one_is_degenerate(self):
        reason = oracle_engine.is_degenerate([1.0] * 64)
        assert reason is not None

    def test_partial_saturation_is_not_degenerate(self):
        """
        Que muchos empaten a 0.0 es el comportamiento conocido del checkpoint
        (25 % del split de test), y rank_candidates() lo desempata con los
        diagnósticos. Sólo se rechaza si empata el catálogo entero.
        """
        assert oracle_engine.is_degenerate([0.0] * 63 + [0.8]) is None

    def test_nan_is_degenerate(self):
        assert oracle_engine.is_degenerate([float("nan"), 0.5]) is not None

    def test_infinity_is_degenerate(self):
        assert oracle_engine.is_degenerate([float("inf"), 0.5]) is not None

    def test_empty_is_degenerate(self):
        assert oracle_engine.is_degenerate([]) is not None


# ---------------------------------------------------------------------------
# model_ranking + fallback
# ---------------------------------------------------------------------------

class TestModelRanking:
    def test_returns_permutation_of_indices(self, monkeypatch):
        _use(monkeypatch, _FakeRecommender([0.1, 0.9, 0.5]))
        assert oracle_engine.model_ranking([1, 2, 3]) == [1, 2, 0]

    def test_empty_input_falls_back(self, monkeypatch):
        _use(monkeypatch, _FakeRecommender())
        assert oracle_engine.model_ranking([]) is None

    def test_unloadable_model_falls_back(self, monkeypatch):
        _use(monkeypatch, None)
        assert oracle_engine.model_ranking([1, 2, 3]) is None

    def test_exception_during_inference_falls_back(self, monkeypatch):
        _use(monkeypatch, _FakeRecommender(raises=RuntimeError("boom")))
        assert oracle_engine.model_ranking([1, 2, 3]) is None

    def test_degenerate_scores_fall_back(self, monkeypatch):
        _use(monkeypatch, _FakeRecommender([0.5, 0.5, 0.5]))
        assert oracle_engine.model_ranking([1, 2, 3]) is None

    def test_widedeep_mode_propagates_exception(self, monkeypatch):
        """En modo widedeep los errores no se enmascaran: es para diagnóstico."""
        monkeypatch.setenv("ORACLE_ENGINE", "widedeep")
        _use(monkeypatch, _FakeRecommender(raises=RuntimeError("boom")))
        with pytest.raises(RuntimeError, match="boom"):
            oracle_engine.model_ranking([1, 2, 3])

    def test_widedeep_mode_raises_on_degenerate(self, monkeypatch):
        monkeypatch.setenv("ORACLE_ENGINE", "widedeep")
        _use(monkeypatch, _FakeRecommender([0.5, 0.5, 0.5]))
        with pytest.raises(RuntimeError, match="degenerada"):
            oracle_engine.model_ranking([1, 2, 3])


class TestLoaderCaching:
    def test_failed_load_is_not_retried(self, monkeypatch):
        """Un fallo de carga por petición convertiría un problema de arranque
        en un timeout por request."""
        attempts = []

        def _fail():
            attempts.append(1)
            raise FileNotFoundError("sin checkpoint")

        monkeypatch.setattr(oracle_engine, "resolve_model_dir", _fail)
        assert oracle_engine.get_recommender() is None
        assert oracle_engine.get_recommender() is None
        assert len(attempts) == 1
        assert "sin checkpoint" in oracle_engine.last_load_error()


# ---------------------------------------------------------------------------
# Contrato del endpoint
# ---------------------------------------------------------------------------

ITEM_FIELDS = {
    "simulation_id", "title", "base_career", "categoria",
    "nivel_dificultad", "duracion_horas", "matched_skills", "scores",
}
SCORE_FIELDS = {
    "label", "engagement_probability", "skill_overlap_score",
    "difficulty_match_score", "confidence_interval",
}
RESPONSE_FIELDS = {
    "user_id", "engine", "catalog_size", "resolved_skill_ids",
    "unresolved_skills", "recommendations",
    # Procedencia explícita: `engine` solo decía quién ordenó, y se leía como
    # si los números fueran del modelo. Ver RecommendationResponse.
    "scored_by", "ranked_by",
}

PROFILE = {
    "skills": ["Python", "SQL", "Visual Design"],
    "education_level": "Bachelor's",
    "field_of_study": "Computer Science",
    "analytical_score": 78,
    "creative_score": 72,
    "social_score": 45,
    "linguistic_score": 50,
    "hands_on_score": 65,
    "top_n": 10,
}


def _recommend(client, headers, **overrides):
    payload = {**PROFILE, **overrides}
    response = client.post("/api/v1/oracle/recommend", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


class TestEndpointContract:
    def test_shape_is_identical_under_both_engines(self, client, auth_headers, monkeypatch):
        """
        El punto de todo el diseño: el frontend no debe notar qué motor
        respondió. Mismos campos, mismos tipos, en los dos caminos.
        """
        monkeypatch.setenv("ORACLE_ENGINE", "heuristic")
        heuristic = _recommend(client, auth_headers)

        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        monkeypatch.setattr(
            oracle_engine, "get_recommender",
            lambda force=False: _FakeRecommender([i / 64.0 for i in range(64)]),
        )
        model = _recommend(client, auth_headers)

        assert heuristic["engine"] == oracle_engine.ENGINE_HEURISTIC
        assert model["engine"] == oracle_engine.ENGINE_WIDEDEEP

        # `ranked_by` es el alias explícito de `engine`: mismo valor en los dos
        # caminos, incluido el fallback. Si divergieran, uno de los dos estaría
        # mintiendo sobre qué motor ordenó.
        assert heuristic["ranked_by"] == oracle_engine.ENGINE_HEURISTIC
        assert model["ranked_by"] == oracle_engine.ENGINE_WIDEDEEP

        # Lo que este cambio existe para dejar por escrito: los números son del
        # heurístico SIEMPRE, también cuando el Wide&Deep ordenó.
        assert heuristic["scored_by"] == oracle_engine.ENGINE_HEURISTIC
        assert model["scored_by"] == oracle_engine.ENGINE_HEURISTIC

        for payload in (heuristic, model):
            assert set(payload) == RESPONSE_FIELDS
            assert payload["engine"] == payload["ranked_by"]
            assert payload["catalog_size"] == 64
            assert len(payload["recommendations"]) == PROFILE["top_n"]
            for item in payload["recommendations"]:
                assert set(item) == ITEM_FIELDS
                assert set(item["scores"]) == SCORE_FIELDS
                assert 0.0 <= item["scores"]["engagement_probability"] <= 1.0
                # El campo sigue en el contrato, pero nadie estima
                # incertidumbre: va siempre a null. Se fija aquí porque
                # SCORE_FIELDS solo comprueba que la clave exista, y antes
                # llevaba una banda inventada de (prob-0.1, prob+0.1).
                assert item["scores"]["confidence_interval"] is None

    def test_model_changes_the_order(self, client, auth_headers, monkeypatch):
        """Si el orden no cambiara, el modelo estaría siendo ignorado."""
        monkeypatch.setenv("ORACLE_ENGINE", "heuristic")
        heuristic = _recommend(client, auth_headers)

        # Orden inverso al del catálogo: garantiza un ranking distinto.
        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        monkeypatch.setattr(
            oracle_engine, "get_recommender",
            lambda force=False: _FakeRecommender([i / 64.0 for i in range(64)]),
        )
        model = _recommend(client, auth_headers)

        ids_heuristic = [r["simulation_id"] for r in heuristic["recommendations"]]
        ids_model = [r["simulation_id"] for r in model["recommendations"]]
        assert ids_heuristic != ids_model

    def test_scores_always_come_from_the_heuristic(self, client, auth_headers, monkeypatch):
        """
        La probabilidad cruda del modelo NO se publica. El score de cada
        simulación debe ser el mismo responda quien responda; lo único que
        cambia es el orden.

        Se pide el catálogo entero (top_n=64) a propósito: con un top-10 los dos
        rankings pueden no solaparse y la comparación no probaría nada.
        """
        full = dict(PROFILE, top_n=64)

        monkeypatch.setenv("ORACLE_ENGINE", "heuristic")
        heuristic = client.post("/api/v1/oracle/recommend", json=full, headers=auth_headers).json()

        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        monkeypatch.setattr(
            oracle_engine, "get_recommender",
            lambda force=False: _FakeRecommender([i / 64.0 for i in range(64)]),
        )
        model = client.post("/api/v1/oracle/recommend", json=full, headers=auth_headers).json()

        by_id = {r["simulation_id"]: r["scores"] for r in heuristic["recommendations"]}
        assert len(by_id) == 64
        for item in model["recommendations"]:
            assert item["scores"] == by_id[item["simulation_id"]]

        # ...y el orden sí difiere: el modelo lo invirtió respecto al catálogo.
        assert [r["simulation_id"] for r in model["recommendations"]] != list(by_id)

    def test_broken_model_still_returns_200(self, client, auth_headers, monkeypatch):
        """La demo no se rompe: el fallback responde igual."""
        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        monkeypatch.setattr(
            oracle_engine, "get_recommender",
            lambda force=False: _FakeRecommender(raises=RuntimeError("checkpoint corrupto")),
        )
        payload = _recommend(client, auth_headers)
        assert payload["engine"] == oracle_engine.ENGINE_HEURISTIC
        assert len(payload["recommendations"]) == PROFILE["top_n"]

    def test_degenerate_model_still_returns_200(self, client, auth_headers, monkeypatch):
        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        monkeypatch.setattr(
            oracle_engine, "get_recommender",
            lambda force=False: _FakeRecommender([0.0] * 64),
        )
        payload = _recommend(client, auth_headers)
        assert payload["engine"] == oracle_engine.ENGINE_HEURISTIC
        assert len(payload["recommendations"]) == PROFILE["top_n"]


# ---------------------------------------------------------------------------
# Coherencia del mapeo OOV entre catálogo y modelo
# ---------------------------------------------------------------------------

#: Skills del perfil que dispararon el caso: Research, Visual Design y Adobe
#: Creative Suite. Son los tres a los que `sim_ux_designer` mapea sus cinco
#: skills fuera de vocabulario (Figma, UI Design, UX Research, User Research,
#: Wireframing), así que el solapamiento tiene que ser total.
UX_PROFILE_SKILLS = ["Research", "Visual Design", "Adobe Creative Suite"]
UX_SKILL_IDS = [17, 38, 39]


class TestOovMappingCoherence:
    """
    Regresión del caso real: con el motor `wide_and_deep`, `sim_ux_designer`
    llegaba al top de la respuesta con `matched_skills: []` y
    `skill_overlap_score: 0.0`.

    La causa era que el mapeo OOV sólo existía del lado del modelo: el
    featurizador veía la simulación con sus skills traducidos y la subía al
    primer puesto, mientras el heurístico —que llena los `scores` visibles—
    seguía viendo IDs sintéticos ≥1000 sin resolver.
    """

    def test_catalog_resolves_ux_designer_to_trained_skills(self):
        """Los cinco skills OOV colapsan en los tres entrenados."""
        from app.services.oracle_catalog import get_catalog

        catalog = get_catalog()
        ux = next(s for s in catalog.simulations if s.simulation_id == "sim_ux_designer")
        assert ux.simulation_skill_ids == UX_SKILL_IDS

    def test_no_simulation_keeps_unmapped_synthetic_ids(self):
        """Las 16 equivalencias están decididas: no debe sobrevivir ninguno."""
        from app.services.oracle_catalog import EXTRA_SKILL_ID_OFFSET, get_catalog

        catalog = get_catalog()
        leftovers = {
            sid
            for sim in catalog.simulations
            for sid in sim.simulation_skill_ids
            if sid >= EXTRA_SKILL_ID_OFFSET
        }
        assert leftovers == set()

    def test_user_skills_are_mapped_too(self):
        """
        Simetría con `inference.py`, que mapea los dos bloques. Quien escriba
        "Figma" queda registrado con el ID de Adobe Creative Suite.
        """
        from app.services.oracle_catalog import get_catalog

        catalog = get_catalog()
        assert catalog.resolve_skill_names(["Figma"]) == [39]
        # Y sigue sin ser un "no lo entiendo": nunca estuvo en unresolved.
        assert catalog.unresolved_skill_names(["Figma"]) == []

    def test_ux_designer_has_matched_skills_under_widedeep(
        self, client, auth_headers, monkeypatch
    ):
        """
        El caso reportado, end-to-end: perfil que resuelve a [17, 38, 39],
        motor `wide_and_deep`, y `sim_ux_designer` empujada al primer puesto
        por el modelo. Antes del mapeo llegaba con matched_skills vacío.
        """
        from app.services.oracle_catalog import get_catalog

        catalog = get_catalog()
        ux_index = next(
            i for i, s in enumerate(catalog.simulations)
            if s.simulation_id == "sim_ux_designer"
        )

        # Probabilidades que ponen a sim_ux_designer arriba, pase lo que pase
        # con el resto: reproduce el ranking que dio el modelo real.
        probabilities = [0.1] * len(catalog.simulations)
        probabilities[ux_index] = 0.99

        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        _use(monkeypatch, _FakeRecommender(probabilities))

        payload = _recommend(client, auth_headers, skills=UX_PROFILE_SKILLS, top_n=5)

        assert payload["engine"] == oracle_engine.ENGINE_WIDEDEEP
        assert payload["resolved_skill_ids"] == UX_SKILL_IDS

        top = payload["recommendations"][0]
        assert top["simulation_id"] == "sim_ux_designer"
        assert top["matched_skills"] != []
        assert sorted(top["matched_skills"]) == sorted(
            ["Research", "Visual Design", "Adobe Creative Suite"]
        )
        assert top["scores"]["skill_overlap_score"] > 0.0

    def test_matched_skills_do_not_depend_on_the_engine(
        self, client, auth_headers, monkeypatch
    ):
        """
        El objetivo de fondo: `matched_skills` y `skill_overlap_score` describen
        el catálogo, no el motor. Los dos caminos tienen que coincidir para la
        misma simulación.
        """
        monkeypatch.setenv("ORACLE_ENGINE", "heuristic")
        heuristic = _recommend(client, auth_headers, skills=UX_PROFILE_SKILLS, top_n=64)

        monkeypatch.setenv("ORACLE_ENGINE", "auto")
        _use(monkeypatch, _FakeRecommender())
        model = _recommend(client, auth_headers, skills=UX_PROFILE_SKILLS, top_n=64)

        assert heuristic["engine"] == oracle_engine.ENGINE_HEURISTIC
        assert model["engine"] == oracle_engine.ENGINE_WIDEDEEP

        def by_id(payload):
            return {i["simulation_id"]: i for i in payload["recommendations"]}

        left, right = by_id(heuristic), by_id(model)
        assert left.keys() == right.keys()
        for sim_id, item in left.items():
            assert item["matched_skills"] == right[sim_id]["matched_skills"], sim_id
            assert (
                item["scores"]["skill_overlap_score"]
                == right[sim_id]["scores"]["skill_overlap_score"]
            ), sim_id

    def test_published_vocabulary_still_has_68_names(self, client, auth_headers):
        """
        Mapear no debe reducir lo que el cliente puede ofrecer. Los 16 nombres
        OOV siguen listados, apuntando al ID de su equivalente — que es el que
        `resolve_skill_names` devuelve de verdad.
        """
        response = client.get("/api/v1/oracle/skills", headers=auth_headers)
        assert response.status_code == 200, response.text
        body = response.json()

        assert body["count"] == 68
        assert len(body["skills"]) == 68

        names = {entry["name"] for entry in body["skills"]}
        assert "Figma" in names
        assert "Adobe Creative Suite" in names

        by_name = {entry["name"]: entry["skill_id"] for entry in body["skills"]}
        assert by_name["Figma"] == by_name["Adobe Creative Suite"] == 39
