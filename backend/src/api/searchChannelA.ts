/**
 * searchChannelA.ts — Channel A: Semantic search over approved policy facts.
 *
 * Channel A facts are human-reviewed and approved. They live in
 * role_facts.json (repo-root, SSOT) and their OpenAI embeddings are
 * precomputed into backend/data/fact_embeddings.json via
 * `npm run embeddings:build`.
 *
 * At query time we only embed the query once and cosine-match it against
 * the cached vectors. This replaces the previous per-request strategy,
 * which re-embedded every fact on every call and scaled poorly with the
 * knowledge base size (109 → 1,001 facts).
 */

import type { EmbedFn } from "../lib/embeddingClient.js";
import {
  FACT_EMBEDDINGS_PATH,
  readEmbeddingFile,
  type FactEmbeddingEntry,
  type FactEmbeddingFile,
} from "../lib/factEmbeddingStore.js";
import { loadKnowledgeBase } from "../lib/knowledgeRepository.js";
import type { TopicId } from "../types/knowledge.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ChannelAResult {
  id: string;
  text: string;
  topic: TopicId;
  topic_label: string;
  role: string;
  score: number;
  channel: "A";
}

export interface SearchChannelARequest {
  query: string;
  /** Optional topic filter */
  topic?: TopicId;
  /** Optional role filter — also matches facts tagged all_roles */
  role?: string;
  /** Min similarity score 0–1. Default: 0.1 */
  min_score?: number;
}

export interface SearchChannelAResponse {
  query: string;
  channel: "A";
  total: number;
  results: ChannelAResult[];
}

// ---------------------------------------------------------------------------
// Embedding store cache
// ---------------------------------------------------------------------------

interface CachedEntry extends FactEmbeddingEntry {
  topic_label: string;
  vector_norm: number;
}

let cachedStore: {
  built_at: string;
  entries: CachedEntry[];
} | null = null;
let cachedLoadPromise: Promise<void> | null = null;

function norm(a: number[]): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * a[i];
  return Math.sqrt(s);
}

function dot(a: number[], b: number[]): number {
  let s = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) s += a[i] * b[i];
  return s;
}

async function loadStoreOnce(): Promise<void> {
  if (cachedStore) return;
  if (cachedLoadPromise) return cachedLoadPromise;

  cachedLoadPromise = (async () => {
    const file: FactEmbeddingFile | null = await readEmbeddingFile();
    if (!file) {
      throw new Error(
        `Channel A embedding store not found at ${FACT_EMBEDDINGS_PATH}. ` +
          `Run: npm run embeddings:build`
      );
    }

    const kb = await loadKnowledgeBase();
    const topicLabels = new Map<string, string>();
    for (const [topic, data] of Object.entries(kb)) {
      if (topic.startsWith("_") || !data || typeof data !== "object") continue;
      const label = (data as { _label?: string })._label ?? topic;
      topicLabels.set(topic, label);
    }

    const entries: CachedEntry[] = file.entries.map((entry) => ({
      ...entry,
      topic_label: topicLabels.get(entry.topic) ?? entry.topic,
      vector_norm: norm(entry.vector),
    }));

    cachedStore = { built_at: file.built_at, entries };
  })();

  try {
    await cachedLoadPromise;
  } finally {
    cachedLoadPromise = null;
  }
}

/** For tests / manual refresh — forces the next search to reload the store. */
export function resetChannelACache(): void {
  cachedStore = null;
  cachedLoadPromise = null;
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function searchChannelA(
  request: SearchChannelARequest,
  embedFn: EmbedFn
): Promise<SearchChannelAResponse> {
  const { query, topic, role, min_score = 0.1 } = request;

  if (!query?.trim()) {
    throw new Error("query is required");
  }

  await loadStoreOnce();
  if (!cachedStore) {
    throw new Error("Channel A store failed to load");
  }

  const queryVec = await embedFn(query);
  const qNorm = norm(queryVec);
  if (qNorm === 0) {
    return { query, channel: "A", total: 0, results: [] };
  }

  const scored: ChannelAResult[] = [];
  for (const entry of cachedStore.entries) {
    if (topic && entry.topic !== topic) continue;
    if (role && entry.role !== role && entry.role !== "all_roles") continue;

    const denom = qNorm * entry.vector_norm;
    if (denom === 0) continue;
    const score = dot(queryVec, entry.vector) / denom;
    if (score < min_score) continue;

    scored.push({
      id: entry.id,
      text: entry.text,
      topic: entry.topic,
      topic_label: entry.topic_label,
      role: entry.role,
      score: Math.round(score * 10000) / 10000,
      channel: "A",
    });
  }

  scored.sort((a, b) => b.score - a.score);

  return {
    query,
    channel: "A",
    total: scored.length,
    results: scored,
  };
}
