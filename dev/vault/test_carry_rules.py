#!/usr/bin/env python3
"""
Self-test for the chunk-carry rules and the refetch guard that protects them.

S206 lifted `carry_pages` out of build_wiki_index so expand_vault could reuse the
RULE without sharing the chunker; S207 added `carry_sections` on the same contract.
Both are load-bearing: a regression silently costs every re-ingested chunk its
"頁 N ↗" anchor or its section URL, and nothing else in the pipeline would notice.

S209 added `refetch_block_reason`: carrying a section URL is worth nothing if a
single `--fetch` can throw the multi-page extract away. The guard is asserted
here rather than beside the fetch code because the invariant it protects is the
same one the carry rules protect.

Usage:
  python3 dev/vault/test_carry_rules.py --self-test
  python3 dev/vault/test_carry_rules.py --prove-assertions   # break the impl, expect failures
"""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wiki_index as bwi  # noqa: E402
import expand_vault as ev  # noqa: E402

FAILS: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        FAILS.append(label)


def run_page_tests(carry_pages) -> None:
    print("carry_pages():")
    check("no markers at all → byte-identical (chunk ids stay stable)",
          carry_pages(["alpha", "beta"]) == ["alpha", "beta"])
    check("chunks before the first marker are left unchanged",
          carry_pages(["front", "=== Page 3 ===\nbody"])[0] == "front")
    check("a marker-less chunk inherits the preceding chunk's page",
          carry_pages(["=== Page 3 ===\nbody", "tail"])[1] == "=== Page 3 ===\ntail")
    check("a chunk spanning two markers carries the page it ENDS on",
          carry_pages(["=== Page 3 ===\na\n=== Page 4 ===\nb", "tail"])[1]
          == "=== Page 4 ===\ntail")
    check("output length always equals input length",
          len(carry_pages(["a", "=== Page 1 ===", "b", "c"])) == 4)
    # S209 — a page number belongs to one document. In a multi-document extract a
    # chunk can open the next section before that document's first page marker;
    # inheriting the previous document's page cited a page past the end of the
    # file (g28: a 1-page circular was handed page 2, a 3-page one page 8).
    check("a chunk that opens a new section does not inherit the previous page",
          carry_pages(["=== Page 8 ===\ntail of doc A", "=== doc_b ===\nintro"])[1]
          == "=== doc_b ===\nintro")
    check("the reset persists until the new document's own page marker",
          carry_pages(["=== Page 8 ===\nA", "=== doc_b ===\nintro", "more intro"])[2]
          == "more intro")
    check("the new document's own page marker resumes carrying",
          carry_pages(["=== Page 8 ===\nA", "=== doc_b ===\n=== Page 1 ===\nx", "y"])[2]
          == "=== Page 1 ===\ny")
    check("a page marker alone never counts as opening a section",
          carry_pages(["=== Page 3 ===\na", "b"])[1] == "=== Page 3 ===\nb")
    check("two page markers on one line do not fake a section boundary",
          carry_pages(["=== Page 5 === 6 (Blank Page) === Page 6 ===", "tail"])[1]
          == "=== Page 6 ===\ntail")


def run_section_tests(carry_sections) -> None:
    print("carry_sections():")
    check("no markers at all → all None (source keeps its header URL)",
          carry_sections(["alpha", "beta"]) == [None, None])
    check("chunks before the first marker resolve to None",
          carry_sections(["front", "=== chapter-one ===\nbody"])[0] is None)
    check("a marker-less chunk inherits the preceding chunk's section",
          carry_sections(["=== chapter-one ===\nbody", "tail"])[1] == "chapter-one")
    check("a chunk spanning two markers carries the section it ENDS in",
          carry_sections(["=== chapter-one ===\na\n=== chapter-two ===\nb", "tail"])[1]
          == "chapter-two")
    check("`=== Page 12 ===` is never read as a section label",
          carry_sections(["=== Page 12 ===\nbody"]) == [None])
    check("a page marker does not clear a section already carried",
          carry_sections(["=== searching_chi ===\na", "=== Page 2 ===\nb"])[1]
          == "searching_chi")
    check("a label with spaces is kept whole",
          carry_sections(["=== general principles at school_chi ===\na"])[0]
          == "general principles at school_chi")
    check("a marker arriving mid-line (chunker overlap tail) is still seen",
          carry_sections(["…培育課程。 === chapter-one ===\n[資料庫] 第一章"])[0] == "chapter-one")
    check("two page markers on one line do not fake a section around the text between",
          carry_sections(["=== Page 5 === 6 (Blank Page) === Page 6 ==="]) == [None])
    check("a real section survives a page marker on the same line",
          carry_sections(["=== searching_chi === === Page 1 === 內文"])[0] == "searching_chi")
    check("`===` inside a line of prose is not a marker",
          carry_sections(["the operator === means identity"]) == [None])
    check("output length always equals input length",
          len(carry_sections(["a", "=== s ===", "b", "c"])) == 4)


def run_refetch_guard_tests(block_reason) -> None:
    """The registry field, the fail-closed reading of it, and the fetch loop."""
    print("refetch guard:")
    check("no `refetch_blocked` key → re-fetch allowed",
          block_reason({"source_id": "x"}) is None)
    check("explicit false → re-fetch allowed (opt-out is writable)",
          block_reason({"source_id": "x", "refetch_blocked": False}) is None)
    check("a reason string is returned, trimmed",
          block_reason({"refetch_blocked": "  crawled  "}) == "crawled")
    check("key present but unreadable (True) still blocks — fail closed",
          bool(block_reason({"refetch_blocked": True})))

    # Registry invariant: the guard must cover every source that carries section
    # URLs, not just the two known today. A future multi-page crawl added without
    # the field fails here instead of silently at the next --fetch.
    registry = ev.load_registry()
    carriers = [s for s in registry if s.get("section_urls")]
    check("registry still has section-URL carriers to protect", len(carriers) >= 2)
    unguarded = [s["source_id"] for s in carriers if not block_reason(s)]
    check(f"every section_urls source is refetch-blocked (unguarded: {unguarded or 'none'})",
          not unguarded)
    for sid in ("g14", "g17"):
        row = next((s for s in registry if s.get("source_id") == sid), None)
        check(f"{sid} is refetch-blocked", bool(row) and bool(block_reason(row)))

    # End-to-end: the fetch loop refuses BEFORE the download, and says so. Dry-run
    # keeps this offline — the guard sits ahead of the dry-run short-circuit, so a
    # blocked source prints the lock and an ordinary one does not.
    blocked_src = {"source_id": "fake_blocked", "source_type": "html",
                   "url_primary": "https://example.invalid/x.html", "title": "t",
                   "refetch_blocked": "crawled over ten pages"}
    plain_src = dict(blocked_src)
    del plain_src["refetch_blocked"]
    plain_src["source_id"] = "fake_plain"

    def fetch_output(src) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ev.run_fetch([src], dry_run=True)
        return buf.getvalue()

    out_blocked, out_plain = fetch_output(blocked_src), fetch_output(plain_src)
    check("run_fetch refuses a blocked source and names the reason",
          "refetch blocked" in out_blocked and "crawled over ten pages" in out_blocked)
    check("a blocked source never reaches the dry-run/download branch",
          "[dry-run] skipped" not in out_blocked)
    check("an ordinary source is untouched by the guard",
          "[dry-run] skipped" in out_plain and "refetch blocked" not in out_plain)
    check("the summary counts it as blocked, not as skipped or failed",
          "1 blocked," in out_blocked and "0 blocked," in out_plain)

    # S209 — a multi-document extract must be cut at its section markers BEFORE
    # sizing, or a chunk holds the tail of one PDF and the head of the next: it is
    # assigned the new document's URL while its text still carries the previous
    # document's page marker, which the backend parses at read time. carry_pages
    # cannot fix that — the stale page is inside the text.
    body = "front\n=== doc_a ===\n=== Page 1 ===\nA\n=== doc_b ===\n=== Page 1 ===\nB"
    parts = ev.split_on_section_markers(body)
    check("split: front-matter, then one part per document",
          len(parts) == 3 and parts[1].strip().startswith("=== doc_a ==="))
    check("split: every document part carries its own section marker",
          all(p.strip().startswith("=== doc_") for p in parts[1:]))
    check("split: a body with no section markers stays one part",
          ev.split_on_section_markers("plain\n=== Page 2 ===\nx") == ["plain\n=== Page 2 ===\nx"])
    check("split: two page markers on one line are not a section boundary",
          len(ev.split_on_section_markers("=== Page 5 === 6 (Blank) === Page 6 ===\nx")) == 1)

    # The override exists and is the ONLY way through.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.run_fetch([blocked_src], dry_run=True, allow_blocked=True)
    check("--allow-blocked-refetch lets a blocked source through",
          "[dry-run] skipped" in buf.getvalue())


def main() -> int:
    prove = "--prove-assertions" in sys.argv
    if prove:
        # Deliberately break both rules and require the tests to notice. A green
        # suite proves nothing unless it can also go red (S206 discipline).
        carry_pages = lambda chunks: list(chunks)                      # noqa: E731
        carry_sections = lambda chunks: [None] * len(chunks)           # noqa: E731
        block_reason = lambda source: None                             # noqa: E731
        ev.refetch_block_reason = block_reason   # run_fetch resolves it by name
        print("PROVE MODE — implementations replaced with no-ops; failures are the point.\n")
    else:
        carry_pages, carry_sections = bwi.carry_pages, bwi.carry_sections
        block_reason = ev.refetch_block_reason

    run_page_tests(carry_pages)
    run_section_tests(carry_sections)
    run_refetch_guard_tests(block_reason)

    print()
    if prove:
        ok = len(FAILS) >= 19
        print(f"{'ALL PASS' if ok else 'BROKEN'} — {len(FAILS)} assertions fired against the no-op "
              f"implementations (expected ≥ 19: 11 carry rules + 8 refetch guard).")
        return 0 if ok else 1
    if FAILS:
        print(f"{len(FAILS)} FAILED: " + "; ".join(FAILS))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
