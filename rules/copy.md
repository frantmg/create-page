# Rules: copy at grade 5 (section 4)

## 4. Write the copy at grade 5

Owned by page-content. Every word goes in `content/content.json` (shape in 0.3); the designer renders it as written. Every word on the page is written for a 5th-grade reader. Target Flesch-Kincaid grade **5.0**, hard maximum **5.9** for the page and for each block.

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
