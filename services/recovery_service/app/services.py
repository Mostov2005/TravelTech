import os

import httpx
from dotenv import load_dotenv
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import DisruptionCase, RebookingProposal
from repositories import DisruptionCaseRepository, RebookingProposalRepository
from schemas import (
    DisruptionCaseCreate,
    RebookingProposalCreate,
    RebookingSagaCreate
)

load_dotenv()

TRIP_SERVICE_URL = os.getenv(
    "TRIP_SERVICE_URL",
    "http://localhost:8000"
)


class RecoveryService:
    def __init__(self, db: Session):
        self.case_repository = DisruptionCaseRepository(db)
        self.proposal_repository = RebookingProposalRepository(db)

    def create_disruption_case(self, data: DisruptionCaseCreate):
        case = DisruptionCase(
            trip_id=data.trip_id,
            flight_id=data.flight_id,
            disruption_type=data.disruption_type,
            description=data.description
        )

        return self.case_repository.create(case)

    def get_disruption_case(self, case_id: UUID):
        case = self.case_repository.get_by_id(case_id)

        if not case:
            raise HTTPException(
                status_code=404,
                detail="Disruption case not found"
            )

        return case

    def get_all_disruption_cases(self):
        return self.case_repository.get_all()

    def create_rebooking_proposal(
            self,
            case_id: UUID,
            data: RebookingProposalCreate
    ):
        self.get_disruption_case(case_id)

        proposal = RebookingProposal(
            disruption_case_id=case_id,
            alternative_flight_id=data.alternative_flight_id,
            description=data.description
        )

        return self.proposal_repository.create(proposal)

    def get_proposals_by_case(self, case_id: UUID):
        self.get_disruption_case(case_id)
        return self.proposal_repository.get_by_case(case_id)

    def create_trip_booking(
            self,
            trip_id: UUID,
            flight_id: UUID,
            booking_reference: str,
            ticket_number: str | None = None
    ):
        response = httpx.post(
            f"{TRIP_SERVICE_URL}/trips/{trip_id}/bookings",
            json={
                "flight_id": str(flight_id),
                "booking_reference": booking_reference,
                "ticket_number": ticket_number
            },
            timeout=10.0
        )

        response.raise_for_status()
        return response.json()

    def delete_trip_booking(self, booking_id: UUID):
        response = httpx.delete(
            f"{TRIP_SERVICE_URL}/trips/bookings/{booking_id}",
            timeout=10.0
        )

        response.raise_for_status()

    def execute_rebooking_saga(
            self,
            case_id: UUID,
            data: RebookingSagaCreate
    ):
        case = self.get_disruption_case(case_id)

        booking = self.create_trip_booking(
            trip_id=case.trip_id,
            flight_id=data.alternative_flight_id,
            booking_reference=data.booking_reference,
            ticket_number=data.ticket_number
        )

        try:
            proposal = RebookingProposal(
                disruption_case_id=case_id,
                alternative_flight_id=data.alternative_flight_id,
                description=data.description
            )

            proposal = self.proposal_repository.create(proposal)

            return {
                "status": "completed",
                "booking": booking,
                "proposal": proposal
            }

        except Exception:
            self.delete_trip_booking(UUID(booking["id"]))
            raise
