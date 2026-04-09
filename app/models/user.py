"""
app.models.user — User ORM Model

Represents an application user in PostgreSQL. Supports role-based access
control with 'user' and 'admin' roles. Passwords are stored as bcrypt
hashes (never plaintext). Has a one-to-many relationship with Inspection.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default="user")

    inspections = relationship("Inspection", back_populates="owner")