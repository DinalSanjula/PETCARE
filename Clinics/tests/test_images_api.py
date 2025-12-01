# Clinics/tests/test_images_api.py
import pytest
from types import SimpleNamespace
from io import BytesIO
from PIL import Image

# If your images router is mounted under a prefix change this to match.
# Example: if you include router with app.include_router(images_router, prefix="/images"),
# set PREFIX = "/images". Otherwise leave empty string.
PREFIX = "/images"  # e.g. "/images" or "/clinic-images"

async def create_png_bytes(color=(255, 0, 0)):
    buf = BytesIO()
    img = Image.new("RGB", (2, 2), color=color)
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

@pytest.mark.anyio
async def test_upload_and_list_image(client, monkeypatch):
    # ensure auth fake is active via conftest client fixture
    # 1) create a clinic first
    payload = {
        "owner_id": 1,
        "name": "Img Clinic",
        "description": "For images",
        "phone": "0773333333",
        "address": "Test Rd",
        "profile_pic_url": None,
        "area_id": None
    }
    create_resp = await client.post("/clinics/", json=payload)
    assert create_resp.status_code == 201, create_resp.text
    cid = create_resp.json()["id"]

    # 2) upload an image for that clinic
    png_bytes = await create_png_bytes()
    files = {"file": ("test.png", png_bytes, "image/png")}
    upload_url = f"{PREFIX}/clinics/{cid}/" if PREFIX else f"/clinics/{cid}/"
    resp = await client.post(upload_url, files=files)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "id" in data and data["id"] > 0
    assert data["url"].startswith("http://testserver/fake/")

    # 3) list images for clinic
    list_url = f"{PREFIX}/clinics/{cid}/" if PREFIX else f"/clinics/{cid}/"
    list_resp = await client.get(list_url)
    assert list_resp.status_code == 200
    arr = list_resp.json()
    assert isinstance(arr, list)
    assert any(item["id"] == data["id"] for item in arr)

@pytest.mark.anyio
async def test_get_patch_and_delete_image(client):
    # create clinic
    payload = {
        "owner_id": 1,
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

    # upload
    png_bytes = await create_png_bytes((0,255,0))
    files = {"file": ("test2.png", png_bytes, "image/png")}
    upload_url = f"{PREFIX}/clinics/{cid}/" if PREFIX else f"/clinics/{cid}/"
    resp = await client.post(upload_url, files=files)
    assert resp.status_code == 201
    img = resp.json()
    img_id = img["id"]

    # get
    get_url = f"{PREFIX}/{img_id}/" if PREFIX else f"/{img_id}/"
    get_resp = await client.get(get_url)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == img_id

    # patch: update metadata (no file) - change original_filename or url
    patch_url = f"{PREFIX}/{img_id}" if PREFIX else f"/{img_id}"
    patch_resp = await client.patch(patch_url, data={"original_filename": "renamed.png", "url": "http://example/new.png"})
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["original_filename"] == "renamed.png" or patched["url"] == "http://example/new.png"

    # delete
    del_url = f"{PREFIX}/{img_id}/" if PREFIX else f"/{img_id}/"
    del_resp = await client.delete(del_url)
    assert del_resp.status_code == 204

    # confirm deletion
    get_after = await client.get(get_url)
    assert get_after.status_code == 404