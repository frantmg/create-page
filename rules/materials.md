# Rules: materials (section 2)

## 2. Read the materials

page-content reads the facts, compliance documents, current site facts and voice, and the benchmark. page-designer reads the logo, brand guide and the current site's look. Both follow the priority rule at the end.

- **Logo:** the orchestrator copies it into `<work>/materials/` (from the attachment or the current website) and the brief gives its path, or says `Logo: none`. page-designer always runs `scripts/logo.py` on it: it trims empty space, resizes raster logos to 400px wide at most, writes a data URI (or a cleaned inline SVG), and reports whether the logo is light or dark plus its main color. Embed the result in the header and the footer with `alt="[Practice name] logo"`. A light logo sits only on a dark or brand-color background, never on white. With no logo, use the practice name as a text wordmark in the display font. The logo spot is never empty.
- **Brand guidelines:** pull the primary brand color (the color seed), any secondary or accent color, the fonts, and voice rules. Brand rules win over the defaults in this kit when they conflict, except the reading level and compliance rules.
- **Brand guide = the limits of the design.** When a brand guide is shared, the orchestrator writes `<work>/brand.json` from it before the build, using only what the guide says (never filling a field from taste; write `unspecified` when the guide is silent):

```json
{
  "source": "materials/<brand guide file>",
  "colors": { "primary": "#HEX", "secondary": ["#HEX"], "accent": ["#HEX"], "neutrals": ["#HEX"] },
  "fonts": { "display": "Font name", "body": "Font name" },
  "corners": { "buttons": "square | rounded | pill | unspecified", "media": "square | rounded | unspecified", "radius_px": null },
  "gradients": "allowed | not allowed | unspecified",
  "decorative_elements": "allowed | approval required | not allowed | unspecified",
  "photo_style": "what the guide says about imagery",
  "dont": ["each rule the guide states as a don't, in its own words"],
  "approved": {}
}
```

  With `brand.json` present the page stays inside the guide: its colors (no invented accent color), its fonts as designed, its corner style, and **no decorative style the guide does not allow or mention** (no ornaments, grain, patterns, gradients or uneven shapes). This wins over the art-direction defaults in section 5 (the gradient moment, grain, signature shapes). Where the guide is silent, use the most neutral option (even, plain corners; solid brand color; no decoration) and list each one as an assumption for the user to confirm. Something beyond the guide goes in only when the user explicitly approves it; record it under `approved`. `scripts/qa.py --brand <work>/brand.json` checks the finished page against it.
- **Compliance documents:** list every rule that affects copy, claims, testimonials, images, forms or disclaimers. Follow them strictly. They override everything in this kit, including the reading level if a required disclaimer must be word-for-word.
- **Practice facts:** collect what is real. Anything not provided stays a `[placeholder]`.
- **Content document:** when the user shares their own content (a Word, PDF or text file with the page's words), it is in `<work>/materials/` and the brief says `Content: document`. page-content uses its words as described in `rules/copy.md` 4.3.
- **Current website:** the orchestrator runs `scripts/fetch_site.py` during the intake, which saves `<work>/materials/site/summary.json` (title, phones, emails, address lines, navigation, headings, the colors and fonts the site uses, the logo) and `text.md` (each page's readable text). Read those first; open the site yourself (WebFetch, or the browser if it needs rendering) only for what they do not have. Pull real practice facts (services, providers, locations, hours, insurance, phone), the logo, colors, fonts and voice in use. Treat these facts as provided by the practice, but flag anything that looks out of date. When there is no brand guide, the current site is the brand reference.
- **Benchmark website:** open it and take **structure ideas only**: section order, which kinds of modules it uses, how it leads to the CTA, how the form or quiz flows, how much content it shows. Write 3 to 5 short takeaways and map each one to blocks from the library (3.1). Never take its colors, fonts, imagery, logo or copy.
- **Priority when sources disagree:** compliance documents, then brand guidelines, then the current website, then the art direction in section 5. The benchmark only informs structure and never overrides any of these.
