from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.analysis_service import get_analysis
from backend.services.model_service import run_optimization
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
app = FastAPI()

# allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/analysis")
def analysis():
    return get_analysis()

@app.get("/optimize")
def optimize():
    return run_optimization()