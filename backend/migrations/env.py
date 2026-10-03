from alembic import context

from app.config import Settings
from app.db.base import Base
from app.db.connection import make_engine
from app.models import Classification, Comment, Feedback  # noqa: F401

target_metadata = Base.metadata


def run_migrations():
    settings = Settings()
    if context.is_offline_mode():
        if settings.migration_database_url is None:
            raise ValueError("MIGRATION_DATABASE_URL is required")
        context.configure(
            url=settings.migration_database_url.get_secret_value(),
            target_metadata=target_metadata,
            literal_binds=True,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        engine = make_engine(settings, migrations=True)
        try:
            with engine.connect() as connection:
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                )
                with context.begin_transaction():
                    context.run_migrations()
        finally:
            engine.dispose()


run_migrations()
