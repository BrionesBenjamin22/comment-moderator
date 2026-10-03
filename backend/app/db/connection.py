from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import Settings


def make_engine(settings: Settings, *, migrations: bool = False) -> Engine:
    url = settings.migration_database_url if migrations else settings.database_url
    if url is None:
        raise ValueError("MIGRATION_DATABASE_URL is required for migrations")
    return create_engine(
        url.get_secret_value(),
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": settings.db_connect_timeout_seconds,
            "options": "-c statement_timeout=5000",
        },
    )


def check_database(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def make_session_factory(engine: Engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
