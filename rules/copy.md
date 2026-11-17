# Rules: copy at grade 5 (section 4)

## 4. Write the copy at grade 5

Owned by page-content. Every word goes in `content/content.json` (shape in 4.1); the designer renders it as written. The intake sets the content mode: **write** (page-content writes every word), **document** (the client's own content document is the source, 4.3) or **lorem** (placeholder text, 4.2). Every word on the page is written for a 5th-grade reader. Target Flesch-Kincaid grade **5.0**, hard maximum **5.9** for the page and for each block.

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

Slot names follow the block's content slots in 3.1 (headline, bullets, steps, faq items, and so on). Image needs go in `image_brief` slots so the designer knows what each photo should show. Run `scripts/readability.py` on `content.json` and fix every block marked `FIX`.

### 4.2 Lorem pages (placeholder text)

When the brief says `Content: lorem`, the user wants the design and will add the words later. There is no `content.json`; the orchestrator writes `plan.md` and the designer fills the slots in the markup:

- **Lorem ipsum** in headlines, leads, paragraphs, bullets, steps, card text, stats context, testimonials, FAQ questions and answers, and captions.
- **Real-size lorem:** keep the lengths of this section so the layout fits real copy later: headlines up to 8 words, sentences 8 to 12 words, bullets 2 to 6 words, and the slot counts from 3.1. Sentence case, ending with periods; no em dashes.
- **Real words where structure or the law needs them:** the practice name and the logo alt text, button and CTA labels from the brief's actions, navigation labels, the footer legal links, form labels, the form note ("Please don't include medical details.") and the privacy link, and image alt text that says what the photo should show.
- **No invented facts as lorem stand-ins:** numbers, ratings, review counts, prices and phone numbers stay `[placeholders]`.

readability.py is not run on lorem pages; QA lists the copy checks (area A, area B wording) under "Not checked".

### 4.3 Content documents

When the brief says `Content: document`, the client's content document (in `<work>/materials/`) is the source of the words:

- Use the document's own words and order where they fit the plan; map each part to the block and slot it belongs to.
- Change the document's words only to fit a slot (length, count), to reach grade 5.9 or lower, or to follow compliance (claims, disclaimers). Keep the meaning and the client's voice, and list **every** change in the report (block, slot, before → after, why).
- Write only what the document does not have (for example a button label or a missing FAQ answer), in its voice, and say which parts you wrote. Never invent facts: anything unknown stays a `[placeholder]`.
- If the document conflicts with the brief or with compliance, follow compliance, keep the brief's messages and CTA words, and note the conflict.

