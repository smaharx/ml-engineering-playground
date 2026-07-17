from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Callable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
QUEUE_PATH = OUTPUT_DIR / "refresh_queue.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary.json"
MODEL_RESULTS_PATH = OUTPUT_DIR / "model_results.json"
PDF_PATH = OUTPUT_DIR / "flyrank_refresh_model_results.pdf"

PAGE_SIZE = landscape(letter)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
LEFT_MARGIN = 0.48 * inch
RIGHT_MARGIN = 0.48 * inch
TOP_MARGIN = 0.42 * inch
BOTTOM_MARGIN = 0.42 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

BRAND_DARK = colors.HexColor("#16232A")
BRAND_TEXT = colors.HexColor("#27343B")
BRAND_MUTED = colors.HexColor("#65737A")
BRAND_PURPLE = colors.HexColor("#6F4E7C")
BRAND_TEAL = colors.HexColor("#426B69")
BRAND_BLUE = colors.HexColor("#4E79A7")
BRAND_LAVENDER = colors.HexColor("#8C6BB1")
BRAND_GREEN = colors.HexColor("#59A14F")
BRAND_ORANGE = colors.HexColor("#F28E2B")
BRAND_RED = colors.HexColor("#E15759")
LIGHT_BG = colors.HexColor("#F6F4F7")
LIGHT_TEAL = colors.HexColor("#EEF6F5")
LIGHT_BLUE = colors.HexColor("#EEF3FA")
LINE = colors.HexColor("#D9DEE2")


class HorizontalBarChart(Flowable):
    def __init__(
        self,
        title: str,
        items: list[tuple[str, float]],
        *,
        width: float = CONTENT_WIDTH,
        height: float = 2.45 * inch,
        color_palette: list[colors.Color] | None = None,
        value_formatter: Callable[[float], str] | None = None,
        max_label_chars: int = 34,
    ) -> None:
        super().__init__()
        self.title = title
        self.items = items
        self.width = width
        minimum_height = 42 + len(items) * 17 + max(0, len(items) - 1) * 6 + 8
        self.height = max(height, minimum_height)
        self.color_palette = color_palette or [
            BRAND_PURPLE,
            BRAND_TEAL,
            BRAND_BLUE,
            BRAND_LAVENDER,
            BRAND_GREEN,
            BRAND_ORANGE,
        ]
        self.value_formatter = value_formatter or (lambda value: f"{value:,.0f}")
        self.max_label_chars = max_label_chars

    def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
        self.width = min(self.width, available_width)
        return self.width, self.height

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()

        canvas.setFillColor(BRAND_DARK)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(0, self.height - 15, self.title)

        if not self.items:
            canvas.setFillColor(BRAND_MUTED)
            canvas.setFont("Helvetica", 9)
            canvas.drawString(0, self.height - 40, "No data available")
            canvas.restoreState()
            return

        label_width = 2.45 * inch
        value_width = 0.85 * inch
        chart_x = label_width
        chart_width = self.width - label_width - value_width
        chart_top = self.height - 34
        bottom_padding = 8
        row_gap = 6
        row_height = max(
            12,
            (chart_top - bottom_padding - row_gap * (len(self.items) - 1))
            / max(len(self.items), 1),
        )
        max_value = max(value for _, value in self.items) or 1

        for index, (raw_label, raw_value) in enumerate(self.items):
            y = chart_top - (index + 1) * row_height - index * row_gap
            label = raw_label
            if len(label) > self.max_label_chars:
                label = f"{label[: self.max_label_chars - 1]}…"

            canvas.setFillColor(BRAND_TEXT)
            canvas.setFont("Helvetica", 8.5)
            canvas.drawRightString(label_width - 8, y + row_height * 0.31, label)

            canvas.setFillColor(colors.HexColor("#E9EDF0"))
            canvas.roundRect(chart_x, y, chart_width, row_height, 4, fill=1, stroke=0)

            bar_width = chart_width * (raw_value / max_value)
            canvas.setFillColor(self.color_palette[index % len(self.color_palette)])
            canvas.roundRect(chart_x, y, bar_width, row_height, 4, fill=1, stroke=0)

            canvas.setFillColor(BRAND_TEXT)
            canvas.setFont("Helvetica-Bold", 8.5)
            canvas.drawString(
                chart_x + bar_width + 7,
                y + row_height * 0.31,
                self.value_formatter(raw_value),
            )

        canvas.restoreState()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_queue_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def format_int(value: object) -> str:
    return f"{int(float(value)):,}"


def format_float(value: object, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def format_score(value: object) -> str:
    return f"{float(value):.1f}"


def pct_metric(value: object) -> str:
    return f"{float(value):.3f}"


def chunks(items: list, chunk_size: int) -> list[list]:
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=BRAND_DARK,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=BRAND_MUTED,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            textColor=BRAND_DARK,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=BRAND_TEXT,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=BRAND_MUTED,
            spaceAfter=3,
        ),
        "card_value": ParagraphStyle(
            "CardValue",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=BRAND_DARK,
            alignment=TA_CENTER,
        ),
        "card_label": ParagraphStyle(
            "CardLabel",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.5,
            textColor=BRAND_MUTED,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.2,
            textColor=BRAND_TEXT,
        ),
    }


def card_grid(
    cards: list[tuple[str, str, str]],
    styles: dict[str, ParagraphStyle],
    *,
    cards_per_row: int = 4,
) -> Table:
    rows = []
    for card_row in chunks(cards, cards_per_row):
        cells = []
        for value, label, note in card_row:
            cells.append(
                Table(
                    [
                        [Paragraph(value, styles["card_value"])],
                        [Paragraph(label, styles["card_label"])],
                        [Paragraph(note, styles["card_label"])],
                    ],
                    colWidths=[CONTENT_WIDTH / cards_per_row - 8],
                    style=TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                            ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ]
                    ),
                )
            )
        while len(cells) < cards_per_row:
            cells.append("")
        rows.append(cells)

    return Table(
        rows,
        colWidths=[CONTENT_WIDTH / cards_per_row] * cards_per_row,
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        ),
    )


def styled_table(
    data: list[list[object]],
    *,
    col_widths: list[float] | None = None,
    header_background: colors.Color = BRAND_DARK,
    right_align_from: int | None = None,
    right_align_columns: tuple[int, ...] = (),
) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), header_background),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.4),
        ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_TEXT),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if right_align_from is not None:
        commands.append(("ALIGN", (right_align_from, 1), (-1, -1), "RIGHT"))
    for column in right_align_columns:
        commands.append(("ALIGN", (column, 1), (column, -1), "RIGHT"))
    table.setStyle(TableStyle(commands))
    return table


def model_metric_rows(results: dict) -> list[list[str]]:
    rows = [["Model", "ROC AUC", "Avg precision", "Precision@50", "Recall", "F1"]]
    for name, metrics in results["models"].items():
        rows.append(
            [
                name,
                pct_metric(metrics["roc_auc"]),
                pct_metric(metrics["average_precision"]),
                pct_metric(metrics["precision_at_50"]),
                pct_metric(metrics["recall"]),
                pct_metric(metrics["f1"]),
            ]
        )
    baseline = results["baseline"]
    rows.append(
        [
            "baseline_rules",
            pct_metric(baseline["baseline_roc_auc"]),
            pct_metric(baseline["baseline_average_precision"]),
            pct_metric(baseline["baseline_precision_at_50"]),
            pct_metric(baseline["baseline_recall"]),
            pct_metric(baseline["baseline_f1"]),
        ]
    )
    return rows


def reason_counts(rows: list[dict[str, str]]) -> Counter:
    counter: Counter = Counter()
    for row in rows:
        for reason in row["final_reason_codes"].split("|"):
            if reason:
                counter[reason] += 1
    return counter


def action_label(action: str) -> str:
    return {
        "refresh_and_review_ctr": "refresh + CTR",
        "refresh_and_review_engagement": "refresh + engagement",
        "expand_and_refresh": "expand + refresh",
    }.get(action, action)


def readable_reasons(reason_codes: str) -> str:
    return reason_codes.replace("_", " ").replace("|", ", ")


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(BRAND_MUTED)
    canvas.drawString(
        LEFT_MARGIN,
        0.22 * inch,
        "FlyRank ML Internship 2026 — Refresh Opportunity Model Results — anonymized data",
    )
    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        0.22 * inch,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def build_pdf() -> None:
    summary = load_json(SUMMARY_PATH)
    results = load_json(MODEL_RESULTS_PATH)
    queue_rows = load_queue_rows(QUEUE_PATH)
    styles = make_styles()

    action_counter = Counter(row["suggested_action"] for row in queue_rows)
    confidence_counter = Counter(row["confidence"] for row in queue_rows)
    reason_counter = reason_counts(queue_rows)
    best_model = summary["best_model"]
    best_metrics = results["models"][best_model]

    document = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=PAGE_SIZE,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="FlyRank Refresh Opportunity Model Results",
        author="FlyRank",
    )

    story = [
        Paragraph("FlyRank ML Internship 2026", styles["title"]),
        Paragraph("Refresh Opportunity / Content Decay Predictor — Results PDF", styles["subtitle"]),
        card_grid(
            [
                (format_int(summary["rows_scored"]), "Rows scored", "Anonymized BigQuery export"),
                (best_model.replace("_", " "), "Best model", "Selected by Precision@50"),
                (pct_metric(best_metrics["roc_auc"]), "ROC AUC", "Ranking separation quality"),
                (pct_metric(best_metrics["precision_at_50"]), "Precision@50", "Top-50 decline hit rate"),
                (format_int(summary["high_confidence_rows"]), "High confidence", "Rows ready for manual review"),
                (pct_metric(summary["target_positive_rate"]), "Declining-label rate", "Supervised target balance"),
                (format_score(summary["top_queue_score"]), "Top queue score", "0–100 final priority score"),
                ("client holdout", "Validation style", "Uses anonymized client split"),
            ],
            styles,
        ),
        Spacer(1, 0.16 * inch),
        Paragraph("How to read this quickly", styles["section"]),
        styled_table(
            [
                ["Question", "Answer"],
                [
                    "What is the artifact?",
                    "A ranked queue of content rows that should be reviewed for refresh priority.",
                ],
                [
                    "What is the model doing?",
                    "It predicts decline risk, then combines model probability with a non-leaky rule baseline for final prioritization.",
                ],
                [
                    "What should mentors inspect first?",
                    "High-confidence rows with `refresh`, `refresh_and_review_ctr`, or `refresh_and_review_engagement` actions.",
                ],
                [
                    "What is not included?",
                    "No URLs, titles, keywords, domains, client names, or raw private identifiers.",
                ],
            ],
            col_widths=[2.2 * inch, CONTENT_WIDTH - 2.2 * inch],
        ),
        Spacer(1, 0.16 * inch),
        Paragraph(
            "Bottom line: this is a practical decision-support model for the internship capstone. "
            "It is not an automatic publishing decision and should be paired with editorial review.",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("1. Model Quality", styles["section"]),
        styled_table(
            model_metric_rows(results),
            col_widths=[2.0 * inch] + [1.25 * inch] * 5,
            right_align_from=1,
        ),
        Spacer(1, 0.18 * inch),
        HorizontalBarChart(
            "Precision@50 comparison",
            [
                (name, metrics["precision_at_50"])
                for name, metrics in results["models"].items()
            ]
            + [("baseline_rules", results["baseline"]["baseline_precision_at_50"])],
            value_formatter=lambda value: f"{value:.3f}",
            color_palette=[BRAND_BLUE, BRAND_TEAL, BRAND_PURPLE, BRAND_ORANGE],
        ),
        Spacer(1, 0.1 * inch),
        styled_table(
            [
                ["Metric", "Plain-English interpretation"],
                ["ROC AUC", "How well the model ranks declining rows ahead of non-declining rows."],
                ["Average precision", "Quality of the ranked list when positives are mixed with negatives."],
                ["Precision@50", "How many of the top 50 recommended rows are actually decline-labelled."],
                ["Recall", "How many decline-labelled rows are captured at the default 0.5 probability threshold."],
            ],
            col_widths=[1.8 * inch, CONTENT_WIDTH - 1.8 * inch],
        ),
        PageBreak(),
        Paragraph("2. Queue Shape", styles["section"]),
        card_grid(
            [
                (
                    format_int(confidence_counter.get("high", 0)),
                    "High confidence",
                    "Best first review set",
                ),
                (
                    format_int(confidence_counter.get("medium", 0)),
                    "Medium confidence",
                    "Useful after high-confidence pass",
                ),
                (
                    format_int(confidence_counter.get("low", 0)),
                    "Low confidence",
                    "Mostly monitor / deprioritize",
                ),
                (
                    format_int(action_counter.get("monitor", 0)),
                    "Monitor",
                    "Not urgent for refresh",
                ),
            ],
            styles,
        ),
        Spacer(1, 0.12 * inch),
        HorizontalBarChart(
            "Suggested action mix",
            action_counter.most_common(),
            color_palette=[BRAND_TEAL, BRAND_PURPLE, BRAND_BLUE, BRAND_ORANGE, BRAND_GREEN],
        ),
        Spacer(1, 0.08 * inch),
        HorizontalBarChart(
            "Confidence distribution",
            [(label, confidence_counter.get(label, 0)) for label in ["high", "medium", "low"]],
            height=1.75 * inch,
            color_palette=[BRAND_GREEN, BRAND_ORANGE, BRAND_RED],
        ),
        PageBreak(),
        Paragraph("3. Why Pages Rank High", styles["section"]),
        HorizontalBarChart(
            "Top model features",
            [
                (item["feature"], float(item["importance"]))
                for item in results["best_model"]["feature_importance_top"][:12]
            ],
            value_formatter=lambda value: f"{value:.3f}",
            color_palette=[BRAND_BLUE, BRAND_TEAL, BRAND_PURPLE],
            max_label_chars=38,
        ),
        Spacer(1, 0.1 * inch),
        Paragraph(
            "Strong signals are mostly visibility and freshness related: days with impressions, recent search visibility, "
            "average position, content age, word count, CTR, and engagement-style metrics.",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("4. Recommendation Reasons", styles["section"]),
        HorizontalBarChart(
            "Top recommendation reason codes",
            reason_counter.most_common(12),
            color_palette=[BRAND_LAVENDER, BRAND_PURPLE, BRAND_TEAL, BRAND_BLUE],
            max_label_chars=38,
        ),
        Spacer(1, 0.08 * inch),
        Paragraph(
            "Reason codes explain why a row appears in the queue. They are designed for mentor review and intern explainability, "
            "not for automatic publishing decisions.",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("5. Top Queue Preview", styles["section"]),
        Paragraph(
            "These rows are anonymized. Use `content_id` only to join back internally when mentors are ready to inspect real pages.",
            styles["small"],
        ),
        styled_table(
            [
                [
                    "Rank",
                    "Score",
                    "Prob.",
                    "Confidence",
                    "Action",
                    "Impr.",
                    "Sess.",
                    "Trend",
                    "Reasons",
                ]
            ]
            + [
                [
                    row["final_rank"],
                    format_score(row["final_refresh_score"]),
                    format_float(row["best_model_probability"], 3),
                    row["confidence"],
                    Paragraph(action_label(row["suggested_action"]), styles["table_cell"]),
                    format_int(row["impressions_90d"]),
                    format_int(row["sessions_90d"]),
                    row["trend_direction"],
                    Paragraph(readable_reasons(row["final_reason_codes"]), styles["table_cell"]),
                ]
                for row in queue_rows[:10]
            ],
            col_widths=[
                0.45 * inch,
                0.55 * inch,
                0.55 * inch,
                0.75 * inch,
                1.0 * inch,
                0.62 * inch,
                0.55 * inch,
                0.55 * inch,
                CONTENT_WIDTH - 5.02 * inch,
            ],
            header_background=BRAND_PURPLE,
            right_align_columns=(0, 1, 2, 5, 6),
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Recommended next validation pass", styles["section"]),
        styled_table(
            [
                ["Step", "Validation action"],
                ["1", "Manually inspect the top 25 high-confidence rows in `refresh_queue.csv`."],
                ["2", "Check whether the recommended action matches editorial context and business priority."],
                ["3", "If accepted, convert this into the intern capstone task: reproduce, evaluate, explain, and improve the queue."],
                ["4", "Avoid treating model score as an automatic publishing decision."],
            ],
            col_widths=[0.55 * inch, CONTENT_WIDTH - 0.55 * inch],
        ),
    ]

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote PDF report: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
