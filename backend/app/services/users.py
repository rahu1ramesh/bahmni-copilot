from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import parse_obj_as
from app.models.users import Users
from app.schemas.users import UserCreate, UserUpdate, User


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
        new_user = Users(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return parse_obj_as(User, new_user)

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
