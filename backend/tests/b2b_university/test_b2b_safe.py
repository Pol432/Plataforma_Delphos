import pytest
from pydantic import ValidationError
from app.models.b2b_university import AcademicProgram, UniversityStudent, ProgramSimulation, UniversityReport
from app.models.analytics import CandidateEvent, SimulationAnalytics, SimulationCohort, ConversionFunnel
from app.schemas.b2b_university import AcademicProgramCreate, UniversityStudentCreate, ProgramSimulationCreate, UniversityReportCreate, CandidateEventCreate, SimulationAnalyticsCreate, SimulationCohortCreate, ConversionFunnelCreate

class TestB2BSafe:
    def test_schema_academic_program_valido(self):
        data = AcademicProgramCreate(universidad_id=1, nombre_programa="Ingeniería", tipo_programa="pregrado", total_creditos=240)
        assert data.tipo_programa == "pregrado"
        
    def test_schema_academic_program_invalido(self):
        with pytest.raises(ValidationError):
            AcademicProgramCreate(universidad_id=1, nombre_programa="Curso", tipo_programa="invalido")

    def test_schema_university_student_valido(self):
        data = UniversityStudentCreate(usuario_id=5, universidad_id=2, estado_estudiante="egresado")
        assert data.estado_estudiante == "egresado"

    def test_schema_program_simulation_semestre_rango(self):
        with pytest.raises(ValidationError):
            ProgramSimulationCreate(simulacion_id=1, programa_id=1, semestre_sugerido=11)

    def test_schema_university_report_tasa_rango(self):
        with pytest.raises(ValidationError):
            UniversityReportCreate(universidad_id=1, periodo="2025-I", tasa_aprobacion=101.0)

    def test_schema_candidate_event_metadata(self):
        data = CandidateEventCreate(candidato_empresa_id=1, tipo_evento="entrevista", metadata_evento={"zoom": True})
        assert data.metadata_evento["zoom"] is True

    def test_schema_simulation_analytics_nps_rango(self):
        with pytest.raises(ValidationError):
            SimulationAnalyticsCreate(simulacion_id=1, empresa_id=1, nps_score=150.0)

    def test_model_instantiation_memory(self):
        # Valida que los defaults actúen correctamente
        cohorte = SimulationCohort(simulacion_id=3, nombre_cohorte="Enero", tasa_retencion_dia_7=68.5)
        assert cohorte.nombre_cohorte == "Enero"
        
        funnel = ConversionFunnel(simulacion_id=5, paso_1_nombre="Landing", paso_1_usuarios=1000, tasa_conversion_total=23.4)
        assert funnel.paso_1_usuarios == 1000
