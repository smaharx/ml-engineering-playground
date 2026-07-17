---
name: building-baselines
description: Builds the transparent rule-based baseline every model must beat — a hand-written score with reason codes, ranked output, and precision@K evaluation. Use before training any model, or when someone reports model results with nothing to compare against.
---

# Building baselines

A model without a baseline is a number without a meaning. The baseline is a rule a human can
read — and its job is to be honestly beatable.

## Build it in this order

**1. Say the rule in plain words first.** "A page is worth reviewing if it used to get traffic,
it's getting old, and its position is slipping." If you can't say it, you can't code it.

**2. Code it as a transparent score.** Multiply/add simple conditions; no fitted weights:

```python
stale   = (df["days_since_update"] >= 180).astype(int)
visible = (df["impressions"] >= 500).astype(int)
df["score"] = stale * visible * df["impressions"]     # readable on purpose
```

**3. Attach reason codes.** Every scored item carries WHY it scored ("stale_but_visible",
"position_slipping"). Reason codes are what make a ranked list trustworthy to a human.

**4. Rank and evaluate at K.** For "which ones first?" problems the honest metric is
**precision@K**: of the top K the rule flags, how many were actually right?

```python
def precision_at_k(scores, labels, k):
    import numpy as np
    order = np.argsort(-np.asarray(scores))
    return np.asarray(labels)[order[:k]].mean()
```

Always print the **base rate** next to it (labels.mean()): precision@50 of 0.60 means little
until you know whether random picking gives 0.55 or 0.10.

**5. Review the top of the list by hand.** The top 20 is where bad logic shows itself. For each:
the action, the reason code, a confidence note, and what would make it wrong.

## Also useful

- A dummy baseline (predict the majority class / mean) is the floor below the floor — one line
  with sklearn's DummyClassifier, and surprisingly clarifying.
- Keep the baseline frozen once the model work starts. Moving the goalposts mid-game convinces
  nobody, including you.

## How to verify

- The rule fits in three sentences a non-engineer understands.
- precision@K is computed on the SAME data slice and labels the model will use later.
- The top-20 hand review found at least one weak pick — if it found none, look harder.
