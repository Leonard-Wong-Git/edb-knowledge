import OpenAI from "openai";

import { getOpenAIApiKey } from "../config/env.js";

/**
 * A function that takes a text string and returns its embedding vector.
 */
export type EmbedFn = (text: string) => Promise<number[]>;

const EMBEDDING_MODEL = "text-embedding-3-small";

/**
 * Creates an embedding client backed by OpenAI text-embedding-3-small.
 * The returned function accepts a single text string and resolves to its
 * embedding vector (1536 dimensions).
 */
export function createEmbeddingClient(): EmbedFn {
  const client = new OpenAI({ apiKey: getOpenAIApiKey() });

  return async function embed(text: string): Promise<number[]> {
    const response = await client.embeddings.create({
      model: EMBEDDING_MODEL,
      input: text,
    });
    return response.data[0].embedding;
  };
}
