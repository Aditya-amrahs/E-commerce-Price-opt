from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace({0: np.nan})


def _merge_history_features(
    data: pd.DataFrame,
    group_col: str,
    month_col: str,
    prefix: str,
    value_col: str = "item_price",
) -> pd.DataFrame:
    monthly = (
        data.groupby([group_col, month_col], as_index=False)
        .agg(
            month_demand=("order_id", "count"),
            month_avg_price=(value_col, "mean"),
            month_avg_freight=("freight_value", "mean"),
        )
        .sort_values([group_col, month_col])
    )
    grouped = monthly.groupby(group_col, sort=False)
    monthly[f"{prefix}_demand_lag1"] = grouped["month_demand"].shift(1)
    monthly[f"{prefix}_price_lag1"] = grouped["month_avg_price"].shift(1)
    monthly[f"{prefix}_freight_lag1"] = grouped["month_avg_freight"].shift(1)
    monthly[f"{prefix}_demand_roll3"] = grouped["month_demand"].transform(
        lambda s: s.shift(1).rolling(3, min_periods=1).mean()
    )
    monthly[f"{prefix}_price_roll3"] = grouped["month_avg_price"].transform(
        lambda s: s.shift(1).rolling(3, min_periods=1).mean()
    )
    monthly[f"{prefix}_price_trend"] = (
        monthly[f"{prefix}_price_lag1"] - monthly[f"{prefix}_price_roll3"]
    )
    merge_cols = [
        group_col,
        month_col,
        f"{prefix}_demand_lag1",
        f"{prefix}_price_lag1",
        f"{prefix}_freight_lag1",
        f"{prefix}_demand_roll3",
        f"{prefix}_price_roll3",
        f"{prefix}_price_trend",
    ]
    return data.merge(monthly[merge_cols], on=[group_col, month_col], how="left")


def build_feature_matrix(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    items = tables["raw_order_items"].copy()
    orders = tables["raw_orders"].copy()
    products = tables["raw_products"].copy()
    customers = tables["raw_customers"].copy()
    sellers = tables["raw_sellers"].copy()

    data = (
        items.merge(orders, on="order_id", how="inner")
        .merge(products, on="product_id", how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(sellers, on="seller_id", how="left", suffixes=("_customer", "_seller"))
    )

    if "raw_product_category_translation" in tables:
        translation = tables["raw_product_category_translation"].copy()
        data = data.merge(translation, on="product_category_name", how="left")
        data["product_category_name_english"] = data[
            "product_category_name_english"
        ].fillna(data["product_category_name"])

    payments = tables.get("raw_order_payments")
    if payments is not None:
        payment_features = payments.groupby("order_id", as_index=False).agg(
            payment_value=("payment_value", "sum"),
            payment_installments=("payment_installments", "max"),
            payment_types=("payment_type", "nunique"),
        )
        data = data.merge(payment_features, on="order_id", how="left")

    reviews = tables.get("raw_order_reviews")
    if reviews is not None:
        review_features = reviews.groupby("order_id", as_index=False).agg(
            review_score=("review_score", "mean"),
        )
        data = data.merge(review_features, on="order_id", how="left")

    data["order_purchase_timestamp"] = pd.to_datetime(
        data["order_purchase_timestamp"], errors="coerce"
    )
    data = data.dropna(subset=["order_purchase_timestamp", "price"])
    data = data.sort_values(["order_purchase_timestamp", "order_id", "order_item_id"]).reset_index(
        drop=True
    )

    data["item_price"] = pd.to_numeric(data["price"], errors="coerce")
    data["freight_value"] = pd.to_numeric(data["freight_value"], errors="coerce").fillna(0)
    data["total_item_cost"] = data["item_price"] + data["freight_value"]
    data["freight_ratio"] = _safe_divide(data["freight_value"], data["item_price"]).fillna(0)
    data["log_freight_value"] = np.log1p(data["freight_value"])

    data["purchase_year"] = data["order_purchase_timestamp"].dt.year
    data["purchase_month"] = data["order_purchase_timestamp"].dt.month
    data["purchase_dayofweek"] = data["order_purchase_timestamp"].dt.dayofweek
    data["purchase_hour"] = data["order_purchase_timestamp"].dt.hour
    data["purchase_day"] = data["order_purchase_timestamp"].dt.day
    data["is_weekend"] = data["purchase_dayofweek"].isin([5, 6]).astype(int)
    data["month_sin"] = np.sin(2 * np.pi * data["purchase_month"] / 12)
    data["month_cos"] = np.cos(2 * np.pi * data["purchase_month"] / 12)
    data["dow_sin"] = np.sin(2 * np.pi * data["purchase_dayofweek"] / 7)
    data["dow_cos"] = np.cos(2 * np.pi * data["purchase_dayofweek"] / 7)

    delivery = pd.to_datetime(data.get("order_delivered_customer_date"), errors="coerce")
    estimated = pd.to_datetime(data.get("order_estimated_delivery_date"), errors="coerce")
    purchase = data["order_purchase_timestamp"]
    data["delivery_days"] = (delivery - purchase).dt.total_seconds().div(86400)
    data["estimated_delivery_days"] = (estimated - purchase).dt.total_seconds().div(86400)
    data["late_delivery_days"] = (delivery - estimated).dt.total_seconds().div(86400)
    data["late_delivery_flag"] = (data["late_delivery_days"] > 0).fillna(False).astype(int)

    data["product_volume_cm3"] = (
        data["product_length_cm"].fillna(0)
        * data["product_height_cm"].fillna(0)
        * data["product_width_cm"].fillna(0)
    )
    data["product_weight_kg"] = data["product_weight_g"].fillna(0) / 1000
    data["log_product_volume_cm3"] = np.log1p(data["product_volume_cm3"])
    data["log_product_weight_kg"] = np.log1p(data["product_weight_kg"])

    product_month = (
        data.groupby(["product_id", "purchase_year", "purchase_month"])["order_id"]
        .transform("count")
        .astype(int)
    )
    category_col = (
        "product_category_name_english"
        if "product_category_name_english" in data.columns
        else "product_category_name"
    )
    category_month = data.groupby([category_col, "purchase_year", "purchase_month"])[
        "order_id"
    ].transform("count")

    data["demand_qty"] = product_month
    data["category_month_demand"] = category_month.astype(int)
    data["seller_month_order_count"] = data.groupby(
        ["seller_id", "purchase_year", "purchase_month"]
    )["order_id"].transform("count")
    customer_order_sequence = (
        data[["customer_unique_id", "order_id", "order_purchase_timestamp"]]
        .drop_duplicates()
        .sort_values(["customer_unique_id", "order_purchase_timestamp", "order_id"])
    )
    customer_order_sequence["customer_prior_order_count"] = (
        customer_order_sequence.groupby("customer_unique_id").cumcount()
    )
    data = data.merge(
        customer_order_sequence[["order_id", "customer_prior_order_count"]],
        on="order_id",
        how="left",
    )
    data["customer_order_count"] = data["customer_prior_order_count"].fillna(0)
    data["same_state_customer_seller"] = (
        data["customer_state"].fillna("unknown") == data["seller_state"].fillna("unknown")
    ).astype(int)
    data["year_month"] = data["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()

    data = _merge_history_features(data, "product_id", "year_month", "product")
    data = _merge_history_features(data, category_col, "year_month", "category")
    data = _merge_history_features(data, "seller_id", "year_month", "seller")

    first_product_purchase = data.groupby("product_id")["order_purchase_timestamp"].transform("min")
    first_seller_purchase = data.groupby("seller_id")["order_purchase_timestamp"].transform("min")
    data["product_age_days"] = (
        data["order_purchase_timestamp"] - first_product_purchase
    ).dt.total_seconds().div(86400)
    data["seller_age_days"] = (
        data["order_purchase_timestamp"] - first_seller_purchase
    ).dt.total_seconds().div(86400)
    data["log_product_age_days"] = np.log1p(data["product_age_days"].clip(lower=0))
    data["log_seller_age_days"] = np.log1p(data["seller_age_days"].clip(lower=0))

    lag_fill_defaults = {
        "product_demand_lag1": 0,
        "product_demand_roll3": 0,
        "product_price_trend": 0,
        "category_demand_lag1": 0,
        "category_demand_roll3": 0,
        "category_price_trend": 0,
        "seller_demand_lag1": 0,
        "seller_demand_roll3": 0,
        "seller_price_trend": 0,
    }
    for col, default in lag_fill_defaults.items():
        if col in data.columns:
            data[col] = data[col].fillna(default)

    keep = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "order_purchase_timestamp",
        "item_price",
        "freight_value",
        "total_item_cost",
        "freight_ratio",
        "purchase_year",
        "purchase_month",
        "purchase_day",
        "purchase_dayofweek",
        "purchase_hour",
        "is_weekend",
        "month_sin",
        "month_cos",
        "dow_sin",
        "dow_cos",
        "delivery_days",
        "estimated_delivery_days",
        "late_delivery_days",
        "late_delivery_flag",
        "product_volume_cm3",
        "product_weight_kg",
        "log_product_volume_cm3",
        "log_product_weight_kg",
        "demand_qty",
        "category_month_demand",
        "seller_month_order_count",
        "customer_order_count",
        "same_state_customer_seller",
        "product_demand_lag1",
        "product_price_lag1",
        "product_freight_lag1",
        "product_demand_roll3",
        "product_price_roll3",
        "product_price_trend",
        "category_demand_lag1",
        "category_price_lag1",
        "category_freight_lag1",
        "category_demand_roll3",
        "category_price_roll3",
        "category_price_trend",
        "seller_demand_lag1",
        "seller_price_lag1",
        "seller_freight_lag1",
        "seller_demand_roll3",
        "seller_price_roll3",
        "seller_price_trend",
        "product_age_days",
        "seller_age_days",
        "log_product_age_days",
        "log_seller_age_days",
        "log_freight_value",
        "price_cluster",
        "price_iqr_outlier",
        "freight_value_iqr_outlier",
        "year_month",
        "product_category_name",
        category_col,
        "customer_state",
        "seller_state",
        "order_status",
    ]
    existing = [col for col in keep if col in data.columns]
    features = data[existing].replace({np.inf: np.nan, -np.inf: np.nan}).copy()
    return features.dropna(subset=["item_price", "demand_qty"])


def model_columns(
    df: pd.DataFrame,
    excluded_extra: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    excluded = {
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "order_purchase_timestamp",
        "item_price",
    }
    if excluded_extra:
        excluded.update(excluded_extra)
    categorical = [
        col
        for col in df.columns
        if col not in excluded
        and (
            df[col].dtype == "object"
            or str(df[col].dtype) == "category"
            or pd.api.types.is_string_dtype(df[col])
        )
    ]
    numeric = [
        col
        for col in df.columns
        if col not in excluded and col not in categorical and pd.api.types.is_numeric_dtype(df[col])
    ]
    return numeric, categorical
