from __future__ import annotations

import pandas as pd

from ml.config.constants import KEY_COLUMNS, VALID_ORDER_STATUSES


def null_key_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for table_name, keys in KEY_COLUMNS.items():
        frame = tables.get(table_name)
        if frame is None:
            continue
        for key in keys:
            if key in frame.columns:
                rows.append(
                    {
                        "table_name": table_name,
                        "column_name": key,
                        "null_count": int(frame[key].isna().sum()),
                        "duplicate_count": int(frame.duplicated(subset=[key]).sum()),
                    }
                )
    return pd.DataFrame(rows)


def invalid_order_statuses(orders: pd.DataFrame) -> pd.DataFrame:
    if "order_status" not in orders.columns:
        return pd.DataFrame()
    mask = ~orders["order_status"].isin(VALID_ORDER_STATUSES)
    return orders.loc[mask, ["order_id", "order_status"]].copy()


def invalid_price_rows(order_items: pd.DataFrame) -> pd.DataFrame:
    required = ["order_id", "order_item_id", "price", "freight_value"]
    if not set(required).issubset(order_items.columns):
        return pd.DataFrame()
    data = order_items[required].copy()
    for col in ("price", "freight_value"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data.loc[
        data["price"].isna()
        | data["freight_value"].isna()
        | (data["price"] <= 0)
        | (data["freight_value"] < 0)
    ].copy()
