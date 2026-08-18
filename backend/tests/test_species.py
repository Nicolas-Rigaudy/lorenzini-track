from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_species_returns_list():
    response = client.get("/species")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    for item in body:
        assert "scientific_name" in item
        assert "record_count" in item


def test_get_species_detail_has_histogram():
    listing = client.get("/species").json()
    if not listing:
        return  # no data ingested in this environment
    name = listing[0]["scientific_name"]
    response = client.get(f"/species/{name}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["monthly_histogram"]) == 12
    assert "facts" in body


def test_get_species_404_for_unknown():
    response = client.get("/species/Nonexistent nonexistent")
    assert response.status_code == 404
