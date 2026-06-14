# 文件修訂功能（checklist gap analysis）— S160

> Leonard 通宵指示：「準備好功能，使用者會上載文件(PDF/doc/docx)，然後你可以按 checklist 去修訂及補回相關資料，並供下載。」
> 本功能已**實作 + 雙路 verify 通過**（backend python e2e + frontend browser），**staged 未 deploy**，待 Leonard review。

## 1. 一句話

新 app.html「📝 文件修訂」tab：使用者上載/貼上本校政策文件 → 揀政策範疇（14 域之一）+ 校類 → 系統按該域 EDB 清單**逐項語義比對**，標示 **已涵蓋 / 部分 / 未見**，為缺漏項**補回標準條文**（即政策範本背後嘅學校版 clause），可下載 Word 修訂建議。

設計取向（誠實）：用 **embedding 語義相似度**做覆蓋估算（deterministic、無 LLM、快、平），輸出框定為「自動估算、供檢視」，唔當定論；真正價值 = 逐項列出要求 + 補回標準條文。

## 2. 架構

```
app.html ReviewPanel (client extract pdf.js/mammoth — 原檔不上載)
   │  POST {text, domain, school_type?, filename?}
   ▼
backend  POST /api/checklist-revise  (checklistRevise.ts)
   │  ① segmentText(text)            （重用 analyzeDocument）
   │  ② 載入 checklists_bundle.json   （repo root，14 域 items+clauses）
   │  ③ embeddingClient.batch([...docSegs, ...itemReqs])  一次 OpenAI call
   │  ④ 每 item: max cosine over docSegs → covered/partial/missing
   │  ⑤ 缺漏項: clause.si===section+1 && clause.covers∋localIdx → 補回 text
   ▼  回 {sections:[{name, items:[{status, similarity, best_excerpt, supplement, sources}]}], 統計}
app.html  render 報告 + buildRevisedDocx() client-side Word（缺漏項+標準條文，不上載）
GET /api/checklist-domains → 域 selector
```

## 3. 檔案（本 session）

| 檔案 | 動作 | 說明 |
|---|---|---|
| `backend/src/api/checklistRevise.ts` | **NEW** | 端點邏輯（embedding coverage + clause supplement）。`MAX_TEXT_CHARS=60k`、`MAX_DOC_SEGMENTS=150`、`MAX_ITEMS=220`、`COVERED=0.50`/`PARTIAL=0.42`（tunable） |
| `backend/src/server.ts` | **MODIFIED（純加法）** | +`POST /api/checklist-revise`（10/min limiter + 413 cap，同 analyze-document）+`GET /api/checklist-domains`（無 limiter）。現有 route byte-identical |
| `checklists_bundle.json`（root，1.4MB） | **NEW** | 14 域 items(req/page/source_id/school_types)+clauses(si/covers/school_types/text)+src。backend runtime 載入（`../../../`，同 role_facts.json，Render 有） |
| `dev/checklists/_work/gen_checklists_bundle.py` | **NEW** | 由 `_work/<域>/checklist.json+clauses.json` 生成 bundle。**改清單後 re-run** |
| `app.html` | **MODIFIED（純加法）** | +`ReviewPanel` +`buildRevisedDocx` +`'review'` tab。`REVISE_BACKEND_URL` localhost→:8787 否則 onrender |

## 4. QC（雙路 verify）

**Backend（python e2e，真 OpenAI，:8787）：**
- ✅ HIGH-coverage：safety 中學 docx 文字 → domain=safety/secondary = **covered 198 / partial 10 / missing 0**（sim 0.677）。
- ✅ NEGATIVE control：無關活動文字 → **covered 1 / partial 5 / missing 202**（清晰區分）。
- ✅ 錯誤路徑：未知 domain → HTTP 400。
- ✅ `npm run check`（tsc --noEmit）+ `npm run build` 全 PASS。GET /api/checklist-domains 回 14 域。

**Frontend（browser，fetch-stub，:8095）：**
- ✅ Babel 編譯零錯；6 tabs（📝 文件修訂 就位）；window.docx + pdfjsLib loaded。
- ✅ 域 selector 由 GET 填充（3 opt）；提交 → 報告 render（對照 5 項、2 section、5 item card）。
- ✅ 缺漏/部分項 3 個「建議標準條文」`<details>`；來源連結帶 `#page=N`。
- ✅ 狀態篩選：揀「未見 2」→ 只剩 2 item。
- ✅ 「下載修訂建議 Word」→ 有效 docx blob（8365 bytes、PK header ✓）。

> 註：browser→backend 真 fetch 因 CORS（localhost 非 allowlist origin）未做整鏈；改用 backend python e2e + frontend stub 雙路覆蓋。Body shape 兩路一致。

## 5. 已知限制 / 待決定

1. **覆蓋率係估算** — embedding 相似度非語義理解；門檻 0.50/0.42 經 e2e 校過（match≈95% covered、unrelated≈97% missing）但可調（`checklistRevise.ts` 常數）。UI/docx 已明示「自動估算、人手覆核」。
2. **大域截斷** — curriculum 629 項 / school_governance 489 項；超 `MAX_ITEMS=220` 會截（UI 有提示）。如要全量，調高常數（embedding 一次 batch 仍 OK，但報告會好長）。
3. **無 LLM** — 純 embedding；要更準可加 LLM 覆核 borderline 項（Phase 2.5，有 token 成本）。
4. **Mobile shell 未有** — desktop React only（同 文件分析 / 政策範本，已知 scope）。
5. **bundle 公開** — checklists_bundle.json 喺 root，GitHub Pages 會 serve（公開、EDB 衍生內容，benign）。
6. **Deploy 與否** — 本 session **staged 未 deploy**（新 user-facing feature + 新 backend endpoint，留 Leonard review）。deploy 見 §6。

## 6. 一鍵 deploy（Leonard review 後）

於 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`：
```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && git push origin main
```
push = GitHub Pages（前端）+ Render（backend）**同時** auto-deploy。前端 `REVISE_BACKEND_URL` 自動指向 onrender；Render 會 build `checklistRevise.ts` + 載入 root `checklists_bundle.json`。deploy 後 smoke：`curl https://edb-knowledge.onrender.com/api/checklist-domains`。

## 7. 重生流程（清單更新後）

```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/checklists/_work/gen_checklists_bundle.py && python3 dev/checklists/_work/gen_templates_manifest.py
```
→ 覆寫 `checklists_bundle.json`（backend）+ `policy_templates.json`（前端範本 tab）。**DOC_SYNC**：清單/clauses 改 → 必 re-run 兩個 generator。
