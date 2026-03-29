# src/db/database.py
# Creates the SQLAlchemy engine (the connection to PostgreSQL)
# and a session factory. Every database operation goes through
# a session — think of it like a transaction wrapper.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# The engine is the actual connection to PostgreSQL
# pool_pre_ping=True means SQLAlchemy checks the connection
# is alive before using it — prevents stale connection errors
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.environment == "development",  # logs SQL in dev only
)

# SessionLocal is a factory that creates database sessions
# autocommit=False means we control when changes are saved
# autoflush=False means we control when changes are sent to DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI dependency — automatically opens a DB session for a
    request and closes it when the request finishes, even if
    an error occurs. Used in every route that needs the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()