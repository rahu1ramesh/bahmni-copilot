from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.departments import router as departments_router
from app.api.routes.forms import router as forms_router
from app.api.routes.fields import router as fields_router
from app.api.routes.patients import router as patients_router
from app.api.routes.users import router as users_router
from app.api.routes.transcriptions import router as transcriptions_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(departments_router)
router.include_router(forms_router)
router.include_router(fields_router)
router.include_router(patients_router)
router.include_router(users_router)
router.include_router(transcriptions_router)
