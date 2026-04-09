import type { EmbedFn } from "../lib/embeddingClient.js";
import { loadKnowledgeBase } from "../lib/knowledgeRepository.js";
import { selectKnowledge } from "../services/knowledgeSelector.js";
import { buildKnowledgePrompt } from "../services/promptBuilder.js";
import { detectTopics } from "../services/topicDetector.js";
import type {
  AnalyzeCircularRequest,
  AnalyzeCircularResponse,
  RoleId,
} from "../types/knowledge.js";
import { ROLE_IDS } from "../types/knowledge.js";

export interface AnalyzeCircularDependencies {
  llmClient: (prompt: string) => Promise<string>;
  embeddingClient: EmbedFn;
}

function assertValidRequest(input: AnalyzeCircularRequest): void {
  if (!input.circular_text || !input.circular_text.trim()) {
    throw new Error("Invalid request: circular_text is required.");
  }

  if (!ROLE_IDS.includes(input.role as RoleId)) {
    throw new Error("Invalid request: role is not supported.");
  }
}

export async function analyzeCircular(
  input: AnalyzeCircularRequest,
  dependencies: AnalyzeCircularDependencies
): Promise<AnalyzeCircularResponse> {
  assertValidRequest(input);

  const knowledgeBase = await loadKnowledgeBase();

  // Semantic topic detection via embedding cosine similarity
  const detection = await detectTopics(input.circular_text, dependencies.embeddingClient);

  const selection = selectKnowledge(knowledgeBase, detection.topics, input.role);
  const prompt = buildKnowledgePrompt({
    circularText: input.circular_text,
    role: input.role,
    detectedTopics: selection.detectedTopics,
    usedFacts: selection.usedFacts,
  });

  const analysis = await dependencies.llmClient(prompt);

  return {
    detected_topics: selection.detectedTopics,
    used_facts: selection.usedFacts,
    similarity_scores: detection.similarityScores ?? {},
    total_fact_chars: selection.totalCharCount,
    analysis,
  };
}
