from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bahmni Copilot"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_overridden_swagger():
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"<title>Bahmni - Copilot</title>" in response.content


def test_overridden_redoc():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert b"<title>Bahmni - Copilot</title>" in response.content
