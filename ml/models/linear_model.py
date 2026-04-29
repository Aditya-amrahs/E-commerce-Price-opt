from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from ml.config.constants import MODELING_TARGET, PRICE_MODEL_EXCLUDED_FEATURES
from ml.config.settings import settings
from ml.features.engineer import model_columns
from ml.preprocessing.pipeline import build_model_preprocessor, save_pipeline
from ml.utils.metrics import regression_metrics
from ml.utils.splitter import train_validation_test_split


class ClippedLogTargetRegressor(BaseEstimator, RegressorMixin):
    def __init__(
        self,
        regressor=None,
        lower_quantile: float = 0.001,
        upper_quantile: float = 0.999,
    ) -> None:
        self.regressor = regressor
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(self, x, y):
        base_regressor = (
            self.regressor if self.regressor is not None else Ridge(alpha=3.0)
        )
        self.lower_bound_ = float(pd.Series(y).quantile(self.lower_quantile))
        self.upper_bound_ = float(pd.Series(y).quantile(self.upper_quantile))
        self.model_ = TransformedTargetRegressor(
            regressor=clone(base_regressor),
            func=np.log1p,
            inverse_func=np.expm1,
        )
        self.model_.fit(x, y)
        return self

    def predict(self, x):
        predictions = self.model_.predict(x)
        return np.maximum(
            np.clip(predictions, self.lower_bound_, self.upper_bound_), 0.01
        )


def train_linear_regression(
    features: pd.DataFrame,
    target_column: str = MODELING_TARGET,
) -> dict[str, object]:
    train, validation, test = train_validation_test_split(features, target_column)
    numeric_features, categorical_features = model_columns(
        features,
        excluded_extra=PRICE_MODEL_EXCLUDED_FEATURES,
    )
    pipeline = Pipeline(
        steps=[
            (
                "preprocess",
                build_model_preprocessor(numeric_features, categorical_features),
            ),
            (
                "model",
                ClippedLogTargetRegressor(
                    regressor=Ridge(alpha=3.0),
                ),
            ),
        ]
    )

    x_train = train[numeric_features + categorical_features]
    y_train = train[target_column]
    pipeline.fit(x_train, y_train)

    results: dict[str, object] = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "splits": {
            "train_rows": int(len(train)),
            "validation_rows": int(len(validation)),
            "test_rows": int(len(test)),
        },
        "target_transform": "log1p",
        "estimator": "clipped_ridge",
    }
    for split_name, split in (
        ("train", train),
        ("validation", validation),
        ("test", test),
    ):
        x_split = split[numeric_features + categorical_features]
        y_split = split[target_column]
        predictions = pipeline.predict(x_split)
        results[f"{split_name}_metrics"] = regression_metrics(y_split, predictions)

    scored_splits: dict[str, pd.DataFrame] = {}
    for split_name, split in (
        ("train", train),
        ("validation", validation),
        ("test", test),
    ):
        scored_split = split.copy()
        scored_split["linear_prediction"] = pipeline.predict(
            scored_split[numeric_features + categorical_features]
        )
        scored_split["linear_residual"] = (
            scored_split[target_column] - scored_split["linear_prediction"]
        )
        scored_splits[split_name] = scored_split

    scored = pd.concat(scored_splits.values(), axis=0).sort_index()

    model_path = save_pipeline(pipeline)
    residual_path = settings.model_dir / "linear_residuals.parquet"
    metrics_path = settings.model_dir / "linear_metrics.json"
    residual_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        scored.to_parquet(residual_path, index=False)
    except ImportError:
        residual_path = residual_path.with_suffix(".pkl")
        scored.to_pickle(residual_path)
    metrics_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return {
        "pipeline": pipeline,
        "model_path": model_path,
        "residual_path": residual_path,
        "metrics_path": metrics_path,
        "metrics": results,
        "scored_splits": scored_splits,
        "scored_features": scored,
    }


def load_linear_pipeline(path: Path | None = None) -> Pipeline:
    return joblib.load(path or settings.model_dir / "linear_regression_pipeline.joblib")
