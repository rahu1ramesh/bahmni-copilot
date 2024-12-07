from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import parse_obj_as
from typing import List
from app.models.forms import Forms
from app.schemas.forms import FormCreate, FormUpdate, Form


class FormsService:
    @staticmethod
    def get_all_forms(db: Session) -> List[Form]:
        return parse_obj_as(List[Form], db.query(Forms).all())

    @staticmethod
    def get_form_by_id(db: Session, form_id: int) -> Form:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with id {form_id} not found"
            )
        return parse_obj_as(Form, form)

    @staticmethod
    def create_form(db: Session, form_data: FormCreate) -> Form:
        new_form = Forms(**form_data.dict())
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        return parse_obj_as(Form, new_form)

    @staticmethod
    def update_form(db: Session, form_id: int, form_data: FormUpdate) -> Form:
        form = FormsService.get_form_by_id(db, form_id)
        for key, value in form_data.dict(exclude_unset=True).items():
            setattr(form, key, value)
        db.commit()
        db.refresh(form)
        return parse_obj_as(Form, form)

    @staticmethod
    def delete_form(db: Session, form_id: int) -> None:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        db.delete(form)
        db.commit()
