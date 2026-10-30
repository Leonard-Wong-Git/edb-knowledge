/**
 * S241 — offline regression for src/lib/circularRef.ts (no network).
 *   node_modules/.bin/tsx scripts/circularRefRegression.ts
 */
import assert from "node:assert/strict";
import { buildCircularIndex, candidateSourceIds, headerCircularKey, parseCircularRef } from "../src/lib/circularRef.js";

let count = 0;
function test(name: string, check: () => void) {
  check(); count++; console.log(`PASS ${name}`);
}

test("Chinese full form", () => assert.equal(parseCircularRef("教育局通函第134/2026號"), "通函|134|2026"));
test("通告 vs 通函 kept apart", () => assert.equal(parseCircularRef("教育局通告第12/2026號"), "通告|12|2026"));
test("no 第 / 號, spaces, full-width", () => {
  assert.equal(parseCircularRef("通函 134 / 2026 有咩要做"), "通函|134|2026");
  assert.equal(parseCircularRef("通函１３４／２０２６"), "通函|134|2026");
});
test("English forms; EDBCM is a memorandum, not a circular", () => {
  assert.equal(parseCircularRef("EDBCM 134/2026"), "通函|134|2026");
  assert.equal(parseCircularRef("EDB Circular Memorandum No. 79/2025"), "通函|79|2025");
  assert.equal(parseCircularRef("EDBC 4/2026"), "通告|4|2026");
  assert.equal(parseCircularRef("EDB Circular No. 17/2024"), "通告|17|2024");
});
test("no year → no guess", () => assert.equal(parseCircularRef("教育局通函第134號"), null));
test("ordinary queries do not trigger", () => {
  for (const q of ["SEN學生留級安排", "師生比例 1/11", "幼稚園每班最多可以收幾多個學生", "2026/27學年的推廣閱讀津貼", "年假"]) {
    assert.equal(parseCircularRef(q), null, q);
  }
});

const header = (n: string) => `=== Page 1 ===檔號： 0004-0065-8060-9055-0030-0001-P001教育局通函第${n}號分發名單：各官立學校`;
test("header with spaced-out digits", () =>
  assert.equal(headerCircularKey("=== Page 1 ===1檔號：1125-2035-8060-9070-00016-P001教育局通函第1 4 2 / 2 0 2 6 號分發名單"), "通函|142|2026"));
test("header only on page 1", () => assert.equal(headerCircularKey(header("134/2026").replace("Page 1", "Page 3")), null));
test("a cited number without 檔號 is not a header", () =>
  assert.equal(headerCircularKey("=== Page 1 ===根據教育局通告第10/2009號，幼稚園須…"), null));
test("index: one source, one number", () => {
  const idx = buildCircularIndex([
    { source_id: "edbcm134_2026", text: header("134/2026") },
    { source_id: "edbcm134_2026", text: "=== Page 2 ===正文" },
  ]);
  assert.equal(idx.get("通函|134|2026"), "edbcm134_2026");
});
test("index: ambiguity is dropped, not guessed", () => {
  const idx = buildCircularIndex([
    { source_id: "manual", text: header("10/2009") },
    { source_id: "manual", text: header("19/2025") },   // one source, two numbers
    { source_id: "a", text: header("5/2022") },
    { source_id: "b", text: header("5/2022") },         // one number, two sources
    { source_id: "ok", text: header("7/2026") },
  ]);
  assert.equal(idx.size, 1);
  assert.equal(idx.get("通函|7/2026".replace("/", "|")), "ok");
});

test("id candidates follow ingest naming, memorandum vs circular", () => {
  assert.ok(candidateSourceIds("通函|134|2026").includes("edbcm134_2026"));
  assert.ok(candidateSourceIds("通函|60|2026").includes("edbcm060_2026"));
  assert.ok(candidateSourceIds("通告|12|2026").includes("edbc012_2026"));
  assert.ok(candidateSourceIds("通告|4|2026").includes("EDBC_4_2026_E"));
  assert.ok(!candidateSourceIds("通告|12|2026").some((id) => id.startsWith("edbcm")));
});

console.log(`ALL PASS (${count})`);
