from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.forms import FormCreate, FormUpdate, Forms
from app.config.database import get_db
from app.services.forms import FormsService


router = APIRouter(
    prefix="/forms",
    tags=["Forms"],
)


@router.get("/", response_model=list[Forms], status_code=status.HTTP_200_OK)
def get_all_forms(db: Session = Depends(get_db)):
    """
    Retrieve all forms.
    """
    return FormsService.get_all_forms(db)


@router.get("/{form_id}", response_model=Forms, status_code=status.HTTP_200_OK)
def get_form_by_id(form_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a form by ID.
    """
    return FormsService.get_form_by_id(db, form_id)


@router.post("/", response_model=Forms, status_code=status.HTTP_201_CREATED)
def create_form(form_data: FormCreate, db: Session = Depends(get_db)):
    """
    Create a new form.
    """
    return FormsService.create_form(db, form_data)


@router.put("/{form_id}", response_model=Forms, status_code=status.HTTP_200_OK)
def update_form(form_id: int, form_data: FormUpdate, db: Session = Depends(get_db)):
    """
    Update an existing form by ID.
    """
    return FormsService.update_form(db, form_id, form_data)


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(form_id: int, db: Session = Depends(get_db)):
    """
    Delete a form by ID.
    """
    FormsService.delete_form(db, form_id)
    return {"detail": "Forms deleted successfully"}
