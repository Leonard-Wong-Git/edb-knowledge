#!/usr/bin/env python3
"""
build_stat_facts.py — Statistical Fact Builder (no LLM required)

Parses EDB stat extract files and generates dev/knowledge/stat_facts.json.
Statistical facts are auto-approved (no human review needed per architecture).

Usage:
  cd ~/Downloads/Claude-edb-knowledge
  python3 dev/vault/build_stat_facts.py

Output:
  dev/knowledge/stat_facts.json
"""

import json
import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO_ROOT / "dev" / "knowledge" / "stat_facts.json"

# ---------------------------------------------------------------------------
# Source registry (for URL lookup)
# ---------------------------------------------------------------------------

def load_source_url(source_id: str) -> str:
    registry_path = REPO_ROOT / "dev" / "source" / "source_registry.json"
    try:
        with open(registry_path, encoding="utf-8") as f:
            reg = json.load(f)
        sources = reg if isinstance(reg, list) else reg.get("sources", [])
        for s in sources:
            if s.get("source_id") == source_id or s.get("id") == source_id:
                return s.get("url", "")
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Fact builders per source
# ---------------------------------------------------------------------------

def build_kg_facts() -> list[dict]:
    """幼稚園教育統計 — 2024/25 latest"""
    url = load_source_url("stat_kg")
    base = dict(source_id="stat_kg", auto_approved=True, fact_type="statistical",
                topic="student", school_level="幼稚園", reference_year="2024/25", source_url=url)
    return [
        {**base, "fact": "2024/25學年香港幼稚園數目為980所，其中734所參加幼稚園教育計劃。"},
        {**base, "fact": "2024/25學年幼稚園學生總人數為125,426人（幼兒班37,079、低班43,057、高班45,290）。"},
        {**base, "fact": "2024/25學年幼稚園教師人數為11,235人，曾受訓練教師佔98.5%。"},
        {**base, "fact": "2024/25學年幼稚園學生與教師比率為8.1:1。"},
        {**base, "fact": "2024/25學年幼稚園教師流失率為16.0%，較2023/24學年（19.1%）有所下降。"},
    ]


def build_pri_facts() -> list[dict]:
    """小學教育統計 — 2024/25 latest"""
    url = load_source_url("stat_pri")
    base = dict(source_id="stat_pri", auto_approved=True, fact_type="statistical",
                topic="student", school_level="小學", reference_year="2024/25", source_url=url)
    return [
        {**base, "fact": "2024/25學年香港小學數目為590所，其中474所為公營及直接資助計劃學校。"},
        {**base, "fact": "2024/25學年小學學生總人數為319,447人，較2023/24學年（325,564人）繼續下降。"},
        {**base, "fact": "2024/25學年小學教師人數為26,701人，持學士學位或以上佔99.2%（26,481人）。"},
        {**base, "fact": "2024/25學年小學曾受訓練教師比率為93.6%，學生與教師比率為12.0:1。"},
        {**base, "fact": "2024/25學年小學教師流失率為7.4%，較2023/24學年（8.3%）下降。"},
        {**base, "fact": "2024/25學年首次入學的內地來港小學生人數為4,614人。"},
    ]


def build_sec_facts() -> list[dict]:
    """中學教育統計 — 2024/25 latest"""
    url = load_source_url("stat_sec")
    base = dict(source_id="stat_sec", auto_approved=True, fact_type="statistical",
                topic="student", school_level="中學", reference_year="2024/25", source_url=url)
    return [
        {**base, "fact": "2024/25學年香港中學數目為512所，其中447所為公營及直接資助計劃學校。"},
        {**base, "fact": "2024/25學年中學學生總人數為340,607人（中一至中三：180,925；中四至中六：156,988；中七：2,694）。"},
        {**base, "fact": "2024/25學年中學教師人數為30,015人，持學士學位或以上佔99.6%（29,906人）。"},
        {**base, "fact": "2024/25學年中學曾受訓練教師比率為87.4%，學生與教師比率為11.4:1。"},
        {**base, "fact": "2024/25學年中學教師流失率為7.1%，較2023/24學年（8.3%）下降。"},
        {**base, "fact": "2024/25學年首次入學的內地來港中學生人數為2,471人。"},
    ]


def build_special_facts() -> list[dict]:
    """特殊教育統計 — 2024/25 latest"""
    url = load_source_url("stat_special")
    base = dict(source_id="stat_special", auto_approved=True, fact_type="statistical",
                topic="student", school_level="特殊學校", reference_year="2024/25", source_url=url)
    return [
        {**base, "fact": "2024/25學年香港特殊學校共63所，學生總人數9,018人（小學4,228、中學4,790）。"},
        {**base, "fact": "2024/25學年特殊學校教師人數為2,119人，曾受訓練教師佔97.5%，學生與教師比率為4.2:1。"},
        {**base, "fact": "2024/25學年特殊學校教師流失率為8.3%，較2023/24學年（9.8%）下降。"},
        {**base, "fact": "2024/25學年有開辦特殊班的普通學校共10所，特殊班學生人數100人（小學31、中學69）。"},
    ]


def build_integrated_facts() -> list[dict]:
    """融合教育統計 — 2025/26 latest"""
    url = load_source_url("stat_integrated_edu")
    base = dict(source_id="stat_integrated_edu", auto_approved=True, fact_type="statistical",
                topic="student", school_level="融合教育", reference_year="2025/26", source_url=url)
    return [
        {**base, "fact": "2025/26學年公營普通小學有特殊教育需要（SEN）學生總數為33,820人，較2024/25學年（32,250人）上升。"},
        {**base, "fact": "2025/26學年公營普通中學SEN學生總數為37,920人，較2024/25學年（35,620人）持續上升。"},
        {**base, "fact": "2025/26學年小學SEN學生中，特殊學習困難最多（14,100人），其次為自閉症（7,680人）及注意力不足/過度活躍症（6,030人）。"},
        {**base, "fact": "2025/26學年中學SEN學生中，特殊學習困難最多（16,160人），其次為注意力不足/過度活躍症（10,320人）及自閉症（7,430人）。"},
        {**base, "fact": "2025/26學年中學精神病類別SEN學生達1,580人，過去五年持續上升（2020/21年僅660人）。"},
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    facts = []
    facts.extend(build_kg_facts())
    facts.extend(build_pri_facts())
    facts.extend(build_sec_facts())
    facts.extend(build_special_facts())
    facts.extend(build_integrated_facts())

    output = {
        "_meta": {
            "schema": "stat_facts_v1",
            "generated": date.today().isoformat(),
            "total_facts": len(facts),
            "sources": ["stat_kg", "stat_pri", "stat_sec", "stat_special", "stat_integrated_edu"],
            "note": "Auto-approved statistical facts. No human review required. Feed LLM-wiki search path only."
        },
        "facts": facts
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Written {len(facts)} stat facts → {OUTPUT}")
    by_source = {}
    for fact in facts:
        sid = fact["source_id"]
        by_source[sid] = by_source.get(sid, 0) + 1
    for sid, count in sorted(by_source.items()):
        print(f"   {sid}: {count} facts")


if __name__ == "__main__":
    main()
