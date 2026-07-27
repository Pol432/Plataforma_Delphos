import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Construir la URL de la base de datos usando variables de entorno con fallback
# Esto permite ejecutar la app localmente contra Docker (db) o contra localhost
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "aurum_db")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Crear la sesión usando el engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la DB en cada solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
