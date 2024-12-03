from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.schemas.forms import FormCreate, FormUpdate, Forms


class FormsService:
    @staticmethod
    def get_all_forms(db: Session) -> List[Forms]:
        return db.query(Forms).all()

    @staticmethod
    def get_form_by_id(db: Session, form_id: int) -> Forms:
        form = db.query(Forms).filter(Forms.id == form_id).first()
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with id {form_id} not found"
            )
        return form

    @staticmethod
    def create_form(db: Session, form_data: FormCreate) -> Forms:
        new_form = Forms(**form_data.dict())
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        return new_form

    @staticmethod
    def update_form(db: Session, form_id: int, form_data: FormUpdate) -> Forms:
        form = FormsService.get_form_by_id(db, form_id)
        for key, value in form_data.dict(exclude_unset=True).items():
            setattr(form, key, value)
        db.commit()
        db.refresh(form)
        return form

    @staticmethod
    def delete_form(db: Session, form_id: int) -> None:
        form = FormsService.get_form_by_id(db, form_id)
        db.delete(form)
        db.commit()
