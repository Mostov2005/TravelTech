import sys
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))

from app.services import IdentityService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    identity_service = IdentityService(db)
    identity_service.user_repository = MagicMock()
    identity_service.role_repository = MagicMock()
    identity_service.session_repository = MagicMock()
    return identity_service


def test_register_success(service):
    data = MagicMock()
    data.email = "test@example.com"
    data.username = "testuser"
    data.password = "password123"

    service.user_repository.get_by_email.return_value = None
    service.user_repository.get_by_username.return_value = None

    role = MagicMock()
    role.id = uuid4()
    service.role_repository.get_by_name.return_value = role

    service.user_repository.create.side_effect = lambda user: user

    result = service.register(data)

    assert result.email == data.email
    assert result.username == data.username
    service.user_repository.create.assert_called_once()


def test_register_duplicate_email(service):
    data = MagicMock()
    data.email = "test@example.com"
    data.username = "testuser"

    service.user_repository.get_by_email.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.register(data)

    assert exc.value.status_code == 409
    service.user_repository.create.assert_not_called()


def test_register_duplicate_username(service):
    data = MagicMock()
    data.email = "test@example.com"
    data.username = "testuser"

    service.user_repository.get_by_email.return_value = None
    service.user_repository.get_by_username.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.register(data)

    assert exc.value.status_code == 409
    service.user_repository.create.assert_not_called()


def test_login_success(service):
    data = MagicMock()
    data.email = "test@example.com"
    data.password = "password123"

    user = MagicMock()
    user.id = uuid4()
    user.password_hash = "hashed_password"

    service.user_repository.get_by_email.return_value = user

    service_module = sys.modules["app.services"]
    service_module.verify_password = lambda password, hashed: True
    service_module.create_access_token = lambda user_id: "access_token"
    service_module.create_refresh_token = lambda user_id: ("refresh_token", MagicMock())
    service_module.hash_refresh_token = lambda token: "token_hash"

    result = service.login(data)

    assert result["access_token"] == "access_token"
    assert result["refresh_token"] == "refresh_token"
    assert result["token_type"] == "bearer"
    service.session_repository.create.assert_called_once()


def test_login_invalid_credentials(service, monkeypatch):
    data = MagicMock()
    data.email = "test@example.com"
    data.password = "wrong_password"

    user = MagicMock()
    user.password_hash = "hashed_password"

    service.user_repository.get_by_email.return_value = user

    monkeypatch.setattr("app.services.verify_password", lambda password, hashed: False)

    with pytest.raises(HTTPException) as exc:
        service.login(data)

    assert exc.value.status_code == 401
    service.session_repository.create.assert_not_called()


def test_refresh_tokens_success(service, monkeypatch):
    user_id = uuid4()
    refresh_token = "old_refresh_token"

    session = MagicMock()
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    user = MagicMock()
    user.id = user_id

    service.session_repository.get_by_token_hash.return_value = session
    service.user_repository.get_by_id.return_value = user

    monkeypatch.setattr(
        "app.services.decode_token",
        lambda token: {"type": "refresh", "sub": str(user_id)}
    )
    monkeypatch.setattr("app.services.hash_refresh_token", lambda token: "token_hash")
    monkeypatch.setattr("app.services.create_access_token", lambda user_id: "new_access_token")
    monkeypatch.setattr(
        "app.services.create_refresh_token",
        lambda user_id: ("new_refresh_token", datetime.now(timezone.utc) + timedelta(days=7))
    )

    result = service.refresh_tokens(refresh_token)

    assert result["access_token"] == "new_access_token"
    assert result["refresh_token"] == "new_refresh_token"
    assert result["token_type"] == "bearer"
    service.session_repository.delete.assert_called_once_with(session)
    service.session_repository.create.assert_called_once()


def test_get_user_success(service):
    user_id = uuid4()
    user = MagicMock()
    user.id = user_id

    service.user_repository.get_by_id.return_value = user

    result = service.get_user(user_id)

    assert result.id == user_id
    service.user_repository.get_by_id.assert_called_once_with(user_id)
