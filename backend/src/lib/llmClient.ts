import OpenAI from "openai";

import { getOpenAIApiKey, getOpenAIModel } from "../config/env.js";
import { sdkFetch } from "./sdkFetch.js";

export interface LlmClientOptions {
  model?: string;
  maxRetries?: number;
}

export interface LlmJsonSchema {
  name: string;
  schema: Record<string, unknown>;
}

export function createLlmClient(options: LlmClientOptions = {}) {
  const client = new OpenAI({
    apiKey: getOpenAIApiKey(),
    ...(options.maxRetries !== undefined ? { maxRetries: options.maxRetries } : {}),
    fetch: sdkFetch,
  });

  const model = options.model ?? getOpenAIModel();

  return async function runPrompt(prompt: string, format?: LlmJsonSchema): Promise<string> {
    const response = await client.responses.create({
      model,
      input: prompt,
      ...(format ? { text: { format: { type: "json_schema" as const, strict: true, ...format } } } : {}),
    });

    if (format && response.status !== "completed") throw new Error("Structured response incomplete");
    return response.output_text.trim();
  };
}
