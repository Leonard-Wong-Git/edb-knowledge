#!/usr/bin/env node
// status_page_test.mjs — offline logic test for status-07cc7942c0.html (S234)
//
// The page's front line is one sentence ("系統運作正常" / "系統可能出了問題" …), and
// its whole value is that the sentence can be trusted. The cases below hold it to
// the properties that matter, including the two that would silently rot it:
//   * search-quality debts must NOT colour the banner (else it is red every day
//     and cannot say which day something broke);
//   * "could not read" must never present as "nothing is waiting".
// It also pins the two page-side defences on data that arrives from a public repo.
//
//   node dev/source/status_page_test.mjs
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const html = fs.readFileSync(path.join(root, "status-07cc7942c0.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// A DOM just big enough for the script to load; render targets record what they get.
const els = {};
const el = (id) => (els[id] ??= { id, innerHTML: "", textContent: "", className: "",
  classList: { add() {}, remove() {} }, addEventListener() {} });
const ctx = {
  document: { getElementById: el, querySelectorAll: () => [] },
  fetch: () => new Promise(() => {}),               // never settles: no network, no render
  navigator: {}, window: { isSecureContext: false }, setTimeout: () => {},
  console,
};
vm.createContext(ctx);
vm.runInContext(script + "\n;this.__t = { summarize, safeUrl, renderAttention, renderOps };", ctx);
const { summarize, safeUrl, renderAttention, renderOps } = ctx.__t;

let fails = 0;
const check = (name, cond) => {
  console.log(`  ${cond ? "PASS" : "FAIL"}  ${name}`);
  if (!cond) fails++;
};

const NOW = Date.parse("2026-09-29T12:00:00Z");
const hoursAgo = (h) => new Date(NOW - h * 36e5).toISOString();
const infra = (over = {}) => ["BACKEND_HEALTH", "SEARCH_PIPELINE_LIVE", "FREEZE_CONTRACT",
  "MIRROR_CONSISTENCY"].map((id) => ({ id, group: "infra", status: over[id] || "PASS", detail: "d" }));
const decision = { level: "decision", kind: "new-circular", headline: "有新通告", hint: "h",
  since: hoursAgo(72), url: "https://github.com/Leonard-Wong-Git/edb-knowledge/issues/3", number: 3 };
const alarm = { level: "alarm", kind: "service-down", headline: "線上服務無法使用", hint: "h",
  since: hoursAgo(2), url: "https://github.com/Leonard-Wong-Git/edb-knowledge/issues/40", number: 40 };
const base = (over = {}) => ({ generatedAt: hoursAgo(1), overallStatus: "ERROR",
  checks: infra(), attention: { items: [], ignored_outside: 0 }, ...over });

console.log("summarize");
let r = summarize(base(), NOW);
check("all quiet → 運作正常 (ok)", r.level === "ok" && r.title === "系統運作正常");

r = summarize(base({ attention: { items: [decision, decision] } }), NOW);
check("decisions waiting → still 運作正常, but says how many (info)",
  r.level === "info" && r.title === "系統運作正常" && r.desc.includes("2 項"));

r = summarize(base({ attention: { items: [alarm] } }), NOW);
check("an alarm issue → 系統可能出了問題 (err)", r.level === "err" && r.title === "系統可能出了問題");

r = summarize(base({ checks: infra({ SEARCH_PIPELINE_LIVE: "FAIL" }) }), NOW);
check("an infra check FAIL → err", r.level === "err");

// THE DECOUPLING: a report full of standing quality failures, overall BLOCKER,
// must not touch the banner when the running system is fine.
const noisy = base({
  overallStatus: "BLOCKER",
  checks: infra().concat([
    { id: "EVAL_LATEST", group: "measurable", status: "FAIL" },
    { id: "PAGE_ANCHORED", group: "pointing", status: "FAIL" },
    { id: "REGISTRY_PHANTOM", group: "pointing", status: "FAIL" }]),
});
check("standing search-quality FAILs (overall BLOCKER) do NOT colour the banner",
  summarize(noisy, NOW).level === "ok");

r = summarize(base({ attention: null }), NOW);
check("unreadable issue list → ok, but the page says it could not read it",
  r.level === "ok" && r.desc.includes("未能讀取"));
r = summarize(base({ attention: undefined }), NOW);
check("an old report without the field behaves like unreadable, not like empty",
  r.desc.includes("未能讀取"));

check("40h old → warn", summarize(base({ generatedAt: hoursAgo(40) }), NOW).level === "warn");
r = summarize(base({ generatedAt: hoursAgo(80) }), NOW);
check("80h old → 已過期 (err) even though every check passed — a dead page is not green",
  r.level === "err" && r.title === "本頁資料已經過期");
check("missing generatedAt → 已過期 (err)",
  summarize(base({ generatedAt: undefined }), NOW).title === "本頁資料已經過期");
check("staleness outranks a green check list, but an alarm outranks a mere warn",
  summarize(base({ generatedAt: hoursAgo(40), attention: { items: [alarm] } }), NOW).level === "err");

console.log("\nsafeUrl");
check("an issue link in this repository is followed",
  safeUrl("https://github.com/Leonard-Wong-Git/edb-knowledge/issues/3") !== null);
check("another host is refused", safeUrl("https://evil.example/x") === null);
check("another repository on github.com is refused",
  safeUrl("https://github.com/someone-else/edb-knowledge/issues/1") === null);
check("javascript: is refused", safeUrl("javascript:alert(1)") === null);
check("non-string is refused", safeUrl(undefined) === null && safeUrl(42) === null);

console.log("\nrender defences");
renderAttention(base({ attention: { items: [
  { ...decision, headline: "<img src=x onerror=alert(1)>", hint: "\"><script>bad()</script>" }] } }), NOW);
const out = els.attnList.innerHTML;
check("a hostile headline/hint is escaped, never becomes markup",
  !out.includes("<img") && !out.includes("<script") && out.includes("&lt;img"));

renderAttention(base({ attention: { items: [{ ...decision, url: "https://evil.example/x" }] } }), NOW);
check("a foreign link is not rendered as an anchor", !els.attnList.innerHTML.includes("<a "));

renderAttention(base({ attention: null }), NOW);
check("null list says it could not read — not 'nothing waiting'",
  els.attnList.innerHTML.includes("未能讀取") && !els.attnList.innerHTML.includes("目前沒有"));
renderAttention(base({ attention: { items: [] } }), NOW);
check("empty list says nothing is waiting", els.attnList.innerHTML.includes("目前沒有"));

renderAttention(base({ attention: { items: [decision], ignored_outside: 3 } }), NOW);
check("outsider issues are disclosed as a count, not shown",
  els.attnList.innerHTML.includes("另有 3 則"));

renderOps(base({ attention: { items: [{ ...alarm, kind: "monitor-watchdog" }] } }));
check("a watchdog alarm marks 自動監察 as stopped", els.ops.innerHTML.includes("有監察停了"));
renderOps(base({ attention: null }));
check("unreadable list marks 自動監察 as unread, not as healthy",
  els.ops.innerHTML.includes('<span class="pill p-unk">未能讀取</span>') &&
  !els.ops.innerHTML.includes('<span class="pill p-ok">準時運作</span>'));
renderOps(base());
check("healthy → four 正常 pills and a 準時運作 pill",
  (els.ops.innerHTML.match(/<span class="pill p-ok">正常<\/span>/g) || []).length === 4 &&
  els.ops.innerHTML.includes('<span class="pill p-ok">準時運作</span>'));

console.log(`\n${fails ? `${fails} FAILED` : "ALL PASS"}`);
process.exit(fails ? 1 : 0);
