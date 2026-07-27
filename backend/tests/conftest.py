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

TEST_DB_FILE = "test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# CRITICAL: Activar Foreign Keys en SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once per test session"""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_FILE):
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
    
    app.dependency_overrides[get_db] = override_get_db
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
