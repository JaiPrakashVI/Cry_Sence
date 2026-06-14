from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    max_upload_mb: int = 25
    model_path: str = "ml_pipeline/saved_models/crysense_cnn.keras"
    storage_dir: str = "backend/storage"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CRYSENSE_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
