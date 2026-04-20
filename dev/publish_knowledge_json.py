#!/usr/bin/env python3
"""
publish_knowledge_json.py — derive public `knowledge.json` from `role_facts.json`.
==================================================================================

Context
-------
`role_facts.json` (repo-root) is the internal SSOT. It carries every approved
fact plus `_source_refs` traceability metadata per topic. The public API
endpoint `knowledge.json` is what Circular System (and any external consumer)
hits — it must stay on the documented public schema.

This script does exactly three things:

  1. Strip `_source_refs` from every topic block (internal traceability, not
     part of the public contract).
  2. Ensure every topic block exposes all 8 public role buckets
     (`all_roles`, `principal`, `vice_principal`, `subject_head`,
     `panel_chair`, `teacher`, `eo_admin`, `supplier`) as arrays. Missing
     buckets are filled with [] so external consumers can rely on the schema
     shape.
  3. Write `knowledge.json` with a refreshed `_meta`.

Usage
-----
  python3 dev/publish_knowledge_json.py                # dry-run preview
  python3 dev/publish_knowledge_json.py --write        # write knowledge.json
  python3 dev/publish_knowledge_json.py --write --version 1.5.0

When --version is omitted, the existing `knowledge.json._meta.version` is
preserved. When --write is omitted, nothing is written — use it to inspect
the diff.

Guidelines.json is not touched here. It is a separate artifact with its own
content; only its version number needs to be bumped when published jointly.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROLE_FACTS_PATH = REPO_ROOT / "role_facts.json"
KNOWLEDGE_JSON_PATH = REPO_ROOT / "knowledge.json"

PUBLIC_ROLE_BUCKETS = (
    "all_roles",
    "principal",
    "vice_principal",
    "subject_head",
    "panel_chair",
    "teacher",
    "eo_admin",
    "supplier",
)

PUBLIC_TOPIC_META_KEYS = ("_label", "_keywords_zh", "_sources")
# _source_refs is internal traceability and is dropped.


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_facts(kb: dict) -> int:
    total = 0
    for topic, tk in kb.items():
        if topic.startswith("_") or not isinstance(tk, dict):
            continue
        for role, facts in tk.items():
            if role.startswith("_") or not isinstance(facts, list):
                continue
            total += sum(1 for f in facts if isinstance(f, str) and f.strip())
    return total


def transform(role_facts: dict, new_version: str | None, old_meta: dict) -> dict:
    """Return the public-shape knowledge.json dict."""
    today = datetime.date.today().isoformat()
    version = new_version or old_meta.get("version") or role_facts.get("_meta", {}).get("version", "")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise SystemExit(f"Invalid version string: {version!r}")

    fact_count = count_facts(role_facts)
    description = (
        f"EDB 學校管理知識庫 — 供 EDB 通告智能分析系統注入 LLM prompt 使用。"
        f"{fact_count} 事實全部 approved。"
        "角色拆分為 panel_chair（各統籌主任）與 subject_head（科主任）；"
        "兩者均適用時雙寫。"
    )

    out: dict = {
        "_meta": {
            "version": version,
            "created": old_meta.get("created", today),
            "updated": today,
            "description": description,
        }
    }

    for topic, tk in role_facts.items():
        if topic.startswith("_") or not isinstance(tk, dict):
            continue
        topic_out: dict = {}
        # preserve public topic-level meta fields (not _source_refs)
        for k in PUBLIC_TOPIC_META_KEYS:
            if k in tk:
                topic_out[k] = tk[k]
        # emit every public role bucket as an array (fill missing with [])
        for role in PUBLIC_ROLE_BUCKETS:
            facts = tk.get(role)
            if isinstance(facts, list):
                cleaned = [f for f in facts if isinstance(f, str) and f.strip()]
            else:
                cleaned = []
            topic_out[role] = cleaned
        out[topic] = topic_out

    return out


def diff_summary(old: dict, new: dict) -> list[str]:
    lines: list[str] = []
    lines.append(f"fact count: {count_facts(old)} → {count_facts(new)}")
    lines.append(
        f"version:    {old.get('_meta',{}).get('version','?')} → {new['_meta']['version']}"
    )
    lines.append(
        f"updated:    {old.get('_meta',{}).get('updated','?')} → {new['_meta']['updated']}"
    )
    # per-topic fact deltas
    for topic in new.keys():
        if topic.startswith("_"):
            continue
        old_tk = old.get(topic, {}) if isinstance(old.get(topic), dict) else {}
        old_n = sum(
            len(v) for k, v in old_tk.items() if not k.startswith("_") and isinstance(v, list)
        )
        new_n = sum(
            len(v) for k, v in new[topic].items() if not k.startswith("_") and isinstance(v, list)
        )
        delta = new_n - old_n
        sign = "+" if delta >= 0 else ""
        lines.append(f"  {topic:<11} {old_n:>4} → {new_n:>4} ({sign}{delta})")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="actually write knowledge.json")
    parser.add_argument("--version", type=str, default=None, help="new _meta.version (e.g. 1.5.0)")
    args = parser.parse_args()

    role_facts = load_json(ROLE_FACTS_PATH)
    old_knowledge = load_json(KNOWLEDGE_JSON_PATH) if KNOWLEDGE_JSON_PATH.exists() else {}
    old_meta = old_knowledge.get("_meta", {}) if isinstance(old_knowledge, dict) else {}

    new_knowledge = transform(role_facts, args.version, old_meta)

    print("# publish_knowledge_json")
    print(f"source: {ROLE_FACTS_PATH.relative_to(REPO_ROOT)}")
    print(f"target: {KNOWLEDGE_JSON_PATH.relative_to(REPO_ROOT)}")
    print("")
    for line in diff_summary(old_knowledge, new_knowledge):
        print(line)
    print("")

    if not args.write:
        print("dry-run — pass --write to update knowledge.json")
        return

    KNOWLEDGE_JSON_PATH.write_text(
        json.dumps(new_knowledge, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {KNOWLEDGE_JSON_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
