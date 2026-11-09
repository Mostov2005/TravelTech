from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AirportCreate(BaseModel):
    iata_code: str
    name: str
    city: str
    country: str


class AirportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    iata_code: str
    name: str
    city: str
    country: str


class FlightCreate(BaseModel):
    flight_number: str
    airline: str
    departure_airport_id: UUID
    arrival_airport_id: UUID
    departure_time: datetime
    arrival_time: datetime


class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    flight_number: str
    airline: str
    departure_airport_id: UUID
    arrival_airport_id: UUID
    departure_time: datetime
    arrival_time: datetime
    created_at: datetime