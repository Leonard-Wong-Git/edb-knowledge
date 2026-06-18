import OpenAI from "openai";

import { getOpenAIApiKey, getOpenAIModel } from "../config/env.js";
import { sdkFetch } from "./sdkFetch.js";

export interface LlmClientOptions {
  model?: string;
}

export function createLlmClient(options: LlmClientOptions = {}) {
  const client = new OpenAI({
    apiKey: getOpenAIApiKey(),
    fetch: sdkFetch,
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
