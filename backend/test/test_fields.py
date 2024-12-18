import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.schemas.forms import FormCreate
from app.schemas.fields import FieldCreate
from app.models.fields import Fields
from app.models.forms import Forms
from app.services.fields import FieldsService
from app.services.forms import FormsService
from app.models.departments import Departments
from app.models.users import Users
from app.services.auth import create_access_token

client = TestClient(app)


def override_get_db():
    from app.config.database import SessionLocal

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_db():
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Fields).delete()
        db.query(Forms).delete()
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
def create_form(test_db: Session):
    form_data = FormCreate(name="Test Form")
    form = FormsService.create_form(test_db, form_data)
    return form


def test_get_all_fields(test_db: Session, auth_headers, create_form):
    response = client.get("/api/fields/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_field_by_id(test_db: Session, auth_headers, create_form):
    field_data = FieldCreate(name="Test Field", form_id=create_form.id)
    field = FieldsService.create_field(test_db, field_data)
    response = client.get(f"/api/fields/{field.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == field_data.name


def test_field_not_found(test_db: Session, auth_headers, create_form):
    response = client.get(f"/api/fields/{20}", headers=auth_headers)
    assert response.status_code == 404


def test_get_fields_by_form_id(test_db: Session, auth_headers, create_form):
    field_data = FieldCreate(name="Test Field", form_id=create_form.id)
    FieldsService.create_field(test_db, field_data)
    response = client.get(f"/api/fields/form/{create_form.id}", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == field_data.name


def test_create_field(test_db: Session, auth_headers, create_form):
    field_data = {"name": "New Field", "form_id": create_form.id}
    response = client.post("/api/fields/", json=field_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == field_data["name"]


def test_update_field(test_db: Session, auth_headers, create_form):
    field_data = FieldCreate(name="Test Field", form_id=create_form.id)
    field = FieldsService.create_field(test_db, field_data)
    update_data = {"name": "Updated Field", "form_id": create_form.id}
    response = client.put(f"/api/fields/{field.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]


def test_update_field_not_found(test_db: Session, auth_headers, create_form):
    update_data = {"name": "Updated Field", "form_id": create_form.id}
    response = client.put(f"/api/fields/{20}", json=update_data, headers=auth_headers)
    assert response.status_code == 404


def test_delete_field(test_db: Session, auth_headers, create_form):
    field_data = FieldCreate(name="Test Field", form_id=create_form.id)
    field = FieldsService.create_field(test_db, field_data)
    response = client.delete(f"/api/fields/{field.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_field_not_found(test_db: Session, auth_headers, create_form):
    response = client.delete("/api/fields/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Field with id 999 not found"
