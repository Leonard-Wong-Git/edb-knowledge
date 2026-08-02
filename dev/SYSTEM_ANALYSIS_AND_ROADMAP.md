# 系統分析與改進路線圖（SYSTEM ANALYSIS & ROADMAP）

> **文件定位**：這是一份**點時間**（2026-07-05, S192 起草）的策略性分析 + 改進規劃，**非治理 SSOT、非鎖定決策**。
> 目的：令日後任何 claude agent 讀完即可挑一個項目落手執行，唔使重新摸索系統全貌。
> **優先序低於** `SESSION_HANDOFF.md`（當前狀態）/ `PROJECT_MASTER_SPEC.md`（長期規格 + 不變量）。若本文件同上述衝突，以上述為準。
> **本文件唔記 live 數字**（chunks / facts / 版本號逐 session 變）——一律以 `SESSION_HANDOFF.md` Current Baseline 為準。本文件只講**結構、方向、改進機會**。
> 起草者只做 read-only 分析（無改任何 code / data）。每個改進項都標明 risk / 工作量 / Leonard 是否要拍板 / 首步 / 相關檔案。

---

## 0. 一頁摘要（給趕時間的 agent）

**系統本質**：一個**有根有據、可追溯到 EDB 官方原文**的香港學校政策知識平台（policychecker.wongfu.net）。核心價值＝**可信度 + 可追溯性**，唔係 AI 自由發揮。已由早期「K1 政策 Q&A」有機生長成一套**學校政策工具套件**（語義搜尋 + 文件分析 + 文件標註 + 政策範本 + 文件修訂 + 通告分析）。

**成熟度評估**：**生產成熟、功能豐富、0 outstanding bug**。RAG 檢索管道（Supabase pgvector + 主題路由 + LLM 合成）穩定；自動入庫管道（Option A）4 phase 全 ✅ 且端到端 VERIFIED LIVE；4 條監察 CI 常設。**系統唔係「差」，而係去到「該收斂 / 該打好地基迎下一階段」嘅位。**

**最值得投資嘅 5 個方向（詳見 §4，已排序）**：
1. **R1 檢索品質 eval harness** —— 用客觀 metric（recall@k / MRR）取代 ad-hoc live smoke，令 ranking 回歸有得自動抓（治本現時最痛嘅「逐源手調 route」痛點）。
2. **R2 資訊架構 / tab 收斂** —— 桌面已 ~8 tab，主要用戶旅程唔清；mobile 得 4 entry（parity gap）。收斂成幾個清晰 mode。
3. **R3 Channel A 正式退役**（下游轉 Channel B S146 已完成；R3 現只 gated on route-probe 8/5〔NEXT ①〕+ backend dismantle〔NEXT ⑥〕，不再等下游）—— 清 dormant code、三層同步、combined endpoint，大幅減 surface。
4. **R4 codebase 可維護性** —— 單檔 app.html 逾 3,000 行 inline JSX；Leonard 早已 flag「偏亂難維護」。評估「保持單一部署但拆模組 / 加輕量 build」。
5. **R5 安全 backlog 埋尾**（S187 已 flag）—— repo 私有化 + Supabase RLS 加固 + sibling Circular System 審計。

**唔好掂嘅不變量（violate 即倒退，詳見 §5）**：可追溯性優先於覆蓋率、policy fact 人工審核閘、`INITIAL_DATA` 唔可改回 async fetch、Channel A 三層同步、唔掂 Circular System repo。

---

## 1. 現時功能全圖（2026-07-05 code-verified）

> 以下由 `app.html` nav labels + `backend/src/server.ts` route table + `CODEBASE_CONTEXT.md` 落地核實，非靠記憶。

### 1.1 前端使用者介面

| 介面 | 功能 | 狀態 |
|---|---|---|
| `index.html` | EDB palette 入口頁；hero + 統計（`knowledge.json._meta.stats` 動態）+ CTA 導向搜尋/文件庫 | live |
| `app.html`（主 SPA，React 18 CDN 單檔） | 見下方 8 個功能面 | live |
| `q.html` / `t-purchase.html` | Quick Q&A / 範本草稿流程 | **dormant**（S119 起 inbound link 全移除、檔留可逆） |
| `mobile.js` + `mobile.css` | 手機層：4 步 onboarding + 角色揀選 + bottom-nav **4 entry**（政策搜尋 / 指引文件 / 範本下載〔靜態導引〕/ 平台介紹） | live |

**app.html 桌面 8 個功能面**（nav 實證）：
1. **平台介紹** —— hero + 動態統計 + 功能說明
2. **政策搜尋** —— Channel-B-only 語義搜尋（Supabase 原文 + LLM 合成 + 頁碼可跳轉）；底有 WhatsApp 分享（S182）
3. **指引文件庫** —— EDB 文件三層排序瀏覽（範疇→子類→年份）
4. **通告分析** —— 貼入 EDB 通告文字 → AI 識別主題/角色/要點
5. **文件分析** —— client-side 抽 PDF/docx 文字 → per-segment 指引配對報告（S154）
6. **文件標註** —— desktop-only；上載文件 → `/api/annotate-document` 合併「指引配對 + checklist 缺口」→ 在原檔就地螢光+批註下載（S161/S163）
7. **政策範本** —— 15 域 106 份學校版/清單 docx 下載 + 校類 filter（S160）
8. **文件修訂** —— 上載文件 → 按 checklist 逐項 covered/partial/missing + 補回標準條文 → 生成修訂版 docx（S160）

> ⚠️ **觀察**：桌面 8 tab vs 手機 4 entry；且 5–8（文件工具）功能定位相近但各佔一個 top-level tab。詳見 §4 R2。

### 1.2 後端 API（Node + TS，Render `edb-knowledge.onrender.com`）

| Route | 用途 |
|---|---|
| `GET /health` | 健康檢查（cache_a warm/size）|
| `POST /api/search/channel-b` | 主線：wiki cosine + 主題路由 + LLM 合成 + 頁碼 |
| `POST /api/search/channel-a` | Channel A（keyword+embedding，前端已唔 call、endpoint 留存）|
| `POST /api/search/combined` | A+B 合併（dormant）|
| `POST /analyze-circular` | 通告分析 |
| `POST /api/analyze-document` | 文件分析（per-segment 指引配對）|
| `POST /api/annotate-document` | 文件標註（指引+checklist 合併 findings）|
| `POST /api/checklist-revise` + `GET /api/checklist-domains` | 文件修訂（checklist coverage）|
| `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks` | Channel B 增量同步（Q4 Phase 2，**dormant** 至設 key）|

護欄（S187）：per-IP 10/min + 全域 backstop、body-size cap → 413、Channel A `min_score` floor + result cap。

### 1.3 資料層

- **Supabase pgvector `wiki_chunks`**（Channel B 知識庫，主資產）—— live 數字見 handoff；IVFFlat lists=60 probes=8；RLS=ON + anon SELECT-only（S121）。
- **Channel A**（`knowledge.json` / `role_facts.json` 三層）—— **凍結 @455 facts**（S143 Phase 1），schema 不變、繼續供下游。
- **公開端點**（GitHub Pages）：`knowledge.json` / `guidelines.json`（152 文件）/ `K1_API_SPEC.md`。
- **工具資料**：`checklists_bundle.json`（15 域）/ `policy_templates.json`（15 域 106 docx）/ `source_registry.json`（source provenance）。

### 1.4 營運自動化（GitHub Actions CI + Option A 管道）

- **4 條監察**（detection-only、人工再入庫閘不變）：`check_freshness`（已入庫源改動）/ `discover_sources`（新文件）/ `check_served_urls`（用戶點到嘅連結壞）/ `check_new_circulars`（通告 feed；**S191 每日 cron 已退役**，被 ops `approval-issue.yml` 取代）。
- **Option A 自動入庫管道**（4 phase 全 ✅ + VERIFIED LIVE）：feed → 準備入庫包 → 私密 ops repo Issue 剔掣批准 → executor 自動 embed+INSERT+route-patch+display-sync+commit+push+deploy。每日 19:30 HK cron 兜底 + idempotency guard。

---

## 2. 系統健康評估（誠實版）

**做得好、唔好推翻嘅地方**：
- **RAG 架構清晰穩定**：前端→Render→嵌入→主題路由→向量搜尋→LLM 合成→pgvector，四輪 Channel B 治理（§E.3）換嚟一個唔會 SAG-domination 嘅檢索層。
- **可追溯性紀律硬淨**：每答案指回 EDB 原文 URL + 頁碼；page-carry 管道令 vault 可追溯率去到 ~88% 結構天花板。
- **治理成熟**：AGENTS.md + PMS + DOC_SYNC + session log archive，跨 session 交接可靠；drift 有 banner 提醒（§G.2）。
- **自動入庫閉環**：Option A 令新通告可以「手機剔掣 → 自動入庫部署」，大幅降低 Leonard 手動成本。

**技術債 / 摩擦點（改進機會所在）**：
1. **手調 route 表隨源數線性膨脹** —— `searchChannelB.ts` 的 SOURCE_SETS / TOPIC_KEYWORDS 逐源手維護；源愈多，短 query 撞 crowded route 排名低嘅 case 愈多（S186 2 源、S152 cgss 同類）。這是**檢索層可擴展性瓶頸**。
2. **驗證重手動** —— 大量 live smoke 靠 Leonard 喺 Terminal 跑 curl（Mac SSL / sandbox egress 限制）。`regression:semantic` 係 offline 固定 case，冇客觀 retrieval metric，ranking 回歸靠人肉發現。
3. **前端無測試 + 單檔巨大** —— app.html 逾 3,000 行 inline JSX/Babel Standalone、零測試；改動只能靠 preview / 人眼。Leonard 早已 flag「codebase 偏亂難維護」（PMS §F banner）。
4. **功能面膨脹、IA 未收斂** —— 桌面 8 tab；文件工具（分析/標註/範本/修訂）定位相近但各佔 top-level；mobile 得 4 entry。
5. **Channel A dormant 包袱** —— 凍結但 code path / 三層 / combined endpoint 仍在，構成理解成本；Q4 Phase 2（下游轉 Channel B）S146 已完成，退役（R3）現只 gated on route-probe 8/5 + backend dismantle。
6. **安全 backlog 未埋尾** —— repo public 令 backend IP（routing/keywords/prompts）+ vault verbatim world-readable；Supabase RLS 只做咗 defense-in-depth 一半；sibling Circular System 未審（S187 已 flag，係現時 Open Priorities #1）。
7. **infra 磨擦** —— Render free-tier idle 15 分鐘冷啟 ~50s，傷首 query 體驗。

---

## 3. 產品方向觀察（給 Leonard 拍板用）

系統已由「K1 政策 Q&A」生長成**學校政策工作流套件**。值得一個**刻意嘅方向聲明**，因為佢直接決定 IA 同優先序：

- **定位 A —「可信政策搜尋引擎」**：核心係搜尋 + 可追溯；文件工具係輔助。→ 優先投檢索品質（R1）、搜尋 UX，文件工具收埋入次級。
- **定位 B —「學校文件合規工作台」**：核心係「上載你份文件 → 我幫你對政策 / 標註 / 補條文 / 出範本」；搜尋係其中一件工具。→ 優先投文件工具打通成一條 workflow（分析→標註→修訂→範本一條龍），搜尋做支撐。

呢兩個定位**唔互斥**，但「邊個係主 CTA」會改晒首頁、tab 結構、mobile scope。**建議**：下個策略 session 由 Leonard 一句話定主線，先做 §4 R2（IA 收斂）。在未定之前，R1（檢索 eval）係兩個定位都需要嘅地基，可以無悔先做。

---

## 4. 改進項目（已排序，每項 agent 可直接執行）

> 格式：**現況/問題 → 為何重要 → 建議方向 → Risk / 工作量 → 首步（agent 落手）→ 依賴 / Leonard 決策 → 相關檔案**。
> Risk 用 AGENTS.md §3 定義（HIGH = ≥3 檔 / 不可逆 / 外部系統 / 改治理或鎖定決策）。凡改鎖定決策（PMS §F）必走 §3 HIGH-risk PLAN 等 Leonard 確認。

### R1 — 檢索品質 eval harness（🥇 最高槓桿、無悔）
- **現況/問題**：檢索品質靠 ad-hoc live smoke + `regression:semantic` 固定 case；冇客觀 metric，短-query ranking 回歸靠人肉發現（S186 2 源監察、S152 cgss）。
- **為何重要**：檢索係核心價值。冇 eval，任何 route / chunk / model 改動都係「盲改」，且逐源手調 route 表唔可持續。有咗 golden-query eval，ranking 改動可量化、CI 可 gate。
- **建議方向**：建一個 golden-query 評測集（≥40 條真實短 query，覆蓋各範疇 + memory 的「短 query 優先」原則），標註每 query 的 gold source_id(s)，離線跑 Channel B 檢索算 **recall@k / MRR / gold-in-top-8 率**；納入 `backend` npm script，改 route/chunk 後必跑。可加「LLM-judge 合成品質」子項（可選）。
- **Risk / 工作量**：**LOW risk**（純新增測試、唔改生產路徑）/ 中工作量（建 query 集最花時間，可分批）。
- **首步**：讀 `backend/src/api/searchChannelB.ts` + 現有 `npm run regression:semantic` 實作 → 抽 20 條 handoff/log 提過嘅真實 query（含 S186 兩個 monitor 源、sen/年假 等短 query）做 seed 集 → 寫 `backend/eval/retrieval_eval.(ts|py)` 離線跑 + 出 metric 表 → 先唔 gate，收集 baseline。
- **依賴 / 決策**：無需 Leonard 拍板即可做 baseline 版；是否 CI-gate 由 Leonard 定。**注意**：live 檢索要真 embedding，離線集要 pre-compute 或用 Leonard Terminal 跑一次生 baseline（Mac SSL / egress 限制，見 PMS §D.7）。
- **相關檔案**：`backend/src/api/searchChannelB.ts`、`backend/src/lib/wikiRepository.ts`、現有 `regression:semantic`、memory `feedback_short_query_first`。

### R2 — 資訊架構 / tab 收斂（🥈 用戶體驗最痛）
- **現況/問題**：桌面 8 top-level tab；文件工具（分析/標註/範本/修訂）定位相近各佔一 tab；mobile 得 4 entry（parity gap）；主要用戶旅程唔清。
- **為何重要**：功能多但入口散 = 用戶搵唔到、認知負荷高。收斂 IA 直接提升可用性，亦係 mobile 全功能化嘅前提。
- **建議方向**：由 8 tab 收成 3–4 個清晰 mode，例如：**① 政策搜尋**（主）｜**② 文件工具**（分析/標註/修訂 收入一個帶子分頁嘅工作台）｜**③ 範本庫**｜**④ 通告分析**（或收入文件工具）。平台介紹降為首頁/about。配合 §3 產品定位決定邊個係主 CTA。
- **Risk / 工作量**：**MEDIUM–HIGH risk**（改主 SPA 導航、≥3 檔含 mobile.js、影響用戶熟悉路徑）/ 中工作量。
- **首步**：**先出 IA 提案（純設計、唔改 code）**畀 Leonard 睇 —— 列現 8 tab → 建議分組 → 每 mode 主 CTA + 次要動作；標明 mobile 對應。Leonard 拍板後先郁 code。
- **依賴 / 決策**：**必須 Leonard 先定 §3 產品定位（A/B）** + IA 提案批准。改鎖定 surface 走 §3 HIGH-risk PLAN。
- **相關檔案**：`app.html`（nav + tab render）、`mobile.js`（bottom-nav `buildXShell`）、PMS §B.1 / §B.5、`dev/MOBILE_UI_SPEC_v1.md`。

### R3 — Channel A 正式退役（減 surface；下游 ready，S146 已轉 Channel B）
- **現況/問題**：Channel A 凍結 @455、admin 已刪，但 code path dormant、`role_facts.json` 三層同步、`/api/search/channel-a` + `/combined` endpoint 仍在。Q4 Phase 2（下游 Circular System 轉食 Channel B）**S146 已完成**（Leonard 確認 + S202 route-probe 零 channel-a 流量佐證）。
- **為何重要**：dormant 雙通道係持續嘅理解成本 + 維護面。下游既已全轉 Channel B，Channel A 就係純包袱，可大刀清走。
- **建議方向**：**分階段、可逆**。(1) ~~先確認下游已唔再 fetch `knowledge.json`~~ **已確認（S146 + S202 零流量）** → (2) 移除前端 dormant code path（q.html / combined 相關）→ (3) 收 endpoint（`channel-a` / `combined`）→ (4) 三層 / `role_facts.json` 歸檔。每步 git-revertable。
- **Risk / 工作量**：**HIGH risk**（動對外契約 + 不可逆感）/ 中工作量。前置：route-probe 8/5 讀完刪 probe（NEXT ①）+ backend dismantle（NEXT ⑥）。
- **首步**：route-probe 觀察窗 8/5 第二次讀確認仍零外部呼叫 → 刪 `server.ts:168–198` probe（NEXT ①），即解鎖 R3 執行。
- **依賴 / 決策**：**Leonard 跨 repo 確認 + 拍板**。這是 PMS §F.2 / §F.11 鎖定決策範圍。
- **相關檔案**：PMS §F.2 / §A.3、`dev/CHANNEL_B_SYNC_SPEC.md`、`backend/src/api/searchCombined.ts`、`backend/src/api/searchChannelA.ts`、三層 `role_facts.json`。

### R4 — codebase 可維護性（Leonard 早已 flag）
- **現況/問題**：`app.html` 逾 3,000 行 inline JSX via Babel Standalone、零測試、零模組邊界；改一個功能要喺巨檔搵位。Leonard 明示「codebase 偏亂難維護」（PMS §F banner 2026-05-16）。
- **為何重要**：維護成本 + 回歸風險隨檔案大小上升；係 R1/R2 之後令未來所有改動更快更安全嘅地基。
- **建議方向（3 選 1，帶 trade-off）**：
  - **(a) 保守 —— 檔內模組化**：唔加 build，但用清晰 section marker + 抽共用 helper，純可讀性。低風險、增益有限。
  - **(b) 中庸 —— 輕量 build 但仍出單檔**：引入 esbuild/vite 將多個 source 檔 bundle 成單一 `app.html` 部署（保持「單檔部署 + 無 runtime fetch」不變量）。**關鍵**：白屏教訓（§E.1）係關於 **runtime async fetch data**，唔係關於 build tooling——build-time inline data 可同時滿足「無 runtime fetch」+「有模組邊界」。中風險、增益大。
  - **(c) 進取 —— 全面重構**：唔建議（大 scope、高風險、無即時 ROI）。
- **Risk / 工作量**：(a) LOW / (b) **HIGH risk（推翻 PMS §F.1「無 build pipeline」鎖定決策）**、大工作量 / (c) 過高。
- **首步**：**唔好郁 code**。先出一份「app.html 模組拆分地圖 + build 選項 trade-off 表」畀 Leonard，明確指出 (b) 會推翻 §F.1、需 §3 HIGH-risk PLAN + 白屏不變量點樣守。
- **依賴 / 決策**：**Leonard 拍板**（尤其 (b) 動鎖定決策）。
- **相關檔案**：`app.html`、PMS §F.1 / §E.1、`CODEBASE_CONTEXT.md` Stack。

### R5 — 安全 backlog 埋尾（已在 Open Priorities #1–2）
- **現況/問題**：repo public → backend IP（SOURCE_SETS/keywords/prompts/thresholds）+ `source_registry` + `dev/vault` verbatim world-readable；Supabase RLS 只做 defense-in-depth 一半；sibling `EDB-AI-Circular-System`（circular.wongfu.net，亦 public）未審。
- **為何重要**：競爭者可照藍圖 rebuild；且安全審計係 Leonard 已表明嘅下個焦點。
- **建議方向**：(1) sibling Circular System 用 S187 同級 rigor 審（secrets/git history/暴露面/寫入面/rate-limit/anon 權限）；(2) repo 私有化 —— **同 Option A 嘅 private-ops 方向合一**（hosting 公開、code/批准私密）；(3) Supabase 收 anon 為 RPC-only + revoke table SELECT（令 anon key 漏都 dump 唔到 table）。
- **Risk / 工作量**：審計＝LOW risk（read-only）；私有化 + Supabase DDL＝HIGH risk（改 hosting + 生產 DDL 走 Dashboard）。
- **首步**：跑 sibling repo 安全審計（SESSION_LOG S190 closeout 有現成 paste prompt；可用 agent-team 5 維度並行，全程 read-only）。
- **依賴 / 決策**：私有化 / Supabase DDL 需 Leonard 授權 + Dashboard 親手。
- **相關檔案**：PMS §C.4 / §E.10、handoff Open Priorities #1–2、SESSION_LOG S187 / S190。

### R6 — infra：Render 冷啟緩解（細、快勝）
- **現況/問題**：Render free-tier idle 15 分鐘後冷啟 ~50s，傷首 query。
- **建議方向**：(a) 加一條 keep-warm cron（每 ~10 分鐘 ping `/health`）保暖；(b) 或評估 paid tier；(c) Azure fallback 已在。
- **Risk / 工作量**：LOW / 細。**注意**：keep-warm 會令 free-tier 一直 active，需確認冇違 Render 免費條款 + 唔會撞 rate-limit backstop。
- **首步**：確認 Render 免費條款容許 self-ping → 加 `.github/workflows` cron ping（或 external uptime pinger）。
- **依賴 / 決策**：Leonard 決定值唔值得（冷啟係已知、非 bug）。
- **相關檔案**：`backend/src/server.ts` `/health`、Render 設定。

### R7 — Mobile 全功能化（大 scope，排 R2 之後）
- **現況/問題**：文件工具（分析/標註/範本真下載）desktop-only；mobile shell 只 4 entry。
- **為何重要**：學校用戶手機使用漸增；但 mobile 全功能化須先 R2（IA 收斂）定咗結構先做，否則重複做 shell-routing。
- **建議方向**：R2 之後，按收斂後結構重做 mobile shell-routing，逐個文件工具評估手機可行性（標註/修訂涉檔案上載 + Word/PDF 生成，手機體驗要真機驗）。
- **Risk / 工作量**：MEDIUM–HIGH / 大。**明確排喺 R2 之後。**
- **首步**：R2 IA 定案後再開 PLAN。
- **相關檔案**：`mobile.js` / `mobile.css`、PMS §B.5、`dev/MOBILE_UI_SPEC_v1.md`。

### R8 — （研究向、低急）檢索層進階：reranking / hybrid
- **現況/問題**：純向量 + 手調 keyword route；短 query 撞 crowded route 排名低係結構性。
- **建議方向**：R1 eval 有 baseline 後，實驗 (a) top-N 之上加 cross-encoder / LLM rerank；(b) BM25 + vector hybrid。目標：減對手調 route 表嘅依賴、提升短 query 準確。**必須有 R1 eval 先做**（否則無法量度改善）。
- **Risk / 工作量**：MEDIUM（改檢索核心）/ 大。
- **首步**：等 R1 完成 → 用 eval 集做 A/B。
- **依賴**：R1 前置。
- **相關檔案**：`searchChannelB.ts`、PMS §E.3。

---

## 5. 不變量 / 護欄（改任何嘢前必守，violate 即倒退）

摘自 PMS §A.2 / §E / §F —— 呢啲係血淚教訓，唔可為「乾淨 / 快」而破：
1. **可追溯性優先於覆蓋率** —— 寧可答「搵唔到」都唔可畀無來源答案。
2. **policy fact 人工審核閘** —— LLM 唔可自主發佈；監察全部 detection-only、再入庫係人工 gate（Option A 的 Issue 剔掣批准就係呢個閘）。
3. **`INITIAL_DATA` 唔可改回 async fetch** —— Babel Standalone + `file://` CORS = 白屏（§E.1，踩過兩次）。
4. **Channel A 三層同步不變量** —— 若動 role_facts 必三層同步（§E.2，踩過三次）。
5. **唔掂 Circular System repo** —— K1 只出公開 JSON 端點（§A.3 / §E.9）。
6. **Supabase RPC/DDL 前必 INSPECT live `pg_get_functiondef`** —— schema.sql 曾 drift 致 PGRST203 生產全 0（§E.13）；生產 DDL 只走 Dashboard。
7. **外部平台字段一律實測、禁憑記憶** —— 最貴 rework 來源（§E.4 / AGENTS §0b）。
8. **handoff 的「root cause = X」係 hypothesis 唔係 ground truth** —— triage 必先 reproduce 觀察 actual failure trace（§G.2 / §G.3）。
9. **改鎖定決策（PMS §F）走 §3 HIGH-risk PLAN** —— 出 PLAN → 等 Leonard 確認 → 先 CHANGE。

---

## 6. 建議執行次序（roadmap）

| 階段 | 項目 | 為何呢個次序 |
|---|---|---|
| **即刻（無悔、無需拍板）** | **R1** 檢索 eval baseline · **R5** sibling 安全審計（read-only） | 兩者都 LOW risk、唔改生產、且係其他項嘅地基/已定焦點 |
| **待 Leonard 一句方向** | **§3 產品定位 A/B** → **R2** IA 提案 | R2 依賴定位；定位係 Leonard 專屬決策 |
| **中期** | **R4** 可維護性提案（trade-off 表）· **R6** 冷啟緩解 | R4 令之後改動更快；R6 快勝 |
| **下游 ready（S146 已轉）** | **R3** Channel A 退役 | 下游轉 Channel B S146 已完成；現只 gated on route-probe 8/5〔①〕+ backend dismantle〔⑥〕 |
| **後續** | **R7** mobile 全功能（排 R2 後）· **R8** reranking（排 R1 後） | 明確有前置依賴 |

**一句總結**：先用 **R1** 打好「檢索有得客觀量度」嘅地基（無悔）＋跑 **R5** sibling 審計（已定焦點）；同時等 Leonard 用一句話定產品主線（定位 A/B），再落 **R2** IA 收斂。其餘按依賴鏈跟上。

---

## 7. 日後 agent 點揀項目落手

1. 讀 `SESSION_HANDOFF.md` Current Baseline + Open Priorities（**live 狀態以嗰度為準**，本文件只係方向）。
2. 揀本文件 §4 一個 R 項 → 睇「首步」+「相關檔案」+「依賴/決策」。
3. 若「依賴/決策」寫住要 Leonard 拍板 → **先出提案/PLAN，唔好郁 code**（尤其 R2/R3/R4 動鎖定決策）。
4. 落手前跑 PMS §G.3「動手前自問」7 條 + 對照本文件 §5 護欄。
5. 完成後照 AGENTS.md §3 PERSIST / §4 closeout，並喺本文件對應 R 項補「進度」註記（如已做 R1 baseline，標明喺邊）。

---

*本文件由 Claude（Opus 4.8）於 2026-07-05 起草，read-only 分析，未改任何 code / data。提煉自 PROJECT_MASTER_SPEC 全文 + CODEBASE_CONTEXT + SESSION_HANDOFF S191 baseline + app.html/server.ts code 核實。方向性文件——當系統結構/定位有大變時由日後 agent 更新。*
