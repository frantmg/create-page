# Macallan Page Builder: START HERE

You are reading the page builder kit. If the user asked for a page and you were sent here (by the `/create-page` loader skill, a pasted repo link, or Claude Code opened in this repo), you are the **orchestrator**: follow this file from section 0.

**Kit version 6.1.1** (see `VERSION` and `CHANGELOG.md`)

Builds landing pages and website pages for healthcare practices (home, specialty, condition, location, provider, about, insurance, testimonials, contact). Pages are assembled from the Macallan block library below, art-directed with the `frontend-design` approach (a distinct visual identity per practice, no generic AI look), built as one plain HTML file on Material Design logic (no build tools or installs), and written at a 5th-grade reading level, because plain copy converts best.

This kit runs as a relay: the **orchestrator** (you, in the user's conversation) runs the intake and the relay, the **page-content** agent writes the plan and every word, the **page-designer** agent designs and builds, and the **page-qa** agent reviews independently. Section 0 says who does what. Do not skip the intake gate.

0. How this runs (roles, brief, the relay, fix routing)
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
| 0, 1, 7, 9 | `START-HERE.md` (this file) |
| 2 | `rules/materials.md` |
| 3 (3.1 to 3.4) | `rules/blocks-and-plan.md` |
| 4 | `rules/copy.md` |
| 5 (5.1 to 5.9) | `rules/design-build.md` |
| 6 (6.1 to 6.3) | `rules/qa.md` |
| 8.1 / 8.2 / 8.3 | `scripts/readability.py` / `scripts/m3_scheme.py` / `scripts/qa.py` |
| 8.5 | `scripts/logo.py` (trims, resizes and embeds the logo; reports light or dark and its main color) |
| 8.4 | `templates/page.html` (copy it to `<work>/index.html`) |
| 8.6 | `scripts/wireframe.py` (stacks the planned blocks from `blocks/` into `<work>/wireframe.html` for plan approval) |
| axe-core | `scripts/vendor/axe.min.js` (bundled, with its `LICENSE`) |
| Block reference HTML | `blocks/<ID>-*.html` (structure and content reference only; never their styling) |
| Agent roles | `agents/content.md`, `agents/designer.md`, `agents/qa.md` |

Run scripts from the kit, for example `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --brand-fonts "Brand Font"`. Never edit the kit while building a page; client work goes in the work folder.

---

## 0. How this runs

### 0.1 Roles

The page is made by a relay: content first, then design, then an independent review. Each agent owns its lane and never edits another's work.

| Role | Who | Owns | Hands off | Never |
|---|---|---|---|---|
| Orchestrator | The main conversation (when the user runs `/create-page` or asks for a page) | Section 1 intake, the brief, running the relay and fix routing (0.6), delivery (section 7) | Brief to page-content | Writes copy or builds the page when the agents are available |
| page-content | Agent (`page-content`) | Sections 2 (facts, compliance, current site, benchmark), 3 and 4: block plan, every word, compliance wording, placeholders | `content/plan.md` + `content/content.json` | Touches layout, styles or code |
| page-designer | Agent (`page-designer`) | Sections 2 (brand, logo, current site look), 5 and 6.1: design plan, build, mobile, ADA build quality | `<work>/index.html` | Changes any word; it sends a copy change request instead |
| page-qa | Agent (`page-qa`), fresh for every review | Section 6 in full | QA report | Edits anything, sees the other agents' notes |

If you were started by the user (or by `/create-page`), you are the orchestrator. If your prompt says you are page-content, page-designer or page-qa, follow 0.3, 0.4 or 0.5.

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
- Brand fonts: ... or none given
- Logo: <absolute path in <work>/materials/> (attached / from the current website) or none
- Other materials (absolute paths in <work>/materials/): brand guide ..., compliance docs ..., photos ... (or none)
- Current website: URL or none        - Benchmark website: URL or none
- Practice facts given by the user: name, phone, locations, hours, providers, insurance, reviews
- Approved block plan (if the user approved one): ...
- Work folder: <absolute path>
```

### 0.3 page-content mode

Skip section 1. Read the brief; if a required field is missing, return `BRIEF INCOMPLETE` with the list and stop. Do the content parts of section 2 (practice facts, compliance documents, current website facts and voice, benchmark structure takeaways), then section 3 (block plan; use the approved plan if the brief has one) and section 4 (every word). Write two files in `<work>/content/`:

- `plan.md`: the ordered block list, one block per line starting with its number and full block ID including the variant (for example `2. M01-B: Message 1 · Seen this week`), with the message it carries; benchmark ideas used go on lines after the list. `scripts/wireframe.py` reads this list.
- `content.json`: every word on the page, in this shape:

```json
{
  "meta": { "page_title": "", "meta_description": "", "cta_primary": "", "cta_secondary": "", "keyword": "" },
  "blocks": [
    { "id": "M01-B", "message": "1", "slots": { "h1": "", "who": "", "bullets": [""], "cta": "", "image_brief": "Photo: doctor with patient, 4:5" } }
  ],
  "legal": { "disclaimer": "", "before_after_disclosure": "", "form_note": "Please don't include medical details." },
  "placeholders": ["[City]"],
  "compliance_notes": ["what you could not confirm and why"]
}
```

Slot names follow the block's content slots in 3.1 (headline, bullets, steps, faq items, and so on). Image needs go in `image_brief` slots so the designer knows what each photo should show. Run `scripts/readability.py` on `content.json` and fix every block marked `FIX`. Return:

```
CONTENT REPORT
Files: <plan.md path>, <content.json path>
Block plan: <ordered block IDs and the message each carries>
Reading grade: <page grade, every block OK>
Placeholders: <list>     Compliance notes: <list>
```

In a fix round you receive findings or copy change requests. Change only what they ask, keep the grade at 5.9 or lower, and return `CONTENT FIX REPORT` (each finding or request ID, what changed, or why not).

### 0.4 page-designer mode

Skip sections 1, 3 and 4. Read the brief, `plan.md` and `content.json`. Do the design parts of section 2 (logo, brand guide, the current website's look), run `scripts/logo.py` on the brief's logo, then section 5: design plan, review, build. Write `<work>/index.html` from `templates/page.html` and the blocks, copying every word from `content.json` exactly; never type, cut or reword copy in the markup. If the copy does not fit the design (a headline too long for the hero, too many bullets for a block, a missing slot), do not change it: return a `COPY CHANGE REQUEST` with the block ID, slot, the problem and the limit (for example "M01-B h1: 9 words wraps to 4 lines on 390px; max 6 words"). Run the automated checks in 6.1 and fix design-side failures. Return:

```
DESIGN REPORT
Preview: <path to <work>/index.html>   Size: <KB>   Screenshots: <paths>
Design direction: <palette, type pairing, the memorable element>
Automated checks: <pass/fail summary from qa.py>
Copy change requests: <list or none>
Logo: <embedded image or text wordmark; light or dark; the background it sits on>
Flags: <font, asset or brand issues the designer could not resolve>
```

In a fix round, fix the design, mobile and ADA findings sent to you in `<work>/index.html`, bring in any updated copy from `content.json`, rerun 6.1, and return `DESIGN FIX REPORT` (each finding ID, what changed, or why not). Minor findings are fixed directly and are not re-reviewed.

### 0.5 page-qa mode

You review a page you did not make. You get the preview path, the brief and the client's materials, nothing else. Stay read-only (scratch files in `/tmp/qa/`). Follow section 6 completely and return the report in 6.3. In a re-review you also get the list of findings that failed last round: re-check only those, plus the automated checks in 6.1, and return the same report format.

### 0.6 Orchestration: the relay

1. **Intake** (section 1). If the user chose to approve the plan first, start page-content with an instruction to return only `plan.md`. Then run `python3 <kit>/scripts/wireframe.py <work>/content/plan.md --title "<Practice> <page type>"`, send `<work>/wireframe.html` to the user (section 7) together with the short plan list, and ask with a guided question (Approve plan · Change something). If the user changes the plan, have page-content update `plan.md`, rebuild the wireframe and ask again. Record the approved plan in the brief.
2. **Brief:** write `brief.md` (0.2), including the review mode from the intake (full review by default).
3. **Content:** start `page-content` with the brief path. Wait for its `CONTENT REPORT`. If `BRIEF INCOMPLETE`, ask the user and restart.
4. **Design:** start `page-designer` with the brief path and the two content files. If it returns copy change requests, send them to page-content (continue the same agent with SendMessage if available, otherwise start a new one with the brief, content files and requests), then send the updated content back to page-designer. At most 2 copy round trips; after that, the designer adapts the layout to the copy.
5. **First draft to the user, right away:** as soon as `<work>/index.html` exists, send it to the user (as in section 7) with the line "First draft, QA is running." Do not wait for the review.
6. **Quick draft mode** (the user chose "Quick draft" in the intake): stop here. Deliver the page with the designer's automated check results (qa.py and readability.py), say clearly that no independent review ran, and skip steps 7 to 9.
7. **QA:** start a **fresh** `page-qa` with only the preview path, the brief path and the material paths. Never pass the other agents' reports or notes.
8. **Fix routing:** if the verdict is FAIL, split the findings by owner:
   - **page-content:** area A (copy, brief, reading level, CTA words), area B wording (claims, disclaimers, placeholders, form note), area F order and plan.
   - **page-designer:** areas C (design quality), D (mobile), E (ADA), area B items that are build issues (tracking scripts, form markup, legal links missing from the footer layout).
   - A finding that needs both goes to page-content first, then page-designer.
   - Send **minor** findings too: the owner fixes them directly, and they are not re-reviewed.
   Content fixes run first, then the designer updates `index.html` with the new `content.json` plus its own fixes.
9. **Re-review:** start a **new** page-qa with the preview, brief and material paths plus the list of blocker and major findings that failed. It re-checks only those findings plus the automated checks (6.1). **Default is 1 fix round.** Run a second round only if blockers remain; remaining majors are reported at delivery.
10. **Deliver** (section 7) with the final QA report. If blockers or majors remain, say so first and list them; never present a failing page as passing. Delivery is not done until the page is published or the user was told why it couldn't be.

Tell the user one line when each stage starts (writing content, designing, first draft sent, reviewing, fixing); keep the task list updated.

**Starting the agents.** If named agents `page-content`, `page-designer` and `page-qa` are installed (Claude Code opened in this repo loads them from `.claude/agents/`), use them. Otherwise start `general-purpose` agents with the prompt: "Read `<kit>/agents/content.md` and follow it. Kit folder: `<kit>`. Brief: `<work>/brief.md`." (or `designer.md`, `qa.md`), always passing the absolute kit and work paths. If no agent tool exists at all, do each stage yourself in order, keeping the same files and lane rules, do the QA as a separate clean pass reading only the page, brief and materials, and tell the user the review was not independent.

---

## 1. Intake (gate)

Ask with **guided questions**: the `AskUserQuestion` tool, which shows clickable options and always lets the user type their own answer ("Other"). Ask in rounds, not as one long text message. Do not plan, write or build until Round 1 and Round 2 are answered.

Before asking, read anything already in the request (logo, URL, notes) and tailor the options to it: use the practice's specialty, city and services in the examples. Skip any question the request already answers clearly, and say what you took from it in one line.

**Round 1: page basics (one `AskUserQuestion` call, 4 questions)**

| Header | Question | Options (2 to 4, tailor them) |
|---|---|---|
| Page type | What kind of page are we building? | Landing page (for ads) · Home page · Treatment page · Other website page (location, provider, about, insurance, testimonials, contact: user types it) |
| Audience | Who is this page for? | New patients with [main condition] · New patients in [city] · Existing patients · Referring doctors |
| Main action | What is the one action visitors should take? | Book a visit · Call now · Schedule a conversation · Check my insurance |
| Plan first? | Do you want to approve the block plan before I build? | Show me the plan first (Recommended) · Go straight to the finished page |

The page goal = audience + main action (+ page type). If the user wants a second action, they can type it under "Other" on Main action, or ask in Round 2.

**Round 2: top 3 messages, in order (one `AskUserQuestion` call, 3 questions)**

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

- Every round must be answered before the next. Required answers are page type, audience, main action and all 3 messages (plus Round 2b in conversion mode; its defaults apply if the user skips it). If an answer is vague, ask one short follow-up (another guided question if possible).
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
- Wireframes (`<work>/wireframe.html` from `scripts/wireframe.py`) are not published; send them with SendUserFile (display 'render'). If SendUserFile is not available (for example in the terminal), give the absolute path and open the file in the user's browser (`open <path>` on macOS, `xdg-open` on Linux). Say in one line that the wireframe shows block order and layout with sample words, not the final design or copy.
- For a website: publish each page as its own artifact and list the links in the sitemap line.
- Include the final QA report: verdict, number of fix rounds (or "Quick draft: automated checks only, no independent review"), what was fixed (and by which agent), and any open findings. If the verdict is still FAIL, say so first.
- Send the screenshots only if the user wants a quick look.
- Add `<!-- Built with create-page vX.Y.Z -->` (the kit version from `VERSION`) as the first line inside `<head>` of every page's `index.html` (`templates/page.html` already has the line; set the version).
- In conversion mode, also give: a pre-launch compliance checklist (disclaimers, before/after disclosures and consent, review authenticity, HIPAA-compliant form processing, no tracking pixels on the form without a BAA) for the team to tick before launch, and a message-match line (keyword → H1 → 2 or 3 matching ad headlines) so the ad and page stay aligned.
- Finish with a short note: the kit version, the design direction in one line (palette, type pairing, the memorable element), the block plan used (and the benchmark ideas it borrowed, if any), the page's reading grade, the list of `[placeholders]` the practice must fill, and any compliance flags.
- Offer next steps as options, for example: A/B variant of the hero, another page from the sitemap, or a dark theme.

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
