# Users/tests/test_users.py
import pytest
from jose import jwt

@pytest.mark.anyio
async def test_get_all_users_requires_auth(async_client):
    r = await async_client.get("/users/")
    assert r.status_code == 401


@pytest.mark.anyio
async def test_get_all_users_admin_only(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}
    r = await async_client.get("/users/", headers=headers)
    assert r.status_code == 403


@pytest.mark.anyio
async def test_get_all_users_as_admin(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "bobstrongpw",
        "role": "owner",
    }
    await async_client.post("/auth/register", json=payload)

    r = await async_client.get("/users/?limit=10&offset=0", headers=headers)
    assert r.status_code == 200

    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert body["total"] >= 1


# --------------------------------------------------
# SELF ACCESS (via /users/{id})
# --------------------------------------------------
@pytest.mark.anyio
async def test_get_user_by_id_self_access(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    # decode JWT WITHOUT signature verification (test-only)
    payload = jwt.decode(
        owner_token["access_token"],
        key=None,
        options={"verify_signature": False}
    )
    user_id = payload["user_id"]

    r = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["id"] == user_id


@pytest.mark.anyio
async def test_user_cannot_get_other_user(async_client, owner_token, admin_token):
    owner_headers = {"Authorization": f"Bearer {owner_token['access_token']}"}
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    payload = {
        "name": "Other",
        "email": "other@example.com",
        "password": "otherpw123",
        "role": "owner",
    }
    await async_client.post("/auth/register", json=payload)

    users_resp = await async_client.get("/users/", headers=admin_headers)
    users = users_resp.json()["data"]

    target = next(u for u in users if u["email"] == payload["email"])

    r = await async_client.get(
        f"/users/{target['id']}",
        headers=owner_headers,
    )
    assert r.status_code == 403


@pytest.mark.anyio
async def test_admin_can_delete_user(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    payload = {
        "name": "ToDelete",
        "email": "todelete@example.com",
        "password": "deletepw123",
        "role": "owner",
    }
    await async_client.post("/auth/register", json=payload)

    r = await async_client.get("/users/", headers=headers)
    users = r.json()["data"]

    target = next(u for u in users if u["email"] == payload["email"])
    user_id = target["id"]

    del_resp = await async_client.delete(f"/users/{user_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    r2 = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r2.status_code == 404


@pytest.mark.anyio
async def test_non_admin_cannot_delete_user(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}
    r = await async_client.delete("/users/1", headers=headers)
    assert r.status_code == 403