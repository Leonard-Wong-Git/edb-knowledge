import OpenAI from "openai";

import { getOpenAIApiKey, getOpenAIModel } from "../config/env.js";

export interface LlmClientOptions {
  model?: string;
}

export function createLlmClient(options: LlmClientOptions = {}) {
  const client = new OpenAI({
    apiKey: getOpenAIApiKey(),
  });

  const model = options.model ?? getOpenAIModel();

  return async function runPrompt(prompt: string): Promise<string> {
    const response = await client.responses.create({
      model,
      input: prompt,
    });

    return response.output_text.trim();
  };
}
