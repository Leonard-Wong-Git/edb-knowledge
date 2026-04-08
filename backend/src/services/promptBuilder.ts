import type { PromptBuildInput } from "../types/knowledge.js";

function formatTopics(topics: string[]): string {
  return topics.length > 0 ? topics.join(", ") : "general";
}

function formatFacts(facts: string[]): string {
  if (facts.length === 0) {
    return "沒有可注入的已審批知識。";
  }

  return facts.map((fact, index) => `${index + 1}. ${fact}`).join("\n");
}

export function buildKnowledgePrompt(input: PromptBuildInput): string {
  const { circularText, role, detectedTopics, usedFacts } = input;

  return [
    "你是香港教育局通告分析助手。",
    "以下「已審批知識」只可作為顧問層背景，用來協助理解角色責任、政策重點與執行建議。",
    "不可把這些知識當作自動適用於所有通告的硬性結論；若知識不足，必須以通告原文為準並保守回答。",
    "不可捏造不存在於通告或已審批知識中的規則、金額、時限或程序。",
    "",
    `目標角色：${role}`,
    `偵測主題：${formatTopics(detectedTopics)}`,
    "",
    "已審批知識：",
    formatFacts(usedFacts),
    "",
    "請根據以下教育局通告內容，輸出清晰、可執行的分析：",
    "1. 這份通告對該角色的主要影響",
    "2. 該角色需要採取的具體行動",
    "3. 如有不確定之處，明確指出哪些內容需要人工核實",
    "",
    "通告內容：",
    circularText.trim(),
  ].join("\n");
}
