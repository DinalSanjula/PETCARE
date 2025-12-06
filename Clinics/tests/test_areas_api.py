import pytest
from sqlalchemy import select
from Clinics.models.models import Area

@pytest.mark.anyio
async def test_create_area_returns_201_and_persists(client, async_session):
    payload = {
        "name": "Testville",
        "main_region": "North",
        # formatted_address, coords optional
    }
    resp = await client.post("/areas/admin", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "Testville"
    assert "id" in data

    # verify DB row exists
    result = await async_session.execute(select(Area).where(Area.name == "Testville"))
    row = result.scalar_one_or_none()
    assert row is not None
    assert row.main_region == "North"

@pytest.mark.anyio
async def test_list_areas_and_pagination(client):
    # create a few areas
    await client.post("/areas/admin", json={"name": "A1", "main_region": "R1"})
    await client.post("/areas/admin", json={"name": "A2", "main_region": "R1"})
    await client.post("/areas/admin", json={"name": "B1", "main_region": "R2"})

    resp = await client.get("/areas?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2

    # filter by region
    resp2 = await client.get("/areas?main_region=R1")
    assert resp2.status_code == 200
    names = [a["name"] for a in resp2.json()]
    assert "A1" in names and "A2" in names

@pytest.mark.anyio
async def test_get_area_by_id_returns_404_for_missing(client):
    resp = await client.get("/areas/99999")
    assert resp.status_code == 404

@pytest.mark.anyio
async def test_update_area_changes_fields_and_triggers_regeocode(client, async_session):
    # create
    resp = await client.post("/areas/admin", json={"name": "UpdTown", "main_region": "MR"})
    assert resp.status_code == 201
    created = resp.json()
    area_id = created["id"]

    # update name
    resp2 = await client.patch(f"/areas/admin/{area_id}", json={"name": "UpdatedName"})
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["name"] == "UpdatedName"

@pytest.mark.anyio
async def test_autocomplete_prefix_and_substring(client):
    # ensure known items exist
    await client.post("/areas/admin", json={"name": "AlphaCity", "main_region": "X"})
    await client.post("/areas/admin", json={"name": "BetaTown", "main_region": "X"})
    await client.post("/areas/admin", json={"name": "GammaVillage", "main_region": "X"})

    resp = await client.get("/areas/autocomplete?q=Al&limit=5")
    assert resp.status_code == 200
    names = [a["name"] for a in resp.json()]
    assert any("Alpha" in n for n in names)

    # substring search
    resp2 = await client.get("/areas/autocomplete?q=ma&limit=5")
    assert resp2.status_code == 200
    names2 = [a["name"] for a in resp2.json()]
    assert any("Gamma" in n for n in names2)

@pytest.mark.anyio
async def test_delete_area_and_404_on_missing(client):
    # create
    resp = await client.post("/areas/admin", json={"name": "ToDelete", "main_region": "D"})
    assert resp.status_code == 201
    area_id = resp.json()["id"]

    # delete
    resp2 = await client.delete(f"/areas/admin/{area_id}")
    assert resp2.status_code == 204

    # confirm gone
    resp3 = await client.get(f"/areas/{area_id}")
    assert resp3.status_code == 404