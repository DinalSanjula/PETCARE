# conftest.py (project root) — patched to force root db module early into sys.modules
import os
import sys
import types
import importlib
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import warnings

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# --------------- Early env setup ----------------
load_dotenv()
# Force a stable SECRET_KEY in test runs
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "test-secret-key"))
os.environ.setdefault("FASTAPI_ENV", os.getenv("FASTAPI_ENV", "test"))

DEFAULT_TEST_DB = os.getenv("TEST_DATABASE_URL", None)
if not DEFAULT_TEST_DB:
    DEFAULT_TEST_DB = f"sqlite+aiosqlite:///{Path.cwd() / 'test_petcare.db'}"
os.environ.setdefault("DATABASE_URL", DEFAULT_TEST_DB)

# --------------- Create test engine and sessionmaker ----------------
_engine = create_async_engine(os.environ["DATABASE_URL"], echo=False, future=True)
_async_session_local = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# --------------- Ensure a top-level 'db' module object exists in sys.modules ----------------
# If a real db.py exists, import it; otherwise create a module-like namespace and insert it
try:
    db_mod = importlib.import_module("db")
except ModuleNotFoundError:
    # create a lightweight module-like object to satisfy imports
    db_mod = types.SimpleNamespace()
    sys.modules["db"] = db_mod

# Patch the db module (real or fake) to use our test engine/session/Base placeholder
db_mod.engine = _engine
db_mod.AsyncSessionLocal = _async_session_local
db_mod.async_sessionmaker = _async_session_local  # compatibility name

# Provide get_db / get_db_session compat functions
async def _get_db_compat():
    async with _async_session_local() as s:
        try:
            yield s
        finally:
            try:
                await s.close()
            except Exception:
                pass

db_mod.get_db = getattr(db_mod, "get_db", _get_db_compat)
db_mod.get_db_session = getattr(db_mod, "get_db_session", db_mod.get_db)

# --------------- Create a compatibility wrapper module for app.database.session if absent -----------
# If your code imports app.database.session, ensure it exists and points to the same objects.
if "app.database.session" not in sys.modules:
    # try to import existing module path; if it fails create a SimpleNamespace and insert
    try:
        session_mod = importlib.import_module("app.database.session")
        # patch it so it uses our test engine/session when tests run
        setattr(session_mod, "engine", _engine)
        setattr(session_mod, "AsyncSessionLocal", _async_session_local)
        if not hasattr(session_mod, "get_db"):
            setattr(session_mod, "get_db", _get_db_compat)
        if not hasattr(session_mod, "get_db_session"):
            setattr(session_mod, "get_db_session", _get_db_compat)
    except Exception:
        # create a simple wrapper that re-exports from top-level db_mod
        wrapper = types.SimpleNamespace()
        wrapper.engine = db_mod.engine
        wrapper.AsyncSessionLocal = db_mod.AsyncSessionLocal
        wrapper.async_sessionmaker = db_mod.async_sessionmaker
        wrapper.get_db = db_mod.get_db
        wrapper.get_db_session = db_mod.get_db_session
        wrapper.Base = getattr(db_mod, "Base", None)
        sys.modules["app.database.session"] = wrapper
        session_mod = wrapper
else:
    session_mod = sys.modules["app.database.session"]
    # patch attributes to test engine/session
    setattr(session_mod, "engine", _engine)
    setattr(session_mod, "AsyncSessionLocal", _async_session_local)
    setattr(session_mod, "get_db", getattr(session_mod, "get_db", _get_db_compat))
    setattr(session_mod, "get_db_session", getattr(session_mod, "get_db_session", _get_db_compat))

# --------------- Autodiscover & import model modules AFTER db/session are patched ----------------
def import_models_from(package_root: str, models_subdir: str = "models"):
    pkg_path = Path.cwd() / package_root / models_subdir
    if not pkg_path.exists():
        return
    for py in sorted(pkg_path.glob("*.py")):
        if py.name == "__init__.py":
            continue
        module_name = f"{package_root}.{models_subdir}.{py.stem}"
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            warnings.warn(f"Failed to import models module {module_name}: {exc!r}")

# Try import app models then Clinics models; it's safe because db/session are patched above
import_models_from("app")
import_models_from("Clinics")

# If Base is defined in either module, use it; prefer explicit attribute if exists
Base = getattr(db_mod, "Base", None)
if Base is None and hasattr(session_mod, "Base"):
    Base = getattr(session_mod, "Base")

# --------------- Create / drop tables helpers ----------------
async def _create_all():
    if Base is None:
        # nothing to create
        return
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def _drop_all():
    if Base is None:
        return
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# --------------- Pytest fixtures ----------------
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
async def async_session():
    async with _async_session_local() as session:
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass

@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """
    Create all tables once per test session (autouse). Tear down after tests finish.
    """
    # create DB file and tables
    asyncio.run(_create_all())

    # debug print (visible with pytest -s)
    try:
        print("TEST DATABASE_URL:", os.environ.get("DATABASE_URL"))
        if Base is not None:
            print("TABLES:", sorted(list(Base.metadata.tables.keys())))
    except Exception:
        pass

    yield

    # teardown
    try:
        asyncio.run(_drop_all())
    except Exception:
        pass
    try:
        asyncio.run(_engine.dispose())
    except Exception:
        pass

    # remove test db file if used
    try:
        url = os.environ.get("DATABASE_URL", "")
        if url.startswith("sqlite") and "://" in url:
            if url.startswith("sqlite+aiosqlite:///"):
                path = url.replace("sqlite+aiosqlite:///", "")
            elif url.startswith("sqlite:///"):
                path = url.replace("sqlite:///", "")
            else:
                path = None
            if path:
                p = Path(path)
                if p.exists():
                    p.unlink()
    except Exception:
        pass

from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="session")
async def async_client():
    """
    Provide an httpx AsyncClient using ASGITransport for the FastAPI app.
    Tests should use this shared async_client fixture.
    """
    # Import the FastAPI app (try project root main first, fallback to app.main)
    # Note: import *after* we have patched sys.modules so app imports see patched db/session.
    try:
        from main import app as _app
    except Exception:
        try:
            from app.main import app as _app
        except Exception as exc:
            raise

    transport = ASGITransport(app=_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client