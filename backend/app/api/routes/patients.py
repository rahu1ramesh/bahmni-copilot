from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.auth import get_current_user
from app.services.patients import PatientService
from app.services.departments import DepartmentsService
from app.core.emr_client import EMRClient

emr_client = EMRClient()
patient_service = PatientService(emr_client)

router = APIRouter(prefix="/patients", tags=["Patients"], dependencies=[Depends(get_current_user)])


@router.get("/{patient_id}", response_model=str, status_code=status.HTTP_200_OK)
async def get_patient_context(
    patient_id: str, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)
):
    """
    Analyzes the patient context using AI models to provide a detailed summary
    based on patient details, observations, conditions, and allergies.

    :param patient_id: The patient uuid as in the emr system.
    :return: A detailed patient summary as a dictionary.
    :raises HTTPException: If the AI response parsing fails.
    """
    department = DepartmentsService.get_department_by_id(db, user_data.department_id)
    patient_context = patient_service.get_patient_context(patient_id, user_data, department)
    return patient_context
