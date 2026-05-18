# HANDOFF PACKAGE — EDB K1 知識平台

> 給接手呢個專案嘅**新 AI agent**。本文件由 Claude 經**實測**製作，原 Session `Claude_20260516_1652`（S110），**Session `Claude_20260516_1952`（S111 truth-pass v2）重新實測校正**：每個數字 / 架構斷言都 verify 過 actual code / data / git，**唔係抄文檔**。原因：Leonard 唔完全信任既有文檔；實測確認文檔（連本「快照」自己）會 drift（見 §2 元教訓 + §5）。

---

## 0. 你係邊個 / 點用呢份文件

- 你係接手嘅 AI agent。**Leonard**（Education Consultant，本專案 owner + 唯一 admin / 知識策展者）想要一個乾淨、可信嘅交接。
- 本文件係 **self-contained 可信狀態快照 + 接手指南**，凌駕「抄返舊文檔」嘅做法。
- **起手序（強制，AGENTS.md §1）**：先讀 `AGENTS.md`（governance SSOT），再按序讀
  `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/CODEBASE_CONTEXT.md` → `dev/PROJECT_MASTER_SPEC.md`。
  本文件係嗰四份之上嘅可信摘要 — 文檔與實際 code 衝突時，**以 code/data 為準**。
- 環境：repo root = `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（**路徑含空格，所有 shell 指令必須雙引號包覆絕對路徑**）。Leonard 偏好：永遠俾完整絕對路徑指令 + `&&` 串連成一個 paste-and-run block；多步前講明 working directory。

## 1. 一句話：呢個系統做乜（可信，長期不變）

為香港中小學 / 幼稚園學校管理人員提供一個**有根有據、可追溯到 EDB 官方文件原文**嘅政策知識查詢平台。核心價值係**可信度與可追溯性**，唔係 AI 自由發揮。詳見 `dev/PROJECT_MASTER_SPEC.md` §A（系統定位 / 不變量 / 「呢個系統唔係乜」）。

## 2. 已驗證嘅當前狀態（2026-05-16 Session 111 truth-pass v2 重新實測 — 可放心引用）

> ⚠️ **元教訓**：本「乾淨可信快照」由 Session 110 製作後，**同一日內自己就 drift 咗**（dedup 792→455 + HEAD 推進 8 個 commit，S110 自己嘅編輯又從未 commit）。Session 111 接手時連呢份都係 stale。下面係 Session 111 重新對齊嘅值；**仍然：load-bearing 數字動手前 verify actual code/data/git，連本表都當線索。**

| 項 | 已驗證值 | 驗證方法 |
|---|---|---|
| 版本 / git | v2.3.0；`main` = `origin/main` @ `ae31084`（**S110 寫嘅 `c78685f` 之後仲有 8 個 2026-05-16 commit，已過時**）；working tree 有未 commit 嘅 Session 111 truth-pass v2 文檔修正（5 dev 檔 + 本檔） | `git log` / `git status` |
| 知識三層同步 | `role_facts.json` 與 `dev/knowledge/role_facts.json` **byte-identical（md5 一致）**，`knowledge.json` 同為 v2.3.0；`_meta.stats = {facts:`**455**`, chunks:10736, sources:120, guidelines:39, topics:7}`（2026-05-16 dedup 792→455，commit `711f911`，reversible log `dev/DEDUP_LOG_2026-05-16.md`）。E.2「三層脫節」風險現時 **clean** ✅ | md5 + JSON parse |
| 指引 vs 來源（易混，4 數字）| `app.html` `GUIDELINES_REGISTRY` = **148**（用戶內庫全集，全 channel 知識基礎）；`guidelines.json` = **39**（公開端點，148 嘅嚴格子集，v2.2.0）；`source_registry.json` = **151**；vault-extracted = **120**（= stats.sources）。「39 是否擴到 148」= **OPEN DECISION**（PROJECT_MASTER_SPEC §B.1，本次未收斂）| JSON count + grep registry |
| Backend | 編譯正常；Channel B = **Supabase pgvector**（`match_wiki_chunks` RPC，非本地 wiki_index）；線上 `https://edb-knowledge.onrender.com`（Render free tier，冷啟 ~30s）。**S116：RPC live 真實簽名 = `(query_embedding TEXT,...)` 內部 `::vector` cast（`schema.sql` 曾 drift 成 vector(1536) → S116 PGRST203 live 事故，已修；任何 RPC DDL 前必 INSPECT live，PMS §E.13）；函數現 plpgsql VOLATILE + `set local ivfflat.probes=8`（CB-2 PLAN-1 Stage-1 FULL PASS，生產現行 probes=8；Stage 2 未做＝promote 未完成）。🔴 `searchCombined.ts` `.catch` 隱形化 Channel B 例外（fake「未配置」）= deferred promote-blocker。** | `select pg_get_functiondef` live / PMS §C.4·§E.13 |
| 搜尋參數 | min_score default：**A=0.1，B/AB=0.22**（已對齊 code） | grep `searchChannel*.ts` |
| Mobile UI | `app.html` mobile search 已 ship 並接 `/api/search/combined`；`index.html` / `q.html` / `t-purchase.html` / `app.html#guidelines` 嘅 mobile content **未 render** | SESSION_HANDOFF + code |

> 會逐 session 變嘅數字，永遠以 `dev/SESSION_HANDOFF.md` Current Baseline 為準；但本 session 實測證明連 SESSION_HANDOFF 都會 drift，**load-bearing 常數動手前一律 verify code/data**。

## 3. 邊度亂 / 接手要小心（Leonard 明示 codebase 偏亂難維護）

- `app.html` = **4,759 行單檔 React SPA**（CDN React/Babel/Tailwind，零 build pipeline）— 主要複雜度集中地。大改用 PROJECT_MASTER_SPEC §D.2 兩步寫法（先 Write CSS+HTML 留佔位，再 Edit 換 JS）。
- **Stale code comments**：`backend/src/api/searchChannelB.ts` header 仲寫「min_score=0.30 / wiki_index.json 810 chunks」，與實際（0.22 / Supabase）不符。行為以 code 為準；清理屬獨立小任務，唔好當行為 bug 追。
- 文檔曾 drift（見 §5）— 養成「verify actual code/data，唔淨信文檔」習慣。
- `bump_version.py` 曾於 Session 64 **實際 wipe role_facts.json schema** — 跑前必 backup，跑後必驗 schema（PROJECT_MASTER_SPEC §E.8）。
- 線上驗證（EDB / onrender.com / App Store）sandbox egress 去唔到 → 一律包成 curl 指令交 Leonard 自己 Terminal 跑（附完整 `cd` 絕對路徑）。

## 4. 開放決策 —— 產品方向審視中（Leonard 2026-05-16 明示）

`dev/PROJECT_MASTER_SPEC.md` §F「鎖定決策」記錄嘅係 **current-state 決策，唔係不可變法律**。Leonard 已表明產品方向可能要變。接手時：

- 把 §F 當「點解現況係咁」嘅背景，**唔係「不准郁」嘅禁令**。
- 任何方向 / scope / 架構調整，**同 Leonard 確認後**即可推翻對應條目，並喺 PROJECT_MASTER_SPEC **同 pass 更新**。
- 變更鎖定決策走 AGENTS.md §3 **HIGH-risk PLAN 流程**（出 PLAN → 等 user 確認 → 先 READ/CHANGE）。
- **未鎖、等 Leonard 拍板嘅大方向問題**：產品 scope / 目標用戶 / Channel B 是否接 Circular System / Mobile UI Phase 2 是否繼續。**唔好假設沿用舊 scope。**

## 5. 文檔修正歷史（等你知文檔已修正、可信）

### 5a. Session 110（純文檔，未動 code）
- `PROJECT_MASTER_SPEC.md`：§B.1 數字釐清框（**當時寫「148→39」——已被 5b 推翻，148 先係 app 內庫實數**）；新增 **E.10**（公開站 client-side admin 閘門 + 密碼曾入 log，🔴 至今 open，碰 admin/auth 前必讀）、**E.11**（Channel A topic 污染）、**E.12**（EDB 改版一次打爛 26 URL）；強化 E.4/E.5/E.8；§F 產品方向 banner；§G.2 drift 方法論 banner。
- `CODEBASE_CONTEXT.md`：`1,001→792`；`wikiRepository.ts` 改寫 Supabase pgvector；+AI Maintenance Log。
- `SESSION_HANDOFF.md` baseline #5：`min_score B/AB 0.15→0.22`（**仍有效**）。
- ⚠️ S110 嘅修正**從未 commit**，且部分（792、148→39）已被 5b 更正。

### 5b. Session 111 truth-pass v2（純文檔，未動 code / data / 公開契約）
- 發現 governance/state desync：8 個 un-logged commit `c78685f..ae31084`（dedup 792→455、Channel B Supabase enablement kit、mobile fallback、app refactor）已 push 但冇入 SESSION_LOG。
- `PROJECT_MASTER_SPEC.md`：§B.1 釐清框重寫成 **4 數字（148 app 內庫 / 39 公開子集 / 151 registry / 120 extracted）**，「148 是過時計數」舊說法更正為錯；§B.1 表 39→148（app tab 實 render）；§F.9 加 guidelines open-decision 指針；§E.2 加第三次 dedup 復發；§G.2 banner 改寫成 drift 級聯 + 「commit 必入 SESSION_LOG」。
- `CODEBASE_CONTEXT.md`：「792 as of v2.3.0」→ 455（×2）；guidelines.json 行加 39-vs-148 OPEN DECISION 註；+AI Maintenance Log。
- `SESSION_HANDOFF.md`：Current Baseline facts 792→455 / HEAD ae31084；Open Priorities 重生；+Session 111 record。
- `guidelines.json` **維持 39 唔郁**（Leonard 拍板：收斂屬對外契約變更，留 open decision）。

## 6. 接手後第一步（Post-startup first action）

完成 AGENTS.md §1 起手序後，**先 verify git HEAD + `knowledge.json._meta.stats` 對唔對得返 SESSION_HANDOFF Current Baseline**（Session 111 證實會 drift），再問 Leonard 以下未決事項：
1. **guidelines.json 39→148 OPEN DECISION**（Leonard 傾向收斂、本次未執行）——要唔要而家正式走 §3 HIGH-risk PLAN 做契約收斂（影響下游 Circular System）。見 PROJECT_MASTER_SPEC §B.1 釐清框。
2. **產品方向**：scope / 目標用戶 / Channel B 是否接 Circular System / Mobile UI Phase 2 是否繼續——仍 open，唔好假設沿用舊 scope。

**未得 Leonard 確認前，唔好對 scope / §F 鎖定決策 / 公開契約落手。** 碰 admin / auth / 公開推送之前，必讀 `PROJECT_MASTER_SPEC.md` §E.10（全專案歷時最長、後果最嚴重嘅未解風險）。**任何改 code/data 嘅 commit 必須同 pass 入 SESSION_LOG**（Session 111 desync 根因）。

---

*本 HANDOFF PACKAGE 由 Claude 於 2026-05-16 經實測製作（S110），同日 S111 truth-pass v2 重新校正。每次接手後若狀態有變，更新本文件 §2/§4/§6 並 commit（S111 教訓：唔 commit 嘅快照等於冇）；歷史改動入 `dev/SESSION_LOG.md`。*
