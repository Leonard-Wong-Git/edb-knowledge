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
  | "guideline";

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
const SOURCE_ALIASES: Record<string, string> = {
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

export function invalidateWikiCache(): void {
  // No-op: no local cache in Supabase mode
}
