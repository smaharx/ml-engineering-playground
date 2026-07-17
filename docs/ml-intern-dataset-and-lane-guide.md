# FlyRank ML Internship - Your Dataset and Lane Guide

Status: your guide for the Applied Search Intelligence track.

Read this together with:

- `docs/ml-core-foundation-framework.md` (ships in this repo — a deep reference, not week-one reading)
- `docs/intern-free-tooling-guide.md` (ships in this repo)
- the week-by-week curriculum on your portal board
- the data dictionary and manifest that ship inside the dataset release on Hugging Face

> This starter repo ships only the small anonymized starter dataset (`data/raw/content_refresh_anonymized.csv`).
> The much larger warehouse release lives on Hugging Face at
> [`FlyRank/internship-warehouse`](https://huggingface.co/datasets/FlyRank/internship-warehouse).
> It is gated, which means you click "request access" and accept the data-use terms first —
> approval is instant, so you can get it yourself whenever your lane needs it.

This guide shows you how to use the data without turning the internship into a fill-in-the-blank exercise. The goal is not to memorize FlyRank's existing rules. The goal is to understand the problem, look at the evidence, build a simple starting point, test a better method, check it honestly, and turn the result into a ranked list of safe recommendations.

## 0. Where These Numbers Come From

Every count and date in this guide was checked against the real data pipeline, not written from memory. The release itself was built, scrambled, and verified on FlyRank's side before it was published; the details of that build live in the dataset manifest that ships with the release on Hugging Face. You don't need any of that tooling — everything you need is already in this repo and on Hugging Face:

- the runnable starter pipeline (`scripts/01`–`05`, `ml_utils.py`, `run_all.py`);
- its verified committed outputs (`outputs/model_report.md`, `outputs/refresh_queue_sample.csv`, `outputs/charts/`); `outputs/model_results.json` is regenerated when you run the pipeline;
- the small anonymized starter dataset (`data/raw/content_refresh_anonymized.csv`).

One important rule about snapshots (a snapshot is a copy of the data frozen at one moment in time):

- For warehouse work, use the Hugging Face release. It is a fixed snapshot with the exact date windows written out below.
- Stick to this release for your internship work — it is the snapshot every number in this guide describes, so results built on it can be compared and rerun.
- You never need raw BigQuery credentials, raw client names, raw domains, raw URLs, raw private queries, or raw text. Everything sensitive was removed or scrambled before release.

## 1. The Core Idea

The whole track follows one workflow:

```text
research question -> safe data contract -> signal audit -> baseline score -> your chosen lane -> validation -> ranked action recommendations
```

Here is what those words mean, in order. A **research question** is the one question your project answers. A **data contract** is a short written promise about which data you will use and how. A **signal audit** is a check of whether the columns actually contain useful information. A **baseline** is the simplest possible method, built first, so you have something honest to beat. **Validation** is the test that proves your result is real and not an accident. **Ranked action recommendations** are the final output: a list of pages, ordered by which one someone should look at first.

The teaching method is:

```text
core idea first -> AI-assisted implementation second -> human judgment last
```

That means:

- Start with the content and search problem, not with a model.
- Use AI to draft code, ideas, checks, and explanations — but never let AI decide what is true. You check that yourself, against the data.
- Treat product scores and flags as useful background, not as the truth.
- Prefer simple methods you can explain, until something harder is clearly worth it.
- Tie every claim you make to something the data can actually prove.

Your deliverables along the way are notebooks, and they already have homes: pre-named skeleton notebooks live in `work/notebooks/` (for example `w01_research_question.ipynb` through `w07_action_playbook.ipynb`, plus `capstone.ipynb`). You fill those in — you do not create separate report files.

## 2. Which Data To Use

Your internship data is the warehouse release described below, plus the small runnable starter dataset that ships in this repo. Both contain **observable signals only** — real measurements of what happened, never the product's own decisions.

### About the Release

The warehouse release, and how to get it:

- Release: [`FlyRank/internship-warehouse`](https://huggingface.co/datasets/FlyRank/internship-warehouse) on Hugging Face. It is gated — request access, accept the data-use terms, and approval is instant. Notebook 03 shows the DuckDB workflow for reading it. Build id: `flyrank_pseudonymized_warehouse_release_v20260703`.
- Source: `central_data_warehouse`
- Export date: `2026-07-03`
- Freshness lag: the freshest 3 days were cut off on purpose, because the very newest rows are often incomplete — 3 days back from `2026-07-03` means daily time-series facts stop at `2026-06-30`
- Chunk size: 10,000 rows per CSV part
- How it was scrambled and verified: identifiers were pseudonymized (replaced with stable scrambled codes) and the release passed its checks before publishing — the full details are in the dataset manifest on Hugging Face.

> **Building features and iterating?** Develop against one middle month (e.g. `month=2026-03`) and run the full fact table only for your final pass — hitting the full table over and over can trip Hugging Face rate limits (HTTP 429 errors). Avoid the `_sample` table for experiments: it holds the LAST month of data, and if your label is about "what happens next", experimenting there means peeking at the future you're supposed to predict.

When you write about the data, use only the counts and date windows below — they match the release exactly.

### Which Lanes Are Ready, and With What Data

A **lane** is a project direction you can pick. Four lanes are predefined, and freestyle means bringing your own question (section 9 explains it).

| Lane | Type | Default dataset | Output |
|---|---|---|---|
| Ranking Signal Analysis | Core lane | warehouse release or starter dataset | Signal report and evidence-backed recommendations |
| Refresh / Content Opportunity Scoring | Core lane | starter playground plus warehouse support | Ranked review queue with scores, actions, and reason codes |
| Structured Content Archetype Clustering | Core lane | warehouse release or starter dataset | Cluster profiles and action mapping; do not call this semantic clustering |
| CTR / Engagement Opportunity Scoring | Core lane | warehouse release or starter dataset | Ranked opportunity score; position/volume adjusted |
| AI Referral Opportunity | Freestyle direction | warehouse daily facts (`sessions_ai`; starter dataset: `ai_sessions_90d` / `ai_traffic_pct`) | EDA/ranking only by default; positive examples are sparse |
| Growth / Recovery / Momentum Prediction | Freestyle direction | warehouse daily facts with time windows you build yourself | Future-window model with strict leakage audit |

### The Warehouse Tables

The warehouse release gives you **dimension tables** and **fact tables**. A dimension table describes things (one row per client, one row per content item). A fact table records events over time (one row per content item per day). You define your own joins, windows, labels, and leakage checks — that freedom is the point.

The release is hosted at
[`FlyRank/internship-warehouse`](https://huggingface.co/datasets/FlyRank/internship-warehouse)
(gated; Parquet files; see notebook 03). Ready-made example cuts for each lane live at
[`FlyRank/internship-lanes`](https://huggingface.co/datasets/FlyRank/internship-lanes). Build id:

```text
flyrank_pseudonymized_warehouse_release_v20260703
```

| Table | Rows | Grain | Main use |
|---|---:|---|---|
| `dim_clients` | 104 | one row per pseudonymized client | grouping, client-level checks, per-client history coverage (`gsc_data_start`, `ga4_data_start`) |
| `dim_content` | 519,606 | one row per pseudonymized content item | content metadata and joins |
| `fact_content_daily_performance` | 78,835,655 | daily x client x content | time-series features, trend labels, forward-window validation |
| `fact_content_query_90d` | 2,414,248 | client x content x query hash (fixed 90-day window) | query-mix features: diversity, concentration, rare/anonymized tail |

(**Grain** means "what one row stands for." Always know the grain before you touch a table.)

Use the warehouse data when you want the most freedom. The trade is that you must then write a stronger data contract, because you now control the joins, the windows, the labels, and the leakage risks yourself.

What went into the snapshot:

| Source object | Source rows | Clients | Content items | What it contributes |
|---|---:|---:|---:|---|
| `all_content_data` | 520,006 | 84 | 519,606 | Primary content dimension source |
| `daily_content_performance_v2` | 78,835,655 | 70 | 427,292 | Primary daily fact source (v2 full history), excluding the freshest 3 days |

The snapshot's date windows:

| Source/date field | Min date | Max date |
|---|---|---|
| `all_content_data.content_created_at` | 2024-10-16 | 2026-07-06 |
| `daily_content_performance_v2.report_date` | 2025-01-27 | 2026-06-30 |

The history is an **unbalanced panel** — a fancy way of saying that different clients have different amounts of history. The daily data starts 2025-01-27 at the earliest, and each client's history begins whenever their tracking started (9 of the 70 clients have 12+ months, which is enough for seasonality work). Rows from before a client's GA4 start contain search data only, with `ga4_data_available = FALSE`. So before you define any time window, check `dim_clients.gsc_data_start` and `ga4_data_start` — otherwise you may accidentally treat "no tracking yet" as "no traffic."

How dense each metric is inside the snapshot (not every row has every measurement):

| Metric presence | Rows |
|---|---:|
| daily fact rows | 78,835,655 |
| rows with GSC impressions | 28,970,051 |
| rows with GSC clicks | 3,112,607 |
| rows with GA4 sessions | 2,778,564 |
| rows with AI sessions | 30,177 |
| rows with scroll events | 600,821 |

What this table tells you:

- The search-performance and lifecycle lanes have the deepest data.
- The CTR and engagement lanes have enough direct signal, but you will still need minimum-volume filters (rules like "only look at pages with at least N impressions") to keep noise out.
- AI-referral analysis is possible, but AI-session rows are far thinner than search impressions — notice 30,177 versus 28,970,051.
- The daily table is huge because it is a fact table. Do not flatten it into one row per page without thinking; first choose your decision grain and your feature and target windows.

How the tables were assembled (one-paragraph version — the manifest has the rest):

- `dim_clients` combines every client that appears in the client, content, and daily performance sources.
- `dim_content` deduplicates content into one row per pseudonymized content item.
- `fact_content_daily_performance` cuts off the freshest 3 days: `report_date <= DATE_SUB(DATE('2026-07-03'), INTERVAL 3 DAY)` (so daily facts run through `2026-06-30`).
- Raw client names, domains, raw URLs, raw queries, raw keywords, content titles, and any files that could link scrambled ids back to real ones are not in the release.

Keys and joins (a **join** connects two tables through a shared id column):

| Table | Key |
|---|---|
| `dim_clients` | `client_hash_id` |
| `dim_content` | `content_hash_id` |
| `fact_content_daily_performance` | `report_date + client_hash_id + content_hash_id` |

Join rules:

- Join content facts to `dim_content` on `content_hash_id`.
- Join client-level facts to `dim_clients` on `client_hash_id`.
- Use `keyword_hash_id` and `url_hash_id` (on `dim_content`) for grouping, deduplication, leakage checks, and case analysis. Never try to work out what real keyword or URL a hash stands for.

## 3. Field Types

When you open a table, sort every column into one of these buckets before you model anything. This ten-minute habit prevents most of the painful mistakes later.

| Field type | Meaning | Example fields | Default use |
|---|---|---|---|
| Join keys | Scrambled ids that connect tables | `client_hash_id`, `content_hash_id`, `url_hash_id`, `keyword_hash_id` | Join and group only; the codes themselves mean nothing |
| Observed signals | Real measurements from search, analytics, or content metadata | impressions, clicks, position, CTR, sessions, scroll rate, word count, age | Good candidate features, as long as they were known before the decision point |
| Derived measurements | Numbers calculated from observed signals | `trend_pct`, age/freshness tiers, position tier | Usually fine, if calculated only from the feature window |
| Product context | Rule-outputs FlyRank's app computes (`health_score`, `priority_score`, `action_type`, refresh flags) — these are NOT shipped in your data | `health_score`, `priority_score`, `action_type`, `refresh_tier`, flags | Not in your dataset. If you ever rebuild one yourself, treat it as background or as a baseline to beat — never as a feature or a label for discovery |
| Target/proxy fields | The thing your model or analysis tries to predict or rank | future decline, recovery, top-K action priority, cluster membership | You must define these yourself, in your data contract |
| Raw-origin context | Columns that started life as real search queries, web addresses, titles, or client details | raw query/URL/title/client fields | These were scrambled before you got them, and the originals are never in your data. If your output ever shows something that looks like a real name or address, stop and remove it |

## 4. Observable Signals, Not Product Decisions

FlyRank's product computes rule-based decision flags and combined scores with hand-tuned SQL — things like `health_score`, `needs_ctr_fix`, `is_quick_win`, a `priority_score`, and an `action_type`. Those are how the live app decides which pages to surface.

Those product decisions are deliberately **not** in your data. Your data ships observable search and engagement signals, plus transparent derived buckets (tiers, `trend_direction`, `trend_pct`, ctr, rates) — and nothing else. This is on purpose, so you discover signal from evidence instead of accidentally copying the product's own answers.

Here is why this matters so much: if you feed the product's own decision into your model, the model just learns to copy that decision. The score looks great, but you discovered nothing — the answer was already in the input. That trap is called a **circular result**. So build only from observable signals (things that were true BEFORE anyone decided anything), and let your model find its own signal.

The strongest labels for supervised learning come from **future observed outcomes**, not from a current decision. Prefer labels like: traffic that later declined, a page that later recovered, CTR that later changed, or engagement that later changed — always measured after a clearly defined decision point. If you ever choose to rebuild a product flag and predict it, say so out loud in your write-up, and present it honestly as "can I reproduce the existing rule?" rather than as a discovery.

## 5. The Starter Playground: What It Proves

The starter playground is a runnable example, not the whole internship. **It is this repo.**

Main input:

```text
data/raw/content_refresh_anonymized.csv
```

The pipeline (run all of it with `python scripts/run_all.py`):

```text
01_prepare_features.py -> 02_baseline_score.py -> 03_train_model.py -> 04_evaluate_and_export.py -> 05_build_pdf_report.py
```

The starter target — the thing the starter model predicts — is:

```text
is_declining_label = trend_direction == "down"
```

This is simple on purpose. It shows the workflow end to end, but notice its weakness: it is a bucket calculated from the current window, not a future outcome. That makes it a beginner **proxy label** — a stand-in for the thing you really care about. Treat it that way, not as the ideal capstone target. A stronger capstone defines a future-looking outcome, like:

```text
features from prior 90 days -> decline or recovery over next 30 days
```

Exactly what the starter feature prep does:

- Input: `data/raw/content_refresh_anonymized.csv`.
- Required columns include `content_id`, `client_id`, `impressions_90d`, `sessions_90d`, `content_age_days`, and `trend_direction`.
- Rows are kept only when `impressions_90d > 0` and `content_age_days >= 90`.
- Rows are deduplicated by `content_id`.
- The data ships observable signals only; FlyRank's product decision flags were never included, so there is nothing to strip out. The label is `trend_direction == "down"`.

The starter model's features:

- Numeric features: search volume, competition, CPC, word/char count, logged 90d impressions/clicks/sessions/AI sessions, days with impressions/sessions, age, freshness, CTR, average position, engagement rate, scroll rate, and AI traffic percentage.
- Categorical features: competition level, content type, main intent, age tier, freshness tier, word-count tier, impression tier, and position tier.

The starter baseline score, exactly as coded:

```text
baseline_refresh_score =
  0.40 * visibility_score
+ 0.30 * freshness_risk_score
+ 0.25 * position_opportunity_score
+ 0.05 * depth_gap_score
```

Starter baseline reason codes (a **reason code** is a short tag that tells a human WHY a page got its score):

- `stale_visible_page`: `days_since_last_update >= 180` and `impressions_90d >= 500`
- `declining_with_demand`: `trend_direction == "down"` and `impressions_90d >= 100`
- `thin_visible_page`: `word_count > 0`, `word_count < 1200`, and `impressions_90d >= 250`
- `page_one_decay_risk`: `avg_position > 0`, `avg_position <= 10`, and `content_age_days >= 180`
- `low_ctr_visible_page`: `impressions_90d >= 500`, `0 < avg_position <= 20`, and `ctr < 0.5`
- `low_engagement_visible_page`: `sessions_90d >= 30` and `engagement_rate` or `scroll_rate` below 30

The starter's final score, exactly as coded:

```text
final_refresh_score =
  100 * (0.70 * best_model_probability + 0.30 * normalized_baseline_score)
```

Final starter reason codes:

- `model_decline_risk`: model probability >= 0.65
- `visible_model_opportunity`: model probability >= 0.50 and `impressions_90d >= 500`
- `ctr_review_candidate`: `impressions_90d >= 500`, average position 1-20, and `ctr < 0.5`
- `engagement_review_candidate`: `sessions_90d >= 30` and `engagement_rate` or `scroll_rate` below 30

The starter's high-confidence label also demands enough evidence: final score above the 80th percentile, `impressions_90d >= 500`, `sessions_90d >= 10`, and model probability >= 0.50.

Starter model results, verified from `outputs/model_results.json` and `outputs/model_report.md`:

| Method | ROC AUC | Average precision | Precision@50 |
|---|---:|---:|---:|
| baseline rules | 0.627 | 0.468 | 0.240 |
| logistic regression | 0.700 | 0.522 | 0.400 |
| decision tree | 0.742 | 0.575 | 0.540 |
| random forest | 0.750 | 0.618 | 0.740 |

What these numbers mean in plain words:

- **Precision@50** asks: of the top 50 pages the system says to review first, how many actually turned out positive by the chosen label?
- The baseline got about 12 of its top 50 right: `0.240 * 50`.
- The random forest got about 37 of its top 50 right: `0.740 * 50`.
- That is strong evidence that a learned ranking can beat a fixed rule — on this starter slice.

Keep the scope honest:

- This result comes from a 30,000-row anonymized starter slice.
- It used client-holdout validation (whole clients kept out of training, so the model is tested on clients it never saw).
- It is not a benchmark on the full ~79M-row daily warehouse.
- The full warehouse gives you the scale and structure to test stronger definitions — but the result has to be earned all over again, with proper validation.

## 6. What "The Right Page To Fix" Means

In this internship, "the right page to fix" usually means:

```text
the right page to REVIEW FIRST, based on evidence and limited capacity
```

It does not mean:

```text
a page guaranteed to recover if someone edits it
```

To prove that a refresh CAUSED a recovery, you would need an experiment or another causal design — something this data alone cannot give you. Most capstones here are **decision-support** projects: they rank candidates so a human reviewer spends their limited time on the most promising pages first.

A good candidate page usually has:

- enough demand or exposure to matter;
- evidence of movement, weakness, or opportunity;
- an action someone could realistically take;
- reason codes a reviewer can inspect;
- no obvious leakage or private-data issue;
- no obvious consolidation, seasonality, or noise explanation (section 7 explains those three).

## 7. Decline Versus Consolidation, Seasonality, And Noise

Not every drop in traffic is a decline. Before you label a page "declining," rule out the look-alikes:

| Pattern | What it means | How to check |
|---|---|---|
| Real decline | The same content keeps losing visibility, clicks, or position over a sustained window | Compare an earlier window to a later one; check impressions, clicks, position, and whether the drop persists |
| Consolidation | One URL drops because a related URL on the same site absorbed the demand | Check related content/keyword/url hash groups — did a sibling page gain what this one lost? |
| Seasonality | Demand naturally drops with the calendar or the market | Compare to site-level trends, topic groups, or the same period in earlier history where available |
| SERP or AI click loss | Impressions and position hold steady while clicks drop (the search page itself changed) | Look at impressions, clicks, CTR, position, and AI-session context separately, not as one blob |
| Noise | Small, low-volume wiggles with no lasting pattern | Require minimum volume and persistence, and say how confident you are |

The line between these is a definition YOU choose and defend. A strong definition spells out:

- magnitude: for example, a drop bigger than a threshold you wrote down;
- window: for example, the prior 90 days versus the next 30 days;
- persistence: the drop lasts longer than a short blip;
- minimum volume: enough impressions or sessions that it cannot be pure noise;
- group checks: related pages did not simply absorb the traffic;
- prediction-time discipline: your feature window never overlaps your target window.

## 8. Lane Guide

Whichever lane you pick, you produce the same core artifacts: a data contract, a signal audit, a baseline, a model or analysis, validation, a ranked action output, and a public-safe write-up. These live in your `work/notebooks/` skeletons — one notebook per assignment, already named for you.

### Lane 1: Ranking Signal Analysis

Question:

```text
Which safe content and search signals are associated with visibility, clicks, engagement, or movement?
```

Good data:

- the warehouse release (`dim_content` + `fact_content_daily_performance`) or the starter dataset.

Good methods:

- EDA (exploratory data analysis — looking at the data with summaries and charts before modeling anything);
- correlations and grouped summaries;
- simple regressions or classification, if you define a target;
- feature importance from a simple model;
- effect sizes (not just "is there a link" but "how big is it").

Output:

- a signal report;
- charts;
- practical content recommendations;
- clear caveats that your results are observational — you watched, you did not experiment.

Common mistakes:

- claiming you proved a Google algorithm factor;
- using a score like `health_score` as both a feature and the target;
- reading big meaning into weak correlations.

### Lane 2: Refresh / Content Opportunity Scoring

Question:

```text
Which pages should be reviewed first for refresh, expansion, protection, pruning, or monitoring?
```

Good data:

- the warehouse release (`dim_content` + `fact_content_daily_performance`) or the starter dataset;
- the warehouse daily table if you want stronger time-window labels.

Good methods:

- a transparent baseline score;
- logistic regression, decision tree, random forest, or gradient boosting where the extra complexity earns its keep;
- a ranked queue with reason codes;
- precision@K, recall, average precision, and a by-hand review of your top 20.

Useful baseline ideas:

- stale visible page;
- declining with demand;
- thin visible page;
- page-one decay risk;
- CTR or engagement review context.

Output:

- a ranked action queue;
- a suggested action per page;
- reason codes;
- a confidence label;
- a model or analysis card (a one-page summary of what you built, what it is for, and where it breaks).

Common mistakes:

- treating "declining" as a guarantee that a refresh will pay off;
- using metrics from the future window as features;
- hiding the reason behind a high score.

### Lane 3: Structured Content Archetype Clustering

Question:

```text
What performance archetypes exist across the content inventory?
```

(An **archetype** is a recurring "type" of page — clustering finds groups of pages that behave alike.)

Good data:

- the warehouse release (`dim_content` + `fact_content_daily_performance`) or the starter dataset.

The release supports structured clustering from safe metrics, buckets, token counts, and content metadata. It does not contain article text, so true semantic (meaning-based) clustering is not possible here — and calling metric clustering "semantic" would be claiming something you did not do.

Good methods:

- scaling numeric features so no single one dominates;
- K-Means or another clustering method you can explain;
- PCA or another two-dimensional projection for visualization;
- cluster profiling — describing each cluster with its typical numbers.

Possible archetypes:

- champions;
- rising stars;
- hidden gems;
- stale visible pages;
- weak/no-demand pages;
- engagement-problem pages;
- cannibalization-risk pages.

Output:

- cluster profiles;
- archetype names;
- an action mapping such as protect, improve, rewrite, merge, prune, or monitor.

Common mistakes:

- naming clusters before actually inspecting what is in them;
- treating clusters as true labels instead of a lens;
- using unsafe text fields or raw URLs;
- calling metric/token-count clustering "semantic clustering."

### Lane 4: CTR / Engagement Opportunity Scoring

Question:

```text
Which visible pages under-capture clicks or engagement and deserve metadata, content, or monitoring review?
```

Good data:

- the warehouse release (`dim_content` + `fact_content_daily_performance`) or the starter dataset;
- the warehouse daily table.

Good features:

- impressions;
- clicks;
- CTR;
- average position;
- position tier;
- intent/content type;
- age and freshness;
- sessions and engagement context.

Good methods:

- expected CTR by position tier (pages at position 1 always get more clicks than pages at position 9 — compare pages only to others in the same tier);
- residual or gap analysis — how far below its tier's expected CTR a page sits;
- ranked scoring;
- classification, if you define a leakage-safe label.

Output:

- a ranked list of CTR or engagement review candidates;
- reason codes such as high impressions, low CTR, strong position, enough volume, enough sessions, or weak engagement;
- action suggestions such as rewrite title/meta, improve intent match, improve snippet structure, improve on-page engagement, or monitor.

Common mistakes:

- comparing CTR across different positions without adjusting for position;
- ignoring low-volume noise;
- assuming low CTR always means the title or meta description is bad.

## 9. Freestyle — Your Own Question

Freestyle means you skip the four lanes and bring your own search or discoverability question: your own joins, your own features, your own labels, and your own model, built on the full warehouse. No approval, no gate — freestyle is a normal choice, and it follows the same "what done looks like" bar as every lane: data contract, signal audit, baseline, validation, ranked output, public-safe write-up.

If you want a harder start but not a blank page, here are two battle-tested freestyle directions. Both work; both bite if you skip their warnings.

### Freestyle direction: AI Referral Opportunity

Question:

```text
What broad content patterns appear around AI-referred traffic, and where might AI visibility be improved?
```

Good data:

- the warehouse daily facts column `sessions_ai` in `fact_content_daily_performance` (starter dataset: `ai_sessions_90d` / `ai_traffic_pct`).

Best use:

- EDA;
- broad pattern analysis;
- opportunity ranking;
- a careful, written discussion of what this data can and cannot say.

The big warning:

AI-referral sessions are **sparse** — remember the density table: 30,177 rows with AI sessions against 78.8 million daily rows. Treat this direction as EDA and ranking. Do not train a binary classifier on AI sessions alone; with positives this rare, the model will look impressive and mean nothing.

Output:

- a pattern report;
- opportunity segments;
- cautious recommendations about content structure, definitions, FAQ blocks, or source clarity.

Common mistakes:

- treating "no AI sessions" as proof that AI platforms cannot understand the content;
- making strong claims from sparse AI-session data;
- building binary classifiers without valid positive and negative examples;
- claiming AI citations, AI rankings, or AI search visibility — this field only measures sessions where someone actually clicked through from an AI tool.

### Freestyle direction: Growth / Recovery / Momentum Prediction

Question:

```text
Can we predict which pages are likely to decline, recover, or gain momentum?
```

Good data:

- the warehouse release (`dim_content` + `fact_content_daily_performance`) or the starter dataset;
- daily windows you build yourself from `fact_content_daily_performance` — after a leakage review.

The label shape that keeps you honest:

```text
prior feature window -> future target window
```

Examples:

- prior 90 days of features -> next 30 days decline;
- prior 28 days of features -> next 28 days growth;
- prior state after a refresh -> later recovery signal, if the data safely supports it.

The big warning: this direction lives or dies on **clean future-window labels and strict leakage control**. Leakage means information from the future (or from the answer itself) sneaking into your features — it makes results look great and be worthless. Build the windows first, audit them, then model.

Good methods:

- time-aware or client-grouped validation;
- logistic regression, tree, random forest, or gradient boosting;
- calibration and threshold review;
- precision@K for review queues.

Output:

- a prediction report;
- a ranked future-risk or future-opportunity list;
- a validation audit;
- a plain-words explanation of what the model can and cannot claim.

Common mistakes:

- using target-window metrics as features;
- letting pages from the same client land in both train and test without a grouped check;
- calling seasonal movement "model skill."

## 10. Do Not Do This

- Do not train an AI-session classifier on the sparse AI-session data alone.
- If you ever rebuild a product decision flag, `priority_score`, `action_type`, or `health_score`, do not use it as an ordinary model feature — your data is observable-only precisely to protect you from this.
- Do not publish or try to reconstruct raw query, URL, title, domain, client, category, or keyword examples.
- Do not claim a refresh caused a recovery unless you ran an explicit experiment or causal design.
- Do not claim Google algorithm factors, AI citations, or AI rankings from these datasets.

## 11. Thresholds And Decision Policies

A **threshold** is a cutoff you choose — and every threshold is a policy choice, not a universal truth.

Examples of thresholds you will have to pick:

- how many impressions are enough to matter;
- how big a drop counts as decline;
- where CTR becomes weak for a position tier;
- how many pages fit the review team's capacity;
- what score earns the label "high confidence."

A good way to pick one:

1. Start with a simple rule you can explain.
2. Show how many rows it captures.
3. Review real examples from the top, the middle, and the edge.
4. Try alternative thresholds and watch what changes.
5. Compare precision@K, recall, false positives, and the value of the actions taken.
6. Pick the threshold that matches the real decision capacity and risk.
7. Write down the trade-off you accepted.

For ranked action work, top-K metrics usually beat generic accuracy, because they match how the list is actually used:

- Precision@20 if a reviewer checks 20 pages.
- Precision@50 if the team can act on 50 candidates.
- Average precision if the whole ranking matters.
- Recall if missing a true problem is expensive.

## 12. Validation Rules

A model or analysis is only worth something if its validation design matches the problem. Pick the design on purpose:

- a plain train/test split, when examples are truly independent;
- client/group holdout, when pages from the same client may share patterns the model could memorize;
- a time-aware split, when you predict future movement — train on the past, test on the future;
- a top-K review, for ranked queues — read your own top pages;
- cluster stability checks, for archetype lanes — do the clusters survive a re-run?;
- a leakage audit, for every lane, every time.

The leakage checklist — ask each question out loud:

- Are any features calculated after the decision point?
- Does the feature window overlap the target window?
- If you rebuilt any product output (`health_score`, a decision flag, `priority_score`, or `action_type`), did it slip in as a normal feature?
- Does a derived field secretly encode the target?
- Are duplicate or related rows split across train and test in a way that makes the test too easy?
- Are you testing on clients or time periods the model has not effectively already seen?

## 13. Precalculated Columns: How To Use Them

Precalculated columns (like tiers and trend buckets) are allowed and useful. They should make the problem easier to understand — not do the thinking for you.

Good uses:

- understand how FlyRank's existing system frames a page;
- build a transparent baseline;
- compare your model against the existing rule;
- inspect where your model disagrees with the product's framing;
- explain reason codes in your final action queue.

Risky uses:

- rebuilding a product decision flag and then feeding it to a discovery model as a feature;
- calling a product flag "the truth" without checking future outcomes;
- optimizing your model just to agree with the old rule;
- leaning on a combined score like `health_score` instead of explaining the underlying signals.

If you use a precalculated field, answer these five questions first:

- What is it trying to measure?
- Was it available at prediction time?
- Is it context, a feature, a label, or an output?
- Could it leak the answer?
- Does your result still hold if you remove it?

## 14. Public-Safe Output Rules

Your final deliverable is a deployed research paper — a public web page anyone can read — plus your repo. Because it is public, everything in it must be public-safe.

Allowed:

- pseudonymized IDs;
- aggregated metrics;
- charts built from safe data;
- high-level examples;
- careful observed/directional claims ("we observed", "this suggests" — not "this proves");
- generic content actions.

Not allowed:

- client names;
- domains;
- URLs from the data;
- raw private queries;
- titles or text fields that could reveal who a client is;
- credentials or BigQuery internals;
- claims that you proved Google's algorithm;
- claims that a refresh caused a recovery, unless you ran a valid causal design.

## 15. What Done Looks Like: The Capstone Self-Check

Your capstone ships as two things: your **deployed research paper** (a public web page) and your **repo**, where `submission/paper_url.txt` at the repo root holds exactly one line — the direct URL of your deployed paper. The only thing you ever submit, on the capstone card in your portal, is your repo URL. When your paper is live, your notebooks are in `work/notebooks/`, and `paper_url.txt` points at the paper — you are done.

Before you call it done, check that your work answers every one of these:

- What problem are you solving?
- What decision or ranking are you improving?
- What does one row mean — what is your grain?
- What data tables did you use?
- Which fields are features, labels/proxies, context, excluded, or leakage risks?
- What baseline did you build?
- What model or analysis did you choose, and why?
- What split or validation design did you use?
- What metric matches the real decision?
- Did the model beat the baseline? If not, what did you learn?
- What are the top recommendations?
- What reason codes explain them?
- What would make a recommendation wrong?
- Which claims are safe, and which are not proven?
- Could someone else rerun your work from your repo alone?

## 16. One-Sentence Mental Model

You are not building magic SEO automation. You are using safe real-world search and content data to learn which signals help prioritize content decisions, then checking honestly whether that prioritization beats a transparent rule — and saying clearly where human review is still required.
