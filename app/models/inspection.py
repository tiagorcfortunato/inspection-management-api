from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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

    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="inspections")