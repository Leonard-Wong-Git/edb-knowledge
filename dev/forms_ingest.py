#!/usr/bin/env python3
"""forms_ingest.py — batch ingest EDB subsidy-form footnote facts (S177 forms coverage).

Same mechanism as ingest_trg_footnote.py: content_type=footnote_curated, route-independent
overlay, embed = text + " " + " ".join(keywords). All figures verbatim-verified against the
official EDB source PDFs (pymupdf) this session — see dev/FORMS_FOOTNOTE_CANDIDATES.md.

Modes:
  --self-test (default) : embed all + per-entry cosine vs a representative query (gate 0.42);
                          dup-id check. NO WRITE.
  --execute             : INSPECT before (footnote_curated count) + batch INSERT (upsert) +
                          INSPECT after.
Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY from backend/.env.
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
B = "https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/subsidy-info"

# Per-source identity (new source_ids; footnote pass is route-independent so these need NOT
# be in the registry/SOURCE_SET). url -> the verified EN source PDF.
SRC = {
    "trg": ("trg_imc_2023", "為設有法團校董會學校而提供的整合代課教師津貼（2023年9月）", B + "/trg/TRG_guidelines_C.pdf"),
    "ceg": ("ceg_calc_2026", "學校發展津貼（CEG）計算方法（2026/27）", B + "/ref-capacity-enhancement-grant/Calculation%20of%20CEG_en.pdf"),
    "eoebg": ("eoebg_guide_2026", "擴大營辦津貼（EOEBG）使用指引", B + "/ref-e-oebg-cfeg/User%20Guide_EOEBG_e.pdf"),
    "cfeg": ("cfeg_guide_2026", "綜合家具及設備津貼（CFEG）使用指引", B + "/ref-e-oebg-cfeg/User%20Guide_CFEG_e.pdf"),
    "oebg": ("oebg_guide_2026", "營辦津貼（OEBG）使用指引", B + "/ref-e-oebg-cfeg/User%20Guide_OEBG_e.pdf"),
    "ac": ("ac_grant_2026", "資助學校空調津貼（Air-conditioning Grant）", B + "/ref-e-oebg-cfeg/AC%20Grant%20in%20Aided%20Schools_e.pdf"),
    "tips": ("subvention_tips", "處理政府給予資助學校資助的提示", "https://www.edb.gov.hk/en/sch-admin/fin-management/subsidy-info/tips-handling-gov-subventions/index.html"),
    "rates": ("eoebg_rates_2026", "資助學校津貼費率表（2026/27）", B + "/ref-e-oebg-cfeg/E_Sec_Table%20II_2026_e.pdf"),
}

# (fid, src_key, text, keywords, test_query)
F = [
    ("trg_freeze_mpf", "trg",
     "申請整合代課教師津貼而凍結教師空缺，如空缺凍結達60曆日或以上，僱主強積金（MPF）供款點計？僱主MPF供款額為該職位月薪的5%或$1,500，以較少者為準。",
     ["凍結教席", "凍結空缺", "強積金", "MPF", "僱主供款", "5%", "1500", "60日", "60曆日", "代課教師津貼", "TRG"],
     "凍結教席空缺 僱主強積金供款幾多"),
    ("trg_no_freeze_posts", "trg",
     "申請整合代課教師津貼時，邊啲教師職位不可凍結？不可凍結的職位包括：校長／首席教師、外籍英語教師（NET）、學生輔導教師、小學課程統籌主任、特殊教育需要統籌主任（SENCO）、特殊教育需要支援教師。",
     ["不可凍結", "唔可以凍結", "職位", "校長", "外籍英語教師", "NET", "學生輔導教師", "小學課程統籌主任", "SENCO", "特殊教育需要統籌主任", "SEN支援教師", "代課教師津貼"],
     "邊啲教席唔可以凍結 申請代課津貼"),
    ("ceg_bisessional", "ceg",
     "雙課制（上下午校）資助小學的學校發展津貼（CEG）點計算？總班數達25班或以上的雙課制小學，每節（每個課程）當作獨立學校分開計算CEG。",
     ["學校發展津貼", "CEG", "雙課制", "上下午校", "25班", "每節", "獨立學校", "分開計算"],
     "雙課制小學 學校發展津貼點計"),
    ("ceg_both_levels", "ceg",
     "同時設有小學及中學部的學校，學校發展津貼（CEG）用咩費率？一律採用小學費率，合資格班數為核准小學班數加中學班數的總和。",
     ["CEG", "學校發展津貼", "中小學兼收", "小學及中學部", "小學費率", "合資格班數"],
     "中小學兼收 CEG 用咩費率"),
    ("ceg_no_tutorial", "ceg",
     "可唔可以用學校發展津貼（CEG）支付教師補課的酬金？唔可以。CEG不得用於支付教師教授補習／補底班（tutorial classes）的額外酬金。",
     ["CEG", "學校發展津貼", "補課", "補習班", "補底班", "tutorial", "額外酬金", "唔准", "不得"],
     "CEG 可唔可以出錢補課"),
    ("ceg_rates_2627", "ceg",
     "學校發展津貼（CEG）2026/27年度按班數定額幾多？（2026/27）小學1至5班$193,164，逐級遞增至24班或以上封頂$670,238；中學1至12班$305,888，至24班或以上$548,327；特殊學校1至5班$214,627，至19班或以上$744,723。",
     ["CEG", "學校發展津貼", "費率", "班數", "2026/27", "193164", "670238", "305888", "548327", "214627", "744723"],
     "學校發展津貼 2026/27 每班幾多錢"),
    ("eoebg_surplus_12m", "eoebg",
     "擴大營辦津貼（EOEBG）的盈餘可以保留幾多？盈餘保留上限為12個月撥款額（扣除已預留作遣散費／長期服務金的承擔額）；超出上限須經教育局常任秘書長批准方可保留。",
     ["EOEBG", "擴大營辦津貼", "盈餘", "保留", "上限", "12個月", "撥款額", "遣散費", "長期服務金"],
     "EOEBG 盈餘可以保留幾耐"),
    ("eoebg_topup_cap", "eoebg",
     "用EOEBG盈餘補貼（top-up）其他項目有冇上限？有：政府資助項目的經常開支最多補50%；家具設備及其他經常開支最多補25%。",
     ["EOEBG", "盈餘", "top-up", "補貼", "上限", "50%", "25%", "經常開支", "政府資助項目", "家具設備"],
     "EOEBG 盈餘補貼其他項目上限"),
    ("eoebg_meal_cap", "eoebg",
     "學校用津貼支付公務應酬餐飲，每人每餐上限幾多？早餐／其他公務膳食上限$200、午餐$450、晚餐$600（已包括加一服務費及貼士）；超額須由法團校董會提供充分理由。",
     ["應酬", "餐飲", "膳食", "公務", "早餐", "午餐", "晚餐", "200", "450", "600", "上限", "EOEBG", "OEBG"],
     "學校公務應酬飯局上限幾多錢"),
    ("eoebg_unpaid_leave", "eoebg",
     "EOEBG盈餘可唔可以支付無薪假期間的法定假日及年假？可以。可用盈餘支付4類特定無薪假（無薪病假／產假／肺結核假、進修教育課程無薪假、健康欠佳並有醫療證明的無薪假、紓緩裁員的無薪假）期間的法定假日及年假。",
     ["EOEBG", "盈餘", "無薪假", "法定假", "年假", "無薪病假", "產假", "進修", "裁員", "醫療證明"],
     "EOEBG 盈餘可唔可以畀無薪假法定假"),
    ("eoebg_ab_2627", "eoebg",
     "擴大營辦津貼（EOEBG）新校撥款公式同A／B值（2026/27）？公式＝A（基本撥款）＋B（每班率）×N（核准班數）＋校本津貼。2026/27：資助小學A=$393,980、B=$30,274；中學A=$550,193、B（中一至中三）=$48,702／（中四至中六）=$51,332；智障特殊學校A=$594,246、B=$38,025。",
     ["EOEBG", "撥款公式", "A值", "B值", "每班率", "2026/27", "393980", "30274", "550193", "48702", "594246"],
     "EOEBG 撥款公式 A B 值幾多"),
    ("cfeg_surplus_5x", "cfeg",
     "綜合家具及設備津貼（CFEG）的盈餘可以累積幾多？未用的CFEG盈餘最多可累積至該年撥款額的5倍，超出部分由教育局收回。（注意：與EOEBG的12個月上限不同。）",
     ["CFEG", "綜合家具及設備津貼", "盈餘", "累積", "5倍", "上限", "收回", "claw back"],
     "CFEG 盈餘可以累積幾多"),
    ("cfeg_setup_fund", "cfeg",
     "新成立的學校點樣取得CFEG添置家具設備？新校首3年使用開辦費（Set-up Fund）添置；教育局批准結束Set-up Fund戶口後，才開始發放CFEG。",
     ["CFEG", "新校", "開辦費", "Set-up Fund", "首3年", "家具設備", "添置"],
     "新學校點攞CFEG買家具"),
    ("cfeg_rates_2627", "cfeg",
     "綜合家具及設備津貼（CFEG）每班單位率（2026/27）？小學全日制每班$8,418、雙課制每節$5,893、中學每班$17,423；特殊學校按類型計（如視障$24,847）。",
     ["CFEG", "單位率", "每班", "2026/27", "8418", "5893", "17423", "家具設備", "費率"],
     "CFEG 每班幾多錢 2026/27"),
    ("oebg_surplus_12m", "oebg",
     "營辦津貼（OEBG，未成立法團校董會的學校）盈餘上限幾多？OEBG盈餘上限為12個月撥款額；超出上限時，學校可自選由邊個津貼項目收回（建議先扣Special Domain，後扣General Domain）。",
     ["OEBG", "營辦津貼", "盈餘", "12個月", "上限", "收回", "Special Domain", "General Domain"],
     "OEBG 盈餘上限幾多"),
    ("oebg_domain_virement", "oebg",
     "OEBG的Special Domain與General Domain津貼可唔可以互相調撥？Special Domain各項津貼之間不准互調、亦不准調出；但可由General Domain的盈餘補貼（top-up）。",
     ["OEBG", "Special Domain", "General Domain", "調撥", "互調", "virement", "補貼", "top-up"],
     "OEBG Special General Domain 可唔可以調撥"),
    ("ac_special_room_cap", "ac",
     "空調津貼（AC Grant）資助的特別室數目有冇上限？有：小學特別室上限5間、中學12間；特殊學校按類型計8至12間。",
     ["空調津貼", "AC Grant", "特別室", "上限", "封頂", "小學5", "中學12", "特殊學校"],
     "空調津貼資助幾多間特別室"),
    ("ac_equiv_formula", "ac",
     "空調津貼點計算唔同場地的資助額？採等值公式：學生活動中心（SAC）＝1個課室率；標準禮堂＝2.5個特別室率；小組教學室＝0.5個課室率；無禮堂時有蓋操場＝2個特別室率。",
     ["AC Grant", "空調津貼", "等值", "公式", "SAC", "學生活動中心", "標準禮堂", "特別室", "小組教學室", "有蓋操場"],
     "空調津貼禮堂 SAC 點計"),
    ("ac_sac_cap", "ac",
     "空調津貼最多資助幾多個學生活動中心（SAC）？每校最多資助2個SAC（1個SAC，加其他合資格課後活動室合共額外1個SAC率）。",
     ["AC Grant", "空調津貼", "SAC", "學生活動中心", "上限", "2個", "每校"],
     "空調津貼資助幾多個學生活動中心"),
    ("ac_rates_2627", "ac",
     "空調津貼（AC Grant）中學各場地金額（2026/27）？每個課室／SAC$8,384、每個特別室$21,263、每個小組教學室$4,192、標準禮堂$53,158。",
     ["AC Grant", "空調津貼", "金額", "中學", "2026/27", "8384", "21263", "53158", "4192"],
     "空調津貼中學課室禮堂幾多錢"),
    ("procurement_thresholds", "tips",
     "資助學校採購貨品或服務，需要幾多個報價或招標？按金額分級：$5,000或以下免競投（校長／副校長批核）；超過$5,000至$50,000須最少2個口頭報價（校長批核）；超過$50,000至$200,000須最少5個書面報價（校長批核）；超過$200,000須公開招標、邀請最少5個供應商（經投標審批委員會批核）。",
     ["採購", "報價", "招標", "門檻", "5000", "50000", "200000", "口頭報價", "書面報價", "投標", "供應商", "財務上限", "投標審批委員會"],
     "學校採購要幾多個報價"),
    ("boarding_fee_deduct", "rates",
     "寄宿津貼（Boarding Grant）每名寄宿生點計？每名寄宿生每月津貼須扣減每月宿費；2026/27學年宿費為$440。",
     ["寄宿津貼", "Boarding Grant", "寄宿生", "宿費", "440", "2026/27", "扣減"],
     "寄宿津貼宿費扣幾多"),
    ("dlg_incentive_cease", "rates",
     "多元學習津貼（其他課程）的額外獎勵金有冇變動？2025/26對使用率達80%或以上的學校，每班高中額外獎勵$800（全年合共$7,800／班）；此獎勵金由2026/27學年起取消。",
     ["多元學習津貼", "DLG", "Diversity Learning", "使用率", "80%", "800", "7800", "高中", "2026/27", "取消", "獎勵"],
     "多元學習津貼額外獎勵 2026/27"),
    ("mmlc_it_grant", "rates",
     "仍在使用多媒體學習中心（MMLC）的學校有冇額外資訊科技津貼？合資格而仍使用MMLC的學校，每校每年額外獲$59,570（綜合資訊科技津貼）。",
     ["MMLC", "多媒體學習中心", "綜合資訊科技津貼", "Composite IT", "59570", "每校", "資訊科技"],
     "MMLC 多媒體學習中心 額外津貼"),
    ("lwl_sister_floor", "rates",
     "全方位學習津貼加姊妹學校津貼，每校總額有冇下限？每校總額設有上限，但每校不少於$300,000。",
     ["全方位學習津貼", "姊妹學校津貼", "Life-wide Learning", "Sister School", "300000", "下限", "每校", "總額"],
     "全方位學習津貼 姊妹學校 每校最少幾多"),
]


def combine(text, kw):
    return text + " " + " ".join(kw)


def cos(a, b):
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return s / (na * nb) if na and nb else 0.0


def load_service_key():
    k = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'"); break
    return k


def headers_svc():
    svc = load_service_key()
    if not svc:
        sys.exit("ERROR: SUPABASE_SERVICE_KEY missing")
    return {"apikey": svc, "Authorization": f"Bearer {svc}", "Content-Type": "application/json"}


def fn_count(h):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&content_type=eq.footnote_curated",
                     headers={**h, "Range-Unit": "items", "Range": "0-0", "Prefer": "count=exact"}, timeout=40)
    return r.headers.get("content-range", "?")


def build_rows(vectors):
    rows = []
    for (fid, src_key, text, kw, _q), v in zip(F, vectors):
        sid, title, url = SRC[src_key]
        rows.append({
            "id": f"footnote_fn_{fid}", "hash": bw.text_hash(text), "text": text,
            "source_id": sid, "title": title, "url": url,
            "topic": "general", "content_type": "footnote_curated", "fact_type": "policy",
            "embedding": v,
        })
    return rows


def self_test():
    api = bw.load_api_key()
    ids = [f"footnote_fn_{x[0]}" for x in F]
    print(f"entries={len(F)} unique_ids={len(set(ids))}")
    fn_vecs = bw.embed_batch(api, [combine(t, kw) for _, _, t, kw, _ in F])
    q_vecs = bw.embed_batch(api, [q for *_, q in F])
    print("=== per-entry cosine vs representative query (gate LEAD>=0.45) ===")
    weak = 0
    for (fid, *_), fv, qv in zip(F, fn_vecs, q_vecs):
        c = cos(fv, qv); flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "WEAK")
        if c < 0.45:
            weak += 1
        print(f"  {c:.3f} [{flag:5}] {fid}")
    print(f"=== {len(F)-weak}/{len(F)} >= 0.45 lead ===")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated:", fn_count(h))
    vectors = bw.embed_batch(api, [combine(t, kw) for _, _, t, kw, _ in F])
    rows = build_rows(vectors)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    for i in range(0, len(rows), 50):
        batch = rows[i:i + 50]
        resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=batch, timeout=120)
        if resp.status_code not in (200, 201, 204):
            sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
        print(f"  inserted {min(i+50,len(rows))}/{len(rows)}")
    print("=== INSPECT after ===")
    print("  footnote_curated:", fn_count(h))


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
