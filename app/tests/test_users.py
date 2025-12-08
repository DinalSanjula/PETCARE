# tests/test_users.py
import pytest

@pytest.mark.anyio
async def test_get_all_users_requires_auth(async_client):
    # Without auth header should fail when calling secured endpoint
    r = await async_client.get("/users/")
    # Should be 401 because dependency oauth2_scheme tries to validate token
    assert r.status_code == 401

@pytest.mark.anyio
async def test_get_all_users_with_token(async_client, test_user_token):
    token = test_user_token["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create another user to ensure list returns >=1
    new_user_payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "bobstrongpw",
        "role": "owner"
    }
    reg = await async_client.post("/auth/register", json=new_user_payload)
    # allow either 201 or 409 (if already exists)
    assert reg.status_code in (201, 409)

    # Get list
    r = await async_client.get("/users/?limit=10&offset=0", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    # total should be >= 1
    assert body["total"] >= 1

@pytest.mark.anyio
async def test_get_user_by_id_and_delete(async_client, test_user_token):
    token = test_user_token["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # First, create a fresh user we can delete
    payload = {
        "name": "ToDelete",
        "email": "todelete@example.com",
        "password": "deletepw123",
        "role": "owner"
    }
    reg = await async_client.post("/auth/register", json=payload)
    assert reg.status_code in (201, 409)
    # If registration created user, token data returned; otherwise user exists.

    # Fetch users list to find the user's id
    r = await async_client.get("/users/?limit=50&offset=0", headers=headers)
    assert r.status_code == 200
    users = r.json()["data"]
    target = next((u for u in users if u["email"] == payload["email"]), None)
    assert target is not None, "Created user not found in users list"
    user_id = target["id"]

    # Get by id
    r2 = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["success"] is True
    assert body2["data"]["email"] == payload["email"]

    # Delete
    r3 = await async_client.delete(f"/users/{user_id}", headers=headers)
    assert r3.status_code == 200
    body3 = r3.json()
    assert body3["success"] is True

    # Confirm deleted -> get by id should 404
    r4 = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r4.status_code == 404