from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_occurrences_returns_feature_collection():
    response = client.get("/occurrences")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert isinstance(body["features"], list)
