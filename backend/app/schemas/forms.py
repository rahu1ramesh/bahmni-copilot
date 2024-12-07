from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FormCreate(BaseModel):
    name: str
    prompt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FormUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Form(BaseModel):
    id: int
    name: str
    prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
