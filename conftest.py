# PETCARE/conftest.py  (ROOT)
import os
import importlib
from pathlib import Path
from dotenv import load_dotenv

import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,  # <-- real SQLAlchemy function
    AsyncSession,
)

# ---------------------------------------------------------
# Load .env
# ---------------------------------------------------------
load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = (
    os.getenv("TEST_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or f"sqlite+aiosqlite:///{Path.cwd() / 'test_petcare.db'}"
)

# ---------------------------------------------------------
# Modules to scan for Base
# ---------------------------------------------------------
CANDIDATE_MODULES = [
    "db",
    "app.db",
    "app.models.user_model",
    "Clinics.models.models",
    "Clinics.models",
    "Clinics.db",
]

def discover_bases():
    bases = []
    for name in CANDIDATE_MODULES:
        try:
            mod = importlib.import_module(name)
            Base = getattr(mod, "Base", None)
            if Base is not None:
                bases.append((name, Base))
        except Exception:
            pass
    return bases

# ---------------------------------------------------------
# ENGINE FIXTURE
# ---------------------------------------------------------
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    yield engine
    await engine.dispose()

# ---------------------------------------------------------
# SESSIONMAKER FIXTURE  (RENAMED!)
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def get_sessionmaker(test_engine):
    """Return a SQLAlchemy async sessionmaker."""
    return async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

# ---------------------------------------------------------
# CREATE/DROP TABLES
# ---------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    bases = discover_bases()

    async with test_engine.begin() as conn:
        for name, Base in bases:
            print(f"Creating tables for Base from {name}: {sorted(Base.metadata.tables.keys())}")
            await conn.run_sync(Base.metadata.create_all)

    print("TEST DATABASE_URL:", DATABASE_URL)
    for name, Base in bases:
        print(f"Discovered Base: {name} -> tables: {sorted(Base.metadata.tables.keys())}")

    yield

    async with test_engine.begin() as conn:
        for name, Base in bases:
            print(f"Dropping tables for Base from {name}: {sorted(Base.metadata.tables.keys())}")
            await conn.run_sync(Base.metadata.drop_all)

# ---------------------------------------------------------
# ISOLATED SESSION PER TEST
# ---------------------------------------------------------
@pytest.fixture(scope="function")
async def db_session(test_engine, get_sessionmaker):
    async with test_engine.connect() as conn:
        trans = await conn.begin()

        session = get_sessionmaker(bind=conn)
        # await session.begin_nested()
        try:
            yield session
        finally:
            # await session.rollback()
            await session.close()
            # await trans.rollback()

# ---------------------------------------------------------
# PERSISTENT SESSION FOR SEEDING USERS
# ---------------------------------------------------------
@pytest.fixture()
async def persistent_session(get_sessionmaker):
    async with get_sessionmaker() as s:
        yield s

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# --- Backward-compatible alias fixtures for old tests ---

@pytest.fixture()
async def async_session(db_session):
    """Old tests expect async_session -> map it to db_session."""
    return db_session


from httpx import AsyncClient, ASGITransport
from main import app as fastapi_app

@pytest.fixture()
async def async_client(db_session):
    try:
        from db import get_db
        async def _override_get_db():
            yield db_session
        fastapi_app.dependency_overrides[get_db] = _override_get_db
    except Exception:
        pass

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()

@pytest.fixture()
async def test_user_token(async_client):
    payload = {
        "name": "Token User",
        "email": "tokenuser@example.com",
        "password": "strongpassword",
        "role": "owner"
    }

    # Register (ignore if already exists)
    await async_client.post("/auth/register", json=payload)

    # Login
    resp = await async_client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]}
    )
    assert resp.status_code == 200

    return resp.json()["data"]