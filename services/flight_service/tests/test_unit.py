import sys
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))

from app.services import FlightService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    flight_service = FlightService(db)
    flight_service.airport_repository = MagicMock()
    flight_service.flight_repository = MagicMock()
    return flight_service


def test_create_airport_success(service):
    data = MagicMock()
    data.iata_code = "svo"
    data.name = "Sheremetyevo"
    data.city = "Moscow"
    data.country = "Russia"

    service.airport_repository.get_by_iata_code.return_value = None

    airport = MagicMock()
    service.airport_repository.create.return_value = airport

    result = service.create_airport(data)

    assert result == airport
    service.airport_repository.create.assert_called_once()


def test_create_airport_duplicate(service):
    data = MagicMock()
    data.iata_code = "SVO"

    service.airport_repository.get_by_iata_code.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.create_airport(data)

    assert exc.value.status_code == 409
    service.airport_repository.create.assert_not_called()


def test_get_airport_success(service):
    airport_id = uuid4()
    airport = MagicMock()
    service.airport_repository.get_by_id.return_value = airport

    result = service.get_airport(airport_id)

    assert result == airport
    service.airport_repository.get_by_id.assert_called_once_with(airport_id)


def test_get_airport_not_found(service):
    service.airport_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_airport(uuid4())

    assert exc.value.status_code == 404


def test_create_flight_success(service):
    departure_airport_id = uuid4()
    arrival_airport_id = uuid4()

    data = MagicMock()
    data.flight_number = "SU100"
    data.airline = "Aeroflot"
    data.departure_airport_id = departure_airport_id
    data.arrival_airport_id = arrival_airport_id
    data.departure_time = datetime(2026, 11, 12, 10, 0)
    data.arrival_time = datetime(2026, 11, 12, 12, 0)

    service.airport_repository.get_by_id.return_value = MagicMock()

    flight = MagicMock()
    service.flight_repository.create.return_value = flight

    result = service.create_flight(data)

    assert result == flight
    assert service.airport_repository.get_by_id.call_count == 2
    service.flight_repository.create.assert_called_once()


def test_create_flight_invalid_time(service):
    data = MagicMock()
    data.departure_time = datetime(2026, 11, 12, 12, 0)
    data.arrival_time = datetime(2026, 11, 12, 10, 0)

    with pytest.raises(HTTPException) as exc:
        service.create_flight(data)

    assert exc.value.status_code == 400
    service.flight_repository.create.assert_not_called()


def test_get_all_airports(service):
    airports = [MagicMock(), MagicMock()]
    service.airport_repository.get_all.return_value = airports

    result = service.get_all_airports()

    assert result == airports
    service.airport_repository.get_all.assert_called_once()


def test_get_flight_success(service):
    flight_id = uuid4()
    flight = MagicMock()
    service.flight_repository.get_by_id.return_value = flight

    result = service.get_flight(flight_id)

    assert result == flight
    service.flight_repository.get_by_id.assert_called_once_with(flight_id)


def test_get_flight_not_found(service):
    service.flight_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_flight(uuid4())

    assert exc.value.status_code == 404


def test_get_all_flights(service):
    flights = [MagicMock(), MagicMock()]
    service.flight_repository.get_all.return_value = flights

    result = service.get_all_flights()

    assert result == flights
    service.flight_repository.get_all.assert_called_once()
