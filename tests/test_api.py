from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_person_contains_required_fields():
    response = client.get("/api/person?gender=female&min_age=20&max_age=30&seed=demo")
    assert response.status_code == 200

    data = response.json()
    assert data["is_synthetic"] is True
    assert data["gender"] == "female"
    assert 20 <= data["birth"]["age"] <= 30
    assert data["name"]["vietnamese_full_name"]
    assert data["name"]["english_full_name"]
    assert data["name"]["family_name"]
    assert data["name"]["given_name"]


def test_seed_is_deterministic():
    first = client.get("/api/person?seed=fixed").json()
    second = client.get("/api/person?seed=fixed").json()
    assert first == second


def test_invalid_age_range():
    response = client.get("/api/person?min_age=50&max_age=20")
    assert response.status_code == 422
