from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Booking, ItinerarySegment, Trip


class TripRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, trip: Trip) -> Trip:
        self.db.add(trip)
        self.db.flush()
        return trip

    def get_by_id(self, trip_id):
        return self.db.get(Trip, trip_id)

    def get_all_by_owner(self, owner_id):
        query = select(Trip).where(Trip.owner_id == owner_id)
        return self.db.scalars(query).all()

    def delete(self, trip: Trip):
        self.db.delete(trip)
        self.db.commit()

    def update(self, trip: Trip) -> Trip:
        self.db.commit()
        self.db.refresh(trip)
        return trip


class ItinerarySegmentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, segment: ItinerarySegment) -> ItinerarySegment:
        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)
        return segment

    def get_by_trip(self, trip_id):
        query = (
            select(ItinerarySegment)
            .where(ItinerarySegment.trip_id == trip_id)
            .order_by(ItinerarySegment.position)
        )
        return self.db.scalars(query).all()

    def get_by_id(self, segment_id):
        return self.db.get(ItinerarySegment, segment_id)

    def delete(self, segment: ItinerarySegment):
        self.db.delete(segment)
        self.db.commit()


class BookingRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_by_trip(self, trip_id):
        query = (
            select(Booking)
            .where(Booking.trip_id == trip_id)
            .order_by(Booking.created_at)
        )
        return self.db.scalars(query).all()

    def get_by_id(self, booking_id):
        return self.db.get(Booking, booking_id)

    def delete(self, booking: Booking):
        self.db.delete(booking)
        self.db.commit()
