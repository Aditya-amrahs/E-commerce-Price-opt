import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

DATA_PATH = "data/processed/olist_feature_ready_dataset.csv"


def run_optimization():
    df = pd.read_csv(DATA_PATH)

    # Remove extreme outliers

    df = df[df["item_price"] < df["item_price"].quantile(0.99)]

    # Sample
    sample = df.sample(5000, random_state=42)

    # Precompute group statistics
    product_price_map = df.groupby("product_id")["item_price"].median()
    category_price_map = df.groupby("product_category_name_english")["item_price"].median()

    global_price = df["item_price"].median()

    # Smart prediction
    preds = []

    for _, row in sample.iterrows():

        if row["product_id"] in product_price_map:
            pred = product_price_map[row["product_id"]]

        elif row["product_category_name_english"] in category_price_map:
            pred = category_price_map[row["product_category_name_english"]]

        else:
            pred = global_price

        preds.append(pred)

    preds = np.array(preds)
    y_sample = sample["item_price"].values

    # Metrics
    mse = mean_squared_error(y_sample, preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_sample, preds)

    avg_price = y_sample.mean()
    error_percent = (rmse / avg_price) * 100

    if error_percent < 20:
        quality = "excellent"
    elif error_percent < 40:
        quality = "good"
    elif error_percent < 60:
        quality = "acceptable"
    else:
        quality = "poor"

    return {
        "mse": round(mse, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "avg_price": round(avg_price, 2),
        "error_percent": round(error_percent, 2),
        "model_quality": quality,
        "sample_size": len(sample),
    }