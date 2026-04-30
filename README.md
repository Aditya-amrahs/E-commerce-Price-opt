# E-Commerce Price Optimization Engine

## Project Overview

E-Commerce Price Optimization Engine is an end-to-end analytics platform designed to provide intelligent, data-driven pricing strategies for e-commerce. Based on the Olist Brazilian E-Commerce dataset, it enables:

- **Machine Learning-based price optimization:** Predict optimal prices using advanced models and business rules.
- **Competitor & product analysis:** Compare each product’s price with market averages and get actionable improvement recommendations.
- **Interactive dashboard:** Visualize price trends, demand, and model performance insights.
- **REST API (FastAPI):** Query price suggestions and analytics programmatically.
- **Modern React frontend:** User-friendly UI to view recommendations, analysis, and reports.
- **Modular, scalable codebase:** Clean separation for data pipeline, backend API, and frontend visualization.

---

## Setup

1. Copy `.env.example` to `.env`.
2. Put the 9 Olist CSV files in `data/raw/`.
3. Install dependencies:
from root directory
```powershell
pip install -r requirements.txt
```

4. Run the US-01 to US-05 pipeline:
from root directory
```powershell
python -m ml.run_us01_us05 
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

---

## Backend Execution (FastAPI)

To run the backend REST API locally:

```bash
cd backend
uvicorn main:app --reload
```

- Access FastAPI docs and endpoints at: http://localhost:8000
- Main endpoints:
  - `/`: Health check
  - `/analysis`: Product price analysis
  - `/optimize`: Model optimization metrics
  - `/price`: Get price recommendation and trend plot
  - `/adjust`: Price adjustment by predicted price & demand

---

## Frontend Execution (React)

To run the React frontend locally:

```bash
cd frontend
npm install
npm start
```

- Visit http://localhost:3000 in your browser to view the dashboard and interact with analytics.
- The frontend connects automatically to the backend API for predictions, analysis, and charts.

---

## Project Structure

```
E-commerce-Price-opt/
├── data/
├── artifacts/
├── backend/
├── ml/
├── frontend/
├── requirements.txt
└── README.md
```

---

## References

- **Olist Brazilian E-Commerce Dataset:**  
  https://www.kaggle.com/olistbr/brazilian-ecommerce

---

For questions, open an issue or PR on GitHub: https://github.com/Aditya-amrahs/E-commerce-Price-opt.