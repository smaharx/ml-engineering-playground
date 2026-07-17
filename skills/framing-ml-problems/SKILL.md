---
name: framing-ml-problems
description: Frames a data/ML problem before any modeling — the decision, the action, the cost of a wrong call, task type, target, and success metric. Use when picking a project direction, writing a research question, or mapping a problem onto an ML task type.
---

# Framing ML problems

A model is never the goal. A better DECISION is the goal. Frame first, model later.

## The four questions (answer all four, in writing)

1. **What decision does this improve?** Not "predict X" — decisions. "Which page should an
   editor fix first?" is a decision. "Predict decline" is not, yet.
2. **Who acts on the output, and what do they do?** Name the person and the action. If nobody
   would act differently, the work has no customer.
3. **What does a wrong answer cost?** Wasted editor hours? A missed decline? The cost of errors
   decides how careful the method must be, and which errors matter more.
4. **Why does data or ML help at all?** Sometimes a plain rule (an if-statement) is the right
   answer. Sometimes a dashboard is. ML earns its place only when the pattern is real but too
   messy to write by hand — many signals, tangled, shifting over time.

## Map it to a task type

| If your question sounds like… | Task type | Target | Typical metric |
|---|---|---|---|
| "Which ones first?" | Ranking / scoring | a priority score | precision@K |
| "Will this one decline / recover?" | Classification | a yes/no label from an OBSERVED outcome | ROC-AUC, precision/recall vs base rate |
| "What kinds of items exist?" | Clustering | none (unsupervised) | silhouette + human sense-check |
| "Which signals travel together?" | Signal analysis | none | effect sizes, grouped comparisons |

Two rules that save whole projects:

- **The target must be observed, not defined.** A label that comes from someone's rule means your
  model learns the rule, not the world. Prefer outcomes measured in a later time window.
- **Name the metric before training.** "Good" defined after the fact always looks good.

## Write the one-paragraph frame

> For [who], deciding [what], we will build [output type] from [data], predicting/scoring
> [target] measured by [metric]. A wrong call costs [cost]. A plain rule isn't enough because
> [why]. We will claim only [observed / directional / decision-support] results.

If you can fill that paragraph honestly, you are framed. If a blank stays blank, that blank IS
your next task.

## How to verify

- Show your frame to someone (or your assistant) and ask: "what decision does this improve?"
  If their answer differs from yours, the frame isn't done.
- Check the target: is it observed in the data, or defined by a rule? If defined — reframe.
- Check the metric exists in your data. Can you compute it today, on a baseline? Do it.
