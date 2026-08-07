from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
import app.models.user_progress

# Imports de Routers (¡Comunidad añadida al final!)
from app.api.v1 import content, auth, catalogs, universities, empresas, company_users, simulations, users, skills, progress, community, oracle

from app.db.session import get_db

# =============================================================================
# INICIALIZACIÓN DE TABLAS (LLAVE MAESTRA)
# =============================================================================
# Esto crea las tablas en PostgreSQL si aún no existen al arrancar la app
user_model.Base.metadata.create_all(bind=engine)

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

# =============================================================================
# ERRORES DE VALIDACIÓN: NO DEVOLVER CREDENCIALES EN CLARO
# =============================================================================
# FastAPI incluye en cada error de validación el valor recibido, bajo "input".
# En un registro fallido eso significaba devolver (y dejar en logs y en
# herramientas de error) la contraseña en claro: un 422 por password corta
# respondía {"loc": ["body","password"], "input": "short"}. Y con un error a
# nivel de modelo (p. ej. birth_year fuera de rango) el "input" es el cuerpo
# entero, contraseña incluida.
#
# Solo se tapa el valor: loc, type, msg y ctx se devuelven igual que antes.

SENSITIVE_FIELD_NAMES = frozenset({
    "password",
    "password_confirm",
    "confirm_password",
    "current_password",
    "new_password",
    "hashed_password",
    "secret",
    "access_token",
    "refresh_token",
    "token_sesion",
})

REDACTED_PLACEHOLDER = "[REDACTED]"


def _redact_sensitive(value, field_name=None):
    """Tapa los campos sensibles de un valor de error, recursivamente.

    Se compara el nombre EXACTO, no por subcadena: hay campos legítimos que
    contienen "token" y no son secretos (`token_type` vale "bearer",
    `tokens_usados` es un contador) y no deben acabar redactados.
    """
    if field_name is not None and field_name in SENSITIVE_FIELD_NAMES:
        return REDACTED_PLACEHOLDER
    if isinstance(value, dict):
        return {k: _redact_sensitive(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_sensitive(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error = dict(error)
        if "input" in error:
            loc = error.get("loc") or ()
            # El último tramo de loc es el nombre del campo en los errores de
            # campo; en los de modelo es solo ("body",) y hay que recorrer el
            # cuerpo entero buscando claves sensibles.
            field_name = loc[-1] if loc and isinstance(loc[-1], str) else None
            error["input"] = _redact_sensitive(error["input"], field_name)
        errors.append(error)

    # 422 literal a propósito: `status.HTTP_422_UNPROCESSABLE_ENTITY` está
    # deprecado en esta versión de Starlette y emitía un warning por cada
    # error de validación.
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": errors}),
    )


@app.get("/")
def root():
    return {"status": "online", "message": "Aurum API v1.0"}


# =============================================================================
# HEALTHCHECK
# =============================================================================
# El HEALTHCHECK del Dockerfile hace `curl -f http://localhost:8000/health`,
# pero la ruta nunca llegó a existir: solo estaba `/`. Por eso /health devolvía
# 404 y en la demo hubo que usar `/` como sustituto.
#
# Es una sonda de liveness a propósito: responde 200 mientras el proceso
# atienda peticiones y NO consulta la base de datos. Si comprobara la DB, una
# caída de PostgreSQL marcaría el contenedor como unhealthy y Docker lo
# reiniciaría en bucle sin que el fallo esté en la API. La disponibilidad de la
# DB es una comprobación de readiness aparte, si hace falta más adelante.


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok", "service": app.title, "version": app.version}

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