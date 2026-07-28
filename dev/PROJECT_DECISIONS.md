# Project Decisions — EDB K1 知識平台

> Long-term architecture choices, multi-option trade-offs, and cross-session evolution.
> Created S145 (§4 trigger c: Q4 Phase 2 completion).

---

## Architecture Choices

### ADR-001 — Channel B Downstream Integration Model (Q4 Phase 2)
- **Date**: 2026-06-05 (S144 model decision; S145 build + verified live)
- **Status**: IMPLEMENTED + LIVE
- **Context**: Channel A (`knowledge.json` @455 facts, frozen Q4 Phase 1) previously fed Circular System. Q4 Phase 2 = transition downstream to Channel B (Supabase `wiki_chunks` 10,594 chunks, pgvector).
- **Options considered**:
  - A: Export full snapshot (batch file) → ❌ conflicts with near-real-time freshness goal
  - B: Pure query-time API (downstream calls K1 `/api/search/channel-b` per query) → ⚠️ binds downstream to onrender free-tier (cold-start ~30s, 10 req/min/IP, no SLA)
  - **C (chosen): Incremental sync / manifest-diff delta feed** → downstream maintains its own vector index, polls K1 manifest for id-set delta, queries locally. Avoids both snapshot staleness and free-tier dependency.
- **Decision driver**: Downstream Circular System profile confirmed S145 = GitHub Actions ephemeral cron 3×/day + file-based numpy (NOT persistent service / NOT pgvector). Incremental sync avoids re-embedding 10K chunks per cron run; ETag/304 + delta minimises bandwidth.
- **Implementation**: `backend/src/api/channelBSync.ts` — `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`; X-Sync-Key gated; anon-REST; NO CORS; own 60/min + daily chunk budget. Contract = `dev/CHANNEL_B_SYNC_SPEC.md` v0.5.
- **Evidence chain**: S144 model selection (3 options, downstream profile gathering) → S145 downstream reply (embedding path-1 confirmed, 3 reverse-questions answered) → 5-lens adversarial review (40 agents, 4 real fixes) → live smoke PASS (anon reads `embedding` 1536-vec, all 13 fields present). Spec v0.3→v0.5.
- **Uncertainty / watch**: manifest O(N) full-table scan shares free-tier DB budget with live search (§8 spec); cache singleflight + TTL mitigates; monitor for 57014 degradation. Daily budget is soft (in-memory, resets on restart). anon key reading `embedding` column confirmed live (was load-bearing assumption until S145 smoke).
- **Rollback**: `git revert` channelBSync.ts + 2 route lines in server.ts; remove `CHANNEL_B_SYNC_KEY` Render env → endpoint returns 503. Supabase/Channel A/pipeline untouched.

---

# Project Decisions Log

這個檔保存項目的長期演進、決策、架構取捨與學習觀察 narrative。屬 warm 資料層 —— AI 開工**不需要讀**本檔。

🔹 短期 single-task project：本檔保持近空，你不需要 maintain
🔹 長期持續演進項目：AI 會在收工時先做維護觸發檢查；命中觸發或到定期兜底時才完整整理。當你問「我們之前為何這樣做」時，AI 會在這裡找答案

不需要你手動寫 —— AI 在收工時自動 update；重大決策可在發生時即時記錄，不必等到最後才回想。

Research-derived decisions use this compact evidence-chain format inside the relevant section, without creating a new section:

```text
- YYYY-MM-DD [research-derived] Decision summary. Evidence chain: Source=source:<id>; Summary=<source finding>; Inference=<reasoning>; Decision impact=<what changed>; Uncertainty=<limits or none>.
```

The `source:<id>` token must also appear in `dev/PROJECT_INDEX.md` under `Fact Base` or `External Sources`, so later sessions can trace the decision back to its source map.

This file does not store raw build / upload / QC evidence, current next actions, one-time task results, or reusable operating procedures. Keep those in `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, or the relevant rule pack / registered reference.

---

## Evolution Timeline

### S143 (2026-06-05) — Q4 Phase 1: Channel A Frozen
- `knowledge.json` stopped at @455 facts; schema unchanged; downstream zero-impact.
- Guidelines.json NOT frozen; continues live @152 v2.5.0.
- All Channel A endpoints remain (dormant); reversible via git revert docs.

### S145 (2026-06-05) — Q4 Phase 2 K1-side Complete
- Channel B sync endpoints built, adversarially reviewed, deployed, live smoke passed.
- Downstream (Circular System) to build its own consumer from spec v0.5 + sync key.
- Channel A remains frozen; Channel B search remains live; no data mutations.

---

## Decisions Archive

(empty)

## Insights & Learnings

### S195 (2026-07-27) — 三條可轉移教訓：內容雜湊 id 的刪除陷阱、可達性 probe 的自欺、以及一個「唔可以靠調參解決」的安全門檻

- **背景：** 兩輪 session。上半清三條死連結（Leonard「跟你建議」），下半清埋餘下 8 項優先事項（Leonard「全做」）。Supabase 16,035 → 16,062，registry 250 → 256，凍結合約全程零接觸。

- **教訓 1 — chunk id 係內容雜湊時，「刪舊版」唔可以照 `source_id` 刪。**
  - 兩次遇到（`g18` 校車指引改版、`g21`/`g22` 重抽）。chunk id = `vault_<source_id>_<text_hash>`，所以**兩個版本之間文字冇變的段落，id 完全相同**。`g18` 舊 9 條入面有 **3 條**同新版 id 重疊；照 `source_id` 一次過刪就會連現行有效內容一齊刪走，**而且刪完之後總數睇落仲會「啱數」**（因為新版已 upsert 入去），完全唔會爆。
  - **決策：** 刪除集一律 = **舊 id 減新 id**，並且要**排除唔屬 vault 的 content_type**（`g21`/`g22` 各有一條人手寫的 `footnote_curated`，照 source_id 刪就會毀掉人手內容）。兩條刪除腳本都把刪除集**寫死入檔**而唔係執行時重算，免得日後 vault 檔一改就漂。
  - **可轉移原則：** 凡係 content-addressed 的 store（id 由內容決定），「更新一份文件」唔係一個 delete-then-insert 的原子操作，而係一個**集合運算**。用 id 前綴或外鍵去刪，等於假設 id 同文件係一對多的乾淨關係 —— 內容雜湊剛好打破呢個假設。呢類錯誤靜默、事後數字仲對得上。

- **教訓 2 — 用自己揀的 phrasing 去測「搵唔搵得到」，量度緊的係 phrasing，唔係檢索。**
  - 想剪 spotlight overlay（S193 為「新入源被全庫 ANN 擠走」而建）。我寫咗個可達性 probe：對每個源用代表性 query 打全庫 ANN（top-40、min_score 0.22），睇佢入唔入到候選池。6 個源有 4 個 **rank 0**，睇落好明確 —— 於是剪走。
  - **before→after eval 即刻打面**：`ai_intro`／`net_scholar`／`pay_adjust` 三條由 PASS 變 FAIL，失去的**正正就係被剪那三個源**。
  - **根因：** 我用的係自己揀來描述該文件的 phrasing（「人工智能初探 學與教」），而真正重要的係用戶打的**裸名詞**（「人工智能初探」）；加上生產路徑會先做 query expansion 再 embed，所以我個 probe 睇到的候選池**根本唔係生產那個池**。probe 對自己友善，因為 probe 係我寫的。
  - **決策：** 任何 spotlight／SOURCE_SETS／route 次序改動，**一律以 eval before→after 對為準**，唔接受可達性 probe 作證據。教訓寫入 `SPOTLIGHT_SOURCE_IDS` 註釋（改嗰個人一定睇到），失敗那份 run 保留入 `dev/source/eval_runs/` 做證據。
  - **可轉移原則：** 自製的驗證器同被驗證的系統共享你嘅假設 —— 尤其當輸入（query）由你揀。要證明「用戶搵到」，就要用**用戶的輸入分佈**，唔係你嘅。S194 個監察漏咗自己要捉的案，係同一個 class 的錯：**你只係測到自己嘅假設**。

- **教訓 3 — 有些安全門檻唔係「調得啱唔啱」，而係「調唔調得到」。**
  - S183 把 anti-confab judge 的 `vault_extract` bypass 定喺 cosine 0.70。此後入庫的源喺自己主題上只得 0.62–0.63，被拒答，睇落就係門檻定得太高。
  - 冇直接調，先起 `dev/source/judge_probe.py` 量 24 條：6 條完全離題、**14 條「貌似學校事務但答案根本唔喺庫」**（呢類先係會誘發砌數的，S177 砌出「IMC 60%」就係呢類）、4 條正面對照。
  - **結果：敵意類最高 0.632、真命中最低 0.624 —— 兩個分佈重疊。** 降到 0.60 會放行「教師每年可以請幾多日大假」(0.617)、「學校可唔可以借錢俾教職員」(0.615)、「校服供應商招標要幾多間報價」(0.614)：全部語域啱、個數字唔存在。
  - **決策：保留 0.70**，並把實測數字寫入 `searchChannelB.ts` 註釋（唔止留喺 log）。要提升 recall 只剩改 judge prompt 一條路（選項 c），而 `judge_probe.py` 本身就係現成的驗收工具：目標 = 4 條 control 答到、20 條敵意仍拒答。
  - **可轉移原則：** 當一個訊號的「真陽性」同「危險假陽性」分佈重疊，**冇任何門檻數值可以同時滿足兩邊**；再調只係喺兩種錯之間換位。呢個時候應該去**換訊號或換判斷器**，唔係繼續調參。而且要證明呢一點，敵意樣本必須包含「同語域但無答案」那類 —— 只用完全離題的樣本（本次最高只有 0.418）會得出「門檻可以大幅降低」的錯誤結論。

- **同場加映 — 監察要 alert on diff，唔係 alert on count。** 封面核對（S194 建）今次接入 CI 時發現：全掃 flag 18 條而**全部良性**，用 severity 做 gate 會每次跑出 11 個假警報，正正係 S191 花力氣收走的 email 噪音。改為同一份**人手覆核過的 baseline**（`title_baseline.json`）比對，只有「新出現的 flag／覆蓋率跌 ≥0.15／fetch 失敗」先開 Issue；接受一個 flag 的方式就係更新 baseline。實測：加咗 6 個新源、改咗 3 個標題之後 rescan **0 alert**。

### S194 (2026-07-26) — 兩條可轉移教訓：「200 ≠ 正確文件」＋「append-only 歷史唔可以做 sync 目標」

- **背景：** Leonard 叫我核一份 technology-edu 頁面上未入庫的 PDF 是否 `ict_sss_2021` 的新版（原以為係 supersede 小事）。核出的係：該 registry entry 標題寫《資訊及通訊科技（中四至中六）2021》，`url_primary` 卻指向 `CS_CAG_S4-6_Chi_2021.pdf` —— **`CS` 被讀成 Computer Science，實為 Citizenship and Social development**。81 個《公民與社會發展科課程及評估指引》的 chunks 長期掛住 ICT 標題供用戶檢索（生產實測：搜「公民與社會發展科」，top-1 結果標題係「資訊及通訊科技」），而真正的 ICT 2021 指引從未入庫。

- **教訓 1 — HTTP 200 唔係「文件正確」的證據，兩個既有監察都結構上盲。**
  - `check_freshness.py` 問的是「上游 bytes 有無變」，`check_served_urls.py` 問的是「用戶點落去的連結通唔通」。兩者對呢個 entry **年年都綠**：URL 一直活、一直穩定、一直 200 —— 只不過係另一份文件。**冇一個監察問「呢份係唔係你以為的文件」。**
  - **決策：** (a) 入庫紀律 —— 登記或改指任何來源前，必讀 PDF **封面**並對照 registry 標題；檔名縮寫唔算證據（`FRESHNESS_GUIDE.md` §1a）。(b) 建第 5 監察 Method C `check_source_titles.py` 做安全網（確定性 CJK bigram 比對**主題核心**：剝走學段／年份／樣板，因為「中四至中六」「二零二一年」「課程及評估指引」全庫共用，留住的正正係分辨主題的部分）。**唔用 embedding** —— 兩份 EDB 課程指引語域幾乎相同，cosine 會糊化正正需要的分辨力，字元 bigram 反而字面、免費、可重跑。
  - **首跑結果（192 個 PDF 源）：冇第二個指錯文件**；17 條 flagged 全部良性。即係呢個 bug 係孤例，但孤例造成的用戶可見錯配足以構成常設檢查。
  - **自身教訓（值得記）：** 監察 v1 **會 miss 佢自己要捉的案** —— `best_coverage` 取所有標題變體的最大值，而 `title_short`「ICT課程指引2021」去噪後只剩「ICT2021」，個「2021」撞正公社科封面的「由2021/22 學年」→ 假高分 0.500 判 ok。**新監察必須用「已知真陽性」做回歸測試，否則你只係測到自己嘅假設。** 修法後校準由 0.468/0.298（margin 0.017）改善到 **1.000/0.000**。

- **教訓 2 — append-only 歷史檔永遠唔可以做 number-sync 的目標。**
  - display-sync（chunk 總數鏡像）原本用全檔字串取代，目標包含 `CHANGELOG.md` 同 `dev/CODEBASE_CONTEXT.md`。結果**每次入庫都靜默改寫過往條目**：到 S194 發現 S186 的 changelog 條目寫成「15,656 → 15,901（淨 +182）」—— 算術上不可能；另有 5 條 AI 維護日誌記載了發生在該 session **之後**的總數。污染早於 S194，累積多個 session 無人察覺（因為冇人會 diff 舊條目）。
  - **決策：** 兩檔由 `execute_ingest.py` `DISPLAY_SYNC_TARGETS` **移除**。入庫應該向歷史檔**追加一條新條目**（本來就係佢哋的用途），而唔係重述當前狀態。加入該 list 的檔案必須只承載當前值；若同時承載歷史，就唔屬於該 list。
  - **可轉移原則：** 自動化「同步一個數字到 N 個地方」時，先問每個目標係**當前狀態鏡像**定係**歷史紀錄**。前者可以盲改，後者盲改就係篡改。呢個 class 的 bug 完全靜默 —— 唔會爆、唔會 fail CI、只會令你日後信錯自己嘅記錄。

- **同場加映（R5 審計順帶）：** handoff 寫住 sibling repo `EDB-AI-Circular-System`「亦 public、待審」，實際已轉 private 並另開 public 成品 repo `edb-circular-site`。**治理文件對外部世界的斷言同樣會 drift**，read-only 核實成本極低（一個 `gh repo list`），值得每次審計先做。

### S183 (2026-06-25) — 2 governance rules ship：Supersede ranking penalty 0.05 + Judge bypass extension to vault_extract
- **背景：** S183 ingest VE_CF 2026 主框架 93 chunks + EDBC 3/2026 + EDBCM 221/2025 智啟學教（淨 +108 chunks → 15,644）。Post-deploy Leonard mobile screenshot 反饋 + short-query verification 揭發 2 個 governance-class issue 需要 long-term rule，而非 one-off patch。

- **Rule 1 — Supersede ranking penalty 0.05（Leonard 提出）：**
  - **問題：** Retain-but-rank-down 策略下，舊版（如 values_edu_framework_2021_trial cos=0.794）cosine 自然分高過新版（VE_CF_2026 cos=0.753 差 0.041），令 user 查「價值觀教育」短 query 仍 surface 舊版主導 top-5。
  - **決策：** Backend `searchChannelB.ts` +`SUPERSEDED_IDS` Set + `SUPERSEDE_PENALTY=0.05` const + `applySupersedePenalty()` helper；apply 兩次（main results post-mapping + footnote overlay pre-lead-detection、re-sort 後）；對全 channel（vault_extract + footnote_curated + role_facts）統一 apply。
  - **Penalty 值選擇：** 0.05 empirically — 足夠 swap rank（2021 0.794 → 0.744 < 2026 0.753），但保留 retrieve 命中（學校過渡期仍可能引用舊版）。Below penalty 仍 surface 即係新版 cosine 低過 0.041 + 舊版差太大、retrieve 自然偏好舊版相關度（acceptable）。
  - **SSOT 雙處：** registry `superseded_by` field（authoritative）+ backend `SUPERSEDED_IDS` Set（runtime cache）。Future ingest 新 superseding 版時必同步雙處（同 SOURCE_SETS pattern 一致：每次 manually sync）。
  - **未來擴展點：** 如有更多 superseded sources 累積、可考慮：(a)load registry at startup 自動 build set；(b)`superseded_by_chain` 多層；(c)graduated penalty (例如 2021→0.05、2018→0.08)。當前 KISS 一刀切 0.05 sufficient。
  - **Verified：** 3/3 短 query「價值觀教育」「首要價值觀」「12 首要價值觀」VE_CF 2026 rank 0/1/2、2021 試行版 demoted rank-3+。

- **Rule 2 — Judge bypass extension to vault_extract @ score≥0.70（解 anti-confab over-decline）：**
  - **問題：** S177 anti-confab judge（synthesizeAnswer 之前 binary relevance gate）對 vault_extract chunks 過保守 — 即使 rank-0 score 0.75+（empirically direct topical match）仍 over-decline「未能找到」。Leonard mobile screenshot 報告：「智啟學教是什麼」EDBCM 221 rank-0 0.750 + 「價值觀教育」VE_CF 2021 rank-0 0.794 全 over-declined。
  - **既有 fix（S178）：** footnote_curated lead score ≥ FOOTNOTE_LEAD_SCORE (0.45) bypass judge（hand-curated verbatim-verified direct answer by construction）。但 vault_extract 唔屬於該 class。
  - **決策（S183 擴展）：** +`VAULT_LEAD_SCORE = 0.70` 同 footnote-lead pattern：vault_extract lead score ≥ 0.70 bypass judge。Below 0.70 仍經 judge full protection。
  - **Threshold 0.70 選擇：** S177 凍結教席→IMC-60% confab class 嘅 cosine 喺 **0.55-0.65** range（topically-near-but-wrong）；≥0.70 empirically direct topical match（vault chunks at this cosine reliably answer the query）。0.70 是 confab 同 direct-match 分界 empirical line。
  - **Behavior：** Confab protection retained for marginal cosine 0.50-0.65 case；high-cosine direct match no longer false-decline。3/3 Leonard user query post-fix ANSWER + grounded synthesis。
  - **未來監察：** Monitor false-positive synthesis (vault-lead bypass 但實際 confab 漏網) — 如出現可微調 threshold up 至 0.75。

- **配套 procedural learnings：**
  - **Pre-ingest grep discipline：** S183 漏 catch prior `edbc003_2026` 因為齋 grep brand variant「VE_CF / 價值觀 / value_education」而 prior registry title 短「教育局通告第3/2026號」未含 keyword。Future ingest 之前 grep registry 必同時用 (URL filename pattern + 中文 title keyword + brand variants)。
  - **Short-query verification mandatory：** Per memory `feedback_short_query_first`、real user type 2-4 token query；S183 7+ token long-sentence smoke test 7/8 PASS 但短 query 仍 fail（routing OK 但 judge 過保守）。Post-deploy QC 必驗 2-4 token 短 query。
  - **Pages transient outage remediation：** Pages build/report OK + deploy step fail 4s = GitHub Pages 短暫 outage；standard remediation = empty commit retrigger 即修；workflow status 用 public REST API `https://api.github.com/repos/<owner>/<repo>/actions/runs` 查（公開 repo no auth needed）；gh CLI v2.95.0 已裝、`gh auth login` 後可 read private workflow annotations。
  - **Commits 鏈：** `bc26d41`→`edebbbd`→`40923d5`→`a718a83`→`1359916`→`71f1c80`→`4ddffb6` 全 push origin/main、Render 4 round redeploy + Pages #398 success。

### S176 (2026-06-22) — Agent Handoff Kit v0.3.29 升級：雙治理層共存決策
- **背景**：本專案原用自寫治理（`AGENTS.md` `<INSTRUCTIONS>` §0–§14：PLAN→READ→CHANGE→QC→PERSIST、3-section closeout、`### Next Session Handoff Prompt (Verbatim)` 機制），已運行 175 sessions。S176 升級 Agent Handoff Kit v0.1.7→v0.3.29。
- **決策**：**兩套治理層共存、不取代**。AHK managed-core 追加喺 `<INSTRUCTIONS>` 之後（managed-core BEGIN/END 包圍）；原 §0–§14 全保留。理由：(1) 自寫治理含產品專屬鐵律（凍結合約、display-sync 8 點、Supabase INSPECT 授權、node-fetch pin）AHK 無法涵蓋；(2) AHK 提供 doctor 可驗結構 + rule packs + 機器標記（`ack:`）跨工具續傳。兩者互補。
- **衝突解法（已採用）**：closeout 機制兩者並行——本專案 3-section 輸出（含 `### Next Session Handoff Prompt (Verbatim)` 寫入 SESSION_LOG）+ AHK `START_NEXT_SESSION_PROMPT.txt`（由 handoff `Next Session Opening Message` 區塊重生）。S176 entry 同時保留兩種 startup 區塊。
- **git 追蹤更正（S176 closeout 發現）**：`dev/SESSION_HANDOFF.md`／`SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore`，但**實際已 git-tracked**（早於 ignore 規則就 commit；`.gitignore` 唔會 untrack 已追蹤檔）。故 S173–S175 每次收工都照常 commit 三者。升級 commit `788538e` 當時誤判為「不入 git」而漏 commit handoff/log 改動 → S176 收工 commit 補回。stale `.gitignore` 規則屬低優先 cleanup（移除該行 or `git rm --cached`，需 Leonard 定）。
- **衝突原則**：AHK core §5「兩 pack 衝突取較安全、較可驗路徑並記錄」。未來如兩層指令矛盾，取較安全可驗者，收工記錄。
- **可驗收據**：`npx @adamchanadam/agent-handoff-kit@latest doctor --root .` → `status: passed`（48 項）。升級備份＋migration report 在 `dev/governance_migrations/20260622T141715Z/`。
- **教訓**：升級遇 2 衝突檔（SESSION_HANDOFF/LOG 因舊自寫格式缺 `ack:` 標記）係**預期**、非錯誤——installer 故意唔覆寫，留 AI 非破壞性補標記（section markers 要放對語義區段，唔可以淨係 cluster 喺檔頭，否則 doctor semantic-placement check 唔過）。
