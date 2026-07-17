---
name: directing-your-ai-assistant
description: Teaches the working method for using an AI coding assistant on analysis tasks — one task per fresh conversation, search before assuming, interview before big plans, validate everything, commit per finished task. Use at the start of any assignment, whenever a conversation gets long and confused, or when the assistant starts guessing.
---

# Directing your AI assistant

You are the engineer. The assistant is a fast, tireless drafter. This skill is how you stay in
charge — because an assistant with a confused human produces confused work, fast.

## The six rules

**1. One task, one fresh conversation.** An assistant's memory (its "context window") fills up
and its quality drops as it fills. So: finish one assignment section per conversation, then start
a new one. Never drag one giant chat across a whole week — old confusion bleeds into new work.

**2. Load only what the task needs.** Point it at the router (`skills/README.md`), load the one
skill for this task, and stop. More instructions ≠ better output — past a point, more is worse.

**3. Search before assuming.** Before the assistant writes anything, make it look: "Search this
repo first — don't assume something is missing or not implemented." Assistants invent functions
and columns when they haven't looked. Anchoring them in real files kills most hallucinations.

**4. Interview before big plans.** For anything bigger than one cell, say: "Before you write
code, interview me — ask the questions you need answered." Wrong assumptions caught in questions
cost seconds; caught in finished code they cost hours. Do not outsource the thinking.

**5. You validate — always.** The assistant drafts; you check. Every task ends the same way:
run the notebook top to bottom (Runtime → Run all), read the output, and ask "does this actually
answer my question?" An unverified answer is not an answer. Checks are your safety rail: the more
things that can automatically reject bad output (a rerun, an assertion, CI), the safer you move.

**6. Commit each finished task.** When a section works, commit it with a message that says what
and why. Small commits = easy recovery when something later goes wrong.

## Prompts that work (copy these)

- "Read `skills/README.md`, then load `<skill>` for this task."
- "Search the repo first — don't assume it's not implemented. Then propose a plan before coding."
- "Interview me before writing this: what do you need to know?"
- "Write this cell, then tell me exactly how I verify it worked."
- "Here is the error output, unedited: <paste>. Fix the actual cause, not the symptom."

Paste real errors whole — don't summarize them. The assistant fixes what it can see.

## How to verify you're using this skill right

- Your conversations are short and single-purpose; you can name each one's task in five words.
- The assistant asked you at least one clarifying question before any multi-step work.
- Every finished section ran top to bottom before you committed it.
- You can explain, in your own words, everything you committed. If you can't — that's the signal
  to slow down: core idea first, AI second.
