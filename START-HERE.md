# Macallan Page Builder: START HERE

You are reading the page builder kit. If the user asked for a page and you were sent here (by the `/create-page` loader skill, a pasted repo link, or Claude Code opened in this repo), you are the **orchestrator**: follow this file from section 0.

**Kit version 6.4.0** (see `VERSION` and `CHANGELOG.md`)

Builds landing pages and website pages for healthcare practices (home, specialty, condition, location, provider, about, insurance, testimonials, contact). Pages are assembled from the Macallan block library below, art-directed with the `frontend-design` approach (a distinct visual identity per practice, no generic AI look), built as one plain HTML file on Material Design logic (no build tools or installs), and written at a 5th-grade reading level, because plain copy converts best.

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
- Audience: ...             - Main action (CTA words): ...   - Second action: ... or none
- Message 1: ...            - Message 2: ...                 - Message 3: ...
- Keyword: ...  - Traffic: ...  - Lead flow: ...  - Proof available: ...   (conversion mode)
- Plan approval: approved plan below / build directly
- Review mode: full review / quick draft (automated checks only)
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

- **Written content** (the user asked for it): start the **page-content** agent with the brief path. It does the content parts of section 2, the block plan (section 3) and every word (section 4), writes `<work>/content/plan.md` and `<work>/content/content.json` (4.1), runs `readability.py`, and returns `CONTENT REPORT`. It also handles every later content change: copy change requests (`CONTENT FIX REPORT`) and tweak-round text (`CONTENT TWEAK REPORT`). Continue the same agent with SendMessage when you can, so it keeps its context. The orchestrator never writes copy.
- **Placeholder content** (the default unless the user asks for words): page-content is not started. The orchestrator writes only `plan.md` (block plan from 3.2 and 3.3 for the page type and goal, block slots from `blocks-lite/`) and the designer fills every slot with lorem ipsum as in `rules/copy.md` 4.2. No `content.json`, no `readability.py`. If the user later asks for real words, start page-content then; the designer swaps the text in with targeted edits.

Record the choice as `Content: written / placeholder` in the brief. "Content owner" in this kit means page-content.

### 0.4 The agents' instructions

Each agent's full mode (inputs, what to do, report format, fix and tweak rounds) is in its role file: `agents/content.md`, `agents/designer.md`, `agents/qa.md`, plus the short shared section in `agents/shared.md`. Agents read only those files and the rules their role file lists, never this file. Their reports: `CONTENT REPORT` / `CONTENT FIX REPORT` / `CONTENT TWEAK REPORT`, `DESIGN REPORT` / `DESIGN FIX REPORT` / `DESIGN TWEAK REPORT` (with `COPY CHANGE REQUEST`s), and the QA report in `rules/qa.md` 6.3.

### 0.5 Stage timing

Record the start and end of every stage so the real bottleneck shows: `python3 <kit>/scripts/timing.py <work> start <stage>` and `... end <stage>`, with the stages `intake`, `wireframe`, `content`, `design`, `qa`, `fixes`, `tweak` and `deliver` (repeat runs are numbered automatically). The intake starts before the work folder exists: note `date -Iseconds` when you start it and record it later with `--at`. Each call rewrites `<work>/timing.md` (one row per stage run, totals per stage, the total time and the slowest stage). `timing.py <work> report` prints it for the final summary (section 7).

### 0.6 Orchestration: the relay

Time every step (0.5).

1. **Intake** (section 1). If the user chose to approve the plan first, get `plan.md` first: from page-content, told to return only `plan.md` (written content), or write it yourself (placeholder content). Then run `python3 <kit>/scripts/wireframe.py <work>/content/plan.md --title "<Practice> <page type>"`, send `<work>/wireframe.html` to the user (section 7) together with the short plan list, and ask with a guided question (Approve plan · Change something). If the user changes the plan, update `plan.md` the same way, rebuild the wireframe and ask again. Record the approved plan in the brief.
2. **Brief:** write `brief.md` (0.2), including the review mode from the intake (full review by default) and the content choice (0.3).
3. **Content:** only if the user asked for written content, start `page-content` with the brief path and wait for its `CONTENT REPORT`; if `BRIEF INCOMPLETE`, ask the user and restart. With placeholder content, write only `plan.md` and go straight to design (0.3).
4. **Design:** start `page-designer` with the brief path and the content files (only `plan.md` with placeholder content). If it returns copy change requests, send them to page-content (continue the same agent with SendMessage if available, otherwise start a new one with the brief, content files and requests), then send the updated content back to page-designer. Placeholder pages have no copy change requests. At most 2 copy round trips; after that, the designer adapts the layout to the copy.
5. **First draft to the user, right away:** as soon as `<work>/index.html` exists, send it to the user (as in section 7) with the line "First draft, QA is running." Do not wait for the review.
6. **Quick draft mode** (the user chose "Quick draft" in the intake): skip steps 7 to 9. Run the tweak round (step 10), then deliver the page with the designer's automated check results (qa.py and readability.py) and say clearly that no independent review ran.
7. **QA:** start a **fresh** `page-qa` with only the preview path, the brief path, the material paths and the automated results path (`<work>/qa/auto.json`, the designer's final full qa.py run; page-qa reuses it when the page has not changed, so qa.py runs once). Never pass the other agents' reports or notes.
8. **Fix routing:** if the verdict is FAIL, split the findings by owner:
   - **page-content:** area A (copy, brief, reading level, CTA words), area B wording (claims, disclaimers, placeholders, form note), area F order and plan.
   - **page-designer:** areas C (design quality), D (mobile), E (ADA), area B items that are build issues (tracking scripts, form markup, legal links missing from the footer layout).
   - A finding that needs both goes to page-content first, then page-designer. On a placeholder page there are no copy findings; plan findings (area F) are yours to fix in `plan.md`.
   - Send **minor** and **mechanical** findings too (6.3): the owner fixes them directly, and they are not re-reviewed.
   Content fixes run first, then the designer updates `index.html` with the new `content.json` plus its own fixes. **Fixes are edits, not rebuilds:** the designer changes only the parts of `index.html` the findings name, with targeted edits, and finishes with one full qa.py run to `<work>/qa/auto.json`.
9. **Re-review, only for blockers:** if the round had blocker findings, start a **new** page-qa with the preview, brief, material and automated results paths plus the list of blockers and judgment majors from that round. It re-checks only those findings plus the automated results (6.1). With no blockers, there is no re-review: the fixes stand on the owners' checks and are reported at delivery as fixed without re-review. **Default is 1 fix round.** Run a second round only if blockers remain; remaining majors are reported at delivery.
10. **Tweak round** (0.7): once the design is done, give the user the tweak page to fine-tune it, and apply what they send back.
11. **Deliver** (section 7) with the final QA report. If blockers or majors remain, say so first and list them; never present a failing page as passing. Delivery is not done until the page is published or the user was told why it couldn't be.

Tell the user one line when each stage starts (writing content, designing, first draft sent, reviewing, fixing, tweaking); keep the task list updated.

**Starting the agents.** If named agents `page-content`, `page-designer` and `page-qa` are installed (Claude Code opened in this repo loads them from `.claude/agents/`), use them. Otherwise start `general-purpose` agents with the prompt: "Read `<kit>/agents/shared.md` and `<kit>/agents/content.md` and follow them. Kit folder: `<kit>`. Brief: `<work>/brief.md`." (or `designer.md`, `qa.md`), always passing the absolute kit and work paths. If no agent tool exists at all, do each stage yourself in order, keeping the same files and lane rules, do the QA as a separate clean pass reading only the page, brief and materials, and tell the user the review was not independent.

### 0.7 The tweak round

After the design is done (the QA verdict in step 9, or the build in quick draft mode), the user gets the page with a **tweak bar** to finish the design themselves: palettes, a new main colour, single colours with a live contrast check, font pairings or any Google font, sizes, spacing, corners, shadows, page width and button shape; and per block: move, hide, swap to another version, change the background, edit text and leave notes. Skip this round in unattended sessions.

1. **Make the tweak page:** `python3 <kit>/scripts/tweakbar.py <work>/index.html` writes `<work>/tweak.html` (it picks up `alternates.html` and `tweak-options.json` from the work folder; add `--seeds "#HEX"` for palettes made from extra brand colours). If it prints warnings about blocks or alternates, send them to page-designer to fix first. `index.html` is never changed by this.
2. **Show it:** in Claude Code, open it in the user's browser (`open <work>/tweak.html` on macOS, `xdg-open` on Linux) and give the absolute path. In other clients, publish it as its **own** private artifact titled "<Practice> <page type> tweaks" (icon "settings"), never in place of the page's artifact; later rounds republish to the same tweak artifact. Say in one line how it works: change what you like, then open **Finish** and press **Copy changes**, and paste the result here (or download `tweaks.json` and give its path). Their changes are saved in that browser, so they can close it and come back.
3. **Ask** with a guided question: "Tweak the design" · "Looks good, deliver". If they pick deliver, go to section 7.
4. **Receive:** save what they paste to `<work>/tweaks.json` (round 2: `tweaks-2.json`, and so on). Check its `page_hash` against the current `index.html` (`python3 -c "import hashlib,sys;print(hashlib.sha1(open(sys.argv[1],'rb').read()).hexdigest()[:12])" <work>/index.html`); if they differ, the tweaks were made on an older version: say so and apply them carefully. Show the `summary` lines back in one short list.
5. **Confirm brand changes:** if `brand_overrides` is not empty (the brief fixed the brand colours or fonts and the user changed them), ask with a guided question (Use my change · Keep the brand) before routing.
6. **Route** (same lanes as 0.6):
   - **page-content first** (written content only): `copy_edits` (as copy change requests: keep the user's meaning, grade 5.9 or lower and compliance; if a change cannot be kept as written, use the closest version that passes and say why), `blocks.order`, `blocks.hidden` (remove those blocks from `plan.md` and `content.json`), `blocks.variants` (change the block ID in `plan.md` and `content.json`, and fill any slots the new version has that the content lacks), and notes that ask for different words. page-content returns `CONTENT TWEAK REPORT`.
   - **Placeholder content:** there is no content owner; page-designer applies `copy_edits` as written (the user's own words) along with everything else, and the summary notes that those words were not graded.
   - **page-designer next:** everything in `design`, `blocks.variants` and `blocks.backgrounds`, design notes, `contrast_failures`, and the updated content files. It applies them as in 5.10 with targeted edits and returns `DESIGN TWEAK REPORT`.
7. **Check:** the designer's 6.1 run is always required. In full review mode, if blocks or words changed (order, hidden, variants, copy edits), start a **fresh** page-qa limited to the changed blocks plus the automated results (`<work>/qa/auto.json`); changes to the design only (colours, fonts, sizes, shape, backgrounds) need 6.1 only. Route any findings as in 0.6 step 8.
8. **Next round:** rebuild `tweak.html` from the new `index.html` (its saved changes start fresh because the page changed), show it again and ask again. There is no round limit; the user decides when it is done. Then deliver (section 7) and mention what each tweak round changed.

---

## 1. Intake (gate)

Note the start time first (`date -Iseconds`) for the stage timing (0.5).

Ask with **guided questions**: the `AskUserQuestion` tool, which shows clickable options and always lets the user type their own answer ("Other"). Ask in rounds, not as one long text message. Do not plan, write or build until Round 1 and Round 2 are answered.

Before asking, read anything already in the request (logo, URL, notes) and tailor the options to it: use the practice's specialty, city and services in the examples. Skip any question the request already answers clearly, and say what you took from it in one line.

**Round 1: page basics (one `AskUserQuestion` call, 4 questions)**

| Header | Question | Options (2 to 4, tailor them) |
|---|---|---|
| Page type | What kind of page are we building? | Landing page (for ads) · Home page · Treatment page · Other website page (location, provider, about, insurance, testimonials, contact: user types it) |
| Audience | Who is this page for? | New patients with [main condition] · New patients in [city] · Existing patients · Referring doctors |
| Main action | What is the one action visitors should take? | Book a visit · Call now · Schedule a conversation · Check my insurance |
| Content | Should I write the page's words, or use placeholder text so you get the design faster? | Placeholder text (lorem ipsum), fastest (Recommended) · Write the content (adds a few minutes) |

The page goal = audience + main action (+ page type). If the user wants a second action, they can type it under "Other" on Main action, or ask in Round 2.

**Placeholder content:** when the user picks placeholder text, the page uses lorem ipsum in place of the copy (`rules/copy.md` 4.2) and there is no content stage. Round 2 then asks only "Plan first?" plus, in conversion mode, Lead flow and Proof from Round 2b (they shape the blocks); skip the message questions, Keyword and Traffic.

**Round 2: top 3 messages in order, and plan approval (one `AskUserQuestion` call, 4 questions)**

The fourth question is plan approval:

| Header | Question | Options |
|---|---|---|
| Plan first? | Do you want to approve the block plan before I build? | Show me the plan first (Recommended) · Go straight to the finished page |

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
| Materials | Which of these can you share? Attach them in your next message. (multiSelect) | Logo · Brand guide (colors, fonts, voice) · Compliance rules (claims, disclaimers, consent) · Photos |
| Current site | Does the practice have a current website? | Yes (type the URL under Other) · No current website |
| Benchmark | Do you have a website example to use as a benchmark? | Yes (type the URL under Other) · No benchmark |
| Review | Speed or full review? (optional) | Full review (Recommended) · Quick draft: one build plus automated checks, no review agent |

Note in the Materials question that anything not shared becomes a `[placeholder]` and practice facts (phone, locations, hours, providers, insurance, real reviews) can be typed or pasted. The Review question is optional: if it is skipped or unanswered, use Full review. Skip any question the request already answers. If the user picks materials, wait for the attachments, then copy them into `<work>/materials/` (0.2); if they pick none or type "none", continue (the logo still comes from the current website when there is one). If they say "Yes" to a site without giving the URL, ask for it in one short line.

**Rules**

- Every round must be answered before the next. Required answers are page type, audience, main action, the content choice (placeholder if skipped) and all 3 messages (plus Round 2b in conversion mode; its defaults apply if the user skips it). With placeholder content the messages are not required. If an answer is vague, ask one short follow-up (another guided question if possible).
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
