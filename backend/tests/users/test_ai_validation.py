import pytest
from pydantic import ValidationError
from app.schemas.user import UserUpdate

class TestAIFeaturesValidation:
    def test_inferred_skills_valid_dict_accepted(self):
        # Un diccionario de skills válido debe ser aceptado sin errores
        update_data = UserUpdate(
            inferred_skills={
                "pensamiento_analitico": 72.5,
                "creatividad": 65.0,
                "liderazgo": 88.0
            }
        )
        assert update_data.inferred_skills["pensamiento_analitico"] == 72.5
        assert update_data.inferred_skills["creatividad"] == 65.0
        assert update_data.inferred_skills["liderazgo"] == 88.0

    def test_inferred_skills_none_by_default(self):
        # Sin pasar inferred_skills, debe quedar en None (campo opcional)
        update_data = UserUpdate(full_name="Test User")
        assert update_data.inferred_skills is None

    def test_inferred_skills_empty_dict_accepted(self):
        # Un dict vacío es un estado válido (usuario no ha hecho el test aún)
        update_data = UserUpdate(inferred_skills={})
        assert update_data.inferred_skills == {}

    def test_inferred_skills_mixed_numeric_values(self):
        # El dict acepta tanto int como float como valores de skill
        update_data = UserUpdate(
            inferred_skills={
                "planificacion_proyectos": 25,
                "storytelling": 33.3,
                "resolucion_problemas": 90
            }
        )
        assert update_data.inferred_skills["planificacion_proyectos"] == 25
        assert update_data.inferred_skills["storytelling"] == 33.3

    def test_user_update_without_skills_still_valid(self):
        # Los demás campos de UserUpdate siguen funcionando independientemente
        update_data = UserUpdate(full_name="María García", phone="+593999000111")
        assert update_data.full_name == "María García"
        assert update_data.inferred_skills is None
