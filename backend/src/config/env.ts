// S237 — aligned to production (Render OPENAI_MODEL=gpt-4o-mini, Leonard confirmed in the
// dashboard 2026-10-11). The previous default, gpt-4.1-nano, is shut down by OpenAI on
// 2026-10-23, so a missing env var would otherwise leave synthesis silently empty.
//
// S239 — gpt-4o-mini and gpt-4.1-mini are shut down on 2027-01-14 (official deprecations
// page, read 2026-10-18). Defaults move to gpt-6-luna with reasoning effort `none`:
// the cheapest current model with no announced shutdown ($0.10 in / $0.50 out per 1M,
// against $0.15/$0.60 and $0.40/$1.60), chosen as "just enough", not as the newest.
// Measured 2026-10-21 before switching (dev/source/judge_runs/2026-10-21_s239_luna_none_r*.json,
// dev/source/eval_runs/2026-10-21_s239model_*): judge frozen set 33/33 primary x3, zero false
// answers (gpt-4.1-mini: 31/33, D01 + GN10); answer-layer A/B on 36 items, 0 items favour
// the old pair; median model time per search 3.4s -> 2.8s.
const DEFAULT_OPENAI_MODEL = "gpt-6-luna";
// Sent only when the model itself is the default (see default*ReasoningEffort below): the
// non-reasoning models reject a `reasoning` field, and a rejected synthesis call is
// swallowed into an empty answer, so an explicit OPENAI_MODEL=gpt-4o-mini must keep
// working unchanged.
const DEFAULT_MODEL_REASONING_EFFORT = "none" as const;
const DEFAULT_PORT = 8787;
const DEFAULT_JUDGE_MODEL = "gpt-6-luna";
const DEFAULT_CORS_ORIGIN = "https://leonard-wong-git.github.io,https://policychecker.wongfu.net";
const DEFAULT_KNOWLEDGE_PATH_SETTING = "../../../role_facts.json";

// First-party brand origins that must ALWAYS be allowed regardless of the
// CORS_ORIGIN env var. Hardening after S136 incident: a stale Render
// `CORS_ORIGIN` env var (missing policychecker.wongfu.net) silently CORS-blocked
// all searches from the brand domain since the S132 launch. getCorsOrigins()
// now unions these in so a forgotten/misconfigured env var can never again take
// the brand domain offline. Env var can still ADD further origins (e.g. school
// iframe hosts).
const BASELINE_CORS_ORIGINS = [
  "https://leonard-wong-git.github.io",
  "https://policychecker.wongfu.net",
  // S236: the S163 here.now mirror (tender-garnet-hqbd, frozen at v3.0.0) was deleted
  // on Leonard's instruction; its origin is no longer allowed.
];

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value.trim();
}

export function getOpenAIApiKey(): string {
  return requireEnv("OPENAI_API_KEY");
}

export function getOpenAIModel(): string {
  const value = process.env.OPENAI_MODEL?.trim();
  return value || DEFAULT_OPENAI_MODEL;
}

/**
 * S211 — the relevance judge runs on its own model, separate from OPENAI_MODEL.
 *
 * Measured on the frozen acceptance set (dev/source/judge_acceptance.py, 2026-09-01),
 * gpt-4.1-mini against the shipped gpt-4o-mini: primary 31/33 on both, answer half 12/12
 * on both, decline half 19/21 on both with THE SAME two false answers (D01, GN10) — no new
 * confabulation — and 33/35 vs 31/35 once the bare-noun cases are counted, i.e. it fixes
 * S01 and S02. It also answers the S211 qualification query that no rewrite of the prompt
 * could get gpt-4o-mini to accept.
 *
 * Split rather than switching OPENAI_MODEL because synthesis quality was NOT measured here
 * and the judge is the cheap call: ~1,910 input tokens and one output token, so the whole
 * change costs about US$0.0005 per query (US$0.48/month at a thousand queries). Moving
 * synthesis too would nearly triple its cost on no evidence.
 *
 * S239 — the default is now gpt-6-luna with effort `none` (see the top of this file): on
 * the same frozen set it scored 33/33 primary in three runs with zero false answers, i.e.
 * it also closes D01 and GN10. The split is kept, so the two can still be set apart.
 */
export function getJudgeModel(): string {
  const value = process.env.JUDGE_MODEL?.trim();
  return value || DEFAULT_JUDGE_MODEL;
}

export function getPort(): number {
  const value = process.env.PORT?.trim();
  return value ? Number(value) : DEFAULT_PORT;
}

export function getCorsOrigin(): string {
  const value = process.env.CORS_ORIGIN?.trim();
  return value || DEFAULT_CORS_ORIGIN;
}

export function getCorsOrigins(): string[] {
  const fromEnv = getCorsOrigin()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  // Union first-party brand origins with env-configured origins (baseline first
  // so it cannot be dropped by a stale env var), deduped, order preserved.
  const seen = new Set<string>();
  const merged: string[] = [];
  for (const origin of [...BASELINE_CORS_ORIGINS, ...fromEnv]) {
    if (!seen.has(origin)) {
      seen.add(origin);
      merged.push(origin);
    }
  }
  return merged;
}

export function getKnowledgePath(): string {
  const value = process.env.KNOWLEDGE_PATH?.trim();
  return value || DEFAULT_KNOWLEDGE_PATH_SETTING;
}

/**
 * Non-throwing check for whether Channel B (Supabase pgvector) is configured.
 * Returns false when SUPABASE_URL or SUPABASE_ANON_KEY is missing/empty so
 * callers can degrade gracefully instead of throwing.
 */
export function isSupabaseConfigured(): boolean {
  const url = process.env.SUPABASE_URL?.trim();
  const key = process.env.SUPABASE_ANON_KEY?.trim();
  return Boolean(url && key);
}

export function getSupabaseUrl(): string {
  const value = process.env.SUPABASE_URL?.trim();
  if (!value) throw new Error("Missing required environment variable: SUPABASE_URL");
  return value;
}

export function getSupabaseAnonKey(): string {
  const value = process.env.SUPABASE_ANON_KEY?.trim();
  if (!value) throw new Error("Missing required environment variable: SUPABASE_ANON_KEY");
  return value;
}

/**
 * Channel B incremental-sync read keys (Q4 Phase 2; CHANNEL_B_SYNC_SPEC.md §6).
 * Comma-separated to support rotation (multiple valid keys during a swap).
 * Returns [] when unset/empty so the sync endpoints can fail closed with 503
 * (sync disabled) rather than throwing. Never log these values.
 */
export function getChannelBSyncKeys(): string[] {
  const value = process.env.CHANNEL_B_SYNC_KEY?.trim();
  if (!value) return [];
  return value.split(",").map((s) => s.trim()).filter(Boolean);
}

export function isChannelBSyncEnabled(): boolean {
  return getChannelBSyncKeys().length > 0;
}

export {
  DEFAULT_CORS_ORIGIN,
  DEFAULT_KNOWLEDGE_PATH_SETTING,
  DEFAULT_OPENAI_MODEL,
  DEFAULT_PORT,
};

/**
 * S239 — reasoning effort for reasoning models (e.g. gpt-6-luna, which defaults to
 * `medium`). OpenAI bills reasoning tokens as output and counts them against
 * max_output_tokens, so a yes/no judge left on the default can spend more on hidden
 * reasoning than on its answer, and every call gets slower. Unset or unrecognised =
 * undefined = the request carries no `reasoning` field at all, i.e. byte-identical to
 * before. A typo is ignored rather than sent, because the non-reasoning models in
 * production today (gpt-4o-mini, gpt-4.1-mini) reject the parameter.
 * Allowed values per https://developers.openai.com/api/docs/guides/reasoning (2026-10-18).
 */
export const REASONING_EFFORTS = ["none", "minimal", "low", "medium", "high", "xhigh", "max"] as const;
export type ReasoningEffort = (typeof REASONING_EFFORTS)[number];

export function reasoningEffortFromEnv(raw: string | undefined): ReasoningEffort | undefined {
  const v = raw?.trim().toLowerCase();
  return (REASONING_EFFORTS as readonly string[]).includes(v ?? "") ? (v as ReasoningEffort) : undefined;
}

/**
 * Synthesis client: OPENAI_REASONING_EFFORT when set and valid; otherwise `none` if (and
 * only if) the model is the code default, else nothing is sent.
 */
export function getOpenAIReasoningEffort(): ReasoningEffort | undefined {
  const explicit = reasoningEffortFromEnv(process.env.OPENAI_REASONING_EFFORT);
  if (explicit) return explicit;
  return process.env.OPENAI_MODEL?.trim() ? undefined : DEFAULT_MODEL_REASONING_EFFORT;
}

/** Relevance judge client: JUDGE_REASONING_EFFORT, same rule against JUDGE_MODEL. */
export function getJudgeReasoningEffort(): ReasoningEffort | undefined {
  const explicit = reasoningEffortFromEnv(process.env.JUDGE_REASONING_EFFORT);
  if (explicit) return explicit;
  return process.env.JUDGE_MODEL?.trim() ? undefined : DEFAULT_MODEL_REASONING_EFFORT;
}
