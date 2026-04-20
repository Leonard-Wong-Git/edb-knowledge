/**
 * buildFactEmbeddings.ts — precompute OpenAI embeddings for every Channel A fact.
 *
 * Runtime: `npm run embeddings:build` (requires OPENAI_API_KEY).
 *
 * Strategy:
 *   1. Load repo-root role_facts.json (backend SSOT) and enumerate facts.
 *   2. Load existing backend/data/fact_embeddings.json if present.
 *   3. Reuse vectors whose (id, text_hash) pair is unchanged.
 *   4. Batch-embed the rest via OpenAI (batches of EMBEDDING_BATCH_SIZE).
 *   5. Drop entries whose ids no longer appear in the source.
 *   6. Write the new file and print a reuse / rebuild summary.
 *
 * Cost reference: text-embedding-3-small ≈ US$0.02 / 1M tokens.
 * Full rebuild of ~1,000 facts × ~150 tokens ≈ 150K tokens ≈ US$0.003.
 */

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import OpenAI from "openai";

import {
  EMBEDDING_DIM,
  EMBEDDING_MODEL,
  FACT_EMBEDDINGS_PATH,
  enumerateFacts,
  readEmbeddingFile,
  writeEmbeddingFile,
  type FactEmbeddingEntry,
  type FactEmbeddingFile,
  type FactEntry,
} from "../src/lib/factEmbeddingStore.js";
import type { KnowledgeBase } from "../src/types/knowledge.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const ROLE_FACTS_PATH = path.resolve(REPO_ROOT, "role_facts.json");

const EMBEDDING_BATCH_SIZE = 64;

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value.trim();
}

async function embedBatch(
  client: OpenAI,
  inputs: string[]
): Promise<number[][]> {
  if (inputs.length === 0) return [];
  const response = await client.embeddings.create({
    model: EMBEDDING_MODEL,
    input: inputs,
  });
  return response.data.map((d) => d.embedding);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const forceAll = args.includes("--force");
  const dryRun = args.includes("--dry-run");

  console.log(`# buildFactEmbeddings`);
  console.log(`source:     ${path.relative(REPO_ROOT, ROLE_FACTS_PATH)}`);
  console.log(`target:     ${path.relative(REPO_ROOT, FACT_EMBEDDINGS_PATH)}`);
  console.log(`model:      ${EMBEDDING_MODEL}`);
  console.log(`force:      ${forceAll ? "yes (re-embed all)" : "no (incremental)"}`);
  console.log(`dry-run:    ${dryRun ? "yes (no writes, no API calls)" : "no"}`);
  console.log("");

  const raw = await readFile(ROLE_FACTS_PATH, "utf-8");
  const kb = JSON.parse(raw) as KnowledgeBase;
  const sourceMetaVersion = kb._meta?.version ?? null;

  const facts: FactEntry[] = enumerateFacts(kb);
  console.log(`source fact count:         ${facts.length}`);
  console.log(`source _meta.version:      ${sourceMetaVersion ?? "(none)"}`);

  const existing = await readEmbeddingFile();
  const byId = new Map<string, FactEmbeddingEntry>();
  if (existing) {
    for (const entry of existing.entries) byId.set(entry.id, entry);
    console.log(`existing store entries:    ${existing.entries.length}`);
    console.log(`existing built_at:         ${existing.built_at}`);
  } else {
    console.log(`existing store entries:    0 (no prior file)`);
  }

  const reused: FactEmbeddingEntry[] = [];
  const toEmbed: FactEntry[] = [];

  for (const fact of facts) {
    if (!forceAll) {
      const prior = byId.get(fact.id);
      if (prior && prior.text_hash === fact.text_hash && Array.isArray(prior.vector) && prior.vector.length === EMBEDDING_DIM) {
        reused.push({ ...prior, text: fact.text });
        continue;
      }
    }
    toEmbed.push(fact);
  }

  const sourceIds = new Set(facts.map((f) => f.id));
  const droppedCount = existing
    ? existing.entries.filter((e) => !sourceIds.has(e.id)).length
    : 0;

  console.log("");
  console.log(`reused (hash unchanged):   ${reused.length}`);
  console.log(`to embed (new or changed): ${toEmbed.length}`);
  console.log(`dropped (stale ids):       ${droppedCount}`);

  if (dryRun) {
    console.log("");
    console.log("dry-run — no OpenAI calls, no file writes.");
    return;
  }

  let newlyEmbedded: FactEmbeddingEntry[] = [];
  if (toEmbed.length > 0) {
    const apiKey = requireEnv("OPENAI_API_KEY");
    const client = new OpenAI({ apiKey });
    console.log("");
    console.log(`embedding in batches of ${EMBEDDING_BATCH_SIZE}...`);
    for (let i = 0; i < toEmbed.length; i += EMBEDDING_BATCH_SIZE) {
      const batch = toEmbed.slice(i, i + EMBEDDING_BATCH_SIZE);
      const vectors = await embedBatch(
        client,
        batch.map((f) => f.text)
      );
      for (let j = 0; j < batch.length; j++) {
        const fact = batch[j];
        const vector = vectors[j];
        if (!vector || vector.length !== EMBEDDING_DIM) {
          throw new Error(
            `Unexpected embedding dimension for ${fact.id}: got ${vector?.length}, want ${EMBEDDING_DIM}`
          );
        }
        newlyEmbedded.push({ ...fact, vector });
      }
      const done = Math.min(i + EMBEDDING_BATCH_SIZE, toEmbed.length);
      console.log(`  progress: ${done}/${toEmbed.length}`);
    }
  }

  const merged = new Map<string, FactEmbeddingEntry>();
  for (const entry of reused) merged.set(entry.id, entry);
  for (const entry of newlyEmbedded) merged.set(entry.id, entry);

  const ordered: FactEmbeddingEntry[] = facts.map((fact) => {
    const entry = merged.get(fact.id);
    if (!entry) {
      throw new Error(`Missing embedding for ${fact.id} after build`);
    }
    return entry;
  });

  const out: FactEmbeddingFile = {
    model: EMBEDDING_MODEL,
    dim: EMBEDDING_DIM,
    built_at: new Date().toISOString(),
    source_meta_version: sourceMetaVersion,
    fact_count: ordered.length,
    entries: ordered,
  };

  await writeEmbeddingFile(out);
  console.log("");
  console.log(`wrote ${ordered.length} entries → ${path.relative(REPO_ROOT, FACT_EMBEDDINGS_PATH)}`);
  console.log(`done.`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
