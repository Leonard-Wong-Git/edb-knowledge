#!/usr/bin/env python3
"""_s213_corpus.py — read-only corpus lookup so every gold label is auditable.

Phase 1 requires that a gold label be verified against the original document or
an existing auditable chunk, never guessed by a model. This tool is the single
way the gold set is allowed to acquire a passage signature or a page number:
you find a real chunk, and you copy its own text and its own page field.

It reads a cached snapshot of `wiki_chunks` (id, text, source_id, title, url,
page …). It never writes and never calls the search endpoint — so it tells you
what the corpus CONTAINS, which is a different question from what the retriever
RETURNS. Do not use a hit here as evidence that a query works.

USAGE
  python3 dev/_s213_corpus.py sources                       # serving sources + counts
  python3 dev/_s213_corpus.py sources --grep 幼稚園          # filter by id/title
  python3 dev/_s213_corpus.py find "教師與班級比例" --limit 5  # search chunk text
  python3 dev/_s213_corpus.py find "校車" --source g24
  python3 dev/_s213_corpus.py show <chunk_id>               # full chunk + page
  python3 dev/_s213_corpus.py signature <chunk_id> --start 40 --len 30
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = Path(os.environ.get(
    "S213_STORE_CACHE",
    "/private/tmp/claude-501/-Users-leonard-Downloads-Claude-Project-"
    "Claude-edb-knowledge/dd80ac3a-1ae0-4b24-8758-1a3f23ce6d2a/scratchpad/"
    "store_s213.json"))


def squeeze(s: str) -> str:
    """Same normalisation the harness uses: PDF text layers break lines mid-word."""
    return re.sub(r"\s+", "", s or "")


PAGE_MARK = re.compile(r"={2,}\s*Page\s*(\d+)\s*={2,}", re.I)
SECTION_MARK = re.compile(r"={2,}[ \t]*[^=\n]{1,120}?[ \t]*={2,}")


def fold(s: str) -> str:
    """NFKC-fold so a compatibility ideograph equals its unified twin.

    868 chunks (4.93%, 112 sources) carry CJK Compatibility Ideographs
    (U+F900–U+FAFF) — 110 distinct characters, e.g. 理 is U+F9E4 rather than
    U+7406. They are visually identical and semantically the same character,
    but a byte comparison says they differ, so:

      - a passage signature typed with normal codepoints can NEVER match those
        chunks, and a perfectly correct retrieval is scored FAIL;
      - a user typing 「臨時護理室」 does not literally match the passage that
        answers them.

    This was found the hard way: a gold label whose text was verbatim correct
    was quarantined because five of its characters were the compatibility
    variants. Every comparison in this toolchain folds first.

    NOTE: `eval_retrieval.chunk_verdict_for` does NOT fold — it compares under
    `squeeze()` alone, so the shipped harness still has this defect.
    """
    return unicodedata.normalize("NFKC", s or "")


def clean_for_match(raw: str) -> str:
    """What the USER and the harness actually see — markers already removed.

    `cleanChunkText` (searchChannelB.ts:1089) strips `=== Page N ===` and then
    `=== <section> ===` before a chunk is returned, so a passage signature cut
    from the RAW text can contain a marker that no response will ever carry, and
    the assertion would fail against a perfectly correct answer. Order matters
    and is preserved from the TypeScript: page markers first, section markers
    second (two page markers on one line otherwise look like a section wrapping
    the body text between them, and the body would be deleted).

    Whitespace normalisation from the original is deliberately NOT ported: the
    harness compares under `squeeze()`, which removes all whitespace anyway.
    """
    return fold(SECTION_MARK.sub(" ", PAGE_MARK.sub(" ", raw or "")))


def dominant_page(raw: str) -> int | None:
    """Python mirror of `extractDominantPage` (searchChannelB.ts:1054).

    `wiki_chunks` HAS NO `page` COLUMN — the page a user sees is derived at
    query time from the `=== Page N ===` markers in the chunk's own text. A gold
    label that invented its own page rule would be asserting against a number
    the product never produces, so this is a deliberate line-by-line port:
    weight each page by its non-whitespace characters, attribute text before the
    first marker to the preceding page, and keep the EARLIER page on a tie
    (strict `>`), exactly as the TypeScript does.
    """
    marks = [(int(m.group(1)), m.start(), m.end()) for m in PAGE_MARK.finditer(raw or "")]
    if not marks:
        return None
    weight: dict[int, int] = {}

    def add(page: int, text: str) -> None:
        n = len(re.sub(r"\s+", "", text))
        if n > 0:
            weight[page] = weight.get(page, 0) + n

    add(max(1, marks[0][0] - 1), raw[:marks[0][1]])
    for i, (page, _s, e) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(raw)
        add(page, raw[e:end])
    best_page, best_w = None, 0
    for page, w in weight.items():          # insertion order = earliest first
        if w > best_w:
            best_page, best_w = page, w
    return best_page


def load(cache: Path) -> list[dict]:
    if not cache.exists():
        raise SystemExit(
            f"corpus cache not found: {cache}\n"
            f"  regenerate with:  set -a && . backend/.env && set +a && "
            f"python3 dev/_s213_recon.py --cache {cache}")
    rows = json.loads(cache.read_text(encoding="utf-8"))
    assert isinstance(rows, list) and all(isinstance(r, dict) for r in rows), \
        "cache is not a list of rows"
    return rows


def cmd_sources(rows: list[dict], args) -> int:
    per = collections.Counter(r.get("source_id") for r in rows)
    title = {}
    for r in rows:
        title.setdefault(r.get("source_id"), r.get("title"))
    items = sorted(per.items(), key=lambda kv: -kv[1])
    if args.grep:
        g = args.grep
        items = [(s, n) for s, n in items
                 if g in (s or "") or g in (title.get(s) or "")]
    print(f"{'source_id':<34}{'chunks':>7}  title")
    for sid, n in items[:args.limit]:
        print(f"{sid:<34}{n:>7}  {title.get(sid)}")
    print(f"\n{len(items)} sources shown ({len(per)} serving in total)")
    return 0


def cmd_find(rows: list[dict], args) -> int:
    # Fold before comparing: 868 chunks carry CJK compatibility ideographs, so
    # a search typed with normal codepoints silently misses them (see `fold`).
    needle = squeeze(fold(args.text))
    hits = []
    for r in rows:
        if args.source and r.get("source_id") != args.source:
            continue
        if needle in squeeze(fold(r.get("text", ""))):
            hits.append(r)
    print(f"{len(hits)} chunk(s) contain {args.text!r}"
          + (f" in {args.source}" if args.source else ""))
    per = collections.Counter(r.get("source_id") for r in hits)
    if len(per) > 1:
        print("  spread: " + ", ".join(f"{s}×{n}" for s, n in per.most_common(8)))
    for r in hits[:args.limit]:
        raw = re.sub(r"\s+", " ", fold(r.get("text", "")))
        i = squeeze(raw).find(needle)
        print(f"\n--- {r['id']}")
        print(f"    source={r.get('source_id')}  page={dominant_page(r.get('text',''))}  "
              f"title={r.get('title')!r}")
        print(f"    url={r.get('url') or '(none)'}")
        print(f"    …{raw[max(0, i - 60):i + 200]}…")
    return 0


def cmd_show(rows: list[dict], args) -> int:
    for r in rows:
        if r.get("id") == args.chunk_id:
            info = {k: r.get(k) for k in
                    ("id", "source_id", "title", "url", "content_type", "topic")}
            # `wiki_chunks` has no page column; the page a user sees is derived
            # from the chunk's own `=== Page N ===` markers at query time.
            info["page"] = dominant_page(r.get("text", ""))
            print(json.dumps(info, ensure_ascii=False, indent=1))
            print("\n--- text ---")
            print(r.get("text", ""))
            return 0
    print(f"not found: {args.chunk_id}", file=sys.stderr)
    return 1


def cmd_signature(rows: list[dict], args) -> int:
    """Emit a verbatim slice usable as `expected_passage_signature`.

    Uniqueness is checked against the whole corpus and reported: a signature
    that matches many chunks cannot distinguish the right passage from a
    duplicate, and the gold entry has to say so.
    """
    row = next((r for r in rows if r.get("id") == args.chunk_id), None)
    if row is None:
        print(f"not found: {args.chunk_id}", file=sys.stderr)
        return 1
    # Cut from the CLEANED text: markers are stripped before a chunk is served,
    # so a signature carrying one could never match a real response.
    sq = squeeze(clean_for_match(row.get("text", "")))
    sig = sq[args.start:args.start + args.len]
    if not sig:
        print("empty slice — check --start/--len against the chunk length "
              f"({len(sq)} squeezed chars, markers removed)", file=sys.stderr)
        return 1
    matches = [r for r in rows
               if sig in squeeze(clean_for_match(r.get("text", "")))]
    print(json.dumps({
        "chunk_id": row["id"], "source_id": row.get("source_id"),
        "page": dominant_page(row.get("text", "")), "signature": sig,
        "matches_in_corpus": len(matches),
        "matching_sources": sorted({r.get("source_id") for r in matches}),
    }, ensure_ascii=False, indent=1))
    if len(matches) > 1:
        print("\n⚠️  signature is NOT unique — record the duplicates as "
              "`acceptable_alternatives`, or pick a different slice.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sources"); s.add_argument("--grep"); s.add_argument("--limit", type=int, default=60)
    f = sub.add_parser("find"); f.add_argument("text"); f.add_argument("--source"); f.add_argument("--limit", type=int, default=5)
    sh = sub.add_parser("show"); sh.add_argument("chunk_id")
    sg = sub.add_parser("signature"); sg.add_argument("chunk_id")
    sg.add_argument("--start", type=int, default=0); sg.add_argument("--len", type=int, default=30)

    args = ap.parse_args()
    rows = load(args.cache)
    return {"sources": cmd_sources, "find": cmd_find,
            "show": cmd_show, "signature": cmd_signature}[args.cmd](rows, args)


if __name__ == "__main__":
    raise SystemExit(main())
