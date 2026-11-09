# Rules: QA and review (section 6)

## 6. QA and review

page-qa runs all of this; page-designer runs 6.1 on its own build and page-content runs `readability.py` on `content.json` before handing off. Never report a check as done unless it was actually run.

### 6.1 Automated checks

axe-core ships with the kit at `scripts/vendor/axe.min.js`, so there is nothing to install for it. Playwright is usually installed; if not: `pip install --break-system-packages playwright && python3 -m playwright install chromium`.

1. Run `python3 <kit>/scripts/qa.py <work>/index.html --axe <kit>/scripts/vendor/axe.min.js --brand-fonts "<brand fonts from the brief>"` (leave `--brand-fonts` out when the brief names none). It checks 320, 390, 768, 1024 and 1440px for overflow, small tap targets and small input text; runs axe-core for WCAG 2.2 A/AA; tabs through the page for focus order and visible focus; checks the logo in the header and the footer at 390 and 1440px (an `img`, `svg` or `.wordmark` that is visible, at least 24px tall and has 3:1 contrast against its background); reports loaded fonts, the phone first screen (H1 and actions), CTA labels, em dashes, block IDs and the file size; checks alignment at 390 and 1440px (edge near-misses 1 to 12px apart, content overlapping content in another section, rows wider than their text column, and at 1440px items in one row whose tops differ by more than 2px) and style (uppercase on buttons, `a.btn` and nav links, main fonts from the 5.3 cliché list unless passed with `--brand-fonts`); saves screenshots at 390 and 1440px (plus the 390 x 844 phone first screen).
2. Run `python3 <kit>/scripts/readability.py <work>/index.html`. The copy is in the HTML itself, so it grades the page directly.

### 6.2 Review areas

Look at every screenshot (desktop, 390px, phone first screen) and read the source. Then check each area:

**A. Copy and brief**
- Reading grade 5.9 or lower for every block and the page; no sentence over 15 words; medical terms explained.
- H1 says Message 1 (in conversion mode: the offer in the keyword's words, with Message 1 right under it). Messages 2 and 3 appear next, in order.
- Primary CTA in the hero, mid-page and at the end, with identical words; at most 2 distinct actions.
- No em dashes; none of the generated-page tells from section 4; buttons verb-first, sentence case.

**B. Compliance** (the client's documents win)
- No guaranteed outcomes ("cure", "100%", "pain-free for life").
- No invented facts: stats, reviews, ratings, awards, credentials, insurance names, hours. Every unknown is a visible `[placeholder]`.
- Testimonials and before/after only if real, approved and consented, with "Results vary." nearby; FTC note if reviews were incentivized.
- Forms ask only what is needed; no free-text symptom fields unless allowed; "Please don't include medical details" and privacy link; unchecked TCPA consent box if SMS is used; submit target marked `<!-- HIPAA-compliant form endpoint required -->`.
- No third-party tracking scripts; flag pixels on form or condition pages.
- Footer legal links: Privacy policy, Notice of privacy practices (HIPAA), Accessibility, Non-discrimination notice, Terms. Medical disclaimer in conversion mode.
- Provider names and credentials exactly as given; "Medically reviewed by" only with a real reviewer.

**C. Design quality**
- Brand fidelity: colors, fonts and voice match the brand guide (or the current website); the benchmark did not drive the look.
- Logo: the real logo from the brief (or a text wordmark only when the brief says `Logo: none`) in the header and the footer, visible, at least 24px tall, 3:1 contrast against its background (qa.py `logo`), with `alt="[Practice name] logo"`; a light logo is never on white. A missing or invisible logo is a **major** finding.
- Typography (5.5): brand fonts actually loaded, one scale used throughout, clear heading levels, balanced headline wraps with no lone last word, body lines around 45 to 75 characters, no pale, thin or tiny text, uppercase only on short labels.
- Art direction (5.2 to 5.6): one clear memorable element; brand color fields and the gradient moment are present; nothing from the cliché list in 5.3; asymmetry with clear alignment; no fluff padding or doubled section spacing; shadows wide and transparent (or per brand); no stock component look (default all-caps buttons, default browser controls, tight dark elevations).
- Alignment: every offset snaps to a grid line or named edge; planned overlaps only; rows match their column. qa.py `alignment` lists near-misses, overlaps and wide rows.
- Row tops: sibling items in one row (steps, cards, stats, list items) share a top edge within 2px on desktop; steps show sequence with a connecting line or arrow, never a vertical stagger (qa.py `alignment.row_tops_w1440`).
- No uppercase on buttons, `a.btn` or nav links (qa.py `style.uppercase_buttons_and_nav`), and no block styles copied from `blocks/`. Cliché main fonts are flagged by qa.py `style`; a cliché font is fine only when the brief names it as the brand font.
- Restraint: if an icon, border, shadow, label, shape or container can be removed without losing meaning, it is a finding.
- A conversion page is never plainer than a regular page would be.

**D. Mobile and responsive**
- No horizontal overflow at any width; no clipped controls, crowded columns or overlaps that hide text.
- Phone first screen (390 x 844) shows the H1, the who line and the primary CTA in conversion mode.
- Layout recomposed for mobile (not just shrunk); sensible stacking order; important images keep useful size.
- `index.html` about 60 KB or less, before images and video (qa.py reports the file size).

**E. ADA (WCAG 2.2 AA)**
- axe-core: zero critical or serious violations; list moderate ones.
- Keyboard: every link, button and field reachable by Tab in a logical order, focus always visible, skip link works, no keyboard traps (accordion, tabs, dialog, mobile menu, quiz).
- Contrast AA for text, buttons, captions and text on photos (check the real screenshots, not just tokens).
- Reflow at 320px with no loss of content; text resizes to 200% without breaking.
- Every image has meaningful alt text (decorative images `alt=""`); video has a transcript link.
- One H1, headings in order, landmarks (`header`, `nav`, `main`, `footer`), page `lang` and `title`.
- Form fields have visible labels; errors say what is wrong and how to fix it; required fields are marked in text, not color alone.
- Tap targets at least 24px (WCAG 2.2 minimum) and 44 to 48px for main actions; `prefers-reduced-motion` respected; no meaning carried by color alone; link text makes sense out of context.

**F. Conversion mode only** (section 3.4)
- Recipe order respected; FAQ below the conversion zone; keyword block below the fold; form type matches the lead flow; final CTA matches the hero.

### 6.3 QA report format (page-qa returns exactly this)

```
QA REPORT  (create-page vX.Y.Z)
Verdict: PASS | FAIL        Round: <n>
Summary: <2 sentences>

Findings
| ID | Severity | Area | Block | Problem | Evidence | Fix |
|----|----------|------|-------|---------|----------|-----|
| Q1 | blocker  | B    | M26-B | ...     | ...      | ... |

Passed: <areas or checks that passed>
Not checked: <anything that could not run, and why>
```

**Severity**
- **Blocker:** compliance or legal risk (invented facts, guarantees, missing required disclaimer, PHI risk), axe critical or serious, keyboard trap, page broken or overflowing at any width, H1 or CTA missing from the phone first screen in conversion mode, reading grade over 5.9.
- **Major:** brief not followed (messages, CTA words, action count), alignment near-misses or unplanned overlaps (qa.py `alignment`), row items whose tops differ by more than 2px on desktop, uppercase on a button, `a.btn` or nav link, logo missing, invisible, under 24px or under 3:1 contrast in the header or footer, brand font missing without a flag, a cliché from 5.3, contrast or focus issues outside axe, clearly plain or template-like design, mobile layout poorly recomposed.
- **Minor:** polish (wraps, spacing, small inconsistencies, optional refinements).

**Verdict:** FAIL if there is any blocker or major finding; otherwise PASS (minors listed for the record).

The Area column lets the orchestrator route each finding to its owner (0.6): A and B wording to page-content, C, D, E and B build issues to page-designer.
