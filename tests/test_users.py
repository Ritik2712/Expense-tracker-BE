import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/admin/users",
        "/admin/accounts",
        "/admin/transactions",
    ],
)
def test_admin_routes_require_admin_token(client, admin_token, user_token, path):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    invalid_headers = {"Authorization": "Bearer corrupted.token.value"}

    admin_resp = client.get(path, headers=admin_headers)
    assert admin_resp.status_code == 200

    user_resp = client.get(path, headers=user_headers)
    assert user_resp.status_code == 403

    missing_resp = client.get(path)
    assert missing_resp.status_code == 401

    invalid_resp = client.get(path, headers=invalid_headers)
    assert invalid_resp.status_code == 401


def test_user_routes_auth_and_payloads(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_headers = {"Authorization": "Bearer corrupted.token.value"}

    # fetch me - success
    me_resp = client.get("/users/me", headers=headers)
    assert me_resp.status_code == 200

    user_id = me_resp.json()["user"]["id"]

    # missing token
    assert client.get("/users/me").status_code == 401

    # invalid token
    assert client.get("/users/me", headers=invalid_headers).status_code == 401

    # invalid payload (name too short)
    invalid_update = client.put(
        f"/users/update/{user_id}",
        json={"name": "ab"},
        headers=headers,
    )
    assert invalid_update.status_code == 422


def test_user_cannot_access_other_user(client, user_token, test_users):
    other_user_id = test_users["other_user"]["id"]
    headers = {"Authorization": f"Bearer {user_token}"}

    update_resp = client.put(
        f"/users/update/{other_user_id}",
        json={"name": "newname"},
        headers=headers,
    )
    assert update_resp.status_code == 404

    delete_resp = client.delete(f"/users/{other_user_id}", headers=headers)
    assert delete_resp.status_code == 404


def test_admin_get_user_by_id(client, admin_token, test_users):
    user_id = test_users["user"]["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(f"/admin/users/{user_id}", headers=headers)
    assert resp.status_code == 200
    invalid_resp = client.get("/admin/users/not-a-uuid", headers=headers)
    assert invalid_resp.status_code == 422


def test_invalid_uuid_and_negative_pagination_on_users(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    assert client.get("/admin/users?page=-1&limit=10", headers=headers).status_code == 422
    assert client.get("/admin/users?page=1&limit=-5", headers=headers).status_code == 422
