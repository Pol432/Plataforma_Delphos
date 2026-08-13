"""
Oracle Engine — selección de motor de ranking para /api/v1/oracle/recommend.

Dos motores detrás de la misma interfaz:

* `heuristic_bridge_v1` — `RecommendationService`, el puente heurístico. Es
  quien produce SIEMPRE los valores de `MatchingOutput` que viajan en la
  respuesta (`engagement_probability`, `skill_overlap_score`,
  `difficulty_match_score`).
* `wide_and_deep` — el checkpoint entrenado (`oracle/recommendation/inference.py`).
  Se usa **sólo para ordenar** la lista de candidatos.

--------------------------------------------------------------------------
Por qué el modelo sólo ordena
--------------------------------------------------------------------------
La calibración del modelo está sin resolver (AUC 0.9928 en train contra 0.7740
en test, y el 85.6 % de las probabilidades cae fuera de [0.01, 0.99]; un 25 %
son exactamente 0.0 por underflow de sigmoid en float32). Ese número no es
defendible como "probabilidad de engagement" en términos absolutos, y publicarlo
en `scores.engagement_probability` mostraría "0 %" en varias tarjetas de la
demo.

El orden relativo sí es utilizable: AUC 0.7764 sobre test. Así que el modelo
decide el ranking y el heurístico sigue llenando los números visibles. El
contrato JSON no cambia: mismos campos, mismo shape. Lo único que cambia es
`engine`, que refleja qué motor ordenó de verdad — sin eso no habría forma de
distinguir "el modelo respondió" de "cayó al fallback en silencio".

--------------------------------------------------------------------------
Modos (`ORACLE_ENGINE`)
--------------------------------------------------------------------------
    auto       (default) intenta el modelo; ante cualquier problema cae al
               heurístico sin romper la petición.
    heuristic  fuerza el puente heurístico y NO importa MindSpore. Kill switch:
               apaga el modelo sin redeploy si algo sale mal en vivo.
    widedeep   exige el modelo; propaga la excepción en vez de enmascararla.
               Para tests y diagnóstico, no para la demo.
"""
from __future__ import annotations

import logging
import os
import sys
import threading
from pathlib import Path
from typing import Any, List, Optional, Sequence

logger = logging.getLogger(__name__)

ENGINE_HEURISTIC = "heuristic_bridge_v1"
ENGINE_WIDEDEEP = "wide_and_deep"

MODE_AUTO = "auto"
MODE_HEURISTIC = "heuristic"
MODE_WIDEDEEP = "widedeep"
VALID_MODES = (MODE_AUTO, MODE_HEURISTIC, MODE_WIDEDEEP)

#: Dos scores se consideran iguales por debajo de esto. El modelo satura duro,
#: así que el criterio es de igualdad numérica, no de "parecido".
_EPS = 1e-9

#: Fracción del catálogo que puede saturar en el mismo extremo antes de
#: considerar la salida degenerada. Que muchos empaten a 0.0 es esperable y
#: `rank_candidates()` lo desempata con los diagnósticos; que empate TODO
#: significa que el modelo no está discriminando nada y ordenarlo es ruido.
_SATURATION_LIMIT = 1.0


def get_mode() -> str:
    """Modo efectivo. Un valor desconocido cae a `auto` y se avisa."""
    raw = (os.getenv("ORACLE_ENGINE") or MODE_AUTO).strip().lower()
    if raw not in VALID_MODES:
        logger.warning(
            "ORACLE_ENGINE=%r no es válido (%s). Se usa %r.",
            raw, ", ".join(VALID_MODES), MODE_AUTO,
        )
        return MODE_AUTO
    return raw


def resolve_model_dir() -> Path:
    """
    Localiza `oracle/recommendation/` (donde viven inference.py y checkpoints/).

    Misma prioridad que `oracle_catalog._resolve_data_dir`: variable de entorno
    primero (lo que usa Docker), ruta relativa al repo después.

    Pública porque `oracle_catalog` la reutiliza para importar la tabla de
    mapeo OOV — duplicar la lógica de rutas era pedir que se desincronizaran.
    """
    candidates: List[Path] = []
    env_dir = os.getenv("ORACLE_MODEL_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    # backend/app/services/oracle_engine.py -> raíz del repo son 4 niveles arriba
    candidates.append(Path(__file__).resolve().parents[3] / "oracle" / "recommendation")
    candidates.append(Path("/opt/oracle"))

    for candidate in candidates:
        if (candidate / "inference.py").is_file():
            return candidate

    raise FileNotFoundError(
        "No se encontró oracle/recommendation (inference.py). Rutas probadas: "
        + ", ".join(str(c) for c in candidates)
        + ". Define ORACLE_MODEL_DIR."
    )


# --------------------------------------------------------------------------
# Carga perezosa del modelo
# --------------------------------------------------------------------------

_lock = threading.Lock()
_recommender: Any = None
_load_failed = False
_load_error: Optional[str] = None


def get_recommender(force: bool = False) -> Any:
    """
    Devuelve el `WideDeepRecommender` cargado, o None si no se pudo.

    Cargar el checkpoint tarda (construye el grafo de MindSpore), así que se
    hace una sola vez, en la primera petición que lo necesite, bajo lock: dos
    peticiones concurrentes al arrancar no deben construir el grafo dos veces.

    Un fallo se recuerda (`_load_failed`) para no reintentar en cada petición y
    convertir un problema de arranque en 64 timeouts por request.

    Con `force=True` (modo `widedeep`) la excepción se propaga en vez de
    devolver None.
    """
    global _recommender, _load_failed, _load_error

    if _recommender is not None:
        return _recommender
    if _load_failed and not force:
        return None

    with _lock:
        if _recommender is not None:
            return _recommender
        if _load_failed and not force:
            return None
        try:
            model_dir = resolve_model_dir()
            if str(model_dir) not in sys.path:
                sys.path.insert(0, str(model_dir))

            from inference import WideDeepRecommender  # noqa: E402

            # batch_size queda congelado en el grafo. 64 = tamaño del catálogo,
            # así que las 64 simulaciones entran en un solo forward.
            _recommender = WideDeepRecommender.load(root=model_dir, batch_size=64)
            _load_failed = False
            _load_error = None
            logger.info("Wide&Deep cargado desde %s", model_dir)
            return _recommender
        except Exception as exc:  # ImportError, FileNotFoundError, RuntimeError...
            _load_failed = True
            _load_error = f"{type(exc).__name__}: {exc}"
            if force:
                raise
            logger.warning(
                "No se pudo cargar el Wide&Deep (%s). Se usa %s.",
                _load_error, ENGINE_HEURISTIC,
            )
            return None


def reset_cache() -> None:
    """Descarta el modelo cacheado. Para tests — no se llama en producción."""
    global _recommender, _load_failed, _load_error
    with _lock:
        _recommender = None
        _load_failed = False
        _load_error = None


def last_load_error() -> Optional[str]:
    """Último error de carga, para logs y diagnóstico."""
    return _load_error


# --------------------------------------------------------------------------
# Detección de salida degenerada
# --------------------------------------------------------------------------

def is_degenerate(probabilities: Sequence[float]) -> Optional[str]:
    """
    Devuelve el motivo si la salida del modelo no sirve para ordenar, o None.

    Dos formas de degeneración, las dos pedidas explícitamente:

    * **Todo el mismo score.** Si las 64 simulaciones tienen la misma
      probabilidad, el orden resultante es el orden de entrada disfrazado de
      recomendación.
    * **Todo saturado en el mismo extremo.** Equivalente a lo anterior en la
      práctica (0.0 o 1.0 para todos), pero se distingue en el log porque
      apunta a un problema distinto: no es que el modelo no discrimine, es que
      la sigmoid se fue al fondo.

    Que *muchos* empaten a 0.0 no es degenerado: es el comportamiento conocido
    del checkpoint, y `rank_candidates()` los desempata con los diagnósticos
    descriptivos. Sólo se rechaza cuando empata el catálogo entero.

    Un NaN o un infinito también invalidan el orden, así que cuentan.
    """
    if not probabilities:
        return "el modelo no devolvió scores"

    values = [float(p) for p in probabilities]

    if any(v != v or v in (float("inf"), float("-inf")) for v in values):
        return "el modelo devolvió NaN o infinito"

    if len(values) == 1:
        return None

    spread = max(values) - min(values)
    if spread <= _EPS:
        return f"las {len(values)} simulaciones tienen el mismo score ({values[0]:.6g})"

    n = len(values)
    if sum(1 for v in values if v <= _EPS) >= _SATURATION_LIMIT * n:
        return f"las {n} probabilidades están saturadas en 0.0"
    if sum(1 for v in values if v >= 1.0 - _EPS) >= _SATURATION_LIMIT * n:
        return f"las {n} probabilidades están saturadas en 1.0"

    return None


# --------------------------------------------------------------------------
# API pública
# --------------------------------------------------------------------------

def model_ranking(matching_inputs: Sequence[Any]) -> Optional[List[int]]:
    """
    Orden que propone el modelo, como permutación de índices del catálogo.

    Devuelve None cuando hay que caer al heurístico: modo `heuristic`, modelo no
    cargable, excepción durante la inferencia, o scores degenerados. Nunca
    levanta en modo `auto` — el objetivo es que la demo no se rompa.

    El orden viene de `rank_candidates()`, que ordena por probabilidad y
    desempata con los diagnósticos descriptivos (solapamiento de skills, luego
    alineación de dificultad). No se desempata con el logit a propósito: en la
    cola saturada el logit ordena peor que al azar (AUC 0.2129 medido).
    """
    mode = get_mode()
    if mode == MODE_HEURISTIC:
        return None
    if not matching_inputs:
        return None

    recommender = get_recommender(force=(mode == MODE_WIDEDEEP))
    if recommender is None:
        return None

    try:
        ranked = recommender.rank_candidates(matching_inputs)
        order = [index for index, _ in ranked]
        probabilities = [output.engagement_probability for _, output in ranked]
    except Exception as exc:
        if mode == MODE_WIDEDEEP:
            raise
        logger.warning("El Wide&Deep falló durante la inferencia (%s: %s). Se usa %s.",
                       type(exc).__name__, exc, ENGINE_HEURISTIC)
        return None

    if len(order) != len(matching_inputs) or sorted(order) != list(range(len(matching_inputs))):
        logger.warning("rank_candidates() no devolvió una permutación válida. Se usa %s.",
                       ENGINE_HEURISTIC)
        return None if mode != MODE_WIDEDEEP else order

    reason = is_degenerate(probabilities)
    if reason is not None:
        if mode == MODE_WIDEDEEP:
            raise RuntimeError(f"Salida degenerada del Wide&Deep: {reason}")
        logger.warning("Salida degenerada del Wide&Deep (%s). Se usa %s.", reason, ENGINE_HEURISTIC)
        return None

    return order
