#!/usr/bin/env python3
"""Build a clickable wireframe of a block plan from the kit's block library.
Usage: python3 wireframe.py <work>/content/plan.md [--out <work>/wireframe.html] [--title "Practice - Landing page"] [--png]
       python3 wireframe.py --blocks "LP,M01-B,M10,M11-A,M26-A,M31,M29,LP" [--out ...]

Reads the ordered block IDs from plan.md (one block per line, e.g. "1. M01-B: Message 1, seen this week"),
takes each block's desktop and mobile layout from <kit>/blocks/, and stacks them in plan order in one HTML
file with a Desktop / Mobile switch. The rest of each plan line becomes the block's caption.
The wireframe shows the block library's sample copy and gray styling: layout only, not the final design or words.
--png also saves <out>.png (desktop, full page) and <out>-mobile.png with Playwright, if it is installed.
Prints JSON: output path, blocks used, and any IDs it could not find."""
import argparse, html, json, pathlib, re, sys

KIT = pathlib.Path(__file__).resolve().parent.parent
BLOCKS = KIT / "blocks"
ID_RE = re.compile(r"\b(LP|G[1-3]|M\d{2})(?:[-\s]?(?:variant\s+)?([A-C]))?\b")

ap = argparse.ArgumentParser()
ap.add_argument("plan", nargs="?", help="plan.md with one block per line")
ap.add_argument("--blocks", default="", help="comma-separated block IDs instead of plan.md")
ap.add_argument("--out", default="")
ap.add_argument("--title", default="Block plan wireframe")
ap.add_argument("--png", action="store_true")
a = ap.parse_args()
if not a.plan and not a.blocks:
    sys.exit("Give a plan.md path or --blocks")

# 1. Ordered (id, variant, caption) list
items = []
if a.blocks:
    for tok in a.blocks.split(","):
        m = ID_RE.search(tok.strip())
        if m: items.append((m.group(1), m.group(2), ""))
else:
    for line in pathlib.Path(a.plan).read_text(encoding="utf-8").splitlines():
        # only list lines whose first word is a block ID ("2. M01-B: ...", "- M10 ...", "| 3 | M10 | ..."),
        # so IDs mentioned in notes or benchmark ideas are not added as blocks
        head = re.sub(r"^[\s|#>*`•-]*(?:\d+[.)]?[\s|*`]*)?", "", line)
        m = ID_RE.match(head)
        if not m: continue
        line, m = head, m
        caption = line[m.end():].strip(" :-|·*`").strip()
        caption = re.sub(r"\s*\|\s*", " · ", caption).strip(" ·")
        items.append((m.group(1), m.group(2), caption))
if not items:
    sys.exit("No block IDs found (expected IDs like M01-B, M10, G1, LP)")

def find(bid, var):
    """Return (path, note). Variant blocks default to A when no variant is given."""
    if var:
        hits = sorted(BLOCKS.glob(f"{bid}-*-{var}.html"))
        if hits: return hits[0], ""
    hits = sorted(BLOCKS.glob(f"{bid}-*.html"))
    if not hits: return None, ""
    if len(hits) > 1:
        a_hit = [h for h in hits if h.stem.endswith("-A")]
        return (a_hit or hits)[0], f"no variant given, showing {bid}-A" if not var else f"variant {var} not found, showing {bid}-A"
    return hits[0], ""

def scope(css, sel):
    """Prefix every selector so one block's styles never leak into another."""
    out = []
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = ", ".join(f"{sel} {s.strip()}" for s in rule.group(1).split(",") if s.strip())
        out.append(f"{sels}{{{rule.group(2)}}}")
    return "\n".join(out)

def frame(src, kind):
    m = re.search(rf'<section class="doc-frame v-{kind}">(.*?)</section>\s*(?=<div class="doc-(?:label|end)")', src, re.S)
    return m.group(1).strip() if m else ""

sections, used, missing = [], [], []
seen_lp = False
for n, (bid, var, caption) in enumerate(items, 1):
    real_id, note = bid, ""
    if bid == "LP":   # landing header/footer: simplified G1/G3
        real_id, note = ("G3", "LP footer: legal links only") if seen_lp else ("G1", "LP header: logo, phone and CTA only, no nav")
        seen_lp = True
    path, vnote = find(real_id, var)
    note = "; ".join(x for x in (note, vnote) if x)
    label = f"{bid}-{var}" if var else bid
    if not path:
        missing.append(label)
        sections.append(f'<section class="wf-block" id="b{n}"><div class="wf-cap"><b>{n}</b><span class="wf-id">{html.escape(label)}</span>'
                        f'<span>{html.escape(caption)}</span></div><div class="wf-missing">No block file for {html.escape(label)}</div></section>')
        continue
    src = path.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = "\n".join(l for l in css.splitlines() if l.strip().startswith((".v-desktop", ".v-mobile")))
    name = re.sub(r"^[A-Z]\d+-", "", path.stem).replace("-", " ")
    desk, mob = frame(src, "desktop"), frame(src, "mobile")
    used.append({"position": n, "id": label, "file": path.name, **({"note": note} if note else {})})
    sections.append(
        f'<section class="wf-block" id="b{n}"><style>{scope(css, f"#b{n}")}</style>'
        f'<div class="wf-cap"><b>{n}</b><span class="wf-id">{html.escape(label)}</span><span class="wf-name">{html.escape(name)}</span>'
        f'<span>{html.escape(caption)}</span>{f"<em>{html.escape(note)}</em>" if note else ""}</div>'
        f'<div class="wf-frame v-desktop">{desk}</div>'
        f'<div class="wf-frame v-mobile">{mob or "<p class=wf-missing>No mobile layout in this block file; it stacks to one column.</p>"}</div></section>')

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(a.title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#E9EBEE;font-family:Inter,system-ui,sans-serif;color:#0A0A0A}}
.wf-top{{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;justify-content:space-between;padding:16px 24px;background:#0A0A0A;color:#fff}}
.wf-top h1{{margin:0;font-size:18px;font-weight:800}}
.wf-top p{{margin:2px 0 0;font-size:13px;color:#C9CDD3}}
.wf-switch{{display:flex;background:#2A2D33;border-radius:999px;padding:4px}}
.wf-switch button{{font:600 14px Inter,sans-serif;border:0;border-radius:999px;padding:10px 18px;min-height:44px;background:none;color:#fff;cursor:pointer}}
.wf-switch button[aria-pressed=true]{{background:#fff;color:#0A0A0A}}
.wf-list{{padding:24px;display:flex;flex-direction:column;gap:28px;align-items:center}}
.wf-block{{width:100%;display:flex;flex-direction:column;align-items:center}}
.wf-cap{{align-self:stretch;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:baseline;margin:0 0 10px;font-size:14px;color:#3F444C}}
.wf-cap b{{display:inline-grid;place-items:center;min-width:28px;height:28px;border-radius:50%;background:#1463FF;color:#fff;font-size:13px}}
.wf-id{{font-weight:800;color:#0A0A0A}}
.wf-name{{font-weight:600;text-transform:capitalize}}
.wf-cap em{{color:#8A5A00;font-style:normal;font-size:13px}}
.wf-frame{{box-shadow:0 1px 3px rgba(0,0,0,.08),0 8px 24px rgba(0,0,0,.06);overflow:hidden;transform-origin:top left}}
.wf-missing{{padding:32px;background:#fff;border:2px dashed #C2410C;color:#C2410C;font-weight:600}}
body[data-view=desktop] .v-mobile,body[data-view=mobile] .v-desktop{{display:none}}
</style></head>
<body data-view="desktop">
<header class="wf-top"><div><h1>{html.escape(a.title)}</h1>
<p>Wireframe: block order and layout only. Sample words and gray styling come from the block library; the final page uses the practice's brand and real copy.</p></div>
<div class="wf-switch" role="group" aria-label="View"><button type="button" aria-pressed="true" data-v="desktop">Desktop</button><button type="button" aria-pressed="false" data-v="mobile">Mobile</button></div></header>
<main class="wf-list">
{chr(10).join(sections)}
</main>
<script>
const fit=()=>{{const max=document.querySelector('.wf-list').clientWidth;
 document.querySelectorAll('.wf-frame').forEach(f=>{{const inner=f.firstElementChild; if(!inner) return;
  f.style.zoom=''; const w=inner.scrollWidth; if(w>max) f.style.zoom=(max/w).toFixed(4);}});}};
document.querySelectorAll('.wf-switch button').forEach(b=>b.addEventListener('click',()=>{{
 document.body.dataset.view=b.dataset.v;
 document.querySelectorAll('.wf-switch button').forEach(x=>x.setAttribute('aria-pressed',x===b));fit();}}));
addEventListener('resize',fit); addEventListener('load',fit); fit();
</script>
</body></html>"""

out = pathlib.Path(a.out).resolve() if a.out else (pathlib.Path(a.plan).resolve().parent.parent / "wireframe.html" if a.plan else pathlib.Path("wireframe.html").resolve())
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(page, encoding="utf-8")
report = {"wireframe": str(out), "blocks": used, "missing": missing, "kb": round(len(page.encode()) / 1024, 1)}

if a.png:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            for view, w in (("desktop", 1280), ("mobile", 430)):
                pg = b.new_page(viewport={"width": w, "height": 900})
                pg.goto(out.as_uri()); pg.wait_for_load_state("networkidle")
                if view == "mobile": pg.click("button[data-v=mobile]")
                png = out.with_suffix(".png") if view == "desktop" else out.with_name(out.stem + "-mobile.png")
                pg.screenshot(path=str(png), full_page=True); report[f"png_{view}"] = str(png)
            b.close()
    except Exception as e:
        report["png_note"] = f"PNG not made ({type(e).__name__}); open the HTML instead"

print(json.dumps(report, indent=1))
