from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.transcriptions import TranscriptionService
from app.schemas.transcriptions import Transcription
from app.services.auth import get_current_user


router = APIRouter(prefix="/transcriptions", tags=["Transcriptions"], dependencies=[Depends(get_current_user)])


@router.post(
    "/{form_id}",
    response_model=Transcription,
    status_code=status.HTTP_201_CREATED,
    generate_unique_id_function=lambda _: "UploadFile",
)
async def create_transcription(
    form_id: int,
    file: UploadFile = File(..., description="The file with the entity to process"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user),
):
    """
    Create a new transcription record with an uploaded audio file.

    - **form_id**: The form ID associated with the transcription.
    - **file**: The audio file to upload and process.

    Returns the created transcription record.
    """
    transcription = TranscriptionService.create_transcription(db=db, user_id=user_data.id, form_id=form_id, file=file)
    return transcription
