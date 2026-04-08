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
    is_ai_processed: bool = False

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
    is_ai_processed: bool = False

    class Config:
        from_attributes = True


class InspectionAdminListResponse(BaseModel):
    total: int
    items: list[InspectionAdminResponse]