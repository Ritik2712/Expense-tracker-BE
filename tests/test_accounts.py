def test_accounts_routes_auth_and_payloads(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_headers = {"Authorization": "Bearer invalid.token.value"}

    # create account - success
    create_resp = client.post("/accounts", json={"name": "Checking"}, headers=headers)
    assert create_resp.status_code == 201
    account_id = create_resp.json()["account"]["id"]

    # list accounts - success
    list_resp = client.get("/accounts", headers=headers)
    assert list_resp.status_code == 200

    # missing token
    assert client.get("/accounts").status_code == 401
    assert client.post("/accounts", json={"name": "X"}).status_code == 401

    # invalid token
    assert client.get("/accounts", headers=invalid_headers).status_code == 401
    assert client.post("/accounts", json={"name": "X"}, headers=invalid_headers).status_code == 401

    # invalid payloads
    invalid_create = client.post("/accounts", json={"name": ""}, headers=headers)
    assert invalid_create.status_code == 422

    invalid_update = client.put(
        f"/accounts/{account_id}",
        json={"name": "New", "balance": -10},
        headers=headers,
    )
    assert invalid_update.status_code == 422


def test_user_cannot_access_other_account(client, user_token, other_user_token):
    other_headers = {"Authorization": f"Bearer {other_user_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    other_account_resp = client.post(
        "/accounts",
        json={"name": "Other Account"},
        headers=other_headers,
    )
    assert other_account_resp.status_code == 201
    other_account_id = other_account_resp.json()["account"]["id"]

    update_resp = client.put(
        f"/accounts/{other_account_id}",
        json={"name": "Hack", "balance": 1},
        headers=user_headers,
    )
    assert update_resp.status_code == 404

    delete_resp = client.delete(f"/accounts/{other_account_id}", headers=user_headers)
    assert delete_resp.status_code == 404


def test_admin_get_account_by_id(client, admin_token, user_token):
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    account_resp = client.post(
        "/accounts",
        json={"name": "Admin Get Account"},
        headers=user_headers,
    )
    assert account_resp.status_code == 201
    account_id = account_resp.json()["account"]["id"]

    resp = client.get(f"/admin/accounts/{account_id}", headers=admin_headers)
    assert resp.status_code == 200
    invalid_resp = client.get("/admin/accounts/not-a-uuid", headers=admin_headers)
    assert invalid_resp.status_code == 422


def test_invalid_uuid_and_negative_pagination_on_accounts(client, user_token, admin_token):
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    assert client.put(
        "/accounts/not-a-uuid",
        json={"name": "X", "balance": 1},
        headers=user_headers,
    ).status_code == 422

    assert client.delete("/accounts/not-a-uuid", headers=user_headers).status_code == 422

    assert client.get("/accounts?page=-1&limit=10", headers=user_headers).status_code == 422
    assert client.get("/accounts?page=1&limit=-5", headers=user_headers).status_code == 422

    assert client.get("/admin/accounts?page=-1&limit=10", headers=admin_headers).status_code == 422
    assert client.get("/admin/accounts?page=1&limit=-5", headers=admin_headers).status_code == 422
