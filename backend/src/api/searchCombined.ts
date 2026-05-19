/**
 * searchCombined.ts — Channel A+B: Merged semantic search
 *
 * Runs Channel A and Channel B searches in parallel, then merges and
 * re-ranks results by score. Results include a `channel` field ("A" or "B")
 * so the frontend can display source labels.
 *
 * Scoring note:
 *   Channel A scores are re-computed embeddings against approved facts.
 *   Channel B scores are pre-computed embeddings from wiki_index.json.
 *   Both use the same model (text-embedding-3-small) so scores are comparable.
 */

import type { EmbedFn } from "../lib/embeddingClient.js";
import {
  searchChannelA,
  type ChannelAResult,
} from "./searchChannelA.js";
import {
  failedChannelBResponse,
  searchChannelB,
  type ChannelBDegradedKind,
  type ChannelBResult,
  type LlmFn,
  type SearchChannelBResponse,
} from "./searchChannelB.js";
import type { TopicId } from "../types/knowledge.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CombinedResult = (ChannelAResult | ChannelBResult) & {
  channel: "A" | "B";
};

export interface SearchCombinedRequest {
  query: string;
  /** Optional topic filter applied to both channels */
  topic?: TopicId;
  /** Minimum similarity score 0–1. Default: 0.22 */
  min_score?: number;
  /** Maximum results from Channel B. Default: 8 */
  top_k?: number;
  /** Generate LLM synthesis answer. Default: true */
  synthesize?: boolean;
}

export interface SearchCombinedResponse {
  query: string;
  channel: "A+B";
  /** LLM-synthesised answer (Traditional Chinese, ≤120 chars) */
  synthesis?: string;
  total: number;
  total_a: number;
  total_b: number;
  /** true when Channel B was unconfigured/failed and only Channel A contributed */
  channel_b_degraded?: boolean;
  /**
   * Machine-readable reason Channel B did not contribute. "unconfigured" =
   * Supabase env missing; "error" = Channel B failed at search time. Lets
   * monitoring/eval distinguish a real failure from a misconfiguration
   * without string-matching the reason (PROJECT_MASTER_SPEC §E.13).
   */
  channel_b_status?: ChannelBDegradedKind;
  /** Reason Channel B did not contribute, when degraded */
  channel_b_reason?: string;
  results: CombinedResult[];
}

// ---------------------------------------------------------------------------
// Synthesis — reuse same prompt as Channel B
// ---------------------------------------------------------------------------

const SYNTHESIS_PROMPT = `你是香港學校管治的政策顧問。以下是從教育局政策文件中檢索到的相關資料。
請根據這些資料，用簡潔繁體中文回答問題。直接總結資料的重點，不超過120字，不需列出來源編號。

問題：{QUERY}

政策資料：
{CHUNKS}`;

async function synthesizeAnswer(
  query: string,
  results: CombinedResult[],
  llmFn: LlmFn
): Promise<string> {
  const top5 = results.slice(0, 5);
  if (top5.length === 0) return "";

  const chunkText = top5
    .map((r, i) => `[${i + 1}] ${r.text}`)
    .join("\n\n");

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
// Handler
// ---------------------------------------------------------------------------

export async function searchCombined(
  request: SearchCombinedRequest,
  embedFn: EmbedFn,
  llmFn?: LlmFn
): Promise<SearchCombinedResponse> {
  const { query, topic, min_score = 0.22, top_k = 8, synthesize: doSynthesize = true } = request;

  if (!query?.trim()) {
    throw new Error("query is required");
  }

  // Run both channels in parallel. Channel B is isolated: a failure or
  // degraded (unconfigured Supabase) Channel B must NOT break the combined
  // response — Channel A results are still returned successfully.
  const [aResp, bResp] = await Promise.all([
    searchChannelA({ query, topic, min_score }, embedFn),
    searchChannelB({ query, topic, min_score, top_k, synthesize: false }, embedFn).catch(
      (err): SearchChannelBResponse => {
        console.error("[combined] Channel B failed, degrading to Channel A only:", err);
        return failedChannelBResponse(query);
      }
    ),
  ]);

  const channelBDegraded = bResp.degraded === true;

  // Merge and deduplicate by text prefix (Channel A facts may appear in Channel B index)
  const seenPrefixes = new Set<string>();
  const merged: CombinedResult[] = [];

  // Channel A results (human-approved) — processed first to take priority in dedup
  for (const r of aResp.results) {
    const prefix = r.text.slice(0, 80);
    if (!seenPrefixes.has(prefix)) {
      seenPrefixes.add(prefix);
      merged.push(r as CombinedResult);
    }
  }

  // Channel B results
  for (const r of bResp.results) {
    const prefix = r.text.slice(0, 80);
    if (!seenPrefixes.has(prefix)) {
      seenPrefixes.add(prefix);
      merged.push(r as CombinedResult);
    }
  }

  // Re-sort by descending score
  merged.sort((a, b) => b.score - a.score);

  // LLM synthesis over merged top results
  let synthesis: string | undefined;
  if (doSynthesize && llmFn && merged.length > 0) {
    synthesis = await synthesizeAnswer(query, merged, llmFn);
  }

  return {
    query,
    channel: "A+B",
    ...(synthesis ? { synthesis } : {}),
    total: merged.length,
    total_a: aResp.total,
    total_b: bResp.total,
    ...(channelBDegraded
      ? {
          channel_b_degraded: true,
          ...(bResp.degraded_kind ? { channel_b_status: bResp.degraded_kind } : {}),
          ...(bResp.reason ? { channel_b_reason: bResp.reason } : {}),
        }
      : {}),
    results: merged,
  };
}
