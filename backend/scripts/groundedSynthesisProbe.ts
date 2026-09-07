import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { performance } from "node:perf_hooks";
import { createHash } from "node:crypto";
import { selectPrimaryEvidence, synthesizeGroundedAnswer } from "../src/lib/groundedSynthesis.js";
import { createLlmClient } from "../src/lib/llmClient.js";
import { getJudgeModel, getOpenAIModel } from "../src/config/env.js";

const nine = process.argv.includes("--nine");
const acceptance = process.argv.includes("--acceptance");
const affectedAcceptance = process.argv.includes("--acceptance-affected");
if ([nine, acceptance, affectedAcceptance].filter(Boolean).length > 1) {
  throw new Error("Choose only one probe mode.");
}
if (acceptance) {
  throw new Error(
    "The 40-case acceptance fixture contains deprecated NCS gold. Build a replacement retrieval fixture before running a new full acceptance batch.",
  );
}
const repetitions = nine || acceptance || affectedAcceptance ? 1 : 3;
const caseCount = acceptance ? 40 : affectedAcceptance ? 18 : nine ? 9 : 5;
const maximumCalls = repetitions * caseCount * 2;
const approvedCallsArg = process.argv.find((arg) => arg.startsWith("--approved-max-calls="));
const approvedCalls = Number(approvedCallsArg?.slice("--approved-max-calls=".length));
if (!process.argv.includes("--run") || !Number.isInteger(approvedCalls) || approvedCalls < maximumCalls) {
  throw new Error(
    `External API approval required before execution: use --run --approved-max-calls=${maximumCalls} only after Leonard approves this exact batch. Claude must not run this probe.`,
  );
}
const fixture = new URL(acceptance || affectedAcceptance
  ? "../../dev/source/eval_runs/2026-09-04_s214_synthesis.json"
  : nine
    ? "../../dev/source/eval_runs/2026-09-04_s214_user_nine_questions.json"
    : "../../dev/source/eval_runs/2026-09-05_s214_gate2a2_local_synthesis.json", import.meta.url);
const label = process.argv.find((arg) => arg.startsWith("--label="))?.slice(8) ?? "v1";
if (!/^[a-z0-9_]+$/.test(label)) throw new Error("Invalid label");
const output = new URL(`../../dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_${label}.json`, import.meta.url);
if (existsSync(output)) throw new Error("Output already exists; preserve prior evidence.");
const baseline = JSON.parse(readFileSync(fixture, "utf8"));
const activeGold = affectedAcceptance
  ? JSON.parse(readFileSync(new URL("../../dev/_s213_gold_all.json", import.meta.url), "utf8"))
  : [];
const ids: string[] = acceptance
  ? [
      ...baseline.results.filter((r: { cohort: string }) => r.cohort === "no_answer").map((r: { id: string }) => r.id),
      "ss_ncs_history_adapted",
      ...baseline.results.filter((r: { cohort: string }) => r.cohort === "positive_control").map((r: { id: string }) => r.id),
      "sen_special_school_curriculum",
    ]
  : affectedAcceptance
    ? [
        "staff_sp_school", "hr_teacher_reg_fee", "fin_crypto", "hr_overtime",
        "ss_ncs_fee_remission_missing", "bus_fee_noans", "act_eca_min_hours_na",
        "cpd_induction_period_na", "qa_kg_pi_na", "staff_fullday_12", "hr_lsp",
        "fin_lwl", "gov_imc_60pct", "hr_lang_req", "cur_kg_free_play_time",
        "saf_disease_notification", "staff_halfday_12", "sen_special_school_curriculum",
      ]
  : nine ? baseline.results.map((r: { id: string }) => r.id)
    : ["staff_fullday_12", "staff_halfday_12", "staff_fullday_24", "gov_board_pay", "kg_sccc_ratio_confusable"];
if (ids.length !== caseCount || new Set(ids).size !== ids.length) throw new Error("Acceptance case selection drifted.");
// The user-approved cap is an HTTP-attempt cap, not merely a logical-call
// estimate. Probe clients disable SDK retries so one callback equals one HTTP
// request attempt; production clients retain their existing retry policy.
const draft = createLlmClient({ maxRetries: 0 });
const judge = createLlmClient({ model: getJudgeModel(), maxRetries: 0 });
const decline = "TEST_DECLINE";
const report = {
  generated_at: new Date().toISOString(),
  synthesis_model: getOpenAIModel(), judge_model: getJudgeModel(),
  scope: "Saved evidence only; no new retrieval or database access. Production-equivalent primary-evidence selection. Staffing uses its exact source only. Semantic outcomes require manual review.",
  repetitions,
  approved_max_calls: approvedCalls,
  attempted_api_calls: 0,
  results: [] as Record<string, unknown>[],
};
async function paidCall(
  stage: string,
  client: ReturnType<typeof createLlmClient>,
  prompt: string,
  format: Parameters<ReturnType<typeof createLlmClient>>[1],
) {
  if (report.attempted_api_calls >= approvedCalls) throw new Error("Approved API call cap reached");
  report.attempted_api_calls++;
  writeFileSync(output, JSON.stringify(report, null, 2) + "\n");
  const text = await client(prompt, format);
  return { stage, output: text };
}
console.log(JSON.stringify({ synthesis_model: report.synthesis_model, judge_model: report.judge_model }));
for (let repetition = 1; repetition <= report.repetitions; repetition++) {
  for (const id of ids) {
    const original = baseline.results.find((r: { id: string }) => r.id === id);
    if (!original?.results?.length) throw new Error(`Missing evidence: ${id}`);
    const gold = activeGold.find((item: { id: string }) => item.id === id);
    if (affectedAcceptance && !gold) throw new Error(`Missing active gold: ${id}`);
    const query = gold?.query ?? original.query;
    // Production evidence policy A: curated summaries may retrieve, but
    // only verbatim EDB extracts may support a rendered answer.
    const evidence = selectPrimaryEvidence(original.results
      .filter((r: { source_id: string }) => !id.startsWith("staff_") || r.source_id === "staff_est_pri"));
    const evidenceWindowFingerprint = createHash("sha256")
      .update(JSON.stringify(evidence.map((item: { id: string; source_id: string; content_type: string; text: string }) =>
        ({ id: item.id, source_id: item.source_id, content_type: item.content_type, text: item.text }))))
      .digest("hex");
    const calls: { stage: string; output: string }[] = [];
    const start = performance.now();
    const answer = await synthesizeGroundedAnswer(query, evidence,
      async (prompt, format) => { const call = await paidCall("draft", draft, prompt, format); calls.push(call); return call.output; },
      async (prompt, format) => { const call = await paidCall("judge", judge, prompt, format); calls.push(call); return call.output; },
      decline);
    const row = { id, repetition, query, evidence_origin_query: original.query,
      expected_answerable: gold?.answerable ?? original.answerable ?? null,
      cohort: original.cohort ?? (nine ? "user_nine" : "focused"),
      intent: gold?.intent ?? original.intent ?? null,
      expected_source_any: gold?.expected_source_any ?? original.expected_source_any ?? [],
      forbidden_evidence: gold?.forbidden_evidence ?? original.forbidden_evidence ?? [],
      evidence, evidence_window_fingerprint: evidenceWindowFingerprint, baseline_answer: original.synthesis,
      answer, calls, elapsed_ms: Math.round(performance.now() - start), manual_review: null };
    report.results.push(row);
    writeFileSync(output, JSON.stringify(report, null, 2) + "\n");
    console.log(JSON.stringify({ id, repetition, answer, elapsed_ms: row.elapsed_ms }));
  }
}
console.log(`Recorded ${report.results.length} runs; manual semantic QC required.`);
