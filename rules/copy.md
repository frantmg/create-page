# Rules: copy at grade 5 (section 4)

## 4. Write the copy at grade 5

Owned by page-content, which runs only when the user asks for written content (otherwise see 4.2). Every word goes in `content/content.json` (shape in 4.1); the designer renders it as written. Every word on the page is written for a 5th-grade reader. Target Flesch-Kincaid grade **5.0**, hard maximum **5.9** for the page and for each block.

**Rules**

- Short sentences. Average 8 to 12 words. Never more than 15.
- Short words. Prefer one and two syllables.
- Talk to the reader: "you" and "we".
- Active voice. One idea per sentence.
- Headlines: 8 words or fewer, say the benefit. ("Walk without knee pain again.")
- Buttons: start with a verb, 2 to 4 words. ("Book a visit", "Call now", "Check my insurance".)
- Bullets: 2 to 6 words each.
- Medical names are allowed when they are the real name of a condition or treatment. Say the name once, then explain it in plain words right after. ("Sciatica is pain that runs from your low back down your leg.") Pass these words to the checker with `--allow`.
- No em dashes. Use periods, commas, colons or parentheses.
- Avoid generated-page tells: no single word in a headline set in a different color or italic, no uppercase except selectively on short labels, no labels above every heading, no meta strings joined with middle dots, no "→" added to button or link text.
- Never trade accuracy for simplicity. If a plain word changes the medical meaning, keep the right word and explain it.

**Swaps**

| Instead of | Write |
|---|---|
| appointment (when it reads heavy) | visit |
| physician | doctor |
| utilize | use |
| receive | get |
| assist | help |
| individualized / personalized | made for you |
| minimally invasive | uses small cuts (only if clinically true) |
| non-surgical | without surgery |
| comprehensive | full |
| approximately | about |
| commence | start |
| discomfort | pain |
| prior to | before |
| in order to | to |
| a variety of | many |
| consultation (on buttons) | conversation, visit |

**Check it.** Run `scripts/readability.py` on `content.json` before handing off; QA runs it again on the finished `index.html` (6.1). Fix every block marked `FIX`, then run again. Placeholders like `[City]` count as one short word.

### 4.1 Content files

page-content writes two files in `<work>/content/`:

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

Slot names: for engine blocks, use exactly the slot names in the `<!--meta ...-->` line of `engine/blocks/<ID>.html` (for example M01-B: `eyebrow`, `h1`, `who`, `bullets`, `proof` [{value, label}], `image_brief`); `scripts/assemble.py` matches `content.json` blocks to the plan by ID and order, and fills any missing slot with lorem. For other blocks, slot names follow the block's content slots in 3.1 (`blocks-lite/` shows them in place). Image needs go in `image_brief` slots so the designer knows what each photo should show, plus an `alt` slot per meaningful image. Run `python3 <kit>/scripts/readability.py <work>/content/content.json` (add `--allow` for real medical terms and the keyword) and fix every block marked `FIX` before the designer starts.

### 4.2 Placeholder content (lorem ipsum)

When the brief says `Content: placeholder`, the user wants the design fast and will add the words later. There is no `content.json`; the designer fills the slots straight in the markup:

- **Lorem ipsum** in headlines, leads, paragraphs, bullets, steps, card text, stats context, testimonials, FAQ questions and answers, and captions.
- **Real-size lorem:** keep the lengths of 4 so the layout fits real copy later: headlines up to 8 words, sentences 8 to 12 words, bullets 2 to 6 words, the slot counts from 3.1 (for example 3 bullets, 4 FAQ items). Sentence case, ending with periods; no em dashes.
- **Real words where structure or the law needs them:** the practice name (or `[Practice name]`) and the logo alt text, button and CTA labels from the brief's main and second action, navigation labels, the footer legal links, form labels, the form note ("Please don't include medical details.") and the privacy link, and image alt text that says what the photo should show.
- **No invented facts as lorem stand-ins:** numbers, ratings, review counts, prices and phone numbers stay `[placeholders]` (for example `[4.9]`, `[(555) 555-0123]`).

readability.py is not run on placeholder pages, and QA skips the copy checks (area A, and area B wording) and reports them under "Not checked".

