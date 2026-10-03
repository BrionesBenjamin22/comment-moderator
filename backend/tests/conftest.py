import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.config import Settings
from app.db.provision import main as provision


@pytest.fixture(scope="session")
def postgres():
    url = os.environ.get("TEST_DATABASE_URL")
    api_url = os.environ.get("TEST_API_DATABASE_URL")
    if not url or not api_url:
        pytest.skip("Set TEST_DATABASE_URL and TEST_API_DATABASE_URL for PostgreSQL tests")
    parsed = make_url(url)
    if not parsed.database or not parsed.database.endswith("_test"):
        pytest.fail("Integration tests require an isolated database ending in _test")
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    original = {
        key: os.environ.get(key)
        for key in (
            "DATABASE_URL",
            "MIGRATION_DATABASE_URL",
            "DB_APP_PASSWORD",
        )
    }
    os.environ.update(
        {
            "DATABASE_URL": api_url,
            "MIGRATION_DATABASE_URL": url,
            "DB_APP_PASSWORD": make_url(api_url).password or "",
        }
    )
    engine = create_engine(url)
    try:
        command.upgrade(config, "head")
        provision()
        yield engine, api_url, config
    finally:
        command.downgrade(config, "base")
        engine.dispose()
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture
def settings():
    return Settings(
        _env_file=None,
        database_url="postgresql+psycopg://unused:unused@127.0.0.1:1/unused_test",
        app_env="test",
    )
