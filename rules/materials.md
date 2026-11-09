# Rules: materials (section 2)

## 2. Read the materials

page-content reads the facts, compliance documents, current site facts and voice, and the benchmark. page-designer reads the logo, brand guide and the current site's look. Both follow the priority rule at the end.

- **Logo:** the orchestrator copies it into `<work>/materials/` (from the attachment or the current website) and the brief gives its path, or says `Logo: none`. page-designer always runs `scripts/logo.py` on it: it trims empty space, resizes raster logos to 400px wide at most, writes a data URI (or a cleaned inline SVG), and reports whether the logo is light or dark plus its main color. Embed the result in the header and the footer with `alt="[Practice name] logo"`. A light logo sits only on a dark or brand-color background, never on white. With no logo, use the practice name as a text wordmark in the display font. The logo spot is never empty.
- **Brand guidelines:** pull the primary brand color (the color seed), any secondary or accent color, the fonts, and voice rules. Brand rules win over the defaults in this kit when they conflict, except the reading level and compliance rules.
- **Compliance documents:** list every rule that affects copy, claims, testimonials, images, forms or disclaimers. Follow them strictly. They override everything in this kit, including the reading level if a required disclaimer must be word-for-word.
- **Practice facts:** collect what is real. Anything not provided stays a `[placeholder]`.
- **Current website:** open it (WebFetch, or the browser if it needs rendering) and pull real practice facts (services, providers, locations, hours, insurance, phone), the logo, colors, fonts and voice in use. Treat these facts as provided by the practice, but flag anything that looks out of date. When there is no brand guide, the current site is the brand reference.
- **Benchmark website:** open it and take **structure ideas only**: section order, which kinds of modules it uses, how it leads to the CTA, how the form or quiz flows, how much content it shows. Write 3 to 5 short takeaways and map each one to blocks from the library (3.1). Never take its colors, fonts, imagery, logo or copy.
- **Priority when sources disagree:** compliance documents, then brand guidelines, then the current website, then the art direction in section 5. The benchmark only informs structure and never overrides any of these.
