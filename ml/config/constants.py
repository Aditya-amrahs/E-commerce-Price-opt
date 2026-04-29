from __future__ import annotations

RANDOM_SEED = 42

OLIST_CSV_TABLES: dict[str, str] = {
    "olist_customers_dataset.csv": "raw_customers",
    "olist_geolocation_dataset.csv": "raw_geolocation",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_order_payments_dataset.csv": "raw_order_payments",
    "olist_order_reviews_dataset.csv": "raw_order_reviews",
    "olist_orders_dataset.csv": "raw_orders",
    "olist_products_dataset.csv": "raw_products",
    "olist_sellers_dataset.csv": "raw_sellers",
    "product_category_name_translation.csv": "raw_product_category_translation",
}

DATE_COLUMNS: dict[str, list[str]] = {
    "raw_orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "raw_order_reviews": ["review_creation_date", "review_answer_timestamp"],
    "raw_order_items": ["shipping_limit_date"],
}

KEY_COLUMNS: dict[str, list[str]] = {
    "raw_customers": ["customer_id"],
    "raw_geolocation": ["geolocation_zip_code_prefix"],
    "raw_order_items": ["order_id", "order_item_id"],
    "raw_order_payments": ["order_id", "payment_sequential"],
    "raw_order_reviews": ["review_id", "order_id"],
    "raw_orders": ["order_id"],
    "raw_products": ["product_id"],
    "raw_sellers": ["seller_id"],
    "raw_product_category_translation": ["product_category_name"],
}

MODELING_TARGET = "item_price"
RESIDUAL_TARGET = "linear_residual"

PRICE_MODEL_EXCLUDED_FEATURES = {
    "demand_qty",
    "category_month_demand",
    "seller_month_order_count",
    "total_item_cost",
    "freight_ratio",
    "product_avg_price",
    "category_avg_price",
    "relative_category_price",
    "payment_value",
    "payment_installments",
    "payment_types",
    "review_score",
    "price_cluster",
    "price_iqr_outlier",
    "delivery_days",
    "estimated_delivery_days",
    "late_delivery_days",
    "late_delivery_flag",
    "order_status",
    "year_month",
}

VALID_ORDER_STATUSES = {
    "approved",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
    "canceled",
    "created",
}

MODELING_ORDER_STATUSES = {
    "delivered",
}
