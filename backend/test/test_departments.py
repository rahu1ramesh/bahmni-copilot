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
def auth_headers(admin_user):
    access_token = create_access_token(subject=admin_user.user_name)
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


def test_get_all_departments(test_db: Session, departments: List[Departments]):
    response_data = DepartmentsService.get_all_departments(test_db)
    response_departments = [dept for dept in response_data if dept.name != "Admin Department"]
    assert len(response_departments) == len(departments)


def test_get_department_by_id(test_db: Session, department: Departments):
    result = DepartmentsService.get_department_by_id(test_db, department.id)
    assert result.id == department.id
    assert result.name == department.name


def test_get_department_by_id_not_found(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        DepartmentsService.get_department_by_id(test_db, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Department with id 999 not found"


def test_create_department(test_db: Session):
    department_data = DepartmentCreate(name="New Department")
    result = DepartmentsService.create_department(test_db, department_data)
    assert result.name == department_data.name
    assert result.id is not None


def test_update_department(test_db: Session, department: Departments):
    department_data = DepartmentUpdate(name="Updated Department")
    result = DepartmentsService.update_department(test_db, department.id, department_data)
    assert result.name == department_data.name


def test_update_department_not_found(test_db: Session):
    department_data = DepartmentUpdate(name="Updated Department")
    with pytest.raises(HTTPException) as exc_info:
        DepartmentsService.update_department(test_db, 999, department_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Department not found"


def test_delete_department(test_db: Session, department: Departments):
    DepartmentsService.delete_department(test_db, department.id)
    result = test_db.query(Departments).filter(Departments.id == department.id).first()
    assert result is None
