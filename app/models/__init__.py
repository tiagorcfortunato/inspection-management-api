"""
app.models — SQLAlchemy ORM Models

Database entity definitions. Each model maps to a PostgreSQL table
and is managed through Alembic migrations.

    User          Users with email/password auth and role-based access
    Inspection    Road damage reports with AI classification fields

The Inspection model includes a hybrid_property (is_ai_overridden) that
computes whether the current damage_type/severity differs from the
original AI classification — enabling human-in-the-loop override tracking.
"""
