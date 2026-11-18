# Macallan Page Builder: START HERE

You are reading the page builder kit. If the user asked for a page and you were sent here (by the `/create-page` loader skill, a pasted repo link, or Claude Code opened in this repo), you are the **orchestrator**: follow this file from section 0.

**Kit version 6.2.5** (see `VERSION` and `CHANGELOG.md`)

Builds landing pages and website pages for healthcare practices (home, specialty, condition, location, provider, about, insurance, testimonials, contact). Pages are assembled from the Macallan block library below, art-directed with the `frontend-design` approach (a distinct visual identity per practice, no generic AI look), built as one plain HTML file on Material Design logic (no build tools or installs), and written at a 5th-grade reading level, because plain copy converts best.

This kit runs as a relay: the **orchestrator** (you, in the user's conversation) runs the intake and the relay, the **page-content** agent writes the plan and every word, the **page-designer** agent designs and builds (starting on the design system while the words are written), and three **page-qa** agents review independently, in parallel. Section 0 says who does what. Do not skip the intake gate. Agents never read this file: each reads `agents/shared.md` and its own role file.

0. How this runs (roles, brief, content modes, timing, the relay, fix routing, the tweak round)
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
| 0, 1, 7, 9 (0.7 tweak round) | `START-HERE.md` (this file) |
| 2 | `rules/materials.md` |
| 3 (3.1 to 3.4) | `rules/blocks-and-plan.md` |
| 4 (4.1 to 4.3) | `rules/copy.md` |
| 5 (5.1 to 5.11) | `rules/design-build.md` |
| 6 (6.1 to 6.3) | `rules/qa.md` |
| 8.1 / 8.2 / 8.3 | `scripts/readability.py` / `scripts/m3_scheme.py` / `scripts/qa.py` |
| 8.5 | `scripts/logo.py` (trims, resizes and embeds the logo; reports light or dark and its main color) |
| 8.4 | `templates/page.html` (copy it to `<work>/index.html`) |
| 8.6 | `scripts/wireframe.py` (stacks the planned blocks from `blocks/` into `<work>/wireframe.html` for plan approval) |
| 8.7 | `scripts/tweakbar.py` + `templates/tweakbar.html` (makes `<work>/tweak.html`: the page with a tweak bar, for the tweak round in 0.7) |
| 8.8 | `scripts/tweakserve.py` (serves the tweak page locally so Send to Claude hands the changes straight back, 0.7) |
| 8.9 | `scripts/apply_tweaks.py` (writes the mechanical part of a `tweaks.json` into `index.html` in seconds, 0.7) |
| 8.10 | `scripts/timing.py` (records each stage's start and end in `<work>/timing.md`, 0.5) |
| 8.11 | `scripts/setup.py` (installs what the scripts need, in the background during the intake) |
| 8.12 | `scripts/fetch_site.py` (reads the current website once during the intake into `<work>/materials/site/`) |
| 8.13 | `scripts/build_packs.py` (builds `agents/packs/<role>.md`: each role's rule files in one file, word for word; run before every release) |
| axe-core | `scripts/vendor/axe.min.js` (bundled, with its `LICENSE`) |
| Block reference HTML | `blocks/<ID>-*.html` (structure and content reference only; never their styling) |
| Agent roles | `agents/shared.md` (read by every agent) plus `agents/content.md`, `agents/designer.md`, `agents/qa.md` (each agent's full instructions; also in `.claude/agents/`) |

Run scripts from the kit, for example `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --brand-fonts "Brand Font"`. Never edit the kit while building a page; client work goes in the work folder.

---

## 0. How this runs

### 0.1 Roles

The page is made by a relay: content first, then design, then an independent review. Each agent owns its lane and never edits another's work.

| Role | Who | Owns | Hands off | Never |
|---|---|---|---|---|
| Orchestrator | The main conversation (when the user runs `/create-page` or asks for a page) | Section 1 intake, the brief, `brand.json` from the brand guide, the block plan on lorem pages, stage timing (0.5), running the relay and fix routing (0.6), delivery (section 7) | Brief to page-content and page-designer | Writes copy or builds the page when the agents are available |
| page-content | Agent (`page-content`) | Sections 2 (facts, compliance, current site, benchmark), 3 and 4: block plan, every word, compliance wording, placeholders | `content/plan.md` + `content/content.json` | Touches layout, styles or code |
| page-designer | Agent (`page-designer`) | Sections 2 (brand, logo, current site look), 5 and 6.1: design plan, build, mobile, ADA build quality | `<work>/index.html` | Changes any word; it sends a copy change request instead |
| page-qa | Agent (`page-qa`), three fresh ones per review, in parallel (areas A, B, F · C · D, E) | Section 6 for its areas | QA report | Edits anything, sees the other agents' notes |

If you were started by the user (or by `/create-page`), you are the orchestrator. If your prompt says you are page-content, page-designer or page-qa, stop reading this file: follow `agents/shared.md` and your role file in `agents/`.

### 0.2 The brief

As soon as Round 1 of the intake is answered, create the work folder (`<page-slug>/` in the working directory) so the background steps have somewhere to write (1, Before the questions). **Before writing the brief, gather the materials into `<work>/materials/`:**

- Copy every file the user attached (logo, brand guide, compliance documents, photos) into `<work>/materials/`, keeping the file names. Agents only see what is in this folder, so never just mention an attachment in the brief.
- **Brand guide:** if the user shared one, write `<work>/brand.json` from it (`rules/materials.md`) before the build starts.
- **Logo:** if the user did not attach one but the practice has a current website, take the one `fetch_site.py` saved in `<work>/materials/site/` (check that it is really the logo), or get it from the site: find the logo in the site header (an `<img>` src, an inline `<svg>`, or as a last resort the `apple-touch-icon` or `og:image`), download it with `curl -L -o <work>/materials/logo.<ext> <url>` (save inline SVG markup as `logo.svg`), and check that the file is really the logo. Write `Logo: none` only when there truly is no logo anywhere.

Then write `<work>/brief.md`. It is the only thing the relay starts from, so it must be complete:

```markdown
# Brief: <practice> <page type>
- Page type: ...            - Conversion mode: yes/no
- Audience: ...             - Main action (CTA words): ...   - Second action: ... or none
- Message 1: ...            - Message 2: ...                 - Message 3: ...
- Keyword: ...  - Traffic: ...  - Lead flow: ...  - Proof available: ...   (conversion mode)
- Plan approval: approved plan below / build directly
- Review mode: full review / quick draft (automated checks only)
- Content: write / document (<absolute path to the client's content document>) / lorem (rules/copy.md 4.2-4.3)
- Brand guide: <absolute path to brand.json> or none
- Brand fonts: ... or none given
- Logo: <absolute path in <work>/materials/> (attached / from the current website) or none
- Other materials (absolute paths in <work>/materials/): brand guide ..., compliance docs ..., photos ... (or none)
- Current website: URL or none        - Benchmark website: URL or none
- Practice facts given by the user: name, phone, locations, hours, providers, insurance, reviews
- Approved block plan (if the user approved one): ...
- Work folder: <absolute path>
```

### 0.3 Content modes

The intake asks how the words are made (Round 2, "Content"):

- **Write the content with the design** (`Content: write`): page-content writes every word, in parallel with the designer's system work.
- **I have a content document** (`Content: document`): the client's document goes into `<work>/materials/` and page-content uses its words (`rules/copy.md` 4.3), listing every change it had to make, in parallel with the designer.
- **Lorem ipsum** (`Content: lorem`): no words are written. You write `plan.md` yourself (block plan from 3.2 and 3.3 for the page type, goal and messages); the designer fills the slots with lorem (`rules/copy.md` 4.2) and builds in one go. If the user later wants real words, start page-content then; the designer swaps the text in with targeted edits.

### 0.4 The agents' instructions

Each agent's full mode (inputs, what to do, report format, fix and tweak rounds) is in its role file: `agents/content.md`, `agents/designer.md`, `agents/qa.md`, plus the short shared section in `agents/shared.md`. Agents read their role file and their reading pack (`agents/packs/<role>.md`: the rules for that role, word for word, in one file), never this file; the design and copy rules themselves are read in full.

**No cold starts:**
- **Warm-up:** start the content agent and the designer at the beginning of the intake with the message "warm-up": they read their pack and reply `READY` while the user answers the questions. Start the QA reviewers with "warm-up" while the designer builds.
- **One content agent and one designer per job:** keep them for every later step (content, system, blocks, tweak support, copy change requests, fix rounds, tweak rounds) by sending them messages (SendMessage) instead of starting new ones. Write their names or IDs to `<work>/agents.md` so you can find them again after a long conversation. Start a replacement only if a message cannot reach them, and give it `<work>/design-plan.md` (designer) or the content files (content) so it picks up the earlier decisions.
- **QA is fresh for every review** (three reviewers, then a new re-reviewer): they are warmed up but never reused, so they never see how the page was made.
- **The essentials go in each task message:** the brief text, the approved plan, the practice name, the brand colours, fonts and logo path, the content mode, and the phase or review areas, so agents only open files for what is not there. Their reports: `PLAN READY` / `CONTENT REPORT` / `CONTENT FIX REPORT` / `CONTENT TWEAK REPORT`; `SYSTEM READY` / `DESIGN REPORT` / `TWEAK SUPPORT REPORT` / `DESIGN FIX REPORT` / `DESIGN TWEAK REPORT` (with `COPY CHANGE REQUEST`s); and the QA report in `rules/qa.md` 6.3.

### 0.5 Stage timing

Record the start and end of every stage so the real bottleneck shows: `python3 <kit>/scripts/timing.py <work> start <stage>` and `... end <stage>`, with the stages `intake`, `wireframe`, `content`, `design`, `qa`, `fixes`, `tweak` and `deliver` (repeat runs are numbered automatically; stages that run in parallel overlap in the table). The intake starts before the work folder exists: note `date -Iseconds` when you start it and record it later with `--at`. Each call rewrites `<work>/timing.md` (one row per stage run, totals per stage, the total time and the slowest stage). `timing.py <work> report` prints it for the final summary (section 7).

### 0.6 Orchestration: the relay

Time every stage (0.5). Work that does not depend on each other runs at the same time; the design rules, the block review and the full review stay exactly as they are.

1. **Intake** (section 1), with the background steps it starts: `setup.py` and the **warm-up** of the content agent and the designer at the very start (0.4), the work folder after Round 1, `fetch_site.py` as soon as the website is known.
   **Block review**, if the user chose "Show me the plan first" (the recommended answer): get `plan.md` (message the warmed content agent with "plan only" for write and document modes; write it yourself for lorem), run `python3 <kit>/scripts/wireframe.py <work>/content/plan.md --title "<Practice> <page type>"`, send `<work>/wireframe.html` (section 7) with the short plan list, and ask (Approve plan · Change something). If the user changes the plan, update `plan.md` the same way, rebuild the wireframe and ask again. Record the approved plan in the brief; the build follows exactly that plan.
2. **Brief:** write `brief.md` (0.2), with the review mode (full review by default), the content mode (0.3), the content document and `brand.json` when there are any.
3. **Content and design at the same time:**
   - **Write or document:** message the warmed content agent (full content) and the warmed designer (phase **system**) at the same time, each with the essentials (0.4). The designer sets the design plan, tokens, type, header and footer while the words are written, and lays out no blocks yet. When `CONTENT REPORT` arrives (if `BRIEF INCOMPLETE`, ask the user and continue), message the same designer with phase **blocks** and the content path. It builds the blocks around the real words.
   - **Lorem:** message the warmed designer with phase **full build**.
   - **Copy change requests:** at most **one** round trip: send them to the same content agent, then the updated content back to the same designer; after that the designer adapts the layout to the words.
   - While the designer builds, start the three QA reviewers with "warm-up" (0.4).
4. **Build checks:** the designer checks with `qa.py --fast` while working and finishes with one full run to `<work>/qa/auto.json` (with `--brand` when there is a brand.json), then returns `DESIGN REPORT`.
5. **First look right away:** make and show the tweak page (0.7 steps 1 and 2) with the line "Here's your page. The review is running: change anything you like, then press Send to Claude, or Looks good when you're happy." Do not wait for the review.
6. **In the background, at the same time** (start them as background agents; if the client cannot, start them right after showing the page):
   - **QA, three reviewers in parallel** (full review, the default): message the three warmed **fresh** `page-qa` agents with only the preview path, the brief path, the material paths and the automated results path (`<work>/qa/auto.json`, which they reuse while the page is unchanged): reviewer 1 areas A, B and F, reviewer 2 area C, reviewer 3 areas D and E. Never pass the other agents' reports or notes. Merge their reports into one (6.3; FAIL if any found a blocker or major). **Hold the findings:** never change `index.html` while the user may be tweaking it (it would reset their unsent changes); tell the user in one line how many findings there are and that they will be fixed with their changes.
   - **Tweak support:** message the same designer for `alternates.html` and `tweak-options.json` (5.10). When it is done, rebuild `tweak.html` (the page has not changed, so the user's unsent changes are kept) and tell the user in one line: "More block versions and palettes are ready: refresh the tweak page." (Chat: republish the same tweak artifact.)
   - **Quick draft** (only when the user asked for it): no reviewers; the designer's automated checks are the QA.
7. **When the user sends changes or says it looks good** (0.7): apply the tweaks first, then the held findings that still apply (findings on removed or replaced blocks are dropped). Route findings by owner, always to the same content agent and designer as before (0.4):
   - **page-content:** area A (copy, brief, reading level, CTA words), area B wording (claims, disclaimers, placeholders, form note), area F order and plan. On a lorem page there are no copy findings; plan findings are yours to fix in `plan.md`.
   - **page-designer:** areas C (design quality), D (mobile), E (ADA), area B items that are build issues (tracking scripts, form markup, legal links missing from the footer layout).
   - A finding that needs both goes to page-content first, then page-designer.
   - **Fixes are edits, not rebuilds:** the designer changes only what the findings name, with targeted edits (a whole block only when a finding needs that block redesigned, never the whole page), and finishes with one full qa.py run to `<work>/qa/auto.json`. Minor and mechanical findings (6.3) are fixed directly and not re-reviewed.
8. **Re-review:** if there were blocker or judgment-major findings, start a **fresh** page-qa (the reviewers of the affected areas, or one for all) with the preview, brief, material and automated results paths plus those findings. It re-checks only those plus the automated results. **Default is 1 fix round**; a second only if blockers remain; remaining majors are reported at delivery.
9. **Deliver** (section 7) when the user says it looks good, with the merged QA report. If blockers or majors remain, say so first and list them; never present a failing page as passing. Delivery is not done until the page is published or the user was told why it couldn't be.

Tell the user one line when each stage starts (writing content and designing, page ready, reviewing, applying changes); keep the task list updated.

**Starting the agents.** If named agents `page-content`, `page-designer` and `page-qa` are installed (Claude Code opened in this repo loads them from `.claude/agents/`), use them. Otherwise start `general-purpose` agents with the prompt: "Read `<kit>/agents/content.md` and `<kit>/agents/packs/content.md` and follow them. Kit folder: `<kit>`." (or `designer`, `qa`), always passing the absolute kit and work paths, and then the task with the essentials, the phase or the review areas. If continuing a running agent is not possible in this client, start a new agent for each step with the essentials in its first message (0.4). If no agent tool exists at all, do each stage yourself in order, keeping the same files and lane rules, do the QA as a separate clean pass reading only the page, brief and materials, and tell the user the review was not independent.

### 0.7 The tweak round

Right after the build (0.6 step 5), while the review runs, the user gets the page with a **tweak bar** to finish the design themselves: palettes, a new main colour, single colours with a live contrast check, font pairings or any Google font, sizes, and real pixel values measured from the page for button corners, card and photo corners, shadow blur, page width and section spacing, plus button shape presets; and per block (each shown as a live preview): move, hide, swap to another version, replace it with any block from the library or add a library block below it (the tweak page marks the spot; the block is built when the changes come back), change the background, edit text and leave notes; and per element ("Select element": any heading, button, photo or card): change its text colour, background, size, weight, alignment, spacing, width or corners using only the page's own tokens, hide it, replace a photo with their own, or pin a comment to it. Undo and redo cover every change. One button sends everything back. Skip this round in unattended sessions.

1. **Make the tweak page:** `python3 <kit>/scripts/tweakbar.py <work>/index.html` writes `<work>/tweak.html` (it picks up `alternates.html` and `tweak-options.json` from the work folder; add `--seeds "#HEX"` for palettes made from extra brand colours). If it prints warnings about blocks or alternates, send them to page-designer to fix first. `index.html` is never changed by this.
2. **Show it and wait for the button:**
   - **Claude Code:** start `python3 <kit>/scripts/tweakserve.py <work> --once --open` as a **background** command. It opens the tweak page in the browser and exits as soon as the user presses **Send to Claude** or **Looks good, deliver**; its exit wakes you up. Give the user the address from `<work>/tweak-url.txt` in one line and end your turn: no question, nothing to paste. Its output is `RECEIVED apply <work>/tweaks.json` or `RECEIVED approve` (or `TIMEOUT` after an hour: say the tweak page is still open and how to restart it).
   - **Other clients:** publish `tweak.html` as its **own** private artifact titled "<Practice> <page type> tweaks" (icon "settings"), declaring the `db` capability (`capabilities: {db: {}}`), never in place of the page's artifact; later rounds republish to the same tweak artifact. Tell the user: press **Send to Claude** (or **Looks good, deliver**) on the page, then type "done" here. On "done", read the artifact's data (`ArtifactData` get, collection `tweaks`, document `latest`): `action` is `apply` or `approve`, `json` is the change file. If there is no data or the tool is missing, the page has copied the changes instead: ask the user to paste them.
   - Their unsent changes are kept in that browser, so they can close the page and come back.
3. **Approve:** `approve` (or the user says it looks good) means deliver (section 7), after the held QA findings are fixed (0.6 step 7).
4. **Receive:** save the change file to `<work>/tweaks.json` (tweakserve does this itself and keeps earlier rounds as `tweaks-1.json`, ...). Its `page_hash` must match the current `index.html`; apply_tweaks.py refuses otherwise (the tweak page was older: rebuild it and ask again). Show the `summary` lines back in one short list.
5. **Confirm brand changes:** if `brand_overrides` is not empty (the brief fixed the brand colours or fonts and the user changed them), ask with a guided question (Use my change · Keep the brand) before applying; drop the change if they keep the brand.
6. **Words first:** if there are `copy_edits`, `blocks.order`, `blocks.hidden`, `blocks.variants`, `blocks.replacements` or `blocks.added`, send `tweaks.json` to the same content agent (0.4). It updates `plan.md` and `content.json`, writes words for new blocks, and adds a `final` text to every copy edit in `tweaks.json` (the user's words, or the closest version that passes grade 5 and compliance). It returns `CONTENT TWEAK REPORT`.
7. **Apply the mechanical changes in seconds:** `python3 <kit>/scripts/apply_tweaks.py <work>/tweaks.json`. It writes tokens, fonts, sizes, shape, order, hidden blocks, block versions, backgrounds, the `final` text edits, element changes and photos straight into `index.html` (backups in `<work>/backups/`) and prints what it applied, plus `needs_designer` (replaced and added blocks, notes, pinned comments, contrast failures, photos to be attached in the chat, anything it could not do) and `cleanup`. Photos sent from the chat version arrive as attachments: save them to `<work>/materials/uploads/` and pass them to page-designer. Pinned comments that only ask for different words go to page-content as copy change requests.
8. **Designer only when needed:** if `needs_designer` or `cleanup` is not empty, send them to the same designer (0.4) with the content files: it does only those, with targeted edits, and returns `DESIGN TWEAK REPORT`. Otherwise skip the designer.
9. **Check:** the 6.1 run is always required (the designer's, or yours when no designer was needed: `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --out <work>/qa/auto.json`, adding `--brand <work>/brand.json` when it exists). In full review mode, if blocks or words changed (order, hidden, variants, replaced or added blocks, copy edits), start a **fresh** page-qa (warm it up while the designer works) limited to the changed blocks plus 6.1; changes to the design only (colours, fonts, sizes, shape, backgrounds) need 6.1 only. Route any findings as in 0.6 step 8.
10. **Next round:** rebuild `tweak.html` from the new `index.html` and show it again (step 2). There is no round limit; the user decides when it is done. Then deliver (section 7) and mention what each tweak round changed.

---

## 1. Intake (gate)

Ask with **guided questions**: the `AskUserQuestion` tool, which shows clickable options and always lets the user type their own answer ("Other"). Ask in rounds, not as one long text message. Do not plan, write or build until Round 1 and Round 2 are answered.

Before asking, read anything already in the request (logo, URL, notes) and tailor the options to it: use the practice's specialty, city and services in the examples. Skip any question the request already answers clearly, and say what you took from it in one line.

**Before the questions (background, nobody waits for these):** note the start time (`date -Iseconds`) for the stage timing (0.5), and start `python3 <kit>/scripts/setup.py` as a background command so the tools are installed while the user answers. After Round 1, create the work folder (0.2). As soon as the current website is known (from the request or Round 3), start `python3 <kit>/scripts/fetch_site.py <url> <work>/materials` as a background command; the agents read its summary instead of browsing the site again.

**Round 1: page basics (one `AskUserQuestion` call, 4 questions)**

| Header | Question | Options (2 to 4, tailor them) |
|---|---|---|
| Page type | What kind of page are we building? | Landing page (for ads) · Home page · Treatment page · Other website page (location, provider, about, insurance, testimonials, contact: user types it) |
| Audience | Who is this page for? | New patients with [main condition] · New patients in [city] · Existing patients · Referring doctors |
| Main action | What is the one action visitors should take? | Book a visit · Call now · Schedule a conversation · Check my insurance |
| Plan first? | Do you want to approve the block plan before I build? | Show me the plan first (Recommended) · Go straight to the finished page |

The page goal = audience + main action (+ page type). If the user wants a second action, they can type it under "Other" on Main action, or ask in Round 2.

**Round 2: top 3 messages in order, and the content (one `AskUserQuestion` call, 4 questions)**

The fourth question is how the words are made (0.3):

| Header | Question | Options |
|---|---|---|
| Content | How should we handle the page's words? | Write the content with the design (Recommended) · I have a content document (attach it) · Lorem ipsum placeholder for now |

If they have a content document, ask them to attach it with the Round 3 materials (one line) and copy it into `<work>/materials/`. With lorem, the messages still shape the block plan and order.

Ask each message as its own question so the order is kept: header "Message 1", "Message 2", "Message 3". Question text: "What is the #1 thing visitors must know?" (then #2, #3). Offer 3 to 4 likely messages for this practice and page, phrased in plain 5th-grade words, for example: Seen this week · Plan made for you · No surgery first · Most insurance taken · Top-rated doctors · Close to home. Do not offer an option already picked in an earlier message. The user can type their own.

**Round 2b: conversion details (only in conversion mode, one `AskUserQuestion` call, 4 questions)**

Conversion mode is on when the page type is a landing page, or the user says the page is for ads, paid traffic or conversion. Then also ask:

| Header | Question | Options (tailor them) |
|---|---|---|
| Keyword | What search term or ad headline sends people here? (The page headline will match it.) | 2 to 3 likely terms, e.g. "[Specialty] in [City]" · "[Treatment] near me" · Not running search ads |
| Traffic | Where will most visitors come from? | Google search ads · Meta or social ads · Email or text · Organic or referral |
| Lead flow | How should leads come in? | Short form, team calls back fast · Multi-step form, qualify first · Call first (big call button) · Quiz funnel |
| Proof | Which proof can you give us? (multiSelect) | Doctor video (VSL) · Before/after photos · Real patient reviews · None yet |

Defaults if skipped: Google search ads, short form, no video. Meta or social traffic for a considered procedure points to a quiz funnel; an older, call-preferring audience points to Call first.

**Round 3: materials, references and review mode (one `AskUserQuestion` call, up to 4 questions)**

| Header | Question | Options |
|---|---|---|
| Materials | Which of these can you share? Attach them in your next message. (multiSelect) | Brand guide (colors, fonts, voice) · Logo · Compliance rules (claims, disclaimers, consent) · Photos |
| Current site | Does the practice have a current website? | Yes (type the URL under Other) · No current website |
| Benchmark | Do you have a website example to use as a benchmark? | Yes (type the URL under Other) · No benchmark |
| Review | Speed or full review? (optional) | Full review (Recommended) · Quick draft: one build plus automated checks, no review agent |

Note in the Materials question that anything not shared becomes a `[placeholder]` and practice facts (phone, locations, hours, providers, insurance, real reviews) can be typed or pasted. The Review question is optional: if it is skipped or unanswered, use Full review. Skip any question the request already answers. If the user picks materials, wait for the attachments, then copy them into `<work>/materials/` (0.2); if they pick none or type "none", continue (the logo still comes from the current website when there is one). If they say "Yes" to a site without giving the URL, ask for it in one short line.

**Brand guide, always asked:** the Materials question is never skipped, even when the request already gives a website or a logo; a website does not replace a brand guide (the guide's colors, fonts and voice win, `rules/materials.md`). When a guide is shared, write `<work>/brand.json` from it before the build and tell the user in one line that the design will stay inside the guide.

**Rules**

- Every round must be answered before the next. Required answers are page type, audience, main action, all 3 messages and the content choice (write, if skipped), plus Round 2b in conversion mode (its defaults apply if the user skips it). If an answer is vague, ask one short follow-up (another guided question if possible).
- Keep each question self-contained: the user may only see the question dialog.
- If `AskUserQuestion` is not available (some surfaces, scheduled runs), ask the same questions in plain text, one round per message.
- When something optional is missing, say what you will do instead in one line (for example: "No brand color given, so I'll use the logo's blue") and continue. Never invent practice facts; use clear `[placeholders]`.
- If the session is unattended and the required answers are not in the request, stop after asking. Do not guess the goal, action or messages.

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
- Include the final QA report: verdict, number of fix rounds (or "Quick draft: automated checks only, no independent review"), what was fixed (and by which agent), and any open findings. If the verdict is still FAIL, say so first.
- Send the screenshots only if the user wants a quick look.
- Add `<!-- Built with create-page vX.Y.Z -->` (the kit version from `VERSION`) as the first line inside `<head>` of every page's `index.html` (`templates/page.html` already has the line; set the version).
- In conversion mode, also give: a pre-launch compliance checklist (disclaimers, before/after disclosures and consent, review authenticity, HIPAA-compliant form processing, no tracking pixels on the form without a BAA) for the team to tick before launch, and a message-match line (keyword → H1 → 2 or 3 matching ad headlines) so the ad and page stay aligned.
- Include the stage timing: end the `deliver` stage, then paste the totals from `python3 <kit>/scripts/timing.py <work> report` (minutes per stage, total time, slowest stage).
- With a brand guide, list the brand assumptions (what the guide was silent on and the neutral choice made) and confirm the page passed qa.py's brand check.
- On a lorem page, say first that it uses placeholder text and is a design draft, not ready to launch; skip the reading grade and the compliance checklist, and offer to have page-content write the real words next.
- Finish with a short note: the kit version, the design direction in one line (palette, type pairing, the memorable element), the block plan used (and the benchmark ideas it borrowed, if any), the page's reading grade, the list of `[placeholders]` the practice must fill, and any compliance flags.
- Offer next steps as options, for example: another tweak round, A/B variant of the hero, another page from the sitemap, or a dark theme.

---

## 9. Versioning

This kit uses version numbers in the form MAJOR.MINOR.PATCH. The current version is at the top of this file.

- **Patch (1.0.0 to 1.0.1):** small updates. Wording, clearer instructions, new answer options, swap-table entries, bug fixes in the scripts. How the kit works does not change.
- **Minor (1.0.1 to 1.1.0):** new things added without changing the flow. A new block, a new page recipe, a new check.
- **Major (1.x to 2.0.0):** bigger updates that change how the kit works. A new intake flow, a new design system, a new output format, removed or renamed steps.

Every time the kit is changed:

1. Pick the bump using the rules above, and run `python3 <kit>/scripts/build_packs.py` so the reading packs match the rules (`--check` must pass). If unsure between two, ask the user.
2. Update `VERSION` and the version line at the top of this file.
3. Add a line to `CHANGELOG.md`, newest first: version, date, one short sentence on what changed.
4. Never change an old changelog line.
5. Publish a GitHub release tagged `vX.Y.Z`. The `/create-page` loader only uses published release tags, so unreleased edits never reach the team.
