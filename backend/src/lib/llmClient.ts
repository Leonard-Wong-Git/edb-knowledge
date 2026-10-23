import OpenAI from "openai";

import {
  getOpenAIApiKey,
  getOpenAIModel,
  getOpenAIReasoningEffort,
  type ReasoningEffort,
} from "../config/env.js";
import { sdkFetch } from "./sdkFetch.js";

export interface LlmClientOptions {
  model?: string;
  maxRetries?: number;
  /**
   * S239 — `reasoning.effort` for reasoning models. When omitted, the synthesis client
   * (no `model` override) reads OPENAI_REASONING_EFFORT; a client built with an explicit
   * `model` gets none unless the caller passes one, so the judge cannot silently inherit
   * the synthesis setting. undefined = no `reasoning` field is sent.
   */
  reasoningEffort?: ReasoningEffort;
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
  const effort =
    options.reasoningEffort ?? (options.model === undefined ? getOpenAIReasoningEffort() : undefined);

  return async function runPrompt(prompt: string, format?: LlmJsonSchema): Promise<string> {
    const response = await client.responses.create({
      model,
      input: prompt,
      // The installed SDK (4.104) types effort as low|medium|high only; the API accepts the
      // newer values (`none`, `xhigh`, `max`, per the reasoning guide, 2026-10-18) and the
      // SDK sends the body as given. Cast here rather than take a 4→7 major SDK upgrade for
      // one field.
      ...(effort ? { reasoning: { effort: effort as "low" } } : {}),
      ...(format ? { text: { format: { type: "json_schema" as const, strict: true, ...format } } } : {}),
    });

    if (format && response.status !== "completed") throw new Error("Structured response incomplete");
    return response.output_text.trim();
  };
}
