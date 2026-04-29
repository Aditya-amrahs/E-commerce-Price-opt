from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.config.settings import settings


def _improvement(metric_name: str, baseline: float, hybrid: float) -> float:
    if metric_name in {"mae", "rmse"}:
        return baseline - hybrid
    return hybrid - baseline


def compare_baseline_vs_hybrid(
    linear_result: dict[str, object],
    xgb_result: dict[str, object],
) -> dict[str, object]:
    rows = []
    for split_name in ("train", "validation", "test"):
        linear_metrics = linear_result["metrics"][f"{split_name}_metrics"]
        hybrid_metrics = xgb_result["metrics"][f"{split_name}_hybrid_metrics"]
        for metric_name in ("mae", "rmse", "r2"):
            baseline_value = linear_metrics[metric_name]
            hybrid_value = hybrid_metrics[metric_name]
            rows.append(
                {
                    "split": split_name,
                    "metric": metric_name,
                    "baseline_linear": baseline_value,
                    "hybrid_xgb": hybrid_value,
                    "improvement": _improvement(
                        metric_name, baseline_value, hybrid_value
                    ),
                }
            )

    comparison_df = pd.DataFrame(rows)
    metrics_path = settings.model_dir / "baseline_vs_hybrid_metrics.csv"
    json_path = settings.model_dir / "baseline_vs_hybrid_metrics.json"
    comparison_df.to_csv(metrics_path, index=False)
    json_path.write_text(
        json.dumps(comparison_df.to_dict(orient="records"), indent=2),
        encoding="utf-8",
    )
    return {
        "comparison_df": comparison_df,
        "comparison_csv_path": metrics_path,
        "comparison_json_path": json_path,
    }


def save_hybrid_bundle(
    linear_result: dict[str, object],
    xgb_result: dict[str, object],
) -> Path:
    bundle_path = settings.model_dir / "hybrid_bundle.joblib"
    bundle = {
        "linear_pipeline": linear_result["pipeline"],
        "xgb_model": xgb_result["model"],
        "numeric_features": linear_result["metrics"]["numeric_features"],
        "categorical_features": linear_result["metrics"]["categorical_features"],
        "residual_learning_rate": xgb_result["metrics"]["residual_learning_rate"],
        "residual_clip_bounds": xgb_result["metrics"]["residual_clip_bounds"],
        "prediction_bounds": xgb_result["metrics"]["prediction_bounds"],
    }
    joblib.dump(bundle, bundle_path)
    return bundle_path


def predict_hybrid(bundle: dict[str, object], features: pd.DataFrame) -> np.ndarray:
    feature_columns = bundle["numeric_features"] + bundle["categorical_features"]
    linear_pipeline = bundle["linear_pipeline"]
    xgb_model = bundle["xgb_model"]
    residual_clip_bounds = bundle["residual_clip_bounds"]
    prediction_bounds = bundle["prediction_bounds"]
    residual_learning_rate = bundle["residual_learning_rate"]

    linear_prediction = linear_pipeline.predict(features[feature_columns])
    transformed = linear_pipeline.named_steps["preprocess"].transform(
        features[feature_columns]
    )
    residual_prediction = np.clip(
        xgb_model.predict(transformed),
        residual_clip_bounds[0],
        residual_clip_bounds[1],
    )
    hybrid_prediction = linear_prediction + residual_learning_rate * residual_prediction
    return np.maximum(
        np.clip(hybrid_prediction, prediction_bounds[0], prediction_bounds[1]), 0.01
    )


def load_hybrid_bundle(path: Path | None = None) -> dict[str, object]:
    return joblib.load(path or settings.model_dir / "hybrid_bundle.joblib")
