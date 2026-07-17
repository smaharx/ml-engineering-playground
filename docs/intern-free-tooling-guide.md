# Free Tooling Guide For Interns

Status: recommended defaults, not restrictions.

Verified: 2026-06-26, using official pricing/docs pages where possible. InternHQ board content was used only as a discovery aid; specific claims below are based on official vendor pages or are worded conservatively.

You can use any tools you want. This list is the recommended zero-budget stack because it covers the internship work without requiring a paid plan.

## Ground Rules

- Do not pay for tools unless a mentor explicitly says there is no free path.
- Use only approved/anonymized internship data in external AI tools.
- Do not paste client names, domains, raw URLs, raw queries, credentials, or private BigQuery details into any third-party tool.
- Treat every cloud AI tool and free API as third-party processing. If the data is not in the approved internship release, do not upload it.
- Free limits change. If a limit blocks you, switch to another free option or spread work across days.
- When a tool asks for billing, skip it unless the free tier is still usable without adding payment.

## Best Default Stack

| Need | Recommended default | Good alternatives | Notes |
|---|---|---|---|
| Code editor | [VS Code](https://code.visualstudio.com/docs/supporting/faq) | [Cursor Hobby](https://cursor.com/pricing) | VS Code is free for private and commercial use. Cursor Hobby is free with limited Agent requests and Tab completions. |
| Git + repo | [GitHub Free](https://docs.github.com/en/get-started/learning-about-github/githubs-plans) | GitLab Free | GitHub Free supports unlimited public/private repos with limits on some advanced features. |
| Main AI assistant | [Claude Free](https://claude.com/pricing) | ChatGPT Free, Gemini app | Good for explanation, critique, writing, and code review. Free usage is limited. |
| Cross-check model | [ChatGPT Free](https://chatgpt.com/pricing/) or Gemini | Claude Free | Use a second model to challenge assumptions and catch weak reasoning. |
| Free model API | [Gemini API free tier](https://ai.google.dev/gemini-api/docs/pricing) | [Groq free API limits](https://console.groq.com/docs/rate-limits) | Use for programmatic model calls. Gemini/Groq limits are model/account dependent. Do not send private data. |
| Coding agent | [Gemini CLI](https://github.com/google-gemini/gemini-cli) | [GitHub Copilot Free](https://github.com/features/copilot/plans) | Gemini CLI is a strong no-cost default; Copilot Free is useful inside the editor. |
| Python notebooks | Local Jupyter or [Google Colab](https://research.google.com/colaboratory/faq.html) | Kaggle notebooks if your account quota allows | Colab is free but has dynamic limits and no guaranteed GPU. |
| Data work | [pandas](https://pandas.pydata.org/docs/getting_started/index.html), [scikit-learn](https://scikit-learn.org/stable/user_guide.html) | Polars, DuckDB | pandas + scikit-learn are enough for the capstone baseline/modeling work. |
| Open/local models | [Ollama](https://ollama.com/), [LM Studio](https://lmstudio.ai/) | Hugging Face local downloads | Useful when you want local experiments with no API cost. |
| Model/demo hosting | [Hugging Face Spaces](https://huggingface.co/pricing) | Vercel/Netlify static demo | HF Spaces has free CPU Basic and ZeroGPU options with quota limits. |
| Database, optional | [Supabase Free](https://supabase.com/docs/guides/platform/free-project-pausing), [Neon Free](https://neon.com/pricing) | Local Postgres/DuckDB | Only needed if your project needs a database. Not required for notebook-only capstones. |
| Frontend/static deploy, optional | [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Netlify Free](https://www.netlify.com/pricing/) | GitHub Pages, HF Spaces | Use only if you need a public demo UI. Vercel Hobby is for personal/non-commercial use. |
| Eval harness, optional | [promptfoo](https://www.promptfoo.dev/docs/intro/) | Simple Python scripts + JSONL logs | Useful for prompt/model evals; not mandatory. |

## For The ML Track

Use this default path:

1. Work locally with Python, pandas, scikit-learn, and notebooks.
2. Use Colab only when your laptop cannot handle a run.
3. Use Gemini API for model calls only if your lane needs an LLM or embedding-style helper.
4. Use Groq or local Ollama/LM Studio for open-model experiments.
5. Use GitHub for version control and final submission.
6. Use Hugging Face Spaces or a simple static page only if your final demo needs a public UI.

Most ML capstones do not need a paid API, paid GPU, paid vector database, or paid deployment host.

## What Each Tool Is Best For

| Tool | Best use | Avoid using it for |
|---|---|---|
| Claude Free | Explaining concepts, reviewing claims, writing cleaner reports | Large repeated batch jobs |
| ChatGPT Free | Second opinion, code review, alternative framing | Assuming it is always available or unlimited |
| Gemini API | Free programmatic model calls | Uploading private/raw data |
| Gemini CLI | Code edits, repo questions, local workflow help | Treating output as reviewed code without testing |
| GitHub Copilot Free | Inline coding help and small agent tasks | Heavy agent work after limits are hit |
| Colab | Notebook execution when local setup is painful | Guaranteed long GPU jobs |
| pandas | Cleaning, joining, aggregating CSVs | Massive out-of-core jobs without chunking |
| scikit-learn | Baselines, trees, random forests, clustering, validation | Deep learning or huge neural training |
| Hugging Face | Model discovery, datasets, simple demos | Private data upload without approval |
| Supabase/Neon | Small Postgres/pgvector prototypes | Large warehouse-scale storage |
| [Vercel](https://vercel.com/docs/plans/hobby) / [Netlify](https://www.netlify.com/pricing/) / [Render](https://render.com/pricing) | Lightweight demos | Anything that needs guaranteed production uptime |

## Student Unlocks Worth Claiming

If you are currently enrolled as a student, check these before paying for anything:

- [GitHub Student Developer Pack](https://education.github.com/pack): often unlocks GitHub Pro/Copilot/student credits and partner benefits.
- [GitHub Copilot student access](https://github.com/features/copilot/plans): verified students can get the student plan.
- [Figma Education](https://help.figma.com/hc/en-us/articles/360041061214-Figma-for-Education): useful for UX/design interns.
- [Notion for Education](https://www.notion.com/help/notion-for-education): useful if you want a structured personal workspace.

These are optional. The internship should still be doable without student verification.

## Do Not Pay For

- ChatGPT Plus or Claude Pro just for this program.
- Claude Code or any paid coding-agent subscription.
- Paid model API credits before using Gemini API, Groq, or local models.
- GPU rentals before trying local CPU/small-model work and Colab.
- Paid vector databases; use local DuckDB/Postgres or Supabase/Neon free tiers.
- Paid hosting for a capstone demo unless every free demo path fails.
- Paid SEO suites. Use the provided internship data and public docs/tools.

## Minimal Setup Checklist

- GitHub account.
- Google account for Colab and Gemini API/AI Studio.
- VS Code or another editor.
- Python environment with pandas, scikit-learn, matplotlib/seaborn, and Jupyter.
- One primary AI assistant and one second model for cross-checking.
- The approved internship dataset release.

That is enough to complete the internship.
