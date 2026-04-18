/**
 * searchChannelA.ts — Channel A: Semantic search over approved policy facts
 *
 * Channel A facts are human-reviewed and approved. They are stored in
 * role_facts.json and loaded via knowledgeRepository.ts.
 *
 * Search strategy:
 *   1. Embed the user query
 *   2. Score each fact text using cosine similarity against the query embedding
 *   3. Return ALL results above minScore, sorted by descending score
 *
 * Note: Channel A facts are short (< 600 chars each), so we embed them
 * on-the-fly per request. For high traffic, consider pre-embedding and caching.
 */

import type { EmbedFn } from "../lib/embeddingClient.js";
import { loadKnowledgeBase } from "../lib/knowledgeRepository.js";
import type { TopicId } from "../types/knowledge.js";
import { TOPIC_IDS } from "../types/knowledge.js";

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
  /** Optional role filter */
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
// Math helpers
// ---------------------------------------------------------------------------

function dot(a: number[], b: number[]): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}
function norm(a: number[]): number {
  return Math.sqrt(dot(a, a));
}
function cosine(a: number[], b: number[]): number {
  const n = norm(a) * norm(b);
  return n > 0 ? dot(a, b) / n : 0;
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

  const kb = await loadKnowledgeBase();
  const queryVec = await embedFn(query);

  // Collect all facts with their metadata
  const candidates: Array<{
    text: string;
    topicId: TopicId;
    topicLabel: string;
    role: string;
  }> = [];

  for (const topicId of TOPIC_IDS) {
    if (topic && topicId !== topic) continue;
    const topicData = kb[topicId];
    if (!topicData) continue;

    const topicLabel = topicData._label ?? topicId;

    for (const [roleKey, facts] of Object.entries(topicData)) {
      if (roleKey.startsWith("_") || !Array.isArray(facts)) continue;
      if (role && roleKey !== role && roleKey !== "all_roles") continue;

      for (const fact of facts as string[]) {
        if (typeof fact === "string" && fact.trim()) {
          candidates.push({
            text: fact.trim(),
            topicId,
            topicLabel,
            role: roleKey,
          });
        }
      }
    }
  }

  if (candidates.length === 0) {
    return { query, channel: "A", total: 0, results: [] };
  }

  // Embed all candidate facts in one batch
  // For Channel A (< 200 facts), this is fast enough per-request
  const factTexts = candidates.map((c) => c.text);
  const factVecs = await Promise.all(factTexts.map((t) => embedFn(t)));

  // Score and filter
  const scored: ChannelAResult[] = [];
  for (let i = 0; i < candidates.length; i++) {
    const score = cosine(queryVec, factVecs[i]);
    if (score < min_score) continue;
    scored.push({
      id: `A_${candidates[i].topicId}_${i}`,
      text: candidates[i].text,
      topic: candidates[i].topicId,
      topic_label: candidates[i].topicLabel,
      role: candidates[i].role,
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
