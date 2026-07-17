---
name: writing-honest-claims
description: Writes findings in language the evidence can carry — the claim ladder (observed → directional → decision-support, never causal without a design), effect sizes over drama, banned phrasings. Use when writing any conclusion, report section, playbook, or public page from analysis results.
---

# Writing honest claims

A finding is a sentence plus the evidence that carries it. Most analysis goes wrong in the
sentence, not the math: the words claim more than the numbers showed.

## The claim ladder — match words to evidence

| Evidence you actually have | Words you may use |
|---|---|
| A pattern in this dataset, this period | "we **observed**…", "in this data…" |
| A measured comparison between groups | "X is **associated with** Y", "pages with A **showed** B" |
| A validated model that ranks/predicts out-of-sample | "the model **ranks/flags**… at precision@K of…" |
| A controlled experiment or matched design | only THEN: "X **causes/improves** Y" |

Cross-sectional data (one snapshot, no intervention) NEVER supports "doing X will produce Y."
The honest form is decision-support: "these pages look worth reviewing first, because…"

## Banned unless you ran the design for it

- "proves", "causes", "will increase", "the algorithm rewards…"
- "we predicted Google's algorithm" — no one did; you modeled outcomes in one portfolio
- any headline ratio from a tiny bucket (report n or drop it)
- accuracy without its base rate next to it

## Make numbers honest

- **Effect size over drama:** "3.2× higher (12% → 38%, n=1,240 vs n=890)" beats "MASSIVE boost".
- **Selection bias check:** if the "treated" group was CHOSEN (someone picked which pages to
  refresh), part of the gap is the choosing, not the treatment — say so in the same sentence.
- **Survivorship check:** filters like "active items only" silently drop the dead — name the
  filter when stating the finding.
- **Negative results are results.** "We expected X; the data shows no such pattern (details)"
  is a publishable, respect-earning sentence.

## Reviewing someone else's claims (or your own yesterday's)

Ask three questions of every bold sentence: Where does the label come from? What does the
validation design actually test? Would the number survive a grouped/time split? Frame findings
as "how to make it stronger", not "gotcha" — the goal is the next level of rigor, not a scalp.

## How to verify

- Read each conclusion sentence alone, out of context: does it say more than its table shows?
- Have your assistant play skeptic: "attack these claims — which words exceed the evidence?"
  Fix what survives the attack honestly.
