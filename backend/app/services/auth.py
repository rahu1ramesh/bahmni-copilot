import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Union, Any
from app.models.users import Users
from app.config.database import get_db


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_schema = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="JWT"
)


def get_hashed_password(password: str) -> str:
    """Hash the given password using bcrypt."""
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify the given password against the hashed password."""
    return password_context.verify(password, hashed_pass)


def create_token(subject: Union[str, Any], secret_key: str, expires_delta: timedelta) -> str:
    """Create a JWT token."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(subject: Union[str, Any]) -> str:
    """Create an access token."""
    return create_token(subject, JWT_SECRET_KEY, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create a refresh token."""
    return create_token(subject, JWT_REFRESH_SECRET_KEY, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))


def get_user(db: Session, user_name: str) -> Users:
    """Retrieve a user by username."""
    user = db.query(Users).filter(Users.user_name == user_name).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {user_name} not found"
        )
    return user


def authenticate_user(db: Session, user_name: str, password: str) -> Users:
    """Authenticate a user by username and password."""
    user = get_user(db, user_name)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth_schema)) -> Users:
    """Retrieve the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        user = get_user(db, user_name=user_name)
        return user
    except JWTError:
        raise credentials_exception

def is_admin(user: Users = Depends(get_current_user)):
    """Check if the user is an admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return user