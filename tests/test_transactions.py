def test_transactions_routes_auth_and_payloads(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_headers = {"Authorization": "Bearer invalid.token.value"}

    # create account for transactions
    account_resp = client.post("/accounts", json={"name": "Tx Account"}, headers=headers)
    assert account_resp.status_code == 201
    account_id = account_resp.json()["account"]["id"]

    # create transaction - success
    tx_resp = client.post(
        "/transactions",
        json={
            "amount": 10,
            "transaction_type": "Income",
            "description": "Initial",
            "account_id": account_id,
        },
        headers=headers,
    )
    assert tx_resp.status_code == 201

    # list by account - success
    list_resp = client.get(f"/transactions?account_id={account_id}", headers=headers)
    assert list_resp.status_code == 200

    # missing token
    assert client.get(f"/transactions?account_id={account_id}").status_code == 401
    assert (
        client.post(
            "/transactions",
            json={
                "amount": 10,
                "transaction_type": "Income",
                "description": "X",
                "account_id": account_id,
            },
        ).status_code
        == 401
    )

    # invalid token
    assert client.get(f"/transactions?account_id={account_id}", headers=invalid_headers).status_code == 401
    assert (
        client.post(
            "/transactions",
            json={
                "amount": 10,
                "transaction_type": "Income",
                "description": "X",
                "account_id": account_id,
            },
            headers=invalid_headers,
        ).status_code
        == 401
    )

    # invalid payloads
    invalid_payload = client.post(
        "/transactions",
        json={
            "amount": -5,
            "transaction_type": "Income",
            "description": "Bad",
            "account_id": account_id,
        },
        headers=headers,
    )
    assert invalid_payload.status_code == 422


def test_user_cannot_access_other_transactions(client, user_token, other_user_token):
    other_headers = {"Authorization": f"Bearer {other_user_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    other_account_resp = client.post(
        "/accounts",
        json={"name": "Other Tx Account"},
        headers=other_headers,
    )
    assert other_account_resp.status_code == 201
    other_account_id = other_account_resp.json()["account"]["id"]

    other_tx_resp = client.post(
        "/transactions",
        json={
            "amount": 5,
            "transaction_type": "Income",
            "description": "Other",
            "account_id": other_account_id,
        },
        headers=other_headers,
    )
    assert other_tx_resp.status_code == 201
    other_tx_id = other_tx_resp.json()["Transaction"]["id"]

    list_resp = client.get(
        f"/transactions?account_id={other_account_id}",
        headers=user_headers,
    )
    assert list_resp.status_code == 404

    get_resp = client.get(
        f"/transactions/{other_tx_id}?account_id={other_account_id}",
        headers=user_headers,
    )
    assert get_resp.status_code == 404

    update_resp = client.put(
        f"/transactions/{other_tx_id}",
        json={
            "amount": 6,
            "transaction_type": "Income",
            "description": "Hack",
            "account_id": other_account_id,
        },
        headers=user_headers,
    )
    assert update_resp.status_code == 404

    delete_resp = client.delete(
        f"/transactions/{other_tx_id}",
        headers=user_headers,
    )
    assert delete_resp.status_code == 404


def test_admin_get_transaction_by_id(client, admin_token, user_token):
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    account_resp = client.post(
        "/accounts",
        json={"name": "Admin Tx Account"},
        headers=user_headers,
    )
    assert account_resp.status_code == 201
    account_id = account_resp.json()["account"]["id"]

    tx_resp = client.post(
        "/transactions",
        json={
            "amount": 15,
            "transaction_type": "Income",
            "description": "Admin get",
            "account_id": account_id,
        },
        headers=user_headers,
    )
    assert tx_resp.status_code == 201
    tx_id = tx_resp.json()["Transaction"]["id"]

    resp = client.get(f"/admin/transactions/{tx_id}", headers=admin_headers)
    assert resp.status_code == 200
    invalid_resp = client.get("/admin/transactions/not-a-uuid", headers=admin_headers)
    assert invalid_resp.status_code == 422


def test_invalid_uuid_and_negative_pagination_on_transactions(client, user_token, admin_token):
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    assert client.get("/transactions/not-a-uuid?account_id=bad", headers=user_headers).status_code == 422
    assert client.delete("/transactions/not-a-uuid", headers=user_headers).status_code == 422

    assert client.get("/transactions?account_id=bad&page=1&limit=10", headers=user_headers).status_code == 422
    assert client.get("/transactions?account_id=bad&page=-1&limit=10", headers=user_headers).status_code == 422
    assert client.get("/transactions?account_id=bad&page=1&limit=-5", headers=user_headers).status_code == 422

    assert client.get("/admin/transactions?page=-1&limit=10", headers=admin_headers).status_code == 422
    assert client.get("/admin/transactions?page=1&limit=-5", headers=admin_headers).status_code == 422
