#!/usr/bin/env python3
"""Prepare a logo for a single-file page.
Usage: python3 logo.py <logo.png|jpg|jpeg|webp|svg> [--out <folder>] [--max-width 400]

Raster logos: trims empty space (transparent or flat background), resizes to at most 400px wide,
writes <name>.datauri.txt (a WebP or PNG data URI) for <img src="...">.
SVG logos: removes scripts, event handlers, comments, metadata and editor junk, trims the viewBox to the
artwork (needs Playwright), writes <name>.clean.svg (inline) and <name>.datauri.txt (for <img src="...">).
Prints JSON: output paths, size, tone ("light" = mostly white or very light, needs a dark or brand-color
background; "dark" otherwise), the main color, and contrast against white and against near-black.
Needs Pillow (pip install --break-system-packages pillow); Playwright is optional, for SVG trim and tone."""
import argparse, base64, io, json, pathlib, re, sys
from collections import Counter

try:
    from PIL import Image
except ImportError:
    sys.exit("logo.py needs Pillow: pip install --break-system-packages pillow")

ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("--out", default=""); ap.add_argument("--max-width", type=int, default=400)
a = ap.parse_args()
src = pathlib.Path(a.file).resolve()
out_dir = pathlib.Path(a.out).resolve() if a.out else src.parent
out_dir.mkdir(parents=True, exist_ok=True)
ext = src.suffix.lower()
if ext not in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
    sys.exit(f"Unsupported logo type {ext}: use PNG, JPG, SVG or WebP")

def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(c1, c2):
    l1, l2 = sorted((lum(c1), lum(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

def pixels(im):
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())

def hexc(rgb): return "#%02X%02X%02X" % tuple(rgb)

def trim(im):
    """Crop to the artwork: by alpha when transparent, otherwise by difference from the corner color.
    Returns (image, flat_bg) where flat_bg is the background color for opaque images, else None."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    bg = None
    if alpha.getextrema()[0] < 250:
        box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    else:
        rgb = im.convert("RGB"); w, h = rgb.size
        corners = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        bg = Counter(corners).most_common(1)[0][0]
        diff = Image.new("L", rgb.size)
        diff.putdata([255 if sum(abs(p[i] - bg[i]) for i in range(3)) > 30 else 0 for p in pixels(rgb)])
        box = diff.getbbox()
    return (im.crop(box) if box else im), bg

def tone(im, flat_bg=None):
    """Classify the visible pixels: opaque ones, minus the flat background color of an opaque image."""
    im = im.convert("RGBA")
    small = im.copy(); small.thumbnail((200, 200))
    px = [p[:3] for p in pixels(small) if p[3] > 128]
    if not px: return {"tone": "unknown", "main_color": None}
    if flat_bg:
        fg = [p for p in px if sum(abs(p[i] - flat_bg[i]) for i in range(3)) > 30]
        px = fg or px
    mean_l = sum(lum(p) for p in px) / len(px)
    light_share = sum(1 for p in px if lum(p) > 0.6) / len(px)
    q = Counter(tuple((c // 16) * 16 + 8 for c in p) for p in px)
    colored = [(c, n) for c, n in q.most_common() if max(c) - min(c) > 40]   # prefer a real hue over grey/black/white
    main = (colored[0][0] if colored and colored[0][1] > len(px) * 0.05 else q.most_common(1)[0][0])
    light = light_share > 0.7 or mean_l > 0.6
    return {"tone": "light" if light else "dark", "main_color": hexc(main),
            "contrast_on_white": round(contrast(main, (255, 255, 255)), 2),
            "contrast_on_dark": round(contrast(main, (25, 27, 36)), 2),
            "light_pixel_share": round(light_share, 2)}

def encode(im):
    buf = io.BytesIO()
    try:
        im.save(buf, "WEBP", quality=90, method=6); mime = "image/webp"
    except Exception:
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True); mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()

report = {"source": str(src)}

if ext == ".svg":
    svg = src.read_text(encoding="utf-8", errors="replace")
    svg = re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>|<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<(script|metadata|foreignObject|sodipodi:[\w-]+|inkscape:[\w-]+)\b.*?(</\1>|/>)", "", svg, flags=re.S | re.I)
    svg = re.sub(r"\s(on\w+|xmlns:(sodipodi|inkscape)|(sodipodi|inkscape):[\w-]+)\s*=\s*(\"[^\"]*\"|'[^']*')", "", svg, flags=re.I)
    svg = re.sub(r"(href\s*=\s*[\"'])\s*javascript:[^\"']*", r"\1#", svg, flags=re.I)
    open_tag = re.search(r"<svg\b[^>]*>", svg, flags=re.I)
    if not open_tag: sys.exit("No <svg> element found")
    tag = open_tag.group(0)
    if "viewbox" not in tag.lower():
        w = re.search(r'\swidth\s*=\s*["\']([\d.]+)', tag); h = re.search(r'\sheight\s*=\s*["\']([\d.]+)', tag)
        if w and h: tag = tag[:-1] + f' viewBox="0 0 {w.group(1)} {h.group(1)}">'
    if "xmlns=" not in tag: tag = tag[:-1] + ' xmlns="http://www.w3.org/2000/svg">'
    svg = svg[:open_tag.start()] + tag + svg[open_tag.end():]
    svg = svg.strip()
    raster = None
    try:   # trim the viewBox to the artwork and render once for tone analysis
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 800})
            pg.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
            box = pg.evaluate("""() => { const s=document.querySelector('svg'); const b=s.getBBox();
                return b.width&&b.height ? [b.x,b.y,b.width,b.height] : null }""")
            if box:
                vb = " ".join(str(round(v, 2)) for v in box)
                svg = re.sub(r'viewBox\s*=\s*["\'][^"\']*["\']', f'viewBox="{vb}"', svg, count=1, flags=re.I)
                report["trimmed_viewbox"] = vb
            for _ in range(2):   # drop fixed width and height so CSS sizes the logo
                svg = re.sub(r'(<svg\b[^>]*?)\s(width|height)\s*=\s*["\'][^"\']*["\']', r"\1", svg, count=1, flags=re.I)
            pg.set_content(f'<body style="margin:0;background:transparent"><div style="width:600px">{svg}</div></body>')
            pg.evaluate("document.querySelector('svg').style.width='600px';document.querySelector('svg').style.height='auto'")
            raster = Image.open(io.BytesIO(pg.locator("svg").screenshot(omit_background=True)))
            b.close()
    except Exception as e:
        report["note"] = f"SVG not trimmed or analysed (Playwright unavailable: {type(e).__name__}); check the logo by eye"
    clean = out_dir / f"{src.stem}.clean.svg"; clean.write_text(svg, encoding="utf-8")
    uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    (out_dir / f"{src.stem}.datauri.txt").write_text(uri)
    report.update({"kind": "svg", "inline_svg": str(clean), "data_uri_file": str(out_dir / f"{src.stem}.datauri.txt"),
                   "bytes": len(svg.encode())})
    if raster is not None:
        report["aspect_ratio"] = round(raster.width / raster.height, 3)
        report.update(tone(raster))
    else:
        cols = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in re.findall(r"#([0-9a-fA-F]{6})\b", svg)]
        if cols:
            main = Counter(cols).most_common(1)[0][0]
            report.update({"tone": "light" if lum(main) > 0.6 else "dark", "main_color": hexc(main),
                           "contrast_on_white": round(contrast(main, (255, 255, 255)), 2),
                           "contrast_on_dark": round(contrast(main, (25, 27, 36)), 2)})
        else:
            report.update({"tone": "unknown", "main_color": None})
else:
    im, flat_bg = trim(Image.open(src))
    if im.width > a.max_width:
        im = im.resize((a.max_width, round(im.height * a.max_width / im.width)), Image.LANCZOS)
    uri = encode(im)
    f = out_dir / f"{src.stem}.datauri.txt"; f.write_text(uri)
    report.update({"kind": "raster", "data_uri_file": str(f), "width": im.width, "height": im.height,
                   "aspect_ratio": round(im.width / im.height, 3), "bytes": len(uri)})
    report.update(tone(im, flat_bg))

report["placement"] = ("LIGHT logo: place it only on a dark or brand-color background (dark header band or dark footer), never on white."
                       if report.get("tone") == "light" else
                       "Dark logo: place it on a light background; on a dark band use a light version if the brand has one."
                       if report.get("tone") == "dark" else "Tone unknown: check the logo by eye before placing it.")
print(json.dumps(report, indent=1))
