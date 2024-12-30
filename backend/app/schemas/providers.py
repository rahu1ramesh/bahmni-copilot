from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from datetime import datetime


class ProviderCreate(BaseModel):
    user_id: int
    name: constr(max_length=255)
    specialty: Optional[constr(max_length=255)] = "General Medicine"
    department_id: int

    model_config = ConfigDict(from_attributes=True)


class ProviderUpdate(BaseModel):
    name: Optional[constr(max_length=255)] = None
    specialty: Optional[constr(max_length=255)] = None
    department_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Provider(BaseModel):
    id: int
    user_id: int
    name: constr(max_length=255)
    specialty: Optional[constr(max_length=255)]
    department_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
