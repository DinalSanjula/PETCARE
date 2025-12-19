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
async def test_upload_and_list_image(client, db_session):
    # 1) Create clinic (inactive by default)
    payload = {
        "name": "Img Clinic",
        "description": "For images",
        "phone": "0773333333",
        "address": "Test Rd",
        "profile_pic_url": None,
        "area_id": None
    }

    create_resp = await client.post("/clinics/", json=payload)
    assert create_resp.status_code == 201
    cid = create_resp.json()["id"]

    # Activate clinic
    await activate_clinic(db_session, cid)

    # 2) Upload image
    png_bytes = await create_png_bytes()
    files = {"file": ("test.png", png_bytes, "image/png")}

    upload_url = f"{PREFIX}/clinics/{cid}"
    resp = await client.post(upload_url, files=files)
    assert resp.status_code == 201

    data = resp.json()
    assert data["id"] > 0
    assert data["url"].startswith("http://testserver/fake/")

    # 3) List images
    list_url = f"{PREFIX}/clinics/{cid}"
    list_resp = await client.get(list_url)
    assert list_resp.status_code == 200

    arr = list_resp.json()
    assert any(img["id"] == data["id"] for img in arr)


@pytest.mark.anyio
async def test_get_patch_and_delete_image(client, db_session):
    # 1) Create clinic
    payload = {
        "name": "Img Clinic 2",
        "description": "For images",
        "phone": "0774444444",
        "address": "Test Rd 2",
        "profile_pic_url": None,
        "area_id": None
    }

    create_resp = await client.post("/clinics/", json=payload)
    assert create_resp.status_code == 201
    cid = create_resp.json()["id"]

    # Activate clinic
    await activate_clinic(db_session, cid)

    # 2) Upload image
    png_bytes = await create_png_bytes((0, 255, 0))
    files = {"file": ("test2.png", png_bytes, "image/png")}

    upload_url = f"{PREFIX}/clinics/{cid}"
    resp = await client.post(upload_url, files=files)
    assert resp.status_code == 201

    img = resp.json()
    img_id = img["id"]

    # 3) Get image
    get_url = f"{PREFIX}/{img_id}"
    get_resp = await client.get(get_url)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == img_id

    # 4) Patch metadata only
    patch_url = f"{PREFIX}/{img_id}"
    patch_resp = await client.patch(
        patch_url,
        data={
            "original_filename": "renamed.png",
            "url": "http://example/new.png"
        }
    )
    assert patch_resp.status_code == 200

    patched = patch_resp.json()
    assert (
        patched["original_filename"] == "renamed.png"
        or patched["url"] == "http://example/new.png"
    )

    # 5) Delete
    del_url = f"{PREFIX}/{img_id}"
    del_resp = await client.delete(del_url)
    assert del_resp.status_code == 204

    # 6) Confirm deletion
    get_after = await client.get(get_url)
    assert get_after.status_code == 404