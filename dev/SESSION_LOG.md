# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-16 Session 111 — truth-pass v2 + agent teams（文件編號對齊）+ #3 登入後 admin review-state 修復

- **ID:** Claude_20260516_1952
- **Summary:** Leonard 開工。三大塊：**(1) truth-pass v2** — §1 起手序後實測 git/data 揭發 governance/state desync：S109 closeout `c78685f` 之後 **8 個 2026-05-16 commit**（`c78685f..ae31084`，已 push，含 dedup 792→455 `711f911` / Channel B Supabase enablement kit / mobile fallback / app refactor / 對外 specs+README+index.html reconcile `0806c90`）**完全冇入 SESSION_LOG**，同時 S110 自己治理文檔修正**從未 commit** 且停喺 792。**(2) agent teams**（Leonard 指示）：Team A 對齊所有對外文件編號；Team B read-only audit 登入後 admin staleness。**(3) #3 修登入後 admin review-state**（Leonard 範圍：只修資料對齊）。全程 4+ 輪與 Leonard 確認收窄 scope。
- **Key finding（過程中自我修正，已固化入 §G.2）:** 一度照 commit `0871bbe` message 誤判「app.html guidelines=148 係 regression」；verify `GUIDELINES_REGISTRY.length` 後更正 —— **148 = app 內庫實數（全 channel 知識基礎），39 = guidelines.json 公開精選子集（148 嚴格子集），兩者皆對**；舊「148 是過時計數」說法本身先錯。連 commit message 都要 verify。
- **Changed — 治理文檔（truth-pass v2，純文檔）:** `dev/PROJECT_MASTER_SPEC.md`（§B.1 表 39→148 + 釐清框重寫 4 數字 + open decision；§F.9 guidelines open-decision 指針；§E.2 第三次 dedup 復發；§G.2 banner drift 級聯 +「commit 必入 SESSION_LOG」+ 教訓行）, `dev/CODEBASE_CONTEXT.md`（L13/L40 792→455；guidelines 行 39-vs-148 OPEN DECISION 註；+AI Maintenance Log S111×2）, `dev/HANDOFF_PACKAGE.md`（header + §2 元教訓 banner + 表 ae31084/455/4 數字；§5 5a+5b；§6 重寫；footer）, `dev/SESSION_HANDOFF.md`（baseline #1 ae31084 / #3 facts 455 + 4 數字指針；Open Priorities 重生；S111 record）
- **Changed — Team A 對外文件編號對齊（已 verify diff）:** `CHANGELOG.md`（+ `[v2.3.0] 2026-05-16` 792→455 dedup entry；解決 version 撞號：舊誤標 `v2.3.0@05-03`→`v2.2.1`，歷史數字保留）, `K1_API_SPEC.md`（§3 v1.3.1→2.3.0 + stats block + dates；§6 guidelines v→2.2.0，**count:39 刻意保留**；footer date）, `README.md`（148 標明「in-app 瀏覽庫」+ 39 公開子集釐清；dedup 註加 commit/log）；`K1_KNOWLEDGE_INTERFACE_SPEC.md` 已對齊無需改。
- **Changed — #3 admin review-state（app.html，Leonard 範圍=只修資料對齊）:** Team B 確認 `INITIAL_REVIEW_STATE`@1481 仍 keyed 舊 1,001 index、與 455 INITIAL_DATA 嚴重錯位。修：用一次性 `dev/regen_review_state_s111.py`（先 backup `dev/init_backup/20260516_202411_UTC/app.html`）由 knowledge.json 重生 **455 全 approved**，保持單行 inlined `JSON.parse` literal（E.1）；comment @713/@1483 更新；`LOCAL_SNAPSHOT_KEY` `…-v2`→`-v3`@691（回訪 admin 棄舊壞 localStorage 快照、由乾淨 455 baseline 起，未匯出本地編輯會失但本來就 keyed 壞 index 不可信）。SEV-2 候選 queue 空 = 預期（baseline「0 candidates」，S79 archive），無需改。
- **Verified（實測）:** knowledge.json `_meta` v2.3.0 stats `{facts:455,chunks:10736,sources:120,guidelines:39,topics:7}`；role_facts 三層 byte-identical md5 `7d00330…`；`git HEAD==origin/main==ae31084`；guidelines.json 39 = `GUIDELINES_REGISTRY`(148) 嚴格子集。
- **QC:** truth-pass — residual 792/1,001 逐個審 = 全部正確歷史/刻意 drift 記錄，無一當 live。Team A — git diff 逐檔 verify，零 code/data/app.html scope creep，39 保留。#3 — `INITIAL_REVIEW_STATE` OLD 1001→NEW **455** keys、全 `approved`、單行（無 `\n`）、prefix/suffix shape OK、range cross-check（finance.all_roles 83=83 / general.eo_admin 1=1）；changeset **零 json/data 檔改動**。§4a：本次觸發（421→149 行，4 條舊 entry 封存 `dev/archive/SESSION_LOG_2026_Q2.md`，保留 S111+S110）。未跑 backend regression（無改公開契約/data，§3c 不觸發）。
- **Known residual doc-debt（留下個 agent）:** S110 凍結歷史處（不改寫）；CODEBASE_CONTEXT L29「v1.3.1 approved facts」版本標籤 drift（實際 _meta v2.3.0 / 契約 v2.0.0）；HANDOFF_PACKAGE §3「4,759 行」實為 ~4,057；`searchChannelB.ts` stale header（0.30/810→0.22/Supabase）；`semanticRegression.ts` 斷言 guidelines version `1.3.1`（實 2.2.0，pre-existing stale test，非本次引入）。
- **Pending（用戶 Terminal，含空格路徑雙引號）:** 一個 consolidated git add+commit+push（治理文檔 + Team A 對外文件 + app.html #3 + 新 HANDOFF_PACKAGE.md + regen 腳本，連同 S110 從未 commit 嘅編輯一併入庫）+ MemPalace sync。Leonard 自行 browser/admin-login 驗證登入後 459→455 review/approve/snapshot（sandbox 入唔到 admin 閘門）。
- **Next:** 等 Leonard：(1) guidelines 39→148 OPEN DECISION 要唔要正式走 §3 HIGH-risk PLAN 收斂；(2) 產品方向；(3) 原 Open Priorities（Mobile UI Phase 2 / Q&A §E.10 / HKEAA）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Doc-drift truth-pass / accuracy correction | 修正帶 stale 值嘅 PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / SESSION_HANDOFF / HANDOFF_PACKAGE；CODEBASE_CONTEXT AI Maintenance Log；HANDOFF_PACKAGE §2/§5；SESSION_LOG drift 記錄 | ✓ Done |
| Long-term spec / locked decision / architecture invariant change | PROJECT_MASTER_SPEC §B.1 釐清框 + §F.9 guidelines open decision + §E.2/§G.2；CODEBASE_CONTEXT（無方向轉變 N/A 直接改 directory note）；SESSION_HANDOFF baseline | ✓ Done |
| New cross-agent handoff knowledge doc added | N/A（HANDOFF_PACKAGE 已存在，本次只 refresh §2/§5/§6，非新增） | N/A |
| Product version / release milestone change | CHANGELOG（+ v2.3.0 2026-05-16 dedup entry，解決 version 撞號）；README/K1_API_SPEC 編號對齊；SESSION_HANDOFF/LOG | ✓ Done |
| Product behavior / tuning change | #3 app.html admin review-state 重生 455 + LOCAL_SNAPSHOT_KEY v3；SESSION_HANDOFF baseline/priorities + SESSION_LOG QC evidence | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（S110 建、S111 truth-pass v2 重新校正嘅可信狀態快照）。⚠️ 起手務必自行 verify：git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline——Session 111 已證實連治理讀set +「可信快照」+ commit message 都會 drift（commit 咗但冇入 SESSION_LOG 係根因）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號包覆絕對路徑）。

⚠️ 若 Leonard 仲未喺自己 Terminal 跑收尾 git/MemPalace 指令：working tree 會有一批未 commit 改動（治理文檔 + CHANGELOG/K1_API_SPEC/README + app.html #3 + 新 dev/HANDOFF_PACKAGE.md + dev/regen_review_state_s111.py）。先確認 git status，唔好當已入庫。

Current objective and progress state:
- Session 111 (2026-05-16, Claude_20260516_1952) 三塊全部完成：(1) truth-pass v2 — 揭發並消化 8 個 un-logged commit（c78685f..ae31084，含 dedup 792→455 / Channel B Supabase enablement kit / mobile fallback / app refactor，已 push）+ S110 從未 commit 文檔修正；治理讀set 重對齊 455/ae31084 + 指引 4 數字釐清框。(2) Team A — CHANGELOG/K1_API_SPEC/README 編號對齊（CHANGELOG 補 v2.3.0 2026-05-16 dedup entry + 解 version 撞號；guidelines 公開 count 39 保留）。(3) #3 — app.html `INITIAL_REVIEW_STATE` 由舊 1,001-keyed 重生為 455 全 approved + `LOCAL_SNAPSHOT_KEY` v2→v3（修登入後 admin review/approve/snapshot 對唔上）。
- 商品狀態（已實測）：v2.3.0 / role_facts 三層 byte-identical 455 / guidelines.json 公開 39（app 內庫 GUIDELINES_REGISTRY 148）/ Supabase 10,736 chunks / git main=origin/main @ ae31084（未計本 session 未 commit 改動）。
- 未郁公開契約（guidelines.json 維持 39）；#3 屬資料對齊非功能改寫。

Pending tasks in priority order:
1. 等 Leonard 拍板 guidelines 39→148 OPEN DECISION（傾向收斂、未執行）——要做須走 §3 HIGH-risk PLAN（對外契約變更，影響下游 Circular System，curriculum 桶 ~25→127）。見 PROJECT_MASTER_SPEC §B.1 釐清框。
2. 等 Leonard 拍板產品方向（scope / 目標用戶 / Channel B 是否接 Circular System / Mobile UI Phase 2 是否繼續）——未確認前唔好對 scope 或 §F 鎖定決策落手。
3. Leonard 自行 browser admin-login 驗證 #3：登入後「知識提煉/知識管理」見 455（非 1,001）、approve/reject toggle + snapshot 匯出正常、v3 key 令舊壞 localStorage 棄掉（sandbox 入唔到 admin 閘門，必須 Leonard 親驗）。
4. Mobile UI Phase 2 餘下：index.html / q.html / t-purchase.html / app.html#guidelines mobile content。
5. Q&A admin-login security password gate（🔴 PROJECT_MASTER_SPEC §E.10，全專案最嚴重未解風險）+「34 問題」audit。
6. HKEAA source family 補完（S105 SBA gap）；（doc-debt 低）CODEBASE_CONTEXT L29「v1.3.1」標籤 / searchChannelB.ts stale header / semanticRegression.ts guidelines version 斷言 1.3.1（實 2.2.0）。

Key files changed in this session:
- 治理：dev/PROJECT_MASTER_SPEC.md（§B.1+釐清框/§F.9/§E.2/§G.2）, dev/CODEBASE_CONTEXT.md（455/guidelines 註/AI Log）, dev/HANDOFF_PACKAGE.md（§2 元教訓+表/§5/§6）, dev/SESSION_HANDOFF.md（baseline/Open Priorities/S111 record）, dev/SESSION_LOG.md（本 entry + §4a 封存 4 條去 dev/archive/SESSION_LOG_2026_Q2.md）, dev/DOC_SYNC_CHECKLIST.md
- 對外文件：CHANGELOG.md（+v2.3.0 entry + v2.2.1 重編號）, K1_API_SPEC.md（§3/§6 版本日期，count 39 留）, README.md（148/39 釐清）
- 產品：app.html（INITIAL_REVIEW_STATE 重生 455 / comment @713/@1483 / LOCAL_SNAPSHOT_KEY v3）；新增 dev/regen_review_state_s111.py（一次性重生工具）；backup dev/init_backup/20260516_202411_UTC/app.html

Known risks / blockers / cautions:
- 🔴 PROJECT_MASTER_SPEC §E.10：公開站 client-side admin 閘門非安全邊界 + 密碼曾入 log；碰 admin/auth/公開推送前必讀（全專案最嚴重未解風險，仍 open）。
- 🔴 治理紀律根因：改 code/data 嘅 commit 必須同 pass 入 SESSION_LOG，否則交接讀set 失真（S111 desync 教訓）。load-bearing 數字（facts / git HEAD / min_score / 連 commit message）動手前一律 verify actual code/data/git。
- guidelines 39 vs 148 = OPEN DECISION，未經 §3 HIGH-risk PLAN 唔好收斂或改 guidelines.json / app.html GUIDELINES_REGISTRY。
- #3 後：回訪 admin localStorage 已 bump v3，舊本地未匯出編輯會棄（原本已 keyed 壞 index 不可信）；Leonard 親驗未做。
- 產品方向未定 → 唔好假設沿用舊 scope。
- Repo 路徑含空格 → shell 指令必雙引號絕對路徑；舊路徑 ~/Downloads/Claude-edb-knowledge 已不存在。
- Cowork sandbox egress 不含 edb.gov.hk / onrender.com / apps.apple.com → 線上 / admin-login 驗證交 Leonard Terminal/browser。
- Render free tier cold start ~30s after 15min idle。bump_version.py S64 曾 wipe role_facts schema（只動 _meta.version）→ 跑前 backup。
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直 hit SSLCertVerificationError，用 curl 繞。
- Shared MemPalace recovery workaround hnsw:num_threads=1；備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838。Supabase free tier 500MB（現 ~50MB）。

Validation status:
- PASS: truth-pass residual 逐個審無一當 live count；Team A diff 逐檔 verify 零 scope creep；#3 INITIAL_REVIEW_STATE 1001→455 全 approved、單行 inlined（E.1）、range cross-check OK、零 json/data 改動；§4a 已 apply（421→149，封存 4 條）。
- PENDING: 用戶一個 consolidated git commit+push（含本 session 全部 + S110 從未 commit 編輯）+ MemPalace sync；Leonard browser admin-login 親驗 #3；Leonard 拍板 guidelines open decision + 產品方向。

Post-startup first action: 完成 §1 起手序 + 讀 HANDOFF_PACKAGE 後，先 verify git status（本 session 改動是否已入庫）+ git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，再問 Leonard：(1) #3 admin-login 親驗結果如何（如有 bug 即修）；(2) guidelines 39→148 OPEN DECISION 要唔要而家走 §3 HIGH-risk PLAN；(3) 產品方向 / Open Priorities。未得確認前唔好對 scope / §F 鎖定決策 / 公開契約落手。
```

---

## 2026-05-16 Session 110 — 文檔 drift truth-pass + 乾淨 cross-agent handoff package

- **ID:** Claude_20260516_1652
- **Summary:** Leonard 想要一個乾淨、可信、可整份交畀另一個 AI agent 嘅 handoff（動機：codebase 偏亂、產品方向可能要變、不信任既有文檔）。**確認唔係 from-scratch 重建**（會丟棄 792 人工核實事實/vault/Supabase——無價值且仍要 migrate）。做法：先實測 verify 真實 repo state（唔抄文檔），出 drift 清單，修正所有 drift，再產出 self-contained `dev/HANDOFF_PACKAGE.md`。產品方向**保持 open**（§F 標為 current-state 非鎖死）。
- **Changed:** `dev/PROJECT_MASTER_SPEC.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/DOC_SYNC_CHECKLIST.md`（+1 row）, `dev/HANDOFF_PACKAGE.md`（新增）, `dev/SESSION_LOG.md`
- **Verified (實測，非抄文檔):**
  - 三層 role_facts **byte-identical md5 一致** @ v2.3.0 / stats {facts:792, sources:120, guidelines:39}；E.2 風險現時 clean ✅
  - guidelines.json=39 docs；source_registry=151 entries；vault-extracted=120（三者不同層，舊「148」過時）
  - backend `dist/` 已編譯；`wikiRepository.ts` = Supabase pgvector（`match_wiki_chunks` RPC），**非**本地 wiki_index cosine
  - min_score code default：A=0.1，B/AB=**0.22**（非文檔寫嘅 0.15）
  - git 乾淨 `main` @ `c78685f`；app.html 4,759 行單檔
- **Drift fixed:** D1 §B.1 148→39（+釐清框）；D2/D3 CODEBASE_CONTEXT 1,001→792（×2）；D4 wikiRepository L39 改寫成 Supabase 架構（原描述已被取代）；D5 SESSION_HANDOFF baseline #5 min_score 0.15→0.22
- **§E 補完:** +E.10（公開站 client-side admin 閘門 + 密碼曾入 log，🔴 跨 S19–27、至今 open）、+E.11（Channel A topic 污染 S19→66 patch 4 次）、+E.12（EDB 改版打爛 26 URL S61）；強化 E.4（~5 backend session ViewState chain）/ E.5（跨工具復發）/ E.8（bump_version S64 實際 fire）
- **Banners:** PROJECT_MASTER_SPEC §F 加「產品方向審視中、§F 非不可變」；§G.2 加「連 SESSION_HANDOFF/CODEBASE_CONTEXT 都會 drift，load-bearing 常數 verify code」
- **QC:** 每個 drift 修正值皆 re-verify against actual code/data；未動任何 code / tech stack（純文檔準確性）；§4a check 未觸發（SESSION_LOG <400 行、最舊條目 <30 天）
- **Pending（用戶 Terminal，新路徑）:** Git commit + push；Leonard review HANDOFF_PACKAGE 內容是否需補
- **Next:** 等 Leonard 拍板產品方向；未確認前唔好對 scope/§F 落手

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Doc-drift truth-pass / accuracy correction | 修正 PROJECT_MASTER_SPEC + CODEBASE_CONTEXT + SESSION_HANDOFF 帶 stale 值處；CODEBASE_CONTEXT AI Maintenance Log；HANDOFF_PACKAGE §2/§5；SESSION_LOG drift 表 | ✓ Row added + applied |
| New cross-agent handoff knowledge doc added | CODEBASE_CONTEXT Directory Map（+HANDOFF_PACKAGE 條目）+ AI Maintenance Log；DOC_SYNC registry；SESSION_HANDOFF/LOG | ✓ Done |
| Long-term spec / locked decision / architecture invariant change | PROJECT_MASTER_SPEC §B/§E/§F/§G；CODEBASE_CONTEXT Key Decisions（無方向轉變 N/A）；SESSION_HANDOFF baseline #5（已修） | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block | N/A（非實際 API 變更，僅修正 directory-map stale 描述；Supabase 已記於 SESSION_HANDOFF Supabase Technical Notes + PROJECT_MASTER_SPEC §C.4。已知 doc-debt：CODEBASE_CONTEXT External Services 無獨立 Supabase block，留俾下個 agent） |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md —— 呢份係 Session 110 經實測製作嘅乾淨可信狀態快照（凌駕「抄舊文檔」），含 verified-state 表、邊度亂、開放決策、接手第一步。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號包覆絕對路徑）。

Current objective and progress state:
- Session 110 (2026-05-16)：文檔 drift truth-pass + 新增 dev/HANDOFF_PACKAGE.md。已實測 verify 真實 state 並修正 D1–D5 drift（148→39 / 1,001→792 / wikiRepository 改寫 Supabase / min_score 0.15→0.22）；PROJECT_MASTER_SPEC §E 補 E.10–E.12 + 強化 E.4/E.5/E.8 + §F/§G banner。未動任何 code。
- 產品方向 Leonard 表明可能要變、**保持 open**；§F 鎖定決策已標為 current-state 非不可變。
- 商品狀態（已實測）：v2.3.0 / role_facts 三層 byte-identical 792 / guidelines 39 / source_registry 151（vault-extracted 120）/ Channel B = Supabase pgvector / git clean @ c78685f。

Pending tasks in priority order:
1. 等 Leonard 拍板產品方向（係咪要變 / 定先做 Open Priorities）——未確認前唔好對 scope 或 §F 鎖定決策落手
2. Mobile UI Phase 2 餘下：index.html / q.html / t-purchase.html / app.html#guidelines mobile content
3. Q&A backlog：admin login security password gate（🔴 見 PROJECT_MASTER_SPEC §E.10）+「34 問題」audit
4. HKEAA / 考評局 source family 補完（Session 105 SBA query 揭發 vault gap）
5. （doc-debt，低優先）CODEBASE_CONTEXT External Services 補 Supabase block；清 searchChannelB.ts stale header comment（0.30/810→0.22/Supabase）

Key files changed in this session:
- dev/PROJECT_MASTER_SPEC.md（§B.1 + 釐清框 / +E.10–E.12 / 強化 E.4/E.5/E.8 / §F + §G.2 banner）
- dev/CODEBASE_CONTEXT.md（1,001→792 ×2 / wikiRepository→Supabase / +HANDOFF_PACKAGE 目錄條目 / +AI Maintenance Log）
- dev/SESSION_HANDOFF.md（baseline #5 min_score 0.15→0.22 / Last Session Record / Open Priorities）
- dev/DOC_SYNC_CHECKLIST.md（+「Doc-drift truth-pass」row）
- dev/HANDOFF_PACKAGE.md（新增 — 乾淨可信交接快照）
- dev/SESSION_LOG.md（Session 110 entry）

Known risks / blockers / cautions:
- 🔴 PROJECT_MASTER_SPEC §E.10：公開站 client-side admin 閘門非安全邊界 + 密碼曾入 log；碰 admin/auth/公開推送前必讀（全專案最嚴重未解風險，仍 open）
- 文檔曾 drift（本 session 已修 D1–D5）；load-bearing 常數動手前一律 verify actual code/data
- 產品方向未定 → 唔好假設沿用舊 scope
- Repo 路徑含空格 → shell 指令必雙引號絕對路徑；舊路徑 ~/Downloads/Claude-edb-knowledge 已不存在
- Cowork sandbox egress 不含 edb.gov.hk / onrender.com / apps.apple.com → 線上驗證交 Leonard Terminal/browser
- Render free tier cold start ~30s after 15min idle
- bump_version.py S64 曾實際 wipe role_facts schema → 跑前 backup 跑後驗
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直 hit SSLCertVerificationError，用 curl 繞
- Shared MemPalace recovery workaround hnsw:num_threads=1；備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB（現 ~50MB）

Validation status:
- PASS: 所有 drift 修正值已 re-verify against actual code/data；未動 code/tech-stack（純文檔準確性）；HANDOFF_PACKAGE self-contained 完成；§4a 未觸發
- PENDING: 用戶 git push（含本 session 文檔修正）；Leonard review HANDOFF_PACKAGE / 拍板產品方向

Post-startup first action: 完成 §1 起手序 + 讀 dev/HANDOFF_PACKAGE.md 後，問 Leonard：產品方向係咪要變，定先做 Open Priorities（Mobile UI Phase 2 / Q&A admin-login security / HKEAA source family）。未得 Leonard 確認方向前，唔好對 scope 或 §F 鎖定決策落手。碰 admin/auth/公開推送前必讀 PROJECT_MASTER_SPEC §E.10。
```

---
