const DEFAULT_OPENAI_MODEL = "gpt-4.1-nano";
const DEFAULT_PORT = 8787;
const DEFAULT_JUDGE_MODEL = "gpt-4.1-mini";
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
  // S163QC: frontend mirror on here.now (repo set private → GitHub Pages free
  // unpublished; static site re-hosted here, permanent). Exact origin (no trailing
  // slash, matching the browser Origin header). Add a new line if the slug changes.
  "https://tender-garnet-hqbd.here.now",
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
