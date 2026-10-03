"""Provision the database execution credential, not application identities."""

import os

from psycopg import connect, sql
from sqlalchemy.engine import make_url

from app.config import Settings


def main():
    settings = Settings()
    if settings.migration_database_url is None:
        raise ValueError("MIGRATION_DATABASE_URL is required")
    password = os.environ["DB_APP_PASSWORD"]
    url = make_url(settings.migration_database_url.get_secret_value())
    role = sql.Identifier("butchery_api")
    with connect(
        host=url.host,
        port=url.port or 5432,
        dbname=url.database,
        user=url.username,
        password=url.password,
        connect_timeout=3,
    ) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            ("butchery_api",),
        ).fetchone()
        if not exists:
            connection.execute(sql.SQL("CREATE ROLE {} LOGIN").format(role))
        connection.execute(
            sql.SQL(
                "ALTER ROLE {} PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT"
            ).format(role, sql.Literal(password))
        )
        connection.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(url.database),
                role,
            )
        )
        connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        connection.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(role))
        connection.execute(
            sql.SQL("GRANT SELECT, INSERT ON comments, classifications, feedbacks TO {}").format(
                role
            )
        )
        connection.execute(
            sql.SQL(
                "REVOKE UPDATE, DELETE, TRUNCATE ON comments, classifications, feedbacks FROM {}"
            ).format(role)
        )


if __name__ == "__main__":
    main()
