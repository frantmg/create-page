#!/usr/bin/env python3
"""Bring an edited Claude Design artboard back into the kit's single-file page ("bring the design back").
Usage: python3 from_design.py <artboard.dc.html> --base <work>/backups/index-before-design.html --out <work>/index.html
                              [--assets <folder with the canvas assets, each named <id>.<ext>>]

Takes the artboard's <helmet> styles and font links back into the page's <style> and <head>, its <x-dc> markup back
into <body>, fills any {{hole}} with its data-props default, swaps every /_blob/<id> address for the downloaded asset
(embedded as a data URI), and adds back the head (title, meta, built-with line) and the scripts (menu, tabs,
before/after) from the base page, since a canvas runs no scripts of its own.
Prints JSON: blocks found, whether they are still direct children of <main> (the tweak bar needs that), holes filled,
assets embedded or missing, and Design-only parts (<dc-import>, <sc-for>, <sc-if>, mounted components) that the
designer has to rebuild in the page. Then run qa.py (with --brand when there is a brand.json) on the result."""
import argparse, base64, html, json, mimetypes, pathlib, re, sys

ap = argparse.ArgumentParser(); ap.add_argument("artboard"); ap.add_argument("--base", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--assets", default="")
a = ap.parse_args()
s = pathlib.Path(a.artboard).read_text(encoding="utf-8")
base = pathlib.Path(a.base).read_text(encoding="utf-8")
report = {"blocks": [], "blocks_in_main": True, "holes_filled": 0, "assets_embedded": 0, "assets_missing": [], "design_only": []}

helmet = re.search(r"<helmet>(.*?)</helmet>", s, re.S)
hel = helmet.group(1) if helmet else ""
css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", hel, re.S)).strip()
fonts = re.findall(r'<link[^>]+href="([^"]*fonts\.googleapis\.com/css2[^"]*)"', hel)
xdc = re.search(r"<x-dc>(.*?)</x-dc>", s, re.S)
body = xdc.group(1) if xdc else ""
body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S).strip()
root = re.match(r'\s*<div class="kit-page">(.*)</div>\s*$', body, re.S)
if root: body = root.group(1).strip()

props = re.search(r"data-props='(.*?)'", s, re.S)
defaults = {}
if props:
    try: defaults = {k: v.get("default") for k, v in json.loads(html.unescape(props.group(1))).items() if isinstance(v, dict) and "default" in v}
    except json.JSONDecodeError: pass
def hole(m):
    k = m.group(1).split(".")[0]
    if k in defaults: report["holes_filled"] += 1; return html.escape(str(defaults[k]))
    return m.group(0)
body = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", hole, body); css = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", hole, css)
left_holes = sorted(set(re.findall(r"\{\{\s*([\w.]+)\s*\}\}", body + css)))
if left_holes: report["design_only"].append(f"values set in Claude Design's code ({', '.join(left_holes)}): set them by hand")

assets = {}
if a.assets:
    for f in pathlib.Path(a.assets).glob("*"):
        if f.is_file(): assets[f.stem] = f
def blob(m):
    aid = m.group(1); f = assets.get(aid)
    if not f: report["assets_missing"].append(aid); return m.group(0)
    report["assets_embedded"] += 1
    mime = mimetypes.guess_type(f.name)[0] or "image/webp"
    return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
body = re.sub(r"/_blob/([A-Za-z0-9_-]+)", blob, body); css = re.sub(r"/_blob/([A-Za-z0-9_-]+)", blob, css)

for tag in ("dc-import", "sc-for", "sc-if", "x-import"):
    if f"<{tag}" in body: report["design_only"].append(f"<{tag}> (a Claude Design feature): rebuild it as plain markup")
report["blocks"] = re.findall(r'data-block="([^"]+)"', body)
main = re.search(r"<main[^>]*>(.*?)</main>", body, re.S)
if main:   # every block section must still be a direct child of <main>
    depth, ok = 0, True
    for m in re.finditer(r"<(/?)(\w[\w-]*)([^>]*)>", main.group(1)):
        close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if tag in ("img", "br", "hr", "input", "meta", "link", "source", "wbr"): continue
        if not close:
            if "data-block=" in attrs and depth != 0: ok = False
            depth += 1
        else: depth -= 1
    report["blocks_in_main"] = ok
else: report["blocks_in_main"] = False

head = re.search(r"<head>(.*?)</head>", base, re.S).group(1)
head = re.sub(r"<style>.*?</style>", lambda m: "<style>\n" + css + "\n</style>", head, count=1, flags=re.S)
if fonts:
    head = re.sub(r'<link[^>]+fonts\.googleapis\.com/css2[^>]*>', "", head)
    head = head.replace("<style>", "".join(f'<link href="{f}" rel="stylesheet">\n' for f in fonts) + "<style>", 1)
scripts = "\n".join(re.findall(r"<script(?![^>]*src=)[^>]*>.*?</script>", re.search(r"<body[^>]*>(.*)</body>", base, re.S).group(1), re.S))
page = f"<!doctype html>\n<html lang=\"en\">\n<head>{head}</head>\n<body>\n{body}\n{scripts}\n</body>\n</html>\n"
pathlib.Path(a.out).write_text(page, encoding="utf-8")
report["out"] = a.out; report["size_kb"] = round(len(page.encode()) / 1024, 1)
print(json.dumps(report, indent=1))
