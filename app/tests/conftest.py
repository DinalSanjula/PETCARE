# tests/conftest.py
import os
import pytest
import tempfile
import asyncio

# Ensure SECRET_KEY is set BEFORE importing security module anywhere in tests
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_pytest")

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import app.database.session as session_mod
from app.database.session import Base  # metadata
# Import app only AFTER we've prepared/changed session_mod inside fixtures when necessary
from app.main import app  # FastAPI app (has lifespan that calls init_database)

@pytest.fixture(scope="session")
def anyio_backend():
    # required for pytest-asyncio/anyio compatibility
    return "asyncio"

@pytest.fixture(scope="session")
async def test_db(tmp_path_factory):
    """
    Create a temporary SQLite DB file and patch session module to use it.
    This fixture yields after creating tables and disposes engine at teardown.
    """
    tmp_dir = tmp_path_factory.mktemp("db")
    db_file = tmp_dir / "test_petcare.db"
    database_url = f"sqlite+aiosqlite:///{db_file}"

    # create test engine
    engine = create_async_engine(database_url, echo=False, future=True)

    # patch session module variables so get_db_session uses this engine/sessionmaker
    session_mod.engine = engine
    session_mod.AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # tests run here

    # teardown - dispose engine
    await engine.dispose()

@pytest.fixture
async def async_client(test_db):
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver"
    ) as client:
        yield client

@pytest.fixture
async def test_user_token(async_client):
    """
    Register a test user and return the access token string.
    Returns dict: {"access_token": "...", "refresh_token": "..."}
    """
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "strongpassword",
        "role": "owner"
    }

    # Register
    r = await async_client.post("/auth/register", json=payload)
    assert r.status_code in (201, 409)  # allow if previous test run already created (rare)
    data = r.json()
    if not data.get("success"):
        # if registration conflict, login to get token
        login_r = await async_client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
        assert login_r.status_code == 200
        tokens = login_r.json()["data"]
    else:
        tokens = data["data"]

    return tokens