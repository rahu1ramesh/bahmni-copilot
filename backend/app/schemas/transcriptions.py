from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TranscriptionCreate(BaseModel):
    user_id: int
    form_id: int

    class Config:
        from_attributes = True


class Transcriptions(BaseModel):
    id: int
    upload_uuid: str
    user_id: int
    form_id: int
    transcription_text: Optional[str] = None
    status: str = "pending"
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
