# tests/test_users.py
import pytest


@pytest.mark.anyio
async def test_get_all_users_requires_auth(async_client):
    r = await async_client.get("/users/")
    assert r.status_code == 401


@pytest.mark.anyio
async def test_get_all_users_with_token(async_client, test_user_token, db_session):
    # Promote token user to admin for this test
    from app.models.user_model import User
    from sqlalchemy import select

    token = test_user_token["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    result = await db_session.execute(
        select(User).where(User.email == "tokenuser@example.com")
    )
    admin_user = result.scalar_one()
    admin_user.role = "admin"
    admin_user.is_active = True
    await db_session.commit()

    # Create another user
    new_user_payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "bobstrongpw",
        "role": "owner"
    }
    reg = await async_client.post("/auth/register", json=new_user_payload)
    assert reg.status_code in (201, 409)

    r = await async_client.get("/users/?limit=10&offset=0", headers=headers)
    assert r.status_code == 200

    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert body["total"] >= 1


@pytest.mark.anyio
async def test_get_user_by_id_and_delete(async_client, test_user_token, db_session):
    from app.models.user_model import User
    from sqlalchemy import select

    token = test_user_token["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Promote token user to admin
    result = await db_session.execute(
        select(User).where(User.email == "tokenuser@example.com")
    )
    admin_user = result.scalar_one()
    admin_user.role = "admin"
    admin_user.is_active = True
    await db_session.commit()

    payload = {
        "name": "ToDelete",
        "email": "todelete@example.com",
        "password": "deletepw123",
        "role": "owner"
    }
    reg = await async_client.post("/auth/register", json=payload)
    assert reg.status_code in (201, 409)

    r = await async_client.get("/users/?limit=50&offset=0", headers=headers)
    assert r.status_code == 200

    users = r.json()["data"]
    target = next((u for u in users if u["email"] == payload["email"]), None)
    assert target is not None

    user_id = target["id"]

    r2 = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["data"]["email"] == payload["email"]

    r3 = await async_client.delete(f"/users/{user_id}", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["success"] is True

    r4 = await async_client.get(f"/users/{user_id}", headers=headers)
    assert r4.status_code == 404