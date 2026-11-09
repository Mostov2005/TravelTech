from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Airport, Flight
from repositories import AirportRepository, FlightRepository
from schemas import AirportCreate, FlightCreate


class FlightService:
    def __init__(self, db: Session):
        self.airport_repository = AirportRepository(db)
        self.flight_repository = FlightRepository(db)

    def create_airport(self, data: AirportCreate):
        if self.airport_repository.get_by_iata_code(data.iata_code):
            raise HTTPException(
                status_code=409,
                detail="Airport with this IATA code already exists"
            )

        airport = Airport(
            iata_code=data.iata_code.upper(),
            name=data.name,
            city=data.city,
            country=data.country
        )

        return self.airport_repository.create(airport)

    def get_airport(self, airport_id: UUID):
        airport = self.airport_repository.get_by_id(airport_id)

        if not airport:
            raise HTTPException(
                status_code=404,
                detail="Airport not found"
            )

        return airport

    def get_all_airports(self):
        return self.airport_repository.get_all()

    def create_flight(self, data: FlightCreate):
        if data.arrival_time <= data.departure_time:
            raise HTTPException(
                status_code=400,
                detail="Arrival time must be later than departure time"
            )

        self.get_airport(data.departure_airport_id)
        self.get_airport(data.arrival_airport_id)

        flight = Flight(
            flight_number=data.flight_number,
            airline=data.airline,
            departure_airport_id=data.departure_airport_id,
            arrival_airport_id=data.arrival_airport_id,
            departure_time=data.departure_time,
            arrival_time=data.arrival_time
        )

        return self.flight_repository.create(flight)

    def get_flight(self, flight_id: UUID):
        flight = self.flight_repository.get_by_id(flight_id)

        if not flight:
            raise HTTPException(
                status_code=404,
                detail="Flight not found"
            )

        return flight

    def get_all_flights(self):
        return self.flight_repository.get_all()