from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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

    return app


app = get_application()


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Bahmni Copilot"}
