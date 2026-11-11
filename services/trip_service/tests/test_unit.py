from datetime import date
from uuid import uuid4
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from fastapi import HTTPException

import sys
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))

from app.services import TripService
from app.schemas import TripCreate, TripUpdate
from app.services import ItinerarySegmentService, BookingService
from app.schemas import ItinerarySegmentCreate, BookingCreate


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    trip_service = TripService(db)
    trip_service.repository = MagicMock()
    return trip_service


def test_create_trip_success(service):
    owner_id = uuid4()
    data = TripCreate(
        name="Поездка в Москву",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 10)
    )

    created_trip = MagicMock()
    created_trip.id = uuid4()
    created_trip.owner_id = owner_id
    created_trip.name = data.name

    service.repository.create.return_value = created_trip

    with patch("app.services.publish_message") as publish:
        result = service.create_trip(owner_id, data)

    assert result == created_trip
    service.repository.create.assert_called_once()
    publish.assert_called_once()


def test_create_trip_invalid_dates(service):
    owner_id = uuid4()
    data = TripCreate(
        name="Некорректная поездка",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 1)
    )

    with pytest.raises(HTTPException) as exc:
        service.create_trip(owner_id, data)

    assert exc.value.status_code == 400
    service.repository.create.assert_not_called()


def test_get_trip_success(service):
    trip_id = uuid4()
    expected_trip = MagicMock()

    service.repository.get_by_id.return_value = expected_trip

    result = service.get_trip(trip_id)

    assert result == expected_trip
    service.repository.get_by_id.assert_called_once_with(trip_id)


def test_get_trip_not_found(service):
    trip_id = uuid4()
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_trip(trip_id)

    assert exc.value.status_code == 404


def test_update_trip_invalid_dates(service):
    trip_id = uuid4()
    data = TripUpdate(
        name="Поездка",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 1)
    )

    service.repository.get_by_id.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.update_trip(trip_id, data)

    assert exc.value.status_code == 400
    service.repository.update.assert_not_called()


def test_delete_trip_not_found(service):
    trip_id = uuid4()
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.delete_trip(trip_id)

    assert exc.value.status_code == 404
    service.repository.delete.assert_not_called()


def test_update_trip_success(service):
    trip_id = uuid4()
    trip = MagicMock()

    data = TripUpdate(
        name="Поездка в Санкт-Петербург",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 10)
    )

    service.repository.get_by_id.return_value = trip
    service.repository.update.return_value = trip

    with patch("app.services.redis_client.delete") as cache_delete:
        result = service.update_trip(trip_id, data)

    assert result == trip
    assert trip.name == data.name
    assert trip.start_date == data.start_date
    assert trip.end_date == data.end_date
    service.repository.update.assert_called_once_with(trip)
    cache_delete.assert_called_once_with(f"trip:{trip_id}")


def test_delete_trip_success(service):
    trip_id = uuid4()
    trip = MagicMock()

    service.repository.get_by_id.return_value = trip

    with patch("app.services.redis_client.delete") as cache_delete:
        service.delete_trip(trip_id)

    service.repository.delete.assert_called_once_with(trip)
    cache_delete.assert_called_once_with(f"trip:{trip_id}")


@pytest.fixture
def segment_service(db):
    service = ItinerarySegmentService(db)
    service.repository = MagicMock()
    return service


@pytest.fixture
def booking_service(db):
    service = BookingService(db)
    service.repository = MagicMock()
    return service


def test_create_segment_success(segment_service, db):
    trip_id = uuid4()
    flight_id = uuid4()

    db.get.return_value = MagicMock()

    data = ItinerarySegmentCreate(
        flight_id=flight_id,
        departure_airport="SVO",
        arrival_airport="LED",
        departure_time=datetime(2026, 12, 1, 10, 0),
        arrival_time=datetime(2026, 12, 1, 12, 0),
        position=1
    )

    segment_service.repository.create.return_value = MagicMock()

    result = segment_service.create_segment(trip_id, data)

    assert result is not None
    db.get.assert_called_once()
    segment_service.repository.create.assert_called_once()


def test_create_segment_trip_not_found(segment_service, db):
    trip_id = uuid4()
    db.get.return_value = None

    data = ItinerarySegmentCreate(
        flight_id=uuid4(),
        departure_airport="SVO",
        arrival_airport="LED",
        departure_time=datetime(2026, 12, 1, 10, 0),
        arrival_time=datetime(2026, 12, 1, 12, 0),
        position=1
    )

    with pytest.raises(HTTPException) as exc:
        segment_service.create_segment(trip_id, data)

    assert exc.value.status_code == 404
    segment_service.repository.create.assert_not_called()


def test_create_segment_invalid_time(segment_service, db):
    trip_id = uuid4()
    db.get.return_value = MagicMock()

    data = ItinerarySegmentCreate(
        flight_id=uuid4(),
        departure_airport="SVO",
        arrival_airport="LED",
        departure_time=datetime(2026, 12, 1, 12, 0),
        arrival_time=datetime(2026, 12, 1, 10, 0),
        position=1
    )

    with pytest.raises(HTTPException) as exc:
        segment_service.create_segment(trip_id, data)

    assert exc.value.status_code == 400
    segment_service.repository.create.assert_not_called()


def test_delete_segment_not_found(segment_service):
    segment_id = uuid4()
    segment_service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        segment_service.delete_segment(segment_id)

    assert exc.value.status_code == 404
    segment_service.repository.delete.assert_not_called()


def test_delete_segment_success(segment_service):
    segment_id = uuid4()
    segment = MagicMock()
    segment_service.repository.get_by_id.return_value = segment

    segment_service.delete_segment(segment_id)

    segment_service.repository.delete.assert_called_once_with(segment)


def test_create_booking_success(booking_service, db):
    trip_id = uuid4()

    db.get.return_value = MagicMock()

    data = BookingCreate(
        flight_id=uuid4(),
        booking_reference="ABC123",
        ticket_number="TICKET123"
    )

    booking_service.repository.create.return_value = MagicMock()

    result = booking_service.create_booking(trip_id, data)

    assert result is not None
    db.get.assert_called_once()
    booking_service.repository.create.assert_called_once()


def test_create_booking_trip_not_found(booking_service, db):
    trip_id = uuid4()
    db.get.return_value = None

    data = BookingCreate(
        flight_id=uuid4(),
        booking_reference="ABC123",
        ticket_number="TICKET123"
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(trip_id, data)

    assert exc.value.status_code == 404
    booking_service.repository.create.assert_not_called()


def test_delete_booking_not_found(booking_service):
    booking_id = uuid4()
    booking_service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        booking_service.delete_booking(booking_id)

    assert exc.value.status_code == 404
    booking_service.repository.delete.assert_not_called()


def test_delete_booking_success(booking_service):
    booking_id = uuid4()
    booking = MagicMock()
    booking_service.repository.get_by_id.return_value = booking

    booking_service.delete_booking(booking_id)

    booking_service.repository.delete.assert_called_once_with(booking)


def test_get_trip_segments_success(segment_service, db):
    trip_id = uuid4()
    trip = MagicMock()
    segments = [MagicMock(), MagicMock()]

    db.get.return_value = trip
    segment_service.repository.get_by_trip.return_value = segments

    result = segment_service.get_trip_segments(trip_id)

    assert result == segments
    segment_service.repository.get_by_trip.assert_called_once_with(trip_id)


def test_get_trip_segments_trip_not_found(segment_service, db):
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        segment_service.get_trip_segments(uuid4())

    assert exc.value.status_code == 404
    segment_service.repository.get_by_trip.assert_not_called()


def test_get_trip_bookings_success(booking_service, db):
    trip_id = uuid4()
    trip = MagicMock()
    bookings = [MagicMock(), MagicMock()]

    db.get.return_value = trip
    booking_service.repository.get_by_trip.return_value = bookings

    result = booking_service.get_trip_bookings(trip_id)

    assert result == bookings
    booking_service.repository.get_by_trip.assert_called_once_with(trip_id)


def test_get_trip_bookings_trip_not_found(booking_service, db):
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        booking_service.get_trip_bookings(uuid4())

    assert exc.value.status_code == 404
    booking_service.repository.get_by_trip.assert_not_called()
