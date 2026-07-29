"""
Wide & Deep inference wrapper.

Expone la misma firma que `RecommendationService.predict()` del backend
(recibe un MatchingInput, devuelve un MatchingOutput) pero resuelve la
recomendación con el modelo Wide&Deep entrenado en vez de la heurística.

    from inference import WideDeepRecommender
    rec = WideDeepRecommender.load()
    out = rec.predict(matching_input)     # -> MatchingOutput

El contrato es estructural, no nominal: `predict()` acepta cualquier objeto con
`.user_features` y `.simulation_features`, así que sirve tanto el modelo
Pydantic del backend (`app.schemas.ml.MatchingInput`) como las dataclasses de
este módulo. Nada de aquí importa desde `backend/`.

--------------------------------------------------------------------------
Featurización
--------------------------------------------------------------------------
Reproduce exactamente `build_widedeep_features` del notebook de entrenamiento
(Week 3 / 02_model_build_and_train.ipynb, celda 8). Cada muestra son 115 pares
(ID, peso) sobre una tabla de embeddings única de 148 filas:

    bloque              IDs        peso
    5 categóricas       encoded + offset       1.0
    6 continuas         38..43                 scores/100, duración/20
    52 skills usuario   44..95                 multi-hot 0/1
    52 skills simulación 96..147               multi-hot 0/1

Los offsets, bases y tamaños NO están hardcodeados: se leen de
`checkpoints/training_config.json`, que fue escrito por el propio
entrenamiento. Si el checkpoint cambia, este módulo lo sigue.

--------------------------------------------------------------------------
Skills fuera del vocabulario entrenado
--------------------------------------------------------------------------
El modelo vio 52 skills (`data/processed/skills_catalog.csv`, skill_id 1..52,
posición en el vector = skill_id - 1). El catálogo de simulaciones referencia
16 skills adicionales (Figma, Scrum, UX Research...) a los que el backend
asigna IDs sintéticos ≥ 1000; el modelo nunca los vio y no tienen fila en la
tabla de embeddings.

Decisión: **se descartan y se reportan**. Descartar mantiene la featurización
de inferencia idéntica a la de entrenamiento, que es la propiedad que hace
fiable a un wrapper de inferencia. Reportarlos (`FeaturizationReport.oov_*`)
evita que sea un descarte silencioso.

Consecuencia conocida: 6 de las 64 simulaciones tienen algún skill fuera de
vocabulario y `sim_ux_designer` los tiene todos fuera (0/5), así que se puntúa
sólo por sus features categóricas y continuas. La heurística del backend SÍ usa
los IDs sintéticos, de modo que ambos motores discrepan justamente en
diseño/UX. Es esperado, no un defecto.

--------------------------------------------------------------------------
Limitaciones registradas
--------------------------------------------------------------------------
* Los vectores de skills del entrenamiento son más ralos que el catálogo actual
  (media 2.77 vs 3.50 skills activos por simulación): el catálogo se enriqueció
  después de entrenar. Featurizar desde el catálogo introduce un corrimiento de
  distribución pequeño pero real.
* `skill_overlap_score` y `difficulty_match_score` del MatchingOutput son
  diagnósticos descriptivos calculados aquí, NO salidas del modelo. El modelo
  produce un único logit. No son comparables con los de la heurística.
* `confidence_interval` se deja en None: el modelo no estima incertidumbre y
  fabricar un intervalo sería inventar.
"""
from __future__ import annotations

import json
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple

import numpy as np

# --------------------------------------------------------------------------
# Constantes derivadas de los artefactos de entrenamiento
# --------------------------------------------------------------------------

#: Umbral de decisión del checkpoint de referencia (checkpoints/evaluation_results.json).
#: Distinto del 0.6 que usa la heurística del backend — son modelos distintos.
DEFAULT_THRESHOLD = 0.65

#: Nº de features continuas (5 psicométricas + duración), fijado por el entrenamiento.
N_CONTINUOUS = 6

#: Nº de slots de skill por lado. El modelo tiene 52 de usuario y 52 de simulación.
N_SKILL_SLOTS = 52

#: Normalizador de la duración, tal como en el notebook: `dur / 20.0`.
DURATION_SCALE = 20.0

#: Valores de `education_level` que el backend acepta pero el modelo no vio.
#: Doctorate/PhD es la misma cosa con distinto nombre; los otros dos se
#: aproximan al nivel formal más cercano dentro del vocabulario entrenado.
EDUCATION_ALIASES = {
    "Doctorate": "PhD",
    "Associate's": "High School",
    "Bootcamp": "Bachelor's",
}

#: Fallback cuando un valor categórico del usuario no existe ni por alias.
#: Son las modas del dataset de entrenamiento (unified_training_dataset_v3.csv).
FALLBACK_EDUCATION_LEVEL = "Bachelor's"
FALLBACK_FIELD_OF_STUDY = "Finance"


# --------------------------------------------------------------------------
# Estructuras de datos (espejo estructural de app.schemas.ml)
# --------------------------------------------------------------------------

@dataclass
class UserFeatures:
    """Equivalente local de `UserFeaturesInput`. Sin validación Pydantic."""
    user_skill_ids: List[int]
    education_level: str
    field_of_study: str
    analytical_score: int
    creative_score: int
    social_score: int
    linguistic_score: int
    hands_on_score: int


@dataclass
class SimulationFeatures:
    """Equivalente local de `SimulationFeaturesInput`."""
    simulation_id: str
    simulation_categoria: str
    simulation_nivel_dificultad: str
    simulation_duracion_horas: float
    simulation_industria: str
    simulation_skill_ids: List[int]


@dataclass
class MatchingInput:
    user_features: UserFeatures
    simulation_features: SimulationFeatures


@dataclass
class MatchingOutput:
    """
    Mismos campos que `app.schemas.ml.MatchingOutput`, para que el backend pueda
    consumir este wrapper sin cambiar el contrato del endpoint.
    """
    label: int
    engagement_probability: float
    skill_overlap_score: float
    difficulty_match_score: float
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class FeaturizationReport:
    """Qué tuvo que ajustar el featurizador para que la muestra entrara al modelo."""
    oov_user_skill_ids: List[int] = field(default_factory=list)
    oov_simulation_skill_ids: List[int] = field(default_factory=list)
    substituted_education_level: Optional[str] = None
    substituted_field_of_study: Optional[str] = None
    n_user_skills_in_vocab: int = 0
    n_simulation_skills_in_vocab: int = 0

    @property
    def is_clean(self) -> bool:
        """True si nada se descartó ni se sustituyó."""
        return not (
            self.oov_user_skill_ids
            or self.oov_simulation_skill_ids
            or self.substituted_education_level
            or self.substituted_field_of_study
        )


def _enum_value(v: Any) -> str:
    """Acepta str o Enum (los schemas del backend usan Enums str)."""
    return str(getattr(v, "value", v))


# --------------------------------------------------------------------------
# Featurización
# --------------------------------------------------------------------------

class WideDeepFeaturizer:
    """
    Convierte (usuario, simulación) en los tensores `feat_ids` / `feat_vals`
    que espera `WideDeepModel.construct(id_hldr, wt_hldr)`.

    No depende de MindSpore: es numpy puro y se puede testear sin el framework.
    """

    #: Orden de los campos categóricos. Fija los offsets — no reordenar.
    CATEGORICAL_ORDER = (
        "education_level",
        "field_of_study",
        "simulation_categoria",
        "simulation_nivel_dificultad",
        "simulation_industria",
    )

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root) if root else Path(__file__).resolve().parent
        self.config = self._load_training_config()
        self.encoders = self._load_encoders()
        self.n_skills = self._load_skill_count()

        self.cat_offsets: List[int] = list(self.config["cat_offsets"])
        self.cat_vocab_sizes: List[int] = list(self.config["cat_vocab_sizes"])
        self.cont_base_id: int = int(self.config["cont_base_id"])
        self.skill_base_id: int = int(self.config["skill_base_id"])
        self.sim_skill_base: int = int(self.config["sim_skill_base"])
        self.field_size: int = int(self.config["field_size"])
        self.vocab_size: int = int(self.config["vocab_size"])

        self._validate_layout()

        # IDs fijos, precalculados una vez (igual que el notebook)
        self._cont_ids = np.arange(
            self.cont_base_id, self.cont_base_id + N_CONTINUOUS, dtype=np.int32
        )
        self._user_skill_ids = np.arange(
            self.skill_base_id, self.skill_base_id + N_SKILL_SLOTS, dtype=np.int32
        )
        self._sim_skill_ids = np.arange(
            self.sim_skill_base, self.sim_skill_base + N_SKILL_SLOTS, dtype=np.int32
        )
        # Índice nombre -> código, por campo categórico
        self._class_index = {
            name: {str(c): i for i, c in enumerate(enc.classes_)}
            for name, enc in self.encoders.items()
        }

    # --- carga de artefactos ---

    def _load_training_config(self) -> dict:
        path = self.root / "checkpoints" / "training_config.json"
        if not path.is_file():
            raise FileNotFoundError(f"Falta training_config.json en {path}")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def _load_encoders(self) -> dict:
        path = self.root / "data" / "processed" / "label_encoders.pkl"
        if not path.is_file():
            raise FileNotFoundError(f"Faltan los label encoders en {path}")
        with open(path, "rb") as fh:
            return pickle.load(fh)

    def _load_skill_count(self) -> int:
        """Cuenta los skills del vocabulario entrenado sin necesitar pandas."""
        path = self.root / "data" / "processed" / "skills_catalog.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Falta skills_catalog.csv en {path}")
        with open(path, encoding="utf-8") as fh:
            return sum(1 for _ in fh) - 1  # menos la cabecera

    def _validate_layout(self) -> None:
        """
        El layout del config debe cuadrar con los artefactos. Si algo no encaja,
        fallar aquí es mucho mejor que producir predicciones silenciosamente
        desalineadas con el entrenamiento.
        """
        if self.n_skills != N_SKILL_SLOTS:
            raise ValueError(
                f"skills_catalog.csv tiene {self.n_skills} skills, el modelo espera {N_SKILL_SLOTS}"
            )

        expected_field_size = (
            len(self.CATEGORICAL_ORDER) + N_CONTINUOUS + 2 * N_SKILL_SLOTS
        )
        if self.field_size != expected_field_size:
            raise ValueError(
                f"field_size={self.field_size} en training_config.json, "
                f"pero el layout da {expected_field_size}"
            )

        if self.sim_skill_base + N_SKILL_SLOTS != self.vocab_size:
            raise ValueError(
                f"vocab_size={self.vocab_size} no cierra con "
                f"sim_skill_base={self.sim_skill_base} + {N_SKILL_SLOTS}"
            )

        if self.skill_base_id != self.cont_base_id + N_CONTINUOUS:
            raise ValueError(
                f"skill_base_id={self.skill_base_id} debería ser "
                f"cont_base_id({self.cont_base_id}) + {N_CONTINUOUS}"
            )

        for name in self.CATEGORICAL_ORDER:
            if name not in self.encoders:
                raise ValueError(f"Falta el encoder '{name}' en label_encoders.pkl")

        actual_sizes = [len(self.encoders[n].classes_) for n in self.CATEGORICAL_ORDER]
        if actual_sizes != self.cat_vocab_sizes:
            raise ValueError(
                f"cat_vocab_sizes={self.cat_vocab_sizes} no coincide con los "
                f"encoders={actual_sizes}"
            )

    # --- codificación de campos ---

    def _encode_categorical(
        self, field_name: str, raw_value: Any, report: FeaturizationReport
    ) -> int:
        """
        Codifica un valor categórico a su índice de entrenamiento.

        Los campos de simulación vienen del catálogo y siempre están en
        vocabulario (verificado). Los del usuario pueden no estarlo: se intenta
        alias y, si no, se cae al valor más frecuente del entrenamiento.
        """
        index = self._class_index[field_name]
        value = _enum_value(raw_value)

        if value in index:
            return index[value]

        if field_name == "education_level":
            alias = EDUCATION_ALIASES.get(value)
            substitute = alias if alias in index else FALLBACK_EDUCATION_LEVEL
            report.substituted_education_level = substitute
            return index[substitute]

        if field_name == "field_of_study":
            report.substituted_field_of_study = FALLBACK_FIELD_OF_STUDY
            return index[FALLBACK_FIELD_OF_STUDY]

        raise ValueError(
            f"Valor '{value}' fuera del vocabulario de '{field_name}' "
            f"(conocidos: {sorted(index)})"
        )

    def _skill_multihot(
        self, skill_ids: Iterable[int], oov_sink: List[int]
    ) -> np.ndarray:
        """
        Multi-hot de 52 posiciones. `position = skill_id - 1` (verificado contra
        los vectores de entrenamiento). Todo ID fuera de 1..52 — incluidos los
        sintéticos ≥1000 del backend — se descarta y se anota en `oov_sink`.
        """
        vec = np.zeros(N_SKILL_SLOTS, dtype=np.float32)
        for raw in skill_ids or ():
            skill_id = int(raw)
            position = skill_id - 1
            if 0 <= position < N_SKILL_SLOTS:
                vec[position] = 1.0
            else:
                oov_sink.append(skill_id)
        return vec

    # --- API pública ---

    def featurize(
        self, matching_input: Any
    ) -> Tuple[np.ndarray, np.ndarray, FeaturizationReport]:
        """
        Devuelve `(feat_ids[115] int32, feat_vals[115] float32, report)`.

        Réplica exacta de `build_widedeep_features` del notebook.
        """
        user = matching_input.user_features
        sim = matching_input.simulation_features
        report = FeaturizationReport()

        raw_categoricals = (
            user.education_level,
            user.field_of_study,
            sim.simulation_categoria,
            sim.simulation_nivel_dificultad,
            sim.simulation_industria,
        )
        cat_ids = np.array(
            [
                self._encode_categorical(name, value, report) + self.cat_offsets[i]
                for i, (name, value) in enumerate(
                    zip(self.CATEGORICAL_ORDER, raw_categoricals)
                )
            ],
            dtype=np.int32,
        )

        user_vec = self._skill_multihot(user.user_skill_ids, report.oov_user_skill_ids)
        sim_vec = self._skill_multihot(
            sim.simulation_skill_ids, report.oov_simulation_skill_ids
        )
        report.n_user_skills_in_vocab = int(user_vec.sum())
        report.n_simulation_skills_in_vocab = int(sim_vec.sum())

        cont_vals = np.array(
            [
                float(user.analytical_score) / 100.0,
                float(user.creative_score) / 100.0,
                float(user.social_score) / 100.0,
                float(user.linguistic_score) / 100.0,
                float(user.hands_on_score) / 100.0,
                float(sim.simulation_duracion_horas) / DURATION_SCALE,
            ],
            dtype=np.float32,
        )

        feat_ids = np.concatenate(
            [cat_ids, self._cont_ids, self._user_skill_ids, self._sim_skill_ids]
        ).astype(np.int32)
        feat_vals = np.concatenate(
            [np.ones(len(cat_ids), dtype=np.float32), cont_vals, user_vec, sim_vec]
        ).astype(np.float32)

        return feat_ids, feat_vals, report

    def featurize_batch(
        self, inputs: Sequence[Any]
    ) -> Tuple[np.ndarray, np.ndarray, List[FeaturizationReport]]:
        """Featuriza N muestras -> `(ids[N,115], vals[N,115], reports)`."""
        if not inputs:
            empty_ids = np.zeros((0, self.field_size), dtype=np.int32)
            return empty_ids, empty_ids.astype(np.float32), []

        triples = [self.featurize(item) for item in inputs]
        ids = np.stack([t[0] for t in triples])
        vals = np.stack([t[1] for t in triples])
        return ids, vals, [t[2] for t in triples]


# --------------------------------------------------------------------------
# Diagnósticos descriptivos (no salen del modelo)
# --------------------------------------------------------------------------

#: Orden ordinal de la dificultad, tal como la vio el entrenamiento.
_DIFFICULTY_ORDER = (
    "Beginner",
    "Lower-Intermediate",
    "Upper-Intermediate",
    "Advanced",
    "Expert",
)


def _jaccard_from_vectors(user_vec: np.ndarray, sim_vec: np.ndarray) -> float:
    """Solapamiento sobre los mismos multi-hot que se le dieron al modelo."""
    union = float(np.logical_or(user_vec, sim_vec).sum())
    if union == 0.0:
        return 0.0
    return float(np.logical_and(user_vec, sim_vec).sum()) / union


def _difficulty_alignment(analytical_score: int, difficulty: str) -> float:
    """
    Distancia ordinal normalizada entre la competencia declarada del usuario
    (proxy: analytical_score) y el nivel de la simulación. Diagnóstico, no
    predicción: existe sólo para llenar `difficulty_match_score` con algo
    interpretable en vez de un cero.
    """
    level = _enum_value(difficulty)
    if level not in _DIFFICULTY_ORDER:
        return 0.0
    n = len(_DIFFICULTY_ORDER)
    sim_rank = _DIFFICULTY_ORDER.index(level) / (n - 1)
    user_rank = min(max(analytical_score, 0), 100) / 100.0
    return round(1.0 - abs(sim_rank - user_rank), 4)


# --------------------------------------------------------------------------
# Wrapper de inferencia
# --------------------------------------------------------------------------

class WideDeepRecommender:
    """
    Wrapper del checkpoint Wide&Deep con la firma de `RecommendationService`.

    MindSpore se importa de forma diferida: instanciar el featurizador y correr
    sus tests no requiere el framework, que sólo tiene wheels hasta Python 3.11.
    """

    #: Checkpoint de referencia. El `_final.ckpt` es histórico — ver
    #: README_CHECKPOINT_STATUS.md — y no debe usarse para la demo.
    DEFAULT_CHECKPOINT = Path("checkpoints") / "baseline" / "dao_wide_deep_best.ckpt"

    def __init__(
        self,
        featurizer: WideDeepFeaturizer,
        network: Any,
        predictor: Any,
        batch_size: int,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.featurizer = featurizer
        self.network = network
        self.predictor = predictor
        self.batch_size = batch_size
        self.threshold = threshold

    # --- construcción ---

    @classmethod
    def load(
        cls,
        root: Optional[Path] = None,
        checkpoint: Optional[Path] = None,
        batch_size: int = 64,
        threshold: float = DEFAULT_THRESHOLD,
        device_target: str = "CPU",
    ) -> "WideDeepRecommender":
        """
        Carga checkpoint y construye la red.

        `batch_size` queda congelado en el grafo: `WideDeepModel.construct` usa
        `self.batch_size` como entero literal en un Reshape, así que toda
        inferencia se rellena hasta ese tamaño exacto. Por defecto 64, que es el
        tamaño del catálogo de simulaciones.
        """
        featurizer = WideDeepFeaturizer(root=root)
        network, predictor = cls._build_network(
            featurizer, featurizer.root, checkpoint, batch_size, device_target
        )
        return cls(featurizer, network, predictor, batch_size, threshold)

    @staticmethod
    def _build_network(
        featurizer: WideDeepFeaturizer,
        root: Path,
        checkpoint: Optional[Path],
        batch_size: int,
        device_target: str,
    ):
        """Import diferido de MindSpore — sólo se ejecuta si se va a predecir."""
        import sys

        src_dir = root / "src"
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

        import mindspore as ms  # noqa: E402
        from mindspore import context  # noqa: E402
        from wide_and_deep import PredictWithSigmoid, WideDeepModel  # noqa: E402

        context.set_context(mode=context.GRAPH_MODE, device_target=device_target)

        cfg = featurizer.config
        model_config = _ModelConfig(
            batch_size=batch_size,
            field_size=featurizer.field_size,
            vocab_size=featurizer.vocab_size,
            emb_dim=int(cfg["emb_dim"]),
            deep_layer_dim=list(cfg["deep_layer_dim"]),
            deep_layer_act=cfg["deep_layer_act"],
        )

        network = WideDeepModel(model_config)

        ckpt_path = Path(checkpoint) if checkpoint else root / WideDeepRecommender.DEFAULT_CHECKPOINT
        if not ckpt_path.is_file():
            raise FileNotFoundError(f"No existe el checkpoint {ckpt_path}")

        params = ms.load_checkpoint(str(ckpt_path))
        not_loaded = ms.load_param_into_net(network, params)
        # MindSpore devuelve la lista de parámetros que no encontró destino.
        if not_loaded:
            raise RuntimeError(
                f"El checkpoint {ckpt_path.name} no encaja con la arquitectura; "
                f"parámetros sin cargar: {not_loaded}"
            )

        network.set_train(False)
        predictor = PredictWithSigmoid(network)
        predictor.set_train(False)
        return network, predictor

    # --- predicción ---

    def predict(self, matching_input: Any) -> MatchingOutput:
        """Misma firma que `RecommendationService.predict()`."""
        return self.predict_many([matching_input])[0]

    def predict_verbose(
        self, matching_input: Any
    ) -> Tuple[MatchingOutput, FeaturizationReport]:
        """Como `predict()` pero devuelve además qué se descartó o sustituyó."""
        outputs, reports = self._run([matching_input])
        return outputs[0], reports[0]

    def predict_many(self, inputs: Sequence[Any]) -> List[MatchingOutput]:
        """Puntúa N muestras. Rellena internamente hasta múltiplos de batch_size."""
        return self._run(inputs)[0]

    def predict_many_verbose(
        self, inputs: Sequence[Any]
    ) -> Tuple[List[MatchingOutput], List[FeaturizationReport]]:
        return self._run(inputs)

    def _run(
        self, inputs: Sequence[Any]
    ) -> Tuple[List[MatchingOutput], List[FeaturizationReport]]:
        if not inputs:
            return [], []

        ids, vals, reports = self.featurizer.featurize_batch(inputs)
        probs = self._forward(ids, vals)

        outputs = []
        for i, item in enumerate(inputs):
            prob = float(probs[i])
            user_vec = vals[i][self.featurizer.field_size - 2 * N_SKILL_SLOTS :][
                :N_SKILL_SLOTS
            ]
            sim_vec = vals[i][self.featurizer.field_size - N_SKILL_SLOTS :]
            outputs.append(
                MatchingOutput(
                    label=1 if prob >= self.threshold else 0,
                    engagement_probability=round(prob, 4),
                    skill_overlap_score=round(_jaccard_from_vectors(user_vec, sim_vec), 4),
                    difficulty_match_score=_difficulty_alignment(
                        item.user_features.analytical_score,
                        item.simulation_features.simulation_nivel_dificultad,
                    ),
                    confidence_interval=None,
                )
            )
        return outputs, reports

    def _forward(self, ids: np.ndarray, vals: np.ndarray) -> np.ndarray:
        """Corre la red por lotes del tamaño congelado, con padding."""
        import mindspore as ms

        n = len(ids)
        results = np.zeros(n, dtype=np.float32)

        for start in range(0, n, self.batch_size):
            chunk_ids = ids[start : start + self.batch_size]
            chunk_vals = vals[start : start + self.batch_size]
            actual = len(chunk_ids)

            if actual < self.batch_size:
                pad = self.batch_size - actual
                chunk_ids = np.concatenate([chunk_ids, np.tile(chunk_ids[-1:], (pad, 1))])
                chunk_vals = np.concatenate(
                    [chunk_vals, np.zeros((pad, self.featurizer.field_size), np.float32)]
                )

            dummy_labels = ms.Tensor(np.zeros((self.batch_size, 1), np.float32))
            _, probs, _ = self.predictor(
                ms.Tensor(chunk_ids), ms.Tensor(chunk_vals), dummy_labels
            )
            results[start : start + actual] = probs.asnumpy().reshape(-1)[:actual]

        return results


@dataclass
class _ModelConfig:
    """
    Config mínima que consume `WideDeepModel.__init__`.

    Los valores de arquitectura vienen de training_config.json; el resto son los
    del entrenamiento standalone en CPU. `dropout_flag=False` porque en
    inferencia no se aplica dropout.
    """
    batch_size: int
    field_size: int
    vocab_size: int
    emb_dim: int
    deep_layer_dim: List[int]
    deep_layer_act: str

    dropout_flag: bool = False
    keep_prob: float = 1.0
    weight_bias_init: Tuple[str, str] = ("normal", "normal")
    emb_init: str = "normal"
    init_args: Tuple[float, float] = (-0.01, 0.01)
    host_device_mix: int = 0
    parameter_server: int = 0
    sparse: bool = False
    field_slice: bool = False
    full_batch: bool = False
    manual_shape: Any = None
    vocab_cache_size: int = 0
    deep_table_slice_mode: str = "column_slice"
    use_sp: bool = True
