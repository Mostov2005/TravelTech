from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TripCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime


class TripUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date


class ItinerarySegmentCreate(BaseModel):
    flight_id: UUID
    departure_airport: str = Field(min_length=3, max_length=3)
    arrival_airport: str = Field(min_length=3, max_length=3)
    departure_time: datetime
    arrival_time: datetime
    position: int = Field(ge=1)


class ItinerarySegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    flight_id: UUID
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    position: int


class BookingCreate(BaseModel):
    flight_id: UUID
    booking_reference: str = Field(min_length=1, max_length=50)
    ticket_number: str | None = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    flight_id: UUID
    booking_reference: str
    ticket_number: str | None
    status: str
    created_at: datetime
