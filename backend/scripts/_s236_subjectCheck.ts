/**
 * S236 — 路線乙 v1（src/lib/subjectCheck.ts）的三種驗證。全部不呼叫任何模型。
 *
 *   --self-test          移植 probe 的斷言，加拒答句與 search_log 判定
 *   --parity ROWS.json   與 Python 原型逐題比對（ROWS 由
 *                        `python3 dev/source/subject_check_probe.py --export-rows ROWS.json --gold <run>` 產生）
 *   --smoke              本機端到端：真檢索（生產 Supabase）＋旗標開關對照，最多 4 次 LLM 呼叫
 *                        （Leonard 2026-10-07 批准判官呼叫）；需 --env-file=.env
 *   --live OUT.json      以生產 /api/search/channel-b（x-probe、synthesize:false，即零 LLM、只做檢索；每 7 秒一次，約 30 分鐘）
 *                        取回五套題的現時合成窗（前五段），用上線版 checkSubjects 判定；
 *                        OUT 只存 id、查詢、片段 id 與判定，不存片段全文
 *
 * 用法（在 backend/ 內）：
 *   node_modules/.bin/tsx scripts/_s236_subjectCheck.ts --self-test
 *   node_modules/.bin/tsx scripts/_s236_subjectCheck.ts --parity <scratchpad>/s236_rows.json
 *   node_modules/.bin/tsx --env-file=.env scripts/_s236_subjectCheck.ts --smoke
 *   node_modules/.bin/tsx scripts/_s236_subjectCheck.ts --live ../dev/source/eval_runs/<date>_s236_subject_live.json
 */
import fs from "node:fs";
import path from "node:path";
import {
  checkSubjects,
  questionSubjects,
  SUBJECT_DECLINE_PREFIX,
  subjectDeclineMessage,
} from "../src/lib/subjectCheck.js";
import { isSynthesisDecline, searchChannelB, SYNTHESIS_DECLINE } from "../src/api/searchChannelB.js";
import { createEmbeddingClient } from "../src/lib/embeddingClient.js";
import { createLlmClient } from "../src/lib/llmClient.js";
import { getJudgeModel } from "../src/config/env.js";

const ENDPOINT = "https://edb-knowledge.onrender.com/api/search/channel-b";
/** 生產限速每 IP 每分鐘 10 次（server.ts RATE_LIMIT）；與 eval_retrieval.py DEFAULT_PACE_S 相同。
 *  S236 第一次跑用 400ms，全數撞 429，即使 x-probe 亦不豁免限速。 */
const PACE_MS = 7_000;
const SOURCE_DIR = path.resolve(import.meta.dirname, "../../dev/source");

function selfTest(): number {
  let fails = 0;
  const ok = (n: string, c: boolean) => {
    if (!c) fails++;
    console.log(`  ${c ? "ok  " : "FAIL"} ${n}`);
  };
  const staff = ["僱員如申請病假超逾兩天，必須出示有效的醫生證明書。", "月薪教學及非教學人員病假：首年28天。"];

  ok("學生問題判為 STUDENT", JSON.stringify(questionSubjects("學生請病假要唔要交醫生紙")) === '["STUDENT"]');
  ok("跨空格不拼出「學生」", questionSubjects("小學 生涯規劃").length === 0);
  ok("D01 型：窗內無學生應攔下", !checkSubjects("學生請病假要唔要交醫生紙", staff).pass);
  ok("教師對照：員工／僱員算教師", checkSubjects("老師請病假要唔要交醫生紙", staff).pass);
  ok("非教學人員不同時判為教師", JSON.stringify(questionSubjects("非教學人員產假有幾多日")) === '["NONTEACH"]');
  ok("只有非教學人員的窗不冒充教師", !checkSubjects("老師有幾多日病假", ["非教學人員病假首年28天。"]).pass);
  ok("校董在窗內應通過", checkSubjects("法團校董會校董有冇薪酬", ["法團校董會不得向任何校董提供任何酬勞。"]).pass);
  ok("無對象詞不作判斷", checkSubjects("幼稚園每班師生比例係幾多", []).subjects.length === 0);
  ok("同義詞「學童」算學生", checkSubjects("學生請病假要唔要交醫生紙", ["學童缺課須由家長通知學校。"]).pass);
  ok("全形空白與 NFKC 摺疊", checkSubjects("學生病假", ["學　生"]).pass);
  // v2（具體角色）已否決：v1 對「家長義工」只看「家長」
  ok("v1 不做 v2 的具體角色核對", checkSubjects("家長義工要唔要做查核", ["如有關學生的家長提出查閱資料"]).pass);

  const d01 = checkSubjects("學生請病假要唔要交醫生紙", staff);
  const msg = subjectDeclineMessage(d01);
  ok("拒答句說明缺學生", msg.includes("未有找到適用於學生的明確規定"));
  ok("拒答句說明窗內涉及誰", msg.includes("檢索到的資料只提及教師、非教學人員。"));
  ok("拒答句以固定前綴開頭", msg.startsWith(SUBJECT_DECLINE_PREFIX));
  ok("窗內無任何人群時不寫「只提及」",
    !subjectDeclineMessage(checkSubjects("學生請病假", ["病假須出示證明書。"])).includes("只提及"));
  // RED-TEST — search_log 以前用 `=== SYNTHESIS_DECLINE`，對新拒答句會記成「已作答」
  ok("search_log：對象拒答算拒答", isSynthesisDecline(msg));
  ok("search_log：原拒答句照舊算拒答", isSynthesisDecline(SYNTHESIS_DECLINE));
  ok("search_log：一般回答不算拒答", !isSynthesisDecline("學生病假須出示醫生證明書。"));
  ok("search_log：空回答不算拒答", !isSynthesisDecline(undefined) && !isSynthesisDecline(""));

  console.log(fails === 0 ? "\nALL PASS" : `\n${fails} FAILED`);
  return fails === 0 ? 0 : 1;
}

interface Row {
  set: string;
  id: string;
  query: string;
  want: string;
  texts: string[];
  py_v1: { subjects: string[]; missing: string[]; pass: boolean };
}

function parity(rowsPath: string): number {
  const rows: Row[] = JSON.parse(fs.readFileSync(rowsPath, "utf8"));
  const diffs = rows.filter((r) => {
    const ts = checkSubjects(r.query, r.texts);
    return (
      ts.pass !== r.py_v1.pass ||
      JSON.stringify(ts.subjects) !== JSON.stringify(r.py_v1.subjects) ||
      JSON.stringify(ts.missing) !== JSON.stringify(r.py_v1.missing)
    );
  });
  const blocked = rows.filter((r) => !r.py_v1.pass);
  console.log(`比對 ${rows.length} 題；帶對象 ${rows.filter((r) => r.py_v1.subjects.length).length}；` +
    `Python 攔 ${blocked.length}；TS 與 Python 不同 ${diffs.length}`);
  for (const r of blocked) console.log(`  ✋ [${r.set}] ${r.id} want=${r.want} ${r.query} 缺：${r.py_v1.missing.join(",")}`);
  for (const r of diffs) console.log(`  ≠ [${r.set}] ${r.id} ${r.query}`);
  return diffs.length === 0 ? 0 : 1;
}

interface LiveCase { set: string; id: string; query: string; want: string }

function liveCases(): LiveCase[] {
  const out: LiveCase[] = [];
  for (const [set, file] of [
    ["acceptance", "judge_acceptance_cases.json"],
    ["fresh_s202", "judge_transplant_fresh_s202.json"],
    ["sx_s235", "judge_subject_s235.json"],
    ["hx_s235", "judge_subject_heldout_s235.json"],
  ] as const) {
    const cases = JSON.parse(fs.readFileSync(path.join(SOURCE_DIR, file), "utf8")).cases;
    for (const c of cases) out.push({ set, id: c.id, query: c.query, want: c.want });
  }
  const gold = JSON.parse(fs.readFileSync(path.join(SOURCE_DIR, "eval_runs/2026-09-28_s233_prod_gold.json"), "utf8"));
  for (const r of gold.results) out.push({ set: "gold", id: r.id, query: r.query, want: "-" });
  return out;
}

async function fetchWindow(query: string): Promise<{ id: string; text: string }[]> {
  let last = "";
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const res = await fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-probe": "1" },
        body: JSON.stringify({ query, top_k: 10, synthesize: false }),
        signal: AbortSignal.timeout(90_000),
      });
      if (res.ok) {
        const body = (await res.json()) as { results: { id: string; text: string }[] };
        return body.results.slice(0, 5).map((r) => ({ id: r.id, text: r.text }));
      }
      last = `HTTP ${res.status}`;
    } catch (e) {
      last = e instanceof Error ? e.message : String(e);
    }
    // 429 = 生產限速（每 IP 每分鐘 10 次）；退避要長過一個限速窗
    await new Promise((r) => setTimeout(r, (last === "HTTP 429" ? 20_000 : 5_000) * attempt));
  }
  throw new Error(last);
}

async function live(outPath: string): Promise<number> {
  const cases = liveCases();
  const rows = [];
  for (const [i, c] of cases.entries()) {
    try {
      const win = await fetchWindow(c.query);
      const v = checkSubjects(c.query, win.map((w) => w.text));
      rows.push({ ...c, chunk_ids: win.map((w) => w.id), subjects: v.subjects, missing: v.missing, pass: v.pass });
    } catch (e) {
      rows.push({ ...c, error: e instanceof Error ? e.message : String(e) });
    }
    if ((i + 1) % 25 === 0) console.log(`  ${i + 1}/${cases.length}`);
    await new Promise((r) => setTimeout(r, PACE_MS));
  }
  const ok = rows.filter((r) => !("error" in r)) as { set: string; id: string; query: string; want: string; subjects: string[]; missing: string[]; pass: boolean }[];
  const blocked = ok.filter((r) => !r.pass);
  const summary = {
    total: rows.length,
    errors: rows.length - ok.length,
    with_subject: ok.filter((r) => r.subjects.length).length,
    blocked: blocked.length,
    blocked_answerable: blocked.filter((r) => r.want === "能").length,
    blocked_gold: blocked.filter((r) => r.set === "gold").length,
  };
  fs.writeFileSync(outPath, JSON.stringify({
    _meta: {
      session: "S236",
      endpoint: ENDPOINT,
      request: { top_k: 10, synthesize: false, header: "x-probe: 1" },
      window: "results[0:5]，即 synthesizeAnswer 的 defaultWindow",
      checker: "backend/src/lib/subjectCheck.ts checkSubjects（v1）",
      run_at: new Date().toISOString(),
      summary,
    },
    results: rows,
  }, null, 1));
  console.log(JSON.stringify(summary));
  for (const r of blocked) console.log(`  ✋ [${r.set}] ${r.id} want=${r.want} ${r.query} 缺：${r.missing.join(",")}`);
  for (const r of rows.filter((r) => "error" in r)) console.log(`  ⚠ [${r.set}] ${r.id} ${(r as { error: string }).error}`);
  return 0;
}

const SMOKE_MAX_LLM_CALLS = 4;

/** 生產同一條 searchChannelB 路徑（route-first 開啟，與 Render 相同），只切換 FEATURE_SUBJECT_CHECK。 */
async function smoke(): Promise<number> {
  process.env.SUPABASE_URL ||= "https://youkcekbrbywuqjxgibe.supabase.co";
  process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
  process.env.FEATURE_ROUTE_FIRST_SEARCH = "1";
  let calls = 0;
  const guard = (fn: (p: string) => Promise<string>) => async (p: string) => {
    if (++calls > SMOKE_MAX_LLM_CALLS) throw new Error(`LLM 呼叫超過批准上限 ${SMOKE_MAX_LLM_CALLS}`);
    return fn(p);
  };
  const llm = createLlmClient();
  const judge = createLlmClient({ model: getJudgeModel() });
  const embed = createEmbeddingClient();
  const plan: [string, "1" | "0", "subject" | "judge-or-answer"][] = [
    ["學生請病假要唔要交醫生紙", "1", "subject"],          // D01
    ["家長可唔可以請侍產假", "1", "subject"],              // SX01
    ["老師請病假要唔要交醫生紙", "1", "judge-or-answer"],  // 對照：窗內有教職員，不應被攔
    ["學生請病假要唔要交醫生紙", "0", "judge-or-answer"],  // 旗標關閉：行為與今日生產相同
  ];
  let fails = 0;
  for (const [query, flag, expect] of plan) {
    process.env.FEATURE_SUBJECT_CHECK = flag;
    const before = calls;
    const r = await searchChannelB({ query, synthesize: true }, embed, guard(llm), guard(judge));
    const s = r.synthesis ?? "";
    const isSubject = s.startsWith(SUBJECT_DECLINE_PREFIX);
    const good = expect === "subject" ? isSubject && calls === before : !isSubject;
    if (!good) fails++;
    console.log(`${good ? "ok  " : "FAIL"} flag=${flag} 「${query}」 LLM+${calls - before} → ${s.slice(0, 90)}`);
  }
  console.log(`LLM 呼叫合計 ${calls}／上限 ${SMOKE_MAX_LLM_CALLS}`);
  return fails === 0 ? 0 : 1;
}

const arg = (flag: string) => {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
};

if (process.argv.includes("--self-test")) process.exit(selfTest());
else if (process.argv.includes("--smoke")) process.exit(await smoke());
else if (arg("--parity")) process.exit(parity(arg("--parity")!));
else if (arg("--live")) process.exit(await live(arg("--live")!));
else {
  console.log("用法：--self-test | --parity ROWS.json | --smoke | --live OUT.json");
  process.exit(2);
}
