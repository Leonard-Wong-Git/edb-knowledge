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

  const resp = await fetch(rpcUrl, {
    method: "POST",
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const rawText = await resp.text();

  if (!resp.ok) {
    throw new Error(`Supabase RPC error ${resp.status}: ${rawText}`);
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
  let finalRows: typeof deduped;
  if (overFetchEnabled) {
    const sourceCounts = new Map<string, number>();
    const gated: typeof deduped = [];
    const cap = maxPerSource as number;
    const limit = topK as number;
    for (const row of deduped) {
      const count = sourceCounts.get(row.source_id) ?? 0;
      if (count >= cap) continue;
      sourceCounts.set(row.source_id, count + 1);
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
