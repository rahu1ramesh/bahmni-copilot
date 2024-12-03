from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.schemas.fields import FieldCreate, FieldUpdate, Fields
from app.services.forms import FormsService


class FieldsService:
    @staticmethod
    def get_all_fields(db: Session, form_id: Optional[int] = None) -> List[Fields]:
        query = db.query(Fields)
        if form_id:
            query = query.filter(Fields.form_id == form_id)
        return query.all()

    @staticmethod
    def get_field_by_id(db: Session, field_id: int) -> Fields:
        field = db.query(Fields).filter(Fields.id == field_id).first()
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field with id {field_id} not found"
            )
        return field

    @staticmethod
    def get_fields_by_form_id(db: Session, form_id: int) -> List[Fields]:
        FormsService.get_form_by_id(db, form_id=form_id)
        fields = db.query(Fields).filter(Fields.form_id == form_id)
        return fields

    @staticmethod
    def create_field(db: Session, field_data: FieldCreate) -> Fields:
        FormsService.get_form_by_id(db, form_id=field_data.form_id)
        new_field = Fields(**field_data.dict())
        db.add(new_field)
        db.commit()
        db.refresh(new_field)
        return new_field

    @staticmethod
    def update_field(db: Session, field_id: int, field_data: FieldUpdate) -> Fields:
        field = FieldsService.get_field_by_id(db, field_id)
        for key, value in field_data.dict(exclude_unset=True).items():
            setattr(field, key, value)
        db.commit()
        db.refresh(field)
        return field

    @staticmethod
    def delete_field(db: Session, field_id: int) -> None:
        field = FieldsService.get_field_by_id(db, field_id)
        db.delete(field)
        db.commit()
