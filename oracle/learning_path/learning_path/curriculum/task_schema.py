"""
task_schema.py — Data structures for the task curriculum.

TaskItem       : a single 20–60 min micro-task
LearningPhase  : all tasks for one skill (one phase of the path)
LearningPath   : the complete ordered sequence of phases for a user+career
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TaskItem:
    task_id:          int     # microtareas_lpo.id
    skill_id:         int
    title:            str
    task_type:        str     # lectura | practica | quiz | proyecto | video | ejercicio
    difficulty:       float   # 0–1
    estimated_minutes: int
    skill_gain:       float   # expected mastery points on completion
    resource_url:     Optional[str] = None
    instructions:     Optional[str] = None
    min_pass_score:   int = 60   # % needed to pass


@dataclass
class LearningPhase:
    phase_id:         int       # fases_ruta_aprendizaje.id  (0 if not yet persisted)
    skill_id:         int
    skill_name:       str
    order:            int       # 1-based position in the path
    current_mastery:  float     # at time of path generation
    target_mastery:   float
    priority_score:   float
    tasks:            List[TaskItem] = field(default_factory=list)
    unlocked:         bool = False   # True = user can start now

    @property
    def estimated_total_time(self) -> int:
        """Total estimated minutes for this phase."""
        return sum(t.estimated_minutes for t in self.tasks)

    @property
    def mastery_gap(self) -> float:
        return max(0.0, self.target_mastery - self.current_mastery)

    @property
    def total_skill_gain(self) -> float:
        return sum(t.skill_gain for t in self.tasks)


@dataclass
class LearningPath:
    user_id:              str
    career_slug:          str
    phases:               List[LearningPhase] = field(default_factory=list)
    generated_at:         Optional[str] = None   # ISO timestamp string

    @property
    def total_estimated_hours(self) -> float:
        return sum(p.estimated_total_time for p in self.phases) / 60.0

    @property
    def total_tasks(self) -> int:
        return sum(len(p.tasks) for p in self.phases)

    def get_current_phase(self) -> Optional[LearningPhase]:
        """Return the first unlocked, incomplete phase."""
        for phase in self.phases:
            if phase.unlocked and phase.mastery_gap > 0:
                return phase
        return None

    def get_first_task(self) -> Optional[TaskItem]:
        """Return the very first task the user should do."""
        phase = self.get_current_phase()
        if phase and phase.tasks:
            return phase.tasks[0]
        return None

    def summary(self) -> dict:
        return {
            "user_id":       self.user_id,
            "career_slug":   self.career_slug,
            "phases":        len(self.phases),
            "total_tasks":   self.total_tasks,
            "total_hours":   round(self.total_estimated_hours, 1),
            "generated_at":  self.generated_at,
        }
