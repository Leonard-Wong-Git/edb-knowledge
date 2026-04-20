/**
 * factEmbeddingStore.ts — shared types & IO for pre-computed Channel A embeddings.
 *
 * The store lives at backend/data/fact_embeddings.json and is the runtime
 * source of truth for Channel A semantic search. Build it with
 * `npm run embeddings:build`; verify freshness with `npm run embeddings:verify`.
 *
 * Design:
 *   - Every approved fact in role_facts.json gets a stable id `{topic}/{role}/{index}`
 *     derived from its position in the source file.
 *   - Each entry records a sha256 text hash so drift between the source and
 *     the store is detectable without re-embedding.
 *   - Vectors are stored as plain number[] arrays (JSON). This keeps the
 *     file git-friendly enough while avoiding a binary dependency.
 */

import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import type { KnowledgeBase, TopicId } from "../types/knowledge.js";
import { TOPIC_IDS } from "../types/knowledge.js";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));

export const EMBEDDING_MODEL = "text-embedding-3-small";
export const EMBEDDING_DIM = 1536;

export const FACT_EMBEDDINGS_PATH = path.resolve(
  CURRENT_DIR,
  "../../data/fact_embeddings.json"
);

export interface FactEntry {
  id: string;
  topic: TopicId;
  role: string;
  index: number;
  text: string;
  text_hash: string;
}

export interface FactEmbeddingEntry extends FactEntry {
  vector: number[];
}

export interface FactEmbeddingFile {
  model: string;
  dim: number;
  built_at: string;
  source_meta_version: string | null;
  fact_count: number;
  entries: FactEmbeddingEntry[];
}

export function hashText(text: string): string {
  return createHash("sha256").update(text, "utf-8").digest("hex");
}

/**
 * Walk role_facts.json deterministically and emit one FactEntry per string.
 * Ordering: TOPIC_IDS × alphabetical role keys × positional index.
 * This order must be stable so entry ids are reproducible across builds.
 */
export function enumerateFacts(kb: KnowledgeBase): FactEntry[] {
  const out: FactEntry[] = [];
  for (const topic of TOPIC_IDS) {
    const topicData = kb[topic];
    if (!topicData) continue;
    const roleKeys = Object.keys(topicData)
      .filter((k) => !k.startsWith("_") && Array.isArray(topicData[k as keyof typeof topicData]))
      .sort();
    for (const role of roleKeys) {
      const facts = topicData[role as keyof typeof topicData] as unknown as string[];
      facts.forEach((text, idx) => {
        if (typeof text === "string" && text.trim()) {
          const clean = text.trim();
          out.push({
            id: `${topic}/${role}/${idx}`,
            topic,
            role,
            index: idx,
            text: clean,
            text_hash: hashText(clean),
          });
        }
      });
    }
  }
  return out;
}

export async function readEmbeddingFile(
  filePath: string = FACT_EMBEDDINGS_PATH
): Promise<FactEmbeddingFile | null> {
  try {
    const raw = await readFile(filePath, "utf-8");
    return JSON.parse(raw) as FactEmbeddingFile;
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === "ENOENT") return null;
    throw err;
  }
}

export async function writeEmbeddingFile(
  file: FactEmbeddingFile,
  filePath: string = FACT_EMBEDDINGS_PATH
): Promise<void> {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, JSON.stringify(file, null, 2) + "\n", "utf-8");
}
