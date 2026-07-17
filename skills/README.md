# Skills — the router

This folder is a small library of **skills**: focused instruction files your AI assistant loads
one at a time. One skill per task keeps the assistant sharp — its context window is small, and
filling it with everything makes it worse at the one thing you need.

**How to use it (repo-reading agents — Claude Code, Cursor, Codex):** they find this file
automatically via `AGENTS.md` / `CLAUDE.md`. Just tell your assistant which task you're doing.

**Using a chat-only assistant (ChatGPT / Gemini in a browser)?** Open the skill file on GitHub,
copy its whole content, and paste it into your chat before asking for help. That's it.

## The table — find your task, load ONE skill

| Your task | Load this skill | Also load for data work |
|---|---|---|
| Any task — how to work with your assistant at all | `directing-your-ai-assistant/SKILL.md` | — |
| Pick a lane, frame your question (ML-02, ML-03) | `framing-ml-problems/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Write + verify the data contract (ML-04) | `writing-data-contracts/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Query the big warehouse without downloading it (ML-04/05, capstone) | `querying-big-datasets/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| EDA + signal tests with verdicts (ML-06) | `auditing-signals/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Build the rule baseline + ranked queue (ML-07) | `building-baselines/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Train and compare the model (ML-08) | `training-honest-models/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Hunt leakage; validate honestly (ML-05, ML-09) | `hunting-leakage-and-validating/SKILL.md` | `flyrank/flyrank-data/SKILL.md` |
| Write claims that hold (ML-09, ML-10, the paper) | `writing-honest-claims/SKILL.md` | — |
| Write the research paper (ML-11, W7) | `writing-research-papers/SKILL.md` | — |
| Deploy the paper as a page (ML-11) | `deploying-static-pages/SKILL.md` | — |
| Understand FlyRank + the problem (background) | `flyrank/flyrank-context/SKILL.md` | — |

## Reuse this on your next project

Every skill outside `flyrank/` is **general** — take this whole folder to any future project.
Delete `skills/flyrank/` and the flyrank column above, and everything else still works.
