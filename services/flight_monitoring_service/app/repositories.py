from uuid import UUID

from sqlalchemy.orm import Session

from models import FlightMonitoring, FlightStatus


class FlightMonitoringRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, monitoring: FlightMonitoring):
        self.db.add(monitoring)
        self.db.commit()
        self.db.refresh(monitoring)
        return monitoring

    def get_by_id(self, monitoring_id: UUID):
        return self.db.query(FlightMonitoring).filter(
            FlightMonitoring.id == monitoring_id
        ).first()

    def get_by_flight_id(self, flight_id: UUID):
        return self.db.query(FlightMonitoring).filter(
            FlightMonitoring.flight_id == flight_id
        ).first()

    def get_all(self):
        return self.db.query(FlightMonitoring).all()


class FlightStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, status: FlightStatus):
        self.db.add(status)
        self.db.commit()
        self.db.refresh(status)
        return status

    def get_by_monitoring_id(self, monitoring_id: UUID):
        return self.db.query(FlightStatus).filter(
            FlightStatus.monitoring_id == monitoring_id
        ).order_by(FlightStatus.recorded_at.desc()).all()