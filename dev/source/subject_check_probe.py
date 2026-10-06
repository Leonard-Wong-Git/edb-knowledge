#!/usr/bin/env python3
"""subject_check_probe.py — 路線乙：問題對象 vs 資料對象的決定性核對（S235，只離線量度）

病徵（D01）：問「學生請病假要唔要交醫生紙」，窗內五段全部是教職員病假規則，
判官答「能」，合成器第一句便寫「學生請病假需要提交有效的醫生證明書」。
換判官提示與換判官模型都已證修不了（S202、S211、S230）。

本檔量度一個不靠模型的檢查（presence 版）：
  1. 用詞表找出問題問的是哪一類人（學生／家長／教師／校長／非教學人員／校董）；
  2. 窗內五段之中，只要有一段提到該類人（含同義詞）即通過；
  3. 問題提到的每一類人都要通過，否則判為「對象不在窗內」。
問題沒有提到任何一類人時不作判斷（直接通過）。

另附 cooccur 版（對象詞與問題詞須在同一句出現），S235 實測對 gold 誤報 9／50，
只作對照，不建議採用。

用法：
    python3 dev/source/subject_check_probe.py --self-test
    python3 dev/source/subject_check_probe.py --cached          # 驗收集 35 + fresh 10 的緩存窗
    python3 dev/source/subject_check_probe.py --gold dev/source/eval_runs/2026-09-28_s233_prod_gold.json
        # 以 backend/.env 的 service key 唯讀取回各題前五段全文（只 GET，不寫入）

本檔不改生產、不呼叫任何模型。設計與結論見 dev/source/SUBJECT_CHECK_DESIGN.md。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CHUNKS_URL = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/wiki_chunks"

# q   = 在問題中出現即視為問及該類人
# sat = 在窗內片段中出現即視為資料涉及該類人（教師／非教學人員接受泛稱「員工」「僱員」「教職員」）
GROUPS: dict[str, dict[str, list[str]]] = {
    "STUDENT": {"q": ["學生", "學童", "同學", "幼兒", "小朋友", "兒童"],
                "sat": ["學生", "學童", "同學", "幼兒", "小朋友", "兒童"]},
    "PARENT": {"q": ["家長"], "sat": ["家長", "父母", "監護人"]},
    "TEACHER": {"q": ["教師", "老師", "教學人員", "教員", "代課"],
                "sat": ["教師", "老師", "教學人員", "教員", "代課", "教職員", "員工", "僱員"]},
    "PRINCIPAL": {"q": ["校長"], "sat": ["校長"]},
    "NONTEACH": {"q": ["非教學人員", "職員", "工友", "校工", "文員", "技術員"],
                 "sat": ["非教學人員", "職員", "工友", "校工", "文員", "技術員", "教職員", "員工", "僱員"]},
    "DIRECTOR": {"q": ["校董"], "sat": ["校董"]},
}
# v2（S235）：問題提到更具體的角色時，窗內必須出現該角色本身（或其同義詞），
# 一般類別（教師／家長）出現不算數。這一規則在讀新驗證題集之前寫好並凍結。
SPECIFIC: dict[str, list[str]] = {
    "實習教師": ["實習"], "實習老師": ["實習"], "師訓學生": ["實習", "師訓"],
    "義工": ["義工", "志願"], "志願人員": ["義工", "志願"],
    "代課": ["代課", "代職"], "臨時教師": ["臨時教師", "臨時"], "兼職": ["兼職"],
    "副校長": ["副校長"], "校監": ["校監"],
    "家長校董": ["家長校董"], "教員校董": ["教員校董"], "校友校董": ["校友校董"], "獨立校董": ["獨立校董"],
    "教學助理": ["教學助理", "教師助理"], "教師助理": ["教學助理", "教師助理"],
    "社工": ["社工", "社會工作"], "保母": ["保母", "保姆", "護送"], "司機": ["司機"],
    "宿舍家長": ["宿舍家長"], "外籍英語教師": ["外籍英語", "NET"],
}
STOP = set("嘅咗喺啲係唔要有冇幾多點樣可以甚麼什麼是否需要嗎呢的了和及或與在把被就都也還")
SENT = re.compile(r"[。；;！？\n]")


def fold(s: str | None) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s or ""))


def _mask(text: str, group: str) -> str:
    # 「非教學人員」內含「教學人員」，查教師時先遮走，免得非教學人員的片段冒充教師
    return text.replace("非教學人員", "") if group == "TEACHER" else text


def question_subjects(query: str) -> list[str]:
    # 問題保留空格：「小學 生涯規劃」去空格後會變出「學生」（S235 審核發現）
    q = unicodedata.normalize("NFKC", query or "")
    return [g for g, d in GROUPS.items() if any(t in _mask(q, g) for t in d["q"])]


def window_mentions(texts: list[str], group: str) -> bool:
    return any(any(t in _mask(fold(x), group) for t in GROUPS[group]["sat"]) for x in texts)


def _matter_bigrams(query: str, groups: list[str]) -> set[str]:
    q = fold(query)
    for g in groups:
        for t in sorted(GROUPS[g]["q"], key=len, reverse=True):
            q = q.replace(t, " ")
    s = "".join(ch if ("一" <= ch <= "鿿" and ch not in STOP) else " " for ch in q)
    return {s[i:i + 2] for i in range(len(s) - 1) if " " not in s[i:i + 2]}


def _cooccur(texts: list[str], group: str, matter: set[str]) -> bool:
    for x in texts:
        for sent in SENT.split(fold(x)):
            if any(t in _mask(sent, group) for t in GROUPS[group]["sat"]) and any(b in sent for b in matter):
                return True
    return False


def question_specifics(query: str) -> list[str]:
    q = unicodedata.normalize("NFKC", query or "")
    found = [k for k in SPECIFIC if k in q]
    # 只留最長的：「家長校董」已含「校董」意思，不再另查較短的詞
    return [k for k in found if not any(k != o and k in o for o in found)]


def check(query: str, texts: list[str]) -> dict:
    groups = question_subjects(query)
    specifics = question_specifics(query)
    folded = [fold(x) for x in texts]
    spec_missing = [k for k in specifics if not any(any(t in x for t in SPECIFIC[k]) for x in folded)]
    if not groups:
        return {"subjects": [], "specifics": specifics, "missing": spec_missing,
                "presence_v1_pass": True, "presence_pass": not spec_missing, "cooccur_pass": True}
    missing = [g for g in groups if not window_mentions(texts, g)]
    matter = _matter_bigrams(query, groups)
    return {"subjects": groups, "specifics": specifics, "missing": missing + spec_missing,
            "presence_v1_pass": not missing, "presence_pass": not missing and not spec_missing,
            "cooccur_pass": all(_cooccur(texts, g, matter) for g in groups)}


# ── data loaders ─────────────────────────────────────────────────────────────
def _texts(items) -> list[str]:
    return [x if isinstance(x, str) else (x or {}).get("text", "") for x in items]


def cached_rows() -> list[dict]:
    rows = []
    for cases_f, cache_f in [("judge_acceptance_cases.json", "judge_runs/chunks_cache.json"),
                             ("judge_transplant_fresh_s202.json", "judge_runs/chunks_cache_fresh_s202.json")]:
        cases = json.loads((HERE / cases_f).read_text(encoding="utf-8"))["cases"]
        cache = json.loads((HERE / cache_f).read_text(encoding="utf-8"))
        for c in cases:
            rows.append({"id": c["id"], "query": c["query"], "want": c["want"],
                         "texts": _texts(cache.get(c["id"], {}).get("chunks", []))})
    return rows


def _service_key() -> str:
    for line in (ROOT / "backend" / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("SUPABASE_SERVICE_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("backend/.env 沒有 SUPABASE_SERVICE_KEY")


def gold_rows(run_path: str) -> list[dict]:
    run = json.loads(pathlib.Path(run_path).read_text(encoding="utf-8"))
    rows = [{"id": r["id"], "query": r["query"], "ids": list(r["chunk_ids"])[:5]}
            for r in run["results"] if "chunk_ids" in r]
    key, texts = _service_key(), {}
    wanted = sorted({i for r in rows for i in r["ids"]})
    for i in range(0, len(wanted), 40):
        flt = "in.(" + ",".join(f'"{x}"' for x in wanted[i:i + 40]) + ")"
        url = f"{CHUNKS_URL}?select=id,text&id={urllib.parse.quote(flt)}"
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    texts.update({c["id"]: c["text"] for c in json.load(resp)})
                break
            except Exception as exc:  # noqa: BLE001 — retried, then reported
                if attempt == 3:
                    raise RuntimeError(f"讀取片段失敗：{exc}") from exc
                time.sleep(3 * (attempt + 1))
    missing = [i for i in wanted if i not in texts]
    if missing:
        print(f"⚠️ {len(missing)} 個片段已不在庫內（窗口內容與當日不同）", file=sys.stderr)
    for r in rows:
        r["texts"] = [texts.get(i, "") for i in r["ids"]]
    return rows


# ── reports ──────────────────────────────────────────────────────────────────
def report(rows: list[dict], label: str) -> None:
    subj = [(r, check(r["query"], r["texts"])) for r in rows]
    subj = [(r, c) for r, c in subj if c["subjects"] or c["specifics"]]
    pf = [(r, c) for r, c in subj if not c["presence_pass"]]
    cf = [(r, c) for r, c in subj if not c["cooccur_pass"]]
    print(f"[{label}] 共 {len(rows)} 題；問題帶對象 {len(subj)} 題；presence 攔下 {len(pf)}；cooccur 攔下 {len(cf)}")
    for r, c in pf:
        print(f"  presence ✋ {r['id']}  want={r.get('want', '-')}  {r['query']}  缺：{','.join(c['missing'])}")
    for r, c in cf:
        if c["presence_pass"]:
            print(f"  cooccur  ✋ {r['id']}  want={r.get('want', '-')}  {r['query']}")


def self_test() -> int:
    failures = []

    def expect(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)

    staff = ["僱員如申請病假超逾兩天，必須出示有效的醫生證明書。", "月薪教學及非教學人員病假：首年28天。"]
    expect(question_subjects("學生請病假要唔要交醫生紙") == ["STUDENT"], "學生問題應判為 STUDENT")
    expect(question_subjects("小學 生涯規劃") == [], "跨空格不應拼出「學生」")
    expect(not check("家長義工要唔要做查核", ["如有關學生的家長提出查閱資料"])["presence_pass"],
           "v2：問家長義工，窗內只有一般家長，應攔下")
    expect(not check("實習教師有冇病假", ["常額教師首年可享28天病假"])["presence_pass"],
           "v2：問實習教師，窗內只有常額教師，應攔下")
    expect(check("家長校董任期幾耐", ["家長校董的任期為兩年"])["presence_pass"], "v2：家長校董在窗內應通過")
    expect(question_specifics("家長校董任期幾耐") == ["家長校董"], "v2：只取最長的具體角色")
    expect(not check("學生請病假要唔要交醫生紙", staff)["presence_pass"], "D01 型：窗內無學生應攔下")
    expect(check("老師請病假要唔要交醫生紙", staff)["presence_pass"], "教師對照：員工／僱員應算教師")
    expect(question_subjects("非教學人員產假有幾多日") == ["NONTEACH"], "非教學人員不應同時判為教師")
    expect(not check("老師有幾多日病假", ["非教學人員病假首年28天。"])["presence_pass"],
           "只有非教學人員的窗不應冒充教師")
    expect(check("法團校董會校董有冇薪酬", ["法團校董會不得向任何校董提供任何酬勞。"])["presence_pass"],
           "校董問題、窗內有校董應通過")
    expect(check("幼稚園每班師生比例係幾多", [])["subjects"] == [], "無對象詞的問題不作判斷")
    expect(check("學生請病假要唔要交醫生紙", ["學童缺課須由家長通知學校。"])["presence_pass"],
           "同義詞「學童」應算學生")
    # 真實緩存窗：D01 必須攔下；所有 want=能 的題目必須一題不攔
    rows = cached_rows()
    by_id = {r["id"]: r for r in rows}
    expect(not check(by_id["D01_student_sickleave"]["query"], by_id["D01_student_sickleave"]["texts"])["presence_pass"],
           "緩存 D01 應攔下")
    wrong = [r["id"] for r in rows if r["want"] == "能" and not check(r["query"], r["texts"])["presence_pass"]]
    expect(not wrong, f"want=能 的題目被攔：{wrong}")
    for f in failures:
        print("FAIL", f)
    print(f"self-test：{'全部通過' if not failures else f'{len(failures)} 項失敗'}")
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--cached", action="store_true", help="驗收集與 fresh 集的緩存窗（離線）")
    p.add_argument("--gold", metavar="RUN_JSON", help="gold 運行檔；唯讀取回片段全文")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if a.cached:
        report(cached_rows(), "緩存驗收窗")
    if a.gold:
        report(gold_rows(a.gold), "gold")
    if not (a.cached or a.gold):
        p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
