from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    user_name: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    user_name: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    name: str
    user_name: str
    email: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
