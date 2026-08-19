#!/usr/bin/env python3
"""
Self-test for the two chunk-carry rules shared by both ingestion pipelines.

S206 lifted `carry_pages` out of build_wiki_index so expand_vault could reuse the
RULE without sharing the chunker; S207 added `carry_sections` on the same contract.
Both are load-bearing: a regression silently costs every re-ingested chunk its
"頁 N ↗" anchor or its section URL, and nothing else in the pipeline would notice.

Usage:
  python3 dev/vault/test_carry_rules.py --self-test
  python3 dev/vault/test_carry_rules.py --prove-assertions   # break the impl, expect failures
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wiki_index as bwi  # noqa: E402

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


def main() -> int:
    prove = "--prove-assertions" in sys.argv
    if prove:
        # Deliberately break both rules and require the tests to notice. A green
        # suite proves nothing unless it can also go red (S206 discipline).
        carry_pages = lambda chunks: list(chunks)                      # noqa: E731
        carry_sections = lambda chunks: [None] * len(chunks)           # noqa: E731
        print("PROVE MODE — implementations replaced with no-ops; failures are the point.\n")
    else:
        carry_pages, carry_sections = bwi.carry_pages, bwi.carry_sections

    run_page_tests(carry_pages)
    run_section_tests(carry_sections)

    print()
    if prove:
        ok = len(FAILS) >= 7
        print(f"{'ALL PASS' if ok else 'BROKEN'} — {len(FAILS)} assertions fired against the no-op "
              f"implementations (expected ≥ 6).")
        return 0 if ok else 1
    if FAILS:
        print(f"{len(FAILS)} FAILED: " + "; ".join(FAILS))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
