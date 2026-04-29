import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/olist_feature_ready_dataset.csv")

plt.scatter(df['price'], df['demand'])
plt.xlabel("Price")
plt.ylabel("Demand")
plt.title("Price vs Demand")
plt.show()