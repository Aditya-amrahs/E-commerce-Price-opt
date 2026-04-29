import pandas as pd

DATA_PATH = "data/processed/olist_feature_ready_dataset.csv"


def compute_competitor_prices(df):
    # Average price per product (all sellers)
    avg_price = df.groupby("product_id")["item_price"].mean().reset_index()
    avg_price.rename(columns={"item_price": "competitor_price"}, inplace=True)

    # Merge back
    df = df.merge(avg_price, on="product_id", how="left")

    return df


def analyze_product(row):
    our_price = row["item_price"]
    competitor_price = row["competitor_price"]

    diff = our_price - competitor_price

    if diff > 0:
        status = "Higher"
        recommendation = "Decrease price"
    elif diff < 0:
        status = "Lower"
        recommendation = "Increase price"
    else:
        status = "Equal"
        recommendation = "Keep same"

    percent = (
        round((diff / competitor_price) * 100, 2)
        if competitor_price != 0 else 0
    )

    return {
        "product_id": row["product_id"],
        "seller_id": row["seller_id"],
        "ourPrice": round(our_price, 2),
        "competitorPrice": round(competitor_price, 2),
        "difference": round(diff, 2),
        "percentDiff": percent,
        "status": status,
        "recommendation": recommendation,
    }


def get_analysis():
    df = pd.read_csv(DATA_PATH)

    # Compute full dataset stats BEFORE slicing
    total_products = len(df)
    avg_price = df["item_price"].mean()
    min_price = df["item_price"].min()
    max_price = df["item_price"].max()

    # Apply competitor logic
    df = compute_competitor_prices(df)

    # Take small sample for frontend charts
    sample_df = df.head(20)

    analyzed_data = [
        analyze_product(row) for _, row in sample_df.iterrows()
    ]

    return {
        "data": analyzed_data,
        "summary": {
            "total_products": int(total_products),
            "avg_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
        },
    }