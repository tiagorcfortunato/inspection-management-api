"""
app.schemas — Pydantic Request/Response Models

API contract definitions using Pydantic. Schemas validate incoming requests
and shape outgoing responses, keeping the API contract separate from the
database models.

    auth.py          UserRegister (with password validation), TokenResponse
    inspection.py    Create/Update/Response schemas with AI override fields

Key design decision: InspectionResponse includes computed fields
(is_ai_overridden) that are populated from the ORM model's hybrid_property,
keeping the override logic in one place.
"""
