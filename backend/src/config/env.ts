const DEFAULT_OPENAI_MODEL = "gpt-5-nano";
const DEFAULT_PORT = 8787;
const DEFAULT_CORS_ORIGIN = "https://leonard-wong-git.github.io";
const DEFAULT_KNOWLEDGE_PATH_SETTING = "../../../role_facts.json";

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

export function getKnowledgePath(): string {
  const value = process.env.KNOWLEDGE_PATH?.trim();
  return value || DEFAULT_KNOWLEDGE_PATH_SETTING;
}

export {
  DEFAULT_CORS_ORIGIN,
  DEFAULT_KNOWLEDGE_PATH_SETTING,
  DEFAULT_OPENAI_MODEL,
  DEFAULT_PORT,
};
