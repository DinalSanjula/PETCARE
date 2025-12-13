import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from alembic import context

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
import asyncio

# ---- IMPORTANT PART ----
from db import Base

# Import models so tables are registered
import app.models.user_model
import Clinics.models.models
# ------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ONE metadata only
target_metadata = Base.metadata


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
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()