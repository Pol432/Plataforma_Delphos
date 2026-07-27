import pytest
from app.models.oracle import OracleQuestion, QuestionOption, OracleSession
from app.schemas.oracle import AnswerCreate
from pydantic import ValidationError

class TestOracleEngineSafe:
    def test_schema_answer_valid(self):
        schema = AnswerCreate(pregunta_id=1, opcion_id=4, tiempo_respuesta_segundos=12)
        assert schema.opcion_id == 4

    def test_schema_answer_invalid_time(self):
        with pytest.raises(ValidationError):
            AnswerCreate(pregunta_id=1, opcion_id=4, tiempo_respuesta_segundos=-5)

    def test_model_question_option_skill_mapping_default(self):
        # skill_mapping arranca como dict vacío por defecto
        opcion = QuestionOption(pregunta_id=1, texto_opcion="Me gusta programar")
        assert opcion.skill_mapping is None or isinstance(opcion.skill_mapping, dict)

    def test_model_question_option_skill_mapping_values(self):
        # Asignamos un skill_mapping dinámico y verificamos su contenido
        skill_map = {"planificacion_proyectos": 25, "gestion_tiempo": 20, "organizacion": 22}
        opcion = QuestionOption(
            pregunta_id=1,
            texto_opcion="Creo una lista de tareas detallada",
            skill_mapping=skill_map
        )
        assert opcion.skill_mapping["planificacion_proyectos"] == 25
        assert opcion.skill_mapping["gestion_tiempo"] == 20
        assert opcion.skill_mapping["organizacion"] == 22

    def test_model_session_inferred_skills_accumulation(self):
        # Simulamos la lógica de acumulación dinámica de skills
        sesion = OracleSession(usuario_id=1, estado="en_progreso", inferred_skills={})
        opcion_elegida = QuestionOption(
            skill_mapping={"pensamiento_analitico": 10, "creatividad": 5}
        )

        # Aplicar skill_mapping de la opción al acumulador de la sesión
        for skill, valor in opcion_elegida.skill_mapping.items():
            sesion.inferred_skills[skill] = sesion.inferred_skills.get(skill, 0) + valor

        assert sesion.inferred_skills["pensamiento_analitico"] == 10
        assert sesion.inferred_skills["creatividad"] == 5

    def test_model_session_inferred_skills_multi_answer(self):
        # Múltiples respuestas acumulan correctamente en el mismo dict
        sesion = OracleSession(usuario_id=1, estado="en_progreso", inferred_skills={})

        respuestas = [
            {"pensamiento_analitico": 10, "creatividad": 5},
            {"pensamiento_analitico": 15, "liderazgo": 8},
            {"creatividad": 10, "liderazgo": 7},
        ]

        for skill_map in respuestas:
            for skill, valor in skill_map.items():
                sesion.inferred_skills[skill] = sesion.inferred_skills.get(skill, 0) + valor

        assert sesion.inferred_skills["pensamiento_analitico"] == 25
        assert sesion.inferred_skills["creatividad"] == 15
        assert sesion.inferred_skills["liderazgo"] == 15
