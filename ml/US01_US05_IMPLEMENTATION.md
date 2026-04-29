# US-01 to US-05 Implementation Summary

Scope completed: data ingestion, preprocessing, feature engineering, linear baseline, and XGBoost residual hybrid model for the Olist price optimization foundation.

## How To Run

```powershell
python run_us01_us05.py
```

Input files expected in `data/raw/`: all 9 Olist CSV files.

## US-01 Data Collection

- `ingestion/csv_loader.py`: reads all 9 Olist CSVs, normalizes column names, parses known date columns.
- `ingestion/db_writer.py`: writes each CSV to raw SQL tables with SQLAlchemy-compatible dtypes.
- `database/engine.py`: creates the local DB engine from `DATABASE_URL`.
- `config/constants.py`: maps CSV filenames to raw table names.

Output: raw tables such as `raw_orders`, `raw_order_items`, `raw_products`, `raw_customers`, and others.

## US-02 Preprocessing

- `preprocessing/cleaner.py`: casts numeric/date columns, removes duplicates, filters modeling data to delivered orders, handles invalid prices/freight, fills product/customer/seller fields, adds IQR flags and price clusters.
- `preprocessing/validators.py`: creates quality reports for null keys, invalid statuses, and invalid price rows.

Outputs: `artifacts/key_quality_report.csv`, `artifacts/invalid_order_statuses.csv`, `artifacts/invalid_price_rows.csv`.

## US-03 Feature Engineering

- `features/engineer.py`: builds the modeling feature matrix with product, seller, customer, time, freight, size, demand, lag, rolling, and trend features.
- Leakage control: model excludes post-purchase review/delivery/payment outcome features and same-period/global target-like averages.
- `features/feature_store.py`: saves the feature matrix to parquet/pickle, dashboard-ready CSV, and the `feature_matrix` DB table.

Outputs: `artifacts/features/model_features.parquet`, `data/processed/olist_feature_ready_dataset.csv`.

## US-04 Linear Regression Baseline

- `preprocessing/pipeline.py`: builds preprocessing with median imputation, missing indicators, robust scaling, and one-hot encoding.
- `utils/splitter.py`: creates chronological train, validation, and test splits.
- `models/linear_model.py`: trains a clipped regularized Ridge baseline with `log1p(price)` target transform, saves predictions and residuals.
- `utils/metrics.py`: computes MAE, RMSE, and R2.

Outputs: `artifacts/models/linear_regression_pipeline.joblib`, `artifacts/models/linear_residuals.parquet`, `artifacts/models/linear_metrics.json`.

## US-05 XGBoost Hybrid Model

- `models/xgb_model.py`: trains XGBoost on linear residuals using validation monitoring, regularized trees, residual shrinkage, residual clipping, and bounded final price predictions.
- `models/hybrid.py`: compares baseline vs hybrid metrics, saves the hybrid bundle, and provides `predict_hybrid()`.
- `database/model_registry.py`: records linear, XGBoost residual, and hybrid model runs in `model_registry`.
- `run_us01_us05.py`: runs US-01 through US-05 in one command.

Outputs: `artifacts/models/xgb_residual_model.joblib`, `artifacts/models/hybrid_bundle.joblib`, `artifacts/models/xgb_metrics.json`, `artifacts/models/baseline_vs_hybrid_metrics.csv`.

## Current Architecture State

- Local source of truth: SQLAlchemy DB with SQL Server/Azure SQL-compatible design.
- Modeling target: `item_price`.
- Hybrid approach: Linear/Ridge baseline plus XGBoost residual correction.
- Ready for next stage: recommendation engine/API layer can load `hybrid_bundle.joblib` and call `predict_hybrid()` for price predictions.

## Verified Run Result

Latest full run completed successfully with `python run_us01_us05.py`.

- Rows: train `66118`, validation `22039`, test `22040`.
- Linear test metrics: MAE `56.20`, RMSE `156.27`, R2 `0.349`.
- Hybrid test metrics: MAE `51.56`, RMSE `143.75`, R2 `0.449`.
- Test improvement: MAE `+4.64`, RMSE `+12.51`, R2 `+0.100`.
