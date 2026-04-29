from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def _path(name: str, default: str) -> Path:
    return Path(os.getenv(name, default)).resolve()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///artifacts/local_dev.db")
    raw_data_dir: Path = _path("RAW_DATA_DIR", "data/raw")
    processed_data_dir: Path = _path("PROCESSED_DATA_DIR", "data/processed")
    artifact_dir: Path = _path("ARTIFACT_DIR", "artifacts")
    model_dir: Path = _path("MODEL_DIR", "artifacts/models")
    feature_store_path: Path = _path(
        "FEATURE_STORE_PATH", "artifacts/features/model_features.parquet"
    )
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    test_size: float = float(os.getenv("TEST_SIZE", "0.2"))
    validation_size: float = float(os.getenv("VALIDATION_SIZE", "0.2"))


settings = Settings()


def ensure_project_dirs() -> None:
    for path in (
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.artifact_dir,
        settings.model_dir,
        settings.feature_store_path.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)
