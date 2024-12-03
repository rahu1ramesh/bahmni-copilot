from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from app.db.database import create_tables
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

    create_tables([forms.Base, fields.Base, users.Base, transcriptions.Base])

    return app


app = get_application()


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Bahmni Copilot"}


app.mount("/static", StaticFiles(directory="app/static"), name="static")
favicon_path = 'static/favicon.ico'


@app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Bahmni - Copilot", swagger_favicon_url=favicon_path)


@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="Bahmni - Copilot", redoc_favicon_url=favicon_path)
