import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Airport(Base):
    __tablename__ = "airports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iata_code = Column(String(3), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)

    departures = relationship(
        "Flight",
        foreign_keys="Flight.departure_airport_id",
        back_populates="departure_airport"
    )

    arrivals = relationship(
        "Flight",
        foreign_keys="Flight.arrival_airport_id",
        back_populates="arrival_airport"
    )


class Flight(Base):
    __tablename__ = "flights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number = Column(String(20), nullable=False)
    airline = Column(String(100), nullable=False)

    departure_airport_id = Column(
        UUID(as_uuid=True),
        ForeignKey("airports.id"),
        nullable=False
    )

    arrival_airport_id = Column(
        UUID(as_uuid=True),
        ForeignKey("airports.id"),
        nullable=False
    )

    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    departure_airport = relationship(
        "Airport",
        foreign_keys=[departure_airport_id],
        back_populates="departures"
    )

    arrival_airport = relationship(
        "Airport",
        foreign_keys=[arrival_airport_id],
        back_populates="arrivals"
    )