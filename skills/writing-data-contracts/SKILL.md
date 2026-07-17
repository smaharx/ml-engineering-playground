---
name: writing-data-contracts
description: Writes a data contract — what a row means, which fields are features vs labels vs context vs excluded, over which time windows — and verifies every claim with a query. Use before any feature building or modeling, or when results look wrong and the data definition is suspect.
---

# Writing data contracts

Most weak analysis fails here, before any model: nobody wrote down what a row means. A data
contract is that write-down — and a contract your code has checked, not just stated.

## The contract, section by section

1. **Unit of analysis.** One row = one WHAT? (a page? a page-day? a client?) State it.
2. **Time window.** Which dates does each field cover? Draw the windows if they differ.
3. **Field classification.** Every field you may touch goes in exactly one bucket:
   - **Feature** — knowable BEFORE the moment you predict, safe to use.
   - **Label / proxy** — the thing you predict, or what it is computed from. Never a feature.
   - **Context** — for grouping, joining, splitting, reading — never for the model to learn from
     (IDs live here).
   - **Excluded** — private, product-decision flags, or future information. Each gets a one-line why.
4. **Missing values.** Which fields go blank, how often, and is the missingness random or does it
   follow a pattern (it usually follows a pattern — check by category).
5. **Output.** What the analysis hands to the human, in one sentence.

## Verify every claim with a query

A contract line without a query next to it is a guess. For each claim, write the check:

- Grain: `SELECT unit_columns, COUNT(*) c FROM t GROUP BY unit_columns HAVING c > 1 LIMIT 5`
  — zero rows back means the grain holds.
- Counts: total rows, rows per group, rows in your window. Compare to what the docs promised.
- Missingness: `AVG(CASE WHEN col IS NULL THEN 1.0 ELSE 0 END)` per column — and again grouped
  by category, to catch patterned gaps.
- Windows: `MIN(date), MAX(date)` — per group too, because histories rarely start together.

## Traps that look innocent

- Two tables with the same column name but different windows — align windows BEFORE joining.
- Per-item context columns repeated on every row of a detail table: read them with a
  first/any-value, never SUM them (double counting).
- A "complete" table that only accrues from each item's registration day — earlier history is
  absent, not zero.

## How to verify

- Every contract section has at least one executed query cell under it, and the query output
  matches the sentence above it.
- Someone who has never seen the data could read your contract and predict the row count within
  a few percent. If they couldn't, the contract is still too vague.
