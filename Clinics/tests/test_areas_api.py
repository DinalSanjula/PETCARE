import pytest
from sqlalchemy import select
from Clinics.models.models import Area


# ---------------------------------------------------------
# CREATE AREA (ADMIN ONLY)
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_create_area_returns_201_and_persists(
    async_client,
    admin_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    payload = {
        "name": "Testville",
        "main_region": "North",
    }

    resp = await async_client.post(
        "/areas/admin",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["name"] == "Testville"
    assert "id" in data

    # verify DB row exists
    result = await db_session.execute(
        select(Area).where(Area.name == "Testville")
    )
    row = result.scalar_one_or_none()
    assert row is not None
    assert row.main_region == "North"


@pytest.mark.anyio
async def test_create_area_requires_admin(
    async_client,
    owner_token,
):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    resp = await async_client.post(
        "/areas/admin",
        json={"name": "Nope", "main_region": "X"},
        headers=headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------
# LIST & FILTER AREAS (PUBLIC)
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_list_areas_and_pagination(
    async_client,
    admin_token,
):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    await async_client.post(
        "/areas/admin",
        json={"name": "A1", "main_region": "R1"},
        headers=headers,
    )
    await async_client.post(
        "/areas/admin",
        json={"name": "A2", "main_region": "R1"},
        headers=headers,
    )
    await async_client.post(
        "/areas/admin",
        json={"name": "B1", "main_region": "R2"},
        headers=headers,
    )

    resp = await async_client.get("/areas?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2

    # filter by region
    resp2 = await async_client.get("/areas?main_region=R1")
    assert resp2.status_code == 200
    names = [a["name"] for a in resp2.json()]
    assert "A1" in names
    assert "A2" in names


# ---------------------------------------------------------
# GET AREA
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_get_area_by_id_returns_404_for_missing(async_client):
    resp = await async_client.get("/areas/99999")
    assert resp.status_code == 404


# ---------------------------------------------------------
# UPDATE AREA (ADMIN ONLY)
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_update_area_changes_fields(
    async_client,
    admin_token,
):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    resp = await async_client.post(
        "/areas/admin",
        json={"name": "UpdTown", "main_region": "MR"},
        headers=headers,
    )
    assert resp.status_code == 201

    area_id = resp.json()["id"]

    resp2 = await async_client.patch(
        f"/areas/admin/{area_id}",
        json={"name": "UpdatedName"},
        headers=headers,
    )
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["name"] == "UpdatedName"


@pytest.mark.anyio
async def test_update_area_requires_admin(
    async_client,
    owner_token,
):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    resp = await async_client.patch(
        "/areas/admin/1",
        json={"name": "Hack"},
        headers=headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------
# AUTOCOMPLETE (PUBLIC)
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_autocomplete_prefix_and_substring(
    async_client,
    admin_token,
):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    await async_client.post(
        "/areas/admin",
        json={"name": "AlphaCity", "main_region": "X"},
        headers=headers,
    )
    await async_client.post(
        "/areas/admin",
        json={"name": "BetaTown", "main_region": "X"},
        headers=headers,
    )
    await async_client.post(
        "/areas/admin",
        json={"name": "GammaVillage", "main_region": "X"},
        headers=headers,
    )

    resp = await async_client.get("/areas/autocomplete?q=Al&limit=5")
    assert resp.status_code == 200
    names = [a["name"] for a in resp.json()]
    assert any("Alpha" in n for n in names)

    # substring search
    resp2 = await async_client.get("/areas/autocomplete?q=ma&limit=5")
    assert resp2.status_code == 200
    names2 = [a["name"] for a in resp2.json()]
    assert any("Gamma" in n for n in names2)


# ---------------------------------------------------------
# DELETE AREA (ADMIN ONLY)
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_delete_area_and_404_on_missing(
    async_client,
    admin_token,
):
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    resp = await async_client.post(
        "/areas/admin",
        json={"name": "ToDelete", "main_region": "D"},
        headers=headers,
    )
    assert resp.status_code == 201

    area_id = resp.json()["id"]

    resp2 = await async_client.delete(
        f"/areas/admin/{area_id}",
        headers=headers,
    )
    assert resp2.status_code == 204

    resp3 = await async_client.get(f"/areas/{area_id}")
    assert resp3.status_code == 404


@pytest.mark.anyio
async def test_delete_area_requires_admin(
    async_client,
    owner_token,
):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    resp = await async_client.delete(
        "/areas/admin/1",
        headers=headers,
    )
    assert resp.status_code == 403