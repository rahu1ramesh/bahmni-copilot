from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: constr(max_length=255)
    user_name: constr(max_length=255)
    email: constr(max_length=255)
    password: constr(max_length=255)
    specialty: Optional[constr(max_length=255)] = "General Medicine"
    department_id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    user_name: constr(max_length=255)
    name: Optional[constr(max_length=255)] = None
    email: Optional[constr(max_length=255)] = None
    password: Optional[constr(max_length=255)] = None
    specialty: Optional[constr(max_length=255)] = None
    department_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    name: constr(max_length=255)
    user_name: constr(max_length=255)
    email: constr(max_length=255)
    specialty: Optional[constr(max_length=255)]
    department_id: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
