#!/usr/bin/env python3
"""
dedup_check.py — Fact Deduplication Checker

Analyses approved facts from a Dashboard admin snapshot (or role_facts.json)
and reports similar / duplicate pairs before you export role_facts.json.

No API key required — uses character n-gram similarity (Chinese-friendly).

Usage:
  # Check admin snapshot (exported from Dashboard → 匯出 → 管理快照)
  cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
  python3 dev/vault/dedup_check.py <path-to-admin-snapshot.json>

  # Check existing role_facts.json
  python3 dev/vault/dedup_check.py role_facts.json

  # Adjust similarity threshold (default 0.50)
  python3 dev/vault/dedup_check.py snapshot.json --threshold 0.45

  # Also check against existing role_facts.json for cross-file duplication
  python3 dev/vault/dedup_check.py snapshot.json --against role_facts.json

Output:
  Prints a report of similar pairs grouped by topic.
  Similarity 0.85+  → 🔴 Very likely duplicate — recommend deleting one
  Similarity 0.60+  → 🟡 Similar — review carefully
  Similarity 0.50+  → 🔵 Possibly related — check if both add value
"""

import argparse
import json
import sys
from pathlib import Path
from itertools import combinations

# ---------------------------------------------------------------------------
# Similarity: character n-gram Jaccard (works well for Chinese)
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove punctuation and whitespace for comparison."""
    return "".join(c for c in text if c.strip() and c not in "，。、：；！？「」『』【】（）—…,.;:!?()[]{}\"'")


def ngrams(text: str, n: int) -> set:
    """Generate character n-grams."""
    c = clean_text(text)
    return {c[i:i+n] for i in range(len(c) - n + 1)} if len(c) >= n else {c}


def jaccard(sa: set, sb: set) -> float:
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def similarity(a: str, b: str) -> float:
    """
    Combined similarity score:
    - Bigram Jaccard (captures more Chinese character overlap)
    - Trigram Jaccard
    - Unique CJK word overlap (words of 2+ chars)
    Returns the max of the three scores.
    """
    bi_score  = jaccard(ngrams(a, 2), ngrams(b, 2))
    tri_score = jaccard(ngrams(a, 3), ngrams(b, 3))

    # CJK word-level overlap: extract 2-char and 3-char substrings as "words"
    def cjk_words(text: str) -> set:
        c = clean_text(text)
        words = set()
        for n in (2, 3):
            for i in range(len(c) - n + 1):
                chunk = c[i:i+n]
                if all('\u4e00' <= ch <= '\u9fff' for ch in chunk):
                    words.add(chunk)
        return words
    word_score = jaccard(cjk_words(a), cjk_words(b))

    return max(bi_score, tri_score, word_score)


def is_substring(a: str, b: str) -> bool:
    """Check if one fact is substantially contained in the other."""
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    s = clean_text(short)
    l = clean_text(long_)
    return len(s) >= 10 and s in l


# ---------------------------------------------------------------------------
# Fact extraction
# ---------------------------------------------------------------------------

ROLE_KEYS = ["all_roles", "principal", "vice_principal", "panel_chair",
             "subject_head", "teacher", "eo_admin", "supplier"]


def extract_facts_from_snapshot(data: dict, review_state: dict) -> dict[str, list[dict]]:
    """
    Returns {topic: [{fact, role, key, approved}]} — only approved facts.
    """
    result = {}
    for topic, topic_data in data.items():
        if topic == "_meta" or not isinstance(topic_data, dict):
            continue
        facts = []
        for role in ROLE_KEYS:
            role_facts = topic_data.get(role, [])
            if not isinstance(role_facts, list):
                continue
            for idx, fact_text in enumerate(role_facts):
                key = f"{topic}.{role}.{idx}"
                state = review_state.get(key, "approved")  # default approved if not set
                facts.append({
                    "fact": fact_text,
                    "role": role,
                    "key": key,
                    "approved": state == "approved",
                })
        if facts:
            result[topic] = facts
    return result


def extract_facts_from_role_facts(data: dict) -> dict[str, list[dict]]:
    """Extract facts from plain role_facts.json (all treated as approved)."""
    result = {}
    for topic, topic_data in data.items():
        if topic == "_meta" or not isinstance(topic_data, dict):
            continue
        facts = []
        for role in ROLE_KEYS:
            role_facts = topic_data.get(role, [])
            if not isinstance(role_facts, list):
                continue
            for idx, fact_text in enumerate(role_facts):
                facts.append({
                    "fact": fact_text,
                    "role": role,
                    "key": f"{topic}.{role}.{idx}",
                    "approved": True,
                })
        if facts:
            result[topic] = facts
    return result


# ---------------------------------------------------------------------------
# Pair analysis
# ---------------------------------------------------------------------------

def find_similar_pairs(facts: list[dict], threshold: float) -> list[dict]:
    """Find all pairs of approved facts above the similarity threshold."""
    approved = [f for f in facts if f["approved"]]
    pairs = []
    for a, b in combinations(approved, 2):
        sim = similarity(a["fact"], b["fact"])
        substr = is_substring(a["fact"], b["fact"])
        if sim >= threshold or substr:
            pairs.append({
                "sim": sim,
                "substr": substr,
                "a": a,
                "b": b,
            })
    return sorted(pairs, key=lambda p: -p["sim"])


def find_cross_topic_pairs(
    facts_map: dict[str, list[dict]],
    baseline_map: dict[str, list[dict]],
    threshold: float
) -> list[dict]:
    """
    Find approved facts in facts_map that are very similar to facts in baseline_map
    (cross-file duplication check).
    """
    pairs = []
    all_new = [(t, f) for t, fl in facts_map.items() for f in fl if f["approved"]]
    all_base = [(t, f) for t, fl in baseline_map.items() for f in fl]
    for (t_new, f_new) in all_new:
        for (t_base, f_base) in all_base:
            sim = similarity(f_new["fact"], f_base["fact"])
            substr = is_substring(f_new["fact"], f_base["fact"])
            if sim >= threshold or substr:
                pairs.append({
                    "sim": sim,
                    "substr": substr,
                    "new_topic": t_new,
                    "base_topic": t_base,
                    "a": f_new,
                    "b": f_base,
                })
    return sorted(pairs, key=lambda p: -p["sim"])


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

TOPIC_LABELS = {
    "finance": "財務採購",
    "hr": "人力資源",
    "curriculum": "課程發展",
    "activity": "學生活動",
    "student": "學生支援",
    "it": "資訊科技",
    "general": "一般行政",
}


def severity_icon(sim: float, substr: bool) -> str:
    if substr or sim >= 0.85:
        return "🔴"
    if sim >= 0.60:
        return "🟡"
    return "🔵"


def print_report(facts_map: dict, threshold: float, baseline_map: dict = None):
    total_pairs = 0
    red_count = 0

    print("\n" + "=" * 60)
    print("  FACT DEDUPLICATION REPORT")
    print("=" * 60)

    # ── Within-topic pairs ──
    print("\n【同 Topic 內相似 Facts】\n")

    for topic, facts in sorted(facts_map.items()):
        approved_count = sum(1 for f in facts if f["approved"])
        pairs = find_similar_pairs(facts, threshold)
        if not pairs:
            continue

        label = TOPIC_LABELS.get(topic, topic)
        print(f"  ▍ {label} ({topic})  — {approved_count} approved facts, {len(pairs)} similar pairs")
        print()

        for p in pairs:
            icon = severity_icon(p["sim"], p["substr"])
            sim_pct = f"{p['sim']*100:.0f}%"
            extra = " [包含關係]" if p["substr"] else ""
            print(f"    {icon} 相似度 {sim_pct}{extra}")
            print(f"       A [{p['a']['role']}]: {p['a']['fact']}")
            print(f"       B [{p['b']['role']}]: {p['b']['fact']}")
            print(f"       建議: {'刪除其中一個' if p['sim'] >= 0.85 or p['substr'] else '確認兩者是否各有獨立價值'}")
            print()
            total_pairs += 1
            if p["sim"] >= 0.85 or p["substr"]:
                red_count += 1

    # ── Cross-file pairs ──
    if baseline_map:
        cross_pairs = find_cross_topic_pairs(facts_map, baseline_map, threshold)
        if cross_pairs:
            print("\n【與現有 role_facts.json 的重複】\n")
            for p in cross_pairs:
                icon = severity_icon(p["sim"], p["substr"])
                sim_pct = f"{p['sim']*100:.0f}%"
                extra = " [包含關係]" if p["substr"] else ""
                print(f"    {icon} 相似度 {sim_pct}{extra}")
                print(f"       新 [{p['new_topic']} / {p['a']['role']}]: {p['a']['fact']}")
                print(f"       舊 [{p['base_topic']} / {p['b']['role']}]: {p['b']['fact']}")
                print(f"       建議: {'新 fact 可刪除，現有已覆蓋' if p['sim'] >= 0.85 or p['substr'] else '確認是否更新或保留兩者'}")
                print()
                total_pairs += 1
                if p["sim"] >= 0.85 or p["substr"]:
                    red_count += 1

    # ── Summary ──
    print("=" * 60)
    print(f"  總計：{total_pairs} 對相似 facts")
    print(f"  🔴 強烈建議刪除：{red_count} 對")
    print(f"  閾值：{threshold*100:.0f}%  (調整用 --threshold)")
    print("=" * 60)

    if total_pairs == 0:
        print("\n  ✅ 未發現相似 facts，可安全匯出 role_facts.json。\n")
    else:
        print("\n  ⚠️  請在 Dashboard 刪除重複 facts 後再匯出 role_facts.json。\n")
        print("  操作方法：Dashboard → Admin → Knowledge 標籤 → 找到對應 fact → 刪除\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fact deduplication checker")
    parser.add_argument("input", help="Admin snapshot JSON or role_facts.json")
    parser.add_argument("--threshold", type=float, default=0.50,
                        help="Similarity threshold 0.0-1.0 (default: 0.50)")
    parser.add_argument("--against", default=None,
                        help="Also check against this role_facts.json for cross-file duplicates")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        raw = json.load(f)

    # Detect format: admin snapshot vs plain role_facts.json
    if "review_state" in raw and "data" in raw:
        # Admin snapshot format
        print(f"Format: Admin Snapshot (exported {raw.get('exported_at','?')})")
        facts_map = extract_facts_from_snapshot(raw["data"], raw["review_state"])
    else:
        # Plain role_facts.json
        print(f"Format: role_facts.json (version {raw.get('_meta',{}).get('version','?')})")
        facts_map = extract_facts_from_role_facts(raw)

    total_approved = sum(sum(1 for f in fl if f["approved"]) for fl in facts_map.values())
    print(f"Loaded:  {total_approved} approved facts across {len(facts_map)} topics")

    # Optional baseline
    baseline_map = None
    if args.against:
        baseline_path = Path(args.against)
        if baseline_path.exists():
            with open(baseline_path, encoding="utf-8") as f:
                baseline_raw = json.load(f)
            baseline_map = extract_facts_from_role_facts(baseline_raw)
            baseline_total = sum(len(fl) for fl in baseline_map.values())
            print(f"Baseline: {baseline_total} facts from {baseline_path.name}")
        else:
            print(f"Warning: --against file not found: {baseline_path}", file=sys.stderr)

    print_report(facts_map, args.threshold, baseline_map)


if __name__ == "__main__":
    main()
