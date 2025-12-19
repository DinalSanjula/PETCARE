import pytest
from sqlalchemy import select

from Clinics.models.models import Clinic


# --------------------------------------------------
# Helper: activate clinic
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


@pytest.mark.anyio
async def test_create_clinic(client, db_session):
    payload = {
        "name": "Golden Vet",
        "description": "Good clinic",
        "phone": "0771234567",
        "address": "Kurunegala",
        "profile_pic_url": None,
        "area_id": None,
        "latitude": None,
        "longitude": None
    }

    resp = await client.post("/clinics/", json=payload)
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["id"] > 0

    # Newly created clinics are inactive
    assert data["is_active"] is False


@pytest.mark.anyio
async def test_get_clinic_by_id(client, db_session):
    payload = {
        "name": "City Vet",
        "description": "24/7 service",
        "phone": "0771111111",
        "address": "Colombo",
        "profile_pic_url": None,
        "area_id": None
    }

    created = await client.post("/clinics/", json=payload)
    cid = created.json()["id"]

    # Activate clinic before public access
    await activate_clinic(db_session, cid)

    resp = await client.get(f"/clinics/{cid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cid


@pytest.mark.anyio
async def test_get_clinic_by_name(client, db_session):
    payload = {
        "name": "Happy Pets",
        "description": "Pet care",
        "phone": "0779876543",
        "address": "Galle",
        "profile_pic_url": None,
        "area_id": None
    }

    created = await client.post("/clinics/", json=payload)
    cid = created.json()["id"]

    await activate_clinic(db_session, cid)

    resp = await client.get("/clinics/by-name/Happy Pets")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Happy Pets"


@pytest.mark.anyio
async def test_get_clinic_by_phone(client, db_session):
    payload = {
        "name": "Pet Zone",
        "description": "Care",
        "phone": "0775555555",
        "address": "Matara",
        "profile_pic_url": None,
        "area_id": None
    }

    created = await client.post("/clinics/", json=payload)
    cid = created.json()["id"]

    await activate_clinic(db_session, cid)

    resp = await client.get(f"/clinics/by-phone/{payload['phone']}")
    assert resp.status_code == 200
    assert resp.json()["phone"] == "+94775555555"


@pytest.mark.anyio
async def test_list_clinics(client, db_session):
    payloads = [
        {
            "name": "One",
            "description": "Clinic 1",
            "phone": "0771999999",
            "address": "City A",
            "profile_pic_url": None,
            "area_id": None
        },
        {
            "name": "Two",
            "description": "Clinic 2",
            "phone": "0771888888",
            "address": "City B",
            "profile_pic_url": None,
            "area_id": None
        }
    ]

    ids = []
    for p in payloads:
        resp = await client.post("/clinics/", json=p)
        ids.append(resp.json()["id"])

    # Activate both clinics
    for cid in ids:
        await activate_clinic(db_session, cid)

    resp = await client.get("/clinics/?limit=10&offset=0")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.anyio
async def test_update_clinic(client, db_session):
    payload = {
        "name": "Old Clinic",
        "description": "Old desc",
        "phone": "0771000000",
        "address": "Old Road",
        "profile_pic_url": None,
        "area_id": None
    }

    resp = await client.post("/clinics/", json=payload)
    cid = resp.json()["id"]

    await activate_clinic(db_session, cid)

    update_data = {"name": "New Clinic"}
    resp2 = await client.patch(f"/clinics/{cid}", json=update_data)

    assert resp2.status_code == 200
    assert resp2.json()["name"] == "New Clinic"


@pytest.mark.anyio
async def test_delete_clinic(client, db_session):
    payload = {
        "name": "Delete Me",
        "description": "Temp",
        "phone": "0772222222",
        "address": "Road",
        "profile_pic_url": None,
        "area_id": None
    }

    resp = await client.post("/clinics/", json=payload)
    cid = resp.json()["id"]

    await activate_clinic(db_session, cid)

    del_resp = await client.delete(f"/clinics/{cid}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/clinics/{cid}")
    assert get_resp.status_code == 404