from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ml_utils import OUTPUT_DIR, RAW_PATH, ROOT, read_json


STEPS = [
    ("01_prepare_features.py", "Prepare features — clean the data, build the feature vector, define the label"),
    ("02_baseline_score.py", "Baseline — a transparent hand-written rule to beat"),
    ("03_train_model.py", "Train — logistic regression, decision tree, random forest (client-holdout split)"),
    ("04_evaluate_and_export.py", "Evaluate — ranked refresh queue, charts, and the Markdown report"),
    ("05_build_pdf_report.py", "Report — a shareable PDF summary"),
]


def run_step(index: int, script: str, label: str) -> None:
    print(f"\n{'=' * 70}\n▶ Step {index}/{len(STEPS)} — {label}\n{'=' * 70}", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main() -> None:
    if not RAW_PATH.exists():
        raise SystemExit(
            f"Starter data not found: {RAW_PATH}\n"
            "The anonymized starter CSV ships with this repo. "
            "Restore it from git (`git checkout -- data/raw/content_refresh_anonymized.csv`).\n"
            "No BigQuery export is needed here — this repo runs entirely on the bundled sample."
        )

    for index, (script, label) in enumerate(STEPS, start=1):
        run_step(index, script, label)

    summary_path = OUTPUT_DIR / "summary.json"
    if summary_path.exists():
        summary = read_json(summary_path)
        print("\nPipeline complete")
        print(f"Rows scored: {summary['rows_scored']:,}")
        print(f"Best model: {summary['best_model']}")
        print(f"Queue: {summary['queue_output']}")
        print(f"Report: {summary['report_output']}")
        print(f"PDF: {OUTPUT_DIR / 'flyrank_refresh_model_results.pdf'}")


if __name__ == "__main__":
    main()
