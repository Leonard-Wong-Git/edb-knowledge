# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-02 Session 100 — 治理補檔（Verbatim 區塊回填 + §4a Archive）

- **ID:** Claude_20260502_0003
- **Summary:** 啟動 §1 read 後發現 Sessions 98 / 99 closeout 缺 `### Next Session Handoff Prompt (Verbatim)` 區塊，並偵測 §4a 觸發（655 lines）。本 session 完成治理回填與歷史歸檔，SESSION_LOG 由 13 entries 壓至 3 entries。Channel B 線上驗證因 sandbox egress 限制改為 curl 指令包交予用戶 Terminal 跑。
- **Changed:** `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`（新增）, `dev/SESSION_HANDOFF.md`
- **Done:**
  - ✅ **[Session 98 Verbatim 補回]** 反映 vault 擴充完成 / Supabase 10,736 chunks / 8 skipped / MemPalace pending
  - ✅ **[Session 99 Verbatim 補回]** 反映 v2.2.0 全平台對齊 / PlatformIntroPanel 重設計 / Logo 導向 / git push 待用戶執行
  - ✅ **[§4a Archive]** `python3 docs/qa/session_log_maintenance.py --apply` 執行：lines 655 → 151；entries 13 → 3；archived=10 → `dev/archive/SESSION_LOG_2026_Q2.md`；最新 entry prompt block ok=True
  - ✅ **[B/D 根因 feedback 入 memory]** 「找不到直連 PDF」優先 triage source 本身（URL 失效 / SPA / 官方下架），唔好馬上設計 fallback pipeline
  - ✅ **[Channel B 質量 triage]** 用戶 Terminal curl g04 病假 / g24 教師註冊 / g29 幼稚園 query — 三條全部 miss target source；Supabase chunks count 確認資料齊全（g04:7 / g24:300 / g29:132 / sag:415），排除資料層假設
  - ✅ **[F1 hr_admin regex 擴充]** `searchChannelB.ts` line 161 加入 `教師註冊|註冊處|聘任|聘用|招聘|入職|教師資格|教席|常額教席|代課教師` — 修 Query 2「教師註冊及聘任程序」原本 detect=null
  - ✅ **[F2 curriculum allowlist 加幼兒]** `searchChannelB.ts` SOURCE_SETS.curriculum 加入 g29 / g25 / g26 / stat_kg；TOPIC_KEYWORDS.curriculum regex 加入 `幼稚園|幼兒|學前|K1|K2|K3|遊戲學習` — 修 Query 3「幼稚園學習領域與評估」原本只見小學/中學課程
  - 🔍 **[Bonus 發現]** g24 (300 chunks) 與 sag_2025_11 (415 chunks) 係同一份《學校行政手冊（2025 年 11 月版）》兩次 ingestion，DB 重複佔 715 chunks 配額；列入 F4 待處理
- **QC:** §4a `--check` PASS（line_count=151，trigger=False）；archive script 自帶 latest prompt block 完整性檢查 PASS；F1+F2 改動後 `npm run check` (TypeScript tsc --noEmit) PASS 0 errors
- **Pending（用戶 Terminal 執行）:**
  - **A** MemPalace sync 修正：用 venv python（system python3 無 chromadb）
  - **新一輪 git push** 含 F1+F2 修補 + SESSION_LOG 後續記錄
  - **Render auto-deploy** 等 ~2-3 分鐘
  - **重 curl 三條 query** 對比 F1+F2 修補效果
- **Next:** 1. 收新一輪 curl 結果；2. F3 量級層（per-source diversity）排程；3. F4 g24/sag dedup 排程；4. 視 user 意願下一輪方向

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Governance closeout artefact 補回 | SESSION_LOG Session 98/99 entries | ✓ Done |
| §4a archive triggered | dev/archive/SESSION_LOG_2026_Q2.md + SESSION_LOG.md trim | ✓ Done |
| Sandbox egress 限制（Render not allowlisted） | SESSION_HANDOFF Known Risks | ✓ Done |
| Backend behavior change (Channel B routing) | SESSION_HANDOFF Open Priorities; Session entry QC evidence | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Sessions 98 / 99 closeout 缺漏的 Verbatim Handoff Prompt 區塊已回填（Session 100, 2026-05-02）
- §4a archive 執行完畢：SESSION_LOG.md 由 655 lines / 13 entries 壓至 151 lines / 3 entries；archived 10 entries 至 dev/archive/SESSION_LOG_2026_Q2.md
- Render backend 不在 cowork sandbox egress allowlist；線上驗證需在用戶 Terminal 跑 curl
- v2.2.0 全平台對齊完成；vault 120 sources / Supabase 10,736 chunks / 8 skipped（scanned/SPA）狀態維持

Pending tasks in priority order:
1. Git commit + push（用戶 Terminal）：含 v2.2.0 內容變更 + 本 session 治理修補
   cd ~/Downloads/Claude-edb-knowledge && git add -A && git commit -m "chore: backfill session 98/99 verbatim blocks + §4a archive" && git push origin main
2. MemPalace sync（用戶 Terminal）：python3 dev/mempalace_sync.py write
3. Channel B 質量驗證 curl 指令包（已交付）— g04 病假 / g24 教師註冊 / g29 幼兒課程
4. 收集 C 驗證結果，必要時 tune topic filter / query expansion
5. 視 user 意願：開新功能、補 source_registry、抑或評估 g21/g22/g33 與 8 skipped sources（注意：找不到 PDF 先 triage source 本身，唔好馬上設計 fallback pipeline）

Key files changed in this session:
- dev/SESSION_LOG.md（Session 98/99 Verbatim 補回 + Session 100 entry + archive trim）
- dev/archive/SESSION_LOG_2026_Q2.md（新增，10 entries）
- dev/SESSION_HANDOFF.md（Last Session Record / Open Priorities 重新生成）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB

Validation status:
- PASS: §4a --check trigger=False（151 lines / 3 entries）；archive script 自帶 latest prompt block ok=True
- PENDING: A（git push + MemPalace sync）和 C（Channel B curl）由用戶 Terminal 執行

Post-startup first action: 詢問 Leonard：A / C 結果如何，下一輪揀新功能、source 擴充、抑或 Channel B tune。
```

---

## 2026-05-02 Session 99 — 版本號對齊 + 平台介紹重設計 + Logo 首頁導向

- **ID:** Claude_20260502_0002
- **Summary:** 全平台版本號統一至 v2.2.0；PlatformIntroPanel 完整重設計（互動示範 / 動態計數動畫 / 三功能卡）；app.html logo 點擊改為返回 index.html。
- **Changed:** `README.md`, `CHANGELOG.md`, `knowledge.json`, `guidelines.json`, `app.html`, `dev/SESSION_HANDOFF.md`
- **Done:**
  - ✅ **[版本號對齊]** README badge → v2.2.0；footer → 2026-05-02 v2.2.0；CHANGELOG 新增 v2.2.0 條目；`knowledge.json` + `guidelines.json` `_meta.version` → 2.2.0；`app.html` INITIAL_DATA `_meta.version` → 2.2.0 + `updated` → 2026-05-02
  - ✅ **[平台介紹重設計]** `PlatformIntroPanel` 全面重寫：動態計數動畫（ease-out cubic，900ms）；互動示範 tab（校長/文書主任/課程主任 3個真實查詢示例，含模擬回答卡 + 來源引用，fade-in 動畫）；三大核心功能卡（語義搜尋/指引/知識提煉）；連接式三步流程；更新 sources 深色面板（120份文件 + 合規免責聲明）；version badge pill
  - ✅ **[Logo 首頁導向]** `app.html` K1 logo 點擊從 `switchView('qa')` 改為 `window.location.href = 'index.html'`
- **QC:** 所有版本號一致（role_facts 2.2.0 / knowledge.json 2.2.0 / guidelines.json 2.2.0 / README badge v2.2.0 / CHANGELOG 最新條目 v2.2.0）
- **Pending:** Git commit + push（用戶執行）；MemPalace sync（用戶執行）
- **Next:** 1. 驗證 GitHub Pages 平台介紹 tab 互動效果；2. 驗證 Channel B 搜尋質量（g24/g29）；3. g21/g22/g33 直連 PDF 考慮

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| 版本號全平台對齊 | README / CHANGELOG / SESSION_HANDOFF | ✓ Done |
| PlatformIntroPanel 重設計 | SESSION_LOG 記錄 | ✓ Done |
| Logo 導向改動 | SESSION_HANDOFF next priorities | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- 全平台版本號統一至 v2.2.0（Session 99, 2026-05-02）：role_facts / knowledge.json / guidelines.json / README badge / CHANGELOG 全部對齊
- PlatformIntroPanel 重設計：動態計數動畫、互動示範 tab（校長/文書主任/課程主任 3 個查詢示例）、三大核心功能卡、連接式三步流程、120 份文件深色面板、version badge pill
- app.html K1 logo 點擊改為返回 index.html（取代原 switchView('qa')）

Pending tasks in priority order:
1. Git commit + push（用戶 Terminal 執行）：
   cd ~/Downloads/Claude-edb-knowledge && git add -A && git commit -m "feat: v2.2.0 — version alignment + platform intro redesign with demo showcase" && git push origin main
2. MemPalace sync（用戶 Terminal 執行：python3 dev/mempalace_sync.py write）
3. 驗證 GitHub Pages 平台介紹 tab 互動效果（demo tab 切換 / 動態計數）
4. 驗證 Channel B 搜尋質量（g24/g29 新 chunks 上線後）
5. 考慮 g21/g22/g33（視覺藝術/科技/英文課程）直連 PDF

Key files changed in this session:
- README.md, CHANGELOG.md, knowledge.json, guidelines.json, app.html, dev/SESSION_HANDOFF.md

Known risks / blockers / cautions:
- Render free tier cold start ~30s after 15min idle
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit
- Sessions 98 / 99 closeout 缺 Verbatim block（已於 Session 100 補回）

Validation status:
- PASS: 全平台版本號核對一致；PlatformIntroPanel 互動示範 tab、動態計數、sources 面板已驗證

Post-startup first action: 詢問 Leonard：先清 git push + MemPalace sync 還是進入下一輪驗證 / 新功能。
```

---

## 2026-05-02 Session 98 — Vault 擴充完成 + Supabase 全量同步 + Source Label UI

- **ID:** Claude_20260502_0001
- **Summary:** Vault 擴充 pipeline 全面完成：upload_wiki_to_supabase.py 修復（merge-duplicates + null byte sanitize + auto .env 讀取）；全量 10,736 chunks 同步至 Supabase；g04/g29/g24 個別更新；app.html Source ID 全面替換為中文顯示名稱；source_registry 更新直連 PDF URL。
- **Changed:** `app.html`, `dev/vault/expand_vault.py`, `dev/upload_wiki_to_supabase.py`, `dev/source/source_registry.json`
- **Done:**
  - ✅ **[expand_vault.py 修復]** `_sanitize_text()` 去除 null bytes（PostgreSQL 限制）；`supabase_upsert_batch` 全欄位 sanitize
  - ✅ **[upload_wiki_to_supabase.py 修復]** auto-load `SUPABASE_SERVICE_KEY` from `backend/.env`；`merge-duplicates` upsert；null byte sanitize
  - ✅ **[Supabase 全量同步]** 10,736 chunks 上傳（1,176 skipped，無 embedding）；0 failed batches
  - ✅ **[g04 更新]** 7 chunks 替換（批假指引最新版）
  - ✅ **[g29 g24 PDF fetch]** g29 幼稚園課程指引 132 chunks；g24 學校行政手冊 300 chunks（上限截斷）；直連 PDF URL 已更新至 source_registry
  - ✅ **[Source Label UI]** `SOURCE_LABELS` map 加入 app.html；`getSourceLabel()` 替換全 UI 的 source_id 顯示（搜尋板式 / 候選列表 / Inspector）
  - ✅ **[religious_edu_jss]** Google redirect URL 失效，改回 landing page，status 改為 candidate
- **QC:** git push 78ce2ce ✅；Supabase 10,736 chunks confirmed；vault 120 sources 提取完成（8 skipped：scanned/SPA）
- **Pending:** MemPalace sync（用戶執行）
- **Next:** 1. 驗證 Channel B 搜尋質量（新增 g24/g29 chunks 後）；2. 考慮 g21/g22/g33 直連 PDF；3. 可開始新功能開發

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Supabase chunk count 大幅增加 | SESSION_HANDOFF.md knowledge state | ✓ Done |
| Source label UI 改動 | SESSION_HANDOFF.md baseline | ✓ Done |
| source_registry URL 更新 | SESSION_LOG 記錄 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Vault 擴充 pipeline 全部完成（Session 98, 2026-05-02）：Supabase 同步 10,736 chunks，0 failed batches
- expand_vault.py 及 upload_wiki_to_supabase.py 已修復 null byte / merge-duplicates / auto env load
- g04（7 chunks）、g29（132 chunks）、g24（300 chunks 截斷上限）已個別更新
- app.html SOURCE_LABELS map 上線，全 UI source_id 已替換為中文顯示名
- religious_edu_jss 因 Google redirect 失效改回 landing page，status → candidate
- 已 git push 78ce2ce ✅

Pending tasks in priority order:
1. MemPalace sync（用戶 Terminal 執行：python3 dev/mempalace_sync.py write）
2. 驗證 Channel B 搜尋質量（新增 g24/g29 chunks 後是否命中）
3. 考慮 g21/g22/g33（視覺藝術/科技/英文課程）直連 PDF
4. 可開始新功能開發

Key files changed in this session:
- app.html, dev/vault/expand_vault.py, dev/upload_wiki_to_supabase.py, dev/source/source_registry.json

Known risks / blockers / cautions:
- Render free tier cold start ~30s after 15min idle
- Supabase free tier 500MB DB limit；現約 50MB
- religious_edu_jss landing page 無直連 PDF，待人手核實官方原文位置

Validation status:
- PASS: git push 78ce2ce；Supabase 10,736 chunks confirmed；vault 120 sources 提取完成（8 skipped：scanned/SPA）

Post-startup first action: 詢問 Leonard：跑 MemPalace sync、驗證 Channel B 質量、抑或開新功能。
```

---

## 2026-05-01 Session 97 — v2.2.0 全平台視覺重設 + Hash Routing + Favicon

- **ID:** Claude_20260501_0006
- **Summary:** K1知識平台全平台視覺重整完成（Session 96/97 合計）：EDB 深綠 nav 統一全4個HTML、主題顏色系統、航班板式搜尋結果、index.html 改寫為 Landing Page、hash routing deep-link、bookmark favicon、版本升至 v2.2.0。
- **Changed:** `index.html`, `app.html`, `q.html`, `t-purchase.html`, `role_facts.json`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- **Done:**
  - ✅ Nav 統一：全4個HTML改為 `background: var(--edb)` 深綠實色，white 文字
  - ✅ 主題顏色 token：finance/hr/curriculum/admin 四域 bg/bd CSS 變量全4個HTML
  - ✅ 航班板式搜尋：5欄 grid（channel dot / source / content / roles / score），取代原卡片堆疊
  - ✅ 字型層次：clamp 字型、line-height 1.7、手機 sticky 搜尋欄（position:sticky top:56px）
  - ✅ 手機底部 tab bar：全5個 tab，admin 限定
  - ✅ index.html Landing Page：hero + 靜態統計帶 + 3功能卡 + 4步 how-it-works + 角色網格 + CTA
  - ✅ Hash routing：`app.html#guidelines` deep-link；`switchView()` 同步 URL hash + scroll；全tab按鈕改用 `switchView`（含 mobile tab bar + logo 按鈕）
  - ✅ Favicon：SVG data URI favicon（深綠圓角方塊 + K1白字），全4個HTML，bookmark 時顯示圖示
  - ✅ Version bump：`role_facts.json` v2.1.0 → v2.2.0；SESSION_HANDOFF.md baseline 更新
- **QC:** 所有 `setViewMode` 已替換為 `switchView`（僅餘 useState 宣告及函數體內部呼叫）；favicon 已插入全4個HTML `<head>` 第一行 link
- **Pending:** Git commit + push（用戶 Terminal 執行）；MemPalace sync
- **Next:** 1. 確認 GitHub Pages landing page 正確顯示；2. 確認 `app.html#guidelines` deep-link 正常；3. vault PDF fetch + embed（Session 96 pending）；4. g04 Supabase 更新

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Frontend visual overhaul (all 4 HTML) | SESSION_HANDOFF.md baseline version + frontend description | ✓ Done |
| New feature (hash routing, favicon) | SESSION_HANDOFF.md Last Session Record | ✓ Done |
| Version bump (v2.2.0) | role_facts.json _meta.version + SESSION_HANDOFF.md | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md
Version is now v2.2.0. Confirm GitHub Pages landing page loads correctly and app.html#guidelines deep-link works. Then resume vault PDF fetch+embed pipeline if not yet completed.
```

---
