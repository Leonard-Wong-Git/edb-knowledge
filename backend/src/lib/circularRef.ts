/**
 * S241 — EDB circular numbers: read them from a query, and from a circular's own header.
 *
 * WHY. A query that names a circular by number (「教育局通函第134/2026號」) is asking for one
 * specific document, and an embedding cannot tell 第134號 from 第67號. Measured on
 * production (S241, 75 circulars in the store, one query each, synthesize:false): the
 * named circular reached the five-chunk synthesis window 2/75 times, rank 0 never, and
 * 68/75 times it was not in the eight results at all — almost every query returned the
 * same three unrelated documents. The number is an identifier, so it is looked up, not
 * scored.
 *
 * Pure functions only; the store read and the search wiring live in wikiRepository and
 * searchChannelB.
 */

export type CircularKind = "通函" | "通告";

/** `通函|134|2026` — one key format for both the query side and the header side. */
export function circularKey(kind: CircularKind, num: number, year: number): string {
  return `${kind}|${num}|${year}`;
}

/** NFKC folds full-width digits and slashes (１３４／２０２６); whitespace is dropped
 *  because extracted PDF text spaces digits out (「第1 4 2 / 2 0 2 6 號」). */
function squash(s: string): string {
  return (s || "").normalize("NFKC").replace(/\s+/g, "");
}

// Chinese form; 第 and 號 optional because users drop them. Year must be four digits so
// a bare 「通函第134號」 (no year) does not guess a year.
const ZH = /(通函|通告)第?(\d{1,3})\/(\d{4})號?/;
// English forms. Memorandum before plain circular: "EDBCM" also starts with "EDBC".
const EN_CM = /(?:EDBCM|EDBCIRCULARMEMORANDUM|CIRCULARMEMORANDUM)(?:NO\.?)?(\d{1,3})\/(\d{4})/i;
const EN_C = /(?:EDBC|EDBCIRCULAR|CIRCULAR)(?:NO\.?)?(\d{1,3})\/(\d{4})/i;

/** The circular a query names, or null. 通函 = circular memorandum, 通告 = circular. */
export function parseCircularRef(query: string): string | null {
  const q = squash(query);
  const zh = ZH.exec(q);
  if (zh) return circularKey(zh[1] as CircularKind, Number(zh[2]), Number(zh[3]));
  const cm = EN_CM.exec(q);
  if (cm) return circularKey("通函", Number(cm[1]), Number(cm[2]));
  const c = EN_C.exec(q);
  if (c) return circularKey("通告", Number(c[1]), Number(c[2]));
  return null;
}

// A circular's own number sits right after its file reference: 「檔號：…教育局通函第N/YYYY號」.
// Anchoring on 檔號 and on the first page is what keeps out the documents that merely CITE
// a circular — the first draft read any header-like number in a chunk's first 300 chars
// and mapped 《學前機構辦學手冊》 to five circulars it quotes.
const HEADER = /檔號.{0,80}?教育局(通函|通告)第(\d{1,3})\/(\d{4})號/;
const HEADER_WINDOW = 400;

/** The circular number a chunk declares as its own, or null. */
export function headerCircularKey(text: string): string | null {
  const t = text || "";
  if (!t.includes("=== Page 1 ===")) return null;
  const m = HEADER.exec(squash(t.slice(0, HEADER_WINDOW)));
  return m ? circularKey(m[1] as CircularKind, Number(m[2]), Number(m[3])) : null;
}

/**
 * The source_ids a circular is normally ingested under, for an exact-id lookup that does
 * not depend on scanning chunk text (S241 patch 2: the text scan behind the full index
 * can exceed the anon role's 3 s statement_timeout when the database is cold; an id
 * equality read stays well under it). Names with a topic suffix
 * (`edbcm141_2025_blnst`) are not guessable and still come from the full index.
 * A guess is only a candidate — the header of the fetched chunk must confirm the number.
 */
export function candidateSourceIds(key: string): string[] {
  const [kind, numStr, yearStr] = key.split("|");
  const n = Number(numStr);
  const pad = String(n).padStart(3, "0");
  const y = yearStr;
  return kind === "通函"
    ? [`edbcm${n}_${y}`, `edbcm${pad}_${y}`, `EDBCM_${n}_${y}_TC`, `EDBCM_${n}_${y}_E`]
    : [`edbc${n}_${y}`, `edbc${pad}_${y}`, `EDBC_${n}_${y}_E`, `EDBC_${n}_${y}_C`];
}

/**
 * key → source_id. A source that declares two different numbers, or a number declared by
 * two sources, is dropped rather than guessed: a wrong forced lead is worse than none,
 * because the search then answers from the wrong circular with full confidence.
 */
export function buildCircularIndex(rows: Array<{ source_id: string; text: string }>): Map<string, string> {
  const bySource = new Map<string, Set<string>>();
  for (const r of rows) {
    const key = headerCircularKey(r.text);
    if (!key) continue;
    if (!bySource.has(r.source_id)) bySource.set(r.source_id, new Set());
    bySource.get(r.source_id)!.add(key);
  }
  const byKey = new Map<string, Set<string>>();
  for (const [sid, keys] of bySource) {
    if (keys.size !== 1) continue;
    const [key] = keys;
    if (!byKey.has(key)) byKey.set(key, new Set());
    byKey.get(key)!.add(sid);
  }
  const out = new Map<string, string>();
  for (const [key, sids] of byKey) if (sids.size === 1) out.set(key, [...sids][0]);
  return out;
}
