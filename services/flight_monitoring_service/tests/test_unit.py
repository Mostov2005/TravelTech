import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))

from app.services import FlightMonitoringService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    monitoring_service = FlightMonitoringService(db)
    monitoring_service.monitoring_repository = MagicMock()
    monitoring_service.status_repository = MagicMock()
    monitoring_service.monitoring_repository.db = db
    return monitoring_service


def test_create_monitoring_success(service):
    flight_id = uuid4()
    monitoring = MagicMock()
    monitoring.id = uuid4()

    service.monitoring_repository.get_by_flight_id.return_value = None
    service.monitoring_repository.create.return_value = monitoring

    data = MagicMock()
    data.flight_id = flight_id
    data.status = "scheduled"

    with patch("app.services.get_flight") as mock_get_flight:
        result = service.create_monitoring(data)

    assert result == monitoring
    mock_get_flight.assert_called_once_with(str(flight_id))
    service.monitoring_repository.create.assert_called_once()
    service.status_repository.create.assert_called_once()


def test_create_monitoring_duplicate(service):
    service.monitoring_repository.get_by_flight_id.return_value = MagicMock()

    data = MagicMock()
    data.flight_id = uuid4()

    with patch("app.services.get_flight") as mock_get_flight:
        with pytest.raises(HTTPException) as exc:
            service.create_monitoring(data)

    assert exc.value.status_code == 409
    mock_get_flight.assert_called_once_with(str(data.flight_id))
    service.monitoring_repository.create.assert_not_called()


def test_get_monitoring_success(service):
    monitoring_id = uuid4()
    monitoring = MagicMock()
    service.monitoring_repository.get_by_id.return_value = monitoring

    result = service.get_monitoring(monitoring_id)

    assert result == monitoring
    service.monitoring_repository.get_by_id.assert_called_once_with(monitoring_id)


def test_get_monitoring_not_found(service):
    service.monitoring_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_monitoring(uuid4())

    assert exc.value.status_code == 404


def test_get_all_monitorings(service):
    monitorings = [MagicMock(), MagicMock()]
    service.monitoring_repository.get_all.return_value = monitorings

    result = service.get_all_monitorings()

    assert result == monitorings
    service.monitoring_repository.get_all.assert_called_once()


def test_get_status_history(service):
    monitoring_id = uuid4()
    monitoring = MagicMock()
    history = [MagicMock(), MagicMock()]

    service.monitoring_repository.get_by_id.return_value = monitoring
    service.status_repository.get_by_monitoring_id.return_value = history

    result = service.get_status_history(monitoring_id)

    assert result == history
    service.monitoring_repository.get_by_id.assert_called_once_with(monitoring_id)
    service.status_repository.get_by_monitoring_id.assert_called_once_with(monitoring_id)


def test_update_status_success(service, db):
    monitoring_id = uuid4()
    monitoring = MagicMock()
    monitoring.id = monitoring_id

    data = MagicMock()
    data.status = "delayed"
    data.description = "Flight delayed"

    service.monitoring_repository.get_by_id.return_value = monitoring

    result = service.update_status(monitoring_id, data)

    assert result == monitoring
    assert monitoring.status == "delayed"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(monitoring)
    service.status_repository.create.assert_called_once()
