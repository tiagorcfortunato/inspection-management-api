from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.auth import UserRegister
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(user_data, db)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return {"message": "User created successfully"}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    result = login_user(
        form_data.username,
        form_data.password,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return result