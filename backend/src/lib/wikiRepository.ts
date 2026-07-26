/**
 * wikiRepository.ts — Channel B: Supabase pgvector semantic search
 *
 * Uses direct fetch() to call the match_wiki_chunks RPC function,
 * bypassing supabase-js to avoid vector parameter casting issues.
 */

import type { EmbedFn } from "./embeddingClient.js";
import { getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type WikiContentType =
  | "vault_extract"
  | "approved_fact"
  | "stat_fact"
  | "guideline"
  | "footnote_curated";   // S174: curated 附件細字 footnote facts (route-independent overlay)

export type WikiFactType =
  | "policy"
  | "approved_policy"
  | "statistical"
  | "guideline_reference";

export interface WikiChunk {
  id: string;
  hash: string;
  text: string;
  source_id: string;
  title: string;
  url: string;
  topic: string;
  content_type: WikiContentType;
  fact_type: WikiFactType;
  role?: string;
  school_level?: string;
  reference_year?: string;
}

export interface WikiSearchResult {
  chunk: WikiChunk;
  score: number;
  channel: "B";
}

// ---------------------------------------------------------------------------
// Source aliases — same document, different ingestions get unified for quota
// ---------------------------------------------------------------------------

/**
 * Maps redundant source_id values to their canonical equivalent.
 *
 * Background: 學校行政手冊（2025 年 11 月版）was ingested twice into Supabase:
 *   - sag_2025_11 (Session 76, pdftotext partial extract Ch1/3/6/7, 415 chunks)
 *   - g24         (Session 98, PyMuPDF whole-doc fetch incl. cover/TOC, 300 chunks)
 *
 * Hash overlap is 0% because the chunking strategies differ, but content
 * semantics overlap heavily. Treating them as separate source_ids in the
 * per-source quota gate would let one document occupy double the quota
 * (3 + 3 = 6 slots when cap=3), defeating the diversity goal.
 *
 * The alias map below collapses redundant ingestions to a single canonical
 * source_id for quota counting only — chunks remain stored under their
 * original source_id and are returned unchanged in results.
 */
// Exported so the Channel B sync manifest endpoint (channelBSync.ts) can surface
// the same alias map to downstream for de-dup (spec §1 caveat 2 / §3 source_aliases).
export const SOURCE_ALIASES: Record<string, string> = {
  g24: "sag_2025_11",
};

/**
 * Returns the canonical source_id for quota counting purposes.
 * Falls back to the input id if no alias is registered.
 */
function canonicalSource(id: string): string {
  return SOURCE_ALIASES[id] ?? id;
}

// ---------------------------------------------------------------------------
// Search options
// ---------------------------------------------------------------------------

export interface WikiSearchOptions {
  topK?: number;
  minScore?: number;
  topic?: string;
  contentType?: WikiContentType;
  /** Allowlist of source_id values; if provided, only chunks from these sources are returned */
  sourceIds?: string[];
  /**
   * Max chunks per source_id in final results. Prevents a single dominant
   * source (e.g. SAG with 415 chunks) from monopolizing top results.
   * When > 0, the search over-fetches from Supabase (topK * 5) to ensure
   * enough diverse sources are available for the quota gate.
   * Default: undefined (no per-source limit).
   */
  maxPerSource?: number;
}

// ---------------------------------------------------------------------------
// Semantic search via direct REST fetch
// ---------------------------------------------------------------------------

/**
 * Search Channel B using pgvector cosine similarity.
 * Calls match_wiki_chunks via direct fetch to Supabase REST API.
 */
export async function searchWiki(
  query: string,
  embedFn: EmbedFn,
  options: WikiSearchOptions = {}
): Promise<WikiSearchResult[]> {
  const { topK, minScore = 0.1, topic, contentType, sourceIds, maxPerSource } = options;

  const queryVec = await embedFn(query);

  // pgvector text format: "[x,x,x,...]"
  // Use toFixed(8) to avoid scientific notation (e.g. 1e-7) which pgvector may reject
  const embeddingStr = `[${queryVec.map((v) => v.toFixed(8)).join(",")}]`;

  const supabaseUrl = getSupabaseUrl();
  const supabaseKey = getSupabaseAnonKey();

  // Over-fetch when per-source quota is active so the quota gate has
  // enough diverse sources to choose from (otherwise SAG would still
  // dominate Supabase's initial top-K and leave nothing for smaller sources).
  const overFetchEnabled = !!(maxPerSource && maxPerSource > 0 && topK !== undefined);
  const fetchCount = overFetchEnabled ? (topK as number) * 5 : topK;

  const body: Record<string, unknown> = {
    query_embedding: embeddingStr,
    match_threshold: minScore,
  };
  if (fetchCount !== undefined) {
    body.match_count = fetchCount;
  }

  const rpcUrl = `${supabaseUrl}/rest/v1/rpc/match_wiki_chunks`;

  // Supabase free-tier pgvector (ivfflat probes=8) intermittently returns a
  // 57014 "statement timeout" — most often on the first query after the DB has
  // been idle. It is transient: an immediate retry almost always succeeds
  // (empirically 3/3). Retry it here transparently (the embedding above is
  // reused, not recomputed) so a cold-start blip never surfaces as a failed
  // search to the user. Any non-57014 error fails fast — retrying won't help.
  const MAX_ATTEMPTS = 3;
  let rawText = "";
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const resp = await fetch(rpcUrl, {
      method: "POST",
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    rawText = await resp.text();
    if (resp.ok) break;

    const isStatementTimeout = resp.status >= 500 && rawText.includes("57014");
    if (!isStatementTimeout || attempt >= MAX_ATTEMPTS) {
      throw new Error(`Supabase RPC error ${resp.status}: ${rawText}`);
    }
    // brief linear backoff before retrying the RPC (250ms, 500ms)
    await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
  }

  const rows = JSON.parse(rawText) as Array<WikiChunk & { score: number }>;

  // Post-filters
  let filtered = rows;
  if (topic) filtered = filtered.filter((r) => r.topic === topic);
  if (contentType) filtered = filtered.filter((r) => r.content_type === contentType);
  if (sourceIds && sourceIds.length > 0) {
    const allowSet = new Set(sourceIds);
    filtered = filtered.filter((r) => allowSet.has(r.source_id));
  }

  // Deduplicate by first 80 chars
  const seen = new Set<string>();
  const deduped: typeof filtered = [];
  for (const row of filtered) {
    const key = row.text.slice(0, 80);
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(row);
  }

  // Per-source quota gate (cap = upper bound, never forces low-score chunks in)
  // Walks score-DESC list and skips any chunk from a source that already hit cap.
  // Uses canonicalSource() so redundant ingestions of the same document
  // (e.g. g24 + sag_2025_11) share one quota bucket.
  let finalRows: typeof deduped;
  if (overFetchEnabled) {
    const sourceCounts = new Map<string, number>();
    const gated: typeof deduped = [];
    const cap = maxPerSource as number;
    const limit = topK as number;
    for (const row of deduped) {
      const canonical = canonicalSource(row.source_id);
      const count = sourceCounts.get(canonical) ?? 0;
      if (count >= cap) continue;
      sourceCounts.set(canonical, count + 1);
      gated.push(row);
      if (gated.length >= limit) break;
    }
    finalRows = gated;
  } else {
    finalRows = deduped;
  }

  return finalRows.map(({ score, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    score,
    channel: "B" as const,
  }));
}

// ---------------------------------------------------------------------------
// S174 — curated footnote overlay (route- AND ivfflat-independent)
// ---------------------------------------------------------------------------
// The curated 附件細字 footnote chunks (content_type="footnote_curated") must be
// retrievable regardless of (a) category routing — their source_id may sit outside the
// matched SOURCE_SET — and (b) the match_wiki_chunks ivfflat probes=8 recall, which
// intermittently misses freshly-inserted vectors whose list isn't among the query's 8
// probed lists. Because the set is tiny (~33), fetch them ALL once via a plain REST
// SELECT (no RPC / no ivfflat) and score by EXACT cosine. Guaranteed retrieval.
let _footnoteCache: Array<{ chunk: WikiChunk; embedding: number[] }> | null = null;

function parseVec(v: unknown): number[] {
  if (Array.isArray(v)) return v as number[];
  if (typeof v === "string") return JSON.parse(v) as number[];
  return [];
}

async function loadFootnoteChunks(): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  if (_footnoteCache) return _footnoteCache;
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?content_type=eq.footnote_curated` +
    `&select=id,hash,text,source_id,title,url,topic,content_type,fact_type,role,school_level,reference_year,embedding`;
  const key = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
  if (!resp.ok) throw new Error(`footnote overlay load ${resp.status}`);
  const rows = (await resp.json()) as Array<WikiChunk & { embedding: unknown }>;
  _footnoteCache = rows.map(({ embedding, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    embedding: parseVec(embedding),
  }));
  return _footnoteCache;
}

function cosine(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return na && nb ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
}

/**
 * Exact-cosine search over the curated footnote overlay. Caches the (small) footnote
 * set for the process lifetime — invalidate by restarting the backend after re-ingesting
 * footnotes. Caller should treat this as best-effort (try/catch).
 *
 * `qVec` lets the caller share one raw-query embedding across overlay passes (footnote +
 * spotlight) instead of embedding the same text twice. Omit it and the vector is computed
 * here, exactly as before.
 */
export async function searchFootnotes(
  query: string,
  embedFn: EmbedFn,
  minScore: number,
  topN: number,
  qVec?: number[]
): Promise<WikiSearchResult[]> {
  const fns = await loadFootnoteChunks();
  if (fns.length === 0) return [];
  const vec = qVec ?? (await embedFn(query));
  return fns
    .map((f) => ({ chunk: f.chunk, score: cosine(vec, f.embedding), channel: "B" as const }))
    .filter((r) => r.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

// S193 — spotlight overlay cache, keyed by the requested id-set so a changed
// SPOTLIGHT_SOURCE_IDS list (redeploy) never serves a stale set.
let _spotlightCache: { key: string; rows: Array<{ chunk: WikiChunk; embedding: number[] }> } | null =
  null;

/** Hard ceiling on spotlight chunks pulled into memory — bounds the per-query exact-cosine
 *  cost and the cold-start payload if the id list is ever left to grow unpruned. */
const SPOTLIGHT_CHUNK_CAP = 600;

async function loadSpotlightChunks(
  sourceIds: string[]
): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  const key = [...sourceIds].sort().join(",");
  if (_spotlightCache && _spotlightCache.key === key) return _spotlightCache.rows;
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?source_id=in.(${encodeURIComponent(sourceIds.join(","))})` +
    `&select=id,hash,text,source_id,title,url,topic,content_type,fact_type,role,school_level,reference_year,embedding` +
    `&limit=${SPOTLIGHT_CHUNK_CAP}`;
  const anonKey = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` } });
  if (!resp.ok) throw new Error(`spotlight overlay load ${resp.status}`);
  const rows = (await resp.json()) as Array<WikiChunk & { embedding: unknown }>;
  const parsed = rows.map(({ embedding, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    embedding: parseVec(embedding),
  }));
  _spotlightCache = { key, rows: parsed };
  return parsed;
}

/**
 * S193 — Exact-cosine search restricted to a named set of source_ids.
 *
 * Why this exists: `searchWiki` asks Supabase for the global top-(topK*5) chunks above the
 * threshold and only THEN applies the route's source filter in JS. A freshly ingested source
 * with a handful of chunks therefore competes against all ~16k chunks for an over-fetch slot,
 * and loses — so adding it to a SOURCE_SET (or adding routing keywords) cannot make it
 * reachable. This pass mirrors `searchFootnotes`: load the small set with embeddings once,
 * score exactly, and bypass ANN recall entirely. Best-effort — caller wraps in try/catch.
 */
export async function searchSpotlightSources(
  query: string,
  embedFn: EmbedFn,
  sourceIds: string[],
  minScore: number,
  topN: number,
  qVec?: number[]
): Promise<WikiSearchResult[]> {
  if (sourceIds.length === 0) return [];
  const rows = await loadSpotlightChunks(sourceIds);
  if (rows.length === 0) return [];
  const vec = qVec ?? (await embedFn(query));
  return rows
    .map((r) => ({ chunk: r.chunk, score: cosine(vec, r.embedding), channel: "B" as const }))
    .filter((r) => r.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

export function invalidateWikiCache(): void {
  _footnoteCache = null;
  _spotlightCache = null;
}
