export const meta = {
  name: 'school-rewrite-cpd-hr',
  description: 'School-voice rewrite for cpd ch8-12 + hr_admin ch1-11',
  phases: [{ title: 'Rewrite' }, { title: 'Verify' }],
}
const REWRITE_SCHEMA = { type: 'object', required: ['clauses'], properties: { clauses: { type: 'array', items: {
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
    detail: { type: 'string' }, item_id: { type: 'number' } } } } } }
const CHAPTERS = [{"domain": "cpd", "cn": "教師專業發展", "section_no": 8, "name": "校長培訓資格", "n_items": 4, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/cpd/ch_8.json"}, {"domain": "cpd", "cn": "教師專業發展", "section_no": 9, "name": "特殊範疇師訓", "n_items": 10, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/cpd/ch_9.json"}, {"domain": "cpd", "cn": "教師專業發展", "section_no": 10, "name": "專業標準架構", "n_items": 4, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/cpd/ch_10.json"}, {"domain": "cpd", "cn": "教師專業發展", "section_no": 11, "name": "教師資歷政策", "n_items": 4, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/cpd/ch_11.json"}, {"domain": "cpd", "cn": "教師專業發展", "section_no": 12, "name": "行政支援配套", "n_items": 4, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/cpd/ch_12.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 1, "name": "教師聘任資格", "n_items": 49, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_1.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 2, "name": "僱傭合約條款", "n_items": 17, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_2.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 3, "name": "薪酬待遇", "n_items": 6, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_3.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 4, "name": "假期制度", "n_items": 30, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_4.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 5, "name": "工作表現評核", "n_items": 12, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_5.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 6, "name": "申報及合規", "n_items": 28, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_6.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 7, "name": "紀律懲處", "n_items": 13, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_7.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 8, "name": "申訴機制", "n_items": 5, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_8.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 9, "name": "退休離職補償", "n_items": 18, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_9.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 10, "name": "人事記錄管理", "n_items": 13, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_10.json"}, {"domain": "hr_admin", "cn": "人事管理", "section_no": 11, "name": "其他", "n_items": 2, "path": "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/dev/checklists/_work/hr_admin/ch_11.json"}]

function rewritePrompt(c) {
  return '你係香港資助學校政策文件撰寫員。用 Read 工具讀 ' + c.path + '（JSON items[]：id/req/source_id/page/quote）。\n' +
    '呢章屬範疇「' + c.cn + '」第 ' + c.section_no + ' 章「' + c.name + '」，共 ' + c.n_items + ' 條 item。\n\n' +
    '任務：改寫成校本政策文件條文，以「本校」為本位、繁體中文書面語、政策文件語域。\n硬規則：\n' +
    '1. 合併相關 items 成流暢條款，一條可涵蓋多個 items；要讀得似真政策文件。\n' +
    '2. 嚴格保真（最重要）：所有金額/百分比/時限/年期/人數/批核層級原樣保留，唔可以改/漏/含糊化；情態詞唔可以加強或減弱（原文「可」唔可以變「須」、「應」唔可以變「必須」）；唔可以加入 source 冇嘅義務或目的語句。\n' +
    '3. 預填指引訂明嘅典型做法；校名一律「本校」。\n' +
    '4. adjustables：列出條文內屬學校自訂位嘅 verbatim 子字串（同 text 完全一致），例：法團校董會（未設者用校董會）、可調批核職級、委員會成員、本校自定表格名。\n' +
    '5. citations：去重列出實際依據嘅 (source_id, page)；page=-1（無頁碼源）都照列。\n' +
    '6. covers：每個 input item id 必須喺且僅喺一條 clause 嘅 covers 出現一次。\n' +
    '7. 多行平行結構用 table（headers+rows 全字串），該 clause text 寫引入語。\n' +
    '經 StructuredOutput 交出 clauses。'
}
function verifyPrompt(c, rw) {
  return '你係獨立對抗覆核員，預設改寫有錯漏走樣，用 python3 機械檢查＋語意判斷。先 Read ' + c.path + '（' + c.n_items + ' 條原始 item）。\n' +
    '改寫結果：' + JSON.stringify(rw) + '\n\n檢查：\n' +
    '1. 覆蓋：所有 covers id vs 原始 item id；漏=uncovered-item；重=double-covered。\n' +
    '2. 數字保真：每 item 嘅 req+quote 嘅數字/時限/層級，喺 covers 佢嗰條 clause（連 table）有冇原樣保留；改/漏/含糊=distorted-number。\n' +
    '3. 無虛構：clause 加咗 source 唔支持嘅義務/數字/目的語句/情態加強=fabricated。\n' +
    '4. 引用正確：每 citation (source_id,page) 要喺佢 covers 嘅 items 出現過=否則 bad-citation。\n' +
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
return out