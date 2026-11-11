import importlib.util
import sys
import os

os.environ["SECRET_KEY"] = "traveltech_identity_secret_key_2026"
os.environ["ALGORITHM"] = "HS256"

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from jose import jwt

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))
sys.modules.pop("services", None)

spec = importlib.util.spec_from_file_location(
    "trip_service_main",
    APP_DIR / "main.py"
)
trip_service_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trip_service_main)

app = trip_service_main.app
client = TestClient(app)
SECRET_KEY = "traveltech_identity_secret_key_2026"
ALGORITHM = "HS256"


def get_auth_headers(owner_id):
    token = jwt.encode(
        {
            "sub": str(owner_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"Authorization": f"Bearer {token}"}


def test_trip_full_lifecycle():
    owner_id = str(uuid4())
    client.headers.update(get_auth_headers(owner_id))

    # Создание поездки
    create_response = client.post(
        "/trips/",
        params={"owner_id": owner_id},
        json={
            "name": "Integration Test Trip",
            "start_date": "2026-12-01",
            "end_date": "2026-12-10"
        }
    )

    assert create_response.status_code == 201

    trip = create_response.json()
    trip_id = trip["id"]

    assert trip["name"] == "Integration Test Trip"
    assert trip["owner_id"] == owner_id

    # Получение поездки
    get_response = client.get(f"/trips/{trip_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == trip_id

    # Удаление поездки
    delete_response = client.delete(f"/trips/{trip_id}")

    assert delete_response.status_code == 204

    # Проверка удаления
    get_deleted_response = client.get(f"/trips/{trip_id}")

    assert get_deleted_response.status_code == 404


def test_trip_segment_lifecycle():
    owner_id = str(uuid4())
    client.headers.update(get_auth_headers(owner_id))

    # Создание поездки
    trip_response = client.post(
        "/trips/",
        params={"owner_id": owner_id},
        json={
            "name": "Trip with Segment",
            "start_date": "2026-12-01",
            "end_date": "2026-12-10"
        }
    )

    assert trip_response.status_code == 201
    trip_id = trip_response.json()["id"]

    # Создание сегмента маршрута
    segment_response = client.post(
        f"/trips/{trip_id}/segments",
        json={
            "flight_id": str(uuid4()),
            "departure_airport": "SVO",
            "arrival_airport": "LED",
            "departure_time": "2026-12-01T10:00:00",
            "arrival_time": "2026-12-01T12:00:00",
            "position": 1
        }
    )

    assert segment_response.status_code == 201
    segment = segment_response.json()

    assert segment["trip_id"] == trip_id
    assert segment["departure_airport"] == "SVO"
    assert segment["arrival_airport"] == "LED"

    # Получение сегментов поездки
    segments_response = client.get(
        f"/trips/{trip_id}/segments"
    )

    assert segments_response.status_code == 200
    assert len(segments_response.json()) == 1
    assert segments_response.json()[0]["id"] == segment["id"]

    # Удаление поездки
    delete_response = client.delete(f"/trips/{trip_id}")
    assert delete_response.status_code == 204


def test_booking_lifecycle():
    owner_id = str(uuid4())
    client.headers.update(get_auth_headers(owner_id))

    # Создание поездки
    trip_response = client.post(
        "/trips/",
        params={"owner_id": owner_id},
        json={
            "name": "Trip with Booking",
            "start_date": "2026-12-01",
            "end_date": "2026-12-10"
        }
    )

    assert trip_response.status_code == 201
    trip_id = trip_response.json()["id"]

    # Создание бронирования
    booking_response = client.post(
        f"/trips/{trip_id}/bookings",
        json={
            "flight_id": str(uuid4()),
            "booking_reference": "TEST123",
            "ticket_number": "TICKET456"
        }
    )

    assert booking_response.status_code == 201
    booking = booking_response.json()

    assert booking["trip_id"] == trip_id
    assert booking["booking_reference"] == "TEST123"

    # Получение бронирований
    bookings_response = client.get(
        f"/trips/{trip_id}/bookings"
    )

    assert bookings_response.status_code == 200
    assert len(bookings_response.json()) == 1

    # Удаление бронирования
    delete_response = client.delete(
        f"/trips/bookings/{booking['id']}"
    )

    assert delete_response.status_code == 204
