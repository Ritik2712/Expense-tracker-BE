from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_duplicate_user_creation(client, test_users):
    existing_name = test_users["user"]["name"]
    password = "dup_pass_123"
    resp = client.post("/auth", json={"name": existing_name, "password": password})
    assert resp.status_code == 400
