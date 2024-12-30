from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from typing import List
from app.models.providers import Providers
from app.models.users import Users
from app.models.departments import Departments
from app.schemas.providers import ProviderCreate, ProviderUpdate, Provider


class ProvidersService:

    @staticmethod
    def get_all_providers(db: Session) -> List[Provider]:
        return TypeAdapter(List[Provider]).validate_python(db.query(Providers).all())

    @staticmethod
    def get_provider_by_id(db: Session, provider_id: int) -> Provider:
        provider = db.query(Providers).filter(Providers.id == provider_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider with id {provider_id} not found"
            )
        return TypeAdapter(Provider).validate_python(provider)

    @staticmethod
    def get_provider_by_user_id(db: Session, user_id: int) -> Provider:
        provider = db.query(Providers).filter(Providers.user_id == user_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider with user id {user_id} not found"
            )
        return TypeAdapter(Provider).validate_python(provider)

    @staticmethod
    def create_provider(db: Session, provider_data: ProviderCreate) -> Provider:
        user = db.query(Users).filter(Users.id == provider_data.user_id).first()
        department = db.query(Departments).filter(Departments.id == provider_data.department_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {provider_data.user_id} not found"
            )
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {provider_data.department_id} not found",
            )
        new_provider = Providers(**provider_data.model_dump())
        db.add(new_provider)
        db.commit()
        db.refresh(new_provider)
        return TypeAdapter(Provider).validate_python(new_provider)

    @staticmethod
    def update_provider(db: Session, provider_id: int, provider_data: ProviderUpdate) -> Provider:
        provider = db.query(Providers).filter(Providers.id == provider_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider with id {provider_id} not found"
            )
        for key, value in provider_data.model_dump(exclude_unset=True).items():
            setattr(provider, key, value)
        db.commit()
        db.refresh(provider)
        return TypeAdapter(Provider).validate_python(provider)

    @staticmethod
    def delete_provider(db: Session, provider_id: int) -> None:
        provider = db.query(Providers).filter(Providers.id == provider_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider with id {provider_id} not found"
            )
        db.delete(provider)
        db.commit()
