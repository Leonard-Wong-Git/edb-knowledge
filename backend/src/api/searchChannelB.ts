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
    // S142 EDB-sweep §1 — staffing/appointment/BLNST policy
    "edbc13_2022_blnst", "edbcm141_2025_blnst", "blnst_test_notes_nondeg", "blnst_test_candidate_notes",
    "embc5_2005_appointment", "edbc14_2023_student_protect", "staff_medical_health",
    "job_sharing_guide", "surplus_teacher_arr_2026", "private_sch_employment_notes",
    "supply_teacher_guide", "long_service_payment_guide",  // S142 §2: 代課教師指引 + 遣散費長服金指引
    "sch_calendar_guide",   // S152: 學校曆/一般假期/上課日數計算 (校曆 keyword already routes here), Discovery
    "role_facts_hr",
    "role_facts_general",
  ],

  /**
   * Activity grants — 全方位學習津貼, 課外活動
   */
  activity: [
    "g03",               // 全方位學習津貼運用指引
    "sch_activities_guide",   // S152: 戶外活動 + 境外遊學團指引 (Discovery)
    "role_facts_activity",
    "role_facts_general",
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
  student_support: /生涯規劃|和諧校園|欺凌|霸凌|虐待兒童|虐兒|強制舉報|危機處理|關顧學生|訓育|輔導服務|學生精神健康|學生自殺|創傷知情|哀傷輔導|學生支援組|健康校園|禁毒|藥物測試|校園測檢/,
  steam: /STEAM|STEM/,
  // S154 — IMC/SBM school governance. MUST precede `finance` (which owns 法團校董 for g02
  // IMC-finance): a 法團校董會/校董會 query must reach the governance corpus, not finance only.
  // Governance nouns only (校董/校監/辦學團體/學校管理委員會) — pure finance queries
  // (採購/招標/報價, no 校董) don't match and still route to finance. Bare 校董 covers
  // 校董會/校董選舉/委任校董/校董責任/校董守則; 學校管理委員會 (full) avoids stealing
  // safety's 安全管理委員會.
  school_governance: /法團校董會|校董會|校董|校監|辦學團體|學校管理委員會|校本條例/,
  finance: /採購|招標|單一報價|競投|供應商|報價單|分判|貨物|服務合約|財務管理|預算|撥款|開支|報銷|捐款|借款|代收費|利益衝突|申報利益|賄賂|廉署|防賄|資助則例|法團校董|校董會經費|採購門檻|採購程序/,
  hr_admin: /假期|請假|病假|年假|婚假|侍產假|產假|特別假|補假|批假|薪酬|薪金|薪級|增薪點|津貼|教職員假|教師假|教師操守|專業操守|校曆|學年假|在職培訓日|教師註冊|註冊處|聘任|聘用|招聘|入職|教師資格|教席|常額教席|代課教師|基本法.{0,4}測試|國安法.{0,4}測試|BLNST|過剩教師|共享教職|體格檢驗|加強保障學童|遣散費|長期服務金|長服金/,
  activity: /全方位學習|活動津貼|課外活動|全方位學習津貼|戶外活動|境外遊學|遊學團|境外學習活動|參觀活動/,
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
  kg_admin: /幼稚園行政|幼稚園.{0,4}行政|辦學手冊|學前機構|幼稚園.{0,4}辦學|幼稚園.{0,4}營辦|開辦幼稚園|幼稚園牌照|幼稚園.{0,4}人事|幼稚園.{0,4}財務|幼稚園.{0,4}管理|幼稚園.{0,4}質素|幼稚園教育計劃|幼教計劃|免費優質幼稚園|幼稚園.{0,4}周年/,
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
  kg_admin:     "幼稚園行政手冊 學前機構辦學手冊 幼稚園營辦 幼稚園管理 幼稚園人事 幼稚園財務 幼稚園牌照 幼稚園註冊 質素保證 幼稚園教育計劃 免費優質幼稚園教育計劃 周年計劃 校本管理 學前機構",
  conduct:      "教師專業操守指引 教育規例第58條 教員不得向學生施行體罰 操守 學生保護",
  sen:          "特殊教育需要 融合教育 全校參與模式 特殊學校課程指引 融合教育運作指南 特殊教育需要統籌主任 SENCO 學生支援組 個別學習計劃 三層支援模式 校本支援 共融校園 照顧學生個別差異 校內考試特別安排 考試調適 評估調適 特別考試安排",
  gifted:       "資優教育 資賦優異 三層推行模式 校本資優培育課程 拔尖保底 多元智能 資優學生 抽離式課程 校本資優發展計劃",
  steam:        "STEAM教育 跨學科 課程更新重點 七大重點 STEAM專責小組 科學科技工程藝術數學",
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
請根據這些資料，用繁體中文綜合分析並回答問題，緊扣資料重點，約250字（上限300字），不需列出來源編號。

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
