from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from typing import List
from app.models.fields import Fields
from app.schemas.fields import FieldCreate, FieldUpdate, Field
from app.services.forms import FormsService


class FieldsService:
    @staticmethod
    def get_all_fields(db: Session) -> List[Field]:
        return TypeAdapter(List[Field]).validate_python(db.query(Fields).all())

    @staticmethod
    def get_field_by_id(db: Session, field_id: int) -> Field:
        field = db.query(Fields).filter(Fields.id == field_id).first()
        if not field:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with id {field_id} not found")
        return TypeAdapter(Field).validate_python(field)

    @staticmethod
    def get_fields_by_form_id(db: Session, form_id: int) -> List[Field]:
        FormsService.get_form_by_id(db, form_id=form_id)
        fields = db.query(Fields).filter(Fields.form_id == form_id)
        return TypeAdapter(List[Field]).validate_python(fields)

    @staticmethod
    def create_field(db: Session, field_data: FieldCreate) -> Field:
        FormsService.get_form_by_id(db, form_id=field_data.form_id)
        new_field = Fields(**field_data.model_dump())
        db.add(new_field)
        db.commit()
        db.refresh(new_field)
        return TypeAdapter(Field).validate_python(new_field)

    @staticmethod
    def update_field(db: Session, field_id: int, field_data: FieldUpdate) -> Field:
        field = db.query(Fields).filter(Fields.id == field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        for key, value in field_data.model_dump(exclude_unset=True).items():
            setattr(field, key, value)
        db.commit()
        db.refresh(field)
        return TypeAdapter(Field).validate_python(field)

    @staticmethod
    def delete_field(db: Session, field_id: int) -> None:
        field = db.query(Fields).filter(Fields.id == field_id).first()
        if not field:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with id {field_id} not found")
        db.delete(field)
        db.commit()
