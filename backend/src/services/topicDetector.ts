import type { EmbedFn } from "../lib/embeddingClient.js";
import type { TopicDetectionResult, TopicId } from "../types/knowledge.js";

// ---------------------------------------------------------------------------
// Topic anchor texts (Traditional Chinese) — one rich descriptive string per
// topic.  These are embedded once on first request and cached for the life of
// the server process.  Keeping them here rather than in the knowledge JSON
// lets us tune them independently of the knowledge base content.
// ---------------------------------------------------------------------------
const TOPIC_ANCHORS: Partial<Record<TopicId, string>> = {
  finance:
    "財務管理 採購程序 津貼申請 學校開支 供應商報價 競投 採購指引 財務核准 撥款 特別津貼 書簿津貼 公開招標 審計 報帳",
  hr:
    "教師培訓 持續專業發展 CPD 員工假期 招聘程序 合約教師 代課教師 薪酬 人力資源 教師資歷 晉升 負擔 離職 強積金",
  curriculum:
    "課程規劃 學習目標 課程架構 評估 學習成果 課程改革 學科 學業成績 學習領域 課程指引 課程發展 共同備課 課時 評核",
  activity:
    "課外活動 境外遊學 戶外學習 學生活動 活動審批 校外活動 參觀 陸上運動 水上活動 遠足 學生旅行 全方位學習 交流團",
  student:
    "學生紀律 行為問題 學生支援 學生事務 學生福利 輔導 操行 體罰 家長 學生訓導 學生管理 危機處理 欺凌 傳染病 SEN",
  it:
    "資訊科技 學校資訊系統 網絡安全 數據保護 BYOD 電腦設備 資訊保安 學校電腦 雲端 資訊系統管理 軟件更新 寬頻",
};

// Minimum cosine similarity for a topic to be considered detected.
// Tunable: lower → more recall, higher → more precision.
const SIMILARITY_THRESHOLD = 0.45;

// Anti-contamination controls — applied after threshold filtering:
//   MAX_TOPICS  : hard cap on the number of returned topics.
//   SCORE_GAP   : secondary topics must score within this margin of the top
//                 topic.  Topics whose score drops further are treated as noise.
// Together these prevent low-signal secondary topics from filling the 600-char
// fact budget when a circular is clearly dominated by a single topic.
const MAX_TOPICS = 2;
const SCORE_GAP  = 0.05;

// ---------------------------------------------------------------------------
// Module-level cache — populated lazily on the first detectTopics call and
// reused for the entire server process lifetime (no re-embedding needed).
// ---------------------------------------------------------------------------
let _anchorEmbeddings: Map<TopicId, number[]> | null = null;

/**
 * Compute and cache anchor embeddings (called at most once per process).
 * Embeddings are fetched in parallel using Promise.all.
 */
async function getAnchorEmbeddings(embed: EmbedFn): Promise<Map<TopicId, number[]>> {
  if (_anchorEmbeddings !== null) return _anchorEmbeddings;

  const entries = Object.entries(TOPIC_ANCHORS) as Array<[TopicId, string]>;
  const vectors = await Promise.all(entries.map(([, text]) => embed(text)));

  _anchorEmbeddings = new Map<TopicId, number[]>(
    entries.map(([topicId], i): [TopicId, number[]] => [topicId, vectors[i]])
  );
  return _anchorEmbeddings;
}

/**
 * Cosine similarity between two equal-length vectors.
 * Returns a value in [-1, 1]; higher means more similar.
 */
function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot   += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Detects relevant topics for a given circular text using embedding-based
 * semantic similarity against pre-defined topic anchor texts.
 *
 * @param circularText - The full text of the EDB circular to analyse.
 * @param embed        - An embedding function (text → vector).
 * @returns A TopicDetectionResult with topics sorted by descending similarity.
 */
export async function detectTopics(
  circularText: string,
  embed: EmbedFn
): Promise<TopicDetectionResult> {
  const [queryVector, anchors] = await Promise.all([
    embed(circularText),
    getAnchorEmbeddings(embed),
  ]);

  const scored: Array<{ topic: TopicId; score: number }> = [];

  for (const [topic, anchorVector] of anchors.entries()) {
    const score = cosineSimilarity(queryVector, anchorVector);
    if (score >= SIMILARITY_THRESHOLD) {
      scored.push({ topic, score });
    }
  }

  // Highest similarity first
  scored.sort((a, b) => b.score - a.score);

  // Apply anti-contamination filters:
  //   1. Score-gap filter  — keep only topics within SCORE_GAP of the top score.
  //   2. MAX_TOPICS cap    — never return more than MAX_TOPICS topics.
  // similarityScores exposes ALL above-threshold scores for diagnostics; only
  // the filtered set is passed downstream for fact selection.
  const filteredScored =
    scored.length > 0
      ? scored
          .filter((s) => s.score >= scored[0].score - SCORE_GAP)
          .slice(0, MAX_TOPICS)
      : [];

  const topics: TopicId[] =
    filteredScored.length > 0 ? filteredScored.map((s) => s.topic) : ["general"];

  // Expose all above-threshold scores for debugging (not just filtered set).
  const similarityScores: Partial<Record<TopicId, number>> = {};
  for (const s of scored) {
    similarityScores[s.topic] = s.score;
  }

  return {
    topics,
    matchedKeywords: {}, // deprecated in semantic mode; kept for type compatibility
    similarityScores,
  };
}
