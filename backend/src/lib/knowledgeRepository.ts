import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { getKnowledgePath } from "../config/env.js";
import type { KnowledgeBase } from "../types/knowledge.js";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));

export async function loadKnowledgeBase(
  knowledgePath: string = path.resolve(CURRENT_DIR, getKnowledgePath())
): Promise<KnowledgeBase> {
  const raw = await readFile(knowledgePath, "utf-8");
  return JSON.parse(raw) as KnowledgeBase;
}

export const DEFAULT_KNOWLEDGE_PATH = path.resolve(CURRENT_DIR, getKnowledgePath());
