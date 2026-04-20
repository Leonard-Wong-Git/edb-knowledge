/**
 * verifyFactEmbeddings.ts — detect drift between role_facts.json and the
 * precomputed embedding store without calling OpenAI.
 *
 * Runtime: `npm run embeddings:verify` — exits 1 on drift so CI can gate merges.
 *
 * Checks:
 *   A. Store file exists, has the expected model and dimension.
 *   B. Every source fact has an entry; no stale entries remain.
 *   C. Every entry's text_hash matches the source.
 *   D. Every entry's vector has length EMBEDDING_DIM.
 */

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  EMBEDDING_DIM,
  EMBEDDING_MODEL,
  FACT_EMBEDDINGS_PATH,
  enumerateFacts,
  readEmbeddingFile,
} from "../src/lib/factEmbeddingStore.js";
import type { KnowledgeBase } from "../src/types/knowledge.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const ROLE_FACTS_PATH = path.resolve(REPO_ROOT, "role_facts.json");

async function main(): Promise<void> {
  console.log(`# verifyFactEmbeddings`);
  console.log(`source: ${path.relative(REPO_ROOT, ROLE_FACTS_PATH)}`);
  console.log(`store:  ${path.relative(REPO_ROOT, FACT_EMBEDDINGS_PATH)}`);
  console.log("");

  const raw = await readFile(ROLE_FACTS_PATH, "utf-8");
  const kb = JSON.parse(raw) as KnowledgeBase;
  const facts = enumerateFacts(kb);

  const store = await readEmbeddingFile();
  if (!store) {
    console.error(`❌  store file missing — run: npm run embeddings:build`);
    process.exitCode = 1;
    return;
  }

  const problems: string[] = [];

  if (store.model !== EMBEDDING_MODEL) {
    problems.push(
      `model mismatch: store=${store.model} expected=${EMBEDDING_MODEL}`
    );
  }
  if (store.dim !== EMBEDDING_DIM) {
    problems.push(`dim mismatch: store=${store.dim} expected=${EMBEDDING_DIM}`);
  }

  const storeById = new Map(store.entries.map((e) => [e.id, e]));
  const sourceIds = new Set(facts.map((f) => f.id));

  let hashMismatch = 0;
  let missing = 0;
  let vectorWrong = 0;
  for (const fact of facts) {
    const entry = storeById.get(fact.id);
    if (!entry) {
      missing++;
      if (missing <= 3) problems.push(`missing entry: ${fact.id}`);
      continue;
    }
    if (entry.text_hash !== fact.text_hash) {
      hashMismatch++;
      if (hashMismatch <= 3)
        problems.push(
          `hash drift: ${fact.id} store=${entry.text_hash.slice(0, 10)} source=${fact.text_hash.slice(0, 10)}`
        );
    }
    if (!Array.isArray(entry.vector) || entry.vector.length !== EMBEDDING_DIM) {
      vectorWrong++;
      if (vectorWrong <= 3)
        problems.push(
          `bad vector: ${fact.id} dim=${entry.vector?.length ?? "none"}`
        );
    }
  }

  const stale = store.entries.filter((e) => !sourceIds.has(e.id)).length;
  if (stale > 0) problems.push(`${stale} stale store entries not in source`);

  console.log(`source facts:        ${facts.length}`);
  console.log(`store entries:       ${store.entries.length}`);
  console.log(`missing entries:     ${missing}`);
  console.log(`hash mismatches:     ${hashMismatch}`);
  console.log(`bad-dim vectors:     ${vectorWrong}`);
  console.log(`stale store entries: ${stale}`);
  console.log(`store model:         ${store.model}`);
  console.log(`store built_at:      ${store.built_at}`);
  console.log(`store source_meta:   ${store.source_meta_version ?? "(none)"}`);

  if (problems.length > 0) {
    console.log("");
    console.error(`❌  verification failed (${problems.length} problems):`);
    for (const p of problems.slice(0, 10)) console.error(`   - ${p}`);
    if (problems.length > 10) console.error(`   ... and ${problems.length - 10} more`);
    console.error("");
    console.error(`fix: run 'npm run embeddings:build'`);
    process.exitCode = 1;
    return;
  }

  console.log("");
  console.log(`✅  store is in sync with role_facts.json`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
