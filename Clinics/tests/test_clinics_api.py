import pytest

@pytest.mark.anyio
async def test_create_clinic(client):
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
    assert data["owner_id"] > 1
    assert data["id"] > 0


@pytest.mark.anyio
async def test_get_clinic_by_id(client):
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

    resp = await client.get(f"/clinics/{cid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cid


@pytest.mark.anyio
async def test_get_clinic_by_name(client):
    payload = {
        "name": "Happy Pets",
        "description": "Pet care",
        "phone": "0779876543",
        "address": "Galle",
        "profile_pic_url": None,
        "area_id": None
    }

    await client.post("/clinics/", json=payload)

    resp = await client.get("/clinics/by-name/Happy Pets")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Happy Pets"


@pytest.mark.anyio
async def test_get_clinic_by_phone(client):
    payload = {
        "name": "Pet Zone",
        "description": "Care",
        "phone": "0775555555",
        "address": "Matara",
        "profile_pic_url": None,
        "area_id": None
    }

    created = await client.post("/clinics/", json=payload)
    stored_phone = created.json()["phone"]

    resp = await client.get(f"/clinics/by-phone/{payload['phone']}")
    assert resp.status_code == 200
    assert resp.json()["phone"] == stored_phone


@pytest.mark.anyio
async def test_list_clinics(client):

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

    for p in payloads:
        await client.post("/clinics/", json=p)

    resp = await client.get("/clinics/?limit=10&offset=0")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.anyio
async def test_update_clinic(client):

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

    update_data = {"name": "New Clinic"}
    resp2 = await client.patch(f"/clinics/{cid}", json=update_data)

    assert resp2.status_code == 200
    assert resp2.json()["name"] == "New Clinic"


from app.auth.security import get_current_active_user

@pytest.mark.anyio
async def test_delete_clinic(client):


    payload = {
        "name": "Delete Me",
        "description": "Temp",
        "phone": "0772222222",
        "address": "Road",
        "profile_pic_url": None,
        "area_id": None
    }

    # create
    resp = await client.post("/clinics/", json=payload)
    assert resp.status_code == 201
    cid = resp.json()["id"]

    # delete
    del_resp = await client.delete(f"/clinics/{cid}")
    assert del_resp.status_code == 204

    # verify gone
    get_resp = await client.get(f"/clinics/{cid}")
    assert get_resp.status_code == 404