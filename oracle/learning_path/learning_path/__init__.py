"""
learning_path — DELPHOS Learning Path Optimizer package.

Subpackage layout:

  core/         Skill graph foundation (schema, converter, graph builder)
  careers/      Career definitions and DB seeder
  engine/       AI scoring pipeline (gap → urgency → efficiency → priority)
  curriculum/   Task library, path generator, and adaptive engine

Public API (the only surface DELPHOS needs to call):
  from learning_path.api import generate_path, get_current_task, complete_task
"""
