"""
app.routers.auth — Authentication Endpoints

Handles user registration and login. Both endpoints are rate-limited
(5/min for register, 10/min for login) to prevent brute-force attacks.

Login uses OAuth2PasswordRequestForm (form data, not JSON) to comply
with the OAuth2 spec that FastAPI's Swagger UI expects.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.limiter import limiter
from app.schemas.auth import UserRegister, TokenResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(user_data, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return {"message": "User created successfully"}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return result