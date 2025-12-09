# Clinics/tests/conftest.py
import os
import sys
from types import SimpleNamespace
import importlib

# ensure project root is importable BEFORE any Clinics imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from sqlalchemy import select

# import the FastAPI app (root main)
try:
    from main import app as project_app
except Exception:
    from app.main import app as project_app

# Import shared DB session resources from app.database.session
from db import AsyncSessionLocal

# Ensure User model is imported/registered
importlib.import_module("app.models.user_model")
from app.models.user_model import User

# Modules we monkeypatch
import Clinics.crud.area_crud as area_crud_module
import Clinics.utils.admin_permission as admin_perm_module

# Import auth helpers if present
try:
    from app.auth.security import get_current_active_user, get_password_hash
except Exception:
    get_current_active_user = None
    get_password_hash = None

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
async def client(async_client, monkeypatch):
    """
    Clinics-specific client fixture. Reuses the shared async_client from root conftest.
    - monkeypatches geocode and admin permission
    - fakes MinIO storage
    - creates or loads a test user in the shared DB and overrides get_current_active_user
    """

    # 1) stub geocode (avoid network)
    async def fake_geocode(q, countrycode=None):
        return None, None, None

    monkeypatch.setattr(area_crud_module, "geocode_async", fake_geocode)

    # 2) stub admin permission
    async def fake_require_admin():
        return None

    monkeypatch.setattr(admin_perm_module, "require_admin", fake_require_admin)

    # 3) Fake MinIO client
    class _FakeMinioClient:
        def __init__(self):
            self._store = {}

        def bucket_exists(self, bucket):
            return True

        def make_bucket(self, bucket):
            return None

        def put_object(self, bucket, object_name, data, length, content_type=None):
            if hasattr(data, "read"):
                content = data.read()
            else:
                content = data
            self._store[(bucket, object_name)] = {
                "data": content,
                "content_type": content_type,
            }
            return None

        def remove_object(self, bucket, object_name):
            self._store.pop((bucket, object_name), None)
            return None

    monkeypatch.setattr(
        "Clinics.storage.minio_storage._get_client",
        lambda: _FakeMinioClient(),
        raising=False
    )
    try:
        import Clinics.storage.minio_storage as _ms
        _ms._client = _FakeMinioClient()
        _ms.PUBLIC_BASE = "http://testserver/fake"
    except Exception:
        pass

    # 4) create or load test user using shared AsyncSessionLocal
    test_user = None
    if get_password_hash and get_current_active_user:
        async with AsyncSessionLocal() as session:
            existing = await session.execute(select(User).where(User.email == "test@example.com"))
            test_user = existing.scalars().first()

            if not test_user:
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    password_hash=get_password_hash("strongpassword"),
                    role="owner",
                )
                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)

        async def _override_current_user():
            return test_user

        project_app.dependency_overrides[get_current_active_user] = _override_current_user

    # finally yield the shared async_client coming from root conftest
    yield async_client

    # cleanup overrides
    project_app.dependency_overrides.clear()