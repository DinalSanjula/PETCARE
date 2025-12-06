# Clinics/tests/conftest.py
import os
import sys
from types import SimpleNamespace

# --- ensure project root is importable BEFORE any Clinics imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Provide an async fake user callable early so routers that imported
# get_current_user at import-time can still pick it up.
async def _fake_user():
    return SimpleNamespace(id=1)

# Try patching the auth module early (best-effort, silent fail ok)
try:
    import Clinics.utils.auth as _auth_mod
    _auth_mod.get_current_user = _fake_user
except Exception:
    # It's fine if this import isn't resolvable at collection time.
    pass


# -------- Now import testing libs and app/db --------
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app          # app at project root
from db import Base, get_db  # SQLAlchemy Base and get_db

# modules we'll monkeypatch inside the client fixture
import Clinics.crud.area_crud as area_crud_module
import Clinics.utils.admin_permission as admin_perm_module

# Optionally import your lightweight mock models (should define a User model if used).
# If you have Tests/mock_models.py that defines a User model mapped to Base, it should be imported
# BEFORE create_all so that the "users" table exists for foreign keys.
try:
    import Clinics.tests.mock_models  # optional: safe to fail
except Exception:
    pass

TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, future=True, echo=False)
    # create all tables once for the session
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture()
async def async_session(engine):
    AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture()
async def client(async_session, monkeypatch):
    """
    Test client fixture:
     - overrides get_db to yield the async_session
     - stubs geocode and require_admin
     - stubs MinIO upload/delete to avoid network calls
     - installs async fake_user override into app.dependency_overrides
     - creates httpx.AsyncClient with ASGITransport
    """
    # 1) override get_db
    async def _get_test_db():
        try:
            yield async_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_test_db

    # 2) stub geocode_async (no network)
    async def fake_geocode(q, countrycode=None):
        return None, None, None
    monkeypatch.setattr(area_crud_module, "geocode_async", fake_geocode)

    # 3) stub require_admin
    async def fake_require_admin():
        return None
    monkeypatch.setattr(admin_perm_module, "require_admin", fake_require_admin)

    # --- Fake MinIO client (Option A) - robust version ---
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

    # Try to monkeypatch the module-level _get_client. Do raising=False to avoid brittle errors.
    monkeypatch.setattr(
        "Clinics.storage.minio_storage._get_client",
        lambda: _FakeMinioClient(),
        raising=False
    )
    # Replace any existing client instance on the module (defensive)
    try:
        import Clinics.storage.minio_storage as _ms
        _ms._client = _FakeMinioClient()
        _ms.PUBLIC_BASE = "http://testserver/fake"
    except Exception:
        pass

    # 6) create AsyncClient using ASGITransport
    try:
        from httpx import AsyncClient, ASGITransport
    except Exception as exc:
        raise RuntimeError("httpx with ASGITransport is required. Run: python -m pip install 'httpx>=0.23.0'") from exc

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    # 7) cleanup
    app.dependency_overrides.clear()