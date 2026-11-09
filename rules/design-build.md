# Rules: design and build (section 5)

## 5. Design and build (art direction, single-file HTML)

Owned by page-designer. Design every page as if the `frontend-design` skill is active (load it with the Skill tool when it is listed; the rules below summarize it). The goal is a page that looks made for this one practice, never a template. Material Design stays the logic underneath (color roles, contrast, state layers, accessible components), but the look is editorial and specific to the brand.

### 5.1 Ground it in the practice

Before designing, name in one line each: the practice's world (specialty, place, patients), the audience, and the page's one job. Distinct choices come from the subject: an orthopedic surgeon in Layton (movement, bone, mountains, athletes) should look nothing like a med spa in Scottsdale (skin, light, ritual) or a behavioral health clinic (calm, safety, plain talk). Use the brand guide, logo, photos and real practice facts throughout. Design decisions (color, type, imagery, shape) come from the brand guidelines first, then the current website; a benchmark site never drives the look.

### 5.2 Write a design plan, then review it

Before any code, write a short plan:

- **Color:** 4 to 6 named hex values (for example "Summit navy #0B2545", "Trail blue #1463FF", "Snowfield #F2F6FB"), built from the brand color and its tonal palette (`scripts/m3_scheme.py`). Say where each one is used.
- **Type:** the typefaces (brand fonts first) and their roles, plus the one type scale for this project, picked from the ranges in 5.5.
- **Layout:** one sentence and a small ASCII wireframe for the hero and for the overall page rhythm. Say how content aligns, and which benchmark structure ideas you used, if any. State every planned overlap (which element crosses into which section, and the space that section reserves for it).
- **Principles:** 2 or 3 lines on what makes this page unique, and the **one** memorable element where the boldness is spent (for example: a full-bleed brand gradient field behind the hero, a hero photo that breaks the grid, a distinctive display face set with a strong headline shape).

Then review the plan against the brief. If any part reads like the default you would make for any similar practice, change it and say what you changed and why. Check it against the cliché list in 5.3. Show the plan to the user only when they asked to approve the plan first; otherwise keep it in your working notes and build.

### 5.3 Clichés to avoid (unless the brand guide asks for them)

- Purple or violet gradients, purple-to-pink, and any gradient that is not built from the brand's own colors.
- Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Space Grotesk, Playfair Display, or system defaults as the main type.
- The SaaS card kit: content chopped into identical rounded cards, one radius on everything, the same soft grey shadow under each.
- A warm cream background (near #F4F1EA) with a serif display and a terracotta or clay accent (near #D97757).
- A near-black background with one acid-green or vermilion accent.
- Broadsheet layouts with hairline rules and zero radius everywhere.
- Template chrome: tracked all-caps eyebrows above every heading, "A · B · C" meta strings, "→" on every link, tinted near-black (#0B0B0B, #111) standing in for black, monospace for small labels.
- Big number + small label + gradient accent as the default hero.
- Numbered markers (01, 02, 03) on content that is not a sequence. Steps and timelines may be numbered; reasons and benefits may not.
- Fade-and-slide-up on every section, hover effects on every card.

### 5.4 Color and gradients

- The brand color is the seed. Run `scripts/m3_scheme.py "#HEX"` to get Material color roles (for accessible text and surface pairs) and the full tonal palettes (tones 0 to 100) of the brand, secondary, tertiary and neutral hues.
- Use color with intent, not timidly: at least one full-bleed section in a strong brand tone, and one gradient moment built only from brand tones (for example primary tone 20 to primary tone 50, or primary to tertiary), with optional fine grain (an inline SVG noise at low opacity) so it feels printed, not digital. Keep gradients to one or two big moments (hero field, final CTA band), never as decoration on every element.
- Neutrals come from the brand's neutral palette (slightly tinted toward the brand hue), not pure greys. True black is #000 only if the brand uses it.
- Every text and background pair meets WCAG 2.2 AA. Use the role pairs from `scripts/m3_scheme.py` (`on-primary` on `primary`, and so on) or check contrast.

### 5.5 Typography

**Fonts.** Use the approved brand fonts and verify that they load (`scripts/qa.py` lists the loaded families). If a brand font is unavailable, say so and propose a substitute; never swap an approved font silently. Keep the family count to one or two. When the brand names no fonts, pick one distinct pairing (Google Fonts) that fits the practice, and do not reuse the same pairing on every project:

| Feel | Display | Body | Good for |
|---|---|---|---|
| Warm, human | Fraunces (use its optical size and soft axis) | Hanken Grotesk | Family practice, women's health, pediatrics |
| Refined, quiet luxury | Instrument Serif | Instrument Sans | Aesthetics, plastics, med spa, dermatology |
| Energetic, athletic | Bricolage Grotesque (play with width) | Source Serif 4 | Orthopedics, sports medicine, PT, chiropractic |
| Trusted, institutional | Newsreader (large optical size) | Public Sans | Multi-specialty groups, surgery centers |
| Friendly, bright | Young Serif | Figtree | Dental, pediatrics, primary care |
| Calm, very readable | Literata | Atkinson Hyperlegible | Behavioral health, older audiences, eye care |

**Scale.** These are flexible starting ranges. Choose **one coherent scale per project** based on the font's proportions, the brand, content length and viewport, then reuse that small set of styles everywhere. Do not pick a different size for every module.

| Role | Desktop | Mobile | Line height |
|---|---|---|---|
| H1 / hero heading | 48 to 64px | 34 to 42px | 1.05 to 1.18 |
| H2 / section heading | 36 to 44px | 28 to 34px | 1.15 to 1.25 |
| H3 / module heading | 22 to 28px | 21 to 24px | 1.2 to 1.35 |
| H4 / supporting heading | 18 to 20px | 18 to 20px | 1.3 to 1.4 |
| Intro / lead | 19 to 21px | 18 to 19px | 1.5 to 1.65 |
| Body | 17 to 18px | 16 to 18px | 1.5 to 1.7 |
| Eyebrow | 12 to 14px | 12 to 13px | 1.3 to 1.5 |
| Caption / supporting note | 13 to 14px | 13 to 14px | 1.4 to 1.6 |
| Button label | 15 to 17px | 15 to 17px | 1.2 to 1.4 |

Put the chosen scale in the page's token block as CSS custom properties (for example `--text-h1`, `--text-h2`), with `clamp()` between the mobile and desktop values.

**Rules**
- Keep a visible difference between heading levels. Use semantic heading levels by content structure, independent of visual size.
- Use regular or medium weights when the font gives enough hierarchy. Reserve bold for emphasis; do not make every heading heavy by default.
- Body copy around 45 to 75 characters per line on desktop. Let lines get narrower on mobile; never shrink text to keep desktop wrapping.
- Aim for intentional headline shapes. Adjust text width and scale before adding manual line breaks. Avoid a lone last word and awkward short lines (`text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs).
- Tighten heading tracking slightly only when the font benefits. No cramped letters, clipped accents, or extra tracking in body copy.
- Uppercase and wider tracking only for short labels, used selectively, following the brand's capitalization conventions.
- Eyebrows are optional. Omit them when they repeat the heading.
- Do not rely on pale text, very thin weights or tiny type to look sophisticated.
- Sentence case for headings and buttons unless the brand says otherwise. Form input text at least 16px on mobile.

### 5.6 Layout, spacing and motion

- **Strong asymmetry:** a 12-column grid with uneven spans (7/5, 8/4, 5/7), offset starts, media that breaks the container edge, and overlaps (a photo under the headline, a form card overlapping two sections). Avoid centered, symmetric stacks except for one deliberate moment.
- **Zero fluff padding:** spacing comes from a scale tied to the body line-height (for example 0.5x to 6x). Each section gets the space its content needs, not one blanket section padding. No empty wrapper divs, no decorative spacers. Tight is fine; cramped is not.
- **Hierarchy over boxes:** separate content with scale, color fields and alignment before reaching for borders, cards or shadows. When cards are right (directories, provider grids), keep them flat and vary emphasis (one featured item larger) where the content allows.
- **Shadows:** follow the brand guide when it specifies shadows. Otherwise never use short, dark, tight shadows (like `0 1px 3px rgba(0,0,0,.3)` or stock component-library elevations). Use shadows that are **wider and more transparent**: a large blur, a soft downward offset, a negative spread so the edge fades, and low opacity (about 0.06 to 0.14), tinted with the darkest brand neutral instead of pure black. Starting points:
  - Soft (resting cards, panels): `0 12px 32px -8px rgb(<ink> / 0.08)`
  - Raised (forms, overlapping panels): `0 18px 48px -12px rgb(<ink> / 0.10)`
  - Floating (sticky bars, menus, dialogs): `0 24px 64px -16px rgb(<ink> / 0.12)`
  Use them only where a surface truly floats or overlaps; flat content stays flat. Set them once as `--shadow-soft`, `--shadow-raised` and `--shadow-float` in the token block (`templates/page.html`) so every block shares them.
- **Alignment:** keep the asymmetry, but make every position deliberate.
  - Every layout sits on a 12-column grid with one max width and gutter, set as tokens (`--grid-max`, `--grid-gutter`, `--col`; see `templates/page.html`). Place things with `grid-column` spans, not one-off margins.
  - Offsets and bleeds are welcome, but each one snaps to a named edge: a grid column line, the H1's top or baseline, or a section edge. An element never starts or ends at an arbitrary position.
  - When an element overlaps into the next section, that section reserves the space (padding or a matching column offset) so its content never sits under or beside the overlap by accident. State the overlap in the design plan (5.2).
  - Rows inside a column (proof row, dividers, button groups) match their column's width; stat items use equal columns.
  - Hero media is vertically anchored: either its top aligns with the eyebrow or H1 top, or it fills the hero height and bleeds by a set token amount (`--bleed`).
- **Mobile:** design the 390px view first. Keep asymmetry through bleed, offsets and type scale, not tiny columns.
- **Motion:** two moments at most that the user did not trigger: one orchestrated hero entrance (headline, media and CTA in one short sequence) and the CTA attention motion in conversion mode. Motion that answers an action (accordion opening, form step changing, video opening) is welcome. Respect `prefers-reduced-motion`.

### 5.7 Block treatments in HTML and CSS

Semantic HTML and the page's inline CSS do layout, spacing, type and color. Interactive parts use native elements first and small vanilla JS only when needed, restyled with the tokens so nothing looks like a stock widget.

**Blocks define structure and content slots only.** Never copy a block's `<style>`, class styles or inline styles into the page. Restyle every block from the page's token block. In particular, no `text-transform: uppercase` on buttons, headings or nav; uppercase is allowed only on eyebrows and short labels, and only if the brand uses it.

| Block | Treatment |
|---|---|
| Heroes (M01, M02) | Headline from the H1 range with a deliberate shape on the grid, media bleeding off one edge, brand color field or gradient behind. CTA is a `.btn` link with the unique CTA shape |
| Feature cards (M08) | Not three equal cards. An editorial list: large titles with short text on an asymmetric grid, or one featured item with two smaller ones; items in a row share one top line, never offset vertically |
| Stats (M10) | One stat larger in the display face (within the H1 to H2 range), the others smaller beside it, each with plain context; all stats share one top line in equal columns, never offset vertically |
| Steps (M11) | Real sequence, so numbers are allowed: display numerals (H2 size) in an `<ol>`; all steps share one top line and equal columns on desktop, stacked on mobile. Show the sequence with a thin connecting line or arrow between numerals, not by offsetting steps vertically. The section CTA sits centered under the steps or aligned to the grid's first column with the steps spanning the full width |
| Pull quote and reviews (M12, M26) | One large quote set in the display face in a `<blockquote>`; other reviews smaller in a scroll-snap row. Stars in a brand tone |
| Tabs (M13) | `role="tablist"` with buttons and the tabs script from `templates/page.html` (arrow keys, Home, End); vertical on desktop, scrollable on mobile, restyled indicator |
| Comparison (M14) | Plain `<table>` with a caption and the recommended column on a brand color field |
| FAQ (M31) | Native `<details>` and `<summary>` (keyboard accessible with no JS), no shadow, large question type, rules between items |
| Forms (M29, M30) | Native `<input>`, `<select>` and `<label>` styled with the tokens (custom radius, focus color, label style). Multi-step form: one `<fieldset>` per step with a progress bar and a few lines of JS. Quiz: large tappable option cards built on radio inputs |
| Video (M22) | Poster image with a play `<button>`; a native `<dialog>` opens the player, which loads only on click |
| Carousel and gallery (M23, M24) | CSS scroll-snap with previous and next buttons; no carousel library |
| Header and mobile bar (G1, G2, LP) | Thin custom header; the mobile menu script from `templates/page.html` (`aria-expanded`, Escape closes); sticky call/book bar on mobile |
| Insurance strip (M25) | Logos in one tonal color, set on a quiet band, not boxed |
| Icons | Inline SVG with `aria-hidden="true"` (or a label when it carries meaning), used sparingly |

### 5.8 Stack and build

Every page is **one hand-written HTML file**: semantic HTML plus one inline `<style>` and, only where a block needs it, a small inline `<script>`. It is built from the blocks in `blocks/` (structure and content slots) and starts from `templates/page.html`. There are no build tools, installs or frameworks: the file you write is the file that is delivered.

Structure:

```
<work>/
  brief.md
  content/plan.md, content/content.json   # from page-content; the designer never edits them
  index.html                              # the page: tokens, block styles, markup, small JS
```

Rules:
- **Start from `templates/page.html`.** Copy it to `<work>/index.html`, set the kit version in the `<!-- Built with create-page vX.Y.Z -->` line, replace the fonts with the design plan's (2 families max, `display=swap`) and paste the color roles from `scripts/m3_scheme.py`.
- **One token source:** colors (Material roles plus the plan's named colors), type scale, spacing, grid (`--grid-max`, `--grid-gutter`, `--col`), radius and shadows live once as CSS custom properties in the token block at the top of the `<style>`. Block styles use only `var(--...)`; no raw hex, sizes or shadows repeated in blocks.
- **One section per block:** `<section data-block="M01-B">` (or `header`/`footer` for G blocks) in the order of `plan.md`, with that block's styles grouped and commented by block ID.
- **Every word comes from `content.json`:** copy each slot into the markup exactly as written, including alt text and labels. Never type, cut or reword copy.
- **Production-grade HTML and CSS:** semantic elements and landmarks, mobile-first media queries, short readable class names, no dead CSS, no inline `style` attributes, no `!important` outside the reduced-motion rule.
- **JavaScript:** none by default. Use small inline vanilla JS only where a block needs it (mobile menu, tabs, multi-step form, video dialog), always keyboard accessible, and delete the template's scripts the page does not use. No frameworks or libraries.
- Forms do not submit anywhere real. Mark the action with `<!-- HIPAA-compliant form endpoint required -->`.
- **Speed, without giving up design:** at most 2 font families (`display=swap`), images as compressed WebP with `loading="lazy"` below the fold (the logo inline as SVG or a data URI), video loads only on click. Aim for about **60 KB for `index.html` before images**. Gradients, grain, SVG shapes and color fields are nearly free in CSS, so speed is never a reason to drop them.
- The page is `<work>/index.html`: open it directly in a browser. Run the checks in section 6 on it.

### 5.9 Quality floor (always, without announcing it)

Responsive from 360px up, visible keyboard focus, `prefers-reduced-motion` respected, WCAG 2.2 AA contrast, 48px touch targets, one `<h1>`, ordered headings, labels on every field, alt text on every image, skip link. Images: the user's photos when given; otherwise placeholder boxes with the right aspect ratio and a label saying what photo goes there. Never use stock photos of real-looking patients presented as actual patients. No third-party tracking scripts.
