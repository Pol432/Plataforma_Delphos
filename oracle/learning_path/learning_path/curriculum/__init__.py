"""
learning_path.curriculum — Task library, path generation, and adaptive engine.

    task_schema.py          TaskItem, LearningPhase, LearningPath
    task_database.py        120+ micro-tasks + DB seeder
    curriculum_generator.py Assemble phases from priority list
    adaptive_engine.py      Score-based adaptation (skip / reinforce)
"""
from learning_path.curriculum.task_schema import (
    TaskItem, LearningPhase, LearningPath,
)
from learning_path.curriculum.curriculum_generator import (
    generate_curriculum,
    unlock_next_phase,
)
from learning_path.curriculum.adaptive_engine import (
    CompletionResult,
    handle_task_completion,
)
