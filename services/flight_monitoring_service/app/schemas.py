from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FlightMonitoringCreate(BaseModel):
    flight_id: UUID
    status: str = "scheduled"


class FlightMonitoringResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    flight_id: UUID
    status: str
    last_checked_at: datetime | None
    created_at: datetime


class FlightStatusCreate(BaseModel):
    status: str
    description: str | None = None


class FlightStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitoring_id: UUID
    status: str
    description: str | None
    recorded_at: datetime