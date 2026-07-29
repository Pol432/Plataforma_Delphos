"""
Oracle Catalog
Carga el catálogo real del oráculo (simulaciones y skills) y lo traduce al
vocabulario que consumen los schemas de `app.schemas.ml`.

Fuente de verdad: oracle/recommendation/data/processed/
  - skills_catalog.csv      (52 skills con skill_id/slug — los que vio el modelo)
  - simulation_catalog.csv  (64 simulaciones con skills como nombres, no IDs)

El catálogo del oráculo manda: los IDs de skill de este módulo son los del
dataset de entrenamiento, no los de la tabla `skills` del backend. Así el puente
heurístico y el futuro Wide&Deep hablan el mismo idioma.
"""
import ast
import csv
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from app.schemas.ml import SimulationFeaturesInput

# Los skills que aparecen en las simulaciones pero no en skills_catalog.csv
# reciben IDs sintéticos a partir de este offset, para que ambos lados del
# cálculo de solapamiento compartan vocabulario.
EXTRA_SKILL_ID_OFFSET = 1000

_SLUG_INVALID = re.compile(r"[^a-zA-Z0-9_-]+")


def _slugify_simulation_id(raw: str) -> str:
    """
    `SimulationFeaturesInput.simulation_id` exige ^[a-zA-Z0-9_-]+$, pero 3 filas
    del catálogo traen comas y paréntesis. Normalizamos en vez de relajar la
    validación del schema.
    """
    cleaned = _SLUG_INVALID.sub("_", raw).strip("_")
    return cleaned or "sim_unknown"


def _slugify_skill(name: str) -> str:
    return _SLUG_INVALID.sub("_", name.strip().lower()).strip("_")


def _resolve_data_dir() -> Path:
    """
    Localiza data/processed. Prioridad:
      1. ORACLE_DATA_DIR (lo que usa Docker, ver docker-compose.yml)
      2. Ruta relativa al repo (uvicorn local desde backend/)
    """
    env_dir = os.getenv("ORACLE_DATA_DIR")
    candidates: List[Path] = []
    if env_dir:
        candidates.append(Path(env_dir))

    # backend/app/services/oracle_catalog.py -> repo root son 4 niveles arriba
    repo_root = Path(__file__).resolve().parents[3]
    candidates.append(repo_root / "oracle" / "recommendation" / "data" / "processed")
    candidates.append(Path("/opt/oracle_data"))

    for candidate in candidates:
        if (candidate / "simulation_catalog.csv").is_file():
            return candidate

    raise FileNotFoundError(
        "No se encontró el catálogo del oráculo. Rutas probadas: "
        + ", ".join(str(c) for c in candidates)
        + ". Define ORACLE_DATA_DIR apuntando a oracle/recommendation/data/processed."
    )


class OracleCatalog:
    """Catálogo cargado en memoria. Instanciar vía `get_catalog()`."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.skill_id_by_slug: Dict[str, int] = {}
        self.skill_name_by_id: Dict[int, str] = {}
        self.simulations: List[SimulationFeaturesInput] = []
        self.titles_by_id: Dict[str, str] = {}
        self.careers_by_id: Dict[str, str] = {}
        self._load()

    # --- carga ---

    def _load(self) -> None:
        raw_sims = self._read_simulation_rows()
        self._build_skill_vocabulary(raw_sims)
        self._build_simulations(raw_sims)

    def _read_simulation_rows(self) -> List[dict]:
        with open(self.data_dir / "simulation_catalog.csv", newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def _build_skill_vocabulary(self, raw_sims: List[dict]) -> None:
        """IDs 1-52 del catálogo entrenado; el resto, IDs sintéticos estables."""
        with open(self.data_dir / "skills_catalog.csv", newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                skill_id = int(row["skill_id"])
                slug = row["slug"] or _slugify_skill(row["skill_name"])
                self.skill_id_by_slug[slug] = skill_id
                self.skill_id_by_slug[_slugify_skill(row["skill_name"])] = skill_id
                self.skill_name_by_id[skill_id] = row["skill_name"]

        # Skills que las simulaciones referencian pero el catálogo no cubre
        unknown = set()
        for row in raw_sims:
            for name in self._parse_skill_names(row):
                if _slugify_skill(name) not in self.skill_id_by_slug:
                    unknown.add(name)

        for offset, name in enumerate(sorted(unknown)):
            synthetic_id = EXTRA_SKILL_ID_OFFSET + offset
            self.skill_id_by_slug[_slugify_skill(name)] = synthetic_id
            self.skill_name_by_id[synthetic_id] = name

    @staticmethod
    def _parse_skill_names(row: dict) -> List[str]:
        raw = row.get("simulation_required_skills") or "[]"
        try:
            parsed = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return []
        return [str(s) for s in parsed] if isinstance(parsed, list) else []

    def _build_simulations(self, raw_sims: List[dict]) -> None:
        for row in raw_sims:
            skill_ids = self.resolve_skill_names(self._parse_skill_names(row))
            if not skill_ids:
                # SimulationFeaturesInput exige min_length=1
                continue

            sim_id = _slugify_simulation_id(row["simulation_id"])
            self.simulations.append(
                SimulationFeaturesInput(
                    simulation_id=sim_id,
                    simulation_categoria=row["simulation_categoria"],
                    simulation_nivel_dificultad=row["simulation_nivel_dificultad"],
                    simulation_duracion_horas=float(row["simulation_duracion_horas"]),
                    simulation_industria=row["simulation_industria"],
                    simulation_skill_ids=skill_ids,
                )
            )
            self.titles_by_id[sim_id] = row.get("simulation_title", sim_id)
            self.careers_by_id[sim_id] = row.get("base_career", "")

    # --- consulta ---

    def resolve_skill_names(self, names: List[str]) -> List[int]:
        """Traduce nombres o slugs de skill a IDs del vocabulario del oráculo."""
        resolved = []
        for name in names:
            skill_id = self.skill_id_by_slug.get(_slugify_skill(name))
            if skill_id is not None:
                resolved.append(skill_id)
        return sorted(set(resolved))

    def unresolved_skill_names(self, names: List[str]) -> List[str]:
        """Nombres que no existen en el vocabulario — se devuelven al cliente."""
        return [n for n in names if _slugify_skill(n) not in self.skill_id_by_slug]

    def title_for(self, simulation_id: str) -> str:
        return self.titles_by_id.get(simulation_id, simulation_id)

    def career_for(self, simulation_id: str) -> Optional[str]:
        return self.careers_by_id.get(simulation_id) or None


@lru_cache(maxsize=1)
def get_catalog() -> OracleCatalog:
    """Catálogo cacheado en proceso — los CSV son estáticos."""
    return OracleCatalog(_resolve_data_dir())
