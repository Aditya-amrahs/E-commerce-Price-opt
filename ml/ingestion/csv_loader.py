from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.config.constants import DATE_COLUMNS, OLIST_CSV_TABLES
from ml.config.settings import settings
from ml.utils.logger import get_logger

logger = get_logger(__name__)


def _read_csv(path: Path, table_name: str) -> pd.DataFrame:
    date_columns = [c for c in DATE_COLUMNS.get(table_name, [])]
    df = pd.read_csv(
        path,
        encoding="utf-8",
        dtype=str,
        low_memory=False,
    )
    df.columns = [c.strip().lower() for c in df.columns]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=False)
    return df


def load_olist_csvs(raw_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    raw_dir = raw_dir or settings.raw_data_dir
    missing = [name for name in OLIST_CSV_TABLES if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing Olist CSV files in {raw_dir}: {', '.join(missing)}"
        )

    tables: dict[str, pd.DataFrame] = {}
    for csv_name, table_name in OLIST_CSV_TABLES.items():
        path = raw_dir / csv_name
        frame = _read_csv(path, table_name)
        tables[table_name] = frame
        logger.info("Loaded %s as %s with %s rows", csv_name, table_name, len(frame))
    return tables
