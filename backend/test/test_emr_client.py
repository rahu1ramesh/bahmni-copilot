import pytest
from fastapi import HTTPException
from app.core.emr_client import EMRClient
import requests


@pytest.fixture
def emr_client():
    return EMRClient()


def test_get_patient_data_success(requests_mock, emr_client):
    patient_id = "123"
    mock_response = {
        "id": patient_id,
        "name": [{"given": ["John"], "family": "Doe"}],
        "gender": "male",
        "birthDate": "1980-01-01",
        "identifier": [{"value": "12345"}],
        "active": True,
        "deceasedBoolean": False,
        "address": [],
    }
    requests_mock.get(f"{emr_client.base_url}/Patient/{patient_id}", json=mock_response)

    patient = emr_client.get_patient_data(patient_id)
    assert patient.patient_id == patient_id
    assert patient.name.given == ["John"]
    assert patient.name.family == "Doe"


def test_get_patient_data_not_found(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(f"{emr_client.base_url}/Patient/{patient_id}", status_code=404, text="Resource not found")

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_patient_data(patient_id)
    assert exc_info.value.status_code == 404
    assert "Resource not found" in exc_info.value.detail


def test_get_observations_success(requests_mock, emr_client):
    patient_id = "123"
    mock_response = {
        "entry": [
            {"resource": {"id": "obs1", "status": "final", "code": {"text": "Blood Pressure"}}},
            {"resource": {"id": "obs2", "status": "final", "code": {"text": "Heart Rate"}}},
        ]
    }
    requests_mock.get(f"{emr_client.base_url}/Observation?subject:Patient={patient_id}", json=mock_response)

    observations = emr_client.get_observations(patient_id)
    assert len(observations) == 2
    assert observations[0].id == "obs1"
    assert observations[1].id == "obs2"


def test_get_observations_not_found(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(
        f"{emr_client.base_url}/Observation?subject:Patient={patient_id}", status_code=404, text="Resource not found"
    )

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_observations(patient_id)
    assert exc_info.value.status_code == 404
    assert "Resource not found" in exc_info.value.detail


def test_get_conditions_success(requests_mock, emr_client):
    patient_id = "123"
    mock_response = {
        "entry": [
            {"resource": {"id": "cond1", "code": {"text": "Diabetes"}}},
            {"resource": {"id": "cond2", "code": {"text": "Hypertension"}}},
        ]
    }
    requests_mock.get(f"{emr_client.base_url}/Condition?patient={patient_id}", json=mock_response)

    conditions = emr_client.get_conditions(patient_id)
    assert len(conditions) == 2
    assert conditions[0].id == "cond1"
    assert conditions[1].id == "cond2"


def test_get_conditions_not_found(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(
        f"{emr_client.base_url}/Condition?patient={patient_id}", status_code=404, text="Resource not found"
    )

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_conditions(patient_id)
    assert exc_info.value.status_code == 404
    assert "Resource not found" in exc_info.value.detail


def test_get_allergy_details_success(requests_mock, emr_client):
    patient_id = "123"
    mock_response = {
        "entry": [
            {"resource": {"id": "allergy1", "code": {"text": "Peanut"}}},
            {"resource": {"id": "allergy2", "code": {"text": "Shellfish"}}},
        ]
    }
    requests_mock.get(f"{emr_client.base_url}/AllergyIntolerance?patient={patient_id}", json=mock_response)

    allergies = emr_client.get_allergy_details(patient_id)
    assert len(allergies) == 2
    assert allergies[0].id == "allergy1"
    assert allergies[1].id == "allergy2"


def test_get_allergy_details_not_found(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(
        f"{emr_client.base_url}/AllergyIntolerance?patient={patient_id}", status_code=404, text="Resource not found"
    )

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_allergy_details(patient_id)
    assert exc_info.value.status_code == 404
    assert "Resource not found" in exc_info.value.detail


def test_fetch_http_error(requests_mock, emr_client):
    endpoint = "Patient/123"
    requests_mock.get(
        f"{emr_client.base_url}/{endpoint}", status_code=500, text="HTTP error occurred: 500 Server Error"
    )

    with pytest.raises(HTTPException) as exc_info:
        emr_client._fetch(endpoint)
    assert exc_info.value.status_code == 500
    assert "HTTP error occurred: 500 Server Error" in exc_info.value.detail


def test_fetch_authentication_error(requests_mock, emr_client):
    endpoint = "Patient/123"
    requests_mock.get(
        f"{emr_client.base_url}/{endpoint}", status_code=401, text="Failed to authenticate with EMR service"
    )

    with pytest.raises(HTTPException) as exc_info:
        emr_client._fetch(endpoint)
    assert exc_info.value.status_code == 401
    assert "Failed to authenticate with EMR service" in exc_info.value.detail


def test_fetch_request_exception(requests_mock, emr_client):
    endpoint = "Patient/123"
    requests_mock.get(f"{emr_client.base_url}/{endpoint}", exc=requests.exceptions.RequestException("Request failed"))

    with pytest.raises(HTTPException) as exc_info:
        emr_client._fetch(endpoint)
    assert exc_info.value.status_code == 500
    assert "Error occurred while fetching data: Request failed" in exc_info.value.detail


def test_get_patient_data_not_found_exception(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(f"{emr_client.base_url}/Patient/{patient_id}", json={})

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_patient_data(patient_id)
    assert exc_info.value.status_code == 404
    assert f"Patient with ID {patient_id} not found" in exc_info.value.detail


def test_get_observations_not_found_exception(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(f"{emr_client.base_url}/Observation?subject:Patient={patient_id}", json={})

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_observations(patient_id)
    assert exc_info.value.status_code == 404
    assert f"Observations for patient with ID {patient_id} not found" in exc_info.value.detail


def test_get_conditions_not_found_exception(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(f"{emr_client.base_url}/Condition?patient={patient_id}", json={})

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_conditions(patient_id)
    assert exc_info.value.status_code == 404
    assert f"Conditions for patient with ID {patient_id} not found" in exc_info.value.detail


def test_get_allergy_details_not_found_exception(requests_mock, emr_client):
    patient_id = "123"
    requests_mock.get(f"{emr_client.base_url}/AllergyIntolerance?patient={patient_id}", json={})

    with pytest.raises(HTTPException) as exc_info:
        emr_client.get_allergy_details(patient_id)
    assert exc_info.value.status_code == 404
    assert f"Allergy details for patient with ID {patient_id} not found" in exc_info.value.detail
