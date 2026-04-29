from fastapi import FastAPI
import joblib
import pandas as pd
from ml.models.hybrid import predict_hybrid
from backend.pricing import adjust_price   
from ml.models.elasticity import calculate_elasticity
from backend.dashboard import plot_prices

app = FastAPI()

# load model bundle
bundle = joblib.load("artifacts/models/hybrid_bundle.joblib")

# load dataset
data = pd.read_csv("data/processed/olist_feature_ready_dataset.csv")

@app.get("/")
def home():
    return {"message": "API is working"}

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
        "message": "Chart saved as price_plot.png"
    }