---
name: auditing-signals
description: Runs an honest EDA and signal audit — distributions first, heavy-tail handling, verdict-style mini-tests (CONFIRMED/OPPOSITE/MIXED/FALSE), sample-size floors. Use before modeling, when testing whether a popular belief shows up in data, or when a correlation looks too good.
---

# Auditing signals

Look before deciding. A signal audit asks one question per test: "does the data actually show
the story people tell?" — and accepts NO as a valid, publishable answer.

## Order of operations

**1. Distributions first.** Plot or describe every field you'll test. Web/traffic metrics are
almost always heavy-tailed: a few giants, a long tail of tiny values. That one fact changes
everything below.

**2. Handle heavy tails before correlating.** Plain (Pearson) correlation on raw heavy-tailed
values is dominated by the giants and can flip sign after a log transform. Default to:
- `log1p()` the traffic-like columns, or
- rank-based (Spearman) correlation, or
- grouped medians by bucket (tiers), which humans also read best.

**3. One mini-test per signal, with a verdict.** Structure every test identically:
- The claim, in one sentence ("longer pages get more traffic").
- The test: a grouped table or simple comparison, on a defined slice.
- The verdict: **CONFIRMED / OPPOSITE / MIXED / FALSE** — plus one sentence of what it means
  in practice.

**4. Respect sample-size floors.** No verdict from a bucket with fewer than ~50 rows (~30 for
cross-cuts). A huge ratio from a tiny cell is noise wearing a costume — say "insufficient data"
instead, that's a finding too.

## Traps

- **Rates need denominators.** A 100% rate from 2 events is nothing. Show n next to every rate.
- **Ratio metrics can exceed 100%** when numerator and denominator come from different systems —
  check the definition before declaring a data bug or a miracle.
- **Averaging per-row rates ≠ the true rate.** Weight by the denominator (total clicks / total
  impressions, not the mean of per-page CTRs).
- **A zero can mean "not measured."** Check whether 0 in a column means zero, or means the
  instrument wasn't on (a flag column usually tells you).
- **Missingness follows categories.** Test missing rates per category before filling blanks —
  a blind fillna(0) can quietly inject a category signal into your features.

## How to verify

- Every verdict has a table with visible n's under it.
- Rerun one test on a different slice (another period, another group). A real signal survives;
  noise doesn't.
- Read your verdicts as a skeptic: does any CONFIRMED rest on a bucket smaller than the floor?
