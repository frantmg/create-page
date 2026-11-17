# Rules: copy at grade 5 (section 4)

## 4. Write the copy at grade 5

Owned by the content owner: the orchestrator for a single landing page, page-content for full websites or when the user asks for a full copy review. Every word goes in `content/content.json` (shape in 4.1); the designer renders it as written. Every word on the page is written for a 5th-grade reader. Target Flesch-Kincaid grade **5.0**, hard maximum **5.9** for the page and for each block.

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

The content owner writes two files in `<work>/content/`:

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

Slot names follow the block's content slots in 3.1 (headline, bullets, steps, faq items, and so on; `blocks-lite/` shows each block's slots in place). Image needs go in `image_brief` slots so the designer knows what each photo should show, plus an `alt` slot per meaningful image. Run `python3 <kit>/scripts/readability.py <work>/content/content.json` (add `--allow` for real medical terms and the keyword) and fix every block marked `FIX` before the designer starts.
