/**
 * analyzeDocument.ts — 文件分析: per-segment guideline matching for user docs
 *
 * The user pastes / uploads a school document (extraction happens client-side
 * — only the extracted TEXT reaches this endpoint, never the raw file). The
 * text is segmented server-side, each segment is run through the existing
 * Channel B semantic search (searchChannelB public API — routing, page
 * extraction, text cleaning and degraded-state discrimination are all reused
 * unchanged), then ONE LLM call produces a short per-segment note.
 *
 * Design constraints:
 *   - Zero modification to shared retrieval infra (searchChannelB/searchWiki
 *     are consumed strictly through their public signatures).
 *   - Stateless: nothing is persisted server-side (privacy posture).
 *   - Bounded cost/latency: MAX_SEGMENTS segments per request, MAX_TEXT_CHARS
 *     input cap, limited concurrency against Supabase free tier.
 */

import { searchChannelB, type ChannelBResult, type LlmFn } from "./searchChannelB.js";
import type { EmbedFn } from "../lib/embeddingClient.js";

// ---------------------------------------------------------------------------
// Limits
// ---------------------------------------------------------------------------

/** Hard cap on incoming extracted text (~30 A4 pages of Chinese). */
export const MAX_TEXT_CHARS = 60_000;
/** Max segments analyzed per request (cost / latency / Supabase free-tier bound). */
export const MAX_SEGMENTS = 12;
/** Matches requested per segment. */
const MATCHES_PER_SEGMENT = 4;
/** Concurrent Channel B searches (free-tier pgvector tolerates small bursts). */
const SEARCH_CONCURRENCY = 4;
/** Segments shorter than this merge into the next one (headers, list stubs).
 *  Tuned low: Chinese circular body paragraphs are commonly 40–80 chars and
 *  must stay standalone; only true stubs (titles, dates, salutations) merge. */
const MIN_SEGMENT_CHARS = 30;
/** Segments longer than this are split on sentence boundaries. */
const MAX_SEGMENT_CHARS = 1_200;
/** Excerpt length echoed back to the client per segment. */
const EXCERPT_CHARS = 200;
/** Snippet length per matched chunk. */
const SNIPPET_CHARS = 220;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** School type for tailoring per-segment notes ("食" the #3 校類 model at advice level). */
export type SchoolType = "primary" | "secondary" | "special" | "kindergarten";
const SCHOOL_TYPE_LABELS: Record<SchoolType, string> = {
  primary: "小學",
  secondary: "中學",
  special: "特殊學校",
  kindergarten: "幼稚園",
};
function normalizeSchoolType(v: unknown): SchoolType | undefined {
  return typeof v === "string" && v in SCHOOL_TYPE_LABELS ? (v as SchoolType) : undefined;
}

export interface AnalyzeDocumentRequest {
  /** Extracted document text (client-side extraction; required). */
  text: string;
  /** Original filename, echoed back for display only. */
  filename?: string;
  /** Optional school type — tailors the per-segment notes to that school level. */
  school_type?: string;
}

export interface AnalyzeDocumentMatch {
  title: string;
  source_id: string;
  url: string;
  page?: number;
  score: number;
  snippet: string;
}

export interface AnalyzeDocumentSegment {
  index: number;
  excerpt: string;
  /** Full segment text (for building the downloadable annotated docx client-side). */
  text: string;
  char_count: number;
  /** "ok" = searched fine (matches may still be empty); "error" = search failed for this segment */
  status: "ok" | "error";
  matches: AnalyzeDocumentMatch[];
  /** One-line LLM note tying the segment to the matched guidelines (may be absent). */
  note?: string;
}

export interface AnalyzeDocumentResponse {
  ok: boolean;
  filename?: string;
  total_segments: number;
  analyzed_segments: number;
  /** Segments beyond MAX_SEGMENTS that were NOT analyzed (visible truncation). */
  skipped_segments: number;
  segments: AnalyzeDocumentSegment[];
}

export interface AnalyzeDocumentDependencies {
  embeddingClient: EmbedFn;
  llmClient: LlmFn;
}

// ---------------------------------------------------------------------------
// Segmentation
// ---------------------------------------------------------------------------

/**
 * Split document text into analysis segments:
 * blank-line paragraphs → merge tiny fragments forward → split oversized ones
 * on sentence boundaries.
 */
export function segmentText(text: string): string[] {
  const paragraphs = text
    .replace(/\r\n?/g, "\n")
    .split(/\n\s*\n+/)
    .map((p) => p.replace(/\s*\n\s*/g, " ").trim())
    .filter((p) => p.length > 0);

  // Merge fragments below MIN_SEGMENT_CHARS into the following paragraph so
  // section headers travel with their body instead of becoming noise queries.
  const merged: string[] = [];
  let pending = "";
  for (const p of paragraphs) {
    const candidate = pending ? `${pending} ${p}` : p;
    if (candidate.length < MIN_SEGMENT_CHARS) {
      pending = candidate;
      continue;
    }
    merged.push(candidate);
    pending = "";
  }
  if (pending) {
    if (merged.length > 0) merged[merged.length - 1] += ` ${pending}`;
    else merged.push(pending);
  }

  // Split any oversized segment at sentence punctuation.
  const out: string[] = [];
  for (const seg of merged) {
    if (seg.length <= MAX_SEGMENT_CHARS) {
      out.push(seg);
      continue;
    }
    let rest = seg;
    while (rest.length > MAX_SEGMENT_CHARS) {
      const window = rest.slice(0, MAX_SEGMENT_CHARS);
      let cut = Math.max(
        window.lastIndexOf("。"),
        window.lastIndexOf("；"),
        window.lastIndexOf("."),
        window.lastIndexOf(";")
      );
      if (cut < MIN_SEGMENT_CHARS) cut = MAX_SEGMENT_CHARS - 1;
      out.push(rest.slice(0, cut + 1).trim());
      rest = rest.slice(cut + 1).trim();
    }
    if (rest) out.push(rest);
  }
  return out;
}

// ---------------------------------------------------------------------------
// Per-segment notes (single LLM call for the whole document)
// ---------------------------------------------------------------------------

const NOTES_PROMPT = `你是香港學校管治的政策顧問。以下是一份學校文件的分段內容，每段附有從教育局官方指引檢索到的相關資料。{CONTEXT}
請為每個段落用繁體中文寫一句話（40字內）的提示，說明該段落與檢索到的指引有何關連或需注意之處。
輸出格式：每行一句，以段落編號開頭，例如「1: 提示內容」。沒有相關資料的段落輸出「N: 未有對應指引」。不要輸出其他文字。

{SEGMENTS}`;

function buildNotesPrompt(
  segments: string[],
  matchesBySegment: AnalyzeDocumentMatch[][],
  schoolType?: SchoolType
): string {
  const context = schoolType
    ? `\n本校屬「${SCHOOL_TYPE_LABELS[schoolType]}」，請按該校類的實際情況給出提示（例如某指引只適用於其他校類時，請指出本校類是否適用）。`
    : "";
  const blocks = segments.map((seg, i) => {
    const refs = matchesBySegment[i]
      .slice(0, 2)
      .map((m, j) => `  指引${j + 1}（${m.title}）：${m.snippet}`)
      .join("\n");
    return `段落${i + 1}：${seg.slice(0, 300)}\n${refs || "  （未檢索到相關指引）"}`;
  });
  return NOTES_PROMPT
    .replace("{CONTEXT}", context)
    .replace("{SEGMENTS}", blocks.join("\n\n"));
}

/** Parse "1: note" lines; tolerant of full-width colons and stray text. */
export function parseNotes(raw: string, count: number): (string | undefined)[] {
  const notes: (string | undefined)[] = new Array(count).fill(undefined);
  for (const line of raw.split("\n")) {
    const m = line.trim().match(/^(\d{1,2})\s*[:：]\s*(.+)$/);
    if (!m) continue;
    const idx = parseInt(m[1], 10) - 1;
    if (idx >= 0 && idx < count && !notes[idx]) notes[idx] = m[2].trim();
  }
  return notes;
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

function toMatch(r: ChannelBResult): AnalyzeDocumentMatch {
  return {
    title: r.title,
    source_id: r.source_id,
    url: r.url,
    ...(r.page !== undefined ? { page: r.page } : {}),
    score: r.score,
    snippet: r.text.length > SNIPPET_CHARS ? `${r.text.slice(0, SNIPPET_CHARS)}…` : r.text,
  };
}

/** Run tasks with bounded concurrency, preserving order. */
async function mapWithConcurrency<T, R>(
  items: T[],
  limit: number,
  fn: (item: T, index: number) => Promise<R>
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i], i);
    }
  });
  await Promise.all(workers);
  return results;
}

export async function analyzeDocument(
  input: AnalyzeDocumentRequest,
  deps: AnalyzeDocumentDependencies
): Promise<AnalyzeDocumentResponse> {
  const text = input?.text;
  const schoolType = normalizeSchoolType(input?.school_type);
  if (typeof text !== "string" || !text.trim()) {
    throw new Error("text is required");
  }
  if (text.length > MAX_TEXT_CHARS) {
    throw new Error(
      `文件過長（${text.length.toLocaleString()} 字元，上限 ${MAX_TEXT_CHARS.toLocaleString()}）。請分批分析。`
    );
  }

  const allSegments = segmentText(text);
  if (allSegments.length === 0) {
    throw new Error("text is required");
  }
  const segments = allSegments.slice(0, MAX_SEGMENTS);
  const skipped = allSegments.length - segments.length;

  // Per-segment Channel B search through the existing public API.
  // synthesize:false → no per-segment LLM; one document-level notes call below.
  const searchOutcomes = await mapWithConcurrency(
    segments,
    SEARCH_CONCURRENCY,
    async (seg): Promise<{ status: "ok" | "error"; matches: AnalyzeDocumentMatch[] }> => {
      try {
        const resp = await searchChannelB(
          { query: seg, top_k: MATCHES_PER_SEGMENT, synthesize: false },
          deps.embeddingClient
        );
        // Unconfigured/degraded Supabase must stay visible, not look like "no match".
        if (resp.degraded) return { status: "error", matches: [] };
        return { status: "ok", matches: resp.results.map(toMatch) };
      } catch {
        return { status: "error", matches: [] };
      }
    }
  );

  // One LLM call for all per-segment notes; a notes failure must not sink the
  // matches (they are the core deliverable) — notes are simply omitted.
  let notes: (string | undefined)[] = new Array(segments.length).fill(undefined);
  const matchesBySegment = searchOutcomes.map((o) => o.matches);
  if (matchesBySegment.some((m) => m.length > 0)) {
    try {
      const raw = await deps.llmClient(buildNotesPrompt(segments, matchesBySegment, schoolType));
      notes = parseNotes(raw, segments.length);
    } catch {
      /* notes omitted — matches still returned */
    }
  }

  return {
    ok: true,
    ...(input.filename ? { filename: String(input.filename).slice(0, 200) } : {}),
    total_segments: allSegments.length,
    analyzed_segments: segments.length,
    skipped_segments: skipped,
    segments: segments.map((seg, i) => ({
      index: i + 1,
      excerpt: seg.length > EXCERPT_CHARS ? `${seg.slice(0, EXCERPT_CHARS)}…` : seg,
      text: seg,
      char_count: seg.length,
      status: searchOutcomes[i].status,
      matches: searchOutcomes[i].matches,
      ...(notes[i] ? { note: notes[i] } : {}),
    })),
  };
}
