import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/inspection_test.db")
os.environ.setdefault("SECRET_KEY", "smoke-test-secret")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("GROQ_API_KEY", "ci-test-groq-key")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Start each test session from a clean SQLite file, then create the schema
# via SQLAlchemy metadata (production uses Alembic, but tests skip migrations).
db_path = "/tmp/inspection_test.db"
if os.path.exists(db_path):
    os.remove(db_path)

from app.database import Base, engine
from app.models import inspection, user  # noqa: F401 — register models with Base

Base.metadata.create_all(bind=engine)
