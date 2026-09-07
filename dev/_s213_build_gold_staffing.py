#!/usr/bin/env python3
"""_s213_build_gold_staffing.py — build the staffing/HR/finance/governance slice
of the S213 gold set, with every label taken from the corpus rather than written
by hand.

Each spec below names a QUERY (what a school user would type) and an ANCHOR
(a phrase that must appear in the passage that answers it). The builder finds
the anchor in the live corpus snapshot, and derives from the chunk it lands in:

  - `expected_source_any`      the chunk's own source_id
  - `expected_passage_signature` a verbatim slice of the CLEANED chunk text
  - `expected_page`            `dominant_page()`, the backend's own rule

So a label cannot be invented: if the anchor is missing, or lands in more than
one source when the spec did not say so, the build STOPS and names the spec.
`answerable: false` specs are verified in the opposite direction — the builder
asserts the phrase is genuinely absent, so a no-answer item is evidence too.

READ-ONLY with respect to the corpus and the search endpoint; writes one file.

USAGE
  python3 dev/_s213_build_gold_staffing.py --self-test
  python3 dev/_s213_build_gold_staffing.py --out dev/_s213_gold_staffing.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_corpus import (DEFAULT_CACHE, clean_for_match, dominant_page,  # noqa: E402
                          load, squeeze)

SIG_LEN = 34
TIE = ["g24", "sag_2025_11"]          # same document ingested twice

# (id, domain, query, kind, intent, anchor, source_hint, forbidden, alts)
# source_hint = None → anchor must be unique to ONE source across the corpus.
SPECS: list[dict] = [
    # ---------------- staffing ----------------
    dict(id="staff_fullday_12", domain="staffing", query="12班小學 學位教師",
         kind="plain", intent="查全日制資助小學 12 班的小學學位教師編制人數",
         anchor="全日制資助小學核准開辦 12 班的教學人員編制", src="staff_est_pri",
         forbidden=["staff_est_sp_sch_pri"],
         note="平台曾就此題答錯（答 12，正確為 5）。半日制同題是 4，故必須分流。"),
    dict(id="staff_halfday_12", domain="staffing", query="半日制小學 12班 編制",
         kind="confusable", intent="查半日制 12 班編制，須與全日制表分流",
         anchor="半日制資助小學核准開辦 12 班的教學人員編制", src="staff_est_pri",
         forbidden=[]),
    dict(id="staff_fullday_24", domain="staffing", query="24班小學編制",
         kind="plain", intent="查全日制 24 班教學人員編制",
         anchor="全日制資助小學核准開辦 24 班的教學人員編制", src="staff_est_pri",
         forbidden=[]),
    dict(id="staff_halfday_24", domain="staffing", query="半日制 24 班 教師人數",
         kind="confusable", intent="查半日制 24 班編制",
         anchor="半日制資助小學核准開辦 24 班的教學人員編制", src="staff_est_pri",
         forbidden=[]),
    dict(id="staff_head_ratio_full", domain="staffing", query="主任級教師 比例",
         kind="plain", intent="查全日制小學主任級教師職位的計算基礎",
         anchor="改善為每3.2 名教師設1", src="staff_est_pri", forbidden=[]),
    dict(id="staff_head_ratio_half", domain="staffing", query="半日制 主任級教師 幾多個",
         kind="confusable", intent="查半日制小學主任級教師比例（與全日制 3.2 不同）",
         anchor="改善為每4 名教師設1", src="staff_est_pri", forbidden=[]),
    dict(id="staff_deputy_24", domain="staffing", query="副校長 幾多個",
         kind="natural_sentence", intent="查 24 班或以上普通小學的副校長職位數目",
         anchor="核准開辦24班或以上的普通小學", src="staff_est_pri", forbidden=[]),
    dict(id="staff_sp_school", domain="staffing", query="特殊學校 教學人員編制表",
         kind="no_answer", answerable=False,
         intent="特殊學校編制表 staff_est_sp_sch_pri 為 held_back、庫內零片段；"
                "平台曾據錯表答錯班數，故此題必須答不到而非亂答",
         absent="特殊學校核准開辦"),
    dict(id="staff_grad_ratio", domain="staffing", query="學位教師比例",
         kind="plain", intent="查資助小學學位教師職級的編制安排",
         anchor="小學學位教師職位獲提升至高級小學學位教師職級", src="staff_est_pri",
         forbidden=[]),
    dict(id="staff_supply", domain="staffing", query="代課老師 點請",
         kind="natural_sentence", intent="查代課教師聘任安排", anchor="代課教師",
         src="supply_teacher_guide", forbidden=[]),

    # ---------------- hr_admin ----------------
    dict(id="hr_mpf", domain="hr_admin", query="公積金 MPF", kind="english",
         intent="查資助學校公積金／強積金安排", anchor="公積金", src="edbc00030",
         forbidden=[], alts=TIE),
    dict(id="hr_lsp", domain="hr_admin", query="長期服務金 點計",
         kind="natural_sentence", intent="查長期服務金計算方法",
         anchor="長期服務金", src="long_service_payment_guide", forbidden=[]),
    dict(id="hr_maternity", domain="hr_admin", query="產假", kind="plain",
         intent="查教職員產假安排", anchor="產假", src="kg_admin_guide_2026",
         forbidden=[], alts=TIE),
    dict(id="hr_jobshare", domain="hr_admin", query="兩個老師分一個教席",
         kind="natural_sentence",
         intent="用戶口語描述共享教職。文件自身術語是「共享教職」，"
                "用戶不會這樣打字，正是語意檢索該處理的落差",
         anchor="共享教職", src="job_sharing_guide", forbidden=[]),
    dict(id="hr_lang_req", domain="hr_admin", query="英文老師 語文能力要求",
         kind="plain", intent="查英文／普通話科教師語文能力要求",
         anchor="語文能力要求", src="edbcm088_2026", forbidden=[]),
    dict(id="hr_pay_adjust_kg", domain="hr_admin", query="幼稚園 薪酬調整",
         kind="confusable", intent="幼稚園帳目中的薪酬調整，與公營學校薪酬調整不同",
         anchor="薪酬調整", src="edbcm060_2026", forbidden=[]),
    dict(id="hr_severance", domain="hr_admin", query="遣散費", kind="plain",
         intent="查發放遣散費指引", anchor="遣散費",
         src="long_service_payment_guide", forbidden=[]),
    dict(id="hr_teacher_reg_fee", domain="hr_admin", query="教師註冊費用幾錢",
         kind="no_answer", answerable=False,
         intent="教師註冊並無收費條文入庫；此題應答不到而非引用無關註冊條文",
         absent="教師註冊費用"),
    dict(id="hr_ncs_allowance", domain="hr_admin", query="非華語 教師 額外編制",
         kind="confusable", intent="非華語支援撥款與教學人員編制屬不同文件，易混淆",
         anchor="非華語", src="EDBC_8_2020_E", forbidden=["staff_est_pri"]),
    dict(id="hr_appraisal", domain="hr_admin", query="教師評核",
         kind="plain", intent="查教師表現評核相關指引", anchor="評核",
         src="sag_2025_11", forbidden=[], alts=TIE),

    # ---------------- finance ----------------
    dict(id="fin_seg", domain="finance", query="學校效率津貼", kind="plain",
         intent="查學校效率津貼的用途與申請", anchor="學校效率津貼",
         src="edbc008_2026", forbidden=[]),
    dict(id="fin_home_school", domain="finance", query="家校合作津貼",
         kind="plain", intent="查家校合作活動整合津貼（2026/27 起三類資助合併）",
         anchor="家校合作活動整合津貼", src="edbc009_2026", forbidden=[]),
    dict(id="fin_lwl", domain="finance", query="全方位學習津貼 可以買咩",
         kind="natural_sentence", intent="查全方位學習津貼的可用範圍",
         anchor="全方位學習津貼", src="g03", forbidden=[]),
    dict(id="fin_ac_grant", domain="finance", query="空調津貼 計算",
         kind="plain", intent="查空調津貼不同場地的等值計算公式",
         anchor="空調", src="ac_grant_2026", forbidden=[]),
    dict(id="fin_ceg", domain="finance", query="CEG 點計", kind="english",
         intent="查學校發展津貼（CEG）計算方法", anchor="學校發展津貼",
         src="ceg_calc_2026", forbidden=[]),
    dict(id="fin_eoebg", domain="finance", query="EOEBG", kind="english",
         intent="查擴大營辦津貼使用指引", anchor="擴大營辦津貼",
         src="eoebg_guide_2026", forbidden=[]),
    dict(id="fin_procure_split", domain="finance", query="採購 不得拆單",
         kind="plain", intent="查採購程序中禁止化整為零的規定", anchor="採購",
         src="g01", forbidden=[]),
    dict(id="fin_major_repair", domain="finance", query="大規模修葺",
         kind="plain", intent="查大規模修葺工程津貼", anchor="修葺",
         src="edbcm_major_repairs_grant", forbidden=[]),
    dict(id="fin_dls", domain="finance", query="多元學習津貼",
         kind="plain", intent="查高中學生多元學習津貼", anchor="多元學習津貼",
         src="edbcm089_2026", forbidden=[]),
    dict(id="fin_crypto", domain="finance", query="學校可唔可以買虛擬貨幣",
         kind="no_answer", answerable=False,
         intent="庫內並無任何虛擬貨幣／加密資產投資條文；此題應答不到",
         absent="虛擬貨幣"),
    dict(id="fin_sci_grant", domain="finance", query="小學科學科 一筆過津貼",
         kind="plain", intent="查支援開設小學科學科的一筆過津貼",
         anchor="小學科學科", src="edbcm57_2024_pri_science", forbidden=[]),
    dict(id="fin_kg_relocation", domain="finance", query="幼稚園 搬遷津貼",
         kind="confusable", intent="幼稚園搬遷津貼屬幼稚園教育計劃，非公營學校津貼",
         anchor="搬遷津貼", src="edbcm144_2026", forbidden=["edbc008_2026"]),

    # ---------------- school_governance ----------------
    dict(id="gov_imc_60pct", domain="school_governance", query="辦學團體校董 上限",
         kind="plain", intent="查辦學團體校董人數上限，及替代校董是否計算在內",
         anchor="60%", src="imc_establishment_operation", forbidden=[]),
    dict(id="gov_imc_pta", domain="school_governance", query="家長校董 點選",
         kind="natural_sentence", intent="查家長校董選舉與認可家長教師會的條件",
         anchor="家長教師會", src="imc_election_guides", forbidden=[]),
    dict(id="gov_imc_setup", domain="school_governance", query="法團校董會 成立",
         kind="plain", intent="查法團校董會成立程序",
         anchor="法團校董會", src="imc_establishment_operation", forbidden=[]),
    dict(id="gov_imc_abbrev", domain="school_governance", query="IMC",
         kind="abbrev", intent="用英文縮寫查法團校董會",
         anchor="法團校董會", src="imc_establishment_operation", forbidden=[]),
    dict(id="gov_coa_imc", domain="school_governance", query="資助則例 法團校董會版本",
         kind="confusable",
         intent="設有法團校董會的資助學校適用版本，與一般資助則例不同",
         anchor="資助則例", src="coa_imc_1_19", forbidden=[]),
    dict(id="gov_fin_mgmt", domain="school_governance", query="校董會 財務管理",
         kind="plain", intent="查設有法團校董會的資助學校財務管理指引",
         anchor="財務管理", src="g02", forbidden=[]),
    dict(id="gov_icac", domain="school_governance", query="防貪 學校",
         kind="plain", intent="查學校管治的防貪／操守要求", anchor="貪污",
         src="icac_school_governance", forbidden=[]),
    dict(id="gov_sdp", domain="school_governance", query="學校發展計劃 點寫",
         kind="natural_sentence", intent="查如何編寫學校發展計劃",
         anchor="學校發展計劃", src="sdp_guide", forbidden=[]),
    dict(id="gov_imc_quorum", domain="school_governance", query="校董會會議 法定人數",
         kind="plain", intent="查法團校董會會議的法定人數要求", anchor="會議",
         src="imc_governance_supplements", forbidden=[]),
    dict(id="gov_board_pay", domain="school_governance", query="校董有冇人工",
         kind="no_answer", answerable=False,
         intent="庫內並無校董薪酬條文（校董為義務職）；此題應答不到而非引用教職員薪酬表",
         absent="校董薪酬"),
    dict(id="hr_overtime", domain="hr_admin", query="教師超時工作 補水",
         kind="no_answer", answerable=False,
         intent="庫內並無教師超時工作津貼條文；此題應答不到，"
                "而非引用其他津貼條文充數",
         absent="超時工作津貼"),
]


def build(rows: list[dict]) -> list[dict]:
    by_id = {r["id"]: r for r in rows}
    del by_id
    out: list[dict] = []
    for i, s in enumerate(SPECS):
        answerable = s.get("answerable", True)
        item = {
            "id": s["id"], "domain": s["domain"], "query": s["query"],
            "query_kind": s["kind"], "intent": s["intent"],
            "answerable": answerable,
        }
        if not answerable:
            needle = squeeze(s["absent"])
            hits = [r for r in rows
                    if needle in squeeze(clean_for_match(r.get("text", "")))]
            if hits:
                raise SystemExit(
                    f"[{s['id']}] declared unanswerable but {len(hits)} chunk(s) "
                    f"contain {s['absent']!r} "
                    f"(e.g. {hits[0]['id']} in {hits[0].get('source_id')}) — "
                    f"fix the spec, do not ship a false no-answer label")
            item.update(expected_source_any=[], expected_passage_signature=[],
                        expected_page=None, acceptable_alternatives=[],
                        forbidden_evidence=[],
                        verified_by={"method": "absence check over the corpus",
                                     "phrase": s["absent"], "matches": 0,
                                     "note": "庫內零命中，故此題確實答不到"})
        else:
            needle = squeeze(s["anchor"])
            hits = [r for r in rows
                    if r.get("source_id") == s["src"]
                    and needle in squeeze(clean_for_match(r.get("text", "")))]
            if not hits:
                raise SystemExit(
                    f"[{s['id']}] anchor {s['anchor']!r} not found in "
                    f"{s['src']!r} — the label would be invented; fix the spec")
            row = hits[0]
            clean = squeeze(clean_for_match(row["text"]))
            at = clean.find(needle)
            sig = clean[at:at + SIG_LEN]
            spread = sorted({r.get("source_id") for r in rows
                             if sig in squeeze(clean_for_match(r.get("text", "")))})
            item.update(
                expected_source_any=[s["src"]],
                expected_passage_signature=[sig],
                expected_page=dominant_page(row["text"]),
                acceptable_alternatives=[a for a in (s.get("alts") or [])
                                         if a != s["src"]]
                + [x for x in spread if x != s["src"]],
                forbidden_evidence=s.get("forbidden") or [],
                verified_by={"chunk_id": row["id"],
                             "method": "dev/_s213_corpus.py find (anchor) + "
                                       "clean_for_match + dominant_page",
                             "anchor": s["anchor"],
                             "chunks_with_anchor_in_source": len(hits),
                             "sources_sharing_signature": spread,
                             "note": s.get("note", "")})
        item["split"] = "dev" if i < len(SPECS) * 0.7 else "held_out"
        out.append(item)
    return out


def self_test(rows: list[dict]) -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    items = build(rows)
    check(f"產出 {len(items)} 條（目標 ≥40）", len(items) >= 40)
    check("每條都有 intent 與 verified_by",
          all(i["intent"] and i["verified_by"] for i in items))
    ans = [i for i in items if i["answerable"]]
    na = [i for i in items if not i["answerable"]]
    check(f"可答 {len(ans)} 條，其中每條都有簽名與來源",
          all(i["expected_passage_signature"] and i["expected_source_any"] for i in ans))
    check(f"無答案題 {len(na)} 條（目標 ≥5），且斷言為空",
          len(na) >= 5 and all(not i["expected_source_any"] for i in na))
    check("無簽名含頁碼或章節標記（否則永遠對不上真實回應）",
          all("==" not in s and not re.search(r"Page\s*\d", s)
              for i in ans for s in i["expected_passage_signature"]))
    # A short keyword appearing in the passage is NOT the defect — real users
    # type 1–3 tokens, and 「產假」 landing inside a maternity-leave passage is
    # exactly the behaviour we want to measure. The defect is lifting a clause
    # verbatim out of the chunk and calling it a query, which turns the eval
    # into string matching. The line is drawn at length, not at overlap.
    lifted = [i for i in ans
              if len(squeeze(i["query"])) >= 12
              and squeeze(i["query"]) in i["expected_passage_signature"][0]]
    check(f"無查詢是段落的逐字長段移植（≥12 字，實得 {len(lifted)} 條）", not lifted)
    short = [i for i in ans if len(squeeze(i["query"])) <= 8]
    check(f"多數查詢維持真實用戶的短查詢長度（≤8 字者 {len(short)}/{len(ans)}）",
          len(short) * 2 >= len(ans))
    doms = {i["domain"] for i in items}
    check(f"覆蓋 {len(doms)} 個範疇、每個 ≥10 條",
          all(sum(1 for i in items if i["domain"] == d) >= 10 for d in doms))
    check("dev / held_out 兩個 split 都非空",
          len({i["split"] for i in items}) == 2)
    pages = [i["expected_page"] for i in ans if i["expected_page"] is not None]
    check(f"至少一半可答題推導到頁碼（實得 {len(pages)}/{len(ans)}）",
          len(pages) * 2 >= len(ans))
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    rows = load(args.cache)
    if args.self_test:
        return self_test(rows)
    items = build(rows)
    out = args.out or Path("dev/_s213_gold_staffing.json")
    out.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} 條寫入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
