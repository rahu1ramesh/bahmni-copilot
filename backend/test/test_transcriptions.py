import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import status, UploadFile
from app.main import app
from app.config.database import get_db
from app.services.transcriptions import TranscriptionService
from app.schemas.forms import FormCreate
from app.services.fields import FieldsService, FieldCreate
from app.services.forms import FormsService
from app.models.users import Users
from app.models.transcriptions import Transcriptions
from app.models.fields import Fields
from app.models.forms import Forms
from app.services.auth import create_access_token

client = TestClient(app)


def override_get_db():
    from app.config.database import SessionLocal

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def upload_file():
    file_content = b"fake audio content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test.mp3"
    file.file = MagicMock()
    file.file.read.return_value = file_content
    return file


@pytest.fixture
def mock_s3_utils():
    with patch("app.utils.s3.S3Utils.upload_file") as mock:
        yield mock


@pytest.fixture
def mock_openai_utils():
    with patch("app.utils.openai.OpenAIUtils.transcribe_audio") as mock_transcribe, patch(
        "app.utils.openai.OpenAIUtils.prepare_context"
    ) as mock_prepare_context:
        mock_transcribe.return_value = "transcribed text"
        mock_prepare_context.return_value = {"key": "value"}
        yield mock_transcribe, mock_prepare_context


@pytest.fixture
def mock_fields_service():
    with patch("app.services.fields.FieldsService.get_fields_by_form_id") as mock:
        mock.return_value = [MagicMock(name="field1", description="desc1")]
        yield mock


@pytest.fixture
def test_db():
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Transcriptions).delete()
        db.query(Fields).delete()
        db.query(Forms).delete()
        db.query(Users).delete()
        db.commit()
        db.close()


@pytest.fixture
def admin_user(test_db: Session):
    user_data = {
        "user_name": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword",
        "is_admin": True,
    }
    user = Users(**user_data)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(admin_user):
    access_token = create_access_token(subject=admin_user.user_name)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def create_form(test_db: Session):
    form_data = FormCreate(name="Test Form")
    form = FormsService.create_form(test_db, form_data)
    return form


@pytest.fixture
def create_fields(test_db: Session, create_form):
    form_data = FieldCreate(name="Test Form Field", form_id=create_form.id)
    form = FieldsService.create_field(test_db, form_data)
    return form


def test_create_transcription_service(db_session, upload_file, mock_s3_utils, mock_openai_utils, mock_fields_service):
    transcription = TranscriptionService.create_transcription(db=db_session, user_id=1, form_id=1, file=upload_file)

    assert transcription.upload_uuid is not None
    assert transcription.user_id == 1
    assert transcription.form_id == 1
    assert transcription.transcription_text == "transcribed text"
    assert transcription.status == "completed"
    assert transcription.context == {"key": "value"}

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

    mock_s3_utils.assert_called_once()
    mock_openai_utils[0].assert_called_once()
    mock_openai_utils[1].assert_called_once()


def test_create_transcription_endpoint(
    db_session,
    upload_file,
    mock_s3_utils,
    mock_openai_utils,
    mock_fields_service,
    create_form,
    create_fields,
    auth_headers,
):
    response = client.post(
        f"/api/transcriptions/{create_form.id}",
        files={"file": ("test.mp3", upload_file.file.read(), "audio/mpeg")},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["form_id"] == create_form.id
    assert data["transcription_text"] == "transcribed text"
    assert data["status"] == "completed"
    assert data["context"] == {"key": "value"}


def test_create_transcription_unsupported_file_type(
    db_session,
    upload_file,
    mock_s3_utils,
    mock_openai_utils,
    mock_fields_service,
    create_form,
    create_fields,
    auth_headers,
):
    response = client.post(
        f"/api/transcriptions/{create_form.id}",
        files={"file": ("test.txt", upload_file.file.read(), "audio/mpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_transcription_s3_upload_failure(
    db_session, upload_file, mock_openai_utils, mock_fields_service, create_form, create_fields, auth_headers
):
    with patch("app.utils.s3.S3Utils.upload_file", side_effect=ValueError("S3 upload failed")):
        response = client.post(
            f"/api/transcriptions/{create_form.id}",
            files={"file": ("test.mp3", upload_file.file.read(), "audio/mpeg")},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_424_FAILED_DEPENDENCY
        assert "Failed to upload audio file: S3 upload failed" in response.json()["detail"]
