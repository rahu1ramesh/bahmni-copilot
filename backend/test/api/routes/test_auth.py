import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config.database import get_db
from app.schemas.users import UserCreate
from app.services.users import UsersService
from app.models.users import Users

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
    user_data = {
        "user_name": "testuser",
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]


@pytest.fixture
def default_user(test_db: Session):
    user_data = UserCreate(
        user_name="testuser", name="Test User", email="testuser@example.com", password="testpassword"
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
