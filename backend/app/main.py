from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from app.api.routes.root import router as root_router
from app.config.database import create_tables, db_engine
import app.models.fields as fields
import app.models.forms as forms
import app.models.transcriptions as transcriptions
import app.models.users as users


def get_application():
    app = FastAPI(
        title="Bahmni Copilot",
        description=(
            "Bahmni Copilot provides the ability to take user speech, transcribe it into text, "
            "and use this text to automatically fill out forms in the Bahmni EMR system. It "
            "combines natural language processing (NLP) and advanced machine learning models to "
            "recognize form fields and match relevant data from the transcription."
        ),
        version="1.0.0",
        docs_url=None,
        redoc_url=None
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    app.include_router(root_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    create_tables([forms.Base, fields.Base, users.Base, transcriptions.Base], db_engine)

    return app


app = get_application()
