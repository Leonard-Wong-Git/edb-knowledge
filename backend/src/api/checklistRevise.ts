/**
 * checklistRevise.ts — 文件修訂: compare an uploaded school document against a
 * domain's EDB compliance CHECKLIST, flag which requirements look covered /
 * partial / missing, and supply the model 學校版 clause text to fill each gap.
 *
 * Pure embedding-based coverage (deterministic, NO LLM): the document is
 * segmented + embedded, every checklist requirement (filtered by school_type)
 * is embedded, and per-item max cosine over the doc segments classifies it.
 * For partial/missing items, the clauses whose `covers` array includes that
 * item supply the suggested supplement text (the same 學校版 clauses behind the
 * downloadable policy templates). The client assembles the revised docx.
 *
 * Design constraints (mirror analyzeDocument.ts):
 *   - Reuses segmentText() and the shared embedding client unchanged.
 *   - Stateless: nothing persisted (privacy posture — raw file never uploaded;
 *     only extracted text reaches this endpoint).
 *   - Bounded: MAX_TEXT_CHARS input cap, MAX_DOC_SEGMENTS / MAX_ITEMS bounds,
 *     a single batch embedding call.
 *   - Coverage labels are heuristic ESTIMATES; the response is framed for human
 *     review, never as a definitive compliance verdict.
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { segmentText } from "./analyzeDocument.js";
import type { EmbedFn, BatchEmbedFn } from "../lib/embeddingClient.js";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));
// Resolves to repo-root checklists_bundle.json in both dev (tsx, src/api) and
// build (dist/api) — same depth as role_facts.json (../../../).
const BUNDLE_PATH = path.resolve(CURRENT_DIR, "../../../checklists_bundle.json");

// ---------------------------------------------------------------------------
// Limits / thresholds
// ---------------------------------------------------------------------------

/** Hard cap on incoming extracted text (matches analyzeDocument). */
export const MAX_TEXT_CHARS = 60_000;
/** Doc segments embedded for coverage breadth. */
const MAX_DOC_SEGMENTS = 150;
/** Checklist items scored/returned per request (large domains are truncated, flagged).
 *  S163 P3: raised 220→400 so the largest domain (kg_operation, 388 items) is fully
 *  scored instead of silently truncating its later chapters. */
const MAX_ITEMS = 400;
/** max-cosine >= this → "covered"; tunable (text-embedding-3-small, zh policy text). */
const COVERED_THRESHOLD = 0.5;
/** max-cosine in [PARTIAL, COVERED) → "partial"; below → "missing". */
const PARTIAL_THRESHOLD = 0.42;
/** S163 P3 lexical gate: text-embedding-3-small scores ANY two same-register zh policy
 *  sentences ~0.42–0.5 cosine even when topically unrelated, so a 1-sentence input was
 *  marked as "covering" dozens of unrelated requirements (teacher appointment letters,
 *  registration fees…). On top of cosine we require ≥1 shared INFORMATIVE CJK bigram
 *  between the requirement and its best-matching segment; "informative" = appearing in
 *  ≤ this fraction of the domain's items (ubiquitous boilerplate like 本校/幼稚園/須 is
 *  self-calibrated out). No shared informative term → demote to "missing" (avoids false
 *  high-confidence coverage while preserving traceability for genuine matches). */
const STOPWORD_DF_FRACTION = 0.25;
/** Best-matching doc excerpt length echoed per item. */
const EXCERPT_CHARS = 160;
/** Suggested supplement clause length cap per item. */
const SUPPLEMENT_CHARS = 1_200;

// ---------------------------------------------------------------------------
// School type
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Bundle (lazy-loaded once)
// ---------------------------------------------------------------------------

interface BundleItem {
  req: string;
  page?: number;
  source_id?: string;
  school_types?: string[];
}
interface BundleSection {
  name: string;
  items: BundleItem[];
}
interface BundleClause {
  text: string;
  si: number;
  covers?: number[];
  school_types?: string[];
}
interface BundleDomain {
  key: string;
  cn: string;
  src: Record<string, [string, string]>;
  sections: BundleSection[];
  clauses: BundleClause[];
  /** Domain-level school-type scope (S162 ①). Absent = applies to all types.
   *  Used as the fallback when an item/clause has no own school_types, so an
   *  untagged requirement in a type-scoped domain (e.g. kg_operation = 幼稚園-only)
   *  does NOT leak into other school types when the user picks one. */
  school_types?: string[];
}
interface Bundle {
  domains: Record<string, BundleDomain>;
}

let _bundle: Bundle | null = null;
function loadBundle(): Bundle {
  if (!_bundle) {
    _bundle = JSON.parse(readFileSync(BUNDLE_PATH, "utf-8")) as Bundle;
  }
  return _bundle;
}

/** Domain list for the frontend selector. */
export function listChecklistDomains(): { key: string; cn: string; item_count: number }[] {
  const b = loadBundle();
  return Object.values(b.domains).map((d) => ({
    key: d.key,
    cn: d.cn,
    item_count: d.sections.reduce((n, s) => n + s.items.length, 0),
  }));
}

/** Max doc segments embedded for auto-detection (latency bound). */
const AUTO_DETECT_SEGMENTS = 40;
/** A domain is "relevant" when its descriptor's max cosine over the doc ≥ this.
 *  Raised S161 (Leonard "收緊對焦"): 0.30 let weakly-related domains in (a maths
 *  syllabus pulled in 特殊教育需要) — 0.38 keeps only a clearly-on-topic domain. */
const AUTO_DETECT_THRESHOLD = 0.38;

/**
 * Cheap auto-detection of which checklist domains a document touches: embed up
 * to AUTO_DETECT_SEGMENTS doc segments plus one short descriptor per domain
 * (domain name + its section names), then keep the domains whose descriptor
 * best-matches the document. Reuses the shared batch embedder and the bundle;
 * returns at most `max` domain keys, highest-scoring first. Returns [] when the
 * document matches nothing strongly (caller then annotates guidelines only).
 */
export async function detectRelevantDomains(
  text: string,
  deps: ChecklistReviseDependencies,
  max = 2,
  sel?: SchoolType
): Promise<string[]> {
  if (typeof text !== "string" || !text.trim()) return [];
  const docSegs = segmentText(text).slice(0, AUTO_DETECT_SEGMENTS);
  if (docSegs.length === 0) return [];

  const b = loadBundle();
  // S162 ①: when a school type is selected, never auto-detect a domain that does
  // not apply to it (e.g. a 小學 document must not surface the 幼稚園-only kg_operation).
  const domains = Object.values(b.domains).filter(
    (d) => !sel || !d.school_types || d.school_types.includes(sel)
  );
  const descriptors = domains.map(
    (d) => `${d.cn}：${d.sections.slice(0, 8).map((s) => s.name).join("、")}`
  );

  const all = await deps.embeddingClient.batch([...docSegs, ...descriptors]);
  const docEmb = all.slice(0, docSegs.length);
  const domEmb = all.slice(docSegs.length);

  return domains
    .map((d, i) => {
      let best = -1;
      for (const de of docEmb) {
        const s = dot(domEmb[i], de);
        if (s > best) best = s;
      }
      return { key: d.key, score: best };
    })
    .sort((a, b2) => b2.score - a.score)
    .filter((d) => d.score >= AUTO_DETECT_THRESHOLD)
    .slice(0, Math.max(1, max))
    .map((d) => d.key);
}

/** Min segments a SECONDARY (non-top) domain must win as argmax before it
 *  qualifies — one fluke segment must not drag in a whole unrelated domain. The
 *  top domain is always kept when it wins ≥1 segment. */
const SECONDARY_MIN_SEGMENTS = 2;

export interface DetectedDomain {
  key: string;
  /** Document segments for which this domain was the best (argmax) match. */
  segments: number;
  /** Highest cosine of any segment to this domain's descriptor. */
  score: number;
}

/**
 * Per-segment domain detection (Phase 2.5). Instead of collapsing the whole
 * document to one global best-domain (detectRelevantDomains), every document
 * segment is routed to its single best-matching domain (argmax cosine, gated by
 * AUTO_DETECT_THRESHOLD). A domain then qualifies by how many segments it wins:
 * the top domain needs ≥1, any further domain needs ≥ SECONDARY_MIN_SEGMENTS.
 * So a genuinely multi-topic document (e.g. a combined policy manual covering
 * safety + governance + HR) surfaces gaps from each domain it really covers,
 * while a single-topic document still yields exactly one domain and a lone fluke
 * segment cannot pull in an off-topic domain. Same embedding cost as
 * detectRelevantDomains; returns up to `max` domains, most-segments first.
 */
export async function detectDomainsPerSegment(
  text: string,
  deps: ChecklistReviseDependencies,
  max = 3,
  sel?: SchoolType
): Promise<DetectedDomain[]> {
  if (typeof text !== "string" || !text.trim()) return [];
  const docSegs = segmentText(text).slice(0, AUTO_DETECT_SEGMENTS);
  if (docSegs.length === 0) return [];

  const b = loadBundle();
  const domains = Object.values(b.domains).filter(
    (d) => !sel || !d.school_types || d.school_types.includes(sel)
  );
  if (domains.length === 0) return [];
  const descriptors = domains.map(
    (d) => `${d.cn}：${d.sections.slice(0, 8).map((s) => s.name).join("、")}`
  );

  const all = await deps.embeddingClient.batch([...docSegs, ...descriptors]);
  const docEmb = all.slice(0, docSegs.length);
  const domEmb = all.slice(docSegs.length);

  // Route each segment to its single best domain (argmax), tallying wins +
  // tracking each domain's peak cosine across the document.
  const wins = domains.map(() => 0);
  const best = domains.map(() => -1);
  for (const de of docEmb) {
    let bi = -1;
    let bs = -1;
    for (let i = 0; i < domEmb.length; i++) {
      const s = dot(domEmb[i], de);
      if (s > best[i]) best[i] = s;
      if (s > bs) {
        bs = s;
        bi = i;
      }
    }
    if (bi >= 0 && bs >= AUTO_DETECT_THRESHOLD) wins[bi]++;
  }

  const ranked = domains
    .map((d, i) => ({ key: d.key, segments: wins[i], score: best[i] }))
    .filter((d) => d.segments > 0)
    .sort((a, b2) => b2.segments - a.segments || b2.score - a.score);
  if (ranked.length === 0) return [];

  return ranked
    .filter((d, idx) => idx === 0 || d.segments >= SECONDARY_MIN_SEGMENTS)
    .slice(0, Math.max(1, max));
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ChecklistReviseRequest {
  text: string;
  domain: string;
  school_type?: string;
  filename?: string;
}

export type CoverageStatus = "covered" | "partial" | "missing";

export interface ReviseItem {
  section: string;
  req: string;
  status: CoverageStatus;
  /** Max cosine similarity of this requirement against the document (estimate). */
  similarity: number;
  /** Best-matching document excerpt (covered / partial only). */
  best_excerpt?: string;
  /** Model 學校版 clause text to supplement this requirement (partial / missing only). */
  supplement?: string;
  sources?: { title: string; url: string; page?: number }[];
}

export interface ReviseSection {
  name: string;
  covered: number;
  partial: number;
  missing: number;
  items: ReviseItem[];
}

export interface ChecklistReviseResponse {
  ok: boolean;
  domain: string;
  domain_cn: string;
  school_type?: string;
  filename?: string;
  total_items: number;
  scored_items: number;
  /** Items beyond MAX_ITEMS that were not scored (visible truncation). */
  truncated_items: number;
  covered: number;
  partial: number;
  missing: number;
  segment_count: number;
  sections: ReviseSection[];
}

export interface ChecklistReviseDependencies {
  embeddingClient: EmbedFn & { batch: BatchEmbedFn };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Whether an item/clause applies to the selected school type.
 *  Precedence (S162 ①): the item/clause's own school_types wins; when it has none,
 *  fall back to the DOMAIN's school_types; when neither is set, it applies to all.
 *  This stops an untagged requirement in a type-scoped domain (e.g. kg_operation =
 *  幼稚園-only) from leaking into other school types. */
function okType(
  st: string[] | undefined,
  sel: SchoolType | undefined,
  domainSt?: string[]
): boolean {
  if (!sel) return true;
  const scope = st && st.length ? st : domainSt;
  return !scope || scope.length === 0 || scope.includes(sel);
}

/** OpenAI embeddings are unit-normalized, so cosine === dot product. */
function dot(a: number[], b: number[]): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}

/** CJK character bigrams of a string (2-char sliding window over Han chars only).
 *  Used by the S163 P3 lexical-overlap gate. Exported for regression. */
export function cjkBigrams(s: string): string[] {
  const cjk = (s || "").replace(/[^一-鿿]/g, "");
  const out: string[] = [];
  for (let i = 0; i + 1 < cjk.length; i++) out.push(cjk.slice(i, i + 2));
  return out;
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function checklistRevise(
  input: ChecklistReviseRequest,
  deps: ChecklistReviseDependencies
): Promise<ChecklistReviseResponse> {
  const text = input?.text;
  const sel = normalizeSchoolType(input?.school_type);
  if (typeof text !== "string" || !text.trim()) {
    throw new Error("text is required");
  }
  if (text.length > MAX_TEXT_CHARS) {
    throw new Error(
      `文件過長（${text.length.toLocaleString()} 字元，上限 ${MAX_TEXT_CHARS.toLocaleString()}）。請分批處理。`
    );
  }

  const bundle = loadBundle();
  const dom = bundle.domains[input?.domain];
  if (!dom) {
    throw new Error(`未知範疇「${String(input?.domain ?? "")}」`);
  }

  const docSegs = segmentText(text).slice(0, MAX_DOC_SEGMENTS);
  if (docSegs.length === 0) {
    throw new Error("text is required");
  }

  // Flatten checklist items (filtered by school_type), keeping section + local index
  // so each item can be linked back to its supplement clauses (clause.covers is
  // a LOCAL index into checklist.sections[si-1].items).
  interface Flat {
    sectionIdx: number;
    sectionName: string;
    localIdx: number;
    item: BundleItem;
  }
  const flat: Flat[] = [];
  dom.sections.forEach((sec, si) => {
    sec.items.forEach((item, li) => {
      if (okType(item.school_types, sel, dom.school_types)) {
        flat.push({ sectionIdx: si, sectionName: sec.name, localIdx: li, item });
      }
    });
  });
  const totalItems = flat.length;
  const scored = flat.slice(0, MAX_ITEMS);
  const truncated = totalItems - scored.length;

  // One batch embedding call: doc segments first, then item requirements.
  const itemTexts = scored.map((f) => f.item.req);
  const all = await deps.embeddingClient.batch([...docSegs, ...itemTexts]);
  const docEmb = all.slice(0, docSegs.length);
  const itemEmb = all.slice(docSegs.length);

  // S163 P3 lexical-overlap gate setup. Per-item informative CJK bigrams + per-segment
  // bigram sets. A bigram is "informative" if it appears in ≤ STOPWORD_DF_FRACTION of the
  // scored items — ubiquitous boilerplate (本校/幼稚園/須…) is self-calibrated out so it
  // can't manufacture overlap.
  const itemBigramSets = scored.map((f) => new Set(cjkBigrams(f.item.req)));
  const dfCap = Math.max(2, Math.ceil(scored.length * STOPWORD_DF_FRACTION));
  const bigramDf = new Map<string, number>();
  for (const set of itemBigramSets) {
    for (const bg of set) bigramDf.set(bg, (bigramDf.get(bg) ?? 0) + 1);
  }
  const isInformative = (bg: string) => (bigramDf.get(bg) ?? 0) <= dfCap;
  const itemInfoBigrams = itemBigramSets.map((set) => [...set].filter(isInformative));
  const segBigramSets = docSegs.map((seg) => new Set(cjkBigrams(seg)));

  const results: ReviseItem[] = scored.map((f, k) => {
    const e = itemEmb[k];
    let best = -1;
    let bestIdx = 0;
    for (let d = 0; d < docEmb.length; d++) {
      const s = dot(e, docEmb[d]);
      if (s > best) {
        best = s;
        bestIdx = d;
      }
    }
    let status: CoverageStatus =
      best >= COVERED_THRESHOLD ? "covered" : best >= PARTIAL_THRESHOLD ? "partial" : "missing";
    // Graded lexical-overlap gate (S163 P3). A high cosine over same-register policy text
    // is not enough — grade by how many INFORMATIVE terms the requirement shares with its
    // best-matching segment: 0 → "missing" (no real topical link), 1 → at most "partial"
    // (a single shared word is weak evidence, never a confident "covered"), ≥2 → keep the
    // cosine verdict. Skipped only when the requirement is all-boilerplate (no informative
    // bigrams) so genuine matches aren't over-penalised. This is what stops a 1-sentence
    // input from being scored as "covering" dozens of unrelated requirements.
    if (status !== "missing" && itemInfoBigrams[k].length > 0) {
      const segSet = segBigramSets[bestIdx];
      let overlap = 0;
      for (const bg of itemInfoBigrams[k]) {
        if (segSet.has(bg)) {
          overlap++;
          if (overlap >= 2) break;
        }
      }
      if (overlap === 0) status = "missing";
      else if (overlap < 2 && status === "covered") status = "partial";
    }
    const out: ReviseItem = {
      section: f.sectionName,
      req: f.item.req,
      status,
      similarity: Math.round(best * 1000) / 1000,
    };
    if (status !== "missing") {
      const ex = docSegs[bestIdx];
      out.best_excerpt = ex.length > EXCERPT_CHARS ? `${ex.slice(0, EXCERPT_CHARS)}…` : ex;
    }
    if (status !== "covered") {
      const supp = dom.clauses
        .filter(
          (c) =>
            c.si === f.sectionIdx + 1 &&
            Array.isArray(c.covers) &&
            c.covers.includes(f.localIdx) &&
            okType(c.school_types, sel, dom.school_types)
        )
        .map((c) => c.text)
        .join("\n");
      if (supp) {
        out.supplement = supp.length > SUPPLEMENT_CHARS ? `${supp.slice(0, SUPPLEMENT_CHARS)}…` : supp;
      }
    }
    if (f.item.source_id && dom.src[f.item.source_id]) {
      const [title, url] = dom.src[f.item.source_id];
      out.sources = [{ title, url, ...(f.item.page !== undefined ? { page: f.item.page } : {}) }];
    }
    return out;
  });

  // Group by section, preserving first-seen order.
  const secMap = new Map<string, ReviseItem[]>();
  for (const r of results) {
    if (!secMap.has(r.section)) secMap.set(r.section, []);
    secMap.get(r.section)!.push(r);
  }
  const sections: ReviseSection[] = [...secMap.entries()].map(([name, items]) => ({
    name,
    covered: items.filter((i) => i.status === "covered").length,
    partial: items.filter((i) => i.status === "partial").length,
    missing: items.filter((i) => i.status === "missing").length,
    items,
  }));

  const covered = results.filter((i) => i.status === "covered").length;
  const partial = results.filter((i) => i.status === "partial").length;
  const missing = results.filter((i) => i.status === "missing").length;

  return {
    ok: true,
    domain: dom.key,
    domain_cn: dom.cn,
    ...(sel ? { school_type: sel } : {}),
    ...(input.filename ? { filename: String(input.filename).slice(0, 200) } : {}),
    total_items: totalItems,
    scored_items: scored.length,
    truncated_items: truncated,
    covered,
    partial,
    missing,
    segment_count: docSegs.length,
    sections,
  };
}
