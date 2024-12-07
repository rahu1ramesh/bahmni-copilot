from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class TranscriptionCreate(BaseModel):
    user_id: int
    form_id: int

    model_config = ConfigDict(from_attributes=True)


class Transcription(BaseModel):
    id: int
    upload_uuid: str
    user_id: int
    form_id: int
    transcription_text: Optional[str] = None
    status: str = "pending"
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
