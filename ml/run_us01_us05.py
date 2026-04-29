from __future__ import annotations

from ml.config.constants import MODELING_TARGET, RESIDUAL_TARGET
from ml.config.settings import ensure_project_dirs
from ml.database.engine import get_engine
from ml.database.model_registry import register_model_run
from ml.features.engineer import build_feature_matrix
from ml.features.feature_store import save_feature_matrix
from ml.ingestion.csv_loader import load_olist_csvs
from ml.ingestion.db_writer import write_raw_tables
from ml.models.hybrid import compare_baseline_vs_hybrid, save_hybrid_bundle
from ml.models.linear_model import train_linear_regression
from ml.models.xgb_model import train_xgb_residual_model
from ml.preprocessing.cleaner import clean_for_modeling
from ml.preprocessing.validators import (
    invalid_order_statuses,
    invalid_price_rows,
    null_key_report,
)
from ml.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    ensure_project_dirs()
    engine = get_engine()

    logger.info("US-01: Loading raw Olist CSVs")
    raw_tables = load_olist_csvs()
    write_raw_tables(raw_tables, engine=engine)

    logger.info("US-02: Cleaning and validating records")
    key_report = null_key_report(raw_tables)
    invalid_statuses = invalid_order_statuses(raw_tables["raw_orders"])
    invalid_prices = invalid_price_rows(raw_tables["raw_order_items"])
    key_report.to_csv("artifacts/key_quality_report.csv", index=False)
    invalid_statuses.to_csv("artifacts/invalid_order_statuses.csv", index=False)
    invalid_prices.to_csv("artifacts/invalid_price_rows.csv", index=False)
    clean_tables = clean_for_modeling(raw_tables)

    logger.info("US-03: Building pricing feature matrix")
    features = build_feature_matrix(clean_tables)
    feature_outputs = save_feature_matrix(features, engine=engine)
    logger.info("Feature-ready CSV saved to %s", feature_outputs["csv_path"])

    logger.info("US-04: Training linear regression baseline")
    linear_result = train_linear_regression(features)
    linear_splits = linear_result["metrics"]["splits"]
    register_model_run(
        engine,
        model_name="linear_regression",
        model_version="lr_v1",
        model_stage="baseline",
        target_name=MODELING_TARGET,
        artifact_path=linear_result["model_path"],
        metrics=linear_result["metrics"],
        train_rows=linear_splits["train_rows"],
        validation_rows=linear_splits["validation_rows"],
        test_rows=linear_splits["test_rows"],
    )

    logger.info("US-05: Training XGBoost residual model and hybrid bundle")
    xgb_result = train_xgb_residual_model(linear_result)
    hybrid_bundle_path = save_hybrid_bundle(linear_result, xgb_result)
    comparison_result = compare_baseline_vs_hybrid(linear_result, xgb_result)
    register_model_run(
        engine,
        model_name="xgb_residual",
        model_version="xgb_residual_v1",
        model_stage="candidate",
        target_name=RESIDUAL_TARGET,
        artifact_path=xgb_result["model_path"],
        metrics=xgb_result["metrics"],
        train_rows=linear_splits["train_rows"],
        validation_rows=linear_splits["validation_rows"],
        test_rows=linear_splits["test_rows"],
    )
    register_model_run(
        engine,
        model_name="hybrid_linear_xgb",
        model_version="hybrid_v1",
        model_stage="candidate",
        target_name=MODELING_TARGET,
        artifact_path=hybrid_bundle_path,
        metrics=comparison_result["comparison_df"].to_dict(orient="records"),
        train_rows=linear_splits["train_rows"],
        validation_rows=linear_splits["validation_rows"],
        test_rows=linear_splits["test_rows"],
    )

    logger.info("Linear metrics saved to %s", linear_result["metrics_path"])
    logger.info("XGBoost metrics saved to %s", xgb_result["metrics_path"])
    logger.info(
        "Model comparison saved to %s", comparison_result["comparison_csv_path"]
    )
    logger.info("Hybrid bundle saved to %s", hybrid_bundle_path)


if __name__ == "__main__":
    main()
