"""
Test configuration and fixtures
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.db.session import get_db
from app.api.deps import get_db as deps_get_db

TEST_DB_FILE = "test.db"

# Por defecto SQLite en fichero: es lo que había y lo que hace que la suite
# corra sin depender de ningún servicio. `TEST_DATABASE_URL` permite apuntarla
# a un motor real —en la práctica el Postgres del compose— para verificar lo
# que SQLite no cubre: tipos de columna reales y FKs con su semántica nativa.
#
#   docker compose exec -e TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/aurum_test web pytest
#
# No apuntar a la base de la app: la suite hace create_all/drop_all.
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or f"sqlite:///{TEST_DB_FILE}"
IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # `check_same_thread` es un argumento del driver de SQLite; pasárselo a
    # psycopg2 revienta la conexión.
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

# CRITICAL: Activar Foreign Keys en SQLite
# SQLite las ignora salvo que se pidan por conexión. En Postgres son nativas,
# así que el listener sobra (y `PRAGMA` ni siquiera es SQL válido ahí).
if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once per test session"""
    if IS_SQLITE and os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if IS_SQLITE and os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

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
