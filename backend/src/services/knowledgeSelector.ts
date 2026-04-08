import type {
  KnowledgeBase,
  RoleId,
  SelectedKnowledge,
  TopicId,
} from "../types/knowledge.js";
import { MAX_INJECTED_KNOWLEDGE_CHARS } from "../types/knowledge.js";

function uniqueFacts(facts: string[]): string[] {
  return [...new Set(facts.map((fact) => fact.trim()).filter(Boolean))];
}

function getRoleFacts(topicKnowledge: KnowledgeBase[TopicId], role: RoleId): string[] {
  switch (role) {
    case "department_head":
      return uniqueFacts([
        ...(topicKnowledge.department_head ?? []),
        ...(topicKnowledge.subject_head ?? []),
        ...(topicKnowledge.panel_chair ?? []),
      ]);
    case "subject_head":
      return uniqueFacts([
        ...(topicKnowledge.subject_head ?? []),
        ...(topicKnowledge.department_head ?? []),
      ]);
    case "panel_chair":
      return uniqueFacts([
        ...(topicKnowledge.panel_chair ?? []),
        ...(topicKnowledge.department_head ?? []),
      ]);
    default:
      return uniqueFacts(topicKnowledge[role] ?? []);
  }
}

function getTopicFacts(knowledgeBase: KnowledgeBase, topic: TopicId, role: RoleId): string[] {
  const topicKnowledge = knowledgeBase[topic];
  if (!topicKnowledge) return [];

  const sharedFacts = topicKnowledge.all_roles ?? [];
  const roleFacts = role === "all_roles" ? [] : getRoleFacts(topicKnowledge, role);

  return uniqueFacts([...sharedFacts, ...roleFacts]);
}

function trimFactsToBudget(
  facts: string[],
  maxChars: number
): { usedFacts: string[]; totalCharCount: number } {
  const usedFacts: string[] = [];
  let totalCharCount = 0;

  for (const fact of facts) {
    const nextTotal = totalCharCount + fact.length;
    if (nextTotal > maxChars) {
      break;
    }

    usedFacts.push(fact);
    totalCharCount = nextTotal;
  }

  return { usedFacts, totalCharCount };
}

export function selectKnowledge(
  knowledgeBase: KnowledgeBase,
  detectedTopics: TopicId[],
  role: RoleId,
  maxChars: number = MAX_INJECTED_KNOWLEDGE_CHARS
): SelectedKnowledge {
  const orderedFacts: string[] = [];

  for (const topic of detectedTopics) {
    const topicFacts = getTopicFacts(knowledgeBase, topic, role);
    for (const fact of topicFacts) {
      if (!orderedFacts.includes(fact)) {
        orderedFacts.push(fact);
      }
    }
  }

  const { usedFacts, totalCharCount } = trimFactsToBudget(orderedFacts, maxChars);

  return {
    detectedTopics,
    usedFacts,
    totalCharCount,
  };
}
