export const meta = {
  name: 'checklist-distill-batch2',
  description: "Distill checklist items for batch2: conduct+safety+gov_admin+qa_inspection",
  phases: [{ title: 'Distill' }, { title: 'Verify' }, { title: 'Critic' }],
}
const ITEM_SCHEMA = { type: 'object', required: ['items'], properties: { items: { type: 'array', items: {
  type: 'object', required: ['req','section','page','approx','quote','chunk_id','source_id'],
  properties: { req: { type: 'string' }, section: { type: 'string' }, page: { type: 'number' },
                approx: { type: 'boolean' }, quote: { type: 'string' },
                chunk_id: { type: 'string' }, source_id: { type: 'string' },
                domains: { type: 'array', items: { type: 'string' } } } } } } }
const VERIFY_SCHEMA = { type: 'object', required: ['verdicts'], properties: { verdicts: { type: 'array', items: {
  type: 'object', required: ['idx','chunk_ok','quote_ok','page_ok','correct_page'],
  properties: { idx: { type: 'number' }, chunk_ok: { type: 'boolean' },
    quote_ok: { type: 'string', enum: ['exact','ws','fail'] }, page_ok: { type: 'boolean' },
    correct_page: { type: 'number' }, note: { type: 'string' } } } } } }
const DOMAINS = [{"key": "conduct", "kind": "domain", "cn": "教師專業操守", "lens": "教師專業操守：操守準則、行為界線、利益、師生關係、申報與處理機制。", "tags": null, "n_chunks": 29, "bucket_paths": ["/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/conduct/bucket_0.json"]}, {"key": "safety", "kind": "domain", "cn": "學校安全", "lens": "學校安全：學生安全、消防裝置、職安健、氣體洩漏、實驗室、惡劣天氣（颱風/暴雨）安排、安全管理委員會、斜坡維修、校車安全、視藝/科技教育安全。", "tags": null, "n_chunks": 164, "bucket_paths": ["/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/safety/bucket_0.json", "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/safety/bucket_1.json", "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/safety/bucket_2.json"]}, {"key": "gov_admin", "kind": "domain", "cn": "校務行政", "lens": "校務行政：廉政管治、籌款活動、大型/緊急維修工程程序、校舍擴建、校名更改、保險、學校發展計劃編寫。", "tags": null, "n_chunks": 125, "bucket_paths": ["/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/gov_admin/bucket_0.json", "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/gov_admin/bucket_1.json", "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/gov_admin/bucket_2.json"]}, {"key": "qa_inspection", "kind": "domain", "cn": "質素保證與視學", "lens": "質素保證：學校自評（SSE）、表現指標、問責框架、視學配合義務、報告與披露。", "tags": null, "n_chunks": 54, "bucket_paths": ["/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/qa_inspection/bucket_0.json"]}]
const RULES = "硬規則：\n- 每條 item = 一句校本政策文件應覆蓋嘅要求/義務（繁體中文，命令式一句）。\n- 寧缺勿估：每條必須有 verbatim 引文（≤50字，由 chunk text 原樣複製，可保留 PDF 怪空格/異體字）。冇引文支持就唔出。\n- 優先「必須/不得/應」條款、金額、百分比、時限、年期、人數、批核層級 — 數字原樣保留。\n- Skip 目錄、前言、純背景、純教學法內容；合併重複。\n- 頁碼：chunk text 內嵌 '=== Page N ===' 標記；引文位置之前最近嘅標記就係頁碼 N；如引文喺 chunk 首個標記之前，用首個標記嘅 N 並設 approx=true，否則 approx=false。\n- 每條 item 帶：req / section（建議章節，2-6字中文，自定）/ page / approx / quote / chunk_id / source_id。\n- READ-ONLY：唔好寫/改 repo 檔（/tmp 草稿可以）。"
const TAGFIELD = "\n- 因為呢個係跨域池，每條 item 額外要有 \"domains\" 欄：array，可選值 = TAGS（見任務描述），揀所有適用嘅域。"

function distillPrompt(d, path) {
  let p = '你係香港學校政策知識平台嘅蒸餾員。用 Read 工具讀 ' + path +
    '（JSON：sources[] 每個有 source_id/source_title/chunks[]{id,text}；token 多可分段讀或用 python3 處理）。\n\n' +
    '任務範疇：' + d.cn + '。範疇視角：' + d.lens + '\n\n' + RULES
  if (d.tags) p += TAGFIELD + '\nTAGS = ' + JSON.stringify(d.tags)
  p += '\n\n經 StructuredOutput 交出 items。'
  return p
}
function verifyPrompt(d, items) {
  return '你係獨立對抗覆核員，預設下面 items 嘅引文/頁碼有錯，用 python3 機械驗證（唔好肉眼）。\n' +
    '原始 chunk 資料喺呢啲檔（JSON sources[].chunks[]{id,text}）：' + JSON.stringify(d.bucket_paths) + '\n' +
    'Items（idx=0-based）：' + JSON.stringify(items) + '\n\n' +
    '每條 item 驗：(1) chunk_ok：chunk_id 存在且 source_id 匹配；' +
    '(2) quote_ok：quote 係 chunk text 原樣子串=exact；唔係就去晒空白再比= ws；再唔係 NFKC 正規化後比，仲唔得= fail；' +
    "(3) page_ok：喺 chunk text 揾 quote 位置（空白不敏感），位置之前最近嘅 '=== Page N ===' 標記 N 應等於 item.page；如 quote 喺首個標記之前，N=首標記且 item.approx 應為 true。correct_page=你計出嘅 N（計唔到=-1）。\n" +
    '經 StructuredOutput 交出全部 verdicts。'
}
function criticPrompt(d, items) {
  return '你係完整性批判員。下面係範疇「' + d.cn + '」已蒸餾嘅 checklist items（淨 req/source_id/page）。' +
    '用 Read/python3 重讀全部原始 chunk 檔：' + JSON.stringify(d.bucket_paths) + '\n' +
    '已覆蓋：' + JSON.stringify(items.map(i => ({ req: i.req, source_id: i.source_id, page: i.page }))) + '\n\n' +
    '揾出**漏咗**嘅 load-bearing 義務（金額/時限/百分比/人數/必須/不得 優先），最多 15 條，' +
    '同樣規則（verbatim 引文≤50字＋頁碼＋approx；寧缺勿估；空 array 係合法答案）。範疇視角：' + d.lens +
    (d.tags ? TAGFIELD + '\nTAGS = ' + JSON.stringify(d.tags) : '') +
    '\n經 StructuredOutput 交出 items。'
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
return out