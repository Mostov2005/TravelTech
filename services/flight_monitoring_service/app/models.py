import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class FlightMonitoring(Base):
    __tablename__ = "flight_monitoring"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    flight_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    status = Column(String(30), nullable=False, default="scheduled")

    last_checked_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    status_history = relationship(
        "FlightStatus",
        back_populates="monitoring",
        cascade="all, delete-orphan"
    )


class FlightStatus(Base):
    __tablename__ = "flight_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    monitoring_id = Column(
        UUID(as_uuid=True),
        ForeignKey("flight_monitoring.id"),
        nullable=False
    )

    status = Column(String(30), nullable=False)

    description = Column(String(500), nullable=True)

    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    monitoring = relationship(
        "FlightMonitoring",
        back_populates="status_history"
    )