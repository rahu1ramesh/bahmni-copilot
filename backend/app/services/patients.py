from app.core.emr_client import EMRClient
from fastapi import HTTPException
from app.schemas.patients import (
    PatientContext,
    Patient,
    ObservationResource,
    ConditionResource,
    AllergyIntoleranceResource,
)
from app.schemas.users import User
from app.schemas.departments import Department
from typing import List
from app.utils.openai import OpenAIUtils


class PatientService:
    def __init__(self, emr_client: EMRClient):
        self.emr_client = emr_client

    def get_patient_context(self, patient_id: str, user: User, department: Department) -> str:
        try:
            patient: Patient = self.emr_client.get_patient_data(patient_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            observations: List[ObservationResource] = self.emr_client.get_observations(patient_id)
            conditions: List[ConditionResource] = self.emr_client.get_conditions(patient_id)
            allergies: List[AllergyIntoleranceResource] = self.emr_client.get_allergy_details(patient_id)

            patient_context: PatientContext = PatientContext(
                patient=patient,
                observations=observations,
                conditions=conditions,
                allergies=allergies,
            )
            patient_diagnosis = OpenAIUtils.analyze_patient_context(
                patient_context=patient_context,
                user=user,
                department=department,
            )
            return patient_diagnosis
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
