from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ml_utils import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    MODEL_CATEGORICAL_FEATURES,
    MODEL_NUMERIC_FEATURES,
    NUMERIC_COLUMNS,
    PROCESSED_DIR,
    RAW_PATH,
    display_path,
    ensure_dirs,
    to_bool_series,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare FlyRank refresh feature vector.")
    parser.add_argument("--input", default=str(RAW_PATH), help="Raw anonymized CSV export.")
    parser.add_argument(
        "--output",
        default=str(PROCESSED_DIR / "refresh_feature_vector.csv"),
        help="Prepared feature-vector CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Raw input not found: {input_path}. Restore data/raw/content_refresh_anonymized.csv from git "
            "(mentor repos can re-export it with 00_export_bigquery_anonymized.mjs)."
        )

    df = pd.read_csv(input_path)
    initial_rows = len(df)

    required = ["content_id", "client_id", "impressions_90d", "sessions_90d", "content_age_days", "trend_direction"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
        else:
            df[column] = 0

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = to_bool_series(df[column])
        else:
            df[column] = False

    for column in CATEGORICAL_COLUMNS:
        if column in df.columns:
            df[column] = df[column].fillna("unknown").astype(str).replace({"": "unknown", "nan": "unknown"})
        else:
            df[column] = "unknown"

    numeric_fill_zero = [
        "search_volume",
        "competition",
        "cpc",
        "word_count",
        "char_count",
        "impressions_90d",
        "clicks_90d",
        "pageviews_90d",
        "sessions_90d",
        "users_90d",
        "engaged_sessions_90d",
        "ai_sessions_90d",
        "scroll_events_90d",
        "days_with_impressions",
        "days_with_sessions",
        "impressions_last_30d",
        "clicks_last_30d",
        "sessions_last_30d",
        "impressions_prev_30d",
        "clicks_prev_30d",
        "sessions_prev_30d",
        "content_age_days",
        "age_tier_order",
        "days_since_last_update",
        "ctr",
        "avg_position",
        "engagement_rate",
        "scroll_rate",
        "ai_traffic_pct",
        "trend_pct",
    ]
    for column in numeric_fill_zero:
        df[column] = df[column].replace([np.inf, -np.inf], np.nan).fillna(0)

    df = df[(df["impressions_90d"] > 0) & (df["content_age_days"] >= 90)].copy()
    df = df.drop_duplicates(subset=["content_id"]).reset_index(drop=True)

    df["is_declining_label"] = df["trend_direction"].str.lower().eq("down").astype(int)

    df["log_impressions_90d"] = np.log1p(df["impressions_90d"])
    df["log_clicks_90d"] = np.log1p(df["clicks_90d"])
    df["log_sessions_90d"] = np.log1p(df["sessions_90d"])
    df["log_ai_sessions_90d"] = np.log1p(df["ai_sessions_90d"])
    df["has_clicks"] = (df["clicks_90d"] > 0).astype(int)
    df["has_ai_sessions"] = (df["ai_sessions_90d"] > 0).astype(int)
    df["measurable_opportunity"] = (
        (df["impressions_90d"] >= 100) & (df["sessions_90d"] > 0)
    ).astype(int)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    metadata = {
        "input": display_path(input_path),
        "output": display_path(output_path),
        "initial_rows": int(initial_rows),
        "prepared_rows": int(len(df)),
        "declining_rows": int(df["is_declining_label"].sum()),
        "declining_rate": float(df["is_declining_label"].mean()) if len(df) else 0.0,
        "model_numeric_features": MODEL_NUMERIC_FEATURES,
        "model_categorical_features": MODEL_CATEGORICAL_FEATURES,
        "target_definition": "trend_direction == 'down'",
    }
    write_json(PROCESSED_DIR / "feature_metadata.json", metadata)

    print(f"Prepared {len(df):,} rows from {initial_rows:,} raw rows")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

