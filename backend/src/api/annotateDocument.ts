/**
 * annotateDocument.ts — 文件標註: a MERGED endpoint behind the unified
 * 「文件標註」tab. It combines, for one uploaded school document:
 *   (a) guideline matching   — every paragraph is matched against EDB guidelines
 *                              (reuses analyzeDocument unchanged), and
 *   (b) checklist-gap review  — selected (or auto-detected) compliance domains
 *                              are scanned for partial / missing requirements
 *                              (reuses checklistRevise unchanged).
 *
 * The response is a flat findings[] list whose `span` field is a verbatim-ish
 * substring of the document text, so the CLIENT can locate each span inside the
 * ORIGINAL .docx XML and highlight it in place (format preserved) + attach a
 * Word comment. Findings with no locatable span (missing requirements) carry
 * `span: null` and are rendered in a "建議補充" appendix instead.
 *
 * Design constraints (mirror analyzeDocument / checklistRevise):
 *   - Zero modification to the two reused modules — they are consumed strictly
 *     through their public functions, so the existing /api/analyze-document and
 *     /api/checklist-revise endpoints keep byte-identical behaviour.
 *   - Stateless: the raw file never reaches the server (client extracts text);
 *     nothing is persisted.
 *   - Bounded: MAX_TEXT_CHARS input cap, ≤ MAX_DOMAINS domains scanned,
 *     ≤ MAX_FINDINGS findings returned (visible truncation flags).
 *   - Coverage / matches are heuristic ESTIMATES framed for human review.
 */

import {
  analyzeDocument,
  MAX_TEXT_CHARS as ANALYZE_MAX_TEXT_CHARS,
  type AnalyzeDocumentDependencies,
} from "./analyzeDocument.js";
import {
  checklistRevise,
  detectRelevantDomains,
  listChecklistDomains,
  type ChecklistReviseDependencies,
  type SchoolType,
} from "./checklistRevise.js";

// ---------------------------------------------------------------------------
// Limits
// ---------------------------------------------------------------------------

/** Hard cap on incoming extracted text (shared with the two reused modules). */
export const MAX_TEXT_CHARS = ANALYZE_MAX_TEXT_CHARS;
/** Max compliance domains scanned per request when the caller selects them. */
const MAX_DOMAINS = 3;
/** Domains auto-detected when the caller selects none — single best-matching
 *  domain only (S161 "收緊對焦": auto-detecting 2 pulled unrelated domains like
 *  特殊教育需要 into a maths-syllabus doc). Explicit selection can still pick ≤3. */
const AUTO_DETECT_COUNT = 1;
/** Hard cap on total findings returned (keeps the annotated doc manageable). */
const MAX_FINDINGS = 120;
/** Per-domain cap on "partial" findings (the low PARTIAL threshold over-labels,
 *  so we keep only the strongest matches — otherwise weak partials flood the doc
 *  and starve the actionable "missing" requirements). */
const MAX_PARTIAL_PER_DOMAIN = 12;
/** Per-domain cap on "missing" findings. Auto-detected runs use the tighter cap
 *  (S161 "收緊對焦": a subject/curriculum doc shouldn't be flooded with whole-domain
 *  "you also lack policy X" items); explicit domain selection = full completeness. */
const MAX_MISSING_PER_DOMAIN = 25;
const MAX_MISSING_PER_DOMAIN_AUTO = 8;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AnnotateDocumentRequest {
  /** Extracted document text (client-side extraction; required). */
  text: string;
  /** Original filename, echoed back for display only. */
  filename?: string;
  /** Optional school type — primary | secondary | special | kindergarten. */
  school_type?: string;
  /** Compliance domains to gap-check. Empty / omitted → auto-detect. */
  domains?: string[];
}

export interface AnnotateSource {
  title: string;
  url: string;
  page?: number;
}

export interface AnnotateFinding {
  /** "guideline" = paragraph relates to an EDB guideline; "checklist-gap" = a
   *  requirement is partially/not covered. */
  kind: "guideline" | "checklist-gap";
  /** Original-text substring to locate + highlight in the docx; null = the
   *  finding has no place in the text (a missing requirement) → appendix only. */
  span: string | null;
  /** "info" (guideline) | "partial" | "missing" (checklist-gap). */
  status: "info" | "partial" | "missing";
  /** Checklist-gap only: which domain raised it. */
  domain?: string;
  domain_cn?: string;
  /** Short human-facing note (guideline note, or "section｜requirement"). */
  note: string;
  /** Model 學校版 clause text to supplement a gap (checklist-gap only). */
  suggestion?: string;
  source?: AnnotateSource;
}

export interface AnnotateDomainSummary {
  domain: string;
  domain_cn: string;
  total_items: number;
  covered: number;
  partial: number;
  missing: number;
}

export interface AnnotateDocumentResponse {
  ok: boolean;
  filename?: string;
  school_type?: string;
  /** true when `domains` was empty and the server auto-detected them. */
  auto_detected: boolean;
  domains: AnnotateDomainSummary[];
  total_segments: number;
  analyzed_segments: number;
  skipped_segments: number;
  /** Findings beyond MAX_FINDINGS that were dropped (visible truncation). */
  truncated_findings: number;
  findings: AnnotateFinding[];
}

export type AnnotateDocumentDependencies = AnalyzeDocumentDependencies &
  ChecklistReviseDependencies;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const VALID_DOMAIN_KEYS = new Set(listChecklistDomains().map((d) => d.key));
const VALID_SCHOOL_TYPES = new Set(["primary", "secondary", "special", "kindergarten"]);
function normalizeSchoolType(v: unknown): string | undefined {
  return typeof v === "string" && VALID_SCHOOL_TYPES.has(v) ? v : undefined;
}

/** Strip a trailing ellipsis so a truncated excerpt can still locate its paragraph. */
function spanFromExcerpt(excerpt: string | undefined): string | null {
  if (!excerpt) return null;
  const cleaned = excerpt.replace(/[…\.]+$/u, "").trim();
  return cleaned.length >= 8 ? cleaned : null;
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function annotateDocument(
  input: AnnotateDocumentRequest,
  deps: AnnotateDocumentDependencies
): Promise<AnnotateDocumentResponse> {
  const text = input?.text;
  if (typeof text !== "string" || !text.trim()) {
    throw new Error("text is required");
  }
  if (text.length > MAX_TEXT_CHARS) {
    throw new Error(
      `文件過長（${text.length.toLocaleString()} 字元，上限 ${MAX_TEXT_CHARS.toLocaleString()}）。請分批處理。`
    );
  }

  // Resolve domains: explicit (validated, deduped) or auto-detected.
  const requested = Array.isArray(input?.domains)
    ? [...new Set(input.domains.filter((d) => VALID_DOMAIN_KEYS.has(d)))]
    : [];
  let domainKeys = requested.slice(0, MAX_DOMAINS);
  let autoDetected = false;
  if (domainKeys.length === 0) {
    // S162 ①: pass the selected school type so auto-detect never picks a domain
    // outside that type's scope (e.g. 小學 doc must not surface 幼稚園-only kg_operation).
    const selType = normalizeSchoolType(input?.school_type) as SchoolType | undefined;
    domainKeys = await detectRelevantDomains(text, deps, AUTO_DETECT_COUNT, selType);
    autoDetected = domainKeys.length > 0;
  }

  // (a) Guideline matching + (b) per-domain checklist gap. The guideline pass
  // and each domain pass are independent, so run them concurrently.
  const reviseInput = (domain: string) => ({
    text,
    domain,
    ...(input.filename ? { filename: input.filename } : {}),
    ...(input.school_type ? { school_type: input.school_type } : {}),
  });
  const [analysis, ...reviseSettled] = await Promise.all([
    analyzeDocument(
      {
        text,
        ...(input.filename ? { filename: input.filename } : {}),
        ...(input.school_type ? { school_type: input.school_type } : {}),
      },
      deps
    ),
    ...domainKeys.map((dk) =>
      checklistRevise(reviseInput(dk), deps).then(
        (r) => r,
        () => null // a single domain failure must not sink the whole annotation
      )
    ),
  ]);
  const reviseResults = reviseSettled.filter(
    (r): r is NonNullable<typeof r> => r !== null
  );

  // ── Build findings ────────────────────────────────────────────────────────
  const guidelineFindings: AnnotateFinding[] = [];
  for (const seg of analysis.segments) {
    if (!seg.matches || seg.matches.length === 0) continue;
    const top = seg.matches[0];
    guidelineFindings.push({
      kind: "guideline",
      span: seg.text,
      status: "info",
      note: seg.note || `與《${top.title}》相關`,
      source: {
        title: top.title,
        url: top.url,
        ...(top.page !== undefined ? { page: top.page } : {}),
      },
    });
  }

  const partialFindings: AnnotateFinding[] = [];
  const missingFindings: AnnotateFinding[] = [];
  const missingCap = autoDetected ? MAX_MISSING_PER_DOMAIN_AUTO : MAX_MISSING_PER_DOMAIN;
  for (const rr of reviseResults) {
    // Collect this domain's gaps, then keep only the strongest partials so weak
    // 0.42-similarity matches don't flood the highlight layer.
    const partialPool: { f: AnnotateFinding; sim: number }[] = [];
    let missingForDomain = 0;
    for (const sec of rr.sections) {
      for (const it of sec.items) {
        if (it.status === "covered") continue;
        const base: AnnotateFinding = {
          kind: "checklist-gap",
          span: null,
          status: it.status,
          domain: rr.domain,
          domain_cn: rr.domain_cn,
          note: `${sec.name}｜${it.req}`,
          ...(it.supplement ? { suggestion: it.supplement } : {}),
          ...(it.sources && it.sources[0] ? { source: it.sources[0] } : {}),
        };
        if (it.status === "partial") {
          partialPool.push({
            f: { ...base, span: spanFromExcerpt(it.best_excerpt) },
            sim: typeof it.similarity === "number" ? it.similarity : 0,
          });
        } else if (missingForDomain < missingCap) {
          missingFindings.push(base);
          missingForDomain++;
        }
      }
    }
    partialPool
      .sort((a, b2) => b2.sim - a.sim)
      .slice(0, MAX_PARTIAL_PER_DOMAIN)
      .forEach((p) => partialFindings.push(p.f));
  }

  // Priority order: in-place highlights first (guideline, then partial), then
  // appendix-only missing items, so truncation drops the least-locatable last.
  const ordered = [...guidelineFindings, ...partialFindings, ...missingFindings];
  const findings = ordered.slice(0, MAX_FINDINGS);
  const truncated = ordered.length - findings.length;

  const schoolType = normalizeSchoolType(input.school_type);
  return {
    ok: true,
    ...(input.filename ? { filename: String(input.filename).slice(0, 200) } : {}),
    ...(schoolType ? { school_type: schoolType } : {}),
    auto_detected: autoDetected,
    domains: reviseResults.map((r) => ({
      domain: r.domain,
      domain_cn: r.domain_cn,
      total_items: r.total_items,
      covered: r.covered,
      partial: r.partial,
      missing: r.missing,
    })),
    total_segments: analysis.total_segments,
    analyzed_segments: analysis.analyzed_segments,
    skipped_segments: analysis.skipped_segments,
    truncated_findings: truncated,
    findings,
  };
}
