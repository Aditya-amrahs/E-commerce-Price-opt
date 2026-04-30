from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.analysis_service import get_analysis
from backend.services.model_service import run_optimization
from backend.pricing import adjust_price
from backend.dashboard import plot_prices

import sys
import os
import joblib
import pandas as pd

from ml.models.hybrid import predict_hybrid
from ml.models.elasticity import calculate_elasticity

# setup path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# create app
app = FastAPI()

# load model
bundle = joblib.load("artifacts/models/hybrid_bundle.joblib")

# load dataset
data = pd.read_csv("data/processed/olist_feature_ready_dataset.csv")

# enable static for chart
app.mount("/static", StaticFiles(directory="."), name="static")

# allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTES ---------------- #


@app.get("/")
def home():
    return {"message": "API is working"}


@app.get("/analysis")
def analysis():
    return get_analysis()


@app.get("/optimize")
def optimize():
    return run_optimization()


@app.get("/price")
def get_price(index: int = 0):
    features = data.iloc[[index]]

    prediction = predict_hybrid(bundle, features)[0]
    demand = features["order_item_id"].values[0]

    final_price = adjust_price(prediction, demand)

    start = index
    end = index + 20
    sample_prices = data["freight_value"].iloc[start:end].tolist()

    plot_prices(sample_prices)

    return {
        "base_price": float(prediction),
        "final_price": float(final_price),
        "message": "Chart saved as price_plot.png",
    }


# adjust pricing API
@app.get("/adjust")
def adjust(predicted_price: float, demand: int):
    adjusted = adjust_price(predicted_price, demand)

    return {
        "predicted_price": predicted_price,
        "demand": demand,
        "adjusted_price": adjusted,
    }
