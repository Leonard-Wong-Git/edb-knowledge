/**
 * wikiRepository.ts — Channel B: Supabase pgvector semantic search
 *
 * Phase 2: wiki_index.json embeddings are stored in Supabase (wiki_chunks table).
 * Search uses the match_wiki_chunks RPC function (cosine similarity via pgvector).
 *
 * Falls back gracefully if SUPABASE_URL / SUPABASE_ANON_KEY are not set,
 * returning an empty result with a clear error message.
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

import type { EmbedFn } from "./embeddingClient.js";
import { getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";

// ---------------------------------------------------------------------------
// Types (shared with searchChannelB / searchCombined)
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
// Supabase client (singleton)
// ---------------------------------------------------------------------------

let _client: SupabaseClient | null = null;

function getClient(): SupabaseClient {
  if (!_client) {
    _client = createClient(getSupabaseUrl(), getSupabaseAnonKey());
  }
  return _client;
}

// ---------------------------------------------------------------------------
// Search options
// ---------------------------------------------------------------------------

export interface WikiSearchOptions {
  /** Maximum number of results. Default: unlimited (all above threshold). */
  topK?: number;
  /** Minimum cosine similarity 0–1. Default: 0.1 */
  minScore?: number;
  /** Filter by topic */
  topic?: string;
  /** Filter by content_type */
  contentType?: WikiContentType;
}

// ---------------------------------------------------------------------------
// Semantic search via Supabase RPC
// ---------------------------------------------------------------------------

/**
 * Search Channel B using pgvector cosine similarity.
 * Calls the match_wiki_chunks SQL function in Supabase.
 * Returns ALL results above minScore unless topK is specified.
 */
export async function searchWiki(
  query: string,
  embedFn: EmbedFn,
  options: WikiSearchOptions = {}
): Promise<WikiSearchResult[]> {
  const { topK, minScore = 0.1, topic, contentType } = options;

  const supabase = getClient();
  const queryVec = await embedFn(query);

  // pgvector requires the embedding as a string "[x,x,x,...]" when passed via
  // Supabase JS RPC — passing a raw number[] is not recognised by the cast.
  const embeddingStr = `[${queryVec.join(",")}]`;

  // Call the match_wiki_chunks RPC function
  const { data, error } = await supabase.rpc("match_wiki_chunks", {
    query_embedding: embeddingStr,
    match_threshold: minScore,
    match_count: topK ?? null,
  });

  if (error) {
    throw new Error(`Supabase search error: ${error.message}`);
  }

  const rows = (data ?? []) as Array<WikiChunk & { score: number }>;

  // Apply optional post-filters (topic / contentType)
  let filtered = rows;
  if (topic) {
    filtered = filtered.filter((r) => r.topic === topic);
  }
  if (contentType) {
    filtered = filtered.filter((r) => r.content_type === contentType);
  }

  // Deduplicate near-identical chunks (first 80 chars as key)
  const seenPrefixes = new Set<string>();
  const deduped: typeof filtered = [];
  for (const row of filtered) {
    const prefix = row.text.slice(0, 80);
    if (seenPrefixes.has(prefix)) continue;
    seenPrefixes.add(prefix);
    deduped.push(row);
  }

  return deduped.map(({ score, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    score,
    channel: "B" as const,
  }));
}

/** Invalidate client cache (e.g. for testing). */
export function invalidateWikiCache(): void {
  _client = null;
}
