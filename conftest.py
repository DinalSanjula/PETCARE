# PETCARE/conftest.py (ROOT)

import os
import importlib
from pathlib import Path
from dotenv import load_dotenv

import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
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
    "Users.db",
    "Users.models.user_model",
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
# SESSIONMAKER FIXTURE
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def get_sessionmaker(test_engine):
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
        for _, Base in bases:
            await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        for _, Base in bases:
            await conn.run_sync(Base.metadata.drop_all)

# ---------------------------------------------------------
# ISOLATED SESSION PER TEST
# ---------------------------------------------------------
@pytest.fixture(scope="function")
async def db_session(test_engine, get_sessionmaker):
    async with test_engine.connect() as conn:
        await conn.begin()
        session = get_sessionmaker(bind=conn)
        try:
            yield session
        finally:
            await session.close()

# ---------------------------------------------------------
# PERSISTENT SESSION (OPTIONAL)
# ---------------------------------------------------------
@pytest.fixture()
async def persistent_session(get_sessionmaker):
    async with get_sessionmaker() as s:
        yield s

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# ---------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------
@pytest.fixture()
async def async_session(db_session):
    return db_session

# ---------------------------------------------------------
# HTTP CLIENT
# ---------------------------------------------------------
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
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()

# ---------------------------------------------------------
# TOKEN FIXTURES (RBAC)
# ---------------------------------------------------------

@pytest.fixture()
async def owner_token(async_client):
    payload = {
        "name": "Owner User",
        "email": "owner@example.com",
        "password": "strongpassword",
        "role": "owner",
    }

    await async_client.post("/auth/register", json=payload)

    resp = await async_client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200

    return resp.json()["data"]


@pytest.fixture()
async def clinic_token(async_client):
    payload = {
        "name": "Clinic User",
        "email": "clinic@example.com",
        "password": "strongpassword",
        "role": "clinic",
    }

    await async_client.post("/auth/register", json=payload)

    resp = await async_client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200

    return resp.json()["data"]


@pytest.fixture()
async def admin_token(async_client):
    payload = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "strongpassword",
        "role": "admin",
    }

    await async_client.post("/auth/register", json=payload)

    resp = await async_client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200

    return resp.json()["data"]


@pytest.fixture()
async def welfare_token(async_client):
    payload = {
        "name": "Welfare User",
        "email": "welfare@example.com",
        "password": "strongpassword",
        "role": "welfare",
    }

    await async_client.post("/auth/register", json=payload)

    resp = await async_client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200

    return resp.json()["data"]

import pytest
import socket

@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def guard(*args, **kwargs):
        raise RuntimeError("Network access disabled during tests")

    monkeypatch.setattr(socket, "getaddrinfo", guard)