import OpenAI from "openai";

import { getOpenAIApiKey } from "../config/env.js";
import { sdkFetch } from "./sdkFetch.js";

/**
 * A function that takes a text string and returns its embedding vector.
 */
export type EmbedFn = (text: string) => Promise<number[]>;

/**
 * A function that takes an array of strings and returns their embedding vectors
 * in a single API call (up to 2,048 inputs per call).
 */
export type BatchEmbedFn = (texts: string[]) => Promise<number[][]>;

const EMBEDDING_MODEL = "text-embedding-3-small";

/**
 * Creates an embedding client backed by OpenAI text-embedding-3-small.
 * Returns both a single-embed function and a batch-embed function.
 *
 * The batch function sends all texts in a single API call, which is far
 * more efficient than calling the single function in a Promise.all loop.
 */
export function createEmbeddingClient(): EmbedFn & { batch: BatchEmbedFn } {
  const client = new OpenAI({ apiKey: getOpenAIApiKey(), fetch: sdkFetch });

  const embed = async function embed(text: string): Promise<number[]> {
    const response = await client.embeddings.create({
      model: EMBEDDING_MODEL,
      input: text,
    });
    return response.data[0].embedding;
  };

  embed.batch = async function batchEmbed(texts: string[]): Promise<number[][]> {
    if (texts.length === 0) return [];
    // OpenAI supports up to 2,048 inputs per request; chunk if needed
    const BATCH_SIZE = 2048;
    const results: number[][] = [];
    for (let i = 0; i < texts.length; i += BATCH_SIZE) {
      const chunk = texts.slice(i, i + BATCH_SIZE);
      const response = await client.embeddings.create({
        model: EMBEDDING_MODEL,
        input: chunk,
      });
      // Sort by index to guarantee order
      const sorted = response.data.sort((a, b) => a.index - b.index);
      results.push(...sorted.map((d) => d.embedding));
    }
    return results;
  };

  return embed;
}
