"""
app.database — SQLAlchemy Database Configuration

Sets up the database engine, session factory, and declarative base.
Handles the Render PostgreSQL URL format quirk (postgres:// -> postgresql://)
and falls back to SQLite for free-tier demo deployments.

SessionLocal is used both by FastAPI's dependency injection (via get_db)
and by background tasks that need their own independent DB session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = normalize_database_url(settings.DATABASE_URL)
IS_SQLITE = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=not IS_SQLITE,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
