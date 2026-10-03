from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: SecretStr
    migration_database_url: SecretStr | None = None
    app_env: Literal["local", "test", "production"] = "local"
    cors_origins: list[str] = ["http://localhost:3000"]
    db_connect_timeout_seconds: int = Field(default=3, ge=1, le=30)
    classifier_backend: Literal["fake"] = "fake"
    comments_page_size_default: int = Field(default=12, ge=1, le=200)
    comments_page_size_max: int = Field(default=50, ge=1, le=200)

    @model_validator(mode="after")
    def validate_configuration(self):
        for url in (self.database_url, self.migration_database_url):
            if url and not url.get_secret_value().startswith("postgresql+psycopg://"):
                raise ValueError("Database URLs must use postgresql+psycopg")
        if self.comments_page_size_default > self.comments_page_size_max:
            raise ValueError("Default page size must not exceed maximum")
        if any(
            origin == "*" or not origin.startswith(("http://", "https://"))
            for origin in self.cors_origins
        ):
            raise ValueError("CORS requires explicit HTTP origins")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
