"""Application settings."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Recipe HTML Parser"
    environment: str = "local"
    database_url: str = Field(default="sqlite:///./recipe_parser.db", alias="DATABASE_URL")
    frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("FRONTEND_URL", "FRONTEND_ORIGIN"),
    )
    max_html_size_bytes: int = Field(default=2_000_000, alias="MAX_HTML_SIZE_BYTES")
    http_timeout_seconds: float = Field(default=10.0, alias="HTTP_TIMEOUT_SECONDS")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return list({self.frontend_url, "http://127.0.0.1:3000"})


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
