import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.schemas.users import UserCreate
from app.services.users import UsersService
from app.models.users import Users
from app.services.auth import (
    JWT_SECRET_KEY,
    ALGORITHM,
    authenticate_user,
    get_current_user,
    validate_refresh_token,
    JWT_REFRESH_SECRET_KEY,
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
        db.commit()
        db.close()


def test_sign_up(test_db: Session):

    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    user_data = {
        "user_name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.fixture
def default_user(test_db: Session):

    user_data = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword",
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


def test_refresh(test_db: Session, default_user):
    login_data = {"username": default_user.user_name, "password": default_user.password}
    response = client.post(
        "/api/auth/login", data=login_data, headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}, headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["refresh_token"] == refresh_token


def test_refresh_with_invalid_refresh_token(test_db: Session, default_user):
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": "refresh_token"}, headers={"accept": "application/json"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_get_user_not_found(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(test_db, "nonexistentuser", "password")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User with username nonexistentuser not found"


def test_get_user_not_found_with_invalid_user_id(test_db: Session):
    invalid_payloads = {"exp": datetime.utcnow() + timedelta(hours=1), "sub": "12"}
    invalid_token = jwt.encode(invalid_payloads, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        validate_refresh_token(
            test_db,
            invalid_token
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User with id 12 not found"


def test_authenticate_user_not_found(test_db: Session):
    response = client.get("/api/users/nonexistentuser")
    assert response.status_code == 401


def test_authenticate_user_invalid_password(test_db: Session, default_user):
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(test_db, default_user.user_name, "wrongpassword")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"


def test_authenticate_user_invalid_username(test_db: Session, default_user):
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(test_db, "wrongusername", "wrongpassword")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User with username wrongusername not found"


def test_get_current_user_invalid_token(test_db: Session):
    invalid_token = "invalidtoken"
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user_no_sub(test_db: Session):
    payload = {"exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(test_db, token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_invalid_refresh_token_payload(test_db: Session):
    invalid_payloads = {"exp": datetime.utcnow() + timedelta(hours=1), "sub": "12"}
    invalid_token = jwt.encode(invalid_payloads, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": invalid_token}, headers={"accept": "application/json"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User with id 12 not found"


def test_expired_refresh_token(test_db: Session):
    expired_payload = {
        "exp": datetime.utcnow(),
        "sub": "1",
    }
    expired_token = jwt.encode(expired_payload, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": expired_token}, headers={"accept": "application/json"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_missing_sub_in_refresh_token(test_db: Session):
    invalid_payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    invalid_token = jwt.encode(invalid_payload, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": invalid_token}, headers={"accept": "application/json"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"
