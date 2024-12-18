import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.schemas.users import UserCreate
from app.services.users import UsersService
from app.models.users import Users
from app.models.departments import Departments
from app.services.auth import (
    JWT_SECRET_KEY,
    ALGORITHM,
    authenticate_user,
)
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

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
        db.query(Departments).delete()
        db.commit()
        db.close()


def test_sign_up(test_db: Session):
    user_data = {
        "user_name": "testuser",
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "specialty": "General Medicine",
        "department_id": 1,
    }
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]


@pytest.fixture
def default_user(test_db: Session):
    department = Departments(name="Admin Department")
    test_db.add(department)
    test_db.commit()
    test_db.refresh(department)

    user_data = UserCreate(
        user_name="testuser",
        name="Test User",
        email="testuser@example.com",
        password="testpassword",
        specialty="General Medicine",
        department_id=department.id,
    )
    UsersService.create_user(test_db, user_data)
    return user_data


def test_login(test_db: Session, default_user):
    login_data = {"username": default_user.user_name, "password": default_user.password}

    response = client.post(
        "/api/auth/login", data=login_data, headers={"content-type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_login_invalid_credentials(test_db: Session, default_user):
    login_data = {"username": default_user.user_name, "password": "wrongpassword"}
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_get_user_not_found(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(test_db, "nonexistentuser", "password")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User with username nonexistentuser not found"


def test_authenticate_user_not_found(test_db: Session):
    response = client.get("/api/users/nonexistentuser")
    assert response.status_code == 401


def test_authenticate_user_invalid_password(test_db: Session, default_user):
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(test_db, default_user.user_name, "wrongpassword")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"


def test_get_current_user_invalid_token(test_db: Session):
    invalid_token = "invalidtoken"
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user_no_sub(test_db: Session):
    payload = {"exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
