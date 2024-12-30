from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from typing import List
from app.models.users import Users
from app.schemas.users import UserCreate, UserUpdate, User
from app.services.auth import get_hashed_password


class UsersService:

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        return TypeAdapter(List[User]).validate_python(db.query(Users).all())

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
        return TypeAdapter(User).validate_python(user)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
        return TypeAdapter(User).validate_python(user)

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        existing_email = db.query(Users).filter(Users.email == user_data.email).first()
        existing_user_name = db.query(Users).filter(Users.user_name == user_data.user_name).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"User with email id {user_data.email} already exist."
            )
        if existing_user_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"User with username {user_data.user_name} already exist."
            )
        hashed_password = get_hashed_password(user_data.password)
        user_data_dict = user_data.model_dump()
        user_data_dict["password"] = hashed_password
        new_user = Users(**user_data_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return TypeAdapter(User).validate_python(new_user)

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        new_user = db.query(Users).filter(Users.id == user_id).first()
        if not new_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user_id {user_id} not found")
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(new_user, key, value)
        db.commit()
        db.refresh(new_user)
        return TypeAdapter(User).validate_python(new_user)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user_id {user_id} not found")
        db.delete(user)
        db.commit()
