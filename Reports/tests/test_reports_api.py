import pytest


@pytest.mark.anyio
async def test_create_report(async_client, welfare_token):
    headers = {"Authorization": f"Bearer {welfare_token['access_token']}"}

    resp = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Dog",
            "condition": "Broken leg",
            "description": "Dog injured near road",
            "address": "Colombo",
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["animal_type"] == "Dog"
    assert body["status"] == "OPEN"


@pytest.mark.anyio
async def test_list_reports_public(async_client):
    resp = await async_client.get("/reports/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_owner_can_read_own_report(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Cat",
            "condition": "Injured",
            "description": "Cat stuck",
            "address": "Kandy",
        },
    )
    report_id = create.json()["id"]

    resp = await async_client.get(
        f"/reports/{report_id}",
        headers=headers,
    )
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_other_user_cannot_read_report(async_client, owner_token, welfare_token):
    owner_headers = {"Authorization": f"Bearer {owner_token['access_token']}"}
    welfare_headers = {"Authorization": f"Bearer {welfare_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=owner_headers,
        data={
            "animal_type": "Bird",
            "condition": "Wing injury",
            "description": "Cannot fly",
            "address": "Galle",
        },
    )
    report_id = create.json()["id"]

    resp = await async_client.get(
        f"/reports/{report_id}",
        headers=welfare_headers,
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_admin_update_report_status(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Cow",
            "condition": "Severe injury",
            "description": "Collapsed on road",
            "address": "Matara",
        },
    )
    report_id = create.json()["id"]

    resp = await async_client.patch(
        f"/reports/{report_id}/status",
        headers=headers,
        json={"status": "RESCUED"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "RESCUED"