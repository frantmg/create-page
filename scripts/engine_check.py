#!/usr/bin/env python3
"""Check the whole engine: every block in every theme, assembled and run through qa.py.
Usage: python3 engine_check.py [--out /tmp/engine-check] [--fast]

For each theme in engine/themes/, builds one landing page with every engine block (twice for blocks with
versions, so the swap works both ways), placeholder content and a test seed, then runs qa.py (all five widths,
or 390 and 1440 with --fast). Prints one line per theme and a JSON summary; exits 1 when any check fails.
Run it after adding or changing a block or a theme (rules/design-build.md 5.11). Needs Playwright."""
import argparse, json, pathlib, subprocess, sys

KIT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/tmp/engine-check"); ap.add_argument("--fast", action="store_true")
a = ap.parse_args()
blocks = sorted(p.stem for p in (KIT / "engine" / "blocks").glob("*.html") if p.stem not in ("LP", "LP-footer"))
heroes = [b for b in blocks if b.startswith("M01")]
rest = [b for b in blocks if not b.startswith("M01") and b != "M29"]
summary, bad = {}, False
for theme_file in sorted((KIT / "engine" / "themes").glob("*.css")):
    theme = theme_file.stem
    for i, hero in enumerate(heroes):
        work = pathlib.Path(a.out) / f"{theme}-{hero}"; (work / "content").mkdir(parents=True, exist_ok=True)
        order = [hero] + rest[i::1] + ["M29"]
        (work / "content" / "plan.md").write_text("1. LP\n" + "".join(f"{n + 2}. {b}\n" for n, b in enumerate(order)))
        (work / "build.json").write_text(json.dumps({"practice": "Test Practice Physical Therapy", "theme": theme, "seed": ["#2E6B4F", "#1E5A8C"][i % 2]}))
        r = subprocess.run([sys.executable, str(KIT / "scripts" / "assemble.py"), str(work / "build.json")], capture_output=True, text=True)
        if r.returncode: summary[f"{theme}/{hero}"] = {"assemble_error": r.stderr[-400:]}; bad = True; continue
        q = subprocess.run([sys.executable, str(KIT / "scripts" / "qa.py"), str(work / "index.html")] + (["--fast"] if a.fast else []), capture_output=True, text=True)
        try: d = json.loads(q.stdout)
        except json.JSONDecodeError: summary[f"{theme}/{hero}"] = {"qa_error": q.stderr[-400:]}; bad = True; continue
        issues = {}
        axe = d.get("axe_violations")
        if isinstance(axe, list) and axe: issues["axe"] = [(v["id"], v["impact"], v.get("target")) for v in axe]
        for w in [k for k in d if k.startswith("w") and k[1:].isdigit()]:
            x = {k: v for k, v in d[w].items() if v}
            if x: issues[w] = x
        for w, v in d.get("alignment", {}).items():
            if w == "row_tops_w1440":
                if v: issues["row_tops"] = v
            else:
                x = {k: v[k] for k in ("near_misses", "overlaps", "wide_rows") if v.get(k)}
                if x: issues[f"align_{w}"] = x
        logo = [d["logo"][w][s]["pass"] for w in d.get("logo", {}) for s in ("header", "footer")]
        if logo and not all(logo): issues["logo"] = d["logo"]
        if d.get("style", {}).get("uppercase_buttons_and_nav"): issues["uppercase"] = d["style"]["uppercase_buttons_and_nav"]
        hidden_focus = [x for x in d.get("keyboard_tab_order", []) if not x["visible_focus"]]
        if hidden_focus: issues["focus"] = hidden_focus
        if d.get("tweak_leftovers"): issues["leftovers"] = d["tweak_leftovers"]
        summary[f"{theme}/{hero}"] = issues or "pass"
        bad |= bool(issues)
        print(f"{theme:10} {hero:6} {'PASS' if not issues else 'FAIL ' + ', '.join(issues)}", flush=True)
print(json.dumps(summary, indent=1, default=str))
sys.exit(1 if bad else 0)
