import json

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
from messaging import publish_message
from models import Booking, ItinerarySegment, Trip
from repositories import (
    BookingRepository,
    ItinerarySegmentRepository,
    TripRepository,
)
from schemas import (
    BookingCreate,
    ItinerarySegmentCreate,
    TripCreate,
    TripResponse,
    TripUpdate,
)

from cache import redis_client


class TripService:

    def __init__(self, db: Session):
        self.repository = TripRepository(db)

    def create_trip(self, owner_id: UUID, data: TripCreate) -> Trip:
        if data.end_date < data.start_date:
            raise HTTPException(
                status_code=400,
                detail="Дата окончания путешествия не может быть раньше даты начала"
            )

        trip = Trip(
            owner_id=owner_id,
            name=data.name,
            start_date=data.start_date,
            end_date=data.end_date
        )

        trip = self.repository.create(trip)

        publish_message(
            queue_name="trip_events",
            message={
                "event": "trip.created",
                "trip_id": str(trip.id),
                "owner_id": str(trip.owner_id),
                "trip_name": trip.name
            }
        )

        return trip

    def get_trip(self, trip_id: UUID) -> Trip:
        trip = self.repository.get_by_id(trip_id)

        if not trip:
            raise HTTPException(status_code=404, detail="Путешествие не найдено")

        return trip

    def get_trip_cached(self, trip_id: UUID) -> TripResponse:
        cache_key = f"trip:{trip_id}"

        cached_trip = redis_client.get(cache_key)

        if cached_trip:
            return TripResponse.model_validate_json(cached_trip)

        trip = self.get_trip(trip_id)
        trip_response = TripResponse.model_validate(trip)

        redis_client.setex(
            cache_key,
            300,
            trip_response.model_dump_json()
        )

        return trip_response

    def get_user_trips(self, owner_id: UUID):
        return self.repository.get_all_by_owner(owner_id)

    def delete_trip(self, trip_id: UUID):
        trip = self.get_trip(trip_id)
        self.repository.delete(trip)

        redis_client.delete(f"trip:{trip_id}")

    def update_trip(self, trip_id: UUID, data: TripUpdate) -> Trip:
        trip = self.get_trip(trip_id)

        if data.end_date < data.start_date:
            raise HTTPException(
                status_code=400,
                detail="Дата окончания путешествия не может быть раньше даты начала"
            )

        trip.name = data.name
        trip.start_date = data.start_date
        trip.end_date = data.end_date

        updated_trip = self.repository.update(trip)

        redis_client.delete(f"trip:{trip_id}")

        return updated_trip


class ItinerarySegmentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ItinerarySegmentRepository(db)

    def create_segment(
            self,
            trip_id: UUID,
            data: ItinerarySegmentCreate
    ) -> ItinerarySegment:
        trip = self.db.get(Trip, trip_id)

        if not trip:
            raise HTTPException(status_code=404, detail="Путешествие не найдено")

        if data.arrival_time <= data.departure_time:
            raise HTTPException(
                status_code=400,
                detail="Время прибытия должно быть позже времени отправления"
            )

        segment = ItinerarySegment(
            trip_id=trip_id,
            flight_id=data.flight_id,
            departure_airport=data.departure_airport,
            arrival_airport=data.arrival_airport,
            departure_time=data.departure_time,
            arrival_time=data.arrival_time,
            position=data.position
        )

        return self.repository.create(segment)

    def get_trip_segments(self, trip_id: UUID):
        trip = self.db.get(Trip, trip_id)

        if not trip:
            raise HTTPException(status_code=404, detail="Путешествие не найдено")

        return self.repository.get_by_trip(trip_id)

    def delete_segment(self, segment_id: UUID):
        segment = self.repository.get_by_id(segment_id)

        if not segment:
            raise HTTPException(status_code=404, detail="Сегмент не найден")

        self.repository.delete(segment)


class BookingService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BookingRepository(db)

    def create_booking(
            self,
            trip_id: UUID,
            data: BookingCreate
    ) -> Booking:
        trip = self.db.get(Trip, trip_id)

        if not trip:
            raise HTTPException(status_code=404, detail="Путешествие не найдено")

        booking = Booking(
            trip_id=trip_id,
            flight_id=data.flight_id,
            booking_reference=data.booking_reference,
            ticket_number=data.ticket_number
        )

        return self.repository.create(booking)

    def get_trip_bookings(self, trip_id: UUID):
        trip = self.db.get(Trip, trip_id)

        if not trip:
            raise HTTPException(status_code=404, detail="Путешествие не найдено")

        return self.repository.get_by_trip(trip_id)

    def delete_booking(self, booking_id: UUID):
        booking = self.repository.get_by_id(booking_id)

        if not booking:
            raise HTTPException(status_code=404, detail="Бронирование не найдено")

        self.repository.delete(booking)
