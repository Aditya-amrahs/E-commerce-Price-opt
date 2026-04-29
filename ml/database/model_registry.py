from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import insert
from sqlalchemy.engine import Engine

from ml.database.models import Base, model_registry


def register_model_run(
    engine: Engine,
    *,
    model_name: str,
    model_version: str,
    model_stage: str,
    target_name: str,
    artifact_path: Path,
    metrics: dict[str, object],
    train_rows: int,
    validation_rows: int,
    test_rows: int,
    is_active: bool = False,
) -> None:
    Base.metadata.create_all(engine, tables=[model_registry])
    payload = {
        "model_name": model_name,
        "model_version": model_version,
        "model_stage": model_stage,
        "target_name": target_name,
        "artifact_path": str(artifact_path),
        "metrics_json": json.dumps(metrics, default=str),
        "is_active": is_active,
        "train_rows": train_rows,
        "validation_rows": validation_rows,
        "test_rows": test_rows,
        "trained_at": datetime.utcnow(),
    }
    with engine.begin() as connection:
        connection.execute(insert(model_registry).values(**payload))
