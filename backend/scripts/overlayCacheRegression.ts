/**
 * overlayCacheRegression.ts (S249) — offline. The footnote overlay must (1) not refetch
 * inside the TTL, (2) serve the copy it holds while a stale refresh runs, (3) pick up the
 * new rows once that refresh lands, and (4) keep the old rows when a refresh fails.
 * No network: global fetch and Date.now are replaced.
 *
 *   npx tsx scripts/overlayCacheRegression.ts
 */
process.env.SUPABASE_URL = "https://example.invalid";
process.env.SUPABASE_ANON_KEY = "test";
process.env.OVERLAY_CACHE_TTL_MINUTES = "30";

let now = 1_000_000_000_000;
Date.now = () => now;

let calls = 0;
let mode: "v1" | "v2" | "fail" = "v1";
const row = (text: string) => ({
  id: "footnote_fn_x", hash: "h", text, source_id: "s", title: "t", url: "u", topic: "general",
  content_type: "footnote_curated", fact_type: "policy", role: null, school_level: null,
  reference_year: null, embedding: "[1,0]",
});
globalThis.fetch = (async () => {
  calls += 1;
  if (mode === "fail") return new Response("boom", { status: 500 });
  return new Response(JSON.stringify([row(mode === "v1" ? "old $670,238" : "new $670,236")]), { status: 200 });
}) as typeof fetch;

let failures = 0;
function check(name: string, ok: boolean): void {
  console.log(`  [${ok ? "PASS" : "FAIL"}] ${name}`);
  if (!ok) failures += 1;
}
const settle = () => new Promise((r) => setTimeout(r, 20));

const { _loadFootnoteChunksForTest: load, overlayCacheStatus } = await import("../src/lib/wikiRepository.js");
const origWarn = console.warn;
console.warn = () => undefined;

let rows = await load();
check("cold load fetches once", calls === 1 && rows[0].chunk.text.includes("670,238"));
rows = await load();
check("inside the TTL nothing is refetched", calls === 1);

mode = "v2";
now += 31 * 60_000;
rows = await load();
check("a stale read is answered from the held copy (no waiting)", rows[0].chunk.text.includes("670,238"));
await settle();
check("…and triggers exactly one background refresh", calls === 2);
rows = await load();
check("the next read sees the corrected row", rows[0].chunk.text.includes("670,236") && calls === 2);
check("/health reports when the footnotes were last read",
  overlayCacheStatus().footnote_loaded_at === new Date(now).toISOString());
const lastGoodRead = new Date(now).toISOString();

mode = "fail";
now += 31 * 60_000;
rows = await load();
await settle();
check("a failed refresh keeps the old rows", (await load())[0].chunk.text.includes("670,236"));
// S252 — /health used to show a made-up time here: the retry delay was implemented by
// overwriting the same stamp /health reports, so a failed refresh displayed "loaded 25
// minutes ago" although nothing had been loaded then.
check("a failed refresh does not change the reported last-read time",
  overlayCacheStatus().footnote_loaded_at === lastGoodRead);
check("…and /health says when the refresh failed",
  overlayCacheStatus().footnote_refresh_failed_at === new Date(now).toISOString());
const afterFail = calls;
await load();
check("…and is not retried on every request", calls === afterFail);
now += 6 * 60_000;
mode = "v1";
await load();
await settle();
check("…but is retried after the retry delay", calls === afterFail + 1);
check("a successful retry updates the last-read time and clears the failure",
  overlayCacheStatus().footnote_loaded_at === new Date(now).toISOString()
  && overlayCacheStatus().footnote_refresh_failed_at === null);

console.warn = origWarn;
console.log(failures === 0 ? "overlayCacheRegression: ALL PASS" : `overlayCacheRegression: ${failures} FAIL`);
process.exit(failures ? 1 : 0);
