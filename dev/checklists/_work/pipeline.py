#!/usr/bin/env python3
# S155 autonomous batch pipeline: per-domain checklist + school-version generation.
# Subcommands:
#   prep <batch|domain>        build _work/<domain>/bucket_*.json from all_chunks cache
#   mkflow-distill <batch>     emit _work/flow_distill_<batch>.js  (Workflow scriptPath)
#   ingest-distill <batch> <output.json path>   split workflow result into per-domain items_raw.json
#   mech-verify <domain>       3-tier quote+page verification -> items_verified.json
#   build-md <domain>          assemble DRAFT_checklist_<domain>.md + checklist.json
#   mkflow-rewrite <batch>     emit _work/flow_rewrite_<batch>.js from checklist.json chapters
#   ingest-rewrite <batch> <output.json path>    -> per-domain clauses.json (+ fixes report)
import json, os, re, sys, unicodedata
from collections import Counter, OrderedDict

ROOT = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
WORK = os.path.join(ROOT, "dev/checklists/_work")
OUTBASE = os.path.join(ROOT, "dev/checklists")
BUCKET_MAX = 55

POOLS = {
    "pool_sag": {"sources": ["sag_2025_11"],
                 "tags": ["cpd", "conduct", "sen", "hr_admin", "student_support",
                          "qa_inspection", "gov_admin", "safety", "curriculum"],
                 "lens": "《學校行政手冊》係跨域行政手冊：抽取學校管理層必須遵守嘅行政義務，並為每條 item 標註所屬域 tags（可多個）：cpd=教師專業發展/培訓；conduct=教師專業操守；sen=特殊教育需要；hr_admin=人事聘任假期薪酬；student_support=學生支援福祉訓輔；qa_inspection=質素保證自評視學問責；gov_admin=校務行政（籌款/維修/保險/校名/擴建/廉政）；safety=學校安全；curriculum=課程編排管理。同 tags 完全無關嘅內容（純財務/收生機制）可略過。"},
    "pool_g06": {"sources": ["g06"],
                 "tags": ["cpd", "sen", "gifted", "curriculum"],
                 "lens": "課程指引（g06）：只抽取學校層面嘅政策/管理義務（課程規劃、照顧多樣性、資優、教師發展、評估政策），逐條標 tags：cpd/sen/gifted/curriculum。純教學法內容略過。"},
}

D = lambda cn, sources, pools, lens: {"cn": cn, "sources": sources, "pools": pools, "lens": lens}
DOMAINS = OrderedDict([
    ("school_governance", D("校董會治理",
        ["imc_establishment_operation", "imc_briefing_qa", "imc_governance_supplements",
         "imc_election_guides", "g02", "coa_imc_1_19", "sdp_guide"], [],
        "校董會治理：法團校董會成立、章程、組成、各類校董產生/選舉/委任、角色職權、會議規程、申報利益、管治責任、學校發展計劃。g02/coa 抽治理角度（財務細則屬另一範疇，僅保留治理權責層面）。")),
    ("kg_admission", D("幼稚園收生",
        ["g26", "g25", "k1_admission_2627", "kg_admin_guide"], [],
        "幼稚園收生及相關行政：K1 入學安排、收生程序、註冊證、學費及售賣物品規則。")),
    ("placement", D("學位分配",
        ["edbc18_2019_sspa", "stims_guide_2025", "s4_placement_2026"], [],
        "學位分配：小一入學/中學學位分配/中四學位安排/學生資料管理系統（STIMS）下學校嘅義務。")),
    ("activity", D("全方位學習及活動",
        ["g03", "sch_activities_guide"], [],
        "全方位學習津貼運用＋學校活動指引：津貼用途界線、活動規劃、安全與帶隊要求、收費與記錄。")),
    ("conduct", D("教師專業操守", ["g05"], ["pool_sag"],
        "教師專業操守：操守準則、行為界線、利益、師生關係、申報與處理機制。")),
    ("safety", D("學校安全",
        ["edbc22_2024_student_safety", "fire_service_installation", "occupational_safety_health",
         "gas_odour_measures", "lab_prep_room_aircon", "edbc_tropical_cyclone_day",
         "edbc_tropical_cyclone_night", "safety_mgmt_committee", "slope_rmi_ei_notes",
         "g18", "g21", "g22"], ["pool_sag"],
        "學校安全：學生安全、消防裝置、職安健、氣體洩漏、實驗室、惡劣天氣（颱風/暴雨）安排、安全管理委員會、斜坡維修、校車安全、視藝/科技教育安全。")),
    ("gov_admin", D("校務行政",
        ["icac_school_governance", "fundraising_guide", "edbcm_major_repairs_grant",
         "edbc14_2024_spms", "sch_extension_guide", "sch_name_change_guide", "sdp_guide",
         "bip_insurance_notes_2025", "major_repairs_proc_nonestate", "major_repairs_proc_estate",
         "emergency_repairs_guide"], ["pool_sag"],
        "校務行政：廉政管治、籌款活動、大型/緊急維修工程程序、校舍擴建、校名更改、保險、學校發展計劃編寫。")),
    ("qa_inspection", D("質素保證與視學",
        ["sse_tools_2025", "perf_indicators_2022", "edbc15_2022_accountability"], ["pool_sag"],
        "質素保證：學校自評（SSE）、表現指標、問責框架、視學配合義務、報告與披露。")),
    ("hr_admin", D("人事管理",
        ["g04", "g05", "g11", "edbc13_2022_blnst", "edbcm141_2025_blnst",
         "blnst_test_notes_nondeg", "blnst_test_candidate_notes", "embc5_2005_appointment",
         "edbc14_2023_student_protect", "staff_medical_health", "job_sharing_guide",
         "surplus_teacher_arr_2026", "private_sch_employment_notes", "supply_teacher_guide",
         "long_service_payment_guide", "sch_calendar_guide"], ["pool_sag"],
        "人事管理：教職員聘任（包括性罪行定罪紀錄查核/保護學生）、批假、薪酬、基本法及國安法測試要求、代課、超額教師、遣散費長期服務金、職位共享、員工健康、校曆編訂。")),
    ("student_support", D("學生支援與福祉",
        ["edbc015_2021_lpe", "lpe_framework_primary", "edbc18_2008_harmonious",
         "edbc15_2025_child_abuse", "edbcm83_2020_student_care", "crisis_mgmt_handbook",
         "kg_crisis_mgmt", "edbc100_2002_healthy_sch", "hsp_framework",
         "hsp_drug_testing_2026", "g16", "g17"], ["pool_sag"],
        "學生支援與福祉：生命教育、和諧校園/防欺凌、保護兒童/懷疑虐兒處理、學生關顧、危機管理、健康校園、藥物測試、訓育及輔導。")),
    ("cpd", D("教師專業發展",
        ["circ_edbc24017", "tdtf_report_2019"], ["pool_sag", "pool_g06"],
        "教師專業發展：培訓要求、專業發展時數/安排、T-標準、新入職/在職培訓義務。")),
    ("sen", D("特殊教育需要",
        ["g10", "g19", "sen_exam_arrangements_2025", "cgss_2024"], ["pool_sag", "pool_g06"],
        "特殊教育需要：全校參與模式融合教育、特殊學校課程、校內考試特別安排、SENCO 統籌、家校溝通、資源運用。")),
    ("gifted", D("資優教育",
        ["gifted_policy_docs", "gifted_tp_resource_kit", "gifted_osalp_compendium",
         "gifted_ge_series", "g14"], ["pool_g06"],
        "資優教育：三層架構推行模式、校本資優培育、人才庫、課程及活動安排、識別與支援。")),
    ("curriculum", D("課程管理",
        ["kgecg_2017", "pri_curr_guide_2024", "g13", "g25", "g26", "g29", "g38",
         "mce_framework_2008", "circ_edbc24017", "edbc18_2023_pri_science",
         "edbc20_2023_ph_pri", "edbc9_2024_ph_pri", "edbc12_2025_ph_pri",
         "edbc197_2024_ph_pri", "edbc13_2025_pri_science", "edbc002_2026",
         "edbc003_2026", "edbc005_2026"], ["pool_sag", "pool_g06"],
        "課程管理（全校層面）：課程規劃與時數、科目開設（小學人文科/科學科推行）、評估政策、課程文件要求、價值觀教育/德育框架推行。科本教學內容唔屬範疇（剔除科本 KLA 指引）。")),
])

BATCHES = {
    "batch1": ["school_governance", "kg_admission", "placement", "activity", "pool_sag", "pool_g06"],
    "batch2": ["conduct", "safety", "gov_admin", "qa_inspection"],
    "batch3": ["hr_admin", "student_support", "cpd"],
    "batch4": ["sen", "gifted"],
    "batch5": ["curriculum"],
}

# ---------- shared loaders ----------
def load_chunks():
    return json.load(open(os.path.join(WORK, "all_chunks.json")))

def load_reg():
    reg = json.load(open(os.path.join(ROOT, "dev/source/source_registry.json")))
    srcs = reg.get("sources", reg) if isinstance(reg, dict) else reg
    return {s.get("source_id"): {"title": s.get("title", ""), "url": s.get("url_primary") or ""} for s in srcs}

def spec_of(key):
    if key in POOLS:
        p = POOLS[key]
        return {"kind": "pool", "cn": key, "sources": p["sources"], "lens": p["lens"], "tags": p["tags"]}
    d = DOMAINS[key]
    return {"kind": "domain", "cn": d["cn"], "sources": d["sources"], "lens": d["lens"], "tags": None}

# ---------- prep ----------
def prep(keys):
    rows = load_chunks()
    reg = load_reg()
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source_id"], []).append(r)
    for key in keys:
        sp = spec_of(key)
        dirp = os.path.join(WORK, key)
        os.makedirs(dirp, exist_ok=True)
        buckets, cur, cur_n = [], [], 0
        meta_sources = {}
        for sid in sp["sources"]:
            chs = by_src.get(sid, [])
            meta_sources[sid] = {"title": reg.get(sid, {}).get("title", sid),
                                 "url": reg.get(sid, {}).get("url", ""), "chunks": len(chs)}
            i = 0
            while i < len(chs):
                room = BUCKET_MAX - cur_n
                take = chs[i:i + room]
                cur.append({"source_id": sid, "source_title": meta_sources[sid]["title"],
                            "chunks": [{"id": c["id"], "text": c["text"]} for c in take]})
                cur_n += len(take); i += len(take)
                if cur_n >= BUCKET_MAX:
                    buckets.append(cur); cur, cur_n = [], 0
        if cur: buckets.append(cur)
        for bi, b in enumerate(buckets):
            json.dump({"key": key, "bucket": bi, "lens": sp["lens"], "tags": sp["tags"],
                       "sources": b}, open(os.path.join(dirp, f"bucket_{bi}.json"), "w"),
                      ensure_ascii=False)
        json.dump({"key": key, "kind": sp["kind"], "cn": sp["cn"], "lens": sp["lens"],
                   "tags": sp["tags"], "sources": meta_sources, "n_buckets": len(buckets)},
                  open(os.path.join(dirp, "meta.json"), "w"), ensure_ascii=False, indent=1)
        tot = sum(v["chunks"] for v in meta_sources.values())
        print(f"prep {key}: {tot} chunks -> {len(buckets)} buckets")

# ---------- workflow emission: distill ----------
DISTILL_RULES = """硬規則：
- 每條 item = 一句校本政策文件應覆蓋嘅要求/義務（繁體中文，命令式一句）。
- 寧缺勿估：每條必須有 verbatim 引文（≤50字，由 chunk text 原樣複製，可保留 PDF 怪空格/異體字）。冇引文支持就唔出。
- 優先「必須/不得/應」條款、金額、百分比、時限、年期、人數、批核層級 — 數字原樣保留。
- Skip 目錄、前言、純背景、純教學法內容；合併重複。
- 頁碼：chunk text 內嵌 '=== Page N ===' 標記；引文位置之前最近嘅標記就係頁碼 N；如引文喺 chunk 首個標記之前，用首個標記嘅 N 並設 approx=true，否則 approx=false。
- 每條 item 帶：req / section（建議章節，2-6字中文，自定）/ page / approx / quote / chunk_id / source_id。
- READ-ONLY：唔好寫/改 repo 檔（/tmp 草稿可以）。"""

def js_str(s):
    return json.dumps(s, ensure_ascii=False)

def mkflow_distill(batch):
    keys = BATCHES[batch]
    bucket_specs, domain_specs = [], []
    for key in keys:
        meta = json.load(open(os.path.join(WORK, key, "meta.json")))
        sp = spec_of(key)
        paths = [os.path.join(WORK, key, f"bucket_{i}.json") for i in range(meta["n_buckets"])]
        bucket_specs.append({"key": key, "paths": paths})
        domain_specs.append({"key": key, "kind": meta["kind"], "cn": meta["cn"],
                             "lens": meta["lens"], "tags": meta["tags"],
                             "n_chunks": sum(v["chunks"] for v in meta["sources"].values()),
                             "bucket_paths": paths})
    tag_field = """
- 因為呢個係跨域池，每條 item 額外要有 "domains" 欄：array，可選值 = TAGS（見任務描述），揀所有適用嘅域。"""
    # build JS
    item_props = """req: { type: 'string' }, section: { type: 'string' }, page: { type: 'number' },
                approx: { type: 'boolean' }, quote: { type: 'string' },
                chunk_id: { type: 'string' }, source_id: { type: 'string' },
                domains: { type: 'array', items: { type: 'string' } }"""
    js = []
    js.append("export const meta = {")
    js.append(f"  name: 'checklist-distill-{batch}',")
    js.append(f"  description: {js_str('Distill checklist items for ' + batch + ': ' + '+'.join(keys))},")
    js.append("  phases: [{ title: 'Distill' }, { title: 'Verify' }, { title: 'Critic' }],")
    js.append("}")
    js.append("const ITEM_SCHEMA = { type: 'object', required: ['items'], properties: { items: { type: 'array', items: {")
    js.append("  type: 'object', required: ['req','section','page','approx','quote','chunk_id','source_id'],")
    js.append("  properties: { " + item_props + " } } } } }")
    js.append("""const VERIFY_SCHEMA = { type: 'object', required: ['verdicts'], properties: { verdicts: { type: 'array', items: {
  type: 'object', required: ['idx','chunk_ok','quote_ok','page_ok','correct_page'],
  properties: { idx: { type: 'number' }, chunk_ok: { type: 'boolean' },
    quote_ok: { type: 'string', enum: ['exact','ws','fail'] }, page_ok: { type: 'boolean' },
    correct_page: { type: 'number' }, note: { type: 'string' } } } } } }""")
    js.append("const DOMAINS = " + json.dumps(domain_specs, ensure_ascii=False))
    js.append("const RULES = " + js_str(DISTILL_RULES))
    js.append("const TAGFIELD = " + js_str(tag_field))
    js.append("""
function distillPrompt(d, path) {
  let p = '你係香港學校政策知識平台嘅蒸餾員。用 Read 工具讀 ' + path +
    '（JSON：sources[] 每個有 source_id/source_title/chunks[]{id,text}；token 多可分段讀或用 python3 處理）。\\n\\n' +
    '任務範疇：' + d.cn + '。範疇視角：' + d.lens + '\\n\\n' + RULES
  if (d.tags) p += TAGFIELD + '\\nTAGS = ' + JSON.stringify(d.tags)
  p += '\\n\\n經 StructuredOutput 交出 items。'
  return p
}
function verifyPrompt(d, items) {
  return '你係獨立對抗覆核員，預設下面 items 嘅引文/頁碼有錯，用 python3 機械驗證（唔好肉眼）。\\n' +
    '原始 chunk 資料喺呢啲檔（JSON sources[].chunks[]{id,text}）：' + JSON.stringify(d.bucket_paths) + '\\n' +
    'Items（idx=0-based）：' + JSON.stringify(items) + '\\n\\n' +
    '每條 item 驗：(1) chunk_ok：chunk_id 存在且 source_id 匹配；' +
    '(2) quote_ok：quote 係 chunk text 原樣子串=exact；唔係就去晒空白再比= ws；再唔係 NFKC 正規化後比，仲唔得= fail；' +
    "(3) page_ok：喺 chunk text 揾 quote 位置（空白不敏感），位置之前最近嘅 '=== Page N ===' 標記 N 應等於 item.page；如 quote 喺首個標記之前，N=首標記且 item.approx 應為 true。correct_page=你計出嘅 N（計唔到=-1）。\\n" +
    '經 StructuredOutput 交出全部 verdicts。'
}
function criticPrompt(d, items) {
  return '你係完整性批判員。下面係範疇「' + d.cn + '」已蒸餾嘅 checklist items（淨 req/source_id/page）。' +
    '用 Read/python3 重讀全部原始 chunk 檔：' + JSON.stringify(d.bucket_paths) + '\\n' +
    '已覆蓋：' + JSON.stringify(items.map(i => ({ req: i.req, source_id: i.source_id, page: i.page }))) + '\\n\\n' +
    '揾出**漏咗**嘅 load-bearing 義務（金額/時限/百分比/人數/必須/不得 優先），最多 15 條，' +
    '同樣規則（verbatim 引文≤50字＋頁碼＋approx；寧缺勿估；空 array 係合法答案）。範疇視角：' + d.lens +
    (d.tags ? TAGFIELD + '\\nTAGS = ' + JSON.stringify(d.tags) : '') +
    '\\n經 StructuredOutput 交出 items。'
}

phase('Distill')
const results = await pipeline(
  DOMAINS,
  (d) => parallel(d.bucket_paths.map((p) => () =>
      agent(distillPrompt(d, p), { label: 'distill:' + d.key + ':' + p.split('bucket_')[1], phase: 'Distill', schema: ITEM_SCHEMA })))
    .then((parts) => ({ d, items: parts.filter(Boolean).flatMap((x) => x.items) })),
  (prev) => {
    if (!prev || !prev.items.length) return prev
    const CH = 80
    const slices = []
    for (let i = 0; i < prev.items.length; i += CH) slices.push(prev.items.slice(i, i + CH).map((it, j) => ({ ...it, _gidx: i + j })))
    return parallel(slices.map((sl) => () =>
        agent(verifyPrompt(prev.d, sl), { label: 'verify:' + prev.d.key, phase: 'Verify', schema: VERIFY_SCHEMA })
          .then((v) => ({ base: sl[0]._gidx, verdicts: v ? v.verdicts : null }))))
      .then((vs) => ({ ...prev, verify: vs.filter(Boolean) }))
  },
  (prev) => {
    if (!prev) return prev
    if (prev.d.kind === 'pool' || !prev.items.length) return { ...prev, critic: [] }
    return agent(criticPrompt(prev.d, prev.items), { label: 'critic:' + prev.d.key, phase: 'Critic', schema: ITEM_SCHEMA })
      .then((c) => ({ ...prev, critic: c ? c.items : [] }))
  }
)
const out = {}
for (const r of (results || []).filter(Boolean)) {
  out[r.d.key] = { items: r.items, verify: r.verify || [], critic: r.critic || [] }
  log(r.d.key + ': items=' + r.items.length + ' critic=' + (r.critic || []).length)
}
return out""")
    path = os.path.join(WORK, f"flow_distill_{batch}.js")
    open(path, "w").write("\n".join(js))
    print("emitted", path)

# ---------- ingest distill results ----------
def ingest_distill(batch, outfile):
    raw = json.load(open(outfile))
    res = raw.get("result", raw)
    if isinstance(res, str): res = json.loads(res)
    for key, payload in res.items():
        dirp = os.path.join(WORK, key)
        os.makedirs(dirp, exist_ok=True)
        json.dump(payload, open(os.path.join(dirp, "items_raw.json"), "w"), ensure_ascii=False)
        print(f"{key}: items={len(payload['items'])} critic={len(payload.get('critic', []))}")

# ---------- mechanical verification ----------
PAGE_RE = re.compile(r"===\s*Page\s+(\d+)\s*===")
def strip_map(s):
    out, idx = [], []
    for i, ch in enumerate(s):
        if not ch.isspace(): out.append(ch); idx.append(i)
    return "".join(out), idx
def nfkc_char(s):
    return "".join(unicodedata.normalize("NFKC", c) if len(unicodedata.normalize("NFKC", c)) == 1 else c for c in s)

def mech_verify(key):
    chunks = {r["id"]: (r["source_id"], r["text"]) for r in load_chunks()}
    dirp = os.path.join(WORK, key)
    raw = json.load(open(os.path.join(dirp, "items_raw.json")))
    items = raw["items"] + [dict(it, addendum=True) for it in raw.get("critic", [])]
    kept, dropped, fixed = [], 0, 0
    seen_quotes = set()
    for it in items:
        cid = it.get("chunk_id")
        if cid not in chunks: dropped += 1; continue
        sid, text = chunks[cid]
        if sid != it.get("source_id"): dropped += 1; continue
        st, idx = strip_map(text); sq, _ = strip_map(it.get("quote", ""))
        if not sq: dropped += 1; continue
        pos = st.find(sq)
        if pos < 0:
            pos = nfkc_char(st).find(nfkc_char(sq))
            if pos < 0: dropped += 1; continue
        opos = idx[min(pos, len(idx) - 1)]
        pages = [(m.start(), int(m.group(1))) for m in PAGE_RE.finditer(text)]
        if pages:
            prior = [p for s, p in pages if s <= opos]
            comp, approx = (prior[-1], False) if prior else (pages[0][1], True)
            if comp != it.get("page"): it["page"] = comp; fixed += 1
            it["approx"] = approx
            it["no_page"] = False
        else:
            it["no_page"] = True  # structurally unpaged source
        qk = (it["source_id"], nfkc_char(sq))
        if qk in seen_quotes and not it.get("addendum"):
            dropped += 1; continue  # exact duplicate item
        seen_quotes.add(qk)
        kept.append(it)
    json.dump(kept, open(os.path.join(dirp, "items_verified.json"), "w"), ensure_ascii=False)
    print(f"mech-verify {key}: in={len(items)} kept={len(kept)} dropped={dropped} page-fixed={fixed}")

# ---------- build checklist md ----------
def build_md(key):
    sp = spec_of(key)
    dirp = os.path.join(WORK, key)
    meta = json.load(open(os.path.join(dirp, "meta.json")))
    items = json.load(open(os.path.join(dirp, "items_verified.json")))
    # merge pooled items tagged for this domain
    for pool in DOMAINS[key]["pools"]:
        pf = os.path.join(WORK, pool, "items_verified.json")
        if os.path.exists(pf):
            for it in json.load(open(pf)):
                if key in (it.get("domains") or []):
                    items.append(dict(it, pooled=pool))
        else:
            print(f"WARN: pool {pool} not verified yet; {key} missing pool items")
    reg = load_reg()
    src_used = OrderedDict()
    for it in items:
        sid = it["source_id"]
        if sid not in src_used:
            src_used[sid] = {"title": reg.get(sid, {}).get("title", sid), "url": reg.get(sid, {}).get("url", "")}
    # group sections by name, order by count
    secs = OrderedDict()
    for it in items:
        secs.setdefault(it.get("section") or "其他", []).append(it)
    ordered = sorted(secs.items(), key=lambda kv: -len(kv[1]))
    cn = meta["cn"]
    L = [f"# 校本「{cn}」政策文件 — 要求清單（DRAFT v0.1）", "",
         f"> **狀態：DRAFT，待 Leonard 審。** S155 自主批次產出（2026-06-12）。範疇視角：{DOMAINS[key]['lens']}",
         "> 生成方法同 finance 樣板：蒸餾 → 獨立對抗覆核 → 完整性批判 → 本機機械重驗（exact→去空格→NFKC 三級引文比對＋頁碼重計）。每條必帶原文引文；引文照錄 PDF 文字層原樣。", "",
         "## 來源文件", "", "| source_id | 文件 | 連結 |", "|---|---|---|"]
    for sid, v in src_used.items():
        L.append(f"| `{sid}` | 《{v['title']}》 | [開啟]({v['url']}) |")
    L += ["", "## 要求清單", ""]
    total = 0
    cjson = {"key": key, "cn": cn, "sections": [], "src": {sid: [v["title"], v["url"]] for sid, v in src_used.items()}}
    for si, (sname, sitems) in enumerate(ordered, 1):
        L.append(f"### {si}. {sname}")
        L.append("")
        sec_items = []
        for j, it in enumerate(sitems, 1):
            total += 1
            t_ = src_used[it["source_id"]]
            add = "（覆核補遺）" if it.get("addendum") else ""
            if it.get("no_page"):
                cite = f"《{t_['title']}》（無頁碼源） — [開啟原文]({t_['url']})"
            else:
                flag = " ⚠️頁碼近似" if it.get("approx") else ""
                cite = f"《{t_['title']}》第 {it['page']} 頁{flag} — [開啟原文]({t_['url']}#page={it['page']})"
            L.append(f"- **R-{si}.{j}** {add}{it['req']}")
            L.append(f"  - 出處：{cite}")
            L.append(f"  - 引文：「{it['quote']}」")
            sec_items.append(it)
        L.append("")
        cjson["sections"].append({"name": sname, "items": sec_items})
    L += ["## 覆蓋度與 QC 紀錄", "",
          f"- 條目總數：**{total}**；本機機械重驗全通過（fail 已剔）。",
          f"- 範疇 scope 限制：{DOMAINS[key]['lens']}",
          "- 本清單係指引義務蒸餾，唔係法律意見；源文件改版須重新派生（freshness 週跑已監察）。", ""]
    outdir = os.path.join(OUTBASE, key)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, f"DRAFT_checklist_{key}.md"), "w").write("\n".join(L) + "\n")
    json.dump(cjson, open(os.path.join(dirp, "checklist.json"), "w"), ensure_ascii=False)
    print(f"build-md {key}: {total} items, {len(ordered)} sections -> {outdir}")

# ---------- workflow emission: rewrite ----------
def mkflow_rewrite(batch):
    keys = [k for k in BATCHES[batch] if k in DOMAINS]
    chapters = []
    for key in keys:
        cj = json.load(open(os.path.join(WORK, key, "checklist.json")))
        for si, sec in enumerate(cj["sections"], 1):
            ch_items = [{"id": i, "req": it["req"], "source_id": it["source_id"],
                         "page": it.get("page", -1), "quote": it["quote"]}
                        for i, it in enumerate(sec["items"])]
            cpath = os.path.join(WORK, key, f"ch_{si}.json")
            json.dump({"domain": key, "cn": cj["cn"], "section_no": si, "name": sec["name"],
                       "items": ch_items}, open(cpath, "w"), ensure_ascii=False)
            chapters.append({"domain": key, "cn": cj["cn"], "section_no": si,
                             "name": sec["name"], "n_items": len(ch_items), "path": cpath})
    js = []
    js.append("export const meta = {")
    js.append(f"  name: 'school-rewrite-{batch}',")
    js.append(f"  description: 'School-voice rewrite for {batch} chapters',")
    js.append("  phases: [{ title: 'Rewrite' }, { title: 'Verify' }],")
    js.append("}")
    js.append("""const REWRITE_SCHEMA = { type: 'object', required: ['clauses'], properties: { clauses: { type: 'array', items: {
  type: 'object', required: ['text','citations','adjustables','covers'],
  properties: { text: { type: 'string' },
    citations: { type: 'array', items: { type: 'object', required: ['source_id','page'], properties: { source_id: { type: 'string' }, page: { type: 'number' } } } },
    adjustables: { type: 'array', items: { type: 'string' } },
    covers: { type: 'array', items: { type: 'number' } },
    table: { type: ['object','null'], properties: { headers: { type: 'array', items: { type: 'string' } }, rows: { type: 'array', items: { type: 'array', items: { type: 'string' } } } } } } } } } }
const VERIFY_SCHEMA = { type: 'object', required: ['ok','issues','input_item_count','covered_item_count'], properties: {
  ok: { type: 'boolean' }, input_item_count: { type: 'number' }, covered_item_count: { type: 'number' },
  issues: { type: 'array', items: { type: 'object', required: ['kind','detail'], properties: {
    kind: { type: 'string', enum: ['uncovered-item','distorted-number','fabricated','bad-citation','double-covered'] },
    detail: { type: 'string' }, item_id: { type: 'number' } } } } } }""")
    js.append("const CHAPTERS = " + json.dumps(chapters, ensure_ascii=False))
    js.append("""
function rewritePrompt(c) {
  return '你係香港資助學校政策文件撰寫員。用 Read 工具讀 ' + c.path + '（JSON items[]：id/req/source_id/page/quote）。\\n' +
    '呢章屬範疇「' + c.cn + '」第 ' + c.section_no + ' 章「' + c.name + '」，共 ' + c.n_items + ' 條 item。\\n\\n' +
    '任務：改寫成校本政策文件條文，以「本校」為本位、繁體中文書面語、政策文件語域。\\n硬規則：\\n' +
    '1. 合併相關 items 成流暢條款，一條可涵蓋多個 items；要讀得似真政策文件。\\n' +
    '2. 嚴格保真（最重要）：所有金額/百分比/時限/年期/人數/批核層級原樣保留，唔可以改/漏/含糊化；情態詞唔可以加強或減弱（原文「可」唔可以變「須」、「應」唔可以變「必須」）；唔可以加入 source 冇嘅義務或目的語句。\\n' +
    '3. 預填指引訂明嘅典型做法；校名一律「本校」。\\n' +
    '4. adjustables：列出條文內屬學校自訂位嘅 verbatim 子字串（同 text 完全一致），例：法團校董會（未設者用校董會）、可調批核職級、委員會成員、本校自定表格名。\\n' +
    '5. citations：去重列出實際依據嘅 (source_id, page)；page=-1（無頁碼源）都照列。\\n' +
    '6. covers：每個 input item id 必須喺且僅喺一條 clause 嘅 covers 出現一次。\\n' +
    '7. 多行平行結構用 table（headers+rows 全字串），該 clause text 寫引入語。\\n' +
    '經 StructuredOutput 交出 clauses。'
}
function verifyPrompt(c, rw) {
  return '你係獨立對抗覆核員，預設改寫有錯漏走樣，用 python3 機械檢查＋語意判斷。先 Read ' + c.path + '（' + c.n_items + ' 條原始 item）。\\n' +
    '改寫結果：' + JSON.stringify(rw) + '\\n\\n檢查：\\n' +
    '1. 覆蓋：所有 covers id vs 原始 item id；漏=uncovered-item；重=double-covered。\\n' +
    '2. 數字保真：每 item 嘅 req+quote 嘅數字/時限/層級，喺 covers 佢嗰條 clause（連 table）有冇原樣保留；改/漏/含糊=distorted-number。\\n' +
    '3. 無虛構：clause 加咗 source 唔支持嘅義務/數字/目的語句/情態加強=fabricated。\\n' +
    '4. 引用正確：每 citation (source_id,page) 要喺佢 covers 嘅 items 出現過=否則 bad-citation。\\n' +
    '經 StructuredOutput 交出。'
}
phase('Rewrite')
const results = await pipeline(
  CHAPTERS,
  (c) => agent(rewritePrompt(c), { label: 'rw:' + c.domain + ':' + c.section_no, phase: 'Rewrite', schema: REWRITE_SCHEMA })
    .then((rw) => ({ c, rw })),
  (prev) => {
    if (!prev || !prev.rw) return prev
    return agent(verifyPrompt(prev.c, prev.rw), { label: 'vf:' + prev.c.domain + ':' + prev.c.section_no, phase: 'Verify', schema: VERIFY_SCHEMA })
      .then((v) => ({ ...prev, v }))
  }
)
const out = {}
for (const r of (results || []).filter(Boolean)) {
  const dk = r.c.domain
  out[dk] = out[dk] || []
  out[dk].push({ section_no: r.c.section_no, name: r.c.name, clauses: r.rw ? r.rw.clauses : null,
                 verify: r.v || null })
  log(dk + ' ch' + r.c.section_no + ': clauses=' + (r.rw ? r.rw.clauses.length : 0) +
      ' verify=' + (r.v ? (r.v.ok ? 'OK' : 'ISSUES=' + r.v.issues.length) : 'MISSING'))
}
return out""")
    path = os.path.join(WORK, f"flow_rewrite_{batch}.js")
    open(path, "w").write("\n".join(js))
    print("emitted", path, f"({len(chapters)} chapters)")

def ingest_rewrite(batch, outfile):
    raw = json.load(open(outfile))
    res = raw.get("result", raw)
    if isinstance(res, str): res = json.loads(res)
    for key, chs in res.items():
        dirp = os.path.join(WORK, key)
        chs.sort(key=lambda c: c["section_no"])
        json.dump(chs, open(os.path.join(dirp, "clauses.json"), "w"), ensure_ascii=False)
        issues = [i for c in chs if c.get("verify") and not c["verify"]["ok"] for i in c["verify"]["issues"]]
        miss = [c["section_no"] for c in chs if not c.get("verify")]
        print(f"{key}: chapters={len(chs)} issue-flags={len(issues)} verify-missing={miss}")
        for c in chs:
            if c.get("verify") and not c["verify"]["ok"]:
                for i in c["verify"]["issues"]:
                    print(f"   ch{c['section_no']} [{i['kind']}] item {i.get('item_id')}: {i['detail'][:160]}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    keys = BATCHES.get(arg, [arg] if arg else [])
    if cmd == "prep": prep(keys)
    elif cmd == "mkflow-distill": mkflow_distill(arg)
    elif cmd == "ingest-distill": ingest_distill(arg, sys.argv[3])
    elif cmd == "mech-verify":
        for k in keys: mech_verify(k)
    elif cmd == "build-md":
        for k in (k for k in keys if k in DOMAINS): build_md(k)
    elif cmd == "mkflow-rewrite": mkflow_rewrite(arg)
    elif cmd == "ingest-rewrite": ingest_rewrite(arg, sys.argv[3])
    else: print("unknown cmd")
