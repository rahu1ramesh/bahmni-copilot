from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from typing import List
from app.models.forms import Forms
from app.schemas.forms import FormCreate, FormUpdate, Form


class FormsService:
    @staticmethod
    def get_all_forms(db: Session) -> List[Form]:
        return TypeAdapter(List[Form]).validate_python(db.query(Forms).all())

    @staticmethod
    def get_form_by_id(db: Session, form_id: int) -> Form:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with id {form_id} not found"
            )
        return TypeAdapter(Form).validate_python(form)

    @staticmethod
    def create_form(db: Session, form_data: FormCreate) -> Form:
        new_form = Forms(**form_data.model_dump())
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        return TypeAdapter(Form).validate_python(new_form)

    @staticmethod
    def update_form(db: Session, form_id: int, form_data: FormUpdate) -> Form:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        for key, value in form_data.model_dump(exclude_unset=True).items():
            setattr(form, key, value)
        db.commit()
        db.refresh(form)
        return TypeAdapter(Form).validate_python(form)

    @staticmethod
    def delete_form(db: Session, form_id: int) -> None:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        db.delete(form)
        db.commit()
