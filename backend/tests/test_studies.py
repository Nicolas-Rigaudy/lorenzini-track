from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_studies_returns_list():
    response = client.get("/studies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_study_404_for_unknown_id():
    response = client.get("/studies/999999")
    assert response.status_code == 404
