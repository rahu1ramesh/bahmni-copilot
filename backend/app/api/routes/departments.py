from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, Department
from app.config.database import get_db
from app.services.departments import DepartmentsService
from app.services.auth import get_current_user, is_admin


router = APIRouter(prefix="/departments", tags=["Departments"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[Department], status_code=status.HTTP_200_OK, dependencies=[Depends(is_admin)])
def get_all_departments(db: Session = Depends(get_db)):
    """
    Retrieve all departments.
    """
    return DepartmentsService.get_all_departments(db)


@router.get(
    "/{department_id}", response_model=Department, status_code=status.HTTP_200_OK, dependencies=[Depends(is_admin)]
)
def get_department_by_id(department_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a department by ID.
    """
    return DepartmentsService.get_department_by_id(db, department_id)


@router.post("/", response_model=Department, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_admin)])
def create_department(department_data: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Create a new department.
    """
    return DepartmentsService.create_department(db, department_data)


@router.put(
    "/{department_id}", response_model=Department, status_code=status.HTTP_200_OK, dependencies=[Depends(is_admin)]
)
def update_department(department_id: int, department_data: DepartmentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing department by ID.
    """
    return DepartmentsService.update_department(db, department_id, department_data)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    """
    Delete a department by ID.
    """
    DepartmentsService.delete_department(db, department_id)
    return {"detail": "Departments deleted successfully"}
