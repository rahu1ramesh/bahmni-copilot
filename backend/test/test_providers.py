import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.providers import Providers
from app.models.users import Users
from app.models.departments import Departments
from app.services.auth import create_access_token

client = TestClient(app)


@pytest.fixture
def db_session():
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Providers).delete()
        db.query(Users).delete()
        db.query(Departments).delete()
        db.commit()
        db.close()


@pytest.fixture
def admin_user(db_session: Session):

    user_data = {
        "user_name": "admin",
        "email": "admin@example.com",
        "password": "adminpassword",
        "is_admin": True,
    }
    user = Users(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    department_data = {
        "name": "Test Department",
    }
    department = Departments(**department_data)
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)

    return user


@pytest.fixture
def auth_headers(admin_user):
    access_token = create_access_token(subject=admin_user.user_name)
    return {"Authorization": f"Bearer {access_token}"}


def test_create_provider_success(db_session: Session, auth_headers):
    provider_data = {"user_id": 1, "name": "Test Provider", "specialty": "Cardiology", "department_id": 1}
    response = client.post("/api/providers/", json=provider_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Provider"


def test_create_provider_missing_fields(db_session: Session, auth_headers):
    provider_data = {"user_id": 1, "name": "Test Provider"}
    response = client.post("/api/providers/", json=provider_data, headers=auth_headers)
    assert response.status_code == 422


def test_create_provider_non_existent_user(db_session: Session, auth_headers):
    provider_data = {"user_id": 999, "name": "Test Provider", "specialty": "Cardiology", "department_id": 999}
    response = client.post("/api/providers/", json=provider_data, headers=auth_headers)
    assert response.status_code == 404


def test_create_provider_non_existent_department(db_session: Session, auth_headers):
    provider_data = {"user_id": 1, "name": "Test Provider", "specialty": "Cardiology", "department_id": 999}
    response = client.post("/api/providers/", json=provider_data, headers=auth_headers)
    assert response.status_code == 404


def test_get_provider_success(db_session: Session, auth_headers):
    provider = Providers(id=1, user_id=1, name="Test Provider", specialty="Cardiology", department_id=1)
    db_session.add(provider)
    db_session.commit()

    response = client.get("/api/providers/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Provider"


def test_get_provider_by_user_id_success(db_session: Session, auth_headers):
    provider = Providers(id=1, user_id=1, name="Test Provider", specialty="Cardiology", department_id=1)
    db_session.add(provider)
    db_session.commit()

    response = client.get("/api/providers/user/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Provider"


def test_get_provider_by_user_id_failure(db_session: Session, auth_headers):
    provider = Providers(id=1, user_id=1, name="Test Provider", specialty="Cardiology", department_id=1)
    db_session.add(provider)
    db_session.commit()

    response = client.get("/api/providers/user/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Provider with user id 999 not found"


def test_get_provider_not_found(db_session: Session, auth_headers):
    response = client.get("/api/providers/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_provider_success(db_session: Session, auth_headers):
    provider = Providers(id=1, user_id=1, name="Test Provider", specialty="Cardiology", department_id=1)
    db_session.add(provider)
    db_session.commit()

    update_data = {"name": "Updated Provider", "specialty": "Neurology"}
    response = client.put("/api/providers/1", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Provider"


def test_update_provider_not_found(db_session: Session, auth_headers):
    update_data = {"name": "Updated Provider", "specialty": "Neurology"}
    response = client.put("/api/providers/999", json=update_data, headers=auth_headers)
    assert response.status_code == 404


def test_delete_provider_success(db_session: Session, auth_headers):
    provider = Providers(id=1, user_id=1, name="Test Provider", specialty="Cardiology", department_id=1)
    db_session.add(provider)
    db_session.commit()

    response = client.delete("/api/providers/1", headers=auth_headers)
    assert response.status_code == 204


def test_delete_provider_not_found(db_session: Session, auth_headers):
    response = client.delete("/api/providers/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_all_providers_success(db_session: Session, auth_headers):
    provider1 = Providers(id=1, user_id=1, name="Test Provider 1", specialty="Cardiology", department_id=1)
    provider2 = Providers(id=2, user_id=1, name="Test Provider 2", specialty="Cardiology", department_id=1)
    db_session.add(provider1)
    db_session.add(provider2)
    db_session.commit()

    response = client.get("/api/providers/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
