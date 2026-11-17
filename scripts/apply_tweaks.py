#!/usr/bin/env python3
"""Apply the mechanical part of a tweaks.json straight to the page, in seconds, without the designer.
Usage: python3 apply_tweaks.py <work>/tweaks.json [--page <work>/index.html] [--alternates <work>/alternates.html]
                               [--copy-as-written] [--force] [--dry-run]

Applies: colour and other tokens (real values written into the :root token block; a palette made from a seed is
recomputed with m3_scheme.py when it is installed), size, spacing, corner and shadow scales (the token literals are
multiplied, no calc() left behind), page width and button shape, fonts (the Google Fonts link), block order, hidden
blocks (removed with their CSS), block versions from alternates.html (markup and its <style data-variant> CSS; the
replaced block moves into alternates.html so the user can switch back), block backgrounds (band-* classes on the
token pairs), and text edits: an edit's "final" text (set by page-content), or its "after" text with --copy-as-written
(placeholder pages).
Leaves for page-designer (listed under needs_designer): replaced and added library blocks, notes, contrast failures,
block versions without CSS, and text edits with no final text.
Block CSS is moved or removed only when it sits between /* block:ID */ and /* /block:ID */ markers (design-build 5.8).
Refuses when tweaks.json was made on another version of the page (page_hash), unless --force.
Writes index.html and alternates.html in place (copies go to <work>/backups/ first) and prints a JSON report.
Needs Playwright's Chromium (the same as qa.py): the page is edited with the browser's own HTML parser."""
import argparse, datetime as dt, hashlib, json, pathlib, re, shutil, subprocess, sys
from playwright.sync_api import sync_playwright

KIT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("tweaks"); ap.add_argument("--page", default=""); ap.add_argument("--alternates", default="")
ap.add_argument("--copy-as-written", action="store_true"); ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
tw_path = pathlib.Path(a.tweaks).resolve(); work = tw_path.parent
tw = json.loads(tw_path.read_text(encoding="utf-8"))
page = pathlib.Path(a.page).resolve() if a.page else work / "index.html"
alt = pathlib.Path(a.alternates).resolve() if a.alternates else work / "alternates.html"
src = page.read_bytes()
if tw.get("page_hash") and tw["page_hash"] != hashlib.sha1(src).hexdigest()[:12] and not a.force:
    sys.exit(json.dumps({"error": "tweaks.json was made on another version of index.html (page_hash differs). "
                         "Rebuild the tweak page and ask again, or rerun with --force."}))

seed_tokens, warnings = {}, []
seed = ((tw.get("design") or {}).get("palette_seed") or "").strip()
if seed:
    r = subprocess.run([sys.executable, str(KIT / "scripts" / "m3_scheme.py"), seed], capture_output=True, text=True)
    root = re.search(r":root\s*\{([^}]*)\}", r.stdout) if r.returncode == 0 else None
    if root: seed_tokens = dict(re.findall(r"(--md-sys-color-[\w-]+):\s*(#[0-9A-Fa-f]{6})", root.group(1)))
    else: warnings.append(f"m3_scheme.py could not run for {seed}; used the tweak bar's preview colours (pip install --break-system-packages materialyoucolor)")

JS = r"""
({page, alts, tw, seedTokens, copyAsWritten}) => {
  const P = new DOMParser(), doc = P.parseFromString(page, 'text/html');
  const ad = P.parseFromString(alts || '', 'text/html');
  const R = { applied: [], needs_designer: [], cleanup: [], skipped: [] };
  const design = tw.design || {}, blocks = tw.blocks || {};
  const style = [...doc.querySelectorAll('style')].find(s => /:root\s*\{/.test(s.textContent)) || doc.querySelector('style');
  let css = style ? style.textContent : '';
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const round = n => +(+n).toFixed(4);
  const scale = (v, k) => v.replace(/(-?\d*\.?\d+)(rem|px|em|vw|vh|ch|%)/g, (m, n, u) => round(n * k) + u);
  const cutBlockCss = id => {   // remove /* block:ID */ ... /* /block:ID */ and return it
    const re = new RegExp('\\n?[ \\t]*/\\*\\s*block:' + esc(id) + '\\s*\\*/[\\s\\S]*?/\\*\\s*/block:' + esc(id) + '\\s*\\*/[ \\t]*', 'm');
    const m = css.match(re); if (!m) return null; css = css.replace(re, ''); return m[0].trim();
  };

  // 1. Tokens into the first :root block
  const tokens = {};
  for (const [k, v] of Object.entries(design.tokens || {})) tokens[k] = { from: v.from, to: seedTokens[k] || v.to };
  const rootRe = /:root\s*\{([^}]*)\}/;
  const rm = css.match(rootRe);
  if (rm) {
    let block = rm[1];
    for (const [k, { from, to }] of Object.entries(tokens)) {
      const sm = /^calc\((.*) \* ([\d.]+)\)$/.exec(to || '');
      const val = sm && from ? scale(from, +sm[2]) : to;
      if (val == null) continue;
      const re = new RegExp('(' + esc(k) + '\\s*:\\s*)([^;]+)(;)');
      if (re.test(block)) block = block.replace(re, (m, x, y, z) => x + val + z); else block = block.replace(/\s*$/, `\n  ${k}: ${val};\n`);
      R.applied.push(`token ${k}: ${val}`);
    }
    css = css.replace(rootRe, () => ':root {' + block + '}');
  } else if (Object.keys(tokens).length) R.needs_designer.push('No :root token block found; apply design.tokens by hand');

  // 2. Fonts
  if (design.fonts && design.fonts.href) {
    let l = doc.querySelector('link[rel="stylesheet"][href*="fonts.googleapis.com"]');
    if (!l) { l = doc.createElement('link'); l.rel = 'stylesheet'; doc.head.appendChild(l); }
    l.setAttribute('href', design.fonts.href); R.applied.push(`fonts: ${design.fonts.name}`);
  }

  // 3. Blocks, keyed exactly like the tweak bar
  const map = new Map(), n = {}, main = doc.querySelector('main');
  const gs = [...doc.querySelectorAll('header[data-block], footer[data-block]')].filter(e => !e.closest('main'));
  const ms = main ? [...main.children].filter(e => e.hasAttribute('data-block')) : [];
  [...gs, ...ms].forEach(e => { const id = e.getAttribute('data-block'); n[id] = (n[id] || 0) + 1; map.set(n[id] > 1 ? `${id}#${n[id]}` : id, e); });
  const origOrder = ms.map(e => [...map].find(([, x]) => x === e)[0]);
  const byPath = (root, p) => p.reduce((x, i) => x && x.children[i], root);

  // 3a. Versions from alternates.html
  for (const [key, v] of Object.entries(blocks.variants || {})) {
    const e = map.get(key); if (!e) { R.skipped.push(`variant ${key} → ${v}: block not found`); continue; }
    const old = e.getAttribute('data-block');
    const tpl = [...ad.querySelectorAll('template[data-alt-for]')].find(t => t.getAttribute('data-alt-for') === old &&
      (t.getAttribute('data-variant') === v || (t.content.firstElementChild && t.content.firstElementChild.getAttribute('data-block') === v)));
    const vcss = [...ad.querySelectorAll('style[data-variant]')].find(s => s.getAttribute('data-variant') === v);
    if (!tpl || !vcss) { R.needs_designer.push(`Swap ${key} to ${v}: ${!tpl ? 'version not found in alternates.html' : 'its CSS is not in a <style data-variant="' + v + '">'}`); continue; }
    const nu = doc.importNode(tpl.content.firstElementChild, true);
    e.replaceWith(nu); map.set(key, nu);
    css += `\n/* block:${v} */\n${vcss.textContent.trim()}\n/* /block:${v} */\n`;
    tpl.remove(); vcss.remove();
    const oldCss = [...map.values()].some(x => x.getAttribute('data-block') === old) ? null : cutBlockCss(old);
    // keep the replaced block as a version so the user can switch back
    const back = ad.createElement('template');
    back.setAttribute('data-alt-for', v); back.setAttribute('data-variant', old); back.setAttribute('data-label', 'As first built');
    back.content.appendChild(ad.importNode(e, true)); (ad.body || ad.documentElement).appendChild(back);
    if (oldCss) { const st = ad.createElement('style'); st.setAttribute('data-variant', old); st.textContent = oldCss.replace(/^\/\*[^*]*\*\/\s*|\s*\/\*[^*]*\*\/$/g, ''); ad.head.appendChild(st); }
    else R.cleanup.push(`${old}: old CSS left in index.html (no block markers); remove it and add it to alternates.html as <style data-variant="${old}">`);
    ad.querySelectorAll(`template[data-alt-for="${CSS.escape(old)}"]`).forEach(t => t.setAttribute('data-alt-for', v));
    R.applied.push(`swap ${key}: ${old} → ${v}`);
  }

  // 3b. Order
  if (blocks.order && main) {
    const marks = origOrder.map(k => { const m = doc.createComment('tw'); map.get(k).before(m); return m; });
    origOrder.forEach(k => map.get(k).remove());
    const order = [...blocks.order.filter(k => origOrder.includes(k)), ...origOrder.filter(k => !blocks.order.includes(k))];
    marks.forEach((m, i) => m.replaceWith(map.get(order[i])));
    R.applied.push(`order: ${order.join(', ')}`);
  }

  // 3c. Backgrounds (band-* classes on the token pairs)
  const BG = { 'Plain': 'band-plain', 'Light tint': 'band-tint-low', 'Tint': 'band-tint', 'Brand colour': 'band-brand', 'Dark': 'band-dark' };
  let usedBg = false;
  for (const [key, label] of Object.entries(blocks.backgrounds || {})) {
    const e = map.get(key), cls = BG[label]; if (!e || !cls) continue;
    [...e.classList].filter(c => /^band-/.test(c)).forEach(c => e.classList.remove(c));
    e.classList.add(cls); usedBg = true; R.applied.push(`background ${key}: ${label}`);
  }
  if (usedBg && !/\/\*\s*block:tweak-bands\s*\*\//.test(css)) css += `
/* block:tweak-bands */
.band-plain { background: var(--md-sys-color-surface); color: var(--md-sys-color-on-surface); }
.band-tint-low { background: var(--md-sys-color-surface-container-low, var(--md-sys-color-surface)); color: var(--md-sys-color-on-surface); }
.band-tint { background: var(--md-sys-color-surface-container, var(--md-sys-color-surface)); color: var(--md-sys-color-on-surface); }
.band-brand { background: var(--md-sys-color-primary-container); color: var(--md-sys-color-on-primary-container); }
.band-dark { background: var(--md-sys-color-inverse-surface); color: var(--md-sys-color-inverse-on-surface); }
:is(.band-brand, .band-dark) :is(h1, h2, h3, h4, p, li, a:not(.btn)) { color: inherit; }
/* /block:tweak-bands */
`;

  // 3d. Text edits
  for (const c of tw.copy_edits || []) {
    const text = c.final != null ? c.final : (copyAsWritten ? c.after : null);
    if (text == null) { R.needs_designer.push(`Text edit in ${c.block} has no final text from page-content: "${c.after}"`); continue; }
    const e = map.get(c.block), cur = (blocks.variants || {})[c.block] || null;
    if (!e || (c.variant || null) !== cur) { R.skipped.push(`text edit in ${c.block}: block or version changed`); continue; }
    const node = byPath(e, c.path || []);
    if (!node || node === e) { R.skipped.push(`text edit in ${c.block}: element not found`); continue; }
    node.textContent = text; R.applied.push(`text ${c.block} ${c.element}: "${text}"`);
  }

  // 3e. Hidden blocks: removed with their CSS
  for (const key of blocks.hidden || []) {
    const e = map.get(key); if (!e) continue;
    const id = e.getAttribute('data-block'); e.remove(); map.delete(key);
    if (![...map.values()].some(x => x.getAttribute('data-block') === id) && !cutBlockCss(id)) R.cleanup.push(`${id}: CSS left in index.html (no block markers)`);
    R.applied.push(`removed ${key}`);
  }

  // 4. For the designer
  for (const [key, r] of Object.entries(blocks.replacements || {})) R.needs_designer.push(`Replace ${key} with ${r.block} (${r.name || ''}) from blocks-lite/, in the page's style`);
  for (const x of blocks.added || []) R.needs_designer.push(`Add ${x.block} (${x.name || ''}) after ${x.after}, from blocks-lite/, in the page's style`);
  for (const [key, t] of Object.entries(blocks.notes || {})) R.needs_designer.push(`Note on ${key}: ${t}`);
  if (tw.note) R.needs_designer.push(`General note: ${tw.note}`);
  for (const f of tw.contrast_failures || []) R.needs_designer.push(`Contrast: ${f.pair} is ${f.ratio}:1, needs ${f.needs}:1 (${f.fg} on ${f.bg})`);

  if (style) style.textContent = css;
  const out = '<!doctype html>\n' + doc.documentElement.outerHTML + '\n';
  const altsOut = (ad.head.innerHTML + '\n' + ad.body.innerHTML).trim() + '\n';
  return { out, altsOut, R };
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    res = pg.evaluate(JS, {"page": src.decode("utf-8"), "alts": alt.read_text(encoding="utf-8") if alt.exists() else "",
                           "tw": tw, "seedTokens": seed_tokens, "copyAsWritten": a.copy_as_written})
    b.close()

report = dict(res["R"]); report["warnings"] = warnings
if not a.dry_run and report["applied"]:
    bk = work / "backups"; bk.mkdir(exist_ok=True); stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(page, bk / f"index-{stamp}.html")
    if alt.exists(): shutil.copy2(alt, bk / f"alternates-{stamp}.html")
    page.write_text(res["out"], encoding="utf-8")
    if alt.exists() or (tw.get("blocks") or {}).get("variants"): alt.write_text(res["altsOut"], encoding="utf-8")
report["written"] = [] if a.dry_run or not report["applied"] else [str(page), str(alt)]
report["next"] = ("Run qa.py (--fast, then the full run with --out). " +
                  ("Send needs_designer and cleanup to page-designer." if report["needs_designer"] or report["cleanup"] else "No designer needed."))
print(json.dumps(report, indent=1, ensure_ascii=False))
