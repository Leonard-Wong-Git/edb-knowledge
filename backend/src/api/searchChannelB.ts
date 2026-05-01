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
  /**
   * Enable automatic query-topic detection to restrict search to relevant
   * source documents and prevent high-volume sources (e.g. SAG) from
   * drowning out smaller but more relevant admin guides. Default: true
   */
  enable_topic_filter?: boolean;
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
// Topic-aware source filtering
// ---------------------------------------------------------------------------

/**
 * Source sets by query category.
 *
 * Problem: sag_2025_11 has 415 chunks (14% of index) and covers many topics.
 * For narrow admin queries (procurement, HR), its sheer volume causes it to
 * dominate results, pushing out smaller but far more relevant guides.
 *
 * Solution: detect the query category from keywords and restrict the search
 * to the most relevant source documents.
 */
const SOURCE_SETS: Record<string, string[]> = {
  /**
   * Finance / Procurement — 採購, 招標, 財務管理, 資助則例
   * Exclude SAG: its "門檻" references are teacher-registration thresholds,
   * not procurement thresholds; would drown out g01 (32 chunks).
   */
  finance: [
    "g01",               // 資助學校採購程序指引
    "g02",               // 法團校董會財務管理指引
    "coa_imc_1_19",      // 資助則例 (IMC)
    "role_facts_finance",
    "role_facts_general",
  ],

  /**
   * HR / Leave / Professional conduct — 假期, 批假, 薪酬, 操守
   * Include SAG (it has meaningful HR sections); exclude pure curriculum guides.
   */
  hr_admin: [
    "g04",               // 教職員批假指引
    "g05",               // 教師專業操守指引
    "g11",               // 擬定校曆表指引
    "sag_2025_11",       // School Administration Guide (HR sections)
    "role_facts_hr",
    "role_facts_general",
  ],

  /**
   * Activity grants — 全方位學習津貼, 課外活動
   */
  activity: [
    "g03",               // 全方位學習津貼運用指引
    "role_facts_activity",
    "role_facts_general",
  ],

  /**
   * Curriculum / Teaching — 課程, 科目, 教學, 評估, CPD
   * Exclude SAG (minimal curriculum content, adds noise).
   */
  curriculum: [
    "eng_pri_guide_2025",
    "ph_pri_guide_2025",
    "pri_science_guide_2025",
    "ma_kla_guide_2017",
    "pri_curr_guide_2024",
    "chi_hist_jss_2019",
    "music_p1_s6_2024",
    "gs_pri_guide_2017",
    "va_p1_s6_2024",
    "chi_jss_guide_2023",
    "chi_pri_guide_2023",
    "pe_kla_2017",
    "role_facts_curriculum",
    "edbc18_2023_pri_science",
    "edbc20_2023_ph_pri",
    "edbc9_2024_ph_pri",
    "edbc12_2025_ph_pri",
    "edbc13_2025_pri_science",
    "edbc002_2026",
    "edbc003_2026",
    "edbc005_2026",
    "circ_edbc24017",
  ],
};

/** Keyword patterns for each category (Traditional Chinese). */
const TOPIC_KEYWORDS: Record<string, RegExp> = {
  finance: /採購|招標|單一報價|競投|供應商|報價單|分判|貨物|服務合約|財務管理|預算|撥款|開支|報銷|捐款|借款|代收費|利益衝突|申報利益|賄賂|廉署|防賄|資助則例|法團校董|校董會經費|採購門檻|採購程序/,
  hr_admin: /假期|請假|病假|年假|婚假|侍產假|產假|特別假|補假|批假|薪酬|薪金|薪級|增薪點|津貼|教職員假|教師假|教師操守|專業操守|校曆|學年假|在職培訓日/,
  activity: /全方位學習|活動津貼|課外活動|全方位學習津貼/,
  curriculum: /課程|科目|教學|學習目標|評估|教材|課程發展|學習領域|教師發展|CPD|專業發展|英文科|中文科|數學科|常識科|科學科|體育科|音樂科|視藝科|小學課程|中學課程|課程指引|學習成果|評核/,
};

/**
 * Detect query category from keywords.
 * Returns the category key (matching SOURCE_SETS) or null if none detected.
 * Finance takes precedence over HR to avoid overlap (e.g. "薪酬採購").
 */
function detectQueryCategory(query: string): string | null {
  for (const [category, pattern] of Object.entries(TOPIC_KEYWORDS)) {
    if (pattern.test(query)) return category;
  }
  return null;
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
    enable_topic_filter = true,
  } = request;

  if (!query?.trim()) {
    throw new Error("query is required");
  }

  // Validate optional topic filter
  if (topic && !(TOPIC_IDS as readonly string[]).includes(topic)) {
    throw new Error(`Invalid topic: ${topic}`);
  }

  // Auto-detect query category for source filtering
  const detectedCategory = enable_topic_filter ? detectQueryCategory(query) : null;
  const sourceIds = detectedCategory ? SOURCE_SETS[detectedCategory] : undefined;

  // When a topic filter is active we've already narrowed to relevant sources,
  // so we can afford a lower similarity threshold to surface relevant chunks
  // that use different terminology (e.g. "財政限額" vs "採購門檻").
  const effectiveMinScore = sourceIds ? Math.min(min_score, 0.08) : min_score;

  const rawResults = await searchWiki(query, embedFn, {
    minScore: effectiveMinScore,
    topK: top_k,
    ...(topic ? { topic } : {}),
    ...(content_type ? { contentType: content_type } : {}),
    ...(sourceIds ? { sourceIds } : {}),
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
