/**
 * channelBSync.ts — Q4 Phase 2: Channel B incremental-sync read endpoints (K1-side)
 *
 * Implements the dev/CHANNEL_B_SYNC_SPEC.md v0.4 contract:
 *   GET  /api/channel-b/manifest  — {id, source_id, hash, topic, content_type} manifest
 *                                   (delta cursor = content-hash id set; downstream set-diff)
 *   POST /api/channel-b/chunks    — fetch full WikiChunk[+embedding] by id (≤150/call)
 *
 * Net-new PostgREST table-read paths over `wiki_chunks` using the ANON key
 * (RLS `wiki_chunks_anon_read` SELECT-only is sufficient, S121) — NOT the
 * existing `match_wiki_chunks` vector RPC. These endpoints are gated solely by
 * the X-Sync-Key header (server-to-server) and emit NO CORS headers (spec §6).
 *
 * Additive + reversible: revert this file + the 2 route lines in server.ts to
 * remove. Supabase schema / RPC / grants / upload pipeline / Channel A are
 * never touched here.
 *
 * awaiting test-verification: anon-key SELECT over wiki_chunks incl. `embedding`
 * column is assumed (S121 anon = table-level SELECT); verify live post-deploy.
 */

import { createHash, timingSafeEqual } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";

import { getChannelBSyncKeys, getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";
import { SOURCE_ALIASES } from "../lib/wikiRepository.js";

// ── Contract constants (spec v0.4 §3/§7/§11) ───────────────────────────────────
const CONTRACT_VERSION = "1.0";
const EMBEDDING_MODEL = "text-embedding-3-small";
const EMBEDDING_DIM = 1536;

const MANIFEST_CACHE_TTL_MS = 45_000; // 30–60s window: bounds DB scan cost (spec §3/§6/§8)
const MAX_IDS_PER_FETCH = 150;        // spec §4/§10 — no silent truncation
const SYNC_RATE_LIMIT = 60;           // req/min (spec §6/§11.3)
const SYNC_RATE_WINDOW_MS = 60_000;
const DAILY_CHUNK_BUDGET = 31_800;    // ≈3× corpus (spec §6/§11.3) — soft exfil guard
const PG_PAGE = 1000;                 // PostgREST server max-rows per request (Supabase default)
const MAX_BODY_BYTES = 262_144;       // 256KB cap on POST body (≤150 ids is tiny)
// Safe id shape for the PostgREST in.() filter (defense-in-depth; vault ids are
// [a-z0-9_], this lenient set never false-rejects a legitimate id).
const SAFE_ID_RE = /^[A-Za-z0-9_-]{1,128}$/;

// Full WikiChunk column set returned by the chunks endpoint (spec §4).
const CHUNK_COLS = [
  "id", "hash", "source_id", "title", "url", "topic",
  "content_type", "fact_type", "role", "school_level", "reference_year", "text",
] as const;

// ── Auth: X-Sync-Key (timingSafeEqual, multi-key rotation, fail-closed) ─────────
type KeyVerdict = "ok" | "missing" | "wrong" | "disabled";

function sha256(s: string): Buffer {
  return createHash("sha256").update(s).digest();
}

/**
 * Verify the X-Sync-Key header against comma-separated CHANNEL_B_SYNC_KEY env.
 * Hashes both sides to a fixed 32 bytes so timingSafeEqual never throws on
 * length mismatch and key length is not leaked. Never logs the key/header.
 *   no keys configured → "disabled" (503 fail-closed)
 *   header absent/empty → "missing" (401)
 *   no key matches      → "wrong"   (403)
 */
function verifySyncKey(req: IncomingMessage): KeyVerdict {
  const keys = getChannelBSyncKeys();
  if (keys.length === 0) return "disabled";
  const provided = req.headers["x-sync-key"];
  if (typeof provided !== "string" || provided.length === 0) return "missing";
  const providedHash = sha256(provided);
  let matched = false;
  for (const key of keys) {
    // constant work across all keys (no early break) — minor timing hygiene
    if (timingSafeEqual(providedHash, sha256(key))) matched = true;
  }
  return matched ? "ok" : "wrong";
}

// ── Sync rate limiter (60/min) + daily chunk budget (UTC day) ──────────────────
// In-memory: resets on process restart (Render free-tier). The hard gate is the
// sync key; the budget is a soft exfil guard, not a security boundary (spec §6).
const syncWindow: number[] = [];

function checkSyncRate(now: number): { allowed: boolean; retryAfterSec: number } {
  const cutoff = now - SYNC_RATE_WINDOW_MS;
  while (syncWindow.length > 0 && syncWindow[0] <= cutoff) syncWindow.shift();
  if (syncWindow.length >= SYNC_RATE_LIMIT) {
    const retryAfterSec = Math.ceil((syncWindow[0] + SYNC_RATE_WINDOW_MS - now) / 1000);
    return { allowed: false, retryAfterSec: Math.max(1, retryAfterSec) };
  }
  syncWindow.push(now);
  return { allowed: true, retryAfterSec: 0 };
}

let budgetDay = "";
let budgetUsed = 0;

function utcDay(now: number): string {
  return new Date(now).toISOString().slice(0, 10);
}

function rollBudgetDay(now: number): void {
  const day = utcDay(now);
  if (day !== budgetDay) {
    budgetDay = day;
    budgetUsed = 0;
  }
}

function budgetRemaining(now: number): number {
  rollBudgetDay(now);
  return DAILY_CHUNK_BUDGET - budgetUsed;
}

function secondsToUtcMidnight(now: number): number {
  const d = new Date(now);
  const next = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1, 0, 0, 0, 0);
  return Math.max(1, Math.ceil((next - now) / 1000));
}

// ── Supabase REST (anon key) with own 57014 retry budget (spec §8) ─────────────
function sbHeaders(extra?: Record<string, string>): Record<string, string> {
  const key = getSupabaseAnonKey();
  return { apikey: key, Authorization: `Bearer ${key}`, ...(extra ?? {}) };
}

/**
 * Manifest full-table scan has a worse statement-timeout profile than the
 * single-row RPC, so it gets its own retry budget (spec §8) rather than the
 * RPC's linear-3. Returns the raw Response; caller reads/validates.
 */
async function sbFetch(
  path: string,
  init: RequestInit & { headers?: Record<string, string> } = {},
  attempts = 4,
): Promise<{ status: number; ok: boolean; text: string }> {
  const url = `${getSupabaseUrl()}/rest/v1/${path}`;
  let lastText = "";
  let lastStatus = 0;
  for (let i = 1; i <= attempts; i++) {
    const resp = await fetch(url, { ...init, headers: sbHeaders(init.headers) });
    lastText = await resp.text();
    lastStatus = resp.status;
    if (resp.ok) return { status: resp.status, ok: true, text: lastText };
    const is57014 = resp.status >= 500 && lastText.includes("57014");
    if (!is57014 || i >= attempts) {
      return { status: resp.status, ok: false, text: lastText };
    }
    await new Promise((r) => setTimeout(r, 300 * i)); // 300/600/900ms backoff
  }
  return { status: lastStatus, ok: false, text: lastText };
}

// ── Manifest ────────────────────────────────────────────────────────────────
interface ManifestRow {
  id: string;
  source_id: string;
  hash: string;
  topic: string;
  content_type: string;
}

/**
 * Mirror of the Channel B search stat-hiding rule (searchChannelB.ts:570 — SSOT):
 * a chunk is "statistical" when content_type === "stat_fact" OR source_id starts
 * with "stat_". Manifest excludes these unless include_statistical=true.
 */
function isStatChunk(r: { content_type: string; source_id: string }): boolean {
  return r.content_type === "stat_fact" || r.source_id.startsWith("stat_");
}

// Offset/Range pagination over the live table is NOT isolated from concurrent
// upload mutations: a re-ingest mid-scan can skip/duplicate a row. Acceptable by
// contract — the downstream's two-poll delete-safety (spec §5/§8) absorbs
// transient id-set inconsistency (a spuriously-missing id = pending-add, not delete).
async function scanManifestRows(includeStatistical: boolean): Promise<ManifestRow[]> {
  const rows: ManifestRow[] = [];
  let offset = 0;
  for (;;) {
    const res = await sbFetch(
      "wiki_chunks?select=id,source_id,hash,topic,content_type&order=id.asc",
      { headers: { Range: `${offset}-${offset + PG_PAGE - 1}`, "Range-Unit": "items" } },
    );
    if (!res.ok) {
      throw new Error(`manifest scan failed ${res.status}: ${res.text.slice(0, 200)}`);
    }
    const page = JSON.parse(res.text) as ManifestRow[];
    rows.push(...page);
    if (page.length < PG_PAGE) break;
    offset += PG_PAGE;
  }
  const filtered = includeStatistical ? rows : rows.filter((r) => !isStatChunk(r));
  // Deterministic id-asc ordering (order= already asc; re-sort defensively for hash stability).
  filtered.sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  return filtered;
}

interface ManifestEntry {
  at: number;
  etag: string;
  body: string;
}

// Cache keyed by include_statistical so each variant has its own TTL window.
const manifestCache = new Map<string, ManifestEntry>();
// In-flight scans, so concurrent cache-misses for one key share a single scan.
const manifestInflight = new Map<string, Promise<ManifestEntry>>();

async function buildManifest(includeStatistical: boolean, now: number): Promise<ManifestEntry> {
  const cacheKey = includeStatistical ? "all" : "default";
  const hit = manifestCache.get(cacheKey);
  if (hit && now - hit.at < MANIFEST_CACHE_TTL_MS) return hit;

  // Singleflight: concurrent cache-misses for the same key await one scan instead
  // of each launching an O(N) full-table scan — protects the shared free-tier DB
  // statement budget / live search (spec §8 "scan 必須節流，勿餓死 live search").
  const inflight = manifestInflight.get(cacheKey);
  if (inflight) return inflight;

  const job = (async (): Promise<ManifestEntry> => {
    try {
      const rows = await scanManifestRows(includeStatistical);
      const ids = rows.map((r) => r.id); // already id-asc sorted

      // manifest_hash folds in contract_version + embedding_model + sorted id-set so a
      // model/version change is visible to 304 consumers (spec §3 blocker-2 fix).
      // It must NOT include generated_at or any timestamp, or 304 caching breaks.
      const manifestHash = createHash("sha256")
        .update(CONTRACT_VERSION).update("\n")
        .update(EMBEDDING_MODEL).update("\n")
        .update(ids.join(",")).digest("hex");

      const payload = {
        contract_version: CONTRACT_VERSION,
        embedding_model: EMBEDDING_MODEL,
        embedding_dim: EMBEDDING_DIM,
        generated_at: new Date(now).toISOString(),
        ingest_in_progress: false, // v1: K1 never sets sentinel (spec §3/§11.4)
        count: rows.length,        // post-filter count == chunks.length (excludes stat by default)
        manifest_hash: manifestHash,
        source_aliases: SOURCE_ALIASES,
        chunks: rows.map((r) => ({
          id: r.id,
          source_id: r.source_id,
          hash: r.hash,
          topic: r.topic,
          content_type: r.content_type,
        })),
        next_cursor: null,
      };

      // ETag = content identity (manifest_hash), NOT the full body: `generated_at`
      // changes every refresh, so hashing the body would break 304. manifest_hash is
      // derived from the same rows as the body → ETag/body stay consistent (spec §3).
      // Stable across process restarts (DB-derived, not memory-derived).
      const entry: ManifestEntry = {
        at: now,
        etag: `"${manifestHash}"`,
        body: JSON.stringify(payload),
      };
      manifestCache.set(cacheKey, entry);
      return entry;
    } finally {
      manifestInflight.delete(cacheKey);
    }
  })();
  manifestInflight.set(cacheKey, job);
  return job;
}

// ── chunks-by-id ──────────────────────────────────────────────────────────────
async function fetchChunksByIds(ids: string[], includeEmbedding: boolean): Promise<unknown[]> {
  if (ids.length === 0) return [];
  const cols = includeEmbedding ? [...CHUNK_COLS, "embedding"] : [...CHUNK_COLS];
  // id = vault_<source_id>_<hash> (safe chars); encode each defensively. Commas /
  // parens stay literal as PostgREST in.() syntax. ≤150 ids × ~42 chars ≈ 6KB URL.
  const inList = ids.map((id) => encodeURIComponent(id)).join(",");
  const res = await sbFetch(`wiki_chunks?id=in.(${inList})&select=${cols.join(",")}`);
  if (!res.ok) {
    throw new Error(`chunks fetch failed ${res.status}: ${res.text.slice(0, 200)}`);
  }
  const rows = JSON.parse(res.text) as Array<Record<string, unknown>>;
  // Null-field convention: role/school_level/reference_year ALWAYS present as
  // explicit null (PostgREST omits SQL NULLs from the row object) — spec §4.
  return rows.map((r) => {
    const out: Record<string, unknown> = {
      id: r.id,
      hash: r.hash,
      source_id: r.source_id,
      title: r.title,
      url: r.url,
      topic: r.topic,
      content_type: r.content_type,
      fact_type: r.fact_type,
      role: r.role ?? null,
      school_level: r.school_level ?? null,
      reference_year: r.reference_year ?? null,
      text: r.text,
    };
    if (includeEmbedding) out.embedding = r.embedding ?? null; // pgvector "[...]" string or null
    return out;
  });
}

// ── HTTP helpers ────────────────────────────────────────────────────────────
function sendJson(res: ServerResponse, code: number, obj: unknown): void {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(obj));
}

/** Gate + rate-limit shared by both endpoints. Returns false once a response is sent. */
function gate(req: IncomingMessage, res: ServerResponse, now: number): boolean {
  const verdict = verifySyncKey(req);
  if (verdict === "disabled") { sendJson(res, 503, { error: "sync disabled" }); return false; }
  if (verdict === "missing") { sendJson(res, 401, { error: "missing X-Sync-Key" }); return false; }
  if (verdict === "wrong") { sendJson(res, 403, { error: "invalid X-Sync-Key" }); return false; }
  const rl = checkSyncRate(now);
  if (!rl.allowed) {
    res.setHeader("Retry-After", String(rl.retryAfterSec));
    sendJson(res, 429, { error: "rate limited", retry_after_sec: rl.retryAfterSec });
    return false;
  }
  return true;
}

function readJsonBody(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    req.on("data", (c: Buffer) => {
      const buf = Buffer.isBuffer(c) ? c : Buffer.from(c);
      size += buf.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error("body too large"));
        req.destroy();
        return;
      }
      chunks.push(buf);
    });
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf-8")));
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

// ── Route handlers (NO CORS headers — server-to-server, spec §6) ───────────────

/** GET /api/channel-b/manifest */
export async function handleManifest(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const now = Date.now();
  if (!gate(req, res, now)) return;

  const url = new URL(req.url ?? "/", "http://internal");
  const includeStatistical = url.searchParams.get("include_statistical") === "true";

  try {
    const entry = await buildManifest(includeStatistical, now);
    const inm = req.headers["if-none-match"];
    res.setHeader("ETag", entry.etag);
    if (typeof inm === "string" && inm === entry.etag) {
      res.writeHead(304);
      res.end();
      return;
    }
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(entry.body);
  } catch (error) {
    // Log detail server-side only; never echo upstream/Supabase text to clients.
    console.error("[channel-b/manifest] upstream error:", error);
    sendJson(res, 502, { error: "upstream error" });
  }
}

/** POST /api/channel-b/chunks */
export async function handleChunks(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const now = Date.now();
  if (!gate(req, res, now)) return;

  let body: unknown;
  try {
    body = await readJsonBody(req);
  } catch {
    sendJson(res, 400, { error: "invalid JSON body" });
    return;
  }

  const rawIds = (body as { ids?: unknown } | null)?.ids;
  if (!Array.isArray(rawIds) || !rawIds.every((x) => typeof x === "string")) {
    sendJson(res, 400, { error: "ids must be an array of strings" });
    return;
  }
  if (rawIds.length > MAX_IDS_PER_FETCH) {
    sendJson(res, 400, { error: "too many ids", max_ids: MAX_IDS_PER_FETCH });
    return;
  }
  // Defense-in-depth: reject malformed ids before they reach the in.() filter
  // (encodeURIComponent already neutralises injection; this is a second barrier).
  if (!(rawIds as string[]).every((id) => SAFE_ID_RE.test(id))) {
    sendJson(res, 400, { error: "malformed id" });
    return;
  }
  // Dedupe: PostgREST in.() dedupes anyway; keep budget accounting honest and the
  // URL short (spec §4 does not forbid duplicate ids in a request).
  const ids = [...new Set(rawIds as string[])];
  const includeEmbedding = (body as { include_embedding?: unknown }).include_embedding !== false;

  // Reserve budget synchronously BEFORE the await (single-threaded → atomic between
  // check and reserve, no TOCTOU overspend); refund the unserved remainder after.
  if (budgetRemaining(now) < ids.length) {
    const retryAfterSec = secondsToUtcMidnight(now);
    res.setHeader("Retry-After", String(retryAfterSec));
    sendJson(res, 429, { error: "daily budget exhausted", retry_after_sec: retryAfterSec });
    return;
  }
  budgetUsed += ids.length; // reserve

  try {
    const chunks = await fetchChunksByIds(ids, includeEmbedding);
    budgetUsed -= ids.length - chunks.length; // refund ids not served (missing → pending-add, spec §4)
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({
      contract_version: CONTRACT_VERSION,
      embedding_model: EMBEDDING_MODEL,
      chunks,
    }));
  } catch (error) {
    budgetUsed -= ids.length; // refund full reservation on failure
    console.error("[channel-b/chunks] upstream error:", error);
    sendJson(res, 502, { error: "upstream error" });
  }
}
