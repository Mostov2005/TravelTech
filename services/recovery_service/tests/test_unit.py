import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from uuid import uuid4

SERVICE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = SERVICE_DIR / "app"

sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(APP_DIR))

from app.services import RecoveryService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    recovery_service = RecoveryService(db)
    recovery_service.case_repository = MagicMock()
    recovery_service.proposal_repository = MagicMock()
    return recovery_service


def test_create_disruption_case_success(service):
    data = MagicMock()
    data.trip_id = uuid4()
    data.flight_id = uuid4()
    data.disruption_type = "cancellation"
    data.description = "Flight cancelled"

    created_case = MagicMock()
    service.case_repository.create.return_value = created_case

    result = service.create_disruption_case(data)

    assert result == created_case
    service.case_repository.create.assert_called_once()


def test_get_disruption_case_success(service):
    case_id = uuid4()
    case = MagicMock()
    service.case_repository.get_by_id.return_value = case

    result = service.get_disruption_case(case_id)

    assert result == case
    service.case_repository.get_by_id.assert_called_once_with(case_id)


def test_get_disruption_case_not_found(service):
    service.case_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_disruption_case(uuid4())

    assert exc.value.status_code == 404


def test_get_all_disruption_cases(service):
    cases = [MagicMock(), MagicMock()]
    service.case_repository.get_all.return_value = cases

    result = service.get_all_disruption_cases()

    assert result == cases
    service.case_repository.get_all.assert_called_once()


def test_create_rebooking_proposal_success(service):
    case_id = uuid4()
    data = MagicMock()
    data.alternative_flight_id = uuid4()
    data.description = "Alternative flight"

    service.case_repository.get_by_id.return_value = MagicMock()
    proposal = MagicMock()
    service.proposal_repository.create.return_value = proposal

    result = service.create_rebooking_proposal(case_id, data)

    assert result == proposal
    service.case_repository.get_by_id.assert_called_once_with(case_id)
    service.proposal_repository.create.assert_called_once()


def test_create_rebooking_proposal_case_not_found(service):
    case_id = uuid4()
    data = MagicMock()

    service.case_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.create_rebooking_proposal(case_id, data)

    assert exc.value.status_code == 404
    service.proposal_repository.create.assert_not_called()
