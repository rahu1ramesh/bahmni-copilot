import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.schemas.patients import (
    Patient,
    ObservationResource,
    ConditionResource,
    AllergyIntoleranceResource,
)
from app.schemas.users import User
from app.schemas.departments import Department
from app.services.patients import PatientService


@pytest.fixture
def emr_client_mock():
    return Mock()


@pytest.fixture
def patient_service(emr_client_mock):
    return PatientService(emr_client_mock)


@pytest.fixture
def user():
    return User(
        id=1,
        name="Test User",
        user_name="Test User",
        email="testuser@example.com",
        specialty="General",
        department_id=1,
        is_admin=False,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )


@pytest.fixture
def department():
    return Department(
        id=1, name="Test Department", created_at="2023-01-01T00:00:00Z", updated_at="2023-01-01T00:00:00Z"
    )


def test_get_patient_context_success(patient_service, emr_client_mock, user, department):
    patient = Patient(
        id="patient123",
        identifier=[{"value": "12345"}],
        active=True,
        name={"text": "John Doe"},
        gender="male",
        birthDate="2000-01-01",
        deceasedBoolean=False,
        address=[],
    )
    observations = [ObservationResource(id="obs1", code={"text": "Blood Pressure"})]
    conditions = [ConditionResource(id="cond1", code={"text": "Diabetes"})]
    allergies = [AllergyIntoleranceResource(id="allergy1", code={"text": "Peanut"})]

    emr_client_mock.get_patient_data.return_value = patient
    emr_client_mock.get_observations.return_value = observations
    emr_client_mock.get_conditions.return_value = conditions
    emr_client_mock.get_allergy_details.return_value = allergies

    with patch("app.utils.openai.OpenAIUtils.analyze_patient_context", return_value="Patient Diagnosis Summary"):
        result = patient_service.get_patient_context("patient123", user, department)
        assert result == "Patient Diagnosis Summary"


def test_get_patient_context_patient_not_found(patient_service, emr_client_mock, user, department):
    emr_client_mock.get_patient_data.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        patient_service.get_patient_context("patient123", user, department)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient not found"


def test_get_patient_context_internal_server_error(patient_service, emr_client_mock, user, department):
    emr_client_mock.get_patient_data.side_effect = Exception("Unexpected error")

    with pytest.raises(HTTPException) as exc_info:
        patient_service.get_patient_context("patient123", user, department)
    assert exc_info.value.status_code == 500
    assert "Internal Server Error" in exc_info.value.detail
