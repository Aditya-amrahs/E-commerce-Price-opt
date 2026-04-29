# Peer Handoff: US-01 to US-14 Context

This project is currently complete for `US-01` to `US-05`. The data and model foundation is in place and should now be treated as the shared base for the remaining user stories.

## What is already covered by US-01 to US-05

### US-01 Data Collection

Purpose: load all 9 Olist CSV files into raw relational tables.

Relevant files:
- `ingestion/csv_loader.py`
- `ingestion/db_writer.py`
- `database/engine.py`
- `config/constants.py`
- `run_us01_us05.py`

What it does:
- Reads all Olist CSVs from `data/raw/`
- Normalizes columns and known date fields
- Writes raw tables into the local SQLAlchemy database

Raw source-of-truth tables created:
- `raw_customers`
- `raw_geolocation`
- `raw_order_items`
- `raw_order_payments`
- `raw_order_reviews`
- `raw_orders`
- `raw_products`
- `raw_sellers`
- `raw_product_category_translation`

### US-02 Data Preprocessing

Purpose: clean and validate records before feature creation and modeling.

Relevant files:
- `preprocessing/cleaner.py`
- `preprocessing/validators.py`
- `config/constants.py`
- `run_us01_us05.py`

What it does:
- Removes duplicates
- Casts numeric and datetime columns
- Filters modeling data to clean `delivered` orders
- Handles missing customer, seller, and product fields
- Applies IQR flags for price and freight
- Generates invalid-record reports

Outputs:
- `artifacts/key_quality_report.csv`
- `artifacts/invalid_order_statuses.csv`
- `artifacts/invalid_price_rows.csv`

### US-03 Feature Engineering

Purpose: create model-ready pricing and demand features.

Relevant files:
- `features/engineer.py`
- `features/feature_store.py`
- `database/models.py`

What it does:
- Creates time, price, freight, product, seller, customer, lag, rolling, and trend features
- Stores a feature-ready dataset for downstream services
- Keeps the model feature matrix in both file and database form

Important design choice:
- Leakage-prone features such as post-purchase review/delivery outcome signals are excluded from the price model path

Outputs:
- `artifacts/features/model_features.parquet`
- `data/processed/olist_feature_ready_dataset.csv`
- DB table: `feature_matrix`

### US-04 Linear Regression Baseline

Purpose: provide the baseline model for price prediction.

Relevant files:
- `preprocessing/pipeline.py`
- `utils/splitter.py`
- `utils/metrics.py`
- `models/linear_model.py`

What it does:
- Builds a preprocessing pipeline
- Uses chronological train/validation/test split
- Trains a clipped Ridge baseline on `log1p(item_price)`
- Saves predictions and residuals for the hybrid stage

Outputs:
- `artifacts/models/linear_regression_pipeline.joblib`
- `artifacts/models/linear_metrics.json`
- `artifacts/models/linear_residuals.parquet`

### US-05 XGBoost Model

Purpose: improve the baseline by learning residual corrections.

Relevant files:
- `models/xgb_model.py`
- `models/hybrid.py`
- `database/model_registry.py`
- `run_us01_us05.py`

What it does:
- Trains XGBoost on baseline residuals
- Uses validation-aware training and regularization
- Builds a hybrid predictor: linear baseline + residual correction
- Saves performance comparison and model registry records

Outputs:
- `artifacts/models/xgb_residual_model.joblib`
- `artifacts/models/hybrid_bundle.joblib`
- `artifacts/models/xgb_metrics.json`
- `artifacts/models/baseline_vs_hybrid_metrics.csv`
- DB table: `model_registry`

Current verified result:
- Linear test: MAE `56.20`, RMSE `156.27`, R2 `0.349`
- Hybrid test: MAE `51.56`, RMSE `143.75`, R2 `0.449`

## Shared contract the other peers should follow

The remaining work should treat these as stable interfaces:

- Raw data source: DB raw tables loaded by `run_us01_us05.py`
- Clean feature dataset: `data/processed/olist_feature_ready_dataset.csv`
- Feature store artifact: `artifacts/features/model_features.parquet`
- Final model bundle for prediction use: `artifacts/models/hybrid_bundle.joblib`
- Hybrid inference helper: `models/hybrid.py` -> `predict_hybrid()`

Do not re-implement ingestion, cleaning, or feature creation separately in later user stories. Reuse these outputs so API, dashboard, logic, and deployment all stay consistent.

## How US-06 to US-09 should proceed

Owner theme: analytics + API + pricing engine + dashboard.

### US-06 Demand Elasticity

Goal:
- Estimate how demand changes with price at product/category/segment level

Recommended approach:
- Start from `data/processed/olist_feature_ready_dataset.csv`
- Use engineered lag and demand features from `features/engineer.py`
- Build elasticity analysis as a separate module, not inside current training files

Suggested new files:
- `models/elasticity.py`
- `notebooks/06_demand_elasticity.ipynb` if analysis notebook is needed

Suggested logic:
- Aggregate by product, category, month, or seller depending on sparsity
- Use log-log regression or controlled grouped elasticity estimation
- Output elasticity tables and confidence flags

Suggested outputs:
- `artifacts/models/elasticity_metrics.csv`
- `artifacts/models/elasticity_summary.json`

Important:
- Use the same cleaned dataset and same time logic as `utils/splitter.py`
- Do not use future rows when computing historical elasticity for dynamic pricing logic

### US-07 Pricing API

Goal:
- Serve optimal price or predicted price recommendations through FastAPI

Recommended approach:
- Load the hybrid model bundle from `artifacts/models/hybrid_bundle.joblib`
- Reuse `predict_hybrid()` from `models/hybrid.py`
- Do not rebuild features manually inside the API if the request payload can map to the trained feature schema cleanly

Suggested new files:
- `api/main.py`
- `api/schemas.py`
- `api/services/pricing_service.py`

Suggested API responsibilities:
- Load model once at startup
- Validate request fields
- Build inference dataframe aligned to training feature columns
- Return predicted price and optionally elasticity-adjusted recommendation

Important:
- The API peer should align request schema to the feature columns already used by `models/hybrid.py`
- If new inference-time transformations are needed, keep them in a reusable service module, not inside route handlers

### US-08 Business Dashboard

Goal:
- Show price insights, model metrics, demand patterns, and recommended prices

Recommended approach:
- Use `data/processed/olist_feature_ready_dataset.csv` for charts
- Use model metric artifacts from `artifacts/models/`
- Read API responses from US-07 for live recommendation cards if needed

Suggested frontend data sources:
- `artifacts/models/linear_metrics.json`
- `artifacts/models/xgb_metrics.json`
- `artifacts/models/baseline_vs_hybrid_metrics.csv`
- Elasticity outputs from US-06

Suggested views:
- Model performance summary
- Price distribution and cluster insights
- Demand trend and elasticity views
- Product/category recommendation explorer

Important:
- The dashboard should not directly own model logic
- It should consume prepared artifacts or API endpoints

### US-09 Dynamic Pricing

Goal:
- Convert prediction + elasticity logic into pricing recommendation rules

Recommended approach:
- Keep this as business-logic orchestration on top of US-05 and US-06
- Use hybrid prediction as the baseline expected price
- Apply rule-based adjustments using elasticity, seller/category context, and policy bounds

Suggested new files:
- `pricing/engine.py`
- `pricing/rules.py`
- `pricing/policy.py`

Suggested logic parts:
- Floor and ceiling rules
- Max percentage change guardrails
- Margin protection
- Elasticity-aware uplift/downlift
- Optional inventory/promotion hooks if added later

Important:
- Separate “predicted price” from “recommended action price”
- Predicted price comes from the model; recommended price should come from explicit pricing policy

## How US-10 to US-14 should proceed

Owner theme: extension logic + storage hardening + optimization + UX + deployment.

### US-10 Competitor Analysis

Goal:
- Add external or synthetic competitor price comparison logic

Recommended approach:
- Keep competitor data in separate tables or files
- Do not mix competitor columns into existing raw Olist tables unless the source is stable and versioned

Suggested new files:
- `competitor/collector.py`
- `competitor/compare.py`
- `database/models.py` extension for competitor tables if needed

Suggested outputs:
- competitor-vs-our-price comparison table
- underpriced/overpriced signal table

### US-11 Data Storage

Goal:
- Finalize storage design for broader app usage

Current base already exists:
- DB engine in `database/engine.py`
- feature store table in `database/models.py`
- model registry table in `database/models.py`

Recommended next step:
- Add migration tooling and versioned schema evolution
- Introduce separate tables for recommendation logs, API request logs, elasticity outputs, and competitor data

Suggested new files:
- `database/migrations/...`
- maybe `database/repositories/` for CRUD abstraction

### US-12 Model Optimization

Goal:
- Improve model performance beyond current US-05 hybrid

Recommended approach:
- Start from current hybrid as the benchmark
- Tune XGBoost hyperparameters and feature subsets
- Compare against the saved metrics in `artifacts/models/baseline_vs_hybrid_metrics.csv`

Suggested new files:
- `models/tuning.py`
- `notebooks/07_model_optimization.ipynb`

Important:
- Keep train/validation/test chronology unchanged
- Log every tuned run into `model_registry`
- Do not overwrite the current baseline bundle without versioning

### US-13 UI Enhancements

Goal:
- Improve dashboard UX after US-08 is functional

Recommended approach:
- This should build on the dashboard peer’s output, not on the ML code directly
- Focus on discoverability, filtering, responsiveness, and actionable presentation

Suggested areas:
- better category/product filters
- comparison cards
- trend highlighting
- recommendation explanation widgets

### US-14 Azure Deployment

Goal:
- Deploy DB, API, and frontend with minimal conflict

Recommended approach:
- Keep the current vendor-neutral SQLAlchemy design
- Move local `DATABASE_URL` to Azure SQL connection string
- Deploy FastAPI and frontend separately if needed

Likely deployment targets:
- Azure SQL for database
- Azure App Service or Container Apps for FastAPI
- Azure Static Web Apps or equivalent for frontend
- Blob storage if artifact hosting is separated later

Important:
- The deploy peer should use the current artifact and DB contracts rather than changing training code

## Practical team split

Peer 1: `US-01` to `US-05`
- Already completed
- Owns data pipeline, feature pipeline, baseline model, hybrid model

Peer 2: `US-06` to `US-09`
- Should build analytics, API, dashboard, and pricing logic on top of:
  - `models/hybrid.py`
  - `artifacts/models/hybrid_bundle.joblib`
  - `data/processed/olist_feature_ready_dataset.csv`

Peer 3: `US-10` to `US-14`
- Should extend storage, optimization, deployment, and extra logic without changing the current data/model contract unless versioned

## Recommended development rule

For all remaining user stories:
- reuse existing outputs
- do not duplicate preprocessing logic
- keep model inference through `predict_hybrid()`
- keep new business logic in separate modules
- version any schema or model changes instead of silently replacing current behavior
