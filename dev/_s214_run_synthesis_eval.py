#!/usr/bin/env python3
"""S214 Phase 1.1: read-only synthesis/abstention evaluation.

Runs every no-answer Gold Set query, a matched set of answerable controls, and
all queries carrying forbidden evidence.  This script never writes to the
service; its only network operation is POSTing search requests with x-probe=1.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "https://edb-knowledge.onrender.com/api/search/channel-b"
DEFAULT_GOLD = Path("dev/_s213_gold_all.json")
DEFAULT_BASELINE = Path("dev/source/eval_runs/2026-09-04_s213_gold_baseline.json")
DEFAULT_OUT = Path("dev/source/eval_runs/2026-09-04_s214_synthesis.json")
DECLINE = (
    "根據檢索到的教育局文件，暫時未能找到可直接回答此問題的明確資料。"
    "下方為主題相關的原始文件，或可參考；亦可嘗試以其他關鍵詞重新搜尋。"
)
FORBIDDEN_IDS = {
    "sen_special_school_curriculum",
    "ss_ncs_history_adapted",
    "bus_guide_audience_confusable",
    "kg_sccc_ratio_confusable",
}


def select_cases(gold: list[dict], baseline: dict) -> list[dict]:
    """Return 19 no-answer, 19 domain-matched controls, plus forbidden cases."""
    no_answer = [item for item in gold if not item.get("answerable", True)]
    by_id = {row["id"]: row for row in baseline["results"]}
    candidates = [
        item for item in gold
        if item.get("answerable", True)
        and by_id.get(item["id"], {}).get("chunk_verdict") == "PASS"
    ]

    controls: list[dict] = []
    used: set[str] = set()
    for target in no_answer:
        match = next(
            (item for item in candidates
             if item["domain"] == target["domain"] and item["id"] not in used),
            None,
        )
        if match:
            controls.append(match)
            used.add(match["id"])

    for item in candidates:
        if len(controls) >= len(no_answer):
            break
        if item["id"] not in used:
            controls.append(item)
            used.add(item["id"])

    if len(controls) != len(no_answer):
        raise RuntimeError(
            f"need {len(no_answer)} positive controls, found {len(controls)}"
        )

    selected: list[dict] = []
    selected_ids: set[str] = set()
    for cohort, items in (("no_answer", no_answer), ("positive_control", controls)):
        for item in items:
            selected.append({**item, "cohort": cohort})
            selected_ids.add(item["id"])

    for item in gold:
        if item["id"] in FORBIDDEN_IDS and item["id"] not in selected_ids:
            selected.append({**item, "cohort": "forbidden_addon"})
            selected_ids.add(item["id"])

    missing = FORBIDDEN_IDS - selected_ids
    if missing:
        raise RuntimeError(f"forbidden query ids missing from Gold Set: {sorted(missing)}")
    return selected


def query_once(endpoint: str, query: str, top_k: int) -> dict:
    body = json.dumps({
        "query": query,
        "top_k": top_k,
        "synthesize": True,
    }).encode("utf-8")
    last_error = ""
    for attempt in range(1, 4):
        req = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json", "x-probe": "1"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.read()[:200]!r}"
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                break
        except OSError as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 3:
                break
        time.sleep(7 * attempt)
    raise RuntimeError(last_error or "request failed")


def evaluate_case(item: dict, response: dict) -> dict:
    results = response.get("results") or []
    synthesis = (response.get("synthesis") or "").strip()
    expected = set(item.get("expected_source_any") or [])
    expected.update(item.get("acceptable_alternatives") or [])
    forbidden = set(item.get("forbidden_evidence") or [])
    source_ids = [row.get("source_id") for row in results]
    top_five = source_ids[:5]
    is_decline = synthesis == DECLINE

    if not item.get("answerable", True):
        automatic_outcome = "correct_abstention" if is_decline else "answered_no_answer_case"
    elif is_decline:
        automatic_outcome = "false_abstention"
    elif expected.intersection(top_five):
        automatic_outcome = "answer_with_expected_source_in_window"
    else:
        automatic_outcome = "answer_without_expected_source_in_window"

    return {
        "id": item["id"],
        "domain": item["domain"],
        "cohort": item["cohort"],
        "query": item["query"],
        "intent": item.get("intent"),
        "answerable": item.get("answerable", True),
        "expected_source_any": sorted(expected),
        "forbidden_evidence": sorted(forbidden),
        "declined": is_decline,
        "automatic_outcome": automatic_outcome,
        "expected_in_top5": bool(expected.intersection(top_five)),
        "forbidden_positions": [
            index for index, source_id in enumerate(source_ids)
            if source_id in forbidden
        ],
        "forbidden_in_top5": bool(forbidden.intersection(top_five)),
        "synthesis": synthesis,
        "results": [
            {
                "rank": index,
                "id": row.get("id"),
                "source_id": row.get("source_id"),
                "title": row.get("title"),
                "content_type": row.get("content_type"),
                "score": row.get("score"),
                "page": row.get("page"),
                "text": row.get("text"),
            }
            for index, row in enumerate(results)
        ],
        "manual_review": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--pace", type=float, default=7.0)
    args = parser.parse_args()

    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    cases = select_cases(gold, baseline)
    print(
        f"selected {len(cases)} cases: "
        f"{sum(c['cohort'] == 'no_answer' for c in cases)} no-answer, "
        f"{sum(c['cohort'] == 'positive_control' for c in cases)} controls, "
        f"{sum(c['cohort'] == 'forbidden_addon' for c in cases)} forbidden add-ons"
    )

    rows: list[dict] = []
    errors = 0
    for index, item in enumerate(cases, 1):
        if index > 1:
            time.sleep(args.pace)
        try:
            response = query_once(args.endpoint, item["query"], 8)
            row = evaluate_case(item, response)
            print(
                f"[{index:02d}/{len(cases)}] {item['id']:<38} "
                f"decline={row['declined']} outcome={row['automatic_outcome']}"
            )
        except RuntimeError as exc:
            errors += 1
            row = {
                "id": item["id"],
                "domain": item["domain"],
                "cohort": item["cohort"],
                "query": item["query"],
                "error": str(exc),
            }
            print(f"[{index:02d}/{len(cases)}] {item['id']:<38} ERROR {exc}")
        rows.append(row)

    summary = {
        "cases": len(cases),
        "errors": errors,
        "no_answer": sum(row.get("cohort") == "no_answer" for row in rows),
        "correct_abstentions": sum(
            row.get("automatic_outcome") == "correct_abstention" for row in rows
        ),
        "positive_controls": sum(
            row.get("cohort") == "positive_control" for row in rows
        ),
        "false_abstentions": sum(
            row.get("automatic_outcome") == "false_abstention" for row in rows
        ),
        "forbidden_cases": sum(bool(row.get("forbidden_evidence")) for row in rows),
        "forbidden_in_top5": sum(bool(row.get("forbidden_in_top5")) for row in rows),
    }
    output = {
        "label": "S214 Phase 1.1 synthesis and abstention evaluation",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": args.endpoint,
        "top_k": 8,
        "synthesis_window_assumption": 5,
        "decline_text": DECLINE,
        "selection": (
            "all 19 no-answer cases; 19 answerable controls preferring a chunk-PASS "
            "case in each no-answer domain; all four forbidden-evidence cases"
        ),
        "observability_boundary": (
            "Public response exposes synthesis and ranked results only; internal "
            "judgeCanAnswer and trustedVaultLead bypass decisions are not observable."
        ),
        "summary": summary,
        "results": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {args.out}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
