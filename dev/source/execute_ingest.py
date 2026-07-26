#!/usr/bin/env python3
"""
execute_ingest.py  —  Option A, Phase 2 (S189) + Phase 3 live wiring (S190)
==========================================================================
The ingest EXECUTOR for the automated-ingest pipeline. --dry-run produces an
auditable plan (Phase 2); --live performs the 6 steps for real (Phase 3).

Where prepare_ingest_package.py (Phase 1) turns an EDB circular candidate into a
reviewable "ingest package", this script takes an APPROVED package and produces a
complete, auditable EXECUTION PLAN: exactly what the live executor (Phase 3) will
do to ingest the source end-to-end. In Phase 2 it SIMULATES every live step and
writes nothing live — so the whole automated path can be inspected and trusted
before any token, secret, or scheduled job exists.

The live steps it plans / (later) performs, mirroring the manual S186 pipeline:

  1. copy-to-vault   extract_<id>.txt  ->  dev/vault/<id>/extract_<id>.txt
  2. registry-append construct + append the source_registry.json entry
  3. ingest          chunk + embed + INSERT (dev/ingest_one_source.py <id>)
  4. route-patch     add "<id>" to SOURCE_SETS[<route>] in searchChannelB.ts
  4b. spotlight      register "<id>" in SPOTLIGHT_SOURCE_IDS (route-independent exact-cosine
                     pass) so a small new source is retrievable at all — see S193
  5. display-sync    bump _meta.stats.chunks across the display-sync touch points
  6. commit          git commit + push (-> Render redeploy + Pages redeploy)

SAFETY / SCOPE:
  - --dry-run writes only execution_plan.json (staging, gitignored) + a console
    report; it touches nothing live.
  - --live performs those steps for real, but is gated three ways:
      (a) APPROVAL — runs only when ops/approvals/<id>.approval.json has
          decision == "approved" (human overrides tier/route/topic apply over the
          package's auto-proposals);
      (b) SECRETS — refuses (exit 3) unless OPENAI_API_KEY + SUPABASE_SERVICE_KEY
          are present, so a run without secrets is inert (the scheduled ops
          workflow injects them from GitHub Secrets);
      (c) IDEMPOTENT + RESUMABLE — every step is safe to repeat and progress is
          journalled to execution_state.json; a failed run leaves the candidate
          approved and re-runs skip completed steps.
  - Bare invocation (neither --dry-run nor --live) errors; --live is explicit.

Usage (from repo root):
  python3 dev/source/execute_ingest.py --package edbc007_2026 --dry-run
  python3 dev/source/execute_ingest.py --all-prepared --dry-run     # every non-dupe staged pkg
  python3 dev/source/execute_ingest.py --package edbc007_2026 --init-approval   # write pending record
  SUPABASE_SERVICE_KEY=… OPENAI_API_KEY=… \
    python3 dev/source/execute_ingest.py --package edbc007_2026 --live          # Phase 3 real ingest
"""
import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
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
UPDATE_LOG_PATH = REPO_ROOT / "update_log.json"
ROUTE_FILE = REPO_ROOT / "backend" / "src" / "api" / "searchChannelB.ts"
VAULT_DIR = REPO_ROOT / "dev" / "vault"
INGEST_SCRIPT = REPO_ROOT / "dev" / "ingest_one_source.py"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
WIKI_TABLE = "wiki_chunks"
RENDER_HEALTH = "https://edb-knowledge.onrender.com/health"
CHANNEL_B_API = "https://edb-knowledge.onrender.com/api/search/channel-b"
# git files the live committer stages (display-sync targets added dynamically).
LIVE_COMMIT_PATHS = [
    "dev/source/source_registry.json",
    "backend/src/api/searchChannelB.ts",
]

# display-sync touch points: where _meta.stats.chunks is mirrored as CURRENT state.
# The executor's live step rewrites the count in each; dry-run lists them with
# before -> after. fmt = "raw" (15838) or "comma" (15,838).
#
# S194 — `CHANGELOG.md` and `dev/CODEBASE_CONTEXT.md` were REMOVED from this list.
# Both are append-only histories, not mirrors of current state, and a blind
# whole-file replace silently rewrote past entries every single ingest: by S194
# the S186 changelog entry read "15,656 → 15,901 (淨 +182)" — arithmetically
# impossible — and five AI-maintenance-log entries claimed totals that postdated
# the sessions they describe. Corrected in S194; the fix is to stop touching them
# here. An ingest should APPEND a new entry to each (which is what they are for),
# never restate history. Anything added to this list must hold only the current
# total; if a file also carries history, it does not belong here.
DISPLAY_SYNC_TARGETS = [
    ("knowledge.json", "raw"),
    ("role_facts.json", "raw"),
    ("dev/knowledge/role_facts.json", "raw"),
    ("K1_API_SPEC.md", "raw"),
    ("app.html", "raw"),
    ("index.html", "comma"),
    ("README.md", "comma"),
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
        "circular_number": pkg.get("circular_number"),   # so the executor can regenerate the package from the feed
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
    text = re.sub(r"^(# .+\n)+", "", text, flags=re.MULTILINE).strip()   # strip header — match load_vault_sources (ingest path)
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


SPOTLIGHT_START = "// ack:spotlight:start"
SPOTLIGHT_END = "// ack:spotlight:end"


def plan_spotlight_patch(source_id: str) -> Dict:
    """Preview registering the new source in SPOTLIGHT_SOURCE_IDS (searchChannelB.ts).

    Why this step exists (S193): step 4 only adds the id to a SOURCE_SET, which narrows an
    already-retrieved candidate list. The main search asks Supabase for the GLOBAL top-(top_k*5)
    chunks and filters by source set afterwards, so a source with a handful of chunks never
    enters the window and stays unreachable no matter how it is routed. Registering it in the
    spotlight list gives it a route-independent exact-cosine pass until it can compete on its
    own. Found by probing the 4 sources this pipeline ingested unattended after S192: 2 of them
    could not be retrieved even by their own title.
    """
    if not ROUTE_FILE.exists():
        return {"error": f"route file missing: {ROUTE_FILE}"}
    lines = ROUTE_FILE.read_text(encoding="utf-8").splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        if SPOTLIGHT_START in ln:
            start = i
        elif SPOTLIGHT_END in ln:
            end = i
            break
    if start is None or end is None:
        return {"found": False,
                "note": f"spotlight markers not found in {ROUTE_FILE.name} — new sources will "
                        f"stay ANN-unreachable until registered by hand (see S193)."}
    already = any(f'"{source_id}"' in lines[k] for k in range(start, end + 1))
    insert_line = f'  "{source_id}", // (auto) Option A watcher ingest — prune once it surfaces via ANN'
    return {
        "found": True, "already_present": already,
        "file": str(ROUTE_FILE.relative_to(REPO_ROOT)),
        "block_lines": f"{start + 1}-{end + 1}",
        "insert_at_line": end + 1,
        "insert_text": insert_line,
        "listed": sum(1 for k in range(start + 1, end) if lines[k].strip().startswith('"')),
    }


def live_spotlight_patch(source_id: str) -> Dict:
    sp = plan_spotlight_patch(source_id)
    if sp.get("error"):
        raise RuntimeError(sp["error"])
    if not sp.get("found"):
        # Non-fatal: the ingest itself is fine, but say so loudly — this is the difference
        # between "searchable" and "silently invisible".
        _annotate("warning", f"{source_id}: spotlight markers missing in searchChannelB.ts — "
                             f"source may be unreachable by search until registered manually")
        return {"patched": False, "reason": "markers missing"}
    if sp.get("already_present"):
        return {"patched": False, "reason": "already present"}
    lines = ROUTE_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    lines.insert(sp["insert_at_line"] - 1, sp["insert_text"] + "\n")
    ROUTE_FILE.write_text("".join(lines), encoding="utf-8")
    return {"patched": True, "listed_after": sp["listed"] + 1}


def _annotate(level: str, message: str) -> None:
    """Emit a GitHub Actions annotation when running in CI, plus a plain console line.
    Keeps the signal visible in the ops workflow without needing an ops-repo change."""
    one_line = message.replace("\n", " ")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level}::{one_line}")
    print(f"  {'⚠' if level == 'warning' else 'ℹ'} {one_line}")


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
            "4b_spotlight_patch": plan_spotlight_patch(source_id),
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

    sp = s["4b_spotlight_patch"]
    if sp.get("found"):
        flag = "already listed ✓ (no-op)" if sp.get("already_present") else f"insert @ line {sp['insert_at_line']}"
        print(f"[4b] spotlight      SPOTLIGHT_SOURCE_IDS (block {sp['block_lines']}, {sp['listed']} listed)  {flag}")
    else:
        print(f"[4b] spotlight      ⚠ {sp.get('note', sp.get('error'))}")

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


# ── LIVE EXECUTION (Phase 3, S190) ───────────────────────────────────────────
# Wires the 6 steps for real. Guarded by: (a) the approval gate, (b) a secrets
# pre-flight (no OPENAI/SUPABASE key → refuse, so a no-secret run is still inert),
# (c) per-step idempotency + a resumable execution_state.json so a failed run is
# safely re-runnable (the candidate stays "approved" and re-opens). Every step is
# safe to repeat: copy overwrites, registry/route skip-if-present, ingest upserts
# by PK (merge-duplicates), display-sync is state-gated, commit/push is a no-op if
# nothing changed.

def _read_secret(key: str) -> str:
    """Read a secret from the environment, falling back to backend/.env."""
    v = os.environ.get(key, "")
    if not v and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key}=") and not line.startswith("#"):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return v


def secrets_status() -> Dict[str, bool]:
    return {"OPENAI_API_KEY": bool(_read_secret("OPENAI_API_KEY")),
            "SUPABASE_SERVICE_KEY": bool(_read_secret("SUPABASE_SERVICE_KEY"))}


def live_source_count(source_id: str) -> Optional[int]:
    """Authoritative chunk count for one source in Supabase (post-ingest delta for a
    new source). Used for display-sync so the count can't drift from the real insert."""
    import requests
    svc = _read_secret("SUPABASE_SERVICE_KEY")
    if not svc:
        return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{WIKI_TABLE}?select=id&source_id=eq.{source_id}",
                         headers={"apikey": svc, "Authorization": f"Bearer {svc}",
                                  "Range-Unit": "items", "Range": "0-0", "Prefer": "count=exact"},
                         timeout=40)
        cr = r.headers.get("content-range", "")          # e.g. "0-0/6" or "*/0"
        return int(cr.split("/")[-1]) if "/" in cr else None
    except Exception:
        return None


def _ingest_env() -> Dict[str, str]:
    """os.environ + backend/.env secrets so the ingest subprocess sees the keys."""
    env = dict(os.environ)
    for key in ("OPENAI_API_KEY", "SUPABASE_SERVICE_KEY"):
        if not env.get(key):
            val = _read_secret(key)
            if val:
                env[key] = val
    env.setdefault("SUPABASE_URL", SUPABASE_URL)
    return env


# ── resumable execution state ────────────────────────────────────────────────
def state_path(source_id: str) -> Path:
    return STAGING_DIR / source_id / "execution_state.json"


def load_state(source_id: str) -> Dict:
    p = state_path(source_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"source_id": source_id, "steps": {}, "started_at": None,
            "before_total": None, "after_total": None, "chunks": None}


def save_state(st: Dict) -> None:
    state_path(st["source_id"]).write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def _done(st: Dict, name: str) -> bool:
    return st["steps"].get(name, {}).get("status") == "done"


def _mark(st: Dict, name: str, **info) -> None:
    st["steps"][name] = {"status": "done",
                         "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **info}
    save_state(st)


def record_execution(source_id: str, status: str, **info) -> None:
    """Annotate the approval record with the run outcome (re-open path on failure)."""
    appr = load_approval(source_id)
    if not appr:
        return
    appr["execution"] = {"status": status,
                         "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **info}
    approval_path(source_id).write_text(json.dumps(appr, ensure_ascii=False, indent=2), encoding="utf-8")


# ── live steps (each idempotent) ─────────────────────────────────────────────
def live_copy_to_vault(pkg: Dict, eff: Dict) -> Dict:
    sid = pkg["source_id"]
    src = REPO_ROOT / pkg["extract"] if pkg.get("extract") else STAGING_DIR / sid / f"extract_{sid}.txt"
    if not src.exists():
        raise RuntimeError(f"extract missing: {src}")
    text = src.read_text(encoding="utf-8")
    topic = eff.get("topic") or "general"
    # rewrite the header topic_tags to the effective (post-override) topic; the
    # vault header is the metadata source ingest_one_source reads (build_wiki_index).
    if re.search(r"^# topic_tags:.*$", text, flags=re.MULTILINE):
        text = re.sub(r"^# topic_tags:.*$", f"# topic_tags: {topic}", text, count=1, flags=re.MULTILINE)
    dest = VAULT_DIR / sid / f"extract_{sid}.txt"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    warn = None if topic in bw.VALID_TOPICS else \
        f"topic '{topic}' not in VALID_TOPICS — ingest will fall back to 'curriculum'"
    return {"dest": str(dest.relative_to(REPO_ROOT)), "bytes": dest.stat().st_size,
            "topic_written": topic, "warn": warn}


def live_registry_append(pkg: Dict, eff: Dict) -> Dict:
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = reg.get("sources", [])
    sid = pkg["source_id"]
    if any(s.get("source_id") == sid for s in sources):
        return {"appended": False, "reason": "already in registry", "count": len(sources)}
    e = plan_registry_entry(pkg, eff)
    entry = {
        "source_id": e["source_id"], "title": e["title"], "title_en": None,
        "title_short": e["title_short"], "url_landing": e["url_landing"],
        "url_primary": e["url_primary"], "source_type": "pdf", "authority": "edb",
        "spine": False, "topic_tags": e["topic_tags"], "access_mode": "public",
        "status": "verified", "version_label": e["version_label"],
        "last_checked_at": e["last_checked_at"], "supersedes": None, "notes": e["notes"],
    }
    sources.append(entry)
    reg["sources"] = sources
    if isinstance(reg.get("_meta"), dict):
        reg["_meta"]["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    REGISTRY_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"appended": True, "count": len(sources)}


def live_ingest(sid: str) -> Dict:
    """Run dev/ingest_one_source.py <sid> (chunk + embed + INSERT). Idempotent
    (upsert by PK via merge-duplicates). Raises on non-zero exit."""
    if not INGEST_SCRIPT.exists():
        raise RuntimeError(f"ingest script missing: {INGEST_SCRIPT}")
    proc = subprocess.run([sys.executable, str(INGEST_SCRIPT), sid],
                          cwd=str(REPO_ROOT), env=_ingest_env(),
                          capture_output=True, text=True, timeout=600)
    tail = (proc.stdout or "")[-800:] + (("\n[stderr] " + proc.stderr[-400:]) if proc.stderr else "")
    if proc.returncode != 0:
        raise RuntimeError(f"ingest_one_source.py exit {proc.returncode}:\n{tail}")
    return {"returncode": 0, "stdout_tail": tail.strip()}


def live_route_patch(route: str, sid: str) -> Dict:
    rp = plan_route_patch(route, sid)
    if rp.get("error"):
        raise RuntimeError(rp["error"])
    if not rp.get("found"):
        raise RuntimeError(f"route '{route}' is not an existing SOURCE_SET. A new route also "
                           f"needs TOPIC_KEYWORDS + a smoke test — refusing to auto-create. "
                           f"Add the route manually, then re-run.")
    if rp.get("already_present"):
        return {"patched": False, "reason": "already present", "route": route}
    lines = ROUTE_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    insert_idx = rp["insert_at_line"] - 1                       # 1-based → 0-based (the closing-bracket line)
    lines.insert(insert_idx, rp["insert_text"] + "\n")
    ROUTE_FILE.write_text("".join(lines), encoding="utf-8")
    return {"patched": True, "route": route, "block_lines": rp["block_lines"]}


def live_display_sync(before: int, after: int) -> Dict:
    """Rewrite the chunk count before→after across the mirror files. State-gated by
    the caller so it never double-bumps; within a file, replaces every occurrence
    of the exact count string (matching the manual display-sync)."""
    results = []
    for rel, fmt in DISPLAY_SYNC_TARGETS:
        p = REPO_ROOT / rel
        if not p.exists():
            results.append({"file": rel, "exists": False, "replaced": 0})
            continue
        b_str = f"{before:,}" if fmt == "comma" else str(before)
        a_str = f"{after:,}" if fmt == "comma" else str(after)
        text = p.read_text(encoding="utf-8")
        n = text.count(b_str)
        if n:
            p.write_text(text.replace(b_str, a_str), encoding="utf-8")
        results.append({"file": rel, "exists": True, "replaced": n, "sub": f"{b_str}->{a_str}"})
    return {"before": before, "after": after, "targets": results}


def _fmt_circular(num: Optional[str]) -> str:
    """'EDBCM096/2026' -> '教育局通函第96/2026號' ; 'EDBC007/2026' -> '教育局通告第7/2026號'."""
    m = re.match(r"(EDBCM|EDBC)0*(\d+)/(\d{4})", num or "")
    if not m:
        return num or ""
    kind = "通函" if m.group(1) == "EDBCM" else "通告"
    return f"教育局{kind}第{m.group(2)}/{m.group(3)}號"


def live_append_update_log(pkg: Dict) -> Dict:
    """Prepend one concise entry to the public update_log.json (idempotent by title)."""
    if not UPDATE_LOG_PATH.exists():
        return {"appended": False, "reason": "no update_log.json"}
    data = json.loads(UPDATE_LOG_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    title = pkg.get("title") or pkg.get("source_id")
    num = pkg.get("circular_number")
    if num:
        title = f"{title}（{_fmt_circular(num)}）"
    if any(e.get("title") == title for e in entries):
        return {"appended": False, "reason": "already logged", "title": title}
    summary = (pkg.get("summary") or "").replace("\n", " ").strip()
    first = summary.split("。")[0].strip()
    desc = (first[:58] + "…") if len(first) > 60 else (first + "。" if first else title)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries.insert(0, {"date": today, "action": "新增", "title": title, "desc": desc})
    data["entries"] = entries
    UPDATE_LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"appended": True, "title": title}


def live_commit_push(pkg: Dict, eff: Dict, chunks: int, after: Optional[int]) -> Dict:
    sid = pkg["source_id"]
    paths = list(LIVE_COMMIT_PATHS) + ["update_log.json", f"dev/vault/{sid}/"] + [rel for rel, _ in DISPLAY_SYNC_TARGETS]
    existing = [p for p in paths if (REPO_ROOT / p).exists()]
    subprocess.run(["git", "add", "--"] + existing, cwd=str(REPO_ROOT), check=True)
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            cwd=str(REPO_ROOT), capture_output=True, text=True).stdout.strip()
    if not staged:
        return {"committed": False, "reason": "nothing staged (already committed?)"}
    msg = plan_commit_message(pkg, eff, chunks, after)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(REPO_ROOT), check=True)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          cwd=str(REPO_ROOT), capture_output=True, text=True).stdout.strip()
    push = subprocess.run(["git", "push", "origin", "HEAD:main"],
                          cwd=str(REPO_ROOT), capture_output=True, text=True)
    if push.returncode != 0:
        raise RuntimeError(f"git push failed (commit {head} is local):\n{push.stderr[-400:]}")
    return {"committed": True, "commit": head, "files": staged.splitlines()}


def post_deploy_smoke(pkg: Dict) -> Dict:
    """Wait for Render to come back, then check the new source is actually RETRIEVABLE.

    S193 — this used to record a single true/false that nobody read, so a source could be
    ingested, committed, deployed and logged while being unreachable by any query. It now
    probes several phrasings, reports the rank per probe, and raises a GitHub Actions warning
    annotation when the source cannot be surfaced — the pipeline's only "did this actually
    work for a user?" check. Still never fatal: the chunks are already in the store, and a
    cold Render / lagging deploy must not be reported as an ingest failure.
    """
    try:
        import requests
    except Exception as exc:                                    # pragma: no cover
        return {"ran": False, "note": f"requests unavailable: {exc}"}
    sid = pkg["source_id"]
    health_ok = False
    for _ in range(20):                                         # ~20 × 8s ≈ 160s for cold start
        try:
            r = requests.get(RENDER_HEALTH, timeout=15)
            if r.status_code == 200 and r.json().get("ok"):
                health_ok = True
                break
        except Exception:
            pass
        time.sleep(8)
    if not health_ok:
        _annotate("warning", f"{sid}: Render did not report healthy within ~160s — "
                             f"surfaceability unverified (chunks are ingested; re-check the site)")
        return {"ran": True, "health_ok": False, "surfaced": None, "probes": []}

    title = (pkg.get("title") or "").strip()
    # Probe the phrasings a school user would actually type: the document's own title
    # (trimmed of bracket noise), a short head of it, and the circular number.
    plain = re.sub(r"[《》「」（）()]", " ", title).strip()
    probes = [p for p in [plain[:24], plain[:12], _fmt_circular(pkg.get("circular_number"))] if p]
    results = []
    for probe in dict.fromkeys(probes):                         # dedup, preserve order
        try:
            r = requests.post(CHANNEL_B_API, json={"query": probe, "top_k": 8}, timeout=45)
            rows = r.json().get("results", [])
            rank = next((i for i, row in enumerate(rows) if row.get("source_id") == sid), None)
            results.append({"query": probe, "rank": rank,
                            "top": [row.get("source_id") for row in rows[:3]]})
        except Exception as exc:
            results.append({"query": probe, "error": str(exc)[:80]})
        time.sleep(1)
    surfaced = any(p.get("rank") is not None for p in results)
    for p in results:
        if "error" in p:
            print(f"  [smoke] «{p['query']}» → error: {p['error']}")
        else:
            state = f"rank {p['rank']}" if p["rank"] is not None else "ABSENT"
            print(f"  [smoke] «{p['query']}» → {state}  (top: {', '.join(p['top'])})")
    if not surfaced:
        _annotate("warning",
                  f"{sid}: ingested and deployed, but NOT retrievable by any probe "
                  f"({', '.join(repr(p['query']) for p in results)}). The chunks are in the store; "
                  f"search cannot reach them. Likely causes: the source needs a routing keyword, "
                  f"or its chunks score below the spotlight lead bar. Needs a human look.")
    return {"ran": True, "health_ok": True, "surfaced": surfaced, "probes": results}


# ── live orchestrator ────────────────────────────────────────────────────────
def exec_live(source_id: str) -> int:
    pkg = load_package(source_id)
    approval = load_approval(source_id)
    eff = effective(pkg, approval)

    # (a) approval + sanity gate — same blockers the dry-run plan flags
    blockers: List[str] = []
    if pkg.get("in_registry_already"):
        blockers.append("package flagged in_registry_already (duplicate)")
    if pkg.get("needs_ocr"):
        blockers.append("package flagged needs_ocr (held for manual extraction)")
    if not pkg.get("extract"):
        blockers.append("package has no extract file")
    decision = (approval or {}).get("decision", "no-approval-record")
    if decision != "approved":
        blockers.append(f"approval gate: decision='{decision}' (live execution requires 'approved')")
    if blockers:
        print(f"⛔ {source_id}: refusing live execution —")
        for b in blockers:
            print(f"     - {b}")
        return 1

    # (b) secrets pre-flight — a no-secret run stays inert (the Phase 3 safety net)
    sec = secrets_status()
    missing = [k for k, ok in sec.items() if not ok]
    if missing:
        print(f"⛔ {source_id}: live execution needs secrets that are not set: {', '.join(missing)}.\n"
              f"   Set them in the environment or backend/.env (the ops workflow injects them\n"
              f"   from GitHub Secrets). Nothing was written.", file=sys.stderr)
        return 3

    st = load_state(source_id)
    st["started_at"] = st.get("started_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_state(st)
    print(f"▶ LIVE execute {source_id}  route={eff['route']} topic={eff['topic']} T{eff['tier']} ({eff['source']})")

    try:
        # 1 copy-to-vault
        if not _done(st, "1_copy"):
            r = live_copy_to_vault(pkg, eff)
            if r.get("warn"):
                print(f"  ⚠ {r['warn']}")
            _mark(st, "1_copy", **r)
            print(f"  [1] vault ← {r['dest']} ({r['bytes']}B, topic={r['topic_written']})")
        # 2 registry-append
        if not _done(st, "2_registry"):
            r = live_registry_append(pkg, eff)
            _mark(st, "2_registry", **r)
            print(f"  [2] registry {'appended' if r['appended'] else r.get('reason')} (count={r['count']})")
        # 3 ingest — capture before-total ONCE (current display count) before ingesting
        if st.get("before_total") is None:
            st["before_total"] = current_chunk_total()
            save_state(st)
        if not _done(st, "3_ingest"):
            r = live_ingest(source_id)
            # authoritative delta = this source's live Supabase row count (immune to
            # chunk-estimate drift; S190 off-by-one fix). Fall back to the estimate only
            # if the count query fails.
            actual = live_source_count(source_id)
            if actual is None:
                actual = plan_chunks(pkg).get("chunks", 0)
            st["chunks"] = actual
            st["after_total"] = (st["before_total"] + actual) if st["before_total"] is not None else None
            _mark(st, "3_ingest", chunks=actual, **r)
            save_state(st)
            print(f"  [3] ingest OK (+{actual} chunks)")
        # 4 route-patch
        if not _done(st, "4_route"):
            r = live_route_patch(eff["route"], source_id)
            _mark(st, "4_route", **r)
            print(f"  [4] route {eff['route']}: {'patched' if r['patched'] else r.get('reason')}")
        # 4b spotlight registration — makes the new source reachable at all (S193)
        if not _done(st, "4b_spotlight"):
            r = live_spotlight_patch(source_id)
            _mark(st, "4b_spotlight", **r)
            print(f"  [4b] spotlight: {'registered' if r['patched'] else r.get('reason')}")
        # 5 display-sync
        if not _done(st, "5_display_sync"):
            if st["before_total"] is None or st["after_total"] is None:
                raise RuntimeError("chunk total unknown — cannot display-sync safely")
            r = live_display_sync(st["before_total"], st["after_total"])
            _mark(st, "5_display_sync", **r)
            hit = sum(t["replaced"] for t in r["targets"])
            print(f"  [5] display-sync {st['before_total']}→{st['after_total']} ({hit} replacements)")
        # 5b update-log (concise public entry, idempotent by title)
        if not _done(st, "5b_update_log"):
            r = live_append_update_log(pkg)
            _mark(st, "5b_update_log", **r)
            print(f"  [5b] update-log: {'appended' if r.get('appended') else r.get('reason')}")
        # 6 commit + push
        if not _done(st, "6_commit"):
            r = live_commit_push(pkg, eff, st["chunks"] or 0, st["after_total"])
            _mark(st, "6_commit", **r)
            print(f"  [6] commit {'pushed ' + r.get('commit', '') if r['committed'] else r.get('reason')}")
    except Exception as exc:
        last = next((k for k in ("1_copy", "2_registry", "3_ingest", "4_route", "5_display_sync", "6_commit")
                     if not _done(st, k)), "?")
        st["steps"][last] = {"status": "failed", "error": str(exc)[:600],
                             "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        save_state(st)
        record_execution(source_id, "failed", failed_step=last, error=str(exc)[:600])
        print(f"\n✖ {source_id} FAILED at step {last}:\n   {exc}\n"
              f"   State saved ({state_path(source_id).relative_to(REPO_ROOT)}). The candidate stays\n"
              f"   approved; fix the cause and re-run — completed steps are skipped.", file=sys.stderr)
        return 1

    # post-deploy smoke (best-effort, non-fatal)
    smoke = post_deploy_smoke(pkg)
    st["steps"]["7_smoke"] = {"status": "done", **smoke,
                              "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    save_state(st)
    if smoke.get("ran"):
        print(f"  [7] smoke health_ok={smoke['health_ok']} surfaced={smoke['surfaced']} "
              f"({len(smoke.get('probes') or [])} probes)")
    record_execution(source_id, "success",
                     commit=st["steps"].get("6_commit", {}).get("commit"),
                     chunk_delta=st["chunks"], after_total=st["after_total"], smoke=smoke)
    print(f"✅ {source_id} ingested live (+{st['chunks']} → {st['after_total']}).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Executor for the Option A automated-ingest pipeline "
                                             "(dry-run plan in Phase 2; live ingest in Phase 3).")
    ap.add_argument("--package", help="staged source_id under dev/source/ingest_packages/")
    ap.add_argument("--all-prepared", action="store_true", help="act on every staged package whose status=='prepared'")
    ap.add_argument("--init-approval", action="store_true", help="write a pending approval record for --package and exit")
    ap.add_argument("--dry-run", action="store_true", help="produce the execution plan without any live writes")
    ap.add_argument("--live", action="store_true", help="PERFORM the live ingest (needs approval + secrets); Phase 3")
    args = ap.parse_args()

    if args.dry_run and args.live:
        ap.error("--dry-run and --live are mutually exclusive")

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

    if args.live:
        rc = 0
        for sid in ids:
            rc = exec_live(sid) or rc
        return rc

    if not args.dry_run:
        ap.error("specify --dry-run (plan only) or --live (perform the ingest)")
        return 2

    for sid in ids:
        plan = build_plan(sid)
        out = STAGING_DIR / sid / "execution_plan.json"
        out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print_plan(plan)
        print(f"plan written: {out.relative_to(REPO_ROOT)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
