# tests/test_auth.py
import pytest

@pytest.mark.anyio
async def test_register_and_login(async_client):
    payload = {
        "name": "Alice Register",
        "email": "alice@example.com",
        "password": "verysecurepw",
        "role": "owner"
    }

    # Register
    r = await async_client.post("/auth/register", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["success"] is True
    assert body["data"] is not None
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]

    # Login with same credentials
    r2 = await async_client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["success"] is True
    assert body2["data"]["access_token"] is not None