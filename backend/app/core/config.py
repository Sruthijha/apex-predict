"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./apex_predict.db"
    cors_origins: str = "http://localhost:3000"
    jolpica_base_url: str = "https://api.jolpi.ca/ergast/f1"
    data_cache_dir: str = str(BACKEND_DIR.parent / "data" / "raw")
    processed_data_dir: str = str(BACKEND_DIR.parent / "data" / "processed")
    model_artifact_dir: str = str(BACKEND_DIR.parent / "data" / "models")
    simulation_seed: int = 42

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
