# Macallan Page Builder

Builds conversion-focused landing pages and full websites for healthcare practices: the Macallan block library, distinctive on-brand design delivered as one plain HTML file (no build tools or installs), every word at a 5th-grade reading level, and an independent QA review (copy, compliance, design, mobile, ADA) before anything is delivered.

## For the team: how to make a page

1. In Claude, start a new chat and type **`/create-page`**, plus a short note. Example:
   > /create-page Landing page for Regional Healthcare example, knee pain patients in Austin. Logo attached. Their site is Regionalhealthcareexample.com.
2. Answer the questions Claude asks (click an option or type your own). About a minute.
3. Claude writes the content, designs the page, reviews it, and fixes what the review finds. You get:
   - the page itself, shown right in the chat (plus a preview link when available), with a first draft sent while QA runs
   - the QA report
   - the list of `[placeholders]` the practice still needs to fill
   - for landing pages: the pre-launch compliance checklist and matching ad headlines

No `/create-page`? Paste this instead: *"Use the page builder at **REPO_URL** and build a landing page for ..."*

Keep patient information out of the chat. Pages contain practice marketing content only.

## How it works

`/create-page` is a small loader skill. It downloads the **latest published release** of this repository and follows `START-HERE.md`, which runs a relay of three agents:

| Agent | Job |
|---|---|
| page-content | Block plan and every word (`content.json`), grade 5, compliance wording |
| page-designer | Design and write the single-file `index.html`; never changes the words |
| page-qa | Independent review; never edits; findings go back to whoever owns them |

## What's in here

| Path | What it is |
|---|---|
| `START-HERE.md` | The orchestrator: intake questions, the relay, delivery, versioning |
| `rules/` | Materials, block plan, copy, design and build, QA standards |
| `agents/` | The three agent roles (also in `.claude/agents/` for Claude Code) |
| `blocks/` | The 47 original block HTML files (structure reference) |
| `scripts/` | Reading level checker, brand color generator, logo prep (`logo.py`), plan wireframe (`wireframe.py`), automated QA (incl. ADA and the logo check), bundled axe-core in `scripts/vendor/` |
| `templates/page.html` | Starter single-file page: design tokens, skip link, focus styles, small accessible JS |
| `VERSION`, `CHANGELOG.md` | Current version and history |

## For maintainers: updating the kit

1. Edit the files. Bump the version using `START-HERE.md` section 9 (patch for small fixes, minor for additions, major for changes to how it works).
2. Update `VERSION` and the version line in `START-HERE.md`, and add a line at the top of `CHANGELOG.md`.
3. Publish a GitHub release tagged `vX.Y.Z` (for example `v6.0.1`). The loader only uses published release tags, so unreleased edits never reach the team.
4. Only maintainers can push to this repository or publish releases. Whoever controls it controls what Claude does for the whole team.

**Never commit client work, client materials or anything with patient information.** This repository is public.

## Claude Code

Open Claude Code in this repository: `CLAUDE.md`, the three named agents in `.claude/agents/` and the kit load automatically. Ask for a page and Claude follows `START-HERE.md`.
