#!/usr/bin/env python3
"""Convert the kit's page into a Claude Design canvas (one full-width page artboard), for "Edit in Claude Design".
Usage: python3 to_design.py <work>/index.html [--out <work>/design] [--title "Practice landing page"]
       python3 to_design.py <work>/index.html --out <work>/design --fill <work>/design/urls.json

Step 1 (no --fill) writes, under <out>:
  project/canvas.json     the canvas index: one artboard, Main.dc.html, a fluid page ("expand": "fill") 1440px wide
  project/Main.dc.html    the page as a Design Component artboard: the page's <style> and font link in <helmet>,
                          the body markup in <x-dc> (scripts removed: a canvas runs none), every attribute quoted and
                          every element closed, data-block sections kept so the page can come back to the kit
  assets/                 every embedded image (img src and CSS url() data URIs) as a file to upload, with
  assets.json             [{"token": "__TW_ASSET_1__", "file": "assets/asset-1.webp"}]: the token stands in the
                          artboard until the upload gives each file its /_blob/<id> address
Step 2 (--fill urls.json, {"__TW_ASSET_1__": "/_blob/<id>", ...}) puts the uploaded addresses into Main.dc.html.
The orchestrator then publishes project/canvas.json and project/Main.dc.html to a new Design canvas
(START-HERE.md 0.8). from_design.py brings the edited artboard back. Needs Playwright (to measure the page height)."""
import argparse, base64, datetime as dt, hashlib, html, json, pathlib, re, sys
from html.parser import HTMLParser

ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--out", default=""); ap.add_argument("--title", default="")
ap.add_argument("--fill", default="")
a = ap.parse_args()
page = pathlib.Path(a.page).resolve(); out = pathlib.Path(a.out).resolve() if a.out else page.with_name("design")
art = out / "project" / "Main.dc.html"

if a.fill:   # step 2: put the uploaded addresses in place of the tokens
    urls = json.loads(pathlib.Path(a.fill).read_text())
    s = art.read_text(encoding="utf-8"); left = []
    for tok, url in urls.items(): s = s.replace(tok, url)
    left = sorted(set(re.findall(r"__TW_ASSET_\d+__", s)))
    art.write_text(s, encoding="utf-8")
    print(json.dumps({"artboard": str(art), "filled": len(urls), "missing": left})); sys.exit(1 if left else 0)

src = page.read_text(encoding="utf-8")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
assets, seen = [], {}
(out / "assets").mkdir(parents=True, exist_ok=True); (out / "project").mkdir(parents=True, exist_ok=True)
def asset(datauri):
    if datauri in seen: return seen[datauri]
    m = re.match(r"data:([\w/+.-]+)(;base64)?,(.*)", datauri, re.S)
    if not m: return datauri
    mime, b64, body = m.groups()
    ext = {"image/svg+xml": "svg", "image/jpeg": "jpg"}.get(mime, mime.split("/")[-1].split("+")[0])
    data = base64.b64decode(body) if b64 else urllib_unquote(body).encode()
    n = len(assets) + 1; f = out / "assets" / f"asset-{n}.{ext}"; f.write_bytes(data)
    tok = f"__TW_ASSET_{n}__"; assets.append({"token": tok, "file": str(f.relative_to(out)), "type": mime}); seen[datauri] = tok
    return tok
def urllib_unquote(s):
    from urllib.parse import unquote; return unquote(s)

class Conv(HTMLParser):
    """Re-serialises the body as strict markup and collects the head's style and font links."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.styles = []; self.fonts = []; self.title = ""
        self.where = []; self.skip = 0; self.in_body = False
    def handle_starttag(self, tag, attrs):
        if tag == "body": self.in_body = True; return
        if tag in ("script", "noscript"): self.skip += 1; return
        if tag == "style": self.where.append("style"); return
        if tag == "title": self.where.append("title"); return
        if tag == "link":
            d = dict(attrs)
            if "fonts.googleapis.com/css2" in (d.get("href") or ""): self.fonts.append(d["href"])
            return
        if not self.in_body or self.skip: return
        parts = []
        for k, v in attrs:
            if k.startswith("on"): continue
            v = "" if v is None else v
            if k in ("src", "href", "poster") and v.startswith("data:"): v = asset(v)
            if k == "style": v = re.sub(r'url\(\s*(?:"(data:[^"]*)"|\'(data:[^\']*)\'|(data:[^)\s]*))\s*\)', lambda m: f'url("{asset(m.group(1) or m.group(2) or m.group(3))}")', v)
            parts.append(f' {k}="{html.escape(v, quote=True)}"')
        self.out.append(f"<{tag}{''.join(parts)}>" if tag in VOID else f"<{tag}{''.join(parts)}>")
        if tag in VOID: return
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.in_body and not self.skip and tag not in ("script", "style", "title", "link", "body"): self.out.append(f"</{tag}>")
    def handle_endtag(self, tag):
        if tag in ("script", "noscript"): self.skip = max(0, self.skip - 1); return
        if tag in ("style", "title") and self.where: self.where.pop(); return
        if tag in ("body", "html", "head") or tag in VOID or not self.in_body or self.skip: return
        self.out.append(f"</{tag}>")
    def handle_data(self, d):
        if self.where and self.where[-1] == "style": self.styles.append(d); return
        if self.where and self.where[-1] == "title": self.title += d; return
        if self.in_body and not self.skip: self.out.append(html.escape(d, quote=False))
    def handle_comment(self, d):
        if self.in_body and not self.skip and "HIPAA" in d: self.out.append(f"<!--{d}-->")

c = Conv(); c.feed(src)
css = "\n".join(c.styles)
DATA_URL = re.compile(r'url\(\s*(?:"(data:[^"]*)"|\'(data:[^\']*)\'|(data:[^)\s]*))\s*\)')   # quoted with " or ', or bare
css = DATA_URL.sub(lambda m: f'url("{asset(m.group(1) or m.group(2) or m.group(3))}")', css)
body = "".join(c.out).strip()

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 900}); pg.goto(page.as_uri()); pg.wait_for_timeout(400)
    H = int(pg.evaluate("Math.ceil(document.documentElement.scrollHeight)")); b.close()

title = a.title or html.unescape(c.title.strip()) or page.parent.name
digest = hashlib.sha1(src.encode()).hexdigest()[:12]
fonts = "".join(f'\n<link rel="stylesheet" href="{html.escape(f, quote=True)}">' for f in c.fonts)
props = json.dumps({"$preview": {"width": 1440, "height": H}})
artboard = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<!-- from the page builder kit: source page_hash {digest}; bring it back with from_design.py -->
<x-dc>
<helmet>{fonts}
<style>
{css.strip()}
</style>
</helmet>
<div class="kit-page">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
"""
art.write_text(artboard, encoding="utf-8")
canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, "title": title,
          "launch": {"view": "canvas"}, "pages": [], "boards": {"Main.dc.html": {"x": 0, "y": 0, "w": 1440, "h": H, "title": "Page", "expand": "fill"}},
          "order": ["Main.dc.html"], "notes": {}, "designSystems": []}
(out / "project" / "canvas.json").write_text(json.dumps(canvas, indent=1), encoding="utf-8")
(out / "assets.json").write_text(json.dumps(assets, indent=1), encoding="utf-8")
print(json.dumps({"root": str(out), "canvas": str(out / "project" / "canvas.json"), "artboard": str(art), "height": H,
                  "assets_to_upload": [x["file"] for x in assets], "size_kb": round(len(artboard.encode()) / 1024, 1), "source_page_hash": digest}, indent=1))
