from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    encrypted_password: str
    admin: Optional[bool] = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    encrypted_password: Optional[str] = None

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
