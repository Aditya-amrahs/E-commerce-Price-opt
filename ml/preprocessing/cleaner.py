from __future__ import annotations

import numpy as np
import pandas as pd

from ml.config.constants import DATE_COLUMNS, MODELING_ORDER_STATUSES


def cast_numeric_columns(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    numeric_columns = {
        "raw_geolocation": ["geolocation_lat", "geolocation_lng"],
        "raw_order_items": ["order_item_id", "price", "freight_value"],
        "raw_order_payments": [
            "payment_sequential",
            "payment_installments",
            "payment_value",
        ],
        "raw_order_reviews": ["review_score"],
        "raw_products": [
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
    }
    cleaned = {name: frame.copy() for name, frame in tables.items()}
    for table_name, columns in numeric_columns.items():
        frame = cleaned.get(table_name)
        if frame is None:
            continue
        for column in columns:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return cleaned


def normalize_dates(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {name: frame.copy() for name, frame in tables.items()}
    for table_name, columns in DATE_COLUMNS.items():
        frame = cleaned.get(table_name)
        if frame is None:
            continue
        for column in columns:
            if column in frame.columns:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return cleaned


def deduplicate_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {name: frame.drop_duplicates().copy() for name, frame in tables.items()}


def clean_order_items(order_items: pd.DataFrame) -> pd.DataFrame:
    data = order_items.copy()
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    data["freight_value"] = pd.to_numeric(data["freight_value"], errors="coerce")
    data = data.dropna(subset=["order_id", "product_id", "seller_id", "price"])
    data = data[(data["price"] > 0) & (data["freight_value"].fillna(0) >= 0)].copy()
    data["freight_value"] = data["freight_value"].fillna(0.0)
    data["freight_value"] = data["freight_value"].clip(lower=0)
    return data


def add_iqr_flags(
    df: pd.DataFrame, column: str, prefix: str | None = None
) -> pd.DataFrame:
    result = df.copy()
    prefix = prefix or column
    q1 = result[column].quantile(0.25)
    q3 = result[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    result[f"{prefix}_iqr_outlier"] = (
        (result[column] < lower) | (result[column] > upper)
    ).astype(int)
    result[f"{prefix}_iqr_capped"] = result[column].clip(lower=lower, upper=upper)
    return result


def add_price_clusters(df: pd.DataFrame, price_column: str = "price") -> pd.DataFrame:
    result = df.copy()
    labels = ["budget", "value", "mid", "premium", "luxury"]
    try:
        result["price_cluster"] = pd.qcut(
            result[price_column],
            q=5,
            labels=labels,
            duplicates="drop",
        ).astype(str)
    except ValueError:
        result["price_cluster"] = "mid"
    return result


def clean_for_modeling(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = deduplicate_tables(normalize_dates(cast_numeric_columns(tables)))
    if "raw_order_items" in cleaned:
        items = clean_order_items(cleaned["raw_order_items"])
        items = add_iqr_flags(items, "price")
        items = add_iqr_flags(items, "freight_value")
        items = add_price_clusters(items, "price_iqr_capped")
        cleaned["raw_order_items"] = items

    if "raw_orders" in cleaned:
        orders = cleaned["raw_orders"].copy()
        orders = orders.dropna(
            subset=["order_id", "customer_id", "order_purchase_timestamp"]
        )
        orders["order_status"] = orders["order_status"].fillna("unknown")
        orders = orders.loc[orders["order_status"].isin(MODELING_ORDER_STATUSES)].copy()
        cleaned["raw_orders"] = orders

    if "raw_products" in cleaned:
        products = cleaned["raw_products"].copy()
        products["product_category_name"] = products["product_category_name"].fillna(
            "unknown"
        )
        dimension_cols = [
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
        for col in dimension_cols:
            if col in products.columns:
                products[col] = products[col].fillna(products[col].median())
                products[col] = products[col].clip(lower=0)
        sparse_text_cols = [
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
        ]
        for col in sparse_text_cols:
            if col in products.columns:
                products[col] = products[col].fillna(0).clip(lower=0)
        cleaned["raw_products"] = products.replace({np.inf: np.nan, -np.inf: np.nan})

    if "raw_customers" in cleaned:
        customers = cleaned["raw_customers"].copy()
        for col in ("customer_city", "customer_state", "customer_zip_code_prefix"):
            if col in customers.columns:
                customers[col] = customers[col].fillna("unknown")
        cleaned["raw_customers"] = customers

    if "raw_sellers" in cleaned:
        sellers = cleaned["raw_sellers"].copy()
        for col in ("seller_city", "seller_state", "seller_zip_code_prefix"):
            if col in sellers.columns:
                sellers[col] = sellers[col].fillna("unknown")
        cleaned["raw_sellers"] = sellers
    return cleaned
