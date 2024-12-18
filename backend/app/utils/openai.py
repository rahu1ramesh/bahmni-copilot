import os
from fastapi import HTTPException, status
from typing import Dict
from openai import OpenAI
from app.schemas.departments import Department
from app.schemas.patients import PatientContext
from app.schemas.users import User


class OpenAIUtils:
    """
    Utility class for interacting with OpenAI's Whisper API for transcription
    and generating responses based on transcription data.
    """

    _client = None

    @classmethod
    def initialize_client(cls):
        """Initializes the OpenAI client if not already initialized."""
        if cls._client is None:
            cls._client = OpenAI()

    @classmethod
    def transcribe_audio(cls, file_path: str) -> str:
        """
        Transcribes audio into its original language.

        :param file_path: Path to the audio file.
        :return: Transcription text.
        :raises ValueError: If the file does not exist.
        :raises HTTPException: If transcription fails.
        """
        cls.initialize_client()

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File '{file_path}' does not exist."
            )

        with open(file_path, "rb") as audio_file:
            try:
                transcription = cls._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                )
                return transcription
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail=f"Failed to transcribe audio from the file: {file_path}. Error: {e}",
                )

    @classmethod
    def validate_transcription(cls, transcription_text: str, form_structure: Dict[str, str]) -> Dict[str, str]:
        """
        Prepares the context for the AI to fill out a form based on the transcription text.

        :param transcription_text: Transcription text from audio input.
        :param form_structure: Dictionary containing form field names as keys and their descriptions as values.
        :return: Dictionary with form field names and their corresponding values populated from the transcription.
        :raises HTTPException: If the response parsing fails.
        """
        cls.initialize_client()

        prompt = f"""
            Given a text transcription and a form structure dictionary, evaluate how confidently the
             form can be filled based on the transcription's content. Return a confidence score for
             each form field as a percentage (0-100%) and a final confidence score for the entire form.

            Form Structure:
            {form_structure}

            Transcription:
            {transcription_text}

            Task:
            Understand the context of the transcription and evaluate how well it aligns with the form structure.
            Return the response as a JSON dictionary where the keys are the form field names and the values are
            the confidence scores. The final key should be 'total' with the overall confidence score for the form.
            """

        try:
            response = cls._client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                temperature=0.2,
                top_p=1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            confidence_scores = eval(response.choices[0].message.content)
            if not isinstance(confidence_scores, dict):
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="Failed to parse the AI's response: The AI response is not a valid dictionary.",
                )
            return confidence_scores
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to parse the AI's response: {e}",
            )

    @classmethod
    def prepare_context(cls, transcription_text: str, form_structure: Dict[str, str]) -> Dict[str, str]:
        """
        Prepares the context for the AI to fill out a form based on the transcription text.

        :param transcription_text: Transcription text from audio input.
        :param form_structure: Dictionary containing form field names as keys and their descriptions as values.
        :return: Dictionary with form field names and their corresponding values populated from the transcription.
        :raises HTTPException: If the response parsing fails.
        """
        cls.initialize_client()

        prompt = f"""
        You are an AI assistant filling the form for a user. Make sure that you do not populate
         the form with any data that the user did not provide. Ensure all data shared by users
         are correctly split into function arguments.

        Form Structure:
        {form_structure}

        Transcription:
        {transcription_text}

        Task:
        Extract the relevant details from the transcription to populate the form fields.
        Only use the data explicitly mentioned in the transcription. Return the response
         as a JSON dictionary where the keys are the form field names and the values are
         the extracted data.
        """

        try:
            response = cls._client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                temperature=0.2,
                top_p=1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            result = eval(response.choices[0].message.content)
            if not isinstance(result, dict):
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="Failed to parse the AI's response: The AI response is not a valid dictionary.",
                )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to parse the AI's response: {e}",
            )

    @classmethod
    def analyze_patient_context(cls, patient_context: PatientContext, user: User, department: Department) -> str:
        """
        Analyzes the patient context using AI models to provide a detailed summary
        based on patient details, observations, conditions, and allergies.

        :param patient_context: The complete patient context
        containing personal details, observations, conditions, and allergies.
        :return: A detailed patient summary as a dictionary.
        :raises HTTPException: If the AI response parsing fails.
        """
        cls.initialize_client()

        patient_data = patient_context.dict(by_alias=True, exclude_none=True)

        prompt = f"""
        Generate a structured report tailored to the user’s clinical specialty and department, including:

        Patient Summary: Full name, gender, date of birth, active status, and contact details.
        Medical History: Current and past conditions, onset/progression dates, key clinical findings,
         diagnostic notes, and trends in vital signs or lab results.
        Allergy Profile: Identified allergens, reaction types, severity, and management protocols.
        Clinical Assessment: Current health status, recommended care plans, diagnostic tests, specialist
         referrals, preventive care, lifestyle changes, and initial treatment plans.
        Ensure the report is concise, medically accurate, and decision-oriented, supporting specialists
         in making informed clinical decisions.

        **Patient Context:**
        {patient_data}
        """

        try:
            response = cls._client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                temperature=0.2,
                top_p=1,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an {department.name} expert specializing in {user.specialty}. "
                        f"Your task is to analyze a patient's comprehensive medical profile based on patient "
                        f"demographics, medical history, observations, conditions, and allergies.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            result = response.choices[0].message.content
            print(result)
            return result

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to parse the AI's response: {e}",
            )
