# Clinics/tests/conftest.py
import importlib
import pytest
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def client(monkeypatch, db_session):
    """
    Clinics-specific test client with:
    - mocked geocode
    - mocked admin
    - mocked minio
    - test user injected
    - get_db overridden to use db_session
    """

    # -----------------------------
    # 1) Stub geocoding
    # -----------------------------
    async def fake_geocode(q, countrycode=None):
        return None, None, None

    monkeypatch.setattr("Clinics.crud.geocode.geocode_async", fake_geocode, raising=False)
    monkeypatch.setattr("Clinics.crud.area_crud.geocode_async", fake_geocode, raising=False)

    # -----------------------------
    # 2) Fake MinIO Client
    # -----------------------------
    class _FakeMinioClient:
        def __init__(self):
            self._store = {}

        def bucket_exists(self, bucket):
            return True

        def make_bucket(self, bucket):
            return None

        def put_object(self, bucket, object_name, data, length, content_type=None):
            content = data.read() if hasattr(data, "read") else data
            self._store[(bucket, object_name)] = {"data": content, "content_type": content_type}

        def remove_object(self, bucket, object_name):
            self._store.pop((bucket, object_name), None)

    try:
        import Clinics.storage.minio_storage as _ms
        _ms._client = _FakeMinioClient()
        _ms.PUBLIC_BASE = "http://testserver/fake"
    except Exception:
        monkeypatch.setattr("Clinics.storage.minio_storage._get_client", lambda: _FakeMinioClient(), raising=False)

    # -----------------------------
    # 3) Load or create test user directly via db_session
    # -----------------------------
    test_user = None
    try:
        from app.auth.security import get_current_active_user, get_password_hash
    except Exception:
        get_current_active_user = None
        get_password_hash = None

    try:
        from app.models.user_model import User
    except Exception:
        User = None

    if User and get_password_hash and get_current_active_user:
        result = await db_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        test_user = result.scalars().first()

        if not test_user:
            test_user = User(
                name="Test User",
                email="test@example.com",
                password_hash=get_password_hash("strongpassword"),
                role="owner",
            )
            db_session.add(test_user)
            await db_session.commit()
            await db_session.refresh(test_user)

        async def _override_current_user():
            return test_user

    # -----------------------------
    # 4) Load FastAPI application
    # -----------------------------
    try:
        project_app = importlib.import_module("main").app
    except Exception:
        project_app = importlib.import_module("app.main").app



    # -----------------------------
    # 5) REQUIRED FIX:
    #    Override require_admin at FastAPI dependency layer
    # -----------------------------
    try:
        from Clinics.utils.admin_permission import require_admin
    except Exception:
        require_admin = None

    if require_admin:
        async def _override_admin():
            return None

        project_app.dependency_overrides[require_admin] = _override_admin

    # -----------------------------
    # 6) Override get_current_user
    # -----------------------------
    if get_current_active_user:
        project_app.dependency_overrides[get_current_active_user] = _override_current_user

    # -----------------------------
    # 7) Override get_db to use db_session
    # -----------------------------
    try:
        from db import get_db as app_get_db
    except Exception:
        app_get_db = None

    if app_get_db:
        async def _override_get_db():
            yield db_session
        project_app.dependency_overrides[app_get_db] = _override_get_db

    # -----------------------------
    # 8) Return HTTP client
    # -----------------------------
    transport = ASGITransport(app=project_app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    project_app.dependency_overrides.clear()