from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    user_name: str
    email: str
    password: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    user_name: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    name: str
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
