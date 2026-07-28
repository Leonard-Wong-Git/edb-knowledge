/**
 * Shared CJK bigram helpers.
 *
 * `cjkBigrams` lived in `api/checklistRevise.ts` (S161) and is re-exported from there so
 * every existing import keeps working. It moved here in S196 because a second consumer
 * appeared in `lib/` (the curated-footnote lead gate), and a `lib/ → api/` import would
 * have inverted the layering just to reach four lines of string handling.
 */

/** Every adjacent CJK pair in `s`, with non-CJK characters removed first. */
export function cjkBigrams(s: string): string[] {
  const cjk = (s || "").replace(/[^一-鿿]/g, "");
  const out: string[] = [];
  for (let i = 0; i + 1 < cjk.length; i++) out.push(cjk.slice(i, i + 2));
  return out;
}

/**
 * Self-calibrating stopword filter: the set of bigrams that occur in at most
 * `dfFraction` of `corpus`. A bigram present in most documents of a corpus carries no
 * discriminating signal there (學校/教育/津貼 across EDB material), so leaving it in lets
 * boilerplate manufacture apparent overlap between a query and an unrelated document.
 *
 * Same device as the checklist gap gate (STOPWORD_DF_FRACTION in checklistRevise.ts);
 * calibrating against the corpus rather than a hand-written stopword list means it stays
 * correct as the corpus grows.
 */
export function informativeBigrams(corpus: string[], dfFraction: number): Set<string> {
  const df = new Map<string, number>();
  for (const text of corpus) {
    for (const bg of new Set(cjkBigrams(text))) df.set(bg, (df.get(bg) ?? 0) + 1);
  }
  const cap = Math.max(2, Math.ceil(corpus.length * dfFraction));
  const out = new Set<string>();
  for (const [bg, n] of df) if (n <= cap) out.add(bg);
  return out;
}

/**
 * The query's own informative bigrams. An EMPTY set means the query gives this measure
 * nothing to work with — an English or numeric query ("NET grant", "MPF") has no CJK
 * bigrams at all — and callers must treat that as "cannot judge", never as "no overlap".
 * Conflating the two turns a gate into a blanket refusal for non-Chinese queries.
 */
export function queryInformativeBigrams(query: string, informative: Set<string>): Set<string> {
  return new Set(cjkBigrams(query).filter((b) => informative.has(b)));
}

/** How many of `queryBigrams` appear in `text`. */
export function overlapWith(queryBigrams: Set<string>, text: string): number {
  if (queryBigrams.size === 0) return 0;
  const tb = new Set(cjkBigrams(text));
  let n = 0;
  for (const b of queryBigrams) if (tb.has(b)) n++;
  return n;
}
