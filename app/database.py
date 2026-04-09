"""
app.database — SQLAlchemy Database Configuration

Sets up the database engine, session factory, and declarative base.
Handles the Render PostgreSQL URL format quirk (postgres:// → postgresql://).

SessionLocal is used both by FastAPI's dependency injection (via get_db)
and by background tasks that need their own independent DB session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()