from pydantic import BaseModel
from typing import Optional


class FieldCreate(BaseModel):
    name: str
    query_selector: Optional[str] = None
    description: Optional[str] = None
    field_type: str = "string"
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    enum_options: Optional[str] = None
    form_id: int

    class Config:
        from_attributes = True


class FieldUpdate(BaseModel):
    name: Optional[str] = None
    query_selector: Optional[str] = None
    description: Optional[str] = None
    field_type: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    enum_options: Optional[str] = None

    class Config:
        from_attributes = True


class Fields(BaseModel):
    id: int
    name: str
    query_selector: Optional[str] = None
    description: Optional[str] = None
    field_type: str = "string"
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    enum_options: Optional[str] = None
    form_id: int

    class Config:
        from_attributes = True
