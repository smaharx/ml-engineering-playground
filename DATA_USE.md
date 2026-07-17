# Data Use & Public-Safety Rules

The one dataset that ships with this repo is:

```text
data/raw/content_refresh_anonymized.csv
```

It is a small, **anonymized** slice of FlyRank content-performance data — one row per
pseudonymized content item, with observed search/engagement metrics, content metadata,
age/freshness fields, and derived comparison windows.

## What has already been removed

The starter export contains **no**:

- client names
- domains
- URLs
- page titles
- keywords or raw search queries
- product-rule flags used as composite scores you should trust blindly

Only hashed `content_id` / `client_id` labels plus numeric and categorical metrics remain.

Rate columns (`ctr`, `engagement_rate`, `scroll_rate`, `ai_traffic_pct`, `trend_pct`) are
percentages on a 0–100 scale: `ctr = 0.76` means 0.76%, not 76%.

The hashed IDs are pseudonyms derived from FlyRank-internal database identifiers. They
contain no public information, but treat them as pseudonymous, not anonymous: use them
for grouping and joining only, never as model features, and never attempt to map them back.

## Your rules while working

1. **Do not add raw private client data** to this repo or any fork of it. If you need
   more data than the starter slice, request an approved release from your mentor —
   never export it yourself.
2. **Do not paste this data (or any client data) into third-party tools** — cloud AI
   assistants, free APIs, hosted notebooks — beyond what the approved release allows.
   Treat every external tool as third-party processing.
3. **Hashed IDs are for grouping/joining/validation only** — use them for grouped
   train/test splits, not as model features.
4. **Observable signals only.** The starter data ships observable search/engagement
   metrics and transparent derived buckets. FlyRank's product decision flags and scores
   (`health_score`, `needs_ctr_fix`, `is_quick_win`, …) are intentionally not included,
   so you build from observable evidence and never learn the product's own decision.
5. **Public outputs must use careful language** — *observed, measured, directional,
   decision-support*. Never claim you "predicted Google's algorithm" or proved causal
   refresh impact. Publish aggregates, charts, and pseudonymized IDs — never careless
   row-level dumps.

## When you publish your capstone

Your final repo is public. Before you push:

- confirm no raw client identifiers, URLs, or queries appear anywhere;
- confirm you did not commit a larger dataset than the anonymized starter slice;
- keep claims honest and decision-support framed.

CI fails any commit that includes a dataset or leaks client-identifying
patterns — this rule doubles as the public-safety discipline the internship teaches.
