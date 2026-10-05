from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://license:license@localhost:5432/license_portal"
    # Secret used to sign the checksum segment of every license key.
    # Changing it invalidates every key issued under the old secret.
    license_signing_secret: str = "dev-only-change-me"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
