from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DisruptionCaseCreate(BaseModel):
    trip_id: UUID
    flight_id: UUID
    disruption_type: str
    description: str | None = None


class DisruptionCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    flight_id: UUID
    disruption_type: str
    description: str | None
    status: str
    created_at: datetime


class RebookingProposalCreate(BaseModel):
    alternative_flight_id: UUID
    description: str | None = None


class RebookingProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    disruption_case_id: UUID
    alternative_flight_id: UUID
    status: str
    description: str | None
    created_at: datetime


class RebookingSagaCreate(BaseModel):
    alternative_flight_id: UUID
    booking_reference: str
    ticket_number: str | None = None
    description: str | None = None
