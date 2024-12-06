from fastapi import APIRouter, status
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html


router = APIRouter()

favicon_path = 'static/favicon.ico'


@router.get("/", tags=["Root"], status_code=status.HTTP_200_OK)
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Bahmni Copilot"}


@router.get("/health", tags=["Health"], summary="Perform a Health Check", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


@router.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Bahmni - Copilot", swagger_favicon_url=favicon_path)


@router.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="Bahmni - Copilot", redoc_favicon_url=favicon_path)
