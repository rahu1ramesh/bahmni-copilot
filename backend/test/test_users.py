import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.schemas.users import UserCreate
from app.models.users import Users
from app.services.auth import create_access_token
from app.services.users import UsersService

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
        db.query(Users).delete()
        db.commit()
        db.close()


@pytest.fixture
def admin_user(test_db: Session):
    user_data = {
        "user_name": "admin",
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
def non_admin_user(test_db: Session):
    user_data = {
        "user_name": "non-admin",
        "email": "non-admin@example.com",
        "password": "nonadminpassword",
        "is_admin": False,
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
def non_auth_headers(non_admin_user):
    access_token = create_access_token(subject=non_admin_user.user_name)
    return {"Authorization": f"Bearer {access_token}"}


def test_create_user(test_db: Session, auth_headers):
    user_data = {
        "user_name": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
    }
    response = client.post("/api/users/", json=user_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]


def test_create_user_with_existing_user_name(test_db: Session, auth_headers):
    user_data = {
        "user_name": "admin",
        "email": "newuser@example.com",
        "password": "newpassword",
    }
    response = client.post("/api/users/", json=user_data, headers=auth_headers)
    assert response.status_code == 409


def test_create_user_with_existing_email(test_db: Session, auth_headers):
    user_data = {
        "user_name": "newuser",
        "email": "admin@example.com",
        "password": "newpassword",
    }
    response = client.post("/api/users/", json=user_data, headers=auth_headers)
    assert response.status_code == 409


def test_create_user_missing_field(test_db: Session, auth_headers):
    user_data = {"name": "New User", "password": "newpassword"}
    response = client.post("/api/users/", json=user_data, headers=auth_headers)
    assert response.status_code == 422


def test_get_user_by_id(test_db: Session, auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user = UsersService.create_user(test_db, user_data)
    response = client.get(f"/api/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data.email


def test_get_user_by_id_not_found(test_db: Session, auth_headers):
    response = client.get("/api/users/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_user_by_email(test_db: Session, auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user = UsersService.create_user(test_db, user_data)
    response = client.get(f"/api/users/email/{user.email}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data.email


def test_get_user_by_email_not_found(test_db: Session, auth_headers):
    response = client.get("/api/users/email/nonexistent@example.com", headers=auth_headers)
    assert response.status_code == 404


def test_update_user(test_db: Session, auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user = UsersService.create_user(test_db, user_data)
    update_data = {"user_name": "testuser2", "email": "updateduser@example.com"}
    response = client.put(f"/api/users/{user.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == update_data["email"]


def test_update_user_by_non_admin_user(test_db: Session, non_auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user = UsersService.create_user(test_db, user_data)
    update_data = {"user_name": "testuser2", "email": "updateduser@example.com"}
    response = client.put(f"/api/users/{user.id}", json=update_data, headers=non_auth_headers)
    assert response.status_code == 403


def test_update_user_not_found(test_db: Session, auth_headers):
    update_data = {"user_name": "testuser2", "email": "updateduser@example.com"}
    response = client.put("/api/users/9999", json=update_data, headers=auth_headers)
    assert response.status_code == 404


def test_delete_user(test_db: Session, auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user = UsersService.create_user(test_db, user_data)
    response = client.delete(f"/api/users/{user.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_user_not_found(test_db: Session, auth_headers):
    response = client.delete("/api/users/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_all_users(test_db: Session, auth_headers):
    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    UsersService.create_user(test_db, user_data)
    response = client.get("/api/users/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
