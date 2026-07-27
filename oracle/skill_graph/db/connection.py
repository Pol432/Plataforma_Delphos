from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # drops stale connections before use
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def check_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ DB connection OK")

if __name__ == "__main__":
    check_connection()
