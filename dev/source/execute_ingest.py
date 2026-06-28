#!/usr/bin/env python3
"""
execute_ingest.py  —  Option A, Phase 2 (S189)
==============================================
The ingest EXECUTOR for the automated-ingest pipeline — DRY-RUN ONLY in Phase 2.

Where prepare_ingest_package.py (Phase 1) turns an EDB circular candidate into a
reviewable "ingest package", this script takes an APPROVED package and produces a
complete, auditable EXECUTION PLAN: exactly what the live executor (Phase 3) will
do to ingest the source end-to-end. In Phase 2 it SIMULATES every live step and
writes nothing live — so the whole automated path can be inspected and trusted
before any token, secret, or scheduled job exists.

The 6 live steps it plans / (later) performs, mirroring the manual S186 pipeline:

  1. copy-to-vault   extract_<id>.txt  ->  dev/vault/<id>/extract_<id>.txt
  2. registry-append construct + append the source_registry.json entry
  3. ingest          chunk + embed + INSERT (dev/ingest_one_source.py <id>)
  4. route-patch     add "<id>" to SOURCE_SETS[<route>] in searchChannelB.ts
  5. display-sync    bump _meta.stats.chunks across the display-sync touch points
  6. commit          git commit + push (-> Render redeploy + Pages redeploy)

SAFETY / SCOPE (Phase 2 is intentionally inert):
  - DRY-RUN ONLY. With --dry-run (the default and ONLY wired mode) it writes a
    single execution_plan.json into the package dir (staging, gitignored) and a
    console report. It NEVER touches dev/vault/, Supabase, git, the registry, the
    backend route table, or any display-sync file.
  - LIVE mode is Phase 3. Invoking without --dry-run hard-refuses with guidance,
    so this script can never perform a real ingest by accident.
  - The approval gate: an ingest is "executable" only when its approval record
    (ops/approvals/<id>.approval.json) has decision == "approved". In dry-run we
    still plan un-approved packages, but the plan flags WOULD-BLOCK so the gate is
    visible. Human overrides (tier/route/topic) in the approval record are applied
    over the package's auto-proposals.

Usage (from repo root):
  python3 dev/source/execute_ingest.py --package edbc007_2026 --dry-run
  python3 dev/source/execute_ingest.py --all-prepared --dry-run     # every non-dupe staged pkg
  python3 dev/source/execute_ingest.py --package edbc007_2026 --init-approval   # write pending record
  python3 dev/source/execute_ingest.py --package edbc007_2026       # LIVE -> hard refusal (Phase 3)
"""
import argparse
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]                    # …/Draft
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw                                      # canonical chunker (parity with ingest_one_source)

STAGING_DIR = REPO_ROOT / "dev" / "source" / "ingest_packages"
OPS_DIR = REPO_ROOT / "dev" / "source" / "ops"
APPROVALS_DIR = OPS_DIR / "approvals"
REGISTRY_PATH = REPO_ROOT / "dev" / "source" / "source_registry.json"
KNOWLEDGE_PATH = REPO_ROOT / "knowledge.json"
ROUTE_FILE = REPO_ROOT / "backend" / "src" / "api" / "searchChannelB.ts"

# display-sync touch points: where _meta.stats.chunks is mirrored. The executor's
# live step rewrites the count in each; dry-run lists them with before -> after.
# fmt = "raw" (15838) or "comma" (15,838).
DISPLAY_SYNC_TARGETS = [
    ("knowledge.json", "raw"),
    ("role_facts.json", "raw"),
    ("dev/knowledge/role_facts.json", "raw"),
    ("K1_API_SPEC.md", "raw"),
    ("app.html", "raw"),
    ("index.html", "comma"),
    ("README.md", "comma"),
    ("dev/CODEBASE_CONTEXT.md", "comma"),
    ("CHANGELOG.md", "comma"),
]


# ── package + approval IO ────────────────────────────────────────────────────
def load_package(source_id: str) -> Dict:
    p = STAGING_DIR / source_id / "package.json"
    if not p.exists():
        sys.exit(f"ERROR: no prepared package for '{source_id}' ({p.relative_to(REPO_ROOT)}). "
                 f"Run prepare_ingest_package.py first.")
    return json.loads(p.read_text(encoding="utf-8"))


def approval_path(source_id: str) -> Path:
    return APPROVALS_DIR / f"{source_id}.approval.json"


def init_approval(pkg: Dict) -> Dict:
    """Create a pending approval record from a prepared package (idempotent)."""
    sid = pkg["source_id"]
    path = approval_path(sid)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    rec = {
        "source_id": sid,
        "package_ref": f"dev/source/ingest_packages/{sid}/package.json",
        "title": pkg.get("title"),
        "decision": "pending",                       # pending | approved | rejected
        "decided_by": None,
        "decided_at": None,
        "proposed": pkg.get("proposed", {}),         # echo of auto-proposals (for the approver)
        "overrides": {"topic": None, "route": None, "tier": None},  # human corrections; null = accept proposal
        "notes": "",
    }
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


def load_approval(source_id: str) -> Optional[Dict]:
    path = approval_path(source_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def effective(pkg: Dict, approval: Optional[Dict]) -> Dict:
    """Auto-proposal with human overrides applied."""
    prop = dict(pkg.get("proposed", {}))
    eff = {"topic": prop.get("topic"), "route": prop.get("route"), "tier": prop.get("tier")}
    src = "auto-proposal"
    if approval:
        ov = approval.get("overrides", {}) or {}
        for k in ("topic", "route", "tier"):
            if ov.get(k) is not None:
                eff[k] = ov[k]
                src = "approval-override"
    eff["source"] = src
    return eff


# ── per-step planners (all read-only) ────────────────────────────────────────
def plan_copy_to_vault(pkg: Dict) -> Dict:
    sid = pkg["source_id"]
    src = REPO_ROOT / pkg["extract"] if pkg.get("extract") else STAGING_DIR / sid / f"extract_{sid}.txt"
    dest = REPO_ROOT / "dev" / "vault" / sid / f"extract_{sid}.txt"
    bytes_ = src.stat().st_size if src.exists() else None
    return {
        "src": str(src.relative_to(REPO_ROOT)) if src.exists() else pkg.get("extract"),
        "dest": str(dest.relative_to(REPO_ROOT)),
        "bytes": bytes_,
        "src_exists": src.exists(),
        "dest_exists": dest.exists(),
    }


def plan_registry_entry(pkg: Dict, eff: Dict) -> Dict:
    sid = pkg["source_id"]
    url = pkg.get("pdf_url", "")
    year = (pkg.get("circular_number") or "").split("/")[-1] or None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "source_id": sid,
        "title": pkg.get("title"),
        "title_en": None,
        "title_short": (pkg.get("title") or "")[:24],
        "url_landing": url,
        "url_primary": url,
        "source_type": "pdf",
        "authority": "edb",
        "spine": False,
        "topic_tags": [eff["topic"]],
        "access_mode": "public",
        "status": "verified",
        "version_label": year,
        "last_checked_at": today,
        "supersedes": None,
        "related_source_ids": [],
        "notes": f"(auto, Option A executor) {pkg.get('circular_number')}. route={eff['route']}, "
                 f"Tier {eff['tier']}. watcher→prepare→approve→execute. Channel B vault_extract.",
    }


def plan_chunks(pkg: Dict) -> Dict:
    """Re-chunk the staged extract with the canonical chunker (no embed/insert).
    Identical chunk math to ingest_one_source.py / build_wiki_index."""
    sid = pkg["source_id"]
    extract = REPO_ROOT / pkg["extract"] if pkg.get("extract") else STAGING_DIR / sid / f"extract_{sid}.txt"
    if not extract.exists():
        return {"error": f"extract missing: {extract}"}
    text = extract.read_text(encoding="utf-8").replace("\x00", "")
    seen, ids, lens = set(), [], []
    for ch in bw.chunk_text_with_page_carry(text):
        h = bw.text_hash(ch)
        cid = f"vault_{sid}_{h}"
        if cid in seen:
            continue
        seen.add(cid)
        ids.append(cid)
        lens.append(len(ch))
    lens = lens or [0]
    page_ok = all("=== Page" in ch for ch in bw.chunk_text_with_page_carry(text)) if ids else False
    return {
        "chunks": len(ids),
        "char_min": min(lens), "char_med": int(statistics.median(lens)), "char_max": max(lens),
        "page_resolvable": page_ok,
        "sample_ids": ids[:3],
    }


def plan_route_patch(route: str, source_id: str) -> Dict:
    """Locate SOURCE_SETS[<route>] in searchChannelB.ts and preview the insertion."""
    if not ROUTE_FILE.exists():
        return {"error": f"route file missing: {ROUTE_FILE}"}
    lines = ROUTE_FILE.read_text(encoding="utf-8").splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"\s*{re.escape(route)}:\s*\[", ln):
            start = i
            break
    if start is None:
        return {"route": route, "found": False,
                "note": f"route '{route}' not yet a SOURCE_SET — live executor would CREATE the block "
                        f"(needs human review: a new route also needs TOPIC_KEYWORDS + smoke test)."}
    # find array close
    end = start
    for j in range(start, min(start + 60, len(lines))):
        if "]" in lines[j] and j > start:
            end = j
            break
    already = any(f'"{source_id}"' in lines[k] for k in range(start, end + 1))
    insert_line = f'    "{source_id}",              // (auto) Option A watcher ingest'
    return {
        "route": route, "found": True, "already_present": already,
        "file": str(ROUTE_FILE.relative_to(REPO_ROOT)),
        "block_lines": f"{start + 1}-{end + 1}",
        "insert_at_line": end + 1,
        "insert_text": insert_line,
        "preview": lines[start:start + 1] + ["    …"] + [insert_line, lines[end]],
    }


def current_chunk_total() -> Optional[int]:
    try:
        k = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
        return int(k.get("_meta", {}).get("stats", {}).get("chunks"))
    except Exception:
        return None


def plan_display_sync(new_chunks: int) -> Dict:
    before = current_chunk_total()
    after = (before + new_chunks) if before is not None else None
    targets = []
    for rel, fmt in DISPLAY_SYNC_TARGETS:
        p = REPO_ROOT / rel
        b_str = (f"{before:,}" if fmt == "comma" else str(before)) if before is not None else "?"
        a_str = (f"{after:,}" if fmt == "comma" else str(after)) if after is not None else "?"
        hits = 0
        if p.exists() and before is not None:
            hits = p.read_text(encoding="utf-8", errors="ignore").count(b_str)
        targets.append({"file": rel, "fmt": fmt, "sub": f"{b_str} -> {a_str}", "occurrences": hits,
                        "exists": p.exists()})
    return {"before": before, "after": after, "delta": new_chunks, "targets": targets}


def plan_commit_message(pkg: Dict, eff: Dict, chunks: int, after: Optional[int]) -> str:
    sid = pkg["source_id"]
    total = f" -> {after:,}" if after is not None else ""
    return (f"feat(ingest): {sid} {pkg.get('circular_number')} +{chunks} chunks{total} "
            f"[Option A auto, route={eff['route']}, topic={eff['topic']}, T{eff['tier']}]")


# ── orchestration ────────────────────────────────────────────────────────────
def build_plan(source_id: str) -> Dict:
    pkg = load_package(source_id)
    approval = load_approval(source_id)
    eff = effective(pkg, approval)

    blockers: List[str] = []
    if pkg.get("in_registry_already"):
        blockers.append("package flagged in_registry_already (duplicate)")
    if pkg.get("needs_ocr"):
        blockers.append("package flagged needs_ocr (held for manual extraction)")
    if not pkg.get("extract"):
        blockers.append("package has no extract file (was it run with --dry?)")
    decision = (approval or {}).get("decision", "no-approval-record")
    if decision != "approved":
        blockers.append(f"approval gate: decision='{decision}' (live execution requires 'approved')")

    chunks = plan_chunks(pkg)
    ds = plan_display_sync(chunks.get("chunks", 0))
    plan = {
        "source_id": source_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "phase": "2 (dry-run only)",
        "approval_decision": decision,
        "effective": eff,
        "would_block_in_live": blockers,
        "executable": not blockers,
        "steps": {
            "1_copy_to_vault": plan_copy_to_vault(pkg),
            "2_registry_append": plan_registry_entry(pkg, eff),
            "3_ingest_chunks": chunks,
            "4_route_patch": plan_route_patch(eff["route"], source_id),
            "5_display_sync": ds,
            "6_commit": plan_commit_message(pkg, eff, chunks.get("chunks", 0), ds.get("after")),
        },
    }
    return plan


def print_plan(plan: Dict) -> None:
    sid = plan["source_id"]
    eff = plan["effective"]
    s = plan["steps"]
    print("=" * 72)
    print(f"EXECUTION PLAN (DRY-RUN)  {sid}   approval={plan['approval_decision']}")
    print(f"  effective: route={eff['route']}  topic={eff['topic']}  Tier={eff['tier']}  ({eff['source']})")
    print("=" * 72)

    cp = s["1_copy_to_vault"]
    print(f"[1] copy-to-vault   {cp['src']}")
    print(f"                  → {cp['dest']}   ({cp['bytes']} bytes, dest_exists={cp['dest_exists']})")

    print(f"[2] registry-append  +1 entry to dev/source/source_registry.json")
    print(f"                     topic_tags={s['2_registry_append']['topic_tags']}  "
          f"version_label={s['2_registry_append']['version_label']}")

    ch = s["3_ingest_chunks"]
    print(f"[3] ingest          {ch.get('chunks')} chunks  "
          f"char(min/med/max)={ch.get('char_min')}/{ch.get('char_med')}/{ch.get('char_max')}  "
          f"page_resolvable={ch.get('page_resolvable')}")
    if ch.get("sample_ids"):
        print(f"                    sample id: {ch['sample_ids'][0]}")

    rp = s["4_route_patch"]
    if rp.get("found"):
        flag = "already present ✓ (no-op)" if rp.get("already_present") else f"insert @ line {rp['insert_at_line']}"
        print(f"[4] route-patch     SOURCE_SETS.{rp['route']}  (block {rp['block_lines']})  {flag}")
        if not rp.get("already_present"):
            print(f"                    + {rp['insert_text'].strip()}")
    else:
        print(f"[4] route-patch     ⚠ {rp.get('note', rp.get('error'))}")

    ds = s["5_display_sync"]
    print(f"[5] display-sync    chunks {ds['before']} → {ds['after']}  (+{ds['delta']})  "
          f"across {len(ds['targets'])} files")
    for t in ds["targets"]:
        mark = "" if t["exists"] else " (missing!)"
        print(f"                    {t['file']:32} {t['sub']:>20}  ×{t['occurrences']}{mark}")

    print(f"[6] commit          {s['6_commit']}")

    print("-" * 72)
    if plan["executable"]:
        print("GATE: ✅ all preconditions met — live executor (Phase 3) WOULD proceed.")
    else:
        print("GATE: ⛔ WOULD BLOCK in live mode:")
        for b in plan["would_block_in_live"]:
            print(f"        - {b}")
    print("(Phase 2 dry-run: nothing above was performed. No live writes.)")


def refuse_live() -> int:
    print(
        "⛔ LIVE EXECUTION IS PHASE 3 — NOT WIRED.\n"
        "   This executor only produces dry-run plans (--dry-run). A real ingest needs\n"
        "   cross-repo tokens + Supabase service key + git push, which Phase 3 adds.\n\n"
        "   To ingest a source for real TODAY, use the existing manual path (same as S186):\n"
        "     1. cp dev/source/ingest_packages/<id>/extract_<id>.txt  dev/vault/<id>/\n"
        "     2. add the source_registry.json entry\n"
        "     3. SUPABASE_SERVICE_KEY=… python3 dev/ingest_one_source.py <id>\n"
        "     4. patch SOURCE_SETS[<route>] in backend/src/api/searchChannelB.ts\n"
        "     5. display-sync the chunk count + commit + push\n",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run executor for the Option A automated-ingest pipeline (Phase 2).")
    ap.add_argument("--package", help="staged source_id under dev/source/ingest_packages/")
    ap.add_argument("--all-prepared", action="store_true", help="plan every staged package whose status=='prepared'")
    ap.add_argument("--init-approval", action="store_true", help="write a pending approval record for --package and exit")
    ap.add_argument("--dry-run", action="store_true", help="produce the execution plan without any live writes (Phase 2 default)")
    args = ap.parse_args()

    # select packages
    if args.all_prepared:
        ids = sorted(p.parent.name for p in STAGING_DIR.glob("*/package.json")
                     if json.loads(p.read_text(encoding="utf-8")).get("status") == "prepared")
        if not ids:
            print("No staged packages with status=='prepared'.")
            return 0
    elif args.package:
        ids = [args.package]
    else:
        ap.error("specify --package <id> or --all-prepared")
        return 2

    if args.init_approval:
        for sid in ids:
            rec = init_approval(load_package(sid))
            print(f"approval record: {approval_path(sid).relative_to(REPO_ROOT)}  decision={rec['decision']}")
        return 0

    if not args.dry_run:
        return refuse_live()

    for sid in ids:
        plan = build_plan(sid)
        out = STAGING_DIR / sid / "execution_plan.json"
        out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print_plan(plan)
        print(f"plan written: {out.relative_to(REPO_ROOT)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
