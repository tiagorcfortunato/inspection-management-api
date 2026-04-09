"""
app.core — Cross-Cutting Concerns

Shared infrastructure used by all layers of the application:

    config.py    Environment-based settings (Pydantic Settings)
    deps.py      FastAPI dependency injection (DB sessions, auth)
    enums.py     Domain enums (DamageType, Severity, Status, etc.)
    security.py  Password hashing (bcrypt) and JWT token management
    limiter.py   Rate limiting configuration (SlowAPI)
"""
