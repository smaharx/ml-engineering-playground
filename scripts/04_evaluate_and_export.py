from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ml_utils import (
    CHART_DIR,
    OUTPUT_DIR,
    PROCESSED_DIR,
    display_path,
    normalize,
    read_json,
    simple_svg_bar_chart,
    write_json,
)


FEATURE_PATH = PROCESSED_DIR / "refresh_feature_vector.csv"
BASELINE_PATH = PROCESSED_DIR / "baseline_refresh_queue.csv"
PREDICTION_PATH = PROCESSED_DIR / "model_predictions.csv"
MODEL_RESULT_PATH = OUTPUT_DIR / "model_results.json"
QUEUE_PATH = OUTPUT_DIR / "refresh_queue.csv"
REPORT_PATH = OUTPUT_DIR / "model_report.md"
SUMMARY_PATH = OUTPUT_DIR / "summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create final refresh queue and report.")
    parser.add_argument("--features", default=str(FEATURE_PATH))
    parser.add_argument("--baseline", default=str(BASELINE_PATH))
    parser.add_argument("--predictions", default=str(PREDICTION_PATH))
    parser.add_argument("--model-results", default=str(MODEL_RESULT_PATH))
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--report", default=str(REPORT_PATH))
    return parser.parse_args()


def merged_reason_codes(row: pd.Series) -> str:
    reasons = [
        reason
        for reason in str(row.get("reason_codes", "")).split("|")
        if reason and reason != "nan"
    ]

    if row["best_model_probability"] >= 0.65:
        reasons.append("model_decline_risk")
    if row["best_model_probability"] >= 0.5 and row["impressions_90d"] >= 500:
        reasons.append("visible_model_opportunity")
    if (
        row["impressions_90d"] >= 500
        and row["avg_position"] > 0
        and row["avg_position"] <= 20
        and row["ctr"] < 0.5
    ):
        reasons.append("ctr_review_candidate")
    if row["sessions_90d"] >= 30 and (
        (row["engagement_rate"] > 0 and row["engagement_rate"] < 30)
        or (row["scroll_rate"] > 0 and row["scroll_rate"] < 30)
    ):
        reasons.append("engagement_review_candidate")

    unique_reasons = []
    for reason in reasons:
        if reason not in unique_reasons:
            unique_reasons.append(reason)
    return "|".join(unique_reasons or ["general_refresh_review"])


def suggested_action(row: pd.Series) -> str:
    reasons = set(str(row["final_reason_codes"]).split("|"))
    if "thin_visible_page" in reasons:
        return "expand_and_refresh"
    if "ctr_review_candidate" in reasons and (
        "model_decline_risk" in reasons or "declining_with_demand" in reasons
    ):
        return "refresh_and_review_ctr"
    if "engagement_review_candidate" in reasons and (
        "model_decline_risk" in reasons or "declining_with_demand" in reasons
    ):
        return "refresh_and_review_engagement"
    if {
        "model_decline_risk",
        "declining_with_demand",
        "stale_visible_page",
        "visible_model_opportunity",
    }.intersection(reasons):
        return "refresh"
    return "monitor"


def confidence_label(row: pd.Series, high_threshold: float, medium_threshold: float) -> str:
    if (
        row["final_refresh_score"] >= high_threshold
        and row["impressions_90d"] >= 500
        and row["sessions_90d"] >= 10
        and row["best_model_probability"] >= 0.5
    ):
        return "high"
    if row["final_refresh_score"] >= medium_threshold:
        return "medium"
    return "low"


def metric_table(model_results: dict) -> str:
    lines = [
        "| Model | ROC AUC | Avg precision | Precision@50 | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model_name, metrics in model_results["models"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    model_name,
                    f"{metrics['roc_auc']:.3f}",
                    f"{metrics['average_precision']:.3f}",
                    f"{metrics['precision_at_50']:.3f}",
                    f"{metrics['recall']:.3f}",
                    f"{metrics['f1']:.3f}",
                ]
            )
            + " |"
        )
    baseline = model_results["baseline"]
    lines.append(
        "| baseline_rules | "
        + " | ".join(
            [
                f"{baseline['baseline_roc_auc']:.3f}",
                f"{baseline['baseline_average_precision']:.3f}",
                f"{baseline['baseline_precision_at_50']:.3f}",
                "-",
                "-",
            ]
        )
        + " |"
    )
    return "\n".join(lines)


def make_charts(final_frame: pd.DataFrame, model_results: dict) -> None:
    action_counts = final_frame["suggested_action"].value_counts().head(10)
    simple_svg_bar_chart(
        "Suggested action mix",
        action_counts.index.tolist(),
        action_counts.values.tolist(),
        CHART_DIR / "action_mix.svg",
        color="#426B69",
    )

    confidence_counts = final_frame["confidence"].value_counts().reindex(
        ["high", "medium", "low"],
        fill_value=0,
    )
    simple_svg_bar_chart(
        "Refresh queue confidence",
        confidence_counts.index.tolist(),
        confidence_counts.values.tolist(),
        CHART_DIR / "confidence_mix.svg",
        color="#6F4E7C",
    )

    reason_counts: dict[str, int] = {}
    for reason_text in final_frame["final_reason_codes"]:
        for reason in str(reason_text).split("|"):
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    top_reasons = (
        pd.Series(reason_counts)
        .sort_values(ascending=False)
        .head(12)
    )
    simple_svg_bar_chart(
        "Top refresh reason codes",
        top_reasons.index.tolist(),
        top_reasons.values.tolist(),
        CHART_DIR / "top_reason_codes.svg",
        color="#8C6BB1",
    )

    feature_importance = pd.DataFrame(
        model_results["best_model"]["feature_importance_top"]
    ).head(12)
    simple_svg_bar_chart(
        "Top model features",
        feature_importance["feature"].tolist(),
        feature_importance["importance"].tolist(),
        CHART_DIR / "top_feature_importance.svg",
        color="#4E79A7",
    )

    trend_counts = final_frame["trend_direction"].value_counts().head(10)
    simple_svg_bar_chart(
        "Trend direction distribution",
        trend_counts.index.tolist(),
        trend_counts.values.tolist(),
        CHART_DIR / "trend_distribution.svg",
        color="#B07AA1",
    )


def write_report(final_frame: pd.DataFrame, model_results: dict, report_path: Path) -> None:
    top_features = model_results["best_model"]["feature_importance_top"][:10]
    action_counts = final_frame["suggested_action"].value_counts()
    confidence_counts = final_frame["confidence"].value_counts()
    top_preview = final_frame.head(10)

    top_preview_lines = [
        "| Rank | Score | Model probability | Action | Reasons | Impressions | Sessions | Trend |",
        "|---:|---:|---:|---|---|---:|---:|---|",
    ]
    for row in top_preview.itertuples(index=False):
        readable_reasons = str(row.final_reason_codes).replace("|", ", ")
        top_preview_lines.append(
            f"| {row.final_rank} | {row.final_refresh_score:.1f} | "
            f"{row.best_model_probability:.3f} | {row.suggested_action} | "
            f"{readable_reasons} | {int(row.impressions_90d)} | "
            f"{int(row.sessions_90d)} | {row.trend_direction} |"
        )

    action_lines = "\n".join(
        f"- `{action}` items: {int(count):,}"
        for action, count in action_counts.sort_values(ascending=False).items()
    )

    report = f"""# FlyRank Refresh Opportunity Model Report

This report is generated from the bundled anonymized starter dataset (`data/raw/content_refresh_anonymized.csv`).
The model ranks existing content for refresh review. It does not use titles, URLs, client names, domains, or keywords.

## Data

- Rows scored: {len(final_frame):,}
- Declining-label rows: {int(final_frame["is_declining_label"].sum()):,}
- Declining-label rate: {final_frame["is_declining_label"].mean():.3f}
- Split strategy used for validation: {model_results["split_strategy"]}
- Target: `{model_results["target"]}`

## Model Comparison

Best model: `{model_results["best_model"]["name"]}` selected by `{model_results["best_model"]["selection_metric"]}`.

{metric_table(model_results)}

## Final Queue

- High-confidence items: {int(confidence_counts.get("high", 0)):,}
- Medium-confidence items: {int(confidence_counts.get("medium", 0)):,}
- Low-confidence items: {int(confidence_counts.get("low", 0)):,}
{action_lines}

## Top Features

"""
    for feature in top_features:
        report += f"- `{feature['feature']}`: {feature['importance']:.4f}\n"

    report += "\n## Top 10 Queue Preview\n\n"
    report += "\n".join(top_preview_lines)
    report += """

## Generated Files

- `outputs/refresh_queue.csv`
- `outputs/model_results.json`
- `outputs/summary.json`
- `outputs/charts/action_mix.svg`
- `outputs/charts/confidence_mix.svg`
- `outputs/charts/top_reason_codes.svg`
- `outputs/charts/top_feature_importance.svg`
- `outputs/charts/trend_distribution.svg`

## Practical Use

Use the ranked queue as a reviewer aid, not as an automatic publishing decision.
The safest first production use is to inspect high-confidence rows, verify the page manually, and compare the recommendation against editorial context.
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)


def main() -> None:
    args = parse_args()

    feature_frame = pd.read_csv(args.features)
    baseline_frame = pd.read_csv(args.baseline)
    prediction_frame = pd.read_csv(args.predictions)
    model_results = read_json(Path(args.model_results))

    final_frame = baseline_frame.merge(
        prediction_frame[
            [
                "content_id",
                "best_model_name",
                "best_model_probability",
                "prob_logistic_regression",
                "prob_decision_tree",
                "prob_random_forest",
            ]
        ],
        on="content_id",
        how="left",
    )

    context_columns = [
        "content_id",
        "competition_level",
        "content_type",
        "main_intent",
        "age_tier",
        "freshness_tier",
        "word_count_tier",
        "impression_tier",
        "position_tier",
    ]
    final_frame = final_frame.merge(
        feature_frame[[column for column in context_columns if column in feature_frame.columns]],
        on="content_id",
        how="left",
    )
    final_frame["best_model_probability"] = final_frame["best_model_probability"].fillna(0)
    final_frame["baseline_score_normalized"] = normalize(final_frame["baseline_refresh_score"])
    final_frame["final_refresh_score"] = (
        100
        * (
            0.70 * final_frame["best_model_probability"]
            + 0.30 * final_frame["baseline_score_normalized"]
        )
    ).clip(0, 100)

    final_frame["final_reason_codes"] = final_frame.apply(merged_reason_codes, axis=1)
    final_frame["suggested_action"] = final_frame.apply(suggested_action, axis=1)
    high_threshold = float(final_frame["final_refresh_score"].quantile(0.8))
    medium_threshold = float(final_frame["final_refresh_score"].quantile(0.5))
    final_frame["confidence"] = final_frame.apply(
        lambda row: confidence_label(row, high_threshold, medium_threshold),
        axis=1,
    )
    final_frame = final_frame.sort_values(
        ["final_refresh_score", "impressions_90d", "sessions_90d"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    final_frame["final_rank"] = final_frame.index + 1

    output_columns = [
        "final_rank",
        "content_id",
        "client_id",
        "final_refresh_score",
        "best_model_name",
        "best_model_probability",
        "baseline_refresh_score",
        "confidence",
        "suggested_action",
        "final_reason_codes",
        "is_declining_label",
        "impressions_90d",
        "clicks_90d",
        "sessions_90d",
        "avg_position",
        "ctr",
        "content_age_days",
        "days_since_last_update",
        "word_count",
        "trend_direction",
        "competition_level",
        "content_type",
        "main_intent",
        "age_tier",
        "freshness_tier",
        "word_count_tier",
        "impression_tier",
        "position_tier",
    ]
    output_frame = final_frame[output_columns]

    queue_path = Path(args.queue)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    output_frame.to_csv(queue_path, index=False)

    make_charts(output_frame, model_results)
    write_report(output_frame, model_results, Path(args.report))

    summary_payload = {
        "rows_scored": int(len(output_frame)),
        "best_model": model_results["best_model"]["name"],
        "target_positive_rate": float(model_results["target_positive_rate"]),
        "final_score_p80": high_threshold,
        "final_score_p50": medium_threshold,
        "top_queue_score": float(output_frame["final_refresh_score"].max()),
        "high_confidence_rows": int((output_frame["confidence"] == "high").sum()),
        "queue_output": display_path(queue_path),
        "report_output": display_path(args.report),
        "charts": [
            display_path(CHART_DIR / "action_mix.svg"),
            display_path(CHART_DIR / "confidence_mix.svg"),
            display_path(CHART_DIR / "top_reason_codes.svg"),
            display_path(CHART_DIR / "top_feature_importance.svg"),
            display_path(CHART_DIR / "trend_distribution.svg"),
        ],
    }
    write_json(SUMMARY_PATH, summary_payload)

    print(f"Wrote final refresh queue: {queue_path}")
    print(f"Wrote model report: {args.report}")
    print(f"Wrote charts in: {CHART_DIR}")


if __name__ == "__main__":
    main()
