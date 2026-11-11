from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    AirportCreate,
    AirportResponse,
    FlightCreate,
    FlightResponse
)
from services import FlightService
from auth import get_current_user

router = APIRouter(
    prefix="/flights",
    tags=["Flights"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/airports", response_model=AirportResponse)
def create_airport(
    data: AirportCreate,
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.create_airport(data)


@router.get("/airports", response_model=list[AirportResponse])
def get_airports(db: Session = Depends(get_db)):
    service = FlightService(db)
    return service.get_all_airports()


@router.get("/airports/{airport_id}", response_model=AirportResponse)
def get_airport(
    airport_id: UUID,
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.get_airport(airport_id)


@router.post("/", response_model=FlightResponse)
def create_flight(
    data: FlightCreate,
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.create_flight(data)


@router.get("/", response_model=list[FlightResponse])
def get_flights(db: Session = Depends(get_db)):
    service = FlightService(db)
    return service.get_all_flights()


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(
    flight_id: UUID,
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.get_flight(flight_id)