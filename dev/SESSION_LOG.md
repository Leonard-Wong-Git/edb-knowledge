# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->
Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

Entries are kept, summarized, or archived — not current state. Do not remove validation evidence. Use latest opening message from most recent entry.

<!-- ack:section:session-log-entry-template -->
## Entry Template

- **ID:**
- **Summary:**
- **Changed:**
- **Done:**
- **QC:**
- **Evidence disposition:** <one-time only / kept as recent trace evidence / absorbed into handoff / indexed in PROJECT_INDEX / promoted to PROJECT_DECISIONS / promoted to rule pack>
- **Sync:**
- **Pending:**
- **Risks:**
- **Log maintenance:**

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first, then follow its §1 startup sequence:
Read in order: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
dev/DOC_SYNC_REGISTRY.md
```

---

<!-- ack:log-entry:start -->

## 2026-08-02 Session 203 — ⑩ 文件 drift 清 + ② judge V4 量度（未 ship）+ ⑧ g24/sag 偵查（出 PLAN）

- **ID:** Claude_20260802_S203
- **Summary:** 起手探針 4/4 綠（Supabase `count=exact` 實核 16,062）。Leonard 揀「1+2」再續「B→⑧」。完成三件：⑩ 文件 drift 修好（純文件）、② judge V4 量度完成（Phase A+B，**未 ship**，reframe）、⑧ g24/sag 重登偵查（純唯讀，出 PLAN）。**零生產改動**：生產 judge prompt byte-identical、Supabase 零寫入、v3.2.2/凍結合約零接觸。
- **⑩ 文件 drift（完成）:** Leonard 確認方向＝「下游轉 Channel B 已完成」（依 S146 Leonard 確認 + S202 route-probe 零 channel-a 流量佐證）。改 `PROJECT_MASTER_SPEC.md`（line 49 Phase 2 狀態、line 262 Phase 2 + S145 endpoint 狀態）、`SYSTEM_ANALYSIS_AND_ROADMAP.md`（R1 摘要行 / dormant 包袱 §96 / R3 段 136-141 / 依賴表 214，共 5 處）、`HANDOFF_PACKAGE.md:32`（mobile endpoint combined→channel-b）。grep QC：stale 措辭殘留清零。
- **② judge V4 量度（完成，未 ship）:** Phase A（離線）造 `judge_prompts/v4a_s202.txt`(+8 最小)／`v4b_s202.txt`(+75 明示)（由 v3 base 程式生成，只差指定區）+ fresh held-out 集 `judge_transplant_fresh_s202.json`（10 條，7 移植/gap + 3 對照；逐條讀 5 passage 落 label，**0 flip**）+ harness `judge_acceptance.py` 加 `--cases`/`--cache` override（additive，frozen 不污染）。Phase B（Leonard dashboard reconfirm `gpt-4o-mini`）：`--plumbing-check` 綠 → fresh 集 score V3/V4a/V4b（全 9/10、同漏 FT06、答半 3/3）→ frozen-35 score V4a/V4b + **同 session V3 rebaseline** → 再 V3×2 / V4b×2 = **7 runs 噪音控制**。**定案**：V4b 穩修 GN10（false 0/3 vs V3 4/4）、答半 7 runs 全 12/12（零 recall 損）、但 **D01 3/3 + fresh FT06 照漏**（對象移植頑固）；V4a=V3（淘汰）；GN03 噪音（V3 2/4、V4b 1/3，prompt 無關）。**結論：prompt-only 槓桿掂到明示範圍移植、掂唔到隱含對象移植 → 建議唔 ship、② reframe 做非-prompt 對象核對機制。**
- **⑧ g24/sag 偵查（完成，出 PLAN）:** 親眼驗 Supabase（服務 key REST）：g24 383 / sag_2025_11 409、**正規化文字重疊 377**（推翻 handoff/PMS-era doc/searchChannelB.ts:415/code comment 全部「215」或「sag415·g24300」）、shared chunk ID=0、**g24 零獨有內容**（6 條 g24-only 內容 sag 全語義覆蓋：拭抹試驗/疏散/署任津貼/精神上無行為能力人士/胸肺 全 YES）、封面實寫「2026年5月版」。g24 被 `role_facts.json:694`（general._source_refs）+ `eval_queries.json`（mpf gold + `_tie_aliases`）引用，兩處都同 sag 並列 → remap 乾淨。合併 PLAN 6 步已入 Open Priorities ⑧。
- **Changed:** `dev/PROJECT_MASTER_SPEC.md`、`dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`、`dev/HANDOFF_PACKAGE.md`（⑩）；`dev/source/JUDGE_PROMPT_FINDINGS.md`（S202 段 + Still-open 更新）、`dev/source/judge_prompts/v4a_s202.txt`＋`v4b_s202.txt`（NEW）、`dev/source/judge_transplant_fresh_s202.json`（NEW）、`dev/source/judge_acceptance.py`（+`--cases`/`--cache`）、`dev/source/judge_runs/2026-08-02_s202_*`＋`chunks_cache_fresh_s202.json`（NEW，量度證據）（②）；handoff/log（closeout）。**無 backend production code / 無 Supabase 寫入 / 無 registry / 無 knowledge.json 改動。**
- **Done:** ⑩ 完成；② 量度完成 + findings 記錄 + reframe；⑧ 偵查完成 + PLAN 備妥。
- **QC:** 起手探針 4/4 綠；⑩ grep 殘留清零；② `--self-test`(frozen+fresh 各 0 fail)／`--check-parity`(byte-identical，生產 prompt 未動)／`--plumbing-check`(能) + 7 runs；⑧ 純唯讀 Supabase REST + 語義覆蓋驗證。
- **Evidence disposition:** ② 量度定案 + 方法論 promoted to `JUDGE_PROMPT_FINDINGS.md` S202 段（+ fresh 集 `_meta`、V4a/V4b、harness）；judge 非決定性教訓 → handoff opening message 🧭 紀律 #6；⑧ 真數 + PLAN → Open Priorities ⑧（執行前檔）；run 檔 kept as recent trace evidence（`judge_runs/2026-08-02_s202_*`）。
- **Sync:** ⑩ 純文件（非 code/retrieval/synthesis-gate）→ DOC_SYNC 無命中 code category；② V4 未 ship（parity 綠）；⑧ 純唯讀。凍結合約 + PLATFORM_VERSION 零接觸。Render/Pages 零 deploy。
- **Pending:** ① route-probe 8/5 讀 + 刪 probe；② 非-prompt 對象核對機制（reframed）；③ Channel A Option 2 入庫；⑧ 執行合併（HIGH risk 等 GO）；其餘見 Open Priorities S203 段。
- **Risks:** 🔴 生產度臨時 probe（`server.ts:168–198`）仍 live，8/5 讀完必刪（不變，V4 未 ship 無新增生產 risk）。⚠️ ⑧ 執行時 `searchChannelB.ts:415` + `wikiRepository.ts` 註解 stale 數（215/415/300）待一併清（已入 PLAN 步 ⑥）。
- **Log maintenance:** §4a `--check`：SESSION_LOG 145 行（<400）、最舊 entry 2026-07-30（<30 日）→ **no-op**（S202 已維護至 122，S203 +1 entry）。

### Next Session Handoff Prompt (Verbatim)

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S203 收工已就地更新為 S203 版〔state header S203 / 三件事 ⑩·②·⑧ / NEXT ② reframe / NEXT ⑧ 真數 377+PLAN / NEXT ⑩ DONE〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-08-02 Session 202 — NEXT ① route-probe 觀察窗第一次讀（8/2）＝全窗綠，零外部呼叫

- **ID:** Claude_20260802_S202
- **Summary:** 起手探針 4/4 綠。執行 NEXT ① S198 route-probe 觀察窗第一次讀（Leonard 喺 Render dashboard 讀、Claude 遠端放對照訊號協助）。**結果：由 2026-07-30 09:40 UTC 到 8/2，兩條 channel-a route（`/api/search/channel-a`、`/combined`）零外部呼叫。** 零 code / 零 Supabase / 零 route 改動 —— 純唯讀量度 ＋ handoff checkpoint。commit `2ec82cf`。
- **量度（route-probe 8/2 讀）:** Render Logs「Last 7 days」search `route-probe`：全窗 **26 行全部有主** ＝ 24× `s198-deploycheck-*`（7/30 Leonard 自測）＋ 2× `s201-control-probe`（8/2 Claude 為驗儀器親手放）。零第三方、零非自測 `origin`/`ua`。s198 最早行 7/30 10:40:48 AM（dashboard UTC+1）＝ 09:40:48 UTC，啱好對正觀察窗起點；instance `p2znr`/`26wlj` 對返 S198 紀錄。
- **儀器信心（S198 紀律落地）:** 頭先 search `route-probe` 空手 → **冇當「零流量」**（Render Hobby log negative ≠ 零事件）。先放 `s201-control-probe` 即時對照（curl 兩條 route，HTTP 404 但 probe 喺 `server.ts:190` 判 URL 時已印）→ 出到證儀器 work；再 search `s198` 用 7/30 已知事件回溯 → 首次空手係因「Last 7 days」時間範圍未 set，set 後 24 行全現形 → 證窗涵蓋返起點。雙對照齊先落結論。Hobby 保留 7 日、dashboard UTC+1 均第三度實證。
- **Changed:** `dev/SESSION_HANDOFF.md`（Current Baseline / Open Priorities / Last Session Record / State Reconciliation / Next Session Opening Message 五處 prepend 或重寫為 S202）；`START_NEXT_SESSION_PROMPT.txt`（由 opening message regen，mirror check byte-identical 107 行）；本 log（§4a 維護 ＋ 本 entry）。**無 code / 無 Supabase / 無 registry 改動。**
- **Done:** ① route-probe 8/2 第一次讀完成＝全窗綠；② handoff checkpoint push（`2ec82cf`）；③ §4a log 維護（4 舊 entry 搬 archive）；④ 收工 reconcile。
- **QC:** 起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main / Supabase 沿用 16,062）；probe 儀器 s198＋s201 雙對照證正常；START mirror check byte-identical；§4a `--check` trigger=True → `--apply` 成功（402→122，archive 只搬冇刪）。
- **Evidence disposition:** kept as recent trace evidence（量度證據＋儀器對照方法）；可重用教訓（Hobby log negative≠零事件、必先即時對照＋回溯已知事件驗窗）＝S198 既有紀律再落地，已在 handoff `Last Session Record` §6 ＋ opening message 🧭 #2，無新增 rule pack。
- **Sync:** DOC_SYNC 無命中（純唯讀量度）。凍結合約零接觸。Render/Pages 零 deploy。
- **Pending:** ① route-probe **8/5 第二次讀**（≤8/6 前）＋讀完刪 `server.ts:168–198` probe → 完成 NEXT ①、拆 backend route（⑥）前置；②–⑪ 見 Open Priorities S201 段不變（硬化 judge V4／Channel A Option 2 入庫…）。
- **Risks:** 🔴 生產度臨時 probe（`server.ts:168–198`）仍 live，8/5 讀完必刪。
- **Log maintenance:** §4a 觸發（402 行 > 400）→ `--apply`：402→122 行、entries 7→3，4 舊 entry 搬入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬冇刪，archive pointer 已在）。

### Next Session Handoff Prompt (Verbatim)

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S202 收工已就地更新為 S202 版〔route-probe 8/2 done·8/5 left、state header S202 / HEAD `2ec82cf`〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS〔107 行 byte-identical〕。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-31 Session 201 — NEXT ②：收 footnote judge-bypass（擴闊 decline 集 → 量度 → ship → deploy → live 驗）

- **ID:** Claude_20260731_S201
- **Summary:** 起手探針 4/4 綠。做齊 NEXT ② 一整條線:(b) 擴闊 judge decline 集 → 量 V3 baseline → 移走 footnote judge-bypass → deploy → live before→after 驗。**結果:footnote-lead gap query 由 live 砌數改為老實拒答,正經 footnote 答案零損失。** commit `fc287ff`(backend)deploy 已確認 live。Supabase 16,062 零寫入 / 凍結合約 / v3.2.2 / registry 256 全零接觸。
- **(b) 擴闊 decline 集:** handoff/findings 講「S199 撈咗 14 條 gap candidate」**從未持久化** → 重新 author 14 條,逐條打開 live top-5 passage 親眼讀先落 label。**11 gap + 3 answerable**,3 條逆假設 flip(GN06 gap→能、GN10 能→gap、GN12 gap→能)= passage 話事。入集:10 clean gap → decline **11→21**、GN11(採購>$200k,逐字答到)→ answer **11→12**;drop GN01(borderline);GN06/GN12 留做 findings。**D01 保留 decline**(Leonard domain 確認:學生病假醫生紙=校本要求、無 EDB 出處)。
- **量 V3 baseline(擴闊 35 條集, gpt-4o-mini, dashboard reconfirm):** `2026-07-31_s201_v3_widened.json` —— answer **12/12**(0 false decline)、decline **19/21**(2 false answer: D01 + GN10,**兩條都 transplant 類**)、D00 一票否決正確拒答。**answer 12/12 = 收 bypass 唔會整爛正經答案 → 淨贏**;D01/GN10 係 judge PROMPT 都捉唔到嘅主體/範圍移植,收 bypass 唔 touch(留 V4)。
- **CHANGE(收 bypass):** `searchChannelB.ts` `synthesizeAnswer` 移走 `trustedFootnoteLead`(連 `forcedFootnoteLeads` param/var/賦值一齊清);footnote lead 而家同其他嘢一樣過 V3。**保留:vault bypass(≥0.70)、footnote forced lead slot 排序、lexical gate、`RELEVANCE_JUDGE_PROMPT` 字串**。註解:retire S178 footnote-bypass 理由(D01 證偽)、寫入 S201。
- **Changed:** `searchChannelB.ts`(收 bypass,commit `fc287ff`);`judge_acceptance_cases.json`(+11 case,`_meta.widened_s201`);`JUDGE_PROMPT_FINDINGS.md`(Still open 更新 + S201 頭註);`judge_runs/chunks_cache.json`(35 cached)+ `judge_runs/2026-07-31_s201_v3_widened.json`(baseline run);`CODEBASE_CONTEXT.md`(footnote bypass 描述更新 + AI log);本 log + handoff。
- **QC:** `--self-test` 0 fail;`--check-parity` byte-identical(prompt 未郁);`tsc --noEmit` exit 0;零殘留 `forcedFootnoteLeads`/`trustedFootnoteLead` 引用;`footnote_lead_probe --run` **before==after: positive 30/30 / negative 5/13 / errors 0**(lead-slot 零回歸)。**live before→after(synthesize:true,生產)**:D17 消防演習 **ANSWER 砌數「每12個月」→ DECLINE**(flip ✅);D13 留位費 **ANSWER 970/1570 → 仍 ANSWER**(零退步 ✅);D01 學生醫生紙 **ANSWER → 仍 ANSWER**(V3 miss,維持現狀,pending V4 ✅)。
- **Evidence disposition:** 擴闊集 + label 出處 → `judge_acceptance_cases.json`(frozen);V3 baseline + live before/after 數 → 本 entry + run json(commit);可重用觀察(S199 14-candidate 從未持久化;label passage-driven;3 flip;footnote bypass premise 被 D01 證偽)→ FINDINGS + code 註釋;working scratch(candidate/chunks/labelled/live_check)留 scratchpad 未 commit。
- **Sync:** DOC_SYNC row 41(擴闊驗收集)+ **row 38(Synthesis 前置閘改動 —— 收 footnote bypass 正命中)**:footnote_lead_probe before→after 零損失 ✅、fail-open 保持(judge API error 仍 return true 答)、live 重探 ✅。`update_log.json` N/A。**Render deploy 已確認**(auto-deploy on push,live 驗 D17 flip 證實新 code 在跑);Pages 零改。
- **Pending:** **NEXT ②(新):硬化 judge V4 收 transplant 類(D01/GN10)** —— V3 主體/範圍移植捉唔到;⚠️ 喺已 frozen 嘅 35 條 acceptance set 上 tune 會燒 held-out,要另撈 fresh transplant 驗證集或原則性設計 + 一次量。其餘 handoff Open Priorities(③ Channel A Option 2 入庫、⑤ 8/2+8/5 route-probe 觀察窗、⑦ 拆 backend route…)不變。
- **Risks:** ⚠️ D01/GN10 transplant 類 live 仍會答(V3 判能;收 bypass 令佢哋去見 judge,但 judge 自己都miss → 要 V4)。⚠️ 收 bypass 令每條 footnote-lead query 多一個 judge call(+latency,同其他 query 一樣)。⚠️ S198 probe 仍 live,觀察窗 8/2 未到。
- **Log maintenance:** entry_count=6(<11)/ line_count<1500 → **trigger=False, no-op**。語意觸發:「curated footnote lead ≠ 答緊呢條 query」(D01 證偽 bypass premise)已寫入 code 註釋 + FINDINGS,唔另開 PROJECT_DECISIONS 避免重複。10-closeout backstop 未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S201 收工已整份重生為 S201 版〔NEXT ① route-probe 觀察窗 8/2 時間閘、② 硬化 judge V4 收 transplant〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS〔111 行 byte-identical〕。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-30 Session 200 — ship judge V3（Open Priority ③；Leonard 揀 Option 2，明文閘 override）

- **ID:** Claude_20260730_1548
- **Summary:** 起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main `30838f5` tree 乾淨 / Supabase count=exact 16,062）後，Leonard 揀 Open Priority ③「ship judge V3」。§3 HIGH risk + release gate + 撞到治理硬閘 → present PLAN + 三條路，Leonard 揀 **Option 2（照 ship + 明文 override）**。
- **Changed:** `backend/src/api/searchChannelB.ts`（`RELEVANCE_JUDGE_PROMPT` 換 V3 + 過時 寧緊莫鬆/5-5 rationale 註解重寫）；`dev/source/judge_acceptance.py`（`SHIPPED_PROMPT` 同步換 V3 保 `--check-parity`）；`dev/source/JUDGE_PROMPT_FINDINGS.md`（狀態頭 nothing shipped→SHIPPED + S200 override 記錄）；`dev/CODEBASE_CONTEXT.md`（judge_acceptance baseline 更新 + AI Maintenance Log S200）。commit `bcf7c4f` push origin/main。
- **Done:** V3 shipped（commit+push）。驗收證據＝`2026-07-30_s199_v3_4omini.json`（prompt 同 shipped code byte-identical，301 chars 已核）：primary 21/22、answer 11/11（收返 A02/A05/A06）、decline 10/11、D00 frozen-post=否、false=[D01]。
- **明文 OVERRIDE 記錄（AGENTS §2 rule 6）:** 衝突規則＝DOC_SYNC row 41 + `JUDGE_PROMPT_FINDINGS.md` bar「decline 半邊任何 false answer = 唔准 ship」。V3 有一個 false answer（D01）。override 理由：(a) 非退步（shipped 一樣 D01 答錯，`2026-07-30_s199_shipped_4omini.json`，零新增 false answer）；(b) 一票否決唔中（D00 正確拒答）；(c) D01 lead `footnote_curated` @0.574 > `FOOTNOTE_LEAD_SCORE` 0.45 → 生產行 footnote bypass、judge 從不 serve D01（harness 判係反事實）。risk：越過自己寫嘅閘＝precedent；緩解＝D01 明列 NEXT ④ 未修。
- **更正:** 交接 S199 ③「生產 model 已達…decline 全保」講多咗；artifact 實係 decline **10/11**（D01 漏），已於此記錄同 Current Baseline S200 ② 更正（comm 規則：corrected number 要同原數並存）。
- **QC:** `--self-test` 0 fail；`--check-parity` byte-identical；`--plumbing-check` 兩條 S177 scenario 叫得出「能」；`tsc --noEmit` exit 0；post-ship `footnote_lead_probe.py`（`2026-07-30_s200_postship_footnote.json`）positive **30/30 零損失**、negative 5/13、errors 0（=零回歸，V3 唔郁 bypass）。
- **deploy 已確認 live:** Leonard 貼 Render Events 綠剔「Deploy live for `bcf7c4f`: S200 ship judge V3」（4:50 PM UTC+1 = 15:50 UTC，對上 push）→ **V3 正式喺生產跑緊**。（收工當時外部驗唔到係因為 V3 差異 case 全 bypass judge、答案唔 flip；服務無 version endpoint。auto-deploy on push 已確立 S117。）
- **Evidence disposition:** absorbed into handoff（Current Baseline S200）；override rationale promoted to `JUDGE_PROMPT_FINDINGS.md` S200 header + `CODEBASE_CONTEXT.md`；run artifacts kept in `dev/source/judge_runs/`。
- **Sync:** DOC_SYNC row 41 required docs 全部已更（judge_acceptance.py / JUDGE_PROMPT_FINDINGS.md / CODEBASE_CONTEXT.md / SESSION_LOG / handoff Risks-in-baseline）；`--plumbing-check` 已跑、false-vs-accuracy 分開報、ship 後 footnote probe 已跑 —— row 41 checks 全數滿足。
- **Pending:** ① ~~deploy 確認~~ ✅ 已解（Leonard 貼 Render Events 綠剔 bcf7c4f）；② NEXT ② 收 footnote bypass（修 D01 live 錯 serve）—— 前置 (a) deploy 已解，仲剩 (b) decline 集擴闊 14 條 label 先入 §3 PLAN。
- **Risks:** 🔴 D01 live 仍錯 serve（未變，判 NEXT ②）；override 立咗「越 decline-half 閘」先例（需 NEXT ② 埋單）。deploy 傳播已確認 live（不再係 risk）。
- **Log maintenance:** §4a/N-rule trigger check（S200 收工執行）：SESSION_LOG 377 行（<400/<1500）、6 entries（<11）、最舊 2026-07-27（<30 日）→ **trigger=False → no-op**，未 archive。

（S200 收工完成：authoritative Next Session Opening Message 已於 `dev/SESSION_HANDOFF.md` 重生為 S200 版，`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check byte-identical。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-30 Session 199 — Leonard 叫停 judge、問返 Channel A 退役實況；A(Channel A) 然後 B(judge)，純量度

- **ID:** Claude_20260730_S199
- **Summary:** 起手探針 4/4 綠後跟 handoff 揀 Open Priority ① 修 judge。做到量度階段 Leonard 叫停、問「Channel A 退役到底去到邊，唔好淨係『我錯了』」→ 我停低重構成 A(Channel A)然後 B(judge)。**純量度 session：零 Supabase 寫入、零 code 改（`RELEVANCE_JUDGE_PROMPT` 同 bypass 常數未郁）、零 route 改。** 本 session 最貴一堂＝judge 量錯 model，由 Leonard 撳 Render dashboard 揪返。
- **起手探針 4/4 綠:** served `app.html` `PLATFORM_VERSION 3.2.2` + index 200 / Render `/health` `cache_a.warm=true size=455` / HEAD==origin/main `12bf7c3` tree 乾淨 / Supabase `content-range 0-0/16062`。加驗凍結合約：`_meta` 2.3.0 / facts 455 / guidelines 逐 topic 加總 158 / registry 256 —— 全部同 handoff 對得上，零 drift。
- **A — Channel A 退役重構（Leonard 叫停後）:**
  1. **precondition「Channel B 覆蓋 Channel A」已量 = 覆蓋唔晒。** 兩軸釐清：455 條事實入面 109 條鏡像入 store（`approved_fact`，url 全空 109/109，9 條已退、100 條仲 serve）、346 條淨經 `channel-a` route。職責歸屬類逐條打開 retrieved passage 核實（唔信 tier）：事實係「〔科主任〕須…／〔EO〕負責…」指名角色揹職責，top passage 全部只泛講程序、唔講邊個具名角色揹 → **結構性資料模型缺口，量度補救唔到**。
  2. **Leonard 拍板 Option 2（升做有出處 footnote）。** 唯讀可行性 triage：拆咗「總帳 141/141 有 url」陷阱（url 係 retrieval 目標唔係出處，對 83 UNVERIFIED 係 topically-近但錨點對唔到嗰份 = 44% 陷阱重演）。讀樣本：CLEARED 抽 5 ~3 可升（採購門檻 g01、教師申述 g05）、UNVERIFIED 抽 4 ~0-1。**真實大細：升唔到嘅硬核只有 24 條純職責歸屬（`[角色] 負責…`），唔係 ~100+；117 條「提到角色」大部分揾返出處可升。** → `CHANNEL_A_COVERAGE_FINDINGS.md` §5-6。
- **B — judge / footnote bypass:**
  3. **建凍結驗收工具 `judge_acceptance.py` + 24 條凍結集**（11 answer + 11 decline + 2 secondary，量度前 commit `a65e723`）。answer 半邊由 curated footnote 自己嗰條問題機械抽（每 16 條、剔走 S196 tune 過 4 個題目），11 條 origin footnote 全部 rank-1（答案逐字喺 chunk）。decline 半邊 11 條全新空白 + S177 `D00_s177_frozen_post`（用返 pre-fix chunks），三條複合陷阱（學生醫生紙 chunks 寫住教職員規則 / 成績表保存 chunks 有 3 年 7 年但無學生記錄年期 / 冷氣換 chunks 有 12 個月係消防裝置）。self-test 22 條含「答everything必衰」故意整壞守衛。
  4. **量錯 model：首兩份 baseline 用 code default `gpt-4.1-nano`**（`env.ts` fallback，README/DEPLOY 都寫呢個），**Leonard dashboard 確認 Render 實設 `OPENAI_MODEL=gpt-4o-mini`**。同一 shipped prompt：nano 0/11（constant 否）vs gpt-4o-mini 8/11。**「judge 恆等於否」係 fallback model 特性、唔係 shipped prompt 特性；S196 findings（8/16）全部標「未經生產驗證」。** nano run 改名 `_nano_ARTIFACT` + 檔內標記。
  5. **V3（S196 未 ship 候選）生產 model：21/22、answer 11/11（shipped 8/11）、decline 全保、held-out**（V3 出自 S196 16 條、同呢 24 條零 query 重疊）。
  6. **footnote bypass live 發現：** 7 條 footnote-lead 空白查詢 `synthesize:true` live 全部答咗、0 decline。逐條 Supabase ilike 核實：**D17「消防演習幾耐」實錘砌數**（「消防演習/演練/逃生演習」庫入面 0 條，「每12個月」由「消防裝置檢查」搬過嚟）；**D13「留位費」其實答啱**（g26/k1_admission 有 970/1570 有 url，我一度標錯做空白已更正）。**footnote lead 跳過 judge → 改 judge prompt 唔 touch 佢哋；但 D13 證明同路載住啱答案唔可以照剷 → 修法係「先修 judge、後收 footnote bypass」，次序企穩、件事耦合。**
- **Changed（全部新增/唯讀量度，零 live code）:** 新 `dev/source/judge_acceptance.py` + `judge_acceptance_cases.json` + `judge_prompts/v3_s196.txt` + `judge_runs/`（chunks_cache + 4 份 run：nano ARTIFACT ×2、生產 ×2、footnote bypass live）；擴充 `JUDGE_PROMPT_FINDINGS.md`（S199 段：生產 model 數 + bypass 耦合）+ `CHANNEL_A_COVERAGE_FINDINGS.md`（§5-6）；`CODEBASE_CONTEXT.md` Directory Map（`judge_acceptance.*` 條目 + judge baseline 更正）；`DOC_SYNC_CHECKLIST.md` **+1 row**（32→33）「Anti-confab judge prompt 改動」。
- **Done:** commits `a65e723`(凍結集) → `829aa49`(shipped baseline + plumbing control) → `c96dc6d`(V3 + decline 數更正) → `a80c69b`(model 錯誤修正) → `1aeab49`(A 重構) → `f02c069`(footnote bypass live) → `710d8cc`(Option 2 triage) → 本 closeout commit。
- **QC:** `judge_acceptance.py --self-test` 22/22 PASS ×N；`--check-parity` PASS（harness prompt 同 `searchChannelB.ts` 逐字相同）；`--plumbing-check` 兩 model 都出「能」（證明 constant-否 係判詞唔係 wiring）。D13/D17 砌數判定用 Supabase ilike count 逐條核實。Supabase 16,062 零寫入 / registry 256 / guidelines 158 / facts 455 / v3.2.2 / 凍結合約機械核實零接觸。eval **未重跑**（零檢索改動）。
- **我出過、並已更正嘅錯（四次，全部向「對自己有利」嗰邊）:**
  1. **用錯 judge model** —— 信 code default 而唔係 Render dashboard，出兩份唔代表生產嘅 baseline，Leonard 撳 dashboard 揪返。教訓「對照組證明儀器有反應、證明唔到儀器指住正確系統；凡 Render 側嘅嘢只有 dashboard 答得到」寫入 `judge_acceptance.py` 註釋 + FINDINGS + commit。
  2. **D13 標錯做空白** —— 「越多砌數個發現越大」個方向對我有利，打開 Supabase 核實先發現 970/1570 有出處、footnote 做緊正經嘢，已剔出 decline 集。
  3. **一度講「7/7 砌數」overclaim** —— 逐條讀後散為「7/7 答咗但只 1 條實錘砌數、1 條其實啱」。
  4. **decline 半邊數錯**（commit + findings 一度寫 12，實際 11）—— 直接由檔案數返更正，commit message 寫明無分數受影響。
- **Evidence disposition:** 當前狀態 + 四項未解 next priority → handoff `Current Baseline` S199 + `Open Priorities`；可重用程序知識（model 要 dashboard 確認 / 對照組局限 / url≠出處 / Option 2 triage / footnote bypass 耦合）→ `JUDGE_PROMPT_FINDINGS.md` + `CHANNEL_A_COVERAGE_FINDINGS.md` §5-6 + `judge_acceptance.py` 註釋（唔會被重生嘅位）；量度細節 + 四個自我更正 → 本 entry；凍結集 + 四份 run → `judge_runs/`（commit，跨 session 可比）。
- **Sync:** DOC_SYNC 命中 **1 row（新增，32→33）**「Anti-confab judge prompt 改動」—— 按 anti-pattern guard 先補行再填。`update_log.json` **N/A**（零入庫）。凍結合約 / `PLATFORM_VERSION` / Supabase 16,062 / registry 256 **全部零接觸**。**Render 零 deploy**（`RELEVANCE_JUDGE_PROMPT` 未郁，judge 量度係離線）；**Pages 零改動**（無前端）。`START_NEXT_SESSION_PROMPT.txt` 由 handoff fenced block 程式化抽取重生，mirror check PASS。
- **Pending:** Option 2 真入庫未開始（要 PLAN）；24 條孤兒細決定未做；ship V3 未做（要 PLAN）；footnote bypass 未收；🔴 觀察窗未讀（8/2 + 8/5）、probe 未刪；backend route 未拆；總帳三桶未讀完；`HANDOFF_PACKAGE.md:32` drift 未修。
- **Risks:** ⚠️ D01/D17 呢類 footnote-lead live 砌數而家仍 serve 緊（修要 §3 HIGH risk，唔喺本 session 純量度範圍）。⚠️ judge/synthesis model 係 `gpt-4o-mini` 唔係 code default，任何量度引用做生產前必 dashboard 確認。⚠️ S198 probe 仍 live，觀察窗未讀。⚠️ 3 條矛盾假期日數仍可經 channel-a route 攞到。
- **Log maintenance:** `session_log_maintenance.py --check` → **trigger=False**（line_count=316 / entry_count=4，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 「判斷儀器/量度前先確認佢係咪指住生產系統」屬跨 session 累積模式（S195 spotlight probe / S196 借錯測試集 / S197 44% / S198 log-search + warm 偵測兩次 / 本次 model 錯），但呢條係 S198 已寫入 `PROJECT_DECISIONS.md` Insights 嗰條嘅延伸（對照組局限），已喺 `judge_acceptance.py` 註釋 + FINDINGS 機械化，**唔另開 PROJECT_DECISIONS 條目避免重複**。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->
