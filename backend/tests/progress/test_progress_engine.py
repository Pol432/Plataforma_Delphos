import pytest
from app.models.progress import UserSimulation, UserTask, UserSkill
from app.schemas.progress import EnrollmentCreate, TaskSubmission
from pydantic import ValidationError

class TestProgressEngineSafe:
    def test_schema_enrollment_valid(self):
        schema = EnrollmentCreate(simulation_id=5)
        assert schema.simulation_id == 5

    def test_schema_enrollment_invalid(self):
        with pytest.raises(ValidationError):
            EnrollmentCreate(simulation_id=0) # Must be > 0

    def test_model_user_simulation_init(self):
        # Los defaults de SQLAlchemy se disparan al hacer commit, 
        # aquí verificamos que la instanciación en memoria sea correcta
        enrollment = UserSimulation(user_id=1, simulation_id=10, estado="inscrito", porcentaje_completado=0.0)
        assert enrollment.estado == "inscrito"
        assert float(enrollment.porcentaje_completado) == 0.0

    def test_model_user_task_init(self):
        task = UserTask(user_id=2, task_id=8, estado="pendiente", calificacion_maxima=100.0)
        assert task.estado == "pendiente"
        assert float(task.calificacion_maxima) == 100.0

    def test_user_skill_level_calculation(self):
        # XP base para nivel 1 es 100, para nivel 2 es 400. Rango = 300.
        # Si xp_total = 250 -> 250 - 100 = 150. 150/300 = 50%
        skill = UserSkill(user_id=1, skill_id=3, xp_total=250, nivel=1)
        assert skill.porcentaje_nivel_actual == 50.0
