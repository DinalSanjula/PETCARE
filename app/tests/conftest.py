# PETCARE/app/tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

from main import app as fastapi_app
from conftest import db_session  # noqa: F401 (pytest uses fixture by name)

@pytest.fixture
async def client(db_session):
    # override get_db if available
    try:
        from db import get_db as app_get_db
    except Exception:
        app_get_db = None

    if app_get_db is not None:
        async def _override_get_db():
            try:
                yield db_session
            finally:
                pass
        fastapi_app.dependency_overrides[app_get_db] = _override_get_db

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    # cleanup overrides
    if app_get_db is not None:
        fastapi_app.dependency_overrides.pop(app_get_db, None)