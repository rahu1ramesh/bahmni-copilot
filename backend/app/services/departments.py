from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from typing import List
from app.models.departments import Departments
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, Department


class DepartmentsService:
    @staticmethod
    def get_all_departments(db: Session) -> List[Department]:
        return TypeAdapter(List[Department]).validate_python(db.query(Departments).all())

    @staticmethod
    def get_department_by_id(db: Session, department_id: int) -> Department:
        department = db.query(Departments).filter(Departments.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id {department_id} not found"
            )
        return TypeAdapter(Department).validate_python(department)

    @staticmethod
    def create_department(db: Session, department_data: DepartmentCreate) -> Department:
        new_department = Departments(**department_data.model_dump())
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        return TypeAdapter(Department).validate_python(new_department)

    @staticmethod
    def update_department(db: Session, department_id: int, department_data: DepartmentUpdate) -> Department:
        department = db.query(Departments).filter(Departments.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        for key, value in department_data.model_dump(exclude_unset=True).items():
            setattr(department, key, value)
        db.commit()
        db.refresh(department)
        return TypeAdapter(Department).validate_python(department)

    @staticmethod
    def delete_department(db: Session, department_id: int) -> None:
        department = db.query(Departments).filter(Departments.id == department_id).first()
        db.delete(department)
        db.commit()
