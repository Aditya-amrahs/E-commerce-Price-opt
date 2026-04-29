from __future__ import annotations

import pandas as pd

from ml.config.settings import settings


def train_validation_test_split(
    df: pd.DataFrame,
    target_column: str,
    time_column: str = "order_purchase_timestamp",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if time_column in df.columns:
        ordered = df.sort_values(time_column).reset_index(drop=True)
        test_start = int(len(ordered) * (1 - settings.test_size))
        validation_start = int(
            len(ordered) * (1 - settings.test_size - settings.validation_size)
        )
        train = ordered.iloc[:validation_start].copy()
        validation = ordered.iloc[validation_start:test_start].copy()
        test = ordered.iloc[test_start:].copy()
    else:
        ordered = df.sample(frac=1, random_state=settings.random_seed).reset_index(
            drop=True
        )
        test_start = int(len(ordered) * (1 - settings.test_size))
        validation_start = int(
            len(ordered) * (1 - settings.test_size - settings.validation_size)
        )
        train = ordered.iloc[:validation_start].copy()
        validation = ordered.iloc[validation_start:test_start].copy()
        test = ordered.iloc[test_start:].copy()
    for frame in (train, validation, test):
        frame.dropna(subset=[target_column], inplace=True)
    return train, validation, test
