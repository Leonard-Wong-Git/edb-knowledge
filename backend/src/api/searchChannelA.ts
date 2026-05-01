/**
 * searchChannelA.ts — Channel A: Semantic search over approved policy facts
 *
 * Channel A facts are human-reviewed and approved. They are stored in
 * role_facts.json and loaded via knowledgeRepository.ts.
 *
 * Search strategy:
 *   1. Embed the user query + all fact texts in TWO API calls (batch)
 *   2. Score each fact text using cosine similarity against the query embedding
 *   3. Return ALL results above minScore, sorted by descending score
 *
 * Performance: uses embeddingClient.batch() to send all ~1,001 fact texts in a
 * single OpenAI API call instead of 1,001 individual calls.
 */

import type { EmbedFn, BatchEmbedFn } from "../lib/embeddingClient.js";
import { loadKnowledgeBase } from "../lib/knowledgeRepository.js";
import type { TopicId } from "../types/knowledge.js";
import { TOPIC_IDS } from "../types/knowledge.js";

export type LlmFn = (prompt: string) => Promise<string>;

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
  /** Generate LLM synthesis answer. Default: false */
  synthesize?: boolean;
}

export interface SearchChannelAResponse {
  query: string;
  channel: "A";
  /** LLM-synthesised answer (Traditional Chinese, ≤120 chars) */
  synthesis?: string;
  total: number;
  results: ChannelAResult[];
}

// ---------------------------------------------------------------------------
// Synthesis
// ---------------------------------------------------------------------------

const SYNTHESIS_PROMPT = `你是香港學校管治的政策顧問。以下是從教育局已核實政策事實庫中檢索到的相關資料。
請根據這些資料，用簡潔繁體中文回答問題。直接總結資料的重點，不超過120字，不需列出來源編號。

問題：{QUERY}

政策資料：
{CHUNKS}`;

async function synthesizeAnswer(query: string, results: ChannelAResult[], llmFn: LlmFn): Promise<string> {
  const top5 = results.slice(0, 5);
  if (top5.length === 0) return "";
  const chunkText = top5.map((r, i) => `[${i + 1}] ${r.text}`).join("\n\n");
  const prompt = SYNTHESIS_PROMPT
    .replace("{QUERY}", query)
    .replace("{CHUNKS}", chunkText);
  try {
    return await llmFn(prompt);
  } catch {
    return "";
  }
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
  embedFn: EmbedFn & { batch?: BatchEmbedFn },
  llmFn?: LlmFn
): Promise<SearchChannelAResponse> {
  const { query, topic, role, min_score = 0.1, synthesize: doSynthesize = false } = request;

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

  // Embed all candidate facts in a single API call using batch embedding.
  // This replaces the previous Promise.all of N individual calls, which caused
  // rate-limit failures and connection timeouts on the first search request.
  const factTexts = candidates.map((c) => c.text);
  const batchFn = embedFn.batch ?? ((texts: string[]) => Promise.all(texts.map((t) => embedFn(t))));
  const factVecs = await batchFn(factTexts);

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

  // Deduplicate by first 60 characters to remove near-identical facts
  // (same policy stated with slightly different wording from different sources)
  const seen = new Set<string>();
  const deduped = scored.filter(r => {
    const key = r.text.slice(0, 60);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // LLM synthesis over top results
  let synthesis: string | undefined;
  if (doSynthesize && llmFn && deduped.length > 0) {
    synthesis = await synthesizeAnswer(query, deduped, llmFn);
  }

  return {
    query,
    channel: "A",
    ...(synthesis !== undefined ? { synthesis } : {}),
    total: deduped.length,
    results: deduped,
  };
}
