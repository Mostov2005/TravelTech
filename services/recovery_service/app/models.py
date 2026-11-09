import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class DisruptionCase(Base):
    __tablename__ = "disruption_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), nullable=False)
    flight_id = Column(UUID(as_uuid=True), nullable=False)
    disruption_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="open", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    proposals = relationship(
        "RebookingProposal",
        back_populates="disruption_case",
        cascade="all, delete-orphan"
    )


class RebookingProposal(Base):
    __tablename__ = "rebooking_proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disruption_case_id = Column(
        UUID(as_uuid=True),
        ForeignKey("disruption_cases.id", ondelete="CASCADE"),
        nullable=False
    )
    alternative_flight_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(30), default="pending", nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    disruption_case = relationship(
        "DisruptionCase",
        back_populates="proposals"
    )