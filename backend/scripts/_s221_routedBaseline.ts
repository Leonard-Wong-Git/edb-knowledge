/**
 * _s221_routedBaseline.ts — correctness gate for the S221 match_wiki_chunks_routed change.
 *
 * The change removes `set local enable_bitmapscan = off` from the routed RPC so the
 * source_id btree becomes usable. The claim being tested is that this is a PLAN change
 * only: the same rows must come back with the same scores. This script captures the
 * routed RPC's answer before the DDL and again after it, then diffs the two.
 *
 * Why the RPC response is captured through a fetch wrapper rather than by calling
 * searchWikiRoutedExact directly: SOURCE_SETS is not exported, and going through the
 * real searchChannelB path means the allowlist under test is the one production uses,
 * not a copy that can drift.
 *
 * Determinism: the query vectors are written to disk on the `before` run and reused
 * verbatim on the `after` run. Re-embedding between runs would make any score
 * difference unattributable.
 *
 * Read-only. No DDL, no writes to Supabase, no synthesis (synthesize:false, so no LLM).
 *
 *   npx tsx scripts/_s221_routedBaseline.ts --mode before
 *   npx tsx scripts/_s221_routedBaseline.ts --mode after
 *   npx tsx scripts/_s221_routedBaseline.ts --compare
 */
import fs from 'node:fs';
import path from 'node:path';
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';

const OUT_DIR = path.join('..', 'dev', 'source', 'eval_runs');
const VECTORS = path.join(OUT_DIR, '2026-09-12_s221_vectors.json');
const outFile = (mode: string) => path.join(OUT_DIR, `2026-09-12_s221_routed_${mode}.json`);
const GOLD = path.join('..', 'dev', '_s213_gold_all.json');

// Categories to cover. cpd is the subject; curriculum is the control that already
// plans correctly; the rest are breadth so a plan change elsewhere cannot hide.
const WANTED: Record<string, number> = {
  cpd: 3,
  curriculum: 3,
  finance: 1,
  school_governance: 1,
  kg_admission: 1,
  conduct: 1,
};

type Row = { id: string; score: number };
type Case = {
  id: string;
  query: string;
  category: string | null;
  sourceIds?: string[];
  status?: number | null;
  ms?: number | null;
  rows?: Row[];
  error?: string;
};

function pickCases(): Case[] {
  const gold = JSON.parse(fs.readFileSync(GOLD, 'utf8')) as Array<{ id: string; query: string }>;
  const remaining = { ...WANTED };
  const picked: Case[] = [];
  for (const g of gold) {
    const category = detectQueryCategory(g.query);
    if (!category || !remaining[category]) continue;
    remaining[category] -= 1;
    picked.push({ id: g.id, query: g.query, category });
  }
  return picked;
}

async function run(mode: 'before' | 'after') {
  process.env.SUPABASE_URL ||= 'https://youkcekbrbywuqjxgibe.supabase.co';
  // NOTE: this is the in-process convention flagged in SESSION_HANDOFF Risks 6 — it
  // measures under service_role's 8s ceiling, not anon's 3s. That is deliberate here:
  // this run is a CORRECTNESS baseline and needs the routed RPC to complete rather
  // than time out. Do not read latency from this script as a production figure.
  process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
  process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

  const cases = pickCases();
  const nativeFetch = globalThis.fetch;
  const vectorCache: Record<string, number[]> = fs.existsSync(VECTORS)
    ? JSON.parse(fs.readFileSync(VECTORS, 'utf8'))
    : {};
  let modelCalls = 0;
  let current: Case | null = null;

  globalThis.fetch = async (input: any, init?: any) => {
    const url = new URL(String(input));
    if (url.hostname !== new URL(process.env.SUPABASE_URL!).hostname) {
      throw new Error(`Probe request boundary: ${url.hostname}`);
    }
    const routed = url.pathname.endsWith('/match_wiki_chunks_routed');
    const start = performance.now();
    const response = await nativeFetch(input, { ...init, signal: AbortSignal.timeout(25000) });
    if (routed && current) {
      current.status = response.status;
      current.ms = Math.round(performance.now() - start);
      try {
        current.sourceIds = JSON.parse(String(init?.body ?? '{}')).source_ids;
      } catch {
        current.sourceIds = undefined;
      }
      const data = await response.clone().json();
      current.rows = Array.isArray(data)
        ? data.map((x: any) => ({ id: x.id, score: x.score }))
        : undefined;
    }
    return response;
  };

  async function embed(text: string): Promise<number[]> {
    const hit = vectorCache[text];
    if (hit) return hit;
    if (mode === 'after') {
      // A cache miss after the DDL means the two runs would compare different vectors.
      throw new Error(`No cached vector for: ${text} — re-run --mode before first`);
    }
    modelCalls++;
    const response = await nativeFetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
      signal: AbortSignal.timeout(25000),
    });
    if (!response.ok) throw new Error(`Embedding HTTP ${response.status}`);
    const data = (await response.json()) as any;
    vectorCache[text] = data.data[0].embedding;
    fs.writeFileSync(VECTORS, JSON.stringify(vectorCache));
    return vectorCache[text];
  }

  for (const c of cases) {
    current = c;
    try {
      await searchChannelB({ query: c.query, synthesize: false }, embed);
    } catch (e) {
      c.error = String(e);
    }
    const routedRows = c.rows?.length ?? 0;
    console.log(
      `${(c.category ?? '-').padEnd(18)} ${String(c.status ?? '-').padStart(3)} ` +
        `${String(c.ms ?? '-').padStart(6)}ms  rows=${String(routedRows).padStart(3)}  ${c.query}`
    );
  }
  globalThis.fetch = nativeFetch;

  fs.writeFileSync(
    outFile(mode),
    JSON.stringify({ mode, capturedAt: new Date().toISOString(), modelCalls, cases }, null, 2)
  );
  console.log(`\nwrote ${outFile(mode)} (embedding calls: ${modelCalls})`);
}

function compare() {
  const before = JSON.parse(fs.readFileSync(outFile('before'), 'utf8'));
  const after = JSON.parse(fs.readFileSync(outFile('after'), 'utf8'));
  const byId = new Map<string, Case>(after.cases.map((c: Case) => [c.id, c]));

  // A case whose routed RPC already failed before the change (statement timeout ->
  // HTTP 500 -> empty result -> fallback to the full search) has no correct answer to
  // preserve. It is reported separately: it must not count as a correctness failure
  // when it starts succeeding, and it must not be silently counted as a pass either.
  const identical: string[] = [];
  const improved: string[] = [];
  const failures: string[] = [];

  for (const b of before.cases as Case[]) {
    const a = byId.get(b.id);
    if (!a) {
      failures.push(`${b.id}: missing in after`);
      continue;
    }
    const bOk = b.status === 200;
    const aOk = a.status === 200;
    const bRows = b.rows ?? [];
    const aRows = a.rows ?? [];
    const label = `${b.id.padEnd(38)} ${String(b.ms ?? '-').padStart(6)}ms -> ${String(a.ms ?? '-').padStart(6)}ms`;

    if (!bOk && aOk) {
      improved.push(`${b.id}: HTTP ${b.status} -> 200, ${aRows.length} rows now returned`);
      console.log(`${label}  WAS FAILING -> now 200 (${aRows.length} rows)`);
      continue;
    }
    if (bOk && !aOk) {
      failures.push(`${b.id}: HTTP 200 -> ${a.status} (regression)`);
      console.log(`${label}  REGRESSION (200 -> ${a.status})`);
      continue;
    }
    if (!bOk && !aOk) {
      console.log(`${label}  still failing (HTTP ${a.status})`);
      failures.push(`${b.id}: still HTTP ${a.status} after the change`);
      continue;
    }
    if (bRows.length !== aRows.length) {
      failures.push(`${b.id}: ${bRows.length} rows -> ${aRows.length} rows`);
      console.log(`${label}  DIFFERENT (row count)`);
      continue;
    }
    const rowDiffs = bRows
      .map((r, i) =>
        r.id === aRows[i].id && r.score === aRows[i].score
          ? null
          : `#${i} ${r.id}@${r.score} -> ${aRows[i].id}@${aRows[i].score}`
      )
      .filter(Boolean) as string[];
    if (rowDiffs.length === 0) {
      identical.push(b.id);
      console.log(`${label}  identical (${bRows.length} rows)`);
    } else {
      failures.push(`${b.id}: ${rowDiffs.length} row diff — ${rowDiffs.slice(0, 3).join(' | ')}`);
      console.log(`${label}  DIFFERENT (${rowDiffs.length} rows)`);
    }
  }

  console.log(`\nidentical: ${identical.length}   was-failing-now-ok: ${improved.length}   problems: ${failures.length}`);
  if (improved.length) console.log(`\nIMPROVED (no correct prior answer to preserve):\n  ${improved.join('\n  ')}`);
  if (failures.length) console.log(`\nGATE FAILS — roll back:\n  ${failures.join('\n  ')}`);
  else console.log('\nGATE PASS: every case that previously succeeded returns the same rows with the same scores.');
  process.exitCode = failures.length ? 1 : 0;
}

const arg = process.argv.slice(2);
if (arg.includes('--compare')) compare();
else {
  const mode = arg[arg.indexOf('--mode') + 1];
  if (mode !== 'before' && mode !== 'after') {
    console.error('usage: --mode before | --mode after | --compare');
    process.exitCode = 2;
  } else {
    await run(mode);
  }
}
