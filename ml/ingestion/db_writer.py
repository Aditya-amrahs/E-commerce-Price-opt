from __future__ import annotations

import pandas as pd
from sqlalchemy import BigInteger, DateTime, Float, Integer, NVARCHAR, Text
from sqlalchemy.engine import Engine

from ml.config.constants import DATE_COLUMNS
from ml.database.engine import get_engine
from ml.utils.logger import get_logger

logger = get_logger(__name__)


def _sql_dtype_for(series: pd.Series, table_name: str, column_name: str):
    if column_name in DATE_COLUMNS.get(table_name, []):
        return DateTime()
    if pd.api.types.is_integer_dtype(series):
        return BigInteger()
    if pd.api.types.is_float_dtype(series):
        return Float()
    max_len = int(series.dropna().astype(str).str.len().max() or 0)
    if max_len > 4000:
        return Text()
    return NVARCHAR(length=max(64, min(4000, max_len + 16)))


def write_raw_tables(
    tables: dict[str, pd.DataFrame],
    engine: Engine | None = None,
    if_exists: str = "replace",
) -> None:
    engine = engine or get_engine()
    for table_name, frame in tables.items():
        dtype = {
            col: _sql_dtype_for(frame[col], table_name, col) for col in frame.columns
        }
        frame.to_sql(
            table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=5000,
            dtype=dtype,
        )
        logger.info("Wrote %s rows to %s", len(frame), table_name)
