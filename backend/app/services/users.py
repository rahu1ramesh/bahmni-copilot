from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import parse_obj_as
from app.models.users import Users
from app.schemas.users import UserCreate, UserUpdate, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersService:

    @staticmethod
    def get_all_users(db: Session) -> list[User]:
        return parse_obj_as(list[User], db.query(Users).all())

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return parse_obj_as(User, user)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found"
            )
        return parse_obj_as(User, user)

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        existing_user = db.query(Users).filter(Users.email == user_data.email).first()
        if not existing_user:
            hashed_password = pwd_context.hash(user_data.password)
            user_data_dict = user_data.dict()
            user_data_dict["password"] = hashed_password
            new_user = Users(**user_data_dict)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email id {user_data.email} already exist.")

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        new_user = UsersService.get_user_by_id(db, user_id)
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(new_user, key, value)
        db.commit()
        db.refresh(new_user)
        return parse_obj_as(User, new_user)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        db_user = UsersService.get_user_by_id(db, user_id)
        db.delete(db_user)
        db.commit()
