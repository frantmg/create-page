#!/usr/bin/env python3
"""Grade check. Usage: python3 readability.py page.html|content.json [--max 5.9] [--allow "sciatica,chiropractic"]
Flesch-Kincaid grade per <section data-block> (or per block in content.json) and for the page. Flags long sentences and 3+ syllable words."""
import re, sys, html, argparse
from html.parser import HTMLParser
SKIP = {"script", "style", "svg", "noscript", "title"}
BREAK = ("p","h1","h2","h3","h4","h5","li","button","a","label","td","th","summary","figcaption","blockquote","span","div","br","option")
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.block="(page)"; s.chunks={}; s.order=[]; s.skip=0
    def handle_starttag(s, t, a):
        a=dict(a)
        if t in SKIP: s.skip+=1
        if a.get("data-block"):
            s.block=a["data-block"]
            if s.block not in s.chunks: s.order.append(s.block)
        if t in BREAK: s.chunks.setdefault(s.block,[]).append("\n")
    def handle_endtag(s, t):
        if t in SKIP: s.skip=max(0,s.skip-1)
    def handle_data(s, d):
        if not s.skip: s.chunks.setdefault(s.block,[]).append(d)
def syl(w):
    w=w.lower().strip("'")
    if len(w)<=3: return 1
    w=re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$","",w); w=re.sub(r"^y","",w)
    return max(1,len(re.findall(r"[aeiouy]{1,2}",w)))
def sentences(text):
    out=[]
    for line in text.split("\n"):
        line=re.sub(r"\[[^\]]*\]","X",line)
        line=re.sub(r"\(?\d{3}\)?[\s.-]?\d{3}-\d{4}","phone",line).strip()
        if not line: continue
        for s in re.split(r"(?<=[.!?])\s+",line):
            ws=re.findall(r"[A-Za-z][A-Za-z'’-]*",s)
            if ws: out.append((s,ws))
    return out
def grade(sents):
    W=sum(len(w) for _,w in sents); S=len(sents)
    if not W: return None, 0
    Y=sum(syl(x) for _,ws in sents for x in ws)
    return 0.39*(W/S)+11.8*(Y/W)-15.59, W
ap=argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--max",type=float,default=5.9)
ap.add_argument("--allow",default=""); a=ap.parse_args()
allow={x.strip().lower() for x in a.allow.split(",") if x.strip()}
src=open(a.file,encoding="utf-8").read()
def strings(x):
    if isinstance(x,str): return [x]
    if isinstance(x,dict): return [t for v in x.values() for t in strings(v)]
    if isinstance(x,list): return [t for v in x for t in strings(v)]
    return []
if a.file.endswith((".html",".htm")):
    p=P(); p.feed(src)
    names=(["(page)"] if "(page)" in p.chunks else [])+p.order
    blocks=[(b,"".join(p.chunks[b])) for b in names]
elif a.file.endswith(".json"):   # content.json from page-content: grade each block's slots
    import json; d=json.loads(src)
    blocks=[(b.get("id","?"),"\n".join(strings(b.get("slots",{})))) for b in d.get("blocks",[])]
else: blocks=[("(text)",src)]
alls=[]; fail=False
for name,text in blocks:
    s=sentences(html.unescape(text))
    if not s: continue
    alls+=s; g,W=grade(s); bad=g>a.max; fail|=bad
    print(f"[{'FIX' if bad else 'OK '}] {name}: grade {g:.1f} ({W} words)")
    for x,ws in s:
        if len(ws)>15: print(f"      long sentence ({len(ws)} words): {x[:110]}")
    hard=sorted({w for _,ws in s for w in ws if syl(w)>=3 and w.lower() not in allow})
    if hard: print(f"      3+ syllable words: {', '.join(hard[:25])}")
    if "—" in text: print("      contains an em dash")
g,W=grade(alls)
print(f"\nPAGE: grade {g:.1f} over {W} words (target 5.0, max {a.max})")
sys.exit(1 if (fail or g>a.max) else 0)
