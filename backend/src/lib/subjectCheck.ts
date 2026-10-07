/**
 * S236 — 路線乙 v1：問題對象核對（presence 版，決定性，不呼叫模型）。
 *
 * 病徵（D01）：問「學生請病假要唔要交醫生紙」，合成窗五段全是教職員病假規則，判官放行，
 * 合成器第一句便寫「學生請病假需要提交有效的醫生證明書」。改判官提示與換判官模型都已證
 * 修不了（S202、S211、S230），所以改用一道不靠模型的閘。
 *
 * 規則：
 *   1. 以詞表判斷問題問的是哪一類人（學生／家長／教師／校長／非教學人員／校董）；
 *   2. 窗內只要有一段提到該類人（含同義詞）即通過；教師與非教學人員接受泛稱「員工」等；
 *   3. 問題提到的每一類人都要通過；問題沒有提到任何一類人時不作判斷（通過）。
 *
 * 這是 dev/source/subject_check_probe.py 的 `presence_v1_pass` 逐行移植（v2「最具體角色詞」
 * 已於 S235 否決，不移植）。S235 量度：判官已知漏判 5 條中攔到 3 條，對應答題誤攔 0。
 * 只捕捉「窗內完全沒有該類人」一種錯置；設計、量度與限制見 dev/source/SUBJECT_CHECK_DESIGN.md。
 * 改詞表時必須同步改 probe，並跑 backend/scripts/_s236_subjectParity.ts 確認兩邊逐題相同。
 */

export type SubjectGroup = "STUDENT" | "PARENT" | "TEACHER" | "PRINCIPAL" | "NONTEACH" | "DIRECTOR";

// q   = 在問題中出現即視為問及該類人
// sat = 在窗內片段中出現即視為資料涉及該類人
export const SUBJECT_GROUPS: Record<SubjectGroup, { label: string; q: string[]; sat: string[] }> = {
  STUDENT: {
    label: "學生",
    q: ["學生", "學童", "同學", "幼兒", "小朋友", "兒童"],
    sat: ["學生", "學童", "同學", "幼兒", "小朋友", "兒童"],
  },
  PARENT: { label: "家長", q: ["家長"], sat: ["家長", "父母", "監護人"] },
  TEACHER: {
    label: "教師",
    q: ["教師", "老師", "教學人員", "教員", "代課"],
    sat: ["教師", "老師", "教學人員", "教員", "代課", "教職員", "員工", "僱員"],
  },
  PRINCIPAL: { label: "校長", q: ["校長"], sat: ["校長"] },
  NONTEACH: {
    label: "非教學人員",
    q: ["非教學人員", "職員", "工友", "校工", "文員", "技術員"],
    sat: ["非教學人員", "職員", "工友", "校工", "文員", "技術員", "教職員", "員工", "僱員"],
  },
  DIRECTOR: { label: "校董", q: ["校董"], sat: ["校董"] },
};

const GROUP_ORDER = Object.keys(SUBJECT_GROUPS) as SubjectGroup[];

function fold(s: string | null | undefined): string {
  return (s ?? "").normalize("NFKC").replace(/\s+/g, "");
}

// 「非教學人員」內含「教學人員」，查教師時先遮走，免得非教學人員的片段冒充教師
function mask(text: string, group: SubjectGroup): string {
  return group === "TEACHER" ? text.split("非教學人員").join("") : text;
}

/** 問題保留空格：「小學 生涯規劃」去空格後會拼出「學生」（S235 審核發現）。 */
export function questionSubjects(query: string): SubjectGroup[] {
  const q = (query ?? "").normalize("NFKC");
  return GROUP_ORDER.filter((g) => SUBJECT_GROUPS[g].q.some((t) => mask(q, g).includes(t)));
}

function foldedMentions(folded: string[], group: SubjectGroup): boolean {
  return folded.some((x) => SUBJECT_GROUPS[group].sat.some((t) => mask(x, group).includes(t)));
}

export function windowMentions(texts: string[], group: SubjectGroup): boolean {
  return foldedMentions(texts.map(fold), group);
}

export interface SubjectCheckResult {
  /** 問題問及的人群；空陣列＝不作判斷 */
  subjects: SubjectGroup[];
  /** 問及但窗內完全沒有提到的人群 */
  missing: SubjectGroup[];
  /** 窗內有提到的人群（只用於拒答句說明資料涉及誰） */
  present: SubjectGroup[];
  pass: boolean;
}

export function checkSubjects(query: string, texts: string[]): SubjectCheckResult {
  const subjects = questionSubjects(query);
  if (subjects.length === 0) return { subjects, missing: [], present: [], pass: true };
  const folded = texts.map(fold);
  const missing = subjects.filter((g) => !foldedMentions(folded, g));
  const present = missing.length ? GROUP_ORDER.filter((g) => foldedMentions(folded, g)) : [];
  return { subjects, missing, present, pass: missing.length === 0 };
}

/** 固定前綴：search_log 以此判定為拒答（見 searchChannelB.ts `isSynthesisDecline`）。 */
export const SUBJECT_DECLINE_PREFIX = "根據檢索到的教育局文件，未有找到適用於";

/** 決定性拒答句，不經模型生成 —— 避免 D01 那種「先答錯、再改口」。 */
export function subjectDeclineMessage(result: SubjectCheckResult): string {
  const label = (gs: SubjectGroup[]) => gs.map((g) => SUBJECT_GROUPS[g].label).join("、");
  const scope = result.present.length ? `檢索到的資料只提及${label(result.present)}。` : "";
  return (
    `${SUBJECT_DECLINE_PREFIX}${label(result.missing)}的明確規定；${scope}` +
    "下方為主題相關的原始文件，或可參考；亦可嘗試以其他關鍵詞重新搜尋。"
  );
}
