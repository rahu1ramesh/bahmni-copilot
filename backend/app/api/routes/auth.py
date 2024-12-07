from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.users import UsersService
from app.schemas.users import UserCreate, User
from app.schemas.auth import TokenSchema
from app.services.auth import create_access_token, create_refresh_token, authenticate_user
from app.config.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    response_description="The newly created user",
)
def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. Requires user information such as `name`, `email`, and `password`.

    - **name**: User's full name.
    - **email**: User's email address (must be unique).
    - **password**: User's password (encrypted on creation).
    """
    return UsersService.create_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    response_description="The newly created user",
    generate_unique_id_function=lambda _: "LoginUser",
)
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """
    Authenticate and log in a user, generating and returning access and refresh tokens.

    - **user_data**: OAuth2PasswordRequestForm containing the user's login credentials.
    - **db**: Database session dependency.

    Returns a `TokenSchema` containing:
    - **access_token**: JWT for accessing protected resources.
    - **refresh_token**: JWT for obtaining new access tokens.
    """
    user = authenticate_user(db, user_data.username, user_data.password)
    access_token = create_access_token(subject=user.user_name)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)
