"""
Test configuration and fixtures
"""
import pytest
import os
from urllib.parse import urlsplit, urlunsplit
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.db.session import get_db
from app.api.deps import get_db as deps_get_db

# La suite corre contra el Postgres del compose, no contra SQLite. El stack
# real es Postgres y los modelos usan tipos que sólo existen ahí (JSONB en
# `simulations.real_world_constraints`, entre otros): sobre SQLite la suite ni
# siquiera llega a crear las tablas. Mantener un modo SQLite significaba
# mantener columnas que funcionaran en ambos motores, y eso ya se descartó.
#
# La URL sale, por orden: de `TEST_DATABASE_URL`; si no, de `DATABASE_URL`
# cambiándole el nombre de la base; si no, del default del compose.
DEFAULT_TEST_DB = "aurum_test"
FALLBACK_URL = f"postgresql://postgres:postgres@db:5432/{DEFAULT_TEST_DB}"


def _derive_test_url() -> str:
    explicit = os.getenv("TEST_DATABASE_URL")
    if explicit:
        return explicit
    app_url = os.getenv("DATABASE_URL")
    if not app_url:
        return FALLBACK_URL
    # Misma conexión que la app pero otra base: la suite hace create_all y
    # drop_all, así que apuntarla a la base de la app borraría los datos de
    # desarrollo de quien la corra.
    parts = urlsplit(app_url)
    return urlunsplit(parts._replace(path=f"/{DEFAULT_TEST_DB}"))


SQLALCHEMY_DATABASE_URL = _derive_test_url()

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    raise RuntimeError(
        "La suite ya no corre sobre SQLite: los modelos usan tipos propios de "
        "Postgres (JSONB) que SQLite no sabe crear. Apunta TEST_DATABASE_URL a "
        f"un Postgres, p. ej. {FALLBACK_URL}"
    )


def _ensure_database_exists(url: str) -> None:
    """Crea la base de test si no existe.

    `Base.metadata.create_all` crea las tablas, pero la base tiene que existir
    antes. Hacerlo aquí es lo que permite correr `pytest` a secas sin depender
    de que alguien haya pasado antes por `oracle/scripts/run_tests.sh`.
    """
    parts = urlsplit(url)
    db_name = parts.path.lstrip("/")
    # `postgres` es la base de mantenimiento: siempre existe y no se toca.
    admin_url = urlunsplit(parts._replace(path="/postgres"))
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                # El nombre viene de nuestra propia config, no de entrada de
                # usuario; CREATE DATABASE no admite parámetros ligados.
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        admin_engine.dispose()


_ensure_database_exists(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once per test session"""
    # Arrancar de cero: si una ejecución anterior se cortó a media, las tablas
    # viejas siguen ahí y el create_all no las actualiza.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden DB dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Los routers de auth/users/community dependen de `app.api.deps.get_db`,
    # que es una función distinta de `app.db.session.get_db` aunque la envuelva.
    # FastAPI indexa los overrides por objeto función, así que hay que
    # sobreescribir las dos: si no, esos endpoints se saltan la sesión de test
    # y acaban escribiendo contra la base de datos real.
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[deps_get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def valid_company_data():
    """Valid company data for tests"""
    return {
        "nombre_empresa": "Test Company Inc",
        "slug": "test-company-inc",
        "tipo_empresa": "real_nacional",
        "industria": "Technology",
        "pais": "Ecuador",
        "ciudad": "Quito"
    }

@pytest.fixture
def test_company(db_session, valid_company_data):
    """Create test company"""
    from app.models.empresa import Empresa
    company = Empresa(**valid_company_data)
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company
