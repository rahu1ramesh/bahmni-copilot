import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from app.api.routes.patients import router
from app.core.emr_client import EMRClient
from app.schemas.patients import (
    Patient,
    Address,
    Period,
    CodeableConcept,
    ObservationResource,
    ConditionResource,
    AllergyIntoleranceResource,
)
from app.schemas.users import User
from app.schemas.departments import Department
from app.models.departments import Departments
from app.models.users import Users
from app.services.departments import DepartmentsService
from app.services.patients import PatientService
from app.services.auth import create_access_token


app = FastAPI()
app.include_router(router)

client = TestClient(app)


@pytest.fixture
def db_session():
    return Mock(spec=Session)


@pytest.fixture
def current_user():
    return {"department_id": 1}


@pytest.fixture
def emr_client_mock():
    return Mock(spec=EMRClient)


@pytest.fixture
def departments_service_mock():
    return Mock(spec=DepartmentsService)


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
def test_db():
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Users).delete()
        db.query(Departments).delete()
        db.commit()
        db.close()


@pytest.fixture
def admin_user(test_db: Session):
    department = Departments(name="Admin Department")
    test_db.add(department)
    test_db.commit()
    test_db.refresh(department)

    user_data = {
        "user_name": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword",
        "department_id": department.id,
        "is_admin": True,
    }
    user = Users(**user_data)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(admin_user):
    access_token = create_access_token(subject=admin_user.user_name)
    return {"Authorization": f"Bearer {access_token}"}


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


def test_user_without_department_access(patient_service, emr_client_mock, user, department):
    emr_client_mock.get_patient_data.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        user.department_id = 999
        patient_service.get_patient_context("patient123", user, department)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient not found"


def test_patient_with_no_data(patient_service, emr_client_mock, user, department):
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

    emr_client_mock.get_patient_data.return_value = patient
    emr_client_mock.get_observations.return_value = []
    emr_client_mock.get_conditions.return_value = []
    emr_client_mock.get_allergy_details.return_value = []

    with patch("app.utils.openai.OpenAIUtils.analyze_patient_context", return_value="No significant findings."):
        result = patient_service.get_patient_context("patient123", user, department)
        assert result == "No significant findings."


def test_ai_analysis_failure(patient_service, emr_client_mock, user, department):
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

    with patch("app.utils.openai.OpenAIUtils.analyze_patient_context", side_effect=Exception("AI analysis failed")):
        with pytest.raises(HTTPException) as exc_info:
            patient_service.get_patient_context("patient123", user, department)
        assert exc_info.value.status_code == 500
        assert "AI analysis failed" in exc_info.value.detail


def test_address_custom_mapper():
    data_with_extensions = {"extension": [{"extension": [{"valueString": "123 Main St"}, {"valueString": "Apt 4B"}]}]}
    address = Address(**data_with_extensions)
    assert address.line == ["123 Main St", "Apt 4B"]

    data_without_extensions = {"line": ["456 Elm St"]}
    address = Address(**data_without_extensions)
    assert address.line == ["456 Elm St"]

    data_with_other_fields = {
        "use": "home",
        "type": "postal",
        "text": "456 Elm St, Apt 4B",
        "city": "Springfield",
        "state": "IL",
        "postalCode": "62704",
        "country": "USA",
        "period": {"start": "2023-01-01", "end": "2023-12-31"},
    }
    address = Address(**data_with_other_fields)
    assert address.use == "home"
    assert address.type == "postal"
    assert address.text == "456 Elm St, Apt 4B"
    assert address.city == "Springfield"
    assert address.state == "IL"
    assert address.postalCode == "62704"
    assert address.country == "USA"
    assert address.period == Period(start="2023-01-01", end="2023-12-31")


def test_patient_custom_mapper():
    data_with_meta_and_identifier = {
        "id": "patient123",
        "identifier": [{"value": "12345"}],
        "active": True,
        "name": [{"text": "John Doe"}],
        "gender": "male",
        "birthDate": "2000-01-01",
        "deceasedBoolean": False,
        "address": [{"line": ["123 Main St"]}],
    }
    patient = Patient(**data_with_meta_and_identifier)
    assert patient.identifier == "12345"
    assert patient.name.text == "John Doe"
    assert patient.address[0].line == ["123 Main St"]

    data_without_meta_and_identifier = {
        "id": "patient123",
        "identifier": [{"value": "12345"}],
        "active": True,
        "name": {"text": "John Doe"},
        "gender": "male",
        "birthDate": "2000-01-01",
        "deceasedBoolean": False,
        "address": [{"line": ["123 Main St"]}],
    }
    patient = Patient(**data_without_meta_and_identifier)
    assert patient.identifier == "12345"
    assert patient.name.text == "John Doe"
    assert patient.address[0].line == ["123 Main St"]


def test_observation_resource_custom_mapper():
    data_with_category_and_code = {
        "id": "obs1",
        "status": "final",
        "category": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]},
        "subject": {"reference": "Patient/123"},
        "encounter": {"reference": "Encounter/456"},
        "effectiveDateTime": "2023-01-01T00:00:00Z",
        "issued": "2023-01-01T00:00:00Z",
        "valueQuantity": {"value": 120, "unit": "mmHg"},
        "referenceRange": [{"low": {"value": 90, "unit": "mmHg"}, "high": {"value": 120, "unit": "mmHg"}}],
    }
    observation = ObservationResource(**data_with_category_and_code)
    assert observation.category[0].code == "vital-signs"
    assert observation.code.coding[0].code == "85354-9"

    data_without_category_and_code = {
        "id": "obs2",
        "status": "preliminary",
        "subject": {"reference": "Patient/789"},
        "encounter": {"reference": "Encounter/101"},
        "effectiveDateTime": "2023-02-01T00:00:00Z",
        "issued": "2023-02-01T00:00:00Z",
        "valueQuantity": {"value": 80, "unit": "bpm"},
        "referenceRange": [{"low": {"value": 60, "unit": "bpm"}, "high": {"value": 100, "unit": "bpm"}}],
    }
    observation = ObservationResource(**data_without_category_and_code)
    assert observation.category is None
    assert observation.code == CodeableConcept(coding=None, text=None)


def test_get_patient_context(db_session, current_user, patient_service, departments_service_mock, auth_headers):
    with patch("app.api.routes.patients.get_db", return_value=db_session), patch(
        "app.api.routes.patients.get_current_user", return_value=current_user
    ), patch(
        "app.api.routes.patients.DepartmentsService.get_department_by_id", return_value=departments_service_mock
    ), patch(
        "app.api.routes.patients.patient_service.get_patient_context", return_value="Patient Summary"
    ):
        response = client.get("/patients/patient123", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == "Patient Summary"


def test_get_patient_context_not_found(
    db_session, current_user, patient_service, departments_service_mock, auth_headers
):
    with patch("app.api.routes.patients.get_db", return_value=db_session), patch(
        "app.api.routes.patients.get_current_user", return_value=current_user
    ), patch(
        "app.api.routes.patients.DepartmentsService.get_department_by_id", return_value=departments_service_mock
    ), patch(
        "app.api.routes.patients.patient_service.get_patient_context",
        side_effect=HTTPException(status_code=404, detail="Patient not found"),
    ):
        response = client.get("/patients/patient123", headers=auth_headers)
        assert response.status_code == 404
        assert response.json() == {"detail": "Patient not found"}


def test_get_patient_context_internal_server_exception(
    db_session, current_user, patient_service, departments_service_mock, auth_headers
):
    with patch("app.api.routes.patients.get_db", return_value=db_session), patch(
        "app.api.routes.patients.get_current_user", return_value=current_user
    ), patch(
        "app.api.routes.patients.DepartmentsService.get_department_by_id", return_value=departments_service_mock
    ), patch(
        "app.api.routes.patients.patient_service.get_patient_context",
        side_effect=HTTPException(status_code=500, detail="Internal Server Error"),
    ):
        response = client.get("/patients/patient123", headers=auth_headers)
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error"}
