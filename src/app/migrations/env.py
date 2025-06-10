import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from alembic import context
import sys

from app.db.models import Package, PackageType, Company
from app.db.models.base import Base
from app.core.config import get_settings

settings = get_settings()

# this is the Alembic Config object
config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    try:
        connectable = create_async_engine(DATABASE_URL, echo=settings.debug)
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
