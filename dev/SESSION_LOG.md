# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-01 Session 92 — Phase 2 Channel B Online (Supabase pgvector)

- **ID:** Claude_20260501_0001
- **Summary:** Channel B 全面上線：Supabase pgvector 建立、2,822 chunks 上傳、權限修復、wikiRepository.ts 改用 direct fetch()、debug endpoint 清除、Combined A+B search 線上驗證通過。
- **Changed:** `backend/src/lib/wikiRepository.ts`, `backend/src/server.ts`, `backend/src/config/env.ts`, `backend/package.json`, `dev/upload_wiki_to_supabase.py`, `dev/supabase_setup.sql`（新增）, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- **Done:**
  - Supabase project `edb-knowledge` 建立，pgvector schema + `match_wiki_chunks` function（text 參數，內部 `::vector` cast）
  - `upload_wiki_to_supabase.py` 全局 dedup by id 後批次上傳，2,822 chunks 成功，52 skipped（無 embedding）
  - wikiRepository.ts 棄用 supabase-js，改 direct fetch() + `toFixed(8)` embedding string
  - Render env vars 設定（SUPABASE_URL + SUPABASE_ANON_KEY）；Manual Deploy 成功
  - 根本問題修復：anon role 缺少 `GRANT USAGE ON SCHEMA public`；SQL 執行後 /debug-b 確認 table ✅ + RPC ✅
  - 移除 `/debug-b` diagnostic endpoint 及 wikiRepo verbose logging
  - 線上驗證：`/api/search/combined?query=採購程序` → A: 993 B: 8 ✅
- **QC:** Combined A+B curl PASS (A:993 B:8)；TypeScript build PASS；Render deploy PASS
- **Pending:** git push（sandbox 無法 SSH，由用戶執行）；UI QA browser pass；rate limiting
- **Next:** 1. UI QA browser pass（app.html Channel B / Combined 顯示）；2. Rate limiting；3. Channel A embedding cache

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| External API / service change (Supabase) | CODEBASE_CONTEXT.md External Services; SESSION_HANDOFF.md Supabase notes | ✓ Done |
| Backend behavior change | SESSION_HANDOFF.md baseline; SESSION_LOG.md | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state (Session 92, 2026-05-01):
- Phase 2 Channel B 完全上線：Supabase pgvector 2,822 chunks；Combined A+B online 驗證 PASS (A:993 B:8)
- Render backend: https://edb-knowledge.onrender.com (Channel A + B + Combined + analyzeCircular)
- Supabase: https://youkcekbrbywuqjxgibe.supabase.co；anon key 查詢；service key 只用於上傳

Pending tasks in priority order:
1. git push（若上次 session 未完成：cd ~/Downloads/Claude-edb-knowledge && git push origin main）
2. Optional UI QA browser pass（app.html Channel B / Combined 搜尋顯示）
3. Rate limiting（node-rate-limiter-flexible，10 req/min per IP，公開前必做）
4. Channel A embedding cache（啟動時預計算 1,001 facts embeddings）
5. MemPalace: keep /Users/leonard/mempalace/palace.pre-recovery.20260421_0838 until stable

Key Supabase technical notes (in SESSION_HANDOFF.md):
- anon role 必須有 GRANT USAGE ON SCHEMA public + GRANT SELECT ON wiki_chunks
- match_wiki_chunks function 用 text 參數（非 vector），內部做 ::vector cast
- Upload 用 service_role key；查詢用 anon key

Known risks:
- Render free tier cold start ~30s after 15min idle
- Supabase free tier 500MB DB limit
- MemPalace recovery workaround (hnsw:num_threads=1)

Post-startup first action: 確認 git push 狀態，然後詢問 Leonard：UI QA、rate limiting、還是其他優先項。
```

## 2026-05-01 Session 95 — Channel B UI 免責聲明 + g04 PDF 重新提取

- **ID:** Claude_20260501_0004
- **Summary:** Session 95 完成 Priority 2（Channel B UI 免責聲明）及 Priority 1（g04 vault 從真實 PDF 重新提取）。g04 由 knowledge-based LLM 內容替換為 EMBC1/2006 附錄「教職員批假指引」、EDBC16/2015（侍產假）、EDBC16/2018（產假延長14週）及病假常見問題的真實 PDF 提取內容，7 chunks（原 3 chunks）。Supabase 更新腳本 `dev/update_g04_supabase.py` 已備妥，待用戶本地執行。
- **Changed:** `app.html`（Channel B/AB 免責聲明），`dev/vault/g04/extract_g04.txt`（完整重寫），`dev/update_g04_supabase.py`（新增）, `dev/SESSION_HANDOFF.md`
- **Done:**
  - **Channel B UI 免責聲明**：`app.html` Channel B / A+B 結果區加入黃色警示框「來源文件搜尋結果由 AI 語義搜尋生成，行政及財務類查詢結果準確性待確認，建議對照教育局官方原文核實」
  - **g04 vault 重寫**：`dev/vault/g04/extract_g04.txt` 從以下真實 PDF 重新提取：
    - EMBC1/2006：一般原則、教學/非教學人員假期類型、須事先徵批的假期、無薪假期影響（晉升/公積金/增薪）、假期記錄要求
    - EDBC16/2015：侍產假（服務年資40週、5天全薪、預計出生前4週至出生後14週、通知要求、批核程序）
    - EDBC16/2018：產假延長至14週（由2019年1月1日起，2020年12月11日《僱傭條例》生效）
    - 病假常見問題：首年28天/其後48天/上限168天/120天門檻按月更新/超過兩天需醫生證明
  - **update_g04_supabase.py**：一鍵腳本 delete 舊 g04 → embed 新 7 chunks → upload Supabase；同步更新 local wiki_index.json
  - **預期 Supabase 更新後**：g04 由 3 chunks → 7 chunks；`教職員請假` 查詢應見 g04 真實內容
- **QC:** vault 分塊驗證：7 chunks，avg 592 chars，內容覆蓋所有假期類型 ✅
- **Pending:**
  - 用戶需執行（Terminal）：
    1. `rm -f .git/index.lock`（如有）
    2. `cd ~/Downloads/Claude-edb-knowledge && git add dev/vault/g04/extract_g04.txt dev/update_g04_supabase.py dev/upload_wiki_to_supabase.py && git commit -m "feat(g04): replace knowledge-based extract with real PDF content (EMBC1/2006, EDBC16/2015, EDBC16/2018, sick leave FAQ)" && git push origin main`
    3. `SUPABASE_SERVICE_KEY=sb-... python3 dev/update_g04_supabase.py`（在 repo 根目錄）
  - MemPalace sync：`python3 dev/mempalace_sync.py write`
- **Next:** 1. Vault 擴充全 AI pipeline（104 sources pending）；2. Channel A embedding cache

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| g04 vault content change | SESSION_HANDOFF.md Open Priorities | ✓ Done |
| New tooling (update_g04_supabase.py) | SESSION_LOG.md | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state (Session 95, 2026-05-01):
- v2.1.2 online；Channel B topic filtering + UI 免責聲明 + g04 vault 重寫 全部完成
- g04 vault 已更新為真實 PDF 內容（7 chunks）；Supabase 更新待用戶執行 update_g04_supabase.py

Priority for next session:
1. 確認 g04 Supabase 更新已執行（如未執行：SUPABASE_SERVICE_KEY=sb-... python3 dev/update_g04_supabase.py）
2. Vault 擴充全 AI pipeline：104 個 source registry 來源未提取；設計 pdftotext → chunk → embed → Supabase 自動化流程
3. Channel A embedding cache（startup 預計算 1,001 embeddings，消除 per-query batch call）
```

## 2026-05-01 Session 94 — Channel B Topic Filtering + MemPalace Integration

- **ID:** Claude_20260501_0003
- **Summary:** Channel B 系統性品質修正：keyword-based topic detection + source allowlist + query expansion；三個原問題查詢（採購門檻/單一報價/教職員請假）全部驗證通過。加入 MemPalace 整合腳本 `dev/mempalace_sync.py`。
- **Changed:** `backend/src/api/searchChannelB.ts`, `backend/src/lib/wikiRepository.ts`, `dev/mempalace_sync.py`（新增）, `dev/SESSION_HANDOFF.md`
- **Done:**
  - **MemPalace 整合**：`dev/mempalace_sync.py` write/query/list/stats；7 sessions + handoff snapshot 已寫入；session 流程：query 開始、write 結束
  - **wikiRepository.ts**：`WikiSearchOptions` 加 `sourceIds?: string[]`；post-filter by source_id allowlist
  - **searchChannelB.ts**：
    - `SOURCE_SETS`：finance→g01+g02+coa_imc（排 SAG）；hr_admin→g04+g05+sag；activity→g03；curriculum→所有課程指引
    - `TOPIC_KEYWORDS`：keyword regex → category detection
    - `detectQueryCategory()`：查詢分類函數
    - `QUERY_EXPANSIONS` + `expandQuery()`：finance="採購程序 財政限額 報價 招標 採購指引"等，解決「門檻」embedding 偏移問題
    - `effectiveMinScore`：topic filter 啟動時降至 min(user_score, 0.08)
    - `enable_topic_filter?: boolean`（default: true）
  - **診斷發現**：「採購門檻」scoring 低因「門檻」embedding 被 SAG 教師註冊語境拉偏；query expansion 解決
- **QC:** curl 驗證全 PASS：採購門檻→g01+g02 ✅；單一報價→g01+g02 ✅；教職員請假→sag+g05 ✅；學校管治（無 filter）→多來源 ✅
- **Pending:** g04 PDF 重新提取；Channel B UI 免責聲明；vault 擴充
- **Next:** 1. g04 從 PDF 重新提取；2. Channel B UI 加免責聲明；3. Vault 擴充全 AI pipeline（104 sources pending）；4. Channel A embedding cache

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Channel B search behavior change | SESSION_HANDOFF.md Open Priorities | ✓ Done |
| MemPalace tooling added | SESSION_HANDOFF.md baseline | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state (Session 94, 2026-05-01):
- v2.1.2 online；Channel B topic filtering 完成並驗證：採購→g01+g02，HR→sag+g05
- MemPalace: dev/mempalace_sync.py；session 開始 query，結束 write

Priority for next session:
1. g04 從 PDF 重新提取（現為 knowledge-based LLM content，非真實 PDF）
2. Channel B UI 加免責聲明（行政財務查詢結果準確性待確認）
3. Vault 擴充：104 sources 未提取；全 AI pipeline (pdftotext → chunk → embed → Supabase)
4. Channel A embedding cache（startup 預計算 1,001 embeddings）
```

## 2026-05-01 Session 93 — UI QA + Rate Limiting + Channel B Spot-check

- **ID:** Claude_20260501_0002
- **Summary:** UI QA 發現 SEN 搜尋在 Channel A (case-sensitive) 及 Channel B (min_score 過高) 均無結果；修復後加入三項 UX 改進、後端 rate limiting、及 Channel B 內容抽查。
- **Changed:** `backend/src/api/searchChannelA.ts`, `backend/src/server.ts`, `app.html`, `bump_version.py`, `dev/SESSION_HANDOFF.md`
- **Done:**
  - **Channel A → Backend Semantic Search**：runChannelA 改用 `/api/search/channel-a` backend，取代本地 keyword 搜尋，支援語義搜尋 + LLM synthesis
  - **搜尋 synthesis 統一**：Channel A 加入 `synthesize: true`；A/B/AB 三個 channel 均有整理答案；標籤分別顯示「已核實事實摘要」vs「來源文件摘要」
  - **Loading text**：加入「正在語義搜尋，稍候片刻…（首次查詢約需 10–30 秒）」提示
  - **近似事實 dedup**：前端 IIFE 以首 60 字去重，避免顯示重複事實
  - **Rate limiting**：純 TypeScript in-memory 滑動窗口限速（10 req/min/IP），`server.ts` 加 X-Forwarded-For 支援 Render；429 回應繁中錯誤訊息；前端 catch 429 顯示提示
  - **min_score 調整**：Channel B + Combined 由 0.22 降至 0.15，修復 SEN/短詞無結果問題
  - **Channel label 更新**："離線可用" → "語義搜尋"
  - **版本 bump_version.py 修正**：改追蹤 app.html（原追蹤不存在的 k1-dashboard.html）
  - **版本更新**：v2.1.1 → v2.1.2
  - **Channel B 內容抽查**：確認系統性品質問題（見下）
- **QC:** Rate limit curl PASS (429 on 11th req)；UI 429 error message PASS；SEN search A+B PASS
- **Channel B 品質問題（已確認）：**
  - "採購門檻" → 返回教師註冊內容（錯誤）：SAG (415 chunks) 壓倒 g01 (32 chunks)
  - "單一報價" → 零結果：g01 內容太少，語義向量相似度未達 threshold
  - "教職員請假" → 返回教師資歷內容（錯誤）：同上問題
  - **根本原因**：wiki_index SAG 佔 415/2874 chunks (14%)；g01 行政財務指引僅 32 chunks；g04 為 knowledge-based extract（非 PDF）
- **Pending:** SESSION_LOG.md 此條目 commit；Channel B topic filtering（下 session 首要）
- **Next:** 1. Channel B topic-aware filtering（偵測 finance/HR topic，只搜對應 chunks）；2. g04 從 PDF 重新提取；3. Channel B UI 免責聲明；4. Vault 擴充（全 AI pipeline，104 sources pending）；5. Channel A embedding cache

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Backend API behavior change (Channel A → semantic) | SESSION_HANDOFF.md baseline | ✓ Done |
| Rate limiting added | SESSION_HANDOFF.md baseline | ✓ Done |
| Channel B quality issues confirmed | SESSION_HANDOFF.md Open Priorities | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state (Session 93, 2026-05-01):
- v2.1.2 online；Channel A + B + Combined 均有語義搜尋 + LLM synthesis
- Rate limiting: 10 req/min/IP sliding window (in-memory, server.ts)；前端 429 提示 ✅
- Channel B 系統性品質問題確認：SAG dominates (415/2874 chunks)；g01 admin guide 僅 32 chunks

Priority for next session:
1. Channel B topic filtering：偵測 query topic (finance/HR/curriculum)，filter wiki_chunks by source_id before cosine search
2. g04 重新從 PDF 提取（現為 knowledge-based，非真實 PDF content）
3. Channel B UI 加免責聲明（行政財務查詢結果準確性待確認）
4. Vault 擴充：104 sources 未提取；考慮全 AI pipeline (pdftotext → chunk → embed → Supabase)
5. Channel A embedding cache（startup 預計算 1,001 embeddings）

Key quality data:
- wiki_index: 2,874 chunks; SAG 415, SEN guides 75–275 each, g01 admin guide 32
- g04 is LLM-generated (not PDF-extracted) — verify before using in production
```

## 2026-04-30 Session 88 — 知識三層同步修復 (109 → 1,001 facts)

- **ID:** Claude_20260430_0000
- **Summary:** 系統審計發現 `dev/knowledge/role_facts.json`（1,001 條，v2.1.0）與 repo root `role_facts.json`（109 條，v2.0.0）及 `knowledge.json`（109 條，v1.4.0）嚴重脫節；Session 79 審批的 892 個新事實未有同步到 backend 和公開 API。本 session 執行三層同步修復。
- **Changed:** `role_facts.json`（repo root）, `knowledge.json`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- **Done:** 以 `dev/knowledge/role_facts.json` 為單一真相來源，覆寫 repo root `role_facts.json` 及 `knowledge.json`；三層均為 1,001 facts / v2.1.0 / updated 2026-04-30。
- **QC:** 三層 fact 數核對 PASS (1,001 = 1,001 = 1,001)；q.html flatten rows = 1,001；採購搜尋命中 249 條；CPD/專業發展命中 31 條；`session_log_maintenance.py --check` trigger=False (219 lines, 4 entries)。
- **Pending:** Circular System `_write_policy_signal()`；Phase 4 指引文件庫雙重排序；Optional UI QA pass。
- **Next:** 1. Circular System 落地；2. Phase 4 `sub_category`；3. UI QA。
- **Risks:** Channel A backend 現在注入 1,001 facts per query — token usage 需監察。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Knowledge data sync | SESSION_HANDOFF.md baseline 知識狀態; SESSION_LOG.md 本條目 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- 知識三層同步已修復（Session 88, 2026-04-30）：role_facts.json / knowledge.json / dev/knowledge/role_facts.json 全部統一為 1,001 facts / v2.1.0。
- q.html 和 backend Channel A 現在都使用最新 1,001 條事實。
- 最新 commit 包含 role_facts.json + knowledge.json 更新，待 push 到 GitHub。

Pending tasks in priority order:
1. Circular System: edb_scraper.py `_write_policy_signal()` 落地（持續 deferred）。
2. Phase 4: 指引文件庫 dual sort with `sub_category` (category → sub_category → time desc)。
3. Optional UI QA: browser visual pass on index.html / q.html / t-purchase.html / app.html。
4. MemPalace: keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until stable.

Key files changed this session:
- `role_facts.json` (repo root) — 109 → 1,001 facts, v2.1.0
- `knowledge.json` — 109 → 1,001 facts, v2.1.0
- `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md` — updated

Known risks / blockers / cautions:
- Channel A searchChannelA.ts now embeds ALL 1,001 facts per query — monitor token usage.
- Channel B/A+B requires local backend (npm run dev) — not on GitHub Pages.
- Shared MemPalace recovery workaround (hnsw:num_threads=1); keep backup at /Users/leonard/mempalace/palace.pre-recovery.20260421_0838.
- User preference: use Chinese for instructions, arrangements, updates, and summaries.

Validation status:
- PASS: 三層 fact 數核對 (1,001 = 1,001 = 1,001); q.html flatten rows = 1,001; keyword search probe PASS.
- Pending push: role_facts.json + knowledge.json + governance files not yet pushed to GitHub.

Post-startup first action: 確認 push 狀態，詢問 Leonard 下一步：(1) git push 同步更新到 GitHub，(2) 繼續 Circular System 落地，(3) Phase 4 指引文件庫排序，或 (4) UI QA pass。
```

## 2026-04-22 Session 87 — GitHub Upload After Frontend Cleanup

- **ID:** Codex_20260422_0603
- **Summary:** Release / publish gate for the already-completed frontend copy cleanup, Quick Q&A local search, MemPalace governance setup, and session-log archive changes; prepared current `main` for GitHub upload.
- **Changed:** `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`; staged publish set also includes `.gitignore`, `index.html`, `t-purchase.html`, `q.html`, `app.html`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/archive/SESSION_LOG_2026_Q2.md`, `docs/qa/session_log_maintenance.py`
- **Done:** Confirmed branch `main`, remote `git@github.com:Leonard-Wong-Git/edb-knowledge.git`, reviewed diff scope, ran release-gate checks, committed `188f583`, pushed `main` to GitHub, then completed session closeout.
- **QC:** `git diff --check` PASS; `t-purchase.html` inline JS `node --check` PASS; `q.html` inline JS `node --check` PASS; `app.html` JSX parse via backend esbuild PASS; `knowledge.json` procurement probe returned expected threshold fact; `session_log_maintenance.py --check` PASS; `session_log_maintenance.py --self-test` PASS 5/5; final pre-closeout status was clean at `188f583`.
- **Pending:** Circular System `_write_policy_signal()`; Phase 4 guideline dual sort; optional browser visual pass; keep MemPalace recovery backup until stable.
- **Next:** 1. Continue Circular System policy signal integration; 2. Phase 4 `sub_category` sorting; 3. Optional visual/browser QA.
- **Risks:** GitHub Pages serves static files only; Channel B/A+B and Circular analysis still require local backend runtime; closeout-only governance edits are local until separately pushed.

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | N/A — GitHub upload only; no version/schema milestone changed |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Frontend copy cleanup, Quick Q&A local `knowledge.json` search, MemPalace governance updates, and session-log archive maintenance are complete.
- Latest product/governance changes were committed and pushed to GitHub `main` as `188f583` (`Polish frontend copy and quick QA search`) on 2026-04-22.
- `index.html`, `t-purchase.html`, `q.html`, and `app.html` now avoid public-facing internal design/dev/backend wording and no longer over-claim formal generation/export where only draft UI exists.
- `q.html` now searches local `knowledge.json` and renders matched facts with citations.
- Closeout-only governance edits to `dev/SESSION_HANDOFF.md` and `dev/SESSION_LOG.md` were made after commit `188f583`; push them later if GitHub should also carry this closeout record.

Pending tasks in priority order:
1. Circular System: implement/sync edb_scraper.py `_write_policy_signal()` in the Circular System repo so policy signals include the agreed `url` field.
2. Phase 4: 指引文件庫 dual sort with `sub_category` (category → sub_category → time desc).
3. Optional visual/browser pass on `index.html`, `q.html`, `t-purchase.html`, and `app.html`.
4. Keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until recovered shared MemPalace remains stable.

Key files changed in this session:
- Published commit `188f583`: `.gitignore`, `index.html`, `t-purchase.html`, `q.html`, `app.html`, `docs/qa/session_log_maintenance.py`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`
- Closeout-only local edits after push: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- GitHub Pages serves static files only; Channel B/A+B and Circular analysis still require local backend runtime.
- `q.html` local search is keyword-based; semantic/source-file search remains in `app.html` and requires local backend service.
- Shared MemPalace was rebuilt using a workaround from MemPalace issue #974 (`hnsw:num_threads=1`); old backup remains at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`.
- User preference: use Chinese for future instructions, arrangements, updates, and summaries.

Validation status:
- PASS: `git diff --check`; `t-purchase.html` inline JS `node --check`; `q.html` inline JS `node --check`; `app.html` JSX parse via backend esbuild; local `knowledge.json` procurement search probe; `session_log_maintenance.py --check`; `session_log_maintenance.py --apply`; `session_log_maintenance.py --self-test`.
- PASS: GitHub push succeeded, `main` updated from `2eaff8b` to `188f583`.

Post-startup first action: Ask Leonard whether to push the closeout-only governance edits, continue Circular System policy signal integration, start Phase 4 guideline dual sort, or run the optional browser visual QA pass.
```

## 2026-04-22 Session 86 — Frontend Copy Cleanup + Quick Q&A Local Search

- **ID:** Codex_20260422_0552
- **Summary:** Product / UI layer cleanup: made the new pages honest about current functionality, removed user-facing internal design/dev/backend wording, and made Quick Q&A use local `knowledge.json` search instead of fixed fake answers.
- **Changed:** `index.html`, `t-purchase.html`, `q.html`, `app.html`, `dev/SESSION_HANDOFF.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`
- **Done:** Removed public links to internal `dev/design/*` from the home page; changed template flow wording from "生成" to draft creation/source整理; removed formal `.docx/PDF` export claims where not connected; changed app-facing search/analysis copy away from AI/backend commands; added local fact matching + citation rendering in `q.html`; compacted handoff and archived older session log entries per §4a.
- **QC:** `t-purchase.html` inline JS `node --check` PASS; `q.html` inline JS `node --check` PASS; `app.html` JSX parse via backend esbuild PASS; app tail script `node --check` PASS; local `knowledge.json` search probe for `採購 50,000 以上流程` returns finance procurement threshold fact; session log maintenance `--apply` archived 6 entries and final `--check` PASS.
- **Pending:** Circular System `_write_policy_signal()`; Phase 4 guideline dual sort; keep MemPalace recovery backup until stable.
- **Next:** 1. Continue Circular System policy signal integration; 2. Phase 4 `sub_category` sorting; 3. Optional visual/browser pass on the cleaned frontend pages.
- **Risks:** `q.html` local search uses simple keyword scoring, not semantic search; Channel B/A+B and Circular analysis still need local backend service, but public error copy now avoids exposing commands.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal copy cleanup | Open home/Q&A/template/app pages | Scan visible copy | Public pages avoid internal design/dev/backend wording and over-promised generation/export claims | Main public copy updated; remaining matches are data facts, comments, PDF labels, or code identifiers | PASS |
| Template honesty | Template flow is not formal export-ready | View/click template CTA | UI says draft creation/source整理, not completed formal generation/export | `t-purchase.html` uses 建立草稿 / 草稿已建立 / 重新整理 wording; `.docx/PDF` claim removed from intro | PASS |
| Quick Q&A usable | `knowledge.json` present | Search `採購 50,000 以上流程` | Local facts return a relevant answer/citation path | Probe found finance procurement threshold fact; q.html renders top local matches with citations | PASS |
| Failure path | Backend not running | Use source-file/analysis features | User sees understandable unavailable message without terminal commands | App-facing copy says 本機分析服務/進階來源搜尋暫未連線; no `npm run dev`/API key in visible error copy | PASS |
| Regression | Inline JS/JSX changed | Run syntax/parse checks | No parse regression | `node --check` PASS for q/template/tail script; JSX esbuild parse PASS | PASS |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product behavior / tuning change | CODEBASE_CONTEXT.md Directory Map / AI Maintenance Log if stable product behavior changed | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Frontend copy cleanup and Quick Q&A local search were completed on 2026-04-22.
- `index.html`, `t-purchase.html`, `q.html`, and `app.html` now avoid public-facing internal design/dev/backend wording and no longer over-claim formal generation/export where only draft UI exists.
- `q.html` now searches local `knowledge.json` and renders matched facts with citations.
- Session closeout archived older `SESSION_LOG.md` entries into `dev/archive/SESSION_LOG_2026_Q2.md`; active log now keeps the 3 newest entries.

Pending tasks in priority order:
1. Circular System: implement/sync edb_scraper.py `_write_policy_signal()` in the Circular System repo.
2. Phase 4: 指引文件庫 dual sort with `sub_category`.
3. Optional visual/browser pass on the cleaned frontend pages.
4. Keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until recovered shared MemPalace remains stable.

Key files changed in this session:
- `index.html`, `t-purchase.html`, `q.html`, `app.html`
- `dev/SESSION_HANDOFF.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`

Known risks / blockers / cautions:
- `q.html` local search is keyword-based; semantic/source-file search remains in `app.html` and requires local backend service.
- Channel B/A+B and Circular analysis still require backend service; public error copy is intentionally user-friendly and does not expose terminal commands.
- Shared MemPalace was rebuilt using a workaround from MemPalace issue #974 (`hnsw:num_threads=1`); old backup remains at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`.

Validation status:
- PASS: `t-purchase.html` inline JS `node --check`; `q.html` inline JS `node --check`; `app.html` JSX parse via backend esbuild; app tail script `node --check`; local `knowledge.json` procurement search probe; session-log maintenance `--apply` and final `--check`.

Post-startup first action: Continue with Circular System policy signal integration, Phase 4 guideline dual sort, or run a browser visual pass on the cleaned frontend pages if user prioritizes UI QA.
```

## 2026-04-21 Session 85 — INIT Refresh + MemPalace Local Memory Setup

- **ID:** Codex_20260421_0708
- **Summary:** Development Governance Layer + local tooling setup: refreshed installed INIT governance rules and configured MemPalace for project memory/search.
- **Changed:** `.gitignore`, `AGENTS.md`, `docs/qa/session_log_maintenance.py`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`; local ignored files: `.venv/`, `mempalace.yaml`, `entities.json`, `dev/init_backup/20260421_065226_UTC/`
- **Done:** §5a root/write confirmations received; backup snapshot created; `mempalace 3.3.2` installed in `.venv`; `mempalace init . --yes` generated wing `claude_edb_knowledge`; `.claude/` excluded from mining; fixed `session_log_maintenance.py` heading parser and self-test expectations; recovered shared palace at `/Users/leonard/mempalace/palace`; mined this project into shared palace.
- **QC:** `mempalace --version` PASS; local status/search/wake-up PASS; shared `migrate --dry-run` extracted 5,126 drawers; recovery temp count PASS (5,126); shared `mine .` PASS (132 files processed, 4 skipped, 5,216 drawers filed); shared `status` PASS (6,785 drawers); shared search PASS; session log maintenance check/self-test PASS.
- **Pending:** Circular System `_write_policy_signal()`; Phase 4 guideline dual sort.
- **Next:** 1. Continue Circular System policy signal integration; 2. Phase 4 `sub_category` sorting; 3. Keep old MemPalace backup until recovered palace remains stable.
- **Risks:** Shared MemPalace recovery used GitHub issue #974 workaround (`hnsw:num_threads=1`) after ChromaDB Rust segfaults; old backup preserved at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal setup | `INSTALL_ROOT_OK` and `INSTALL_WRITE_OK` confirmed | Install and initialize MemPalace | Local CLI and project config available | `.venv/bin/mempalace --version` reports `3.3.2`; `mempalace.yaml` wing is `claude_edb_knowledge` | PASS |
| Boundary / local privacy | `.claude/` exists as local tool state | Dry-run mining after `.gitignore` update | `.claude/settings.local.json` is not mined | Second dry-run dropped from 273 files to 136 and no longer listed `.claude/settings.local.json` | PASS |
| Error / failure path | Full mine runs silently for several minutes | Interrupt/stop background process and inspect status | No runaway process; partial index either usable or clearly failed | Background PID stopped; `status` shows 3,963 drawers and search works | PASS with notes |
| Regression | Governance files already installed | Merge INIT updates without deleting existing project-specific user preferences | `AGENTS.md` retains existing content while adding newer INIT clauses | §13 User Work Preferences retained; INIT §1/§4a/§8b/§11/§12 updates merged | PASS |
| Regression | Session log entries use titled headings | Run maintenance check/self-test | Active log entry count is detected and self-tests pass | Parser fixed; `entry_count=8`; self-test `5/5` | PASS |
| Failure path | Shared palace path supplied | Run shared `mine .`, `migrate --dry-run`, `migrate --yes`, `repair --yes` | Either project is mined or failure is classified with evidence | Initial write/repair commands segfaulted in Chroma Rust layer; SQLite extraction + `hnsw:num_threads=1` rebuild recovered palace; final `mine/status/search` pass | PASS with notes |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Governance rule change (AGENTS.md) | INIT.md FILE 1 mirror; README if behavior is user-facing | ✓ Done — `AGENTS.md` merged from current `INIT.md`; README N/A (internal governance behavior) |
| Session-log maintenance utility added/changed | AGENTS.md §4a mechanism enforcement; INIT.md FILE 7 + FILE 1 §4a + §5a backup list; README*.md safeguards section; docs/qa/run_checks.sh | ✓ Done — row restored in checklist; AGENTS §4a/§5a aligned; README/run_checks N/A |
| Tech stack / build / dependency change | CODEBASE_CONTEXT.md Stack or Build section | ✓ Done — MemPalace local tooling recorded in Build & Run / Directory Map |
| External API / service change | CODEBASE_CONTEXT.md External Services block | ✓ Done — MemPalace official sources and local config recorded |
| Governance bootstrap / INIT execution | SESSION_HANDOFF.md Last Session Record; SESSION_LOG.md task entry + handoff prompt | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- INIT governance refresh, MemPalace setup, and session closeout were completed on 2026-04-21.
- MemPalace local project config is initialized for wing `claude_edb_knowledge`.
- Shared palace target is `/Users/leonard/mempalace/palace`; it was recovered and this project is mined successfully.

Pending tasks in priority order:
1. Circular System: implement/sync edb_scraper.py `_write_policy_signal()` in the Circular System repo.
2. Phase 4: 指引文件庫 dual sort with `sub_category`.
3. Keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until recovered shared MemPalace remains stable.

Key files changed in this session:
- `.gitignore`, `AGENTS.md`, `docs/qa/session_log_maintenance.py`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- Local ignored setup: `.venv/`, `mempalace.yaml`, `entities.json`, `dev/init_backup/20260421_065226_UTC/`

Known risks / blockers / cautions:
- Shared palace was rebuilt using a workaround from MemPalace issue #974 (`hnsw:num_threads=1`) after ChromaDB Rust segfaults.
- Old shared palace backup is preserved at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`.
- `.claude/` was added to `.gitignore` to prevent local tool settings from being mined.
- Channel B/A+B still requires backend `npm run dev`; not available on GitHub Pages alone.

Validation status:
- PASS: MemPalace binary found at `/Users/leonard/mempalace/.venv/bin/mempalace`; `init . --yes`; recovery count 5,126; shared `mine .`; shared `status` 6,785 drawers; shared search; session-log maintenance `--check` and `--apply`.

Post-startup first action: Continue with Circular System policy signal integration or Phase 4 guideline dual sort.
```

## 2026-04-20 Session 84 — Traditional Chinese UI Copy + Design Reference Rationale

1. Agent & Session ID: Codex_20260420_1438
2. Task summary: Responded to user concern that the site should use Traditional Chinese UI wording and clarified why `Preview.html`, `Prototype.html`, and `Spec.html` remain in `dev/design/`.
3. Layer classification: Product / UI Copy Layer + Documentation / Design Reference
4. Files changed:
   - `index.html` — MODIFIED: converted visible topic labels, footer counts, design CTA, and product prose to Traditional Chinese UI wording
   - `t-purchase.html` — MODIFIED: converted S3/S4/S5 visible labels and source-mode copy to Traditional Chinese UI wording
   - `q.html` — MODIFIED: converted Quick Q&A title, prompts, answer states, source badges, and no-confident-answer text to Traditional Chinese wording
   - `app.html` — MODIFIED: converted visible Channel A/B, policy-signal, source/result, and admin/review labels to Traditional Chinese wording where user-facing
   - `dev/design/Preview.html` — MODIFIED: converted visible design-preview copy to Traditional Chinese while keeping technical filenames as references
   - `dev/SESSION_HANDOFF.md` — MODIFIED: recorded Traditional Chinese copy baseline and `dev/design/` rationale
   - `dev/CODEBASE_CONTEXT.md` — MODIFIED: updated directory map, live-site URL, Channel A fact count, key decision, and AI Maintenance Log
5. Completed:
   - ✅ User-facing product copy now defaults to Traditional Chinese wording across the active static pages touched this session
   - ✅ `dev/design/` rationale clarified: kept as internal design reference / handoff SSOT, not as the canonical product flow
   - ✅ Stale footer fact count corrected to 1,001 approved facts / 7 topics
   - ✅ `.claude/` left untracked and untouched
6. Pending:
   - Circular System: `edb_scraper.py _write_policy_signal()` (deferred)
   - Phase 4: 指引文件庫 dual sort (`sub_category`)
   - Phase 5: Channel B 後台管理
7. Verification:
   - `sed -n '/<script>/,/<\\/script>/p' t-purchase.html | sed '1d;$d' | node --check` → PASS
   - `sed -n '547,4173p' app.html | node -e "...esbuild.transformSync(...,{loader:'jsx'})"` → PASS (`esbuild jsx parse PASS`)
   - `sed -n '/<script>/,/<\\/script>/p' q.html | sed '1d;$d' | node --check` → PASS
   - `rg -n ">[^<]*(min|Enter|Quick Q|chatbot|hallucinate|verified|Channel A|Channel B)[^<]*<" index.html t-purchase.html q.html app.html dev/design/Preview.html` → PASS with notes (remaining matches are filenames / technical labels / code-facing terms or AI/PDF/docx names)

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | User opens S1/S3/S6 pages | Scan visible UI labels | Primary UI wording is Traditional Chinese | Main labels, CTAs, source badges, and status copy converted | PASS |
| Design reference | User opens Preview page | Read design CTA and preview cards | Page explains Preview/Prototype/Spec as design artifacts in Traditional Chinese | Preview copy translated; filenames preserved for navigation | PASS |
| Regression | S3/S4/S5 scripts unchanged except copy | Run inline JS syntax check | No JavaScript syntax regression | `node --check` passes for `t-purchase.html` script | PASS |
| Regression | React SPA JSX changed only for copy | Run JSX parse check | JSX remains parseable | esbuild JSX transform passes | PASS |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product behavior / tuning change | CODEBASE_CONTEXT.md Directory Map / AI Maintenance Log if stable product behavior changed | ✓ Done |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | N/A — no version number or public data schema changed |

---
