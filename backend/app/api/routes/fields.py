from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.fields import FieldCreate, FieldUpdate, Fields
from app.services.fields import FieldsService


router = APIRouter(
    prefix="/fields",
    tags=["Fields"],
)


@router.get("/", response_model=list[Fields], status_code=status.HTTP_200_OK)
def get_all_fields(form_id: int = None, db: Session = Depends(get_db)):
    """
    Retrieve all fields. Optionally filter by form ID.
    """
    return FieldsService.get_all_fields(db, form_id=form_id)


@router.get("/{field_id}", response_model=Fields, status_code=status.HTTP_200_OK)
def get_field_by_id(field_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a field by ID.
    """
    return FieldsService.get_field_by_id(db, field_id)


@router.get("/form/{form_id}", response_model=list[Fields], status_code=status.HTTP_200_OK)
def get_fields_by_form_id(form_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a field by Form ID.
    """
    return FieldsService.get_fields_by_form_id(db, form_id)


@router.post("/", response_model=Fields, status_code=status.HTTP_201_CREATED)
def create_field(field_data: FieldCreate, db: Session = Depends(get_db)):
    """
    Create a new field.
    """
    return FieldsService.create_field(db, field_data)


@router.put("/{field_id}", response_model=Fields, status_code=status.HTTP_200_OK)
def update_field(field_id: int, field_data: FieldUpdate, db: Session = Depends(get_db)):
    """
    Update an existing field by ID.
    """
    return FieldsService.update_field(db, field_id, field_data)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(field_id: int, db: Session = Depends(get_db)):
    """
    Delete a field by ID.
    """
    FieldsService.delete_field(db, field_id)
    return {"detail": "Field deleted successfully"}