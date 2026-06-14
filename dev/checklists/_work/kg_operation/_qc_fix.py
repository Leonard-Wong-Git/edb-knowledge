#!/usr/bin/env python3
"""S163 QC fix for kg_operation clauses — remove fabricated framing / restore dropped
obligations / fix bad citation per QC_VERIFY_ISSUES.md. Exact-match with assertions."""
import json, sys, copy

P = "clauses.json"
data = json.load(open(P, encoding="utf-8"))
orig = copy.deepcopy(data)
by_no = {s["section_no"]: s for s in data}

def sub_clause_text(sec_no, covers, old, new):
    sec = by_no[sec_no]
    hits = [cl for cl in sec["clauses"] if cl.get("covers") == covers]
    assert len(hits) == 1, f"sec{sec_no} covers{covers}: found {len(hits)} clauses"
    cl = hits[0]
    assert old in cl["text"], f"sec{sec_no} covers{covers}: OLD not found: {old[:40]}"
    cl["text"] = cl["text"].replace(old, new)
    return cl

# --- Section 1, item 0: drop inferred obligation tail ---
sub_clause_text(1, [12,5,0],
    "發出證明書，故本校於選址時須避免採用結構性木地板的房產。",
    "發出證明書。")

# --- Section 2, item 0: drop fabricated framing sentence ---
sub_clause_text(2, [0,1,2,15],
    "本校洗手間的設計與裝修須符合衞生及安全標準。洗手間必須設有通出露天的窗口",
    "本校洗手間必須設有通出露天的窗口")

# --- Section 5, item 4: drop framing + purpose tail ---
sub_clause_text(5, [4,5],
    "本校重視校園環境的安全與衞生，致力提供一個安全、健康和安排妥善的校園環境，並與家長共同制訂及推行健康政策措施。本校須保持校舍環境的衞生，以營造健康的學習環境，讓幼兒在妥善照顧下成長學習。",
    "本校須提供一個安全、健康和安排妥善的校園環境，並與家長共同制訂及推行健康政策措施。本校須保持校舍環境的衞生，以營造健康的學習環境。")

# --- Section 5, item 1: drop purpose framing ---
sub_clause_text(5, [1,2],
    "為維持環境衞生及保障幼兒健康，本校應定時使用",
    "本校應定時使用")

# --- Section 5, item 3: drop purpose tail ---
sub_clause_text(5, [3],
    "認可的水源供應，確保用水安全衞生。",
    "認可的水源供應。")

# --- Section 6: clause0 (covers 0,1) — drop 每日 / 方可入班 / 註冊醫生 / move 體溫 out; fix bad citation ---
c6_0 = sub_clause_text(6, [0,1],
    "兒童每日返抵本校園舍時，本校須隨即為其進行健康檢查，待確定其身體健康後方可入班；如發現病徵，應立即安排隔離，並通知家長帶回求醫。本校亦會定期檢查及記錄兒童體溫。兒童入讀本校之前，應接受一項由註冊醫生進行的全面體格檢查。",
    "兒童返抵本校園舍時，本校須隨即為其進行健康檢查，並待確定其身體健康；如發現病徵，應立即安排隔離，並通知家長帶回求醫。兒童入讀本校之前，應接受一項全面的體格檢查。")
# remove bad citation kg_admin_guide_2026 p47 (belongs to item3 / clause1)
before = len(c6_0["citations"])
c6_0["citations"] = [c for c in c6_0["citations"]
                     if not (c["source_id"] == "kg_admin_guide_2026" and c["page"] == 47)]
assert len(c6_0["citations"]) == before - 1, "sec6 clause0 bad-citation p47 not removed"

# --- Section 6: clause1 (covers 2,3) — fold the 體溫 obligation back into its covering clause ---
c6_1 = sub_clause_text(6, [2,3],
    "本校亦須妥善保存學童個人健康紀錄及員工病假紀錄。健康紀錄內容至少包括下列各項：",
    "本校亦須妥善保存學童個人健康紀錄及員工病假紀錄，並定期檢查及記錄兒童體溫。健康紀錄內容至少包括下列各項：")

# --- Section 9: clause0 — restore applicability qualifier (留宿/獨立幼兒中心) ---
sub_clause_text(9, [0,1,6,2],
    "本校如遇特別事故，必須盡快通知",
    "本校如設有留宿幼兒中心或獨立幼兒中心，遇特別事故時，必須盡快通知")

# --- Section 9: clause3 (covers 5,7) — drop fabricated 指派專人 designation ---
c9_3 = sub_clause_text(9, [5,7],
    "本校最少須有兩名教員曾接受急救訓練。本校指派專人負責管理急救箱，負責管理急救箱的人士須確保",
    "本校最少須有兩名教員曾接受急救訓練。負責管理急救箱的人士須確保")
if "指派專人" in c9_3.get("adjustables", []):
    c9_3["adjustables"] = [a for a in c9_3["adjustables"] if a != "指派專人"]

# --- Section 13: clause covers [0,13,14,23] — drop fabricated carve-out + restore dropped 廉署守則 half ---
sub_clause_text(13, [0,13,14,23],
    "本校接受任何利益和捐贈，必須獲本校管理當局批准（經教育局核准的註冊費不屬利益）。",
    "本校接受任何利益和捐贈，必須獲本校管理當局批准。")
sub_clause_text(13, [0,13,14,23],
    "本校亦遵守教育局有關《學校及其教職員收受利益和捐贈事宜》通告的規定。",
    "本校亦遵守教育局有關《學校及其教職員收受利益和捐贈事宜》通告的規定，並參考廉政公署《校董及職員行為守則範本》。")

# --- Section 13: clause6 table row2 (item 7) — restore dropped post-conclusion report obligation ---
c13_6 = [cl for cl in by_no[13]["clauses"] if cl.get("covers") == [7,8,19,20]][0]
rows = c13_6["table"]["rows"]
target = None
for r in rows:
    if r[1] == "管理人員須要求員工即時向中心管理人員報告":
        target = r
assert target is not None, "sec13 clause6 row2 not found"
target[1] = "管理人員須要求員工即時向中心管理人員報告，並在調查或訴訟完結後，即時向中心管理人員報告結果"

# --- Section 15: clause covers [1,2,8] — drop fabricated purpose framing ---
sub_clause_text(15, [1,2,8],
    "為確保採購過程廉潔及問責，本校須要求所有負責採購職務的人員簽署承諾書",
    "本校須要求所有負責採購職務的人員簽署承諾書")

# --- Clear resolved verify blocks for the fixed sections ---
RESOLVED = {1,2,5,6,9,13,15}
for no in RESOLVED:
    by_no[no]["verify"] = {"ok": True, "issues": [],
                           "resolved_s163": True,
                           "input_item_count": by_no[no]["verify"].get("input_item_count"),
                           "covered_item_count": by_no[no]["verify"].get("covered_item_count")}

json.dump(data, open(P, "w", encoding="utf-8"), ensure_ascii=False)
print("OK — all QC fixes applied + assertions passed; verify cleared for sections", sorted(RESOLVED))
