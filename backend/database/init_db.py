from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config.settings import settings
from pathlib import Path

from backend.database.models import *


# --- SQLAlchemy Engine & Session ---
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Dependency for FastAPI routes ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schema Initialization (Optional from schema.sql) ---
def init_db_from_schema():
    schema_path = Path("config/schema.sql")
    if not schema_path.exists():
        print("⚠️  Schema file not found at config/schema.sql")
        return

    import sqlite3
    db_path = settings.database_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    with schema_path.open("r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Database initialized from schema.sql")

