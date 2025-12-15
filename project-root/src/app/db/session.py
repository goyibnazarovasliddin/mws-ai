"""
DB session generator module.

Task:
- Creates SQLAlchemy engine and SessionLocal.
- Provides `get_db()` dependency (generator).

Connection:
- Gets session via api endpoints `Depends(get_db)`.
- Works with DATABASE_URL in config.py.

Note:
- For hackathon, it is easy to use SQLite `sqlite:///./dev.db`; for production, we will need to switch to Postgres.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite uchun connect_args check_same_thread=False kerak
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

