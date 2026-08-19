#!/usr/bin/env python3
"""
S207 one-shot: clean the two crawled-HTML vault extracts in place.

g14 and g17 were crawled sub-page by sub-page in S146 by a script that no longer
exists, so they cannot be re-fetched (`expand_vault --fetch` would collect only
url_primary and destroy the other sections). The two defects are therefore repaired
on the stored extract:

  (a) g14's header title says 計劃指引; EDB and source_registry.json both say
      課程指引 — the wrong one is what every live chunk shows the user.
  (b) EDB's navigation / footer chrome sits INSIDE the content column, so it survived
      extraction and reads back to the user as part of the quoted passage.

Gate: the rewrite must be provably nothing but (a) + whole-line deletions drawn from
the chrome whitelist. Line multisets are compared before and after; any other change
aborts the write.

  python3 dev/_s207_clean_html_extracts.py --dry-run
  python3 dev/_s207_clean_html_extracts.py --apply
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dev" / "vault"))
from expand_vault import WEB_CHROME_LINES, WEB_CHROME_RE  # noqa: E402

TITLE_FIXES = {"g14": ("# title: 校本資優培育計劃指引", "# title: 校本資優培育課程指引")}
SOURCES = ["g14", "g17"]


def is_chrome(line: str) -> bool:
    probe = line.strip()
    return probe in WEB_CHROME_LINES or bool(WEB_CHROME_RE.match(probe))


def process(sid: str, apply: bool) -> bool:
    path = ROOT / "dev" / "vault" / sid / f"extract_{sid}.txt"
    old = path.read_text(encoding="utf-8")
    old_lines = old.split("\n")

    kept, removed = [], []
    for line in old_lines:
        (removed if is_chrome(line) else kept).append(line)

    new = "\n".join(kept)
    title_changed = False
    if sid in TITLE_FIXES:
        before, after = TITLE_FIXES[sid]
        if before in new:
            new = new.replace(before, after, 1)
            title_changed = True

    # ── gate: every difference must be accounted for ──────────────────────────
    exp = Counter(old_lines)
    for line in removed:
        exp[line] -= 1
    if title_changed:
        before, after = TITLE_FIXES[sid]
        exp[before] -= 1
        exp[after] += 1
    exp = +exp                      # drop zero counts
    got = +Counter(new.split("\n"))
    ok = exp == got

    print(f"\n=== {sid} ===")
    print(f"  lines {len(old_lines)} → {len(new.split(chr(10)))}   chrome lines removed: {len(removed)}")
    for label, count in sorted(Counter(l.strip() for l in removed).items()):
        print(f"    −{count:>3}  {label}")
    if title_changed:
        print(f"    title: {TITLE_FIXES[sid][0]}  →  {TITLE_FIXES[sid][1]}")
    print(f"  GATE (diff is chrome + title only): {'PASS' if ok else 'FAIL'}")
    if not ok:
        for line, n in (exp - got).items():
            print(f"    expected but missing ×{n}: {line[:80]!r}")
        for line, n in (got - exp).items():
            print(f"    unexpected addition ×{n}: {line[:80]!r}")
        return False

    if apply:
        path.write_text(new, encoding="utf-8")
        print("  ✍️  written")
    else:
        print("  (dry-run — not written)")
    return True


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    results = [process(sid, apply) for sid in SOURCES]
    print()
    if not all(results):
        print("ABORTED — gate failed, nothing written for the failing source(s).")
        raise SystemExit(1)
    print("All gates PASS." + ("" if apply else "  Re-run with --apply to write."))
