# Session Handoff

<!-- Markers below have no dedicated local section yet; the next closeout should give each one a home. -->
<!-- ack:section:durable-anchors -->
<!-- ack:section:closeout-reconciled-state -->
<!-- ack:field:first-use-guidance-state -->
5. First-use guidance state: not_applicable — added by upgrade; prior use state is preserved and onboarding is not reactivated.

<!-- ack:section:task-understanding-summary -->
<!-- ack:section:active-objective -->
<!-- ack:section:sync-status -->
<!-- ack:field:user-intent -->
<!-- ack:field:task-essence -->
<!-- ack:field:success-criteria -->

<!-- ack:section:current-baseline -->
## Current Baseline

1. 平台 **v3.3.2**；Supabase **17,610**；`source_registry` **281**；`guidelines.json` `_meta` **2.6.1**；`knowledge.json` **2.3.0** · facts **455**；凍結合約零接觸。（**S218 起手探針再次全部實測相符**：served `app.html` PLATFORM_VERSION 3.3.2、Render `/health` `ok:true` warm 455、Supabase live count 17,610、`source_registry.json` 281、`guidelines.json` `_meta` 2.6.1。）
2. **【S218 更新】git 收斂維持；Render 報的部署 commit 落後屬已知現象，不是漂移。** `HEAD == origin/main == **f3ca973**`（S218 收工 commit，已 push），分歧 **0/0**，工作區乾淨。**判斷準則不是比 hash** —— 治理／持久化 commit 會令 HEAD 不斷前進而生產行為不變；要判斷「線上是否落後」，看 `git diff --name-only <部署commit>..HEAD -- backend app.html` 是否為 **0**。`612e13e..f3ca973` 只有三個純治理／持久化 commit（`72b5adb`、`0f8a7c9` 屬 S217，`f3ca973` 屬 S218 收工），**兩者對 `backend/` 與 `app.html` 零檔案改動**（S218 實測 `git diff --name-only 612e13e..HEAD -- backend app.html` = **0**）。Render `/health` 仍報 `commit` `612e13e`（`started_at` 2026-09-08T06:58:08Z，服務今晨重啟過），**故生產跑的執行碼與 `612e13e` 那次部署相同**；`RENDER_GIT_COMMIT` 不隨新 commit 更新的成因仍**未查證**。S217 記的 `612e13e` 為 HEAD 已過時，作為部署 commit 仍準確。
3. S214 候選全套現為 commit **`4fc2bab`**（rebase 後，內容與 `744a8dc` 逐位元組相同），**已在生產環境**；`FEATURE_EXACT_WINDOW_NARROW` / `FEATURE_GROUNDED_SYNTHESIS` / `FEATURE_ROUTE_FIRST_SEARCH` 三者在 Render 未設環境變數、**仍全部 off**。**產品 verdict 仍為 FAIL**。**【S219 更新】185 題 before／after 已首次跑完**（見 `## Validation / QC` S219 兩段）：`FEATURE_ROUTE_FIRST_SEARCH` 檢索準確度**每個 k 都有淨改善**（Recall@1 71→73、@3 99→103、@5 113→116），四條 PASS→FAIL 全部是 rank 7、在合成窗（前 5）之外故答案層面無影響；**但它的既定目的（修 OP③ 三題）未達成**，且 10/185 付出 routed RPC 失敗延遲，S214 要求的重複穩定性未做。合成側兩個 flag（`FEATURE_GROUNDED_SYNTHESIS`／`FEATURE_EXACT_WINDOW_NARROW`）這套 harness **量不到** —— 它送 `synthesize:false`，兩者只在 `synthesizeAnswer()` 內生效，要另跑 grounded harness（外部模型批次，需另行批准）。**本節仍未啟用任何 flag。已部署 ≠ 已啟用。**
4. 🔴 **【S217 逐檔核對，重要】「三個 flag 全 off」≠「零行為改動」。** S214 的 establishment 路徑改動**沒有任何 flag 保護**，已在生產生效。觸發條件窄：`detectedCategory === "staffing"` **且** query 含「N 班」（1–2 位數），`ESTABLISHMENT_SOURCE_IDS` 現時只有 `staff_est_pri`。三處實際差異：(a) `estLead` 移除了 `!seenIds.has(r.id)` 過濾 → ANN 已撈到同一 chunk 時，精確列現在仍會置頂；(b) 插入方式由「插在 forced prefix 之後」改為「置頂並濾走**整個** establishment 來源的其他列」→ 同一份編制表其他班數的列不再與正確列並存；(c) `trustedVaultLead` 的判斷來源由 `results[forcedLeads]`（overlay 後）改為 `mainSearchLead`（overlay 前）—— 此項技術上覆蓋所有合成呼叫，但無 overlay 觸發時兩者取同一項。**其餘執行碼確認零行為改動**：`llmClient.ts` 新參數為 optional 且舊呼叫端不傳、`groundedSynthesis.ts` 全新檔只在 flag 開時執行、`wikiRepository.ts` 的 `queryVec` optional／`searchWikiRoutedExact` 受 flag 保護、合成窗收窄受 flag 保護並 fallback 回 `defaultWindow`。
5. **（指針）** `match_wiki_chunks_routed` 的安裝狀態與來歷限制 → `## Risks / Blockers` 第 2 項；S215 收工 QC 實測結果 → `## Validation / QC`。
6. S212–S214 的完整基線敘述與舊 Open Priorities 全文已移至下方 `## Detail Archive (S212–S214)`，**一字未刪**。


<!-- ack:section:validation-qc -->
## Validation / QC

QC（S215 收工實測）：`npm check`／`build` exit 0 · `regression:grounded` **48/48** · `route_regression` **46/46** · rank model／`eval_retrieval`／gold validator ALL PASS · active gold **185** · 工作區乾淨。`qc_report.json`（CI 09-06）overall **ERROR**，6 FAIL 之中 5 條屬既有 registry 家族。

**S216（治理升級節）**：`agent-handoff-kit doctor --root .` **status: passed，53/53**（v0.3.66；工具／項目記錄／npm latest 三向對齊）。本節**零程式碼改動**，故上面 S215 的產品側 QC 數值（`regression:grounded` 48/48、`route_regression` 46/46、active gold 185）**未重跑亦未失效** —— 它們綁定的 commit 與檔案未變。`qc_report.json` overall **ERROR** 未處理，狀態同 S215。 `closeout-status` 的 lifecycle 與 sufficiency 兩道語意閘**已通過**；整體仍報 `blocked`，唯一原因是 push 未獲授權（見 `## Risks / Blockers` 第 1 項）。

**S217（push ＋ 部署節）**：推之前跑齊 §3c 機器驗證閘，**全綠**：`npm run check` exit **0** · `npm run build` exit **0**（未弄髒工作區）· `npm run regression:grounded` **48/48 ALL PASS** · `node dev/source/route_regression.mjs` **46/46 PASS**。其中 `both synthesis flags off preserve the legacy synthesis prompt exactly` 一條，**以機器驗證了「flag 全 0 即行為不變」**，不再只是讀碼推斷。部署後生產側煙霧測試：`/api/search/channel-a` 教師專業操守 → 50 條 · `/api/search/channel-b` 幼稚園收生 → 8 條（top1 `k1_admission_2627` 0.738）· `/api/search/combined` → total 58（a 50 + b 8）＋ synthesis 395 字，三個端點全部正常。**未跑：185 題 live 套件**（啟用 flag 的前置閘，未動）。`qc_report.json` overall **ERROR** 未處理，狀態同 S215／S216。

**S217 追加逐檔行為核對（Leonard 追問「push 之後功能有無變」而做）**：以 `git diff 4a25a15 612e13e -- backend/src app.html` 逐個 hunk 讀過。結論分兩半 —— **無 flag 保護而真的改了生產行為的只有 establishment 路徑一處**（詳見 `## Current Baseline` 第 4 項）；其餘執行碼確認零行為改動。**觸發範圍已生產實測驗證為窄**：「小一派位第1班點分」（有「班」但不走 staffing）→ 未被編制表塞入；「教師編制點計」（走 staffing 但無班數）→ 正常。受影響那一條「12班小學有幾多個學位教師」實測回**學位教師 5／副校長 1／助理 14／合計 21**，與 S211 註解記載的正確一行相符（S211 量到的錯答是「學位教師 2／助理 7／合計 10」），且同表其他班數的列已全部不在結果內。**但這是 1 條事後觀察，不是 before／after 對照** —— 舊碼已不在生產環境，無法在同一環境跑對照組；整體有無副作用仍須 185 題 live 套件，未跑。

**S217 收工**：`session_log_maintenance.py --self-test` **5/5 passed**、`--apply` 歸檔完成並經無損驗證。`agent-handoff-kit doctor` **本節跑不到** —— CLI 不在 PATH、全局與本地 `node_modules` 皆無、npm 上 `agent-handoff-kit` 這個名字 404；改為自行驗證交接檔 29 個 `ack` marker 完整。**此項列為未驗證，不當通過。** 生產 `/health` 收工時實測 `ok:true`、`cache_a.warm` 455、`commit` `612e13e`。

**S218（起手探針節）**：**零程式碼改動、零 QC 重跑。** 本節只做起手探針五項，全部實測：served `app.html` **3.3.2** · Render `/health` **`ok:true` warm 455 commit `612e13e`** · Supabase `wiki_chunks` **17,610**（service key `count=exact`）· `source_registry` **281** · `git fetch` 後 `HEAD == origin/main == 0f8a7c9`、分歧 **0/0**、工作區乾淨。**S217 的產品側 QC 數值（`regression:grounded` 48/48、`route_regression` 46/46、`npm check`／`build` exit 0、active gold 185）本節未重跑，亦未失效** —— 綁定的 commit 與檔案本節一字未改。`agent-handoff-kit doctor` 本節同樣跑不到（CLI 仍不在 PATH，狀況同 S217），**列為未驗證，不當通過**。`qc_report.json` overall **ERROR** 未處理，狀態同 S215–S217。**未跑：185 題 live 套件。**

**S219（185 題閘節 —— 本專案第一次真正跑完這道閘）**：Leonard 批准後跑了兩套 185 題。**(1) 生產側 flags-off**（`dev/source/eval_runs/2026-09-08_s219_gold_prod_flags_off.json`）：PASS **117**／FAIL 43／**ERROR 8**，對 09-04 部署前那套（PASS 120／FAIL 44／ERROR 0）182 條共有題只有 10 條變動。**(2) route-first before／after**（in-process，`..._route_first_before.json`／`..._after.json`，raw 見同名 `.jsonl`）：before PASS 122 → after PASS 123；5 條 FAIL→PASS、4 條 PASS→FAIL。**方法學控制組成立**：56 條「無路由」題（flag 物理上無法生效）全部 before ≡ after，噪音底線 **0**，故每條變化均可歸因於該 flag。**四條「退步」全部是 rank 7 → 消失，而合成窗只取前 5（`searchChannelB.ts:962`），故答案層面影響為零**；五條改善為 None → 0／0／1／4／5。Source Recall@1 71→**73**、@3 99→**103**、@5 113→**116**、@8 122→123。**但 flag 的既定目的未達成** —— OP③ 三題目標片段 chunk rank 開掣前後不變（`hr_lsp` 0→0、另外兩題 None→None）。**路由健康度（after 側）**：routed 119／partial 9／silent-fallback 1／no-route 56，即 **10/185（5.4%）付出了 routed RPC 失敗的額外延遲**。S214 驗收條件中的「重複穩定性至少兩次」本節未做。**結論：本節未啟用任何 flag。**

**S219 追加：`57014` statement timeout 是本節最重要的發現，且與三個 flag 全部無關。** 生產側 8 條 ERROR 全屬此碼。三輪定向重跑（每輪 9 題）後分層：**持續壞** `dig_edb_cloud_guideline_na` 3/3、`cur_eight_kla` 3/3；**閃爍** `cur_eng_guide_2007_missing` 2/3；**其餘 5 條在輕負載下 3/3 恢復**，即 Run A 那 8 條有一半是我自己 185 題持續負載所誘發。**`staff_fullday_12` 經重跑 3/3 PASS 且 src rank 0**（09-04 為 rank 2），故先前「疑似被 establishment 改動弄壞」的推測**已推翻**。**【S219 二次更正】當時改提的機制（`searchChannelB.ts:1665` 的 `catch {}` 吞掉 `searchEstablishmentRows()` 超時）亦不成立** —— 後續實測該查詢只需約 338ms（等同網絡地板，服務端執行接近零，因為它不取 `embedding` 欄），以 anon 的 3 秒上限計算不可能是超時。`catch {}` 會靜默吞錯是**程式碼事實**，但它是否為 Run A 那一次失敗的成因**仍未查明**，不得當作已解釋。**未查證**：為何 09-04 同樣 184 題節奏卻 0 error 而今日 8 error（假說為 09-05 bot 入庫後語料變大令帶過濾的向量查詢越過 statement timeout，未證）。

**S219 根因調查：`57014` 的成因已量到，且與語料大小無關。** 直接對 live RPC 實測（繞過後端，54 次 `match_wiki_chunks` 呼叫）：**零超時**，中位 2.4–3.8 秒。由 Run B 的 144 次 routed RPC 儀測反推，**statement timeout = 8 秒**（16 次失敗有 15 次密集落在 8308–9503ms，下限 8308ms）。**兩項結構性發現：** (1) `s214_route_first_candidate.sql` 內 `set local enable_indexscan/bitmapscan = off` 強制全表 seq scan；該段註釋以「route 子集有界（最大約 3,500 條）」為理由，但**限制子集大小並不限制掃描範圍** —— 掃描讀的是全部 17,610 列。實測證實成本不隨子集大小變化：`finance`（34 chunks）458ms、`staffing`（1,415 chunks）560ms、`activity`（54 chunks）8304ms 兩次 57014。(2) **`schema.sql` 只有 ivfflat 向量索引，`source_id` 完全沒有索引** —— 故即使不 disable index scan，`where source_id = any(...)` 一樣只能 seq scan；`wikiRepository.ts:433/506` 那幾條 `source_id=in.(...)` PostgREST 查詢同樣受影響。**主路徑亦無餘裕**：`match_wiki_chunks` 走 ivfflat 索引仍需 2–3.4 秒，對 8 秒上限只有約 2.5 倍餘裕，所以 Run A 的持續負載會產生 8 條超時而輕負載只有 2 條。**⚠️ 以上全部依據 repo SQL，未經 live introspection** —— 依 playbook `inspect-live-infra-before-ddl`（S116 PGRST203 事故），repo schema 是意圖不是現況，任何 DDL 前必須先用 SECURITY DEFINER ritual 抽 live 定義核實。**本節零 DDL。**

**S219 成本模型已實測改正 —— 先前「全表掃描很貴」的假設是錯的，據此提出的兩個索引無法證明有效。** Live introspection（SECURITY DEFINER ritual，抽完即 DROP）核實：**`anon` 角色 `statement_timeout = 3s`**（`authenticated` 8s、`service_role` 無設定取預設 8s）—— 本節所有 in-process 量度都用 service key，即在 8 秒上限之下量度一個實際只有 3 秒上限的系統，故 route-first 的 11.1% 失敗率**低估**，扣除 308ms 網絡開銷後推算 production 為 **26.4%**（未實測，屬推算）。**兩支 `match_wiki_chunks*` 的 live 本體與 repo 逐句相同、各只有一個 overload、`anon` 對表只有 SELECT** → **`## Risks / Blockers` 第 2 項可結案**。索引核實：live 只有 `wiki_chunks_pkey`(btree id) 與 `wiki_chunks_embedding_idx`(ivfflat lists=60)；`vector` 擴充 **0.8.0（HNSW 可用）**、`pg_trgm` **未安裝**；`total_size` **363 MB > shared_buffers 224 MB**。**成本歸屬實測（本節最重要的方法學結果）**：由本機量到網絡地板約 **240ms**；`select=id` 全表掃 17,610 列 **242ms（等於地板，服務端掃描成本近乎零）**；`select=id,embedding` 取 **50 列即 1,042ms**（約 16ms／列）。**結論：成本在「逐列處理 embedding」，不在掃描。** 故 footnote(206 列)／spotlight(267 列) 兩個 overlay 的 1.6–1.8 秒是**傳輸與序列化 embedding**，任何索引都幫不到；establishment 查詢約 338ms 等同地板。**已建的兩個索引（`wiki_chunks_source_id_idx`／`wiki_chunks_content_type_idx`，Leonard 2026-09-08 執行）before/after 對照無法證明有效** —— 對照組（`match_wiki_chunks` RPC，物理上不受索引影響）同時變慢 53%，該輪量度不可信；改用交錯配對設計後，有索引與無索引欄位皆約 250–276ms，差異被網絡地板淹沒。**本機量不到低於約 250ms 的服務端差異，要定論須用 `EXPLAIN (ANALYZE, BUFFERS)`（另一次 SECURITY DEFINER ritual）或由 Render 後端內部計時。** 兩個索引各約 0.5 MB、無害，現予保留但**不得記為已修好任何事**。

**S219 修復落地：Channel B overlay 改為啟動期背景暖機，首請求罰時約 3.2 秒已消除。** 改動三個檔（`backend/src/lib/wikiRepository.ts`／`backend/src/api/searchChannelB.ts`／`backend/src/server.ts`，共 +100/-1 行），沿用 `initFactEmbeddingCache` 既有的「不 await 背景暖機」模式，並為兩個 overlay 載入器加 **in-flight 閘**（否則暖機與首個請求會各發一次同樣的 embedding 載入，冷啟動成本不減反增）。`/health` 新增 `cache_b: {warm, footnote, spotlight}`。**同環境 A/B 實測**（本機後端連 live Supabase，臨時開關停用暖機後量度，量完即移除該開關）：停用暖機時首個請求 **6,126ms**、其後 2,878／2,880ms；啟用後暖機於啟動 **2.46 秒**完成（`cache_b` 206／267），首個請求 **3,404ms**、其後 2,945／3,833ms。**排序零改動已以回歸證明**：`regression:grounded` **48/48**、`route_regression` **46/46**、`npm run check`／`npm run build` 皆 exit 0。**注意這是把成本移離用戶路徑，不是減少總成本** —— 每次程序啟動仍要付那 3.45 秒，只是付在沒有人等的時候。**未部署、未 push。**

<!-- ack:section:risks-blockers -->
## Risks / Blockers

1. **【S217 已解除，只監察】本地與遠端分歧已收斂，七個 commit 已 push 並部署。** Leonard 明示選項 1（連 backend 一齊推、接受觸發部署）。`42b1441..612e13e` push 成功，`HEAD == origin/main`，Render 於 19:26:49Z 起以 `612e13e` 運行。**rebase 保全已驗證**：舊 `463434c..1378b53` 與新 `42b1441..HEAD` 兩個 patch set **105,683 行／150 個檔逐位元組相同**，兩個 bot commit（`de030b7`／`42b1441`）已在祖先鏈。**餘下要監察的**：Option A watcher bot 仍會自行推送，下次開工若再落後，先 rebase 再處理（今次實測本地 commit 與 bot 觸及的三個資料檔零重疊，rebase 屬機械操作）。 **【S218 補】本節開工實測 bot 沒有再推 —— `origin/main` 仍是 S217 收工那個 `0f8a7c9`，不必 rebase。這不代表風險消失：watcher 仍在，只是這一輪沒有觸發。開工探針照樣要 `git fetch` 後比對，不得讀交接記載的 hash 當現況。**
2. `match_wiki_chunks_routed` **已裝於 live Supabase**（S215 零列探針，四參數簽名相符）。PostgREST 讀不到函式本體，故「已裝」不等於「與 repo SQL 相同」；安裝者與授權無記錄；線上 build 引用次數 0。任何 DDL 前仍須先確認 live 定義。
3. **【S217 已解除】** S216 那個治理 closeout commit（58 個路徑）已隨本次 push 上主線，不再是「本地提交未 push」。
4. 只監察 —— **【S216 新增】`AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 三個檔在 `.gitignore` 內且從未 tracked**（`git check-ignore` 實測）。**原因：** 這是本 repo 長期的 ignore 政策，除非 Leonard 改變該政策否則持續成立，本節不提議改動。**影響：** 本次升級改寫了 `AGENTS.md` 的 managed core 與 `GEMINI.md` 全文，這些改動只存在於磁碟、不在版本控制內。**更要留意：** `.gitignore` 的 `AGENTS.md` 規則無前置斜線，會在任何深度命中 —— 連 `dev/governance_migrations/<timestamp>/backup/AGENTS.md` 這份升級前備份都被 ignore（S216 `git check-ignore -v` 實測命中 `.gitignore:9`）。**結論：升級前的 `AGENTS.md` 全世界只剩磁碟上那一份，git 內沒有任何副本，刪咗就無得還原。**

<!-- ack:section:workspace-identity -->
## User Environment (Always Reference Before Giving Shell Commands)
- **Repo path**: `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft` (relocated 2026-05-16 Session 109; path contains a space — quote it)
- **Correct cd**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`
- **Python script invocation**: always from repo root, e.g. `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/vault/extract_candidates.py ...`
- **Backend**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && npm run dev`

<!-- ack:section:next-task-required-reading -->
## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Read `dev/PROJECT_MASTER_SPEC.md` (long-term spec + cross-agent handoff knowledge: goals, architected systems, proven methods, failure lessons, locked decisions)
4b. Read `dev/HANDOFF_PACKAGE.md` (Session 110+ — clean verified-state snapshot built by empirical check, not paraphrase; sits above the §1 read set as the trusted current-state map)
4c. **Lazy-query 共用經驗庫 Playbook**（S138 接駁、AGENTS.md §1 第 5 步 + §14）：開工只讀 `…/Leonard's playbook/playbook/INDEX.md`（細入口，**冇全表**）；撞到 task 就 `grep -i "<關鍵字>" …/playbook/INDEX_TABLE.md` 配 trigger，配到先開對應卡；唔好讀晒所有卡。**S212：pointer 已升 v2，用完一張卡要喺該庫 `usage/policychecker.log.md` 檔尾 append 一行。**
5. Confirm environment: backend needs `OPENAI_API_KEY` in `backend/.env`

---

## Architecture Decisions (Locked — 2026-04-16)

### Decision 1 — Public Entry + Full Workspace
```
index.html  ←  EDB S1 Home / document workspace entry
    │
    ├── q.html                  ← Quick Q&A (local knowledge.json search)
    ├── t-purchase.html         ← Template detail + draft flow
    └── app.html                ← K1知識平台 full React workspace

app.html
    ├── 🔍 政策搜尋              ← 已核實資料 / 來源文件 / 合併搜尋
    ├── 📚 指引文件庫              ← 3-level sort: category → sub_category → time desc
    ├── 📄 通告分析
    ├── ℹ️  平台介紹
    ├── ✍️  知識提煉（Admin）     ← 左右分欄佈局 + 即時行內修訂
    └── ⚙️  知識管理（Admin）
```

### Decision 2 — Backend API for Channel B Search
現有 Node.js TypeScript backend 擴展，新增端點：
```
/api/search/channel-a    ← role_facts.json keyword/semantic search
/api/search/channel-b    ← wiki_index.json cosine search (NO top-k limit, return all)
/api/search/combined     ← A+B merged, deduped, source-labelled
/api/channel-b/prompt    ← GET/SET Channel B extraction & synthesis prompts (Admin)
```
- Channel B 搜尋**不設 top-4 限制**，全數返回，前端分頁顯示
- 利用現有 `embeddingClient.ts` 做 query embedding
- 新增 `backend/src/lib/wikiRepository.ts`（載入 wiki_index.json + cosine 計算）

### Decision 3 — Platform Stats Are Dynamic (A+B Combined)
- 平台介紹 tab 的統計數字（事實數、chunks 數等）從實際資料動態計算
- 反映 Channel A（role_facts.json）+ Channel B（wiki_index.json）合計
- 不再硬編碼「109+」等數字

### Decision 4 — Channel B Admin Prompt Editor
- Channel B candidates 獨立於 Channel A queue
- Admin 可在「Channel B 後台」tab 編輯 SYSTEM_PROMPT_B 及 SYNTHESIS_PROMPT
- 提供測試沙盒（貼入段落 → 即時看提取結果）及新舊 Prompt 對比面板
- 品質指標：字數達標率、來源引用率、合規風險識別率

### Decision 5 — Two-Channel Knowledge Pipeline (Original)
**Channel A — Human Review（主線）**
```
source_registry → vault PDFs → extract_candidates.py
→ candidate_queue.js → Admin Approve (inline edit) → role_facts.json → Circular System
```

**Channel B — Full AI（副線）**
```
source_registry → same vault PDFs → ai_extract.py
→ ai_candidate_queue.json (independent) → wiki_index.json (vector search)
→ /api/search/channel-b (backend) → 智能搜尋 UI
```
- Channel B Circular System 接入**明確暫停**，待質素測試後決定

### Decision 6 — Guidelines Dual Sort
- GUIDELINES_REGISTRY 加入 `sub_category` 欄位（例如 `procurement`、`lsg`、`cpd`、`sen`）
- 排序：範疇 → 同科類 → 時序降序
- 視覺：同科分組小標題

### Decision 7 — WordCloud Removed
- QAPanel 的 floatWord 浮動動畫刪除（視覺效果差）

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. **S126 (2026-05-26)** `check_freshness.py --dry-run` = **Checked: 147 / Changes: 20 / Errors: 1 / Threshold: 7 → exit 0** ✅。**Root cause of 5 連 chronic fail since 2026-04-30 = script `AttributeError` 撞 `freshness_metadata=null` (line 101) crash 喺 entry ~22，唔係 handoff 估計嘅 `if errors > 0: sys.exit(1)`（後者係次要、threshold 太嚴）**；§G.2 verify-don't-trust-docs 再中。修：`meta = src.get("freshness_metadata") or {}` + `threshold = max(5, total_checked // 20)` gate + summary 加 failed-sids list 方便 GH Actions log artifact 分析。20 EDB CHANGE detected（包 sag_2025_11 / g24 / g29 / stat_* 等）+ 1 dead URL g28 — freshness_metadata 寫返 registry 留下次 sub-task；g28 EDB URL re-discovery 列 follow-up。
3. ⚠️ **`npm run regression:semantic` 實測 2026-05-17 S113：overall=FAIL（PASS=9 / FAIL=2）**。原寫「Online semantic regression PASS=12/FAIL=0 (2026-04-12) ✅」**已 false / stale**（2026-04-12 舊值，dedup 前；S113 startup verify 教訓再現 §G.2）。兩個 FAIL 同 S1/S2 無關、Leonard 裁示**只記錄不修**：
   - **FAIL-A（真 product regression）role-bucket `finance_distinct=false`**：S111 dedup（792→455，2026-05-16）把跨角色重複摺入 `all_roles`，令 `finance.all_roles`=83 條/2832 字；`knowledgeSelector` 排序 all_roles 行先→砍 600 字，頭 ~14 條 all_roles 已蓋爆 budget，**subject_head/panel_chair 角色專屬 finance 事實永遠注入唔到** → Circular System 對該兩角色嘅 finance 注入自 2026-05-16 起退化成「只通用、無角色專屬」。無 budget 時 distinct=True（角色拆分本身冇壞）。**未修**（涉 dedup/budget/排序設計決定，待 Leonard 排）。
   - **FAIL-B（瑣碎 doc-debt）schema consistency**：`backend/scripts/semanticRegression.ts:292` 硬斷言 `version === "1.3.1"`，實際 knowledge=2.3.0 / guidelines=2.2.0。stale 測試斷言，無行為影響。**未修**。
4. `npm run check`（typecheck）✅ / `npm run build` ✅（S113 實測，未變）。
5. **✅ S209 實測定案（唔使再查）：`check_served_urls.py` 監察嘅係 `wiki_chunks.url`，唔係 registry `url_primary`。** `fetch_served_urls()` = `SELECT url, source_id FROM wiki_chunks` 全表分頁，CI `limit=0` 全掃。所以**任何 per-chunk URL（含 S207 嘅 section deep link）一入庫即受每週一 11:00 UTC 監察**。證據四重：(a) live 逐源比對 g14 10 + g17 6 = **16/16** 真係喺 `wiki_chunks.url`；(b) CI run #11（2026-08-24 11:18 UTC）17,478 rows → **299 distinct URL 全測**，295 OK / 4 broken / 0 error，broken 冇一條係 g14/g17；(c) 本地 `--verbose` 全掃複現同一組數，16 條逐條印 HTTP 200；(d) distinct URL 08-17 **284** → 08-24 **299**，新 deep link 自動入集。紅測：唔存在嘅 `chapter-seven.html` → 404 → broken → 歸屬 g14。**錯誤源頭已清**：S207 `verify_section_urls` docstring、handoff OP⑥、DOC_SYNC row 41 三處。
6. **⚠️ S209 記錄：監察報住 4 條真 404 冇人跟。** `edb_pnet_annex_jul2025`、`eoebg_rates_2026` 最遲 2026-08-03 起壞；`blnst_test_candidate_notes`、`blnst_test_notes_nondeg` 最遲 2026-08-10 起壞。GitHub Issue #6 開住。用戶撳落去係真 404。**監察系統正常做嘢，係下游冇接手** —— re-anchor 係人手閘，要 Leonard 逐條批。同 S195 嗰兩條一樣嘅家族。
8. **✅ S209 實測定案：公開片段數以前係流水帳，唔係真數。** `execute_ingest.current_chunk_total()` 由 `knowledge.json` 讀個數再加自己嗰筆 delta 寫返七個鏡像檔 —— 純加法、從來冇對過 Supabase，所以歷史上任何一次少計都永久帶落去（實測長期少 1）。已改為入庫後 `live_total_count()` 由 store 讀真數，舊數只留低做「要替換嗰串字」同 fallback，唔夾會出 CI annotation。**改動後唔好再靠加減推算片段數** —— 清走 chunk 之後一律行 `live_display_sync(current_chunk_total(), live_total_count())`。
9. **✅ S209：4 條 404 已清（Leonard 批）。** 兩條純 URL churn re-point（`eoebg_rates_2026`、`edb_pnet_annex_jul2025`，四個引用數字逐個對返新 PDF 先寫）；兩條 `blnst_test_*` 共 13 chunks 係 2026-06-07 場次文件、EDB 整個 notes 家族落架 → 退役刪除，registry status=deprecated。**刻意冇指去 `QA_BLNST_Apr26_tc.pdf`**（另一份文件；200-但-錯檔比 404 更難捉，見 S194 `ict_sss_2021`）。BLNST 覆蓋由 `edbc13_2022_blnst` + `edbcm141_2025_blnst` 承接，backend SOURCE_SET 已清走死 id。
11. **✅ S209：`g28` 已入庫（40 chunks / 7 份文件），但揪出兩個未修嘅殘留。** (a) **`g17` 兩條 chunk 頁碼錯** —— S207 把三份各 1 頁嘅附件連續編成 Page 1/2/3，UI 顯示「頁 2 ↗」「頁 3 ↗」都指唔到；修法＝重生 extract + 重入 13 條。(b) **`gifted_policy_docs` 10/23 chunks** 喺新切法下會改善（佢有 `=== introduction === / === detail ===` 但冇 `section_urls`），要重入庫先生效。(c) **g28 唔使 spotlight** —— 加咗又同一 session 移走：用**內容專屬** query 實測（未部署任何 route 改動嘅 build），「Zoom 保安設定及使用建議」rank **0 @0.628**、「殭屍網絡」rank **1 @0.396**，純 ANN 已經到位。我最初用闊 query（「學校資訊保安」）搵唔到就當係「新細源 ANN 餓死」，**係揀錯 phrasing 得出嘅結論** —— 同 S195 spotlight prune 中嘅陷阱一模一樣，只係方向相反。(d) **route regex 未動** —— `digital_education` 個關鍵字 regex 冇任何資訊保安／網絡安全／雲端字眼，所以「資訊保安」一類 query 仲未 route 到嗰度；g28 而家靠 spotlight overlay 出街。改 regex 係檢索改動，要行 eval before→after 先做。
12. **❌ S209 實測：EDB 冇「學校使用雲端服務指引」。** g28 hub 上 8 份實質文件全文掃描，「雲」／"cloud" 合共 **0** 次；EDB 資訊保安頁「雲」字亦 0 次。最接近嘅權威文件係 **PCPD《雲端運算指引資料》(2025-01，13 頁)**（Leonard 提供），講 PDPO 保障資料第 2(3)/3/4 原則同第 65(2) 條，但「學校」／「教育」0 次，係通用機構指引。OGCIO/DPO 有 ISPG-SM04 雲端保安實務指引，但個 PDF URL 而家跳去 JS-gated 頁，curl 抽唔到，且對象係政府部門。**未入庫，待 Leonard 決定。**
13. **📌 S209 記錄：非-EDB 來源唔係先例問題。** 庫入面已有 **8 個非-EDB 域、208 條 chunk**（教城 81 / 廉署 78 / 衞生署 14 / 教育條例 ILO 11 / 機電署 7 / 審計署 4 / 學資處 2+11）。但 registry `authority` 欄位 **273/273 全部寫死 `edb`** —— 呢個欄位一直冇如實反映，屬資料品質債。
10. **🧭 S209 通則（一 session 內喺四個地方撞到同一條病）：任何要人做決定嘅表面，都必須有出口。** 只入唔出嘅清單一定會變牆紙，跟住真訊號就會被埋葬 —— Issue #6 由 2026-08-03 起準確列住 4 條真 404，冇人跟，因為佢同幾百項噪音混埋。四個實例同修法：(a) **待批入庫清單** 45 日 feed 窗令「唔會剔」嘅過渡通告霸住六星期 → 超過 21 日收摺；(b) **served-url issue** clean run early-return，永遠開住掛住舊清單 → clean run 留言＋自動閂；(c) **discovery issue** 每週重報成個 backlog（238 項，大部分永遠唔會入庫）→ 加 first-seen 帳，只報今次新出現嘅，backlog 收摺；(d) **expiry 清單** 已清走嘅源 chunks=0 但仍然過期，會永遠掛喺待辦 → 拆「待清走 / 已清走」。**改任何一個監察嘅 issue 開閂邏輯或清單長度，順手檢查其餘幾個**（已入 DOC_SYNC row 35）。
7. **✅ S209 新機制：`refetch_blocked`（registry 欄位）+ `expand_vault.run_fetch()` 下載前 fail closed。** 覆蓋 `expand_vault --fetch` 一條路；`dev/vault/process_signals.py` 亦寫 vault extract，但佢只處理通告 feed 嘅新 PDF signal，砌唔到現有 `section_urls` 源，故唔需要同一道閘。`test_carry_rules.py` 17→30 斷言（含結構不變式：有 `section_urls` 必有 `refetch_blocked`），`--prove-assertions` 8→16。

---

<!-- ack:section:next-priorities -->
## Open Priorities

**Recommended next step（S218 重生）：** 補 `backend/README.md` 遺失的 5 行 flag 說明（②），或行離線工作追三題 chunk recall（③）。**理由**：S218 起手探針證實所有狀態量與 S217 收工時一致、bot 本輪未推、無任何會隨時間惡化的事項待處理；餘下各項全部離線可做。**下一道真閘仍是 185 題 live before／after（①）** —— 未跑之前不得啟用任何 feature flag，需 Leonard 另行批准外部模型批次。

① 🔴 **【最高優先，S217 定性後未動】185 題 live before／after 未跑，且現在有兩個非跑不可的理由。** (a) 它是啟用三個 flag 的唯一閘；(b) S217 查出 establishment 路徑的改動**無 flag 保護、已在生產生效**，所以它同時是「已生效改動有無副作用」的唯一量度工具 —— 目前只有 1 條事後觀察，184 條未量。**需 Leonard 批准外部模型批次。**

② **【S215 新增，未補】`backend/README.md` 遺失 5 行 flag 說明。** S215 `reset --hard` 事故所致，無任何備份來源；**不得杜撰**。補寫時須在 commit message 明寫是重寫非還原。

③ **【S214 遺留，未解】三題 chunk recall。** `hr_lsp` 完整公式跨第 3／4 頁而 `dominant_page()` 判第 3 頁；`sen_special_school_curriculum` 的 `g10` 與中史 NCS 目標片段均未入首 8。已證目標 chunk 不在新 RPC 原始 40 項之內，故根因不在後處理 —— 下一步離線查 query expansion 與向量排名。

④ **【S214 遺留，未修】4 條 fidelity 不一致 ＋ 合成窗佔用率。** 3 條分數完全相同而生產 tie 次序非 id 升序（**真正 tie 規則未查證，不得憑猜**）；1 條 `fin_seg` 的 `edbc015_2026` 未解釋。overlay 平均佔 **2.22/5 格**（44%），純提高門檻在數學上不可行。

⑤ **【S212／S213 遺留，全部未動】** 658 代號標題 backfill（`dev/_s213_title_backfill.py` dry-run 已跑，執行被分類器擋住，須 Leonard 自己跑）· `kgecg_2017` 108 條 ZOMBIE · header 剝除正則吃掉 33 行正文（涉 2,212 條 chunk，修正要重入庫）· 七個 standing WARN 無 waiver ＋ 六項人手檢查未簽核 · `g33`／`g37` 標題錯掛 · `TOPIC_KEYWORDS.safety` 認裸「氣體」· 六個監察未接入狀態頁。**全文見下方 Detail Archive。**

> **S218 合規備註：** 依 `AGENTS.md` §4 交接精簡預算（Open Priorities 上限 5 項），S217 的 ① 已結案故移除（事實已在 `## Current Baseline` 第 2 項），治理側兩項（原 ⑥ `ack` marker、原 ⑦ `INIT.md` 鏡像）**原文一字不刪移入下方 `## Backlog` 的「治理側」段**。本節無任何項目完成，故其餘各項按當前狀態重新排序後覆寫，非複製貼上。
## Backlog（次優先序，視 OP 完成情況流轉）

**治理側（S216 新增；S218 由 Open Priorities 原文移入，一字未改）：**

⑥ **【S216 新增，部分已修】交接檔仍有 8 個 `ack` marker 未有專屬章節。** `durable-anchors`／`closeout-reconciled-state`／`task-understanding-summary`／`active-objective`／`sync-status` 五個 section marker，加 `user-intent`／`task-essence`／`success-criteria` 三個 field marker，現時集中放在檔頂並附註釋說明。**不影響 `doctor` 與 `closeout-status`**（前者只檢查 marker 存在，後者只讀四節加開場白），但這些章節對下個 agent 而言機械上讀不到。**已修的一半**：`completed-this-session` 原本會一路抽到 `## State Reconciliation Check`（涵蓋所有 `Previous Session Record` 與 `Detail Archive`），令 `closeout-status` 把 S215 的完成項當成本節完成項來做 lifecycle 比對而報 blocked；S216 在 `## Previous Session Record (S215)` 之前加了一個本地邊界 marker `ack:section:session-history`，抽取長度由 164,616 字元收窄至 2,133 字元，只涵蓋本節記錄。

⑦ **【S216 新增，blocked】`dev/DOC_SYNC_CHECKLIST.md` 的 INIT.md 鏡像規則已失效。** row「Governance rule change (AGENTS.md)」與「New governance file added to install」要求同步 `INIT.md` FILE 1 mirror，但 `INIT.md`（1,036 行，2026-05-10）鏡像的是 package 化之前的 AGENTS.md 結構（§4a／§5a／§11a），v0.3.66 核心根本沒有這些章節。**本節不執行該同步**，因為要先決定 `INIT.md` 是否已退役 —— 這是 Leonard 的決定，不是機械同步。

**S204 新增／流轉：**
- **【S210 新增，Leonard 2026-08-26 拍板】正文連結零監察 —— 開新監察嘅正確落點。** 起因係 Leonard 問「課程專頁使唔使 monitoring」。**定案：課程專頁唔監察** —— 只得 2 條、逐學期換（`debp-pdp.html` 課程表、教城 EdAcademy），監察掛上去週週報「有變」，正正係紀律 #14 嗰種必然變牆紙嘅閘；而耐用嗰半邊（每三年 30 小時培訓／每年 50,000 名額）已經喺 EDBCM156 同《藍圖》入面入咗庫兼受監察。**真缺口喺另一邊**：全庫 17,568 條 chunk 掃過 —— anchor URL（`wiki_chunks.url`，受每週一監察）**420** 條；寫喺 chunk **正文**入面嘅 URL 形狀字串 **3,011** 條；兩者只重疊 **6** 條 → **3,005 條零監察**。頭幾個 host：`www.edb.gov.hk` 733、`applications.edb.gov.hk` 74、`www.hkedcity.net` 45、`bit.ly` 18。用戶喺答案入面撳嘅連結，絕大部分冇任何嘢睇住。**⚠️ 3,005 係上限唔係實數**：PDF 換行會把一條 URL 斬成幾段殘缺字串（S210 喺 EDBCM156 就要人手重組先攞到真 URL），要真數必須先對全庫做同一套重組 —— 呢個重組本身就係呢件工嘅第一步。監察機制上 `check_served_urls.py` 只 `select=url,source_id`，**從來唔讀 chunk 正文**，所以呢個缺口係結構性、唔係漏咗跑。
- ~~**時限性資料標示**~~ → **S209 已建，定案細分咗**（Leonard 2026-08-24 補充）：S204 原本寫「標示而唔係刪」，而家分兩類 —— **年度版本文件**（費率表、校曆、年曆）舊版仍是當年依據 → 照舊 `dated_edition`**標示唔刪**；**一次性事件文件**（簡介會／培訓／比賽／獎項提名／測試場次／報名截止）過咗零參考價值 → `ephemeral` **到期清走**。已落地：`dev/source/lifecycle.py` 分類（入庫時 stamp 四個 registry 欄位）+ `dev/source/check_expiry.py` 第 6 監察 + ops `expiry-issue.yml` 每週二剔一剔清走。**仲未做**：(a) UI 顯示 `現行 / 已過期 / 已有新版` 標示（前端零改動至今）；(b) 271 個舊源冇 `lifecycle` 標，`check_expiry.py --classify` 可出提案但未 backfill；(c) 「每年檢查 landing page 有冇新學年版」呢半邊仍未做。
- **公眾提交表單**（Leonard 提）：Phase 1 = Google Form + 平台加一粒「意見／報錯」掣（零代碼，先驗證有冇人用）；Phase 2 = 站內表單 → 現有 Render 後端 → Supabase 新表（要處理防濫發、唔收非必要個人資料）。
- **範本下載恢復**：`policy_templates.json`（106 檔／15 範疇）未隨知識庫更新，S204 已用 `window.FEATURE_TABS.templates=false` 收起。重新生成 manifest 後把 flag 揼返 true 即復原（面板 code 原封未動）。
- **真亂碼未量度**：S204 掃描時偵測器分唔清長 URL／底線填充，故**冇報數**。`gifted_ge_series` 確有真 CID 亂碼實例（playbook `pdf-extraction-mojibake-triage`）。要做要另寫準確偵測。
- **承 S203 未完**：judge 對象移植非-prompt 機制（②，工具 `v4a/v4b_s202.txt` + fresh 集已備）；Channel A Option 2 入庫 117 條（③，HIGH risk 跨 session）；24 條純職責歸屬孤兒決定（④）；`PUBLISH_PAT` fine-grained 確認（⑤，只有 Leonard 做得到）；拆 backend channel-a 半邊（⑥，**S205 已解鎖** —— route-probe 兩次讀齊、零外部呼叫、probe 已刪，前置條件已滿足）；總帳 172 UNVERIFIED + 107 PROVISIONAL 未讀（⑦）；g24/sag 合併 PLAN 備妥等 GO（⑧，真數 377 重疊、g24 零獨有內容）；維護：封面 baseline 208 / spotlight 6 源 / `MIN_OVERLAP` 兩份鏡像（⑨）。

**原有：**
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）
- **雲端 OCR 引擎選項**（image-PDF ingestion 升級線，S180 評估）：Google Vision `DOCUMENT_TEXT_DETECTION`（逐字信心 + bounding box、每月 1,000 單位永久免費 + ~$1.50/1,000、要綁卡開 billing）／Mistral OCR（Markdown+表格、~$2/1,000）——比現用 `gpt-4o` 圖像 OCR「draft 質」可能更準更平，且 bbox 可餵返 grid 重建。命中 image-PDF 質素問題（如 DEBP 主藍圖 ~16 圖像頁）先評估：**真檔實測 + 開 Google billing**（ingestion 處理公開文件、無未成年私隱顧慮；後端已存在故唔需要 brief 嗰套 serverless key-proxy）。詳見 playbook inbox 提案 `2026-06-24-edb-knowledge-cloud-ocr-engine-options.md` + `doc-extract-method-ladder` 卡。出處：Leonard 一份 OCR 收費版 brief（2026-06，已核實價）。

<!-- ack:section:completed-this-session -->
## Last Session Record

1. UTC date: 2026-09-08
2. Session ID: `Claude_20260908_0705` — S218。由 Leonard 一句「開工」起做起手探針；其後 Leonard 問桌面與 Claude mobile 對話有何分別（純資訊回覆）；最後「先對齊正確的 root，然後收工」。**零程式碼改動、零 QC 重跑、零外部寫入。**
3. Completed:
   - ✅ **起手探針五項全部實測相符**：served `app.html` **3.3.2** · Render `/health` **`ok:true`／`cache_a.warm` 455／`commit` `612e13e`／`started_at` 2026-09-08T06:58:08Z** · Supabase `wiki_chunks` **17,610**（service key `count=exact`，Content-Range 實讀）· `source_registry` **281** · `guidelines.json` `_meta` **2.6.1**。
   - ✅ **git 漂移已查明並定性為非問題**：`HEAD == origin/main == `0f8a7c9``（S217 記的 `612e13e` 已過時），分歧 **0/0**，工作區乾淨。差距只是 S217 自己的兩個 commit（`72b5adb`、`0f8a7c9`）；**`git diff --name-only 612e13e..HEAD -- backend app.html` = 0 個檔**，故生產跑的執行碼與 `612e13e` 那次部署相同。Render `/health` 仍報 `612e13e` 與交接第 5 項記載的 `RENDER_GIT_COMMIT` 現象一致 —— **成因本節同樣未查證，不當已解**。
   - ✅ **Option A watcher bot 本輪未推**：`origin/main` 仍是 S217 收工那個 commit，**不必 rebase**。S217 開工那次「遠端走前兩個 commit」的情況本輪未重演。
   - ✅ **Playbook pointer 自我檢查（§14／該庫 INDEX.md 要求）**：本 project pointer 為 **v3**（最新），無須重裝，無須告知用戶。只讀 `INDEX.md`，**未 grep 全表、未開任何卡**，故按規則**不寫 usage 行**。
   - ℹ️ **一次純資訊回覆**：Leonard 問「在這裡開 session 然後在 Claude mobile 對話，跟桌面有何分別」。已答核心是「運算留在這部 Mac，手機是遙控器兼視窗」，並逐項列出不變／會變的地方，同時**明確標示手機端 UI 細節（Run 掣、批准提示樣式）屬推斷、未實測**。無檔案改動。
4. Not done / 未做：**產品側零推進。** 185 題 live 套件未跑、三個 flag 未啟用、`backend/README.md` 5 行未補、三題 chunk recall／4 條 fidelity／S212–S215 全部遺留一項未動。`agent-handoff-kit doctor` 本節跑不到（CLI 仍不在 PATH），**列為未驗證**。
5. ⚠️ **零程式碼改動、零 Supabase 寫入、零 DDL、零 flag 啟用、零外部模型批次、零 git push。** 本節唯一的寫入動作是本次交接與 log 的持久化。

## Previous Session Record (S217)

1. UTC date: 2026-09-07
2. Session ID: `Claude_20260907_1930` — S217。由 Leonard 一句「開工」起做起手探針，揪出遠端再次走前；Leonard 自行執行 rebase 後選項 1，Claude 過機器驗證閘、push、部署、驗證。**零程式碼改動** —— 本節未寫過一行 `backend/` 或 `app.html`，只是把 S213–S216 已寫好的碼送上主線。
3. Completed:
   - ✅ **起手探針五項**：平台 v3.3.2、Render `/health` `4a25a15` warm 455、Supabase 17,610、`source_registry` 281 全部與交接相符；**唯一漂移是 `origin/main` `463434c` → `42b1441`**（兩個 bot commit：`de030b7` discovery ledger、`42b1441` QC 報告重生），本地由「領先七個」惡化為**真分歧 7 ahead／2 behind**，直接 push 會被拒。
   - ✅ **實測 rebase 零衝突風險再建議**：merge-base `463434c` 起計，本地七個 commit 與 bot 觸及的三個檔（`discovery_seen.json`／`registry_drift.md`／`qc_report.json`）**零重疊**。Leonard 自行執行 rebase。
   - ✅ **rebase 內容保全逐位元組驗證**：舊 `463434c..1378b53` 與新 `42b1441..HEAD` 兩個 patch set **105,683 行／150 個檔完全相同**；兩個 bot commit 確認在祖先鏈（`merge-base --is-ancestor`）。作者名由 rebase 一併正規化為 `leonard-wong-git`。
   - ✅ **§3c 機器驗證閘（推之前跑）全綠**：`npm run check` 0 · `npm run build` 0（未弄髒工作區）· `regression:grounded` **48/48** · `route_regression` **46/46**。其中一條斷言 `both synthesis flags off preserve the legacy synthesis prompt exactly` **以機器證實了「flag 全 0 即行為不變」**，把我上一輪只憑讀碼的推斷升級為驗證。
   - ✅ **Push ＋ 部署**：Leonard 明示選項 1（連 backend 一齊推、接受觸發部署）。`42b1441..612e13e` push 成功，分歧歸零；Render 自動部署，`/health` 於第三次輪詢（19:27:03Z）讀到 `commit=612e13e`、`started_at` 19:26:49Z、`cache_a.warm=true size=455`。**S214 起累積四節 session 的未 push 狀態結清。**
   - ✅ **生產側煙霧測試**：`channel-a` 教師專業操守 → 50 條 · `channel-b` 幼稚園收生 → 8 條（top1 `k1_admission_2627` 0.738）· `combined` → total 58（a 50＋b 8）＋ synthesis 395 字。
   - ⚠️ **一次 0 結果已查明不是 regression**：部署後第一個 `採購程序` 請求回 0 條，隨後連跑 5 次全部回 8 條、shape 一致。發生在實例剛重啟（19:26:49Z）後的首個請求，屬 S118 已記錄的 probes=8 free-tier 冷啟動／間歇族。**但我沒有保存那次的 response body，所以無法證明它是 57014 timeout 而非其他** —— 只能說「不是本次部署引入的新問題」，不能說「已確認成因」。
   - ✅ **Playbook 留底（§14）**：交提案 `inbox/2026-09-07-policychecker-flag-gated-not-behavior-neutral.md`（pattern）。先 grep 全表兩輪並開過 `zero-regression-default-path` 確認方向不同（設計側 vs 驗證側），已註明建議互相引用；`usage/policychecker.log.md` append 一行 `lookup`；零接觸 trunk。順帶清走該庫一個上一 session 遺下未 push 的提案 commit，三個一併推上。
   - ✅ **收工歸檔（§4a 觸發）**：`--check` 報 494 行 > 400 門檻 → `--self-test` 5/5 → `--apply`：494→197 行、8→3 條 entry、5 條入 `dev/archive/SESSION_LOG_2026_Q3.md`。無損已驗證（8 條標題全部可尋回，抽樣逐字相符）。
   - ⚠️ **`72b5adb` 未觸發新部署**：`/health` 的 `commit` 讀 `process.env.RENDER_GIT_COMMIT`（部署時設定），現仍報 `612e13e`，而 `started_at` 由 19:26:49 變 19:50:49 —— **服務重啟過但 `RENDER_GIT_COMMIT` 未更新**。**我沒有查證 Render 的觸發設定，成因未確認。** 實務無影響：`72b5adb` 零執行碼改動。
4. Not done / 未做：**產品側零推進。** 185 題 live 套件未跑、三個 flag 未啟用（閘未開）、`backend/README.md` 5 行未補、三題 chunk recall／4 條 fidelity／S212–S215 全部遺留一項未動。
5. ⚠️ **零程式碼改動、零 Supabase 寫入、零 DDL、零 flag 啟用、零外部模型批次。** 本節的寫入動作只有：一次 `git push`、以及本次交接與 log 的持久化。

## Previous Session Record (S216)

1. UTC date: 2026-09-07
2. Session ID: `Claude_20260907_1900` — S216。由 Leonard 一句「讀取安裝說明頁，在這個資料夾安裝或升級 Agent Handoff Kit」起，做 Kit v0.3.29 → v0.3.66 升級，**零程式碼、零檢索、零產品改動**。
3. Completed:
   - ✅ **升級完成並驗收**：`Draft/` 由 **v0.3.29 → v0.3.66**，`doctor` **status: passed 53/53**，工具／項目記錄／npm latest 三向對齊。create 1 / merge 14 / skip 8 / **conflict 0**。
   - ✅ **解開四層 conflict**（首次 `upgrade --yes` 因 conflict 全數拒寫，零檔案改動）：`GEMINI.md` 舊 stub 換官方 bridge（原檔零本地自訂）· `SESSION_LOG.md` 換官方頭部而 440 行歷史**逐位元組驗證一致** · `communication.md` 改為「官方 v0.3.66 本體 ＋ 本地附錄」，S196 六條 claim discipline 全保留並把交叉引用同步改為 L1–L5 · `SESSION_HANDOFF.md` 21 個 `ack:` marker 由檔頂目錄搬到各自章節。
   - ✅ **查出並修好一個隱形治理 bug**：`lifecycle-conflicts-resolved` 這個 field marker 因 marker 疊在檔頂目錄，`fieldValueAfterMarker()` 向下抓到 `## User Environment` 的 Repo path 當值 —— 該 check 一直靠垃圾值「通過」。
   - ✅ **新建 `## Validation / QC` 與 `## Risks / Blockers` 兩節**：內容由 `Current Baseline` 第 2、4、5 項搬入，原位留指針，零重複、零杜撰（gate 要求這兩節機械可讀，而本檔原本沒有）。
   - ✅ **揪出並還原一次工具造成的資料損失**：`upgrade` 把 `## Next Session Opening Message` 整段換成官方通用開場白，`START_NEXT_SESSION_PROMPT.txt` 由 70 行變 4 行，S215 那 **65 行專案狀態**（六個 commit 明細、事故必讀、四項已確立事實、未解決清單、`Post-startup first action`）在兩個 live 檔同時消失。已由 CLI 備份取回並接在官方合約句之後重建，mirror 重生，`doctor` 仍 53/53。
   - ✅ **逐檔核實無內容損失**：比對 npm 上的 v0.3.29／v0.3.30／v0.3.32／v0.3.43 原檔，證實 `onboarding.md`／`integrations.md`／`knowledge.md`／`safety.md`／`writing.md`／`agent-governance.md` 六個 pack **與其綁定的官方版本逐字相同、零本地自訂**，故換新版沒有失去專案內容；`release.md` 消失行數 0。
   - ✅ **起手數字更正**：本地領先 `origin/main` **六個** commit，非交接記載的五個（漏計 S215 自己的 closeout commit `6cb80c6`）。
   - ✅ **治理檔已本地提交**：本節 S216 closeout commit（58 個路徑，指定檔案逐個 `git add`，未用 `-A`）。按 Leonard 明示，**只 commit 不 push**。
4. Not done / 未做：本節只做治理升級，**產品側零推進**。未完成與未動的項目一律見 `## Open Priorities` ①–⑦ 與 `## Risks / Blockers`，不在此重複列舉（避免同一事實有兩個出處）。
5. ⚠️ **零 push、零 deploy、零 DDL、零 Supabase 寫入、零程式碼改動、零產品行為改動。** 本節唯一的網絡動作是讀取安裝說明頁一次、`npm view`／`npm pack` 取官方 package 五次。
6. ⚠️ **`AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 的升級改動不在版本控制內**（三個檔 gitignored 且從未 tracked），唯一還原點是 `dev/governance_migrations/2026-09-07T18-23-33-046Z-*/backup/`。

<!-- 本地邊界 marker：令 completed-this-session 的抽取範圍止於本節記錄，唔會讀落歷史 session 記錄 -->
<!-- ack:section:session-history -->
## Previous Session Record (S215)

1. UTC date: 2026-09-07
2. Session ID: `Claude_20260907_1400` — S215。由「開工」起，做起手探針覆核 → 盤點 Codex 交低的 97 個髒路徑 → 分批 commit → 遇上 `reset --hard` 事故 → 逐項救援與驗證 → 收工。
3. Completed:
   - ✅ **起手探針揪出四項交接漂移**：Supabase 17,602→**17,610**、`source_registry` 279→**281**、線上部署 `f513a18`→**`4a25a15`**、`HEAD==origin/main` 05ea10e→**`463434c`**。成因是 Option A watcher bot 於 09-05 自行推送兩次入庫（`edbc016_2026` +6、`edbcm141_2026` +2），非人手改動。
   - ✅ **證實 `match_wiki_chunks_routed` 已裝於 live Supabase**（零列探針 `source_ids=[]` 回 `200 []`，四參數簽名相符），推翻交接「RPC 未安裝」的記載。同時證實線上 build 對它的引用次數為 0。
   - ✅ **揪出 merge 次序陷阱**：機械人 09-05 把兩個新來源加入 `SOURCE_SETS` 與 `SPOTLIGHT_SOURCE_IDS`，而 Codex 的本地 `searchChannelB.ts` 對它們引用次數為 0。只取任何一邊都會令 8 條片段跌出 route allowlist —— 與 `chi_hist_jss_ncs_2019` 同一病。
   - ✅ **五個本地 commit**（全部未 push）：`05854d5` 語料 header 根因封死（19 個 extract，正文位元組不變）· `3f31905` 評測工具＋30 個 eval_runs artifact＋gold · `8d90e56` S214 七份報告 · `5f7ce6e` 治理文檔 · `744a8dc` S214 候選全套（三個 flag 全 `0`）。
   - ✅ **`reset --hard` 事故全面救援**（詳見 SESSION_LOG）：四個 commit 用 `merge --ff-only` 救回；`llmClient.ts`／`package.json`／`.env.example` 逐字還原；`schema.sql` 由 `s214_route_first_candidate.sql` 還原（38 +，與原記錄吻合）；`wikiRepository.ts` 由 gitignored 的 `backend/dist` 反建，重新編譯後與倖存 dist **逐位元組一致**。
4. Not done / 未做：185 題 live 套件未跑；三題 chunk recall 未查；4 條 fidelity 不一致未修；合成窗佔用率未改善；S212／S213 遺留全部未動；**`backend/README.md` 5 行永久遺失，未杜撰補回**。
5. ⚠️ **零 push、零 deploy、零 DDL、零 Supabase 寫入、零重切語料。** 本節唯一的網絡動作是三個唯讀探針（HTTP GET ×2、Supabase count ×1）、一次 `git fetch` 與一次 `git pull --ff-only`。
6. ⚠️ **本節有一次由 Claude 造成的資料損失。** Claude 交出的回退指令附了「不會刪走未追蹤檔」這句錯誤保證；Leonard 據此執行後，`reset --hard` 刪走已 commit 的 55 個檔並還原六個未 commit 的 backend 檔。除 `backend/README.md` 外全部已復原並驗證。

## Previous Session Record (S214)

1. UTC date: 2026-09-04 → 2026-09-06（跨午夜；中途機器休眠一次）
2. Session ID: `Claude_20260904_1204` — S214。由「開工」起，Codex 以 QC Governor 身分逐 gate 下單：Phase 1.1 → Gate 1 根因分析（唯讀，兩輪 QC 退回修訂）→ Gate 2A1 測試基建 → Gate 2A2／2A2b 生產實作 → grounded synthesis 兩批 40 題 acceptance → 選窗修正、gold 重審及 18 題 V3 重驗。
3. Completed:
   - ✅ **Phase 1.1 A–E 全部完成**，證據見 `dev/_s214_phase_1_1_report.md`。A 的 NFKC 修正落在 `dev/source/eval_retrieval.py`（新增 `fold()`、`chunk_verdict_for` 兩邊 fold，`verdict_for` source 層一字未改），self-test ALL PASS。
   - ✅ **Gate 1 根因定案**（唯讀，零檔案改動）：`searchChannelB.ts:1495` 無條件前置；意圖（top-5 成員資格）與實作（index 0）不符即根因。經 Codex 兩輪 QC 修訂：位移數字改用 index-0 定義重算、承認註腳正控集**存在**（`footnote_lead_probe.py` ＋ `2026-07-28_s196_fnlead_final.json`，先前寫「不存在」係錯，已收回）、演算法改為 membership 與 order 徹底分離、T4 改為不斷言「永不 index 0」、收回「Source@8 必須不變」的過度宣稱。
   - ✅ **Gate 2A1 測試基建**：`dev/_s214_rank_model.py`（T1–T14，41 條斷言 ALL PASS）、`dev/_s214_gate2a1_replay.py`、`footnote_lead_probe.py` 擴充 `window_of()`（self-test PASS）、43 條 live probe 跑完（正向 30/30）。修好 fidelity 兩個缺陷：全跳過不得回 exit 0（改為 `NO_EVIDENCE`=2）、spotlight 判別須同時違反分數次序（fidelity 174→180/184）。
   - ✅ **Gate 2A2／2A2b 生產實作**：`backend/src/api/searchChannelB.ts` 三處改動，`npm run check` 通過。證據見 `dev/_s214_gate2a2_implementation_report.md`。
   - ✅ **Grounded synthesis 兩批 40 題 acceptance 已執行並保存原始 artifact；其後驗出 harness blocker。** 第一批揭示 audience、核心子類別及策展證據資格問題；方案 A 及離線防線落地後，第二批以 54 次可核證 HTTP 嘗試完成。其後棄權成因覆核確認 probe 先取五格才移除策展摘要，令 18／40 題證據窗少於生產應有的一手文件；兩批 artifact 已降格為 harness-confounded，不可直接作 release 判決。現由生產及 probe 共用 `selectPrimaryEvidence()`；離線回歸 48/48、typecheck、build、diff check、路由回歸 46/46 全綠；semantic regression 唯一 FAIL 是既有版本常數漂移，與本改動無關。外部模型 verdict 維持 FAIL，等待修正後重驗。
   - ✅ **修正後 18 題 V3 已按批次批准完成。** OpenAI Responses API 實錄 25／36 次 HTTP（18 draft＋7 judge，`maxRetries=0`）；不可答題 9／9 棄權、可答題 6／9 作答。人工覆核：4 完整、2 安全但不完整、3 棄權／證據不足；沒有 audience 錯答、OCR 重複或截斷。候選仍為 FAIL，詳見 `dev/_s214_grounded_v3_review.md`。
4. Not done / 未做：兩條新 NCS replacement 及 `gov_imc_60pct`、`hr_lsp`、`sen_special_school_curriculum` 的新鮮 retrieval fixture；`hr_lang_req`、`saf_disease_notification` 完整性回歸；完整 185 條 corpus revalidation及獨立 agent 第二輪覆核；重複穩定性驗收；**歷史 184 題 live 套件未跑**；生產改動未 commit／未 push／未部署；4 條 fidelity 不一致未修（3 條 tie 規則未查證、1 條 `edbc015_2026` 未解釋）；合成窗佔用率未改善；S213 遺留 ④⑤⑥ 全部未動。
5. ⚠️ **本節有部分回合已不在 agent 上下文內**（機器休眠 ＋ context 壓縮）。磁碟上的 S214 報告及不可變 artifact 為權威記錄；**不要憑檔案 mtime 推論作者**。
6. ⚠️ **零 Supabase 寫入、零重入庫、零 commit／push／deploy。** 唯一觸碰的生產檔是 `searchChannelB.ts`，仍在工作區未提交。

## Previous Session Record (S213)

1. UTC date: 2026-09-04
2. Session ID: Claude_20260904_1125 — S213。由「開工」起，Leonard 中途轉單三次：install playbook → 全做 OP → Codex 的 Phase 0／1 檢索基線 brief；最後以「先收工」結束，Phase 1.1 留給下一節。
3. Completed:
   - ✅ **Playbook pointer v2 → v3**（`AGENTS.md` §14；該檔在 `.gitignore`，只存在於本機，換機要重裝）。
   - ✅ **OP⑦ 根因查實並封死源頭**：`build_wiki_index.py:267-268` 靜默 fallback；集合相等已證（19＝19，交集 19，兩邊獨有各 0）；19 個 extract 補回 header（正文位元組不變式逐檔斷言）；守門改 fail loud 並證明會紅。**生產庫 658 條未動。**
   - ✅ **Phase 0 凍結基線**：39 條 legacy 集重跑，PASS=27／FAIL=0／RECORD_ONLY=12／chunk PASS=2／errors=0，與 `qc_report` 的 `EVAL_LATEST` 逐項一致。查詢集 SHA-256 `a2634349...c52bd0d`。
   - ✅ **Phase 1 gold set 162 條**（18 範疇、143 可答＋19 無答案、dev 114／held-out 48），全部經 `_s213_validate_gold.py` 獨立重驗，隔離 1 條。
   - ✅ **五支新量度工具**：`_s213_corpus.py`（含 `dominant_page` 與 `clean_for_match` 兩個後端移植）、`_s213_eval_metrics.py`、`_s213_run_gold.py`、`_s213_validate_gold.py`、`_s213_build_gold_staffing.py`。self-test 合共 54 條全綠。
   - ✅ **量到真實水平**：Source Recall@1 0.364／@5 0.636／@8 0.706；Chunk Recall@5 0.273。
4. Not done / 未做：Phase 1.1 A–E 全部未開始；542 條標題回填未執行（被分類器擋住）；`kgecg_2017` 108 條未刪；七個 standing WARN 未有 waiver；六項人手檢查未簽核；header 正則吃註腳（33 行）未修。
5. ⚠️ **本節零生產寫入、零 deploy、零重切語料、零 commit。** 工作區 20 個已改檔 ＋ 15 個新檔待分類提交，分類見 Open Priorities 上方與開工訊息。
6. ⚠️ **兩項越界結論已自我更正**：(a) 「系統沒有棄權能力」—— 實際是 `synthesize:false` 之下觀察不到棄權層；(b) `forbidden_hits` 寫成「引用」—— 它只證明出現在結果窗。

## Previous Session Record (S212)

1. UTC date: 2026-09-03
2. Session ID: Claude_20260903 — S212。由「開工」起做三個文檔漂移，Leonard 中途下多兩張單（品質檢查頁、Codex 覆檢五點），最後修好一個 91% 不可讀嘅來源。
3. Completed:
   - ✅ **判斷閘 model 文檔漂移補七處**（`backend/.env.example`／`backend/README.md`／`DEPLOY_CHANNEL_B.md`／`README.md`／`PROJECT_MASTER_SPEC.md`／`CODEBASE_CONTEXT.md`／`JUDGE_PROMPT_FINDINGS.md`）。S211 拆咗 `JUDGE_MODEL` 出嚟，但所有部署者實際會睇嘅地方仍寫住判斷閘跟 `OPENAI_MODEL`。
   - ✅ **Playbook pointer v1 → v2**（`AGENTS.md` §14，注意該檔喺 `.gitignore` 第 9 行，唔會經 git 傳去其他機）。
   - ✅ **OP⑤：新增 `info_security` 獨立路由**（`g28` + `pcpd_cloud_computing`，不設 expansion）。交接寫嘅「折入 `digital_education`」被實測否決。
   - ✅ **OP①：eval harness 加片段層**（`chunk_ids` + `expect_text_any` 文字簽名 + `CHUNK_REGRESSED` 獨立判分），eval 集 37 → 39。
   - ✅ **OP②：`check_registry_drift.py`**，五類漂移（ZOMBIE／SERIES_UNMONITORED／UNMANAGED／PHANTOM／UNLISTED），只有 ZOMBIE 退出碼非零。
   - ✅ **品質檢查頁 + 封版閘 + 每日 workflow**（21 項檢查，現時 overall ERROR、閘 7/15 FAIL）。
   - ✅ **`phys_sss_2007_2015` OCR 重抽入庫**：187 條、亂碼 0、頁碼 1–150 全覆蓋；`MOJIBAKE` 檢查 223 → 58，基準已棘輪下調。
   - ✅ **`route_regression` 33 → 46 條**（含六條「必須唔郁」負面案例）。
4. Not done / 未做：`kgecg_2017` 108 條重複登記未刪（已證可刪，但刪除工具被 auto mode 分類器擋住）；八個 standing WARN 未有 waiver；658 條代號標題未 backfill；四對重複登記只驗證咗，未清。
5. ⚠️ **本 session 曾令生產搜尋停機約半小時**（額度耗盡，全站 429）。已恢復，並已建兩道閘防止重演。

## Previous Session Record (S211)

1. UTC date: 2026-08-31 → 2026-09-01（跨午夜；本機時區 BST）
2. Session ID: Claude_20260901 — S211。由 Leonard 一句「收起通告分析卡」開始，途中變成「一條答唔到嘅查詢」嘅逐層拆解。
3. Completed:
   - ✅ **前端五項，平台 v3.3.0 → v3.3.2** —— 收起通告分析卡（兩面）；修平板／橫放手機版面錯位（兩道閘條件不一致，iPad 得到一個樣式表不會套用嘅手機介面，約 362px 無樣式內容把 `#root` 推低）；統計列改為按實際格數開軌；三處寫死嘅功能數字改為推算；清走五句仍在應承已收起功能嘅散文。
   - ✅ **快取鍵教訓** —— `mobile.css`/`mobile.js` 以 `?v=<PLATFORM_VERSION>` 引用，不推版號則回頭客讀舊檔。本 session 實際撞過：改咗檔、本機 server 已是新版，瀏覽器仍重現舊 bug。故 v3.3.1 再 v3.3.2。
   - ✅ **`/health` 加 `commit` / `started_at`** —— 此前無法從外部得知服務中嘅 build。加咗之後即時證明自己（poll 1 無 `commit` 欄＝舊 build、poll 2 新 SHA）。
   - ✅ **判斷閘改用 `gpt-4.1-mini`**（新 `JUDGE_MODEL`，程式預設，Render 無須改）—— 凍結集主集 31/33 打平、decline half 同樣兩個 false answer 無新增、連 bare-noun 33/35 對 31/35。只換判斷閘不換合成器，每條查詢約增 US$0.0005。
   - ✅ **檢索四層修正** —— 新增 `teacher_qualification` 路由（答案由第 10 升至第 1）；bypass 改為讀 `results[forcedLeads]`（一個 0.5057 嘅強制置頂註腳曾令一個 0.7093 嘅合格片段失去豁免）；合成器字數由目標改為上限；`chunk_overlap` 覆寫 ＋ `searchEstablishmentRows()` 詞彙層 overlay。
   - ✅ **內容準確性（Leonard 指出）** —— 資助及官立小學已無半日制，編制答案預設只出全日制；資料未刪，查詢寫明「半日制」仍如實作答。
   - ✅ **防漂移機制** —— `app.html` 分頁開關註釋新增第 8 項（四處散文，點名）同第 9 項（功能數字一律推算）；`DOC_SYNC_CHECKLIST.md`「Tab withdraw / restore」重整為 A flag 驅動／B 推算數字／C 人手散文／D 版本與記錄，驗證欄加入「grep 該功能關鍵詞確認無剩餘應承語」。
   - ✅ **三個新量度工具** —— `route_regression.mjs`（33 條，33/33 PASS，並以改前版本跑同一套證實無舊 query 改路由）、`vault_lead_delta.mjs`（確定性，證實 bypass 改動只影響 3 個 case 且全部 want=能）、`cache_drift.mjs`（凍結 cache 已漂移 9/35）。
4. Pending: 見 Open Priorities。**0 outstanding bug。**⚠️ 一項自認欠賬見 Risks。
5. Next priorities: 見 Open Priorities（① eval chunk 層儀器最相關）。
6. Risks / blockers:
   - ⚠️ **本 session 中途曾有一次已還原嘅生產寫入**：先以「一行一片段」重入 85 條，實測發現答案變成由鄰近班數內插，隨即逐 byte 還原（81 行連原 embedding、全庫回 17,593），確認詞彙層 overlay 之後才再次重入。備份全程在手，最終狀態已驗證。
   - ⚠️ **`staff_est_pri` 過去一段時間喺生產度答緊錯數**（「12 班」答「合計 10 名」，正確 21 名），S211 之前已存在。現已修，但同類表格未逐一檢查——`coa_pri_e` / `coa_ss_e` 亦載編制條款。
   - ⚠️ **凍結 judge 驗收 cache 已漂移**（2026-07-31 版，35 條有 9 條 top-5 已不同、`D00_s177_frozen_post` 只餘 1/5 重疊）。引用該 harness 嘅數字前要知道呢件事；refresh 需逐條重讀原文核 label，未做。
   - 既有：Channel A frozen @455 / 入庫 display sync 七處 / 新源必加 SOURCE_SETS+registry / 57014 cold-start / 路徑空格雙引號 / 勿改 canonical chunker。
   - **檢索 eval（DOC_SYNC row 43／51 要求）：** 對 `2026-08-26_s210_after_leaflet.json`，`2026-09-01_s211_after.json` 為 **PASS=25 / FAIL=0 / errors=0（與基線一致）、SAME 36 / 37、blocking failures 0**。唯一非 SAME 係 `sef` 一條 DISPLACED（尾位 `debp_blueprint` 被 `edbc015_2026` 擠走），而後者係 S210 之後 Option A 管道自動入庫嘅通函，**與本 session 四層改動無關**。
7. commits（全部已 push origin/main）: `08c8c1e`(收卡) → `7e176a2`(v3.3.1 版面錯位) → `4da76e4`(v3.3.2 手機導覽) → `26edba4`(散文＋防漂移) → `d6e0d1f`(日期更正) → `c60c52c`(teacher_qualification 路由) → `25f8cc5`(bypass 讀取位置) → `b6cba5a`(/health commit) → `25ff4f9`(judge 調查記錄) → `1e5324a`(合成器字數＋班數路由) → `1becef8`(judge model) → `6ae5b69`(chunk_overlap 能力＋§7 記錄) → `5a02267`(詞彙層 overlay＋逐行切片) → `22f27fb`(全日制預設) → 本 closeout commit。

## Previous Session Record (S210)

1. UTC date: 2026-08-26
2. Session ID: Claude_20260826_0748 — S210。由 OP⑥ 補 eval 開始；查完發現量度佢嘅閘同交接對 gifted 嘅描述都要更正。Leonard 中途下多兩張單（EDBCM156 網上資源盤點、三摺頁入庫）。
3. Completed:
   - ✅ **OP⑥ 結案** —— 補跑 eval 對 S207 基線，**零退步**。compare 報 5 blocking 逐條拆完：1 條錯喺基線檔（S207 自己撞 Supabase timeout），4 條係自動管道新通函擠掉尾位、verdict 全部冇變。
   - ✅ **修 compare 個閘（新 `DISPLACED`）** —— 固定 top_k 之下「新源入」同「尾位跌出」係同一件事，舊邏輯一個放行一個叫停。Option A 每日入庫 → 呢個閘本來會朝朝紅。加 4 條 self-test，其中兩條專證**佢仲會紅**（cut line 以上跌出、after 短過 before）。blocking 5 → 1。
   - ✅ **eval 集 34 → 37** —— 補保安／雲端三條，**入檔前逐條 live 實測先寫 `expect_any`**。之前 34 條一條都冇掂過 S209 兩個新源，即係 OP⑥ 嘅原定 baseline 對 OP⑦ 係空白。
   - ✅ **`split_on_section_markers` gate 由 registry 改為 extract 判** —— 261 源掃描 **259 byte 級 no-op**，只 g04（7→11）同 `gifted_policy_docs`（23→23）變。重入後跨界 chunk **g04 5→0、gifted 2→0**（live 實查）。
   - ✅ **三摺頁入庫**（Leonard 指示）—— 4 chunks。**搜得到但贏唔到**：獨有詞「四大發展重點」rank=None，因為資訊圖 chunk 係散裝標籤。caveat 寫入 registry notes。
   - ✅ **EDBCM156/2026 網上資源盤點** —— 用 Tavily 抓咗以前抓唔到嘅 EDB／教城頁。10 條引用資源，**4 條已入庫兼受監察，6 條兩樣都冇**。URL 喺 PDF 入面被換行斬開，逐條由原文重組（冇估）。
   - ✅ **正文連結缺口量度 + Leonard 拍板入 Backlog** —— anchor URL 420 條受監察 vs 正文引用 3,011 條，重疊只有 6 條 → **3,005 條零監察**。定案：課程專頁唔監察（2 條、逐學期換、耐用資訊已在庫），力氣放喺正文連結。
   - ✅ **補 DOC_SYNC 缺失 row** —— 「切 chunk 邏輯改動」全 registry 零命中；S209 做嘅正正係呢類改動當時冇加 row。已補，驗證方法寫明「全 vault blast radius 掃描要報 no-op 幾多，唔可以只報變咗嗰啲」。

## Previous Session Record (S209)

1. UTC date: 2026-08-24
2. Session ID: Claude_20260824_1848 — S209。由 OP⑥ 起，Leonard 連下四張單，再加 g28 入庫同雲端資料研究。10 個 commit（另 ops repo 2 個）。
3. Completed:
   - ✅ **OP⑥ 結案** —— 前提本身錯（監察一直讀 `wiki_chunks.url`）。四重實測 + 紅測。真缺口（`--fetch` 得散文擋）補咗 `refetch_blocked` 機制閘 + 結構不變式斷言。
   - ✅ **第 6 監察 expiry** —— `lifecycle.py` 三分類 + `check_expiry.py`（22 斷言）+ ops `expiry-issue.yml` 剔一剔清走。Backfill 26 個 `dated_edition`。
   - ✅ **修長期差 1** —— 公開片段數由流水帳改為由 Supabase 讀真數；現值 17,551 兩邊對齊。
   - ✅ **清 4 條 404** —— 2 條 re-point（引用數字逐個對返新 PDF）、2 條退役（13 chunks，Leonard 批）。
   - ✅ **兩個清單收摺** —— 待批入庫超過 21 日收摺；discovery 加 first-seen 帳只報新嘢。**兩個監察 issue 而家會自己閂**（served-url、discovery）。
   - ✅ **兩個新源** —— `g28` 0 → 40 chunks（7/41 份文件）、`pcpd_cloud_computing` 26 chunks。
   - ✅ **修兩個既有頁碼債** —— g17 兩條錯錨（13 chunks 重入）、`gifted_policy_docs`（19 → 23 chunks 重入）。
4. QC：四支 self-test 全綠（carry 41 / expiry 22 / served-url / discovery）；prove-assertions 19 + 13 條會紅；backend `npm run check` + `build` 通過；`count=exact` **17,551 == 公開顯示**；三個源嘅頁碼錨點 100% 喺自己文件範圍；PCPD 三條 query live rank 0。
5. 未完成：Open Priorities ①–⑤ 零推進（本 session 冇掂）；新開 ⑥（eval 欠賬）⑦（route regex）。
6. 關鍵教訓：(a) **交接寫低嘅前提可以係錯** —— OP⑥ 個描述由 S207 一句 docstring 流出去，三處抄咗一年。動手前實測，唔好照做。(b) **揀嘅 phrasing 決定得出嘅答案** —— 我用闊 query 搵唔到 g28 就當「ANN 餓死」加咗 spotlight，用內容專屬 query 一試就 rank 0，同一 session 移走。同 S195 spotlight prune 同一陷阱、相反方向。(c) **報一個 URL 嘅狀態前確認佢係真連結** —— 我 probe 咗個由截斷 href 估返嚟嘅 URL，報咗個唔存在嘅 404。紀律 #3 再應驗。(d) **只入唔出嘅清單一定變牆紙** —— 一 session 內喺四個地方撞到（見 Regression 第 10 條）。
7. commits：`5d7040d` → `abfad15` → `3bfb551` → `9ece726` → `2bcea04` → `e166d5d` → `ecdfbaa` → `62e20e1` → `d812b89` → `e6f13de`；ops repo `0826bba` → `abd257d`（另 `e5d0e55` expiry workflow）。全部已 push。

## Previous Session Record (S208)
1. UTC date: 2026-08-20
2. Session ID: Claude_20260820_0826 — S208。純溝通交付 session（read-only 分析 + 新文件），零 code / 資料 / Supabase / 對外合約改動。
3. Completed:
   - ✅ **`dev/PROJECT_MILESTONES_REVIEW.md`**（新）—— 由 2026-03-09 原始痛點到今日嘅里程碑回顧：六階段敘事、數字弧線、**功能生死簿（加咗又刪咗）**、11 條紀律、一條由頭到尾嘅線。挖 578 commit + S1–S207 + 三個季度封存 log。
   - ✅ **`dev/INFOGRAPHIC_PROMPT.md`**（新，後按 Leonard 要求整份重寫）—— 三條自足 prompt，**指定輸出 PNG、繁體中文、書面語**，內含全部數字，收圖 agent 唔使查任何嘢；明寫唔好用純圖像生成模型。
   - ✅ **三張 PNG 全部本地出圖**（`dev/design/`）：A `milestones_infographic.png` 2400×10106、B `milestones_slide_16x9.png` 3200×1800、C `milestones_insights_a4.png` 2382×3369；HTML 原檔一併留低可重出。
   - ✅ **DOC_SYNC row 26 兌現**：`CODEBASE_CONTEXT.md` Directory Map 加 5 條（2 個 md + 3 組 html/png）+ 重出圖方法 + 字體注意 + AI Maintenance Log S208。
4. QC：所有 load-bearing 數字**逐個對返源**（`git rev-list --count`=578；chunk 弧線末端 17,473 = live 探針；97.4% = (17473−451)/17473 實算 97.42%；600/60 切片參數由 `build_wiki_index.py:59-60` 讀出；4 個公開 tab 由 `app.html` `FEATURE_TABS` 讀出；5 個監察由 `.github/workflows/` 實 list）。三張 PNG 逐張開圖肉眼檢查：零切字、零豆腐字、零爆版。`git status` 證零 code / 資料檔改動。
5. 未完成：Open Priorities ①–⑥ 全部原封未動（本 session 零 OP 推進）；Backlog 不變。
6. 關鍵教訓：(a) **「報一個數之前打開實例親眼睇」呢條紀律，喺寫回顧時一樣中** —— 我兩個起點數字（登記來源 8、公開分頁 4）都係憑印象寫，對源之後兩個都錯。(b) **出中文圖要先驗字體**：本機冇 PingFang，繁中靠 STHeiti 兜底；唔驗就會出咗豆腐字先發現。(c) 中途 `milestones_infographic.png` 一度喺磁碟消失（生成後、下一步之前），重出即解決 —— 交付圖檔前要 `ls` 實證存在，唔好靠「我頭先生成過」。 (d) **同一 session 第三次憑印象出錯**：收工成份文件寫咗 `2026-08-19`，但 `date -u` 實測係 **2026-08-20**（本機喺 BST，唔係 HKT）—— 我跟住 S207 個日期抄落嚟。Leonard 問「未 commit 去 playbook？」時順手發現並全部修正。**日期同數字一樣，係要查唔係要記。**
7. commits：`052c646`（交付物 + closeout）→ `7c7c5f5`（日期更正）→ 本 entry。Playbook：`d96dc25`（S207 欠低嘅 4 份）→ `cbfa060`（S208 提案 + usage）→ `250e206`（merge librarian）全部已 push。
8. 🔴 **順手揪出 S207 留底從未 commit**（檔寫咗、冇 `git add`，但收工紀錄寫「交咗」）—— 已補交。**§14 留底要 commit + push 先算數；收工前實查 `git status`，唔好靠「我寫咗個檔」。**

## Previous Session Record (S207)
1. UTC date: 2026-08-19
2. Session ID: Claude_20260819_S207 — S207。接力 S206，Leonard「全做」= Open Priority ①（HTML 源指章）+ ②（g14 三個同源缺陷）+ 兩件 housekeeping。
3. Completed:
   - ✅ **OP① 指章完成**：`carry_sections()` + `section_urls` opt-in map，**前端／後端／schema 零改動**（`wiki_chunks.url` 本來就係 per-chunk 欄位）。g14 76 條 → 10 個子頁；g17 13 條 → 6 個目標（3 子頁 + 3 附件 PDF，仲保住 `#page=N`）。
   - ✅ **交接更正**：g17 頭 3 個標記係真子頁（喺另一條 path 之下），唔係淨係附件檔名 → g17 6/6 全部指得到。
   - ✅ **OP② 三缺陷全清**：title 計劃→課程（只有 vault extract 錯，公開鏡像本來就啱）；22 條標記外洩喺 `cleanChunkText` 一次過修；91 行 EDB nav/footer chrome 由 `strip_web_chrome()` 剷走。
   - ✅ **額外揪出並修好 g20/g25 生產庫亂碼**（EDB 唔出 charset → requests 跌返 ISO-8859-1）。g25 而家 score 0.753 命中，以前完全搜唔到。
   - ✅ **新守門**：`dev/vault/test_carry_rules.py`（14 條不變式 + `--prove-assertions` 用 no-op 實作證明測試會紅）；入庫前 section URL 逐條 HEAD 200 fail-closed。
   - ✅ **Housekeeping**：頂層 dormant root 刪咗 2 個 brag 中介 artifact dir（v1 + v2，~21.5 MB），2 個 final deliverable 完整保留；Playbook inbox 交咗 4 份 proposal（S206 欠低嗰兩條 + S207 兩條），`usage/policychecker.log.md` +2 行。
4. QC：`test_carry_rules.py --self-test` 14/14、`--prove-assertions` 觸發 8 條；section URL 16/16 HEAD 200；零內容遺失閘（g14 77/77、g17 12/12 舊 chunk 文字全部喺清洗後 extract 搵得返，唯一「唔覆蓋」係 chunk 邊界切開嘅 3 字 chrome 殘片）；g20/g25 encoding-only 證明（舊文字 latin-1→utf-8 還原同新 extract 逐字對到，除咗舊資料真爛咗嘅位 → 反證舊 row 有損）；`cleanChunkText` 5 case（含「兩個相鄰頁碼標記中間正文要保住」）；`npm run check` / `build` exit 0；eval 30 SAME / 2 RANK_SHIFT / 1 SET_ADDED / 0 regression（1 條 error 係 Supabase 57014 暫時 timeout，live 重試 3 次同 baseline 一致）；post-deploy live 實測 g14 出 chapter-six.html、g17 出 framework.html 同 page=3 附件 PDF、g25 0.753。
5. 未完成：見 Open Priorities ①–⑥ 及 Backlog。（`dev/SESSION_LOG.md` 歸檔已於 S207 收工完成 —— 現為 215 行 / 2 entry，`--check` = trigger=False；S208 起手覆核確認。）
6. 關鍵教訓：(a) **守門要證明佢會紅** —— `--prove-assertions` 模式第一次跑就有價值；淨跑正常 self-test 兩個 regex 陷阱都會靜靜哋過。(b) **放寬一個 regex 一定要即刻搵新 false positive** —— 為修「overlap 甩行錨」而拆走行錨，同一改動立刻製造 847 個幻影 label。(c) **健康指標遇上 encoding bug 會反向** —— 「至少 200 字」呢個閘一直收垃圾、擋好嘢。(d) **S206 第 10 條紀律我自己再中一次**：報咗「683 條標記外洩」先打開實例睇，實數 22 條，差 31 倍。
7. commits：`a7ad697`（管道 + 資料 + 守門）→ `3dc9952`（後端 `cleanChunkText`）。文件更新（本 handoff / SESSION_LOG / CODEBASE_CONTEXT / DOC_SYNC_CHECKLIST）未 commit。


## Previous Session Record (S206)
1. UTC date: 2026-08-18
2. Session ID: Claude_20260818_1900 — S206。同日接力 S205，由 Open Priority ①（檢索「可見 ≠ 見到啱嗰段」）入手，經 Leonard 一句更正後轉為修復「頁碼指路」。
3. Completed:
   - ✅ **OP① live 重現，證明交接嘅兩個修法都修唔到佢自己指嘅 case**（正確資料行 exact cosine 0.6049 排源內 14/81；源內最高 0.6537 係零數據表頭行）。該項已重寫為新 Open Priority ③，唔可以照抄舊描述。
   - ✅ **根因定位：`expand_vault.py` 兩層甩頁碼** —— 抽 PDF 時冇寫 `=== Page N ===`、切 chunk 時冇 carry。自動管道 `execute_ingest.py` 一直冇此問題。
   - ✅ **兩層都修好**：`carry_pages()` 抽出喺 `build_wiki_index.py` 由兩支管道共用（但唔共用 chunker）；`extract_pdf_text` 逐頁寫標記，並把「掃描 PDF」守門由總長度改為只數真文字。
   - ✅ **11 個源重入，全部 0 條無頁碼**：全庫無頁碼 chunk **1,859 → 451**（修 1,408 條），總數 17,472 → 17,473。
   - ✅ **真 UI 實拍確認**：「資助小學教學人員編制 · 3 個片段 · 頁 1, 3 ↗」，DOM 錨 `#page=1` / `#page=3`；`coa_ss_e` p.29、`coa_pri_e` p.100。
   - ✅ **剩餘 451 條已分類**（見 Open Priorities 段尾），真缺陷 139 條。
   - ✅ **HTML 源方向已定**：「指章唔係指頁」，Leonard 同意；實測只有 `g14` 77 條有真 slug。
4. QC：`carry_pages` 不變式 4/4 且證明斷言會響；動 DB 前先證對無標記源 no-op（`edbc00030` 67/67、`g04` 7/7 id 完全相同）；9 個源逐個過「零內容漂移閘」；`extract_pdf_text` 兩面測（空白掃描仍會警告）；eval 對開工基線 PASS=23 / FAIL=0 / errors=0、33 SAME、1 RANK_SHIFT、0 blocking failure；`npm run check` / `build` exit 0。
5. 未完成：見 Open Priorities ①–⑦ 及 Backlog。
6. 關鍵教訓：(a) **交接寫低嘅修法可以指錯目標** —— 唔止選項框架錯，係兩個選項都修唔到指定 case，要 live 重現 + 逐條算 exact cosine 先揭到（S205 第 8 條紀律再中）。(b) **用戶記得嘅嘢可以比我嘅分析更中要害** —— Leonard 一句「出表格就指該頁數」把問題由「檢索排序」重新定位到「頁碼來源」。(c) **報 population 數字要即刻拆類**，否則對方會用自己嘅 mental model 填補（「1,859」曾被合理但錯誤地連去 Channel A 退役）。
7. commits：`98dfbf8`（carry_pages + staff_est_pri）→ `5fa7343`（extract_pdf_text + 9 個源）→ `6ab966c`（edbc12 檔名對齊 + 重入）→ 本 closeout commit。

## Previous Session Record (S205)
1. UTC date: 2026-08-18
2. Session ID: Claude_20260818_1400 — S205。同日接力 S204，單一目標：清 Open Priority ①（由 7/30 賴到今日嘅臨時觀測 code）。
3. Completed:
   - ✅ **交接框架修正**：二選一（刪 / 重開窗）其實有第三個更好選項 —— Hobby 七日保留係 rolling，probe 連續 live 十九日，現成七日窗一直喺 dashboard 等人讀。
   - ✅ **第二次讀完成**：8/11→8/18 七日窗，只得兩行、皆自測 → 兩條 channel-a route 零外部呼叫（連 S202 8/2 讀合共十日、兩次獨立讀）。
   - ✅ **probe 已刪**：`server.ts` 169–200，32 行純刪除（`a1a6442`）。
   - ✅ **部署後 live 讀已閂**：四個帶序號標記全部冇出現（DOC_SYNC row 48 專門要求嘅嗰格，唔准用 `/health` 猜重啟）。
   - ✅ **治理文件已更新**：Open Priorities 五→四項並重編號＋修好兩處交叉引用；opening message 紅旗改寫成已閂結果；CODEBASE_CONTEXT AI Maintenance Log 補一行閂返 S198 嗰筆。
4. QC：`npm run check` + `npm run build` exit 0；`dist/server.js` route-probe = 0；`git diff --stat` = 1 file / 32 deletions；部署後 `/health` 仍 warm 455、兩條 route 行為不變（GET → 404）。起手探針 6/6 綠。
5. 未完成：見 Open Priorities ①–④ 及 Backlog。
6. 關鍵教訓：(a) **rolling 保留窗唔使「重開」，只需要讀** —— 交接嘅二選一框架本身可以係錯，落手前先驗前提。(b) **「應該冇」唔係「冇」** —— Leonard 第一次答「應該一行都冇」係期望語氣，追問一句先落結論；放四個標記就係為咗有嘢俾人睇，靠推斷閂數就白放（S197／S198 同一個坑第三次，今次未遂）。
7. commits：`a1a6442`（刪 code）→ `37e0e71`（治理文件）→ `bee54c9`（閂讀數）。

## Previous Session Record (S204)
1. UTC date: 2026-08-18
2. Session ID: Claude_20260818_1115 — S204。由一個真實用戶問題（「幾多班有幾多老師／校工」答唔到）拆到底，順帶完成 v3.3.0、累積計數器、beta 標示、tab 開關。
3. Completed:
   - ✅ **頁碼歸屬修正 ship**：`extractDominantPage`；真 PDF 核對 147/147 + 127/127（舊 74.1% / 63.0%）；全庫 35% chunk 頁碼改變。
   - ✅ **人手編制文件群入庫**：registry +11、Supabase → 17,472；新 `extract_table_rows.py`（座標重建 + 算術守門，72/48 行零失敗）；`expand_vault` 加 per-source `chunk_cap`／`chunk_max_chars`。
   - ✅ **可達性四層修正**：SOURCE_SET + TOPIC_KEYWORDS（新「編制」詞）+ SPOTLIGHT +7 + 獨立 `staffing` route（避開令 cosine 跌 0.20 嘅 expansion）+ 逐行 chunk。四條查詢由 <0.60 升至 0.607–0.816。
   - ✅ **v3.3.0 + 顯示同步**：chunks 17,472、sources 120→288（積壓漂移校正）、指引 177；README／index／CHANGELOG（只 append）同步。
   - ✅ **累積使用計數器**：`usage_daily` + 兩個 SECURITY DEFINER 函數（Leonard 貼 DDL）、後端 `usageCounter.ts` + `GET /api/stats/usage`、`x-probe` 排除自測、桌面第 5 卡 + 手機 hero。
   - ✅ **快取修正**：`mobile.js`/`mobile.css` 加 `?v=3.3.0`（實測回訪瀏覽器一直行舊版）。
   - ✅ **beta 標示 + `FEATURE_TABS` tab 開關**，`templates` 已收起。首版逐個手 gate 漏咗兩個位（平台介紹核心功能卡 + 使用手冊摺疊），已改成 `view` key 統一 filter；7 個受影響位 + 恢復程序寫入開關註解，並加入 DOC_SYNC 一行。
4. QC：eval before→after 兩次 PASS=23/FAIL=0/errors=0（31/34 不變）；路由 15/15；頁碼函數 7/7；計數器 live 3 測；headless render 驗版本／指引數／片段數。`npm run check`／`build` 全綠。
5. 未完成：見 Open Priorities ①–⑤ 及 Backlog。
6. 關鍵教訓：(a) **入庫 ≠ 可達** —— 要 SOURCE_SET、TOPIC_KEYWORDS、SPOTLIGHT、route expansion 四層都啱先搵到，每層都要實測先知；(b) **加料可以幫倒忙** —— `hr_admin` expansion 令編制查詢 cosine 由 0.816 跌到 0.616；(c) **令系統答到嘢可以係退步** —— 特殊學校表入庫後由「老實 decline」變「自信答錯」，回滾先係啱；(d) 假設要逐個實測，我今日有三個假設（Q&A 格式、chunk 被切爛、mojibake 2.4%）都係測完先發現唔成立。
7. commits：`f5d42a2` → `deea141` 共 12 個（見 `git log 5f07cf7..HEAD`）。

## Previous Session Record (S203)
1. UTC date: 2026-08-02
2. Session ID: Claude_20260802_S203 — ⑩ 文件 drift 清 + ② judge V4 量度（未 ship）+ ⑧ g24/sag 偵查（出 PLAN）。
3. Completed:
   - ✅ **文件 drift 修好**（純文件）：PMS 3 處 + roadmap 5 處 + `HANDOFF_PACKAGE.md:32` 統一為「下游轉 Channel B S146 已完成」；grep QC 殘留清零。
   - ✅ **judge V4 量度完成（🔴 未 ship）**：`v4a/v4b_s202.txt` + fresh held-out 10 條 + harness `--cases`/`--cache`；7 runs 噪音控制。定案：V4b 穩修 GN10（範圍移植）、零 recall 損，但 D01/FT06（對象移植）照漏 → **prompt-only 封頂，建議唔 ship，② reframe 為非-prompt 對象核對機制**。
   - ✅ **g24/sag 偵查完成（純唯讀，出 PLAN）**：親眼驗 Supabase → 真實文字重疊 **377**（舊 doc「215」全 stale）、g24 383 / sag 409、**g24 零獨有內容**、版本＝2026年5月版。合併 PLAN 6 步備妥，HIGH risk 等 GO。
4. QC：⑩ grep 殘留清零；② `--self-test`／`--check-parity`（byte-identical）／`--plumbing-check` 綠 + 7 runs；⑧ 純唯讀 Supabase REST。零 Supabase 寫入、零生產 code 改動。
5. 關鍵教訓：(a) **judge LLM 非決定性** —— 單次 run 分唔到信號同噪音（GN03 同一 prompt 兩次 run flip），任何 judge verdict 要重複 run 先落結論。(b) **報數前親眼驗實例** —— ⑧「215」三處 doc 全錯、實 377，靠直接數 Supabase 先揪到。
6. 詳細證據見 `dev/SESSION_LOG.md` 2026-08-02 Session 203 entry。

## Previous Session Record (S202)
1. UTC date: 2026-08-02
2. Session ID: Claude_20260802_S202 — NEXT ① route-probe 觀察窗第一次讀（8/2）
3. Completed:
   - ✅ **route-probe 8/2 讀 ＝ 全窗綠**：Render Logs「Last 7 days」search `route-probe`，2026-07-30 09:40 UTC→8/2 共 **26 行全部有主**（24× `s198-deploycheck-*` 自測 ＋ 2× `s201-control-probe` 對照），零第三方 / 零非自測 origin/ua → 兩條 channel-a route（`/api/search/channel-a`、`/combined`）由 7/30 起零外部呼叫。
   - ✅ **儀器雙重對照確認正常**：Claude 遠端放 `s201-control-probe`（即時，出到＝儀器 work）＋ s198 7/30 回溯（「Last 7 days」下 24 行全現形＝窗涵蓋起點）。頭先空手 search 冇當「零流量」（S198 紀律落地）。
   - ✅ **checkpoint 入 handoff OP① ＋ push**：commit `2ec82cf`。
   - ✅ **§4a log 維護**：SESSION_LOG 402→122 行，4 舊 entry 搬入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬冇刪）。
4. QC：起手探針 4/4 綠；probe 儀器經 s198＋s201 雙對照證正常；**零 code／零 Supabase／零 route 改動**（純唯讀量度）。
5. 未完成（詳見 Open Priorities）：① route-probe **8/5 第二次讀**（≤8/6 前）＋讀完刪 `server.ts:168–198` probe；②–⑪ 見 S201 段（硬化 judge V4／Channel A Option 2 入庫…）不變。
6. 關鍵教訓：Render Hobby log search「搜唔到」≠「零事件」——必先放即時對照（s201）＋回溯已知事件（s198 7/30）驗窗涵蓋，先可信 negative（S198 真金白銀那一堂再落地）。「Last 7 days」時間範圍未 set 會令 search 空手＝儀器操作問題唔係流量。
7. commits：`2ec82cf`（8/2 checkpoint）＋本 closeout commit。Supabase 16,062 零寫入、registry 256 / v3.2.2 / 凍結合約零接觸。

## Previous Session Record (S201)
1. UTC date: 2026-07-31
2. Session ID: Claude_20260731_S201 — NEXT ②：收 footnote judge-bypass（擴闊 decline 集 → 量 V3 → 收 bypass → deploy → live 驗）。Leonard 逐步揀:(A) groundwork → (A) 開 ② 本體 → 量度後揀 (B) 收 bypass V3 先 → push → 收工。
3. Completed:
   - ✅ **(b) 擴闊 judge decline 集 11→21**:S199 講嘅「14 條 candidate」從未持久化 → 重新 author 14 條逐條讀 passage label（11 gap + 3 answerable,3 條逆假設 flip）。10 clean gap 入 decline、GN11 入 answer;`judge_acceptance_cases.json` 24→35 frozen（commit `ded9504`）。
   - ✅ **量 V3 baseline（擴闊 35 條、gpt-4o-mini dashboard reconfirm、`--plumbing-check` 綠）**:answer **12/12**、decline **19/21**（2 false = D01/GN10,皆 transplant 類）、D00 一票否決正確拒答。run `2026-07-31_s201_v3_widened.json`（commit `b7627b7`）。
   - ✅ **收 footnote judge-bypass**:`searchChannelB.ts` `synthesizeAnswer` 移走 `trustedFootnoteLead`（連 `forcedFootnoteLeads`）→ footnote lead 過 V3;保留 vault bypass(≥0.70)/forced lead slot/lexical gate/prompt。commit `fc287ff`,**deploy 已確認 live**。
   - ✅ **live before→after 驗**（synthesize:true 生產）:D17 消防演習 砌數「每12個月」**→ 拒答**;D13 留位費 仍正確答 970/1570（零退步）;D01 仍答（V3 miss,pending V4）。
4. QC 全綠: `--self-test` 0 fail / `--check-parity` byte-identical（prompt 未郁）/ `tsc --noEmit` exit 0 / 零殘留 bypass 引用 / `footnote_lead_probe --run` before==after 30/30·5/13·0err（lead-slot 零回歸）。Supabase 16,062 零寫入 / 凍結合約 / v3.2.2 / registry 256 全零接觸。
5. 未完成（詳見 Open Priorities）: ① S198 觀察窗 8/2+8/5 讀 route-probe（剩 2 日）;② 硬化 judge V4 收 transplant 類（D01/GN10）;③ Channel A Option 2 入庫;⑥ 拆 backend route。
6. 關鍵教訓: footnote bypass 前提（curated footnote lead = 答緊呢條 query）被 D01 證偽（正確 staff 規則被 retrieve 去答 student 問題）→ 已移走 + 寫入 code 註釋 / FINDINGS。
7. commits: `ded9504`（擴闊集）→ `b7627b7`（V3 baseline）→ `fc287ff`（收 bypass）→ `4e7d90b`（persist）+ 本 closeout commit。Supabase 16,062 零寫入。

## Previous Session Record (S200)
1. UTC date: 2026-07-30
2. Session ID: Claude_20260730_1548 (S200) — ship judge V3（Open Priority ③）;Leonard 揀 Option 2 明文閘 override。
3. Completed: ship V3（`RELEVANCE_JUDGE_PROMPT` 換 V3,commit `bcf7c4f`,deploy 已確認 live）;驗收 primary 21/22、answer 11/11、decline 10/11、false=[D01];明文 OVERRIDE(§2 rule 6) 越 decline false-answer 硬閘（理由:非退步 / D00 過關 / D01 生產行 footnote bypass）。QC 全綠。
4. 註: S200 記「D01 生產行 footnote bypass、judge 從不 serve」—— **S201 已收 bypass,D01 而家過 judge（V3 仍答,pending V4）**,此句已 stale。
5. commits: `bcf7c4f`(ship V3) + `0755aa1`/`7716b13`(closeout)。Supabase 16,062 零寫入。

## Previous Session Record (S199)
1. UTC date: 2026-07-30
2. Session ID: Claude_20260730_S199 — 起手探針 4/4 綠後揀 Open Priority ① 修 judge;做到中途 Leonard 叫停、問返 Channel A 退役實況 → 轉做 A(Channel A) 然後 B(judge)。Leonard 揀 Option 2、批「收工」。**純量度 session,零 Supabase 寫入、零 code 改、零 route 改。**
3. Completed:
   - ✅ **A —— Channel A 退役重構成資料模型缺口**：precondition「Channel B 覆蓋 Channel A」已量 = 覆蓋唔晒;職責歸屬類逐條打開 passage 核實,文件結構性冇「〔角色〕負責」寫法。Leonard 拍板 **Option 2(升做有出處 footnote)**。
   - ✅ **Option 2 唯讀可行性 triage**：升唔到嘅硬核 **24 條**純職責歸屬(唔係 ~100+),117 條「提到角色」大部分揾返出處可升。拆咗「總帳 url = retrieval 目標唔係出處」個陷阱。→ `CHANNEL_A_COVERAGE_FINDINGS.md` §5-6。
   - ✅ **B —— judge 驗收工具 + 凍結 24 條驗收集**(量度前 commit `a65e723`)：`dev/source/judge_acceptance.py`(self-test 22 條 + `--plumbing-check` + `--check-parity`)。
   - ✅ **揪出並更正 model 錯誤**：首兩份 baseline 用咗 code default `gpt-4.1-nano`,Leonard dashboard 確認 Render 實設 `OPENAI_MODEL=gpt-4o-mini`。同一 prompt nano 0/11 vs gpt-4o-mini 8/11。nano run 改名 `_nano_ARTIFACT`,S196 findings 標「未經生產驗證」。
   - ✅ **V3 生產 model 量度**：21/22、answer 11/11、decline 全保、held-out。
   - ✅ **footnote bypass live 發現**：7 條 footnote-lead 空白查詢 live 全部答咗、0 decline;D17 實錘砌數、D13 更正返係啱、修法同 judge 耦合。→ `JUDGE_PROMPT_FINDINGS.md`。
4. QC: `judge_acceptance.py --self-test` 22/22 PASS ×N;`--check-parity` PASS(harness prompt 同 `searchChannelB.ts` 逐字相同);`--plumbing-check` 兩 model 都出「能」(證明 constant-否 係判詞唔係 wiring);D13/D17 砌數判定用 Supabase ilike count 逐條核實(消防演習=0、留位費 970/1570 有出處)。Supabase 16,062 零寫入 / registry 256 / guidelines 158 / facts 455 / v3.2.2 / 凍結合約機械核實零接觸。eval **未重跑**(零檢索改動)。
5. 未完成: Option 2 真入庫未開始(要 PLAN);24 條孤兒細決定未做;ship V3 未做(要 PLAN);footnote bypass 未收;觀察窗未讀(8/2 + 8/5)、probe 未刪;backend route 未拆;總帳三桶未讀完;`HANDOFF_PACKAGE.md:32` drift 未修。
6. 本 session 我出過嘅錯同已記錄嘅更正: (a) **用錯 judge model** —— 信 code default 而唔係 Render dashboard,出咗兩份唔代表生產嘅 baseline,由 Leonard 撳 dashboard 揪返;教訓「對照組證明儀器有反應、證明唔到儀器指住正確系統」寫入 code + findings + commit;(b) **D13 標錯做空白** —— 「越多砌數個發現越大」個方向對我有利,打開 Supabase 核實先發現 970/1570 有出處、footnote 做緊正經嘢,已更正;(c) **一度講「7/7 砌數」overclaim** —— 逐條讀後散為「7/7 答咗但只 1 條實錘砌數、1 條其實啱」;(d) **decline 半邊數錯**(講 12 實際 11),直接由檔案數返更正。全部寫入 SESSION_LOG S199 + commit message。
7. commits: `a65e723` → `829aa49` → `c96dc6d` → `a80c69b` → `1aeab49` → `f02c069` → `710d8cc` → 本 closeout commit。Supabase **16,062 零寫入** / registry **256** / v3.2.2 / 凍結合約零接觸。

## Previous Session Record (S198)
1. UTC date: 2026-07-30
2. Session ID: Claude_20260730_1015 — Leonard 交返 S197 ① 嘅 Render logs 答案；我冇當佢係零流量，查落發現個指示本身量唔到嘢，改為主動 instrument。
3. Completed: ✅ 證實 S197 ① 係結構上量唔到嘢嘅指示(三層根因、逐層對照組;per-request log = Pro plan 功能,此為 Hobby)。✅ `[route-probe]` 上線 live 驗(handler 最頂、只認兩條 route、永不印 body;24 請求→24 行)。✅ 按 §3 停低一次修正 IP 認人(改印全鏈,`getClientIp()`+rate limiter 零接觸)。✅ 全 repo grep 確認兩條 route 零內部呼叫點。✅ DOC_SYNC +1 row(31→32) + §4a 歸檔(462→199 行、8→4 entries) + 修好既有 `ack:log-entry` marker 唔平衡。
4. QC: `npm run check`/`npm run build` exit 0 ×2;probe 本機自檢 ×2 對數;live 24 請求→24 行。Supabase 16,062 零寫入 / registry 256 / v3.2.2 / 凍結合約零接觸。
5. 我出過嘅錯: (a) 一個鐘內踩兩次「信量唔到嘢嘅工具沉默」陷阱(log search + `/health` 重啟偵測);(b) 講錯 cold start 歸因(實際 08:52 UTC 早我 43 分鐘,dashboard UTC+1);(c) PLAN 承諾 IP 認人首版做唔到。全寫入 SESSION_LOG S198 + PROJECT_DECISIONS Insights。
6. 🔴 遺留: 觀察窗未讀(8/2 + 8/5)、probe 未刪、backend route 未拆。
7. commits: `ddc98d5` → `16fec71` → `2eb642f` → `07173f6` → `b74f5f4` → `12bf7c3`(closeout)。

## Previous Session Record (S197)
1. UTC date: 2026-07-29
2. Session ID: Claude_20260729_S197 — Leonard 由「roadmap 有無建議」開始，定咗退役標準，批「做」三次；我中途兩次推翻自己並停低報告。
3. Completed:
   - ✅ **量度工具 `dev/source/channel_a_coverage.py`**（self-test 34 項，含兩條故意整壞證明守衛會 FAIL）+ **`CHANNEL_A_RETIREMENT_LEDGER.tsv`**（455 條逐條 tier + 出處 + 頁碼）+ **`CHANNEL_A_COVERAGE_FINDINGS.md`**。455 條全跑，0 error，對數 OK。
   - ✅ **前端 Channel A 路徑全清**（−109/+8 行），已證摸唔到，live 驗零殘留。
   - ✅ **9 條有已證出處嘅鏡像 chunk 退出服務路徑**，逐條附引文；Supabase 零寫入。
   - ✅ **eval 補盲**：30 → 34 條，新增 4 條「邊個負責」query；其中 2 條由 baseline 證實我釘錯預期，已即時更正而唔係留住永久紅燈。
4. QC: eval 34 條 before→after **PASS 23 / FAIL 0 / errors 0，0 blocking failures**，32 條完全相同；唯一 SET_ADDED = `procurement` 加入 `subvention_tips`（預期效果）；`bus_escort` RANK_SHIFT 屬容許嘅 ANN tie flip、未獨立證實成因。live 抽驗 4 條 query 逐條符合設計意圖。tsc exit 0 ×2。凍結合約機械核實零接觸。
5. 未完成: backend 兩條 route（阻塞於 Render logs）；總帳 172 UNVERIFIED + 107 PROVISIONAL 未讀；133 CLEARED 未抽樣；judge prompt（S196 遺留）；`PUBLISH_PAT` scope。
6. 本 session 我出過嘅錯同已記錄嘅更正: (a) 把尺壞咗 —— 中文數字令工具系統性高報缺口，修完 71 條轉桶；(b) 憑一條 query 提議整批剷走 109 條並講「拎走唔係損失」，量埋成批證實 93/109 冇替代品、剷走會蝕；(c) eval 新 query 我釘錯咗兩條預期，由 baseline 捉返。三項全部寫入 SESSION_LOG S197 同 `CHANNEL_A_COVERAGE_FINDINGS.md` §8。
7. commits: `c01e646` → `596e383` → `2d70ef7` → `5754c00` → `3ba92fe` → `d554b4c` → 本 closeout commit。Supabase **16,062 零寫入** / registry **256** / v3.2.2 / 凍結合約零接觸。

## Previous Session Record (S196)
1. UTC date: 2026-07-28
2. Session ID: Claude_20260728_S196 — Leonard 三次批 "go"。任務由「修 route 次序」開始，兩次因為實測推翻前提而停低報告，最後以「設定規則防止我再犯武斷及疏忽」收結。
3. Completed:
   - ✅ **A：新 `school_bus` route**（g18 + 5 份姊妹指引，bus tokens 由 safety 搬過去）+ 修正 query expansion（第一版塞晒受眾名詞，eval 捉到「跟車保母」跌位）。校巴內容由 rank 5 @0.506 → rank 2-7 @0.743-0.768。
   - ✅ **B：curated footnote lead 加 lexical gate**（DF 自校準、≥2 informative bigram、query 訊號不足則 fail open）；judge bypass 改為綁定「gate 批准嘅 lead」。**被拒 footnote 唔會被刪，只收走特權。**
   - ✅ 新驗收工具 `dev/source/footnote_lead_probe.py`（含集合對數守衛，已用故意整壞證明會 FAIL）。
   - ✅ **量度到 judge 本身近乎恆等於「否」**（shipped prompt 8/16，8 條有答案嘅全部拒晒，4 條答案逐字喺 chunk 入面）→ 寫成 `dev/source/JUDGE_PROMPT_FINDINGS.md`，**冇 ship 任何 judge 改動**。
   - ✅ **規則落地**：`dev/rules/communication.md` 5→10 條（第 3 條改寫、第 10 條方向不對稱貫穿條款）+ `dev/RULE_PACKS.md` 擴闊載入條件。
4. QC: eval 三對（baseline → after_a → after_a2 → after_b → final），最終 **PASS 20/30 FAIL 0 errors 0**；footnote probe 三次（before → final → relabelled/corrected），最終 **positive 30/30、negative 5/13**；全語料覆核 **206/206** footnote 自問仍攞到 lead；TS 同 Python 鏡像 informative bigram 同為 **7828**；tsc exit 0 ×4。凍結合約機械核實零接觸。
5. 未完成: judge prompt 改良（需未經 tune 嘅驗收集，見 JUDGE_PROMPT_FINDINGS.md）；收緊 footnote bypass（**必須喺修好 judge 之後**，否則淨蝕）；`PUBLISH_PAT` scope（只有 Leonard 做得到）。
6. 本 session 我出過嘅錯同已記錄嘅更正: 三條 query 被我判「borderline」而剔走（三次判錯、方向一致、令我低報殘餘問題 2/10 vs 實際 5/13）；靠 ilike 命中就下結論（打開先知係 g07 講家課時間）；跨行 regex 食咗 handoff 一段（git diff 捉到、已還原重做）；把「判過但判錯」講成「冇判過」。全部已寫入 SESSION_LOG「紀錄更正」段，並成為新規則第 3/6/8/9 條嘅來源。
7. commits: `b61e108` → `7078719` → `528435d` → `969698e` → `138dfca` → `ece0a41` → `2cdcce4` → `ad71c0f` → `bb07bc3` → `3d4ecf0` → `9804239` → `c4e5830` → 本 closeout commit。Supabase **16,062 零接觸** / registry **256** / v3.2.2 / 凍結合約零接觸。


## Previous Session Record (S195B)
1. UTC date: 2026-07-27
2. Session ID: Claude_20260727_S195B (S195 下半) — Leonard「全做」→ 開 task list、先攞 eval baseline、逐項落手 8 項優先事項 → 其中 1 項做唔到（需佢帳戶權限）、2 項結論同原假設相反、1 項我做錯由 eval 捉返即刻還原 → 兩次 DELETE 由 Leonard 執行（權限閘擋我）。
3. Completed（詳見 SESSION_LOG S195B）:
   - ✅ **① 五份校車姊妹指引入庫**（28 chunks，頁碼逐份自檢全對齊，live rank 0 @0.624）。
   - ✅ **③ g21／g22 引文錯配修好**（Issue #5）：g22 補回封面頁修正整體錯開一頁；g21 拆出 `va_safety_sec`（中學版），解決「一半 chunks 掛錯文件」。刪 106 條舊 chunk，**兩條人手 footnote 明文保護未被刪**。
   - ✅ **⑤ 封面核對接 CI**：月跑 workflow + `--baseline` diff 模式（alert on change, not on count）+ 9 條 self-test。
   - ✅ **⑥ 重複登記合併**：`kgecg_2017`／`g31` deprecated（合併前先證實同一份文件），清走 2 個 dead allowlist 引用。
   - ✅ **② judge 門檻實測 → 決定保留 0.70**（敵意 0.632 vs 真命中 0.624，分佈重疊；新工具 `judge_probe.py`）。
   - ✅ **⑧ 公開庫重複行 + 死連結清走**，凍結 count 158 不變（原以為要 158→159）。
   - ✅ eval query 25 → **30**（新增 5 條守住今次入庫嘅源）；最終 **PASS 20 / FAIL 0 / errors 0**。
4. QC: 四份 eval run（before → after〔捉到 3 條 regression〕→ after_revert〔對 baseline 25/25 全同〕→ final〔20/30 PASS〕）全部 commit；頁碼錨點逐源自檢全 offset 0；刪除逐條驗；凍結合約 sha256/count 機械核實；tsc exit 0 ×4。
5. 未完成: ④ `PUBLISH_PAT` scope（只有 Leonard 睇得到）；「校巴營辦商責任」route 次序；judge 選項 (c) 改良 prompt。
6. commits: `7f4c306`（主體）→ `2f04c42`（spotlight revert）→ 本 closeout commit。Supabase **16,062** / registry **256** / v3.2.2 / 凍結合約零接觸。

## Previous Session Record (S195 上半)
1. UTC date: 2026-07-27
2. Session ID: Claude_20260727_S195 (S195) — Draft root 開工 → §1 startup → 起手探針 4/4 綠（HEAD==origin/main `138588a`、無新 bot commit）→ 我建議「①判斷交 Leonard、②③ 我做」→ Leonard「跟你建議」→ READ 階段兩度發現實況超出我原述、按 §3 停低報告 → Leonard 兩個決定（Supabase 一齊修／g21-g22 只記錄）→ 執行 + 全掃驗證 → 收工。
3. Completed（詳見 SESSION_LOG S195）:
   - ✅ **修好 2 條真 404（積咗 4 星期）**：`g01` 資助學校採購程序指引（34 chunks）、`ls_jss_2010` 生活與社會課程指引（251 chunks）。用 playbook 方法 B re-crawl 揾返真檔（前者上游改名、後者搬入 PSHE 檔案庫），**逐頁比對證明 30/30 同 183/183 頁完全相同** → 判定 re-point 而非 re-ingest。
   - ✅ **同一條 URL 6 處副本一次過對齊**：`source_registry.json`、`app.html` GUIDELINES_REGISTRY、`guidelines.json`（**經 `build_guidelines.py --write` 重生，非手改**，符合 DOC_SYNC row 35「NEVER hand-edit」）、`data.json`、`dev/checklists/_src/secmeta.json`、Supabase `wiki_chunks.url` **285 行**（`#page=` 錨點原樣保留）。
   - ✅ **③ 5 條 pdf-serve-HTML 全部更正**：`g21`／`g22` registry 追上 store 實際供應的直連 PDF；`g31` 指返真身 PDF ＋標與 `eng_pri_guide_2025` 同一文件；`g30` `source_type` pdf→html；`religious_edu_jss` 揾返直連 PDF、**封面核實為 2024 版**（原記 legacy）、status candidate→verified。
   - ✅ **GitHub 追蹤留底**：Issue #4 補上修復證據並說明仍為 `g18` 開住；新開 Issue #5 記錄 g21／g22 引文錯配。
4. QC: `check_served_urls.py --check` 全掃 **268 URL／267 OK／0 error**（修前 2 broken）/ live Channel B 實測兩源都返新 URL（`g01` rank 1-3；`ls_jss_2010` rank 0 @0.715 p.30，p.30 內容與 vault 一致）/ Supabase `count=exact` **16,035 前後同值**、285 行全部 PATCH 成功、舊 URL 殘留 0 / 凍結合約經機械核實未動（`knowledge.json`+`role_facts.json` sha256 相同、guidelines 158/v2.6.1、`PLATFORM_VERSION` 3.2.2）/ `build_guidelines.py --self-test` PASS（registry 167 / public 158 / dropped 9）。
5. 未修（已記錄）: `g18` 404 需 re-ingest（改版非改名）；`g21`／`g22` 引文錯配（Issue #5）；`religious_edu_jss` 入公開庫會令 158→159（需拍板）。
6. commits: 本 session 主體 + closeout commit。Supabase **16,035** / registry **250** / v3.2.2 / 凍結合約 = 全部不變。

## Previous Session Record (S194)
1. UTC date: 2026-07-26
2. Session ID: Claude_20260726_S194 (S194) — 頂層 dormant root「開工」→ redirect Draft → §1 startup → 起手探針 4/4 綠 → Leonard 一次授權三件事「R1 同意／R5 做／①＋②」+ 釐清 technology-edu index 頁＝監察對象、`IIT_Summary on AI_TC.pdf`＝入庫對象 → ② 在 READ 階段由「核 supersede」升級為真 bug → AskUserQuestion → Leonard 揀「A 完整修」＋「做全庫封面掃描」→ 全部完成並 LIVE 驗 → 「收工」full closeout。
3. Completed（詳見 SESSION_LOG S194）:
   - ✅ **修 `ict_sss_2021` 長期指錯文件**：`CS_CAG` 被當 Computer Science，實為 Citizenship and Social development → 81 個公社科 chunks 長期掛 ICT 標題（prod 實測 top-1 標題錯配），真 ICT 2021 從未入庫，且 `curriculum` route 從未有任何 ICT 源。修法：新 `cgss_sss_2021` 承載該 81 chunks（**hash set 81/81 相同**，內容逐字不變）→ DELETE 舊 81（post-count 0）→ `ict_sss_2021` 改指 EDB 官方檔 + 入真正文 116 chunks + route/supersede 補齊。
   - ✅ **入庫《人工智能初探》框架正文** `iit_ai_framework_2026`（18 chunks）；通函 `edbcm113_2026` 只有 3 chunks（封面+摘要），正文才係實質內容。
   - ✅ **roadmap R1 eval harness**（`dev/source/eval_retrieval.py` + `eval_queries.json` + `eval_runs/`）：25 條短 query、可 diff 兩次跑、容 tie flip、429 唔當零結果。入庫前後兩份 run 已 commit 作跨 session 對照基線。
   - ✅ **第 5 監察／Method C 封面核對**（`dev/source/check_source_titles.py`）：補 freshness（問「bytes 有無變」）同 served-url（問「連結通唔通」）結構上睇唔到嘅「指錯文件」類。
   - ✅ **修程序缺陷**：display-sync 全檔字串取代一直靜默改寫 CHANGELOG／CODEBASE_CONTEXT **歷史條目**；已修正受影響數字 + 兩檔由 `execute_ingest.py` `DISPLAY_SYNC_TARGETS` 移除。
   - ✅ **R5 sibling 審計（read-only）**：推翻 handoff 舊假設（該 repo 已 private，public 面係 `edb-circular-site`）；兩 repo 全歷史 679 commits secret 掃描乾淨。
4. QC: tsc exit 0 / py_compile ✅ / 兩個新工具 `--self-test` 各 24 項全綠（含針對自身 2 個校準缺陷的回歸測試）/ **eval PASS 12→14、errors 0**（`ict_guide` FAIL→PASS rank 0 @0.624、`nonlocal` FAIL→PASS rank 2、`cgss` top 由 mislabel 0.568 → `cgss_sss_2021` 0.773 且 synthesis grounded）/ chunk hash set 81/81 / live 總數 16,035 由 `count=exact` 直查 / 封面掃描 192 源冇第二個指錯文件。
5. commits: `3f2c9d9`（主體）→ `e0e2f3b`（eval run + 修 ai_intro 斷言）→ `76e5719`（log/handoff checkpoint）→ `744af53`（§4a archive）→ 本 closeout commit。Supabase **16,035** / registry **250** / v3.2.2 不變 / 凍結合約零接觸。

## Previous Session Record (S193)
1. UTC date: 2026-07-26
2. Session ID: Claude_20260726_1219 (S193) — 頂層 dormant root「開工」→ redirect Draft → §1 startup → 起手探針 4/4 綠（其中 git 探針揪出本地落後 origin/main 4 個 bot commit → ff-pull）→ 逐條 live 探測 4 條自動入庫源 → 揪出 2 條檢索唔到 → Leonard 批「1＋2＋Monitor technology-edu 頁」→ 修根因 + 補機制 + 核實監察 → 「收工」full closeout。
3. Completed（詳見 SESSION_LOG S193）:
   - ✅ **修「入庫但搵唔到」根因**（code-verified：全庫 ANN top-40 先於 SOURCE_SET post-filter → 細源結構上入唔到窗口）：新 `wikiRepository.searchSpotlightSources()` route/ANN-獨立 exact-cosine + `SPOTLIGHT_SOURCE_IDS` 一個 lead slot @0.60（實測門檻：on-topic 0.62–0.72 vs 20 條敵意 off-topic 最高 0.563）；raw-query embedding 兩 overlay 共用故呼叫數不變。
   - ✅ **管道唔再靜默留債**：`execute_ingest.py` 步驟 **4b** 自動註冊新源入 spotlight + `post_deploy_smoke` 由無人睇嘅 bool 改為真閘（多 phrasing 報 rank、搵唔到發 `::warning::` annotation）。
   - ✅ **Monitor 核實**：Leonard 指定嘅 technology-edu 課程文件頁早已在 discovery 62 個監察頁內（無需新增）；對該頁 11 個文件連結 diff → 揪出 2 條未入庫（`IIT_Summary on AI_TC.pdf` = edbcm113 框架正文、`ICT_C&A Guide_c_final.pdf`）→ 列 Open Priorities 待 Leonard 拍板。
   - ✅ **治理**：DOC_SYNC 補 Option A 管道 row（原本無 row 覆蓋該機制）+ CODEBASE_CONTEXT Directory Map ×2 + AI log + handoff/log；handoff opening message 由 generic 模板收斂為權威 state-rich 版（S192 曾令 handoff↔START drift），prompt mirror check PASS。
4. QC: tsc 0 ×2 / py_compile ✅ / discover self-test ALL PASS / executor dry-run 4b 正確且批准閘仍擋 + 零 live 寫入核實 / **LIVE 目標源 6/6 PASS** + synthesis grounded / **live 回歸 13 條：污染 0/13、既有預期 5/5、9 條仍有 footnote 參與** / A/B 14 條 12 相同（2 條差異經隔離測試證與本改動無關）。
5. commits: `ef426cc`（code）→ `ffd7f22`（治理持久化）→ 本 closeout commit。Supabase 15,901 / registry 248 / v3.2.2 / 凍結合約 全部零接觸（純檢索行為修復，同 S174/S183 先例一致唔 bump）。

## Previous Session Record (S183)
1. UTC date: 2026-06-25
2. Session ID: Claude_20260625_S183 — 「開工」→ 頂層 redirect → Draft active root；起手探針 4 條全綠（HEAD `77d133f` == origin/main S182 closeout / app v3.2.2 / Render cache_a warm 455 / Supabase 15,536）→ Leonard 指出 https://www.edb.gov.hk/tc/curriculum-development/4-key-tasks/moral-civic/ve_curriculum_framework2026.html 「價值觀教育 2026 未入呀」→ confirmed gap via grep + WebFetch（registry 只得 2021 試行版 + 2023 EDBC 183 enrich，2026 正式版未入）→ PLAN HIGH risk + AskUserQuestion Option A scope（主框架 only + 配套通告 + 2021/2023 supersede retain）→ workflow（download → extract → registry update + supersede mark → adversarial subagent review → live INSERT）→ 中途 Leonard 加 EDBCM 221/2025 piggyback（AI 撥款計劃，topic=it）→ live INSERT 113 chunks → post-INSERT 3 issue + 2 governance rule + brand fix + Pages outage debug → 「收工」full closeout（本 commit）。
3. Completed（詳見 SESSION_LOG S183）:
   - ✅ **3 sources LIVE INGEST + 揭發 duplicate post-INSPECT 修復**：(1)`values_edu_framework_2026` 主框架 93 chunks topic=curriculum（86 substantive pages、5 章節、12 首要價值觀、總體方向「立根中華、聯通世界、擁抱未來」）+ (2)`edbc_3_2026_values_edu` 5 chunks（即發現同份 PDF prior session 已 ingest 做 `edbc003_2026` 6 chunks → hard-delete 我嘅 5 chunks，retain prior） + (3)`edbcm_221_2025_smart_teaching` 15 chunks topic=it（『智』啟學教 AI 撥款 50 萬/校）。Supabase 15,536→15,649→15,644（淨 +108）；source_registry 225→228→227（淨 +2）。
   - ✅ **Adversarial verbatim subagent review GO-as-is**：programmatic per-page parity 103/103 pages 0 divergence；12 首要價值觀完整 + 5 章節 titles + 中華經典引文（范仲淹/杜甫/屈原/諸葛亮/岳飛/文天祥 等 8 條 quotes）byte-exact；總體方向全 instances 對。
   - ✅ **Backend `searchChannelB.ts` 2 routes patch**：新 `value_education` route SOURCE_SETS (5 sources) + TOPIC_KEYWORDS（價值觀／首要價值觀／立根中華／12 首要 等）+ QUERY_EXPANSIONS；擴 `digital_education` SOURCE_SETS +`edbcm_221_2025_smart_teaching` + TOPIC_KEYWORDS +「智啟學教／數字素養／數字技能」；**兩者提到 finance 之上**（first-match precedence 解 finance「撥款」keyword 偷 query）。Routing smoke 12/12 PASS。
   - ✅ **Anti-confab judge bypass 擴 vault_extract**（S183 governance rule）：synthesizeAnswer 加 `VAULT_LEAD_SCORE = 0.70`，bypass judge for vault_extract chunks 高 cosine（S178 footnote-lead bypass 只 cover footnote_curated；vault_extract rank-0 score 0.75+ 仍俾 judge over-decline）。Post-fix 3/3 user query ANSWER + grounded synthesis（「智啟學教是什麼」、「智啟學教撥款適用範圍」、「價值觀教育」）。
   - ✅ **Supersede ranking penalty 0.05**（S183 governance rule，Leonard 提出 long-term rule）：backend +`SUPERSEDED_IDS` Set + `SUPERSEDE_PENALTY=0.05` + `applySupersedePenalty()` helper（apply 兩次：main results + footnote overlay、re-sort 後）。Initial set {values_edu_framework_2021_trial, edbcm183_2023_values_edu}。Post-fix 3/3 短 query「價值觀教育」「首要價值觀」「12 首要價值觀」VE_CF 2026 rank 0/1/2、2021 試行版 demoted rank-3+。SSOT = registry `superseded_by` field；future 新 superseding version ingest 時 manually sync set。
   - ✅ **WhatsApp share text brand fix**：app.html line 2683 + mobile.js line 292 由「EDB K1 知識平台 · 政策搜尋」改為「香港學校政策搜尋平台 · 政策搜尋」（跟 product banner 一致）。純前端 2 line edit。
   - ✅ **Display-sync 9 處**（15,536 → 15,649 → 15,644）：role_facts.json / K1_API_SPEC.md / index.html (×3) / app.html (×4) / knowledge.json / README.md (×4) / dev/CODEBASE_CONTEXT.md / dev/knowledge/role_facts.json / CHANGELOG.md。
   - ✅ **update_log.json user-facing 📋 modal entry 加咗 1 條**（newest top；date 2026-06-25 / 新增 VE_CF 2026 + EDBCM 221/2025 簡潔 desc）。
   - ✅ **CHANGELOG S183 entry prepend** + **CODEBASE_CONTEXT AI Maintenance Log S183 entry** + **PROJECT_DECISIONS append** 2 governance rules（待寫入 closeout）。
   - ✅ **Pages deploy transient outage 救活**：commit `1359916` (supersede penalty) Pages workflow #397 deploy step 4s 失敗（build + report ok、單 deploy step issue、subsequent `71f1c80` push 排隊 behind 失敗 #397）→ empty commit `4ddffb6` 觸發 #398 success → 確認 transient outage（no persistent issue）→ 工具補裝 gh CLI 2.95.0 via brew、public REST API 查 workflow run status 不需 auth。
4. Pending:
   - **VE planning tools 4 條 PDF** S183 Option C deferred 部分（VE Curriculum Plan Table / VE Activity Plan Table / Secondary Tools / Primary Tools，規劃工具表格）— Leonard 揀 Option A 時 deferred。
   - S182 Feature 2a 追問 multi-turn + Feature 2b 文件 scoped Q&A（per Leonard sequence A 隱含繼續，estimate 1.5-2 日）。
   - S181 NEXT 仍 valid（Phase 3 full_chunks_routed + 4 新 route / source_registry.json 26 fold-in / freshness 5 變動 / 既有 monitor / playbook OCR 提案 push / footnote broad sweep）。
   - ⚠️ **CRITICAL**：SESSION_LOG archive 第 5 次 defer（trigger 行數 602 > 400 + N=13 entries）— next session **開頭即跑** `python docs/qa/session_log_maintenance.py --apply --session-log dev/SESSION_LOG.md --archive-dir dev/archive`，唔好繼續 defer。
5. Next priorities: ① **CRITICAL** SESSION_LOG archive（5th defer 唔可再 defer）→ ② Feature 2a + 2b 一齊做（共享 conversation UI、estimate 1.5-2 日）→ ③ Phase 3 full_chunks_routed（覆蓋率最後一哩 medium risk）→ ④ VE planning tools 4 PDF（Option C deferred 部分）→ ⑤ source_registry 26 fold-in / 既有 monitor。
6. Risks: 🟢 HEAD==origin/main `4ddffb6`（7 commits chain 全 push、Pages #398 + Render 4 redeploys 全 LIVE verified、0 outstanding bug）、Supabase **15,644** vault_extract +108 net、source_registry **227**、凍結合約零接觸（`_meta` 2.3.0 / facts 455 / guidelines 158 不變）、PLATFORM_VERSION 3.2.2 不 bump。⚠️ Backend code 4 round patch（route patch / judge bypass / supersede penalty / brand fix）— 累積 risk surface 廣，monitor 1-2 週確保 regression-free。⚠️ Supersede penalty `SUPERSEDED_IDS` Set 雙處 SSOT（registry + backend hardcoded set）易漂移；future ingest 新 superseding 版時必同步雙處（手 sync pattern 同 SOURCE_SETS 一致）。⚠️ Pages transient outage 唔保證唔再發；standard remediation = empty commit retrigger。⚠️ Adversarial subagent 確認原 PDF 但唔保 future re-ingest 自動 verify（每次入新源仍要 subagent review）。⚠️ Query 5/8 fail（query 含「試行版」誤導 keyword）= semantic correct behavior、retain entries 設計 expected。
7. commits（push origin/main，7 條全 push）: `bc26d41`(feat S183 ingest +113 → 15,649) + `edebbbd`(fix S183 hard-delete duplicate -5 + 2 routes patch → 15,644) + `40923d5`(docs S183 update_log.json) + `a718a83`(fix S183 judge bypass vault_extract ≥0.70) + `1359916`(feat S183 supersede penalty 0.05 governance rule) + `71f1c80`(fix S183 WhatsApp share text brand 香港學校政策搜尋平台) + `4ddffb6`(chore retrigger Pages empty commit) + 本 closeout commit（handoff/log reconcile + PROJECT_DECISIONS append）。Render 4 round redeploy 全 live verified；Pages #398 success；Supabase 1 INSERT (113 chunks) + 1 DELETE (5 chunks) 全 Leonard 明確授權。

## Previous Session Record (S182)
1. UTC date: 2026-06-25 | Claude_20260625_S182
2. WhatsApp 分享按鈕 SHIPPED desktop + mobile，純前端 frontend-only，平台 v3.2.1→v3.2.2；政策搜尋整理答案 card 底加綠色「📤 分享至 WhatsApp」按鈕（synthesis-gated）；點擊開 `wa.me/?text=<encoded>`（mobile WhatsApp app／desktop WhatsApp Web）；訊息 compact format（綜合答案 + 來源 dedup top-5、每源 ≤3 pages、wa.me URL ~965 字）。QC 7/8 PASS、1 DEFERRED（localhost CORS、live verify post-push 8/8 PASS）。0 backend/Supabase/Render restart、凍結合約零接觸。**S183 brand fix on top**: share text 第一行 brand「EDB K1 知識平台」→「香港學校政策搜尋平台」（跟 product banner 一致）。commits `d2e4480`(feat) + `4433afe`(docs) + `77d133f`(closeout) + S183 brand fix。詳見 SESSION_LOG S182。

## Previous Session Record (S181)
1. UTC date: 2026-06-25
2. Session ID: Claude_20260625_S181 — 「開工」→ 頂層 redirect → Draft active root；起手探針全綠（HEAD `55e428a`==origin/main S180 housekeeping commit、app v3.2.1、Render cache_a warm 455、Supabase 15,414/footnote_curated 84）→ Leonard 講「agents team 全部做、QC plan、QC審批、敵意審查」→ Agent team workflow Phase 1-5（plan→9 並行 research→2 並行 adversarial review→QC 合成→Option B Leonard GO→ingest+verify+push）→ live 122 footnote 全 8/8 Render verify rank-0/1 + synthesis grounded → 「收工」full closeout。
3. Completed（詳見 SESSION_LOG S181）:
   - ✅ **8 angles discovery 大入庫 LIVE 122 條 footnote_curated overlay**（Supabase footnote_curated 84→**206**、total 15,414→**15,536**）：教師註冊 13（Cap.279 §42-§61 + TPC sanction ladder + supply teacher）／學校註冊+DSS 10（§10-§14 + DSS 2⅓ unit + 10%/50¢ + EDBC 10/2012）／NCS 行政資助 18（**EDBC 4/2026** Composite Grant + 8/2020 5-tier + 9/2019 SEN + KG 5-tier）／傳染病停課準則 15（**CHP 2025-Nov** + 20% ILI / 7-day closure + 漂水稀釋 + 床距 1m）／學費減免+書簿津貼 17（SFAA AFI + 2024/25 thresholds + KCFR 15 Aug + TA 31 Oct）／NET 計劃 18（**EDBC 8/2025** 二選一 + HK$900k/$1M + IELTS 7.5 + 兩級 gratuity 10%/15%）／校舍法定安全/EMSD 13（**EDBC 12/2026** 消防 + Cap.618 升降機 monthly/12mo/5yr + EDBC 22/2024 30 Nov）／SAG 附錄深抽 14（病假 28→48→168 + 罰款表 + 利益衝突 10 例 + 假期批核矩陣）。canonical source_id：Cap.279→`cap279_education_ordinance`、EDBC 10/2012→`edbc_10_2012_fee_remission`。
   - ✅ **Agent team workflow（PLAN+QC+adversarial）**：Phase 1 = 9 個 general-purpose subagent 並行 verbatim research（180 candidates harvested）／Phase 2a = adversarial reviewer A sample audit 22/26 PASS + 4 fix-then-pass（無 hallucination：CHP 通報表還原序、漂水 §3.4.1 label、CHP 信加 [...] ellipsis、EDBC 22/2024 split §2/§5）／Phase 2b = reviewer B coverage+routing 113/127 novel (89%) + canonicalize source_ids + URL health 11/11 OK／Phase 3 = QC 合成 + 修 + drop 5 redundant／GO Gate = Leonard 揀 Option B（R1+R2 footnote sweep，no backend code change）／Phase 4 = self-test embed 122 candidates + cosine ≥0.45 LEAD = **122/122 (100%)**〔1 entry `sag_apx_leave_approval_matrix` re-tune q+keywords 0.401→0.750 一次過搞掂〕／Phase 5 = INSPECT before 84/15414 → INSERT 122 → after 206/15536 無 collision無 missing。
   - ✅ **Render live verify 8/8 PASS**（8 representative queries 1 per angle）：7 條 rank #0（教師註冊撤銷 0.683 / DSS 學費減免 0.723 / NCS Composite 0.679 / 流感停課 0.650 / AFI 公式 0.690 / EMSD 升降機 0.601 / SAG 病假 0.640）+ 1 條 rank #1（NET grant 0.608，rank #0 為 `net_grant_min_1nat` 0.639 = 另一條 S181 NET footnote）；synthesis 全 grounded with 新 verbatim text（Cap.279 §47、AFI 公式、HK$900k/$1M、Composite baseline/additional/enrichment、ILI 7-day closure 等）。
   - ✅ **display-sync 8 點完成**：knowledge.json + role_facts.json + dev/knowledge/role_facts.json + K1_API_SPEC.md + README.md + index.html + app.html + CHANGELOG.md（新 S181 章節）= 15,414→15,536。凍結合約零接觸（`_meta` 2.3.0 / facts 455 / guidelines 158）；PLATFORM_VERSION 3.2.1 不變。
4. Pending（已少咗 8 條 discovery angle 主題、餘 backlog 仍 open）:
   - source_registry.json 26 新源 metadata fold-in（minimal title/url 已足；reviewer B 列嘅 26 個新 source_id 已用 canonical 化版本入庫；registry 文件待補 metadata）
   - **Phase 3 full_chunks_routed**：reviewer B 估計 ~60 full chunk + 要 patch backend `searchChannelB.ts` 加 4 個新 route（`teacher_registration` Cap.279 + `ncs_support` 或擴 sen + `net_scheme` + `safety` 加 EMSD/Cap.618 keywords）+ Render redeploy + routing verify；屬 medium risk follow-up（已試 S171 加 `digital_education` route 同 pattern）。
   - footnote broad sweep（optional 低值）／freshness 5 變動（detection-only）／既有 monitor（MPF bypass / 文件標註 / Render cold-start / per-segment / undici / SMC recall / DEBP OCR）。
   - playbook OCR 提案 push（S180 留低 local `ead3749`，cross-repo push）。
5. Next priorities: ① Phase 3 full_chunks_routed + 4 backend route patch（如 Leonard 想極致覆蓋率）→ ② source_registry fold-in（如想顯示面 polish）→ ③ 既有 monitor + freshness 跟進。
6. Risks: 🟢 HEAD==origin/main `cd47779`、Supabase **15,536**、footnote_curated **206**、凍結合約零接觸、PLATFORM_VERSION 3.2.1 不變、0 outstanding bug。⚠️ live Supabase 寫入＝安全閘 gated 要明確授權（本 session Leonard 揀 Option B＝明確授權 INSERT 122）。⚠️ 入/改 footnote 後必 restart Render（push 已觸發 redeploy、live 已驗）。⚠️ source_registry 26 新源 metadata 待 fold-in（chunks 已 live、retrieve 不受影響、只係顯示面 polish）。⚠️ Phase 3 full_chunks_routed pending（覆蓋率仍有上升空間，但 footnote_curated 已 capture 大部分 substantive policy verbatim）。⚠️ playbook 跨 repo push 仍待 Leonard 授權（S180 留低）。⚠️ OpenAI quota 曾用爆（已充值、warm=455 健康）。
7. commits（push origin/main）: `cd47779`(feat S181 122 footnote ingest + 8 display-sync mirror + CHANGELOG + ingest script audit trail) + closeout commit（handoff/log reconcile）。live Supabase INSERT 122（Leonard Option B 明確授權、INSPECT before/after 全綠、Render live verify 8/8 rank-0/1 + grounded）。

## Previous Session Record (S180)
1. UTC date: 2026-06-24 | Claude_20260624_1415_S180
2. SAG 學校行政手冊版本核對（2025-11 → 2026-05）：§3.7.3 新增段 curated overlay 入庫 LIVE。footnote_curated 83→84、Supabase 15,413→15,414。registry version_label sag_2025_11/g24→2026-05 + 公開指引 title sync（guidelines.json 2.6.0→2.6.1 + app.html count 158 不變）。SAG dedup 確認由 soft-dedup 妥善處理。雲端 OCR 引擎參考袋低 Backlog（playbook proposal `ead3749` local-only 未 push）。commits `fb1f8fc`→`e521dee`→`0707faa`→`7828f3e`→`2acf631`→`79840e5`→`55e428a`。詳見 SESSION_LOG S180。

## Previous Session Record (S179)
1. UTC date: 2026-06-23 | Claude_20260623_S179
2. footnote 擴充第三批 14 + discovery 三快贏 8 + kg_operation 補標 + TRG 404 修復，全 LIVE（Render 6/6+8/8）；footnote_curated 61→83、Supabase 15,391→15,413。commits `3897169`→`89eee3a`。詳見 SESSION_LOG S179。

## Previous Session Record (S178)
1. UTC date: 2026-06-23 | Claude_20260623_S178
2. forms 第二批 + MPF 漏答修復，全 LIVE（Render 6/6）：tips #27 出租校舍 40% 入政府帳（EDBC 5/2011）+ #28 12 個月重複採購 $50k/$200k 不得拆單（EDBC 4/2013）verbatim 核 Tips TC PDF（footnote_curated 59→61、Supabase 15,389→15,391）；MPF 漏答修復＝top 係 curated footnote 且 cosine≥0.45 時跳過 S177 judge（`searchChannelB.ts`，真因＝judge 過度保守非缺關鍵詞）。commits `f19da01`→`41b7991`。詳見 SESSION_LOG S178。

## Previous Session Record (S177)
1. UTC date: 2026-06-23 | Claude_20260622_S177
2. 政策搜尋砌數修復 + EDB 津貼表格 footnote 入庫，全 LIVE：①TRG 凍結教席「10%」footnote（修砌 IMC 60%）②synthesis 前防砌數 binary judge（`searchChannelB.ts`）③EDB 津貼表格細字 25 條 footnote（footnote_curated 34→59、Supabase 15,364→**15,389**，全 verbatim 核）。commits `71763f8`→`1f0d959`→`7827712`→`ef50b48`。詳見 SESSION_LOG S177。

## Previous Session Record (S175)
1. UTC date: 2026-06-22
2. Session ID: Claude_20260622 (S175) — 「開工」→ startup reads + ① footnote 擴充 defer（Leonard「暫時看不到」）→ proactively 修其他可行項：手機首次導覽 tour（4 步 overlay + CSS，`k1_mobile_tour_v1` localStorage gate，tour→role picker 序列）+ checklist school_types 補標（curriculum 79 項 + kg_admission 16 項）+ DOC_SYNC 文件更新（CHANGELOG / PROJECT_MASTER_SPEC §B.5 / README）→ 收工。
3. Completed（詳見 SESSION_LOG S175）:
   - ✅ **手機首次導覽 onboarding tour**（`c714abe`，`mobile.js` + `mobile.css`）：4 步全螢幕 overlay（platform → search → guidelines → ready）；z-index 210 > role picker 200；`k1_mobile_tour_v1` localStorage gate；first-run 序列由直接 role picker 改為 tour → role picker。
   - ✅ **Checklist school_types 補標**（commits `839d741`、`02d9ca0`、`a3babce`）：curriculum 79 項（6 小學 rollout `['primary']` + 3 中小兼 `['primary','secondary']` + 70 pri_curr_guide_2024 `['primary']`）；kg_admission 16 項（k1_admission_2627 ×7 + kg_admin_guide ×9 → `['kindergarten']`）；`checklists_bundle.json` 重生（1573KB，15 域）。
   - ✅ **DOC_SYNC 文件更新**（`5cb978d`）：CHANGELOG 新 S175 章節；`dev/PROJECT_MASTER_SPEC.md §B.5` first-run 序列描述；`README.md` mobile 段加 onboarding 說明。
4. Pending: kg_operation 域 388 項全 KG-only（`kg_admin_guide_2026` 205 + `kg_operation_manual_2026` 183）仍無 `school_types`——大批次，待 Leonard 明確授權後再做。
5. Next priorities: ① footnote 擴充（待 Leonard 定）→ ② 文件標註精準度 monitor → ③ kg_operation school_types 補標（待授權）。
6. Risks: 🟢 HEAD==origin/main `5cb978d`（5 commits，已 push，tree clean，0 outstanding bug）。🟢 Supabase 15,363 零接觸；凍結合約 `_meta` 2.3.0·facts 455·guidelines 158 不變；PLATFORM_VERSION 3.2.1 不變。⚠️ kg_operation 388 項 untagged（待 Leonard 授權）。⚠️ Render free-tier cold-start ~50s + footnote cache restart（`invalidateWikiCache`）。⚠️ OpenAI node-fetch Premature close 復發 → Azure fallback。
7. commits（已 push origin/main）: `c714abe`(feat: mobile onboarding tour) → `839d741`(fix: 6 primary rollout items) → `02d9ca0`(fix: 3 primary+secondary items) → `a3babce`(fix: 70 pri_curr_guide_2024 + 16 kg_admission) → `5cb978d`(docs: CHANGELOG/README/PROJECT_MASTER_SPEC §B.5)。零 Supabase 改動。

## Previous Session Record (S174)
1. UTC date: 2026-06-21
2. Session ID: Claude_20260621_1200 (S174) — 「開工」探針全綠 → Leonard 指出 EDB 文件附件細字 footnote 藏住實質要求 → harvest 33 → Leonard /loop 批 A live 入庫（INSPECT+INSERT 15,363）→ 揭路由盲點 → 修 searchFootnotes 路由獨立 overlay → live 100% → 收工。
3. Completed（詳見 SESSION_LOG S174）: ✅ 附件細字 footnote 入庫（33 條 `footnote_curated`，15,330→**15,363**）；✅ 路由獨立 `searchFootnotes` overlay（繞 `sourceIds` post-filter + ivfflat probes=8 盲點）；✅ 敵意準確度 62%→75.8%→live 100%；✅ display-sync 15,363 ×8 + CHANGELOG。commits `8f2cace`→`9b3d8f9`。

## Previous Session Record (S173)
1. UTC date: 2026-06-18
2. Session ID: Claude_20260618_0839 (S173) — 「開工」起手探針全綠 → Leonard 畀真 .docx（博智小學免責聲明）做 NEXT ① 真檔收貨 → 驗保留格式+表格命中（合成表格補驗）→ 揭發 off-domain 強行配對 → Leonard 批「加相關性下限」→ guideline floor 0.62 → 揭發第二頭（domain 偵測同 over-fire）→ Leonard 批 domain floor 0.45 → bump v3.2.1 push → 部署觸發 Render OpenAI `Premature close` 生產事故 → 隔離（key 健康/問題喺 Render egress undici）→ Leonard 批 node-fetch + pin Node 22 修復 → live 全驗綠 → 收工。
3. Completed（詳見 SESSION_LOG S173）:
   - ✅ **真 .docx 收貨（NEXT ① 完成）**：保留格式 `buildCleanOriginalDocx` + 表格內段落命中 端到端驗（忠實 harness：真 mammoth 1.6.0 → 真 Render → 逐字抽出真 builder 離線跑；真檔無表 → 合成表格證 note 正確插入 `<w:tc>`；mammoth 每 cell `\n\n` → 逐 cell segment）。
   - ✅ **文件標註 off-domain 相關性下限 → v3.2.1**：`GUIDELINE_RELEVANCE_FLOOR=0.62`（指引比對）+ `DOMAIN_RELEVANCE_FLOOR=0.45`（範疇偵測）只喺 `annotateDocument.ts` 層、reused module byte-identical、手動選範疇不受影響 + `app.html`「未找到貼題指引」空狀態。本地端到端 + 多範疇零 regression（Render pre==Local post）+ live 驗綠（off `0/0/[]`、on `guideline=2`/`課程管理`）。
   - ✅ **生產事故修復（OpenAI 韌性）**：v3.2.1 部署觸發 Render undici 對每 OpenAI 呼叫 `Premature close`（stale keep-alive、restart 唔修、cache 0/455、全降級）；隔離為 Render egress undici keep-alive（key/code 由其他出口 200）→ 兩個 OpenAI client 注入共用 `sdkFetch`(node-fetch、每請求新連線) + pin Node `22.x`；local embedding/LLM 驗綠 + live 復原（cache_a warm 455）。
   - ✅ commits `78605bd`(floors+v3.2.1)→`f254d0c`(OpenAI 韌性) 全 push；Desktop 留 2 樣本 docx 俾 Leonard 睇成品。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: 文件標註精準度 monitor → EDB monitor-driven 入庫 → mobile onboarding。
6. Risks: 🟢 HEAD==origin/main `f254d0c`（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines 158）、Supabase 15,330 零接觸。⚠️ **OpenAI node-fetch 修復只 live 驗綠一次** —— 留意 `Premature close` 復發或 Node 22 有 issue（Azure swap = fallback；見 NEXT ⑧）。⚠️ Render free-tier cold-start ~50s + auto-deploy 偶爾卡（要手動 Deploy latest commit）。⚠️ per-segment 範疇偵測收斂單一 broad 範疇（既有偵測質素、monitor、NEXT ⑦）。
7. commits（已 push origin/main）: `78605bd`(v3.2.1：guideline+domain floor + 空狀態 + version bump)→`f254d0c`(OpenAI node-fetch sdkFetch + pin Node 22.x)+本 closeout commit。

## Previous Session Record (S172)
1. UTC date: 2026-06-17
2. Session ID: Claude_20260617_1731 (S172) — 「開工」起手探針全綠 → Leonard「1-3」batch（NEXT ①②③）→ 建 served-URL 監察 → 首跑揭發 2 條現存 404 → 授權即修（#1 re-point / #2 deprecate）→ band-aid cleanup → Leonard 真檔 PDF 收貨揭發精準度問題 → KG-tagging 修復 → CI 啟用驗證 → 收工。
3. Completed（詳見 SESSION_LOG S172）:
   - ✅ **served-URL 健康檢查（Method B 監察）**：`dev/source/check_served_urls.py` + `.github/workflows/served_url_check.yml`（self-test 21 PASS；CI run #1 conclusion=success、198/200/0 broken；每週一 11:00 UTC 自動跑生效）。
   - ✅ **2 條現存 user-facing 404 即修**：#1 `edbc12_2025_ph_pri` re-point（Supabase UPDATE 10 chunks → registry 200 URL、url-only）；#2 `sch_calendar_guide` deprecate（DELETE 6 + registry status→deprecated + hr_admin SOURCE_SET dead-ref 移除）。served-URL 重掃 **198/198 OK**。
   - ✅ **band-aid cleanup**：移除 app.html+mobile.js `SOURCE_URL_FIXUPS`（SAG store 已永久修好、verified no-op）。
   - ✅ **文件標註真檔收貨 + 精準度修復**：curriculum 76 KG-source 清單項（kgecg_2017+g29）tag `['kindergarten']` + 重生 bundle；live 驗 primary 580→504、KG 污染 0、課業項浮現、SAG p199 命中。
   - ✅ Supabase **15,336→15,330**（deprecate −6）+ display-sync 8 點；playbook proposal deposited（repo `8bccdbc`）。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: 真 .docx 收貨「保留格式」→ 文件標註精準度 monitor → EDB monitor-driven 入庫。
6. Risks: 🟢 HEAD==origin/main（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines 158）；display-sync 完整（chunks **15,330**）。⚠️ 文件標註 narrow×broad missing 噪音（非 KG、已修 KG 部分、monitor）+ 短 PDF 分段偏粗。⚠️ Render free-tier cold-start ~50s + auto-deploy 偶爾卡（要手動 Deploy latest commit）。
7. commits（已 push origin/main）: `4b68f97`(①②)→`b2ab8a2`(③)→`f38b511`(④)→`f1bafc6`(④ live)→`2626e8c`(CI 驗)+本 closeout commit。live Supabase PATCH(10)+DELETE(6)（Leonard 授權）。playbook repo `8bccdbc`。

## Previous Session Record (S171)
1. UTC date: 2026-06-17
2. Session ID: Claude_20260617_0911 (S171) — session 開喺頂層 umbrella root → Leonard「每次一開 session 都行 Draft」→ 設頂層 redirect-only → 重開通告分析入口 → DEBP 6 源入庫 + 路由 + 首頁更新日誌 → 指引庫正名數字教育 + 收錄 DEBP → 跨範疇 also_in → 收工。
3. Completed（詳見 SESSION_LOG S171）:
   - ✅ 頂層 umbrella root 設 **redirect-only**（非 git；頂層 `dev/SESSION_HANDOFF.md` + `START_NEXT_SESSION_PROMPT.txt` 指向 Draft，免再撞 onboarding 空殼）。
   - ✅ 重開「EDB 通告分析系統」入口連結（`index.html` 還原 S154 停用；URL 301→circular.wongfu.net 200 verified）。
   - ✅ **DEBP 6 源入庫 Channel B**：4 文字層（`fetch_extract`）+ 2 OCR（`ocr_extract` gpt-4o，draft 質、各 1 illegible region）→ canonical chunker（未改）→ 209 chunks → live INSERT（Leonard 授權「6 源全部入」、INSPECT before/after）→ Supabase **15,127→15,336**；新 `digital_education` route（`detectQueryCategory` 16/16、Render live DEBP query **8/8 全 debp_***）；registry +6=**225 源**。
   - ✅ 首頁「資料庫更新日誌」icon+modal（root `update_log.json`、XSS-safe DOM、dot=未讀最新）。
   - ✅ 指引文件庫分類「資訊科技」正名「數字教育」+ 收錄 DEBP 6 份（`build_guidelines.py` regen `guidelines.json` v2.5.0→**2.6.0**、公開 152→**158**、app 161→**167**、it/數字教育 1→7）。
   - ✅ 指引庫跨範疇 `also_in`（12 份多類顯示：SEN/資優→學生事務、校曆/g28→行政、DEBP→課程；科目安全 g21/g22/g23 **只課程**；全部 unique 不變、純 UI、下游契約零改）。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: served-URL 健康檢查 → band-aid cleanup → Leonard 真機/真檔收貨。
6. Risks: 🟢 HEAD==origin/main `e5053e8`（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455）；display-sync 完整（chunks 15,336 + guidelines 158）。⚠️ DEBP 2 OCR 補充 draft 質 + 主藍圖 ~16 圖像頁無文字層（monitor、命中可補 OCR）。⚠️ `digital_education` route 真查詢待觀察。⚠️ 監察 served-URL 盲點待補（NEXT ①）。⚠️ Render free-tier cold-start ~50s。
7. commits（已 push origin/main）: `972ab78`(重開入口)→`da33b8c`→`10bd47f`(route)→`9e51b6f`(DEBP+更新日誌+display-sync+registry+6 vault)→`4d0f3a6`→`beddcd8`(指引庫正名+DEBP 6 份)→`4b3985b`→`6488b44`(跨範疇 also_in)→`e5053e8`(治理)。Supabase live INSERT 209 chunks（Leonard 授權）。頂層 redirect 檔=本地非 git。

## Previous Session Record (S170)
1. UTC date: 2026-06-15
2. Session ID: Claude_20260615_2123 (S170) — 「開工」→ 起手探針全綠 → ④ Phase 0 唯讀爬取 → 監察 email 主題 → 揭發學校行政手冊 404 → 清訊號 + 404 兩層修 + v3.2.0 封版 + 收工。
3. Completed（詳見 SESSION_LOG S170）:
   - ✅ **① 監察清訊號**（`eb9d90b`）：freshness write-sync 重 seed 全 215 baseline（假警報 9→0、修 stub-baseline artifact：舊 1–3KB 殼頁 vs 新 multi-MB PDF + Last-Modified 倒退）；discover `ENUMERATION_PAGE_CAP=25`（likely-real 680→223、no-loss、self-test +3 PASS）。
   - ✅ **② 學校行政手冊 404 兩層修**（`59b8d2b` + Leonard Supabase UPDATE）：前端 `SOURCE_URL_FIXUPS` 改寫畸形 URL（app.html+mobile.js）+ Supabase 383 `sag_2025_11` chunks url index.html→SAG_C_markup.pdf（url-only、verified live API 回 `.pdf`）。根因 registry↔store drift、範圍 SAG-only。
   - ✅ **③ 平台 v3.2.0 正式版**（`6309333`）：PLATFORM_VERSION 3.1.0→3.2.0 + README badge/footer + CHANGELOG。凍結 knowledge.json `_meta` 2.3.0 不動。headless boot 驗 v3.2.0、無 stale 3.1.0。
   - ✅ **④ EDB 每週監察 email**：核實 GitHub Actions 真有跑（freshness 12 次、discover 今日首次）；Leonard 設好 Watch→Issues（#1/#2 每週一 email）。
   - ✅ **⑤ playbook 沉澱**（repo `7057db8`）+ **⑥ ④ 全入庫 triaged ＝無乾淨批次值得入 → monitor-driven on-demand**。
4. Pending: ① served-URL 健康檢查（404 盲點 follow-up）；② band-aid cleanup（Supabase 已修、可移除 `SOURCE_URL_FIXUPS`）；③ Leonard 真機/真檔收貨 S169 ①②③；④ EDB 入庫 monitor-driven。
5. Next priorities: 見 Open Priorities 頂部 🔜 NEXT 區塊。
6. Risks: 🟢 HEAD==origin/main `6309333`（已 push）。🟢 清訊號/版本/前端純改、零接觸 backend/凍結合約（_meta 2.3.0·facts 455·guidelines 152）；Supabase 只 SAG **url-only** UPDATE（chunk 數 15,127/_meta/display-sync 不變、非 count 變故無需 7 點同步）。⚠️ band-aid redundant-but-harmless（Supabase 已修、留住做雙保險）。⚠️ S169 ①②③ 仍待真機/真檔收貨。⚠️ 監察 served-URL 盲點待補（見 NEXT ①）。⚠️ Render free-tier cold-start ~50s。
7. commits（**已 push origin/main**）: `eb9d90b`(清訊號) → `59b8d2b`(404 band-aid) → `6309333`(v3.2.0 release) → `5186d0f`(收工治理) → `0ff1925`(RAG 架構圖入庫) → `35458c7`(README ASCII truth-pass)。playbook repo `7057db8`。Supabase：Leonard UPDATE 383 `sag_2025_11` url（verified live）。

## Previous Session Record (S169)
1. UTC: 2026-06-15 | Claude_20260615_S169
2. 文件標註乾淨成品版「保留格式」+改動摘要（`2150f59`）+ onboarding 6 步導覽（`12f33fb`）+ in-app 使用手冊+FAQ（`12f33fb`）+ dead-code cleanup app.html −464（`967dd7d`）。純前端、Node builder 32/0 + headless boot 驗；QC PASS-with-flags（no blocker）。詳見 SESSION_LOG S169。

## Previous Session Record (S161)
1. UTC date: 2026-06-14
2. Session ID: Claude_20260614_S161 (S161) — 全權自主
3. Completed: 「文件標註」合併主線 Phase 1 SHIPPED LIVE（合併 文件分析+文件修訂 → 📝 文件標註 tab；新 annotateDocument.ts + /api/annotate-document；app.html AnnotatePanel + buildAnnotatedOriginalDocx〔JSZip highlight + w:ins 追蹤修訂 + 附錄 + header〕）+ Leonard 真檔 4 輪反饋全修。commits `6885dbe`→`9b1f6a5`+gov 全 push。詳見 SESSION_LOG/archive。

## Previous Session Record (S160)
1. UTC date: 2026-06-14
2. Session ID: Claude_20260614_S160 (S160) — 通宵自主（Leonard 授權 agent teams/workflow、留 token buffer）
3. Completed（詳見 SESSION_LOG S160）:
   - ✅ **P2 政策範本下載 tab**（`fcccc34`，**LIVE**）：app.html +TemplatesPanel +'templates'；`policy_templates.json`（14 域 102 docx）；連現有 live docx；browser-verify 102 連結 / 校類 filter / fetch 200。
   - ✅ **P3 文件修訂 feature**（`bd99b91`，**LIVE**）：backend `checklistRevise.ts`（embedding coverage + clause supplement，無 LLM）+ `/api/checklist-revise` + `/api/checklist-domains`；`checklists_bundle.json`（root，14 域）；app.html +ReviewPanel +'review' +buildRevisedDocx。onrender live e2e PASS（14 域 / 真實報告 / CORS）。
   - ✅ **#2 幼稚園 Phase 2 KG LIVE 入庫**（Leonard sign-off supervised，`1bf497c`）：INSPECT→live INSERT `kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks** → Supabase 14,674→**15,109**（per-source 218/217 驗）；新 `kg_admin` route（擺 curriculum 前；route 7/7 + 本機 routed smoke 命中新源 p1/p78、收生無回歸）；display-sync ×7 →15,109（live Pages 驗）；registry 216→218。
4. Pending: **#2 收尾**（verify Render KG 路由 deploy `1bf497c` propagating — 本機已綠）+ **幼稚園清單 pilot**（用新 2 源起 KG checklist→docx→manifest）；#3 docx review；文件修訂 Phase 2.5。
5. Next priorities: KG 路由 deploy verify + 清單 pilot → #3 review → Phase 2.5。
6. Risks: 🟢 HEAD==origin/main（已 push）。⚠️ Render KG 路由 deploy 仍 propagating（本機 routed smoke 已實證正確；live「學前機構辦學手冊」未 flip = 慢 deploy，非 build fail — tsc build PASS）。`kg_admin`「幼稚園質素」query 命中 qa_inspection（minor mis-route、acceptable）。覆蓋門檻估算（tunable）。
7. commits（**已 push origin/main**）: `fcccc34`(P2)→`bd99b91`(P3)→deploy gov→`1bf497c`(KG 入庫)→收尾 gov。
   - QC：P2 browser-verify 全綠；P3 e2e（match 198/10/0 vs 1/5/202、400）+ onrender live；KG = INSPECT + 2×live INSERT(218/217) + route 7/7 + 本機 routed smoke(p1/p78、收生無回歸) + tsc/build + display-sync live 驗。

## Previous Session Record (S155)
1. UTC date: 2026-06-11/13
2. Session ID: Claude_20260613_0900 (S155)
3. Completed:
   - ✅ **任務①** PAGE_COVERAGE_REPORT.md（207 源/14,505 chunks）
   - ✅ **任務②** 14 範疇 × 2 docx = 28 files 全部生成
   - ✅ **Git commit 122a7b9**（804 files）→ **4e496a2**（closeout）— **已 push** (68fe43d..4e496a2 → origin/main)

## Previous Session Record (S154)
1. UTC date: 2026-06-10
2. Session ID: Claude_20260610_0100 (S154)
3. Completed:
   - ✅ **[起手核實 全 live]** HEAD `8bf828d`==origin/main clean / facts 455 三層(md5 4c3631) / Supabase 14,276(content-range 0-999/14276) / guidelines 152 / knowledge.json stats 14,276·152 / onrender /health 200 + manifest 401。
   - ✅ **[NEW 文件分析 — scope]** Leonard 揀「新功能」並定義：用戶上載學校文件 → 系統加上相關指引資料 → 輸回上傳者。AskUserQuestion 釘實：格式 PDF(文字層)/docx/貼文字（無 OCR）；Phase 1 螢幕報告、Phase 2 目標可下載標註文件；私隱 = hybrid（client 抽取、原始檔不上載；文字→server→OpenAI、stateless、可見私隱提示）。**OpenAI 香港封鎖疑慮已核實**：用戶唔受影響（egress = Render 美國 IP；只 browser-direct / HK-hosted backend 先中招）；Azure OpenAI = 有界 fallback（llmClient+embeddingClient swap）。
   - ✅ **[Backend]** NEW `analyzeDocument.ts`（分段：空行段落 + <30 字 stub 前併 + >1,200 字句界切；每段經 `searchChannelB` 公開 API synthesize:false top_k=4 併發 4 — **shared 檢索 infra 零修改**；一次 LLM 提示 call "N: …" best-effort；60k 字/12 段 cap；stateless）。`server.ts` 新 route 喺 10/min limiter 後 + `readJsonBody` optional `maxBytes`（淨新 route 用 ~244KB cap→413；**QC 捉到並修咗 RST-before-413 bug**〔drain 唔好 destroy〕；現有 route byte-identical）。
   - ✅ **[Frontend app.html]** +pdf.js 3.11.174 / mammoth 1.6.0 CDN（**3.x UMD 特登 — 4.x ESM-only 唔啱 no-build 頁**；URL curl-200 驗證）；`AnalyzePanel`（檔案/貼文字、runtime 庫 guard、私隱提示、逐段報告卡 `url#page=N` + noopener noreferrer + **https-only href allowlist**〔對抗覆核 flag 修正〕）；VALID_VIEWS/tab/router +'analyze'。**mobile.js 零接觸**（平板 shell = Phase 1.5）。
   - ✅ **[QC 文件分析]** typecheck+build exit 0；unit smoke segmentText/parseNotes（**MIN_SEGMENT_CHARS 60→30**：中文通告段落 40–80 字要企得住獨立段）；**local live e2e**（:8123 真 Supabase+OpenAI）：3 段樣本通告 → 遊學團→`sch_activities_guide` p91 / 採購→`g01` p7 / 校車→`g18` p2-3 全帶頁、9.7s warm；錯誤路徑 400 空/400 過長/413 oversize；現有 channel-b endpoint 零回歸；semantic regression PASS=9+notes=1+**既知 2 FAIL 0 新增**；browser-verify（preview fetch-stub）10/10（頁碼 link/無分數/fail-visible/4 tab 回歸/真 pdf.js worker 頁內抽取）；**對抗覆核 subagent VERDICT PASS-with-flags 0 critical**（flag 1 href allowlist 已修 + 重驗 `javascript:` URL 降純文字；flags 2-6 non-blocking 記錄於 SESSION_LOG）。
   - ✅ **[NEW IMC/SBM 校董會治理入庫 +229]** Leonard：「指引欠校董會治理本體」+ 5 條 sbm.edb.gov.hk URL（3 加入 / 2 Monitor）。Crawl references 子頁 enumerate → pre-flight 12 PDF 全 TEXT-OK（U+FFFD=0、page-resolvable）→ **4 源拆法**（兩份大文件獨立=頁碼全對，兩組細 fragment 分組；避免 grouped 連續頁碼 overshoot）→ live ingest Supabase 14,276→**14,505**（97+48+27+57）。**新 `school_governance` route 擺 finance 前**（SOURCE_SET 連 g02+coa_imc_1_19+sdp_guide）；registry 212→216；display sync 7 處 14,505（三層 md5 4c3631→`1bf7fd` byte-identical、facts 455/guidelines 152 不變、無 bump）。**2 個 Monitor index 頁已在 discover watch-list（coa_imc_1_19 + sag/g24 url_landing）— 已 cover、無需改動。** QC：typecheck/build PASS、routed smoke 4/4 治理查詢 surface 帶正確頁碼 + 採購/招標 留 finance（唔被偷）、regression 0 新 FAIL、對抗覆核 PASS-with-flags 0 critical（12-query regex trace 確認零誤偷）、post-deploy onrender 治理 synthesis 373 字 + policychecker.wongfu.net 顯示 14,505。
   - ✅ **[Cloudflare 統計]** Leonard 畀 token → 4 公開 HTML（index/app/q/t-purchase）裝 cookieless beacon + index/app footer 私隱細字；Playbook analytics-minors-cookieless 卡（私隱優先、唔用 GA4）；§0b 核實官方 setup/limits + beacon URL curl-200；browser-verify **執行級**（app+index 都見 RUM POST 去 cloudflareinsights.com/cdn-cgi/rum）+ 0 console error；External Services block 記錄「+1 對外 runtime 服務」架構轉變。報表：Cloudflare dashboard → Web Analytics。
   - ✅ **[通告分析入口暫停]** Leonard：「button 保留、link 失效」→ index.html「進入 EDB 通告分析系統」button → 停用 `<span>`（暫停開放字樣 + opacity .55 + not-allowed；原 `<a>` 連 URL 留 comment 恢復用）；app.html intro 卡 `externalLink` comment 掉（本身係 dead data — channels.map 從未 render 過佢）。驗證：兩 surface 零活鏈、卡片照 render、0 console error。註：原 link 其實 301→circular.wongfu.net 200（非 404）— 照指示停用、下游點解唔深究（§A.3）。
4. Pending: 文件分析 Phase 1.5（mobile shell）/ Phase 2（可下載標註文件）；IMC grouped-源頁碼 overshoot = monitor（見 Open Priorities #4）。**0 outstanding bug。**
5. Next priorities: 見 Open Priorities。
6. Risks / blockers:
   - 🟢 **0 outstanding bug**。
   - ⚠️ **文件分析私隱姿態**：原始檔永不上載，但抽取文字會經 server→OpenAI（stateless、有可見提示）。任何改動呢個 data flow 必須同步改 UI 私隱文案。
   - ⚠️ **LLM 逐段提示 = best-effort**（e2e 3 段得 2 段有 note；缺 note 唔影響 matches 核心交付）= monitor。
   - ⚠️ app.html 兩個搜尋 UI（React desktop + mobile.js shell）：政策搜尋結果渲染改動必須兩邊都改；**文件分析目前淨 desktop React**（mobile shell 未有入口 = 已知 scope，非 bug）。
   - 既有：synthesis ~328 字 soft cap / cgss_2024 rank 低 / admin 永久移除（重建走 §3+真 server-auth）/ Channel A frozen @455 / 入庫 display sync 7 處 / 新源必加 SOURCE_SETS+registry / 57014 cold-start / Stage-2 closed / 路徑空格雙引號 / commit 必入 SESSION_LOG / 勿改 canonical chunker / stats.sources=120 cosmetic-stale。
7. commits: `a6547c6`(文件分析 code) → `d17c25d`(governance) → `46376f4`(IMC 入庫) → `60da7f0`(governance) → `37995bc`(Cloudflare ×4) → `36af538`(governance) → `0c34611`(入口停用) → `db4fe12`(governance) → 收工 closeout commit。


## Detail Archive (S212–S214)

> S215 收工搬遷。以下兩節是 S212–S214 期間累積的 `Current Baseline` 與 `Open Priorities` 原文，**逐字保留、零刪減**，只因 AGENTS §4 的 compactness budget（Current Baseline 6 行、Open Priorities 5 項）而由當前狀態區移到此處。查歷史成因請讀這裏，查**現況**請一律讀上方 `## Current Baseline`。

<details>
<summary>舊 Current Baseline 全文（S212–S214）</summary>

> **2026-09-07 啟動離線覆核更正：** 已找到 `2026-09-07_s214_route_first_focused.json`，其 trace 記錄新 RPC 成功及三題 before／after，故下文「RPC 未安裝／未跑 focused」已不能當作現況。現在 live 定義、安裝授權及生產 flag 未驗，不得直接重做 DDL。三題仍缺完整目標答案；特殊學校曾 57014，after 整題 16.7 秒。下一步先離線查 query expansion／排名，不立即擴大至 185 題付費批次。詳見 `dev/_s214_route_first_focused_review.md`。

> **🆕 S214 Codex continuation（2026-09-05 至 09-06，本機候選）—— grounded synthesis 已實作但預設關閉。** 新增 strict Structured Outputs、逐項 claim、NFKC／空白正規化逐字引文核對、輸出衞生閘、獨立 judge 與 fail-closed 路徑；`FEATURE_EXACT_WINDOW_NARROW=0`、`FEATURE_GROUNDED_SYNTHESIS=0`。生產及 probe 現共用先篩一手文件再取五格的 `selectPrimaryEvidence()`；離線回歸 **48/48 PASS**，typecheck／build／route regression 46/46／排序模型均通過。semantic regression 唯一 FAIL 是既有 `guidelines 2.5.0` 測試常數與權威 2.6.1 的漂移，與本次 helper 無關。兩批 40 題 acceptance 其後證實有 18／40 題受舊 harness 選窗次序影響，故不可直接作 release 判決；候選維持 FAIL。未 commit、未 push、未 deploy。
>
> **外部模型操作邊界：** Claude 只可用 Claude Code CLI 的 Plan 額度，不得使用 API key／SDK。Codex 已按兩次明確批准完成兩批固定 40 題 OpenAI probe；第二批使用 54/80 次 HTTP 嘗試，批准已隨該批結束，不可挪用餘額。任何新批次仍須先列明服務、模型、案例範圍及最高 HTTP 次數，再取得 Leonard 明確批准；目前只執行離線工作。
>
> **S214 grounded acceptance V3：候選仍為 FAIL，不可啟用。** 修正選窗後已按 Leonard 明確批准重驗受影響 18 題，OpenAI Responses API 實錄 **25／36 次 HTTP**（18 draft＋7 judge，`maxRetries=0`）。不可答題 **9／9 全部棄權、0 個錯答**；可答題 **6／9 作答、3／9 棄權**。人工覆核為 4 個完整 PASS、2 個安全但不完整、3 個棄權／證據不足；未再出現 audience 錯答、OCR 重複或截斷。這證明安全性有改善，但完整性仍未達 release 標準。下一 gate 是為兩條新 NCS replacement 及 `gov_imc_60pct`、`hr_lsp`、`sen_special_school_curriculum` 建立新鮮檢索證據，再針對 `hr_lang_req`、`saf_disease_notification` 的完整性做回歸。完整證據見 `dev/_s214_grounded_acceptance_report.md`、`dev/_s214_grounded_v3_review.md`、`dev/_s214_gold_abstention_review.md` 及 V3 artifact。
>
> **S214 五題 fresh retrieval：2 PASS／1 PARTIAL／2 FAIL。** 中文第二語言框架及校董 60% 一手原文進首 5；長期服務金只有部分註釋；特殊學校 `g10` 及非華語中史目標未進首 8。查實 `chi_hist_jss_ncs_2019` 已入庫但漏 `SOURCE_SETS.curriculum`，已作最小 allowlist 修正並加回歸；候選單題驗證令來源升至 rank 0／1／3，但目標第 17 頁片段仍未進首 8，故只修好 Source Recall，Chunk Recall 仍 FAIL。`g10` 已在正確 route，未作猜測式 spotlight。另更正 `gov_imc_60pct` gold 的錯亂 signature、頁碼 21→4 及 chunk id。沒有 commit、push、deploy 或 Supabase 寫入。
>
> **S214 Phase B route-first 候選已備，預設關閉，尚未 live 驗證。** 離線反例支持「SQL 先按 route allowlist 過濾，再精確向量排序」，不支持 lexical 單獨主排名。已新增獨立 `match_wiki_chunks_routed`、`searchWikiRoutedExact` 及 `FEATURE_ROUTE_FIRST_SEARCH=0`；舊 RPC 不變，失敗回退舊 ANN，共用 embedding，並有三次限定 `57014` 重試。Claude Code CLI 唯讀覆核為 PASS-with-flags、無 code blocker；本地 typecheck／build／grounded 48/48／route 46/46／retry mock／diff check 全綠。**RPC 未安裝、未跑 live 185 題 before／after，因此不得聲稱檢索已提升，產品 verdict 仍 FAIL。** 下一步需 Leonard 明確批准 Supabase schema 寫入後才可安裝及驗證；不得自行 deploy。

> **🆕 S214（2026-09-04 → 09-05，跨午夜）—— Phase 1.1 完成、Gate 1 根因定案、Gate 2A1 測試基建落成，並已改動一個生產檔但未提交未部署。** 起手探針全綠：`app.html` 200 ／ `PLATFORM_VERSION 3.3.2`；Supabase **17,602** 不變；`source_registry` 279 不變；`guidelines.json` `_meta` 2.6.1 不變；凍結合約零接觸。`HEAD == origin/main == 05ea10e`，**本節零 commit、零 push、零 deploy、零 Supabase 寫入、零重切語料**。
>
> 🔴 **最重要一項：`backend/src/api/searchChannelB.ts` 有未提交改動（+31 −21），已通過 `npm run check`，但未跑 184 題 live 套件、未部署。** 線上仍行舊 build（`/health` commit `f513a18`）。這是本交接最高風險項，下一節開工必須先處置，見 Open Priorities ①。
>
> **① Phase 1.1 五項全部完成**（詳見 `dev/_s214_phase_1_1_report.md`）：A canonical 評測器 NFKC 修正（self-test ALL PASS；39 條 live run PASS 27／FAIL 0／errors 0，與 S213 凍結基線比對無 blocking failure）；B 棄權機制實測（19 條無答案題 13 條標準棄權，19 條正向對照 2 條誤拒答）；C forbidden 實際影響（4/4 進首五格，**僅 1/4 可證答案實際採用並造成對象混淆**）；D 排序反事實（**全域 score sort 有害，已否決**）；E Gold Set 補至 **184 條全通過 validator**。
>
> **② Gate 1 根因定案（唯讀）**：`searchChannelB.ts:1495` 的 `[...lead, ...rest]` 無條件前置註腳 lead，資格只看絕對門檻（0.45 ＋ 2 bigram），**從不與被壓者比分**。設計意圖（`:1146` 寫明「reaches the synthesis window (top-5)」＝成員資格）與實作（index 0 ＝位置）不符，此落差即根因。實證：**全 162 題僅 3 條有 exact 1.0，三條全部被 0.48–0.52 的註腳壓住**，其中兩條壓在頂的是《幼稚園營運手冊》而問題問小學編制。九題探針 8/9 出現高分被壓，合成窗平均 **2.22/5 格（44%）** 由 overlay 佔據。
>
> **③ Gate 2A1 測試基建落成**：`dev/_s214_rank_model.py`（CURRENT／PROPOSED 純模型 ＋ T1–T14，**41 條斷言 ALL PASS**）、`dev/_s214_gate2a1_replay.py`（離線 replay）、`dev/source/footnote_lead_probe.py` 擴充為記錄完整 top-8 `window`（self-test PASS）。43 條 live probe 已跑完（**正向 30/30 保住 lead**，errors 0）。**fidelity 由 174/184 升至 180/184** —— 修好一個我自己的判別 bug：spotlight 偵測原本只看來源是否在 `SPOTLIGHT_SOURCE_IDS`，但 `staff_est_pri`／`edbcm116_2026` 本身憑分數就攞第一，令 184 條之中誤判 6 條並靜靜丟失一個 chunk；改為必須同時違反分數次序後修正。
>
> **④ 餘下 4 條 fidelity 不一致，成因已查清、未修**：3 條係**分數完全相同**（如兩個 0.7284），生產的 tie 次序不是 id 升序，而模型用 id 升序（為 T2 決定性）——**生產真正的 tie 規則未查證，不得憑猜**；1 條 `fin_seg` 係 `edbc015_2026` 排在 5 個更高分項目之前，與 Gate 1 揪到的 `edu_sen_lsg_outsource` **同一來源、同一病徵，仍未解釋**。
>
> **⑤ Gate 2A2／2A2b 已改生產程式碼**（證據見 `dev/_s214_gate2a2_implementation_report.md`）：落地 EXACT-ONLY 變體後，Codex 用 local backend 跑 `staff_fullday_24` 做行為 QC 揪出真缺陷 —— exact chunk 已由 ANN 在 rank 2 出現，舊 `seenIds` 過濾把 score=1 版本篩走，令合成答案講「大約40」而 exact 那行明文寫住 40。修正三處：dedup 方向對調、`mainSearchLead` 在 overlay 前明確擷取（`undefined` 時 fail closed）、`forcedLeads` 只用於插入定位不再用於 judge bypass。
>
> ⚠️ **本節有部分回合已不在 agent 上下文內（機器休眠 ＋ context 壓縮），檔案逐行歸屬無法可靠重建。** 以磁碟上兩份報告為權威記錄，不要憑 mtime 推論作者。

> **🔙 S213（2026-09-04）—— 為檢索準確度建可信基線；順帶揪出 658 條代號標題的單一根因。零生產寫入、零 deploy、零重切。** HEAD==origin/main @ `05ea10e`；**Supabase 17,602 不變**；`source_registry` 279 不變；`GUIDELINES_REGISTRY` 177 不變；平台 v3.3.2 不變；凍結合約零接觸（`_meta` 2.3.0 · facts 455 · `guidelines.json` 2.6.1 · 158）。⚠️ **工作區有未提交改動，開工先按下方分類處理，勿混合提交、勿還原。** **① 舊 eval 的「PASS 27/39」用準確度語言講就是 Source Recall@8 = 1.000，而且恆真** —— `verdict_for()` 在預期來源出現於窗內任何位置就判 PASS，rank 0 與 rank 7 同分，39 條之中 12 條完全無斷言、37 條對段落零斷言。它是回歸偵測器，不是準確度量度。**② 新建 162 條 gold set 量出真實水平：Source Recall@1/@3/@5/@8 = 0.364/0.552/0.636/0.706（MRR 0.474）；Chunk Recall@1/@3/@5 = 0.119/0.245/0.273（MRR 0.184）。143 條可答題之中 42 條在 8 格內完全搵唔到正確來源。** dev 0.340／held-out 0.419（@1），未見過擬合。**③ OP⑦ 根因查實，不是「要跑一次 UPDATE」**：`dev/vault/build_wiki_index.py:267-268` 的靜默 fallback —— extract 缺 `# title:` 就拿 source_id 頂替、缺 `# url:` 就留空。集合相等已證（庫內代號標題 19 個 source_id ／ extract 缺 header 19 個 ／ 交集 19 ／ 兩邊獨有各 0），同一行代碼同時製造 `SOURCE_TITLE_REAL`(658) 與 `ANCHOR_URL_PRESENT` 的無連結片段。**源頭已封死**（19 個 extract 補回 header，逐檔斷言正文位元組不變故 hash 不動；守門改 fail loud 並證明會紅），**生產庫 658 條未動**。**④ 兩個新語料缺陷**：CJK 相容表意文字 868 條 chunk（4.93%／112 源／110 個變體字，例：理 U+F9E4 而非 U+7406）—— **現行 `eval_retrieval.chunk_verdict_for` 無 NFKC folding，目標段落落在這 868 條時正確檢索會被判 FAIL**；header 剝除正則吃掉正文 `# ` 開頭行，16 個來源、33 行真正消失（實例：`g24` 一行強制舉報懷疑虐兒的交叉引用）。**⑤ 60/162 結果不是分數遞減排列，該 60 條位 0 全部是 `footnote_curated`**，該組 Recall@1 0.308、其餘 0.396 —— **此為相關性，未證因果**。**⑥ 產品 verdict = FAIL（Chunk Recall@5 = 0.273）；工具 verdict = Phase 1 完成。兩項必須分開講。** QC Governor 暫不批准直接改生產，NEXT 為 Phase 1.1 A–E。

> **🆕 S212（2026-09-03）—— 由三個文檔漂移開始，交付咗一張公開品質檢查頁；期間自己整停咗生產搜尋。** HEAD==origin/main；**Supabase 17,597 → 17,602**（`phys_sss_2007_2015` 182→0→187，OCR 重抽）；`source_registry` 279 不變；`GUIDELINES_REGISTRY` 177 不變；平台 v3.3.2 不變；凍結合約零接觸（`_meta` 2.3.0 · facts 455 · `guidelines.json` 2.6.1 · 158）。**① 新交付：公開品質檢查頁 `https://policychecker.wongfu.net/status-07cc7942c0.html`**（不設任何入站連結，同通告系統嗰張同一契約）＋ `qc_report.json` ＋ `.github/workflows/qc_report.yml`（每日 12:00 UTC 自己重生兼 commit）。21 項檢查按四條問題分組：政策指唔指得清楚／片段合唔合標準／有冇切得太碎或太粗／質素量唔量得到。**門檻用基準值不用零，而且等於基準報 WARN 不報 PASS** —— 仍在服務中嘅缺陷唔係綠燈。**② 封版閘（`dev/source/release_gate.json`）**：未有 waiver 嘅 WARN 一律 NOT_MET（預設係擋，waiver 要 owner／reason／`accept_until`，過期自動失效）；六項人手檢查冇日期簽核係 NOT_MET 唔係「不存在」；`NOT_MEASURED` 等於 NOT_MET。**出廠 7/15 FAIL，係真實狀態，我冇替 Leonard 填 owner 令佢變綠。** **③ 第一次跑就揪出四件從未量化過嘅事**：658 條片段以內部代號做標題（用戶喺答案見到 `stat_enrolment_2014`）；956 組逐字重複／多出 980 條（**全部跨來源、同源內 0，即問題喺登記兩次，唔喺切片器**）；835 條由半句開始；130 條全無連結。**④ `phys_sss_2007_2015` 由 165/182 不可讀變 187 條亂碼 0**：原 PDF 嘅 ToUnicode CMap 壞咗，`pdftotext` 抽出同樣亂碼，所以**重抽文字層冇用**；亂碼可以純算術還原（三個固定偏移、98.4%）但**冇採用** —— 交叉核對見到「二零一五年十一月」被還原成八個似是而非嘅漢字，即靜靜錯。改用 `dev/ocr_extract.py`（S147 為此 failure mode 而建）。順帶修好舊 extract 漏咗真空白第 2 頁、導致之後每個頁碼標記都少 1。**⑤ 我整停咗生產搜尋約半小時**：先刪 182 條，之後先發現額度被同一 session 嘅 150 頁 OCR 耗盡，全站查詢 429，而 `/health` 由頭到尾報 `ok:true`（佢只驗 Channel A 快取）。已變成兩道閘：DOC_SYNC row 54「先驗入得到再刪」，同 `qc_report` 新增 `SEARCH_PIPELINE_LIVE`（BLOCKER，直接打生產查詢端點，429／零結果／無回應都要紅）。

> **🆕 S210（2026-08-26）—— 補返 S209 欠嘅 eval，證實零退步；順手發現量度佢嘅閘本身壞咗：** HEAD==origin/main；**Supabase 17,568 → 17,576**（開工先 `--ff-only` 收咗隔夜 Option A 入庫 `edbcm156_2026` +17，再 +4 g04 重切、+4 三摺頁）；`source_registry` 275 → **276**；`GUIDELINES_REGISTRY` **177 不變**；平台 **v3.3.0 不變**；**凍結合約（`_meta` 2.3.0 · facts 455 · `guidelines.json` 2.6.1 · 158）全部零接觸**。起手探針 5/5 綠（served 3.3.0 / `/health` warm 455 / HEAD 對齊 / count=exact / 無頁碼數）。① **OP⑥ 結案 —— 補跑咗，零退步。** S209 動過切 chunk 邏輯同加咗兩個源但冇跑 eval；今次補跑對 `2026-08-19_s207_after.json`，PASS=23/FAIL=0/errors=0。compare 報 5 blocking，**逐條拆完冇一條係退步**：1 條 ERROR 錯喺**基線檔**（S207 嗰次 `nonlocal` 撞 Supabase 57014 timeout，0 個源；今次答得正常），4 條 SET_LOST 全部係自動管道新入庫嘅通函擠入 top_k=8、撞跌最尾位（掉低嗰個 before 排 [7]/[7]/[7]/[6]，verdict 一個都冇變）。② **量度嘅閘本身壞咗，已修。** harness 當「新源入 top_k」無害（SET_ADDED 非 blocking）但當同一件事撞跌尾位係 blocking —— 固定 top_k 之下呢係一件事嘅兩個講法。Option A 每日入庫兼自己 push，即係**呢個閘由今日起會朝朝紅**（紀律 #14 嗰種必然變牆紙嘅閘）。新增 `DISPLACED`：有新入者 + 掉低嗰啲全部喺 cut line 以下 + after 唔短過 before 先降級，否則照 SET_LOST。③ **開工探針 +10 無頁碼 = S209 修好嘢，唔係退步。** 461 條入面新增嗰 10 條全部係 `gifted_policy_docs`；用 S207 版 vs S209 版 `carry_pages` 跑同一份 extract 對證，**10 條全部由「Page 8」變 None**。嗰份 PDF 得 8 頁，而 10 條入面 9 條係 extract 尾嘅網頁段落（`=== introduction === / === detail ===`，本身冇頁碼），舊邏輯一路 carry 落去 = 叫用戶揭第 8 頁搵一段網頁文字。**交接寫嘅「10/23 有缺陷等修」要反轉理解。** ④ **`split_on_section_markers` 個 gate 由 registry 改為 extract 判。** S209 gate 喺 `source_section_urls(sid)`，但橫跨係文字嘅屬性 —— 有 `=== label ===` 就跨得，同 registry 有冇 per-section URL 無關。兩個源一直喺閘外：`gifted_policy_docs`（一條 chunk 揸住 page 8 尾 + `=== introduction ===` 頭）同 `g04`。261 個 vault 源逐個對 chunk 內容 hash：**259 byte 級 no-op**，只有 g04（7→11）同 gifted（23→23）變；重入後**跨界 chunk g04 5→0、gifted 2→0**（live 實查）。⑤ **eval 集補咗保安／雲端三條**（34→37）：`cyber_campaign`「網絡安全運動」→g28 rank 0–2、`cloud_privacy`「雲端運算 私隱」→pcpd rank 0–2、`info_security_broad`「學校資訊保安」RECORD_ONLY（OP⑥ 撬點）。**三條全部入檔前 live 實測過先寫 `expect_any`。** 之前 34 條**一條都冇掂過** S209 兩個新源。⑥ **三摺頁入咗庫但贏唔到**（Leonard 指示入）：4 chunks。「創新型終身學習者」rank 6 → 搜得到、**唔係 route 擋**；但「四大發展重點」（**全庫只有佢一條**有呢詞）**rank=None**，輸畀無關課程文件 @0.538。成因係佢係資訊圖，chunk 係三十幾個互不相連嘅圖標籤，撐唔起 embedding 方向。caveat 已寫死入 registry notes。**唔建議加入 `digital_education` SOURCE_SET**（入咗只會同更強兼已 routed 嘅 `debp_blueprint` 爭位）。⑦ **全 session 檢索淨影響**（`baseline37 → after_leaflet`）：SET_LOST 1 / SET_ADDED 1 / RANK_SHIFT 2 / SCORE_MOVED 1 / SAME 32。唯一 blocking 係 `pay_adjust` 掉低 `edbcm135_2026`（尾位）—— **成因係 g04 切細後多佔一個 top-k 位，係切細嘅真實代價，唔係雜訊**（verdict 仍 PASS，等緊嘅 `edbcm094_2026` 仍 rank 1）。呢條**冇被 DISPLACED 吸收**，因為 g04 本身已喺 before 名單、`added` 係空 —— 呢個邊界係**刻意保留**：SET_LOST 意思係「本來搵到嘅源而家完全搵唔到」，呢個情況確實係。

> **🆕 S209（2026-08-24）—— 只入唔出嘅清單、一個永久偏差、四條死連結，同兩個新源：** HEAD==origin/main；**Supabase 17,473 → 17,551**；`source_registry` 268 → **274**（+3 Option A 自動入庫、+`pcpd_cloud_computing`，另 g28 由空殼變 40 chunks）；`GUIDELINES_REGISTRY` 177 不變；平台 **v3.3.0** 不變；**凍結合約（`_meta` 2.3.0 · facts 455 · `guidelines.json` 2.6.1 · 158）全部零接觸**。① **OP⑥ 結案 —— 前提本身錯**：`check_served_urls.py` 由 S172 出世就只掃 `wiki_chunks.url`，per-chunk deep link 一入庫已受每週監察（四重實測 + 紅測，見 Regression 第 5 條）。真缺口係 `--fetch` 得散文擋 → 已補 `refetch_blocked` 機制閘。② **第 6 監察上線**：`lifecycle.py` 三分類（reference 永不掃 / dated_edition 標示唔刪，即 S204 定案 / ephemeral 到期清走）+ `check_expiry.py` + ops `expiry-issue.yml` 剔一剔清走。③ **公開片段數以前係流水帳唔係真數**（純加法、從來冇對過 store，長期少 1）→ 改為由 Supabase 讀真總數。④ **4 條 404 清晒**：2 條 re-point、2 條（13 chunks）過期試場文件退役。⑤ **兩個新源**：`g28` 學校資訊保安 40 chunks（7/41 份文件）、`pcpd_cloud_computing` PCPD 雲端運算指引 26 chunks（registry 第一個 `authority != edb`）。⑥ **實測定案：EDB 冇「學校使用雲端服務指引」** —— g28 八份實質文件「雲」/「cloud」共 0 次，EDB 資訊保安頁亦 0 次。⑦ **三個自己整出嚟嘅錯已修並記低**（chunk 跨文件污染頁碼、報咗個估返嚟嘅 URL 嘅 404、用闊 phrasing 誤判要加 spotlight）。⚠️ **本 session 未行 `eval_retrieval.py` before→after** —— 動咗切 chunk 邏輯同加咗兩個源，按紀律 #5 呢個係已知欠賬。

> **🔙 S208（2026-08-20）—— 純溝通交付：五個月里程碑回顧 + 三張分享圖（零 code / 零資料改動）：** HEAD==origin/main；**Supabase 17,473 / `source_registry` 268 / `GUIDELINES_REGISTRY` 177 / 平台 v3.3.0 / 凍結合約（`_meta` 2.3.0 · facts 455 · `guidelines.json` 2.6.1 · 158）全部零接觸**，開工五項探針（served v3.3.0、Render `/health` warm 455、HEAD==origin/main、chunk=17,473、無頁碼=451）**全綠、逐項實測**。① Leonard 要準備對外分享，要一份由最初痛點講到今日嘅里程碑回顧。挖咗 **578 個 commit + S1–S207**（含 `dev/archive/SESSION_LOG_2026_Q1~Q3.md` 共 14,196 行）+ PMS + PROJECT_DECISIONS，出 `dev/PROJECT_MILESTONES_REVIEW.md`（六階段敘事 / 數字弧線 / 功能生死簿 / 11 條紀律）。② 敘事定調：**核心轉捩點係 S119 —— Leonard 親手實測五條 query 後裁定「原文搜尋贏、人手事實庫係雜訊」，同日定「頁數可追溯」為北極星**；跟住診斷出頁碼根本冇入語料（113 份 extract 只有 39 份帶標記），兩步救到今日 97.4%。③ 出 `dev/INFOGRAPHIC_PROMPT.md` 三條自足 prompt（A 長圖 / B 16:9 / C 三個反直覺發現），**指定輸出 PNG、繁中、書面語**，並寫明唔好用純圖像生成模型（中文密集文字會出豆腐字）。④ Leonard 再要 PNG，三張全部本地 headless Chrome render 完成，存 `dev/design/`。⑤ **QC 揪出並更正自己兩個數**：登記來源起點（唔係「8 份底稿」，registry 係 S48 先建）、公開分頁起點（唔係 4，S74 鎖定架構係 6 個 tab）。⑥ **一個要記住嘅環境事實**：本機**冇 PingFang**，繁中靠 `STHeiti` / `Songti TC` 兜底；換機重出圖前必須先確認字體，否則出咗豆腐字先發現。⑦ 本 session **零 OP 推進** —— Open Priorities ①–⑥ 原封不動，唔好誤讀成有進展。

> **🆕 S207（2026-08-19）—— 指章唔係指頁：per-chunk 子頁 URL + g14/g17 三缺陷 + 兩個源解亂碼：** HEAD==origin/main @ `3dc9952`（`a7ad697` 管道／資料 + `3dc9952` 後端顯示）；**Supabase 17,473 不變**（91 刪 91 入）、`source_registry` **268 不變**、`GUIDELINES_REGISTRY` **177 不變**、平台 **v3.3.0 不變**、凍結合約零接觸（`_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158）。① **OP① 完成（g14 + g17）：** `wiki_chunks.url` 本身就係 per-chunk 欄位 —— 只係入庫時全部填同一個 landing 頁，所以修法**前端／後端／schema 一律唔使改**。新 `carry_sections()`（`build_wiki_index.py`，同 `carry_pages` 同一契約、無標記源全 None = 完全 no-op）+ `source_registry.json` `section_urls` opt-in map。**g14 76 條 → 10 個子頁；g17 13 條 → 6 個目標（3 子頁 + 3 附件 PDF，後者仲保住 `#page=N`，live 實見 `page=3`）。** ② **交接講少咗：** 交接寫「只有 g14 有真 slug」，實測 g17 頭 3 個標記亦係真子頁（喺 `whole-school-approach-to-guidance-discipline/`，唔喺 registry `url_primary` 之下），故 g17 6/6 都指得到。③ **Fail-closed 閘第一次跑就捉到自己個錯**（3 條附件 PDF 漏 `/attachment` 前綴 → 404）；per-chunk URL 冇任何監察讀，冇呢個閘就會靜靜哋入庫。④ **兩個 regex 陷阱：**(a) chunker overlap 用空格接尾巴 → 標記甩行錨 → 行錨 regex **靜靜哋只認到全文第一個標記**；(b) 放寬行錨後，兩個相鄰頁碼標記夾住正文 → 讀成章節名，全庫 **847 個幻影 label / 135 源**。正解係**兩步（先剷頁碼、再認段落）**，同一次序喺 `cleanChunkText` 亦係 load-bearing。⑤ **OP② 三缺陷全清：** title 計劃→課程（**只有 vault extract 一份錯，三個公開鏡像本來就啱**）、22 條標記外洩喺 `cleanChunkText` 一次過修（覆蓋全庫 past+future、零 chunk id 成本）、91 行 EDB nav/footer chrome 由新 `strip_web_chrome()` 剷走。⑥ **額外揪出 g20/g25 生產庫亂碼：** EDB 唔出 charset → requests 跌返 ISO-8859-1；**個 200 字守門一直放行佢哋，正正因為亂碼撐大咗字元數**。已加 `min_extract_chars` override。g25 而家喺「幼稚園售賣教育用品收費服務指引」score **0.753** 命中（以前完全搜唔到）。⑦ **eval：** 30 SAME / 2 RANK_SHIFT / **1 SET_ADDED（`kg_admission` 多咗 g25）** / 0 regression；1 條 error 係 Supabase `57014` 暫時性 timeout，live 重試 3 次回傳同 baseline 一致。

> **🔙 S206（2026-08-18）—— 頁碼指路修復：`expand_vault` 兩層甩頁碼，11 個源重入：** HEAD==origin/main（本 closeout commit）；**Supabase 17,472 → 17,473**（11 個源刪→重入，淨 +1）；`source_registry` **268 不變**、`GUIDELINES_REGISTRY` **177 不變**、平台 **v3.3.0 不變**、凍結合約零接觸（`_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158）。**帶 `=== Page N ===` 標記嘅 chunk：15,613 → 17,022；無頁碼 1,859 → 451。** ① **OP① 重新定位：** live 重現證明交接嘅兩個修法（擴 synthesis 窗 / 改 spotlight 條件）**都修唔到佢自己指嘅 case** —— 正確資料行 exact cosine 0.6049 排源內 14/81，源內最高 0.6537 係零數據表頭行。Leonard 指出真正機制係「表格類問題指去該頁」，而該機制一早 ship（`mobile.js:519` / `app.html:2503,3404`）。② **根因兩層，同一支人手管道：** `expand_vault.py` 抽 PDF 時 `"\n".join()` **從來冇寫頁碼標記**；切 chunk 時用自己嘅 `chunk_text()` **冇 page carry**。自動管道 `execute_ingest.py:218` 一直用 `chunk_text_with_page_carry`，**從無此問題**。③ **修法：規則共用、chunker 唔共用** —— `carry_pages()` 抽出喺 `build_wiki_index.py`，`expand_vault` import 佢但保留自己嘅切法（共用切法會 re-hash 佢寫過嘅每一條 chunk）。④ **11 個源重入、全部 0 條無頁碼**；動 Supabase 前先證對無標記源係 no-op（`edbc00030` 67/67、`g04` 7/7 id 完全相同），每個源入庫前過「零內容漂移閘」。⑤ **eval 對開工基線：PASS=23 / FAIL=0 / errors=0 兩邊一致、0 blocking failure。** ⑥ **代價已量：** 標記令 cosine 溝淡 ~0.015–0.02（`coa_pri_e` 喺 `mpf` 由 rank 4→7），同全庫另外 15,613 條帶標記 chunk 一直付緊嘅價一樣。

> **🔙 S205（2026-08-18）—— Open Priority ① 收尾：S198 route-probe 兩次讀齊、零外部呼叫、probe 已刪：** HEAD==origin/main @ `bee54c9`；**零 Supabase 寫入／零檢索改動／零 synthesis-gate 改動**，chunks 仍 17,472、`source_registry` 268、`GUIDELINES_REGISTRY` 177、平台 v3.3.0、凍結合約零接觸（`_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158）。**① 交接框架有錯，已更正：** 交接寫「(a) 直接刪 / (b) 重開新觀察窗」，但 git 歷史證明 probe 只有一個 commit（`ddc98d5` 7/30）、之後零改動、Render auto-deploy on push → **連續 live 十九日**；而 Hobby 七日保留係 **rolling**，dashboard 一直坐住現成七日窗（8/11→8/18），「重開新窗」係唔存在嘅成本。**② 兩次獨立讀皆零第三方：** S202 8/2 讀 7/30→8/2 共 26 行全自測；S205 8/18 讀 8/11→8/18 共 2 行 = 當日親手放嘅 `s205-control-probe`。合共十日。**③ 儀器先行（S198 紀律第三次落地）：** 先 curl 放對照訊號證儀器活住（dashboard 15:06:59，對到秒，UTC+1 第四度實證），先數零。**④ probe 已刪：** commit `a1a6442`，`server.ts` 169–200 共 32 行純刪除；`getClientIp` / rate limiter / CORS / 其餘 route 零接觸。**⑤ 部署後 live 讀已閂：** 四個帶序號標記（14:15:05 / 14:17:03 / 14:17:32 / 14:22:28 UTC，最遲一個喺 push 後十四分鐘）**全部冇出現** → 新版真落地、probe 生產上已死。**⑥ 拆 backend channel-a 半邊（Backlog ⑥）前置由此解鎖。**

> **🆕 S204（2026-08-18）—— 人手編制文件群入庫 + 頁碼歸屬修正 + v3.3.0 + 累積計數器：** HEAD==origin/main；**Supabase 16,070 → 17,472**（＋1,344 入庫、−23 換 109 逐行重入、−28 回滾特殊學校表）；`source_registry` 257→**268**；`GUIDELINES_REGISTRY` 166→**177**；平台 **v3.2.2 → v3.3.0**；凍結合約零接觸（`knowledge.json._meta.version` 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158）。**① 頁碼歸屬修正已 ship：** `extractFirstPage`→`extractDominantPage`，真 PDF 核對 g24 74.1%→147/147、kg_admin 63.0%→127/127，全庫 5,453/15,601（35%）頁碼改變（4,927 條 −1）；`page` 唔入 scoring／synthesis，只影響頁碼同 `#page=N`。**② 資助小學學位教師文件群 10 份可搜尋**（特殊學校表 held back，見 ⑤）；新 `dev/vault/extract_table_rows.py` 座標重建表格＋算術不變式守門。**③ 可達性要四層**（SOURCE_SET → TOPIC_KEYWORDS → SPOTLIGHT → 獨立 `staffing` route 免 expansion ＋ 逐行 chunk），入庫本身唔等於搵到。**④ 新增累積計數器**（`usage_daily` + `bump_usage`/`get_usage_total`，`GET /api/stats/usage`，`x-probe` 排除自測），現值由 0 起計。**⑤ 特殊學校編制表 held_back**：入庫後令合成器對「12班小學有幾多學位教師」3/3 答錯（12 vs 正確 5），已刪 chunk，恢復條件寫入 registry notes。**⑥ eval before→after 兩次 PASS=23/FAIL=0**，31/34 完全不變。 **⑦ tab 開關機制成文：** `window.FEATURE_TABS` 驅動 7 個受影響位（唯一例外 index.html 靜態卡靠 inline style），註解列晒清單 + 恢復程序，`DOC_SYNC_CHECKLIST.md` 新增「Tab withdraw / restore」一行。教訓：首次實作逐個手 gate 漏咗兩個位，改成 `view` key 統一 filter 後先真正一個 flag 搞掂。

> **🆕 S203（2026-08-02）—— 文件 drift 清（⑩）＋ judge V4 量度（②，未 ship）＋ g24/sag 偵查（⑧，出 PLAN）：** HEAD==origin/main（本 closeout commit）；**Supabase 16,062 零寫入**（本 session `count=exact` 實核）、registry 256、平台 v3.2.2、凍結合約全部零接觸；起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main `bc2a8ae` / Supabase 16,062 exact）。Leonard 揀「1+2」再續 ⑧。**① NEXT ⑩ 文件 drift 修好（純文件）：** PMS 3 處 + roadmap 5 處 + `HANDOFF_PACKAGE.md:32` 統一為「下游轉 Channel B **S146 已完成**」（Leonard 確認方向＝已完成；S202 route-probe 零 channel-a 流量佐證）；R3 現只 gated on route-probe 8/5 + backend dismantle，不再等下游。**② NEXT ② judge V4 量度完成（Phase A+B，🔴 未 ship，零生產改動）：** 造 `v4a_s202.txt`(+8 最小)／`v4b_s202.txt`(+75 明示) + fresh held-out 10 條（`judge_transplant_fresh_s202.json`，逐條讀 passage、0 flip）+ harness `--cases`/`--cache`；dashboard reconfirm `gpt-4o-mini`；**7 次 run 噪音控制**。結論：**V4b 穩定修 GN10（範圍移植，0/3 vs V3 4/4）、零 recall 損（答半 7 runs 全 12/12），但 D01（對象移植）3/3 照漏、fresh FT06 照漏** → prompt-only 槓桿掂到明示範圍移植、掂唔到隱含對象移植 → **建議唔 ship、② reframe 做「非-prompt 對象核對機制」**（findings 已寫入 `dev/source/JUDGE_PROMPT_FINDINGS.md` S202 段）。**③ NEXT ⑧ g24/sag 偵查完成（純唯讀，出 PLAN）：** 親眼驗 Supabase → **真實文字重疊 377**（舊 doc/handoff 寫「215」全 stale）、g24 383 / sag_2025_11 409、**g24 零獨有內容**（6 條 g24-only 內容 sag 全覆蓋）、封面實寫「2026年5月版」（`sag_2025_11` 係 stale 命名）；g24 被 `role_facts.json:694` + eval gold 引用但都同 sag 並列（remap 乾淨）。合併 PLAN 備妥（remap → eval before→after → 刪 383 → live before→after → 清 code），**HIGH risk 另等 GO**（future session）。**④ probe 仍未刪**（`server.ts:168–198` 待 8/5 第二次讀後刪）。

> **🆕 S202（2026-08-02）—— NEXT ① route-probe 觀察窗第一次讀（8/2）＝全窗綠，零外部呼叫：** HEAD==origin/main（`2ec82cf`＝S202 8/2 checkpoint ＋本 closeout commit）；**Supabase 16,062 零寫入**、registry 256、平台 v3.2.2、凍結合約全部零接觸；起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main〔push 前〕/ Supabase 沿用 16,062 未重數）。**① route-probe 8/2 讀（Leonard 喺 Render dashboard、Claude 遠端放對照訊號協助）：** Render Logs「Last 7 days」search `route-probe`，2026-07-30 09:40 UTC → 08-02 全窗 **26 行全部有主** ＝ 24× `s198-deploycheck-*`（7/30 自測）＋ 2× `s201-control-probe`（8/2，Claude 為驗儀器親手放），**零第三方 / 零非自測 origin/ua** → 兩條 channel-a route（`/api/search/channel-a`、`/combined`）由 7/30 起零外部呼叫。**② 儀器信心＝S198 紀律落地：** 頭先 search 空手，冇當「零流量」；先放 `s201-control-probe` 即時對照（出到＝儀器 work）、再用 s198（7/30 回溯，「Last 7 days」下 24 行全現形）確認窗涵蓋返起點，先落結論。Hobby log 保留 7 日、dashboard UTC+1 均第三度實證。**③ probe 未刪**（`server.ts:168–198` 仍 live，留待 8/5 第二次讀後一齊刪）。**④ 零 code / 零 Supabase / 零 route 改動**，純唯讀量度 ＋ handoff checkpoint（commit `2ec82cf`）＋ §4a log 維護（402→122 行，4 舊 entry 搬入 `dev/archive/SESSION_LOG_2026_Q3.md`，只搬冇刪）。**🔜 8/5（≤8/6 前）再讀一次，讀完＋刪 probe ＝ 拆 backend route（⑥）前置。**

> **🆕 S201（2026-07-31）—— NEXT ② 收 footnote judge-bypass 完成（ship + deploy + live 驗）：** HEAD==origin/main（`fc287ff` = 收 bypass；本 session commits `ded9504`〔擴闊 decline 集 11→21〕→ `b7627b7`〔V3 baseline run〕→ `fc287ff`〔收 bypass〕）；**Supabase 16,062 零寫入**；registry 256 / 平台 v3.2.2 / 凍結合約全部零接觸；起手探針 4/4 綠。**① 擴闊 judge decline 集 11→21**（10 條 fresh gap 逐條讀 passage、GN11 入 answer 半邊；`judge_acceptance_cases.json` frozen）。**② 量 V3 baseline（擴闊 35 條、gpt-4o-mini dashboard reconfirm）**:answer 12/12、decline 19/21（2 false = D01/GN10，皆 transplant 類）。**③ 收 footnote judge-bypass**:`searchChannelB.ts` 移走 `trustedFootnoteLead`，footnote-lead query 而家過 V3；vault bypass + lead-slot 排序 + prompt 不變。**④ deploy + live 驗**:D17 消防演習 砌數→**拒答**、D13 留位費 仍正確答、D01 仍答（V3 miss，pending V4）。QC 全綠（tsc 0 / check-parity byte-identical / footnote_lead_probe before==after）。**🔴 新 open：②b 硬化 judge V4 收 transplant 類（D01/GN10）**，見 Open Priorities。
>
> **🔙 S200（2026-07-30）—— ship judge V3，連一個明文閘 override（Leonard 揀 Option 2）：** 換 `RELEVANCE_JUDGE_PROMPT`（`backend/src/api/searchChannelB.ts`）為 V3（byte-identical `dev/source/judge_prompts/v3_s196.txt`）＋同步改 `dev/source/judge_acceptance.py` `SHIPPED_PROMPT`（`--check-parity` byte-identical）＋重寫過時 rationale 註解。commit **`bcf7c4f`**（4 檔）已 push origin/main。Supabase 16,062 零寫入；registry 256、平台 v3.2.2、凍結合約全部零接觸。
> **① 驗收證據（生產 model gpt-4o-mini，`2026-07-30_s199_v3_4omini.json`，prompt 同 shipped byte-identical）：** primary 21/22、answer 半邊 **11/11**（收返 A02/A05/A06 vs shipped 8/11）、decline 半邊 **10/11**、`D00_s177_frozen_post`=否（正確拒答）、false answers=[`D01`]。
> **② 明文 override（AGENTS §2 rule 6）：** DOC_SYNC row 41 ＋ findings bar 寫「decline 半邊任何 false answer = 唔准 ship」。V3 有一個（D01）→ 照 ship，理由：(a) **非退步**——現行 shipped 一樣 D01 答錯（`2026-07-30_s199_shipped_4omini.json`），V3 零新增 false answer；(b) **一票否決唔中**——D00 正確拒答；(c) **D01 lead 係 `footnote_curated` @0.574 > `FOOTNOTE_LEAD_SCORE` 0.45**，生產行 footnote bypass、judge 從不 serve D01 → ship V3 唔改 D01 live 行為，D01 屬 NEXT ④（收 bypass）。**更正交接 S199 ③「decline 全保」＝講多咗，實係 10/11。**
> **③ QC 全綠：** `--self-test` 0 fail／`--check-parity` byte-identical／`--plumbing-check` 叫得出「能」／`tsc --noEmit` exit 0／post-ship `footnote_lead_probe.py`（`2026-07-30_s200_postship_footnote.json`）**positive 30/30 零損失**、negative 5/13、errors 0（V3 唔郁 bypass，lead gate 不變＝零回歸）。
> **④ ✅ deploy 已確認 live（Leonard 貼 Render Events，2026-07-30）。** Events 綠剔「Deploy live for `bcf7c4f`: S200 ship judge V3」，dashboard 顯示 4:50 PM（UTC+1）= 15:50 UTC，同 push 時間對上 → **V3 正式喺生產跑緊**。（當時外部觀察唔到係因為 V3 同舊 judge 有分別嗰啲 case〔A02/A05/A06〕live 全部行 footnote bypass、答案唔 flip；服務無 version endpoint。Render auto-deploy on push 已確立〔S117〕，今次亦係自動觸發。）順帶：`OPENAI_MODEL=gpt-4o-mini` 於 S199 同日 dashboard 已確認。
> **⑤ 🔴 D01 live 仍然錯 serve（未變）：** 「學生請病假要唔要交醫生紙」live 仍會攞教職員規則砌落學生度。ship V3 唔 touch 呢個（judge 唔行呢條）。屬 NEXT ④ 耦合修法（收 footnote bypass，令呢類 case 去見修好嘅 judge）。
> **⑥ 收工完成（Leonard「全做」）：** `Open Priorities`／`Last Session Record`／`Next Session Opening Message`／`State Reconciliation Check` 全部重生為 S200、`START_NEXT_SESSION_PROMPT.txt` 由 opening message 重生並 mirror check。deploy：**Render auto-deploy on push to main 已確立（S117，見下 Supabase Technical Notes）→ `bcf7c4f` 之 deploy 已自動觸發**；外部只確認唔到 judge prompt 已換（差異 case 全 bypass judge），故留 Open Priorities ① 由 Leonard 喺 Render Events 一眼確認。

> **🆕 S199（2026-07-30）—— 純量度 session：把 Channel A 退役由「量度未夠」重構成「一個資料模型缺口 + 一個已拍板嘅路向」，並在 judge 上踩中又更正一個 model 錯誤：** HEAD==origin/main（S199 commits `a65e723` → `829aa49` → `c96dc6d` → `a80c69b` → `1aeab49` → `f02c069` → `710d8cc` → 本 closeout commit）；**Supabase 16,062 零寫入**；**source_registry 256 不變**；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines 逐 topic 加總 158）；起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main / Supabase count=exact 16,062）。**零 Supabase 寫入、零 code 改（`RELEVANCE_JUDGE_PROMPT` 同 bypass 常數未郁）、零 route 改。** 全部係唯讀量度 + 記錄。
> **① Leonard 叫停 judge 工作、問返 Channel A 退役實況 → 重構成資料模型缺口。** 退役實況:前端已退(S197)、backend 兩條 route 未退(卡 S198 觀察窗)、**precondition「Channel B 覆蓋 Channel A」已量 = 覆蓋唔晒**。455 條事實:109 條鏡像入 store(url 全空)、346 條淨經 route。職責歸屬類逐條打開 passage 核實:文件只泛講程序、唔講邊個具名角色揹職責 → **結構性缺口,量度補救唔到**。詳見 `CHANNEL_A_COVERAGE_FINDINGS.md` §5。
> **② Leonard 拍板 Option 2(升做有出處 footnote)。** 做咗唯讀可行性 triage:總帳「141/141 有 url」係 retrieval 目標唔係出處(44% 陷阱);讀樣本 CLEARED ~3/5 可升、UNVERIFIED ~0-1/4。**真實大細:升唔到嘅硬核只有 24 條純職責歸屬(`[角色] 負責…`),唔係 ~100+;其餘 117 條「提到角色」大部分揾返出處就升得到。** 真入庫 = §3 HIGH risk + 跨 session,要獨立 PLAN + go。詳見 `CHANNEL_A_COVERAGE_FINDINGS.md` §6。
> **③ judge:先量錯 model,由 Leonard 撳 dashboard 揪返。** 建咗凍結驗收工具 `dev/source/judge_acceptance.py` + 24 條凍結集(量度前 commit)。首兩份 baseline 我用咗 code default `gpt-4.1-nano` —— **Render 實設 `OPENAI_MODEL=gpt-4o-mini`**(Leonard dashboard 確認)。同一 prompt:nano 0/11、gpt-4o-mini 8/11。**「judge 恆等於否」係 fallback model 特性,唔係 shipped prompt 特性;S196 findings 全部變「未經生產驗證」。** nano run 已改名 `_nano_ARTIFACT`。
> **④ V3 喺生產 model:21/22(shipped 18/22),answer 半邊 11/11 vs 8/11,decline 全保。但兩個 prompt 共用同一個 false answer,而且係 live。** V3 冇 tune 過呢個集 → held-out。
> **⑤ 🔴 D01/D17 呢類 live 錯答而家仲 serve 緊,而改 judge 救唔到。** 7 條 footnote-lead 空白查詢 live 全部答咗、冇一條 decline。逐條核實:D17「消防演習幾耐」實錘砌數(「消防演習」庫入面 0 條,「每12個月」由「消防裝置檢查」搬過嚟);D13「留位費」**其實答啱**(970/1570 有出處,我標錯做空白,已更正)。**footnote lead 跳過 judge,所以改 judge prompt 唔 touch 佢哋 —— 修法係「先修 judge、後收 footnote bypass」,次序企得穩,件事係耦合。** 詳見 `JUDGE_PROMPT_FINDINGS.md`。
> **⑥ 本 session 最貴一堂:對照組證明「儀器有反應」,證明唔到「儀器指住正確系統」。** `--plumbing-check` 過關但捉唔到 model 用錯 —— 凡 Render 側嘅嘢,「係咪生產行緊嗰個」只有 dashboard 答得到。已寫入 `judge_acceptance.py` 註釋、`JUDGE_PROMPT_FINDINGS.md`、commit message。

> **🔙 S198（2026-07-30）—— S197 留低嘅阻塞項唔係「等 Leonard 覆」，係「問錯咗地方」；換咗個量得到嘢嘅儀器，而家等一個 7 日窗：** HEAD==origin/main（S198 commits `ddc98d5` → `16fec71` → `2eb642f` → `07173f6` → `b74f5f4` → 本 closeout commit）；**Supabase 16,062 零寫入**；**source_registry 256 不變**；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines 逐 topic 加總 158）。起手探針 4/4 綠。本 session **零入庫、零檢索改動**，故 eval 未重跑。
> **① S197 ①「去 Render Logs search `channel-a`」係一個結構上量唔到嘢嘅指示。** Leonard 依足做，回「No matching logs」。**冇當佢係零流量** —— 呢個結論啱好對我有利（我想拆 route）。查落三層：`server.ts` 全檔只有三句 `console`（一句錯誤、兩句開機），**冇任何 per-request log**；**對照組**——一個確實發生過嘅 `/health` request（親手 curl 收到 200 JSON）search「health」**同樣零命中**；**正對照**——search `CORS` **搵到** `server.ts:396` 開機輸出。機制由官方文檔確認（<https://render.com/docs/logging>）：**per-request log 係 Pro workspace 以上功能**，呢個係 Hobby free instance；同時查到 **Hobby log 保留期 7 日**。
> **② 已換成主動量度並 live 驗證。** `[route-probe]` 加喺 `server.ts` handler 最頂（OPTIONS 同 POST rate limiter **之上**，所以 preflight 同被 throttle 嘅呼叫都捉到），只認兩條 route，印 method/path/origin/user-agent/**完整 XFF 鏈**/socket peer，**永不印 body**。**本機自檢 ×2 都對數**：首版 4 請求→3 行（GET 錯 method 照捉、channel-b negative control 零行）；XFF 版 3 請求→2 行。**live 驗**：三輪帶序號自測流量 **24 請求 → 24 行**，一行不多一行不少。
> **③ 中途按 §3 停低過一次。** PLAN 寫明 IP 用嚟認下游，首版用 `getClientIp()`（取最右跳，S187 為 rate limiter 防偽造而設）—— live 實測最右跳係 Render 內部 `10.x`，**認唔到任何人**，即 PLAN 承諾嘅嘢做唔到。停低報告、Leonard 批「改」後先改成印全鏈；`getClientIp()` 同 rate limiter **零接觸**（仍在 `server.ts:247`）。修正後 live 鏈 = `90.240.109.123`（真實公網）/ `172.64.x`·`141.101.x`（Cloudflare）/ `10.25.116.1`（Render 內部）—— **舊 code 只印到最右嗰個。**
> **④ 同一個 session 入面我踩咗兩次同一個陷阱。** 部署後我用 `/health` 嘅 `cache_a.warm` 偵測重啟，行足 421 秒零命中，一度想寫「未部署」。實情係 **Render 零停機部署會先暖好新 instance 先切流量，外部永遠見唔到 `warm=false`** —— 同「信 log search 嘅沉默」一模一樣。真憑據係 instance id 變咗（`pcwrl`→`p2znr`→`26wlj`）。**兩次沉默都啱好指向我想要嘅答案**，所以靠「覺得唔妥」係捉唔到嘅，已寫成硬規矩入 `PROJECT_DECISIONS.md` Insights + DOC_SYNC 驗收欄 + code 註釋。
> **⑤ 順帶更正咗自己另一句話。** 我曾講「09:52 嗰個 cold start 同我杯 curl 對得上」—— **錯**。由 seq=1 錨點（本機 09:40:48 UTC ↔ dashboard 顯示 10:40:48 AM）證實 **dashboard 時間戳係 UTC+1 顯示**，即嗰次開機係 **08:52 UTC**，喺我第一杯 curl（約 09:35 UTC）**之前 43 分鐘**。有嘢喺我開始之前叫醒過個 instance，**來源未查明** —— 唔係 channel-a 流量嘅證據，但唔應該當唔存在。
> **⑥ 獨立確認：兩條 route 喺 repo 內零呼叫點。** 全 repo grep（`.html/.js/.ts/.py/.json`，排除 log/archive）只喺 `server.ts` 自己出現；`mobile.js` 早於 S119 已轉 `/api/search/channel-b`。**唯一可能消費者只剩下游 Circular System（跨 repo）。** ⚠️ 順帶揪出 `dev/HANDOFF_PACKAGE.md:32` 仍寫「mobile search 接 `/api/search/combined`」，**已過時、未修**。
> **⑦ 🔴 生產度而家有一段臨時 code。** 觀察窗 **2026-07-30 09:40 UTC 開始**，**8 月 2 日 + 8 月 5 日各讀一次**（Hobby 只保留 7 日），讀時**扣起 24 行 `ua=s198-*`**，**讀完必須刪走 probe**。目前 32 分鐘內零外部呼叫 —— **呢個數字唔代表任何嘢**。

> **🔙 S197（2026-07-29）—— Channel A 退役：量度完先發現真問題唔喺覆蓋率，而喺 Channel A 自己載住乜；我兩次推翻自己：** HEAD==origin/main（S197 commits `c01e646` → `596e383` → `2d70ef7` → `5754c00` → `3ba92fe` → `d554b4c`）；**Supabase 16,062 零寫入**（只加 code 層 filter）；**source_registry 256 不變**；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines 158）。起手探針 4/4 綠。**eval 由 30 擴到 34 條，PASS 23 / FAIL 0 / errors 0，before→after 0 blocking failures。**
> **① 退役標準由 Leonard 定：「已喺 Channel B 或可追蹤出處就可以退」。** 但「輸出完全一樣」做唔到標準 —— Channel A 事實係**冇 URL 冇頁碼嘅裸句**（455 條散喺 47 個〔範疇×角色〕桶，`_source_refs` 只喺範疇層），Channel B 出原文＋URL＋頁碼。改為量「substance 覆蓋」。
> **② 量度必須剔走語料入面 Channel A 自己嘅鏡像，否則個數係假嘅。** `wiki_chunks` 16,062 = `vault_extract` 15,721 + `footnote_curated` 206 + **`approved_fact` 109** + **`stat_fact` 26**（逐類點過、總和相符）。嗰 109 條**逐字係 455 條嘅子集**（精確字串比對 109/109 命中、0 條外來），同 26 條 stat_fact 一樣 **url 全空**。唔剔走，攞事實去搵第一個命中就係佢自己 @0.828 → 量到「455/455 全覆蓋」，而個數純粹係「問題就係佢自己嘅答案」。
> **③ 已做：前端 Channel A 路徑全清**（`2d70ef7`，−109/+8 行）。已證摸唔到而唔止係無人用：`CHANNEL_OPTS` 只得一項，selector 寫住 `length > 1` 先 render，所以 `setSearchChannel` 永遠只收到 `'B'`。live 驗：served `app.html` 六個關鍵字全部 0、1280px 重載 console 零 error、Channel B 搜尋 200/7 條/synthesis 正常。
> **④ 已做：9 條有已證出處嘅鏡像 chunk 退出服務路徑**（`3ba92fe`，`RETIRED_MIRROR_CHUNK_IDS` + `retiredMirrorFilter`，套三個映射點）。觸發證據：live 實測「採購門檻」rank-0 係 `role_facts_finance`（**url 空、page null**）壓住 `g01` **p.5**（同一條規則、有頁碼）—— 即無出處嘅副本贏緊佢自己嘅出處。修完 rank-0 變 `g01` p.5。**Supabase 零寫入，刪一行即還原。**
> **⑤ 我推翻自己兩次，兩次都係向「對自己有利」嗰邊錯:** (a) **把尺壞咗** —— 首輪報「8月15日前交假期表」搵唔到錨點，開 `g11` 一睇係「於每年**八月十五日**前……」，**同一規則中文數字寫**；首 29 條有 10 條同一原因。加中文數字折算離線重判，**71 條轉桶、COVERED 100→149**。呢個 bug 令工具**系統性高報缺口**，而每個假缺口都係「唔可以退」嘅理由。(b) **由一個實例推去成批** —— 我憑「採購門檻」一條就提議**整批剷走 109 條**、講「拎走唔係損失」。量埋成批：**93/109 冇已證替代品**，大部分係 `[角色] 負責…` 呢種語料唔會有嘅形態；live 實測「訓導主任 社工」鏡像佔 rank 0/1、語料最近似（`g16` p.17）講跨部門聯繫而唔講邊個負責。**剷走真係會蝕。**
> **⑥ 最要記住嘅數字：機械判定 `CLEARED` 有 44% 撐唔住人手覆核。** 總帳畀 16 條「有可引用替代品」候選，逐條讀完**只有 9 條過關**。7 條失效模式各異：段落講另一科目（人文科 vs 小學科學）／用「五種基要學習經歷」嘅**定義**冒充津貼用途**規則**／實質有但**職責歸屬冇**／所謂替代品係一份**問卷通告**。**紀律已寫入 `searchChannelB.ts` 該常數註釋：唔准由總帳直接延長個 list，每條都要開段落嚟讀。**
> **⑦ eval 集本來對呢個改動完全盲，已修。** 原 30 條**冇一條** expect `role_facts_*`、冇一條問「邊個負責」→ 剷走鏡像會量到零回歸，而個綠燈係假嘅（同 S195 spotlight prune 同一形態）。加 4 條角色職責 query；其中 2 條由 baseline 證實**我釘錯咗預期**（`g19` p.13/p.57 先係服務緊 SENCO），已即時更正，`curr_coord_role` 改 RECORD_ONLY —— 冇來源答得好，釘任何一個都係把爛答案封為正確。
> **⑧ 順帶揪出：3 條 Channel A 事實同現行《學校行政手冊》直接矛盾** —— 病假「36天」vs `sag_2025_11` 附錄9「首年28天／其後48天／累積168天」；非教學人員年假「18/21/24天」vs「7天起、上限14天」。**已查證呢 3 條唔喺 Supabase**（store 含「36天」嘅 `approved_fact` = 0），唔會經 Channel B 出街，只可經 `/api/search/channel-a` 攞到 → 會隨 backend route 退役一齊斷。另外 455 條入面有問卷題（「**貴校**需評分…1至5分」）、活動統計、殘缺片段（「取得校長批准。」／「2013年4月1日作出修訂。」← 已鎖定係 `coa_imc_1_19` 修訂註腳欄被抽成事實）、簡體字同日文漢字「関」等抽取瑕疵。
> **⑨ 未做（阻塞）：backend `/api/search/channel-a` + `/api/search/combined` 未郁。** PLAN 出咗、READ 做完（依賴已查清：`searchChannelA.ts` 只被 `searchCombined.ts` 用、`searchCombined.ts` 只被 route 用、`factEmbeddingCache.ts` 只服務 Channel A；**但 `knowledgeRepository.ts` 要留**，`analyzeCircular.ts` 仍 import）、驗收矩陣寫好。**唯一阻塞＝Leonard 未覆 Render logs `channel-a` 有冇真流量。**

> **🆕 S196（2026-07-28）—— 修好「校巴營辦商責任」，但真根因同 handoff 記錄嘅唔同，而且影響面闊過一條 query：** HEAD==origin/main（S196 commits `b61e108` → `7078719` → `528435d` → `969698e` → `138dfca`）；**Supabase 16,062 零接觸**（純檢索行為修復，無入庫）；**source_registry 256 不變**；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines 158）。起手探針 4/4 綠。**最終 eval PASS 20 / FAIL 0 / errors 0**。
> **① handoff 原本寫「TOPIC_KEYWORDS first-match 次序問題」係錯嘅。** `detectQueryCategory("校巴營辦商責任")` 一直都返 `safety`（六種 phrasing 全部一樣），改次序係 no-op。真根因兩層：`SOURCE_SETS.safety` 同時載住 `sag_2025_11`（學校行政手冊 215 chunks，採購／籌款段落 0.602 壓過校巴指引 0.506）；加上兩條 `footnote_curated` 靠 0.45 門檻攞咗 rank 0/1，**而 footnote lead 會跳過 anti-confab judge** → 出街答案講「校巴經營利潤必須運用於學生的直接利益」（攞 IMC 小賣部條款砌成）。**唔止排名差，係答錯嘢。**
> **② 修法 A：新 `school_bus` route**（g18 ＋ 5 份 2026/27 姊妹指引，bus tokens 由 safety 搬過去唔係複製）。校巴內容由 rank 5 @0.506 升到 rank 2-7 @0.743-0.768。第一版 query expansion 塞晒六個受眾名詞，eval 即刻捉到「跟車保母」由 escorts 跌落 operators —— **姊妹之間唯一嘅分別詞被自己洗走**，改為只留共通詞彙後 SET_LOST 歸零。
> **③ 修法 B：footnote lead 加 lexical gate。** footnote 要同 query 共享 ≥2 個 informative bigram（喺 206 條 footnote 語料上做 DF 自校準）先攞得到 lead slot；judge bypass 由「邊個坐 rank 0」改為綁定「gate 批准嘅 lead」。**被拒嘅 footnote 唔會被刪，照按分數 merge —— 收走嘅只係特權。** 新 lib `backend/src/lib/textBigrams.ts`（`cjkBigrams` 由 checklistRevise 搬入並 re-export）＋ `wikiRepository.footnoteInformativeBigrams()`。
> **④ 兩個 deploy 完先捉到嘅嘢（記住：離線校準過關唔代表得）：** (a) 門檻 1 唔夠 —— 中文 bigram 分唔開 `營辦商` 同 `承辦商`（都有 `辦商`），SCRC footnote 照樣攞到 lead，**要 live 重探先發現**；(b) 淨係抬到 2 會令 1 條**幾乎全英文**嘅 footnote 問題失去席位（overlap=1 淨係來自 `要點`）。正解 = **gate 只喺 query 本身有 ≥2 個 informative bigram 先啟動，唔夠就 fail open**。
> **⑤ 影響面闊過報上嚟嗰條：** 最終 eval 6 條 SET_LOST 逐條人手判斷，**全部係離題 curated footnote 失去唔應該有嘅頭位**，而每條 query 嘅正確文件都升咗（考試調適原本俾幼稚園非華語津貼 footnote 帶頭、家校合作俾寄宿津貼、薪酬調整俾 NET 計劃改革）。即 30 條 eval 入面有 6 條中招。
> **⑥ 驗收證據：** 新工具 `dev/source/footnote_lead_probe.py`（positive = 每條 footnote 自己嘅問題；negative = judge_probe 嘅 plausible-gap ＋ 校巴）。**positive 26/26 零損失、全語料 206/206 自問仍攞到 lead**；negative 剷走 4 條。TS 同 Python 兩份鏡像算出 informative bigram **都係 7828**（無實作漂移）。
> **⑦ 收工前追加一輪：我自己個 probe 標錯 label，實際殘餘問題細好多。** 我原本直接借用 `judge_probe.py` 嘅 negative set 做 footnote probe 嘅敵意組 —— 但 judge_probe 量度嘅係 **vault** 門檻，佢問「vault 答唔答到」；curated footnote 其實**精準答到**當中幾條。逐條核實 14 條之後：`幼稚園每班最多可以收幾多個學生`（辦學手冊附10：每班不超過30人、午睡20人）／`老師病假連續請幾耐先要交醫生紙`（附錄9：超逾兩天）／`校服供應商招標要幾多間報價`（>$200k 公開招標最少5個供應商）／`體罰投訴要幾多日內處理完`（投訴指引：兩個月／14天）**全部係真命中，footnote 帶頭係功能正常唔係缺陷**。已改為新 `ANSWERABLE_CONTROLS` 類並當 positive 計。**重跑：positive 30/30 全保。** ⚠️ **同一 session 內要再更正一次**：我第一次報「2/10」係錯嘅 —— 重寫 negative list 時，3 條 borderline（解僱教師遣散費／學校借錢俾教職員／教師評核合格分）冇歸入任何一堆就消失咗，而我冇對過拆完之後總數返唔返到 14。三條**全部仍然攞到 footnote lead**，即個疏忽一路向自己有利，令我低報咗一半以上。逐條打開語料實物核實（唔係靠關鍵字命中）後三條都證實係真空白，已放回 negative → **修正後 negative 5/13**。**教訓：拆分或重標一個測試集之後必須對返總數，尤其當個錯會令自己個結果好睇。**
> **⑧ 殘餘 5 條，而且唔係同一種形狀。** 2 條屬「答咗隔籬嗰條問題」：`教師每年可以請幾多日大假`（庫有病假冇大假，於是答咗病假）同 `學校每堂補習費可以收幾多`（有核准收費表但冇補習費上限）。**但 `學校可唔可以借錢俾教職員` 性質更嚴重 —— 全庫根本冇任何「學校借錢俾教職員」嘅規則**（`借貸`／`借錢`／`貸款` 命中全部係 BAFS 會計科、學生賭博警號、學生資助貸款），系統卻答得斬釘截鐵。**呢條係真‧砌數，所以殘餘問題唔可以統稱為「答隔籬」。** 另 2 條：`解僱教師要俾幾多個月遣散費`（庫只有按比例計法，冇法定月數）／`教師評核幾多分先算合格`（庫入面「合格」指合格教師資格同基本法測試及格，唔同意思）。
> **⑩ 最後一輪（Leonard 再批 go）：查實 judge 本身壞咗，所以 bypass 收唔到。** 收緊 bypass 嘅設計本身成立（覆蓋率分得開：negative 0.40/0.62 vs positive p10 0.77，ratio ≥0.70 兩條全擋，代價係 2 條 answerable control 失去 bypass）。**但我把嗰 2 條放咗俾真 judge 判，佢兩條都拒答** —— 於是收緊 bypass = 用兩個「答啱」換兩個「答隔籬」，淨蝕。
> **⑪ 直接量度 judge（離線叫佢本身，16 條 case：8 條庫有答案、8 條冇）：shipped prompt 得 8/16 —— 8 條有答案嘅全部拒晒**，包括四條答案逐字喺 chunk 入面嘅（病假超逾兩天／投訴兩個月＋14天／招標最少5個報價／每班不超過30人）。**即係話生產睇落正常，係因為兩個 bypass 幫佢繞過咗 judge；judge 一旦真係行到，就近乎恆等於「否」。** 呢個亦解釋返 S194／S195B 觀察到嘅「judge 過度拒答」——根因喺 prompt 嗰段「有任何不確定一律答否」被模型當成一條全局信心題嚟答。
> **⑫ 已試改良，但**未** ship：** V3（把判斷寫成「對住文本做一個測試」而唔係一種態度）由 8/16 升到 **11/16 且零誤放**（連 S177 凍結教席砌數案例都照樣拒）；V4 寫得更詳細反而跌返 8/16。**我冇 ship，因為 16 條 case 係我自己 tune 出嚟嘅，而呢個係 anti-confab 骨幹** —— 由「永遠拒」改成「有時答」嘅風險面，遠大過我呢個測試集覆蓋到嘅範圍。完整量度、V3 全文、同 ship 之前需要乜，見 **`dev/source/JUDGE_PROMPT_FINDINGS.md`**（新檔）。**關鍵發現係量度方法**：chunk 攞一次快取起，prompt 可以離線迭代，唔使部署 —— 所以下次做呢件事成本好低。
> **⑨ vault 側嘅舊結論不受影響**：`不應超過30` 雖然真係喺 vault 出現，但嗰條係 g07 講家課時間（家課不應超過30分鐘），唔係班級人數；班級人數只存在於 curated footnote。所以 S195B「VAULT_LEAD_SCORE 降唔到」嘅結論**企得住**，唔使重開。

> **🆕 S195 下半（2026-07-27）reconciled —— Leonard「全做」：一次過清埋餘下 8 項優先事項，其中兩項嘅答案同原本假設相反，一項係我自己整錯即刻還原：** HEAD==origin/main；**Supabase 16,033 → 16,062**（校車五份 +28／g21 22＋va_safety_sec 27＋g22 58 新入 −106 舊）；**source_registry 250 → 256**；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines **158** —— 見下 ⑧，原以為要 158→159，實情唔使）。**最終 eval：PASS 20 / FAIL 0 / errors 0**（query 由 25 擴到 30，新增 5 條專門守住今次入庫嘅源）。
> **① 校車五份姊妹指引入庫**（司機/保姆/營辦商/家長/學童，28 chunks）：g18 只講學校自己嘅責任，呢五份係學校要監督或告知嘅對象，所以「跟車保母有咩要求」以前根本無嘢可答。五份頁碼逐頁核對全對齊；live rank 0 @0.624。
> **③ g21／g22 引文錯配已修（Issue #5）**：g22 原本漏咗封面頁令**每個引用頁碼都早一頁**（重抽 52 頁修正）；g21 更嚴重 —— vault 係小學版＋中學版兩份串埋，49 條 chunks 全掛小學版連結，即約一半引文指向一份佢哋唔屬於嘅 22 頁文件。已拆成 `g21`（小學）+ 新 `va_safety_sec`（中學）。**兩條人手寫嘅 footnote chunk 有明文保護冇被刪**，並已重指去正確 PDF 頁。DELETE 106 行由 Leonard 執行（權限閘擋我），事後驗 23/59/27 全對。
> **⑤ 封面核對接 CI**：`.github/workflows/title_check.yml` 月跑（1 號 13:00 UTC，無需 secret）。**關鍵設計 = alert on diff, not on count** —— 全掃會 flag 18 條而全部良性，用 severity 做 gate 會每次出 11 個假警報。改為同 `dev/source/title_baseline.json`（人手覆核過嘅接受狀態）比對，只有「新出現嘅 flag／覆蓋率跌 ≥0.15／fetch 失敗」先開 Issue。加咗 9 條 self-test 守住呢個邏輯。
> **⑥ 重複登記**：`kgecg_2017`／`g31` 標 deprecated（兩者皆 0 chunks，內容分別由 `g29`／`eng_pri_guide_2025` 承載），並清走 `kgecg_2017` 喺 SOURCE_SETS 兩處 dead 引用。合併前先證實兩個 KG 檔係同一份文件（同 108 頁、逐頁對齊、差異純屬文字層抽取瑕疵）。
> **② judge 門檻：實測後決定唔改，而且係「改唔到」而非「唔想改」。** 新工具 `dev/source/judge_probe.py` 跑 24 條 probe：敵意類（14 條「似學校事務但答案根本唔喺庫」）最高衝到 **0.632**，真命中最低 **0.624** —— **兩個分佈重疊**。降到 0.60 會放行「教師每年可以請幾多日大假」(0.617)、「學校可唔可以借錢俾教職員」(0.615)，即 S177 砌數重演。結論：cosine 分唔開「揾到對嘅文件」同「揾到語域相同嘅文件」，要提升要換 judge 唔係換數字。實測已寫入 code 註釋。
> **⑧ 唔使郁凍結 count**：查實公開指引庫一早已有正確嘅 2024 宗教教育指引（`religious_edu_jss_2024`），被剔走嗰個 `religious_edu_jss` 係**重複行 + 死連結**（全檔唯一一條 vertexaisearch AI 轉址殘留）。刪走重複行即可，公開數目維持 **158**。⚠️ 同時更正我自己上半場嘅錯：我曾把 `religious_edu_jss` 改名成 2024 版而製造 registry 重複，已改回 `superseded`。
> **⑦ spotlight prune：我做錯咗，eval 捉到，已還原。** 我用「ANN pool 可達性」probe 判定 4 個源可以剪，但 before→after eval 顯示 `ai_intro`／`net_scholar`／`pay_adjust` 由 PASS 變 FAIL，失去嘅正正就係被剪嗰 3 個。**probe 唔忠實**：我用自己揀嘅描述性 phrasing（「人工智能初探 學與教」）去測，而真正重要嘅係用戶打嘅裸名詞（「人工智能初探」），加上生產路徑會先做 query expansion 再 embed，所以 probe 睇到嘅候選池根本唔係生產嘅池。已全部還原、重跑 eval 對 baseline **25/25 全同**，並把呢個教訓寫喺 `SPOTLIGHT_SOURCE_IDS` 上面。
> **④ 唯一做唔到嘅**：`PUBLISH_PAT` 係咪 fine-grained、只限 `edb-circular-site` contents:write —— fine-grained PAT 嘅權限只可以喺 GitHub 帳戶 Settings → Developer settings → Personal access tokens 睇，API 唔會俾 token 自報 scope。**只有 Leonard 做得到。**
> ⚠️ 新發現未處理：「校巴營辦商責任」會被 governance route 搶走（返 IMC／學校行政手冊）—— 屬 route 次序問題，要自己一對 before→after 證據，未郁。

> **🆕 S195（2026-07-27）reconciled（數字以本段為準）—— 清兩條積咗 4 星期嘅死連結 + 整理 registry↔store drift，零內容改動：** HEAD==origin/main（S195 commits：本 session 主體 + closeout commit）；**Supabase 16,035 → 16,033**（前半純改 `url` 欄 285 行、零 INSERT／DELETE；後半 g18 改版 ＋7／−6）；**source_registry 250 不變**（只改既有條目欄位）；平台 **v3.2.2** 不變；**凍結合約零接觸**（`_meta` 2.3.0 / facts 455 / guidelines **158**、`guidelines.json` v2.6.1 —— 只有 `_meta.updated` 隨 `build_guidelines.py --write` 重生為 2026-07-27）。起手探針 4/4 綠。**S195 = Leonard「跟你建議」→ 做 ②（2 條真 404）＋③（5 條 pdf-serve-HTML），中途兩次因發現超出原述而停低確認。****核心發現：呢兩條 404 唔止係 registry 污糟，而係用戶真係撳到 404** —— `g01` 34 chunks ＋ `ls_jss_2010` **251 chunks** 服務緊死連結，另外 `app.html` 指引文件庫／`guidelines.json`／`data.json`／`secmeta.json` 各自都有一份副本（同一條 URL 散落 6 個地方）。兩條都用 playbook 方法 B re-crawl 揾返：`g01` 係上游改名（`…Trad Chi_2024.pdf`→`Guidelines on Procurement Procedures_TC.pdf`）、`ls_jss_2010` 係搬入 PSHE 檔案庫。**關鍵證據＝逐頁比對 vault：30/30 同 183/183 頁完全相同**，所以判定為**純 re-point 而唔係 re-ingest**（避開 playbook `freshness-monitor-test-served-url` 警告嘅「churn 照 re-point」陷阱）。**QC**：`check_served_urls.py --check` 全掃兩次 —— 修完頭兩條後 267 OK／1 broken（即揪出 g18），修完 g18 後 **268／268 OK／0 broken／0 error，成個 store 首次全綠**；live Channel B 實測 `g01` rank 1-3、`ls_jss_2010` rank 0 @0.715 p.30 且 URL 已係新值。**③ 5 條全部證實零用戶影響**（`g21`／`g22` 嘅 store 一早 serve 緊真 PDF，係 registry 落後；`g30`／`g31`／`religious_edu_jss` 各 0 chunks），已逐條更正；`religious_edu_jss` 仲揾返直連 PDF 並經封面核實為 **2024 版**（非原記錄嘅 legacy）。**同一 session 續做（Leonard「go」）：`g18` 校車安全指引 re-ingest 完成** —— 上游 2025/26 版落架、出咗 2026/27 版（6 頁 vs 8 頁、只 3/8 頁相同 = 改版非改名），故走完整 extract→INSERT→DELETE 而非改 URL：**Supabase 16,035 → 16,033**（＋7 新版／−6 舊版獨有）。**過程揪出一個會靜默刪錯嘢嘅陷阱**：chunk id 係內容 hash，兩版有 3 段文字完全相同故 id 重疊 —— **照 `source_id` 一次過刪舊 9 條會連現行內容刪走 3 條**，正確刪除集係「舊 id − 新 id」= 6 條。DELETE 步驟被 auto-mode 權限閘擋，改由 **Leonard 親自執行** `dev/_s195_delete_stale_g18.py --apply`，事後我驗證 g18=7 行／舊 id 殘留 0／總數 16,033。自檢頁碼錨點 **6/6 頁對齊 offset 0**（無 g21/g22 那種錯位）。live 驗：搜「校車 學生服務車輛 安全 座位」→ g18 **rank 0/1 @0.725/0.716**、標題已係（2026/27）、URL 已係新版。⚠️ **2 項仍未修**：(1) **`g21`／`g22` 引文頁碼錯開一頁，`g21` 一半 chunks 實際來自中學版文件卻掛小學版連結** = S194 `ict_sss_2021` 同一家族、五個監察全部睇唔到（GitHub issue #5，Leonard 指示只記錄）。(2) `religious_edu_jss` 修好連結後理論上可入公開指引庫（158→159），**未做**，因為會郁凍結 count。另：校車頁另有 5 份 2026/27 版（司機／保姆／營辦商／家長／學生）從未入庫，待決定。**監察系統證實健康**：Issue #4 由 2026-06-29 起就準確列住呢兩條 404，係無人跟進而唔係捉唔到。0 outstanding bug。
>
> **🆕 S194（2026-07-26）reconciled—— 修一個長期指錯文件的來源 + 人工智能初探框架正文入庫 + 建 roadmap R1 eval harness 同第 5 監察：** HEAD==origin/main（S194 commits `3f2c9d9` 主體 → `e0e2f3b` eval run → 本 checkpoint commit）；**Supabase 15,901 → 16,035**（+215 INSERT／−81 DELETE）；**source_registry 248 → 250**；平台 **v3.2.2** 不變（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 零接觸）。起手探針 4/4 綠。**核心：`ict_sss_2021` 一直指錯文件** —— 標題《資訊及通訊科技 (中四至中六) 2021》但 url 指 `CS_CAG_S4-6_Chi_2021.pdf`，`CS` 被當 Computer Science 實為 **C**itizenship and **S**ocial development → 81 個公社科 chunks 長期掛 ICT 標題（prod 實測：搜「公民與社會發展科」top-1 標題係「資訊及通訊科技」），真 ICT 2021 從未入庫，且 `curriculum` route **從未有任何 ICT 源**。修：新 `cgss_sss_2021` 承載該 81 chunks（**hash set 81/81 相同**，內容逐字不變）→ DELETE 舊 81（post-count 0）→ `ict_sss_2021` 改指 EDB 官方檔 + 入真正文 116 chunks；`curriculum` +2 ICT 源、新 `cgss` route、`SUPERSEDED_IDS` +`ict_sss_2007_2015`。**另入庫**《人工智能初探》框架正文 `iit_ai_framework_2026`（18 chunks；`edbcm113_2026` 只係通函 3 chunks）。**新工具**：`dev/source/eval_retrieval.py`+`eval_queries.json`（roadmap R1，25 短 query、可 diff、容 tie flip）、`dev/source/check_source_titles.py`（第 5 監察／Method C 封面核對）。**LIVE 驗**：eval PASS **12→14**、errors 0；`ict_guide` FAIL→PASS rank 0 @0.624、`nonlocal` FAIL→PASS rank 2、`cgss` top 由 mislabel 0.568 → `cgss_sss_2021` **0.773 且 synthesis grounded**。**封面掃描首跑 192 源：冇第二個指錯文件**（17 flagged 全良性），副產品揪出 2 條真 404（`g01`/`ls_jss_2010`）+ 5 條 registry 寫 pdf 但 serve HTML。**修一個程序缺陷**：display-sync 全檔字串取代一直改寫 CHANGELOG／CODEBASE_CONTEXT **歷史條目**（S186 條曾寫成「15,656→15,901（淨+182）」算術不成立），已修正並將兩檔由 `execute_ingest.py` `DISPLAY_SYNC_TARGETS` 移除。**R5 sibling 審計（read-only）推翻舊假設**：`EDB-AI-Circular-System` 已 **PRIVATE**、另有 public `edb-circular-site`（拆分已完成）；兩 repo 全歷史 secret 掃描（85+594 commits）**乾淨**、public 站零後端碼零 runtime API。⚠️ **1 個未解、需 Leonard 決**：新源檢索命中但 synthesis 被 anti-confab judge 拒答（0.62–0.63 落喺 S183 `vault_extract ≥0.70` bypass 之下；已用控制組證實屬既有門檻行為非本次 regression；降門檻會重開 S177 confab 區間 0.55–0.65 = 安全取捨，故未自行改）。0 outstanding bug。
>
> **🆕 S193（2026-07-26）reconciled — 修「入庫但搵唔到」根因 + 令自動管道唔再靜默留債（backend 檢索修復，LIVE 驗證）：** HEAD==origin/main（S193 3 個 commit：**`ef426cc`** code 修復 → **`ffd7f22`** 治理持久化 → 本 closeout commit）；**Supabase 15,901**（+27 / 4 源，全部由 **Option A 管道自 S192 起無人手自動入庫**：`edbcm076_2026` 我的行動承諾 +8 / `edbc013_2026` 非本地兒童入學 +9 / `edbcm094_2026` 2026-27 教職員薪酬調整 +7 / `edbcm113_2026` 小學資訊與創新科技課程框架「人工智能初探」+3；bot commits `b791819`→`d310800`→`281b5f4`→`a94ec71`，本 session 起手 ff-pull 同步本地）；**source_registry 248**；平台 **v3.2.2** 不變（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 全零接觸、無 bump）。起手探針 4/4 綠（served app.html v3.2.2 + 標題 200 / Render `/health` warm 455 / HEAD==origin/main tree 乾淨 / Supabase count=exact 15,901）。**S193 = 逐條 live 探測 4 條自動入庫源 → 揪出 2 條連自己標題都檢索唔到 → Leonard 批「1＋2＋Monitor technology-edu 頁」→ 修根因 + 補機制 + 核實監察**。**根因（code-verified，比「route 擁擠」更深）**：`searchWiki` 向 Supabase 取**全庫** top-(top_k×5)=40，之後才在 JS 按 SOURCE_SET post-filter → 3–14 chunks 的新源要同全庫 15,901 chunks 爭 40 個位，**加 SOURCE_SET／TOPIC_KEYWORDS 結構上救唔到**（實測 edbcm094 對自己標題 cosine 0.722 卻完全唔出）。**修法**＝沿用 S174 footnote overlay 同一結構：`searchSpotlightSources()` 對 `SPOTLIGHT_SOURCE_IDS` 做 route/ANN 獨立 exact-cosine，未可見則給 **1 個 lead slot、門檻 0.60**（實測定：on-topic 0.62–0.72 vs **20 條敵意 off-topic 最高 0.563**，收 0/20 敵意；低分 merge 刻意唔做）；raw-query embedding 兩個 overlay 共用故 **embedding 呼叫數不變**。**機制**＝`execute_ingest.py` 新步驟 **4b** 自動註冊新源入 spotlight（`ack:spotlight` marker 為插入點）+ `post_deploy_smoke` 由「印個無人睇的 bool」改為**真閘**（多 phrasing 探測、報 rank、搵唔到即發 `::warning::` annotation，仍非 fatal）。**LIVE 驗**：目標源 **6/6 PASS**（edbcm113 rank 0；edbcm094 rank 2 ×3 phrasing；edbcm066 rank 2 ×2）+ synthesis grounded；**live 回歸 13 條：spotlight 污染 0/13、既有預期 5/5、9 條仍有 footnote 參與**；A/B 14 條 12 相同，2 條差異經隔離測試證與本改動無關（見 SESSION_LOG S193）。**S186 兩條 monitor 半解**：edbcm066 ✅ 修好；edbcm073 仍唔出（chunk 對「電子學習撥款」只 0.458，低於 bar，屬設計邊界）。**Monitor 核實**：Leonard 指定嘅 technology-edu 課程文件頁**早已在 discovery watch list**（62 頁之一，無需新增）；對該頁 11 個文件連結 diff 揪出 **2 條未入庫**——`IIT_Summary on AI_TC.pdf`（= edbcm113 通函公布嘅框架**正文**，561KB/200）+ `ICT_C&A Guide_c_final.pdf`（2.6MB/200）→ 待 Leonard 決定入庫。0 outstanding bug。

> **🆕 S192（2026-07-05）reconciled — 系統分析 + 改進路線圖 deliverable（read-only，零 code/data 改動）：** HEAD==origin/main **`a47eedf`**（= S191 closeout docs commit，本 session 之後接一條 closeout docs commit）；起手 live 探針 **4/4 綠**（served app.html `PLATFORM_VERSION 3.2.2` + title「香港學校政策搜尋平台」HTTP 200 / Render `/health` cache_a warm=true size=455 / Draft HEAD==origin/main、tree 乾淨 / Supabase **15,874** 文檔值未直連）；registry **244**、平台 **v3.2.2**、凍結合約全不變。**S192 = Leonard「分析及規劃現時系統功能同方向、改進空間，hands-off、寫成日後 claude agent 可執行嘅 deliverable，然後收工」**（頂層 dormant root「開工」→ redirect Draft → 跟 Draft §1 startup + 起手探針 → 交付分析文件 → 收工）。**交付：`dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`（NEW）** —— read-only 分析（無改任何 code/data），提煉自 PMS 全文 + CODEBASE_CONTEXT + S191 baseline + app.html/server.ts code 核實。內容：現時功能全圖（8 桌面 tab + 11 backend routes 落地核實）、系統健康評估、產品方向 A/B 觀察、**8 個已排序改進項 R1–R8**（每項帶 risk/工作量/首步/Leonard 決策/相關檔案）、不變量護欄、roadmap 執行次序。**建議即刻無悔項：R1 檢索 eval harness baseline + R5 sibling Circular System 安全審計（read-only）；待 Leonard 一句定產品定位 A/B → R2 IA 收斂。****本 session 零產品改動**（純分析文件 + 治理持久化）；backend/Supabase/凍結合約/PLATFORM_VERSION 全零接觸；頂層 dormant root 文件層面零接觸（redirect 仍 valid）。0 outstanding bug。

> **🆕 S191（2026-06-29）reconciled — GitHub 電郵收嘈（CI workflow 通知收斂）：** HEAD==origin/main **`e9fa583`**（S191 1 commit：`new_circular_check.yml` 停每日 cron + `served_url_check.yml` 加 @mention；push、Pages/Render no-op redeploy）；Supabase **15,874** 零接觸；registry **244** 不變；平台 **v3.2.2**（凍結合約全不變、無 bump）。**S191 = Leonard「GitHub 電郵太多，只想留最重要」→ 揀「只留最重要」收斂程度 → 兩槓桿並用**。查到 6 個 workflow 產生電郵（全部已「有發現先郁、綠色跑唔出聲」）：①ops `approval-issue.yml`（每日 @你批准候選，最重要）②主 `new_circular_check.yml`（每日，**同①重複**）③主 `served_url_check.yml`（每週，連結壞）④主 `freshness_check.yml`（每週，改來源）⑤主 `discover_check.yml`（每週，多噪音）⑥ops `executor.yml`（只失敗先 email）。監察更新已開 Issue 係**靜默改 body（唔 email）**，只第一次開 Issue 先 email。**槓桿 B（我改 code）**：(1) **退役 `new_circular_check.yml`**——停每日 cron（保留 `workflow_dispatch` 後備、加 RETIRED 註解指向 approval-issue.yml），因已被 ops `approval-issue.yml` 完全取代（掃同一 feed + checkbox 批准 + @mention-on-new）；即少一條每日重複 email。(2) **`served_url_check.yml` body 頂加 `@Leonard-Wong-Git`**——令連結壞咗（真故障）即使 Watch=@mentions-only 都照 ping；無壞唔開 Issue 嘅 gating 不變、Issue 持開期間靜默 update 唔 re-ping。**唔郁** `executor.yml`（關鍵管道，失敗由 GitHub Actions failure email channel 兜）/`freshness`/`discover`（靜音即可）。**QC**：兩檔 YAML valid；new_circular triggers=[workflow_dispatch] only（0 active cron）；served_url triggers=[schedule,dispatch] + @mention 1 處 + broken<1 gating intact；只動 2 檔、其餘 4 workflow 零接觸。**槓桿 A（Leonard 已做，github.com）**：兩 repo（edb-knowledge + edb-knowledge-ops）Watch → 「Participating and @mentions」+ Settings→Notifications→Actions 保留 failed-workflow email。**最終結果 = 只收 3 類 email：①批准入庫候選（@你）②連結壞咗（真故障 @你）③pipeline 跑失敗（Actions channel）**；freshness/discovery/重複 new_circular 全靜音（Issue 仍建立、上 repo 自睇）。0 outstanding bug。

> **🆕 S190（2026-06-29）reconciled — Option A 自動入庫管道 Phase 3+4 SHIPPED + 端到端 VERIFIED LIVE（2 次全自動入庫成功：edbc007 經 manual run、edbcm096 經 Issue 剔掣批准）：** HEAD==origin/main **`0f2e6c8`**（最新 = off-by-one 修；executor bot commits `87997f1` edbc007 +30、`7ce3e9f` edbcm096 +6；之前 main S190 commits `328b411` Phase 3 wiring → `8cdc107` Phase 4 circular_number → `50c61f5` failed-step 修；後接 closeout docs commit）；**ops repo `Leonard-Wong-Git/edb-knowledge-ops`（private）HEAD `4bd9a00`**（6 檔：README/APPROVAL_FORMAT/approvals{_TEMPLATE+edbc007 demo，帶 circular_number}/`.github/workflows/executor.yml`〔active、workflow_dispatch only、cron 仍註解〕/.gitignore）。**Supabase 15,838 → 15,868（edbc007 +30）→ 15,874**（edbcm096 +6，經 Issue 批准 loop）；**source_registry 242 → 244**；平台 **v3.2.2**（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 全不變——機械人只改 `_meta.stats.chunks` 15838→15868 display-sync）。**S190 = Leonard 自建 private ops repo → 我做齊 ②populate(git over SSH) ③wire `--live` ④`executor.yml` → Leonard 加 3 secrets → 跑 demo 端到端驗成功**。`execute_ingest.py --live` = 6 步真執行（copy-to-vault〔header topic 改 effective〕→ registry-append〔idempotent〕→ ingest_one_source〔embed+INSERT，upsert by PK〕→ route-patch〔route 缺則 raise〕→ display-sync 9 檔〔state-gated〕→ commit+push）+ post-deploy smoke；三重閘＝approval `decision==approved` + secrets pre-flight〔無 key→exit 3 inert〕+ idempotent/resumable `execution_state.json`。`executor.yml`（ops workflow）= scan approvals → `prepare_ingest_package.py --ids <circular_number>` **由 feed 確定性重生 package**（解決主 repo `ingest_packages/` gitignored；integrity 取捨：執行時重抽，EDB 通告穩定+dupe-check 緩解，要 byte-pin 改批准時 snapshot）→ copy approval → `execute_ingest --live`（PAT-auth checkout 自行 commit+push 主 repo → Render+Pages redeploy）。**首跑 bug + 修**：第一次 run fail（19s，step 3 `ingest_one_source.py exit 1`＝runner 缺 `openai` package，workflow 只裝 requests/pymupdf；embed 喺 INSERT 前死 → 零 leaked insert、零 push、可逆）→ 修 `pip install requests pymupdf openai`（ops `4bd9a00`）+ 修 exec_live failed-step 偵測次序報最早未完成步（main `50c61f5`）→ **re-run 成功**：bot commit `87997f1`、Supabase edbc007=30 / 總 15,868、registry 243、searchChannelB.ts:335 edbc007 入 activity route、vault extract 建、display-sync 9 檔、凍結合約 intact。**live 驗**：Channel B「開放學校設施 推動體育發展」→ edbc007 **rank 1/2/3**（0.71/0.64/0.64）+ synthesis grounded。**S190 後續（同 session）**：✅ **cron 已開**（`executor.yml` `0 12 * * *` = HK 20:00 每日自動，ops `401a9b1`）+ **加 idempotency guard**（已喺 main registry 嘅 source 直接 skip、唔 re-ingest、唔漂 chunk count → 解決 stale approval / cron 重撞 edbc007 問題；workflow summary 加 `skipped` count）。✅ **更新日誌（index.html modal + update_log.json）精簡定案**（main 至 `a4cc3f2`）：經兩輪——先改多來源 link，Leonard 睇完反饋「完全不顯來源 link」→ **最終 = 每條只顯 日期+標籤+標題+簡潔描述,零 link**；移除「（共 N 個知識片段）」「text-layer 逐字抽取/可追溯頁碼」「（首份經自動入庫管道入庫）」等雜訊/技術/內部字眼；`update_log.json` entry schema 收為 `{date,action,title,desc}`（URL 唔再存日誌、registry 為來源真源）；加咗 edbc007 entry。preview 實測 8 entry、0 link、0 雜訊。✅ **批准 UX = Issue 剔掣／留言批准 BUILT**（Leonard 揀此方向）：`approval-issue.yml`（ops repo `799723a`，GITHUB_TOKEN only、無新 secret）—— **refresh** job（每日 11:30 UTC + manual）跑 `check_new_circulars.py` 砌私密 Issue「📥 待批准入庫候選」（label `option-a-approval`，每候選一 checkbox + PDF link + 信號）；**approve** job（issues edited / issue_comment）剔 box = 批准（auto 建議）或留言 `/approve EDBC007/2026 route=activity` = override → 寫 `approvals/<id>.approval.json` decision=approved + commit + dispatch executor + Issue 回覆。**✅ 端到端 VERIFIED LIVE**：Leonard refresh→建 Issue「📥 待批准入庫候選」(20 候選) → 剔 EDBCM096/2026 → approve job 寫 `edbcm096_2026.approval.json`+commit(ops `fdb654a`) → executor 自動入庫 (bot commit `7ce3e9f`，route=finance T2) → Supabase edbcm096=6。**揪出 + 修 off-by-one bug**：executor commit 原寫「+7→15,875」但 Supabase 實際 6/15,874 —— `plan_chunks` chunk staged extract 時冇 strip `# header`(真 ingest `load_vault_sources` 有 strip)→ delta 多 1(edbc007 啱啱唔受影響故首次冇暴露；edbcm077/101 實測 8→7、4→3)。修：plan_chunks strip header + exec_live 改用 **live Supabase source count 做權威 delta**(免再漂)；9 display-sync 檔 15,875→15,874 修正(main `0f2e6c8`)。⚠️ GITHUB_TOKEN dispatch executor 若被抑制，每日 cron(12:00 UTC) 兜底(本次有觸發成功)。**🔜 餘下（非阻塞低優先）**：(1) ✅ **executor 自動寫 update_log**（每次入庫 prepend 一行 entry：標題=文件名+格式化通告號、desc=首句截短、idempotent by title、隨 ingest commit；edbcm096 已補；更新日誌精簡定案＝每條一行、無 link、無 synopsis）；(2) write-back annotate ops approval（commit/chunk delta）未 wired；(3) refresh 重寫 Issue body 會重置未入庫候選嘅剔號（cosmetic，approval record 已存、executor cron 兜底）。0 outstanding bug。

> **🆕 S189（2026-06-28）reconciled — Option A 自動入庫管道 Phase 2（dry-run executor + 批准格式 + ops scaffold）BUILT + QC：** HEAD==origin/main（S189 commit：`execute_ingest.py` + .gitignore）；Supabase **15,838** 零接觸；registry **242** 不變；平台 **v3.2.2**（凍結合約全不變、無 bump）。**S189 = Leonard `/goal 1` → 推進 Option A Phase 2**（接住 S188 Phase 1 staging）。起 **dry-run executor `dev/source/execute_ingest.py`**（tracked）：接 staged package → 模擬 6 個 live 步驟（copy→vault / registry-append / ingest chunk〔重用 canonical chunker，唔 embed/INSERT〕/ route-patch〔searchChannelB.ts SOURCE_SETS 定位+preview〕/ display-sync〔knowledge `_meta.stats.chunks` before→after × 9 touch-point，raw+逗號兩格式〕/ commit msg）→ 寫 `execution_plan.json`；**批准 gate**（approval `decision==approved` 先得，否則標 WOULD-BLOCK；**live 模式 hard-refuse exit 2**＝Phase 3 未 wired）+ human overrides（topic/route/tier）。**+ ops repo scaffold `dev/source/ops/`**（gitignored、未來 private `edb-knowledge-ops` 種子）：README（架構 + 為何 hosting public/批准 private + Phase 3/4 Leonard 設置清單）+ APPROVAL_FORMAT.md + executor.yml.template + approval 模板 + DEMO record。**QC：** py_compile ✅ + 3 staged package（edbc007 finance/T1 +30、edbcm077 activity/T3 +8、edbcm101 placement/T3 +4）全跑通 + 完整批准流程示範（init→approve+override route finance→activity→GATE ⛔→✅、route-patch 改指 activity block）+ live hard-refuse 驗 + **零 live 寫入核實**（vault 無建 dir / registry 242 / knowledge 15838 / searchChannelB.ts diff 空）。**Phase 2 = LOW risk、純 staging、可逆。Phase 3（wire --live）+ Phase 4（executor.yml 排程）需 Leonard 先開 private repo + PAT + secrets**（清單見 `dev/source/ops/README.md`），屬 HIGH risk。0 outstanding bug。

> **🆕 S188（2026-06-28）reconciled — Option A 自動入庫管道 Phase 1（包生成器）BUILT + 測試：** HEAD==origin/main（S188 commit：`prepare_ingest_package.py` + .gitignore + docs）；Supabase **15,838** 零接觸；registry **242** 不變；平台 **v3.2.2**。**S188 = Leonard「做埋」→ 揀只起 Option A（唔郁 live 站、唔轉 private）→ 起 Phase 1 包生成器**（`dev/source/prepare_ingest_package.py`，STAGING-ONLY、零 live 寫入 = 唔掂 Supabase/git push/vault/deploy）。今日手動 pipeline 腳本化:fetch feed → 下載 PDF → text-layer probe（image/OCR 自動 hold）→ PyMuPDF verbatim 抽 canonical extract（同 ingest_one_source 格式 byte-identical）→ dry-run chunk（count + page-resolvable）→ **dupe-check vs registry** → 自動建議 source_id/topic/route/tier（重 lean dashboard 嘅 urgency/compliance/k1_topics）→ attach deadlines/grant_info/channel_b_facts gap → 寫 `dev/source/ingest_packages/<id>/package.json` + extract + INDEX.md（staging，gitignored）。**QC：** py_compile ✅ + 實測 4 候選（EDBCM080 今日已入 → DUP 正確 skip；EDBCM077 卓越教學獎 → T3 event；EDBCM101 測驗日期 → T3+placement；EDBC007 體育計劃 → T1 borderline）全部 extract+chunk+page-resolvable 正確、deadlines 全捕捉。**Phase 1 = LOW risk、純 staging、可逆。下一步 Phase 2-4 需 Leonard 參與**（建 private ops repo + 批准格式 + executor dry-run → cross-repo token/secrets + live executor → 端到端串通），屬 HIGH risk、每 phase 落 sub-PLAN。0 outstanding bug。

> **🆕 S187（2026-06-28）reconciled — 安全加固（API abuse surface）：** HEAD==origin/main **`d12a2c2`**（S187 1 commit：API hardening；push、Render auto-deploy LIVE 驗）；Supabase **15,838** 零接觸；registry **242** 不變；平台 **v3.2.2**（凍結合約全不變、無 bump）。**S187 = Leonard 問「PolicyChecker 核心放 GitHub 是否人人可取用 / 15,838 chunks 會否被 clone 走」→ 開 12-agent 安全審計 workflow（5 維度並行 + 每發現敵意覆核，全程 read-only）→ 修 1 HIGH + 2 MED**。審計結論：(1) repo `Leonard-Wong-Git/edb-knowledge` **PUBLIC**（GitHub Pages 免費 plan 所需）→ 成個 tree + git history world-readable；**sibling `EDB-AI-Circular-System` 都 public**（circular.wongfu.net dashboard 來源）。(2) **Secrets 全清白** ✅：Supabase service key / anon key / OpenAI key 從未 commit（`backend/.env` gitignored + git history 零 JWT）。(3) **15,838 chunks 本身保護良好** ✅：住 Supabase 非 repo、anon key 不在 repo/前端（直連 REST 401）、無 write endpoint、sync endpoint X-Sync-Key gated、Channel B 每 query top-8 + 大 top_k 拒 → 唔易整批 clone。**修咗：** 🔴 rate-limit XFF spoof denial-of-wallet（`getClientIp` 改右 hop + `GLOBAL_RATE_LIMIT=120/min` backstop）+ 🟠 search/analyze-circular body cap 16KB/MAX_TEXT_CHARS + 413（防 memory DoS）+ 🟢 Channel A `min_score` floor 0.05 + result cap 50（防 `min_score:0` 一 call dump 455）。**本地測 3/3 PASS（min_score:0→50 / oversized→413 / 11req→429）+ tsc 0 + prod LIVE 驗（min_score:0 由 455→50、正常搜尋 8 results+synthesis top=edbcm080_2026、oversized→413、health warm 455）。** ⚠️ **未修（Leonard 揀只修 API、其餘留 backlog）**：🟠 backend IP 全公開（SOURCE_SETS/keywords/prompts/judge/thresholds + source_registry 242 + dev/vault 19MB verbatim）= 競爭者可照藍圖 rebuild（修法=repo 轉 private，同 Option A private-repo 方向合一）；🟢 `schema.sql` RLS-off + anon SELECT（潛在，若 anon key 將來漏可繞 proxy dump table；defense-in-depth 建議開 RLS / anon RPC-only）；🟢 Channel A 455 + curation blueprint public-by-design；sibling repo 待同樣審。0 outstanding bug。

> **🆕 S186（2026-06-28）reconciled — 數字以本段為準（下面 S185 及更早為歷史背景）：** HEAD==origin/main **`b79f475`**（S186 1 commit：ingest+route+display-sync+docs；push、Render auto-deploy(On Commit) + Pages redeploy 全 LIVE 驗；後接 closeout docs commit）；Supabase **15,656 → 15,838**（淨 +182 `vault_extract` chunks，14 新源）；source_registry **228 → 242**（+14）；平台 **v3.2.2** 維持（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 全不變、無 bump）。**S186 = 第 4 監察 (S185 new-circular watcher) 首次真實捕捉 → 14 條 2026/6 EDB 通告／通函批次入庫（Tier 1+2）LIVE**。Workflow：頂層 dormant root「開工」→ redirect Draft → 起手探針全綠（HEAD `c545bea`==origin/main、app v3.2.2、Render warm 455、Supabase 15,656）→ Leonard 手動行收到 watcher email（GitHub Issue #3，29 條候選）→ 我 dupe check + K1 triage（Tier 1 核心 6 / Tier 2 撥款 8 / Tier 3 過渡 15）→ AskUserQuestion → Leonard 揀 **Tier 1+2=14** → 跟 S181/S183 pipeline：14 份 PDF 全 text-layer（無 OCR）→ PyMuPDF verbatim 抽（canonical header + `=== Page N ===`、NUL=0）→ dry-run chunk（182 全 page-resolvable、char med ~590）→ 逐源 INSPECT before=0（查重）→ live INSERT 182 → **searchChannelB.ts 9 route SOURCE_SETS + keywords + activity 提升至 finance 之上**（防「家校合作活動整合津貼」被 finance「津貼」偷）→ tsc 0 + routing smoke **21/21** → registry 242 + display-sync 7 處 + update_log + CHANGELOG → push `b79f475` → Render+Pages redeploy → **live verify 12/14 源 top-8 surface 全帶 synthesis**。14 源 chunks：edbcm080(14)/edbcm060(68)/edbcm088(5)/edbcm081(7)/edbc010(5)/edbc012(3)/edbc009(9)/edbcm070(10)/edbcm089(15)/edbcm073(12)/edbc011(5)/edbcm066(14)/edbcm107(10)/edbcm095(5)。**起手探針**：served app.html=200 + PLATFORM_VERSION 3.2.2 + Render `/health` cache_a warm=true size=455 + HEAD==origin/main `b79f475`（後接 closeout docs commit）+ Supabase **15,838**。⚠️ **2 源 monitor**（in-route 可檢索但短 query crowded-route 排名低，S152 cgss 同類，非遺失）：edbcm073_2026（電子學習撥款，被 digital_education 嘅 DEBP/AI corpus 0.69-0.73 擠出 top-8）+ edbcm066_2026（準英語教師獎學金，被 hr_admin sag/g04 0.73 擠出；fuller query 可 surface rank-7）→ Leonard 報 miss 先 boost。⚠️ 餘下 29 條未入嘅 15 條 = Tier 3 過渡公告（活動/比賽/日期/獎項），按 S170 鐵律不入。⚠️ Render free-tier cold-start ~50s。0 outstanding bug。

> **🆕 S185（2026-06-28）reconciled — 數字以本段為準（下面 S184 及更早為歷史背景）：** HEAD==origin/main **`a99ce48`**（S185 4 commits：`41ce199` index.html footer 加設計者 → `7bca227` app.html footer 移除設計者 → `5dca4cf` 第 4 監察 watcher → `a99ce48` cron 改 HK 19:30；全 push、Pages + Actions LIVE；後接 closeout docs commit）；Supabase **15,656** 零接觸；source_registry **228** 不變；平台 **v3.2.2** 維持（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 全不變、無 bump）。**S185 = 設計者 credit（index.html only）+ scratch 大清理 + 第 4 監察「EDB 通告 dashboard watcher」SHIPPED LIVE + Option A 自動入庫方向定案（下次起）**。Workflow：頂層 dormant root「開工」→ redirect Draft → 起手探針全綠（HEAD `e55eb3f`==origin/main、app v3.2.2、title 統一、Render /health warm 455）→ Leonard 4 點 →（1）**index.html footer 加「· 設計者：Leonard Wong」**（app.html footer 原有「設計及維護：Leonard Wong」按 Leonard 指示**移除**，credit 只留首頁；live 驗兩頁；依 Leonard 指示**不入 CHANGELOG/update_log**）（2）解釋 Open Priorities = backlog（非 bug）（3）**清 19 個 untracked scratch**（原 flag 2 個 + research/_s179/_s181 目錄、footnote_harvest×5、.pre 備份、vault/_s184、discovered/freshness/served_url changes；全 untracked、working tree clean）（4）**detect 機制問答 → 揭 gap → 建第 4 監察**：查實 discover 只爬 registry 已知 .html landing（62 個全主題頁、**冇一個係 EDB 通告總索引**）+ freshness 只監察已入庫源 → 新通告（如學校效率津貼 EDBC 8/2026）**結構上 detect 唔到**（實測 debp.html 冇 link 住）→ Leonard 提供 **`https://circular.wongfu.net/circulars.json`**（佢自己個「EDB 通告智能分析系統」每日 feed，174 條，含 number/date/title/全文/topics/**pdf_urls**/deadlines/grant_info/**k1_topics**/**channel_b_facts** 等 K1-aligned 欄）→ **建 `dev/source/check_new_circulars.py` + `.github/workflows/new_circular_check.yml`**（fetch feed → PDF basename diff registry → isNew 或近 N 日 + 唔喺 registry = 候選 → 開/更新 `new-circular` GitHub Issue；detection-only、人手 verbatim 入庫閘不變、零 secret）→ **QC：compile+run ✅、撈到 29 條真候選、反向對照（registry 排除 EDBC26008C.pdf）證實會捉到「學校效率津貼 isNew=true」✅、YAML valid、workflow GitHub 註冊 active**；cron 設 **每日 11:30 UTC = HK 19:30**（feed ~HK 18:57 生成後先讀，避 stale）。**起手探針**：served app.html=200 + PLATFORM_VERSION 3.2.2 + Render `/health` cache_a warm=true size=455 + HEAD==origin/main `a99ce48`（後接 closeout docs commit）+ Supabase **15,656**（零接觸）。⚠️ Render free-tier cold-start：起手 /health 可能 warm=false、輪詢即升 455=良性。⚠️ **Option A（一鍵批准自動入庫管道）下次專注 session 正式 PLAN**：Leonard 揀 A，但揭發**公開 repo 隱患**——policychecker.wongfu.net 經 Pages 可反查到 `Leonard-Wong-Git/edb-knowledge`（public，Issues 全世界睇到）→ GitHub Issue 做批准面**唔真私密** → 定案修法 = 營運/批准搬去**新 private repo**（hosting 公開、批准私密）。#2 時效 + #3 識分 已大半可由 dashboard 現成欄解（deadlines / k1_topics / channel_b_facts gap）。0 outstanding bug。

> **🆕 S184（2026-06-26）reconciled — 數字以本段為準（下面 S183 及更早為歷史背景）：** HEAD==origin/main **`3d856a2`**（S184 2 commits：`c08f6de` ingest+route+display-sync → `3d856a2` index.html 單一真源整理；全 push、Pages + Render auto-redeploy LIVE 驗）；Supabase **15,644 → 15,656**（淨 +12 vault_extract chunks，`edbc008_2026` 學校效率津貼 topic=it、page-resolvable）；source_registry **227 → 228**（+1 new source）；平台 **v3.2.2** 維持（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines.json 2.6.1 公開 158 全不變、無 PLATFORM_VERSION bump）。**S184 = 教育局通告第8/2026號「學校效率津貼」入庫 + index.html 單一真源整理（2 項全 LIVE 驗）**。Workflow：頂層 dormant root「開工」→ redirect Draft → 起手探針全綠 → Leonard「加入 EDBC26008C.pdf 分析入庫更新日誌；有剩 token 修 index.html 2 個單一真源問題」→ **入庫**：下載通告第8/2026號(10 頁，學校效率津貼=2026/27 起設立、支持教育數字化轉型、配合《數字教育發展藍圖》DEBP) → **grep dupe check 0 hit**（吸取 S183 duplicate ingest 教訓、入庫前查重）→ PyMuPDF `get_text()` verbatim 直抽 → canonical chunker(600/60 page-carry) 12 chunks 全 page-resolvable(char med 588) → `ingest_one_source.py edbc008_2026` live INSERT(INSPECT before 0 → after 12) → total **15,656** exact → backend `digital_education` route 擴充(+SOURCE_SET `edbc008_2026` + TOPIC_KEYWORDS 加 `學校效率津貼|效率津貼|學校效率|教育數字化|數字化轉型` 維持 finance 之上 first-match 防被 finance「津貼」偷 + QUERY_EXPANSIONS) → tsc exit 0 → push `c08f6de` → Render redeploy → **live query「學校效率津貼」HIT rank-3/4 + synthesis grounded**「學校效率津貼於2026/27學年正式推出…加快推動教育數字化轉型」✓ → display-sync 7 點 + CHANGELOG + update_log。**index.html 單一真源整理**(Leonard 2 flag)：(1)版本號自打交 — hero eyebrow `v3.0·2026` + footer `v2.3` 同頁兩個版本號違反單一真源 → 收斂為**頁面單一** footer `v3.2.2`(對齊 app.html PLATFORM_VERSION)、eyebrow 移走版本號；(2)四個平台名並存 — hero eyebrow 第4個 stray「資助學校管治平台」(contradicts 定位) → 定位描述「香港資助學校·EDB 政策知識庫·2026」，收斂成「香港學校政策搜尋平台」(產品正名)+「PolicyChecker/政策核對」(品牌標記)一對 → preview eval+screenshot 驗(eyebrow/footer 正確 + landing 統計帶 live 顯示 15,656) → push `3d856a2`。**③ 統一所有對外標題（closeout 後追加，push `ce9b9d6`）**：Leonard「share / add to home screen / WhatsApp / browser 標題都要統一」→ 發現 4 個唔一致標題（index.html title=「EDB 學校政策搜尋平台」、app.html title=「搜尋工作室」、og:site_name=「PolicyChecker·政策核對」、body=「香港學校政策搜尋平台」）→ 統一所有 `<title>`/og:title/twitter:title + 兩頁加 `apple-mobile-web-app-title`+`application-name`（加到主畫面 home-screen 標籤）為**香港學校政策搜尋平台**；WhatsApp share brand 已係此名(S183)不變；og:site_name 維持「PolicyChecker」品牌對(S184 accepted)；preview eval 驗兩頁 4 標題面全 = 香港學校政策搜尋平台。**起手探針**：served app.html=200 + PLATFORM_VERSION 3.2.2 + browser title「香港學校政策搜尋平台」+ Render `/health` cache_a warm=true size=455 + HEAD==origin/main `ce9b9d6`（後接 closeout docs commit）+ Supabase **15,656**。⚠️ Render free-tier cold-start：起手 /health 可能 warm=false size=0、輪詢十幾秒升 455=良性（S184 起手親見）。⚠️ §4a SESSION_LOG archive 已執行（685→186 行、11 entries 入 `dev/archive/SESSION_LOG_2026_Q2.md`、清咗自 S180 defer 5 次嘅債）。0 outstanding bug。

> **🆕 S183（2026-06-25）reconciled — 數字以本段為準（下面 S182/S181/S180 及累積 baseline 為歷史背景）：** HEAD==origin/main **`4ddffb6`**（7 commits chain `bc26d41`+`edebbbd`+`40923d5`+`a718a83`+`1359916`+`71f1c80`+`4ddffb6` 全 push、Pages #398 + Render auto-redeploy 全 LIVE 驗）；Supabase **15,536→15,649→15,644**（淨 +108 vault_extract chunks：3 source INSERT 113 → post-INSPECT 揭發 duplicate hard-delete 5 chunks）；source_registry **225→227**（+2 effective new sources，去咗 1 duplicate post-discovery）；平台 **v3.2.2** 維持（凍結合約 `_meta` 2.3.0 / facts 455 / guidelines.json 2.6.1 公開 158 全不變、無 PLATFORM_VERSION bump）。**S183 = 《價值觀教育課程架構》(2026) 正式版 + EDBC 3/2026 通告 + EDBCM 221/2025「『智』啟學教」AI 撥款計劃入庫 + multi-issue debug + 2 governance rules ship + brand fix + Pages outage 救活**。Workflow：Leonard 指出 EDB 4 key tasks 之一嘅 value education framework 由 2021 試行版升到 2026 正式版 registry 缺 → AskUserQuestion Option A scope（主框架 only + 配套通告 + 2021/2023 supersede 標注 retain）→ Leonard 中途加 EDBCM 221/2025 piggyback（AI 撥款 topic=it）→ download 3 PDFs → `_extract_s183.py` pymupdf 抽 text 入 canonical vault → registry update + supersede mark → **adversarial subagent verbatim review GO-as-is（programmatic per-page parity 103/103 pages 0 divergence；12 首要價值觀 + 5 章節 + 中華經典引文 byte-exact）** → live INSERT 93+5+15 = 113 chunks → 15,649。**Post-INSERT 揭發 3 issue + 2 governance rule + 1 brand fix + 1 Pages outage**：(a) **Duplicate ingest** — prior session 已 ingest `edbc003_2026` (6 chunks, 同份 PDF, registry title 短「教育局通告第3/2026號」未含 value education keyword、我 grep 漏 catch) → hard-delete 我新 `edbc_3_2026_values_edu` 5 chunks，retain prior；15,649→15,644。(b) **Routing surface fail** — VE_CF 主框架 chunks 不在 top-8 + EDBCM 221 被 finance route 偷「智啟學教 撥款」query → backend `searchChannelB.ts` 加 dedicated `value_education` route SOURCE_SETS (VE_CF_2026 + edbc003_2026 + values_edu_framework_2021_trial + edbcm183_2023_values_edu + sec_curr_guide_2017_booklet_6a) + 擴 `digital_education` SOURCE_SETS +`edbcm_221_2025_smart_teaching` + 兩者 TOPIC_KEYWORDS（價值觀／首要價值觀／立根中華／智啟學教／數字素養／12 首要 等）+ QUERY_EXPANSIONS + **提兩者到 finance 之上（first-match precedence 解 finance「撥款」keyword 偷 query）** → routing smoke 12/12 PASS（5 value_education + 3 digital_education + 4 regression：finance/curriculum/gifted/school_governance 行為不變）→ Render redeploy + 8 live query 7/8 PASS（1 fail = query 含「試行版」誤導 keyword 命中 2023 試行版 enrich，語義合理）。(c) **Synthesis judge fail（Leonard mobile screenshot 反饋）** — 「智啟學教是什麼」EDBCM 221 rank-0 score 0.750 + 「價值觀教育」VE_CF 2021 rank-0 score 0.794 仍俾 anti-confab judge over-decline「未能找到」→ S178 footnote-lead bypass 只 cover footnote_curated → **擴 `VAULT_LEAD_SCORE = 0.70` for vault_extract**（S177 凍結教席→IMC-60% confab class 喺 0.55-0.65、≥0.70 已 empirically direct match）→ 3/3 query post-fix ANSWER + grounded synthesis。(d) **Governance rule 1：Supersede ranking penalty 0.05** — Leonard 提出「新文件版本應 ranking 優先 surface 過舊版」做 long-term rule → backend +`SUPERSEDED_IDS` Set + `SUPERSEDE_PENALTY=0.05` const + `applySupersedePenalty()` helper + apply 兩次（main results post-mapping + footnote overlay pre-lead-detection、re-sort 後）→ initial set {values_edu_framework_2021_trial, edbcm183_2023_values_edu} → 3/3 短 query (「價值觀教育」「首要價值觀」「12 首要價值觀」) VE_CF 2026 rank 0/1/2，2021 試行版 demoted rank-3+。SSOT = registry `superseded_by` field；ingest 新 superseding 版時 manually sync set（同 SOURCE_SETS pattern 一致）。(e) **Governance rule 2：Judge bypass extension** — S178 footnote-lead bypass 概念擴展至 vault_extract @ score≥0.70；保 protection for marginal (S177 confab class) 同時解 direct match (S183 case) judge over-decline。(f) **Brand fix** — Leonard 反饋 WhatsApp share text 第一行 brand 應跟 product banner = 「香港學校政策搜尋平台」not「EDB K1 知識平台」→ app.html line 2683 + mobile.js line 292 2 line edit（純前端 string swap）。(g) **Pages deploy transient outage** — commit `1359916` (supersede penalty) Pages workflow #397 deploy step 失敗 4s（build + report ok、單 deploy step issue）→ subsequent push `71f1c80` queued behind 失敗 #397 → empty commit `4ddffb6` 觸發 #398 success → 確認 transient outage（no persistent issue）→ standard remediation pattern「**empty commit retrigger**」記低做 future Pages outage 處理。**起手探針**：served app.html=200 + PLATFORM_VERSION 3.2.2 + 「香港學校政策搜尋平台 · 政策搜尋」brand live + Render `/health` cache_a warm=true size=455 + HEAD==origin/main `4ddffb6` + Supabase **15,644**（vault_extract +108 net）。**DOC_SYNC 9 點 + CHANGELOG + update_log.json + CODEBASE_CONTEXT AI Log + PROJECT_DECISIONS append + 本 handoff + SESSION_LOG**。⚠️ Render redeploy 4 次（route patch / judge bypass / supersede penalty / brand fix backend touch）+ Pages redeploy 3 次（ingest display-sync / fix display-sync / brand fix） 全 live verified。

> **✅ S182（2026-06-25）：WhatsApp 分享按鈕 SHIPPED，desktop + mobile 純前端、平台 v3.2.1→v3.2.2。** 政策搜尋整理答案 card 底加綠色「📤 分享至 WhatsApp」按鈕（synthesis-gated）；點擊開 `wa.me/?text=<encoded>`（mobile WhatsApp app／desktop WhatsApp Web）；訊息 compact format（綜合答案 + 來源 dedup top-5、每源 ≤3 pages、wa.me URL ~965 字）；source_id mapping fix（runChannelB/runCombined 帶 source_id 供 SOURCE_LABELS 用中文短名）。QC 7/8 PASS、1 DEFERRED（localhost CORS、live verify post-push 全 8/8 PASS）。**S183 brand fix update**：share text 第一行 brand 由「EDB K1 知識平台 · 政策搜尋」改正為「香港學校政策搜尋平台 · 政策搜尋」（跟 product banner 一致）。**Feature 2a 追問 + Feature 2b scoped Q&A 仍待**（per Leonard sequence A、共享 conversation UI）。commits `d2e4480`→`4433afe`（S183 brand fix on top）。

> **🔙 [S183 reconciliation 之前的 S182 baseline 完整 entry 已遷至「Previous Session Record (S182)」 — 見下方歷史 section]**

> **🆕 S182（2026-06-25）reconciled — 數字以本段為準（下面 S181/S180/S179 及累積 baseline 為歷史背景）：** HEAD==origin/main **`d2e4480`**（前 `eb751ac` S181 closeout 之上加 S182 feat commit）；Supabase **15,536** 零接觸（`footnote_curated` 206 不變）；平台 **v3.2.1 → v3.2.2**（user-facing `PLATFORM_VERSION` bump；凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S182 = WhatsApp 分享按鈕 SHIPPED（desktop QAPanel + mobile shell，純前端 frontend-only，零 backend／retrieval/synthesis 改）**：Leonard 同 session 繼續講「1 搜尋後以 WhatsApp share 結果，引用文件及頁數要非常簡潔；2 搜尋後追問或 base 文件再問」→ PLAN 拆三 feature（WhatsApp share／追問 multi-turn／文件 scoped Q&A）+ 提 sequence A/B/C → Leonard 揀 A「WhatsApp 先 ship」→ 5-step workflow（PLAN→READ→CHANGE→QC→PERSIST）。政策搜尋整理答案 card 底加綠色「📤 分享至 WhatsApp」按鈕（synthesis-gated，無 synthesis 不出），點擊開 `https://wa.me/?text=<URL-encoded>`（mobile 開 WhatsApp app／desktop 開 WhatsApp Web 揀 contact share）。訊息格式 compact per Leonard「非常簡潔」要求：`【EDB K1 知識平台·政策搜尋】 ／ 問：<q> ／ <綜合答案 ~250 字> ／ 來源：《SAG》 p.80 · 《採購指引》 p.12 · 《財務管理指引》 p.45 ／ 🔗 https://policychecker.wongfu.net/app.html`；source_id dedup + score-sort top-5 + 每源最多 3 個 page；wa.me URL 實測 ~965 字（WhatsApp 4096 字限大量 headroom）。**QC 7/8 PASS**（buildShareText 邏輯／desktop QAPanel button render #25D366 8px radius 13px/600 152×36／mobile shell button render #25D366 99px pill／synthesis-gated visibility／wa.me URL 長度／PLATFORM_VERSION 3.2.2 header 顯示／mobile-shell-active body class @ 375×812／Node syntax check on mobile.js），**1 DEFERRED**：localhost CORS 阻 live backend fetch → live verify 跟 push 後 prod 做（真 query → 確認按鈕出 + click 開 wa.me 帶正確文字）。**起手探針**：(post-push 待驗) served app.html=200 + PLATFORM_VERSION 3.2.2 + Render /health cache_a warm=true size=455 + HEAD == origin/main + Supabase 15,536 不變。**DOC_SYNC display-sync 6 點**：app.html / README badge+footer / CHANGELOG 新 v3.2.2 section / CODEBASE_CONTEXT AI Log / 本 handoff Current Baseline + Open Priorities / SESSION_LOG S182 entry。⚠️ Render 無需 restart（純前端、後端 byte-identical）；Pages auto-redeploy（push origin/main 觸發）。⚠️ `_meta.stats` 不變（純 UI 改、無 chunk 變動）。⚠️ **Feature 2a 追問 multi-turn + 2b 文件 scoped Q&A 待續**（Leonard 揀 sequence A 隱含後續分批做、共享 conversation UI、可一齊做）。commits 鏈 `d2e4480`(feat S182: WhatsApp share button + PLATFORM_VERSION 3.2.2 + DOC_SYNC 6 點)。

> **🆕 S181（2026-06-25）reconciled — 數字以本段為準（下面 S180/S179 及累積 baseline 為歷史背景）：** HEAD==origin/main **`cd47779`**；Supabase **15,536**（`footnote_curated` **206** ＝ S180 ×84 ＋ S181 ×122）；平台 **v3.2.1**（凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S181 = 8 angles agent team 大入庫（122 條 footnote_curated overlay，全 LIVE 8/8 Render verify rank-0/1 + synthesis grounded）**：Leonard「agents team 全部做、QC plan、QC審批、敵意審查」→ agent team workflow（Phase 1 = 9 並行 general-purpose research subagent verbatim 抽 180 candidates / Phase 2 = 2 並行 adversarial reviewer 做 verbatim spot-check + coverage/routing audit / Phase 3 = QC 合成 + 4 verbatim 修 + 5 redundant drop / GO Gate Leonard 揀 Option B = R1+R2 footnote sweep / Phase 4 = self-test 122/122 LEAD ≥0.45 〔1 條 re-tune 0.401→0.750〕→ live INSERT 122 rows 無 collision / Phase 5 = display-sync 8 點 + push + Render redeploy + live verify 8/8 PASS）。8 angles 入庫分佈：教師註冊 13（Cap.279 §42-§61 + TPC + supply）／學校註冊+DSS 10（§10-§14 + 2⅓ + 10%/50¢）／NCS 18（**EDBC 4/2026** Composite + 8/2020 5-tier + 9/2019 SEN + KG）／傳染病停課 15（**CHP 2025-Nov** + 20% ILI/7-day + 漂水）／學費減免 17（SFAA AFI + 2024/25 + KCFR + TA）／NET 18（**EDBC 8/2025** + HK$900k/$1M + IELTS 7.5）／校舍安全/EMSD 13（**EDBC 12/2026** + Cap.618）／SAG 附錄 14（病假 28→48→168 + 罰款表 + 利益衝突 10 例）。canonical source_id：Cap.279→`cap279_education_ordinance`、EDBC 10/2012→`edbc_10_2012_fee_remission`。**起手探針**：app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a warm=true size=455（Channel A 凍結不變）+ HEAD `cd47779`（==origin/main）+ Supabase **15,536**（footnote_curated 206）+ knowledge.json `_meta.stats.chunks` 15,536。⚠️ live Supabase 寫入＝安全閘 gated 要明確授權（本 session Leonard 揀 Option B = 明確授權 INSERT 122）。⚠️ 入/改 footnote 後必 restart Render（push 已觸發 redeploy、live 已驗）。⚠️ source_registry.json 26 新源 metadata 待 fold-in（minimal，列 backlog）；Phase 3 full_chunks_routed +4 新 backend route 待下次（reviewer B 估 ~60 chunk + 4 route：teacher_registration / ncs_support / net_scheme / safety EMSD keywords）。0 outstanding bug。commits 鏈 `cd47779`(S181 ingest + display-sync + CHANGELOG)。

> **🆕 S180（2026-06-24）reconciled — 數字以本段為準（下面 S179 及累積 baseline 為歷史背景）：** HEAD==origin/main **`79840e5`**（S180 收工 commit）；Supabase **15,414**（`footnote_curated` **84** ＝ S179 ×83 ＋ S180 ×1〔SAG §3.7.3 懷疑性侵犯轉介報警 overlay〕）；平台 **v3.2.1**（凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S180 一項 LIVE（Render verify overlay rank-1 + grounded synthesis）**：SAG 學校行政手冊版本核對 — EDB 已由 2025-11 換到 **2026-05 版**（markup/clean Last-Modified 2026-05-20、served 同檔名故結構上避過 served-URL/freshness 監察）；官方 Log_sheet 證自 2025-11 起唯一 delta=item 73（§3.7.3「與性有關的問題」）；逐字 diff 揭實質改動=1 新增段（懷疑性侵犯→須遵照社署《保護兒童免受虐待–多專業合作程序指引》、諮詢社署保護家庭及兒童服務課或警務處虐兒案件調查組、涉刑事須報警）→ 捕捉為 1 curated overlay（`footnote_fn_sag_sexual_abuse_referral`、url SAG_C_markup.pdf#page=80）+ registry `version_label` sag_2025_11/g24 → 2026-05 + display-sync 8 點。commit `fb1f8fc`（push）。**起手探針**：app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a warm 455（warm=false 多屬 free-tier cold-start、輪詢十幾秒即升 455＝良性，持續 0 先查 OpenAI billing）+ HEAD `79840e5`（驗 ==origin/main）+ Supabase **15,414**（footnote_curated 84）。✅ Side-finding（已調查 resolved）：SAG 雙重 ingest（`sag_2025_11` markup 383 + `g24` clean 383）由 **soft-dedup 妥善處理**（`wikiRepository` alias g24→sag_2025_11 + seen-Set dedup + 共用 per-source quota）、**無需 hard-dedup**；公開指引標籤亦已同步 2026-05（`guidelines.json` 2.6.0→2.6.1 + `app.html` GUIDELINES_REGISTRY，count 158 不變）。commits 全鏈 `fb1f8fc`→`e521dee`→`0707faa`→`7828f3e`→`2acf631`→`79840e5`(收工)。⚠️ 入/改 footnote 後必 restart Render（本 session push 已觸發 redeploy、live 已驗）。⚠️ live Supabase 寫入＝安全閘 gated，要 Leonard 明確授權。

> **🆕 S179（2026-06-23）reconciled — 數字以本段為準（下面累積 baseline 為歷史背景）：** HEAD==origin/main **`89eee3a`**；Supabase **15,413**（`footnote_curated` **83** ＝ S174 ×33 ＋ S177 ×26 ＋ S178 ×2 ＋ S179 ×22〔footnote 擴充 14 ＋ discovery 三快贏 8〕）；平台 **v3.2.1**（凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S179 四項 LIVE（全 verbatim 核 + live 驗）**：①**footnote 擴充第三批 14 條**（SAG 假期/HR 8〔病假 28→48 封頂168／肺病假 3/6/12月／侍產假5天產假14週／年假/緊急私事假/遴選委員會≤60%/受聘前胸肺X光/超額主任調配/改編學位教師〕＋ IMC免稅s.88／幼稚園租金九月計/每班最少1教師/戶外活動師生比例 ＋ forms 手尾 #7 CEG未上載追回 #18 CFEG家具無上限）→ Render live **6/6**；②**discovery 三快贏 8 條**（處理學校投訴×3／4Rs約章+三層應急機制×3／私隱條例Cap.486×2，route-independent overlay 無需改路由）→ Render live **8/8**；③**kg_operation 388 items + 162 clauses 補標 `['kindergarten']`** + bundle 重生（→1603KB）；④**TRG served-URL 404 修復**（`trg_imc_2023` 3 chunk url `en/...C.pdf`404→`tc/...c.pdf`200，Leonard「一次過做」明確授權）。commits `3897169`→`89eee3a`。**起手探針**：app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a warm 455 + HEAD `89eee3a` + Supabase **15,413**（footnote_curated 83）。⚠️ 入/改 footnote 後**必 restart Render**（footnote in-memory cache；本 session push 已觸發 redeploy、live 已驗）。⚠️ live Supabase 寫入＝安全閘 gated，要 Leonard 白紙黑字明確授權（「全部都做」covers footnote scope；新揪出嘅 production 寫入如 TRG 要逐個明確授權）。⚠️ OpenAI quota 曾用爆（已充值；warm=false 或搜尋 429 即查 billing）。

1. **Version / git**: **平台 v3.2.1**（user-facing `PLATFORM_VERSION='3.2.1'` in app.html，與凍結資料合約分離；S173：文件標註 off-domain 相關性下限〔guideline 0.62 + domain 0.45 floor〕+ OpenAI node-fetch 韌性修復）；資料合約 knowledge 凍結 @2.3.0、guidelines @2.6.0（`_meta.version` 不變）；git **`main` HEAD == `origin/main`（已 push `788538e`，S176 Agent Handoff Kit v0.1.7→v0.3.29 升級〔治理層，零產品改動，doctor 48/48〕；前 `5cb978d` S175 手機首次導覽 tour + checklist school_types 補標）**；Supabase **15,363**（S174 +33 `footnote_curated` overlay；S172 deprecate `sch_calendar_guide` −6；S171 +DEBP 209，新 `digital_education` route）。**⚠️ 起手 FIRST：探針 https://policychecker.wongfu.net/app.html HTTP 200 + PLATFORM_VERSION 3.2.1；再 verify HEAD==origin/main + Supabase 15,363 + Render /health（cache_a warm 455）。〔hosting 已穩定。〕** **S174（2026-06-21，Leonard /loop 自主 → 批 A live 入庫 → A 收工）：附件細字 footnote 入庫機制 SHIPPED LIVE — Leonard 指出 EDB 文件附件表格底細字（註/備註/footnote）藏住正文無講嘅實質要求（費用上限/資助級別/批核權/計算公式/安全門檻/法律定義/校曆/人手比例）→ 全庫 209 掃 footnote（1104→精煉 61→triage）→ 33 條策展入 Channel B（`content_type=footnote_curated`、15,330→15,363、INSPECT 齊、`id=footnote_*` 可逆）。揭發路由盲點（`searchWiki` RPC 後 `sourceIds` post-filter 丟 footnote + ivfflat probes=8 recall）→ 修 `wikiRepository.searchFootnotes`（exact-cosine overlay 繞路由/ivfflat）+ `searchChannelB` footnote pass（強配對 ≥0.45 lead 入合成窗、best-effort）；re-embed text+keywords。敵意 held-out 62%→75.8%→**live 100%**（synthesize 證原 hallucination〔代課批准亂作「30日」〕修正為真「6個月/大多數校董」）。display-sync 15,363；凍結合約零接觸、無 PLATFORM_VERSION bump。commits `8f2cace`→`9b3d8f9`.**S163QC（2026-06-14，Leonard 22:40 自啟全權）：v3.0 release QC 6 blockers NO-GO→GO。** P1 app.html header/footer displayVersion→PLATFORM_VERSION(v3.0.0,凍結 _meta 2.3.0 不變；local 驗,待 Pages 復原 live 驗)。P2 searchChannelB kg_admin route +幼稚園營運/營運手冊/運作/健康紀錄（**Render LIVE 驗**：query「幼稚園營運 手冊 健康紀錄」surface kg_operation_manual+kg_admin_guide，原 g26-only；export detectQueryCategory）。P3 checklistRevise graded 詞彙重疊閘（informative CJK-bigram，DF 自校準）+MAX_ITEMS 220→400（**Render LIVE 驗**：短 KG 文 covered 20→5/partial 55→30；richer 文 covered=37 無 false-neg；export cjkBigrams）。P4 README v3.0.0／P5 .gitignore 備份(不刪)／P6 mobile scope 文檔(search/guidelines/about；annotate+templates=desktop)。Regression 修 2 stale FAIL（schema 1.3.1→2.3.0/2.5.0；role-bucket→union both-roles）+P2/P3 cases=20 PASS/0 FAIL。commits `39e6df1`(backend)→`3f239bf`(frontend/docs)+gov 全 push。**S163（2026-06-14，Leonard「ABC」全權自主）：完成 C+A+版本/首頁+B 四項，全部 push + Pages/Render live 驗。** C 核 KG QC：17 flags 全修（`_qc_fix.py`）+ **揭發並修 S162 結構 bug**（kg_operation/clauses.json 非標準 schema `section_no/name`→canonical `si/section_name`：修 backend supplement linkage 388/388 由失效恢復 + 學校版 docx 章節名空白）→ `ef43517`. A 文件標註 Phase 2.5：`detectDomainsPerSegment`（per-segment argmax 路由）取代 whole-doc detect（多範疇文件各段路由其域，單範疇仍 1 域；比 legacy 更準——maths legacy 誤判 qa_inspection、新版正確 curriculum）→ `d71ae1e`（Render 驗 SEN doc→['sen']）. 版本+首頁+平台介紹：`PLATFORM_VERSION='3.0.0'` decouple；app.html 平台介紹 channels 改 政策搜尋/文件標註/範本下載/指引文件庫/通告分析；index.html +文件標註+範本下載 卡+v3.0 eyebrow；CHANGELOG v3.0.0 → `f510ee8`. B 文件標註 Phase 2 PDF inline highlight：+pdf-lib 1.17.1；`extractPdf` 抽座標；`buildAnnotatedPdf` 原 PDF 就地螢光+編號 marker+CJK sticky-note（UTF-16BE `PDFHexString.fromText`，免嵌 CJK 字型）→ `7289380`. commits `ef43517`→`d71ae1e`→`f510ee8`→`7289380` 全 push。**S162（2026-06-14，全權自主，4123 排序做 ④①②③）：完成 ④①②，③ 留下次。④ 幼稚園清單 pilot — 新範疇 `kg_operation`（幼稚園營運，388 items/162 clauses/20 章；源 kg_operation_manual_2026+kg_admin_guide_2026）行勻 14-域 pipeline → **15 域**；4 docx 入「範本下載」（+幼稚園 filter，106 docx）；backend 零 code 改（bundle-driven）；live e2e KG doc auto-detect 單域。17 覆核 issues：修法團校董會→校董會，16 軟性 fabricated 入 `dev/checklists/kg_operation/QC_VERIFY_ISSUES.md` 待 Leonard 核。① 跨校類 filter — bundle 加 domain-level `school_types`（由 `_school_type_profiles.json` applies_to）+ backend `okType` precedence（clause→domain→all）+ `detectRelevantDomains` 加 sel；untagged clause 唔再跨校類漏（live A-D+regression PASS；一併修 6 既有型別專屬域）。② dead-code：刪 AnalyzePanel/ReviewPanel/buildAnnotatedDocx/buildRevisedDocx（app.html 4345→3715，browser-verify 0 err）。commits `ec01e1b`(④)→`5dde30f`(①)→`51b6df2`(②) 全 push；Supabase 15,109 零接觸。③（文件標註 Phase 2 PDF inline highlight / Phase 2.5 per-segment auto-detect）= 大 feature，留 fresh session。**S161（2026-06-14，全權自主）：「文件標註」合併主線 Phase 1 SHIPPED LIVE — 合併 文件分析+文件修訂 → 一個「📝 文件標註」tab：上載 .docx → 比對 EDB 指引 + 合規清單 gap → **原檔就地標註**（保留格式 + 螢光 highlight + 就地可見內聯建議（💡指引／⚠修訂）+ 未能定位項入文末附錄）→ 下載。新 `backend/src/api/annotateDocument.ts`（重用 analyzeDocument 指引比對 + checklistRevise 清單 gap，零改兩模組）+ `/api/annotate-document` route（10/min+413 cap）；`checklistRevise.ts` 加 `detectRelevantDomains`（auto-detect 涉及範疇）；`app.html` 加 `AnnotatePanel` + `buildAnnotatedOriginalDocx`（JSZip 操作原 docx XML）+ JSZip 3.10.1 CDN；舊 `#analyze`/`#review` hash → redirect `#annotate`。commits `6885dbe`(feature)→`0e71802`(gov)→`1aafeda`(反饋1:可見內聯建議+公開名)→`a1bc18f`(反饋2:校類filter對比+隱藏內部清單+標註文件header)→`745b02f`(反饋3:建議條文用 Word 追蹤修訂 w:ins，接受即套用) 全 push。live e2e onrender PASS（safety doc → 3 guideline〔Supabase live〕+24 partial+50 missing、auto-detect 學校安全+學生支援、0 truncated）。**Leonard 真檔（數學 docx）試用 2 輪反饋已即修 live**：(1)隱形 Word 批註→可見內聯建議、內部名→公開名；(2)政策範本隱藏「文件要求清單」(內部對照用)、修 `.filter-tab` 喺淺底白字隱形（加 `.filter-tab-light`）、標註文件加頂部 header（平台/校類/範疇/圖例）+ guideline framing「參考」+ checklist 可編輯「✎ 建議條文」。⚠️ 舊 `AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 變 dead code（已無 tab/render 引用，但保留——`REVISE_SCHOOL_OPTS`/`REVISE_STATUS_META`/`REVISE_BACKEND_URL` 仍被新 panel 用；cleanup 列 follow-up）。****S160（2026-06-14，通宵自主 + Leonard supervised）：(A) 政策範本下載 tab + 文件修訂 feature（`/api/checklist-revise`）LIVE deployed（live e2e PASS：14 域/真實報告/CORS）。(B) #2 幼稚園 Phase 2 KG LIVE 入庫（Leonard sign-off）：`kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks** → Supabase 14,674→**15,109**；新 `kg_admin` route（searchChannelB.ts，擺 curriculum 前；routed smoke 命中新源 p1/p78、收生無回歸）；display-sync ×7（→15,109）；registry 216→**218**。commits `fcccc34`(P2)→`bd99b91`(P3)→`1bf497c`(KG)+gov，全 push（Render KG 路由 deploy propagating）。****S159（2026-06-13）：(1) #3 學校版分校類 mass-gen — 13 域 per-type(小/中/特) docx 102 份入 `dev/checklists/<域>/`；修全 14 域學校版 docx「undefined」章節 bug；13 域 348 校類 carve-outs（school_types field）；Leonard 科目→校類 ruling 已套。(2) #4 文件分析 Phase 2 SHIPPED LIVE — 標註版 docx 下載 + 校類選擇器（analyzeDocument.ts/app.html，onrender e2e PASS）。(3) #2 KG 入庫 prep — 2 核心源抽取完成（435 chunks 待 INSERT，dev/vault/，live 入庫留下個 session）。Supabase 14,674 未動。****S157：checklist QC 全清（128 verify_issues、0 pending）。S158（2026-06-13）：(1) `ph_pri_guide_2025` 完整重抽入 Supabase 146→315 chunk（舊抽取封頂 80/262 頁、缺 ch3-6 正文；DELETE 146 舊 + INSERT 315 新）→ 總 14,505→**14,674**、公開 Channel B 搜尋實測命中 ch5/ch6；(2) curriculum 人文科 8/9 verify-issue 引用由 EDB 通告 re-anchor 去真指引 `ph_pri_guide_2025` 真物理頁（p8/11/19/123/127/192/196/245；idx7 培訓 刪），2 份 curriculum docx 重生；(3) 刪 人文科 idx7 + 科學科 4 條 30hr/15hr 培訓證書 items（行政公布非校本政策要求）；(4) display sync 14,505→14,674 × 7 處。**
2. **Frontend**: `index.html` landing；**`app.html` = Channel-B-only 唯讀 SPA（S151：admin 登入閘 + 知識提煉/知識管理 tab + CRUD/匯出/候選審核 全移除；淨 3 tab〔平台介紹/政策搜尋/指引文件〕+ 文件預覽抽屜；app.html 4100→2935 行 −1176）**；`t-purchase.html` draft flow（dormant）；`q.html` local knowledge.json Quick Q&A（dormant）。**S153：政策搜尋（Channel B）合成分析放長 ≤120→約250字（上限300 soft；live ~328）+ 來源頁碼喺結果顯示並可點跳去 PDF 第 N 頁。⚠️ app.html 有兩個搜尋 UI：React desktop `QAPanel`/`SourcesAccordion` + 手寫 mobile shell `mobile.js`（平板用）— 兩個 surface 都改咗；mobile 來源名亦改全中文(`displayName`) + 去走「原文·分數」badge。** **S154：+📄文件分析（第 4 個 tab，desktop React surface）— 用戶上載 PDF/docx 或貼文字 → client-side 抽取（pdf.js 3.11.174 + mammoth 1.6.0 CDN；原始檔永不上載）→ `POST /api/analyze-document` 逐段比對指引 → 逐段報告（指引 `url#page=N` link + LLM 一句提示 best-effort + 私隱提示 + 60k 字/12 段 cap）。mobile.js shell 未做（Phase 1.5）；Phase 2 目標 = 可下載標註文件。** **S154(3)：全 4 個公開 HTML（index/app/q/t-purchase）裝咗 Cloudflare Web Analytics 免 cookie beacon（`</body>` 前一行 defer script；token 係公開 client-side 識別碼非 secret）+ index/app footer 私隱細字「本站採用免 Cookie 匿名流量統計」。報表喺 Leonard Cloudflare dashboard → Web Analytics。架構：前端由零對外 runtime 服務 → +1（已入 CODEBASE External Services）。** **S164：mobile shell（`mobile.js`/`mobile.css`，≤640px/mobile UA 觸發）底部導航 3→4 入口（🔍搜尋/📚指引文件/📋範本下載/ℹ️平台介紹）；`#templates` = `buildTemplatesShell()` 純靜態「桌面版功能」畫面（badge+說明+`templates-preview.png` 截圖，img onerror 優雅隱藏，不提供下載）；文件標註維持 desktop-only 手機無入口。desktop React app.html 零接觸。** **S165：文件標註面板（desktop React）下載列重整為 3 按鈕——新「可編輯 Word 版」（`buildEditableDocx`，docx-lib 由抽取文字砌：配對段黃螢光+AI 建議綠螢光直寫、非 w:ins 追蹤修訂、Word/PDF/貼文字皆出）為推薦 primary；標註版原檔（`buildAnnotatedOriginalDocx` Word 追蹤修訂／`buildAnnotatedPdf` PDF 螢光，需上載檔）；建議清單。加「三種下載」指引塊（教 Word 校閱接受/拒絕）。現有 3 個 builder 不改。mobile.js 搜尋框 +enterkeyhint+Enter keydown handler。**
3. **Knowledge state**: **455** Channel A facts（三層同步 byte-identical，md5 `720f5f`）、0 queue；Supabase **13,667** chunks（S148 13,473 → **S149 安全指引 +115**〔g18 校車+9 / g21 視藝+48 / g22 科技+58，文字層〕 → **S150 gifted +94**〔gifted_policy_docs +19 / gifted_tp_resource_kit +41 / gifted_osalp_compendium +19〕）；**新增 2 條 dedicated route**：`safety`(+keyword 校車/視藝安全/科技安全)、`gifted`(+keyword 資優/資賦)；指引（161 app / 152 公開 / **205** registry）；**display sync EXECUTED**（`_meta.stats` chunks→**13,667** 三層 byte-identical + app.html + K1_API_SPEC + README；guidelines 152 不變、無 bump、facts 455 不變）；Phase 3 全完成。**S151：app.html admin UI（知識提煉/知識管理/登入/CRUD/匯出）全移除 → 公眾完全 Channel-B-only；以上知識數字、role_facts/knowledge.json/guidelines.json 凍結資料與對外契約零接觸（admin 只係 client-side localStorage、無真實寫能力）。** **S152（2026-06-09）：Discovery 全量 triage（54 頁/400 候選）+ B-group 16 sibling-dup 全覆蓋確認（缺口清空）;入庫 7 個新發現源 +609 → Supabase **14,276**（三層 _meta.stats md5 720f5f→`4c3631` byte-identical）、registry 205→**212**;新源：`kgecg_2017`（幼稚園教育課程指引2017，補平台一直缺嘅 KG 課程）/`gifted_ge_series`/`cgss_2024`/`sch_calendar_guide`/`sch_activities_guide`/`k1_admission_2627`/`kg_admin_guide`，各加 SOURCE_SET route（curriculum/gifted/sen/hr_admin/activity/kg_admission）+ 2 keyword;display sync 7 處 14,276（facts 455/guidelines 152 不變、無 bump）。routed smoke 6/7 surface 帶頁;`cgss_2024` in-route 但 rank 低 top-8（monitor）。** **S154（2026-06-10）：IMC/SBM 校董會治理入庫 +229 → Supabase **14,505**（三層 _meta.stats md5 4c3631→`1bf7fd` byte-identical）、registry 212→**216**;4 新源（sbm.edb.gov.hk references，全文字層 page-resolvable）：`imc_establishment_operation`(成立與運作手冊2014, 97ch) / `imc_briefing_qa`(簡介會問答2013, 48ch) / `imc_governance_supplements`(Ch5/角色責任/會議/法例提醒/良好管治/行為守則 6PDF, 27ch) / `imc_election_guides`(家長/教師/校友選舉+委任五步曲 4PDF, 57ch);**新 `school_governance` route（擺 finance 前 — finance 佔 `法團校董` token 為 g02，唔擺前則校董會查詢全 route 去 finance、治理本體永不 surface；SOURCE_SET 連 g02+coa_imc_1_19+sdp_guide）**;display sync 7 處 14,505（facts 455/guidelines 152 不變、無 bump）。routed smoke 4/4 surface 帶正確頁碼、採購/招標 留 finance（唔被偷）。monitor：code-of-aid-IMC + sch-admin-guide 兩 index 頁已在 discover watch-list（Leonard 要求 Monitor — 已 cover）。**
4. **Backend**: Channel A+B+A+B search APIs live at `https://edb-knowledge.onrender.com`；**Q4 Phase 2 NEW**: `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`（X-Sync-Key gated，`CHANNEL_B_SYNC_KEY` set on Render；live smoke PASS：13 欄 + anon reads embedding 1536-vec confirmed）；rate limiting 10 req/min/IP + sync 60/min。
5. **Channel A frozen @455**（Q4 Phase 1 EXECUTED S143）：knowledge.json 停更 @455（schema 不變、下游零改變）；pipeline dormant 可逆；endpoint 不刪；guidelines.json 不凍續 live @152 v2.5.0。
6. **Channel B sync（Q4 Phase 2 全鏈完成 S146）**：K1 端 `dev/CHANNEL_B_SYNC_SPEC.md` v0.5 + `backend/src/api/channelBSync.ts` LIVE（manifest/chunks 401-gated 健康）；**下游 Circular System consumer 已 build 好 + 完成工作**（S146 Leonard 確認）；交接包 `dev/CHANNEL_B_HANDOVER.md`。incremental sync 自動帶新源 delta（本 session +11 源，下游下次 poll 自動執）。

</details>

<details>
<summary>舊 Open Priorities 全文（S212–S214，原編號 ①–⑧）</summary>

> **🔜 S214（2026-09-05）重生。Phase 1.1 A–E 全部完成，已從清單移除。** 新 ①–③ 為 S214 產生的未了項，④ 起承接 S213 未動項目（原編號在括號內註明）。

① 🔴 **【最高優先】S214 grounded synthesis V3 仍為 FAIL；Phase B route-first 候選已備但未安裝。** `FEATURE_ROUTE_FIRST_SEARCH=0`；獨立 exact RPC、fail-open fallback、共用 embedding 及 `57014` 重試已通過本地與 Claude Code 唯讀覆核。下一 gate 是經 Leonard 明確批准後安裝 Supabase schema，先跑三題 focused retrieval，再跑 active gold 185 題 before／after及效能量度；未通過不得啟用。`hr_lsp` 跨頁第 4 頁錯判第 3 頁屬獨立 Phase B2，檢索改善不可冒充頁碼已修好。另須為 `hr_lang_req` 與 `saf_disease_notification` 建立完整性回歸。任何新外部呼叫或雲端寫入須另取批准；完成前不得 commit／push／deploy。

② **【S214 新增，未修】餘下 4 條 fidelity 不一致。** 3 條係分數完全相同而生產 tie 次序非 id 升序 —— **要查生產真正的 tie 規則（很可能是 Postgres RPC 回傳次序 ＋ V8 stable sort），未查證前不得在模型內憑猜對齊**。1 條 `fin_seg`：`edbc015_2026` 排在 5 個更高分項目之前，與 `edu_sen_lsg_outsource` 同源同病徵，**兩次獨立出現，仍未解釋**，值得專門追一次。

③ **【S214 新增，未做】本修正不減少合成窗佔用率。** 實測 overlay 平均佔 **2.22/5 格（44%）**，Gate 2A1 的排序修正只改次序與 exact 優先，**未改變「這些項目是否值得佔窗」**。S196 實測 negative 15 條之中 **7 條仍取得註腳 lead**，且正負 `lead_score` 分佈重疊（正向下限 0.6061 vs 負向上限 0.7213）——**純提高門檻在數學上不可行**。此屬 P0 audience 閘範圍，見 `dev/_s214_phase_1_1_report.md` §7。

④ **【S213 ⑥ 遺留，全部未動】** (a) 七個 standing WARN 未有 waiver ＋ 六項人手檢查未簽核；**waiver 只覆蓋 WARN 不覆蓋 FAIL**。(b) `kgecg_2017` 108 條 ZOMBIE 已證可刪，工具被分類器擋住。(c) `g33`／`g37` 瀏覽清單掛錯文件標題，**且 `app.html` 的條目不可刪**（刪任何一條會令 `guidelines.json` count 由 158 跌至 157，`FREEZE_CONTRACT` 即時 FAIL）。(d) `TOPIC_KEYWORDS.safety` 認裸「氣體」。(e) 特殊學校編制表恢復。(f) `content_kind` 框架重新定義。(g) 六個現有監察未接入狀態頁。

⑤ **【S213 ⑤ 遺留】658 條代號標題根因已封死，生產庫未改。** `dev/_s213_title_backfill.py` dry-run 已跑（542 條，UPDATE 非 DELETE，舊值就是 source_id，可完全回退），**執行被 auto mode 分類器擋住，要 Leonard 自己跑**。

⑥ **【S213 ⑧ 遺留，未修】** header 剝除正則 `^(# .+\n)+` 用了 `MULTILINE`，吃掉正文中以 `# ` 開頭的註腳行：16 個來源、33 行、涉 2,212 條 chunk（12.6%）。修正要重入庫，embedding 成本約 US$0.02，須有自己的 eval before→after。

**⚠️ 承 S211 未做：** `coa_pri_e` / `coa_ss_e` 亦載編制條款，未逐一檢查有無同類「答錯班數」問題。

<details><summary>🔙 S213（2026-09-04）舊 Open Priorities（Phase 1.1 已完成，存檔備查）</summary>

> **🔙 S213（2026-09-04）重生。** 舊 ①（waiver）②（kgecg 刪除）③（掛錯標題）④（safety 認裸氣體）⑤（特殊學校編制表）⑥（content_kind）⑧（監察接入狀態頁）全部**未動**，降為 ⑥ 統一承接；舊 ⑦（658 條代號標題）根因已查實、源頭已封死、生產庫未改，改列 ⑤。**①–④ 為 Codex QC Governor 指定的 Phase 1.1，做完停下等 Leonard 批准，不得 deploy／寫 Supabase／重切語料。**

① **【Phase 1.1 A＋E　量度器修正與 gold set 補足】** A：把 NFKC folding 加入 `dev/source/eval_retrieval.py` 的 chunk matching，加 self-test 證明相容碼位會命中、不同漢字不會誤命中，再重跑 39 條 baseline 確認 verdict／rank／查詢集無非預期變化（**不改生產搜尋邏輯**）。E：`kg_admission`(4)／`kg_operation`(5)／`digital_education`(6)／`info_security`(2) 各補至 ≥10 條、每類 ≥8 條可答，保持 dev／held-out 分離，新 label 須過 corpus／signature／source／page／NFKC 驗證。工具已備：`dev/_s213_corpus.py`、`_s213_validate_gold.py`。

② **【Phase 1.1 B　驗證現有棄權機制】** 19 條 no-answer 題以 **`synthesize:true`** 執行，另配 ≥19 條可答題做 positive control。每題分類為：正確拒答／正確作答／有依據但答非所問／無依據作答／技術錯誤。須記錄 judge 結果、有無觸發 `trustedVaultLead` bypass、實際 synthesis、採用的前五個 chunk。**不可用「返回了搜尋結果」代替「系統作出了答案」。批量呼叫外部模型前先報預計次數、token 與成本（紀律 #17）。**

③ **【Phase 1.1 C　驗證 forbidden source 的實際影響】** 四條 `forbidden_hits` 查詢以 `synthesize:true` 執行，分四類報告：(1) 只在原始結果出現；(2) 進入 synthesis window；(3) 答案實際採用其內容；(4) 答案因對象混淆而錯誤。**只有第 3、4 類才可稱為「答案引用」或「答錯」。** 四條為 `sen_special_school_curriculum`、`ss_ncs_history_adapted`、`bus_guide_audience_confusable`、`kg_sccc_ratio_confusable`。

④ **【Phase 1.1 D　排序反事實測試，不改生產】** 比較三種策略：現行 forced-footnote 排序／結構化 exact match 優先再合資格 footnote 再原排序／全域 score sort（**僅作反例**）。每種報 Source Recall、Chunk Recall、MRR、forbidden exposure，以及原有 footnote positive control 的損失。**不得只以 Recall@1 選方案；Chunk Recall@3／@5 與錯答風險優先。** ⚠️ Codex 實測純 score 重排 Source Recall@1 升至約 0.420 但 Chunk Recall@5 反跌至約 0.245，**該數由 Codex 提供，S213 未獨立複核**。

⑤ **【根因已封死，生產庫未改】** 658 條代號標題 + 130 條無連結片段同源於 `build_wiki_index.py:267-268`。`dev/_s213_title_backfill.py` dry-run 已跑（542 條，UPDATE 非 DELETE，舊值就是 source_id，可完全回退），**執行被 auto mode 分類器擋住，要 Leonard 自己跑**。順帶：`stat_integrated` 那 2 條同時是 `REGISTRY_UNMANAGED` 的唯一成因。

⑥ **【S212 遺留，全部未動】** (a) 七個 standing WARN 未有 waiver ＋ 六項人手檢查未簽核；**waiver 只覆蓋 WARN 不覆蓋 FAIL**，`NO_ERROR_FAIL` 由 `NO_MIDCLAUSE_START`／`REGISTRY_ZOMBIE`／`REGISTRY_SERIES`／`REGISTRY_UNMANAGED` 四項造成，其中三項可由 ⑤ 與刪 `kgecg_2017` 清掉。(b) `kgecg_2017` 108 條 ZOMBIE 已證可刪，工具被分類器擋住。(c) `g33`／`g37` 瀏覽清單掛錯文件標題（實為 2021／2017 版），**且 `app.html` 的條目不可刪** —— 刪任何一條會令 `guidelines.json` count 由 158 跌至 157，`FREEZE_CONTRACT` 即時 FAIL（下游 EDB 通告系統依賴此值）。(d) `TOPIC_KEYWORDS.safety` 認裸「氣體」。(e) 特殊學校編制表恢復（須先移出 `SOURCE_SETS.staffing`）。(f) `content_kind` 框架重新定義。(g) 六個現有監察未接入狀態頁。

⑧ **【S213 新增，未修】** header 剝除正則 `^(# .+\n)+` 用了 `MULTILINE`，吃掉正文中以 `# ` 開頭的註腳行：16 個來源、33 行、涉 2,212 條 chunk（12.6%）。修正要重入庫，embedding 成本約 US$0.02，但須有自己的 eval before→after。受影響最多的正是 `coa_ss_e`(707) 與 `coa_pri_e`(494) —— 即交接一直掛住「亦載編制條款，未逐一檢查」那兩個。

**⚠️ 承 S211 未做：** `coa_pri_e` / `coa_ss_e` 亦載編制條款，未逐一檢查有無同類「答錯班數」問題。

</details>

</details>

<!-- ack:section:state-reconciliation-check -->
## State Reconciliation Check

- **2026-09-08 S218 closeout reconciliation（起手探針節）：** 於本次收工當下完成，非沿用舊快照。本節**零程式碼改動**，故產品側狀態多數逐段確認 current 而非重寫。

<!-- ack:field:state-sections-rewritten-or-confirmed -->
- **State sections rewritten or confirmed current（S218）：** **重寫**：`Current Baseline` 第 1 項（探針歸屬改 S218 並補齊五個實測值）· 第 2 項（HEAD 由 `612e13e` 更正為 `0f8a7c9`，並新增「Render 報舊 commit 屬正常、零執行碼差異」的定性）· `Validation / QC`（新增 S218 段，明寫零重跑、S217 數值為何仍有效、`doctor` 仍未驗證）· `Risks / Blockers` 第 1 項（補 S218 實測 bot 本輪未推）· `Open Priorities`（**整段重生**：S217 的 ① 已結案故移除，②' 升為 ①，其餘重排；治理側原 ⑥⑦ 依 §4 五項上限原文移入 `## Backlog` 治理側段，`grep` 實測全檔只出現一次 = 搬非複製）· `Last Session Record`（重生為 S218，S217 降為 `Previous Session Record (S217)`，內容一字未改）· `Next Session Opening Message`（重生，新增「/health 報舊 commit 是正常」的防誤判段）。**逐段讀過確認仍 current、不改**：`Architecture Decisions`、`Regression / Verification Notes`、`Backlog` 原有內容、`User Environment`、`Mandatory Start Checklist`、`Supabase Technical Notes`、`Detail Archive`、所有 `Previous Session Record`。

<!-- ack:field:lifecycle-conflicts-resolved -->
- **Lifecycle conflicts resolved（S218）：** 是，逐項對過五節。(a) **已完成項不再以未了項身分留存**：S217 的七個 commit 去向已於上節結案，本節從 `Open Priorities` 移除，其事實改由 `Current Baseline` 第 2 項承載。(b) **本節無任何完成項** —— 探針與資訊回覆都不產生待辦，故無新項需要降級。(c) **未解項全部保留**：185 題 live、`backend/README.md`、三題 recall、fidelity、S212／S213 遺留、治理兩項、`qc_report.json` ERROR 全部仍列未解，無一被誤標完成。(d) **未驗證項明確標示**：`agent-handoff-kit doctor` 連續兩節跑不到，`Validation / QC` 與開場白皆寫明「列為未驗證，不當通過」。(e) **開場白與現況一致**：HEAD、部署 commit、flag 狀態、OP 編號三處對齊。

<!-- ack:field:persistence-routing-checked -->
- **Persistence routing checked（S218）：** 是。當前狀態／風險／建議下一步／OP 重排 → 本 handoff；探針逐項數值、git 差距的逐檔驗證、桌面與 mobile 的分別問答 → `dev/SESSION_LOG.md` S218 條（trace 證據）。**未升 `dev/PROJECT_DECISIONS.md`** —— 本節無架構取捨、無研究推導決定。**未改 `dev/CODEBASE_CONTEXT.md`** —— 技術棧、目錄、build 指令、External Services、Key Decisions 本節皆未變。**未改 `dev/PROJECT_INDEX.md` 的 Branch / commit 列**？已改（見下方 Sync）。

- **Opening message matches current state（S218）：** 是。開場白已重生並含：新 HEAD `0f8a7c9`、部署 commit `612e13e` 及其「屬正常」的解釋、🔴 flag 閘未開、🔴🔴 establishment 無 flag 保護、⚠️ bot 探針紀律（含本輪未推）、五條已確立事實、九條未解項、`Post-startup first action`。

- **Sufficiency check（S218）：** 通過。下一個 agent 只讀 `AGENTS.md` ＋ 本 handoff ＋ `dev/PROJECT_INDEX.md` 即可續做：起手探針五項、HEAD／部署 commit 差距的正確解讀、下一道閘是甚麼、離線可做的兩件事、以及哪些事未得批准不得做。**不需翻 `dev/SESSION_LOG.md` 或 `dev/archive/`。**

- **2026-09-07 S217 closeout reconciliation（push ＋ 部署 ＋ 行為核對節）：** 於本次收工當下完成，非沿用舊快照。

<!-- ack:field:state-sections-rewritten-or-confirmed -->
- **State sections rewritten or confirmed current（S217）：** **重寫**：`Current Baseline`（第 1 項起手探針全部實測；第 2 項 git／部署由 `463434c`／`4a25a15` 更正為 `612e13e`、分歧 0/0；第 3 項改寫；**新增第 4 項**記無 flag 保護的行為改動；為守 §4 六行上限把兩條純指針合併為第 5 項）· `Validation / QC`（新增 S217 機器閘段、追加逐檔行為核對段、收工段）· `Risks / Blockers`（第 1 項由「受阻」改為「已解除，只監察」；第 3 項標已解除）· `Open Priorities`（Recommended next step 重寫；① 結案；**新增 ②'**）· `Last Session Record`（重生為 S217，S216 降為 `Previous Session Record (S216)`，內容一字未改）· `Next Session Opening Message`（重生，新增 🔴🔴 陷阱段）。**逐段讀過確認仍 current、不改**：`Architecture Decisions`、`Regression / Verification Notes`、`Backlog`、`User Environment`、`Mandatory Start Checklist`、`Supabase Technical Notes`、`Detail Archive`、所有 `Previous Session Record`。**無損驗證**：29 個 `ack` marker 一個不少。

<!-- ack:field:lifecycle-conflicts-resolved -->
- **Lifecycle conflicts resolved（S217）：** 是，逐項對過五節。(a) **已完成項不再以未了項身分留存**：七個 commit 的去向在 `Open Priorities ①` 標「已完成，結案」、`Risks / Blockers 1` 標「已解除，只監察」、`Last Session Record` 記為完成、開場白改為 ✅ 段 —— 四處一致，無一處仍寫成待辦。(b) **未完成項未被誤標完成**：185 題 live 套件在四處一致寫為未跑，且新增 ②' 說明它已由「啟用 flag 的閘」升格為「已生效改動有無副作用的唯一量度」。(c) **反向檢查我自己的錯誤宣稱**：「flag 全 off = 零行為改動」這句已在 `Current Baseline 4`、`Validation / QC`、`Open Priorities ②'`、開場白 🔴🔴 段、`SESSION_LOG` 第 8 點、`DOC_SYNC_REGISTRY`（`not_applicable` → `confirmed`）六處一致更正，無一處留住舊講法。(d) **只監察項有明確理由**：`Risks 1` 保留為監察是因 watcher bot 會繼續推送，非因未解決。

<!-- ack:field:persistence-routing-checked -->
- **Persistence routing checked（S217）：** 是。當前狀態／風險／建議下一步 → 本 handoff；rebase 保全數字、機器閘結果、部署輪詢時序、逐個 hunk 核對、煙霧測試 → `dev/SESSION_LOG.md` 作 trace 證據；workspace identity（commit／未提交摘要）→ `dev/PROJECT_INDEX.md`；本節 sync 義務與 `Public behavior change` 的更正 → `dev/DOC_SYNC_REGISTRY.md`；新改動類別 → `dev/DOC_SYNC_CHECKLIST.md` 補 row；**可轉移的操作程序 → Playbook 提案**（不只留在 handoff／log，符合「reusable procedure 不可只存於 handoff」）。未升 `PROJECT_DECISIONS.md` —— 本節無架構取捨。

- **Opening message matches current state（S217）：** 是。開場白已重生並含：新 HEAD／部署 commit、✅ 七個 commit 已結清、🔴 flag 閘未開、🔴🔴 無 flag 保護路徑的陷阱與通則、⚠️ 遠端會自己走前的教訓、四項已確立事實、未解決清單。`START_NEXT_SESSION_PROMPT.txt` 由該 fenced block 重生並 **byte-for-byte mirror check PASS**。

- **Sufficiency check（S217）：** 通過。下一個 agent 只讀 `AGENTS.md` ＋ 本 handoff ＋ `dev/PROJECT_INDEX.md` 即可續做：起手探針四項、rebase 流程、七個 commit 已結清、下一道閘是 185 題、以及最重要的「flag 全 off ≠ 零行為改動」陷阱，全部在 handoff 內，**不需翻舊 log 歷史**（本節已歸檔 5 條舊 entry，故此項特別核過）。

- **未驗證項（S217，明確標示不當通過）：** `agent-handoff-kit doctor` 本節跑不到（CLI 不在 PATH，npm 名稱 404），改為自行驗證 29 個 `ack` marker 完整；`72b5adb` 未觸發新部署的成因未查證（`RENDER_GIT_COMMIT` 仍報 `612e13e` 而 `started_at` 已更新）。

- **2026-09-07 S216 closeout reconciliation（Agent Handoff Kit v0.3.29 → v0.3.66 升級節）：**

<!-- ack:field:state-sections-rewritten-or-confirmed -->
- **State sections rewritten or confirmed current:** **重寫**：`Risks / Blockers`（第 1 項由「五個 commit」更正為**六個**並補 HEAD `6cb80c6`；新增第 3、4 項）· `Validation / QC`（補 S216 doctor 53/53，並明寫 S215 產品側數值未失效及理由）· `Open Priorities`（①更正為六個 commit ＋ 17 個治理檔；換走 upgrade 佔位的 Recommended next step；新增 ⑥⑦）· `Last Session Record`（重生為 S216，舊者降為 `Previous Session Record (S215)`，內容一字未改）· `Next Session Opening Message`。**結構性修正**：孤兒 `workspace-identity` 這個 section marker marker 搬到 `## User Environment` 之前（它原本被我上一步插入的兩節隔開，抽取結果為空）。**逐段讀過確認仍然 current、不改**：`Current Baseline`、`Architecture Decisions`、`Regression / Verification Notes`、`Backlog`、`Mandatory Start Checklist`、`Supabase Technical Notes`、`Detail Archive`、所有 `Previous Session Record`。

<!-- ack:field:lifecycle-conflicts-resolved -->
- **Lifecycle conflicts resolved:** 是，逐項對過五節。(a) **數字衝突已消**：`Open Priorities ①`、`Risks / Blockers 1`、`Last Session Record 3`、開場白四處現時一致寫**六個 commit**，S215 遺留的「五個」已全數更正並註明成因。(b) **本節完成項無一項留在待辦**：升級、四層 conflict 解決、marker 修正、65 行還原、逐檔無損失核實，全部只在 `Completed This Session`，未出現在 `Next Priorities` 或 `Risks / Blockers`。(c) **反方向亦對過**：新增的 ⑥（8 個無家 marker）與 ⑦（INIT.md 鏡像失效）都是本節**量到而未修**的，⑦ 明確標為 **blocked** 並寫明解封條件（要先決定 INIT.md 是否退役）。(d) **刻意不升做 OP 的一項**：`completed-this-session` 抽取範圍過闊，屬本檔結構副產品、不影響任何 check，已記在 ⑥ 內文而非另開一條。

<!-- ack:field:persistence-routing-checked -->
- **Persistence routing checked:** 是。當前狀態、風險、建議下一步 → 本 handoff；升級逐步經過、conflict 逐個判斷依據、還原證據 → `SESSION_LOG.md`；Kit 版本／新增檔案／QC 指令／workspace identity → `PROJECT_INDEX.md`；本節觸及的 sync 義務與 blocked 理由 → `DOC_SYNC_REGISTRY.md`；開場白 → 只由 handoff 的 fenced block 生成 `START_NEXT_SESSION_PROMPT.txt`，**未複製入 log**。**未寫 `PROJECT_DECISIONS.md`**：本節是工具升級，非架構取捨；但「upgrade 會靜靜取代開場白」這一點屬跨 session 可重用教訓，已寫入下面的 opening message 與 log，若日後再遇同類事件應升為 decision 條目。

<!-- ack:field:stale-snapshots-left -->
- **Stale snapshots left:** 無。**本節更正了兩項既有記載**：(a) S215 交接的「領先五個 commit」實測為六個；(b) `dev/PROJECT_INDEX.md` `Workspace Identity` 的 branch/commit 仍停在 S213 的 `05ea10e`、未提交摘要仍停在 S213 的 35 個檔，兩者皆已按實測更新。

<!-- ack:field:closeout-outcome -->
- Closeout outcome: blocked — 治理寫入與讀回全部成功（`doctor` 53/53、prompt mirror 一致、`closeout-status` 的 lifecycle 與 sufficiency 閘皆過），本節治理檔亦已本地提交（S216 closeout commit）。**唯一未達 `complete` 的原因**：本項目 `## Session Close Checklist` 的收工持久化包含 `git push origin main`，而 Leonard 本節明示只做本地 commit、不 push。

<!-- ack:field:project-required-persistence -->
- Project-required persistence: blocked — **確切邊界**：commit 已完成（S216 closeout commit）；**push 未獲授權**，七個本地 commit 仍未上 `origin/main`，去向待 Leonard 決定。另 `dev/DOC_SYNC_CHECKLIST.md` 的 INIT.md 鏡像同步亦為 blocked，解封條件是先決定 `INIT.md` 是否已退役（OP ⑦）。

<!-- ack:field:recommended-next-step-explicit -->
- Recommended next step is explicit and reasoned: 是 —— `Open Priorities` 開首一句寫明單一建議動作（決定六個 commit ＋ 17 個治理檔的去向）及理由（只有它會隨時間惡化，因為 watcher bot 會繼續推送到 `origin/main`），並註明需 Leonard 決定、AI 不得自行 push。

<!-- ack:field:next-ai-can-continue -->
- Next AI can continue: yes — 見上面 `## Handoff Sufficiency Check` 的 `Answer` 與 `Reconstruction evidence` 兩行；下一步、前置條件、邊界與未讀缺口全部在本檔可讀，毋須翻舊 log。

<!-- ack:field:opening-message-matches-current-state -->
- **Opening message matches current state:** 是。逐項對過：六個未 push commit ＋ 17 個未提交治理檔、Kit v0.3.66 且 doctor 53/53、三個 flag 全 `0` 與 verdict FAIL 不變、`backend/README.md` 5 行仍未補、`AGENTS.md` 等三檔不在版本控制內 —— 五項在開場白與本檔各節一致。`START_NEXT_SESSION_PROMPT.txt` 由本檔唯一的 fenced block 重生並經 `doctor` prompt mirror check 讀回。

- **2026-09-07 S215 closeout reconciliation:**

- **State sections rewritten or confirmed current:** `Current Baseline` 整節重寫為 6 行當前狀態（舊 87,154 字元全文逐字移入 `## Detail Archive (S212–S214)`，程式化驗證 `in` 為 True）；`Open Priorities` 整組重生為 ①–⑤（舊 4,679 字元全文同樣移入 Detail Archive，零刪減）；`Last Session Record` 重生為 S215，舊者降為 `Previous Session Record (S214)`，內容一字未改；`Next Session Opening Message` 重寫並同步至 `SESSION_LOG.md` 與 `START_NEXT_SESSION_PROMPT.txt`。

- **Lifecycle conflicts resolved:** S214 的「未提交生產改動三選一」已完成（選項 a 的 commit 半邊，push 半邊未做），故從 Open Priorities 移除，改列為「五個 commit 未 push」；「RPC 未安裝」已由實測推翻，改列為「已裝但來歷不明」。

- **Persistence routing checked:** 當前狀態→handoff；事故經過與逐項救援證據→SESSION_LOG；回退指令教訓→Claude 長期記憶＋playbook inbox 提案；檔案映射→PROJECT_INDEX。

- **Stale snapshots left:** 無。

- **Opening message matches current state:** 是（五個 commit 未 push、三個 flag 全 0、verdict FAIL、README 5 行遺失，四項皆一致）。

- **2026-09-06 S214 V3 reconciliation:** 已把修正後 18 題實測寫回 `Current Baseline`、`Open Priorities`、`Last Session Record`、`Next Session Opening Message`、`SESSION_LOG.md`、`PROJECT_INDEX.md`、`_s214_grounded_acceptance_report.md` 及 `_s214_grounded_v3_review.md`。所有位置一致記錄：25／36 次 HTTP；不可答題 9／9 棄權、可答題 6／9 作答；人工覆核 4 完整、2 安全但不完整、3 棄權／證據不足；無 audience 錯答、OCR 重複或截斷；release verdict 仍為 FAIL。已完成的「18 題重驗」不再列作下一步；下一 gate 改為五條新鮮 retrieval fixture及兩條完整性回歸。兩個 feature flags 維持 `0`；沒有 commit、push、deploy 或 Supabase 寫入。

- **2026-09-06 S214 fresh retrieval reconciliation:** 五題 fixture 已完成並落盤，結果 2 PASS／1 PARTIAL／2 FAIL。`chi_hist_jss_ncs_2019` 漏 route allowlist及 `gov_imc_60pct` gold 標籤錯誤已作最小修正；候選中史單題驗證顯示 Source Recall 恢復但目標 Chunk Recall 仍失敗。`g10` 排序缺口與 `hr_lsp` 公式不完整保留為未解。下一步改為兩條 completeness 回歸及 `g10`／中史 NCS／`hr_lsp` 可泛化修法。零 Supabase 寫入、零 commit、零 push、零 deploy。

- **2026-09-06 S214 continuation reconciliation:** 已把第二批 40 題 post-fix acceptance、兩道離線輸出衞生閘、probe 選窗 blocker 及 Leonard 批准的 gold 修訂寫回 `Current Baseline`、`Open Priorities`、`Last Session Record`、`Next Session Opening Message`、`SESSION_LOG.md`、`PROJECT_INDEX.md`、`CODEBASE_CONTEXT.md`、`_s214_grounded_acceptance_report.md` 及 `_s214_gold_abstention_review.md`。所有位置一致記錄：兩批舊 artifact 受 18／40 題 harness 偏差影響，不可直接作 release 判決；生產及 probe 共用 `selectPrimaryEvidence()`，回歸 48/48；active gold 184→185，兩條舊 NCS 已保存至 deprecated audit，七條新／修訂標籤最小 cache 驗證 7/7；兩個 feature flags 維持 `0`；下一 gate 是另取 API 批次批准後重跑 18 題、建立兩條新 NCS retrieval fixture及獨立覆核。沒有新外部 API 呼叫；沒有 commit、push、deploy 或 Supabase 寫入。

- **Reconciled at:** 2026-09-05（S214 closeout — Leonard「收工」）。
- **S214 state sections rewritten or confirmed current:** `Current Baseline`（**prepend S214 五項** ＋ 頂置紅旗未提交生產改動；S213 段降為 🔙 歷史，內容一字未改）；`Open Priorities`（**整組重生為 ①–⑥**：① 未提交生產改動列為最高優先並附三選項與驗證閘，② 4 條 fidelity 不一致，③ 合成窗佔用率未改善，④⑤⑥ 承接 S213 遺留並註明原編號；舊 S213 段整段收入 `<details>` 摺疊存檔，零刪減）；`Last Session Record`（重生為 S214，S213 降為 `Previous Session Record (S213)`，內容一字未改）；`Next Session Opening Message`（整段重生，紅旗置頂 ＋ 已完成四項 ＋ 未解決兩項 ＋ `Post-startup first action`）；本段。`Architecture Decisions` / `Regression / Verification Notes` / `Backlog` / `User Environment` / `Mandatory Start Checklist` / `Supabase Technical Notes` 逐段讀過，**本節未改動其所述事實，確認仍然 current，不改**。
- **S214 lifecycle conflicts resolved:** 是。Phase 1.1 A–E 已完成，**已從 Open Priorities 移除**，不再以未了項身分留在清單（S213 段的 ①–④ 隨舊段落一併摺疊存檔）。反向檢查：`searchChannelB.ts` 未提交改動同時出現在 `Current Baseline`（紅旗）、`Open Priorities ①`、`Last Session Record` 第 4 項、`Next Session Opening Message`（紅旗＋首要動作）——四處**一致描述為「已改、已通過 typecheck、未跑 184 live、未部署」**，無一處寫成已完成或已驗證。
- **S214 stale snapshots left:** 無。S213 段已明確標為 🔙 歷史；舊 Open Priorities 收入 `<details>` 並註明「Phase 1.1 已完成，存檔備查」。
- **S214 persistence routing checked:** 是。當前狀態與下一步 → `SESSION_HANDOFF.md`；本節逐條證據與指令 → `SESSION_LOG.md`；工具檔案地圖 → `PROJECT_INDEX.md`；兩份詳細技術報告留在 `dev/_s214_phase_1_1_report.md` 與 `dev/_s214_gate2a2_implementation_report.md`（交接只留指標，不複製內容）。
- **S214 opening message matches current state:** 是。`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並做 mirror check（見下 Sync）。
- **⚠️ S214 歸屬限制（必須保留）：** 本節有部分回合已不在 agent 上下文內（機器休眠 ＋ context 壓縮），**檔案逐行歸屬無法可靠重建**。磁碟上兩份 S214 報告為權威記錄，**不得憑檔案 mtime 推論作者**。

- **Reconciled at:** 2026-09-04（S213 closeout — Leonard「先收工」，並要求把 Codex 的 Phase 1.1 brief 一併寫入）
- **S213 state sections rewritten or confirmed current:** `Current Baseline`（prepend S213 六項：舊 eval 的 PASS 恆真、gold set 量到的真實水平、OP⑦ 根因、兩個新語料缺陷、註腳置頂之相關性、產品與工具兩個 verdict）；`Open Priorities`（**整組重生**：①–④ 為 Codex 指定的 Phase 1.1 A–E，⑤ 為根因已封死但生產庫未改，⑥ 統一承接 S212 七項未動遺留，⑧ 為 S213 新增的 header 正則吃註腳）；`Last Session Record`（重生為 S213，S212 降為 `Previous Session Record (S212)`，內容一字未改）；`Next Session Opening Message`（整段重生，含未提交改動的三類分類與 Phase 1.1 全文）。`Architecture Decisions` / `Regression Notes` / `Backlog` / `User Environment` / `Supabase Technical Notes` 逐段讀過，內容仍然成立，不改。
- **S213 lifecycle check:** 對得上。`Completed` 各項無一項留在 `Open Priorities`：Playbook v3、Phase 0 凍結基線、gold set 162 條、五支量度工具、extract header 修復與 fail-loud 守門，全部是本節完成並驗證，不是待辦。**反方向亦對過**：新 ①–④ 全部是 Codex 覆核後指定而本節未開始的；⑤⑥⑧ 全部是量到而未修的。**兩項刻意不升做 OP**：(a) 舊 harness 的 `verdict_for` 語意本身（它作為回歸偵測器是稱職的，要修的是「不可讀成準確度」這個理解，已寫入 Current Baseline）；(b) `text_hash` 是 sha256[:16] 而 `eval_retrieval` 註釋寫 md5[:12]（純註釋錯，已記入開工訊息「S213 查實」，不值得開一條 OP）。
- **S213 persistence routing checked:** 是。當前狀態 → handoff `Current Baseline` + `Last Session Record`；逐條量度、自己犯的六個錯、工具 self-test 結果 → `SESSION_LOG.md`；量度工具、gold set、新 QC 指令 → `dev/PROJECT_INDEX.md`（本次 append）；三條可重用紀律（#19 報血緣範圍前先逐條實測／#20 量度工具本身要先驗／#21 關掉了某一層就不可以講該層的能力）→ 開工訊息紀律段；未提交改動的三類分類 → 開工訊息 ⛔ 段，因為它是下一節第一件要做的事。**沒有把可重用紀律只留在 handoff 或 log。**
- **S213 stale snapshots left:** 無。**同時更正本節自己一度講錯的四項**：(a) 報 header 正則吃掉 55 行／23 源／3,714 條，實測係 33 行／16 源／2,212 條，而我舉的頭號例子 `staff_est_pri` 根本沒受影響；(b) 「系統沒有棄權能力」是 `synthesize:false` 之下的越界結論；(c) `forbidden_hits` 寫成「引用」，它只證明出現在結果窗；(d) 一度把註腳置頂與 Recall@1 較低講成代價已量到，那是相關性不是因果。**另更正 Codex brief 的一項前提**：它寫「S213 Gold Set 使用 synthesize」，實測 `eval_retrieval.py:251` 寫死 `"synthesize": False`，gold run 從未用過 synthesize —— 但它的結論仍然成立，只是理由相反。
- **S213 opening message matches current state:** 是。逐項對過：平台 v3.3.2（本節零前端改動）／Supabase 17,602（本節零寫入）／registry 279／GUIDELINES_REGISTRY 177／凍結合約零接觸／HEAD == origin/main @ `05ea10e`（0/0）／工作區 20 個已改檔 ＋ 15 個新檔，與 `git status` 逐行對過／兩個 eval run 檔存在且 errors=0。
- **S213 sync status:** 本節零生產改動、零對外數字變動，`qc_report` 四個數（17,602／658／130／842）未變，故 **DOC_SYNC 無新行命中**。row 43（檢索 eval harness）**未命中** —— 本節新建的是平行工具，未改 `eval_retrieval.py`；下一節 Phase 1.1 A 會改它，屆時 row 43 必然命中。
- **S213 log maintenance:** 無觸發。`session_log_maintenance.py --check` 實跑報 `trigger=False`、`line_count=162`、`entry_count=2`（門檻 400 行）。`PROJECT_DECISIONS.md` 觸發條件 (c) 成立但**刻意延後**：三種排序策略的取捨要有反事實量度才寫得成 ADR，那正是 Phase 1.1 D 的交付，本節寫只會寫成推測。
- **⚠️ S213 未完成而下個 session 必須知：** (a) 四項生產寫入仍卡在同一道權限閘（auto mode 分類器擋住 `cb3_deprecate_stale.py` 與 `_s213_title_backfill.py --execute`），要 Leonard 自己跑或加 Bash 權限規則；(b) 工作區 35 個檔待分類提交，**A／B 兩類不可混合提交**；(c) Phase 1.1 B、C 需要 `synthesize:true` 的批量外部模型呼叫，**動手前先報次數、token 與成本**。 (d) **`doctor` 現時報 `status: failed`，唯一原因是 `dev/rules/closeout.md` 不存在 —— 這是既有版本漂移，不是 S213 造成**：該檔在 git 歷史從未存在、`RULE_PACKS.md` 沒有引用它，已安裝 template 是 0.3.29 而 doctor 跑的是 v0.3.64。本節改動過的每個治理檔都報 `ok`。要清掉它得跑 `upgrade`，**那是獨立決定，不在收工範圍**。

- **舊記錄（S212 closeout）：**

- **Reconciled at:** 2026-09-03（S212 closeout — Leonard「全做，收工」）
- **S212 state sections rewritten or confirmed current:** `Current Baseline`（整段換成 S212 五項：狀態頁／封版閘／首次量度四個發現／phys 重抽／自己造成嘅停機）；`Open Priorities`（**整組重生為 8 項**，舊 ①②⑤ 結案移除，舊 ③④ 改寫為新 ⑤⑥，新增 ①②③④⑦⑧）；`Last Session Record`（換成 S212，S211 降格為 `Previous Session Record (S211)`）；`Next Session Opening Message`（整段重寫，紀律加至 18 條）。`Architecture Decisions` / `Regression Notes` / `Backlog` / `Supabase Technical Notes` 逐段讀過，內容仍然成立，不改。
- **S212 lifecycle check:** 對得上。`Completed` 各項無一項留在 `Open Priorities`：舊 ①（eval 片段層）已建並現場證綠，結案；舊 ②（登記漂移監察）監察半邊已建，**但人手策展佇列半邊仍未做，故改寫為新 ③ 並補上 S212 新發現嘅標題錯掛**；舊 ⑤（保安路由）已 ship 並 eval 過，結案。反方向亦對過：新 ①②③④⑦⑧ 全部係 S212 量到而未修嘅，不是把已完成工作當成待辦。
- **S212 persistence routing checked:** 是。當前狀態 → handoff `Current Baseline` + `Last Session Record`；逐條拆解、自己犯嘅錯 → `SESSION_LOG.md`；工具與指令 → `dev/PROJECT_INDEX.md`（3 個工具行 + 3 條 QC 指令行 + 2 個 Last verified 更新）；可重用操作紀律 → `dev/DOC_SYNC_CHECKLIST.md` row 53（品質檢查／封版閘改動）同 row 54（重抽既有來源並重入庫）；路由缺口 → `route_regression.mjs` KNOWN_GAPS；架構取捨 → `PROJECT_DECISIONS.md`（本次 append）。**冇把可重用紀律只留喺 handoff 或 log。**
- **S212 stale snapshots left:** 無。**同時更正三項本 session 自己一度講錯或量錯嘅嘢**：(a) 事實計數器行錯 knowledge.json 結構，把完好嘅凍結契約報成破損 —— 已修並加斷言；(b) 標題基準值用咗「我見過嗰一個來源」嘅 116，全庫真數係 658 —— 已重數；(c) 一度把「普適氣體定律」搵唔到算落 OCR 錯字頭上，實測「普適」對「普通」只差 0.019，真兇係 `safety` 認裸「氣體」—— 已改寫並入 KNOWN_GAPS。另**更正兩處自 S195 起錯咗嘅原始碼註釋**（`searchChannelB.ts:585/647` 寫 `kgecg_2017` 有 0 chunks，實際 108）。
- **S212 opening message matches current state:** 是。逐項對過：平台 v3.3.2（未變，本 session 無前端改動）／Supabase **17,602**（實測 `content-range`）／registry 279／GUIDELINES_REGISTRY 177／凍結合約四值全部 PASS（`qc_report` FREEZE_CONTRACT）／狀態頁 URL 實測 HTTP 200 且 `releaseGate` 為 FAIL 7/15／自動化清單已加每日 qc_report workflow（首次執行已於 15:33 UTC 自行 commit，數字與本機一致）。
- **S212 sync status:** DOC_SYNC **row 51（切 chunk 邏輯／重入庫）命中並兌現**（七個鏡像行 `live_display_sync(17597, 17602)`、eval before→after 已跑、blast radius 已記）；**row 53 與 row 54 為本 session 新增**並即時適用於自身改動；row 43（eval harness）命中並兌現（harness 改動 + self-test + 新 baseline run）。其餘各行本 session 未觸及。
- **S212 log maintenance:** 無觸發。`SESSION_LOG.md` 5 個 session entry（N=5 < 11）、行數未逾 1500，故不啟動 N-rule 歸檔。`PROJECT_DECISIONS.md` 觸發條件 (c)（多選項架構取捨連理由）已兌現：算術還原 vs OCR、折入既有路由 vs 獨立路由、chunk id vs 文字簽名，三項本次 append。
- **⚠️ S212 未完成而下個 session 必須知：** 四項生產寫入卡喺同一道權限閘（`dev/cb3_deprecate_stale.py` 被 auto mode 分類器擋住，連 dry-run）：`kgecg_2017` 108 條、`g24` 383 條、`stat_integrated` 2 條、以及 658 條代號標題 backfill。全部已驗證安全，只差 Leonard 自己跑或加 Bash 權限規則。
- **舊記錄（S211 closeout）：**
- **Reconciled at:** 2026-09-01（S211 closeout — Leonard「收工」）
- **S211 state sections rewritten or confirmed current:** `Current Baseline`（prepend S211 段，⑨ 項：前端五項、快取鍵教訓、`/health` version endpoint、判斷閘換 model、檢索四層、內容準確性、兩處過度觸發收窄、一次已還原嘅生產寫入、eval 零回歸；S210 及更早段原文保留）；`Open Priorities`（**舊 ① 結案移除並明寫其根因描述已被推翻**，舊 ②–⑥ 上移為 ①–⑤，③ 特殊學校表前置條件更新為「S211 已建可移植答案但索引欄不同、不可照搬」，兩處因重新編號而指錯嘅交叉引用已修）；`Last Session Record` 重生為 S211、S210 降為 `Previous Session Record (S210)`（內容一字未改）；`Next Session Opening Message` 整段重生。`Architecture Decisions` / `User Environment` / `Mandatory Start Checklist` / `Regression Notes` / `Backlog` 逐段核過，**確認 current、無需要改**。
- **S211 lifecycle check:** 對得上。`Completed` 各項無一項留在 `Open Priorities`：舊 ①（「12 班」個案）已由本 session 落實並結案移除；前端五項、`/health`、judge model、檢索四層、內容準確性全部係本 session 完成並驗證，非待辦。**由 completed 流去待辦嘅只有一項**：`coa_pri_e` / `coa_ss_e` 亦載編制條款、未逐一檢查，已記入 `Risks` 同 opening message 末段，**不升做 OP**——因為未有證據顯示佢哋有同類問題，升做 OP 會變成一條無出口嘅清單（紀律 #14）。
- **S211 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Last Session Record`；session trace、自己犯嘅六個錯、逐層拆解→`SESSION_LOG.md`；**可重用結論→`JUDGE_PROMPT_FINDINGS.md` §5–§7**（判斷提示唔係槓桿、凍結 cache 已漂移、班數查詢真兇），唔淨止留喺 log；**架構取捨→`PROJECT_DECISIONS.md` 兩則 ADR**（詞彙層檢索 vs 調門檻、判斷閘與合成器分用模型），兩則皆列明被實測否決嘅選項同否決理由；三個量度工具 + `JUDGE_MODEL` 環境變數 + `/health` 新欄位→`PROJECT_INDEX.md`；防漂移程序→`app.html` 分頁開關註釋第 8、9 項同 `DOC_SYNC_CHECKLIST.md`「Tab withdraw / restore」重整。
- **S211 stale snapshots left:** 無。**同時更正兩項本 session 自己一度講錯嘅嘢**：(a) 曾判斷「Render 部署失敗」並寫成報告請 Leonard 介入，實情只係慢，已即時收回並補上 `/health` version endpoint；(b) 曾以單次 live 呼叫斷言「S177 旗艦 case 喺真站答緊」，重複量度後修正為「該 case 喺門檻邊緣、判斷非決定性」。**另更正交接嘅一項描述**：舊 OP① 寫根因係「『12 班』喺 embedding 上贏唔到腳註同兄弟行」，方向啱但結論唔完整——單靠 soft re-rank 救唔到，因為稠密向量根本對唔到數字。
- **S211 opening message matches current state:** 是。逐項對過：平台 v3.3.2 / Supabase 17,597 / registry 279 / GUIDELINES_REGISTRY 177 / 凍結合約零接觸 / eval PASS=25 FAIL=0 errors=0 / NEXT ①–⑤ 對應重生後嘅 Open Priorities 編號 / 部署確認方法改為 `/health` `commit`。
- **S211 sync status:** DOC_SYNC **row 37（Channel-B vault source backfill）命中並兌現**（registry entry 更新 `chunk_max_chars` / `chunk_overlap` + 可達性實測 + 七個鏡像片段數同步 17,593 → 17,597）；**row 43（檢索 eval harness）命中並兌現**（before→after 一對齊全、run 檔保留）；**row 51（切 chunk 邏輯改動）命中並兌現**（`chunk_overlap` 覆寫、受影響源重入庫、七鏡像同步、blast radius 記於 log：`staff_est_pri` 81 → 85、半行開頭 74/81 → 2/85）；**「Tab withdraw / restore」一行重整**為 A flag 驅動／B 推算數字／C 人手散文／D 版本與記錄，驗證欄新增「grep 該功能關鍵詞確認無剩餘應承語」。
- **S211 log maintenance:** 無觸發。`SESSION_LOG.md` 4 個 session entry（N=4 < 11）、行數未逾 1500，故不啟動 R-010 N-rule；`PROJECT_DECISIONS.md` 觸發條件 (c)（多選項架構取捨連理由）已兌現，本 session 已 append 兩則 ADR；十個 closeout 一次嘅全面維護 backstop 未到（由主 log 加 archive index 計算）。

- **舊記錄（S210 closeout）：**
- **Reconciled at:** 2026-08-26 (S210 closeout — Leonard「a」= commit + push 然後收工)
- **S210 state sections rewritten or confirmed current:** `Current Baseline`（prepend S210 段：⑦ 項，含探針、OP⑥ 結案、DISPLACED、無頁碼 +10 之反轉、split gate、eval 集擴充、三摺頁、全 session 淨影響）；`Open Priorities`（**舊 ⑥ 結案移除、舊 ⑦ 升做 ⑥ 並補寫「已備好 baseline」**，①–⑤ 逐項覆核內容不變）；`Backlog`（新增正文連結一條，Leonard 拍板）；`Last Session Record` 重生為 S210、S209 降做 `Previous Session Record (S209)`；`Next Session Opening Message` 整段重生。
- **S210 lifecycle check:** 對得上。`Completed` 九項冇一項留喺 `Open Priorities`：OP⑥ 已結案移除；DISPLACED / split gate / eval 集擴充 / 三摺頁 / DOC_SYNC row 全部係本 session 完成並驗證，唔係待辦。**唯一由 completed 流去待辦嘅係正文連結**，佢明確降級做 Backlog（Leonard 拍板唔喺本 session 開），唔係未完成嘅 OP。`pay_adjust` 掉低一個尾位源**唔升做 OP** —— verdict 冇變、成因已查實（g04 切細多佔一位），記喺 Current Baseline ⑦ 同 Risks 做監察項。
- **S210 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Last Session Record`；session trace／逐條 compare 拆解／自己犯嘅錯→`SESSION_LOG.md`；**可重用程序知識→ `DOC_SYNC_CHECKLIST.md` 新 row（切 chunk 邏輯）**，唔淨止留喺 log；環境事實（PDF 管道要 python3.13）→`CODEBASE_CONTEXT.md`；對照 baseline→`dev/source/eval_runs/` 四個檔保留。
- **S210 stale snapshots left:** 無。**同時更正兩項交接寫錯嘅嘢**：(a)「`gifted_policy_docs` 10/23 chunks 有缺陷等修」實情反轉（係修好之後如實變無頁碼，old-vs-new `carry_pages` 對證 10/10）；(b)「S209 可能有 regression」實測零退步。**另補記一項 S209 收工漏做**：S209 冇寫 `State Reconciliation Check` block（AGENTS §4 步驟 6 要求），本段係 S208 之後第一段。
- **S210 opening message matches current state:** 是。逐項對過：Supabase 17,576 / registry 276 / GUIDELINES_REGISTRY 177 / 平台 v3.3.0 / 凍結合約零接觸 / eval 37 條 PASS=25 FAIL=0 errors=0 / 下一步指向 OP⑥ route regex 且講明 before 檔名。
- **S210 sync status:** DOC_SYNC **row 43「檢索 eval harness 改動」命中並兌現**（query set 變動連理由入 log、eval_runs 保留對照、before→after 一對齊全）；**row 37「Channel-B vault source backfill」命中並兌現**（registry entry + 可達性實測 + 鏡像片段數 `live_display_sync`）；**新增一 row「切 chunk 邏輯改動」**（原本全 registry 零命中，觸發 anti-pattern guard）。`CODEBASE_CONTEXT.md` 唔逐個列 vault 源目錄，故三摺頁目錄不需入 Directory Map。
- **舊記錄（S208 closeout）：**

- **Reconciled at:** 2026-08-20 (S208 closeout — Leonard「做埋 B C，然後收工」)
- **S208 state sections rewritten or confirmed current:** `Current Baseline`（prepend S208 段：交付物、敘事定調、兩個自我更正、字體環境事實、明寫零 OP 推進；S207 及更早段原文保留）；`Open Priorities`（**逐項覆核後決定整份不變**，banner 已重寫講明係「核完決定不變」而非跳過重生）；`Last Session Record`（S208 全新；S207 整段降為 `Previous Session Record (S207)`，內容一字未改，只改咗其中一句已完成事項嘅 stale 描述，見下）；`Next Session Opening Message`（整段重生）。`Architecture Decisions` / `User Environment` / `Mandatory Start Checklist` / `Regression Notes` / `Backlog` / `Supabase Technical Notes` 逐段核過，**確認 current、無需要改**（本 session 零 code / 資料改動，佢哋本來就冇受影響）。
- **S208 lifecycle check:** 對得上。`Completed This Session` 全部係新文件 + 新圖，**冇一項出現喺 NEXT**；`Next Priorities` ①–⑥ **冇一項喺 Completed 出現過**（本 session 冇掂過任何 OP）。`Risks` 零新增（純文件交付、無 live surface）。**主動修正一項 lifecycle 殘留**：S207 記錄第 5 點原寫「SESSION_LOG 已過 400 行門檻…留待收工做」，但該歸檔其實 S207 收工已完成（現 215 行 / 2 entry，`--check` = trigger=False，S208 起手實跑覆核），已改為完成式 —— 免下個 agent 當佢係未做嘅待辦。同一句 stale 描述亦已由開場白清走。
- **S208 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Last Session Record`；session trace / QC 證據 / 數字對源→`SESSION_LOG.md` S208 entry；**檔案地圖 + 可重用操作規程**→`CODEBASE_CONTEXT.md` Directory Map（5 條新項目 **連埋三張圖嘅重出指令同字體注意**，唔淨係列檔名）+ AI Maintenance Log；交付物本身→`dev/PROJECT_MILESTONES_REVIEW.md` / `dev/INFOGRAPHIC_PROMPT.md` / `dev/design/*`。**冇一項只留喺 handoff 或 log。** `PROJECT_DECISIONS.md` **不觸發**：本 session 冇新架構決策、冇 trade-off，只係把已有歷史重述成對外材料。
- **S208 stale snapshots left:** 無。**收工後修正一項自己嘅錯**：S208 全份文件原本寫 UTC 日期 `2026-08-19`（跟 S207 抄），`date -u` 實測係 `2026-08-20`（本機 BST）；handoff / log / CODEBASE_CONTEXT / 開場白 / `START_NEXT_SESSION_PROMPT.txt` / 回顧圖 A 嘅「今日狀態」全部已改，Session ID 一併由 `Claude_20260819_S208` 正規化為 `Claude_20260820_0826`（合 §12 格式）。S207 及更早嘅 `2026-08-19` **冇郁**，嗰個係真嘅。**主動記低本 session 自己報錯咗兩個數**：回顧檔初稿寫「登記來源 8 份底稿」（實情 registry S48 先建，正確係 120→151→244→268）同「公開分頁 4 → 8 → 4」（實情起點係 6，S74 鎖定架構已有 6 個 tab），兩個都係憑印象寫、對源之後更正，兩份檔已改、殘留檢查 clean。呢兩個錯**唔靜靜哋改走**，寫入 `Last Session Record` 教訓 (a)。
- **S208 opening message matches current state:** 是。整段重生並逐項對過：state header＝S208 / Supabase 17,473 / registry 268 / GUIDELINES_REGISTRY 177 / v3.3.0 / 凍結合約四個值 —— 全部同 `Current Baseline` 及開工探針一致；NEXT ①–⑥ 同 `Open Priorities` 逐條對；stale 嘅「收工待辦：log 歸檔」一句已清走。`START_NEXT_SESSION_PROMPT.txt` 由本 fenced block 重生並跑 mirror check。
- **S208 sync status:** DOC_SYNC **row 26「Knowledge operating architecture / planning doc」命中並兌現**（`CODEBASE_CONTEXT.md` Directory Map ✓ + AI Maintenance Log ✓；`SESSION_HANDOFF` priorities / risks **N/A** —— 冇 follow-up work 改變；`SESSION_LOG` task entry ✓）。**唔命中嘅 row 明確記低：** row 44「New user-facing feature」唔命中（零 backend endpoint、零前端 surface）；row 37 / 39 / 42 / 43（檢索、閘、eval、judge）一律唔命中（零 code 改動）。**凍結合約、`PLATFORM_VERSION`、Supabase、Render、GitHub Pages 全部零接觸**，故無 display-sync、無 redeploy。
- **舊記錄（S207 closeout）：**

- **Reconciled at:** 2026-08-19 (S207 closeout — Leonard「收工」)
- **S207 state sections rewritten or confirmed current:** `Current Baseline`（prepend S207 block：OP①② 完成／g17 交接更正／fail-closed 閘捉到自己個錯／兩個 regex 陷阱／g20-g25 亂碼／eval 結果；S206 及更早段原文保留、降為 🔙 歷史）；`Open Priorities`（**整段重生** —— 舊 ①② 已完成並移除、舊 ③④⑤⑥⑦ 上移為 ①②③④⑤、新增 ⑥ 監察缺口；段尾「451 條分類」更新為 86 條已有 deep link、真缺陷 139 → 53）；`Last Session Record`（S207 全新；舊 S206 段整段降為 `Previous Session Record (S206)`，內容一字未改）；`Next Session Opening Message`（state header S206→S207、新增「網頁源指章機制」事實段、NEXT 清單重生為 ①–⑥、探針加埋無頁碼 chunk 查法）。`Architecture Decisions` / `User Environment` / `Mandatory Start Checklist` / `Regression Notes` / `Backlog` 逐段核過，**確認 current、無需要改**。
- **S207 lifecycle check:** 舊 Open Priority ①（HTML 源指章）同 ②（g14 三缺陷）**已完成，已從 Open Priorities 移除**，唔會以未解狀態殘留；佢哋嘅完成證據喺 `Current Baseline` S207 段 + `Last Session Record` 3/4 + SESSION_LOG S207 entry。**新開嘅 ⑥ 唔係舊項目改名** —— 佢係「shipping deep link 之後先存在」嘅監察缺口，S207 之前唔存在。`Completed This Session` ↔ `Next Priorities` ↔ `Risks` ↔ 開場白四者對得上：完成項冇一個仲以未解狀態出現喺 NEXT，而 NEXT ①–⑥ 亦冇一個喺 Completed 出現過。**兩項明示 monitor-only / 靠註釋擋（非 blocker）：** (a) `g14`/`g17` 唔准 `--fetch`（registry notes 擋，唔係機制擋）；(b) per-chunk URL 無監察（已升格為 Open Priority ⑥，唔留喺 Risks 扮已處理）。
- **S207 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Open Priorities` + `Last Session Record`；逐步量度數字 / 閘證據 / 三條教訓→`SESSION_LOG.md` S207 entry；**可重用操作規程**→(a) `dev/DOC_SYNC_CHECKLIST.md` 新 row「Per-chunk deep link」（原本冇 row 覆蓋呢個 change type，按 registry rule 加咗先做）、(b) 「唔准 `--fetch`」→ `source_registry.json` notes、(c) 兩個 regex 陷阱嘅理由→code 註釋 + `dev/vault/test_carry_rules.py` 斷言（唔會被重生沖走）；架構／實作 narrative→`CODEBASE_CONTEXT.md` AI Maintenance Log；**跨 project 可轉移經驗**→Playbook inbox 4 份 proposal（S206 欠低嗰兩條 + S207 兩條）+ `usage/policychecker.log.md` 2 行。冇一項只留喺 handoff 或 log。
- **S207 stale snapshots left:** 無。S206 及更早段全部保留原文。**主動更正一處因本 session 而 stale 嘅述句**：交接原寫「真正指得到章嘅只有 g14 嗰 77 條」，實測 g17 6/6 亦指得到（3 個真子頁喺另一條 path 之下 + 3 個附件 PDF），已喺 `Current Baseline` S207 段 ② 明文更正，唔靠讀者自己對數。另**主動記低自己報錯咗一個數**（標記外洩 683 → 實數 22，差 31 倍，因偵測器 false positive），寫入 `Last Session Record` 教訓 (d) 同 SESSION_LOG Risks，唔靜靜哋改走。
- **S207 opening message matches current state:** 是。整段重生並**逐項對過**：state header＝S207 / HEAD＝本 closeout commit / Supabase 17,473 / registry 268 / GUIDELINES_REGISTRY 177 / v3.3.0 / 凍結合約四個值 —— 全部同 `Current Baseline` 同 live 探針一致。`START_NEXT_SESSION_PROMPT.txt` 已由本 fenced block 重生，並跑 mirror check **byte-identical = True**。
- **S207 sync status:** DOC_SYNC **row 37「Channel-B vault source backfill / page-carry into Supabase」命中並兌現**（registry entry ✓；SOURCE_SETS / TOPIC_KEYWORDS / QUERY_EXPANSIONS parity **N/A** —— 零新源、零 route 改動；handoff Current Baseline 記低 chunk 數 ✓；SESSION_LOG 帶閘證據 ✓；CODEBASE_CONTEXT AI Maintenance Log ✓，無新 vault 目錄；typecheck + build exit 0 ✓；live smoke ✓）。**Registry updated:** 新增 row「Per-chunk deep link」。**公開合約零改動**：`guidelines.json` / `app.html` GUIDELINES_REGISTRY / `data.json` 一律未改（實查證 g14 title 喺嗰三處本來就啱，錯嘅只有 vault extract 一份），故 row 「guidelines.json public contract」**唔命中**。平台版本號未 bump（`cleanChunkText` 係後端顯示清理、`app.html` 零改動）。
- **舊記錄（S206 closeout）：**

- **Reconciled at:** 2026-08-18 (S206 closeout — Leonard「同意，收工」)
- **S206 state sections rewritten or confirmed current:** `Current Baseline`（prepend S206 block：OP① 重新定位／根因兩層／規則共用唔共用 chunker／11 源重入／eval 綠／代價已量；S205 段原文保留降為 🔙 歷史）；`Open Priorities`（**整份重生**：舊 ① 因根因重新定位而改寫成新 ③ 並明寫「唔可以照抄舊描述」，新增 ① HTML 指章、② g14 三個同源缺陷、④ eval chunk-層儀器缺口，並喺段尾釘死「剩餘 451 條分類」免下次重數）；`Last Session Record`（S206 全新，S205 降 `Previous Session Record (S205)` 原文保留）；`Next Session Opening Message`（整段重生）。
- **S206 lifecycle check:** 舊 Open Priority ①（檢索「可見 ≠ 見到啱嗰段」）**冇當完成、亦冇原文保留** —— 佢嘅兩個修法已被實測否定，故重寫為新 ③ 並附否定證據（0.6049 / 14-81 / 0.6537 表頭行）同一個明確禁令（唔可以照抄）。舊 ②（GUIDELINES_REGISTRY 落後）、③（特殊學校表）、④（content_kind）**未做，原文保留**，順序下移為 ⑤⑥⑦。S206 本身完成嘅嘢（頁碼修復）**唔會以未解狀態殘留**：剩餘工作已明確拆成 ①②（HTML 源）同「已 work / 修唔到」兩類，唔係籠統掛住「451 條未修」。
- **S206 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Open Priorities` + `Last Session Record`；逐步量度、Gate 證據、UI 實拍→`SESSION_LOG.md` S206 entry；**可重用操作知識（唔會被重生嘅位）**：根因兩層同「共用規則、唔共用 chunker」嘅理由→`build_wiki_index.py` `carry_pages` docstring + `expand_vault.py` 兩段註釋 + 三個 commit message；11 個源日後 refresh 注意事項（尤其 `staff_est_pri` 唔准 `--fetch --force`）→`source_registry.json` notes；「報數要拆類」→ 已存 memory `feedback_breakdown_before_scope`。
- **S206 stale snapshots left:** 無。S205 段全部保留原文。**主動更正兩處因本 session 而 stale 嘅述句**：(a) 我早前根據 `repage_pdfs.py` docstring 講「repage 只跑過 3 個源」= **錯**，實際 `PILOT_OUT` 68 項、磁碟 117 個 `_repaged.txt`，docstring 過時（已喺對話更正，並改為指出真根因係 `expand_vault` 從未寫標記）；(b) 我早前把 HTML 源可救條數講成 93，實測後更正為 **77（只有 g14 有真 slug）**，已寫入 Open Priority ①。
- **S206 opening message matches current state:** 是。整段重生（state header＝S206／HEAD＝本 closeout commit／chunk 17,473／無頁碼 451／NEXT 七項／新增一條紀律），並逐字鏡像至 `START_NEXT_SESSION_PROMPT.txt`（mirror check 見 closeout 輸出）。
- **S206 sync status:** DOC_SYNC **row 37「Channel-B vault source backfill / page-carry into Supabase」命中並兌現**：registry entry ✓（11 個源 notes 補 repage 記錄）、SOURCE_SETS/TOPIC_KEYWORDS parity **N/A**（零新源、零 route 改動）、handoff Current Baseline 已載 chunk 總數 **17,473** 同帶標記數 **17,022** ✓、log entry 帶 Gate1/Gate2 證據 ✓、`CODEBASE_CONTEXT.md` AI Maintenance Log ✓（無新 vault 目錄故 Directory Map 不變）。Gate1 markers==pages 全部對數（121/121、197/197、9/9…）；Gate2 post-count==insert。`update_log.json` **N/A**（無新來源公開，只係現有來源重入）。凍結合約 + `PLATFORM_VERSION` 零接觸。
- **舊記錄（S205 closeout）：**

- **Reconciled at:** 2026-08-18 (S205 closeout — Leonard「收工」)
- **S205 state sections rewritten or confirmed current:** `Current Baseline`（prepend S205 block：probe 兩次讀齊 + 已刪 + 部署後讀已閂；S204 段原文保留降為歷史）；`Open Priorities`（**整份重生**：舊 ① route-probe 已完成故移除，餘四項上移並重新編號 ①–④，順手修好兩處指向舊編號嘅交叉引用）；`Last Session Record`（改寫為 S205，S204 原文完整降為 `Previous Session Record (S204)`，零刪減）；`Next Session Opening Message`（重生為 S205 版）。`Architecture Decisions` / `Regression / Verification Notes` / `User Environment` / `Mandatory Start Checklist` / `Supabase Technical Notes` 本 session 零改動、確認仍然 current。
- **S205 lifecycle check:** 舊 Open Priority ①（route-probe）**已完成並已從 Open Priorities 移除**，唔會以未解狀態殘留喺 next priorities / risks / opening message —— opening message 嗰個 🔴🔴 紅旗亦已改寫成已閂結果。Backlog ⑥「拆 backend channel-a」由「等 OP① 有結果」改為「S205 已解鎖前置」，係**條件變更**而非完成，故仍留 Backlog。`START_NEXT_SESSION_PROMPT.txt` 本 session 中途有意 drift，本次 closeout 已重生對齊（見下）。零 completed-but-still-open 衝突。
- **S205 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` + `Open Priorities` + `Last Session Record`；逐步證據 / 四個標記時間 / 兩次讀數→`SESSION_LOG.md` S205 entry；穩定專案事實（probe 已移除、S198 記錄閂上）→`CODEBASE_CONTEXT.md` AI Maintenance Log；DOC_SYNC row 48 生命週期收尾→已記於 log `Sync` 欄。**可轉移經驗**（rolling 保留窗唔使重開 / 期望語氣唔等於觀察）→ 未入 playbook，已列為下 session 可做嘅 inbox 提案（見 Open Priorities 下方 Backlog 未列，故記於此）。
- **S205 stale snapshots left:** 無。S204 段全部保留原文（降 `Previous Session Record (S204)`）。另主動更正兩處因本 session 而 stale 嘅述句：Open Priorities 舊 ⑤ 內文「同 ② 係同一個根」→「同 ① 係同一個根」；Backlog「拆 backend channel-a（⑥，等 OP① 有結果）」→「S205 已解鎖」。
- **S205 opening message matches current state:** 是。整段重生（state header＝S205／HEAD＝`bee54c9`／NEXT 四項／probe 段由紅旗改為已閂結果），並已逐字鏡像至 `START_NEXT_SESSION_PROMPT.txt`（mirror check 見 closeout 輸出）。
- **S205 sync status:** DOC_SYNC_CHECKLIST **row 48「臨時觀測 code 加落既有 backend route」＝ 生命週期收尾**（該 row 四項要求全部兌現：臨時性、刪除責任、讀取日期、自測識別標記）。本 session 零入庫、零檢索改動、零 synthesis-gate 改動、零凍結合約接觸 → 其餘 row 無命中。
- **舊記錄（S203 closeout）：**

- **Reconciled at:** 2026-08-02 (S203 closeout — Leonard「收工」)
- **S203 state sections rewritten or confirmed current:** `Current Baseline`（prepend S203 block：⑩ 文件 drift 修好／② judge V4 量度未 ship＋reframe／⑧ g24/sag 偵查出 PLAN／probe 未刪／零生產改動）；`Open Priorities`（**整份重生為 S203 段**：① 8/5 route-probe 不變、② reframe 非-prompt、⑧ 更新真數 377＋PLAN、⑩ 標 DONE 移出、S202 段降歷史）；`Last Session Record` 由 S202 重寫為 S203（S202 降 `Previous Session Record (S202)`，no-loss）；`Next Session Opening Message` 就地更新（state header→S203／做咗段→S203 三件事／NEXT ② reframe／NEXT ⑧ 真數＋PLAN／NEXT ⑩ DONE／必讀 (a)→FINDINGS S202 段／紀律 +#6 judge 非決定性）；本段。
- **S203 lifecycle check:** ⑩ 完成 → 已從 Open Priorities 移出（標 ✅ DONE，非殘留未解）。② 量度完成 → 由「硬化 judge V4」reframe 為「非-prompt 對象核對機制」（未完成、方向已轉、V4 prompt-tuning 明確標為 dead-end 不再試）。⑧ 偵查完成 → 仍為未解（執行合併未做，PLAN 備妥、HIGH risk 等 GO，正確保留）。① route-probe 8/5 讀＋刪 probe 不變（未做，正確保留）。**無已完成項殘留為未解 next priority／active risk**。**Risk 更新**：生產度臨時 probe 仍 live（`server.ts:168–198`），8/5 讀完必刪 — active 不變；V4 未 ship 故無新增生產 risk。
- **S203 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` S203 ＋ `Open Priorities`；**可重用知識（唔會被重生嘅位）**：⑩ 修正落 `PROJECT_MASTER_SPEC.md`/`SYSTEM_ANALYSIS_AND_ROADMAP.md`/`HANDOFF_PACKAGE.md` 正文；② 量度定案＋方法論落 `dev/source/JUDGE_PROMPT_FINDINGS.md` S202 段（+ `judge_transplant_fresh_s202.json` `_meta`、V4a/V4b prompt、harness `--cases`）；judge 非決定性教訓 → opening message 🧭 紀律 #6；⑧ 偵查真數＋PLAN → Open Priorities ⑧（執行前檔）；session trace/QC/run 檔 → `dev/SESSION_LOG.md` S203 entry + `judge_runs/2026-08-02_s202_*`。無 stack/service/secret 改動。
- **S203 stale snapshots left:** 無。S202 段全部保留原文（降 `Previous Session Record (S202)`）。**主動標註並更正因本 session 而 stale 嘅舊述**：⑧「215 條文字相同」（handoff/PMS-era doc/searchChannelB.ts:415 註解/code comment sag 415·g24 300）→ 實測 377／g24 383·sag 409，已在 Open Priorities ⑧ ＋ Current Baseline 更正（searchChannelB.ts:415 + wikiRepository.ts 註解數字 stale 待 ⑧ 執行時一併清，已列入 PLAN 步 ⑥）。
- **S203 opening message matches current state:** 是。就地更新（state header＝S203／HEAD＝本 closeout commit／三件事＝⑩·②·⑧／NEXT list 已同步）。`START_NEXT_SESSION_PROMPT.txt` 由本 block 重生並 mirror check（見下 sync）。
- **S203 sync status:** ⑩ 純文件（PMS/roadmap/HANDOFF_PACKAGE 正文）——非 backend/retrieval/synthesis-gate 改動，DOC_SYNC 無命中 code change category；② V4 未 ship（生產 judge prompt byte-identical，`--check-parity` 綠）、Supabase 零寫入；⑧ 純唯讀偵查、零檔改（除治理檔）。凍結合約＋`PLATFORM_VERSION` 零接觸（Supabase 16,062 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / served 3.2.2）。Render/Pages 零 deploy（無 production code 改）。§4a：SESSION_LOG 145 行（<400）→ no-op（S202 已維護至 122，S203 加一 entry）。
- **舊記錄（S202 closeout）：**

- **Reconciled at:** 2026-08-02 (S202 closeout — Leonard「收工」)
- **S202 state sections rewritten or confirmed current:** `Current Baseline`（prepend S202 block：route-probe 8/2 讀＝全窗綠 26 行全部有主／儀器雙重對照＝S198 紀律落地／probe 未刪／零 code·Supabase·route 改動＋§4a log 維護）；`Open Priorities`（prepend S202 權威 block：① 8/2 已讀更新為淨剩 8/5 讀＋刪 probe，②–⑪ 明列不變見 S201 段）；`Last Session Record` 由 S201 重寫為 S202（S201 降 `Previous Session Record (S201)`，no-loss）；`Next Session Opening Message` 五處就地更新（state header→S202／🔴🔴 route-probe→8/2 done·8/5 left／做咗→S202／NEXT ①→8/5 only／⏰⏰ 時間關鍵→8/5）；本段。
- **S202 lifecycle check:** S201 唯一時效遺留（NEXT ① route-probe 觀察窗，8/2+8/5 讀）**第一次讀已完成**＝全窗綠零外部呼叫，已由「剩 2 日內」更新為「淨剩 8/5 一次讀＋刪 probe」，**未從 Open Priorities 移除**（因 8/5 讀＋刪 probe 仍未做，正確保留為 ①，非殘留已完成項）。②–⑪ 全部沿用 S201、無變動、無已完成項殘留為未解 next priority。新增未解項：無（純執行既有 ①）。**Risk 更新**：生產度臨時 probe 仍 live（`server.ts:168–198`），8/5 讀完必刪 — 仍為 active，量度視窗確認零外部後即可拆。
- **S202 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` S202 ＋ `Open Priorities`；量度結果 + 儀器對照方法 + §4a 維護 → `dev/SESSION_LOG.md` S202 entry；**可重用教訓（Render Hobby log negative≠零事件、必先即時對照＋回溯已知事件驗窗、「Last 7 days」未 set 令 search 空手）** 已在 handoff `Last Session Record` §6 ＋ opening message 🧭 紀律 #2（S198 既有紀律再落地，無需新增 rule pack）。無 code／Supabase／registry 改動故無 CODEBASE_CONTEXT 更新。working scratch（screenshot 觀察）未持久化。
- **S202 stale snapshots left:** 無。S201 段全部保留原文（降為 `Previous Session Record (S201)`），無改寫歷史。opening message 舊 route-probe「8/2+8/5 剩 2 日」述已就地更新為 8/2-done。
- **S202 opening message matches current state:** 是。`Next Session Opening Message` 五處就地更新（見上），state header ＝ S202 / HEAD 2ec82cf / route-probe 8/2 done·8/5 left。`START_NEXT_SESSION_PROMPT.txt` ＝頂層 dormant root redirect（指向 Draft、非 per-session state），本 session 零改動仍 valid（Draft opening message 為權威）。
- **S202 sync status:** 本 session 零入庫、零檢索改動、零 synthesis-gate 改動 → DOC_SYNC 無命中 change category（純唯讀量度＋handoff/log 持久化）。§4a：`--check` trigger=True（402 行）→ `--apply` 執行，402→122 行、4 舊 entry 搬入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬冇刪、archive pointer 已在）。凍結合約＋`PLATFORM_VERSION` 零接觸（Supabase 16,062 零寫入 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / served 3.2.2）。Render/Pages 零 deploy（無 code 改）。
- **舊記錄（S201 closeout）：**

- **Reconciled at:** 2026-07-31 (S201 closeout — Leonard「C = 收工」)
- **S201 state sections rewritten or confirmed current:** `Current Baseline`（prepend S201 block：擴闊 decline 集 11→21／量 V3 baseline 12-12·19-21／收 footnote judge-bypass fc287ff／deploy+live 驗 D17 flip·D13 保留·D01 未變）；`Open Priorities`（**整份重生為 S201 段 11 項**，S200 段 footnote-bypass 線全部完成降歷史；route-probe 觀察窗升 **①**〔時間閘 8/2 剩 2 日〕、硬化 judge V4 收 transplant 為 **②**）；`Last Session Record` 由 S200 重寫為 S201（S200 降 `Previous Session Record (S200)`，no-loss，並標註 S200「D01 judge 從不 serve」已因 S201 收 bypass 而 stale）；`Next Session Opening Message` 重生（S201 做咗／NEXT 以 route-probe 觀察窗為 #1／transplant V4 為 #2／必讀改指 FINDINGS S201 段）；本段。
- **S201 lifecycle check:** S200 唯一未完 active 遺留（NEXT ②「收 footnote bypass」，兩硬前置 deploy+decline 集擴闊）**已完成**：兩前置齊 → ship（移走 trustedFootnoteLead）→ deploy → live 驗，已從 Open Priorities 移除、唔再列未解。其衍生**新項「硬化 judge V4 收 transplant 類」**（D01/GN10，V3 judge prompt 自己 miss）正確列為 ②（未完成、有明確前置陷阱：frozen set 上 tune 會燒 held-out）。S198 route-probe 觀察窗（原 S200 ⑤）**時效已到 → 升為 ①**（8/2+8/5，剩 2 日）。**無已完成項殘留為未解 next priority／active risk**：D01/GN10 live 仍答係**明確標為 pending V4 嘅已知殘留**（收 bypass 令佢哋去見 judge，但 judge 自己 miss，唔係 regression、唔係本次可完成之交付）。新增未解項：硬化 judge V4（②）。
- **S201 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` S201 + `Open Priorities`；**可重用知識 →唔會被重生嘅位**：`backend/src/api/searchChannelB.ts` `synthesizeAnswer` S201 註解（footnote bypass premise 被 D01 證偽）、`dev/source/JUDGE_PROMPT_FINDINGS.md` S201 頭註（D01 而家過 judge）+ Still open（擴闊集數 + transplant 兩條 + frozen-set tune 陷阱）、`judge_acceptance_cases.json` `_meta.widened_s201`、`dev/CODEBASE_CONTEXT.md`（footnote bypass 描述更新 + AI Log S201）；量度/QC/live before→after → `dev/SESSION_LOG.md` S201 entry；V3 baseline run + 擴闊集 → `dev/source/judge_runs/2026-07-31_s201_v3_widened.json` + `judge_acceptance_cases.json`（commit）；working scratch（candidate/chunks/labelled/live_check/poll）留 scratchpad 未 commit。
- **S201 stale snapshots left:** 無。**主動標註三處因本 session 而 stale 嘅舊述**並就地更正：(a) S200「D01 生產行 footnote bypass、judge 從不 serve」→ 收 bypass 後 D01 過 judge（Previous Session Record S200 §4 + FINDINGS S201 頭註）;(b) CODEBASE_CONTEXT footnote_lead_probe 描述「takes lead slot *and* skips judge」→ 加 S201 判-skip 已移走;(c) FINDINGS Still open「14 candidate awaiting labelling」→ 已 retire 記 S201 實況。**冇靜靜改寫歷史**（S200 record 保留原文 + 加 stale 標註）。
- **S201 opening message matches current state:** 是。`Next Session Opening Message` 重生（HEAD S201 commits chain / 收 bypass fc287ff deploy live / NEXT ① route-probe 8/2 時間閘 / ② transplant V4 / 必讀 FINDINGS S201），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check（見下 sync）。
- **S201 sync status:** DOC_SYNC 命中 **row 38「Synthesis 前置閘改動」**（收 footnote bypass）—— footnote_lead_probe before→after 30/30·5/13·0err 零損失 ✓ / fail-open 保持（judge API error 仍答）✓ / **live 重探 before→after ✓**（D17 flip / D13 保留 / D01 未變）/ CODEBASE_CONTEXT ✓ / SESSION_LOG before→after ✓；另 **row 41「Anti-confab judge 驗收集擴闊」**（+11 case，非 prompt 改動、parity 已證）。required checks 全跑（--self-test / --check-parity / --plumbing-check / tsc / footnote_lead_probe before==after）。凍結合約 + `PLATFORM_VERSION` 零接觸（Supabase 16,062 零寫入 / registry 256 / `_meta` 2.3.0 facts 455 / guidelines 158 / served 3.2.2）。Pages 零改動；**Render auto-deploy on push（S117）→ `fc287ff` backend redeploy，live 驗 D17 flip 證實新 code 在跑**。`update_log.json` N/A（非入庫、非用戶面新功能）。§4a：`--check` trigger=False（400 行 / 7 entries / 最舊 2026-07-27）→ no-op。
- **舊記錄（S200 closeout）：**

- **Reconciled at:** 2026-07-30 (S200 closeout — Leonard「全做」→「收工」)
- **S200 state sections rewritten or confirmed current:** `Current Baseline`（prepend S200 block，6 點：ship V3／驗收 21-22／明文閘 override／QC 全綠／🔴 deploy 傳播外部驗唔到／🔴 D01 live 未變）；`Open Priorities`（**整份重生為 S200 段**，S199 降歷史；③ ship V3 完成移除、④ 收 bypass 升 #2 連兩硬前置、新增 deploy-confirm #1）；`Last Session Record` 由 S199 重寫為 S200（S199 降 `Previous Session Record (S199)`，no-loss）；`Next Session Opening Message` 重生（狀態頭／S200 做咗／NEXT 清單／必讀 (b)／post-startup deploy 提醒）；本段。
- **S200 lifecycle check:** S199 唯一「決定+方向」遺留（Option 2、judge V3 次序）已推進：**③ ship V3 完成 → 已從 Open Priorities 移除、唔再列未解**；其衍生 ④「收 footnote bypass」升做 S200 #2 並**明列兩個硬前置**（deploy 確認 + decline 集擴闊），非殘留而係有前置嘅新項。S198 觀察窗**原封保留為 S200 ⑤**（時效閘，8/2+8/5 未到）。**無已完成項殘留為未解 next priority／active risk。** 新增未解項：deploy 確認（①，Leonard-only）、收 bypass（②）。
- **S200 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` S200 + `Open Priorities`；**明文 override（§2 rule 6）+ 可重用判斷 →唔會被重生嘅位**：`dev/source/JUDGE_PROMPT_FINDINGS.md` S200 header（override 三理由 + D01 唔係 judge-served）、`dev/CODEBASE_CONTEXT.md`（judge_acceptance baseline 更新 + AI Log S200）、`backend/src/api/searchChannelB.ts` L704-709 code 註釋（V3 rationale，handoff 會重生、code 唔會）；量度/QC 細節 + override 記錄 → `dev/SESSION_LOG.md` S200 entry；run artifact → `dev/source/judge_runs/`（commit）。
- **S200 stale snapshots left:** 無。**主動更正咗交接一處 overclaim**：S199「decline 全保」→ artifact 實 10/11（D01 漏），已喺 SESSION_LOG S200 + Current Baseline S200 ② 連原數並存更正（冇靜靜改）。
- **S200 opening message matches current state:** 是。`Next Session Opening Message` 重生（S200 ship V3 + override + 🔴 deploy 未外部確認 + 🔴 D01 live + NEXT 以 deploy-confirm 為 #1），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check。
- **S200 sync status:** DOC_SYNC 命中 **row 41「Anti-confab judge prompt 改動」** —— required docs 全數更（`judge_acceptance.py` `SHIPPED_PROMPT` + `--check-parity` / `JUDGE_PROMPT_FINDINGS.md` S200 / `CODEBASE_CONTEXT.md` / SESSION_LOG before→after / handoff Risks-in-baseline）；required checks 全跑（`--self-test`／`--check-parity`／**`--plumbing-check`**／false-vs-accuracy 分開報／ship 後 `footnote_lead_probe.py`）。凍結合約 + `PLATFORM_VERSION` 零接觸（Supabase 16,062 零寫入 / registry 256 / `_meta` 2.3.0 facts 455 / guidelines 158 / served 3.2.2）。Pages 零改動；**Render auto-deploy on push（S117）→ `bcf7c4f` 觸發 backend redeploy**（judge prompt code 改）。`update_log.json` N/A（非入庫、非用戶面新功能）。§4a：377 行 / 6 entries / 最舊 2026-07-27 → trigger=False → no-op。
- **Reconciled at:** 2026-07-30 (S199 closeout — Leonard「收工」)
- **S199 state sections rewritten or confirmed current:** `Current Baseline`（prepend S199 block，6 點：Leonard 叫停重構 Channel A 退役／拍板 Option 2 + triage／judge 量錯 model 又更正／V3 生產 model 21-22/D01 共用 false answer／footnote bypass live 發現／「對照組證明唔到儀器指住正確系統」一堂）；`Open Priorities`（**整份重生為 S199 段 12 項**，S198 降為歷史、觀察窗沿用至 ⑤）；`Last Session Record` 由 S198 重寫為 S199（S198 降為 `Previous Session Record (S198)`，no-loss）；`Next Session Opening Message` 重生；本段。
- **S199 lifecycle check:** S198 唯一 active 遺留（觀察窗 + probe）**原封不動保留為 S199 ⑤**（硬外部閘，8/2 + 8/5）。S197 遺留全部收納入 S199 段：judge（S197 ③ → S199 ③，並由「shipped 近乎恆等於否」更正為「嗰個係 fallback model，生產 gpt-4o-mini 8/11」）、總帳未讀桶（S197 ④ → S199 ⑧）、100 條鏡像穿窿（S197 ⑤ → 由 Option 2 決定吸收，Leonard 已拍板升做 footnote → S199 ①②）、g24 dedup（→ ⑨）、維護（→ ⑩）、文件 drift（→ ⑪）、roadmap（→ ⑫）、PAT（→ ⑥）。**無已完成項殘留為未解 next priority**：A 嘅重構同 triage、B 嘅量度全部係「產出決定 + 記錄」，唔係可完成嘅交付;Option 2 方向已定但**執行未開始**，正確列為 ①（未完成，非殘留）。**新增未解項**：Option 2 入庫（①）、24 條孤兒細決定（②）、ship V3（③）、收 footnote bypass（④）。
- **S199 persistence routing checked:** 是。當前狀態→handoff `Current Baseline` S199 block + `Open Priorities`;**可重用程序知識 →三個唔會被重生嘅位**：`dev/source/JUDGE_PROMPT_FINDINGS.md`（判斷 model 要 dashboard 確認 / 生產 model 數 / footnote bypass 耦合）、`dev/source/CHANNEL_A_COVERAGE_FINDINGS.md` §5-6（Channel A 資料模型缺口 + Option 2 triage + url≠出處陷阱）、`dev/source/judge_acceptance.py` 註釋 + `--plumbing-check`（對照組局限）;凍結驗收集 + 四份 run（nano ARTIFACT ×2 + 生產 ×2 + bypass live）→ `dev/source/judge_runs/`（commit，跨 session 可比）;V3 候選 prompt → `dev/source/judge_prompts/v3_s196.txt`（parity 斷言）;量度細節同四個自我更正 → `dev/SESSION_LOG.md` S199 entry;DOC_SYNC 新增「Anti-confab judge prompt 改動」row。
- **S199 stale snapshots left:** 無。**本 session 內主動更正咗自己四次**：(a) 用錯 judge model（code default vs Render dashboard），出兩份唔代表生產嘅 baseline，Leonard 撳 dashboard 揪返，nano run 已改名 ARTIFACT + S196 findings 標「未經生產驗證」;(b) D13 標錯做空白（Supabase 核實 970/1570 有出處），已剔;(c)「7/7 砌數」overclaim，逐條讀後散為「1 條實錘、1 條其實啱」;(d) decline 半邊講 12 實際 11，由檔案數返更正。四項連同 model 教訓全部寫入 SESSION_LOG + commit message。**冇靜靜改寫歷史。**
- **S199 opening message matches current state:** 是。`Next Session Opening Message` 重生（Channel A Option 2 入庫為首要 + 24 條孤兒決定 / judge ship V3 次序 / footnote bypass / 🔴 觀察窗 8/2+8/5 / model 要 dashboard 確認），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check。
- **S199 sync status:** DOC_SYNC 命中 **1 row（新增，「Anti-confab judge prompt 改動」，表格 32→33 行）** —— 按 anti-pattern guard 先補行再填;`CHANNEL_A_COVERAGE_FINDINGS.md` / `JUDGE_PROMPT_FINDINGS.md` 更新屬既有檔內容擴充,`CODEBASE_CONTEXT.md` Directory Map 新增 `judge_acceptance.*` 條目。`update_log.json` **N/A**（零入庫）。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實：Supabase 16,062 零寫入 / registry 256 / `_meta` 2.3.0 facts 455 / guidelines 逐 topic 加總 158 / served `PLATFORM_VERSION 3.2.2`）。Pages **零改動**（無前端改動）;Render **零 deploy**（`searchChannelB.ts` `RELEVANCE_JUDGE_PROMPT` 未郁,判斷 model 用嘅係離線量度,冇部署）。§4a：`--check` trigger=False（316 行 / 4 entries）→ no-op。
- **舊記錄（S198 closeout）：**

- **Reconciled at:** 2026-07-30 (S198 closeout — Leonard「收工」)
- **S198 state sections rewritten or confirmed current:** `Current Baseline`（prepend S198 block，7 點：指示本身量唔到嘢／已換主動量度／§3 停低一次／同一 session 踩兩次同一陷阱／更正 cold start 歸因＋dashboard UTC+1／repo 內零呼叫點／🔴 臨時 code 同觀察窗）；`Open Priorities`（**整份重生為 S198 段**，S197 ① 已被取代，②–⑨ 明文標示沿用）；`Last Session Record` 由 S197 重寫為 S198（S197 降級為 `Previous Session Record (S197)`，no-loss）；`Next Session Opening Message` 重生；本段。
- **S198 lifecycle check:** S197 ① **已解決但唔係用原本嘅方式** —— 原指示係「睇 log 有冇流量」，實測證明佢量唔到嘢，故**唔可以標為完成**，改為重述成「觀察窗進行中，8/2 + 8/5 讀」並降為 ⑤（明文寫住前置＝讀完窗 + 刪 probe）。S197 ②–⑨ **全部原封不動**，重新編號為 S198 ②–④ 加沿用段。**無已完成項殘留為未解 next priority**：probe 上線同 XFF 修正已完成並只以「臨時 code 待刪」形式保留為 risk，唔係 priority。**新增未解項**：觀察窗未讀、probe 未刪、`HANDOFF_PACKAGE.md:32` drift。
- **S198 persistence routing checked:** 是。當前狀態＋觀察窗讀取日期＋刪除責任→handoff `Current Baseline` S198 ⑦ 同 `Open Priorities` S198 ①；**可重用程序知識（「一個工具嘅沉默唔係證據」＋ negative control ＋ 部署確認唔可以靠猜重啟）→三個唔會被重生嘅位**：`dev/PROJECT_DECISIONS.md` Insights S198、`dev/DOC_SYNC_CHECKLIST.md` 新 row 嘅驗收欄、`backend/src/server.ts` probe 註釋（handoff 會被重生、code 唔會）；量度細節同三個自我更正→`dev/SESSION_LOG.md` S198 entry；歸檔內容→`dev/archive/SESSION_LOG_2026_Q3.md`（新檔，原文保留）。
- **S198 stale snapshots left:** 無。**本 session 內主動更正咗自己三次**：(a) 兩次信咗量唔到嘢嘅工具嘅沉默（log search、`/health` 重啟偵測），第二次係喺明知第一次陷阱之後一個鐘內再踩；(b) 講錯 08:52 UTC 嗰個 cold start 係我杯 curl 引起（實際早我 43 分鐘，來源未查明）；(c) PLAN 承諾 IP 認人首版做唔到，按 §3 停低等 Leonard 批先改。**另修好一個既有問題**：`dev/SESSION_LOG.md` `ack:log-entry` marker 唔平衡（S195B 缺 `start`），已補一行、純新增零資訊改動，4/4 平衡；**先查明影響（歸檔腳本用 `^## YYYY-MM-DD` 切 entry、唔用 marker）後至修**。
- **S198 opening message matches current state:** 是。`Next Session Opening Message` 重生（🔴 臨時 code 置頂／觀察窗兩個讀取日期／扣起 24 行自測流量／dashboard UTC+1／落手前必讀由兩件變三件／NEXT 重排為 judge 優先、拆 route 降為等窗）；`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並做 mirror check。
- **S198 sync status:** DOC_SYNC 命中 **1 row（新增，31→32）**「臨時觀測 code 加落既有 backend route」—— 按 anti-pattern guard 先補行再填。`update_log.json` **N/A**（零入庫）。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實：Supabase 16,062 零寫入／registry 256／`_meta` 2.3.0 facts 455／guidelines 逐 topic 加總 158／served `PLATFORM_VERSION 3.2.2`）。Pages **零改動**（本 session 無前端改動）；Render deploy 5 次（每個 commit 一次），probe 已 live 驗。§4a：`--check` trigger=True（462 行／8 entries）→ **已執行 `--apply`**，462→199 行、8→4 entries、4 個 entry 入新檔 `dev/archive/SESSION_LOG_2026_Q3.md`，守恆 4+4=8。
- **舊記錄（S197 closeout）：**

- **Reconciled at:** 2026-07-29 (S197 closeout — Leonard「收工」)
- **S197 state sections rewritten or confirmed current:** Current Baseline（prepend S197 block：Supabase **16,062 零寫入**、registry **256 不變**、v3.2.2 不變、凍結合約機械核實零接觸；退役標準／鏡像剔除嘅必要性／兩次自我推翻／44% 覆核失敗率／阻塞點）；Open Priorities（**整份重生** 9 項，並更正 roadmap 三處過時狀態）；`Last Session Record` 由 S196 重寫為 S197（S196 降級為 `Previous Session Record (S196)`，no-loss）；`Next Session Opening Message` 重生；本段。
- **S197 lifecycle check:** 舊 Open Priorities 6 項處置 —— ①PAT→**原封不動保留**（我做唔到，降為 ②）；②judge prompt→**未做，原文保留為 ③**，前置條件不變；③g24/sag→**不變**，降為 ⑥；④封面 baseline→**不變**，併入 ⑦ 維護；⑤spotlight→**不變**，併入 ⑦；⑥MIN_OVERLAP 鏡像→**不變**，併入 ⑦。新增 ①（Render logs 阻塞）／④（總帳未讀桶）／⑤（100 條鏡像仍穿窿）／⑧（文件 drift）／⑨（roadmap 過時更正）。**無已完成項殘留為未解 next priority 或 active risk**：前端退役同 9 條鏡像退役已完成並已從清單移除，只保留仍然穿窿嗰 100 條為 ⑤。
- **S197 persistence routing checked:** 是。當前狀態→handoff Current Baseline S197 block；**量度方法＋兩次自我推翻＋44% 覆核失敗率→`dev/source/CHANNEL_A_COVERAGE_FINDINGS.md`**（可重用程序知識，唔止留喺 log）；逐條 tier + 出處→`CHANNEL_A_RETIREMENT_LEDGER.tsv`（tracked）；三份 eval run→`dev/source/eval_runs/`（commit，跨 session 可比）；**「唔准由總帳延長 retired list」呢條紀律→`searchChannelB.ts` `RETIRED_MIRROR_CHUNK_IDS` 上面嘅註釋**（下一個想加 id 嘅人一定睇到，唔係只留喺 log）；跨 session 累積模式（機械判定唔可以取代讀原文）→`dev/PROJECT_DECISIONS.md` Insights；DOC_SYNC 新增「store chunk 退出服務路徑」row；run JSON + 14MB embed cache→gitignored（可由工具重生）。
- **S197 stale snapshots left:** 無。**本 session 內主動更正咗自己三次**：(a) 把尺壞咗（中文數字），修完 71 條轉桶、COVERED 100→149，並明寫個 bug 方向係「令保留 Channel A 睇落更有道理」；(b) 憑一條 query 提議整批剷走 109 條並講「拎走唔係損失」，量埋成批後證實錯，已喺報告、commit message、findings 檔逐處更正；(c) eval 新增嘅 4 條 query 有 2 條預期釘錯，由 baseline 捉返並即時改（而唔係留住永久紅燈）。**另發現一個未修嘅既有問題**：`dev/SESSION_LOG.md` 嘅 `ack:log-entry:start`／`end` marker 數目本身唔對稱（本 session 前 2/3，我加咗一對後 3/4）—— **唔係本 session 造成，冇靜靜改寫歷史 entry**，記錄喺此待日後修。
- **S197 opening message matches current state:** 是。`Next Session Opening Message` 重生（16,062 零寫入／前端＋9 條鏡像已退／backend 阻塞於 Render logs／44% 紀律／eval 34 條），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 **byte-for-byte mirror check PASS**。
- **S197 sync status:** DOC_SYNC 命中 2 row（檢索 eval harness 改動 ✓ eval_queries 30→34＋三份 run＋before→after 對／**新增 1 row「store chunk 退出服務路徑（by chunk id）」** ✓ 按 anti-pattern guard 先補行）。`update_log.json` **N/A**（零入庫、純服務路徑改動）。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實：Supabase 16,062 零寫入／registry 256／`_meta` 2.3.0 facts 455／guidelines 158／served `PLATFORM_VERSION 3.2.2`）。Pages 已隨 `app.html` push redeploy 並 live 驗；Render deploy 1 次並 live 驗。§4a：`--check` trigger=False（381 行／6 entries）→ no-op。
- **舊記錄（S196 closeout）：**

- **Reconciled at:** 2026-07-28 (S196 closeout)
- **S196 state sections rewritten or confirmed current:** Current Baseline（prepend S196 block：Supabase **16,062 零接觸**、registry **256 不變**、v3.2.2 不變、凍結合約機械核實零接觸；A/B 兩個檢索改動 + 兩次自我推翻 + judge 發現）；Open Priorities（**整份重生**：舊 ② route 次序已證唔存在並由實測取代、舊 ⑤ baseline 查實已做，新 ② 為 judge prompt 並釘死「先修 judge 後收 bypass」次序）；`Last Session Record` 由 S195B 重寫為 S196（S195B 降級為 `Previous Session Record (S195B)`，no-loss）；`Next Session Opening Message` 重生；本段。
- **S196 lifecycle check:** 舊 Open Priorities 6 項處置 —— ①PAT→**原封不動保留**（我做唔到）；②route 次序→**證實唔存在**（`detectQueryCategory` 一直返 `safety`），已由真根因取代並修好，唔再列為未解項；③g24/sag→**不變**；④judge prompt→**升為 ②**，並由「應付裸名詞短 query」重寫為實測發現（judge 近乎恆等於否）＋新增前置依賴；⑤封面 baseline→**查實已覆蓋 S195B 新源（208 條）**，降為維護項；⑥spotlight→**不變**，維護項。**無已完成項殘留為未解 next priority 或 active risk。**
- **S196 persistence routing checked:** 是。當前狀態→handoff Current Baseline S196 block；五份 eval run + 四份 footnote probe run→`dev/source/eval_runs/`（commit，跨 session 可比）；**兩個常數嘅實測分佈→`searchChannelB.ts` code 註釋**（下一個想調呢兩個數嘅人一定睇到）；**judge 量度結果同未 ship 嘅理由→`dev/source/JUDGE_PROMPT_FINDINGS.md`**（新檔，可重用程序知識，唔止留喺 log）；**可重用嘅報告紀律→`dev/rules/communication.md` 第 3/6-10 條 + `dev/RULE_PACKS.md` 載入條件**（即係唔會淨係留喺 handoff／log）；集合對數→**寫成 `partition_gaps()` + self-test 斷言**（機器化而非靠人記得）；DOC_SYNC 新增「Synthesis 前置閘改動」row。
- **S196 stale snapshots left:** 無。**本 session 內主動更正咗自己三次**：(a) 報「7 條 negative」→ 實際 5 條（借錯 vault 用途嘅測試集）；(b) 講「S195B 數據標錯」→ 打開原文後證實 S195B 企得住（`不應超過30` 係 g07 講家課時間）；(c) 講「我冇為三條 query 做過決定」→ 實錄顯示我逐條判過且三次判錯。三項連同兩個 commit message 不準確之處，全部寫入 SESSION_LOG「紀錄更正」段。
- **S196 opening message matches current state:** 是。`Next Session Opening Message` 重生（16,062 零接觸／A+B 兩個改動／judge 發現列為最重要必讀／新增第 3 條紀律），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 **byte-for-byte mirror check PASS**（74 行）。
- **S196 sync status:** DOC_SYNC 命中 3 row（檢索 eval harness ✓ 三對 run／Channel-B SOURCE_SETS+TOPIC_KEYWORDS+QUERY_EXPANSIONS parity ✓／**Synthesis 前置閘改動 ✓ 本 session 新增嘅 row**）。`update_log.json` **N/A**（純檢索行為修復、零入庫，按 S190 定案）。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實：Supabase 16,062／registry 256／knowledge `_meta` 2.3.0 facts 455／guidelines 2.6.1 實際條目 158／served `PLATFORM_VERSION 3.2.2`）。Pages 無需 redeploy（純 backend + 治理檔）；Render 已 deploy 4 次。§4a：`--check` trigger=False（375 行／6 entries）→ no-op。
- **舊記錄（S195B closeout）：**

- **Reconciled at:** 2026-07-27 (S195 下半 closeout)
- **S195B state sections rewritten or confirmed current:** Current Baseline（prepend S195 下半 block：Supabase **16,062**、registry **256**、v3.2.2 不變、凍結合約零接觸、8 項優先事項逐項交代包括 1 項做唔到／2 項結論相反／1 項自己整錯已還原）；Open Priorities（**整份重生**：舊 8 項有 6 項完成、2 項結論改變，新列 6 項並全部標明性質同前置條件）；`Last Session Record` 由 S195 上半重寫為 S195B（上半降級為 `Previous Session Record (S195 上半)`，no-loss）；`Next Session Opening Message` 重生；本段。
- **S195B lifecycle check:** 舊 Open Priorities 8 項處置 —— ①校車五份→**完成**（已從清單移除）；②judge 門檻→**完成但結論係「唔改」**，並衍生新項「改良 judge prompt」；③g21/g22→**完成**（Issue #5 可關）；④PAT→**唯一原封不動保留**（我做唔到）；⑤CI→**完成**，衍生「baseline 要跟住更新」維護項；⑥重複登記→**完成**；⑦spotlight→**嘗試後還原**，重列為「下次要用 eval 對」維護項；⑧religious_edu_jss→**完成且唔使郁凍結 count**。**無已完成項殘留為未解 next priority。** 新增 3 項（route 次序／g24-sag 真重複／judge prompt）全部標明需要獨立證據或 PLAN。
- **S195B persistence routing checked:** 是。**可轉移教訓→`dev/PROJECT_DECISIONS.md` Insights**（三條：content-hash id 刪除陷阱／自製 probe 量度自己假設／分佈重疊嘅門檻調唔到）＋**共用經驗庫 inbox 兩份提案**（playbook commit `ee70298`，並開咗 `usage/policychecker.log.md`）—— 即係可重用嘅程序知識冇淨係留喺 handoff／log。其餘：當前狀態→handoff Current Baseline；四份 eval run + judge probe 輸出→`dev/source/eval_runs/`（commit，跨 session 可比對，唔止留喺 log）；**門檻實測→`searchChannelB.ts` code 註釋**（下一個想調呢個數嘅人一定睇到）；**spotlight 教訓→`SPOTLIGHT_SOURCE_IDS` 註釋**；每條 registry 改動理由→各條目 `notes`；監察 diff 設計 + baseline 維護紀律→`FRESHNESS_GUIDE` §0/§2；用戶面→`update_log.json` 3 條 + CHANGELOG。
- **S195B stale snapshots left:** 無。**主動更正咗自己上半場一個錯**：我曾把 `religious_edu_jss` 改名成 2024 版、status 改 verified，實情 registry 一早有 `religious_edu_jss_2024` 並已宣告 `supersedes`，我嗰個改動製造咗重複 —— 已改回 legacy 身份 + `superseded` + `superseded_by`，並在該條目 notes 寫低整件事。
- **S195B opening message matches current state:** 是。`Next Session Opening Message` 重生（16,062／256／8 項處置結果／兩條「唔好再犯」紀律），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check PASS。
- **S195B sync status:** DOC_SYNC 命中 4 row（Channel-B vault backfill ✓／檢索 eval harness 改動 ✓ eval_queries 25→30 + 4 份 run／Monitoring-CI change ✓ 新 workflow + FRESHNESS_GUIDE，**無新 secret 依賴**／guidelines.json 契約 ✓ `--write` 重生、158 不變）。`update_log.json` +3 條。凍結合約（`_meta` 2.3.0／facts 455／guidelines 158）+ `PLATFORM_VERSION` 3.2.2 零接觸（機械核實）。Pages 隨 push redeploy；Render 已 deploy 兩次（主體 + revert）。§4a：`--check` trigger=False（331 行／5 entries）→ no-op。
- **舊記錄（S195 上半 closeout）：**
- **Reconciled at:** 2026-07-27 (S195 closeout)
- **S195 state sections rewritten or confirmed current:** Current Baseline（prepend S195 block：Supabase **16,035 不變**、registry **250 不變**、v3.2.2 不變、凍結合約零接觸、2 條 404 修好 + 5 條登記整理 + 3 項新發現未修，全部 LIVE 驗）；Open Priorities（**重生**：S194 的 ②③ 已完成故移除，其餘 5 項收納入新 S195 段，新增 3 項〔g18 re-ingest／g21-g22 Issue #5／religious_edu_jss 158→159〕並重新排序；S194 原行降級標示為歷史）；`Last Session Record` 由 S194 重寫為 S195（S194 段降級保留為 `Previous Session Record (S194)`，no-loss）；`Next Session Opening Message` 重生；本段。S194 及更早 = 歷史背景不變。
- **S195 lifecycle check:** S194 的 ②（2 條真 404）③（5 條 pdf-serve-HTML）**兩項皆已完成，已從 Open Priorities 移除、唔再列為未解項**。②的結果比原描述嚴重（唔止 registry 污糟，而係 285 條 chunks + 5 個檔案副本都服務緊死連結），已在 baseline + log 寫明真相而非沿用舊描述。新增 3 項全部標明性質：①＝需 Leonard 拍板（g18 要 re-ingest，唔可照 re-point）、③＝已開 GitHub Issue #5 留底（Leonard 明確指示只記錄唔修）、⑧＝需拍板（會郁凍結 count 158→159）。**無已完成項殘留為未解 next priority 或 active risk。** Issue #4 保持開住係正確狀態（仍有 1 條真 broken URL `g18`），已在 issue 內註明範圍。
- **S195 persistence routing checked:** 是。當前狀態→handoff Current Baseline S195 block；trace + QC 證據（逐頁比對數字／285 行 blast radius／全掃 268 結果／live rank）→SESSION_LOG S195；用戶面 → CHANGELOG entry（**唔入 `update_log.json`** —— 該日誌按 S190 定案只記「新源入庫／既有源重大更新」，純連結修復屬維護、入去會製造雜訊）；未修項 → Open Priorities ①③⑧ + GitHub Issue #4／#5（跨工具留底，唔淨靠 handoff）；registry 每條改動的理由 → 寫入該條目自己的 `notes`（連 g21／g22 的 `OPEN (S195…)` 標記），令下一個 agent 淨睇 registry 都知發生過咩。
- **S195 stale snapshots left:** 無。Current Baseline 頂 S195 block = 準狀態。**主動修正咗一處既有 stale**：`religious_edu_jss` registry 標題／版本（原寫「宗教教育科（中一至中三）」+ legacy，實際上游供應的是《宗教教育課程指引（中一至中三）》**二零二四年**版，已按封面更正）。
- **S195 opening message matches current state:** 是。`Next Session Opening Message` 重生為 S195 版，`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 prompt mirror check PASS。
- **S195 sync status:** DOC_SYNC 命中 3 row —— 「guidelines.json public contract / app.html GUIDELINES_REGISTRY change」（**照 row 指示用 `build_guidelines.py --write` 重生而非手改**、`--self-test` PASS、per-topic count 158 不變 ✓）、「Doc-drift truth-pass / accuracy correction」（6 處 URL 副本＋registry 標題版本更正 ✓）、「Channel-B vault source backfill」部分適用（registry entry + url 對齊；**無** SOURCE_SETS／TOPIC_KEYWORDS 改動，故 eval before→after 對 **N/A** —— 本次零檢索邏輯改動，url 欄不參與 embedding 或排序）。`update_log.json` 判定為 N/A（理由見上）。凍結合約（`_meta` 2.3.0 / facts 455 / guidelines 158）+ `PLATFORM_VERSION` 3.2.2 = 零接觸 confirmed（sha256 + count 機械核實）。Pages redeploy：`app.html`／`guidelines.json`／`data.json`／`CHANGELOG` 有改 → 隨 push 觸發。
- **舊記錄（S194 closeout）：**
- **Reconciled at:** 2026-07-26 (S194 full closeout — Leonard「收工」)
- **S194 state sections rewritten or confirmed current:** Current Baseline（prepend S194 reconciled block：Supabase **16,035**、registry **250**、v3.2.2 不變、凍結合約零接觸、mislabel 修復 + 框架正文入庫 + 2 新工具 + display-sync 程序缺陷修復 + R5 審計，全部 LIVE 驗）；Open Priorities（頂加 S194 8 項，並明標 S193 的 ①② 已完成）；`Last Session Record` 由 S193 重寫為 S194（S193 段降級保留為 `Previous Session Record (S193)`，no-loss）；`Next Session Opening Message` 重生；本段。S193 及更早 = 歷史背景不變。
- **S194 lifecycle check:** S193 遺留 ①（入庫 IIT 框架正文）②（核 ICT guide）**兩項皆已完成，已從 Open Priorities 移除、唔再列為未解項**；②的結果比原描述嚴重（唔係 supersede 而係指錯文件），已在 baseline + log 寫明真相而非沿用舊描述。新增 8 項全部標明性質：①＝**需 Leonard 拍板的安全取捨**（judge 門檻，附 3 選項 + 已證非本次 regression）、②③＝封面掃描副產品待修、④＝只有 Leonard 做得到（PAT scope）、⑤⑥⑦＝維護提醒、⑧＝記錄更正。**無已完成項殘留為未解 next priority 或 active risk。** S186 edbcm073 monitor 仍 open（未受本 session 影響，續留 S193 區塊）。
- **S194 persistence routing checked:** 是。當前狀態→handoff Current Baseline S194 block；trace + QC 證據（hash set 比對／實測 cosine／eval 前後對照／封面掃描結果／R5 審計細節）→SESSION_LOG S194；模組事實 + 新工具描述→CODEBASE_CONTEXT Directory Map ×2 + AI log；入庫時封面核對紀律 + Method C 監察模型→`dev/source/FRESHNESS_GUIDE.md` §0 + 新 §1a（**可重用程序知識唔止留喺 handoff/log**）；eval harness 同步義務→DOC_SYNC 新 row；跨 repo durable 教訓（URL 200 ≠ 正確文件、append-only 歷史唔可做 sync 目標）→`dev/PROJECT_DECISIONS.md` Insights；用戶面→`update_log.json` 3 條 + CHANGELOG entry；可重現＝commits `3f2c9d9`/`e0e2f3b`/`76e5719`/`744af53`/本 closeout commit。
- **S194 stale snapshots left:** 無。Current Baseline 頂 S194 block = 準狀態。**主動修正咗兩處既有 stale**：(a) CHANGELOG S186 條 + CODEBASE_CONTEXT 5 條 AI log 被歷次 display-sync 盲目改寫的歷史數字（S186 條曾寫「15,656→15,901（淨+182）」算術不成立）；(b) Open Priorities ⑧ 更正 S190 NEXT ③「sibling repo 亦 public」——該 repo 已 private。
- **S194 opening message matches current state:** 是。`Next Session Opening Message` 重生為 S194 state-rich 版（HEAD/16,035/250/judge 門檻待決/8 項 NEXT），`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 **prompt mirror check PASS（byte-for-byte 相等）**。頂層 dormant root redirect prompt 不變（仍 valid，本 session 跟 S193 先例唔寫該 root）。
- **S194 sync status:** DOC_SYNC 命中 4 row —— 「Channel-B vault source backfill」（registry entry + backend SOURCE_SETS/TOPIC_KEYWORDS/QUERY_EXPANSIONS parity + display-sync ✓）、「Doc-drift truth-pass / accuracy correction」（修正被污染的歷史數字 + CODEBASE_CONTEXT AI log ✓）、「Monitoring / CI workflow change」（FRESHNESS_GUIDE §0 Method C + §1a + CODEBASE_CONTEXT Directory Map ✓）、「Option A 自動入庫管道改動」（`execute_ingest.py` DISPLAY_SYNC_TARGETS ✓）；**新增 1 row**（檢索 eval harness 改動 —— 原本無 row 覆蓋，按 anti-pattern guard 先補 row）。display-sync 7 檔（15,901→16,035）+ `update_log.json` 3 條 + CHANGELOG entry ✓。凍結合約（`_meta` 2.3.0 / facts 455 / guidelines 158）+ `PLATFORM_VERSION` 3.2.2 = 零接觸 confirmed。Pages redeploy：index.html/app.html/README/update_log 有改 → 已隨 push 觸發。§4a log maintenance：`--check` 報 **trigger=True**（420 行 > 400）→ 跑 `--apply` → 420→187 行、9→3 entries、6 條入 `dev/archive/SESSION_LOG_2026_Q2.md`（raw 保留、零刪除）→ 重跑 `--check` = trigger=False。
- **舊記錄（S193 closeout）：**
- **Reconciled at:** 2026-07-26 (S193 full closeout — Leonard「收工」)
- **S193 state sections rewritten or confirmed current:** Current Baseline（prepend S193 block：HEAD `ef426cc`、Supabase **15,901**、registry **248**、v3.2.2 不變、凍結合約零接觸、起手探針 4/4 綠、spotlight 修復 + executor 4b/可見度閘 LIVE 驗）；Open Priorities（頂加 S193 5 項：IIT 框架正文入庫 / ICT guide 核版 / spotlight 名單維護 / edbcm073 仍唔出 / eval harness 必容 tie flip）；本段。S192 及更早 = 歷史背景不變。
- **S193 lifecycle check:** S186 兩條 monitor → edbcm066 已解（移出 monitor，記錄於 S193 baseline）、edbcm073 仍 open（明確重列為 Open Priorities ④ 並寫明原因＝0.458 低於門檻，屬設計邊界非 bug）。本 session 完成項（spotlight 修復 / 4b / 可見度閘 / monitor 核實）**無殘留為未解 next priority**；新增 5 項全部標明待 Leonard 決或屬維護提醒。
- **S193 persistence routing checked:** 是。當前狀態→handoff Current Baseline；根因機制＋門檻實證→code 註解（`SPOTLIGHT_SOURCE_IDS` 段）+ SESSION_LOG S193 QC 段；模組事實→CODEBASE_CONTEXT（Directory Map ×2 + AI log）；管道改動義務→DOC_SYNC 新 row；可重現＝commits `ef426cc`+`ffd7f22`+本 closeout commit。
- **S193 stale snapshots left:** 無。Current Baseline 頂 S193 block = 準狀態；`Last Session Record` 由停留 9 個 session 嘅 S183 重寫為 S193（舊段降級保留為 `Previous Session Record (S183)`，no-loss）；S192 及更早 = 歷史背景（已明標）。
- **S193 opening message matches current state:** 是。`Next Session Opening Message` 由 generic 模板改為權威 state-rich 版（帶 HEAD `ffd7f22` / 15,901 / 248 / ff-pull 提醒 / S193 修復摘要 / ①-⑤ NEXT），`START_NEXT_SESSION_PROMPT.txt` 重生並 **prompt mirror check PASS（byte-for-byte 相等）**——修正 S192 起 handoff↔START 各寫一份嘅 drift。頂層 dormant root 嘅 redirect prompt 不變（仍 valid）。
- **S193 sync status:** DOC_SYNC 命中「Product behavior / tuning change」（handoff+log+QC ✓）+ 新增「Option A 自動入庫管道改動」row；CODEBASE_CONTEXT Directory Map ×2 + AI log ✓；**無** Supabase／registry／凍結合約／`PLATFORM_VERSION`／display-sync／前端 改動 → 無需 Pages redeploy、無需 display-sync。§4a log maintenance：`session_log_maintenance.py --check` → trigger=False（349 行 / 8 entries）→ no-op。
- **舊記錄（S192 closeout）：**
- **Reconciled at:** 2026-07-05 (S192 closeout)
- **State sections rewritten or confirmed current:** Current Baseline（prepend S192 reconciled block：read-only 分析 deliverable、HEAD `a47eedf`、起手探針 4/4 綠、Supabase 15,874 / registry 244 / v3.2.2 全部零接觸＝沿用 S191、新交付 `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`）；S191 及更早段確認為歷史背景（不變）；Open Priorities 頂加 S192 roadmap 指針行（🔜 NEXT active 優先序不變，Circular 安全審計仍 #1 = roadmap R5）；State Reconciliation Check（本段更新到 S192）。
- **Stale snapshots left:** 無。Current Baseline 頂 S192 block = 準狀態（HEAD `a47eedf`、Supabase 15,874、registry 244、v3.2.2、凍結合約 `_meta` 2.3.0/facts 455/guidelines 158 全 intact）；下面 S191 及更早為歷史背景（已明標）。
- **Lifecycle conflicts resolved:** S192 = 純 read-only 分析 + 治理持久化，無產品改動、無已完成項殘留為未解 next priority／active risk。交付物（roadmap 檔）本身唔係 next priority，而係「日後 agent 揀 next priority 嘅地圖」，已喺 Open Priorities 頂明標。R1–R8 全部標明 Leonard 決策依賴，無 lifecycle 衝突。
- **Persistence routing checked:** 是。當前狀態→handoff Current Baseline S192 block；分析內容→新 deliverable `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`（方向性文件，非 live 狀態）；session trace + QC→SESSION_LOG S192；reproducible＝git commit（新 doc + handoff/log/CODEBASE_CONTEXT directory-map 1 行）；DOC_SYNC＝新增 dev 治理/分析文件命中 directory-map 更新（CODEBASE_CONTEXT +1 行），無 backend/stack/service/secret/凍結合約改動。
- **Opening message matches current state:** 是（HANDOFF generic opening 不變；`START_NEXT_SESSION_PROMPT.txt` 重生為 S192 state-rich prompt，帶 HEAD `a47eedf` + roadmap 檔指針 + 起手探針指令）。
- **Sync Status:** S192 = 純分析 deliverable + 治理持久化 confirmed（新 `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md` + handoff/log/CODEBASE_CONTEXT directory-map 1 行 + START 重生）；Backend/Supabase/registry/凍結合約/PLATFORM_VERSION = 全零接觸 confirmed（無 code/data 改動、無 Render/Pages redeploy 需要）；頂層 dormant root = 文件層面零接觸 confirmed（redirect 仍 valid）。

`SESSION_LOG.md` carries recent evidence. do not create an archive directory by default. The next AI can continue from `AGENTS.md`, this handoff, `dev/PROJECT_INDEX.md`, and needed rule packs without searching old log history. See `dev/DOC_SYNC_REGISTRY.md`.

Lifecycle consistency rule: compare `Completed This Session`, `Validation / QC`, `Next Priorities`, `Risks / Blockers`, and `Next Session Opening Message`. A completed or verified item must not remain as an unresolved next priority, active risk, or startup instruction unless it is explicitly reclassified as monitor-only, follow-up scope, blocked, or reopened with the missing evidence or trigger condition stated.
Persistence routing rule: one-time delivery instructions, historical validation evidence, old hashes, old version facts, and incident notes must stay in trace evidence unless they still affect the next action.
Recommended next-step rule: `Next Priorities` must name the single recommended next action and a short reason before listing additional options, unless the next action is blocked or genuinely requires a user decision.

<!-- ack:section:handoff-sufficiency-check -->
## Handoff Sufficiency Check

Can the next AI continue from `AGENTS.md`, this handoff, `dev/PROJECT_INDEX.md`, and needed rule packs without searching old log history?

Answer: yes — S216 closeout 覆核。下一個 agent 淨睇本檔可以知道：**當前數字**（Supabase **17,610** / `source_registry` **281** / 平台 **v3.3.2** / 凍結合約四值 / `origin/main` `463434c` / 本地 HEAD `6cb80c6` 領先**六個** commit 未 push / 17 個治理檔未提交 / 線上部署 `4a25a15` / Kit **v0.3.66** doctor 53/53）；**點核實**（開場白的 `Post-startup first action` 四項探針，連 `git fetch` 後比對這一步都寫明，S215 正是靠它揪出四項漂移，S216 靠它揪出第五項）；**做緊乜**（`Open Priorities` 開首一句寫明單一建議動作與理由，之後 ①–⑦ 每項寫明前置條件與已被否定的舊方案）；**唔准做乜**（未得批准不得 push／commit／deploy／啟用 flag／執行 DDL／跑外部模型批次；任何 DDL 前先確認 live 函式定義）。

Reconstruction evidence: 只用本檔重建下一步 —— **父目標與消費者**見 `## Architecture Decisions (Locked)` 與 `## Open Priorities` 開首（父：EDB K1 知識平台的檢索準確度；消費者：Leonard 與平台用戶）；**本步與父目標的關係**見 `## Open Priorities` ①（S216 是治理升級節，不推進檢索準確度，只解除 S213 記錄的 `doctor failed` 阻塞並令交接檔機械可讀）；**確切續接點**見 `## Last Session Record` 第 4 項與 `## Risks / Blockers` 第 1、3 項（六個 commit ＋ 17 個治理檔待決定去向）；**餘下驗收**見 `## Validation / QC`（S215 產品側數值仍綁定未變的 commit，185 題 live 套件仍未跑）；**必讀來源與新鮮度**見 `## Mandatory Start Checklist` 與 `## Next Task Required Reading`，另 `## Risks / Blockers` 第 2 項寫明 `match_wiki_chunks_routed` 的 live 定義**每次 DDL 前都要重新確認**，不可沿用本檔記載。**未讀缺口**：185 題 live 套件、`INIT.md` 全文（OP ⑦ blocked 的判斷前提）。


**⚠️ S215 新增治理缺口（未修）**：`backend/README.md` 5 行 flag 說明永久遺失，無備份、沒有杜撰補回；補寫時須在 commit message 明寫是重寫非還原。

**⚠️ 已知治理缺口（S205 發現，S206、S207 沿用同一判斷）**：S204 closeout 冇寫 `State Reconciliation Check` 條目（本節由 S205 起補回並持續）。屬歷史記錄缺口，唔影響當前狀態可信度。

If no, update this handoff before closeout.

Continuity rule: this file carries current state and next action. `dev/SESSION_LOG.md` carries recent evidence only. Archive old detail only when needed; do not create an archive directory by default.

<!-- ack:section:next-session-opening-message -->
## Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft. Read AGENTS.md, then dev/SESSION_HANDOFF.md. Trust the handoff over this generated mirror.

If the root does not match the handoff, stop and ask for confirmation. Do not read dev/SESSION_LOG.md during ordinary startup. Read dev/PROJECT_INDEX.md, dev/RULE_PACKS.md, dev/DOC_SYNC_REGISTRY.md, and task packs only when the current task requires them.

Resume the current objective. A plain `Start Agent Handoff` / `開工` with no same-message task or explicit long-run instruction only authorizes minimum state recovery, one optional display-only current-thread title update when safely supported, the startup card, the current objective/risk/recommended next action, and then the end of the turn. It does not authorize task-specific reads, research, plans, protocols, preflight, file searches, sub-agents, QA, packaging, project-file writes, network access, other external actions, or opt-out execution wording. First-use exception: when this handoff says `First-use guidance state: eligible`, the current objective is empty / `TBD`, and there is no same-message concrete task, load onboarding and include a short first-use welcome plus the most relevant guided choices in the same response instead of ending status-only. A concrete objective found only in this handoff is not authority to complete the objective. A same-message task may begin normally; an explicit instruction such as `開工，繼續做到下一個 blocker` or `開工，繼續完成目前目標` may continue under the normal task and safety rules. Upgrade never resets consumed / not_applicable first-use state back to eligible.

--- 專案狀態（S218, 2026-09-08）---

Current state：平台 v3.3.2；Supabase 17,610；source_registry 281；guidelines.json _meta 2.6.1；
knowledge.json 2.3.0 · facts 455；凍結合約零接觸。Agent Handoff Kit v0.3.66。
HEAD == origin/main == f3ca973（S218 收工 commit，已 push），分歧 0/0，工作區乾淨。
線上部署：Render /health 報 commit 612e13e、cache_a warm 455（started_at 2026-09-08T06:58:08Z）。

⚠️ 先讀這段，否則會把正常狀態誤判為漂移：
   /health 報的 612e13e 比 HEAD 舊，這是【正常】，不是未部署。
   612e13e 之後的 commit 全部是純治理／持久化（S217 的 72b5adb、0f8a7c9，S218 的 f3ca973），
   實測 git diff --name-only 612e13e..HEAD -- backend app.html = 0 個檔，
   即生產跑的執行碼與 612e13e 那次部署完全相同。
   【判斷準則看 diff，不要比 hash】——每次收工都會多一個治理 commit，HEAD 必然前進，
   單看 hash 不同會誤判成「未部署」。
   RENDER_GIT_COMMIT 不隨新 commit 更新的成因【仍未查證】——不要當已解，也不要當故障。

🔴 最高優先（未變）：S214 候選已在生產環境，但三個 flag 仍全部 off
   （FEATURE_EXACT_WINDOW_NARROW／FEATURE_GROUNDED_SYNTHESIS／FEATURE_ROUTE_FIRST_SEARCH，
   Render 未設環境變數）。產品 verdict 仍為 FAIL，185 題 live before／after 仍未跑。
   **已部署 ≠ 已啟用。啟用任何 flag 之前必須先跑 185 題，且需 Leonard 另行批准外部模型批次。**

🔴🔴 S217 查出的陷阱（下一個 agent 一定要知）：「三個 flag 全 off」≠「零行為改動」。
   S214 的 establishment 路徑改動 **沒有任何 flag 保護**，已在生產生效。
   觸發條件窄：detectedCategory === "staffing" 且 query 含「N 班」（1–2 位數），
   ESTABLISHMENT_SOURCE_IDS 現時只有 staff_est_pri。三處差異：
     (a) estLead 移除了 !seenIds.has(r.id) 過濾 —— ANN 已撈到同一 chunk 時精確列仍會置頂；
     (b) 插入方式改為置頂並濾走【整個】establishment 來源的其他列，同表其他班數不再並存；
     (c) trustedVaultLead 的判斷來源由 results[forcedLeads]（overlay 後）
         改為 mainSearchLead（overlay 前）—— 技術上覆蓋所有合成呼叫。
   其餘執行碼已逐個 hunk 核實零行為改動。
   **通則：不要憑「flag 全 0」推斷零行為改動 —— 要 git diff 逐個 hunk 找無 flag 保護的路徑。**

⚠️ 開工探針紀律（S217 教訓，S218 仍適用）：
   Option A watcher bot 會自行推 commit 到 origin/main（只碰 discovery_seen.json、
   registry_drift.md、qc_report.json 三個資料檔）。S217 開工時它推前了兩個，
   令本地變成真分歧、push 被拒；S218 開工實測它本輪【未推】，不必 rebase。
   通則不變：一定要 git fetch 後比對，不能讀交接記載的 hash 當現況。

✅ 已確立的事實（不必再查）：
   1. regression:grounded 有一條斷言 both synthesis flags off preserve the legacy synthesis
      prompt exactly —— 該句只覆蓋合成 prompt，不覆蓋整個系統（見上面 🔴🔴）。
   2. 生產側三個端點實測正常（S217）：channel-a 50 條／channel-b 8 條／combined 58 條＋synthesis。
   3. S217 曾見部署後首個請求回 0 條、隨後 5/5 正常，屬 S118 probes=8 冷啟動／間歇族，
      不是部署引入的新問題；但 response body 未保存，成因未能確證。
   4. establishment 路徑觸發範圍已生產實測為窄（S217 三個 case）。
      但那是事後觀察，不是 before／after 對照 —— 舊碼已不在生產，無法跑對照組。
   5. Playbook pointer 為 v3（最新），S218 已自我檢查，無須重裝。

⚠️ 未解決（不要當已解決）：
   · 185 題 live 套件未跑 —— 這是啟用 flag 的唯一閘（OP ①）。
   · backend/README.md 5 行仍未補（OP ②，S215 遺失，無備份，不得杜撰）。
   · 三題 chunk recall（OP ③）、4 條 fidelity 不一致＋合成窗佔用率（OP ④）、
     S212／S213 全部遺留（OP ⑤）—— 一項未動。
   · 治理側兩項已由 Open Priorities 移入 Backlog「治理側」段（原文一字未刪）：
     交接檔 8 個 ack marker 未有專屬章節、dev/DOC_SYNC_CHECKLIST.md 的 INIT.md 鏡像規則已失效。
   · qc_report.json overall ERROR 未處理。
   · agent-handoff-kit doctor 連續兩節（S217、S218）跑不到 —— CLI 不在 PATH、
     全局與本地 node_modules 皆無、npm 上該名字 404。治理健康度【列為未驗證，不當通過】。
   · AGENTS.md／CLAUDE.md／GEMINI.md 三檔 gitignored 且從未 tracked，S216 升級改動不在版本控制內，
     唯一還原點是 dev/governance_migrations/2026-09-07T18-23-33-046Z-*/backup/，該目錄內的
     AGENTS.md 連同樣被 .gitignore 命中，刪了無得還原。

QC status：S218 零程式碼改動、零 QC 重跑。S217 推之前實測的數值仍有效（綁定 commit 與檔案未變）：
   npm check 0 · npm build 0 · regression:grounded 48/48 · route_regression 46/46 · active gold 185。
   未跑：185 題 live 套件。未驗證：agent-handoff-kit doctor。qc_report.json overall ERROR 未處理。

Post-startup first action: 先做起手探針（served app.html PLATFORM_VERSION + Render /health
+ git fetch 後比對 HEAD／origin/main + Supabase live count + source_registry）。
若落後於 origin/main，先實測零衝突再 rebase。之後如無新指示，行離線工作：
補 backend/README.md 5 行（OP ②），或追三題 chunk recall 的 query expansion 與目標片段位置（OP ③）。
未得明確批准，不得啟用任何 flag、不得執行 DDL、不得作任何外部模型批次、不得 git push。
```

## Session Close Checklist (每次 session 結束必須執行)
```bash
# 1. 更新 SESSION_LOG.md + SESSION_HANDOFF.md（Claude 負責）
# 2. Git commit + push（Leonard S115 授權「push 係你做」— Claude 執行；加指定檔，勿 -A）
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
git add <指定治理/文檔檔> && git commit -m "session close: <描述>" && git push origin main
# （MemPalace sync 已於 S115 移除 — 本專案不再使用 MemPalace）
```

## Supabase Technical Notes (Channel B)
- Project: `edb-knowledge` at `https://youkcekbrbywuqjxgibe.supabase.co`
- Table: `public.wiki_chunks` — vector(1536), IVFFlat index **lists=60** (per `backend/supabase/schema.sql`, the authoritative DDL — S115 §0b corrected: prior "lists=50" + "2,822 rows" were drift; local wiki_index build artifact = 12,906 chunks / 120 src; live Supabase row-count + index not introspected this session)
- Function: `match_wiki_chunks(query_embedding text, match_threshold double precision DEFAULT 0.1, match_count integer DEFAULT NULL)` — **this (text) is the LIVE signature the backend uses (sends embedding as string); schema.sql had drifted to `vector(1536)` and applying it created a 2nd overload → PGRST203 → Channel B 0 (S116 live incident). Always INSPECT live `pg_get_functiondef` before any RPC DDL — see PROJECT_MASTER_SPEC §E.13.**
  - Uses `query_embedding::vector` cast internally; ordered by cosine DESC; null match_count = return all above threshold
  - **S116: now `language plpgsql VOLATILE` with body `set local ivfflat.probes = 8`** (was `language sql stable`, probes=1 default). Mechanism constraints (all empirically hit): function-level `SET ivfflat.probes` clause → 42501 (Supabase blocks ext-GUC clause); `SET`/`SET LOCAL` in STABLE/IMMUTABLE or `language sql` → 0A000 (must be VOLATILE plpgsql). probes=8≈sqrt(lists=60). Production Channel B currently runs probes=8 (Stage-1 FULL PASS, S116). Reference: auto-memory reference_supabase_pgvector_probes.
  - DDL needs Supabase Dashboard SQL Editor (Leonard's auth); no CLI/psql/DB-url/service-via-PostgREST path. Claude prepares exact APPLY+ROLLBACK+read-only INSPECT; Leonard applies.
  - ✅ **S117 FIXED** (was S116 promote-blocker): `searchCombined.ts` `.catch` now returns `failedChannelBResponse` → combined surfaces `channel_b_status:"error"` + `CHANNEL_B_ERROR_REASON`, distinct from genuine unconfigured (`channel_b_status:"unconfigured"` + 未配置). Real Channel B failures now visible to monitoring/eval via the `channel_b_status` discriminator (no more fake "未配置" masking). Genuine-unconfigured path (`searchChannelB.ts` `isSupabaseConfigured()` guard) unchanged. Dedicated `/api/search/channel-b` still recommended for live-grade (no route-level catch — methodology unchanged). Deploy: Render auto-deploys on push to main.
  - 🔴 **S118: free-tier probes=8 intermittent statement-timeout** — live-verify saw 2/5 RPC calls return HTTP 400 / Supabase `57014` "canceling statement due to statement timeout" at probes=8 (succeeded on retry; one was cold-start, one intermittent ~60s after a healthy call). Production-availability risk independent of retrieval correctness; post-S117 it correctly surfaces as `channel_b_status:"error"` (not fake "未配置"). Open Priority — options: lower probes / app-level retry / paid tier. probes=8-live itself still NOT independently introspected (audit-flagged; read-only `pg_get_functiondef`/`proconfig` SQL prepared, not yet run).
  - **S118: Channel B routing +4 dedicated selective routes** (`searchChannelB.ts` `TOPIC_KEYWORDS`/`SOURCE_SETS`/`QUERY_EXPANSIONS`, first-match before `finance`): cpd, kg_admission, conduct, steam (PLAN-1b promote; fixed cutoff unchanged; SAG in cpd/conduct bounded by per-source quota cap=3 → §E.3-safe). Stage-2 adaptive combo abandoned (non-viable; do not revive).
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
