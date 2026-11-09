from uuid import UUID

from sqlalchemy.orm import Session

from models import DisruptionCase, RebookingProposal


class DisruptionCaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, case: DisruptionCase):
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get_by_id(self, case_id: UUID):
        return self.db.query(DisruptionCase).filter(
            DisruptionCase.id == case_id
        ).first()

    def get_all(self):
        return self.db.query(DisruptionCase).all()


class RebookingProposalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, proposal: RebookingProposal):
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def get_by_case(self, case_id: UUID):
        return self.db.query(RebookingProposal).filter(
            RebookingProposal.disruption_case_id == case_id
        ).all()

    def get_by_id(self, proposal_id: UUID):
        return self.db.query(RebookingProposal).filter(
            RebookingProposal.id == proposal_id
        ).first()