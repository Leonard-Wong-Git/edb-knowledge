export const TOPIC_IDS = [
  "finance",
  "hr",
  "curriculum",
  "activity",
  "student",
  "it",
  "general",
] as const;

export type TopicId = (typeof TOPIC_IDS)[number];

export const ROLE_IDS = [
  "all_roles",
  "principal",
  "vice_principal",
  "department_head",
  "subject_head",
  "panel_chair",
  "teacher",
  "eo_admin",
  "supplier",
] as const;

export type RoleId = (typeof ROLE_IDS)[number];

export type FactText = string;

export interface KnowledgeSource {
  title: string;
  url: string;
  retrieved: string;
}

export interface TopicKnowledge {
  _label: string;
  _keywords_zh: string[];
  _sources?: KnowledgeSource[];
  all_roles: FactText[];
  principal?: FactText[];
  vice_principal?: FactText[];
  department_head?: FactText[];
  subject_head?: FactText[];
  panel_chair?: FactText[];
  teacher?: FactText[];
  eo_admin?: FactText[];
  supplier?: FactText[];
}

export interface KnowledgeMeta {
  version: string;
  created: string;
  updated?: string;
  description?: string;
}

export type KnowledgeBase = {
  _meta?: KnowledgeMeta;
} & Record<TopicId, TopicKnowledge>;

export interface AnalyzeCircularRequest {
  circular_text: string;
  role: RoleId;
}

export interface AnalyzeCircularResponse {
  detected_topics: TopicId[];
  used_facts: FactText[];
  similarity_scores: Partial<Record<TopicId, number>>;
  total_fact_chars: number;
  analysis: string;
}

export interface SelectedKnowledge {
  detectedTopics: TopicId[];
  usedFacts: FactText[];
  totalCharCount: number;
}

export interface PromptBuildInput {
  circularText: string;
  role: RoleId;
  detectedTopics: TopicId[];
  usedFacts: FactText[];
}

export interface TopicDetectionResult {
  topics: TopicId[];
  /** Kept for type compatibility; empty object in semantic/embedding mode. */
  matchedKeywords: Partial<Record<TopicId, string[]>>;
  /** Cosine similarity score per detected topic (only present in semantic mode). */
  similarityScores?: Partial<Record<TopicId, number>>;
}

export const MAX_FACT_CHARS = 80;
export const MAX_FACTS_PER_KEY = 5;
export const MAX_INJECTED_KNOWLEDGE_CHARS = 600;
