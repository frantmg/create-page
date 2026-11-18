#!/usr/bin/env python3
"""Quick check of the user's own text edits from the tweak bar, so passing edits go in as written without a content
agent round trip. Usage: python3 check_copy.py <work>/tweaks.json [--content <work>/content/content.json] [--lorem]
                                                [--allow "sciatica,chiropractic"]

For every entry in copy_edits that has no "final" yet, checks the user's text ("after") against rules/copy.md:
  - reading grade 5.9 or lower (Flesch-Kincaid, same formula as readability.py) for texts of 8 words or more,
    sentences of 15 words or fewer, and no word of 4+ syllables in short texts (unless listed with --allow)
  - headlines (h1 to h4) 8 words or fewer, buttons and links 2 to 4 words, short bullets 2 to 6 words
  - no em dashes; no promise words (cure, guarantee, 100%, pain-free, permanent, miracle, risk-free, #1 ...)
  - the main or second call-to-action wording (content.json meta) is not changed in one place only
Passing edits get "final" = the user's words, written back into tweaks.json. Failing edits are listed with their
reasons for page-content, which makes the closest version that passes. --lorem (placeholder pages): all edits pass
as written, but em dashes and promise words are still flagged. Prints JSON: passed, needs_content."""
import argparse, json, pathlib, re

ap = argparse.ArgumentParser(); ap.add_argument("tweaks"); ap.add_argument("--content", default="")
ap.add_argument("--lorem", action="store_true"); ap.add_argument("--allow", default="")
a = ap.parse_args()
tp = pathlib.Path(a.tweaks).resolve(); tw = json.loads(tp.read_text(encoding="utf-8"))
cp = pathlib.Path(a.content) if a.content else tp.parent / "content" / "content.json"
meta = json.loads(cp.read_text(encoding="utf-8")).get("meta", {}) if cp.exists() else {}
ctas = {x.strip().lower() for x in (meta.get("cta_primary"), meta.get("cta_secondary")) if x}
allow = {w.strip().lower() for w in a.allow.split(",") if w.strip()} | {w.lower() for w in re.findall(r"[A-Za-z]+", meta.get("keyword", ""))}

def syl(w):   # same syllable estimate as readability.py
    w = w.lower().strip("'")
    if len(w) <= 3: return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w); w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))
def words(t): return re.findall(r"[A-Za-z][A-Za-z'’-]*", re.sub(r"\[[^\]]*\]", "X", t))
def grade(t):
    sents = [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if words(s)]
    W = sum(len(words(s)) for s in sents); S = len(sents) or 1
    if not W: return 0.0, []
    Y = sum(syl(x) for s in sents for x in words(s))
    return 0.39 * W / S + 11.8 * Y / W - 15.59, [s for s in sents if len(words(s)) > 15]
PROMISE = re.compile(r"\b(cure[sd]?|guarantee[sd]?|pain[- ]free|permanent(ly)?|miracle|risk[- ]free|no risk|instant(ly)? relief)\b|100\s?%|#1\b|number one", re.I)

passed, needs = 0, []
for c in tw.get("copy_edits") or []:
    if c.get("final") is not None: continue
    t, tag, before = str(c.get("after", "")).strip(), str(c.get("element", "")).lower(), str(c.get("before", "")).strip()
    n, why = len(words(t)), []
    if "—" in t: why.append("em dash")
    if PROMISE.search(t): why.append(f"promise word: {PROMISE.search(t).group(0)}")
    if not a.lorem:
        if before.lower() in ctas and t.lower() != before.lower(): why.append("call-to-action wording must stay the same everywhere")
        if tag in ("h1", "h2", "h3", "h4") and n > 8: why.append(f"headline has {n} words (8 or fewer)")
        if tag in ("a", "button") and not 2 <= n <= 4 and len(before.split()) <= 5: why.append(f"button has {n} words (2 to 4)")
        if tag == "li" and len(words(before)) <= 6 and n > 6: why.append(f"bullet has {n} words (2 to 6)")
        if n >= 8:
            g, longs = grade(t)
            if g > 5.9: why.append(f"reading grade {g:.1f} (5.9 or lower)")
            if longs: why.append("a sentence over 15 words")
        else:
            hard = [w for w in words(t) if syl(w) >= 4 and w.lower() not in allow]
            if hard: why.append(f"hard word: {', '.join(hard)}")
    if why: needs.append({"block": c.get("block"), "element": tag, "before": before, "after": t, "reasons": why})
    else: c["final"] = t; passed += 1
tp.write_text(json.dumps(tw, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"passed": passed, "needs_content": needs}, indent=1, ensure_ascii=False))
