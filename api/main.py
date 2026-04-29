from fastapi import FastAPI
from analysis.best_price import get_best_price

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is working"}

@app.get("/price")
def get_price():
    return {"best_price": get_best_price()}