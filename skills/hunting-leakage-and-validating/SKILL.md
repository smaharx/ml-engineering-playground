---
name: hunting-leakage-and-validating
description: Finds label leakage and designs honest validation — leakage taxonomy, grouped and time-aware splits, base rates, and the attack-your-own-model checklist. Use before trusting any metric, when a score looks too good, or when features and labels share time windows or origins.
---

# Hunting leakage and validating

The sneakiest failure in applied ML: the model quietly reads the answer during training. Scores
look amazing; the work is worthless. Your job is to attack your own model before anyone else can.

## The leakage taxonomy — three ways answers sneak in

**1. Label-derived features.** The label was computed FROM a column, and that column (or its
sibling) is in the features. Symptom: one feature towers over all others, and the score is
near-perfect. Test: train once WITH the suspect, once WITHOUT — a collapse from ~1.0 to ~0.7
is the confession.

**2. Future/overlapping windows.** A feature summed over a window that CONTAINS the label's
window already knows the outcome. Draw the timeline: every feature must be knowable at the
moment of prediction, labels strictly after. If a 90-day aggregate overlaps your last-30-day
label — only the earlier sub-window is a legal feature.

**3. Decision-derived features (product flags).** Scores and flags produced by an existing
system encode a decision someone already made. Using them as features means learning the old
rule, not the world — a circular result. They may serve as a BASELINE to beat, never as inputs.

## Honest splits — random is rarely honest

- **Grouped split** (GroupKFold by the entity that repeats — client, site, user): rows from one
  group share hidden character; a random split lets the model memorize the group and fake skill.
  The honest question is "does it work on a group it never saw?"
- **Time split** (train on the past, test on the future): the only split that mimics deployment
  for anything trend-like.
- Report the random-split number next to the honest-split number if you like — the GAP between
  them is itself a finding about how much memorization was happening.

## Always print the base rate

Accuracy of 71% on a label that is 62% positive is 9 points of skill, not 71. Every score sits
next to its naive baseline (majority class / random ranking), always.

## Sealed holdouts leave receipts

If you claim a sealed or holdout evaluation ("touched once, blind"), commit the receipts: the
cell or script that builds the sealed frame, AND the metrics file it produced. A sealed claim
that can only be verified by digging through git history isn't sealed — it's trusted. And
check your population definition for future information: if the rows you keep depend on
anything from the outcome window (e.g. "clients still active in the label month"), say so in
your limitations — it's a choice, not a crime, but hiding it is.

## The attack checklist (run it before you believe anything)

- [ ] Timeline drawn: all features strictly before the label window
- [ ] No label-derived or sibling columns in the features (train-without test on suspects)
- [ ] No product flags / existing-system scores as features
- [ ] Population selection checked for outcome-window information (and disclosed if used)
- [ ] Split grouped by the repeating entity (and/or time-based)
- [ ] Base rate printed next to every metric
- [ ] Top feature importance sanity-checked — "too good" investigated, not celebrated
- [ ] Metrics recomputed out-of-fold, never in-sample
- [ ] Sealed/holdout claims: the frame-builder and the resulting metrics file are committed

## How to verify

- Deliberately ADD a leaky feature and watch the score jump toward 1.0 — if it doesn't, your
  test harness itself is broken. Then remove it and keep the honest number.
- Swap your random split for a grouped split and report both numbers. If you can't explain the
  gap, you're not done.
