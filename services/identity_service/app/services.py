from uuid import UUID

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import User, Role, RefreshSession
from schemas import UserRegister, UserLogin
from repositories import (
    UserRepository,
    RoleRepository,
    RefreshSessionRepository
)
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token
)


class IdentityService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.session_repository = RefreshSessionRepository(db)

    def register(self, data: UserRegister):
        if self.user_repository.get_by_email(data.email):
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

        if self.user_repository.get_by_username(data.username):
            raise HTTPException(
                status_code=409,
                detail="Username already taken"
            )

        role = self.role_repository.get_by_name("user")

        if not role:
            role = self.role_repository.create(
                Role(name="user")
            )

        user = User(
            email=data.email,
            username=data.username,
            password_hash=hash_password(data.password),
            role_id=role.id
        )

        return self.user_repository.create(user)

    def login(self, data: UserLogin):
        user = self.user_repository.get_by_email(data.email)

        if not user or not verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(str(user.id))
        refresh_token, expires_at = create_refresh_token(str(user.id))

        refresh_session = RefreshSession(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=expires_at
        )

        self.session_repository.create(refresh_session)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def refresh_tokens(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )

            user_id = UUID(payload["sub"])

        except Exception:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token"
            )

        token_hash = hash_refresh_token(refresh_token)

        session = self.session_repository.get_by_token_hash(token_hash)

        if not session or session.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Refresh session not found or expired"
            )

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        self.session_repository.delete(session)

        new_access_token = create_access_token(str(user.id))
        new_refresh_token, expires_at = create_refresh_token(str(user.id))

        new_session = RefreshSession(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            expires_at=expires_at
        )

        self.session_repository.create(new_session)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    def get_user(self, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user