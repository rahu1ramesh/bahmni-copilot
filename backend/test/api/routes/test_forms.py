import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.models.forms import Forms
from app.models.users import Users
from app.schemas.forms import FormCreate
from app.services.forms import FormsService
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
        db.query(Forms).delete()
        db.query(Users).delete()
        db.commit()
        db.close()


@pytest.fixture
def admin_user(test_db: Session):
    user_data = {
        "user_name": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword",
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


def test_get_all_forms(test_db: Session, auth_headers):
    response = client.get("/api/forms/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_form_by_id(test_db: Session, auth_headers):
    form_data = FormCreate(name="Test Form")
    form = FormsService.create_form(test_db, form_data)
    response = client.get(f"/api/forms/{form.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == form_data.name


def test_create_form(test_db: Session, auth_headers):
    form_data = {"name": "New Form", "prompt": "Test Prompt"}
    response = client.post("/api/forms/", json=form_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == form_data["name"]


def test_update_form(test_db: Session, auth_headers):
    form_data = FormCreate(name="Test Form")
    form = FormsService.create_form(test_db, form_data)
    update_data = {"name": "Updated Form", "prompt": "Updated Prompt"}
    response = client.put(f"/api/forms/{form.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]


def test_delete_form(test_db: Session, auth_headers):
    form_data = FormCreate(name="Test Form")
    form = FormsService.create_form(test_db, form_data)
    response = client.delete(f"/api/forms/{form.id}", headers=auth_headers)
    assert response.status_code == 204
