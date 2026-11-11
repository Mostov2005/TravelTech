from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    DisruptionCaseCreate,
    DisruptionCaseResponse,
    RebookingProposalCreate,
    RebookingProposalResponse,
    RebookingSagaCreate
)
from services import RecoveryService
from fastapi.security import HTTPAuthorizationCredentials
from auth import get_current_user, security

router = APIRouter(
    prefix="/recovery",
    tags=["Recovery"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/cases", response_model=DisruptionCaseResponse)
def create_disruption_case(
        data: DisruptionCaseCreate,
        db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    return service.create_disruption_case(data)


@router.get("/cases", response_model=list[DisruptionCaseResponse])
def get_disruption_cases(db: Session = Depends(get_db)):
    service = RecoveryService(db)
    return service.get_all_disruption_cases()


@router.get("/cases/{case_id}", response_model=DisruptionCaseResponse)
def get_disruption_case(
        case_id: UUID,
        db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    return service.get_disruption_case(case_id)


@router.post(
    "/cases/{case_id}/proposals",
    response_model=RebookingProposalResponse
)
def create_rebooking_proposal(
        case_id: UUID,
        data: RebookingProposalCreate,
        db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    return service.create_rebooking_proposal(case_id, data)


@router.get(
    "/cases/{case_id}/proposals",
    response_model=list[RebookingProposalResponse]
)
def get_rebooking_proposals(
        case_id: UUID,
        db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    return service.get_proposals_by_case(case_id)


@router.post("/cases/{case_id}/rebooking")
def execute_rebooking_saga(
        case_id: UUID,
        data: RebookingSagaCreate,
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    service = RecoveryService(db)
    return service.execute_rebooking_saga(
        case_id,
        data,
        credentials.credentials
    )
