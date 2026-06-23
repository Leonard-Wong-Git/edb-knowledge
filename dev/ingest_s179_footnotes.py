#!/usr/bin/env python3
"""ingest_s179_footnotes.py — S179 footnote 擴充 (附件細字/附錄 footnote 第三批) + forms 手尾.

14 curated footnotes, all verbatim-verified this session against the official source
(vault repaged extract for SAG/IMC/KG/activities; freshly-downloaded EN PDF for CEG/CFEG):

  SAG 學校行政手冊 (sag_2025_11, SAG_C_markup.pdf) — 8:
    sag_select_committee p189 / sag_medical_exam p191 / sag_surplus_redeploy p218 /
    sag_rank_conversion p220 / sag_sick_leave p224 / sag_tb_leave p226 /
    sag_paternity_maternity p226 / sag_annual_urgent_leave p228
  imc_tax_exempt_s88   (imc_establishment_operation p31)
  kgadmin_rent_sept    (kg_admin_guide_2026 p57)
  kgop_teacher_onduty  (kg_operation_manual_2026 p148)
  activities_ratios    (sch_activities_guide p63-64)
  forms 手尾 (S177 第二批剩餘):
    ceg_plan_clawback  (#7, CEG Ground Rules and Procedures — clawed back if not uploaded by end-Oct)
    cfeg_no_item_cap   (#18, CFEG User Guide Part I(b) — "no financial limit for F&E items")

Same mechanism as ingest_tips_footnotes.py / forms_ingest.py: content_type=footnote_curated,
route-independent overlay (wikiRepository.searchFootnotes), id=footnote_fn_<fid>,
embed = text + " " + " ".join(keywords).

Modes:
  --self-test (default): embed each + cosine vs representative query (gate LEAD>=0.45) +
                         dup-id check + collision check vs live footnote_curated ids. NO WRITE.
  --execute            : INSPECT before (count + per-id collision) + batch INSERT
                         (merge-duplicates upsert) + INSPECT after.

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
NOTE: after --execute, restart/redeploy Render (footnote in-memory cache, invalidateFootnoteCache).
"""
import os
import sys
import math
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw  # canonical embed + hash

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

SAG_URL = "https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/sch-admin-guide/SAG_C_markup.pdf"
KGADMIN_URL = ("https://www.edb.gov.hk/attachment/tc/edu-system/preprimary-kindergarten/"
               "free-quality-kg-edu/KG%20Admin%20Guide_Chi_2026_May.pdf")
KGOP_URL = ("https://www.edb.gov.hk/attachment/tc/edu-system/preprimary-kindergarten/overview/"
            "Operation_manual_%20(Chi)_May%202026_Version%204.3.pdf")
IMC_URL = ("https://sbm.edb.gov.hk/uploads/attachment/tc/sch-admin/sbm/sbm-forms-references/"
           "imc-establishment-operation_chi_25.3.2014.pdf")
ACT_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/admin/about-activities/"
           "sch-activities-guidelines/Outdoor_TC.pdf")
CEG_GR_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/subsidy-info/"
              "ref-capacity-enhancement-grant/Ground%20Rules%20and%20Procedures_en.pdf")
CFEG_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/subsidy-info/"
            "ref-e-oebg-cfeg/User%20Guide_CFEG_e.pdf")

# each = dict(fid, source_id, title, topic, url, text, keywords, q)
F = [
    dict(fid="sag_select_committee", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=189",
         text="未成立法團校董會的資助學校，遴選委員會（招聘／甄選委員會）點組成？辦學團體代表可以佔幾多？"
              "《學校行政手冊》7.3.2 遴選委員會（註）：仍未成立法團校董會的學校，其遴選委員會的成員應包括"
              "辦學團體代表（不超過委員會成員人數的60%）及獨立人士；獨立人士中應盡量包括家長及／或校友，"
              "並不應為有關校董會、同一辦學團體轄下學校校董會或法團校董會的校董，或辦學團體的成員。",
         keywords=["遴選委員會", "招聘委員會", "甄選委員會", "委員會組成", "辦學團體代表", "60%", "六成",
                   "獨立人士", "家長", "校友", "未成立法團校董會", "聘任", "學校行政手冊"],
         q="未成立法團校董會 遴選委員會點組成 辦學團體代表佔幾多"),

    dict(fid="sag_medical_exam", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=191",
         text="教職員受聘前使唔使驗身／照肺（胸肺X光）？《學校行政手冊》7.4.1 體格檢驗：每名教職員"
              "（按日薪聘用的代職人員除外）在受聘前，均須由註冊醫生進行體格檢驗，包括胸肺X光檢查；"
              "在職檢定教師在資助學校之間轉職而期間並無中止服務，則不受此限。校董會可根據《資助則例》及"
              "「學校員工的體格檢驗及健康狀況」豁免入職前胸肺X光檢查；已成立法團校董會的學校，"
              "由法團校董會按《資助學校資助則例》決定是否規定。",
         keywords=["體格檢驗", "驗身", "身體檢查", "胸肺X光", "照肺", "受聘前", "入職前", "註冊醫生",
                   "教職員", "豁免", "資助則例", "學校行政手冊"],
         q="教職員受聘前要唔要驗身照肺 胸肺X光"),

    dict(fid="sag_surplus_redeploy", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=218",
         text="營辦多過一間資助小學的辦學團體，超額主任／校長空缺點處理？可唔可以跨屬校調配抵銷超額？"
              "《學校行政手冊》附錄5 員工晉升及署任安排（註）：營辦超逾一所資助小學的辦學團體，其屬校的"
              "主任級教師／校長空缺須用作處理超額主任／高於核准職級校長的調配之用；如有充分理由，亦可以"
              "一所屬校的主任級教師實缺／校長職級，抵銷另一所屬校的超額主任級教師／超出核准編制職級的校長"
              "（詳見教育局通函第26/2025號）。署任期一般不少於30天。",
         keywords=["超額主任", "超額教師", "辦學團體", "多於一所小學", "屬校", "跨校調配", "抵銷超額",
                   "主任級教師", "校長空缺", "署任", "30天", "通函26/2025", "學校行政手冊"],
         q="辦學團體營辦多間小學 超額主任空缺可唔可以跨屬校抵銷調配"),

    dict(fid="sag_rank_conversion", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=220",
         text="在職非學位教師改編入學位教師職系（改編職系）要點做？要校董會通過咩？有冇限期？"
              "《學校行政手冊》附錄6（註）：學校決定將現職教師改編為學位教師，須充分諮詢校內所有教師、"
              "預先訂立一套客觀、公平和具透明度的校本政策，並獲校董會通過及讓全體教師知悉，"
              "並遵照教育局通告第11/2019號「資助學校教師職位全面學位化」的原則及規定。一般情況下"
              "改編職系生效日期不具追溯效力；現職持認可學位資歷的常額非學位教師如欲改編，"
              "須於每年5月31日或之前向學校表示下一學年的改編意願。",
         keywords=["改編職系", "改編學位教師", "非學位教師", "學位教師職系", "教師職位學位化",
                   "通告11/2019", "校本政策", "校董會通過", "5月31日", "追溯", "學校行政手冊"],
         q="非學位教師改編做學位教師職系點做 要校董會通過咩 幾時截止"),

    dict(fid="sag_sick_leave", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=224",
         text="資助學校教師同非教學人員有幾多病假？可以累積幾多日？《學校行政手冊》附錄9 假期：月薪教學人員"
              "首年受聘享有28天病假，其後每服務滿一年可享全年共48天病假，有薪病假最高可累積至168天；"
              "病假最少以半天為放取單位，申請病假超逾兩天必須出示有效的醫生證明書。按連續性合約受聘的"
              "非教學專責人員／實驗室技術員／學校行政主任，聘用首12個月內每服務滿一個月可享2天病假、"
              "其後每滿一個月可享4天病假，有薪病假最高可累積至120天。",
         keywords=["病假", "sick leave", "幾多病假", "28天", "48天", "168天", "累積病假", "教師病假",
                   "非教學人員", "醫生證明書", "半天", "學校行政手冊", "附錄9"],
         q="資助學校教師有幾多病假 可以累積幾多日"),

    dict(fid="sag_tb_leave", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=226",
         text="資助學校員工嘅「肺病特別假期」有幾耐？點計？《學校行政手冊》附錄9 批准有薪肺病特別假期的條件："
              "服務超過1年但少於4年——最多可給予3個月假期；服務滿4年或以上但少於8年——最多可給予6個月假期；"
              "服務滿8年或以上——可獲假期6個月，另加服務滿8年後服務每超過1年可獲假期兩星期，"
              "最多計算至12個月為止。僱員出示有效醫生證明書可在限額內獲批全薪；肺病特別假期及積存病假"
              "均用罄後，可獲批無薪肺病特別假期。",
         keywords=["肺病特別假期", "肺病假", "結核病假", "TB", "有薪假", "3個月", "6個月", "12個月",
                   "服務年資", "員工假期", "學校行政手冊", "附錄9"],
         q="肺病特別假期有幾耐 服務幾年攞幾多個月"),

    dict(fid="sag_paternity_maternity", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=226",
         text="資助學校男教職員有幾多侍產假？產假又有幾耐？《學校行政手冊》附錄9：合資格男性僱員"
              "（緊接放取侍產假前已連續服務達40個星期）在每次子女出生時最高可獲批5個工作天的全薪侍產假，"
              "須於嬰兒預計出生日期前4星期至實際出生日期當日起計的14星期內放取，可一次過或以半天為單位放取，"
              "未放取的不可折算現金或保留（詳見教育局通告第16/2015號）。產假方面，以薪金津貼支薪的教師"
              "可享有14個星期有薪產假。",
         keywords=["侍產假", "產假", "男教師侍產假", "5天", "5個工作天", "14星期", "40星期",
                   "通告16/2015", "全薪", "學校行政手冊", "附錄9"],
         q="男教職員有幾多日侍產假 產假幾耐"),

    dict(fid="sag_annual_urgent_leave", source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=228",
         text="資助學校非教學人員嘅年假同緊急私事假點計？《學校行政手冊》附錄9：按連續性合約工作每12個月"
              "可享有薪年假——服務滿1年至2年享7天有薪年假，其後每多服務1年可多獲1天，有薪年假最高可累積至"
              "14天（教學人員一般可享學校假期、假期不可累積）。特別有薪假期方面：可因重要的緊急私事放假，"
              "每學年最多2天，假期不可累積。",
         keywords=["年假", "annual leave", "有薪年假", "7天", "14天", "緊急私事假", "特別有薪假期",
                   "每學年2天", "非教學人員", "累積", "學校行政手冊", "附錄9"],
         q="非教學人員有幾多年假 緊急私事假每年幾多日"),

    dict(fid="imc_tax_exempt_s88", source_id="imc_establishment_operation",
         title="法團校董會的成立與運作", topic="general", url=f"{IMC_URL}#page=31",
         text="法團校董會學校想申請免稅（慈善團體免稅地位）要點做？《法團校董會的成立與運作》章程樣本（註）："
              "如設立法團校董會的學校欲向稅務局申請根據《稅務條例》第88條豁免繳稅，其法團校董會章程必須"
              "包括相關條文（例如指明法團校董會清盤／解散時，剩餘財產須轉予其他獲豁免繳稅的慈善機構等）。",
         keywords=["免稅", "豁免繳稅", "稅務條例第88條", "s.88", "慈善團體", "法團校董會章程", "稅務局",
                   "清盤", "解散", "法團校董會", "成立與運作"],
         q="法團校董會學校申請免稅 稅務條例88條 章程要寫咩"),

    dict(fid="kgadmin_rent_sept", source_id="kg_admin_guide_2026", title="幼稚園行政手冊",
         topic="general", url=f"{KGADMIN_URL}#page=57",
         text="幼稚園嘅租金資助額點計？用邊個月嘅學生人數做基準？《幼稚園行政手冊》（註）："
              "租金資助額以有關學年九月的錄取學生人數計算。（配合學費調整：幼稚園申請調整有關學年學費時"
              "提交的預算收生資料，須與此一致。）",
         keywords=["幼稚園", "租金資助", "租金資助額", "點計", "九月", "錄取學生人數", "收生人數",
                   "計算基準", "幼稚園行政手冊"],
         q="幼稚園租金資助額點計 用幾月學生人數"),

    dict(fid="kgop_teacher_onduty", source_id="kg_operation_manual_2026", title="學前機構辦學手冊",
         topic="general", url=f"{KGOP_URL}#page=148",
         text="幼稚園每班最少要有幾多位教師當值？《學前機構辦學手冊》附20（註）：每班最少須有一位教師當值。",
         keywords=["幼稚園", "每班", "最少", "一位教師", "教師當值", "當值", "班級", "師生比例",
                   "學前機構辦學手冊", "人手"],
         q="幼稚園每班最少要幾多位教師當值"),

    dict(fid="activities_ratios", source_id="sch_activities_guide",
         title="學校活動指引(戶外活動/境外遊學團)", topic="activity", url=f"{ACT_URL}#page=63",
         text="學校舉辦戶外活動嘅建議師生比例（一名領隊／教師對幾多學生）係幾多？《學校活動指引》"
              "各項戶外活動的建議師生比例：遠足／遠征訓練／野外露營 1:10；宿營 1:30；野外定向 1:8；"
              "單車旅行 1:5；實地／野外研習 1:18；滑浪風帆 1名持有有效資格人士:5名參加者（12歲或以下 1:4）；"
              "獨木舟 1:8（8至12歲 1:6）。遠足／遠征／露營等最少要由2名領隊帶領，其中1名應為學校教師／導師。",
         keywords=["戶外活動", "師生比例", "領隊", "遠足", "1:10", "遠征", "露營", "宿營", "1:30",
                   "野外定向", "1:8", "單車旅行", "滑浪風帆", "1:5", "獨木舟", "實地研習",
                   "學校活動指引", "安全"],
         q="戶外活動建議師生比例 遠足 露營 一個領隊帶幾多學生"),

    dict(fid="ceg_plan_clawback", source_id="ceg_calc_2026",
         title="學校發展津貼（CEG）基本規則及程序", topic="general", url=CEG_GR_URL,
         text="學校發展津貼（CEG）計劃書有冇限期？唔交或者唔上載會點？《學校發展津貼基本規則及程序》："
              "學校須按擬定周年學校計劃的一般規定擬備CEG計劃，並在經法團校董會／學校管理委員會（IMC／SMC）"
              "通過後，於每年10月底前上載學校網頁；經通過的CEG計劃亦須於每年10月底前送交教育主任"
              "（學位分配及支援）。學校如未能符合上述規定，CEG會被追回（clawed back）。"
              "（CEG使用報告亦須納入周年學校報告，並於每年11月底前上載學校網頁。）",
         keywords=["學校發展津貼", "CEG", "計劃書", "CEG plan", "10月底", "上載網頁", "IMC", "SMC",
                   "校董會通過", "追回", "clawed back", "claw back", "11月底", "周年計劃"],
         q="CEG計劃幾時要交 唔上載會唔會被追回"),

    dict(fid="cfeg_no_item_cap", source_id="cfeg_guide_2026",
         title="綜合家具及設備津貼（CFEG）使用指引", topic="general", url=CFEG_URL,
         text="用綜合家具及設備津貼（CFEG）買家具設備，個別項目有冇金額上限？"
              "《綜合家具及設備津貼（CFEG）使用指引》Part I：只要戶口有足夠款項，購買家具及設備（F&E）"
              "項目本身並無金額上限（there is no financial limit for F&E items to be purchased）；"
              "惟學校須確保開支合理、必需及用於教育用途，並確保CFEG足以涵蓋所有開支。"
              "（注意：CFEG戶口累積盈餘上限為該年撥款的5倍。）",
         keywords=["CFEG", "綜合家具及設備津貼", "家具", "設備", "F&E", "金額上限", "冇上限", "無上限",
                   "購買", "個別項目", "盈餘5倍", "使用指引", "財政限額"],
         q="CFEG買家具設備個別項目有冇金額上限"),
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
