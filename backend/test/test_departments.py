import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from fastapi import HTTPException
from app.models.departments import Departments
from app.schemas.departments import DepartmentCreate, DepartmentUpdate
from app.services.departments import DepartmentsService
from app.config.database import get_db
from typing import List
from app.services.auth import create_access_token
from app.models.users import Users


def override_get_db():
    from app.config.database import SessionLocal

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_db():
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Departments).delete()
        db.query(Users).delete()
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
def non_admin_user(test_db: Session):
    department = Departments(name="Test Department")
    test_db.add(department)
    test_db.commit()
    test_db.refresh(department)

    user_data = {
        "user_name": "nonadmin",
        "name": "Non Admin User",
        "email": "nonadmin@example.com",
        "password": "nonadminpassword",
        "department_id": department.id,
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
def no_auth_headers(non_admin_user):
    access_token = create_access_token(subject=non_admin_user.user_name)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def departments(test_db: Session):
    departments = [
        Departments(name="Department 1"),
        Departments(name="Department 2"),
    ]
    test_db.add_all(departments)
    test_db.commit()
    return departments


@pytest.fixture
def department(test_db: Session):
    department = Departments(name="Department 1")
    test_db.add(department)
    test_db.commit()
    return department


def test_get_all_departments_service(test_db: Session, departments: List[Departments]):
    response_data = DepartmentsService.get_all_departments(test_db)
    response_departments = [dept for dept in response_data if dept.name != "Admin Department"]
    assert len(response_departments) == len(departments)


def test_get_department_by_id_service(test_db: Session, department: Departments):
    result = DepartmentsService.get_department_by_id(test_db, department.id)
    assert result.id == department.id
    assert result.name == department.name


def test_get_department_by_id_not_found_service(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        DepartmentsService.get_department_by_id(test_db, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Department with id 999 not found"


def test_create_department_service(test_db: Session):
    department_data = DepartmentCreate(name="New Department")
    result = DepartmentsService.create_department(test_db, department_data)
    assert result.name == department_data.name
    assert result.id is not None


def test_update_department_service(test_db: Session, department: Departments):
    department_data = DepartmentUpdate(name="Updated Department")
    result = DepartmentsService.update_department(test_db, department.id, department_data)
    assert result.name == department_data.name


def test_update_department_not_found_service(test_db: Session):
    department_data = DepartmentUpdate(name="Updated Department")
    with pytest.raises(HTTPException) as exc_info:
        DepartmentsService.update_department(test_db, 999, department_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Department not found"


def test_delete_department_service(test_db: Session, department: Departments):
    DepartmentsService.delete_department(test_db, department.id)
    result = test_db.query(Departments).filter(Departments.id == department.id).first()
    assert result is None


def test_get_all_departments(client, auth_headers, departments):
    response = client.get("/api/departments/", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len([dept for dept in response_data if dept["name"] != "Admin Department"]) == len(departments)


def test_get_department_by_id(client, auth_headers, department):
    response = client.get(f"/api/departments/{department.id}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == department.id
    assert response_data["name"] == department.name


def test_get_department_by_id_not_found(client, auth_headers):
    response = client.get("/api/departments/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Department with id 999 not found"}


def test_create_department(client, auth_headers):
    department_data = {"name": "New Department"}
    response = client.post("/api/departments/", json=department_data, headers=auth_headers)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == department_data["name"]
    assert response_data["id"] is not None


def test_update_department(client, auth_headers, department):
    department_data = {"name": "Updated Department"}
    response = client.put(f"/api/departments/{department.id}", json=department_data, headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == department_data["name"]


def test_update_department_not_found(client, auth_headers):
    department_data = {"name": "Updated Department"}
    response = client.put("/api/departments/999", json=department_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Department not found"}


def test_delete_department(client, auth_headers, department):
    response = client.delete(f"/api/departments/{department.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_department_not_found(client, auth_headers):
    response = client.delete("/api/departments/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Department with id 999 not found"}


def test_create_department_no_admin(client, no_auth_headers):
    department_data = {"name": "Unauthorized Department"}
    response = client.post("/api/departments/", json=department_data, headers=no_auth_headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to access this resource"}


def test_update_department_no_admin(client, no_auth_headers, department):
    department_data = {"name": "Unauthorized Update"}
    response = client.put(f"/api/departments/{department.id}", json=department_data, headers=no_auth_headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to access this resource"}


def test_delete_department_no_admin(client, no_auth_headers, department):
    response = client.delete(f"/api/departments/{department.id}", headers=no_auth_headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to access this resource"}
