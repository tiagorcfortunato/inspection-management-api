"""
app.services.auth_service — Authentication Business Logic

Handles user registration and login:
- register_user: creates a new user with bcrypt-hashed password
- login_user: verifies credentials and returns a JWT token

Admin role assignment: if the user's email matches ADMIN_EMAIL from
environment config, their role is promoted to admin on login. This
avoids needing a separate admin creation flow.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserRegister
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.enums import UserRole


def register_user(user_data: UserRegister, db: Session):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        return None

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if settings.ADMIN_EMAIL and user.email == settings.ADMIN_EMAIL and user.role != UserRole.admin:
        user.role = UserRole.admin
        db.commit()

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
