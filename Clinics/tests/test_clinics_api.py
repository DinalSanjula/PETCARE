import pytest
from sqlalchemy import select

from Clinics.models.models import Clinic


# --------------------------------------------------
# Helper: activate clinic (admin action)
# --------------------------------------------------
async def activate_clinic(db_session, clinic_id: int):
    result = await db_session.execute(
        select(Clinic).where(Clinic.id == clinic_id)
    )
    clinic = result.scalar_one()
    clinic.is_active = True
    await db_session.commit()
    await db_session.refresh(clinic)
    return clinic


# --------------------------------------------------
# CREATE CLINIC
# --------------------------------------------------
@pytest.mark.anyio
async def test_create_clinic_as_clinic_user(
    async_client,
    clinic_token,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payload = {
        "name": "Golden Vet",
        "description": "Good clinic",
        "phone": "0771234567",
        "address": "Kurunegala",
        "profile_pic_url": None,
        "area_id": None,
        "latitude": None,
        "longitude": None,
    }

    resp = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["id"] > 0
    assert data["is_active"] is False  # new clinics start inactive


@pytest.mark.anyio
async def test_owner_cannot_create_clinic(
    async_client,
    owner_token,
):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    resp = await async_client.post(
        "/clinics/",
        json={
            "name": "Hack Clinic",
            "description": "Nope",
            "phone": "0779999999",
            "address": "Somewhere",
            "profile_pic_url": None,
            "area_id": None,
        },
        headers=headers,
    )
    assert resp.status_code == 403


# --------------------------------------------------
# GET CLINIC (PUBLIC, ACTIVE ONLY)
# --------------------------------------------------
@pytest.mark.anyio
async def test_get_clinic_by_id(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payload = {
        "name": "City Vet",
        "description": "24/7 service",
        "phone": "0771111111",
        "address": "Colombo",
        "profile_pic_url": None,
        "area_id": None,
    }

    created = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    cid = created.json()["id"]

    # activate clinic (admin/system step)
    await activate_clinic(db_session, cid)

    resp = await async_client.get(f"/clinics/{cid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cid


@pytest.mark.anyio
async def test_get_clinic_by_name(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payload = {
        "name": "Happy Pets",
        "description": "Pet care",
        "phone": "0779876543",
        "address": "Galle",
        "profile_pic_url": None,
        "area_id": None,
    }

    created = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    cid = created.json()["id"]

    await activate_clinic(db_session, cid)

    resp = await async_client.get("/clinics/by-name/Happy Pets")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Happy Pets"


@pytest.mark.anyio
async def test_get_clinic_by_phone(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payload = {
        "name": "Pet Zone",
        "description": "Care",
        "phone": "0775555555",
        "address": "Matara",
        "profile_pic_url": None,
        "area_id": None,
    }

    created = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    cid = created.json()["id"]

    await activate_clinic(db_session, cid)

    resp = await async_client.get(f"/clinics/by-phone/{payload['phone']}")
    assert resp.status_code == 200
    assert resp.json()["phone"] == "+94775555555"


# --------------------------------------------------
# LIST CLINICS (PUBLIC)
# --------------------------------------------------
@pytest.mark.anyio
async def test_list_clinics(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payloads = [
        {
            "name": "One",
            "description": "Clinic 1",
            "phone": "0771999999",
            "address": "City A",
            "profile_pic_url": None,
            "area_id": None,
        },
        {
            "name": "Two",
            "description": "Clinic 2",
            "phone": "0771888888",
            "address": "City B",
            "profile_pic_url": None,
            "area_id": None,
        },
    ]

    ids = []
    for p in payloads:
        resp = await async_client.post(
            "/clinics/",
            json=p,
            headers=headers,
        )
        ids.append(resp.json()["id"])

    for cid in ids:
        await activate_clinic(db_session, cid)

    resp = await async_client.get("/clinics/?limit=10&offset=0")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


# --------------------------------------------------
# UPDATE CLINIC (OWNER CLINIC ONLY)
# --------------------------------------------------
@pytest.mark.anyio
async def test_update_clinic_as_owner(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    payload = {
        "name": "Old Clinic",
        "description": "Old desc",
        "phone": "0771000000",
        "address": "Old Road",
        "profile_pic_url": None,
        "area_id": None,
    }

    resp = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    cid = resp.json()["id"]

    await activate_clinic(db_session, cid)

    resp2 = await async_client.patch(
        f"/clinics/{cid}",
        json={"name": "New Clinic"},
        headers=headers,
    )

    assert resp2.status_code == 200
    assert resp2.json()["name"] == "New Clinic"


@pytest.mark.anyio
async def test_non_owner_cannot_update_clinic(
    async_client,
    clinic_token,
    owner_token,
):
    clinic_headers = {
        "Authorization": f"Bearer {clinic_token['access_token']}"
    }
    owner_headers = {
        "Authorization": f"Bearer {owner_token['access_token']}"
    }

    resp = await async_client.post(
        "/clinics/",
        json={
            "name": "Secure Clinic",
            "description": "Protected",
            "phone": "0773333333",
            "address": "City",
            "profile_pic_url": None,
            "area_id": None,
        },
        headers=clinic_headers,
    )
    cid = resp.json()["id"]

    resp2 = await async_client.patch(
        f"/clinics/{cid}",
        json={"name": "Hack"},
        headers=owner_headers,
    )
    assert resp2.status_code == 403


# --------------------------------------------------
# DELETE CLINIC (OWNER CLINIC ONLY)
# --------------------------------------------------
@pytest.mark.anyio
async def test_delete_clinic(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    resp = await async_client.post(
        "/clinics/",
        json={
            "name": "Delete Me",
            "description": "Temp",
            "phone": "0772222222",
            "address": "Road",
            "profile_pic_url": None,
            "area_id": None,
        },
        headers=headers,
    )
    cid = resp.json()["id"]

    await activate_clinic(db_session, cid)

    del_resp = await async_client.delete(
        f"/clinics/{cid}",
        headers=headers,
    )
    assert del_resp.status_code == 204

    get_resp = await async_client.get(f"/clinics/{cid}")
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_owner_cannot_delete_other_clinic(
    async_client,
    clinic_token,
    owner_token,
):
    clinic_headers = {
        "Authorization": f"Bearer {clinic_token['access_token']}"
    }
    owner_headers = {
        "Authorization": f"Bearer {owner_token['access_token']}"
    }

    resp = await async_client.post(
        "/clinics/",
        json={
            "name": "Protected Clinic",
            "description": "Temp",
            "phone": "0774444444",
            "address": "Road",
            "profile_pic_url": None,
            "area_id": None,
        },
        headers=clinic_headers,
    )
    cid = resp.json()["id"]

    del_resp = await async_client.delete(
        f"/clinics/{cid}",
        headers=owner_headers,
    )
    assert del_resp.status_code == 403