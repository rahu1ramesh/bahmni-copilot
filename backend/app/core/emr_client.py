import os
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv
from typing import List
from fastapi import HTTPException
from app.schemas.patients import Patient, ObservationResource, ConditionResource, AllergyIntoleranceResource

load_dotenv()


class EMRClient:
    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.base_url = os.getenv("EMR_BASE_URL")
        self.username = os.getenv("EMR_USERNAME")
        self.password = os.getenv("EMR_PASSWORD")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.username, self.password)
        session.verify = False
        return session

    def _fetch(self, endpoint: str):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            self._handle_http_error(response, http_err)
        except requests.exceptions.RequestException as err:
            raise HTTPException(status_code=500, detail=f"Error occurred while fetching data: {err}")

    def _handle_http_error(self, response, http_err):
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Failed to authenticate with EMR service")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Resource not found: {response.url}")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")

    def get_patient_data(self, patient_id: str) -> Patient:
        data = self._fetch(f"Patient/{patient_id}")
        if data:
            return Patient(**data)
        raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")

    def get_observations(self, patient_id: str) -> List[ObservationResource]:
        data = self._fetch(f"Observation?subject:Patient={patient_id}")
        if data:
            return [ObservationResource(**entry.get("resource", {})) for entry in data.get("entry", [])]
        raise HTTPException(status_code=404, detail=f"Observations for patient with ID {patient_id} not found")

    def get_conditions(self, patient_id: str) -> List[ConditionResource]:
        data = self._fetch(f"Condition?patient={patient_id}")
        if data:
            return [ConditionResource(**entry.get("resource", {})) for entry in data.get("entry", [])]
        raise HTTPException(status_code=404, detail=f"Conditions for patient with ID {patient_id} not found")

    def get_allergy_details(self, patient_id: str) -> List[AllergyIntoleranceResource]:
        data = self._fetch(f"AllergyIntolerance?patient={patient_id}")
        if data:
            return [AllergyIntoleranceResource(**entry.get("resource", {})) for entry in data.get("entry", [])]
        raise HTTPException(status_code=404, detail=f"Allergy details for patient with ID {patient_id} not found")
