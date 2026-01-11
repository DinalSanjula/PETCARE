import sys
import os
import asyncio
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# ------------------------------------------------------------------
# Ensure project root is on sys.path
# ------------------------------------------------------------------
sys.path.append(str(Path(__file__).resolve().parents[1]))

# ------------------------------------------------------------------
# Import Base and models
# ------------------------------------------------------------------
from db import Base
import Users.models.user_model
import Clinics.models.models
import Appointments.model.booking_models
import Reports.models.models
import Notification.model.notification_model
import Users.models.logout_and_forgetpw_model
# ------------------------------------------------------------------

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def get_database_url():
    """
    Get database URL with fallback logic:
    1. DATABASE_URL (Docker/production)
    2. DATABASE_URL_LOCAL (local development)
    3. Raise error if neither is set
    """
    database_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_LOCAL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Please set DATABASE_URL or DATABASE_URL_LOCAL environment variable."
        )

    # Debug: Print which URL is being used (hide password)
    safe_url = database_url.split('@')[1] if '@' in database_url else database_url
    print(f"[Alembic] Using database: {safe_url}")

    return database_url


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    database_url = get_database_url()

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode (ASYNC)."""
    database_url = get_database_url()

    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
        future=True,
    )

    async def run_async_migrations():
        try:
            print("[Alembic] Connecting to database...")
            async with connectable.connect() as connection:
                print("[Alembic] Connected successfully, running migrations...")
                await connection.run_sync(do_run_migrations)
            print("[Alembic] Migrations completed successfully!")
        except Exception as e:
            print(f"[Alembic] Migration failed: {str(e)}")
            raise
        finally:
            await connectable.dispose()

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()