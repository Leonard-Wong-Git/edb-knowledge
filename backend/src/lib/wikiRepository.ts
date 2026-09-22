/**
 * wikiRepository.ts — Channel B: Supabase pgvector semantic search
 *
 * Uses direct fetch() to call the match_wiki_chunks RPC function,
 * bypassing supabase-js to avoid vector parameter casting issues.
 */

import type { EmbedFn } from "./embeddingClient.js";
import { getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";
import { cjkBigrams, informativeBigrams, overlapWith } from "./textBigrams.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type WikiContentType =
  | "vault_extract"
  | "approved_fact"
  | "stat_fact"
  | "guideline"
  | "footnote_curated";   // S174: curated 附件細字 footnote facts (route-independent overlay)

export type WikiFactType =
  | "policy"
  | "approved_policy"
  | "statistical"
  | "guideline_reference";

export interface WikiChunk {
  id: string;
  hash: string;
  text: string;
  source_id: string;
  title: string;
  url: string;
  topic: string;
  content_type: WikiContentType;
  fact_type: WikiFactType;
  role?: string;
  school_level?: string;
  reference_year?: string;
}

export interface WikiSearchResult {
  chunk: WikiChunk;
  score: number;
  channel: "B";
}

// ---------------------------------------------------------------------------
// Source aliases — same document, different ingestions get unified for quota
// ---------------------------------------------------------------------------

/**
 * Maps redundant source_id values to their canonical equivalent.
 *
 * Background: 學校行政手冊 was ingested twice into Supabase:
 *   - sag_2025_11 (Session 76, pdftotext partial extract Ch1/3/6/7, 415 chunks)
 *   - g24         (Session 98, PyMuPDF whole-doc fetch incl. cover/TOC, 300 chunks)
 *
 * Hash overlap was 0% because the chunking strategies differed, but content
 * semantics overlapped heavily. Treating them as separate source_ids in the
 * per-source quota gate would let one document occupy double the quota
 * (3 + 3 = 6 slots when cap=3), defeating the diversity goal.
 *
 * ⚠️ S223 — g24 no longer exists in the store. The 2026年8月版 re-ingest produced
 * ONE cutting of the manual under sag_2025_11 (387 chunks) and g24's 383 chunks
 * were deleted, which is what ended the "two cutting methods" rationale S102 gave
 * for keeping both. The entry below is KEPT deliberately: it is exported to the
 * Channel B sync manifest (channelBSync.ts → spec §3 source_aliases), so any
 * downstream integrator still holding a g24 reference keeps resolving it to the
 * canonical id. Aliasing an id that no longer returns chunks is a no-op for the
 * quota gate, so this costs nothing and only helps callers that are behind.
 */
// Exported so the Channel B sync manifest endpoint (channelBSync.ts) can surface
// the same alias map to downstream for de-dup (spec §1 caveat 2 / §3 source_aliases).
export const SOURCE_ALIASES: Record<string, string> = {
  g24: "sag_2025_11",
};

/**
 * Returns the canonical source_id for quota counting purposes.
 * Falls back to the input id if no alias is registered.
 */
function canonicalSource(id: string): string {
  return SOURCE_ALIASES[id] ?? id;
}

/**
 * S226 — quota families, for MEASUREMENT of a second kind of crowding.
 *
 * DELIBERATELY NOT `SOURCE_ALIASES`. That map is exported to the Channel B sync
 * manifest as `source_aliases` (spec §3), where it means "these ids are the same
 * document, de-duplicate them". The five school-bus guides are NOT the same
 * document: the 2026/27 safety guide is issued separately to drivers, escorts,
 * operators, parents and students, and the gold set expects a SPECIFIC one
 * (`bus_guide_audience_confusable` exists precisely because they are confusable).
 * Telling downstream they are aliases would publish a false claim.
 *
 * What they are is one FAMILY competing for the same window: measured 2026-09-15
 * over the 185-item gold set, `sch_bus_*` took 7 or 8 of 8 slots on nine bus
 * questions and 69 window slots in total, while the per-source quota (3) never
 * bound because each audience version is its own source_id. `values_edu_*`
 * (2021 trial + 2026 final) took 21 slots, `chi_hist_*` (regular + NCS-adapted)
 * 6 — and that last one is a forbidden-citation violation in the gold set.
 *
 * Only consulted when FAMILY_QUOTA=1, which is a measurement flag, not a change.
 */
export const QUOTA_FAMILIES: Record<string, string> = {
  sch_bus_drivers_2026: "fam_sch_bus",
  sch_bus_escorts_2026: "fam_sch_bus",
  sch_bus_operators_2026: "fam_sch_bus",
  sch_bus_parents_2026: "fam_sch_bus",
  sch_bus_students_2026: "fam_sch_bus",
  values_edu_framework_2021_trial: "fam_values_edu",
  values_edu_framework_2026: "fam_values_edu",
  chi_hist_jss_2019: "fam_chi_hist",
  chi_hist_jss_ncs_2019: "fam_chi_hist",
};

/** The bucket the quota gate counts against. FAMILY_QUOTA=1 widens it to the family. */
function quotaBucket(id: string): string {
  const canonical = canonicalSource(id);
  if (process.env.FAMILY_QUOTA !== "1") return canonical;
  return QUOTA_FAMILIES[canonical] ?? canonical;
}

/**
 * S226 — lexical re-rank of the already-over-fetched candidates. MEASUREMENT flag.
 *
 * Why here rather than a bigger quota: the chunk-layer diagnosis measured that the
 * chunk which answers is usually not its own source's top three BY COSINE, and
 * widening the quota to 8 traded 4 source-layer passes for 5 chunk-layer ones — a
 * swap, not a gain. The candidate pool is already 40 rows deep (`topK * 5`
 * whenever a quota is active), so re-ordering it costs no extra database work.
 *
 * The cosine is NOT overwritten: the blend decides ORDER only, and the `score` the
 * caller sees is untouched, so nothing downstream that thresholds on it
 * (VAULT_LEAD_SCORE, the judge gate, the footnote lead) changes meaning. Off by
 * default; `LEXICAL_RERANK_WEIGHT` is read only when the flag is on.
 */
const RERANK_DEFAULT_WEIGHT = 0.05;

function rerankLexical<T extends { text: string; score: number }>(
  rows: T[],
  query: string
): T[] {
  if (process.env.FEATURE_LEXICAL_RERANK !== "1" || rows.length === 0) return rows;
  const raw = Number(process.env.LEXICAL_RERANK_WEIGHT);
  const weight = Number.isFinite(raw) && raw > 0 ? raw : RERANK_DEFAULT_WEIGHT;
  // NOT informativeBigrams() here, and the first attempt at this function shows why.
  // It used the candidate set as the document-frequency corpus, which is what the
  // footnote lead does with the footnote corpus — but these candidates all come
  // from the sources the route already selected, so the user's own words are
  // COMMON among them and got dropped as stopwords. Measured: the flag changed
  // nothing at all on a 3-item smoke run, because qBigrams came back empty.
  // Inside an already-narrowed candidate pool, "this chunk literally contains what
  // the user typed" is the signal, not the noise.
  const qBigrams = new Set(cjkBigrams(query));
  if (qBigrams.size === 0) return rows;
  return rows
    .map((row, i) => ({
      row,
      i,
      // Normalised to [0,1] so the weight means the same thing for a 2-character
      // query and a full sentence; the median cosine gap to the 8th slot was
      // 0.0163, so a 0.05 ceiling can reorder without swamping the embedding.
      blend: row.score + weight * (overlapWith(qBigrams, row.text) / qBigrams.size),
    }))
    // Stable: ties keep the cosine order they arrived in.
    .sort((a, b) => b.blend - a.blend || a.i - b.i)
    .map((x) => x.row);
}

// ---------------------------------------------------------------------------
// Search options
// ---------------------------------------------------------------------------

export interface WikiSearchOptions {
  topK?: number;
  minScore?: number;
  topic?: string;
  contentType?: WikiContentType;
  /** Allowlist of source_id values; if provided, only chunks from these sources are returned */
  sourceIds?: string[];
  /**
   * Max chunks per source_id in final results. Prevents a single dominant
   * source (e.g. SAG with 415 chunks) from monopolizing top results.
   * When > 0, the search over-fetches from Supabase (topK * 5) to ensure
   * enough diverse sources are available for the quota gate.
   * Default: undefined (no per-source limit).
   */
  maxPerSource?: number;
  /**
   * Pre-computed query embedding. When supplied the search skips embedFn, so a
   * caller running more than one search for the same query pays for one embedding.
   */
  queryVec?: number[];
  /**
   * S226 — the RAW user query, for lexical re-ranking only (FEATURE_LEXICAL_RERANK).
   *
   * The `query` argument these functions receive is `expandQuery(query, category)`,
   * i.e. the user's words plus up to 21 route vocabulary terms. Those terms are
   * right for the embedding — they align it with the target documents' wording —
   * and wrong for lexical overlap, where they would reward every chunk that talks
   * about the route's topic instead of the chunk that answers the question. The
   * S226 diagnosis measured the failure concentrated in SHORT raw queries
   * (`plain`, 1-3 tokens: FAIL 24/77 against 6/43 for natural sentences), so the
   * re-rank scores against what the user actually typed. Falls back to the
   * expanded query when the caller does not supply this.
   */
  rerankQuery?: string;
}

// ---------------------------------------------------------------------------
// Semantic search via direct REST fetch
// ---------------------------------------------------------------------------

/**
 * Search Channel B using pgvector cosine similarity.
 * Calls match_wiki_chunks via direct fetch to Supabase REST API.
 */
/**
 * Total wall-clock budget for one RPC's retries, across all attempts.
 *
 * WHY A TIME BUDGET AND NOT AN ATTEMPT COUNT (S220)
 *   Both RPC call sites retried 57014 up to three times on an attempt COUNT with no
 *   regard for how long each attempt took. But a 57014 means the statement hit the
 *   server's statement_timeout — so a failing attempt costs the FULL ceiling, and
 *   three of them cost three ceilings while the user waits. Measured in the S220 gold
 *   run, one routed query spent 8842 + 9183 + 8316ms before its third attempt
 *   succeeded: roughly 27 seconds for a search whose own budget is 3 seconds
 *   (anon statement_timeout, verified S219).
 *
 *   The retry's documented purpose still holds and is preserved: a cold-start blip
 *   where the first attempt times out and the next one succeeds quickly. That case
 *   stays inside the budget (3s failure + a fast success). What the budget removes is
 *   retrying a query that has ALREADY consumed its whole allowance — there is nothing
 *   left to retry into, so a second and third full-ceiling wait buys the user nothing
 *   and costs them everything.
 *
 *   6000ms = two 3s ceilings. It permits exactly one retry after a full-ceiling
 *   timeout, and still permits all three attempts when the failures come back fast
 *   (a non-timeout transient), which is the case the count was protecting.
 */
const RPC_RETRY_DEADLINE_MS = 6000;
const RPC_MAX_ATTEMPTS = 3;

/**
 * POST a pgvector RPC, retrying 57014 statement timeouts within the deadline above.
 * Shared by both call sites: the logic was duplicated byte-for-byte apart from the
 * URL, the body and the error label, so the S220 budget fix would otherwise have had
 * to be written twice and would have drifted.
 */
async function postRpcWithRetry(
  rpcUrl: string,
  key: string,
  body: unknown,
  errorLabel: string
): Promise<string> {
  const startedAt = Date.now();
  let rawText = "";
  for (let attempt = 1; attempt <= RPC_MAX_ATTEMPTS; attempt++) {
    const resp = await fetch(rpcUrl, {
      method: "POST",
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    rawText = await resp.text();
    if (resp.ok) return rawText;

    // Any non-57014 error fails fast — retrying won't help.
    const isStatementTimeout = resp.status >= 500 && rawText.includes("57014");
    const budgetSpent = Date.now() - startedAt >= RPC_RETRY_DEADLINE_MS;
    if (!isStatementTimeout || attempt >= RPC_MAX_ATTEMPTS || budgetSpent) {
      throw new Error(`${errorLabel} ${resp.status}: ${rawText}`);
    }
    // brief linear backoff before retrying the RPC (250ms, 500ms)
    await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
  }
  return rawText;
}

export async function searchWiki(
  query: string,
  embedFn: EmbedFn,
  options: WikiSearchOptions = {}
): Promise<WikiSearchResult[]> {
  const { topK, minScore = 0.1, topic, contentType, sourceIds, maxPerSource, queryVec,
          rerankQuery } = options;

  const resolvedQueryVec = queryVec ?? (await embedFn(query));

  // pgvector text format: "[x,x,x,...]"
  // Use toFixed(8) to avoid scientific notation (e.g. 1e-7) which pgvector may reject
  const embeddingStr = `[${resolvedQueryVec.map((v) => v.toFixed(8)).join(",")}]`;

  const supabaseUrl = getSupabaseUrl();
  const supabaseKey = getSupabaseAnonKey();

  // Over-fetch when per-source quota is active so the quota gate has
  // enough diverse sources to choose from (otherwise SAG would still
  // dominate Supabase's initial top-K and leave nothing for smaller sources).
  const overFetchEnabled = !!(maxPerSource && maxPerSource > 0 && topK !== undefined);
  const fetchCount = overFetchEnabled ? (topK as number) * 5 : topK;

  const body: Record<string, unknown> = {
    query_embedding: embeddingStr,
    match_threshold: minScore,
  };
  if (fetchCount !== undefined) {
    body.match_count = fetchCount;
  }

  const rpcUrl = `${supabaseUrl}/rest/v1/rpc/match_wiki_chunks`;

  // Supabase free-tier pgvector (ivfflat probes=8) intermittently returns a
  // 57014 "statement timeout" — most often on the first query after the DB has
  // been idle. Retried transparently (the embedding above is reused, not
  // recomputed) so a cold-start blip never surfaces as a failed search, but
  // bounded by a TIME budget — see RPC_RETRY_DEADLINE_MS.
  const rawText = await postRpcWithRetry(rpcUrl, supabaseKey, body, "Supabase RPC error");

  const rows = JSON.parse(rawText) as Array<WikiChunk & { score: number }>;

  // Post-filters
  let filtered = rows;
  if (topic) filtered = filtered.filter((r) => r.topic === topic);
  if (contentType) filtered = filtered.filter((r) => r.content_type === contentType);
  if (sourceIds && sourceIds.length > 0) {
    const allowSet = new Set(sourceIds);
    filtered = filtered.filter((r) => allowSet.has(r.source_id));
  }

  // Deduplicate by first 80 chars
  const seen = new Set<string>();
  const deduped: typeof filtered = [];
  for (const row of filtered) {
    const key = row.text.slice(0, 80);
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(row);
  }

  // Per-source quota gate (cap = upper bound, never forces low-score chunks in)
  // Walks score-DESC list and skips any chunk from a source that already hit cap.
  // Uses canonicalSource() so redundant ingestions of the same document
  // (e.g. g24 + sag_2025_11) share one quota bucket.
  // S226 — measurement flag, off by default: re-order candidates before the quota
  // gate walks them. See rerankLexical().
  const ordered = rerankLexical(deduped, rerankQuery ?? query);

  let finalRows: typeof deduped;
  if (overFetchEnabled) {
    const sourceCounts = new Map<string, number>();
    const gated: typeof deduped = [];
    const cap = maxPerSource as number;
    const limit = topK as number;
    for (const row of ordered) {
      const canonical = quotaBucket(row.source_id);
      const count = sourceCounts.get(canonical) ?? 0;
      if (count >= cap) continue;
      sourceCounts.set(canonical, count + 1);
      gated.push(row);
      if (gated.length >= limit) break;
    }
    finalRows = gated;
  } else {
    finalRows = ordered;
  }

  return finalRows.map(({ score, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    score,
    channel: "B" as const,
  }));
}

/**
 * Exact vector search after applying a route source allowlist in SQL.
 *
 * This is deliberately a separately named RPC, not an overload of match_wiki_chunks:
 * PostgREST cannot safely disambiguate the historical overloads. The caller keeps this
 * path behind a feature flag and falls back to searchWiki if the RPC is unavailable.
 */
export async function searchWikiRoutedExact(
  query: string,
  embedFn: EmbedFn,
  options: WikiSearchOptions
): Promise<WikiSearchResult[]> {
  const {
    topK,
    minScore = 0.1,
    topic,
    contentType,
    sourceIds,
    maxPerSource,
    queryVec,
    rerankQuery,
  } = options;

  if (!sourceIds || sourceIds.length === 0) return [];

  const resolvedQueryVec = queryVec ?? (await embedFn(query));
  const embeddingStr = `[${resolvedQueryVec.map((v) => v.toFixed(8)).join(",")}]`;

  const overFetchEnabled = !!(maxPerSource && maxPerSource > 0 && topK !== undefined);
  const fetchCount = overFetchEnabled ? topK! * 5 : topK;

  const rpcUrl = `${getSupabaseUrl()}/rest/v1/rpc/match_wiki_chunks_routed`;
  const anonKey = getSupabaseAnonKey();

  const rawText = await postRpcWithRetry(
    rpcUrl,
    anonKey,
    {
      query_embedding: embeddingStr,
      source_ids: sourceIds,
      match_threshold: minScore,
      match_count: fetchCount,
    },
    "Supabase routed RPC error"
  );

  let rows = JSON.parse(rawText) as (WikiChunk & { score: number })[];

  if (topic) rows = rows.filter((r) => r.topic === topic);
  if (contentType) rows = rows.filter((r) => r.content_type === contentType);

  const seen = new Set<string>();
  const deduped: (WikiChunk & { score: number })[] = [];
  for (const row of rows) {
    const key = row.text.slice(0, 80);
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(row);
  }

  // S226 — the routed path is the one production takes (FEATURE_ROUTE_FIRST_SEARCH
  // has been on since 2026-09-09, verified behaviourally 184/184 on 2026-09-15), so
  // both measurement flags have to reach here too or the A/B measures a path nobody
  // runs. Same defaults: unset FEATURE_LEXICAL_RERANK and unset FAMILY_QUOTA leave
  // this loop byte-identical to what it was.
  const ordered = rerankLexical(deduped, rerankQuery ?? query);

  let finalRows = ordered;
  if (overFetchEnabled) {
    const sourceCounts = new Map<string, number>();
    const gated: (WikiChunk & { score: number })[] = [];
    for (const row of ordered) {
      const canonical = quotaBucket(row.source_id);
      const count = sourceCounts.get(canonical) ?? 0;
      if (count >= maxPerSource!) continue;
      sourceCounts.set(canonical, count + 1);
      gated.push(row);
      if (gated.length >= topK!) break;
    }
    finalRows = gated;
  }

  return finalRows.map(({ score, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    score,
    channel: "B" as const,
  }));
}

// ---------------------------------------------------------------------------
// S174 — curated footnote overlay (route- AND ivfflat-independent)
// ---------------------------------------------------------------------------
// The curated 附件細字 footnote chunks (content_type="footnote_curated") must be
// retrievable regardless of (a) category routing — their source_id may sit outside the
// matched SOURCE_SET — and (b) the match_wiki_chunks ivfflat probes=8 recall, which
// intermittently misses freshly-inserted vectors whose list isn't among the query's 8
// probed lists. Because the set is tiny (~33), fetch them ALL once via a plain REST
// SELECT (no RPC / no ivfflat) and score by EXACT cosine. Guaranteed retrieval.
let _footnoteCache: Array<{ chunk: WikiChunk; embedding: number[] }> | null = null;

function parseVec(v: unknown): number[] {
  if (Array.isArray(v)) return v as number[];
  if (typeof v === "string") return JSON.parse(v) as number[];
  return [];
}

/** S219 — in-flight guard. The startup prewarm and a first user request can arrive
 *  together; without this both issue the same embedding-bearing fetch (206 rows,
 *  measured ~1.7s) and the cold start pays it twice. Cleared on settle so a failed
 *  load is retried rather than cached as a rejection. */
let _footnoteInFlight: Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> | null = null;

async function loadFootnoteChunks(): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  if (_footnoteCache) return _footnoteCache;
  if (_footnoteInFlight) return _footnoteInFlight;
  _footnoteInFlight = fetchFootnoteChunks().finally(() => {
    _footnoteInFlight = null;
  });
  return _footnoteInFlight;
}

async function fetchFootnoteChunks(): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?content_type=eq.footnote_curated` +
    `&select=id,hash,text,source_id,title,url,topic,content_type,fact_type,role,school_level,reference_year,embedding`;
  const key = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
  if (!resp.ok) throw new Error(`footnote overlay load ${resp.status}`);
  const rows = (await resp.json()) as Array<WikiChunk & { embedding: unknown }>;
  _footnoteCache = rows.map(({ embedding, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    embedding: parseVec(embedding),
  }));
  return _footnoteCache;
}

/**
 * S196 — bigram document-frequency calibration over the curated footnote corpus.
 *
 * The caller (searchChannelB) needs to ask "does this footnote actually share subject
 * matter with the query, or only register?". Answering that needs to know which bigrams
 * are boilerplate, and that is a property of the whole footnote corpus, not of the six
 * chunks a single query retrieves — calibrating on the retrieved set would mark a query's
 * own topic words as boilerplate whenever retrieval is topically homogeneous.
 *
 * The corpus is already resident (loadFootnoteChunks caches it), so this costs one pass
 * on first use and nothing after. Cleared by invalidateWikiCache with the corpus itself.
 */
const FOOTNOTE_STOPWORD_DF_FRACTION = 0.25;
let _footnoteInformativeCache: Set<string> | null = null;

export async function footnoteInformativeBigrams(): Promise<Set<string>> {
  if (_footnoteInformativeCache) return _footnoteInformativeCache;
  const fns = await loadFootnoteChunks();
  _footnoteInformativeCache = informativeBigrams(
    fns.map((f) => f.chunk.text),
    FOOTNOTE_STOPWORD_DF_FRACTION
  );
  return _footnoteInformativeCache;
}

function cosine(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return na && nb ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
}

/**
 * Exact-cosine search over the curated footnote overlay. Caches the (small) footnote
 * set for the process lifetime — invalidate by restarting the backend after re-ingesting
 * footnotes. Caller should treat this as best-effort (try/catch).
 *
 * `qVec` lets the caller share one raw-query embedding across overlay passes (footnote +
 * spotlight) instead of embedding the same text twice. Omit it and the vector is computed
 * here, exactly as before.
 */
export async function searchFootnotes(
  query: string,
  embedFn: EmbedFn,
  minScore: number,
  topN: number,
  qVec?: number[]
): Promise<WikiSearchResult[]> {
  const fns = await loadFootnoteChunks();
  if (fns.length === 0) return [];
  const vec = qVec ?? (await embedFn(query));
  return fns
    .map((f) => ({ chunk: f.chunk, score: cosine(vec, f.embedding), channel: "B" as const }))
    .filter((r) => r.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

// S193 — spotlight overlay cache, keyed by the requested id-set so a changed
// SPOTLIGHT_SOURCE_IDS list (redeploy) never serves a stale set.
let _spotlightCache: { key: string; rows: Array<{ chunk: WikiChunk; embedding: number[] }> } | null =
  null;

/** Hard ceiling on spotlight chunks pulled into memory — bounds the per-query exact-cosine
 *  cost and the cold-start payload if the id list is ever left to grow unpruned. */
const SPOTLIGHT_CHUNK_CAP = 600;

/** S219 — in-flight guard, keyed like the cache so a changed id-set starts a fresh load.
 *  Same reason as the footnote one: prewarm and first request must not both pay the fetch. */
let _spotlightInFlight: { key: string; p: Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> } | null =
  null;

async function loadSpotlightChunks(
  sourceIds: string[]
): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  const key = [...sourceIds].sort().join(",");
  if (_spotlightCache && _spotlightCache.key === key) return _spotlightCache.rows;
  if (_spotlightInFlight && _spotlightInFlight.key === key) return _spotlightInFlight.p;
  const p = fetchSpotlightChunks(sourceIds, key).finally(() => {
    if (_spotlightInFlight && _spotlightInFlight.key === key) _spotlightInFlight = null;
  });
  _spotlightInFlight = { key, p };
  return p;
}

async function fetchSpotlightChunks(
  sourceIds: string[],
  key: string
): Promise<Array<{ chunk: WikiChunk; embedding: number[] }>> {
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?source_id=in.(${encodeURIComponent(sourceIds.join(","))})` +
    `&select=id,hash,text,source_id,title,url,topic,content_type,fact_type,role,school_level,reference_year,embedding` +
    `&limit=${SPOTLIGHT_CHUNK_CAP}`;
  const anonKey = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` } });
  if (!resp.ok) throw new Error(`spotlight overlay load ${resp.status}`);
  const rows = (await resp.json()) as Array<WikiChunk & { embedding: unknown }>;
  const parsed = rows.map(({ embedding, ...chunk }) => ({
    chunk: chunk as WikiChunk,
    embedding: parseVec(embedding),
  }));
  _spotlightCache = { key, rows: parsed };
  return parsed;
}

/**
 * S193 — Exact-cosine search restricted to a named set of source_ids.
 *
 * Why this exists: `searchWiki` asks Supabase for the global top-(topK*5) chunks above the
 * threshold and only THEN applies the route's source filter in JS. A freshly ingested source
 * with a handful of chunks therefore competes against all ~16k chunks for an over-fetch slot,
 * and loses — so adding it to a SOURCE_SET (or adding routing keywords) cannot make it
 * reachable. This pass mirrors `searchFootnotes`: load the small set with embeddings once,
 * score exactly, and bypass ANN recall entirely. Best-effort — caller wraps in try/catch.
 */
export async function searchSpotlightSources(
  query: string,
  embedFn: EmbedFn,
  sourceIds: string[],
  minScore: number,
  topN: number,
  qVec?: number[]
): Promise<WikiSearchResult[]> {
  if (sourceIds.length === 0) return [];
  const rows = await loadSpotlightChunks(sourceIds);
  if (rows.length === 0) return [];
  const vec = qVec ?? (await embedFn(query));
  return rows
    .map((r) => ({ chunk: r.chunk, score: cosine(vec, r.embedding), channel: "B" as const }))
    .filter((r) => r.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

/**
 * S230 — the cosine of ONE chunk against a caller-supplied vector, read back from the
 * store rather than inferred from a ranking.
 *
 * WHY THIS EXISTS. `VAULT_LEAD_SCORE = 0.70` (searchChannelB.ts) was calibrated by
 * `dev/source/judge_probe.py`, which embeds the BARE query and queries the WHOLE index.
 * Production applies that same number to `mainSearchLead.score`, which comes from a
 * search over `expandQuery(...)` narrowed to the routed SOURCE_SET. S229 measured the
 * gap on the 24 queries the bar was set with: routing does not lift scores (0 to -0.067)
 * but expansion lifts them by up to +0.3226, and the adversarial/control overlap widens
 * from 0.0080 to 0.0817. So the gate reads a scale its number was never set on.
 *
 * This returns the value the gate should be reading: cosine(bare query vector, the lead
 * chunk). Cosine is pairwise, so the number does not depend on what else the index holds
 * or on which SOURCE_SET was searched — reading the chunk's own embedding back gives
 * exactly the score `judge_probe.py`'s whole-index RPC would report for that chunk.
 * `_s230_bareCosineCheck.ts` asserts that equality against the live RPC rather than
 * asking the reader to trust the argument.
 *
 * Why not a second RPC: `match_wiki_chunks_routed` would answer the same question, but
 * through client-side dedup (first 80 chars), lexical re-rank and the per-source quota —
 * a ranking pipeline, where what is needed is one pairwise number. One row by primary
 * key, the same `select=...,embedding` shape the two overlay loaders already use, is
 * both cheaper and free of those interactions.
 *
 * Returns `undefined` when the chunk is gone or carries no usable vector. Throws on a
 * transport / HTTP failure. The gate treats both as "not measured" and runs the judge.
 */
export async function bareCosineForChunk(
  chunkId: string,
  queryVec: number[]
): Promise<number | undefined> {
  if (!chunkId || queryVec.length === 0) return undefined;
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?id=eq.${encodeURIComponent(chunkId)}` +
    `&select=embedding&limit=1`;
  const anonKey = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` } });
  if (!resp.ok) throw new Error(`lead embedding load ${resp.status}`);
  const rows = (await resp.json()) as Array<{ embedding: unknown }>;
  if (rows.length === 0) return undefined;
  const vec = parseVec(rows[0].embedding);
  if (vec.length === 0) return undefined;
  // Rounded to 4dp because the calibration scale is rounded to 4dp: `match_wiki_chunks`
  // returns `round((1 - (embedding <=> query_embedding))::numeric, 4)::float`
  // (dev/supabase_setup.sql:69), so every score the 0.70 bar was set against had already
  // been through this rounding. Verified against live on 2026-09-21: for all 40 rows the
  // whole-index RPC returned for one bare query, the local cosine rounded to 4dp equals
  // the RPC score exactly (0/40 mismatches; unrounded, all 40 differ by up to 5.0e-05).
  // Without this, a chunk whose true cosine is 0.69996 would clear the bar server-side
  // and fail here — a boundary disagreement with the very scale this is restoring.
  return Math.round(cosine(queryVec, vec) * 1e4) / 1e4;
}

/**
 * S211 — lexical lookup for establishment-table rows keyed by class count.
 *
 * Why a lexical pass rather than another cosine one: on the staff establishment tables the
 * class count IS the index column, and a dense embedding cannot align on it. The 36 rows of
 * staff_est_pri are near-identical sentences differing by a handful of digits, so they sit
 * within a few hundredths of each other and the row the question is about does not surface —
 * 「12 班小學有幾多個學位教師」 scores 0.5923 against its own row while neighbouring rows and
 * the surrounding notes score 0.61-0.67. Measured before this pass existed, the platform
 * answered that question with 校長1／不設副校長／學位教師2／助理7／合計10; the row says
 * 校長1／副校長1／學位教師5／助理14／合計21. It picked a different row and labelled it 12 classes.
 *
 * No threshold and no ranking here on purpose. `N 班的教學人員編制` either appears in a chunk
 * or it does not; there is nothing to tune, and that is the point — this is the one lookup in
 * the pipeline that does not go through a similarity score. Two rows match a given N (全日制
 * and 半日制), which is the honest answer to a query that does not say which.
 *
 * Best-effort: the caller wraps it, and a failure leaves the normal result set untouched.
 */
export async function searchEstablishmentRows(
  classCount: number,
  sourceIds: string[]
): Promise<WikiSearchResult[]> {
  if (sourceIds.length === 0 || !Number.isInteger(classCount) || classCount <= 0) return [];
  // The extracted rows read 「核准開辦 12 班的教學人員編制：…」 — the space after the digits is
  // present in the vault text, so match on the phrase rather than on the bare number, which
  // would also hit 「12至17班」 ranges and page numbers.
  const needle = `%${classCount} 班的教學人員編制%`;
  const url =
    `${getSupabaseUrl()}/rest/v1/wiki_chunks?source_id=in.(${encodeURIComponent(sourceIds.join(","))})` +
    `&text=ilike.${encodeURIComponent(needle)}` +
    `&select=id,hash,text,source_id,title,url,topic,content_type,fact_type,role,school_level,reference_year` +
    `&limit=8`;
  const anonKey = getSupabaseAnonKey();
  const resp = await fetch(url, { headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` } });
  if (!resp.ok) throw new Error(`establishment overlay load ${resp.status}`);
  const rows = (await resp.json()) as WikiChunk[];
  // A lexical hit is an exact match on the row the question names, so it is scored 1: it is
  // not competing with the cosine results, it is answering the question they cannot reach.
  return rows.map((chunk) => ({ chunk, score: 1, channel: "B" as const }));
}

/**
 * S219 — preload both Channel B overlay caches off the request path.
 *
 * WHY: `searchFootnotes` and `searchSpotlightSources` each load their whole corpus WITH
 * embeddings on first use — measured 1.66s (206 rows) and 1.79s (267 rows) against live.
 * Both are awaited in sequence inside the search handler, so before this the first user
 * request after every restart paid ~3.4s that no later request pays. Server startup calls
 * this without awaiting, exactly like `initFactEmbeddingCache`.
 *
 * This moves the cost off the user-visible path; it does not reduce it. The cost is the
 * embedding payload itself (measured ~16ms per row shipped as JSON text), which no index
 * can help — removing it needs server-side similarity, i.e. a new RPC.
 *
 * Best-effort by contract: a failure here must leave the lazy path untouched, so the caller
 * swallows the rejection and the next search loads normally.
 */
export async function preloadOverlayCaches(spotlightSourceIds: string[]): Promise<void> {
  await Promise.all([
    // footnoteInformativeBigrams() also forces the footnote corpus, and is itself a
    // first-use cost (one pass over 206 chunk texts) the first request would otherwise pay.
    footnoteInformativeBigrams(),
    spotlightSourceIds.length > 0 ? loadSpotlightChunks(spotlightSourceIds) : Promise.resolve([]),
  ]);
}

/** S219 — overlay cache state for /health, mirroring `cache_a`. */
export function overlayCacheStatus(): {
  warm: boolean;
  footnote: number | null;
  spotlight: number | null;
} {
  return {
    warm: _footnoteCache !== null && _spotlightCache !== null,
    footnote: _footnoteCache ? _footnoteCache.length : null,
    spotlight: _spotlightCache ? _spotlightCache.rows.length : null,
  };
}

export function invalidateWikiCache(): void {
  _footnoteCache = null;
  _spotlightCache = null;
  // S219 — an in-flight load started before invalidation would otherwise repopulate
  // the cache with pre-invalidation rows the moment it settles.
  _footnoteInFlight = null;
  _spotlightInFlight = null;
  // S196 — derived from _footnoteCache, so it must not outlive it.
  _footnoteInformativeCache = null;
}
