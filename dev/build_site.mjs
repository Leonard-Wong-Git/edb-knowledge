#!/usr/bin/env node
/*
 * build_site.mjs — build the GitHub Pages artifact (S257).
 *
 * WHY: app.html ships its React code as an inline <script type="text/babel"> block and loads
 * the 2.85 MB Babel compiler plus the full 2.93 MB Tailwind 2.2.19 stylesheet, all render-
 * blocking. Cloudflare measured mobile LCP P90 at 19 s, 98 % of it Element Render Delay.
 *
 * WHAT IT DOES: copies every git-tracked file into --out unchanged, except app.html, which is
 * rewritten in the OUTPUT ONLY:
 *   · the text/babel block is compiled by esbuild into app.js (loaded with defer);
 *   · the Babel <script> is removed; React / ReactDOM get `defer`;
 *   · the Tailwind CDN <link> becomes app.css: the same pinned file, reduced to the rules whose
 *     classes actually occur in app.html / mobile.js / feedback.js / move-notice.js.
 *
 * WHAT IT DOES NOT DO: it never edits the repository. app.html in git stays the source of
 * truth with its inline JSX, so build_guidelines.py, check_registry_drift.py,
 * check_downstream_sync.py, qc_report.py and execute_ingest.py (display-sync) keep reading and
 * writing it exactly as before, and opening app.html locally still works through Babel.
 *
 * Usage:
 *   node dev/build_site.mjs --out <dir> [--esbuild <path>] [--tailwind-css <file>]
 *   node dev/build_site.mjs --self-test
 * --esbuild defaults to backend/node_modules/.bin/esbuild (version pinned by backend/package-lock.json).
 * --tailwind-css defaults to downloading the pinned cdnjs file; either way its SHA-256 is checked.
 * Writes only inside --out, which must not exist or must be empty.
 */
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TAILWIND_URL = 'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css';
const TAILWIND_SHA256 = 'b6ad97402eddb903e7a5d7a73ee47a679204efbdda4521a391cbad9df509b932';
// Files whose text can name a Tailwind class that ends up in app.html's DOM.
const CLASS_SOURCES = ['app.html', 'mobile.js', 'feedback.js', 'move-notice.js'];

function fail(msg) { console.error('build_site: ERROR — ' + msg); process.exit(1); }
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const short = (buf) => sha256(buf).slice(0, 10);

/* ── Tailwind reduction ─────────────────────────────────────────────────────────── */

function unescapeCss(s) {
  return s.replace(/\\([0-9a-fA-F]{1,6})\s?|\\(.)/g, (m, hex, ch) => (hex ? String.fromCodePoint(parseInt(hex, 16)) : ch));
}
export function classesOf(selector) {
  const out = [];
  const re = /\.((?:\\[0-9a-fA-F]{1,6}\s?|\\.|[A-Za-z0-9_-])+)/g;
  let m;
  while ((m = re.exec(selector))) out.push(unescapeCss(m[1]));
  return out;
}
function splitTopLevel(text, sep) {
  const parts = []; let depth = 0, quote = null, start = 0;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quote) { if (c === '\\') i++; else if (c === quote) quote = null; continue; }
    if (c === '"' || c === "'") quote = c;
    else if (c === '(' || c === '[') depth++;
    else if (c === ')' || c === ']') depth--;
    else if (c === sep && depth === 0) { parts.push(text.slice(start, i)); start = i + 1; }
  }
  parts.push(text.slice(start));
  return parts;
}
// Parse a block of CSS into nodes: {kind:'rule', sel, body} | {kind:'group', prelude, children}
// | {kind:'raw', text}. Handles quotes, nested braces and comments (keeps /*! license */ ones).
export function parseCss(css) {
  const nodes = []; let i = 0;
  while (i < css.length) {
    if (/\s/.test(css[i])) { i++; continue; }
    if (css.startsWith('/*', i)) {
      const end = css.indexOf('*/', i + 2); if (end < 0) fail('unterminated CSS comment');
      if (css[i + 2] === '!') nodes.push({ kind: 'raw', text: css.slice(i, end + 2) });
      i = end + 2; continue;
    }
    let j = i, quote = null, paren = 0;
    for (; j < css.length; j++) {
      const c = css[j];
      if (quote) { if (c === '\\') j++; else if (c === quote) quote = null; continue; }
      if (c === '"' || c === "'") quote = c;
      else if (c === '(') paren++;
      else if (c === ')') paren--;
      else if (paren === 0 && (c === '{' || c === ';')) break;
    }
    if (j >= css.length) fail('unexpected end of CSS');
    const prelude = css.slice(i, j).trim();
    if (css[j] === ';') { nodes.push({ kind: 'raw', text: prelude + ';' }); i = j + 1; continue; }
    let k = j + 1, depth = 1; quote = null;
    for (; k < css.length && depth; k++) {
      const c = css[k];
      if (quote) { if (c === '\\') k++; else if (c === quote) quote = null; continue; }
      if (c === '"' || c === "'") quote = c;
      else if (c === '{') depth++;
      else if (c === '}') depth--;
    }
    if (depth) fail('unbalanced braces in CSS');
    const inner = css.slice(j + 1, k - 1);
    if (/^@(media|supports)\b/i.test(prelude)) nodes.push({ kind: 'group', prelude, children: parseCss(inner) });
    else if (prelude.startsWith('@')) nodes.push({ kind: 'raw', text: `${prelude}{${inner}}` });
    else nodes.push({ kind: 'rule', sel: prelude, body: inner });
    i = k;
  }
  return nodes;
}
export function purgeCss(css, used) {
  const walk = (nodes) => nodes.map((n) => {
    if (n.kind === 'raw') return n.text;
    if (n.kind === 'group') { const inner = walk(n.children); return inner ? `${n.prelude}{${inner}}` : ''; }
    const keep = splitTopLevel(n.sel, ',').filter((s) => classesOf(s).every((c) => used.has(c)));
    return keep.length ? `${keep.join(',')}{${n.body}}` : '';
  }).join('');
  return walk(parseCss(css));
}
export function usedTokens(texts) {
  const set = new Set();
  for (const t of texts) for (const m of t.match(/[A-Za-z0-9_\-:/.%]+/g) || []) set.add(m);
  return set;
}

/* ── app.html rewrite ───────────────────────────────────────────────────────────── */

function replaceOnce(text, pattern, replacement, label) {
  const hits = text.match(new RegExp(pattern.source, pattern.flags.includes('g') ? pattern.flags : pattern.flags + 'g'));
  if (!hits || hits.length !== 1) fail(`expected exactly one ${label} in app.html, found ${hits ? hits.length : 0}`);
  return text.replace(pattern, replacement);
}
export function extractBabel(html) {
  const open = '<script type="text/babel">';
  const a = html.indexOf(open);
  if (a < 0 || html.indexOf(open, a + 1) >= 0) fail('expected exactly one <script type="text/babel"> block in app.html');
  const b = html.indexOf('</script>', a);
  if (b < 0) fail('text/babel block is not closed');
  return { before: html.slice(0, a), jsx: html.slice(a + open.length, b), after: html.slice(b + '</script>'.length) };
}
export function rewriteHtml(html, jsHash, cssHash) {
  const { before, after } = extractBabel(html);
  let out = before + `<script src="app.js?v=${jsHash}" defer></script>` + after;
  out = replaceOnce(out, /<script src="https:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/babel-standalone\/[^"]+"><\/script>\n?/, '', 'Babel <script>');
  out = replaceOnce(out, /<link href="https:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/tailwindcss\/2\.2\.19\/tailwind\.min\.css" rel="stylesheet">/,
    `<link href="app.css?v=${cssHash}" rel="stylesheet">`, 'Tailwind <link>');
  out = replaceOnce(out, /<script src="(https:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/react\/[^"]+)"><\/script>/, '<script src="$1" defer></script>', 'React <script>');
  out = replaceOnce(out, /<script src="(https:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/react-dom\/[^"]+)"><\/script>/, '<script src="$1" defer></script>', 'ReactDOM <script>');
  if (out.includes('text/babel') || out.includes('babel-standalone')) fail('Babel is still referenced after the rewrite');
  return out.replace('<head>', '<head>\n<!-- Built by dev/build_site.mjs from app.html: JSX precompiled to app.js, Tailwind reduced to app.css. Edit app.html, not this file. -->');
}

/* ── main ───────────────────────────────────────────────────────────────────────── */

function selfTest() {
  let ok = true;
  const check = (name, cond) => { console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`); ok = ok && cond; };
  check('escaped classes are unescaped', JSON.stringify(classesOf('.md\\:w-1\\/2:hover .py-1\\.5,.\\32xl\\:p-4')) === JSON.stringify(['md:w-1/2', 'py-1.5', '2xl:p-4']));
  const css = '/*! keep */*,::before{box-sizing:border-box}.a{x:1}.b,.a:hover{y:2}@media (min-width:1px){.c{z:3}.a{w:4}}@keyframes s{to{opacity:0}}.q[data-x="}{"]{v:5}';
  const got = purgeCss(css, new Set(['a']));
  check('purge keeps element rules, used classes, keyframes and licence', got === '/*! keep */*,::before{box-sizing:border-box}.a{x:1}.a:hover{y:2}@media (min-width:1px){.a{w:4}}@keyframes s{to{opacity:0}}');
  check('tokens include variants and fractions', ['md:flex', 'w-1/2', 'py-1.5'].every((t) => usedTokens(['class="md:flex w-1/2 py-1.5"']).has(t)));
  const html = '<head>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js"></script>\n<link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">\n</head><body><script type="text/babel">const a = <b/>;</script></body>';
  const r = rewriteHtml(html, 'J', 'C');
  check('rewrite removes Babel, defers React, swaps CSS and JSX block',
    !r.includes('babel') && r.includes('react.production.min.js" defer') && r.includes('react-dom.production.min.js" defer')
    && r.includes('href="app.css?v=C"') && r.includes('<script src="app.js?v=J" defer></script>'));
  process.exit(ok ? 0 : 1);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--self-test')) return selfTest();
  const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
  const outDir = opt('--out');
  if (!outDir) fail('--out <dir> is required');
  const out = path.resolve(outDir);
  if (out === REPO || out.startsWith(REPO + path.sep)) fail('--out must be outside the repository');
  if (fs.existsSync(out) && fs.readdirSync(out).length) fail(`--out ${out} is not empty`);
  const esbuild = opt('--esbuild') || path.join(REPO, 'backend', 'node_modules', '.bin', 'esbuild');
  if (!fs.existsSync(esbuild)) fail(`esbuild not found at ${esbuild} (run npm ci in backend/)`);

  // 1. Tailwind source, pinned by hash.
  const twPath = opt('--tailwind-css');
  let tw;
  if (twPath) tw = fs.readFileSync(twPath);
  else {
    const res = await fetch(TAILWIND_URL);
    if (!res.ok) fail(`download ${TAILWIND_URL} → HTTP ${res.status}`);
    tw = Buffer.from(await res.arrayBuffer());
  }
  if (sha256(tw) !== TAILWIND_SHA256) fail('Tailwind CSS SHA-256 does not match the pinned value');

  // 2. Compile the JSX block.
  const appHtml = fs.readFileSync(path.join(REPO, 'app.html'), 'utf8');
  const { jsx } = extractBabel(appHtml);
  const js = execFileSync(esbuild, ['--loader=jsx', '--target=es2018', '--minify', '--charset=utf8', '--legal-comments=none'],
    { input: jsx, maxBuffer: 64 * 1024 * 1024 });

  // 3. Reduce Tailwind to the classes the sources mention.
  const used = usedTokens(CLASS_SOURCES.map((f) => fs.readFileSync(path.join(REPO, f), 'utf8')));
  const css = Buffer.from(purgeCss(tw.toString('utf8'), used), 'utf8');

  // 4. Copy tracked files, then write the three built files.
  const files = execFileSync('git', ['ls-files', '-z'], { cwd: REPO }).toString('utf8').split('\0').filter(Boolean);
  for (const name of ['app.js', 'app.css']) if (files.includes(name)) fail(`${name} is tracked in git; the build would overwrite it`);
  fs.mkdirSync(out, { recursive: true });
  for (const f of files) {
    const src = path.join(REPO, f);
    const st = fs.lstatSync(src, { throwIfNoEntry: false });
    if (!st || !st.isFile()) continue;            // deleted in the working tree, or a symlink
    fs.mkdirSync(path.dirname(path.join(out, f)), { recursive: true });
    fs.copyFileSync(src, path.join(out, f));
  }
  fs.writeFileSync(path.join(out, 'app.js'), js);
  fs.writeFileSync(path.join(out, 'app.css'), css);
  fs.writeFileSync(path.join(out, 'app.html'), rewriteHtml(appHtml, short(js), short(css)));
  execFileSync(process.execPath, ['--check', path.join(out, 'app.js')]);   // syntax check of the bundle

  console.log(`build_site: ${files.length} files → ${out}`);
  console.log(`  app.js  ${(js.length / 1024).toFixed(0)} KB (from ${(Buffer.byteLength(jsx) / 1024).toFixed(0)} KB JSX; Babel 2,783 KB no longer loaded)`);
  console.log(`  app.css ${(css.length / 1024).toFixed(0)} KB (from ${(tw.length / 1024).toFixed(0)} KB Tailwind)`);
}

main().catch((e) => fail(e.stack || String(e)));
