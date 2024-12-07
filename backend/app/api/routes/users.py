from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.users import UsersService
from app.schemas.users import UserCreate, UserUpdate, User
from app.config.database import get_db
from app.services.auth import get_current_user, is_admin


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    response_description="The newly created user",
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db), dependencies=[Depends(is_admin)]) -> User:
    """
    Create a new user. Requires user information such as `name`, `email`, and `password`.

    - **name**: User's full name.
    - **email**: User's email address (must be unique).
    - **password**: User's password (encrypted on creation).
    """
    return UsersService.create_user(db, user_data)


@router.get(
    "/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    response_description="User details by ID",
)
def get_user(user_id: int, db: Session = Depends(get_db), dependencies=[Depends(is_admin)]) -> User:
    """
    Retrieve user details by user ID.
    - **user_id**: The ID of the user to retrieve.
    """
    user = UsersService.get_user_by_id(db, user_id)
    return user


@router.get(
    "/email/{email}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Get user by email",
    response_description="User details by email",
)
def get_user_by_email(email: str, db: Session = Depends(get_db), dependencies=[Depends(is_admin)]) -> User:
    """
    Retrieve user details by email address.
    - **email**: The email of the user to retrieve.
    """
    user = UsersService.get_user_by_email(db, email)
    return user


@router.put(
    "/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update user information",
    response_description="Updated user information",
)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), dependencies=[Depends(is_admin)]) -> User:
    """
    Update an existing user's information. Fields that are not provided will not be updated.
    - **user_id**: The ID of the user to update.
    - **user_data**: The fields to update (optional).
    """
    try:
        return UsersService.update_user(db, user_id, user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the user: {str(e)}",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    response_description="Successfully deleted the user",
)
def delete_user(user_id: int, db: Session = Depends(get_db), dependencies=[Depends(is_admin)]):
    """
    Delete a user by ID. This will permanently remove the user from the system.
    - **user_id**: The ID of the user to delete.
    """
    try:
        UsersService.delete_user(db, user_id)
        return {"message": "User deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the user: {str(e)}",
        )


@router.get(
    "/",
    response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    response_description="List of all users",
)
def get_all_users(db: Session = Depends(get_db), dependencies=[Depends(is_admin)]):
    """
    Retrieve a list of all users in the system.
    """
    return UsersService.get_all_users(db)
