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
  searchFootnotes,
  searchSpotlightSources,
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
  /** LLM-synthesised answer (Traditional Chinese, ≤~250 chars / 上限300) */
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
  // S183 — 價值觀教育課程架構 (value_education route). EDB 4 key tasks 之一。
  // VE_CF_2026 正式版 (93 chunks, S183 入庫) + 配套 EDBC 3/2026 (edbc003_2026, prior 6 chunks)
  // + 試行版 2021 (existing) + 2023 EDBC 183 豐富 (existing, superseded_by 2026) + 中學課程指引 6A
  // (existing, 2017 德育及公民教育). Routed before curriculum so 價值觀 / 首要價值觀 / 立根中華
  // / 德育 / 公民教育 queries reach this dedicated corpus not generic 課程 search.
  value_education: [
    "values_edu_framework_2026",
    "edbc003_2026",
    "values_edu_framework_2021_trial",
    "edbcm183_2023_values_edu",
    "sec_curr_guide_2017_booklet_6a",
    "edbcm076_2026",              // (auto) Option A watcher ingest
  ],
  // S171 — DEBP 中小學數字教育發展藍圖 / AI 素養 (digital_education route). 6 sources
  // ingested 2026-06-17 (209 chunks, topic=it). Cohesive digital-education corpus; routed
  // before curriculum so 數字教育/AI 素養/發展藍圖 queries reach it not generic 課程 search.
  // S183 — 擴 +edbcm_221_2025_smart_teaching (15 chunks, 智啟學教撥款計劃) 入 set; 通函
  // 內容係 AI 賦能教育撥款 + 校本實施承諾, 同 DEBP 路徑一脈。
  // S184 — 擴 +edbc008_2026 (12 chunks, 學校效率津貼) 入 set; 教育局通告第8/2026號,
  // 2026/27 起設立, 支持學校加快教育數字化轉型 (配合 DEBP), 同一脈絡。
  digital_education: [
    "debp_blueprint",
    "debp_exec_summary",
    "debp_ai_literacy_framework",
    "debp_ai_teaching_guide",
    "debp_ailf_example",
    "debp_ai_examples",
    "edbcm_221_2025_smart_teaching",
    "edbc008_2026",
    "edbcm073_2026",     // S186: QEF 電子學習撥款計劃 — 提供流動電腦裝置及上網支援 (2026/27)
    "edbc011_2026",      // S186: 教育局通告11/2026《中小學數字教育發展藍圖》正式通告 (補 DEBP corpus)
    "edbcm107_2026",     // S186: 學校落實 AI 教育規劃培訓 + AI 教師培訓 (第一期 2026/7-9)
    "edbcm113_2026",              // (auto) Option A watcher ingest
    // S194 — 《小學資訊與創新科技課程框架》「人工智能初探」範疇（試行版）正文 (18 chunks).
    // edbcm113_2026 is only the announcing circular (3 chunks = cover + summary); this is
    // the framework itself, so an 「人工智能初探」query has real content to answer from.
    "iit_ai_framework_2026",
  ],
  /**
   * S194 — 公民與社會發展科 (cgss route). Its corpus reached the index by accident: the
   * 公社科 C&A guide was stored under `ict_sss_2021` because the filename CS_CAG was read
   * as Computer Science rather than Citizenship and Social development, so 81 chunks of
   * this subject were served under the ICT title until S194 relabelled them to
   * `cgss_sss_2021`. Without a route the corpus is only reachable when it happens to win
   * the global ANN pass — measured 0.577 for 「公民與社會發展科」 but 0.484 for
   * 「一國兩制 課程」, which loses the global window. Keywords sit AFTER value_education
   * so 公民教育 / 德育 keep routing there, and before curriculum so the subject-specific
   * corpus is not diluted by generic 課程 search. This is also the standing suspect for
   * the long-running "cgss rank 低" monitor.
   */
  cgss: [
    "cgss_sss_2021",
    "ces_jss_2024",   // 公民、經濟與社會（中一至中三）— the junior-secondary feeder subject
  ],
  // ── PLAN-1b selective routes (S118) — matched before the broad production
  // categories below. SAG is intentionally allowed in `cpd`/`conduct` (their
  // gold lives in sag_2025_11) but stays bounded by the per-source quota, so
  // it does not re-introduce the §E.3 SAG-domination these tight sets avoid.
  cpd: [
    "sag_2025_11",
    "g06",
    "circ_edbc24017",
    "tdtf_report_2019",  // S142 §2: 教師專業發展專責小組報告 (T-standard / CPD policy origin)
    "role_facts_hr",
    "role_facts_curriculum",
    "role_facts_general",
  ],
  kg_admission: [
    "g26",
    "g25",
    "k1_admission_2627",   // S152: 2026/27 K1 入學安排 (通函 EDBCM81/2025 + FAQ), Discovery
    "kg_admin_guide",      // S152: 幼稚園學費涵蓋/售賣物品指引, Discovery
    "edbcm080_2026",       // S186: 通函80/2026 — 2027/28學年幼稚園幼兒班收生安排
    "role_facts_general",
  ],
  // S142 §5 — primary/secondary place allocation + student-info-management (P1/SSPA/S4/STIMS).
  // Distinct from kg_admission (KG-only). Most admission content is parent forms/HTML mechanism;
  // these are the thin net-new full-text policy docs.
  placement: [
    "edbc18_2019_sspa", "stims_guide_2025", "s4_placement_2026",
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
    "cgss_2024",         // S152: 特殊學校課程指引資源 (2024) — alongside g10, Discovery backfill
  ],
  // 資優教育 / 天才 (S150). Bare 資優/資賦 queries previously matched no category →
  // whole-index search at the 0.22 floor; g14 (校本資優培育指引, ingested S146) + the new
  // gifted_policy_docs (S150: 資優教育政策文件2008 + 香港資優發展 HTML) had no route. This
  // dedicated set narrows to the real gifted corpus: gifted_policy_docs + g14 + g06 (PECG
  // gifted sections) + general role facts. routing-not-cutoff lever (S118 PLAN-1b). NB: must
  // precede `curriculum` in TOPIC_KEYWORDS (資優教育課程 contains 課程).
  gifted: [
    "gifted_policy_docs",
    "gifted_tp_resource_kit",     // S150: 校本資優教育資源套 (2024)
    "gifted_osalp_compendium",    // S150: 資優教育基金校外進階學習課程匯編 (OSALP)
    "gifted_ge_series",           // S152: 全民資優教育 + 校本學生才能庫 + 學術英才教育單元 (Discovery)
    "edbcm095_2026",              // S186: 通函95/2026 — 資優教育學校網絡計劃2026/27 + 教師專業培訓
    "g14",
    "g06",
    "role_facts_general",
  ],
  // (steam route has no source filter — plain retrieval + expansion only.)

  /**
   * School governance / IMC (法團校董會) — 校董會成立運作, 校董角色責任, 校董會會議,
   * 校董選舉/委任, 校監, 辦學團體, 校董行為守則, 法例提醒. S154 SBM-governance backfill
   * (sbm.edb.gov.hk references). MUST precede `finance` in TOPIC_KEYWORDS: finance owns
   * the substring `法團校董` (for g02 IMC-finance), so without an earlier governance route
   * any 法團校董會/校董會 query routes to finance and the governance corpus never surfaces.
   * This set bundles the new governance docs WITH g02 + coa_imc_1_19 so an IMC query gets
   * the full IMC doc family (governance + finance + 資助則例) in one route. routing-not-cutoff
   * lever (S118 pattern); S135 backfill-allowlist coupling (new Supabase source needs this
   * allowlist entry to surface in routed search).
   */
  school_governance: [
    "imc_establishment_operation",  // 法團校董會的成立與運作 (校本管理手冊 2014, 82pp)
    "imc_briefing_qa",              // 法團校董會簡介會問答 (2013)
    "imc_governance_supplements",   // 成立運作Ch5/角色責任/會議/法例提醒/良好管治/行為守則
    "imc_election_guides",          // 家長/教師/校友校董選舉指引 + 委任五步曲
    "g02",                          // 法團校董會財務管理指引 (IMC family)
    "coa_imc_1_19",                 // 資助則例 (IMC version)
    "sdp_guide",                    // 如何編寫學校發展計劃 (IMC service-contract)
    "smc_constitution_sample",      // S168: SMC 學校管理委員會章程樣本 (補 SMC 內容 gap, corpus 一直 IMC-heavy)
    "role_facts_general",
  ],

  /**
   * Finance / Procurement — 採購, 招標, 財務管理, 資助則例
   * Exclude SAG: its "門檻" references are teacher-registration thresholds,
   * not procurement thresholds; would drown out g01 (32 chunks).
   */
  finance: [
    "g01",               // 資助學校採購程序指引
    "g02",               // 法團校董會財務管理指引
    "coa_imc_1_19",      // 資助則例 (IMC)
    "fin_mgmt_notes_aided",   // S142: 資助學校財務管理注意事項
    "bank_choice_notes",      // S142: 學校選擇銀行注意事項
    "edbcm089_2026",          // S186: 通函89/2026 — 高中多元學習津貼 (其他語言及其他課程, 2026/27) — 津貼 routes here
    "role_facts_finance",
    "role_facts_general",
    "edbcm096_2026",              // (auto) Option A watcher ingest
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
    // S142 EDB-sweep §1 — staffing/appointment/BLNST policy
    "edbc13_2022_blnst", "edbcm141_2025_blnst", "blnst_test_notes_nondeg", "blnst_test_candidate_notes",
    "embc5_2005_appointment", "edbc14_2023_student_protect", "staff_medical_health",
    "job_sharing_guide", "surplus_teacher_arr_2026", "private_sch_employment_notes",
    "supply_teacher_guide", "long_service_payment_guide",  // S142 §2: 代課教師指引 + 遣散費長服金指引
    "edbcm088_2026",     // S186: 通函88/2026 — 英文／普通話科教師語文能力要求 (LPAT) 及行政安排
    "edbcm066_2026",     // S186: 通函66/2026 — 準英語教師獎學金 (2026/27)
    // S172: sch_calendar_guide deprecated (404 + year-specific 2025/26 holidays superseded; chunks DELETEd). 校曆 queries stay covered by g11 擬定校曆表指引 above.
    "role_facts_hr",
    "role_facts_general",
    "edbcm094_2026",              // (auto) Option A watcher ingest
  ],

  /**
   * Activity grants — 全方位學習津貼, 課外活動
   */
  activity: [
    "g03",               // 全方位學習津貼運用指引
    "sch_activities_guide",   // S152: 戶外活動 + 境外遊學團指引 (Discovery)
    "edbc009_2026",      // S186: 通告9/2026 — 家校合作活動整合津貼
    "edbcm070_2026",     // S186: 通函70/2026 — 2026/27 家庭與學校合作活動計劃資助申請
    "role_facts_activity",
    "role_facts_general",
    "edbc007_2026",              // (auto) Option A watcher ingest
  ],

  /**
   * Student guidance / discipline / support — 訓育輔導, 生涯規劃, 和諧校園/反欺凌,
   * 處理懷疑虐待兒童(強制舉報), 關顧學生, 學校危機處理, 學生精神健康. S142 EDB-sweep §3.
   * Includes existing g16 (訓育工作指引) + g17 (理念與指引).
   */
  student_support: [
    "edbc015_2021_lpe", "lpe_framework_primary", "edbc18_2008_harmonious",
    "edbc15_2025_child_abuse", "edbcm83_2020_student_care", "crisis_mgmt_handbook", "kg_crisis_mgmt",
    "edbc100_2002_healthy_sch", "hsp_framework", "hsp_drug_testing_2026",  // S142 §4: 健康校園/禁毒
    "edbcm081_2026",     // S186: 通函81/2026 — 2026/27 為低收入家庭小學生提供在校免費午膳 (welfare)
    "g16", "g17",
    "sag_2025_11",
    "role_facts_student", "role_facts_general",
  ],

  /**
   * Quality Assurance / School inspection / Self-evaluation — 視學, 校外評核(ESR),
   * 學校自我評估(SSE), 表現指標, 質素保證, 問責架構, 校本管理. Split out of gov_admin
   * (S143): bare short QA tokens (e.g. "視學") under-recalled because the docs use the
   * newer 校外評核/自我評估/問責 vocabulary and gov_admin carries NO expansion. A dedicated
   * tight route + targeted expansion bridges the vocabulary gap WITHOUT diluting the broad
   * gov_admin/safety queries (the S142 over-expansion regression). Tight SOURCE_SET + the
   * per-source quota keep SAG bounded, so expansion is safe here.
   */
  qa_inspection: [
    "sse_tools_2025",             // 學校表現評量/自我評估 (SSE) tools
    "perf_indicators_2022",       // 表現指標
    "edbc15_2022_accountability", // 校外評核/問責架構/校本管理
    "sag_2025_11",
    "role_facts_general",
  ],

  /**
   * Governance / Premises / Registration — 防貪內部監控, 校舍修葺, 增設校舍/更改校名,
   * 學校發展計劃, 籌款, 法團校董會, 學校註冊. (QA/視學/自評/問責 → qa_inspection above, S143.)
   * S142 EDB-coverage sweep §1 (學校行政及管理). routing-not-cutoff lever.
   */
  gov_admin: [
    "icac_school_governance", "fundraising_guide", "edbcm_major_repairs_grant",
    "edbc14_2024_spms", "sch_extension_guide", "sch_name_change_guide", "sdp_guide",
    "bip_insurance_notes_2025", "major_repairs_proc_nonestate", "major_repairs_proc_estate",
    "emergency_repairs_guide",
    "sag_2025_11",
    "role_facts_general",
  ],

  /**
   * School safety — 校園安全, 消防, 職安健, 實驗室安全, 氣體事故, 安全管理委員會,
   * 熱帶氣旋/惡劣天氣停課安排, 斜坡維修檢查. S142 EDB-coverage sweep §1.
   */
  safety: [
    "edbc22_2024_student_safety", "fire_service_installation", "occupational_safety_health",
    "gas_odour_measures", "lab_prep_room_aircon", "edbc_tropical_cyclone_day",
    "edbc_tropical_cyclone_night", "safety_mgmt_committee", "slope_rmi_ei_notes",
    // S149 safety-guideline backfill — siblings of g23 (體育安全, whole-index). KLA/student
    // safety guides; added so 校車/視藝/科技 safety queries route here and surface them
    // (S135 backfill-allowlist coupling). TOPIC_KEYWORDS.safety gains 校車/視藝安全/科技安全.
    "g18",               // 學童乘搭校車的安全指引 (2025/26)
    "g21",               // 視覺藝術科安全指引
    "g22",               // 科技教育學習領域安全指引 (2010)
    "edbc012_2026",      // S186: 通告12/2026 — 校舍消防裝置或設備 (消防年檢)
    "sag_2025_11",
    "role_facts_general",
  ],

  /**
   * Curriculum / Teaching — 課程, 科目, 教學, 評估, CPD
   * Exclude SAG (minimal curriculum content, adds noise).
   */
  curriculum: [
    "kgecg_2017",        // S152: 幼稚園教育課程指引 (2017) — KG curriculum, Discovery backfill
    "eng_pri_guide_2025",
    "ph_pri_guide_2025",
    "pri_science_guide_2025",
    "ma_kla_guide_2017",
    "pri_curr_guide_2024",
    "chi_hist_jss_2019",
    "history_jss_2019",  // S135: 西史/世界歷史初中課程指引（中一至中三）2019 — backfilled (§E.12 URL re-discovery); without this, curriculum-category history queries mis-route to chi_hist (中史)
    "history_sss_2007_2015",  // S135 Phase 3a tail: 西史高中歷史課程及評估指引（中四至中六）— pre-existing allowlist gap, added for parity with chi_hist + 初中
    "music_p1_s6_2024",
    "g38",               // S147: 音樂教育學習領域課程指引(2003, 小一至中三) — OCR backfill (153p CID-mojibake). Coexists with music_p1_s6_2024 (2024, P1-S6): different era + level scope, not a clean supersede; per-source quota bounds dominance — monitor for stale-2003-ranking.
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
    "edbc010_2026",      // S186: 通告10/2026 — 中小學數學課程微調 (加強數學建模元素)
    "circ_edbc24017",
    "mce_framework_2008",  // S147: 德育及公民教育課程架構(2008) OCR backfill — title 含「課程」→ 德育公民課程 queries route to curriculum; without this allowlist entry the new source never surfaces in routed search (S135 backfill-allowlist coupling)
    "phys_sss_2007_2015",  // S148: 物理科課程及評估指引(中四至中六, 2007/2015更新) text-layer backfill (clean re-ingest, U+FFFD=0; supersedes the earlier dropped mojibake copy referenced in the `sen` route note). S135 backfill-allowlist coupling.
    "chi_edu_curr_docs",   // S148: 中國語文教育學習領域課程指引(小一至中六, 2017 CLEKLAG full) text-layer backfill; coexists with g09 (43-48 非華語節錄) — per-source quota bounds overlap. S135 coupling.
    "g13",                 // S148: 中學教育課程指引(2017) SECG full (Intro+booklet 1-11+6A-6D+Supp_notes, 17 PDFs) text-layer backfill. S135 coupling.
    // Kindergarten / 幼兒教育 sources（Session 100 加入）
    "g29",               // 幼稚園教育課程指引（2017）
    "g25",               // 幼稚園相關指引及須知
    "g26",               // 2026/27 幼稚園收生安排指引
    "stat_kg",           // 幼稚園統計數字
    "edbc013_2026",              // (auto) Option A watcher ingest
    // S194 — the ICT senior-secondary guides. Neither was in ANY route's SOURCE_SET, so
    // 「資訊及通訊科技 課程指引」 routed to curriculum and could only ever return other
    // subjects' guides (measured pre-fix: top hit g13, neither ICT source in top 8).
    // Same "backfill-allowlist coupling" trap as the S135 entries above: ingesting a
    // source without adding it to the route that its queries reach leaves it unreachable.
    // ict_sss_2021 carries the real 2021 guide from S194 (116 chunks); before that its id
    // held the 公社科 guide, now `cgss_sss_2021`.
    "ict_sss_2021",
    "ict_sss_2007_2015",  // superseded by the 2021 edition → SUPERSEDED_IDS penalty applies
  ],
  /*
   * Kindergarten administration / operation — 幼稚園行政手冊 + 學前機構辦學手冊 (S160).
   * Distinct from kg_admission (收生-only) and curriculum (課程). Its TOPIC_KEYWORDS
   * entry sits BEFORE curriculum so KG-admin queries don't fall into curriculum's
   * broad 幼稚園 match (which lacks these admin manuals).
   */
  kg_admin: [
    "kg_admin_guide_2026",       // S160: 幼稚園行政手冊（2026年5月）
    "kg_operation_manual_2026",  // S160: 學前機構辦學手冊（2026年5月，第4.3版）
    "kg_admin_guide",            // S152: 幼稚園學費涵蓋 / 售賣物品指引
    "kgecg_2017",                // 幼稚園教育課程指引（2017）— broad KG context
    "g25",                       // 幼稚園相關指引及須知
    "g29",                       // 幼稚園教育課程指引（2017）
    "g26",                       // 2026/27 幼稚園收生安排指引
    "stat_kg",                   // 幼稚園統計數字
    "edbcm060_2026",             // S186: 通函60/2026 — 幼稚園提交2025/26經審核周年帳目 (KG 財務合規)
    "role_facts_general",
  ],
};

/** Keyword patterns for each category (Traditional Chinese). */
const TOPIC_KEYWORDS: Record<string, RegExp> = {
  // PLAN-1b selective routes (S118) — first-match precedence; keep first.
  cpd: /CPD|持續專業發展|教師專業發展|教師培訓|專業發展計劃|專業階梯|師訓/,
  kg_admission: /幼稚園收生|幼稚園.{0,3}收生|幼稚園.{0,3}入學|幼稚園.{0,3}報名|K1.{0,3}收生|幼稚園.{0,3}申請入學|幼稚園.{0,6}學費|學費.{0,4}涵蓋|售賣物品|代辦費/,
  // S142 §5 — primary/secondary placement (after kg_admission so 幼稚園 stays there).
  placement: /中學學位分配|學位分配辦法|中一派位|中四學位|小一派位|統一派位|自行分配學位|跨境學童|學生資料管理系統|STIMS|收生實況調查/,
  conduct: /體罰|施行體罰|羞辱學生|虐待學生|教師操守|專業操守|教師專業操守/,
  // S142 §3 — student guidance/discipline/support. After conduct (操守/體罰 stays conduct),
  // before the broad production categories so welfare terms route here not finance/curriculum.
  student_support: /生涯規劃|和諧校園|欺凌|霸凌|虐待兒童|虐兒|強制舉報|危機處理|關顧學生|訓育|輔導服務|學生精神健康|學生自殺|創傷知情|哀傷輔導|學生支援組|健康校園|禁毒|藥物測試|校園測檢|免費午膳|在校午膳/,
  steam: /STEAM|STEM/,
  // S183 — value_education promoted before finance/hr_admin/curriculum (first-match
  // precedence). Original position was below gifted/kg_admin/digital_education, but
  // queries 「智啟學教 撥款」「AI 撥款」get stolen by finance (which matches 撥款).
  // value_education keywords are tight + unique (價值觀教育/首要價值觀/立根中華 etc.),
  // no risk of stealing finance/hr/sen queries. Routed early so 12 美德 list items
  // (堅毅/尊重他人/責任感/...) embedded in value-edu query reach the dedicated corpus.
  value_education: /價值觀教育|首要價值觀|價值觀架構|立根中華|聯通世界|擁抱未來|德育|公民教育|品德教育|品德及倫理|生命教育|國民身份認同|愛國主義教育|承擔精神|12.{0,3}首要|十二.{0,3}首要|VE_CF|VECF/i,
  // S194 — 公民與社會發展科. MUST stay AFTER value_education: that route owns 公民教育 /
  // 德育, and a 「公民教育」 query belongs there, not in this subject corpus. The tokens
  // here are specific to the subject (公民與社會發展 / 公社科 / 一國兩制 / 內地考察) and
  // appear on no other registry source, so nothing else is diverted. Kept before
  // curriculum so the subject corpus is not diluted by generic 課程 search.
  cgss: /公民與社會發展|公民與社會|公社科|\bCGSS\b|一國兩制|內地考察/i,
  // S183 — digital_education promoted before finance (same reason as value_education):
  // 「智啟學教 撥款」/「AI 撥款」get stolen by finance「撥款」. digital_education
  // keywords (數字教育/AI/智啟學教/etc.) are narrow + unique — finance broad queries
  // (採購/招標/報價/競投/供應商) unaffected.
  // S184 — +學校效率津貼/效率津貼/教育數字化轉型 (edbc008_2026). MUST stay before finance:
  // 「學校效率津貼」query 否則被 finance「津貼」偷; 本通告本質係數字化轉型撥款, 屬 digital_education。
  // S186 — +電子學習撥款/流動電腦裝置/上網支援 (edbcm073_2026). MUST stay before finance:
  // 「電子學習撥款」否則被 finance「撥款」偷; 本通函本質係 QEF 電子學習裝置撥款, 屬 digital_education。
  digital_education: /數字教育|數位教育|數碼教育|發展藍圖|\bDEBP\b|人工智能|\bAI\b|AI素養|人工智能素養|生成式人工智能|資訊科技教育|智啟學教|數字素養|數字技能|學校效率津貼|效率津貼|學校效率|教育數字化|數字化轉型|電子學習撥款|電子學習配套|流動電腦裝置|上網支援/i,
  // S154 — IMC/SBM school governance. MUST precede `finance` (which owns 法團校董 for g02
  // IMC-finance): a 法團校董會/校董會 query must reach the governance corpus, not finance only.
  // Governance nouns only (校董/校監/辦學團體/學校管理委員會) — pure finance queries
  // (採購/招標/報價, no 校董) don't match and still route to finance. Bare 校董 covers
  // 校董會/校董選舉/委任校董/校董責任/校董守則; 學校管理委員會 (full) avoids stealing
  // safety's 安全管理委員會.
  // S166: bilingual — real users type the English abbreviations SMC (學校管理委員會 /
  // School Management Committee) and IMC (法團校董會 / Incorporated Management Committee).
  // Chinese-only keywords missed them → "SMC 與 IMC 分別" fell through to generic semantic
  // search and surfaced curriculum junk (audit-confirmed). \b(?:IMC|SMC)\b + /i routes them
  // to the governance corpus; word-boundaries keep them from matching inside other words.
  school_governance: /法團校董會|校董會|校董|校監|辦學團體|學校管理委員會|校本條例|\b(?:IMC|SMC)\b|incorporated management committee|school management committee/i,
  // S186 — activity promoted BEFORE finance (first-match): 「家校合作活動整合津貼」/「家校合作…資助」
  // 否則被 finance「津貼」偷。activity tokens 全部 unique (全方位學習/課外活動/家校合作/家教會) —
  // 純 finance query (採購/招標/報價/撥款) 不含呢啲詞, 故 finance 路由不受影響 (S183/S184 同一 promote pattern)。
  activity: /全方位學習|活動津貼|課外活動|全方位學習津貼|戶外活動|境外遊學|遊學團|境外學習活動|參觀活動|家校合作|家庭與學校合作|家教會|家長教師會/,
  finance: /採購|招標|單一報價|競投|供應商|報價單|分判|貨物|服務合約|財務管理|預算|撥款|開支|報銷|捐款|借款|代收費|利益衝突|申報利益|賄賂|廉署|防賄|資助則例|法團校董|校董會經費|採購門檻|採購程序|多元學習津貼/,
  // S186 — hr_admin +語文能力要求/語文基準/基準試 (edbcm088_2026 LPAT) + 準英語教師獎學金 (edbcm066_2026)。
  // 必在 curriculum 之前 (first-match): 「英文科教師語文能力要求」含「英文科」會被 curriculum 偷。
  hr_admin: /假期|請假|病假|年假|婚假|侍產假|產假|特別假|補假|批假|薪酬|薪金|薪級|增薪點|津貼|教職員假|教師假|教師操守|專業操守|校曆|學年假|在職培訓日|教師註冊|註冊處|聘任|聘用|招聘|入職|教師資格|教席|常額教席|代課教師|基本法.{0,4}測試|國安法.{0,4}測試|BLNST|過剩教師|共享教職|體格檢驗|加強保障學童|遣散費|長期服務金|長服金|語文能力要求|語文基準|語文能力評核|基準試|準英語教師|英語教師獎學金/,
  // SEN — MUST stay before `curriculum` (first-match precedence): "特殊學校課程指引"
  // contains 課程 and would otherwise route to curriculum. \bsen\b/i catches the bare
  // English token (real users type "sen"); the rest catch the Chinese terminology.
  sen: /\bsen\b|\bsenco\b|特殊教育|特殊學校|融合教育|全校參與|統籌主任|特殊學習需要|有特殊教育需要/i,
  // S142 EDB-sweep §1 — school safety + governance/QA/premises. MUST stay before `curriculum`
  // (first-match): some terms (視學, 自我評估) contain chars that curriculum would mis-route.
  safety: /校園安全|學校安全|消防|火警|演習|疏散|職業安全|職安健|實驗室安全|氣體|防墮|斜坡安全|斜坡維修|熱帶氣旋|颱風|暴雨|惡劣天氣|停課安排|安全管理委員會|校車|視藝.{0,3}安全|視覺藝術.{0,4}安全|科技教育.{0,4}安全|科技科.{0,3}安全/,
  // S143 — QA/inspection split out of gov_admin (placed before it, first-match) so bare
  // short QA tokens (視學/校外評核/自我評估/表現指標/問責/校本管理) route here and get the
  // targeted expansion. Uses 自我評估 (NOT bare 評估) so it never steals curriculum
  // assessment queries; still before `curriculum` for first-match.
  qa_inspection: /視學|校外評核|學校自我評估|自我評估|表現指標|質素保證|問責架構|問責|校本管理/,
  gov_admin: /法團校董會|學校發展計劃|防貪|內部監控|籌款|校舍|大規模修葺|修葺工程|增設校舍|擴建校舍|更改校名|改校名|學校註冊/,
  // S150 — 資優教育. MUST precede `curriculum` (資優教育課程 contains 課程). Gifted-specific
  // terms; 資賦 catches 資賦優異, 資優 catches 資優教育/校本資優/資優學生.
  gifted: /資優|資賦|天才教育|拔尖保底|gifted/i,
  // S160: KG administration/operation — MUST precede curriculum (which matches bare 幼稚園).
  // S163 P2: +營運/運作/營運手冊 + 學前機構辦學手冊 health/record operation terms so the
  // natural query「幼稚園營運 手冊 健康紀錄」routes here (was falling through to curriculum →
  // g26 收生指引 only). None of these match the earlier kg_admission regex (收生/入學/學費),
  // so kg_admission queries are unaffected.
  kg_admin: /幼稚園行政|幼稚園.{0,4}行政|辦學手冊|營運手冊|學前機構|幼稚園.{0,4}辦學|幼稚園.{0,4}營辦|幼稚園.{0,4}營運|幼稚園.{0,4}運作|開辦幼稚園|幼稚園牌照|幼稚園.{0,4}人事|幼稚園.{0,4}財務|幼稚園.{0,4}管理|幼稚園.{0,4}質素|幼稚園.{0,4}健康紀錄|幼稚園.{0,4}健康記錄|幼稚園教育計劃|幼教計劃|免費優質幼稚園|幼稚園.{0,4}周年/,
  curriculum: /課程|科目|教學|學習目標|評估|教材|課程發展|學習領域|教師發展|CPD|專業發展|英文科|中文科|數學科|數學建模|常識科|科學科|體育科|音樂科|視藝科|小學課程|中學課程|課程指引|學習成果|評核|幼稚園|幼兒|學前|K1|K2|K3|遊戲學習/,
};

/**
 * Detect query category from keywords.
 * Returns the category key (matching SOURCE_SETS) or null if none detected.
 * Finance takes precedence over HR to avoid overlap (e.g. "薪酬採購").
 */
export function detectQueryCategory(query: string): string | null {
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
  kg_admin:     "幼稚園行政手冊 學前機構辦學手冊 幼稚園營辦 幼稚園管理 幼稚園人事 幼稚園財務 幼稚園牌照 幼稚園註冊 質素保證 幼稚園教育計劃 免費優質幼稚園教育計劃 周年計劃 校本管理 學前機構",
  conduct:      "教師專業操守指引 教育規例第58條 教員不得向學生施行體罰 操守 學生保護",
  sen:          "特殊教育需要 融合教育 全校參與模式 特殊學校課程指引 融合教育運作指南 特殊教育需要統籌主任 SENCO 學生支援組 個別學習計劃 三層支援模式 校本支援 共融校園 照顧學生個別差異 校內考試特別安排 考試調適 評估調適 特別考試安排",
  gifted:       "資優教育 資賦優異 三層推行模式 校本資優培育課程 拔尖保底 多元智能 資優學生 抽離式課程 校本資優發展計劃",
  steam:        "STEAM教育 跨學科 課程更新重點 七大重點 STEAM專責小組 科學科技工程藝術數學",
  // S166: bridge English abbreviations to the Chinese governance corpus so an
  // abbreviation-heavy query ("SMC 與 IMC 分別") embeds near 法團校董會/校董會 chunks.
  // SOURCE_SET is cohesively governance (imc_*/g02/coa_imc/sdp_guide) → no dilution
  // (same rationale as the qa_inspection expansion exception).
  school_governance: "法團校董會 學校管理委員會 校董會 校董 校監 辦學團體 校本管理 法團校董會的成立與運作 Incorporated Management Committee School Management Committee",
  finance:    "採購程序 財政限額 報價 招標 採購指引",
  hr_admin:   "教職員假期 批假 薪酬 操守 病假 首年 168日 上限 醫生證明 教師註冊 聘任",
  activity:   "全方位學習津貼 活動",
  // S142: safety + gov_admin intentionally have NO expansion. Their SOURCE_SETS span
  // diverse doc types (fire/cyclone/lab/slope; premises/registration); a single
  // expansion string would dilute focused queries toward the highest-chunk-count doc
  // (over-expansion regression caught in S142 smoke: cyclone drowned 消防; edbc14 drowned g04).
  // SOURCE_SET filter + the query's own terms surface the right doc without dilution.
  // S143 EXCEPTION — qa_inspection DOES expand: its SOURCE_SET is tight (3 QA docs + SAG)
  // and single-topic, so bridging 視學→校外評核/自我評估/表現指標 vocabulary lifts recall
  // without the cross-topic dilution that broad gov_admin/safety expansion would cause.
  qa_inspection: "校外評核 學校自我評估 表現指標 質素保證 問責架構 校本管理 學校發展",
  digital_education: "中小學數字教育發展藍圖 人工智能素養 AI素養學習架構 在教學上運用人工智能 生成式人工智能 數字素養 數字教育 資訊科技教育 電子學習 智啟學教 AI賦能教育 50萬撥款 數字教育策略發展督導委員會 學與教效能 學校效率津貼 效率津貼 教育數字化轉型 提升學校效率 智慧校園 行政效率 整合代課教師津貼",
  // S183 — value_education expansion (same §EXCEPTION rationale as qa_inspection):
  // SOURCE_SET tight (5 sources, all cohesively value-education) so bridging
  // 價值觀→12 首要價值觀/立根中華/德育/公民教育/品德 lifts recall without
  // cross-topic dilution. Includes framework slogans + 12 美德 list items.
  value_education: "價值觀教育課程架構 首要價值觀 12 首要價值觀 立根中華 聯通世界 擁抱未來 德育及公民教育 品德教育 生命教育 國民教育 國家安全教育 中華文化 堅毅 尊重他人 責任感 國民身份認同 承擔精神 誠信 仁愛 守法 同理心 勤勞 孝親 團結 全人發展 個人成長",
  curriculum: "課程指引 教學 學習目標",
  // S194 — cgss expansion (same §EXCEPTION rationale as qa_inspection/value_education:
  // a tight, single-subject SOURCE_SET, so bridging the subject's own vocabulary lifts
  // recall without cross-topic dilution). Measured need: 「一國兩制 課程」 only reaches
  // 0.484 against this corpus, which loses the global window unaided.
  cgss: "公民與社會發展科 課程及評估指引 一國兩制 下的香港 改革開放以來的國家 互聯相依的當代世界 內地考察 專題研習 香港特別行政區 國家安全 當代世界 公民身份",
};

function expandQuery(query: string, category: string): string {
  const expansion = QUERY_EXPANSIONS[category];
  return expansion ? `${query} ${expansion}` : query;
}

// ---------------------------------------------------------------------------
// Synthesis
// ---------------------------------------------------------------------------

const SYNTHESIS_PROMPT = `你是香港學校管治的政策顧問。以下是從教育局政策文件中檢索到的相關資料。
請根據這些資料，用繁體中文綜合分析並回答問題，緊扣資料重點，約250字（上限300字），不需列出來源編號。

問題：{QUERY}

政策資料：
{CHUNKS}`;

// S177 — relevance judge (anti-confabulation gate). A cheap binary check BEFORE synthesis:
// only synthesize when the retrieved chunks actually contain the answer; otherwise decline
// rather than fabricating from topically-near-but-wrong chunks (the 凍結教席→IMC-60% class).
// Conservative by design (寧緊莫鬆): any uncertainty → 否 → decline. A small model judges a
// binary far more reliably than it can judge-and-answer in one shot (verified: a one-shot
// anti-confab prompt over-refuses on-topic queries; a standalone binary judge scores 5/5).
const RELEVANCE_JUDGE_PROMPT = `以下是從教育局文件檢索到的資料。請判斷這些資料能否「明確、直接」回答用戶的問題。

從嚴判斷（寧緊莫鬆）：只有當資料實際、明確包含問題所問的「具體答案」（所問的數字／上限／比例／條件／規則本身）時，才答「能」。若資料只是同一大主題但其實在講另一件事、或資料未必直接答到所問事項、或你有任何不確定，一律答「否」。寧可答否，也不要勉強當作能——答錯一個數字會誤導用戶，比答找不到更差。

只回答一個字：能 或 否。

問題：{QUERY}

資料：
{CHUNKS}`;

const SYNTHESIS_DECLINE =
  "根據檢索到的教育局文件，暫時未能找到可直接回答此問題的明確資料。下方為主題相關的原始文件，或可參考；亦可嘗試以其他關鍵詞重新搜尋。";

/** S177 — conservative binary relevance gate. Returns true only when the judge is confident
 *  the chunks directly answer the query (寧緊莫鬆: 不肯定 → 否 → decline). On a judge技術性
 *  失敗 (API error) it returns true (answer anyway) so a judge outage never silences all
 *  search — the conservatism is about the judge's verdict, not its availability. */
async function judgeCanAnswer(query: string, chunkText: string, llmFn: LlmFn): Promise<boolean> {
  const prompt = RELEVANCE_JUDGE_PROMPT
    .replace("{QUERY}", query)
    .replace("{CHUNKS}", chunkText);
  try {
    const verdict = (await llmFn(prompt)).trim();
    return verdict.startsWith("能"); // anything else (否 / noise) → decline
  } catch {
    return true; // judge failed technically → fall back to answering, not refusing
  }
}

async function synthesizeAnswer(query: string, results: ChannelBResult[], llmFn: LlmFn): Promise<string> {
  const top5 = results.slice(0, 5);
  if (top5.length === 0) return "找不到相關政策。";

  const chunkText = top5
    .map((r, i) => `[${i + 1}] ${r.text}`)
    .join("\n\n");

  // S177 — anti-confabulation gate: decline rather than fabricate when chunks don't answer.
  // S178 — EXCEPTION: footnote_curated lead scoring ≥ FOOTNOTE_LEAD_SCORE bypasses judge
  // (hand-curated verbatim-verified direct answer by construction, not confab risk).
  // S183 — EXTENDED: vault_extract lead scoring ≥ VAULT_LEAD_SCORE (0.70) also bypasses
  // judge. Confabulation the judge guards against (S177 凍結教席→IMC-60% class) occurs
  // at lower cosine 0.50-0.65 (topically-near-but-wrong); ≥0.70 is empirically direct
  // topical match. Verified live: 「智啟學教是什麼」EDBCM 221 chunk rank-0 score 0.750
  // and 「價值觀教育」VE_CF 2021 chunk rank-0 score 0.794 were over-declined by judge
  // despite being perfect topical matches. Below-0.70 vault chunks still go through
  // the judge unchanged (full confab protection retained for marginal cosine cases).
  const lead = top5[0];
  const trustedFootnoteLead =
    lead.content_type === "footnote_curated" && lead.score >= FOOTNOTE_LEAD_SCORE;
  const trustedVaultLead =
    lead.content_type === "vault_extract" && lead.score >= VAULT_LEAD_SCORE;
  if (!trustedFootnoteLead && !trustedVaultLead) {
    const canAnswer = await judgeCanAnswer(query, chunkText, llmFn);
    if (!canAnswer) return SYNTHESIS_DECLINE;
  }

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

/**
 * S174 — Route-independent footnote pass.
 * Curated 附件細字 footnote chunks (content_type="footnote_curated") are attached to
 * their source document's source_id, but adversarial/oblique queries often route to a
 * category whose SOURCE_SET excludes that source — so the footnote, though fetched
 * globally by the RPC, is discarded by the source-set post-filter (wikiRepository
 * sourceIds gate). Fix: run a second searchWiki restricted to footnote_curated (NO
 * source filter) on its own over-fetch budget, then merge by score. Additive +
 * best-effort (never fails the main search). FOOTNOTE_MIN_SCORE gates off-topic noise;
 * the final score-sort + top_k slice decides whether a footnote actually surfaces.
 */
const FOOTNOTE_MIN_SCORE = 0.42;
/**
 * A footnote scoring ≥ this against the raw query is a precise curated answer — give it a
 * guaranteed lead slot so it reaches the synthesis window (top-5) even when (mis-)routed
 * main-search results outscore it. Footnotes between MIN and LEAD just merge by score.
 */
const FOOTNOTE_LEAD_SCORE = 0.45;
// S183 — vault_extract lead bypass threshold for judge. ≥0.70 = empirically direct
// topical match (vault chunks at this cosine reliably answer the query). Below 0.70
// falls through to judge for confab protection (S177 凍結教席→IMC-60% range was 0.55-0.65).
const VAULT_LEAD_SCORE = 0.70;

// S183 — supersede ranking penalty (governance rule, not source-specific). When a
// new version of a document is ingested and the old version is marked superseded_by,
// the old chunks score is reduced by SUPERSEDE_PENALTY so the new version ranks
// above the old in cosine search. Per Leonard 嘅 retain-but-rank-down 策略:
// superseded sources stay in store (學校過渡期仍可能引用 old version), but new
// version surfaces first when both are topically relevant.
//
// SOURCE-OF-TRUTH for SUPERSEDED_IDS = dev/source/source_registry.json `superseded_by`
// field. When ingesting a new superseding version, add the old source_id here (same
// pattern as SOURCE_SETS — manual sync at ingest time). Penalty 0.05 chosen empirically:
// VE_CF 2021 trial cos≈0.794, VE_CF 2026 new≈0.753 (差 0.041); penalty 0.05 swaps
// the ranking (2021 → 0.744 < 2026), surfacing the official 2026 version first.
const SUPERSEDE_PENALTY = 0.05;
const SUPERSEDED_IDS = new Set<string>([
  // S183 — value_education framework 2026 supersedes:
  "values_edu_framework_2021_trial",
  "edbcm183_2023_values_edu",
  // S194 — the real ICT 2021 C&A guide is now in the corpus (116 chunks), so the 2007/2015
  // edition it replaces takes the penalty. registry `ict_sss_2007_2015.superseded_by` is the
  // SSOT and was set in the same session. Note this rule could not be applied before now:
  // `ict_sss_2021` previously held the 公社科 guide, so there was no 2021 ICT edition to
  // supersede anything.
  "ict_sss_2007_2015",
]);

/**
 * S193 — SPOTLIGHT: sources the global ANN pass cannot reach yet.
 *
 * Failure mode this fixes (found S193 by live-probing the 4 sources the Option A pipeline
 * ingested unattended after S192): `searchWiki` asks Supabase for the global top-(top_k*5)
 * chunks above the threshold and applies the route's SOURCE_SET filter afterwards, in JS.
 * A newly ingested source with 3–14 chunks therefore has to out-rank ~16k chunks GLOBALLY
 * just to enter the over-fetch window — so neither adding it to a SOURCE_SET nor adding
 * TOPIC_KEYWORDS can make it findable. Measured live: edbcm094_2026 scores 0.722 against
 * its own title yet never appeared in top-8; edbcm113_2026 0.621; edbcm066_2026 0.696.
 *
 * Fix = the S174 footnote-overlay shape: exact cosine over this small set (route-independent,
 * ANN-independent), and if the source is not already visible, give its best chunk one lead
 * slot. SPOTLIGHT_LEAD_SCORE is set from measurement, not taste: on-topic direct matches
 * land 0.62–0.72, while 20 adversarial off-topic probes (法團校董會 / 採購招標 / 校車安全 /
 * 病假頂替 / 學校效率津貼 …) peak at 0.563 — so 0.60 admits the true matches and 0/20 of
 * the adversarial ones. Weak-but-real matches below 0.60 are deliberately NOT forced in:
 * at that cosine they are indistinguishable from off-topic neighbours.
 *
 * Lifecycle: the Option A executor appends each newly ingested source here automatically
 * (see dev/source/execute_ingest.py step 4b — keep the ack:spotlight markers, they are the
 * machine insertion point). An id can be pruned once the source is confirmed to surface
 * through the normal ANN path; leaving it costs one cosine per chunk per query.
 */
const SPOTLIGHT_LEAD_SCORE = 0.6;
/** One forced slot only — enough to turn "invisible" into "visible", while leaving 7 of 8
 *  slots organic (footnote leads may already hold up to 2). */
const SPOTLIGHT_MAX_LEADS = 1;
const SPOTLIGHT_SOURCE_IDS: string[] = [
  // ack:spotlight:start
  "edbcm113_2026", // S193: 小學資訊與創新科技課程框架「人工智能初探」(3 chunks, ANN-starved in digital_education)
  "edbcm094_2026", // S193: 2026/27 資助學校教職員薪酬調整 (7 chunks, crowded out by sag_2025_11)
  "edbcm073_2026", // S193: QEF 電子學習撥款 (12 chunks, S186 monitor — crowded out by DEBP corpus)
  "edbcm066_2026", // S193: 準英語教師獎學金 (14 chunks, S186 monitor — crowded out by sag/g04)
  "iit_ai_framework_2026", // S194: 人工智能初探範疇正文 (18 chunks, measured 0.628-0.676 on its own topics)
  "edbc013_2026",  // S194: 非本地兒童入學 (9 chunks; the eval harness caught it missing, measured 0.619)
  // ack:spotlight:end
];

/** S183 — Apply supersede penalty to results in place. Caller is responsible for
 *  re-sorting after (e.g. before any lead-detection or top_k slice). Idempotency
 *  note: only call once per result object (apply at chunk-mapping boundary, not
 *  in re-sort loops). */
function applySupersedePenalty<T extends { source_id: string; score: number }>(results: T[]): T[] {
  for (const r of results) {
    if (SUPERSEDED_IDS.has(r.source_id)) {
      r.score = r.score - SUPERSEDE_PENALTY;
    }
  }
  return results;
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

  // S183 — Apply supersede penalty + re-sort. Old-version chunks (registered in
  // SUPERSEDED_IDS) get score reduced so the new version ranks first when both
  // are topically relevant. Run after mapping, before any lead detection.
  applySupersedePenalty(results);
  results.sort((a, b) => b.score - a.score);

  // S193 — one raw-query embedding shared by both route-independent overlay passes below.
  // Net embedding calls are unchanged: the footnote pass used to compute this itself.
  let rawVec: number[] | undefined;
  try {
    rawVec = await embedFn(query);
  } catch {
    rawVec = undefined; // each overlay falls back to embedding on its own
  }

  // Slots reserved at the front of `results` by an overlay lead, so a later overlay
  // inserts behind them instead of displacing them.
  let forcedLeads = 0;

  // S174 — route-independent footnote pass (see FOOTNOTE_MIN_SCORE above). Exact cosine
  // over the curated footnote overlay (bypasses routing AND ivfflat recall). Uses the RAW
  // query (footnote chunks are not category-tuned). Best-effort: never fails search.
  try {
    const fnRaw = await searchFootnotes(query, embedFn, FOOTNOTE_MIN_SCORE, 6, rawVec);
    if (fnRaw.length > 0) {
      const fnResults = fnRaw.map(toChannelBResult);
      // S183 — apply supersede penalty to footnote results too (footnote overlay is
      // independent retrieve path, needs the same governance rule).
      applySupersedePenalty(fnResults);
      // Strong footnote matches lead (guaranteed synthesis-window slot); weaker ones
      // merge by score. Dedup by id; main results keep score order behind the lead.
      const lead = fnResults.filter((r) => r.score >= FOOTNOTE_LEAD_SCORE).slice(0, 2);
      const seen = new Set(lead.map((r) => r.id));
      const rest: ChannelBResult[] = [];
      for (const r of [...results, ...fnResults]) {
        if (seen.has(r.id)) continue;
        seen.add(r.id);
        rest.push(r);
      }
      rest.sort((a, b) => b.score - a.score);
      results = [...lead, ...rest];
      forcedLeads = lead.length;
    }
  } catch {
    // a footnote-pass failure must never break the main search
  }

  // S193 — spotlight pass (see SPOTLIGHT_SOURCE_IDS above). Exact cosine over the small set
  // of recently ingested sources the global ANN over-fetch cannot reach. Only fires when the
  // source is not already visible in `results`, and only at ≥ SPOTLIGHT_LEAD_SCORE — so it
  // adds reachability without adding mid-pack noise. Best-effort: never fails search.
  try {
    const spotRaw = await searchSpotlightSources(
      query,
      embedFn,
      SPOTLIGHT_SOURCE_IDS,
      SPOTLIGHT_LEAD_SCORE,
      SPOTLIGHT_MAX_LEADS + 1,
      rawVec
    );
    if (spotRaw.length > 0) {
      const spot = spotRaw.map(toChannelBResult);
      applySupersedePenalty(spot);
      spot.sort((a, b) => b.score - a.score);
      const visibleSources = new Set(results.map((r) => r.source_id));
      const seenIds = new Set(results.map((r) => r.id));
      const spotLead = spot
        .filter(
          (r) =>
            !visibleSources.has(r.source_id) &&
            !seenIds.has(r.id) &&
            r.score >= SPOTLIGHT_LEAD_SCORE
        )
        .slice(0, SPOTLIGHT_MAX_LEADS);
      if (spotLead.length > 0) {
        results = [
          ...results.slice(0, forcedLeads),
          ...spotLead,
          ...results.slice(forcedLeads),
        ];
        forcedLeads += spotLead.length;
      }
    }
  } catch {
    // a spotlight-pass failure must never break the main search
  }

  // Filter out statistical facts unless explicitly requested:
  //   - content_type "stat_fact" (auto-approved stats)
  //   - source_id starting with "stat_" (vault extracts from statistical sources)
  if (!include_statistical) {
    results = results.filter(r =>
      r.content_type !== "stat_fact" && !r.source_id.startsWith("stat_")
    );
  }

  // Apply top_k. The S174 footnote-pass merge already ordered results (strong footnotes
  // lead, remaining results by score); don't re-sort or the lead slot would be undone.
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
