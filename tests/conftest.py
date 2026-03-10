import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import pytest
from fastapi.testclient import TestClient

from main import app


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _register_or_login(client: TestClient, role: str, name: str, password: str) -> dict:
    if role == "admin":
        register_path = "/auth/admin"
    else:
        register_path = "/auth"

    register_resp = client.post(register_path, json={"name": name, "password": password})
    if register_resp.status_code == 201:
        user = register_resp.json()["user"]
        return {
            "id": user.get("id") or user.get("sub"),
            "name": name,
            "token": user["token"],
            "role": user.get("role"),
        }

    if register_resp.status_code not in (400, 409):
        raise RuntimeError(
            f"Unexpected register response for {role}: {register_resp.status_code} {register_resp.text}"
        )

    login_resp = client.post("/auth/login", json={"name": name, "password": password})
    if login_resp.status_code != 200:
        raise RuntimeError(
            f"Login failed for {role}: {login_resp.status_code} {login_resp.text}"
        )
    user = login_resp.json()["user"]
    return {
        "id": user.get("id") or user.get("sub"),
        "name": name,
        "token": user["token"],
        "role": user.get("role"),
    }


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def test_users(client: TestClient):
    admin_name = _require_env("TEST_ADMIN_NAME")
    admin_password = _require_env("TEST_ADMIN_PASSWORD")
    user_name = _require_env("TEST_USER_NAME")
    user_password = _require_env("TEST_USER_PASSWORD")
    other_user_name = _require_env("TEST_USER2_NAME")
    other_user_password = _require_env("TEST_USER2_PASSWORD")

    admin = _register_or_login(client, "admin", admin_name, admin_password)
    user = _register_or_login(client, "user", user_name, user_password)
    other_user = _register_or_login(client, "user", other_user_name, other_user_password)

    yield {"admin": admin, "user": user, "other_user": other_user}

    admin_headers = {"Authorization": f"Bearer {admin['token']}"}
    client.delete(f"/admin/users/{user['id']}", headers=admin_headers)
    client.delete(f"/admin/users/{other_user['id']}", headers=admin_headers)
    client.delete(f"/users/{admin['id']}", headers=admin_headers)


@pytest.fixture(scope="session")
def admin_token(test_users):
    return test_users["admin"]["token"]


@pytest.fixture(scope="session")
def user_token(test_users):
    return test_users["user"]["token"]


@pytest.fixture(scope="session")
def other_user_token(test_users):
    return test_users["other_user"]["token"]
