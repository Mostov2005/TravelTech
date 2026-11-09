from uuid import UUID

from sqlalchemy.orm import Session

from models import Airport, Flight


class AirportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, airport: Airport):
        self.db.add(airport)
        self.db.commit()
        self.db.refresh(airport)
        return airport

    def get_by_id(self, airport_id: UUID):
        return self.db.query(Airport).filter(
            Airport.id == airport_id
        ).first()

    def get_by_iata_code(self, iata_code: str):
        return self.db.query(Airport).filter(
            Airport.iata_code == iata_code
        ).first()

    def get_all(self):
        return self.db.query(Airport).all()


class FlightRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, flight: Flight):
        self.db.add(flight)
        self.db.commit()
        self.db.refresh(flight)
        return flight

    def get_by_id(self, flight_id: UUID):
        return self.db.query(Flight).filter(
            Flight.id == flight_id
        ).first()

    def get_all(self):
        return self.db.query(Flight).all()