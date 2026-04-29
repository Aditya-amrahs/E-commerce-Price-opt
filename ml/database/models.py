from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    Boolean,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


feature_matrix = Table(
    "feature_matrix",
    Base.metadata,
    Column("order_id", String(64), nullable=False),
    Column("order_item_id", Integer, nullable=False),
    Column("product_id", String(64), nullable=False),
    Column("seller_id", String(64), nullable=False),
    Column("customer_id", String(64), nullable=False),
    Column("order_purchase_timestamp", DateTime, nullable=False),
    Column("item_price", Float, nullable=False),
    Column("freight_value", Float, nullable=False),
    Column("demand_qty", Integer, nullable=False),
    Column("feature_payload_json", Text, nullable=False),
)

model_registry = Table(
    "model_registry",
    Base.metadata,
    Column("model_registry_id", Integer, primary_key=True, autoincrement=True),
    Column("model_name", String(128), nullable=False),
    Column("model_version", String(128), nullable=False),
    Column("model_stage", String(64), nullable=False),
    Column("target_name", String(128), nullable=False),
    Column("artifact_path", String(512), nullable=False),
    Column("metrics_json", Text, nullable=False),
    Column("is_active", Boolean, nullable=False, default=False),
    Column("train_rows", Integer, nullable=False),
    Column("validation_rows", Integer, nullable=False),
    Column("test_rows", Integer, nullable=False),
    Column("trained_at", DateTime, nullable=False),
)
