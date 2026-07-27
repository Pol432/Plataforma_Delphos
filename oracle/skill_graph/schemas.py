from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class SkillState:
    """Live state of one skill for one user."""
    habilidad_id:    int
    slug:            str
    xp_total:        int
    nivel:           int             # 0–5
    confianza:       float           # 0.0–1.0
    velocidad:       float           # XP points / week
    tendencia_ia:    str             # improving | stable | declining | unknown
    aptitud_predicha: Optional[float]
    fuentes_evidencia: list[str]
    ultimo_inferido_en: Optional[datetime]

    def mastery_0_100(self) -> float:
        """Normalise xp_total to 0–100 for the recommender."""
        return min(self.xp_total / 5.0, 100.0)

    def to_vector_entry(self) -> float:
        return self.mastery_0_100()

    def to_enriched(self) -> dict:
        return {
            "mastery":    self.mastery_0_100(),
            "confidence": self.confianza,
            "velocity":   self.velocidad,
            "trend":      self.tendencia_ia,
            "aptitude":   self.aptitud_predicha,
            "sources":    self.fuentes_evidencia,
        }


@dataclass
class UserSkillProfile:
    """All skill states for one user."""
    usuario_id: int
    skills: dict[str, SkillState] = field(default_factory=dict)  # slug → SkillState
    onboarding_completado: bool = False

    def get_skill_vector(self) -> dict[str, float]:
        return {slug: s.to_vector_entry() for slug, s in self.skills.items()}

    def get_enriched_skills(self) -> dict[str, dict]:
        return {slug: s.to_enriched() for slug, s in self.skills.items()}


@dataclass
class TaskSubmission:
    """Payload from a completed DELPHOS task."""
    tarea_usuario_id: int
    tarea_id:         int
    usuario_id:       int
    submission_text:  Optional[str]
    tiempo_minutos:   int
    pistas_usadas:    list[int]
    total_intentos:   int
    auto_eval_calidad: Optional[int]   # 1–5
    completion_ts:    datetime


@dataclass
class InferenceResult:
    """Raw output from any inference source before DB write."""
    usuario_id:    int
    tipo_fuente:   str               # quiz | tarea | transcript | social | behavioral
    referencia_id: Optional[int]
    skills_raw:    dict[str, float]  # slug → score 0–100
    confianza:     float
    tiempo_ms:     int
