import asyncio
import sys
from logging.config import fileConfig

# Windows에서 asyncpg 호환성 문제 해결
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.database import Base

# 모든 모델 import (Alembic이 테이블을 인식하도록)
from app.models import Pet, User, Walk, WalkPhoto  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# PostGIS/tiger 내장 테이블 무시
EXCLUDE_TABLES = {
    "spatial_ref_sys", "topology", "layer",
    "geocode_settings", "geocode_settings_default",
    "loader_platform", "loader_variables", "loader_lookuptables",
    "pagc_gaz", "pagc_lex", "pagc_rules",
    "county", "county_lookup", "countysub_lookup",
    "state", "state_lookup", "place", "place_lookup",
    "zip_lookup", "zip_lookup_all", "zip_lookup_base",
    "zip_state", "zip_state_loc",
    "addr", "addrfeat", "edges", "faces", "featnames",
    "cousub", "tract", "tabblock", "tabblock20", "bg", "zcta5",
    "direction_lookup", "secondary_unit_lookup", "street_type_lookup",
}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in EXCLUDE_TABLES:
        return False
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
