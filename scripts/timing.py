#!/usr/bin/env python3
"""Stage timing for a page build. The orchestrator calls it at the start and end of every stage.
Usage: python3 timing.py <work> start <stage> [--at 2026-11-17T10:02:00] [--note "..."]
       python3 timing.py <work> end <stage> [--at ...] [--note "..."]
       python3 timing.py <work> report

Stages: intake, wireframe, content, design, qa, fixes, tweak, deliver (repeats are numbered: fixes, fixes 2, ...).
"start" on a stage that is already open is ignored, "end" closes the latest open run of that stage.
--at records a time noted earlier (the intake starts before the work folder exists: note `date -Iseconds` then).
Events are kept in <work>/timing.json; <work>/timing.md is rewritten on every call with one row per stage run,
minutes per stage, totals per stage type, the total from first start to last end, and the slowest stage.
"report" prints timing.md for the final summary."""
import argparse, datetime as dt, json, pathlib, sys

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("action", choices=["start", "end", "report"]); ap.add_argument("stage", nargs="?", default="")
ap.add_argument("--at", default=""); ap.add_argument("--note", default="")
a = ap.parse_args()
work = pathlib.Path(a.work).resolve(); work.mkdir(parents=True, exist_ok=True)
log_path, md_path = work / "timing.json", work / "timing.md"
runs = json.loads(log_path.read_text()) if log_path.exists() else []
now = (dt.datetime.fromisoformat(a.at) if a.at else dt.datetime.now()).replace(microsecond=0)
if now.tzinfo: now = now.astimezone().replace(tzinfo=None)
stage = a.stage.strip().lower()

if a.action in ("start", "end") and not stage: sys.exit("Give a stage name, e.g. design")
if a.action == "start":
    if not any(r["stage"] == stage and not r.get("end") for r in runs):
        n = sum(1 for r in runs if r["stage"] == stage) + 1
        runs.append({"stage": stage, "run": n, "start": now.isoformat(), "end": None, "note": a.note})
elif a.action == "end":
    open_runs = [r for r in runs if r["stage"] == stage and not r.get("end")]
    if open_runs:
        open_runs[-1]["end"] = now.isoformat()
        if a.note: open_runs[-1]["note"] = (open_runs[-1].get("note", "") + " " + a.note).strip()
    else:  # end without a start: record a zero-length run so the stage still shows
        runs.append({"stage": stage, "run": sum(1 for r in runs if r["stage"] == stage) + 1, "start": now.isoformat(), "end": now.isoformat(), "note": (a.note + " (no start recorded)").strip()})
log_path.write_text(json.dumps(runs, indent=1))

def mins(r):
    if not r.get("end"): return None
    return (dt.datetime.fromisoformat(r["end"]) - dt.datetime.fromisoformat(r["start"])).total_seconds() / 60
hm = lambda s: dt.datetime.fromisoformat(s).strftime("%H:%M:%S") if s else "running"
rows = ["# Stage timing", "", "| Stage | Start | End | Minutes | Note |", "|---|---|---|---|---|"]
for r in runs:
    m = mins(r); name = r["stage"] + (f" {r['run']}" if r["run"] > 1 else "")
    rows.append(f"| {name} | {hm(r['start'])} | {hm(r['end'])} | {'' if m is None else f'{m:.1f}'} | {r.get('note', '')} |")
tot = {}
for r in runs:
    m = mins(r)
    if m is not None: tot[r["stage"]] = tot.get(r["stage"], 0) + m
done = [r for r in runs if r.get("end")]
if done:
    span = (max(dt.datetime.fromisoformat(r["end"]) for r in done) - min(dt.datetime.fromisoformat(r["start"]) for r in runs)).total_seconds() / 60
    rows += ["", "| Totals | Minutes | Share |", "|---|---|---|"]
    busy = sum(tot.values()) or 1
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        rows.append(f"| {k} | {v:.1f} | {100 * v / busy:.0f}% |")
    slow = max(tot, key=tot.get)
    rows += ["", f"Total: {span:.1f} minutes from first start to last end. Slowest stage: {slow} ({tot[slow]:.1f} min)."]
md_path.write_text("\n".join(rows) + "\n")
if a.action == "report": print(md_path.read_text())
else: print(f"{a.action} {stage} {now.strftime('%H:%M:%S')}")
