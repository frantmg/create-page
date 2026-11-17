#!/usr/bin/env python3
"""Assemble a page from the engine's designed blocks in about a second (kit v7).
Usage: python3 assemble.py <work>/build.json [--plan <work>/content/plan.md] [--content <work>/content/content.json]

build.json holds the creative decisions (START-HERE.md 0.3 v7):
  {"practice": "Example Physical Therapy", "phone": "[(555) 555-0123]", "cta_primary": "Book a visit",
   "cta_secondary": "Call now", "theme": "editorial", "seed": "#2E6B4F",
   "fonts": null | {"display": "Fraunces", "body": "Hanken Grotesk"} | {"name","display","body","href"},
   "ornament": "contour|arcs|dots|none", "cta_shape": "leaf|pill|soft|square", "media_shape": "cut|round|soft|square",
   "logo": "<work>/materials/logo.datauri.txt", "logo_tone": "dark|light", "content": "placeholder|written",
   "page_title": "...", "meta_description": "...", "tokens": {"--name": "value"}, "extra_css": "<work>/signature.css",
   "photos": {"M01-B": "<url or data URI>"}, "brand_locked": {"colors": false, "fonts": false}, "brand": "<work>/brand.json"}
Brand mode: when <work>/brand.json exists (written from the brand guide, rules/materials.md), the guide decides the look:
its colours, fonts and corner style are used; anything the guide does not allow, or does not mention, falls back to the
most neutral option (even corners, no ornament, no grain, solid colour instead of gradients, no invented accent colour),
and build.json's ornament and shape choices are ignored unless brand.json lists them under "approved". The report lists
every neutral fallback under "brand_assumptions" so they can be confirmed with the user.
Only "practice" is required; everything else has a default (theme editorial, seed from the logo colour or #2E6B4F).

Reads the ordered block IDs from plan.md (LP adds the landing header and footer), fills each block's slots from
content.json (written content) or with lorem ipsum sized to rules/copy.md 4.2 (placeholder content), builds the
colour roles from the seed (m3_scheme.py when materialyoucolor is installed, an OKLCH approximation otherwise) and
writes, next to build.json:
  index.html          the page (tokens, base, theme, only the used blocks' CSS between /* block:ID */ markers)
  alternates.html     the other versions of every used block, ready for the tweak bar (rules/design-build.md 5.10)
  tweak-options.json  palettes and font pairings for the tweak bar
Blocks not in the engine yet get a marked placeholder section and are listed under needs_designer.
Prints JSON: files, blocks, missing blocks, theme, seconds."""
import argparse, colorsys, datetime as dt, html, json, math, pathlib, random, re, subprocess, sys, time

T0 = time.time()
KIT = pathlib.Path(__file__).resolve().parent.parent
ENG = KIT / "engine"
ap = argparse.ArgumentParser()
ap.add_argument("build"); ap.add_argument("--plan", default=""); ap.add_argument("--content", default="")
a = ap.parse_args()
bpath = pathlib.Path(a.build).resolve(); work = bpath.parent
B = json.loads(bpath.read_text(encoding="utf-8"))
plan_path = pathlib.Path(a.plan).resolve() if a.plan else work / "content" / "plan.md"
content_path = pathlib.Path(a.content).resolve() if a.content else work / "content" / "content.json"
warnings, needs = [], []
brand_path = pathlib.Path(B["brand"]) if B.get("brand") else work / "brand.json"
if not brand_path.is_absolute(): brand_path = work / brand_path
BR = json.loads(brand_path.read_text(encoding="utf-8")) if brand_path.exists() else None
assumptions = []

# ── Engine blocks ────────────────────────────────────────────────────────
def load_block(bid):
    f = ENG / "blocks" / f"{bid}.html"
    if not f.exists(): return None
    s = f.read_text(encoding="utf-8")
    meta = json.loads(re.search(r"<!--meta (.*?) -->", s, re.S).group(1))
    meta["css"] = re.search(r"<style>\n?(.*?)</style>", s, re.S).group(1).strip()
    meta["tpl"] = re.search(r"<template>\n?(.*?)</template>", s, re.S).group(1).strip()
    return meta
ENGINE = {p.stem: load_block(p.stem) for p in sorted((ENG / "blocks").glob("*.html"))}
def siblings(bid):
    m = re.match(r"(M\d{2})-[A-C]$", bid)
    return [k for k in ENGINE if m and k != bid and k.startswith(m.group(1) + "-")]

# ── Plan ─────────────────────────────────────────────────────────────────
ID_RE = re.compile(r"\b(LP|G[1-3]|M\d{2})(?:[-\s]?(?:variant\s+)?([A-C]))?\b")
plan = []
if plan_path.exists():
    for line in plan_path.read_text(encoding="utf-8").splitlines():
        head = re.sub(r"^[\s|#>*`•-]*(?:\d+[.)]?[\s|*`]*)?", "", line)
        m = ID_RE.match(head)
        if m: plan.append(m.group(1) + ("-" + m.group(2) if m.group(2) else ""))
if not plan: sys.exit("No block IDs in plan.md")
landing = "LP" in plan
main_ids = [b for b in plan if b not in ("LP", "G1", "G2", "G3")]

# ── Content: written slots or sized lorem ────────────────────────────────
WORDS = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore "
         "magna aliqua enim ad minim veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
         "consequat duis aute irure in reprehenderit voluptate velit esse cillum fugiat nulla pariatur excepteur sint "
         "occaecat cupidatat non proident sunt culpa qui officia deserunt mollit anim id est laborum").split()
STAT_VALUES = ["[4.9]", "[12]", "[20+]", "[5,000+]"]
def lorem(spec, rnd, globs):
    kind, _, rest = spec.partition(":")
    words = lambda n: " ".join(rnd.choice(WORDS) for _ in range(n))
    cap = lambda s: s[:1].upper() + s[1:]
    if kind == "opt": return None
    if kind == "fixed": return rest
    if kind == "fixed-list": return rest.split("|")
    if kind == "global": return globs.get(rest, "")
    if kind == "image": return rest
    if kind == "label": return cap(words(int(rest)))
    if kind == "headline": return cap(words(int(rest))) + "."
    if kind == "question": return cap(words(int(rest))) + "?"
    if kind == "sentence": return cap(words(int(rest))) + "."
    if kind == "para": return " ".join(cap(words(rnd.randint(8, 12))) + "." for _ in range(int(rest)))
    if kind == "list":
        c, n = rest.split(":"); return [cap(words(int(n))) for _ in range(int(c))]
    if kind == "stats":
        c, n = (rest.split(":") + ["3"])[:2]
        return [{"value": STAT_VALUES[i % 4], "label": cap(words(int(n)))} for i in range(int(c))]
    if kind == "items":
        c, _, fields = rest.partition(":")
        fs = [f.split("=", 1) for f in fields.split(";")]
        return [{k: lorem(v, rnd, globs) for k, v in fs} for _ in range(int(c))]
    return ""

written = {}
if B.get("content", "placeholder") == "written":
    if content_path.exists():
        cj = json.loads(content_path.read_text(encoding="utf-8"))
        n = {}
        for blk in cj.get("blocks", []):
            bid = blk.get("id", ""); n[bid] = n.get(bid, 0) + 1
            written[(bid, n[bid])] = blk.get("slots", {})
        B.setdefault("page_title", cj.get("meta", {}).get("page_title"))
        B.setdefault("meta_description", cj.get("meta", {}).get("meta_description"))
        for k in ("cta_primary", "cta_secondary"):
            if cj.get("meta", {}).get(k): B.setdefault(k, cj["meta"][k])
    else:
        warnings.append("content is 'written' but content.json was not found; used lorem ipsum")

# ── Colour: roles + tones from the seed ──────────────────────────────────
def hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def rgb2hex(c): return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in c)
def lin(v): v /= 255; return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def gam(v): return 255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)
def to_oklch(rgb):
    r, g, b = (lin(x) for x in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    Bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, Bb), (math.degrees(math.atan2(Bb, A)) + 360) % 360
def oklch_hex(L, C, H):
    for i in range(200):
        c = max(0, C - i * 0.004); A, Bb = c * math.cos(math.radians(H)), c * math.sin(math.radians(H))
        l = (L + 0.3963377774 * A + 0.2158037573 * Bb) ** 3; m = (L - 0.1055613458 * A - 0.0638541728 * Bb) ** 3
        s = (L - 0.0894841775 * A - 1.2914855480 * Bb) ** 3
        rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
               -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
        if all(-0.0005 <= x <= 1.0005 for x in rgb) or c == 0:
            return rgb2hex([gam(min(1, max(0, x))) for x in rgb])
TONE_L = {10: 0.20, 20: 0.28, 30: 0.37, 40: 0.46, 80: 0.83, 90: 0.92, 95: 0.96}
def oklch_scheme(seed):
    _, c0, h = to_oklch(hex2rgb(seed)); c = max(c0, 0.03); t = (h + 60) % 360
    P = {"primary": (0.47, c, h), "on-primary": (1, 0, h), "primary-container": (0.90, c * .35, h), "on-primary-container": (0.28, c * .8, h),
         "secondary": (0.48, c * .35, h), "on-secondary": (1, 0, h), "secondary-container": (0.91, c * .25, h), "on-secondary-container": (0.30, c * .35, h),
         "tertiary": (0.48, c * .7, t), "on-tertiary": (1, 0, t), "tertiary-container": (0.90, c * .3, t), "on-tertiary-container": (0.28, c * .6, t),
         "error": (0.50, 0.19, 27), "on-error": (1, 0, 27),
         "surface": (0.985, 0.006, h), "on-surface": (0.22, 0.012, h), "on-surface-variant": (0.40, 0.02, h),
         "surface-container-lowest": (1, 0, h), "surface-container-low": (0.965, 0.01, h), "surface-container": (0.95, 0.012, h),
         "surface-container-high": (0.935, 0.014, h), "inverse-surface": (0.30, 0.015, h), "inverse-on-surface": (0.96, 0.008, h),
         "inverse-primary": (0.80, c * .6, h), "outline": (0.56, 0.02, h), "outline-variant": (0.82, 0.02, h)}
    roles = {f"--md-sys-color-{k}": oklch_hex(*v) for k, v in P.items()}
    tones = {t_: oklch_hex(L, c * (0.9 if t_ < 50 else 0.45), h) for t_, L in TONE_L.items()}
    return roles, tones
def m3(seed, variant="fidelity"):
    r = subprocess.run([sys.executable, str(KIT / "scripts" / "m3_scheme.py"), seed, "--variant", variant], capture_output=True, text=True)
    if r.returncode != 0: return None
    root = re.search(r":root\s*\{([^}]*)\}", r.stdout)
    roles = dict(re.findall(r"(--md-sys-color-[\w-]+):\s*(#[0-9A-Fa-f]{6})", root.group(1)))
    tl = re.search(r"/\* primary tones: (.*?) \*/", r.stdout)
    tones = {int(k): v for k, v in re.findall(r"(\d+):(#[0-9A-Fa-f]{6})", tl.group(1))} if tl else {}
    return roles, tones
seed = ((BR or {}).get("colors", {}).get("primary") or B.get("seed") or B.get("logo_color") or "#2E6B4F").strip()
if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", seed): warnings.append(f"seed {seed} is not a hex colour; used #2E6B4F"); seed = "#2E6B4F"
seed = "#" + seed.lstrip("#").upper()
got = m3(seed)
colour_source = "m3_scheme.py" if got else "OKLCH approximation (materialyoucolor not installed)"
roles, tones = got or oklch_scheme(seed)
for t_ in TONE_L:
    tones.setdefault(t_, oklch_scheme(seed)[1][t_])
def on_colour(hx):
    lum = lambda c: 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2])
    L = lum(hex2rgb(hx)); return "#FFFFFF" if (1.05) / (L + 0.05) >= (L + 0.05) / 0.05 else "#000000"
if BR:
    cols = BR.get("colors") or {}
    acc = [c for c in (cols.get("accent") or []) if re.fullmatch(r"#?[0-9A-Fa-f]{6}", str(c))]
    sec = [c for c in (cols.get("secondary") or []) if re.fullmatch(r"#?[0-9A-Fa-f]{6}", str(c))]
    if acc:
        a0 = "#" + acc[0].lstrip("#").upper(); roles["--md-sys-color-tertiary"] = a0; roles["--md-sys-color-on-tertiary"] = on_colour(a0)
    else:   # no accent in the guide: never invent one
        for r in ("", "on-", "-container", "on-container"):
            src = {"": "primary", "on-": "on-primary", "-container": "primary-container", "on-container": "on-primary-container"}[r]
            dst = {"": "tertiary", "on-": "on-tertiary", "-container": "tertiary-container", "on-container": "on-tertiary-container"}[r]
            roles[f"--md-sys-color-{dst}"] = roles[f"--md-sys-color-{src}"]
        assumptions.append("The brand guide names no accent colour: used the brand colour where the theme has an accent (no new colour added)")
    if sec:
        s0 = "#" + sec[0].lstrip("#").upper(); roles["--md-sys-color-secondary"] = s0; roles["--md-sys-color-on-secondary"] = on_colour(s0)
ink = " ".join(str(v) for v in hex2rgb(roles.get("--md-sys-color-on-surface", "#191C1A")))

# ── Theme, fonts, shape, ornament ────────────────────────────────────────
theme = B.get("theme", "editorial")
if not (ENG / "themes" / f"{theme}.css").exists(): warnings.append(f"theme {theme} not found; used editorial"); theme = "editorial"
TH = json.loads((ENG / "themes" / f"{theme}.json").read_text())
def gfont(fam): return "family=" + fam.strip().replace(" ", "+") + ":wght@400;600;700"
fonts = TH["fonts"]
f = B.get("fonts")
if isinstance(f, dict) and f.get("href"): fonts = f
elif isinstance(f, dict) and f.get("display"):
    d, b_ = f["display"], f.get("body") or f["display"]
    fonts = {"name": f"{d} + {b_}", "display": f"\"{d}\", Georgia, serif", "body": f"\"{b_}\", system-ui, sans-serif",
             "href": "https://fonts.googleapis.com/css2?" + "&".join(dict.fromkeys([gfont(d), gfont(b_)])) + "&display=swap"}
bf = (BR or {}).get("fonts") or {}
if BR and bf.get("display"):
    d, b_ = bf["display"], bf.get("body") or bf["display"]
    fonts = {"name": f"{d} + {b_} (brand)", "display": f"\"{d}\", Georgia, serif", "body": f"\"{b_}\", system-ui, sans-serif",
             "href": bf.get("href") or "https://fonts.googleapis.com/css2?" + "&".join(dict.fromkeys([gfont(d), gfont(b_)])) + "&display=swap"}
elif BR: assumptions.append(f"The brand guide names no fonts: used the {TH['name']} theme pairing ({fonts['name']})")
CTA = {"leaf": "22px 4px 22px 4px", "pill": "999px", "soft": "14px", "square": "4px"}
MEDIA = {"cut": ("4px 120px 4px 4px", "28px 4px 28px 28px"), "round": ("28px", "24px"), "soft": ("14px", "14px"), "square": ("4px", "4px")}
shape = {}
if B.get("cta_shape") in CTA: shape["--radius-cta"] = CTA[B["cta_shape"]]
if B.get("media_shape") in MEDIA: shape["--radius-media"], shape["--radius-card"] = MEDIA[B["media_shape"]]
def svg_uri(svg): return 'url("data:image/svg+xml,' + re.sub(r"[<>#\"%]", lambda m: {"<": "%3C", ">": "%3E", "#": "%23", '"': "'", "%": "%25"}[m.group(0)], svg) + '")'
stroke = tones[80]
ORN = {
    "contour": f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600" fill="none" stroke="{stroke}" stroke-width="1.2">'
               '<path d="M-20 420C90 380 160 300 260 310s170 90 270 60 150-140 290-150"/><path d="M-20 460C100 420 170 345 265 352s175 92 272 64 155-128 283-136"/>'
               '<path d="M-20 500C110 462 182 392 272 396s180 92 276 66 160-116 272-122"/><path d="M-20 540C118 504 194 440 280 441s184 90 280 68 165-104 260-108"/>'
               '<path d="M-20 580C126 548 206 488 290 486s188 88 284 70 170-92 246-94"/><path d="M-20 380C80 338 150 255 255 268s165 88 265 56 145-152 300-164"/></svg>',
    "arcs": f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600" fill="none" stroke="{stroke}" stroke-width="1.5">' + "".join(
        f'<circle cx="760" cy="620" r="{120 + i * 70}"/>' for i in range(7)) + "</svg>",
    "dots": f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600" fill="{stroke}">' + "".join(
        f'<circle cx="{400 + x * 28}" cy="{300 + y * 28}" r="2.2"/>' for x in range(14) for y in range(11) if (x + y) % 2 == 0 and x + 13 - y > 6) + "</svg>",
}
ornament = B.get("ornament", TH.get("ornament", "none"))
brand_over = {}
if BR:
    ok = lambda v: str(v or "").lower().startswith("allow")
    appr = BR.get("approved") or {}
    corners = BR.get("corners") or {}
    def radius(kind):
        v = str(corners.get(kind) or "unspecified").lower(); px = corners.get("radius_px")
        if v.startswith("square"): return "0px"
        if v.startswith("pill"): return "999px"
        if v.startswith("round"): return f"{px or 8}px"
        assumptions.append(f"The brand guide does not set {kind} corners: used plain, even {px or 6}px corners")
        return f"{px or 6}px"
    rb, rm = radius("buttons"), radius("media")
    if bf.get("display"): brand_over["--display-stretch"] = "100%"   # the brand font as designed, not widened
    brand_over.update({"--radius-cta": rb, "--radius-media": rm, "--radius-card": rm, "--radius-field": "0px" if rb == "0px" else ("8px" if rb == "999px" else rb)})
    shape = {}
    if not ok(BR.get("decorative_elements")):
        ornament = "none"; brand_over.update({"--hero-grain": "0", "--final-grain": "0"})
        if str(BR.get("decorative_elements") or "unspecified").lower().startswith("unspec"):
            assumptions.append("The brand guide does not mention decorative elements: left out the ornament and grain")
    if not ok(BR.get("gradients")):
        light_hero = theme == "clinical"
        brand_over.update({"--hero-bg": "var(--md-sys-color-surface-container-low)" if light_hero else "var(--md-sys-color-primary)",
                           "--final-bg": "var(--md-sys-color-primary)", "--m01a-overlay": "color-mix(in srgb, var(--tone-10) 78%, transparent)"})
        if not light_hero:
            brand_over.update({"--hero-accent": "var(--md-sys-color-on-primary)", "--hero-btn-bg": "var(--md-sys-color-surface)", "--hero-btn-fg": "var(--md-sys-color-primary)",
                               "--hero-line": "color-mix(in srgb, var(--md-sys-color-on-primary) 30%, transparent)", "--hero-focus": "var(--md-sys-color-on-primary)"})
        brand_over.update({"--final-btn-bg": "var(--md-sys-color-surface)", "--final-btn-fg": "var(--md-sys-color-primary)", "--final-focus": "var(--md-sys-color-on-primary)"})
        if str(BR.get("gradients") or "unspecified").lower().startswith("unspec"):
            assumptions.append("The brand guide does not mention gradients: used solid brand colour for the hero and final bands")
    for k, v in appr.items():   # things the user explicitly approved beyond the guide
        if k == "ornament": ornament = v
        elif k == "cta_shape" and v in CTA: brand_over["--radius-cta"] = CTA[v]
        elif k == "media_shape" and v in MEDIA: brand_over["--radius-media"], brand_over["--radius-card"] = MEDIA[v]
        elif k.startswith("--"): brand_over[k] = v
    if B.get("ornament") or B.get("cta_shape") or B.get("media_shape"):
        warnings.append("Brand mode: build.json ornament and shape choices were ignored (add them to brand.json \"approved\" only if the user approved them)")
orn_css = svg_uri(ORN[ornament]) if ornament in ORN else "none"

# ── Globals for every block ──────────────────────────────────────────────
practice = B.get("practice") or "[Practice name]"
pw = practice.split()
wm = (" ".join(pw[:-2]), " ".join(pw[-2:])) if len(pw) > 2 else (practice, "")
phone = B.get("phone") or "[(555) 555-0123]"
digits = re.sub(r"\D", "", phone)
tel = f"tel:{digits}" if len(digits) >= 10 else "tel:[5555550123]"
logo_src = ""
if B.get("logo"):
    lp = pathlib.Path(B["logo"])
    logo_src = lp.read_text().strip() if lp.exists() else (B["logo"] if B["logo"].startswith(("data:", "http")) else "")
    if not logo_src: warnings.append(f"logo not found: {B['logo']}; used the text wordmark")
wordmark = f"<span>{html.escape(wm[0])}</span>" + (f" <span>{html.escape(wm[1])}</span>" if wm[1] else "")
brand = f'<img class="logo" src="{logo_src}" alt="{html.escape(practice)} logo">' if logo_src else wordmark
tone = B.get("logo_tone", "dark")
G = {
    "practice": practice, "phone": phone, "tel": tel, "brand": brand, "brand_footer": brand,
    "cta_primary": B.get("cta_primary") or "Book a visit", "cta_secondary": B.get("cta_secondary") or "Call now",
    "cta_href": "#book" if "M29" in main_ids else tel, "year": str(dt.date.today().year),
    "header_class": "band-dark" if logo_src and tone == "light" else "",
    "footer_class": "" if logo_src and tone == "dark" else "band-dark",
    "_check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    "_phone_icon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>',
}

# ── Tiny mustache: {{x}} escaped, {{{x}}} raw, {{#x}}..{{/x}} list/if, {{^x}}..{{/x}} if-not, dotted paths ──
SEC = re.compile(r"{{([#^])\s*([\w.]+)\s*}}(.*?){{/\s*\2\s*}}", re.S)
def look(name, stack):
    if name == ".": return stack[-1].get(".")
    head, *rest = name.split(".")
    for ctx in reversed(stack):
        if isinstance(ctx, dict) and head in ctx:
            v = ctx[head]
            for r in rest:
                v = v[int(r)] if isinstance(v, list) and r.isdigit() and int(r) < len(v) else (v.get(r) if isinstance(v, dict) else None)
            return v
    return None
def render(t, stack):
    def sec(m):
        kind, name, body = m.groups(); v = look(name, stack)
        if kind == "^": return render(body, stack) if not v else ""
        if not v: return ""
        if isinstance(v, list):
            return "".join(render(body, stack + [dict(it, _n=i + 1) if isinstance(it, dict) else {".": it, "_n": i + 1}]) for i, it in enumerate(v))
        return render(body, stack + ([v] if isinstance(v, dict) else []))
    t = SEC.sub(sec, t)
    t = re.sub(r"{{{\s*([\w.]+)\s*}}}", lambda m: str(look(m.group(1), stack) or ""), t)
    return re.sub(r"{{\s*([\w.]+)\s*}}", lambda m: html.escape(str(look(m.group(1), stack) or ""), quote=True), t)

def slots_for(bid, key, nth, extra=None):
    meta = ENGINE[bid]; given = dict(extra or written.get((bid, nth), {}))
    rnd = random.Random(f"{key}")
    out = {}
    for name, spec in meta["slots"].items():
        out[name] = given[name] if given.get(name) not in (None, "", []) else lorem(spec, rnd, G)
    for k, v in given.items(): out.setdefault(k, v)
    return out
def photo_html(bid, slots):
    brief = slots.get("image_brief") or "Photo"
    src = (B.get("photos") or {}).get(bid) or slots.get("image_src")
    if src: return f'<div class="photo"><img src="{html.escape(src)}" alt="{html.escape(slots.get("alt") or brief)}" loading="lazy"></div>'
    return f'<div class="photo" role="img" aria-label="{html.escape(brief)}">{html.escape(brief)}</div>'
def render_block(bid, key, slots):
    ctx = dict(G, **slots, _block=bid, _id=key.lower().replace("#", "-"))
    ctx["_photo"] = photo_html(bid, slots)
    return render(ENGINE[bid]["tpl"], [ctx])

# ── Build the page ───────────────────────────────────────────────────────
sections, used_css, missing, nth, keys_slots = [], {}, [], {}, []
for bid in main_ids:
    nth[bid] = nth.get(bid, 0) + 1
    key = bid if nth[bid] == 1 else f"{bid}#{nth[bid]}"
    if bid not in ENGINE:
        missing.append(bid)
        sections.append(f'<section data-block="{bid}" class="engine-missing"><div class="container"><p><b>{bid}</b> is not in the engine yet. page-designer builds it in this page\'s style.</p></div></section>')
        continue
    s = slots_for(bid, key, nth[bid])
    keys_slots.append((bid, key, s))
    sections.append(render_block(bid, key, s))
    used_css[bid] = ENGINE[bid]["css"]
header = footer = ""
if landing:
    header = render_block("LP", "lp", slots_for("LP", "lp", 1)); used_css["LP"] = ENGINE["LP"]["css"]
    footer = render_block("LP-footer", "lp-footer", slots_for("LP-footer", "lp-footer", 1)); used_css["LP-footer"] = ENGINE["LP-footer"]["css"]
else:
    needs.append("This plan uses website header and footer blocks (G1/G3), which are not in the engine yet: page-designer adds them")

tok = dict(roles)
tok.update({f"--tone-{k}": v for k, v in sorted(tones.items()) if k in TONE_L})
tok.update({"--ink": ink, "--font-display": fonts["display"], "--font-body": fonts["body"], "--ornament": orn_css})
over = dict(shape); over.update(brand_over); over.update(B.get("tokens") or {})
token_block = ":root {\n  /* colours: " + colour_source + " from " + seed + " */\n" + "".join(f"  {k}: {v};\n" for k, v in tok.items()) + "}"
block_css = "".join(f"\n/* block:{k} */\n{v}\n/* /block:{k} */\n" for k, v in used_css.items())
if missing: block_css += "\n/* block:engine-missing */\n.engine-missing { padding: var(--space-5) 0; text-align: center; outline: 2px dashed var(--md-sys-color-outline); outline-offset: -12px; }\n/* /block:engine-missing */\n"
extra = ""
if B.get("extra_css"):
    ep = pathlib.Path(B["extra_css"]); ep = ep if ep.is_absolute() else work / ep
    if ep.exists(): extra = f"\n/* block:signature */\n{ep.read_text(encoding='utf-8').strip()}\n/* /block:signature */\n"
    else: warnings.append(f"extra_css not found: {ep}")
version = (KIT / "VERSION").read_text().strip()
title = B.get("page_title") or f"{practice} | {G['cta_primary']}"
desc = B.get("meta_description") or f"{G['cta_primary']} with {practice}."
page = f"""<!doctype html>
<html lang="en">
<head>
<!-- Built with create-page v{version} (engine, theme {theme}) -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{html.escape(fonts['href'])}" rel="stylesheet">
<!-- Analytics: add only a HIPAA-reviewed, BAA-covered tool here. -->
<style>
{token_block}
{(ENG / 'base.css').read_text(encoding='utf-8').strip()}
{(ENG / 'themes' / f'{theme}.css').read_text(encoding='utf-8').strip()}
{(":root {" + chr(10) + "  /* per-practice choices and brand rules: after the theme so they win */" + chr(10) + "".join(f"  {k}: {v};" + chr(10) for k, v in over.items()) + "}" + chr(10)) if over else ""}{block_css}{extra}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
{header}
<main id="main">
{chr(10).join(sections)}
</main>
{footer}
</body>
</html>
"""
(work / "index.html").write_text(page, encoding="utf-8")

# ── Tweak support: alternates + options ──────────────────────────────────
alts, seen = [], set()
for bid, key, s in keys_slots:
    for sib in siblings(bid):
        if (bid, sib) in seen: continue
        seen.add((bid, sib))
        sib_slots = slots_for(sib, key, 1, extra=s)
        alts.append(f'<style data-variant="{sib}">\n{ENGINE[sib]["css"]}\n</style>\n<template data-alt-for="{bid}" data-variant="{sib}" data-label="{html.escape(ENGINE[sib]["name"])}">\n{render_block(sib, key, sib_slots)}\n</template>')
(work / "alternates.html").write_text("\n".join(alts) + "\n", encoding="utf-8")
palettes = []
for variant, label in ([] if BR else  (("tonal_spot", "Softer"), ("vibrant", "Brighter"))):
    g = m3(seed, variant) if got else None
    if g: palettes.append({"name": f"{label} ({variant})", "tokens": g[0]})
if not palettes and not BR:
    _, c0, h0 = to_oklch(hex2rgb(seed))
    for dh, label in ((-25, "Cooler"), (25, "Warmer")):
        alt_seed = oklch_hex(0.5, max(c0, 0.06), (h0 + dh) % 360)
        palettes.append({"name": f"{label} ({alt_seed})", "tokens": oklch_scheme(alt_seed)[0]})
font_opts = [dict(fonts)] + TH.get("alt_fonts", [])
for other in (ENG / "themes").glob("*.json"):
    o = json.loads(other.read_text())
    if o["name"] != TH["name"]: font_opts.append(o["fonts"])
uniq = list({fo["name"]: fo for fo in font_opts}.values())
(work / "tweak-options.json").write_text(json.dumps({"palettes": palettes, "fonts": uniq[1:], "brand_locked": ({"colors": True, "fonts": bool(bf.get("display"))} if BR else B.get("brand_locked", {}))}, indent=1), encoding="utf-8")

if missing: needs.append(f"Build these blocks in the page's style (not in the engine yet): {', '.join(dict.fromkeys(missing))}")
print(json.dumps({"files": [str(work / n) for n in ("index.html", "alternates.html", "tweak-options.json")],
                  "size_kb": round(len(page.encode()) / 1024, 1), "theme": theme, "fonts": fonts["name"], "colours": colour_source,
                  "blocks": main_ids, "missing": missing, "brand_mode": bool(BR), "brand_assumptions": assumptions, "alternates": len(alts), "needs_designer": needs, "warnings": warnings,
                  "seconds": round(time.time() - T0, 2)}, indent=1))
