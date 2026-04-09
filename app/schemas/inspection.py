"""
app.schemas.inspection — Inspection Request/Response Schemas

Defines the API contract for inspection endpoints:
- InspectionCreate: accepts optional damage_type/severity (AI fills them in)
  and optional image_data (base64) for vision classification
- InspectionResponse: includes AI fields (ai_rationale, ai_damage_type,
  ai_severity, is_ai_processed, is_ai_overridden) for transparency
- InspectionAdminResponse: adds user_email for cross-user admin views

Key design decision: InspectionCreate makes damage_type and severity
optional (overriding the base class) because when an image is uploaded,
the AI will classify them — the user doesn't need to guess.
"""

from datetime import datetime

from pydantic import BaseModel

from app.core.enums import DamageType, SeverityLevel, InspectionStatus


class InspectionBase(BaseModel):
    location_code: str
    damage_type: DamageType
    severity: SeverityLevel
    notes: str | None = None


class InspectionCreate(InspectionBase):
    damage_type: DamageType | None = None
    severity: SeverityLevel | None = None
    image_data: str | None = None


class InspectionUpdate(BaseModel):
    location_code: str | None = None
    damage_type: DamageType | None = None
    severity: SeverityLevel | None = None
    status: InspectionStatus | None = None
    notes: str | None = None


class InspectionResponse(InspectionBase):
    id: int
    status: InspectionStatus
    reported_at: datetime
    user_id: int
    image_data: str | None = None
    ai_rationale: str | None = None
    ai_damage_type: str | None = None
    ai_severity: str | None = None
    is_ai_processed: bool = False
    is_ai_overridden: bool = False

    class Config:
        from_attributes = True


class InspectionListResponse(BaseModel):
    total: int
    items: list[InspectionResponse]


class InspectionAdminResponse(BaseModel):
    id: int
    location_code: str
    damage_type: DamageType
    severity: SeverityLevel
    status: InspectionStatus
    notes: str | None
    reported_at: datetime
    user_id: int
    user_email: str
    ai_rationale: str | None = None
    ai_damage_type: str | None = None
    ai_severity: str | None = None
    is_ai_processed: bool = False
    is_ai_overridden: bool = False

    class Config:
        from_attributes = True


class InspectionAdminListResponse(BaseModel):
    total: int
    items: list[InspectionAdminResponse]