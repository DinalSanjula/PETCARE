# Clinics/tests/conftest.py

"""
Clinics test configuration.

This file ONLY contains Clinics-specific mocks:
- Geocoding
- MinIO storage

Auth, DB, client, and RBAC tokens are provided
by the root-level conftest.py.
"""

import pytest


# ---------------------------------------------------------
# MOCK GEOCODING
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_geocoding(monkeypatch):
    async def fake_geocode(q, countrycode=None):
        return None, None, None

    monkeypatch.setattr(
        "Clinics.crud.geocode.geocode_async",
        fake_geocode,
        raising=False,
    )
    monkeypatch.setattr(
        "Clinics.crud.area_crud.geocode_async",
        fake_geocode,
        raising=False,
    )


# ---------------------------------------------------------
# MOCK MINIO STORAGE
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_minio(monkeypatch):
    class _FakeMinioClient:
        def __init__(self):
            self._store = {}

        def bucket_exists(self, bucket):
            return True

        def make_bucket(self, bucket):
            return None

        def put_object(self, bucket, object_name, data, length, content_type=None):
            content = data.read() if hasattr(data, "read") else data
            self._store[(bucket, object_name)] = {
                "data": content,
                "content_type": content_type,
            }

        def remove_object(self, bucket, object_name):
            self._store.pop((bucket, object_name), None)

    try:
        import Clinics.storage.minio_storage as ms
        ms._client = _FakeMinioClient()
        ms.PUBLIC_BASE = "http://testserver/fake"
    except Exception:
        monkeypatch.setattr(
            "Clinics.storage.minio_storage._get_client",
            lambda: _FakeMinioClient(),
            raising=False,
        )