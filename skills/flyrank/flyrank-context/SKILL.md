---
name: flyrank-context
description: FlyRank-specific background — what the company does, the search problem, and the hand-written flags story that the ML internship work builds on. Load for context when an assignment references FlyRank's product, flags, or the "beat the rule" framing. (Project-specific: delete this folder when reusing the skill library elsewhere.)
---

# FlyRank context

**What FlyRank is.** FlyRank builds content as infrastructure: it researches, writes, publishes
content straight into a client's website, then watches search data and optimizes — the full
cycle, run by algorithms and AI rather than people doing it by hand.

**The problem this internship works on.** Content that gets found in Google search ranks, then
quietly decays: rankings slip, clicks drop, and most teams notice too late. The valuable
decision is: *out of thousands of pages, which one should a human fix FIRST?* That is a ranking
problem on messy, real search data — exactly where a learned model can beat a fixed rule.

**The flags story (why "beat the rule" is the framing).** FlyRank's product already flags pages
today — a health score, quick-win tags, needs-attention flags. These are hand-written rules:
if-this-then-that, thresholds chosen by hand. They work, and they run in production. But rules
run out where signals get many, tangled, and shifting — and no trained model has replaced them
yet. The intern capstone lives exactly in that gap.

**Two things this means for your work:**
1. **Product flags are outputs, never inputs.** health_score and friends encode a decision
   someone already made. Use them as a baseline to beat — never as model features (that's a
   circular result; see the leakage skill).
2. **Honest language is house culture.** FlyRank publishes findings as observed / measured /
   directional / decision-support — never "we predicted Google's algorithm." Your work follows
   the same claim discipline.

**The data provenance in one line.** Google Search Console + Google Analytics land in BigQuery,
sync daily, aggregate into warehouse tables, and ship to interns as a pseudonymized public-safe
release (details in the flyrank-data skill).

## How to verify you have the context

You can answer, in one sentence each: what FlyRank sells, what decision the capstone improves,
why product flags can't be features, and which four words describe allowed claim language.
