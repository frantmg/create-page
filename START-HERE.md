# Macallan Page Builder: START HERE

You are reading the page builder kit. If the user asked for a page and you were sent here (by the `/create-page` loader skill, a pasted repo link, or Claude Code opened in this repo), you are the **orchestrator**: follow this file from section 0.

**Kit version 7.0.0** (see `VERSION` and `CHANGELOG.md`)

Builds landing pages and website pages for healthcare practices (home, specialty, condition, location, provider, about, insurance, testimonials, contact). Pages are assembled in seconds from the engine's designed blocks (`engine/`: vetted, accessible block markup and CSS, art-direction themes, brand tokens) and art-directed with the `frontend-design` approach (a distinct visual identity per practice, no generic AI look), built as one plain HTML file on Material Design logic (no build tools or installs), and written at a 5th-grade reading level, because plain copy converts best.

This kit runs as a relay: the **orchestrator** (you, in the user's conversation) runs the intake and the relay, the **page-content** agent writes the plan and every word (only when the user asks for written content; otherwise the page uses placeholder text), the **page-designer** agent designs and builds, and the **page-qa** agent reviews independently. Section 0 says who does what. Do not skip the intake gate. Agents never read this file: each reads `agents/shared.md` and its own role file.

0. How this runs (roles, brief, who writes the content, timing, the relay, fix routing, the tweak round)
1. Intake (gate)
2. Read the materials
3. Plan the page: pick the blocks
4. Write the copy at grade 5
5. Design and build (art direction, single-file HTML)
6. QA and review
7. Deliver

---


## File map

Section numbers used anywhere in this kit point to these files:

| Section | File |
|---|---|
| 0, 1, 7, 9 (0.7 tweak round) | `START-HERE.md` (this file, the orchestrator's) |
| 2 | `rules/materials.md` |
| 3 (3.1 to 3.4) | `rules/blocks-and-plan.md` |
| 4 (4.1 content files) | `rules/copy.md` |
| 5 (5.1 to 5.10) | `rules/design-build.md` |
| 6 (6.1 to 6.3) | `rules/qa.md` |
| 8.1 / 8.2 / 8.3 | `scripts/readability.py` / `scripts/m3_scheme.py` / `scripts/qa.py` |
| 8.5 | `scripts/logo.py` (trims, resizes and embeds the logo; reports light or dark and its main color) |
| 8.4 | `templates/page.html` (copy it to `<work>/index.html`) |
| 8.6 | `scripts/wireframe.py` (stacks the planned blocks from `blocks/` into `<work>/wireframe.html` for plan approval) |
| 8.7 | `scripts/tweakbar.py` + `templates/tweakbar.html` (makes `<work>/tweak.html`: the page with a tweak bar, for the tweak round in 0.7) |
| 8.8 | `scripts/timing.py` (records each stage's start and end in `<work>/timing.md`, 0.5) |
| 8.9 | `scripts/blocks_lite.py` (rebuilds `blocks-lite/` from `blocks/`; run it after changing a block) |
| 8.10 | `scripts/apply_tweaks.py` (writes the mechanical part of a `tweaks.json` into `index.html` in seconds, 0.7) |
| 8.11 | `scripts/tweakserve.py` (serves the tweak page locally so Send to Claude hands the changes straight back, 0.7) |
| 8.12 | `scripts/assemble.py` + `engine/` (builds the page from `build.json` in about a second, 0.6 step 4) |
| 8.13 | `scripts/engine_check.py` (assembles every engine block in every theme and runs qa.py; run after changing the engine) |
| axe-core | `scripts/vendor/axe.min.js` (bundled, with its `LICENSE`) |
| Blocks | `blocks-lite/<ID>-*.html`: structure and content slots, about 1 to 2 KB each (read these). `blocks/<ID>-*.html`: the visual demos, for the wireframe and for looking at a layout only; never their styling |
| Agent roles | `agents/shared.md` (read by every agent) plus `agents/content.md`, `agents/designer.md`, `agents/qa.md` (each agent's full instructions; also in `.claude/agents/`) |

Run scripts from the kit, for example `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --brand-fonts "Brand Font"`. Never edit the kit while building a page; client work goes in the work folder.

---

## 0. How this runs

### 0.1 Roles

The page is made by a relay: content first, then design, then an independent review. Each agent owns its lane and never edits another's work.

| Role | Who | Owns | Hands off | Never |
|---|---|---|---|---|
| Orchestrator | The main conversation (when the user runs `/create-page` or asks for a page) | Section 1 intake, the brief, stage timing (0.5), running the relay and fix routing (0.6), delivery (section 7); the block plan when the page uses placeholder content (0.3) | Brief (and `plan.md`) to page-content or page-designer | Writes copy or builds the page when the agents are available |
| page-content | Agent (`page-content`), started only when the user asked for written content (0.3) | Sections 2 (facts, compliance, current site, benchmark), 3 and 4: block plan, every word, compliance wording, placeholders | `content/plan.md` + `content/content.json` | Touches layout, styles or code |
| page-designer | Agent (`page-designer`) | Sections 2 (brand, logo, current site look), 5 and 6.1: design plan, build, mobile, ADA build quality | `<work>/index.html` | Changes any word; it sends a copy change request instead |
| page-qa | Agent (`page-qa`), fresh for every review | Section 6 in full | QA report | Edits anything, sees the other agents' notes |

If you were started by the user (or by `/create-page`), you are the orchestrator. If your prompt says you are page-content, page-designer or page-qa, stop reading this file: follow `agents/shared.md` and your role file in `agents/`.

### 0.2 The brief

After the intake, create a new work folder (`<page-slug>/` in the working directory). **Before writing the brief, gather the materials into `<work>/materials/`:**

- Copy every file the user attached (logo, brand guide, compliance documents, photos) into `<work>/materials/`, keeping the file names. Agents only see what is in this folder, so never just mention an attachment in the brief.
- **Logo:** if the user did not attach one but the practice has a current website, get it from there: find the logo in the site header (an `<img>` src, an inline `<svg>`, or as a last resort the `apple-touch-icon` or `og:image`), download it with `curl -L -o <work>/materials/logo.<ext> <url>` (save inline SVG markup as `logo.svg`), and check that the file is really the logo. Write `Logo: none` only when there truly is no logo anywhere.

Then write `<work>/brief.md`. It is the only thing the relay starts from, so it must be complete:

```markdown
# Brief: <practice> <page type>
- Page type: ...            - Conversion mode: yes/no
- Audience: ... (default: new patients)  - Main action (CTA words): ...   - Second action: ... or none
- Message 1: ...            - Message 2: ...                 - Message 3: ...
- Keyword: ...  - Traffic: ...  - Lead flow: ...  - Proof available: ...   (conversion mode)
- Plan approval: approved plan below / build directly
- Review mode: quick draft (automated checks only; the default) / full review (when the user asked for it)
- Content: written / placeholder (lorem ipsum, `rules/copy.md` 4.2)
- Brand fonts: ... or none given
- Logo: <absolute path in <work>/materials/> (attached / from the current website) or none
- Other materials (absolute paths in <work>/materials/): brand guide ..., compliance docs ..., photos ... (or none)
- Current website: URL or none        - Benchmark website: URL or none
- Practice facts given by the user: name, phone, locations, hours, providers, insurance, reviews
- Approved block plan (if the user approved one): ...
- Work folder: <absolute path>
```

### 0.3 Who writes the content

The intake asks (Round 1, "Content") whether to write the page's words.

- **Written content** (the user asked for it): start the **page-content** agent with the brief path; it uses the engine's slot names for engine blocks (`rules/copy.md` 4.1). It does the content parts of section 2, the block plan (section 3) and every word (section 4), writes `<work>/content/plan.md` and `<work>/content/content.json` (4.1), runs `readability.py`, and returns `CONTENT REPORT`. It also handles every later content change: copy change requests (`CONTENT FIX REPORT`) and tweak-round text (`CONTENT TWEAK REPORT`). Continue the same agent with SendMessage when you can, so it keeps its context. The orchestrator never writes copy.
- **Placeholder content** (the default unless the user asks for words): page-content is not started. The orchestrator writes only `plan.md` (block plan from 3.2 and 3.3 for the page type and goal, preferring the engine blocks: LP (landing header and footer), M01-A, M01-B, M05-A, M05-B, M09, M10, M11-A, M25, M26-A, M28-A, M28-B, M29, M31) and the designer fills every slot with lorem ipsum as in `rules/copy.md` 4.2. No `content.json`, no `readability.py`. If the user later asks for real words, start page-content then; the designer swaps the text in with targeted edits.

Record the choice as `Content: written / placeholder` in the brief. "Content owner" in this kit means page-content.

### 0.4 The agents' instructions

Each agent's full mode (inputs, what to do, report format, fix and tweak rounds) is in its role file: `agents/content.md`, `agents/designer.md`, `agents/qa.md`, plus the short shared section in `agents/shared.md`. Agents read only those files and the rules their role file lists, never this file. Their reports: `CONTENT REPORT` / `CONTENT FIX REPORT` / `CONTENT TWEAK REPORT`, `DESIGN REPORT` / `TWEAK SUPPORT REPORT` / `DESIGN FIX REPORT` / `DESIGN TWEAK REPORT` (with `COPY CHANGE REQUEST`s), and the QA report in `rules/qa.md` 6.3.

### 0.5 Stage timing

Record the start and end of every stage so the real bottleneck shows: `python3 <kit>/scripts/timing.py <work> start <stage>` and `... end <stage>`, with the stages `intake`, `wireframe`, `content`, `design`, `qa`, `fixes`, `tweak` and `deliver` (repeat runs are numbered automatically). The intake starts before the work folder exists: note `date -Iseconds` when you start it and record it later with `--at`. Each call rewrites `<work>/timing.md` (one row per stage run, totals per stage, the total time and the slowest stage). `timing.py <work> report` prints it for the final summary (section 7).

### 0.6 Orchestration: the relay

Time every step (0.5). The user sees the page as early as possible: right after the build, on the tweak page; everything else runs in the background while they look.

1. **Intake** (section 1). Only if the user asked to approve the plan first: get `plan.md` (from page-content, told to return only `plan.md`, for written content; or write it yourself for placeholder content), run `python3 <kit>/scripts/wireframe.py <work>/content/plan.md --title "<Practice> <page type>"`, send `<work>/wireframe.html` (section 7) with the short plan list, and ask (Approve plan · Change something). Record the approved plan in the brief.
2. **Brief:** write `brief.md` (0.2), with the review mode (quick draft unless the user asked for a full review) and the content choice (0.3).
3. **Content:** only if the user asked for written content, start `page-content` with the brief path and wait for its `CONTENT REPORT`; if `BRIEF INCOMPLETE`, ask the user and restart. With placeholder content, write only `plan.md` and go straight to design.
4. **Build: engine (default) or classic.**
   - **Engine:** make the creative decisions yourself (below), write them to `<work>/build.json` and run `python3 <kit>/scripts/assemble.py <work>/build.json`. In about a second it writes `index.html` from the engine's designed blocks plus `alternates.html` and `tweak-options.json` (tweak support is ready, nothing more to build). If its `needs_designer` list is not empty (blocks not in the engine yet), start page-designer to build only those blocks with targeted edits before you show the page; if more than 2 blocks are missing, use classic mode instead.
   - **Classic** (the user said "classic build", or the page needs mostly blocks outside the engine, such as a website page with the G1/G3 header and footer): start `page-designer` with the brief path and the content files; it hand-builds `index.html` and returns `DESIGN REPORT`. Copy change requests go to page-content (at most 2 round trips). Then the tweak support files come in the background (step 6).
   - **Creative decisions for `build.json`** (they carry the art direction, so take them seriously; `rules/design-build.md` 5.11):
     - `theme`: the look that fits the practice; read each `engine/themes/*.json` description (editorial: energetic, specialty and sports; clinical: calm, trusted, primary care, dental).
     - `seed`: the brand colour. Brand guide first, then the logo's main colour (`scripts/logo.py` reports it), then the current website's main colour.
     - `fonts`: the brand fonts when the brief names them (`{"display": "...", "body": "..."}`); otherwise leave it out and the theme's pairing is used.
     - `ornament` (contour, arcs, dots, none), `cta_shape` (leaf, pill, soft, square) and `media_shape` (cut, round, soft, square): choose them so this practice does not look like the last one (organic and athletic: leaf and cut; surgical and precise: square; family and friendly: pill and round).
     - `logo` (the `.datauri.txt` from `scripts/logo.py`) and `logo_tone` (its light or dark); `photos` by block ID when the user gave photos; `practice`, `phone`, `cta_primary`, `cta_secondary`; `content` (placeholder or written); `brand_locked` from the brief.
     - Optional `extra_css`: a small signature for this practice (`<work>/signature.css`, at most about 40 lines, theme and colour variables only), for example a custom ornament or a distinct hero detail.
5. **Show it right away:** make and show the tweak page (0.7 steps 1 and 2) with the line "Here's your page. Change anything on the tweak page, then press Send to Claude, or Looks good to finish." Do not wait for anything else.
6. **In the background, at the same time** (start them as background agents; if the client cannot, start them right after showing the page):
   - **Tweak support (classic mode only; the engine already wrote it):** ask page-designer (the same agent if you can) for `alternates.html` and `tweak-options.json` (5.10). When it is done, rebuild `tweak.html` (the page has not changed, so the user's unsent changes are kept) and tell the user in one line: "More block versions and palettes are ready: refresh the tweak page." (Chat: republish the same tweak artifact.)
   - **QA, only in full review mode:** start a **fresh** `page-qa` with only the preview path, the brief path, the material paths and the automated results path (`<work>/qa/auto.json`, the designer's full qa.py run, which page-qa reuses while the page is unchanged). Never pass the other agents' reports or notes. **Hold its findings:** never change `index.html` while the user is tweaking (it would reset their unsent changes). Tell the user in one line how many findings there are and that they will be fixed with their changes.
7. **When the user sends changes or says it looks good** (0.7): apply the tweaks first, then the held QA findings that still apply (findings on removed or replaced blocks are dropped). Route findings by owner:
   - **page-content:** area A (copy, brief, reading level, CTA words), area B wording (claims, disclaimers, placeholders, form note), area F order and plan. On a placeholder page there are no copy findings; plan findings are yours to fix in `plan.md`.
   - **page-designer:** areas C (design quality), D (mobile), E (ADA), area B items that are build issues (tracking scripts, form markup, legal links missing from the footer layout).
   - A finding that needs both goes to page-content first. Minor and mechanical findings (6.3) are fixed directly and not re-reviewed. **Fixes are edits, not rebuilds:** the designer changes only what the findings name, with targeted edits, and finishes with one full qa.py run to `<work>/qa/auto.json`.
8. **Re-review, only for blockers:** if QA had blocker findings, start a **new** page-qa with the preview, brief, material and automated results paths plus the blockers and judgment majors. It re-checks only those plus the automated results. With no blockers there is no re-review. **Default is 1 fix round**; a second only if blockers remain; remaining majors are reported at delivery.
9. **Deliver** (section 7) when the user says it looks good, with the QA report (or "Quick draft: automated checks only, no independent review"). If blockers or majors remain, say so first; never present a failing page as passing. Delivery is not done until the page is published or the user was told why it couldn't be.

Tell the user one line when each stage starts (writing content, designing, page ready, reviewing, applying changes); keep the task list updated.

**Starting the agents.** If named agents `page-content`, `page-designer` and `page-qa` are installed (Claude Code opened in this repo loads them from `.claude/agents/`), use them. Otherwise start `general-purpose` agents with the prompt: "Read `<kit>/agents/shared.md` and `<kit>/agents/content.md` and follow them. Kit folder: `<kit>`. Brief: `<work>/brief.md`." (or `designer.md`, `qa.md`), always passing the absolute kit and work paths. If no agent tool exists at all, do each stage yourself in order, keeping the same files and lane rules, do the QA as a separate clean pass reading only the page, brief and materials, and tell the user the review was not independent.

### 0.7 The tweak round

The user finishes the design on a **tweak page**: the page in a live preview with a tweak bar (palettes, a new main colour, single colours with a live contrast check, font pairings or any Google font, sizes, spacing, corners, shadows, page width, button shape; per block: move, hide, swap to another version, replace it with a library block or add one, background, text edits and notes). One button sends everything back. Skip this round in unattended sessions.

1. **Make the tweak page:** `python3 <kit>/scripts/tweakbar.py <work>/index.html` writes `<work>/tweak.html` (it picks up `alternates.html` and `tweak-options.json` when they exist; `--seeds "#HEX"` adds palettes from extra brand colours). Warnings about blocks or alternates go to page-designer. `index.html` is never changed by this.
2. **Show it and wait for the button:**
   - **Claude Code:** start `python3 <kit>/scripts/tweakserve.py <work> --once --open` as a **background** command. It opens the tweak page in the browser and exits as soon as the user presses **Send to Claude** or **Looks good, deliver**; its exit wakes you up. Give the user the address from `<work>/tweak-url.txt` in one line and end your turn: no question, nothing to paste. Its output is `RECEIVED apply <work>/tweaks.json` or `RECEIVED approve` (or `TIMEOUT` after an hour: say the tweak page is still open and how to restart it).
   - **Other clients:** publish `tweak.html` as its **own** private artifact titled "<Practice> <page type> tweaks" (icon "settings"), declaring the `db` capability (`capabilities: {db: {}}`), never in place of the page's artifact; later rounds republish to the same tweak artifact. Tell the user: press **Send to Claude** (or **Looks good**) on the page, then type "done" here. On "done", read the artifact's data (`ArtifactData` get, collection `tweaks`, document `latest`): `action` is `apply` or `approve`, `json` is the change file. If there is no data or the tool is missing, the page has copied the changes instead: ask the user to paste them.
   - Their unsent changes are kept in that browser, so they can close the page and come back.
3. **Approve:** `approve` (or the user says it looks good) means deliver (section 7), after any held QA fixes (0.6 step 7).
4. **Receive:** save the change file to `<work>/tweaks.json` (tweakserve does this itself and keeps earlier rounds as `tweaks-1.json`, ...). Its `page_hash` must match the current `index.html`; apply_tweaks.py refuses otherwise (the tweak page was older: rebuild it and ask again). Show the `summary` lines back in one short list.
5. **Confirm brand changes:** if `brand_overrides` is not empty (the brief fixed the brand colours or fonts and the user changed them), ask (Use my change · Keep the brand) before applying; drop the change if they keep the brand.
6. **Words first:**
   - **Written content:** if there are `copy_edits`, `blocks.order`, `blocks.hidden`, `blocks.variants`, `blocks.replacements` or `blocks.added`, send `tweaks.json` to page-content. It updates `plan.md` and `content.json`, writes words for new blocks, and adds a `final` text to every copy edit in `tweaks.json` (the user's words, or the closest version that passes grade 5 and compliance). It returns `CONTENT TWEAK REPORT`.
   - **Placeholder content:** update `plan.md` yourself for order, hidden, replaced and added blocks; text edits are applied as written.
7. **Apply the mechanical changes in seconds:** `python3 <kit>/scripts/apply_tweaks.py <work>/tweaks.json` (add `--copy-as-written` on a placeholder page). It writes tokens, fonts, sizes, shape, order, hidden blocks, block versions, backgrounds and text edits straight into `index.html` (backups in `<work>/backups/`) and prints what it applied, plus `needs_designer` (replaced and added blocks, notes, contrast failures, anything it could not do) and `cleanup`.
8. **Designer only when needed:** if `needs_designer` or `cleanup` is not empty, or QA findings are held, send them to page-designer with the content files: it does only those, with targeted edits, and returns `DESIGN TWEAK REPORT`. Otherwise skip the designer.
9. **Check:** one full `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --out <work>/qa/auto.json` (the designer's, or yours when no designer was needed). Serious or critical axe findings, overflow or a missing logo go to page-designer. In full review mode, if blocks or words changed, start a **fresh** page-qa limited to the changed blocks plus the automated results.
10. **Next round:** rebuild the tweak page from the new `index.html` and show it again (step 2). There is no round limit; the user decides when it is done. Then deliver (section 7) and mention what each round changed.

---

## 1. Intake (gate)

Note the start time first (`date -Iseconds`) for the stage timing (0.5).

Ask with **guided questions**: the `AskUserQuestion` tool, which shows clickable options and always lets the user type their own answer ("Other"). One screen is the goal: Round 1 is always asked; Round 2 only when the user wants the words written. Do not plan, write or build until the needed rounds are answered.

Before asking, read anything already in the request (logo, URL, notes) and tailor the options to it: use the practice's specialty, city and services in the examples. Skip any question the request already answers clearly, and say what you took from it in one line.

**Round 1: the page (one `AskUserQuestion` call, 4 questions)**

| Header | Question | Options (2 to 4, tailor them) |
|---|---|---|
| Page type | What kind of page are we building? | Landing page (for ads) · Home page · Treatment page · Other website page (location, provider, about, insurance, testimonials, contact: user types it) |
| Main action | What is the one action visitors should take? | Book a visit · Call now · Schedule a conversation · Check my insurance |
| Content | Should I write the page's words, or use placeholder text so you get the design faster? | Placeholder text (lorem ipsum), fastest (Recommended) · Write the content (adds a few minutes) |
| Brand | What can you share for the look? (multiSelect) | Brand guide (colors, fonts, voice) · Logo · Compliance rules (claims, disclaimers) · Their current website (type the URL under Other) |

**Defaults (say them in one line after Round 1, never ask):** build straight away (no plan approval), quick draft (automated checks, no review agent), audience "new patients", and in conversion mode a short form with no video. The user can say "show me the plan first", "full review" or anything else at any time, and you follow it. A benchmark site is used only when the user gives one.

**Brand guide, always asked:** the Brand question is never skipped, even when the request already gives a website or logo; a website does not replace a brand guide (the guide's colors, fonts and voice win, `rules/materials.md`). If they picked any files, ask them to attach those files in one short line, wait for them, then copy them into `<work>/materials/` (0.2). If they picked the current website without giving the URL, ask for it in the same line. If they picked nothing, say in one line that you'll pick a look from the logo or website, and that they can attach a brand guide at any time. Anything not shared becomes a `[placeholder]`; practice facts (phone, locations, hours, providers, insurance, real reviews) can be typed or pasted.

**Placeholder content:** the page uses lorem ipsum in place of the copy (`rules/copy.md` 4.2) and there is no content stage and no Round 2.

**Round 2: only for written content (one `AskUserQuestion` call, 4 questions):** "Audience" (Who is this page for? New patients with [main condition] · New patients in [city] · Existing patients · Referring doctors) and the top 3 messages, each as its own question so the order is kept: header "Message 1", "Message 2", "Message 3", question "What is the #1 thing visitors must know?" (then #2, #3). Offer 3 to 4 likely messages in plain 5th-grade words, for example: Seen this week · Plan made for you · No surgery first · Most insurance taken · Top-rated doctors · Close to home; never repeat an option already picked.

**Round 2b: only for written content in conversion mode (one call, 4 questions).** Conversion mode is on when the page type is a landing page, or the user says the page is for ads, paid traffic or conversion.

| Header | Question | Options (tailor them) |
|---|---|---|
| Keyword | What search term or ad headline sends people here? (The page headline will match it.) | 2 to 3 likely terms, e.g. "[Specialty] in [City]" · "[Treatment] near me" · Not running search ads |
| Traffic | Where will most visitors come from? | Google search ads · Meta or social ads · Email or text · Organic or referral |
| Lead flow | How should leads come in? | Short form, team calls back fast · Multi-step form, qualify first · Call first (big call button) · Quiz funnel |
| Proof | Which proof can you give us? (multiSelect) | Doctor video (VSL) · Before/after photos · Real patient reviews · None yet |

Defaults if skipped: Google search ads, short form, no video. Meta or social traffic for a considered procedure points to a quiz funnel; an older, call-preferring audience points to Call first.

**Rules**

- Required answers: page type, main action and the content choice (placeholder if skipped); for written content also the audience and all 3 messages (Round 2b defaults apply if skipped). If an answer is vague, ask one short follow-up (another guided question if possible).
- Keep each question self-contained: the user may only see the question dialog.
- If `AskUserQuestion` is not available (some surfaces, scheduled runs), ask the same questions in plain text, one round per message.
- When something optional is missing, say what you will do instead in one line (for example: "No brand color given, so I'll use the logo's blue") and continue. Never invent practice facts; use clear `[placeholders]`.
- If the session is unattended and the required answers are not in the request, stop after asking. Do not guess the goal or action.

---

## 7. Deliver

- The orchestrator (not an agent) publishes the final page. Read `<work>/index.html` in full first, then publish it with the artifact publishing tool (`publish_files`, file `index.html`; in other clients the Artifact tool). Before the first publish in a session, read the artifact tool's guide for pages. Title: "<Practice> <page type>". Icon: "page".
- Revisions: republish to the same artifact (same slug, latest version as base) so the link never changes. Never create a second artifact for the same page.
- After publishing, the chat shows a card with the share link. Tell the user in one line that the page is private to them until they share it from the card.
- Also send `index.html` with SendUserFile (display 'render') so it can be downloaded.
- Only if no artifact tool exists in the session, say "Share link not available here; download the file instead." Never skip publishing silently.
- The tweak page (`<work>/tweak.html`) is a review tool: never deliver or publish it as the page, and never copy tweak bar code into `index.html` (qa.py reports `tweak_leftovers`).
- Wireframes (`<work>/wireframe.html` from `scripts/wireframe.py`) are not published; send them with SendUserFile (display 'render'). If SendUserFile is not available (for example in the terminal), give the absolute path and open the file in the user's browser (`open <path>` on macOS, `xdg-open` on Linux). Say in one line that the wireframe shows block order and layout with sample words, not the final design or copy.
- For a website: publish each page as its own artifact and list the links in the sitemap line.
- In quick draft mode, offer a full review before launch as the first next step.
- Include the final QA report: verdict, number of fix rounds (or "Quick draft: automated checks only, no independent review"), what was fixed (and by which agent), and any open findings. If the verdict is still FAIL, say so first.
- Send the screenshots only if the user wants a quick look.
- Add `<!-- Built with create-page vX.Y.Z -->` (the kit version from `VERSION`) as the first line inside `<head>` of every page's `index.html` (`templates/page.html` already has the line; set the version).
- With placeholder content, say first that the page uses lorem ipsum and is a design draft, not ready to launch; skip the reading grade, the message-match line and the compliance checklist, and offer to have page-content write the real content next.
- In conversion mode, also give: a pre-launch compliance checklist (disclaimers, before/after disclosures and consent, review authenticity, HIPAA-compliant form processing, no tracking pixels on the form without a BAA) for the team to tick before launch, and a message-match line (keyword → H1 → 2 or 3 matching ad headlines) so the ad and page stay aligned.
- Include the stage timing: end the `deliver` stage, then paste the totals from `python3 <kit>/scripts/timing.py <work> report` (minutes per stage, total time, slowest stage).
- Finish with a short note: the kit version, the design direction in one line (palette, type pairing, the memorable element), the block plan used (and the benchmark ideas it borrowed, if any), the page's reading grade, the list of `[placeholders]` the practice must fill, and any compliance flags.
- Offer next steps as options, for example: another tweak round, A/B variant of the hero, another page from the sitemap, or a dark theme.

---

## 9. Versioning

This kit uses version numbers in the form MAJOR.MINOR.PATCH. The current version is at the top of this file.

- **Patch (1.0.0 to 1.0.1):** small updates. Wording, clearer instructions, new answer options, swap-table entries, bug fixes in the scripts. How the kit works does not change.
- **Minor (1.0.1 to 1.1.0):** new things added without changing the flow. A new block, a new page recipe, a new check.
- **Major (1.x to 2.0.0):** bigger updates that change how the kit works. A new intake flow, a new design system, a new output format, removed or renamed steps.

Every time the kit is changed:

1. Pick the bump using the rules above. If unsure between two, ask the user.
2. Update `VERSION` and the version line at the top of this file.
3. Add a line to `CHANGELOG.md`, newest first: version, date, one short sentence on what changed.
4. Never change an old changelog line.
5. Publish a GitHub release tagged `vX.Y.Z`. The `/create-page` loader only uses published release tags, so unreleased edits never reach the team.
