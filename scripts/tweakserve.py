#!/usr/bin/env python3
"""Serve the tweak page locally so "Send to Claude" hands the changes straight back (Claude Code).
Usage: python3 tweakserve.py <work> [--once] [--open] [--port 8765] [--timeout 3600]

Serves <work>/tweak.html at http://127.0.0.1:<port>/ (the next free port from --port). The page's "Send to Claude"
and "Looks good, deliver" buttons POST to /__tweaks: the changes are saved to <work>/tweaks.json (an earlier
tweaks.json is kept as tweaks-1.json, tweaks-2.json ...), and the script prints one line:
  RECEIVED apply <path to tweaks.json>      or      RECEIVED approve
--once exits right after that line, so an orchestrator running it in the background is woken up by the exit.
--open opens the page in the default browser. --timeout ends with "TIMEOUT" when nothing arrives in time.
The page is re-read on every request, so a rebuilt tweak.html shows on refresh. Only 127.0.0.1 is served."""
import argparse, http.server, json, pathlib, socketserver, sys, threading, webbrowser

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("--once", action="store_true"); ap.add_argument("--open", action="store_true")
ap.add_argument("--port", type=int, default=8765); ap.add_argument("--timeout", type=int, default=3600)
a = ap.parse_args()
work = pathlib.Path(a.work).resolve(); page = work / "tweak.html"
if not page.exists(): sys.exit(f"Not found: {page} (run tweakbar.py first)")
done = threading.Event()

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/tweak.html"): self._send(200, page.read_bytes(), "text/html; charset=utf-8")
        else: self._send(404, b"not found")
    def do_POST(self):
        if self.path != "/__tweaks": return self._send(404, b"not found")
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, b"bad json")
        action = data.get("action", "apply")
        if action == "approve":
            print("RECEIVED approve", flush=True)
        else:
            out = work / "tweaks.json"
            if out.exists():
                n = 1
                while (work / f"tweaks-{n}.json").exists(): n += 1
                out.rename(work / f"tweaks-{n}.json")
            out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"RECEIVED apply {out}", flush=True)
        self._send(200, b"ok")
        if a.once: done.set()

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True; allow_reuse_address = True

srv = None
for port in range(a.port, a.port + 50):
    try: srv = Server(("127.0.0.1", port), Handler); break
    except OSError: continue
if not srv: sys.exit("No free port")
url = f"http://127.0.0.1:{srv.server_address[1]}/"
(work / "tweak-url.txt").write_text(url + "\n")
print(f"SERVING {url}", flush=True)
threading.Thread(target=srv.serve_forever, daemon=True).start()
if a.open: webbrowser.open(url)
if not done.wait(a.timeout if a.once else None) and a.once:
    print("TIMEOUT", flush=True)
srv.shutdown()
