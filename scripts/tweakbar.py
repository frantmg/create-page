#!/usr/bin/env python3
"""Make a tweak page for a finished page: the page in a live preview with a tweak bar beside it.
Usage: python3 tweakbar.py <work>/index.html [--alternates <work>/alternates.html] [--options <work>/tweak-options.json]
                           [--seeds "#0F6E6E,#7A3E9D"] [--out <work>/tweak.html]

The tweak bar lets the user try palettes, a new main colour, single colour tokens (with a live WCAG AA contrast
check), font pairings or any Google font, heading and body size, spacing, corners, shadows, page width and button
shape; and per block: move, hide, swap to another version, change the background, edit text and leave notes.
"Finish" exports every change as tweaks.json (copy or download) for the orchestrator to route (START-HERE.md 0.7).

Inputs next to index.html are picked up automatically when present:
  alternates.html      other versions of blocks, built by page-designer in the page's own style (rules/design-build.md 5.10):
                       <style> for the versions, then <template data-alt-for="M05-B" data-variant="M05-A" data-label="...">
                       <section data-block="M05-A">...</section></template>
  tweak-options.json   {"palettes": [{"name": "...", "tokens": {"--md-sys-color-primary": "#..."}}],
                        "fonts": [{"name": "...", "display": "\\"Font\\", serif", "body": "...", "href": "https://fonts.googleapis.com/..."}],
                        "brand_locked": {"colors": false, "fonts": true}}
--seeds adds one palette per brand hex, made with m3_scheme.py (needs materialyoucolor).

index.html is never changed. tweak.html is a review tool: never deliver it as the page or publish it in place of index.html.
Prints JSON: output path, size, blocks, alternates found, palettes, font pairings and warnings."""
import argparse, hashlib, html, json, pathlib, re, subprocess, sys
from html.parser import HTMLParser

KIT = pathlib.Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

ap = argparse.ArgumentParser()
ap.add_argument("page")
ap.add_argument("--alternates", default="")
ap.add_argument("--options", default="")
ap.add_argument("--seeds", default="", help="comma-separated brand hex colours; one M3 palette each")
ap.add_argument("--out", default="")
a = ap.parse_args()

page = pathlib.Path(a.page).resolve()
if not page.exists(): sys.exit(f"Not found: {page}")
src = page.read_text(encoding="utf-8")
alt_path = pathlib.Path(a.alternates).resolve() if a.alternates else page.with_name("alternates.html")
opt_path = pathlib.Path(a.options).resolve() if a.options else page.with_name("tweak-options.json")
out = pathlib.Path(a.out).resolve() if a.out else page.with_name("tweak.html")
warnings = []

class Blocks(HTMLParser):
    """Finds [data-block] elements and whether each sits directly in <main> (or is the page header/footer)."""
    def __init__(self):
        super().__init__(); self.stack = []; self.blocks = []; self.templates = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "template" and "data-alt-for" in d:
            self.templates.append({"for": d["data-alt-for"], "variant": d.get("data-variant"), "label": d.get("data-label"), "root": None})
        elif self.templates and self.templates[-1]["root"] is None and self.stack and self.stack[-1][0] == "template":
            self.templates[-1]["root"] = (tag, d.get("data-block"))
        if "data-block" in d and not any(t == "template" for t, _ in self.stack):
            parent = self.stack[-1][0] if self.stack else ""
            in_main = any(t == "main" for t, _ in self.stack)
            self.blocks.append({"id": d["data-block"], "tag": tag, "parent": parent, "in_main": in_main})
        if tag not in VOID: self.stack.append((tag, d))
    def handle_startendtag(self, tag, attrs): pass
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag: del self.stack[i:]; break

pb = Blocks(); pb.feed(src)
main_blocks = [b for b in pb.blocks if b["in_main"]]
for b in main_blocks:
    if b["parent"] != "main":
        warnings.append(f"{b['id']} is not a direct child of <main> (inside <{b['parent']}>); the tweak bar can only move, hide and swap blocks that sit directly in <main>")
if not main_blocks: warnings.append("No <section data-block> found in <main>")
ids = [b["id"] for b in pb.blocks]

alternates, alt_found = "", {}
if alt_path.exists():
    alternates = alt_path.read_text(encoding="utf-8")
    ab = Blocks(); ab.feed(alternates)
    for t in ab.templates:
        root = t["root"]
        if not root or not root[1]:
            warnings.append(f"alternate for {t['for']}: the template must hold one element with data-block (e.g. <section data-block=\"M05-A\">)"); continue
        if t["for"] not in ids: warnings.append(f"alternate {root[1]} is for {t['for']}, which is not on the page")
        alt_found.setdefault(t["for"], []).append(t["variant"] or root[1])
elif a.alternates:
    warnings.append(f"alternates file not found: {alt_path}")

opts = {}
if opt_path.exists():
    try: opts = json.loads(opt_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e: warnings.append(f"{opt_path.name} is not valid JSON: {e}")
elif a.options:
    warnings.append(f"options file not found: {opt_path}")
palettes = [p for p in opts.get("palettes", []) if isinstance(p, dict) and p.get("name") and isinstance(p.get("tokens"), dict)]
fonts = [f for f in opts.get("fonts", []) if isinstance(f, dict) and f.get("name") and f.get("display")]
for f in fonts: f.setdefault("body", f["display"])

for seed in [s.strip() for s in a.seeds.split(",") if s.strip()]:
    if not re.fullmatch(r"#?[0-9a-fA-F]{6}", seed): warnings.append(f"seed {seed} is not a 6-digit hex colour"); continue
    seed = "#" + seed.lstrip("#").upper()
    r = subprocess.run([sys.executable, str(KIT / "scripts" / "m3_scheme.py"), seed], capture_output=True, text=True)
    if r.returncode != 0:
        warnings.append(f"m3_scheme.py failed for {seed} ({r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no output'}); "
                        "install with: pip install --break-system-packages materialyoucolor"); continue
    root = re.search(r":root\s*\{([^}]*)\}", r.stdout)
    tokens = dict(re.findall(r"(--md-sys-color-[\w-]+):\s*(#[0-9A-Fa-f]{6})", root.group(1))) if root else {}
    if tokens: palettes.append({"name": f"Brand {seed}", "tokens": tokens})

m = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
title = html.unescape(m.group(1).strip()) if m else page.parent.name
data = {
    "page": src, "page_file": str(page), "page_title": title, "page_hash": hashlib.sha1(page.read_bytes()).hexdigest()[:12],
    "kit_version": (KIT / "VERSION").read_text().strip(), "alternates": alternates,
    "palettes": palettes, "fonts": fonts, "brand_locked": opts.get("brand_locked", {}),
}
# JSON inside <script>: "</" and "<!--" are escaped so the page's own tags cannot close or comment out the script.
js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\u0021--")
tpl = (KIT / "templates" / "tweakbar.html").read_text(encoding="utf-8")
short = re.split(r"\s+[|·–-]\s+", title)[0][:40]
result = tpl.replace("__TITLE__", html.escape(f"{short} tweaks")).replace("__TWEAK_DATA__", js)
out.write_text(result, encoding="utf-8")

print(json.dumps({
    "output": str(out), "size_kb": round(out.stat().st_size / 1024, 1),
    "blocks": [b["id"] for b in main_blocks], "alternates": alt_found,
    "palettes": [p["name"] for p in palettes], "font_pairings": [f["name"] for f in fonts],
    "warnings": warnings,
}, indent=1))
