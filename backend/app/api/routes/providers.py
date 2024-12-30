from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.services.providers import ProvidersService
from app.schemas.providers import ProviderCreate, ProviderUpdate, Provider
from app.config.database import get_db
from app.services.auth import get_current_user, is_admin


router = APIRouter(prefix="/providers", tags=["Providers"], dependencies=[Depends(get_current_user)])


@router.post(
    "/",
    response_model=Provider,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new provider",
    response_description="The newly created provider",
    dependencies=[Depends(is_admin)],
)
def create_provider(provider_data: ProviderCreate, db: Session = Depends(get_db)) -> Provider:
    """
    Create a new provider. Requires provider information such as `user_id`, `name`, `specialty`, and `department_id`.

    - **user_id**: ID of the user associated with the provider.
    - **name**: Provider's full name.
    - **specialty**: Provider's specialty (optional, defaults to "General Medicine").
    - **department_id**: ID of the department associated with the provider.
    """
    return ProvidersService.create_provider(db, provider_data)


@router.get(
    "/{provider_id}",
    response_model=Provider,
    status_code=status.HTTP_200_OK,
    summary="Get provider by ID",
    response_description="Provider details by ID",
    dependencies=[Depends(is_admin)],
)
def get_provider(provider_id: int, db: Session = Depends(get_db)) -> Provider:
    """
    Retrieve provider details by provider ID.
    - **provider_id**: The ID of the provider to retrieve.
    """
    return ProvidersService.get_provider_by_id(db, provider_id)


@router.get(
    "/user/{user_id}",
    response_model=Provider,
    status_code=status.HTTP_200_OK,
    summary="Get provider by user ID",
    response_description="Provider details by user ID",
    dependencies=[Depends(is_admin)],
)
def get_provider_by_user_id(user_id: int, db: Session = Depends(get_db)) -> Provider:
    """
    Retrieve provider details by user ID.
    - **user_id**: The ID of the user to retrieve the provider for.
    """
    return ProvidersService.get_provider_by_user_id(db, user_id)


@router.put(
    "/{provider_id}",
    response_model=Provider,
    status_code=status.HTTP_200_OK,
    summary="Update provider information",
    response_description="Updated provider information",
    dependencies=[Depends(is_admin)],
)
def update_provider(provider_id: int, provider_data: ProviderUpdate, db: Session = Depends(get_db)) -> Provider:
    """
    Update an existing provider's information. Fields that are not provided will not be updated.
    - **provider_id**: The ID of the provider to update.
    - **provider_data**: The fields to update (optional).
    """
    return ProvidersService.update_provider(db, provider_id, provider_data)


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a provider",
    response_description="Successfully deleted the provider",
    dependencies=[Depends(is_admin)],
)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """
    Delete a provider by ID. This will permanently remove the provider from the system.
    - **provider_id**: The ID of the provider to delete.
    """
    ProvidersService.delete_provider(db, provider_id)


@router.get(
    "/",
    response_model=list[Provider],
    status_code=status.HTTP_200_OK,
    summary="Get all providers",
    response_description="List of all providers",
    dependencies=[Depends(is_admin)],
)
def get_all_providers(db: Session = Depends(get_db)):
    """
    Retrieve a list of all providers in the system.
    """
    return ProvidersService.get_all_providers(db)
