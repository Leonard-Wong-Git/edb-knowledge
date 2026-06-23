#!/usr/bin/env python3
"""ingest_s179_topics.py — S179 discovery 三快贏：新主題 curated chunks（route-independent overlay）.

Discovery agent (S179) found the corpus is curriculum-heavy and missing daily school-admin
/ compliance / pastoral topics. Leonard picked the three quick-wins. These are NOT footnotes
of existing sources — they are KEY load-bearing requirements of NEW topics, crafted as curated
chunks so the route-independent footnote overlay (wikiRepository.searchFootnotes) surfaces them
WITHOUT any backend routing change. content_type=footnote_curated, id=footnote_fn_<fid>,
embed = text + " " + " ".join(keywords). All verbatim-grounded against official EDB PDFs
downloaded this session (dev/_s179_topics/).

  處理學校投訴 (sch_complaint_guide_2023, 處理學校投訴指引 2023) — 3:
    complaint_stages / complaint_review_board / complaint_elements
  校園精神健康 (EDBCM 60/2024 4Rs + 215/2025 三層應急機制) — 3:
    mh_4rs_charter / mh_three_tier / mh_referral_consent
  私隱條例 Cap.486 在校 (pdpo_school_cap486, EDB PDPO note) — 2:
    pdpo_dar_40days / pdpo_minor_access

NOTE: these source_ids are footnote-only (like trg_imc_2023 / subvention_tips) — not added to
source_registry.json; the served-URL monitor still covers their urls (reads wiki_chunks.url).
Deeper full-document ingestion + routing is a follow-up if comprehensive coverage is wanted.

Modes: --self-test (default, NO WRITE) / --execute (INSPECT before/after + INSERT).
Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY from backend/.env.
After --execute: redeploy Render (footnote in-memory cache reload).
"""
import os
import sys
import math
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

COMPLAINT_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/admin/school-complaints/"
                 "Guidelines_for_Handling_School_Complaints_c_Oct_2023.pdf")
MH60_URL = "https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM24060C.pdf"
MH215_URL = "https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM25215C.pdf"
PDPO_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch/"
            "personal-data-ordinace-cap486-note/privacy.pdf")

F = [
    dict(fid="complaint_stages", source_id="sch_complaint_guide_2023",
         title="學校處理投訴指引（2023）", topic="general", url=COMPLAINT_URL,
         text="家長／公眾向學校投訴，學校要點處理？有幾多個階段？《學校處理投訴指引》（2023）："
              "學校須建立校本處理投訴機制；正式調查投訴程序分兩階段——（一）調查階段：委派適當人員調查"
              "及書面回覆投訴人，建議在接獲投訴起計兩個月內完成；（二）上訴階段：投訴人如不接納調查結果，"
              "可在校方覆函發出日期起計十四天內書面提出上訴，由較高職級或另一組別人員處理，建議在接獲"
              "上訴要求起計兩個月內完成。負責調查與上訴的人員須有所不同，上訴階段人員職級原則上應較高。",
         keywords=["學校投訴", "處理投訴", "投訴機制", "校本機制", "調查階段", "上訴階段", "兩個月",
                   "14天", "十四天", "上訴", "投訴人", "書面回覆", "處理投訴指引"],
         q="家長向學校投訴 學校要點處理 調查同上訴幾耐"),

    dict(fid="complaint_review_board", source_id="sch_complaint_guide_2023",
         title="學校處理投訴指引（2023）", topic="general", url=COMPLAINT_URL,
         text="投訴經學校調查同上訴後仍未解決可以點？「學校投訴覆檢委員會」係咩？《學校處理投訴指引》（2023）："
              "獨立覆檢安排只適用於經校本機制調查及上訴程序處理後仍未解決的投訴個案。投訴人、學校或教育局"
              "可在以下情況要求「學校投訴覆檢委員會」覆檢個案：(i)投訴人提出足夠支持理據或新證據，證明學校"
              "及／或教育局處理不當；或(ii)其他指明情況。如覆檢委員會建議個案須重新調查，學校／教育局應"
              "委派高於先前處理人員最少一個職級的人員，並須於兩個月內完成調查及向覆檢委員會書面報告。",
         keywords=["學校投訴覆檢委員會", "覆檢委員會", "覆檢", "投訴未解決", "新證據", "重新調查",
                   "獨立覆檢", "上訴後", "兩個月", "教育局", "處理投訴指引"],
         q="投訴學校後仍未解決 學校投訴覆檢委員會點處理"),

    dict(fid="complaint_elements", source_id="sch_complaint_guide_2023",
         title="學校處理投訴指引（2023）", topic="general", url=COMPLAINT_URL,
         text="學校嘅校本處理投訴機制應該包含咩要素？要唔要向校董會報告投訴情況？《學校處理投訴指引》（2023）："
              "有效的校本機制應包含六項要素——清晰明確、公開透明、簡明易用、公平公正、資料保密、持續完善。"
              "校方應定期檢討校本處理投訴的政策，並向法團校董會報告處理學校投訴的情況（例如投訴／上訴個案"
              "的數據），並在有需要時提出改善措施，以完善校本機制。",
         keywords=["校本投訴機制", "投訴機制要素", "清晰透明", "公平公正", "資料保密", "持續完善",
                   "定期檢討", "向校董會報告", "法團校董會", "投訴數據", "處理投訴指引"],
         q="學校校本投訴機制要有咩要素 要唔要向校董會報告"),

    dict(fid="mh_4rs_charter", source_id="edbcm60_2024_mental_health",
         title="《4Rs 精神健康約章》（教育局通函第60/2024號）", topic="general", url=MH60_URL,
         text="《4Rs精神健康約章》係咩？邊類學校要參加？教育局通函第60/2024號：教育局於2024/25學年推出"
              "《4Rs精神健康約章》，籲請全港公營學校及直接資助計劃（直資）學校參加，並由2024/25學年起"
              "貫徹執行約章內各項推廣學生精神健康的措施，從「普及性」、「選擇性」及「針對性」三個層面"
              "照顧學生精神健康。（4Rs指Rest休息、Relaxation放鬆、Relationship人際關係、Resilience抗逆力。）",
         keywords=["4Rs", "精神健康約章", "校園好精神", "公營學校", "直資學校", "2024/25", "通函60/2024",
                   "學生精神健康", "普及性", "選擇性", "針對性", "心理健康"],
         q="4Rs精神健康約章係咩 邊啲學校要參加"),

    dict(fid="mh_three_tier", source_id="edbcm215_2025_mental_health",
         title="以學校為本的「三層應急機制」（教育局通函第215/2025號）", topic="general", url=MH215_URL,
         text="學校點識別同支援有較高自殺風險嘅學生？「三層應急機制」點分工？教育局通函第215/2025號："
              "政府由2023年12月起透過教育局、醫務衞生局及社會福利署跨部門合作，實施以學校為本的"
              "「三層應急機制」，已在中學恆常化，並擴展至小學四至六年級（高小）試行——第一層：校內跨專業"
              "團隊（輔導主任、教師）及早識別並提供校本支援；第二層：社署組織的「校外支援網絡」提供短期"
              "進一步支援；第三層：學校轉介高自殺風險學生到醫院管理局（醫管局）精神科專科門診服務。",
         keywords=["三層應急機制", "自殺風險", "精神健康", "第一層", "第二層", "第三層", "校外支援網絡",
                   "醫管局", "轉介", "高小", "跨專業團隊", "通函215/2025", "識別支援"],
         q="三層應急機制點分工 學校點支援有自殺風險嘅學生"),

    dict(fid="mh_referral_consent", source_id="edbcm215_2025_mental_health",
         title="以學校為本的「三層應急機制」（教育局通函第215/2025號）", topic="general", url=MH215_URL,
         text="學校經三層應急機制轉介學生，要唔要家長同意？緊急情況點做？教育局通函第215/2025號："
              "第二層轉介至社署「校外支援網絡」時，學校須先取得家長或監護人的同意，並將轉介表格及家長或"
              "監護人同意書一併提交；第三層轉介至醫管局精神科專科門診須由家長陪同並簽發指定校長轉介表格。"
              "教育局設有專為校長而設的電話諮詢熱線（電話 2742 4508）。若學生身體嚴重受傷、有生命危險或"
              "需要即時支援，學校應立即啟動危機處理機制，包括報警求助或將學生送往急症室接受治療。",
         keywords=["三層應急機制", "轉介", "家長同意", "監護人同意", "同意書", "校長轉介表格", "醫管局",
                   "校長熱線", "2742 4508", "危機處理", "報警", "急症室", "通函215/2025"],
         q="三層應急機制轉介學生要唔要家長同意 緊急情況點做"),

    dict(fid="pdpo_dar_40days", source_id="pdpo_school_cap486",
         title="學校與《個人資料（私隱）條例》（第486章）", topic="general", url=PDPO_URL,
         text="有人（家長／學生／教職員）向學校要求查閱或改正個人資料，學校幾耐內要回覆？"
              "《個人資料（私隱）條例》（第486章）學校指引：所有查閱資料要求（DAR）及改正資料要求"
              "均須以書面（中文或英文）提出，口頭要求不獲處理；學校須在40日內遵從要求；如未能（全部或"
              "部分）遵從，須在收到要求後40日內書面告知拒絕理由，並在合理切實可行範圍內盡快遵從。"
              "學校可向要求人收取合理費用。",
         keywords=["私隱條例", "個人資料", "第486章", "Cap.486", "查閱資料要求", "改正資料", "DAR",
                   "40日", "回覆", "書面", "拒絕理由", "收費", "PDPO", "查閱個人資料"],
         q="家長要求查閱學生個人資料 學校幾耐要回覆"),

    dict(fid="pdpo_minor_access", source_id="pdpo_school_cap486",
         title="學校與《個人資料（私隱）條例》（第486章）", topic="general", url=PDPO_URL,
         text="未成年學生嘅個人資料，邊個有權代為查閱／改正？分居又無管養權嘅家長可唔可以攞返子女資料？"
              "《個人資料（私隱）條例》（第486章）學校指引問答：如資料當事人為未成年人（18歲以下），"
              "對該未成年人負有父母責任／管養權（parental responsibility）的人，可代未成年人提出查閱或"
              "改正資料要求。因此，學校可拒絕一名沒有管養權的分居家長查閱其子女資料的要求。",
         keywords=["未成年", "18歲以下", "學生資料", "查閱", "改正", "管養權", "父母責任",
                   "parental responsibility", "分居家長", "拒絕", "私隱條例", "第486章"],
         q="未成年學生個人資料邊個可以查閱 分居無管養權家長可唔可以攞"),
]


def combine(text, kw):
    return text + " " + " ".join(kw)


def cos(a, b):
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return s / (na * nb) if na and nb else 0.0


def load_service_key():
    k = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return k


def headers_svc():
    svc = load_service_key()
    if not svc:
        sys.exit("ERROR: SUPABASE_SERVICE_KEY missing")
    return {"apikey": svc, "Authorization": f"Bearer {svc}", "Content-Type": "application/json"}


def fn_count(h):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&content_type=eq.footnote_curated",
        headers={**h, "Range-Unit": "items", "Range": "0-0", "Prefer": "count=exact"},
        timeout=40,
    )
    return r.headers.get("content-range", "?")


def id_lookup(h, cid):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def build_rows(vectors):
    rows = []
    for e, v in zip(F, vectors):
        rows.append({
            "id": f"footnote_fn_{e['fid']}", "hash": bw.text_hash(e["text"]), "text": e["text"],
            "source_id": e["source_id"], "title": e["title"], "url": e["url"],
            "topic": e["topic"], "content_type": "footnote_curated", "fact_type": "policy",
            "embedding": v,
        })
    return rows


def self_test():
    api = bw.load_api_key()
    ids = [f"footnote_fn_{e['fid']}" for e in F]
    print(f"entries={len(F)} unique_ids={len(set(ids))}")
    fn_vecs = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    q_vecs = bw.embed_batch(api, [e["q"] for e in F])
    print("=== per-entry cosine vs representative query (gate LEAD>=0.45) ===")
    weak = 0
    for e, fv, qv in zip(F, fn_vecs, q_vecs):
        c = cos(fv, qv)
        flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "WEAK")
        if c < 0.45:
            weak += 1
        print(f"  {c:.3f} [{flag:5}] {e['fid']}")
    print(f"=== {len(F)-weak}/{len(F)} >= 0.45 lead ===")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    for e in F:
        cid = f"footnote_fn_{e['fid']}"
        print(f"  id {cid} ->", id_lookup(h, cid))
    vectors = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    rows = build_rows(vectors)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=rows, timeout=180)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    missing = [f"footnote_fn_{e['fid']}" for e in F if not id_lookup(h, f"footnote_fn_{e['fid']}")]
    print("  missing after insert:", missing or "none")


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
