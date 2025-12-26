import pytest


@pytest.mark.anyio
async def test_user_send_report_message(async_client, welfare_token):
    headers = {"Authorization": f"Bearer {welfare_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Dog",
            "condition": "Bleeding",
            "description": "Needs urgent help",
            "address": "Negombo",
        },
    )
    report_id = create.json()["id"]

    resp = await async_client.post(
        f"/reports/{report_id}/messages",
        headers=headers,
        json={"message": "Animal rescued by volunteers"},
    )

    assert resp.status_code == 201
    assert resp.json()["is_read"] is False


@pytest.mark.anyio
async def test_admin_reads_messages_marks_read(async_client, admin_token, welfare_token):
    welfare_headers = {"Authorization": f"Bearer {welfare_token['access_token']}"}
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=welfare_headers,
        data={
            "animal_type": "Dog",
            "condition": "Hit by vehicle",
            "description": "On roadside",
            "address": "Kurunegala",
        },
    )
    report_id = create.json()["id"]

    await async_client.post(
        f"/reports/{report_id}/messages",
        headers=welfare_headers,
        json={"message": "Rescue done"},
    )

    resp = await async_client.get(
        f"/reports/{report_id}/messages",
        headers=admin_headers,
    )

    assert resp.status_code == 200
    assert resp.json()[0]["is_read"] is True