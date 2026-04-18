/**
 * searchChannelB.ts — Channel B: Semantic search over the LLM-wiki index
 *
 * Channel B searches the pre-embedded wiki_index.json (810 chunks from vault
 * extracts, approved facts, and statistical facts). Embeddings are pre-computed
 * — only the query is embedded at search time.
 *
 * Key design decisions:
 *   - Default top_k=8, min_score=0.30 (raised from 0.10 for relevance)
 *   - Statistical facts filtered out by default (include_statistical=false)
 *   - LLM synthesis: top 5 chunks sent to gpt-4.1-nano for a concise answer
 */

import type { EmbedFn } from "../lib/embeddingClient.js";
import {
  searchWiki,
  type WikiContentType,
  type WikiSearchResult,
} from "../lib/wikiRepository.js";
import type { TopicId } from "../types/knowledge.js";
import { TOPIC_IDS } from "../types/knowledge.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type LlmFn = (prompt: string) => Promise<string>;

export interface ChannelBResult {
  id: string;
  text: string;
  title: string;
  source_id: string;
  url: string;
  topic: string;
  content_type: WikiContentType;
  fact_type: string;
  role?: string;
  school_level?: string;
  reference_year?: string;
  /** First PDF page number found in the chunk, if any */
  page?: number;
  score: number;
  channel: "B";
}

export interface SearchChannelBRequest {
  query: string;
  /** Optional topic filter */
  topic?: TopicId;
  /** Optional content_type filter */
  content_type?: WikiContentType;
  /** Minimum similarity score 0–1. Default: 0.22 */
  min_score?: number;
  /** Maximum number of results to return. Default: 8 */
  top_k?: number;
  /** Include statistical facts. Default: false */
  include_statistical?: boolean;
  /** Generate LLM synthesis answer. Default: true */
  synthesize?: boolean;
}

export interface SearchChannelBResponse {
  query: string;
  channel: "B";
  /** LLM-synthesised answer (Traditional Chinese, ≤120 chars) */
  synthesis?: string;
  total: number;
  results: ChannelBResult[];
}

// ---------------------------------------------------------------------------
// Synthesis
// ---------------------------------------------------------------------------

const SYNTHESIS_PROMPT = `你是香港學校管治的政策顧問。以下是從教育局政策文件中檢索到的相關資料。
請根據這些資料，用簡潔繁體中文回答問題。直接總結資料的重點，不超過120字，不需列出來源編號。

問題：{QUERY}

政策資料：
{CHUNKS}`;

async function synthesizeAnswer(query: string, results: ChannelBResult[], llmFn: LlmFn): Promise<string> {
  const top5 = results.slice(0, 5);
  if (top5.length === 0) return "找不到相關政策。";

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

/** Extract the first page number found in a raw chunk (from === Page N === markers) */
function extractFirstPage(raw: string): number | undefined {
  const m = raw.match(/={2,}\s*Page\s*(\d+)\s*={2,}/i);
  return m ? parseInt(m[1], 10) : undefined;
}

/** Clean raw PDF extraction artefacts from chunk text */
function cleanChunkText(raw: string): string {
  const CJK = "\u3000-\u9FFF\uF900-\uFAFF\uFE30-\uFE4F";
  const cjkRe = new RegExp(`([${CJK}])[ \t]+([${CJK}0-9（）、，。：；「」『』—…])`, "g");
  return raw
    .replace(/={2,}\s*Page\s*\d+\s*={2,}/gi, " ")   // strip === Page N ===
    .replace(/\f/g, " ")
    .replace(cjkRe, "$1$2")
    .replace(cjkRe, "$1$2")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function toChannelBResult(r: WikiSearchResult): ChannelBResult {
  const c = r.chunk;
  const page = extractFirstPage(c.text);
  return {
    id: c.id,
    text: cleanChunkText(c.text),
    ...(page !== undefined ? { page } : {}),
    title: c.title,
    source_id: c.source_id,
    url: c.url,
    topic: c.topic,
    content_type: c.content_type,
    fact_type: c.fact_type,
    ...(c.role ? { role: c.role } : {}),
    ...(c.school_level ? { school_level: c.school_level } : {}),
    ...(c.reference_year ? { reference_year: c.reference_year } : {}),
    score: r.score,
    channel: "B",
  };
}

export async function searchChannelB(
  request: SearchChannelBRequest,
  embedFn: EmbedFn,
  llmFn?: LlmFn
): Promise<SearchChannelBResponse> {
  const {
    query,
    topic,
    content_type,
    min_score = 0.22,
    top_k = 8,
    include_statistical = false,
    synthesize: doSynthesize = true,
  } = request;

  if (!query?.trim()) {
    throw new Error("query is required");
  }

  // Validate optional topic filter
  if (topic && !(TOPIC_IDS as readonly string[]).includes(topic)) {
    throw new Error(`Invalid topic: ${topic}`);
  }

  const rawResults = await searchWiki(query, embedFn, {
    minScore: min_score,
    topK: top_k,
    ...(topic ? { topic } : {}),
    ...(content_type ? { contentType: content_type } : {}),
  });

  let results = rawResults.map(toChannelBResult);

  // Filter out statistical facts unless explicitly requested:
  //   - content_type "stat_fact" (auto-approved stats)
  //   - source_id starting with "stat_" (vault extracts from statistical sources)
  if (!include_statistical) {
    results = results.filter(r =>
      r.content_type !== "stat_fact" && !r.source_id.startsWith("stat_")
    );
  }

  // Apply top_k after filtering
  results = results.slice(0, top_k);

  // LLM synthesis
  let synthesis: string | undefined;
  if (doSynthesize && llmFn && results.length > 0) {
    synthesis = await synthesizeAnswer(query, results, llmFn);
  }

  return {
    query,
    channel: "B",
    ...(synthesis !== undefined ? { synthesis } : {}),
    total: results.length,
    results,
  };
}
