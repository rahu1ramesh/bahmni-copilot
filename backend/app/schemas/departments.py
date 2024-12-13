from pydantic import BaseModel, ConfigDict, constr
from datetime import datetime


class DepartmentCreate(BaseModel):
    name: constr(max_length=255)

    model_config = ConfigDict(from_attributes=True)


class DepartmentUpdate(BaseModel):
    name: constr(max_length=255)

    model_config = ConfigDict(from_attributes=True)


class Department(BaseModel):
    id: int
    name: constr(max_length=255)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
