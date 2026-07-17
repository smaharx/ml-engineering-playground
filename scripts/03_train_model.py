from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from ml_utils import (
    MODEL_CATEGORICAL_FEATURES,
    MODEL_NUMERIC_FEATURES,
    OUTPUT_DIR,
    PROCESSED_DIR,
    display_path,
    precision_at_k,
    write_json,
)


FEATURE_PATH = PROCESSED_DIR / "refresh_feature_vector.csv"
BASELINE_PATH = PROCESSED_DIR / "baseline_refresh_queue.csv"
PREDICTION_PATH = PROCESSED_DIR / "model_predictions.csv"
RESULT_PATH = OUTPUT_DIR / "model_results.json"
RANDOM_STATE = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train refresh opportunity models.")
    parser.add_argument("--features", default=str(FEATURE_PATH))
    parser.add_argument("--baseline", default=str(BASELINE_PATH))
    parser.add_argument("--predictions", default=str(PREDICTION_PATH))
    parser.add_argument("--results", default=str(RESULT_PATH))
    return parser.parse_args()


def build_feature_matrix(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    numeric_features = [
        column for column in MODEL_NUMERIC_FEATURES if column in frame.columns
    ]
    categorical_features = [
        column for column in MODEL_CATEGORICAL_FEATURES if column in frame.columns
    ]

    numeric_frame = frame[numeric_features].apply(pd.to_numeric, errors="coerce")
    numeric_frame = numeric_frame.replace([np.inf, -np.inf], np.nan).fillna(0)

    categorical_frame = frame[categorical_features].fillna("unknown").astype(str)
    encoded_frame = pd.get_dummies(
        categorical_frame,
        prefix=categorical_features,
        dummy_na=False,
        dtype=float,
    )

    feature_frame = pd.concat(
        [numeric_frame.reset_index(drop=True), encoded_frame.reset_index(drop=True)],
        axis=1,
    )
    return feature_frame, list(feature_frame.columns)


def make_client_aware_split(
    frame: pd.DataFrame,
    target_series: pd.Series,
) -> tuple[np.ndarray, np.ndarray, str]:
    all_indices = np.arange(len(frame))
    client_series = frame["client_id"].fillna("unknown").astype(str)
    unique_clients = client_series.drop_duplicates().to_numpy()

    if len(unique_clients) >= 5:
        random_generator = np.random.default_rng(RANDOM_STATE)
        shuffled_clients = random_generator.permutation(unique_clients)
        test_client_count = max(1, int(round(len(shuffled_clients) * 0.2)))
        test_clients = set(shuffled_clients[:test_client_count])
        test_mask = client_series.isin(test_clients).to_numpy()
        train_indices = all_indices[~test_mask]
        test_indices = all_indices[test_mask]

        if (
            len(train_indices) > 0
            and len(test_indices) > 0
            and target_series.iloc[train_indices].nunique() == 2
            and target_series.iloc[test_indices].nunique() == 2
        ):
            return train_indices, test_indices, "client_holdout"

    train_indices, test_indices = train_test_split(
        all_indices,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=target_series,
    )
    return np.array(train_indices), np.array(test_indices), "stratified_row_holdout"


def build_models() -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced",
            max_depth=5,
            min_samples_leaf=50,
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            class_weight="balanced_subsample",
            max_depth=10,
            min_samples_leaf=25,
            n_estimators=200,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def predict_probability(model: object, feature_frame: pd.DataFrame) -> np.ndarray:
    if not hasattr(model, "predict_proba"):
        raise TypeError(f"Model does not expose predict_proba: {type(model)!r}")
    probabilities = model.predict_proba(feature_frame)
    return np.asarray(probabilities[:, 1], dtype=float)


def metric_payload(
    target_series: pd.Series,
    probability_scores: np.ndarray,
    *,
    prefix: str = "",
) -> dict[str, float]:
    binary_predictions = (probability_scores >= 0.5).astype(int)
    payload = {
        f"{prefix}accuracy": float(accuracy_score(target_series, binary_predictions)),
        f"{prefix}precision": float(
            precision_score(target_series, binary_predictions, zero_division=0)
        ),
        f"{prefix}recall": float(
            recall_score(target_series, binary_predictions, zero_division=0)
        ),
        f"{prefix}f1": float(f1_score(target_series, binary_predictions, zero_division=0)),
        f"{prefix}precision_at_20": precision_at_k(target_series, probability_scores, 20),
        f"{prefix}precision_at_50": precision_at_k(target_series, probability_scores, 50),
        f"{prefix}precision_at_100": precision_at_k(target_series, probability_scores, 100),
    }
    if target_series.nunique() == 2:
        payload[f"{prefix}roc_auc"] = float(roc_auc_score(target_series, probability_scores))
        payload[f"{prefix}average_precision"] = float(
            average_precision_score(target_series, probability_scores)
        )
    else:
        payload[f"{prefix}roc_auc"] = 0.0
        payload[f"{prefix}average_precision"] = 0.0
    return payload


def top_feature_importance(
    model: object,
    feature_columns: list[str],
    *,
    limit: int = 25,
) -> list[dict[str, float | str]]:
    if isinstance(model, Pipeline):
        classifier = model.named_steps["model"]
        raw_values = np.abs(classifier.coef_[0])
    elif hasattr(model, "feature_importances_"):
        raw_values = np.asarray(model.feature_importances_, dtype=float)
    else:
        raw_values = np.zeros(len(feature_columns), dtype=float)

    importance_frame = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": raw_values,
        }
    )
    importance_frame = importance_frame.sort_values("importance", ascending=False).head(limit)
    return [
        {"feature": str(row.feature), "importance": float(row.importance)}
        for row in importance_frame.itertuples(index=False)
    ]


def main() -> None:
    args = parse_args()

    frame = pd.read_csv(args.features)
    baseline_frame = pd.read_csv(args.baseline)
    if frame.empty:
        raise ValueError("Feature vector is empty")
    if frame["is_declining_label"].nunique() < 2:
        raise ValueError("Training target has only one class; cannot train classifier")

    feature_frame, feature_columns = build_feature_matrix(frame)
    target_series = frame["is_declining_label"].astype(int)
    train_indices, test_indices, split_strategy = make_client_aware_split(frame, target_series)

    train_features = feature_frame.iloc[train_indices]
    test_features = feature_frame.iloc[test_indices]
    train_target = target_series.iloc[train_indices]
    test_target = target_series.iloc[test_indices]

    baseline_lookup = baseline_frame.set_index("content_id")["baseline_refresh_score"]
    baseline_test_scores = (
        frame.iloc[test_indices]["content_id"].map(baseline_lookup).fillna(0).to_numpy()
    )
    baseline_metrics = metric_payload(
        test_target,
        baseline_test_scores,
        prefix="baseline_",
    )

    trained_models = build_models()
    model_results: dict[str, dict[str, float]] = {}
    for model_name, model in trained_models.items():
        model.fit(train_features, train_target)
        test_probabilities = predict_probability(model, test_features)
        model_results[model_name] = metric_payload(test_target, test_probabilities)

    best_model_name = sorted(
        model_results,
        key=lambda name: (
            model_results[name]["precision_at_50"],
            model_results[name]["average_precision"],
            model_results[name]["roc_auc"],
        ),
        reverse=True,
    )[0]

    full_data_models = build_models()
    prediction_frame = frame[["content_id", "client_id", "is_declining_label"]].copy()
    split_label = pd.Series("train", index=frame.index)
    split_label.iloc[test_indices] = "test"
    prediction_frame["split"] = split_label

    for model_name, model in full_data_models.items():
        model.fit(feature_frame, target_series)
        prediction_frame[f"prob_{model_name}"] = predict_probability(model, feature_frame)

    prediction_frame["best_model_name"] = best_model_name
    prediction_frame["best_model_probability"] = prediction_frame[f"prob_{best_model_name}"]

    prediction_path = Path(args.predictions)
    prediction_path.parent.mkdir(parents=True, exist_ok=True)
    prediction_frame.to_csv(prediction_path, index=False)

    best_full_model = full_data_models[best_model_name]
    results_payload = {
        "input_rows": int(len(frame)),
        "train_rows": int(len(train_indices)),
        "test_rows": int(len(test_indices)),
        "split_strategy": split_strategy,
        "target": "is_declining_label",
        "target_positive_rows": int(target_series.sum()),
        "target_positive_rate": float(target_series.mean()),
        "feature_count": int(len(feature_columns)),
        "model_numeric_features": MODEL_NUMERIC_FEATURES,
        "model_categorical_features": MODEL_CATEGORICAL_FEATURES,
        "models": model_results,
        "baseline": baseline_metrics,
        "best_model": {
            "name": best_model_name,
            "selection_metric": "precision_at_50",
            "feature_importance_top": top_feature_importance(best_full_model, feature_columns),
        },
        "prediction_output": display_path(prediction_path),
    }
    write_json(Path(args.results), results_payload)

    print(f"Trained {len(model_results)} models on {len(frame):,} rows")
    print(f"Split strategy: {split_strategy}")
    print(f"Best model: {best_model_name}")
    print(f"Wrote predictions: {prediction_path}")
    print(f"Wrote model results: {args.results}")


if __name__ == "__main__":
    main()
