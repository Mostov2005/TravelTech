from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import FlightMonitoring, FlightStatus
from repositories import (
    FlightMonitoringRepository,
    FlightStatusRepository
)
from schemas import FlightMonitoringCreate, FlightStatusCreate


class FlightMonitoringService:
    def __init__(self, db: Session):
        self.monitoring_repository = FlightMonitoringRepository(db)
        self.status_repository = FlightStatusRepository(db)

    def create_monitoring(self, data: FlightMonitoringCreate):
        existing = self.monitoring_repository.get_by_flight_id(data.flight_id)

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Monitoring for this flight already exists"
            )

        monitoring = FlightMonitoring(
            flight_id=data.flight_id,
            status=data.status
        )

        monitoring = self.monitoring_repository.create(monitoring)

        initial_status = FlightStatus(
            monitoring_id=monitoring.id,
            status=data.status,
            description="Initial flight status"
        )

        self.status_repository.create(initial_status)

        return monitoring

    def get_monitoring(self, monitoring_id: UUID):
        monitoring = self.monitoring_repository.get_by_id(monitoring_id)

        if not monitoring:
            raise HTTPException(
                status_code=404,
                detail="Flight monitoring not found"
            )

        return monitoring

    def get_all_monitorings(self):
        return self.monitoring_repository.get_all()

    def update_status(self, monitoring_id: UUID, data: FlightStatusCreate):
        monitoring = self.get_monitoring(monitoring_id)

        monitoring.status = data.status

        self.monitoring_repository.db.commit()
        self.monitoring_repository.db.refresh(monitoring)

        status = FlightStatus(
            monitoring_id=monitoring.id,
            status=data.status,
            description=data.description
        )

        self.status_repository.create(status)

        return monitoring

    def get_status_history(self, monitoring_id: UUID):
        self.get_monitoring(monitoring_id)

        return self.status_repository.get_by_monitoring_id(monitoring_id)