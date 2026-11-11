from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest
)
from services import IdentityService
from security import decode_token

router = APIRouter(prefix="/auth", tags=["Identity"])

security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    try:
        payload = decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        user_id = UUID(payload["sub"])

    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    return IdentityService(db).get_user(user_id)


@router.post("/register", response_model=UserResponse)
def register(
        data: UserRegister,
        db: Session = Depends(get_db)
):
    return IdentityService(db).register(data)


@router.post("/login", response_model=TokenResponse)
def login(
        data: UserLogin,
        db: Session = Depends(get_db)
):
    return IdentityService(db).login(data)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
        data: RefreshTokenRequest,
        db: Session = Depends(get_db)
):
    return IdentityService(db).refresh_tokens(data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(
        current_user=Depends(get_current_user)
):
    return current_user
