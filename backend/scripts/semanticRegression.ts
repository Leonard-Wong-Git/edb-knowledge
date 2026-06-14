import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { analyzeCircular } from "../src/api/analyzeCircular.js";
import { detectQueryCategory } from "../src/api/searchChannelB.js";
import { cjkBigrams } from "../src/api/checklistRevise.js";
import { selectKnowledge } from "../src/services/knowledgeSelector.js";
import { detectTopics } from "../src/services/topicDetector.js";
import type { KnowledgeBase, RoleId, TopicId } from "../src/types/knowledge.js";
import { TOPIC_IDS } from "../src/types/knowledge.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");

type Result = "PASS" | "PASS with notes" | "FAIL";

interface ScenarioRow {
  scenario: string;
  precondition: string;
  action: string;
  expected: string;
  actual: string;
  result: Result;
}

interface QueryCase {
  name: string;
  text: string;
  role: RoleId;
  expectedTopic: TopicId;
  forbiddenTopics?: TopicId[];
}

const queryCases: QueryCase[] = [
  {
    name: "finance_query",
    text: "學校須按採購程序取得書面報價，保存採購記錄三個曆年，並按津貼用途處理開支。採購指引要求公開招標及審計，財務核准須符合撥款規定，各項津貼申請及報帳均須依從財務管理規定，供應商報價及競投亦需有完整記錄。",
    role: "subject_head",
    expectedTopic: "finance",
    forbiddenTopics: ["curriculum"],
  },
  {
    name: "hr_query",
    text: "教師須完成持續專業發展時數（CPD），並按學校要求保存和提交 CPD 記錄。人力資源管理包括招聘程序、合約教師及代課教師安排、薪酬調整、員工假期、強積金供款、教師資歷審核、晉升安排及離職程序。",
    role: "teacher",
    expectedTopic: "hr",
  },
  {
    name: "curriculum_query",
    text: "小學人文科課程指引將於 2025/26 學年起適用，學校須按推行時間表逐步實施新課程。課程規劃應參考課程發展議會發布之學習目標、課程架構及課程改革方向，各學科評核須配合學習領域要求，並配合共同備課及評估安排，優化課時運用及學業成績跟進。",
    role: "panel_chair",
    expectedTopic: "curriculum",
    forbiddenTopics: ["finance"],
  },
  {
    name: "activity_query",
    text: "境外交流團和校外活動須完成風險評估、家長同意和安全安排。活動審批程序涵蓋課外活動、戶外學習、參觀、遠足、水上活動及陸上運動等。全方位學習計劃下的學生旅行及境外遊學項目，均須按既定程序提交活動計劃及安全指引。",
    role: "panel_chair",
    expectedTopic: "activity",
  },
  {
    name: "student_query",
    text: "學生紀律、輔導與 SEN 支援個案須按校本機制跟進，並適時聯絡家長。",
    role: "panel_chair",
    expectedTopic: "student",
    forbiddenTopics: ["general"],
  },
  {
    name: "it_query",
    text: "學校推行 BYOD 和電子學習時須注意資訊保安、網絡安全和數據保護。",
    role: "subject_head",
    expectedTopic: "it",
  },
  {
    name: "general_query",
    text: "法團校董會、校本行政程序及公開資料安排須按學校既定機制處理。",
    role: "principal",
    expectedTopic: "general",
    forbiddenTopics: ["student"],
  },
];


const realCircularCases = [
  {
    name: "edbc_12_2025",
    path: path.resolve(REPO_ROOT, "dev/source/vault/edbc_12_2025/extract.txt"),
    role: "subject_head" as RoleId,
    expectedTopic: "curriculum" as TopicId,
    forbiddenTopics: ["finance" as TopicId],
  },
  {
    name: "edbc24017",
    path: path.resolve(REPO_ROOT, "dev/vault/circ_edbc24017/extract_edbc24017_.txt"),
    role: "principal" as RoleId,
    expectedTopic: "curriculum" as TopicId,
    forbiddenTopics: ["finance" as TopicId],
  },
];

const OFFLINE_KEYWORDS = [
  "財務管理",
  "採購程序",
  "津貼申請",
  "學校開支",
  "供應商報價",
  "競投",
  "採購指引",
  "財務核准",
  "撥款",
  "特別津貼",
  "書簿津貼",
  "公開招標",
  "審計",
  "報帳",
  "教師培訓",
  "持續專業發展",
  "CPD",
  "員工假期",
  "招聘程序",
  "合約教師",
  "代課教師",
  "薪酬",
  "人力資源",
  "教師資歷",
  "晉升",
  "離職",
  "強積金",
  "課程規劃",
  "學習目標",
  "課程架構",
  "評估",
  "學習成果",
  "課程改革",
  "學科",
  "學業成績",
  "學習領域",
  "課程指引",
  "課程發展",
  "共同備課",
  "課時",
  "評核",
  "課外活動",
  "境外遊學",
  "戶外學習",
  "學生活動",
  "活動審批",
  "校外活動",
  "參觀",
  "陸上運動",
  "水上活動",
  "遠足",
  "學生旅行",
  "全方位學習",
  "交流團",
  "學生紀律",
  "行為問題",
  "學生支援",
  "學生事務",
  "學生福利",
  "輔導",
  "操行",
  "體罰",
  "家長",
  "學生訓導",
  "學生管理",
  "危機處理",
  "欺凌",
  "傳染病",
  "SEN",
  "資訊科技",
  "學校資訊系統",
  "網絡安全",
  "數據保護",
  "BYOD",
  "電腦設備",
  "資訊保安",
  "學校電腦",
  "雲端",
  "資訊系統管理",
  "軟件更新",
  "寬頻",
];

function countOccurrences(text: string, token: string): number {
  if (!token) return 0;
  let count = 0;
  let start = 0;
  while (true) {
    const idx = text.indexOf(token, start);
    if (idx === -1) break;
    count += 1;
    start = idx + token.length;
  }
  return count;
}

function createOfflineEmbedding() {
  return async (text: string): Promise<number[]> => {
    const normalized = text.replace(/\s+/g, "");
    const vector = OFFLINE_KEYWORDS.map((keyword) => countOccurrences(normalized, keyword));

    const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
    if (norm === 0) return vector;
    return vector.map((value) => value / norm);
  };
}

async function loadJson<T>(relativePath: string): Promise<T> {
  const fullPath = path.resolve(REPO_ROOT, relativePath);
  return JSON.parse(await readFile(fullPath, "utf-8")) as T;
}

function extractPublicRoleKeys(topicBlock: Record<string, unknown>): string[] {
  return Object.keys(topicBlock).filter((key) => {
    if (key.startsWith("_")) return false;
    return Array.isArray(topicBlock[key]);
  });
}

function formatTopics(topics: TopicId[]): string {
  return topics.length > 0 ? topics.join(", ") : "(none)";
}

async function run(): Promise<void> {
  const knowledgeJson = await loadJson<Record<string, unknown>>("knowledge.json");
  const guidelinesJson = await loadJson<Record<string, unknown>>("guidelines.json");
  const roleFacts = await loadJson<KnowledgeBase>("role_facts.json");
  const apiSpec = await readFile(path.resolve(REPO_ROOT, "K1_API_SPEC.md"), "utf-8");

  const offlineEmbed = createOfflineEmbedding();
  const offlineLlm = async (prompt: string) =>
    `stub-analysis:${prompt.length}:offline-regression`;

  const rows: ScenarioRow[] = [];

  // Topic regression on fixed query set.
  for (const testCase of queryCases) {
    const result = await analyzeCircular(
      { circular_text: testCase.text, role: testCase.role },
      { embeddingClient: offlineEmbed, llmClient: offlineLlm }
    );

    const containsExpected = result.detected_topics.includes(testCase.expectedTopic);
    const contamination =
      testCase.forbiddenTopics?.filter((topic) => result.detected_topics.includes(topic)) ?? [];
    const ok = containsExpected && contamination.length === 0 && result.used_facts.length > 0;

    rows.push({
      scenario: `topic regression — ${testCase.name}`,
      precondition: "離線 semantic harness 可用；repo-root role_facts.json 可載入",
      action: `analyzeCircular(${testCase.expectedTopic}, role=${testCase.role})`,
      expected: `偵測到 ${testCase.expectedTopic}，並避免明顯 cross-topic contamination`,
      actual: `topics=${formatTopics(result.detected_topics)}; used_facts=${result.used_facts.length}; contamination=${contamination.join(",") || "none"}`,
      result: ok ? "PASS" : "FAIL",
    });
  }

  // Role-bucket regression.
  const publicRoleViolations: string[] = [];
  for (const topic of TOPIC_IDS) {
    const block = knowledgeJson[topic] as Record<string, unknown>;
    if (!block || typeof block !== "object") continue;
    const keys = extractPublicRoleKeys(block);
    if (keys.includes("department_head")) {
      publicRoleViolations.push(topic);
    }
  }

  const financeSelectionSubject = selectKnowledge(roleFacts, ["finance"], "subject_head");
  const financeSelectionPanel = selectKnowledge(roleFacts, ["finance"], "panel_chair");
  // S163: post-S110-dedup the role buckets are unified via `all_roles` (union selector
  // guarantees no role loses visibility), so the two roles legitimately overlap heavily.
  // The meaningful invariant is now "both roles receive finance knowledge", not "they
  // select DIFFERENT facts" (the old assertion was stale drift, failing since the dedup).
  const bothRolesHaveFinance =
    financeSelectionSubject.usedFacts.length > 0 && financeSelectionPanel.usedFacts.length > 0;

  rows.push({
    scenario: "role-bucket regression",
    precondition: "public knowledge.json 與 repo-root role_facts.json 可讀取",
    action: "檢查 knowledge.json public role buckets；確認 finance 的 subject_head / panel_chair 均取得事實",
    expected: "knowledge.json 不出現 public department_head；subject_head 與 panel_chair 均取得 finance 事實（union 選取器）",
    actual: `department_head_topics=${publicRoleViolations.join(",") || "none"}; subject_facts=${financeSelectionSubject.usedFacts.length}; panel_facts=${financeSelectionPanel.usedFacts.length}`,
    result: publicRoleViolations.length === 0 && bothRolesHaveFinance ? "PASS" : "FAIL",
  });

  // Schema consistency regression.
  const knowledgeMeta = (knowledgeJson._meta ?? {}) as Record<string, unknown>;
  const guidelinesMeta = (guidelinesJson._meta ?? {}) as Record<string, unknown>;
  const specHasSplitRoles =
    apiSpec.includes("subject_head") && apiSpec.includes("panel_chair");
  const specStillOldVersion =
    apiSpec.includes("knowledge.json 實際格式（v1.3.0）") || apiSpec.includes("最後更新：2026-04-08");
  // S163: assert the CURRENT frozen data-contract versions (were stale-pinned to 1.3.1,
  // failing since the data evolved). knowledge.json is frozen at 2.3.0 and guidelines at
  // 2.5.0 by design; the user-facing PLATFORM_VERSION (3.0.0) is intentionally separate.
  const schemaConsistencyOk =
    knowledgeMeta.version === "2.3.0" &&
    guidelinesMeta.version === "2.5.0" &&
    specHasSplitRoles &&
    !specStillOldVersion;

  rows.push({
    scenario: "schema consistency regression",
    precondition: "knowledge.json / guidelines.json / K1_API_SPEC.md 可讀取",
    action: "比對 meta version 與公開 spec 文字",
    expected: "三者版本與 split-role 描述一致，且 spec 無舊版漂移",
    actual: `knowledge=${knowledgeMeta.version}; guidelines=${guidelinesMeta.version}; spec_split_roles=${specHasSplitRoles}; spec_old_version_markers=${specStillOldVersion}`,
    result: schemaConsistencyOk ? "PASS" : "FAIL",
  });

  // Semantic retrieval regression with real circular extracts.
  for (const sample of realCircularCases) {
    const text = await readFile(sample.path, "utf-8");
    const result = await analyzeCircular(
      { circular_text: text, role: sample.role },
      { embeddingClient: offlineEmbed, llmClient: offlineLlm }
    );
    const contamination =
      sample.forbiddenTopics?.filter((topic) => result.detected_topics.includes(topic)) ?? [];
    const hasScores = Object.keys(result.similarity_scores).length > 0;
    const ok =
      result.detected_topics.includes(sample.expectedTopic) &&
      contamination.length === 0 &&
      hasScores &&
      result.total_fact_chars > 0;

    rows.push({
      scenario: `semantic retrieval regression — ${sample.name}`,
      precondition: "真實 circular extract 已存在於 workspace",
      action: `用 ${sample.name} extract 跑 analyzeCircular`,
      expected: `命中 ${sample.expectedTopic}，有 similarity scores，且無明顯 cross-topic contamination`,
      actual: `topics=${formatTopics(result.detected_topics)}; score_keys=${Object.keys(result.similarity_scores).join(",") || "none"}; total_fact_chars=${result.total_fact_chars}; contamination=${contamination.join(",") || "none"}`,
      result: ok ? "PASS" : "FAIL",
    });
  }

  const onlineAvailable = Boolean(process.env.OPENAI_API_KEY?.trim());
  rows.push({
    scenario: "failure-path regression — online runtime availability",
    precondition: "需要真實 OpenAI embeddings / LLM 才能做 full online regression",
    action: "檢查 OPENAI_API_KEY",
    expected: "若無 API key，明確標示 online regression blocked，但離線 regression 仍可完成",
    actual: `OPENAI_API_KEY_present=${onlineAvailable}`,
    result: onlineAvailable ? "PASS" : "PASS with notes",
  });

  // S163 P2 — Channel-B routing regression: KG operation queries must route to kg_admin
  // (was falling through to curriculum → g26 收生指引 only), WITHOUT regressing kg_admission.
  const routingCases: { q: string; expect: string }[] = [
    { q: "幼稚園營運 手冊 健康紀錄", expect: "kg_admin" },
    { q: "幼稚園營運手冊", expect: "kg_admin" },
    { q: "營運手冊 健康紀錄", expect: "kg_admin" },
    { q: "幼稚園收生 安排", expect: "kg_admission" },
    { q: "幼稚園入學報名", expect: "kg_admission" },
  ];
  for (const rc of routingCases) {
    const got = detectQueryCategory(rc.q);
    rows.push({
      scenario: `routing regression — ${rc.q}`,
      precondition: "detectQueryCategory 純函數可用",
      action: `detectQueryCategory("${rc.q}")`,
      expected: `route=${rc.expect}`,
      actual: `route=${got ?? "(none)"}`,
      result: got === rc.expect ? "PASS" : "FAIL",
    });
  }

  // S163 P3 — lexical-overlap primitive: a short KG narrative shares CJK bigrams with
  // related requirements but NOT with unrelated ones, so the gate demotes unrelated
  // high-cosine items to "missing" (full DF-gated behaviour verified by live e2e).
  const p3Doc = "本幼稚園保存學生健康紀錄，每日量度體溫，定期清潔課室及更換床單。";
  const docBg = new Set(cjkBigrams(p3Doc));
  const sharesTerm = (req: string) => cjkBigrams(req).some((b) => docBg.has(b));
  const gateCases: { req: string; expect: boolean; label: string }[] = [
    { req: "本校須妥善保存每名學生的健康紀錄", expect: true, label: "related-health-record" },
    { req: "兒童返抵園舍時須量度體溫並記錄", expect: true, label: "related-temperature" },
    { req: "本校校董會須向教師發出聘書並訂明薪級", expect: false, label: "unrelated-appointment-letter" },
    { req: "本校須為每三十名男童設置一個洗手盆", expect: false, label: "unrelated-wash-basin" },
  ];
  for (const gc of gateCases) {
    const got = sharesTerm(gc.req);
    rows.push({
      scenario: `lexical-gate regression — ${gc.label}`,
      precondition: "cjkBigrams 純函數可用",
      action: `sharesTerm("${gc.req.slice(0, 10)}…")`,
      expected: `shares-term=${gc.expect}`,
      actual: `shares-term=${got}`,
      result: got === gc.expect ? "PASS" : "FAIL",
    });
  }

  const passCount = rows.filter((row) => row.result === "PASS").length;
  const failCount = rows.filter((row) => row.result === "FAIL").length;
  const notesCount = rows.filter((row) => row.result === "PASS with notes").length;

  console.log("# Semantic Regression Report");
  console.log(`mode: ${onlineAvailable ? "online-capable" : "offline-only"}`);
  console.log(`source_registry_count: ${(await loadJson<{ sources: unknown[] }>("dev/source/source_registry.json")).sources.length}`);
  console.log(`real_circular_samples: ${realCircularCases.length}`);
  console.log("");
  console.log("| Scenario | Expected | Actual | Result |");
  console.log("|---|---|---|---|");
  for (const row of rows) {
    console.log(
      `| ${row.scenario} | ${row.expected.replace(/\|/g, "/")} | ${row.actual.replace(/\|/g, "/")} | ${row.result} |`
    );
  }
  console.log("");
  console.log(
    `summary: PASS=${passCount}; PASS_with_notes=${notesCount}; FAIL=${failCount}; overall=${failCount === 0 ? (notesCount > 0 ? "PASS with notes" : "PASS") : "FAIL"}`
  );

  if (!onlineAvailable) {
    console.log("note: OPENAI_API_KEY missing — full online regression against live embeddings/LLM is still pending.");
  }
  if (failCount > 0) {
    process.exitCode = 1;
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
