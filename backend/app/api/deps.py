from __future__ import annotations

from app.core.config import get_settings
from app.db.session import get_db
from app.services.data_store import DataStore, get_data_store

__all__ = ["get_store", "get_model_dir", "get_db"]


def get_store() -> DataStore:
    return get_data_store(get_settings().processed_data_dir)


def get_model_dir() -> str:
    return get_settings().model_artifact_dir
