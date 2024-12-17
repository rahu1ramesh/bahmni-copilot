import uuid
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.transcriptions import Transcriptions
from app.schemas.transcriptions import Transcription
from app.services.fields import FieldsService
from app.utils.s3 import S3Utils
from app.utils.openai import OpenAIUtils


class TranscriptionService:

    SUPPORTED_FILE_TYPES = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}

    @staticmethod
    def create_transcription(db: Session, user_id: int, form_id: int, file: UploadFile) -> Transcription:
        """
        Creates a new transcription record and uploads the associated audio file to S3.

        :param db: Database session.
        :param user_id: ID of the user creating the transcription.
        :param form_id: ID of the form associated with the transcription.
        :param file: Uploaded audio file.
        :return: The created Transcriptions record.
        """

        field_list = FieldsService.get_fields_by_form_id(db, form_id)
        form_fields = [{field.name: field.description} for field in field_list]

        file_extension = os.path.splitext(file.filename)[-1].lower().strip(".")
        if file_extension not in TranscriptionService.SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: '{file_extension}'. "
                f"Allowed types are: {', '.join(TranscriptionService.SUPPORTED_FILE_TYPES)}.",
            )

        temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
        try:
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file.file.read())

            file_uuid = str(uuid.uuid4())
            s3_key = f"{file_uuid}.{file_extension}"
            try:
                S3Utils.upload_file(file_path=temp_file_path, object_name=s3_key)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=f"Failed to upload audio file: {str(e)}"
                )
            transcription_text = None

            transcription_text = OpenAIUtils.transcribe_audio(file_path=temp_file_path)

            confidence_score = OpenAIUtils.validate_transcription(
                transcription_text=transcription_text, form_structure=form_fields
            )

            if confidence_score.get("total") < 35:
                fields_with_low_confidence = [
                    field for field, score in confidence_score.items() if score < 35 and field != "total"
                ]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transcription confidence score is too low. "
                    f"Kindly review the following fields: {fields_with_low_confidence}.",
                )

            context = OpenAIUtils.prepare_context(transcription_text=transcription_text, form_structure=form_fields)

            new_transcription = Transcriptions(
                upload_uuid=file_uuid,
                user_id=user_id,
                form_id=form_id,
                transcription_text=transcription_text,
                status="completed",
                context=context,
            )

            db.add(new_transcription)
            db.commit()
            db.refresh(new_transcription)

            return new_transcription
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
