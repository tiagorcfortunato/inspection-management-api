from datetime import datetime

from pydantic import BaseModel

from app.core.enums import DamageType, SeverityLevel, InspectionStatus


class InspectionBase(BaseModel):
    location_code: str
    damage_type: DamageType
    severity: SeverityLevel
    notes: str | None = None


class InspectionCreate(InspectionBase):
    pass


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

    class Config:
        from_attributes = True


class InspectionListResponse(BaseModel):
    total: int
    items: list[InspectionResponse]