#!/usr/bin/env python3
"""_s213_validate_gold.py — re-derive every gold label from the corpus and
reject the ones that do not hold.

A gold set is only worth what its weakest label is worth, and three of the four
slices were written by agents. Their own reports are not evidence: this checks
each claim against the corpus snapshot independently, and an item that fails is
QUARANTINED rather than quietly repaired — a silently "fixed" label is a label
nobody verified.

Checks per item
  structural   required fields present, types correct, split ∈ {dev, held_out}
  chunk        `verified_by.chunk_id` exists in the corpus
  source       that chunk really belongs to a source in `expected_source_any`
  signature    the signature really occurs in that chunk's CLEANED text
               (markers stripped, whitespace squeezed — what the API returns)
  page         `expected_page` equals `dominant_page()` of that chunk
  absence      for `answerable: false`, no chunk anywhere contains the signature,
               and no source is asserted
  query        not a verbatim lift of ≥12 characters out of its own passage

USAGE
  python3 dev/_s213_validate_gold.py --self-test
  python3 dev/_s213_validate_gold.py dev/_s213_gold_*.json
  python3 dev/_s213_validate_gold.py dev/_s213_gold_*.json --merge dev/_s213_gold_all.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_corpus import (DEFAULT_CACHE, clean_for_match, dominant_page,  # noqa: E402
                          fold, load, squeeze)

REQUIRED = ("id", "domain", "query", "query_kind", "intent", "answerable",
            "expected_source_any", "expected_passage_signature",
            "expected_page", "acceptable_alternatives", "forbidden_evidence",
            "verified_by", "split")


def validate_item(it: dict, by_id: dict[str, dict],
                  clean_index: list[tuple[str, str]]) -> list[str]:
    """Return the list of reasons this item is not trustworthy ([] = good)."""
    bad: list[str] = []
    for f in REQUIRED:
        if f not in it:
            bad.append(f"缺欄位 {f}")
    if bad:
        return bad
    if it["split"] not in ("dev", "held_out"):
        bad.append(f"split 非法：{it['split']!r}")
    if not isinstance(it["expected_passage_signature"], list):
        bad.append("expected_passage_signature 必須是 list")
        return bad

    if not it["answerable"]:
        if it["expected_source_any"] or it["expected_passage_signature"]:
            bad.append("無答案題卻帶有來源或簽名斷言")
        return bad

    if not it["expected_source_any"]:
        bad.append("可答題沒有 expected_source_any")
    sigs = [s for s in it["expected_passage_signature"] if s]
    if not sigs:
        bad.append("可答題沒有 expected_passage_signature")
        return bad
    for s in sigs:
        # `===` runs and `Page N` are the markers the backend strips. A lone
        # `=` is legitimate content — a grant formula reads 「（SAC）＝1個課室率」,
        # and NFKC folds that full-width equals to an ASCII one.
        if "==" in s or re.search(r"Page\s*\d", s):
            bad.append(f"簽名含標記，永遠對不上真實回應：{s[:30]!r}")

    cid = (it.get("verified_by") or {}).get("chunk_id")
    if not cid:
        bad.append("verified_by 沒有 chunk_id，標籤無出處")
        return bad
    row = by_id.get(cid)
    if row is None:
        bad.append(f"chunk_id 在語料中不存在：{cid}")
        return bad

    sid = row.get("source_id")
    allowed = set(it["expected_source_any"]) | set(it.get("acceptable_alternatives") or [])
    if sid not in allowed:
        bad.append(f"chunk 屬於 {sid}，不在 expected/alternatives {sorted(allowed)} 之內")

    hay = squeeze(clean_for_match(row.get("text", "")))
    for s in sigs:
        if squeeze(fold(s)) not in hay:
            bad.append(f"簽名不在該 chunk 的清洗後正文：{s[:30]!r}")

    want_page = dominant_page(row.get("text", ""))
    if it["expected_page"] != want_page:
        bad.append(f"頁碼不符：檔案寫 {it['expected_page']}，實際推導 {want_page}")

    q = squeeze(it["query"])
    if len(q) >= 12 and any(squeeze(fold(it["query"])) in squeeze(fold(s)) for s in sigs):
        bad.append("查詢是段落的逐字長段移植（≥12 字），量到的會是字串比對")
    return bad


def validate_absence(it: dict, clean_index: list[tuple[str, str]]) -> list[str]:
    """For no-answer items, prove the corpus really cannot answer."""
    phrase = (it.get("verified_by") or {}).get("phrase")
    if not phrase:
        return []          # not all no-answer items declare a probe phrase
    needle = squeeze(fold(phrase))
    hits = [sid for sid, hay in clean_index if needle in hay]
    if hits:
        return [f"聲稱無答案，但 {len(hits)} 條 chunk 含 {phrase!r}"
                f"（例如 {hits[0]}）"]
    return []


def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    good = {"id": "x", "domain": "d", "query": "短查詢", "query_kind": "plain",
            "intent": "i", "answerable": True, "expected_source_any": ["s1"],
            "expected_passage_signature": ["正文片語"], "expected_page": 7,
            "acceptable_alternatives": [], "forbidden_evidence": [],
            "verified_by": {"chunk_id": "c1"}, "split": "dev"}
    by_id = {"c1": {"id": "c1", "source_id": "s1",
                    "text": "=== Page 7 ===" + "字" * 40 + "正文片語" + "字" * 40}}
    check("正確的條目通過", validate_item(good, by_id, []) == [])
    check("chunk 不存在會紅",
          any("不存在" in r for r in
              validate_item({**good, "verified_by": {"chunk_id": "nope"}}, by_id, [])))
    check("簽名不在該 chunk 會紅",
          any("不在該 chunk" in r for r in
              validate_item({**good, "expected_passage_signature": ["查無此語"]},
                            by_id, [])))
    check("頁碼不符會紅",
          any("頁碼不符" in r for r in
              validate_item({**good, "expected_page": 99}, by_id, [])))
    check("來源對不上會紅",
          any("不在 expected" in r for r in
              validate_item({**good, "expected_source_any": ["other"]}, by_id, [])))
    check("簽名含頁碼標記會紅",
          any("含標記" in r for r in
              validate_item({**good, "expected_passage_signature": ["=== Page 7 ==="]},
                            by_id, [])))
    check("無答案題卻帶斷言會紅",
          any("卻帶有來源" in r for r in
              validate_item({**good, "answerable": False}, by_id, [])))
    check("缺欄位會紅",
          any("缺欄位" in r for r in
              validate_item({k: v for k, v in good.items() if k != "intent"},
                            by_id, [])))
    check("聲稱無答案但語料有該片語會紅",
          validate_absence({"verified_by": {"phrase": "有的"}},
                           [("s1", "這裡有的內容")]) != [])
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--merge", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.files:
        ap.error("give at least one gold file")

    rows = load(args.cache)
    by_id = {r["id"]: r for r in rows}
    clean_index = [(r.get("source_id", "?"), squeeze(clean_for_match(r.get("text", ""))))
                   for r in rows]

    kept, quarantined, seen_ids = [], [], set()
    for f in args.files:
        items = json.loads(f.read_text(encoding="utf-8"))
        ok = 0
        for it in items:
            reasons = validate_item(it, by_id, clean_index)
            if not it.get("answerable", True):
                reasons += validate_absence(it, clean_index)
            if it.get("id") in seen_ids:
                reasons.append(f"id 與其他檔案重複：{it.get('id')}")
            seen_ids.add(it.get("id"))
            if reasons:
                quarantined.append((f.name, it.get("id"), reasons))
            else:
                kept.append(it)
                ok += 1
        print(f"{f.name:<34}{ok:>4}/{len(items)} 通過")

    print(f"\n通過 {len(kept)}，隔離 {len(quarantined)}")
    if quarantined:
        print("\n=== 隔離明細 ===")
        reason_kinds = collections.Counter()
        for fn, iid, rs in quarantined:
            print(f"  [{fn}] {iid}")
            for r in rs:
                print(f"      - {r}")
                reason_kinds[r.split("：")[0].split("（")[0]] += 1
        print("\n原因分類:", dict(reason_kinds))

    print("\n=== 通過者的覆蓋 ===")
    print("範疇:", dict(collections.Counter(i["domain"] for i in kept)))
    print("類型:", dict(collections.Counter(i["query_kind"] for i in kept)))
    print("split:", dict(collections.Counter(i["split"] for i in kept)))
    print("無答案題:", sum(1 for i in kept if not i["answerable"]))
    thin = [d for d, n in collections.Counter(i["domain"] for i in kept).items() if n < 10]
    if thin:
        print(f"⚠️ 不足 10 條的範疇: {thin}")

    if args.merge:
        args.merge.write_text(json.dumps(kept, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        print(f"\n已合併 {len(kept)} 條到 {args.merge}")
    return 1 if quarantined else 0


if __name__ == "__main__":
    raise SystemExit(main())
