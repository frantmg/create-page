#!/usr/bin/env python3
"""Build blocks-lite/ from blocks/: each block reduced to its HTML structure and content slots.
Usage: python3 blocks_lite.py            (rewrites <kit>/blocks-lite/ from <kit>/blocks/)

Keeps the desktop markup only (the mobile copy and the page chrome are demo), drops every <style>, inline style,
font link and demo class, replaces icons with an empty <svg data-role="icon">, unwraps layout-only wrappers, and
turns the demo classes that carry meaning into data-role hints (eyebrow, media, button, card, field ...).
The block's slot list from rules/blocks-and-plan.md 3.1 goes in a comment at the top.
blocks/ stays the visual reference (wireframe.py uses it); agents read blocks-lite/.
Run it again whenever a file in blocks/ changes. Prints each file's size."""
import html, pathlib, re
from html.parser import HTMLParser

KIT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = KIT / "blocks", KIT / "blocks-lite"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP = {"D0"}  # D0 Foundations is a style guide, not a block
ROLE = {"ey": "eyebrow", "img": "media", "lead": "lead", "btn": "button", "lk": "text-link", "card": "card", "tag": "tag",
        "fld": "field", "lab": "label", "in": "input", "sel": "select", "cb": "checkbox", "ck": "check-item", "bi": "benefit-item",
        "ac": "accent-box", "rl": "rule-item", "pill": "pill", "stars": "stars", "num": "number", "faq": "faq-item", "tab": "tab",
        "crumb": "breadcrumb", "logo": "logo", "nav": "nav", "play": "play-button", "g": "tinted-band", "dot": "dot",
        "ico": "icon", "arrow": "arrow", "arow": "arrows", "on": "active"}
KEEP_ATTR = {"href", "alt", "type", "name", "placeholder", "for", "id", "aria-label", "aria-hidden", "role", "open", "value",
             "checked", "required", "autocomplete", "inputmode", "colspan", "scope", "loading", "src", "width", "height"}

class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.kids = tag, attrs or {}, parent, []

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.root = Node("#root"); self.cur = self.root
    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur); self.cur.kids.append(n)
        if tag not in VOID: self.cur = n
    def handle_startendtag(self, tag, attrs): self.cur.kids.append(Node(tag, dict(attrs), self.cur))
    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag: n = n.parent
        if n is not self.root: self.cur = n.parent
    def handle_data(self, d):
        if d.strip(): self.cur.kids.append(d)

def find(n, pred):
    for k in n.kids:
        if isinstance(k, Node):
            if pred(k): return k
            r = find(k, pred)
            if r: return r

def clean(n):
    """Return a cleaned copy of the subtree (or None to drop it)."""
    if n.tag in ("style", "script", "link", "meta"): return None
    if n.tag == "svg": return Node("svg", {"data-role": "icon", "aria-hidden": "true"})
    classes = n.attrs.get("class", "").split()
    attrs = {k: v for k, v in n.attrs.items() if k in KEEP_ATTR and v is not None}
    if attrs.get("href", "").startswith("http"): attrs["href"] = "#"
    roles = [ROLE[c] for c in classes if c in ROLE]
    if "button" in roles and "o" in classes: roles.append("secondary")
    if roles: attrs["data-role"] = " ".join(dict.fromkeys(roles))
    m = Node(n.tag, attrs)
    for k in n.kids:
        if isinstance(k, str): m.kids.append(re.sub(r"\s+", " ", k))
        else:
            c = clean(k)
            if c: c.parent = m; m.kids.append(c)
    # unwrap layout-only wrappers: an attribute-less div/span holding exactly one element and no text
    while m.tag in ("div", "span") and not m.attrs and len(m.kids) == 1 and isinstance(m.kids[0], Node):
        m = m.kids[0]
    if m.tag in ("div", "span") and not m.attrs and not m.kids: return None  # empty decorative box
    return m

def ser(n, depth=0):
    pad = "  " * depth
    if isinstance(n, str): return pad + html.escape(n.strip(), quote=False)
    a = "".join(f' {k}' if v == "" else f' {k}="{html.escape(v)}"' for k, v in n.attrs.items())
    if n.tag in VOID: return f"{pad}<{n.tag}{a}>"
    if not n.kids: return f"{pad}<{n.tag}{a}></{n.tag}>"
    inline = all(isinstance(k, str) or (k.tag in ("svg", "b", "i", "em", "strong", "br", "span", "a") and not any(isinstance(x, Node) for x in k.kids)) for k in n.kids)
    if inline:
        inner = "".join(html.escape(k, quote=False) if isinstance(k, str) else ser(k).strip() for k in n.kids).strip()
        return f"{pad}<{n.tag}{a}>{inner}</{n.tag}>"
    return f"{pad}<{n.tag}{a}>\n" + "\n".join(ser(k, depth + 1) for k in n.kids) + f"\n{pad}</{n.tag}>"

slots = {}
for line in (KIT / "rules" / "blocks-and-plan.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) >= 4 and re.fullmatch(r"(LP|G\d|M\d{2})(-[A-C])?", cells[0]):
        slots[cells[0]] = (cells[1], cells[-1])

OUT.mkdir(exist_ok=True)
for f in sorted(SRC.glob("*.html")):
    bid = re.match(r"(LP|G\d|M\d{2}|D\d)", f.stem).group(1)
    if bid in SKIP: continue
    var = re.search(r"-([A-C])$", f.stem)
    key = f"{bid}-{var.group(1)}" if var else bid
    t = Tree(); t.feed(f.read_text(encoding="utf-8"))
    frame = find(t.root, lambda n: n.tag == "section" and "v-desktop" in n.attrs.get("class", "")) \
        or find(t.root, lambda n: n.tag == "section" and "doc-frame" in n.attrs.get("class", ""))
    head = find(t.root, lambda n: n.tag == "header" and "doc-head" in n.attrs.get("class", ""))
    desc = ""
    if head:
        p = find(head, lambda n: n.tag == "p")
        desc = " ".join(k for k in (p.kids if p else []) if isinstance(k, str)).strip()
    stage = frame.kids[0] if frame and frame.kids and isinstance(frame.kids[0], Node) else frame
    body = [c for c in (clean(k) for k in stage.kids if isinstance(k, Node)) if c]
    tag = "header" if bid == "G1" else "footer" if bid == "G3" else "section"
    name, slot = slots.get(key, slots.get(bid, ("", "")))
    comment = f"<!-- {key}: {name or f.stem}" + (f" · {desc}" if desc and desc != name else "") + \
              (f"\n     Slots: {slot}" if slot else "") + \
              "\n     Structure and slots only: restyle from the page's tokens (rules/design-build.md 5.7). Visual reference: blocks/" + f.name + " -->"
    sec = Node(tag, {"data-block": key}); sec.kids = body
    text = comment + "\n" + ser(sec) + "\n"
    (OUT / f.name).write_text(text, encoding="utf-8")
    print(f"{len(text.encode()):6d}  {f.name}")
