# E-Commerce Price Optimization Engine

Current implementation focus: US-01 to US-05 for the Olist Brazilian E-Commerce dataset.

## Setup

1. Copy `.env.example` to `.env`.
2. Put the 9 Olist CSV files in `data/raw/`.
3. Install dependencies:

```powershell
pip install -r req.txt
```

4. Run the US-01 to US-05 pipeline:

```powershell
python run_us01_us05.py
```

## Outputs

- Raw DB tables: `raw_customers`, `raw_geolocation`, `raw_order_items`, `raw_order_payments`, `raw_order_reviews`, `raw_orders`, `raw_products`, `raw_sellers`, `raw_product_category_translation`
- Feature matrix: `artifacts/features/model_features.parquet`
- Dashboard-ready CSV: `data/processed/olist_feature_ready_dataset.csv`
- Linear model pipeline: `artifacts/models/linear_regression_pipeline.joblib`
- Linear residuals for US-05 XGBoost stacking: `artifacts/models/linear_residuals.parquet`
- XGBoost residual model: `artifacts/models/xgb_residual_model.joblib`
- Hybrid bundle: `artifacts/models/hybrid_bundle.joblib`
- Model comparison: `artifacts/models/baseline_vs_hybrid_metrics.csv`
- Metrics: `artifacts/models/linear_metrics.json`, `artifacts/models/xgb_metrics.json`

## Database

Set `DATABASE_URL` in `.env` to SQL Server/Azure SQL when available:

```text
DATABASE_URL=mssql+pyodbc://localhost/olist_price_opt?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Trusted_Connection=yes
```

The fallback `sqlite:///artifacts/local_dev.db` is only for quick local testing.
