#!/usr/bin/env node
/**
 * route_blast_radius.mjs — 改 TOPIC_KEYWORDS 之前／之後，到底有幾多條 gold query 改咗路由？
 *
 * 點解要有呢支（S227 建）：`route_regression.mjs` 答嘅係「我列出嘅個別案例有冇跑錯」，
 * 但佢只覆蓋 54 條人手挑嘅 query。改一條正則嘅實際影響範圍係成個 gold set —— 一個
 * 寫得太闊嘅 token（S227 嗰次係裸「評核」）可以靜靜哋搶走隔籬路由嘅題目，而個別案例
 * 測試唔一定挑中嗰條。呢支掃晒 185 條，答「我今次真正改咗幾多」。
 *
 * S227 實例：拆 `staff_appraisal` 出嚟之後掃，185 條只有 1 條改路由（`hr_appraisal`），
 * 即零附帶損害。同一次改動如果用咗裸「評核」，呢支會即刻報多三四條。
 *
 * 點解由 git 讀 before 版本而唔係手寫一份還原邏輯：手寫嗰份下次就唔啱用，而且會同
 * 真正改動分岔。同 `route_regression.mjs` 一樣，兩邊都係 eval 真嗰個 object，唔另寫定義。
 *
 * 用法（由 repo root 起）：
 *   node dev/source/route_blast_radius.mjs              # working tree vs origin/main
 *   node dev/source/route_blast_radius.mjs HEAD         # working tree vs HEAD
 *   node dev/source/route_blast_radius.mjs abc1234      # working tree vs 該 commit
 *   node dev/source/route_blast_radius.mjs --self-test  # 純離線自測，唔掃 gold
 *
 * 退出碼：0 = 掃完（**唔代表冇問題** —— 改動範圍要人手睇啱唔啱）；2 = 抽唔到表。
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const TS_PATH = "backend/src/api/searchChannelB.ts";
const GOLD_PATH = "dev/_s213_gold_all.json";

/** 由一段 searchChannelB.ts 原始碼抽出真嗰個 TOPIC_KEYWORDS object。 */
export function extractTopicKeywords(src) {
  const start = src.indexOf("const TOPIC_KEYWORDS");
  if (start < 0) return null;
  const end = src.indexOf("\n};", start);
  const body = src.slice(src.indexOf("{", start) + 1, end)
    .split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  return eval("({" + body + "})");
}

/** 逐條 pattern 按 object key 次序試 —— 同 detectQueryCategory 一模一樣。 */
export function detect(table, query) {
  for (const [key, re] of Object.entries(table)) if (re.test(query)) return key;
  return null;
}

export function diffRoutes(before, after, queries) {
  const changed = [];
  for (const q of queries) {
    const b = detect(before, q.query);
    const a = detect(after, q.query);
    if (b !== a) changed.push({ ...q, before: b, after: a });
  }
  return changed;
}

function selfTest() {
  const checks = [];
  const ok = (name, cond) => checks.push([name, cond]);

  const table = { alpha: /甲|乙/, beta: /丙/ };
  ok("detect: 首個命中者勝", detect(table, "甲") === "alpha");
  ok("detect: 次序決定歸屬", detect({ beta: /丙|甲/, alpha: /甲/ }, "甲") === "beta");
  ok("detect: 唔命中回 null", detect(table, "丁") === null);

  // 同一張表比自己，改變必須係 0。呢條係本工具嘅零假設：如果佢喺無改動之下都報到
  // 差異，之後每一次「只有 N 條變」都信唔過。
  const qs = [{ id: "q1", query: "甲" }, { id: "q2", query: "丙" }, { id: "q3", query: "丁" }];
  ok("diff: 同一張表零改變", diffRoutes(table, table, qs).length === 0);

  const widened = { alpha: /甲|乙/, beta: /丙|丁/ };
  const d = diffRoutes(table, widened, qs);
  ok("diff: 捉到新增命中", d.length === 1 && d[0].id === "q3" && d[0].before === null && d[0].after === "beta");

  // 搶走隔籬路由 —— 正正係 S227 用裸「評核」會出現嗰種。
  const stolen = { beta: /丙|甲/, alpha: /甲|乙/ };
  const d2 = diffRoutes(table, stolen, qs);
  ok("diff: 捉到被搶走", d2.length === 1 && d2[0].id === "q1" && d2[0].before === "alpha" && d2[0].after === "beta");

  ok("extract: 抽唔到表時回 null", extractTopicKeywords("const SOMETHING_ELSE = {};") === null);
  ok("extract: 抽得到真表",
    Object.keys(extractTopicKeywords("const TOPIC_KEYWORDS: Record<string, RegExp> = {\n  x: /甲/,\n};\n") ?? {}).length === 1);

  const failed = checks.filter(([, pass]) => !pass);
  for (const [name, pass] of checks) if (!pass) console.log(`FAIL  ${name}`);
  console.log(failed.length === 0 ? `ALL PASS (${checks.length} assertions)` : `${failed.length}/${checks.length} FAILED`);
  return failed.length === 0 ? 0 : 1;
}

if (process.argv.includes("--self-test")) process.exit(selfTest());

const ref = process.argv[2] ?? "origin/main";
const root = process.cwd();
const after = extractTopicKeywords(fs.readFileSync(path.join(root, TS_PATH), "utf8"));
if (!after) { console.error(`喺工作區嘅 ${TS_PATH} 搵唔到 TOPIC_KEYWORDS`); process.exit(2); }

let beforeSrc;
try {
  beforeSrc = execFileSync("git", ["show", `${ref}:${TS_PATH}`], { cwd: root, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 });
} catch {
  console.error(`讀唔到 ${ref}:${TS_PATH} —— ref 錯咗？`);
  process.exit(2);
}
const before = extractTopicKeywords(beforeSrc);
if (!before) { console.error(`喺 ${ref} 嘅 ${TS_PATH} 搵唔到 TOPIC_KEYWORDS`); process.exit(2); }

const gold = JSON.parse(fs.readFileSync(path.join(root, GOLD_PATH), "utf8"));
const changed = diffRoutes(before, after, gold);

const beforeKeys = Object.keys(before);
const afterKeys = Object.keys(after);
const added = afterKeys.filter((k) => !beforeKeys.includes(k));
const removed = beforeKeys.filter((k) => !afterKeys.includes(k));

console.log(`對照 ${ref}　·　gold query ${gold.length} 條`);
if (added.length) console.log(`新增路由：${added.join("、")}`);
if (removed.length) console.log(`移除路由：${removed.join("、")}`);
console.log(`改變路由：${changed.length} 條`);
for (const c of changed) {
  console.log(`  ${c.id.padEnd(34)} ${String(c.before)} -> ${String(c.after)}   ← ${c.query}`);
}

// 新路由攞走咗邊啲題 —— 唔止係「改變咗」嗰啲。如果入面有一條唔屬該主題，
// 佢而家就係對住一個錯嘅 SOURCE_SET 搜尋。
for (const key of added) {
  const claimed = gold.filter((g) => detect(after, g.query) === key);
  console.log(`\n${key} 現時擁有 ${claimed.length} 條 gold query：`);
  for (const g of claimed) console.log(`  ${g.id.padEnd(34)} ${g.query}`);
}
console.log("\n⚠️ 改變數字本身唔代表啱或錯 —— 逐條睇係咪你預期改嗰啲。");
