from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.users import UserCreate, UserUpdate, Users


class UsersService:

    @staticmethod
    def get_all_users(db: Session) -> list[Users]:
        return db.query(Users).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Users:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Users:
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found"
            )
        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Users:
        db_user = Users(**user_data.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Users:
        db_user = UsersService.get_user_by_id(db, user_id)
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        db_user = UsersService.get_user_by_id(db, user_id)
        db.delete(db_user)
        db.commit()
