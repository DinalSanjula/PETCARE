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
    pass

# -------- Now import testing libs and app/db --------
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from db import Base, get_db

# --- Load model modules BEFORE metadata.create_all so all tables get created ---
# This line is CRITICAL: it ensures the 'users' table exists before FK creation.
from app.models.user_model import User

# modules we monkeypatch
import Clinics.crud.area_crud as area_crud_module
import Clinics.utils.admin_permission as admin_perm_module

# Import auth helpers
try:
    from app.auth.security import get_current_active_user, get_password_hash
except Exception:
    get_current_active_user = None
    get_password_hash = None

TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, future=True, echo=False)

    # --- Create ALL tables (including users) ---
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
    # 1) override get_db
    async def _get_test_db():
        try:
            yield async_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db

    # 2) stub geocode (avoid network)
    async def fake_geocode(q, countrycode=None):
        return None, None, None

    monkeypatch.setattr(area_crud_module, "geocode_async", fake_geocode)

    # 3) stub admin permission
    async def fake_require_admin():
        return None

    monkeypatch.setattr(admin_perm_module, "require_admin", fake_require_admin)

    # ---- Fake MinIO client ----
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

    # ---- Create real test user + override get_current_active_user ----
    test_user = None
    if get_password_hash and get_current_active_user:
        # ---- Create or load test user ----
        from sqlalchemy import select

        existing = await async_session.execute(select(User).where(User.email == "test@example.com"))
        test_user = existing.scalars().first()

        if not test_user:
            test_user = User(
                name="Test User",
                email="test@example.com",
                password_hash=get_password_hash("testpassword"),
                role="owner",
            )
            async_session.add(test_user)
            await async_session.commit()
            await async_session.refresh(test_user)

        async def _override_current_user():
            return test_user

        app.dependency_overrides[get_current_active_user] = _override_current_user

    # 6) HTTP client using ASGITransport
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    # cleanup
    app.dependency_overrides.clear()