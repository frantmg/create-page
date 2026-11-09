# Rules: plan the page (section 3)

## 3. Plan the page: pick the blocks

Owned by page-content. The result is `content/plan.md`.

### 3.1 Block library

These are the Macallan blocks. They define **structure and content**, not styling. Styling always comes from the art direction in section 5. Use the block IDs in your plan and as `data-block` attributes in the HTML.

Each block's original reference file is in `blocks/` (for example `blocks/M01-Home-hero-B.html`): use it for structure and content slots only. Styling always comes from `rules/design-build.md`.

The eyebrows, tags and meta lines in the original blocks are optional. Keep one only when it tells the reader something the heading does not; omit it when it merely repeats the heading. Uppercase with wider tracking is allowed only for short labels, used selectively and following the brand's capitalization conventions.

**Global**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| G1 | Header | Every website page | Utility bar (portal, pay bill, forms, locations, phone); logo + tagline; main nav (Treatments, Conditions, Providers, Locations, Patients, About); primary CTA button; Treatments mega menu grouped by body area + "Find your condition" promo |
| G2 | Mobile header + sticky action bar | Every page on mobile | Logo; menu icon; sticky bottom bar: Call / Book / Directions; drill-down menu |
| G3 | Footer | Every page | Logo + one-line description; link columns (Care, Patients, Locations with phones); copyright; legal links: Privacy, HIPAA notice, Accessibility, Non-discrimination, Terms |
| LP | Landing header/footer (variant of G1/G3) | Landing pages | Logo, phone, primary CTA only. No nav. Footer = legal links only |

**Heroes and banners**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| M01-A | Home hero, full photo with dark overlay | Home, brand landing pages | Eyebrow (specialties); H1; lead sentence; primary + secondary CTA; photo (provider with patient) |
| M01-B | Home hero, split text/photo | Landing pages (best for conversion) | Eyebrow; H1; 3 check bullets; primary + secondary CTA; proof row (rating, review count, years, specialists); photo 4:5 |
| M02-A | Page hero, tinted band + photo | Treatment, condition, location, provider pages | Breadcrumb; eyebrow; H1; one-sentence summary; CTA; photo 4:3 |
| M02-B | Page hero, dark band | Directories, patient resources, about, insurance | Breadcrumb; eyebrow; H1; one-sentence summary |
| M03-A | Full-width banner, photo + overlay | Mid-page push | Eyebrow; headline; one line; CTA |
| M03-B | Full-width banner, brand color, centered | One key differentiator | Eyebrow; headline; one line; link CTA |
| M04 | Announcement strip | Closures, new office, notices | One sentence; action line; link |
| M33 | Finder bar | Under a hero on home/landing | Location select; "What hurts?" select; insurance select; Find care button |

**Content and persuasion**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| M05-A | Image + text, image left | Why us, provider bio | Photo 1:1 or 4:5; eyebrow; H2; paragraph; 2 check bullets; link CTA |
| M05-B | Image + text, text left, tinted | What to expect, first visit | Eyebrow; H2; 2 short paragraphs; link CTA; photo 4:3 |
| M05-C | Image + text, photo bleeds to edge, dark | One featured service | Eyebrow; H2; one line; CTA |
| M06 | Centered statement | Philosophy, approach | Eyebrow; big statement; supporting line; 2 CTAs |
| M07 | Three text columns | Who we are, 3 pillars | Eyebrow; H2; 3 x (short title + 1 sentence) |
| M08-A | Feature cards with icons | Top 3 reasons, benefits | Eyebrow; H2; intro line; 3 x (icon, title, 1 sentence) |
| M08-B | Photo cards | 3 services or care options | Eyebrow; H2; "all" link; 3 x (photo, title, 1 sentence, link) |
| M09 | Two-column checklist | Results, benefits, conditions list | Eyebrow; H2; note line; link; 6 to 8 short check items |
| M10 | Stats | Proof by numbers | 3 to 4 x (big number, 2-line label) |
| M11-A | Numbered steps | How to get started | Eyebrow; H2; intro; 3 to 4 x (number, title, 1 sentence) |
| M11-B | Vertical timeline | Recovery after a procedure | Eyebrow; H2; note (milestones come from the clinical team); 3 to 5 milestones |
| M12 | Pull quote | Doctor philosophy or one approved quote | Quote 15 to 35 words; name, credential, title. Max one per page |
| M13 | Vertical tabs + panel | Treatment options by approach | Eyebrow; H2; intro; 2 to 4 tabs (name, count); panel list with tags |
| M14 | Comparison table | Option A vs B (non-surgical vs surgery) | Eyebrow; H2; 2 columns, one highlighted; 3 to 5 rows |
| M15 | Long-form text + table of contents | Condition and treatment detail | Sticky TOC; sections (Overview, Symptoms, Causes, Diagnosis, Treatment, FAQs); "Medically reviewed by" + date |

**Directories and practice data**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| M16 | Treatments grid with filters | Treatments index, specialty overview | Eyebrow; H2; filter chips by body area; cards (photo, tag, name, 1 line) |
| M17 | Body map | Conditions index, "where does it hurt" | Interactive body areas; condition list per area; "All conditions A to Z" |
| M18 | Provider grid | Providers index, team section | Filters (specialty, location); cards (headshot 4:5, name + credential, specialty, "Accepting new patients") |
| M19 | Location cards + map | Locations index, home | Cards (name, address, open today + hours, phone, Directions, Book here); map |
| M20 | Related content | Bottom of treatment/condition pages | Related treatments; related conditions; specialists |
| M21 | Blog/news feed | Home, about | 3 latest posts (image, type, title, date, reviewed by) |
| M32 | Map + hours | Single location page | Map; name; address; parking note; hours table; directions; phone |

**Media and proof**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| M22-A | Video + text | Doctor explains a treatment | Poster 16:9 + length; eyebrow; H2; one line; transcript link |
| M22-B | Video library grid | Patient education page | Eyebrow; H2; "all" link; 4 video tiles with titles |
| M23-A | Photo mosaic | Office tour | Eyebrow; H2; 4 to 5 labeled photos; "+ N photos" |
| M23-B | Before/after slider | Results (only with written consent) | Slider; "[Condition] with [treatment]"; "Results vary. Shared with the patient's written permission." |
| M24 | Carousel | Photo sets | Eyebrow; H2; arrows; 3+ slides |
| M25 | Insurance logo strip | Insurance proof | Eyebrow; H2; Check your insurance CTA; 5 payer logos + "+N more" |
| M26-A | Single big testimonial | One strong story | Stars; approved quote 20 to 40 words; first name + last initial; treatment + doctor |
| M26-B | Review cards + rating badge | Social proof | Rating + count badge; 2 to 3 real review cards; video testimonial tile |

**Conversion**

| ID | Block | Use for | Content slots |
|---|---|---|---|
| M28-A | CTA panel + photo | End of about/patient pages | Eyebrow; H2; one line; 3 resource links; CTA; photo |
| M28-B | CTA band with phone | End of most pages | Headline; one line; CTA; phone |
| M29 | Appointment form | Landing pages, contact, location | H2; one line; 2 reassurance bullets; phone; fields (first, last, phone, email, location, body area); submit; "Please don't include medical details" note; privacy link |
| M30 | Contact + newsletter form | Contact page | General question form (name, email, message); newsletter signup |
| M31 | FAQ accordion | Objection handling | Photo 4:5; eyebrow; H2; 4 to 6 questions with 1 to 3 sentence answers |

### 3.2 Page recipes

Start from the recipe for the page type, then adjust using the selection rules in 3.3 and any benchmark takeaways from section 2 (structure only; the conversion rules in 3.4 still win on landing pages). Bracketed blocks are optional.

- **Conversion landing page:** use the conversion recipe in 3.4.
- **Home:** G1, M01-A, [M33], M08-A, M16 or M08-B, M10, M18 (4 providers), M26-B, M19, M25, M28-B, G3.
- **Specialty / treatment:** G1, M02-A, M15 (Overview, Who it helps, What to expect), M13 or M14, M11-B, [M22-A], M26-A, M31, M20, M28-B, G3.
- **Condition:** G1, M02-A, M15 (Overview, Symptoms, Causes, Diagnosis, Treatment), M13, M20, M31, M29, G3.
- **Location:** G1, M02-A, M32, M18 (this office only), [M23-A], M25, M26-B, M29, G3.
- **Provider:** G1, M02-A (headshot as photo), M05-A (bio), M09 (what they treat), [M12], [M22-A], M19 (where they see patients), M26-A, M29, G3.
- **Providers directory:** G1, M02-B, M18, M28-B, G3.
- **Locations directory:** G1, M02-B, M19, M28-B, G3.
- **About us:** G1, M02-B, M06, M07, M10, M05-C, M18, [M21], M28-A, G3.
- **Accepted insurance:** G1, M02-B, M25, M14 or M09 (plans list), M31 (billing questions), M28-B, G3.
- **Patient testimonials:** G1, M02-B, M26-A, M26-B, [M22-B], [M23-B], M28-B, G3.
- **Contact:** G1, M02-B, M29, M30, M19, G3.

For a **full website**, plan every page first (sitemap with page type and recipe for each), use one shared G1/G3 and one token set, and link pages with relative URLs.

### 3.3 Selection rules

1. **The hero carries Message 1 and the primary CTA.** The H1 states Message 1 in plain words. (In conversion mode the H1 states the offer in the keyword's words instead, and Message 1 goes in the line under it and the first bullet.)
2. **Messages 1, 2, 3 get the next sections, in that order.** Pick the block by the kind of message:
   - Speed or access ("seen this week") → M10 or M08-A
   - Trust or credentials → M10, M18, M12 or M26
   - Treatment options or "no surgery first" → M08-B, M13 or M14
   - How it works or ease → M11-A or M05-B
   - Cost or insurance → M25 or M09
   - Convenience or locations → M19, M32 or M33
   - Results → M09, M23-B (consent only), M26
3. **Repeat the primary CTA** in the hero, at least once mid-page, and in the final section. Every CTA uses the exact same words. A page has **at most 2 distinct actions** (for example: the form and a call button). Repeating the same action in several places is fine; adding a third action is not.
4. **Landing pages have one goal.** No main nav, no blog, no outbound links except legal and phone. Secondary CTA only if the user gave one.
5. **Do not repeat a block type** on one page unless the content truly needs it. One pull quote max.
6. **Choose variants deliberately:** A vs B by what content exists (no good photo means M01-B with a smaller image or M02-B, not M01-A).
7. **Drop a block if its content does not exist.** A stats block with invented numbers is worse than no stats block.

### 3.4 Conversion mode (landing pages and pages built for conversion)

Three priorities rule the content and structure: **simplicity, scanability, and one clear goal.** Simplicity means fewer messages, fewer fields and fewer actions. It never means less color, plainer type or a quieter layout.

**Conversion mode does not touch the visual design.** It decides what goes on the page, in what order, and how leads come in. Everything about how the page looks (color, gradients, type, imagery, layout, motion) comes from section 5, in full, exactly as on any other page. A landing page should look at least as rich and specific to the brand as the home page.

**Conversion recipe** (in this order; bracketed blocks only when the content exists):

1. **LP header:** logo + call button. If Lead flow is "Call first", the call button is the main action in the header and stays reachable (sticky) after the first scroll.
2. **M01-B hero, above the fold on a phone:** H1 = the offer, in the keyword's words (message match: "Orthopedic Surgeon in Layton", not "Expert care for you"). One line saying who provides it (practice name). 3 bullets with the key facts. Primary CTA (+ call as the second action). Trust signals (rating, years, insurance). On a 390 x 844 phone screen, the H1, the who line and the primary CTA must all show without scrolling.
3. **[M22-A doctor video (VSL)]** right after the hero when a video exists: the doctor explains the practice or procedure. Load it on click (poster image first) so the page stays fast.
4. **Message 1, 2, 3 blocks**, bullets first, short. Use the block-by-message rules in 3.3.
5. **Proof:** [M23-B before/after] high on the page for aesthetic and surgical specialties (consent and disclosure required), M26-B or M26-A real reviews, [M25] insurance badges.
6. **M11-A steps:** how to get started, 3 steps.
7. **Conversion zone:** the form that fits Lead flow:
   - *Short form:* only the fields needed to qualify (usually first name, phone, and one choice like location). Right for clients with a call center that calls back fast.
   - *Multi-step form:* step 1 is low effort (name + phone or one easy choice), then 1 to 3 more short screens with qualifying questions, with a progress bar. Each finished step builds momentum. Right when the client needs more detail before a call.
   - *Call first:* big call button block (M28-B with phone as the main action), form as the second action.
   - *Quiz funnel (QZ block):* 3 to 5 tappable questions, one per screen, with a progress bar (large tappable option cards built on radio inputs), ending in a short contact step and a plain result ("You may be a good fit for a visit."). Best for consideration campaigns and social traffic. Never present the result as a diagnosis.
8. **M31 FAQ, below the conversion zone:** answer the main doubts: recovery time, cost and insurance, pain, and who is a good candidate. Answers come from the practice; use `[placeholders]` until they do.
9. **Keyword block, below the fold:** a short section (M07 or M09 style) that uses the target keyword and close variants naturally, for ad relevance. It must still read at grade 5 and must not crowd the top of the page.
10. **M28-B final CTA**, same words as the hero CTA.
11. **LP footer:** medical disclaimer, before/after disclosure if used, legal links.

**Copy rules (on top of section 4):**
- Make the offer clear above the fold: what it is and who offers it.
- Put key facts in bullets, never in dense paragraphs.
- Use low-friction CTA words: "Schedule a conversation", "Book a visit", "See if you're a fit". Avoid formal words like "consultation" on buttons.
- Treat the ad and the page as one piece: the H1 echoes the keyword and ad headline. The keyword phrase may be used as-is even if it raises the grade a little; pass its words to the checker with `--allow`.

**Action rule:** the primary CTA must be easy to find on every screen of the phone view. How it looks (color, shape, motion) comes from section 5.

If the user chose "Show me the plan first", show the plan as a wireframe plus a short list. Run `python3 <kit>/scripts/wireframe.py <work>/content/plan.md`: it stacks the chosen blocks from `blocks/` in plan order (desktop and mobile) into `<work>/wireframe.html`, so the user sees the page before approving it. Send the wireframe (START-HERE section 7) with the list (section order, block ID, which message it carries) and wait for approval, using a guided question (Approve plan · Change something). After a change, rebuild the wireframe and ask again. Otherwise, show the plan in one short list and keep building.

So the wireframe can read the plan, write `plan.md` with one block per line, starting with its number and full block ID including the variant, for example `2. M01-B: Message 1 · Seen this week`.
