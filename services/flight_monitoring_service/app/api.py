from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    FlightMonitoringCreate,
    FlightMonitoringResponse,
    FlightStatusCreate,
    FlightStatusResponse
)
from services import FlightMonitoringService
from auth import get_current_user

router = APIRouter(
    prefix="/monitoring",
    tags=["Flight Monitoring"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=FlightMonitoringResponse)
def create_monitoring(
    data: FlightMonitoringCreate,
    db: Session = Depends(get_db)
):
    service = FlightMonitoringService(db)
    return service.create_monitoring(data)


@router.get("/", response_model=list[FlightMonitoringResponse])
def get_monitorings(db: Session = Depends(get_db)):
    service = FlightMonitoringService(db)
    return service.get_all_monitorings()


@router.get("/{monitoring_id}", response_model=FlightMonitoringResponse)
def get_monitoring(
    monitoring_id: UUID,
    db: Session = Depends(get_db)
):
    service = FlightMonitoringService(db)
    return service.get_monitoring(monitoring_id)


@router.post("/{monitoring_id}/status", response_model=FlightMonitoringResponse)
def update_status(
    monitoring_id: UUID,
    data: FlightStatusCreate,
    db: Session = Depends(get_db)
):
    service = FlightMonitoringService(db)
    return service.update_status(monitoring_id, data)


@router.get("/{monitoring_id}/history", response_model=list[FlightStatusResponse])
def get_status_history(
    monitoring_id: UUID,
    db: Session = Depends(get_db)
):
    service = FlightMonitoringService(db)
    return service.get_status_history(monitoring_id)