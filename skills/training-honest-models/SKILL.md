---
name: training-honest-models
description: Trains a first model the honest way — method chosen to fit the question, compared against the baseline on the same split and metric, errors read before scores are believed. Use when moving from a rule baseline to a learned model, or when reviewing a model that reports only a single score.
---

# Training honest models

The model is the easy part. The honesty is the work: same data, same split, same metric as the
baseline — then read the errors before believing the score.

## Choose the method to fit the question

| Question shape | Start with | Because |
|---|---|---|
| yes/no with an observed label | Logistic Regression, then Random Forest | readable → stronger |
| "which first?" ranking | any classifier's probability, evaluated at precision@K | ranking needs scores, not labels |
| grouping items | K-Means (pick k with silhouette), then NAME clusters after inspecting them | unsupervised needs human naming |
| "what drives X?" | simple model + permutation importance | importance from a fit, checked by shuffling |

Simplicity is a feature: a depth-2 decision tree you can print and read teaches more than an
opaque model 2 points stronger. Add complexity only when the comparison earns it.

## The comparison table (non-negotiable)

One table, at the end: baseline vs model(s), same split, same metric(s), plus the base rate.
If the model wins at precision@50 but loses at precision@20 — report both; that IS the finding.

## Read the errors

A metric without error analysis is decoration. After training:
- Where is the model most wrong? (which groups, which value ranges)
- What does it lean on? (feature importances — then sanity-check: does the top feature make
  sense, or is it suspiciously perfect? Suspiciously perfect = probably leakage.)
- Show 3 concrete wrong cases and say why they're hard.

## Reproducibility basics

Fix random seeds and say so. Note library versions if a headline number matters — tree-ensemble
results can shift a few points between versions, which is normal and worth one sentence.

## How to verify

- The baseline appears in the same table as the model, computed in the same notebook run.
- You can name the top 3 features and explain why each plausibly relates to the outcome.
- Rerunning the notebook reproduces the table (same seeds → same numbers).
