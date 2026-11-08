from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import TripCreate, TripResponse
from services import ItinerarySegmentService, TripService, BookingService
from schemas import (
    ItinerarySegmentCreate,
    ItinerarySegmentResponse,
    TripCreate,
    TripResponse,
    TripUpdate,
    BookingCreate,
    BookingResponse,
)

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripResponse, status_code=201)
def create_trip(
        data: TripCreate,
        owner_id: UUID,
        db: Session = Depends(get_db)
):
    service = TripService(db)
    return service.create_trip(owner_id, data)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
        trip_id: UUID,
        db: Session = Depends(get_db)
):
    service = TripService(db)
    return service.get_trip_cached(trip_id)

@router.get("/", response_model=list[TripResponse])
def get_user_trips(
        owner_id: UUID,
        db: Session = Depends(get_db)
):
    service = TripService(db)
    return service.get_user_trips(owner_id)


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
        trip_id: UUID,
        data: TripUpdate,
        db: Session = Depends(get_db)
):
    service = TripService(db)
    return service.update_trip(trip_id, data)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
        trip_id: UUID,
        db: Session = Depends(get_db)
):
    service = TripService(db)
    service.delete_trip(trip_id)


@router.post(
    "/{trip_id}/segments",
    response_model=ItinerarySegmentResponse,
    status_code=201
)
def create_segment(
        trip_id: UUID,
        data: ItinerarySegmentCreate,
        db: Session = Depends(get_db)
):
    service = ItinerarySegmentService(db)
    return service.create_segment(trip_id, data)


@router.get(
    "/{trip_id}/segments",
    response_model=list[ItinerarySegmentResponse]
)
def get_trip_segments(
        trip_id: UUID,
        db: Session = Depends(get_db)
):
    service = ItinerarySegmentService(db)
    return service.get_trip_segments(trip_id)


@router.delete("/segments/{segment_id}", status_code=204)
def delete_segment(
        segment_id: UUID,
        db: Session = Depends(get_db)
):
    service = ItinerarySegmentService(db)
    service.delete_segment(segment_id)


@router.post(
    "/{trip_id}/bookings",
    response_model=BookingResponse,
    status_code=201
)
def create_booking(
        trip_id: UUID,
        data: BookingCreate,
        db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.create_booking(trip_id, data)


@router.get(
    "/{trip_id}/bookings",
    response_model=list[BookingResponse]
)
def get_trip_bookings(
        trip_id: UUID,
        db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.get_trip_bookings(trip_id)


@router.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(
        booking_id: UUID,
        db: Session = Depends(get_db)
):
    service = BookingService(db)
    service.delete_booking(booking_id)
