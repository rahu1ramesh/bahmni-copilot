from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    user_name: constr(max_length=255)
    email: constr(max_length=255)
    password: constr(max_length=255)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    user_name: constr(max_length=255)
    email: Optional[constr(max_length=255)] = None
    password: Optional[constr(max_length=255)] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    user_name: constr(max_length=255)
    email: constr(max_length=255)
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
