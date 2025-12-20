import pytest
from io import BytesIO
from PIL import Image
from sqlalchemy import select

from Clinics.models.models import Clinic

PREFIX = "/images"


# --------------------------------------------------
# Helper: create png bytes
# --------------------------------------------------
async def create_png_bytes(color=(255, 0, 0)):
    buf = BytesIO()
    img = Image.new("RGB", (2, 2), color=color)
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


# --------------------------------------------------
# Helper: activate clinic (admin/system step)
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
# UPLOAD & LIST IMAGES (CLINIC ONLY)
# --------------------------------------------------
@pytest.mark.anyio
async def test_upload_and_list_image(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    # 1) Create clinic
    payload = {
        "name": "Img Clinic",
        "description": "For images",
        "phone": "0773333333",
        "address": "Test Rd",
        "profile_pic_url": None,
        "area_id": None,
    }

    create_resp = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    assert create_resp.status_code == 201
    cid = create_resp.json()["id"]

    # Activate clinic
    await activate_clinic(db_session, cid)

    # 2) Upload image
    png_bytes = await create_png_bytes()
    files = {"file": ("test.png", png_bytes, "image/png")}

    upload_url = f"{PREFIX}/clinics/{cid}"
    resp = await async_client.post(
        upload_url,
        files=files,
        headers=headers,
    )
    assert resp.status_code == 201

    data = resp.json()
    assert data["id"] > 0
    assert data["url"].startswith("http://testserver/fake/")

    # 3) List images (public)
    list_url = f"{PREFIX}/clinics/{cid}"
    list_resp = await async_client.get(list_url)
    assert list_resp.status_code == 200

    arr = list_resp.json()
    assert any(img["id"] == data["id"] for img in arr)


@pytest.mark.anyio
async def test_owner_cannot_upload_image(
    async_client,
    owner_token,
):
    headers = {"Authorization": f"Bearer {owner_token['access_token']}"}

    png_bytes = await create_png_bytes()
    files = {"file": ("x.png", png_bytes, "image/png")}

    resp = await async_client.post(
        f"{PREFIX}/clinics/1",
        files=files,
        headers=headers,
    )
    assert resp.status_code == 403


# --------------------------------------------------
# GET, PATCH, DELETE IMAGE
# --------------------------------------------------
@pytest.mark.anyio
async def test_get_patch_and_delete_image(
    async_client,
    clinic_token,
    db_session,
):
    headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}

    # 1) Create clinic
    payload = {
        "name": "Img Clinic 2",
        "description": "For images",
        "phone": "0774444444",
        "address": "Test Rd 2",
        "profile_pic_url": None,
        "area_id": None,
    }

    create_resp = await async_client.post(
        "/clinics/",
        json=payload,
        headers=headers,
    )
    assert create_resp.status_code == 201
    cid = create_resp.json()["id"]

    # Activate clinic
    await activate_clinic(db_session, cid)

    # 2) Upload image
    png_bytes = await create_png_bytes((0, 255, 0))
    files = {"file": ("test2.png", png_bytes, "image/png")}

    upload_url = f"{PREFIX}/clinics/{cid}"
    resp = await async_client.post(
        upload_url,
        files=files,
        headers=headers,
    )
    assert resp.status_code == 201

    img = resp.json()
    img_id = img["id"]

    # 3) Get image (public)
    get_url = f"{PREFIX}/{img_id}"
    get_resp = await async_client.get(get_url)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == img_id

    # 4) Patch metadata (clinic owner only)
    patch_url = f"{PREFIX}/{img_id}"
    patch_resp = await async_client.patch(
        patch_url,
        data={
            "original_filename": "renamed.png",
            "url": "http://example/new.png",
        },
        headers=headers,
    )
    assert patch_resp.status_code == 200

    patched = patch_resp.json()
    assert (
        patched["original_filename"] == "renamed.png"
        or patched["url"] == "http://example/new.png"
    )

    # 5) Delete image
    del_url = f"{PREFIX}/{img_id}"
    del_resp = await async_client.delete(
        del_url,
        headers=headers,
    )
    assert del_resp.status_code == 204

    # 6) Confirm deletion
    get_after = await async_client.get(get_url)
    assert get_after.status_code == 404


@pytest.mark.anyio
async def test_non_owner_cannot_patch_or_delete_image(
    async_client,
    clinic_token,
    owner_token,
    db_session,
):
    clinic_headers = {
        "Authorization": f"Bearer {clinic_token['access_token']}"
    }
    owner_headers = {
        "Authorization": f"Bearer {owner_token['access_token']}"
    }

    # Create clinic
    create_resp = await async_client.post(
        "/clinics/",
        json={
            "name": "Secure Img Clinic",
            "description": "Secure",
            "phone": "0775555555",
            "address": "Road",
            "profile_pic_url": None,
            "area_id": None,
        },
        headers=clinic_headers,
    )
    cid = create_resp.json()["id"]

    await activate_clinic(db_session, cid)

    # Upload image
    png_bytes = await create_png_bytes()
    files = {"file": ("secure.png", png_bytes, "image/png")}

    resp = await async_client.post(
        f"{PREFIX}/clinics/{cid}",
        files=files,
        headers=clinic_headers,
    )
    img_id = resp.json()["id"]

    # Owner tries to patch
    patch_resp = await async_client.patch(
        f"{PREFIX}/{img_id}",
        data={"original_filename": "hack.png"},
        headers=owner_headers,
    )
    assert patch_resp.status_code == 403

    # Owner tries to delete
    del_resp = await async_client.delete(
        f"{PREFIX}/{img_id}",
        headers=owner_headers,
    )
    assert del_resp.status_code == 403