const DEFAULT_OPENAI_MODEL = "gpt-4.1-nano";
const DEFAULT_PORT = 8787;
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

export {
  DEFAULT_CORS_ORIGIN,
  DEFAULT_KNOWLEDGE_PATH_SETTING,
  DEFAULT_OPENAI_MODEL,
  DEFAULT_PORT,
};
