from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from ml.config.constants import MODELING_TARGET, RESIDUAL_TARGET
from ml.config.settings import settings
from ml.utils.metrics import regression_metrics


def train_xgb_residual_model(
    linear_result: dict[str, object],
    target_column: str = MODELING_TARGET,
    residual_column: str = RESIDUAL_TARGET,
    residual_learning_rate: float = 0.65,
) -> dict[str, object]:
    pipeline = linear_result["pipeline"]
    preprocessor = pipeline.named_steps["preprocess"]
    numeric_features = linear_result["metrics"]["numeric_features"]
    categorical_features = linear_result["metrics"]["categorical_features"]
    feature_columns = numeric_features + categorical_features
    scored_splits: dict[str, pd.DataFrame] = linear_result["scored_splits"]

    train = scored_splits["train"]
    validation = scored_splits["validation"]
    test = scored_splits["test"]

    xgb_model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=1200,
        learning_rate=0.03,
        max_depth=3,
        min_child_weight=8,
        subsample=0.75,
        colsample_bytree=0.75,
        reg_alpha=0.1,
        reg_lambda=5.0,
        gamma=0.05,
        random_state=settings.random_seed,
        tree_method="hist",
        n_jobs=4,
        eval_metric="rmse",
        early_stopping_rounds=50,
    )

    x_train = preprocessor.transform(train[feature_columns])
    y_train = train[residual_column]
    x_validation = preprocessor.transform(validation[feature_columns])
    y_validation = validation[residual_column]
    try:
        xgb_model.fit(
            x_train,
            y_train,
            eval_set=[(x_validation, y_validation)],
            verbose=False,
        )
    except TypeError:
        xgb_model.set_params(early_stopping_rounds=None)
        xgb_model.fit(x_train, y_train)

    residual_clip_bounds = tuple(
        float(value)
        for value in train[residual_column].quantile([0.01, 0.99]).to_list()
    )
    prediction_bounds = tuple(
        float(value)
        for value in train[target_column].quantile([0.001, 0.999]).to_list()
    )

    split_metrics: dict[str, object] = {}
    scored_outputs: dict[str, pd.DataFrame] = {}
    for split_name, split in (
        ("train", train),
        ("validation", validation),
        ("test", test),
    ):
        transformed = preprocessor.transform(split[feature_columns])
        scored_split = split.copy()
        raw_residual_prediction = xgb_model.predict(transformed)
        scored_split["xgb_residual_prediction_raw"] = raw_residual_prediction
        scored_split["xgb_residual_prediction"] = (
            pd.Series(raw_residual_prediction, index=scored_split.index)
            .clip(*residual_clip_bounds)
            .mul(residual_learning_rate)
        )
        scored_split["hybrid_prediction"] = (
            scored_split["linear_prediction"] + scored_split["xgb_residual_prediction"]
        ).clip(lower=prediction_bounds[0], upper=prediction_bounds[1])
        scored_split["hybrid_prediction"] = np.maximum(
            scored_split["hybrid_prediction"], 0.01
        )
        scored_split["hybrid_residual"] = (
            scored_split[target_column] - scored_split["hybrid_prediction"]
        )
        scored_outputs[split_name] = scored_split
        split_metrics[f"{split_name}_residual_metrics"] = regression_metrics(
            scored_split[residual_column],
            scored_split["xgb_residual_prediction"],
        )
        split_metrics[f"{split_name}_hybrid_metrics"] = regression_metrics(
            scored_split[target_column],
            scored_split["hybrid_prediction"],
        )

    model_path = settings.model_dir / "xgb_residual_model.joblib"
    metrics_path = settings.model_dir / "xgb_metrics.json"
    prediction_path = settings.model_dir / "hybrid_predictions.parquet"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(xgb_model, model_path)

    combined = pd.concat(scored_outputs.values(), axis=0).sort_index()
    stored_prediction_path = prediction_path
    try:
        combined.to_parquet(prediction_path, index=False)
    except ImportError:
        stored_prediction_path = prediction_path.with_suffix(".pkl")
        combined.to_pickle(stored_prediction_path)

    metrics_payload = {
        "feature_columns": feature_columns,
        "residual_learning_rate": residual_learning_rate,
        "residual_clip_bounds": residual_clip_bounds,
        "prediction_bounds": prediction_bounds,
        "best_iteration": getattr(xgb_model, "best_iteration", None),
        "best_score": getattr(xgb_model, "best_score", None),
        **split_metrics,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    return {
        "model": xgb_model,
        "model_path": model_path,
        "metrics_path": metrics_path,
        "prediction_path": stored_prediction_path,
        "metrics": metrics_payload,
        "scored_splits": scored_outputs,
        "scored_predictions": combined,
    }


def load_xgb_model(path: Path | None = None) -> XGBRegressor:
    return joblib.load(path or settings.model_dir / "xgb_residual_model.joblib")
