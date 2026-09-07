import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";
import {
  selectPrimaryEvidence,
  synthesizeGroundedAnswer,
  type EvidenceChunk,
} from "../src/lib/groundedSynthesis.js";

const chunks: EvidenceChunk[] = [{
  source_id: "fixture", title: "Test evidence",
  page: 7,
  text: "12班全日制資助小學：小學學位教師5名（不包括副校長）。助理小學學位教師14名。",
}];
const quote = "小學學位教師5名（不包括副校長）";
const claim = (text = "小學學位教師5名，不包括副校長。", q = quote, index = 1) =>
  ({ text, citations: [{ index, quote: q }] });
const draft = (claims: unknown[]) => async () =>
  JSON.stringify({ requested_matters: ["test matter"], claims });
const review = (supported = true, fully_answered = true) => async () =>
  JSON.stringify({ verdicts: [{ id: 0, reason: "test", answers_any_part: true, applicable: true, supported }], fully_answered });
const decline = "TEST_DECLINE";
const run = (d: () => Promise<string>, j = review(), evidence = chunks) =>
  synthesizeGroundedAnswer("12班全日制小學學位教師人數？", evidence, d, j, decline);
let count = 0;
async function test(name: string, check: () => void | Promise<void>) {
  await check(); count++; console.log(`PASS ${name}`);
}

await test("primary evidence selection refills slots below curated leads", () => {
  const mixed = [
    { id: "curated-1", content_type: "footnote_curated" },
    { id: "curated-2", content_type: "approved_fact" },
    ...Array.from({ length: 6 }, (_, index) => ({
      id: `primary-${index + 1}`, content_type: "vault_extract",
    })),
  ];
  assert.deepEqual(selectPrimaryEvidence(mixed).map((item) => item.id),
    ["primary-1", "primary-2", "primary-3", "primary-4", "primary-5"]);
});

await test("supported claim has server-rendered citation", async () => {
  assert.equal(await run(draft([claim()])), `${claim().text} 【來源：《Test evidence》第7頁】`);
});
await test("matching quote alone cannot bypass semantic judge", async () => {
  assert.equal(await run(draft([claim("編制保障教學質素。")]), review(false)), decline);
});
await test("fabricated quote is rejected without judge call", async () => {
  assert.equal(await run(draft([claim("教師有8名。", "小學學位教師8名（不包括副校長）")]),
    async () => { assert.fail("judge must not run"); }), decline);
});
for (const index of [0, -1, 2, 1.5]) {
  await test(`invalid citation index ${index}`, async () => {
    assert.equal(await run(draft([claim(undefined, quote, index)])), decline);
  });
}
await test("NFKC and whitespace preserve legitimate evidence matches", async () => {
  assert.match(await run(draft([claim(undefined, "小學學位教師５名 (不包括副校長)")])), /Test evidence/);
});
await test("short quote cannot manufacture evidence", async () => {
  assert.equal(await run(draft([claim(undefined, "5名")])), decline);
});
await test("citation in model prose cannot spoof a source", async () => {
  assert.equal(await run(draft([claim("有5名教師。[99]")])), decline);
});
await test("model prose cannot spoof the server source namespace", async () => {
  assert.equal(await run(draft([claim("有5名教師。【來源：《偽造文件》】")])), decline);
});
await test("multiline model prose cannot escape the claim layout", async () => {
  assert.equal(await run(draft([claim("有5名教師。\n已由教育局核證。")])), decline);
});
await test("truncated sentence is rejected before semantic review", async () => {
  assert.equal(await run(draft([claim(
    "由本局早前委託香港大學教育學院教育政策研究中心進行的「現階段學校發展與問責架構的推行對促進香港學校發展的效能研究」已完成，結果進一步肯定架構在推動學校自我完善方面具正面成",
  )]),
    async () => { assert.fail("judge must not run"); }), decline);
});
await test("obvious repeated OCR phrase is rejected before semantic review", async () => {
  assert.equal(await run(draft([claim("教育局教育局教育局教育局公布政策。")]),
    async () => { assert.fail("judge must not run"); }), decline);
});
await test("ordinary two-time phrase reuse remains valid", async () => {
  assert.match(await run(draft([claim("學校須保存記錄；學校亦須接受審核。")])), /Test evidence/);
});
await test("supported part survives, rejected opinion is not rendered", async () => {
  const answer = await run(draft([claim(), claim("編制保障教學質素。")]), async () =>
    JSON.stringify({ verdicts: [
      { id: 0, reason: "test", answers_any_part: true, applicable: true, supported: true },
      { id: 1, reason: "test", answers_any_part: true, applicable: true, supported: false },
    ], fully_answered: false }));
  assert.match(answer, /5名/); assert.doesNotMatch(answer, /保障/); assert.match(answer, /部分問題/);
});
await test("discarded invalid citation cannot hide partial answer status", async () => {
  assert.match(await run(draft([claim(), claim(undefined, "invented quote")])), /部分問題/);
});
await test("missing subquestion is disclosed even when all claims pass", async () => {
  assert.match(await run(draft([claim()]), review(true, false)), /部分問題/);
});
await test("full rejection is an abstention", async () => {
  assert.equal(await run(draft([claim()]), review(false)), decline);
});
await test("entailed but irrelevant claim is rejected", async () => {
  assert.equal(await run(draft([claim()]), async () => JSON.stringify({
    verdicts: [{ id: 0, reason: "wrong requested matter", answers_any_part: false, applicable: true, supported: true }],
    fully_answered: true,
  })), decline);
});
await test("supported but inapplicable claim is rejected", async () => {
  assert.equal(await run(draft([claim()]), async () => JSON.stringify({
    verdicts: [{ id: 0, reason: "wrong school level", answers_any_part: true, applicable: false, supported: true }],
    fully_answered: true,
  })), decline);
});
await test("unique exact quote repairs a valid but wrong citation index", async () => {
  const evidence = [
    { ...chunks[0], source_id: "other", title: "Other", text: "完全無關的政策內容。" },
    chunks[0],
  ];
  assert.match(await run(draft([claim(undefined, quote, 1)]), review(), evidence), /Test evidence/);
});
await test("ambiguous cross-chunk quote is not rebound", async () => {
  const evidence = [
    { ...chunks[0], source_id: "wrong", title: "Wrong", text: "完全無關的政策內容。" },
    chunks[0],
    { ...chunks[0], source_id: "duplicate", title: "Duplicate" },
  ];
  assert.equal(await run(draft([claim(undefined, quote, 1)]), review(), evidence), decline);
});
await test("source label does not double-wrap an existing book title", async () => {
  const evidence = [{ ...chunks[0], title: "《Test evidence》" }];
  assert.equal(await run(draft([claim()]), review(), evidence),
    `${claim().text} 【來源：《Test evidence》第7頁】`);
});
for (const bad of ["not JSON", "[]", '{"verdicts":[],"fully_answered":true}',
  '{"verdicts":[{"id":9,"supported":true}],"fully_answered":true}',
  '{"verdicts":[{"id":0,"supported":"true"}],"fully_answered":true}']) {
  await test(`malformed judge fails closed: ${bad}`, async () => {
    assert.match(await run(draft([claim()]), async () => bad), /核證暫時未能完成/);
  });
}
await test("duplicate judge ids fail closed", async () => {
  assert.match(await run(draft([claim(), claim()]), async () => JSON.stringify({
    verdicts: [
      { id: 0, reason: "test", answers_any_part: true, applicable: true, supported: true },
      { id: 0, reason: "test", answers_any_part: true, applicable: true, supported: true },
    ], fully_answered: true,
  })), /核證暫時未能完成/);
});
await test("draft outage is not misreported as missing policy", async () => {
  assert.match(await run(async () => { throw new Error("offline"); }), /核證暫時未能完成/);
});
await test("judge outage does not return unverified draft", async () => {
  assert.match(await run(draft([claim()]), async () => { throw new Error("offline"); }), /核證暫時未能完成/);
});
await test("empty evidence makes no LLM call", async () => {
  assert.equal(await run(async () => { assert.fail("no model call"); }, review(), []), decline);
});
await test("empty draft abstains without judge call", async () => {
  assert.equal(await run(draft([]), async () => { assert.fail("no judge call"); }), decline);
});
await test("missing requested matters fails closed without judge call", async () => {
  assert.match(await run(async () => JSON.stringify({ claims: [claim()] }),
    async () => { assert.fail("judge must not run"); }), /核證暫時未能完成/);
});
await test("invalid requested matters fail closed", async () => {
  assert.match(await run(async () => JSON.stringify({ requested_matters: [""], claims: [claim()] })),
    /核證暫時未能完成/);
});
await test("structured schemas reach both model callbacks", async () => {
  const names: string[] = [];
  await synthesizeGroundedAnswer("Q", chunks, async (_prompt, format) => {
    assert.ok(format); names.push(format.name); return draft([claim()])();
  }, async (_prompt, format) => {
    assert.ok(format); names.push(format.name); return review()();
  }, decline);
  assert.deepEqual(names, ["policy_claims", "policy_claim_review"]);
});

const clientSource = readFileSync(new URL("../src/lib/llmClient.ts", import.meta.url), "utf8");
const clientAst = ts.createSourceFile("llmClient.ts", clientSource, ts.ScriptTarget.Latest, true);
const clientFn = clientAst.statements.find((node): node is ts.FunctionDeclaration =>
  ts.isFunctionDeclaration(node) && node.name?.text === "createLlmClient");
assert.ok(clientFn);
const requests: Record<string, unknown>[] = [];
const clientOptions: Record<string, unknown>[] = [];
let responseStatus = "completed";
class FakeOpenAI {
  constructor(options: Record<string, unknown>) { clientOptions.push(options); }
  responses = { create: async (request: Record<string, unknown>) => {
    requests.push(request); return { output_text: "ok", status: responseStatus };
  } };
}
const clientCtx = vm.createContext({ exports: {}, OpenAI: FakeOpenAI,
  getOpenAIApiKey: () => "test-only", getOpenAIModel: () => "test-model", sdkFetch: undefined });
vm.runInContext(ts.transpileModule(clientFn.getText(clientAst), {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
}).outputText, clientCtx);
const client = clientCtx.createLlmClient();
await test("legacy API request does not add text.format", async () => {
  await client("legacy");
  assert.equal(JSON.stringify(requests.at(-1)), JSON.stringify({ model: "test-model", input: "legacy" }));
});
await test("probe client can disable SDK retries", async () => {
  clientCtx.createLlmClient({ maxRetries: 0 });
  assert.equal(clientOptions.at(-1)?.maxRetries, 0);
});
await test("structured API request uses Responses text.format with strict schema", async () => {
  await client("structured", { name: "test", schema: { type: "object" } });
  assert.equal(JSON.stringify(requests.at(-1)?.text), JSON.stringify({
    format: { type: "json_schema", strict: true, name: "test", schema: { type: "object" } },
  }));
});
await test("incomplete structured output is rejected", async () => {
  responseStatus = "incomplete";
  await assert.rejects(client("structured", { name: "test", schema: {} }), /incomplete/);
  responseStatus = "completed";
});

// Execute the real private production function, not a second ordering model.
const source = readFileSync(new URL("../src/api/searchChannelB.ts", import.meta.url), "utf8");
const ast = ts.createSourceFile("searchChannelB.ts", source, ts.ScriptTarget.Latest, true);
const fn = ast.statements.find((node): node is ts.FunctionDeclaration =>
  ts.isFunctionDeclaration(node) && node.name?.text === "synthesizeAnswer");
assert.ok(fn);
const compiled = ts.transpileModule(fn.getText(ast), {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
}).outputText;
const results = [
  { ...chunks[0], id: "other", source_id: "other", score: 1, content_type: "vault_extract" },
  { ...chunks[0], id: "exact", score: 1, content_type: "vault_extract" },
];
function production(env: Record<string, string>, handler: typeof synthesizeGroundedAnswer) {
  const ctx = vm.createContext({
    process: { env }, selectPrimaryEvidence, synthesizeGroundedAnswer: handler,
    SYNTHESIS_DECLINE: decline,
    SYNTHESIS_PROMPT: "{QUERY}\n{CHUNKS}", VAULT_LEAD_SCORE: 0.7,
    judgeCanAnswer: async () => true,
  });
  vm.runInContext(compiled, ctx);
  return ctx.synthesizeAnswer;
}
await test("both synthesis flags off preserve the legacy synthesis prompt exactly", async () => {
  const f = production({}, async () => { assert.fail("new path must not run"); });
  assert.equal(await f("Q", results, async (p: string) => p, undefined, new Set(["fixture"])),
    `Q\n[1] ${results[0].text}\n\n[2] ${results[1].text}`);
});
await test("exact narrowing passes only the exact evidence", async () => {
  const f = production({ FEATURE_GROUNDED_SYNTHESIS: "1", FEATURE_EXACT_WINDOW_NARROW: "1" },
    async (_q, evidence) => { assert.equal(evidence.length, 1); assert.equal(evidence[0].source_id, "fixture"); return "verified"; });
  assert.equal(await f("Q", results, async () => "", undefined, new Set(["fixture"])), "verified");
});
await test("high-score main lead does not bypass grounded review", async () => {
  let calls = 0;
  const f = production({ FEATURE_GROUNDED_SYNTHESIS: "1" }, async () => { calls++; return decline; });
  assert.equal(await f("Q", results, async () => "", results[0], undefined), decline);
  assert.equal(calls, 1);
});
await test("grounded synthesis passes only primary document extracts", async () => {
  const mixed = [
    { ...results[0], id: "curated", content_type: "footnote_curated" },
    { ...results[1], id: "primary", content_type: "vault_extract" },
  ];
  const f = production({ FEATURE_GROUNDED_SYNTHESIS: "1" },
    async (_q, evidence) => {
      assert.equal(evidence.length, 1);
      assert.equal(evidence[0].id, "primary");
      return "verified";
    });
  assert.equal(await f("Q", mixed, async () => "", mixed[1], undefined), "verified");
});
await test("grounded synthesis abstains when only curated evidence is visible", async () => {
  const curated = [{ ...results[0], content_type: "footnote_curated" }];
  const f = production({ FEATURE_GROUNDED_SYNTHESIS: "1" },
    async () => { assert.fail("grounded helper must not run without primary evidence"); });
  assert.equal(await f("Q", curated, async () => "", undefined, undefined), decline);
});
await test("grounded evidence refills five primary slots below curated leads", async () => {
  const mixed = [
    { ...results[0], id: "curated-1", content_type: "footnote_curated" },
    { ...results[0], id: "curated-2", content_type: "approved_fact" },
    ...Array.from({ length: 5 }, (_, index) => ({
      ...results[1], id: `primary-${index}`, content_type: "vault_extract" as const,
    })),
  ];
  const f = production({ FEATURE_GROUNDED_SYNTHESIS: "1" },
    async (_q, evidence) => {
      assert.equal(evidence.length, 5);
      assert.ok(evidence.every((item) => item.content_type === "vault_extract"));
      return "verified";
    });
  assert.equal(await f("Q", mixed, async () => "", mixed[2], undefined), "verified");
});
console.log(`ALL PASS: ${count} checks`);
