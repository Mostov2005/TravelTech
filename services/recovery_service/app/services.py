from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import DisruptionCase, RebookingProposal
from repositories import DisruptionCaseRepository, RebookingProposalRepository
from schemas import DisruptionCaseCreate, RebookingProposalCreate


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