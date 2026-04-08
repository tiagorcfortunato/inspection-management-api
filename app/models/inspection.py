from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.enums import DamageType, SeverityLevel, InspectionStatus
from app.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)

    location_code = Column(String, nullable=False, index=True)
    damage_type = Column(String, nullable=False, default=DamageType.pothole.value)
    severity = Column(String, nullable=False, default=SeverityLevel.medium.value)
    status = Column(String, nullable=False, default=InspectionStatus.reported.value)
    notes = Column(String, nullable=True)

    image_data = Column(Text, nullable=True)
    ai_rationale = Column(String, nullable=True)
    is_ai_processed = Column(Boolean, nullable=False, default=False)

    reported_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="inspections")