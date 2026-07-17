---
name: deploying-static-pages
description: Deploys a static page (research paper, portfolio piece) for free from a GitHub repo using GitHub Pages — setup, file layout, verification, and recording the final URL. Use when publishing a finished write-up as a public web page.
---

# Deploying static pages

Your repo can BE your website. GitHub Pages serves files from your repo at a public URL — free,
no new accounts, done in ten minutes.

## The steps

1. **Make the page.** Simplest: a single `index.html` in a `docs/` folder of your repo (a
   `paper/` exported to HTML also works — the folder just has to contain `index.html`).
   Keep assets (images, css) in the same folder with RELATIVE paths (`img/chart1.png`,
   not `/Users/you/...`).
2. **Turn Pages on.** Repo → Settings → Pages → "Deploy from a branch" → Branch: `main`,
   Folder: `/docs` → Save.
3. **Wait ~1-2 minutes**, then open: `https://<your-username>.github.io/<repo-name>/`
   (Settings → Pages shows the exact URL once it's live).
4. **Verify like a stranger:** open the URL in a private/incognito window AND on your phone.
   Broken images = absolute paths; fix them to relative.
5. **Record the exact final URL** wherever your project requires it — in this repo that is
   one line in `submission/paper_url.txt` (nothing else in the file).

## Notebook → page, two easy routes

- Write the paper as HTML/markdown directly (cleanest control of layout), or
- Export a notebook: `jupyter nbconvert --to html capstone.ipynb`, rename to `index.html`,
  put it in `docs/` — then still write a proper abstract at the top.

## Gotchas

- Pages serves your PUBLIC repo — one last scan that no private data, tokens, or client names
  appear anywhere in the served folder.
- Changes deploy on push, with a 1-2 minute delay; hard-refresh (Cmd/Ctrl+Shift+R) before
  concluding something is broken.
- Your own domain works too (Settings → Pages → Custom domain) — nice for portfolios, optional.

## How to verify

- The URL loads in incognito on desktop AND phone; every image renders; every link works.
- `submission/paper_url.txt` contains exactly that URL, one line, starts with `https://`.
- Push a small edit and confirm it appears at the URL within minutes — now you trust the loop.
