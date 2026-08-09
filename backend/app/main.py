import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- NUEVOS IMPORTS PARA LA BASE DE DATOS ---
from app.db.session import engine
import app.models.user as user_model
# --------------------------------------------

# Imports de Modelos (para inicializar Base)
import app.models.user
import app.models.catalog
import app.models.university
import app.models.empresa
import app.models.usuarios_empresa
import app.models.simulations
import app.models.skill
import app.models.learning_path
import app.models.user_progress

# Imports de Routers (¡Comunidad añadida al final!)
from app.api.v1 import content, auth, catalogs, universities, empresas, company_users, simulations, users, skills, progress, community, oracle

from app.db.session import get_db

# =============================================================================
# INICIALIZACIÓN DE TABLAS (LLAVE MAESTRA)
# =============================================================================
# Esto crea las tablas en PostgreSQL si aún no existen al arrancar la app.
# Si la base de datos no está disponible en el momento de importar la app,
# no abortamos el arranque para permitir entornos de tests y desarrollo.
try:
    user_model.Base.metadata.create_all(bind=engine)
except Exception as exc:
    logging.warning("Unable to create DB tables during app import: %s", exc)

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(
    title="Aurum API",
    version="1.0.0",
    description="Backend para simulaciones educativas empresariales"
)

# =============================================================================
# CONFIGURACIÓN DE CORS
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "online", "message": "Aurum API v1.0"}

# =============================================================================
# REGISTRO DE ROUTERS
# =============================================================================
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(empresas.router, prefix="/api/v1/empresas", tags=["empresas"])
app.include_router(universities.router, prefix="/api/v1/universities", tags=["universities"])
app.include_router(simulations.router, prefix="/api/v1/simulaciones", tags=["simulaciones"])
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
app.include_router(company_users.router, prefix="/api/v1", tags=["company-users"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])

# ¡NUEVA RUTA DE COMUNIDAD!
app.include_router(community.router, prefix="/api/v1/community", tags=["community"])

# Oráculo: recomendación de simulaciones (puente heurístico)
app.include_router(oracle.router, prefix="/api/v1/oracle", tags=["oracle"])