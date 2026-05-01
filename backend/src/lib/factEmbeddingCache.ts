/**
 * factEmbeddingCache.ts — Pre-computed embeddings for Channel A facts
 *
 * Caches the embedding vectors for all ~1,001 approved policy facts at server
 * startup. This eliminates the per-query batch embedding API call in
 * searchChannelA.ts (which was the main latency bottleneck: every search was
 * making TWO OpenAI calls — one for the query, one batch for all 1,001 facts).
 *
 * After warmup, each Channel A search only needs ONE API call (query embed).
 * Memory cost: ~1,001 facts × 1,536 dims × 4 bytes ≈ 6 MB — trivial.
 *
 * Warmup is non-blocking: if a search arrives before the cache is ready,
 * searchChannelA falls back to batch embedding transparently.
 */

import type { BatchEmbedFn, EmbedFn } from "./embeddingClient.js";
import { loadKnowledgeBase } from "./knowledgeRepository.js";
import { TOPIC_IDS } from "../types/knowledge.js";

// ---------------------------------------------------------------------------
// Module-level cache state
// ---------------------------------------------------------------------------

const cache = new Map<string, number[]>();
let warmupDone = false;
let warmupInProgress = false;

// ---------------------------------------------------------------------------
// Initialisation (call once at startup)
// ---------------------------------------------------------------------------

/**
 * Pre-compute embeddings for all Channel A fact texts and store them in the
 * in-memory cache. Safe to call multiple times — subsequent calls are no-ops.
 *
 * Designed to be called without await at server startup so it warms up in the
 * background without delaying the first request.
 */
export async function initFactEmbeddingCache(
  embedFn: EmbedFn & { batch?: BatchEmbedFn }
): Promise<void> {
  if (warmupDone || warmupInProgress) return;
  warmupInProgress = true;

  try {
    const kb = await loadKnowledgeBase();
    const batchFn: BatchEmbedFn =
      embedFn.batch ?? ((texts) => Promise.all(texts.map((t) => embedFn(t))));

    // Collect unique fact texts from every topic and role
    const texts: string[] = [];
    for (const topicId of TOPIC_IDS) {
      const topicData = kb[topicId];
      if (!topicData) continue;

      for (const [roleKey, facts] of Object.entries(topicData)) {
        if (roleKey.startsWith("_") || !Array.isArray(facts)) continue;
        for (const fact of facts as string[]) {
          const trimmed = typeof fact === "string" ? fact.trim() : "";
          if (trimmed && !cache.has(trimmed)) {
            texts.push(trimmed);
          }
        }
      }
    }

    if (texts.length === 0) {
      warmupDone = true;
      return;
    }

    console.log(`[cache] Warming Channel A embedding cache (${texts.length} facts)…`);
    const t0 = Date.now();

    const embeddings = await batchFn(texts);

    for (let i = 0; i < texts.length; i++) {
      cache.set(texts[i], embeddings[i]);
    }

    warmupDone = true;
    const ms = Date.now() - t0;
    console.log(`[cache] Channel A cache ready — ${cache.size} facts in ${ms}ms`);
  } catch (err) {
    // Don't crash the server; searchChannelA will fall back to batch-embed
    console.error("[cache] Channel A cache warmup failed:", err);
    warmupInProgress = false; // allow retry on next request
  }
}

// ---------------------------------------------------------------------------
// Cache lookup
// ---------------------------------------------------------------------------

/**
 * Return cached embeddings for a list of fact texts.
 *
 * Returns `null` if:
 *   - The cache is not yet warm (warmup still in progress), or
 *   - Any text is not present in the cache (e.g. newly added facts)
 *
 * The caller (searchChannelA) should fall back to batch embedding when null.
 */
export function getCachedEmbeddings(texts: string[]): number[][] | null {
  if (!warmupDone) return null;
  const result: number[][] = [];
  for (const text of texts) {
    const vec = cache.get(text);
    if (vec === undefined) return null; // cache miss — fall back
    result.push(vec);
  }
  return result;
}

// ---------------------------------------------------------------------------
// Diagnostics
// ---------------------------------------------------------------------------

export function isCacheWarm(): boolean {
  return warmupDone;
}

export function getCacheSize(): number {
  return cache.size;
}
