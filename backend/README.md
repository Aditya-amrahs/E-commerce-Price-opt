this folder is for backend work
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ core/
│  │  └─ main.py
│  └─ README.md


backend/ peer:
builds FastAPI for US7 and pricing engine logic for US9
should consume ML outputs from:
artifacts/models/hybrid_bundle.joblib
data/processed/olist_feature_ready_dataset.csv
ml/models/hybrid.py