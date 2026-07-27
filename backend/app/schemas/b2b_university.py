from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class AcademicProgramCreate(BaseModel):
    universidad_id: int = Field(..., gt=0)
    nombre_programa: str = Field(..., min_length=2, max_length=200)
    tipo_programa: str = Field(default="pregrado", pattern="^(pregrado|posgrado)$")
    total_creditos: int = Field(default=0, ge=0)

class UniversityStudentCreate(BaseModel):
    usuario_id: int = Field(..., gt=0)
    universidad_id: int = Field(..., gt=0)
    programa_id: Optional[int] = Field(None, gt=0)
    matricula: Optional[str] = Field(None, max_length=100)
    estado_estudiante: str = Field(default="activo", pattern="^(activo|egresado|retirado)$")
    email_institucional: Optional[str] = Field(None, max_length=255)

class ProgramSimulationCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    programa_id: int = Field(..., gt=0)
    es_obligatoria: bool = False
    semestre_sugerido: Optional[int] = Field(None, ge=1, le=10)

class UniversityReportCreate(BaseModel):
    universidad_id: int = Field(..., gt=0)
    programa_id: Optional[int] = Field(None, gt=0)
    periodo: str = Field(..., min_length=1, max_length=50)
    total_estudiantes: int = Field(default=0, ge=0)
    tasa_aprobacion: float = Field(default=0.0, ge=0.0, le=100.0)

class CandidateEventCreate(BaseModel):
    candidato_empresa_id: int = Field(..., gt=0)
    tipo_evento: str = Field(..., min_length=1, max_length=100)
    detalles: Optional[str] = None
    metadata_evento: Optional[Dict[str, Any]] = None

class SimulationAnalyticsCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    empresa_id: int = Field(..., gt=0)
    periodo_tipo: str = Field(default="mensual", pattern="^(diario|semanal|mensual|trimestral)$")
    total_inscritos: int = Field(default=0, ge=0)
    tasa_completado: float = Field(default=0.0, ge=0.0, le=100.0)
    nps_score: Optional[float] = Field(None, ge=-100.0, le=100.0)

class SimulationCohortCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    nombre_cohorte: str = Field(..., min_length=1, max_length=200)
    tasa_retencion_dia_7: float = Field(default=0.0, ge=0.0, le=100.0)

class ConversionFunnelCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    paso_1_nombre: str = Field(..., min_length=1, max_length=100)
    paso_1_usuarios: int = Field(default=0, ge=0)
    tasa_conversion_total: float = Field(default=0.0, ge=0.0, le=100.0)
