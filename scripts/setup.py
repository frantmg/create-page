#!/usr/bin/env python3
"""Install what the kit's scripts need, quietly, so nobody waits for it later.
Usage: python3 setup.py [--check]

The orchestrator starts this as a background command at the very start of the intake (START-HERE.md 0.6 step 1),
so the installs finish while the user answers the questions. Installs only what is missing:
  Playwright + its Chromium (qa.py, logo.py SVG trim, apply_tweaks.py), materialyoucolor (m3_scheme.py), Pillow (logo.py).
--check only reports. Prints one JSON line: what was present, what was installed, what failed."""
import importlib.util, json, subprocess, sys

check = "--check" in sys.argv
pip = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check"]
need = {"playwright": "playwright", "materialyoucolor": "materialyoucolor", "PIL": "pillow"}
out = {"present": [], "installed": [], "failed": []}
for mod, pkg in need.items():
    if importlib.util.find_spec(mod):
        out["present"].append(pkg); continue
    if check: out["failed"].append(f"{pkg} missing"); continue
    r = subprocess.run(pip + [pkg], capture_output=True, text=True)
    if r.returncode:
        r = subprocess.run(pip + ["--break-system-packages", pkg], capture_output=True, text=True)
    (out["installed"] if r.returncode == 0 else out["failed"]).append(pkg)
if importlib.util.find_spec("playwright") or "playwright" in out["installed"]:
    probe = "from playwright.sync_api import sync_playwright\nwith sync_playwright() as p: p.chromium.launch().close()"
    ok = subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0
    if ok: out["present"].append("chromium")
    elif check: out["failed"].append("chromium missing")
    else:
        r = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True, text=True)
        (out["installed"] if r.returncode == 0 else out["failed"]).append("chromium")
print(json.dumps(out))
