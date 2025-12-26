import pytest
from io import BytesIO


def fake_image():
    return ("test.jpg", BytesIO(b"fake-image-bytes"), "image/jpeg")


@pytest.mark.anyio
async def test_owner_can_upload_report_image(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Dog",
            "condition": "Injured",
            "description": "Dog near road",
            "address": "Colombo",
        },
    )
    report_id = create.json()["id"]

    resp = await async_client.post(
        f"/reports/{report_id}/images",
        headers=headers,
        files={"file": fake_image()},
    )

    assert resp.status_code == 201


@pytest.mark.anyio
async def test_admin_can_upload_report_image(
        async_client,
        admin_token,
        owner_token,
):
    # Owner creates the report
    owner_headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=owner_headers,
        data={
            "animal_type": "Cat",
            "condition": "Injured",
            "description": "Cat stuck",
            "address": "Kandy",
        },
    )
    report_id = create.json()["id"]

    # Admin uploads image to owner's report - should succeed
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    resp = await async_client.post(
        f"/reports/{report_id}/images",
        headers=admin_headers,  # Using admin_token now
        files={"file": fake_image()},
    )

    assert resp.status_code == 201


@pytest.mark.anyio
async def test_other_user_cannot_upload_image(
        async_client,
        owner_token,
        welfare_token,
):
    # Owner creates the report
    owner_headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

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

    # Different user (welfare) tries to upload - should be forbidden
    welfare_headers = {"Authorization": f"Bearer {welfare_token['access_token']}"}
    resp = await async_client.post(
        f"/reports/{report_id}/images",
        headers=welfare_headers,  # Using welfare_token now
        files={"file": fake_image()},
    )

    assert resp.status_code == 403


@pytest.mark.anyio
async def test_owner_can_list_report_images(async_client, owner_token):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    create = await async_client.post(
        "/reports/",
        headers=headers,
        data={
            "animal_type": "Dog",
            "condition": "Bleeding",
            "description": "Urgent",
            "address": "Negombo",
        },
    )
    report_id = create.json()["id"]

    await async_client.post(
        f"/reports/{report_id}/images",
        headers=headers,
        files={"file": fake_image()},
    )

    # PUBLIC READ (no auth required)
    resp = await async_client.get(f"/reports/{report_id}/images")

    assert resp.status_code == 200
    assert len(resp.json()) == 1