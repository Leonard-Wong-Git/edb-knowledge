import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import type { EmbedFn } from "./embeddingClient.js";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));

// Resolve wiki_index.json relative to repo root
// CURRENT_DIR = backend/src/lib/ → ../../../ = repo root
const DEFAULT_WIKI_INDEX_PATH = path.resolve(
  CURRENT_DIR,
  "../../../dev/knowledge/wiki_index.json"
);

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
  embedding?: number[];
}

export interface WikiIndex {
  _meta: {
    built_at?: string;
    total_chunks?: number;
    embedding_model?: string;
    version?: string;
  };
  chunks: WikiChunk[];
}

export interface WikiSearchResult {
  chunk: Omit<WikiChunk, "embedding">;
  score: number;
  channel: "B";
}

// ---------------------------------------------------------------------------
// Math helpers (no external dependencies)
// ---------------------------------------------------------------------------

function dot(a: number[], b: number[]): number {
  let sum = 0;
  for (let i = 0; i < a.length; i++) sum += a[i] * b[i];
  return sum;
}

function norm(a: number[]): number {
  return Math.sqrt(dot(a, a));
}

function cosineSimilarity(a: number[], b: number[]): number {
  const n = norm(a) * norm(b);
  return n > 0 ? dot(a, b) / n : 0;
}

// ---------------------------------------------------------------------------
// Index loading (cached in process memory after first load)
// ---------------------------------------------------------------------------

let _cachedIndex: WikiIndex | null = null;
let _cachedPath: string | null = null;

export async function loadWikiIndex(
  indexPath: string = DEFAULT_WIKI_INDEX_PATH
): Promise<WikiIndex> {
  if (_cachedIndex && _cachedPath === indexPath) {
    return _cachedIndex;
  }

  let raw: string;
  try {
    raw = await readFile(indexPath, "utf-8");
  } catch (err) {
    throw new Error(
      `wiki_index.json not found at ${indexPath}. ` +
        "Run: python3 dev/vault/build_wiki_index.py"
    );
  }

  _cachedIndex = JSON.parse(raw) as WikiIndex;
  _cachedPath = indexPath;

  const total = _cachedIndex.chunks.length;
  const withEmb = _cachedIndex.chunks.filter((c) => c.embedding?.length).length;
  console.log(
    `[wikiRepository] Loaded wiki_index.json: ${withEmb}/${total} chunks with embeddings`
  );

  return _cachedIndex;
}

/** Invalidate cache (e.g. after an index rebuild). */
export function invalidateWikiCache(): void {
  _cachedIndex = null;
  _cachedPath = null;
}

// ---------------------------------------------------------------------------
// Semantic search
// ---------------------------------------------------------------------------

export interface WikiSearchOptions {
  /** Maximum number of results to return. Default: unlimited (return ALL). */
  topK?: number;
  /** Minimum cosine similarity threshold (0–1). Default: 0.1 */
  minScore?: number;
  /** Filter by topic */
  topic?: string;
  /** Filter by content_type */
  contentType?: WikiContentType;
}

/**
 * Search the wiki index using cosine similarity.
 * Channel B design: returns ALL results above minScore unless topK is specified.
 * Results are sorted by descending similarity score.
 */
export async function searchWiki(
  query: string,
  embedFn: EmbedFn,
  options: WikiSearchOptions = {}
): Promise<WikiSearchResult[]> {
  const { topK, minScore = 0.1, topic, contentType } = options;

  const index = await loadWikiIndex();
  const queryVec = await embedFn(query);

  // Score all chunks
  const scored: Array<{ score: number; chunk: WikiChunk }> = [];
  const seenPrefixes = new Set<string>();

  for (const chunk of index.chunks) {
    if (!chunk.embedding?.length) continue;

    // Optional filters
    if (topic && chunk.topic !== topic) continue;
    if (contentType && chunk.content_type !== contentType) continue;

    const score = cosineSimilarity(queryVec, chunk.embedding);
    if (score < minScore) continue;

    // Deduplicate near-identical chunks (first 80 chars as key)
    const prefix = chunk.text.slice(0, 80);
    if (seenPrefixes.has(prefix)) continue;
    seenPrefixes.add(prefix);

    scored.push({ score, chunk });
  }

  // Sort by descending score
  scored.sort((a, b) => b.score - a.score);

  // Apply topK limit only if explicitly set
  const results = topK !== undefined ? scored.slice(0, topK) : scored;

  return results.map(({ score, chunk }) => {
    // Omit the large embedding vector from the response
    const { embedding: _emb, ...chunkWithoutEmbedding } = chunk;
    return {
      chunk: chunkWithoutEmbedding,
      score: Math.round(score * 10000) / 10000,
      channel: "B" as const,
    };
  });
}
