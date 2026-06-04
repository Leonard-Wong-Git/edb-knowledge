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

import { isSupabaseConfigured } from "../config/env.js";
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

/**
 * Why Channel B is degraded.
 *   "unconfigured" = Supabase env missing (static, all-or-none guard)
 *   "error"        = Channel B threw at search time (transient / infra)
 * The distinction MUST survive to the client so monitoring/eval can tell a
 * real failure apart from a misconfiguration (PROJECT_MASTER_SPEC §E.13).
 */
export type ChannelBDegradedKind = "unconfigured" | "error";

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
  /** false when Channel B is unconfigured/degraded; omitted (treated as true) otherwise */
  ok?: boolean;
  /** true when Channel B could not contribute (unconfigured OR a runtime failure) */
  degraded?: boolean;
  /** Discriminates *why* it degraded (unconfigured vs real failure) — see ChannelBDegradedKind */
  degraded_kind?: ChannelBDegradedKind;
  /** Human-readable reason for degradation (Traditional Chinese) */
  reason?: string;
  /** LLM-synthesised answer (Traditional Chinese, ≤120 chars) */
  synthesis?: string;
  total: number;
  results: ChannelBResult[];
}

/**
 * Reason text surfaced to clients when Channel B is unconfigured.
 * Exported so the combined handler can reuse the same message.
 */
export const CHANNEL_B_UNCONFIGURED_REASON =
  "Channel B 未配置（Supabase 環境變數缺失）";

/**
 * Reason text when Channel B threw at search time (transient / infra failure
 * — NOT a misconfiguration). Deliberately distinct from
 * CHANNEL_B_UNCONFIGURED_REASON so a real failure is never disguised as
 * "未配置" to monitoring/eval (was a promote-blocker — PROJECT_MASTER_SPEC §E.13).
 */
export const CHANNEL_B_ERROR_REASON =
  "Channel B 暫時無法使用（檢索服務異常）";

/** Build the standard degraded (Supabase unconfigured) Channel B response. */
export function degradedChannelBResponse(query: string): SearchChannelBResponse {
  return {
    query,
    channel: "B",
    ok: false,
    degraded: true,
    degraded_kind: "unconfigured",
    reason: CHANNEL_B_UNCONFIGURED_REASON,
    total: 0,
    results: [],
  };
}

/**
 * Build the degraded Channel B response for a real search-time failure
 * (an exception was thrown). Distinct kind + reason from the unconfigured
 * case so the combined handler never masks a transient/infra failure as
 * "未配置" — keeps Channel B failures visible to monitoring/eval.
 */
export function failedChannelBResponse(query: string): SearchChannelBResponse {
  return {
    query,
    channel: "B",
    ok: false,
    degraded: true,
    degraded_kind: "error",
    reason: CHANNEL_B_ERROR_REASON,
    total: 0,
    results: [],
  };
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
  // ── PLAN-1b selective routes (S118) — matched before the broad production
  // categories below. SAG is intentionally allowed in `cpd`/`conduct` (their
  // gold lives in sag_2025_11) but stays bounded by the per-source quota, so
  // it does not re-introduce the §E.3 SAG-domination these tight sets avoid.
  cpd: [
    "sag_2025_11",
    "g06",
    "circ_edbc24017",
    "role_facts_hr",
    "role_facts_curriculum",
    "role_facts_general",
  ],
  kg_admission: [
    "g26",
    "g25",
    "role_facts_general",
  ],
  conduct: [
    "g05",
    "sag_2025_11",
    "role_facts_student",
    "role_facts_hr",
    "role_facts_general",
  ],
  // SEN / 特殊教育 / 融合教育 (S138). Bare "sen" + 特殊教育/融合教育 queries previously
  // matched no category → fell through to a raw whole-index search at the 0.22 floor
  // and surfaced phys_sss mojibake (now dropped). This dedicated route narrows to the
  // real SEN corpus: g06 (PECG SEN sections) + sag_2025_11 + the student/general role
  // facts (SENCO gold) + g10《特殊學校課程指引》+ g19《全校參與模式融合教育運作指南》
  // (both backfilled S138 — §E.12 URL re-discovery) + sen_exam_arrangements_2025
  // 《為有特殊教育需要學生提供校內考試特別安排》(S141 backfill — sea_guide_c.pdf, distinct from g19).
  // routing-not-cutoff lever (S118 PLAN-1b). NB: new Supabase sources do NOT surface for a
  // topic-routed category until added to this allowlist (S135 backfill-allowlist coupling lesson).
  sen: [
    "g06",
    "sag_2025_11",
    "role_facts_student",
    "role_facts_general",
    "g10",
    "g19",
    "sen_exam_arrangements_2025",
  ],
  // (steam route has no source filter — plain retrieval + expansion only.)

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
    "history_jss_2019",  // S135: 西史/世界歷史初中課程指引（中一至中三）2019 — backfilled (§E.12 URL re-discovery); without this, curriculum-category history queries mis-route to chi_hist (中史)
    "history_sss_2007_2015",  // S135 Phase 3a tail: 西史高中歷史課程及評估指引（中四至中六）— pre-existing allowlist gap, added for parity with chi_hist + 初中
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
    "edbc197_2024_ph_pri",  // S135 Phase 3c: 通函197/2024 小學人文科問卷 — backfilled (§E.12); add to allowlist so it surfaces for curriculum queries
    "edbc13_2025_pri_science",
    "edbc002_2026",
    "edbc003_2026",
    "edbc005_2026",
    "circ_edbc24017",
    // Kindergarten / 幼兒教育 sources（Session 100 加入）
    "g29",               // 幼稚園教育課程指引（2017）
    "g25",               // 幼稚園相關指引及須知
    "g26",               // 2026/27 幼稚園收生安排指引
    "stat_kg",           // 幼稚園統計數字
  ],
};

/** Keyword patterns for each category (Traditional Chinese). */
const TOPIC_KEYWORDS: Record<string, RegExp> = {
  // PLAN-1b selective routes (S118) — first-match precedence; keep first.
  cpd: /CPD|持續專業發展|教師專業發展|教師培訓|專業發展計劃|專業階梯|師訓/,
  kg_admission: /幼稚園收生|幼稚園.{0,3}收生|幼稚園.{0,3}入學|幼稚園.{0,3}報名|K1.{0,3}收生|幼稚園.{0,3}申請入學/,
  conduct: /體罰|施行體罰|羞辱學生|虐待學生|教師操守|專業操守|教師專業操守/,
  steam: /STEAM|STEM/,
  finance: /採購|招標|單一報價|競投|供應商|報價單|分判|貨物|服務合約|財務管理|預算|撥款|開支|報銷|捐款|借款|代收費|利益衝突|申報利益|賄賂|廉署|防賄|資助則例|法團校董|校董會經費|採購門檻|採購程序/,
  hr_admin: /假期|請假|病假|年假|婚假|侍產假|產假|特別假|補假|批假|薪酬|薪金|薪級|增薪點|津貼|教職員假|教師假|教師操守|專業操守|校曆|學年假|在職培訓日|教師註冊|註冊處|聘任|聘用|招聘|入職|教師資格|教席|常額教席|代課教師/,
  activity: /全方位學習|活動津貼|課外活動|全方位學習津貼/,
  // SEN — MUST stay before `curriculum` (first-match precedence): "特殊學校課程指引"
  // contains 課程 and would otherwise route to curriculum. \bsen\b/i catches the bare
  // English token (real users type "sen"); the rest catch the Chinese terminology.
  sen: /\bsen\b|\bsenco\b|特殊教育|特殊學校|融合教育|全校參與|統籌主任|特殊學習需要|有特殊教育需要/i,
  curriculum: /課程|科目|教學|學習目標|評估|教材|課程發展|學習領域|教師發展|CPD|專業發展|英文科|中文科|數學科|常識科|科學科|體育科|音樂科|視藝科|小學課程|中學課程|課程指引|學習成果|評核|幼稚園|幼兒|學前|K1|K2|K3|遊戲學習/,
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

/**
 * Query expansion: append category-specific vocabulary to the query before
 * embedding, so the query vector stays aligned with the terminology used in
 * the target source documents (e.g. g01 uses "財政限額" not "門檻").
 *
 * Without expansion, "採購門檻" embedding gets pulled toward SAG's teacher-
 * registration usage of "門檻" and scores poorly against g01 chunks.
 */
const QUERY_EXPANSIONS: Record<string, string> = {
  // PLAN-1b selective routes (S118) — same single map, no parallel mechanism.
  cpd:          "教師持續專業發展 持續專業發展 教育局通告29/2024 教師培訓要求 專業階梯 校本專業發展政策 師訓會 教師專業能力理念架構",
  kg_admission: "幼稚園收生安排指引 K1 註冊證 報名費 註冊費 統一註冊日期 申請入學 收生程序 空缺",
  conduct:      "教師專業操守指引 教育規例第58條 教員不得向學生施行體罰 操守 學生保護",
  sen:          "特殊教育需要 融合教育 全校參與模式 特殊學校課程指引 融合教育運作指南 特殊教育需要統籌主任 SENCO 學生支援組 個別學習計劃 三層支援模式 校本支援 共融校園 照顧學生個別差異 校內考試特別安排 考試調適 評估調適 特別考試安排",
  steam:        "STEAM教育 跨學科 課程更新重點 七大重點 STEAM專責小組 科學科技工程藝術數學",
  finance:    "採購程序 財政限額 報價 招標 採購指引",
  hr_admin:   "教職員假期 批假 薪酬 操守 病假 首年 168日 上限 醫生證明 教師註冊 聘任",
  activity:   "全方位學習津貼 活動",
  curriculum: "課程指引 教學 學習目標",
};

function expandQuery(query: string, category: string): string {
  const expansion = QUERY_EXPANSIONS[category];
  return expansion ? `${query} ${expansion}` : query;
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

  // Graceful degradation: if Supabase (Channel B backing store) is not
  // configured, return an explicit degraded response instead of throwing.
  // This keeps the dedicated endpoint at HTTP 200 and lets the combined
  // handler fall back to Channel A only.
  if (!isSupabaseConfigured()) {
    return degradedChannelBResponse(query);
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

  // Expand the query with category vocabulary to align the embedding with
  // the terminology used in the target source documents.
  const embeddingQuery = detectedCategory ? expandQuery(query, detectedCategory) : query;

  // Per-source quota: cap each source_id at ~top_k/3 (min 2) so that a single
  // dominant source like SAG (415 chunks) can't monopolize results and crowd
  // out smaller, more relevant guides like g04 (7 chunks) or g29 (132 chunks).
  // Disabled when narrowing to a single source (no diversity needed there).
  const maxPerSource =
    sourceIds && sourceIds.length <= 1 ? undefined : Math.max(2, Math.ceil(top_k / 3));

  const rawResults = await searchWiki(embeddingQuery, embedFn, {
    minScore: effectiveMinScore,
    topK: top_k,
    ...(topic ? { topic } : {}),
    ...(content_type ? { contentType: content_type } : {}),
    ...(sourceIds ? { sourceIds } : {}),
    ...(maxPerSource ? { maxPerSource } : {}),
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
