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

/**
 * Round-robin interleave of two ordered pools.
 *
 * When the knowledge base grew from 109 to 1,001 facts, several topics'
 * `all_roles` pools became large enough (e.g. finance = 1,194 chars, hr =
 * 2,045 chars) to saturate the character budget on their own. That
 * starved every role-specific pool of slots and made role-aware selection
 * collapse — subject_head and panel_chair would receive identical facts.
 *
 * Interleaving preserves the "baseline first" intent (all_roles still
 * leads) while guaranteeing role-specific facts a seat whenever the pool
 * has content, regardless of how large the all_roles pool grows.
 */
function interleave(primary: string[], secondary: string[]): string[] {
  const out: string[] = [];
  const len = Math.max(primary.length, secondary.length);
  for (let i = 0; i < len; i++) {
    if (i < primary.length) out.push(primary[i]);
    if (i < secondary.length) out.push(secondary[i]);
  }
  return out;
}

function getTopicFacts(knowledgeBase: KnowledgeBase, topic: TopicId, role: RoleId): string[] {
  const topicKnowledge = knowledgeBase[topic];
  if (!topicKnowledge) return [];

  const sharedFacts = topicKnowledge.all_roles ?? [];
  if (role === "all_roles") {
    return uniqueFacts(sharedFacts);
  }

  const roleFacts = getRoleFacts(topicKnowledge, role);
  return uniqueFacts(interleave(sharedFacts, roleFacts));
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
