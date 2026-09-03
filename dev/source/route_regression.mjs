#!/usr/bin/env node
/**
 * route_regression.mjs — detectQueryCategory 路由回歸測試（S211）
 *
 * 點解係 .mjs 而唔係跟 dev/source/ 嘅 .py 慣例：TOPIC_KEYWORDS 係 JS regex。用 Python `re`
 * 重寫一份就會有兩份定義，而兩者對 \b、量詞、/i 嘅處理唔完全一樣——測試會靜靜哋同真正
 * 行緊嘅嘢分岔。呢個腳本直接由 searchChannelB.ts 抽真嗰個 object 出嚟評估，唔另寫一份。
 *
 * 用法：node dev/source/route_regression.mjs
 * 退出碼 0 = 全數符合預期；1 = 有 query 路由改變。
 */
import fs from "node:fs";
import path from "node:path";

const TS = path.join(process.cwd(), "backend/src/api/searchChannelB.ts");
const src = fs.readFileSync(TS, "utf8");
const start = src.indexOf("const TOPIC_KEYWORDS");
if (start < 0) { console.error("找不到 TOPIC_KEYWORDS"); process.exit(2); }
const end = src.indexOf("\n};", start);
const body = src.slice(src.indexOf("{", start) + 1, end)
  .split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
const TOPIC_KEYWORDS = eval("({" + body + "})");

const detect = (q) => {
  for (const [k, re] of Object.entries(TOPIC_KEYWORDS)) if (re.test(q)) return k;
  return null;
};

/* 每條 query 標明應該去邊條路由。null = 蓄意唔路由（走通用語義搜尋）。
   新增或改動 TOPIC_KEYWORDS 前後都跑一次，差異就係你今次真正改咗嘅範圍。 */
/* 已知缺口：路由不到，但唔係今次改動造成（S211 前後一樣）。列喺度係為咗唔好靜靜哋當佢
   合格，同時唔會令回歸測試因為舊有問題而長期紅燈。修好其中一條就由呢度搬上 CASES。 */
const KNOWN_GAPS = [
  // S212 — safety 認裸「氣體」（原意係實驗室氣體安全），於是任何氣體相關嘅
  // 物理／化學課程查詢都被硬過濾去校園安全語料。實測「普適氣體定律」：路由去
  // safety → phys_sss_2007_2015 完全攞唔到；關掉路由過濾就返到 2/6。
  // 唔喺 S212 修：改 safety regex 係檢索改動，要行 eval before→after，
  // 而本 session 嘅 baseline 已經用嚟驗物理科重入庫，唔應該一次過驗兩件事。
  ["普適氣體定律", "curriculum", "safety 認裸「氣體」，偷走氣體相關嘅課程查詢"],
  ["氣體定律", "curriculum", "同上"],
];

const CASES = [
  // ── S211 新路由：入職資歷 ───────────────────────────────────────────────
  ["只修讀中學師資資格是否可以在小學任常額職位", "teacher_qualification"],
  ["未有小學師資訓練可唔可以做 APSM",            "teacher_qualification"],
  ["助理小學學位教師入職條件",                    "teacher_qualification"],
  ["中學師訓可唔可以教小學",                      "teacher_qualification"],
  ["檢定教員同准用教員有咩分別",                  "teacher_qualification"],
  // ── 唔可以被新路由偷走嘅舊路由 ─────────────────────────────────────────
  ["教師持續專業發展時數要求",                    "cpd"],
  ["教師培訓日點計",                              "cpd"],
  ["全日制資助小學教學人員編制",                  "staffing"],
  ["12 班小學有幾多個學位教師",                   "staffing"],   // S211 修好（前為已知缺口）
  ["24班中學要幾多個主任",                       "staffing"],
  ["學位教師職系有咩職級",                        "staffing"],
  ["教師病假幾多日要交醫生紙",                    "hr_admin"],
  ["教師年假有幾多日",                            "hr_admin"],
  ["常額教席點樣聘任",                            "hr_admin"],
  ["採購超過 5 萬元程序",                         "finance"],
  ["資助則例邊條講校董會經費",                    "school_governance"], // 校董會 先於 finance，設計如此
  ["SEN 統籌主任職責",                            "sen"],
  ["校車保母有咩要求",                            "school_bus"],
  ["颱風停課安排",                                "safety"],
  ["法團校董會同學校管理委員會分別",              "school_governance"],
  ["幼稚園收生日期",                              "kg_admission"],
  ["幼稚園營運手冊健康紀錄",                      "kg_admin"],
  ["中文科課程指引學習範疇",                      "curriculum"],
  ["資優教育校本課程",                            "gifted"],
  ["視學同校外評核分別",                          "qa_inspection"],
  ["價值觀教育首要價值觀",                        "value_education"],
  ["公民與社會發展科內地考察",                    "cgss"],
  ["數字教育發展藍圖 AI 素養",                    "digital_education"],
  ["全方位學習津貼點用",                          "activity"],
  ["中一派位統一派位",                            "placement"],
  ["體罰學生點處理",                              "conduct"],
  ["校園欺凌強制舉報",                            "student_support"],
  ["STEAM 教育推行",                              "steam"],
  // ── S212 新路由：資訊保安 / 雲端私隱 ───────────────────────────────────
  ["網絡安全運動",                                "info_security"],
  ["雲端運算 私隱",                               "info_security"],
  ["Zoom 保安設定",                               "info_security"],
  ["學校收到勒索軟件點算",                        "info_security"],
  ["雲端服務儲存學生資料要注意咩",                "info_security"],
  // ── S212 必須唔可以被 info_security 偷走（負面案例）───────────────────
  // S209 定案：呢條闊 query 返 SAG / role_facts_it / g24 係啱嘅，g28 冇「建議措施」文件
  // 答得到佢。所以 info_security 蓄意唔認裸「資訊保安」，呢條必須維持唔路由。
  ["學校資訊保安",                                null],
  ["校園安全風險評估",                            "safety"],
  ["實驗室安全指引",                              "safety"],
  ["安全管理委員會職責",                          "safety"],
  ["校車保母安全要求",                            "school_bus"],
  ["數字教育發展藍圖",                            "digital_education"],
  ["資訊科技教育推行",                            "digital_education"],
  ["學生個人資料保存幾耐",                        null],
];

let bad = 0;
for (const [q, want] of CASES) {
  const got = detect(q);
  const ok = got === want;
  if (!ok) bad++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${String(got)}${ok ? "" : `  (預期 ${want})`}  ← ${q}`);
}
console.log(`\n${CASES.length - bad}/${CASES.length} PASS`);

if (KNOWN_GAPS.length) {
  console.log("\n已知缺口（唔計入 PASS/FAIL，S211 前後行為一樣）：");
  for (const [q, want, why] of KNOWN_GAPS) {
    console.log(`  ${String(detect(q))} → 理想 ${want}  ← ${q}\n      ${why}`);
  }
}
process.exit(bad ? 1 : 0);
