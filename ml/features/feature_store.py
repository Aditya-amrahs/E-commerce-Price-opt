from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy.engine import Engine

from ml.config.settings import settings
from ml.database.engine import get_engine
from ml.database.models import Base


def save_feature_matrix(
    features: pd.DataFrame,
    engine: Engine | None = None,
    parquet_path=None,
) -> dict[str, Path]:
    path = parquet_path or settings.feature_store_path
    path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = settings.processed_data_dir / "olist_feature_ready_dataset.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(csv_path, index=False)

    stored_path = path
    try:
        features.to_parquet(path, index=False)
    except ImportError:
        stored_path = path.with_suffix(".pkl")
        features.to_pickle(stored_path)

    engine = engine or get_engine()
    Base.metadata.create_all(engine, tables=[Base.metadata.tables["feature_matrix"]])
    db_rows = features.copy()
    payload_columns = [
        col
        for col in db_rows.columns
        if col
        not in {
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "customer_id",
            "order_purchase_timestamp",
            "item_price",
            "freight_value",
            "demand_qty",
        }
    ]
    db_rows["feature_payload_json"] = db_rows[payload_columns].apply(
        lambda row: json.dumps(row.to_dict(), default=str),
        axis=1,
    )
    db_rows[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "customer_id",
            "order_purchase_timestamp",
            "item_price",
            "freight_value",
            "demand_qty",
            "feature_payload_json",
        ]
    ].to_sql("feature_matrix", engine, if_exists="replace", index=False, chunksize=5000)
    return {
        "db_table": Path("feature_matrix"),
        "feature_store_path": stored_path,
        "csv_path": csv_path,
    }


def load_feature_matrix(path=None) -> pd.DataFrame:
    path = path or settings.feature_store_path
    try:
        return pd.read_parquet(path)
    except ImportError:
        return pd.read_pickle(path.with_suffix(".pkl"))
