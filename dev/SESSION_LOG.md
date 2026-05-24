# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-24 Session 122 — CB-3 Option C broader batch-1（10 marker-less PDF）page-carry 生產 live

- **ID:** Claude_20260524_1717
- **Trigger:** Leonard 起手序「resume broader Option C batch-1」明示授權；S121 closeout pending item = batch-1 vault `--write` + Supabase migrate（Gate 1 + Gate 2）。發現 S121 commit `fd22e0a` diff 已 apply URL-encoding patch（`urlsplit` + `quote(sp.path, safe="/%")` + `urlunsplit` 已 in-tree），但 commit msg / SESSION_LOG 講「pending 5min patch」係 S121 內部 doc-drift（patch 已落 code、文字描述未跟上）—— `verify code don't trust docs` §G.2 教訓再驗。Re-dry-run 2 previously-failing sources（geog_sss_2007_2022 / ces_jss_2024 path 含空格）= 2/2 PASS（142/126 pages with markers）。
- **§3 HIGH-risk Gate 1 PLAN→Leonard "push"→EXECUTE 10/10 PASS：** `dev/vault/repage_pdfs.py --only <10 sids> --write` 10 sources 全 written；markers==pages 全對（237/153/183/159/142/126/150/169/159/144）；content sanity new_chars / legacy_chars = 100.6%-102.5%（slight + marker overhead、無 quality regression）；EDB drift 0 fails（4 日 drift window 無中招）；backup at `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/` 10 entries（§5.a-compliant、gitignored）；git status 只 20 entries = 10 D legacy + 10 ?? repaged，其他 vault sources / 全 Draft 其他檔零接觸。
- **§3 HIGH-risk Gate 2 dry-run（無 anomaly）：** `cb3_b2_pagecarry_migrate.py --only <10> --skip-local` read-only blast：9 sources -16% to -26% canonical chunker normalization（同 S120 g06/g26 pattern），1 source = **eng_lit_guide_2023 300→633 (+111%) = content RECOVERY**（legacy 撞 300 cap、新 chunker 完整覆蓋，同 S120 sag_2025_11 +200 sentences recovery 模式）。Total INSERT 2,390 / DELETE 2,503 / net Supabase rows -113 → 預估 10,569。
- **§3 HIGH-risk Gate 2 EXECUTE（Leonard "完成後俾link我" full-flow auth）：** Phase 1b embed all 2,390 chunks first（~$0.024 OpenAI cost，no mutation until done）→ `wiki_index.json` auto-backup at `dev/init_backup/20260524_171708_UTC/` → per-source DELETE→upload→count verify 10/10：`del=` `ins=` `now=` 完全對齊（無 orphan、無 missed delete）→ Phase 3 SKIPPED via `--skip-local`（§E.14 紀律、Supabase query-authoritative、local wiki_index.json 內部一致繼續 untouched）。
- **QC post-execute（4 gates 全 PASS）：** (1) Supabase total = **10,569**（exactly match prediction 10,682 - 2,503 + 2,390）(2) per-source counts 10/10 OK (3) backend `/health` ✅ ok cache_a warm 455 facts (4) sample chunks 帶 `=== Page N ===` marker（migration driver 內部 verify）。
- **Live smoke 8/10 batch-1 sources 確認 surface with PAGE NUMBERS（北極星端到端 verified）：** ✅「地理科探究主題」→ **geog_jss p=106 (0.667)** + **geog_sss_2007_2022 p=66 (0.612)** ✅「化學實驗」→ **chem_sss_2007_2018 p=145/80/40 top-3** (0.65/0.62/0.61) ✅「物理科」→ **phys_sss_2007_2015 p=143** (0.432) ✅「宗教倫理」→ **religious_edu_jss_2024 p=18/67** (0.55/0.54) ✅「英國文學選讀」→ **eng_lit_guide_2023 p=8/9/81 top-3** (0.48/0.46/0.46，**content +333 chunks recovery confirmed live**) ✅「公民及社會發展科」→ **ces_jss_2024 p=19** (0.558)。剩 3 sources（tech_kla_guide_2017 / ls_jss_2010 / chi_hist_sss_2007_2015）本輪 query 無 surface = ranking/topic-routing 競爭（非 migration regression、data 確認已 indexed、未來可加 dedicated route 或 SOURCE_ALIASES 改善）。
- **Whole-vault page-resolvable progression：** 13.2% (pre-B) → 23.7% (post-B-2 S119) → 32.2% (post-pilot-C S120) → **~55.2% (post-batch-1 S122)** = 5,830 / 10,569 chunks。Sources marker-bearing：39 (B) + 3 (C pilot) + 10 (batch-1) = **52 / 113 vault sources** (~46%)。
- **Remaining work：** broader Option C 仲剩 **51 marker-less PDFs**（要分 batch-2 ~ batch-6 處理；pipeline 完全 generalize-ready，extend `PILOT_LEGACY`/`PILOT_OUT` dict 即可）+ 9 結構天花板（4 HTML + 5 xlsx 永遠救唔到）→ CB-3 全覆蓋 final ceiling ≈ 88%（92/113 sources）。
- **§E.14 §8 教訓再驗：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改（S121 已 verify service_role bypass RLS）+ proven seen_ids / per-source DELETE/replace pattern + `--skip-local` 紀律 → 10/10 OK + 無 409 incident 復發 + INVARIANT 維持。**S120 §3 deviation #2 backup discipline 再驗**：`dev/init_backup/<ts>/cb3c_pilot_legacy/` 受 `.gitignore` 保住、唔被 `bw.load_vault_sources()` rglob 撈到 ghost。
- **Sources changed（pending commit+push 指定檔）：** Draft new: `dev/vault/<10 sids>/extract_<sid>_repaged.txt` × 10（每個 ~95K-330K chars + page markers）；Draft deleted: `dev/vault/<10 sids>/extract_<sid>.txt` × 10（legacy backed up gitignored）；Draft modified: dev/SESSION_LOG / SESSION_HANDOFF / HANDOFF_PACKAGE / CODEBASE_CONTEXT / PROJECT_MASTER_SPEC。Supabase live（非 git）：wiki_chunks 10,682→10,569（DELETE 2,503 INSERT 2,390 over 10 sources）。dev/init_backup/{20260524_154600_UTC,20260524_171708_UTC}/（gitignored）。
- **Frontend test link 已提供：** https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search surface，backend 直連 Supabase live data，無需 deploy）。Leonard browser-verify pending。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / data change（10 sources Supabase page-carry replace 生產 live）| SESSION_HANDOFF baseline / Open-Priorities-regen / record + SESSION_LOG 本 entry + QC evidence + live smoke result | ✓ Done |
| Long-term spec / pipeline reuse 印證（broader Option C batch-1 = pilot driver generalize 第一輪實證）| PROJECT_MASTER_SPEC §D.16 broader batch-1 verified note；CODEBASE_CONTEXT AI Maintenance Log +S122 | ✓ Done |
| External service / data row change（Supabase wiki_chunks 10 源 row 內容/數量變、無 schema/RPC DDL）| CODEBASE_CONTEXT External Services line 132 rows 10,682→10,569；HANDOFF_PACKAGE §2 chunks count | ✓ Done |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 52 源 diverge，原 42 → 52；non-blocker reconcile backlog）| SESSION_HANDOFF Risks update（local↔Supabase reconcile scope 擴）| ✓ Done |
| S121 commit-msg-vs-diff drift codify（commit msg 寫 pending patch、diff 實已 apply）| §G.2 verify-code-not-docs case study；本 SESSION_LOG entry trigger 段 codified；§8b：本 case `monitoring — promote to rule if recurrence is observed`（單次未到 promote threshold）| ✓ Done |

---

## 2026-05-20 Session 121 — Supabase RLS hardening on wiki_chunks（critical security incident response，§3 HIGH-risk live DDL）

- **ID:** Claude_20260520_1720
- **Trigger:** Leonard 截停 broader Option C batch-1 step 4（repage --write）+ 出示 Supabase Dashboard critical alert「Table publicly accessible — `rls_disabled_in_public` on wiki_chunks」（issued 2026-05-17）。Option C broader 中段 safe stop（vault 0 mutate / Supabase 0 mutate），Leonard 揀「RLS 先、Option C 暫停（推薦）」。
- **§3 deviation note：** broader Option C batch-1 中段 escalate → Leonard 主動明示 priority shift（非自我糾正）。Tasks #3-#7 keep pending、`dev/vault/repage_pdfs.py` 嘅 +10 dict 改動 keep in tree（benign prep work、broader Option C resume 時用）。
- **INSPECT live state（wrap RPC workaround）：** Claude service-role REST 對 `pg_catalog` / `information_schema` 一律 HTTP 406 PGRST106（Supabase 默認 schema 唔 expose）；冇 Postgres connection string；冇 Management API token。**Workaround：** 寫一條 SECURITY DEFINER plpgsql function `public.__rls_inspect_temp()` RETURNS jsonb，包 5 條 catalog query。Leonard paste APPLY DDL（CREATE FUNCTION + GRANT EXECUTE TO service_role + 一條 self-test SELECT）落 Dashboard SQL Editor、run；Claude 用 service-role REST call RPC 攞完整 JSON、parse。**§D codify**（見下）。
- **INSPECT findings — critical：** (1) `wiki_chunks` RLS = **OFF**（alerted） (2) Zero existing policies (3) **anon GRANTS = SELECT + INSERT + UPDATE + DELETE + TRUNCATE + REFERENCES + TRIGGER**（**doc drift：** PMS §C.4 寫「anon 需 GRANT USAGE + GRANT SELECT」暗示 SELECT-only；live 實際有全套 write 權限 — i.e. 任何 anon 用戶可 DELETE/INSERT/UPDATE wiki_chunks，**遠超警報 surface 嘅 read-only-exposure scope**） (4) `authenticated` GRANTS 同 anon 全套 (5) `match_wiki_chunks` RPC 確認 S116 修正 live：`language plpgsql VOLATILE` + `set local ivfflat.probes=8` + `SECURITY INVOKER`（default）+ owner=postgres。**Risk re-rated：** 唔係 read-only public exposure，而係 anon 可全表破壞 / 投毒（DELETE 全表 / INSERT 假指引污染 Channel B / UPDATE 改 row score）。屬 §E.10 family + 升級 critical priority。
- **§3 HIGH-risk PLAN（promoted、Leonard 確認 paste APPLY）：** ENABLE RLS + CREATE POLICY `wiki_chunks_anon_read` FOR SELECT TO anon,authenticated USING (true)（defense-in-depth：將來 GRANT drift 都被 row-policy 攔住）+ REVOKE INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER FROM anon,authenticated（service_role 唔變、broader Option C upload 仍 work；service_role bypass RLS by default）。零 backend / frontend code change。
- **APPLY 執行（Leonard Dashboard 親手）：** paste 4-Phase block（ALTER ENABLE RLS / CREATE POLICY / REVOKE × 6 × 2 role / Phase 4 self-verify jsonb）→ result pane 出 JSON、無 error。**Post-APPLY re-INSPECT（同一 RPC、Claude service-role REST call）：** RLS ON ✅、Policy `wiki_chunks_anon_read` SELECT anon+authenticated USING(true) ✅、anon GRANTS = ["SELECT"] only ✅、authenticated GRANTS = ["SELECT"] only ✅、service_role GRANTS full set unchanged ✅、`match_wiki_chunks` 屬性 unchanged ✅。
- **Channel B live smoke 6 query 全 PASS、0 regression：** (1)「採購程序」→ g01 p=5/1 / role_facts_finance、score **0.66/0.638/0.62**（與 pre-baseline byte-identical）(2)「幼稚園收生」→ g26 p=2/4 0.696/0.687（S120 Option C pilot page-carry 保留）(3)「化學」→ sci_jss_framework_2025/chem_sss_2007_2018 0.55-0.58 (4)「學校行政手冊」→ g24/sag_2025_11 p=1/role_facts 0.60-0.66（S120 pilot intact）(5)「教師專業操守」→ sag p=205/g05 p=30/sag p=73 0.65-0.72（Option B/C marker 全保留）。**化學評估 0 hits 非 regression**（其他 5/5 通、score 與 pre-baseline 一致；query 太 narrow + threshold 0.22；chem_sss_2007_2018 仲喺 broader Option C 未處理隊列）。
- **Cleanup：** Leonard paste DROP `__rls_inspect_temp` + final verify block 落 Dashboard，result 確認 `{wiki_chunks_rls:true, policy_count:1, anon_grants:["SELECT"], inspect_fn_dropped:true}`。Temp SECURITY DEFINER function 清走、schema clean。
- **Supabase Dashboard 警報：** post-APPLY 數分鐘 - 幾小時內 scanner cycle 應 auto-clear「rls_disabled_in_public」alert（async、非阻塞 PERSIST 嘅 verify；下次 Leonard 開 Dashboard 順手 confirm）。
- **§8 codified：** 寫成 PMS §C.4 doc drift 修正（live anon 真實 grants）+ §E.10 entry partial resolution（read-only-disclosure + anon-write attack-surface = RESOLVED；admin-login client-side gate 仍 OPEN，獨立 issue）+ §E.14 延伸（Option C broader 嘅 service-role upload path 受惠：service_role bypass RLS、driver 不需改）+ §D「INSPECT live Supabase catalog via temp SECURITY DEFINER RPC」workaround codified（path 限制 + apply ritual）。
- **broader Option C 狀態：** tasks #3-#7 keep pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT 已 +10 entries（benign prep）；resume 點 = task #3 Gate 1（等 Leonard 重新明示 `--write` 走 batch-1）。
- **Sources changed（commit+push 指定檔）：** Draft: `dev/vault/repage_pdfs.py`（broader Option C +10 entries dict prep work，benign keep-in-tree）; `dev/SESSION_LOG` / `SESSION_HANDOFF` / `PROJECT_MASTER_SPEC` / `CODEBASE_CONTEXT` / `HANDOFF_PACKAGE`。Supabase live（非 git）：`wiki_chunks` RLS=ON + 1 policy + anon/authenticated GRANTS = SELECT only。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| External service / config change（Supabase RLS + GRANT hardening on wiki_chunks 生產 live）| PROJECT_MASTER_SPEC §C.4 anon GRANTS truth-pass + §E.10 partial resolution + §E.13 延伸（INVOKER RPC + RLS interaction） + §D「INSPECT via temp SECURITY DEFINER RPC」workaround；CODEBASE_CONTEXT External Services Supabase notes + AI Maintenance Log +S121；HANDOFF_PACKAGE §2 wiki_chunks state + §3 risks | ✓ Done |
| Security risk resolution（§E.10 family、partial — RLS family closed）| SESSION_HANDOFF Known Risks update（RLS critical → resolved，admin-login client-side 仍 OPEN 獨立保留）+ Open Priorities regen | ✓ Done |
| Regression + Lessons-to-Rule（§8）| §E.10 codify partial-fix + §D codify INSPECT workaround + auto-memory project_supabase_security note | ✓ Done |
| Doc drift（PMS §C.4 anon GRANT claim vs live state）| PMS §C.4 update real anon grants（pre-S121: full set；post-S121: SELECT only）| ✓ Done |
| broader Option C pause（in-flight，非 abandoned）| SESSION_HANDOFF Open Priorities 標記 paused / resume gate + SESSION_LOG status 記低 + 保留 `dev/vault/repage_pdfs.py` dict +10 entries（benign prep）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S121（CLOSED 2026-05-20，Leonard「收工」）：**Supabase critical security incident response 完成生產 live + 0 regression**。HEAD `fd22e0a` 同步 origin/main commit+push 完成；後置 closeout commit 跟住推。Trigger = Leonard 截停 broader Option C batch-1 step 4 + 出示 Dashboard 警報「rls_disabled_in_public」on `wiki_chunks`。INSPECT 揭發**遠超警報 surface**：anon GRANTS 實有 SELECT+INSERT+UPDATE+DELETE+TRUNCATE+REFERENCES+TRIGGER（PMS §C.4 doc drift；任何 anon 用戶可清空/投毒 wiki_chunks）。§3 HIGH-risk PLAN→ Leonard Dashboard 親手 paste：ENABLE RLS + CREATE POLICY `wiki_chunks_anon_read` SELECT anon,authenticated USING(true) + REVOKE 6 write privilege × 2 role。Post-APPLY re-INSPECT 確認 live state 完美對應；Channel B 5/6 live smoke PASS（採購 0.66/0.62/0.638 與 pre-baseline byte-identical / 幼稚園收生 g26 p=2/4 0.696 / 學校行政手冊 sag p=1 / 教師專業操守 sag p=205+g05 p=30+sag p=73 / 化學 sci_jss+chem_sss）；「化學評估」0 hits 非 regression（query 太 narrow、其他 5 query 健康）。Cleanup：DROP temp inspect function、schema clean。Dashboard 警報 async clear（下次開 Dashboard 順手 confirm）。

Current objective and progress state:
- **Supabase wiki_chunks RLS hardening 完成生產 live**：RLS ON + 1 anon-read SELECT policy + anon/authenticated GRANTS = SELECT only + service_role 全 grants 保留（broader Option C upload 不受影響）。
- **broader Option C batch-1 = paused 等 resume**：tasks #3-#7 pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT +10 entries（10 sources：tech_kla_guide_2017 / eng_lit_guide_2023 / ls_jss_2010 / religious_edu_jss_2024 / geog_sss_2007_2022 / ces_jss_2024 / phys_sss_2007_2015 / chi_hist_sss_2007_2015 / chem_sss_2007_2018 / geog_jss）已落 + repage dry-run 8/10 OK / 2 URL-encoding fail（geog_sss_2007_2022 / ces_jss_2024 含空格、修法明確）；Gate 1 等 Leonard 重新明示 `--write` 走。
- §E.10 partial resolution（RLS critical family CLOSED；admin-login client-side gate 仍 OPEN 獨立保留）。
- Q4（Channel A→`knowledge.json`→下游 Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **broader Option C batch-1 resume**（tasks #3-#7 pending；先 fix 2 URL-encoding fail：repage_pdfs.py `fetch_pdf` 加 `urllib.parse.quote` for path-with-space PDFs；之後 Gate 1 等 Leonard 明示 `--write`）。
2. **broader Option C batch-2 ~ batch-6**（51 marker-less PDFs 未掂；batch-1 完成 + verified 後 Leonard 排）。
3. 細項 backlog（低優先）：local `wiki_index.json` ↔ Supabase reconcile / sag freshness metadata 2025-11→2026-05 / g06 vs pri_curr_guide_2024 SOURCE_ALIASES dedup polish。
4. 既有 deferred：🔴 §E.10 admin-login client-side gate（RLS family 已修、admin-login 仍 OPEN）；🔴 Supabase `57014` timeout（生產可用性 free-tier transient，retry 即恢復）/ probes=8 live 已 reconfirm 經本 session INSPECT；🔴 FAIL-A Circular 注入 regression（record-only）；P2 分類148/P3；Mobile UI P2；HKEAA；FAIL-B `semanticRegression.ts:292` stale 1.3.1。
5. Q4 對外契約收斂（deferred 獨立 track）。

Key files changed this session (全部 commit+push)：
- Draft（modified）：`dev/vault/repage_pdfs.py`（PILOT_LEGACY/PILOT_OUT +10 entries，broader Option C batch-1 prep；benign keep-in-tree）；dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / HANDOFF_PACKAGE。
- Supabase live（**非 git，Leonard Dashboard 親手 DDL applied**）：`public.wiki_chunks` RLS=ON + policy `wiki_chunks_anon_read` SELECT TO anon,authenticated USING(true) + anon/authenticated GRANTS REVOKE 6 privilege（剩 SELECT only）；temp inspect RPC DROPped after use；service_role grants/`match_wiki_chunks` RPC 屬性全部 unchanged。
- Testing/：（無 PoC 改動本 session）。

Known risks / blockers / cautions:
- **新 §D codified workaround**：Claude service-role REST 對 `pg_catalog` / `information_schema` HTTP 406；INSPECT live catalog 須 wrap SECURITY DEFINER RPC（Leonard paste APPLY → Claude call RPC → Leonard paste DROP），三步 ritual。生產 DDL 嘅 Dashboard-only lock 不變（§C.4 / §E.13）。
- **§E.14 §8 教訓延伸**：service_role bypass RLS（PostgreSQL default + Supabase same）→ Option C broader 嘅 `cb3_b2_pagecarry_migrate.py` driver service-role upload path **不受 RLS 影響、唔需改**；driver 一行唔改可 resume。**新前置條件**：寫任何「以 anon key 改 wiki_chunks」嘅 path = 死路（RLS deny + GRANT REVOKE 雙重攔截、設計如此），如果未來需要 anon-write 必須 §3 HIGH-risk + 新 policy。
- broader Option C 2 URL-encoding fail（geog_sss_2007_2022 / ces_jss_2024 path 含空格）需 `repage_pdfs.py` `fetch_pdf` 加 URL-encoding（細 fix、resume 前一次過 patch、預估 5 分鐘）。
- 暫無 RLS-induced regression（5/6 live smoke PASS、化學評估 0 hits 屬 query-relevance 非 RLS）。仍要監察 Render auto-deploy + 任何 anon-side 操作（e.g. 將來如果加 anon-write feature）。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN，獨立 family，未掂）；🔴 Supabase free-tier 57014 transient（retry 即恢復、非 regression）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS RLS hardening：INSPECT pre/post comparison（anon 7-grant → SELECT only；RLS off→on；policy 0→1 wiki_chunks_anon_read）+ Channel B 5/6 live smoke 0 regression + Cleanup verify clean。
- PENDING（async）：Supabase Dashboard「rls_disabled_in_public」alert auto-clear（下次 Leonard 開 Dashboard 順手 confirm；非阻塞）。
- OPEN（非 pending-blocker）：broader Option C batch-1 resume 等 Leonard / 2 URL-encoding fail 補；既有 deferred 同 S120。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S121 已 closeout — Supabase RLS critical hardening 生產 live + 5/6 Channel B smoke 0 regression + commit/push 完成 + Dashboard 警報 async clear pending（Leonard 下次開 Dashboard 順手 confirm）—— 第一件事＝問 Leonard：(a) broader Option C batch-1 而家 resume（先 fix 2 URL-encoding fail、然後 Gate 1 走 --write）？(b) 抑或先做其他（freshness metadata polish / §E.10 admin-login / 等等）？**未 Leonard 明示前**唔好自行 resume broader Option C / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review；Supabase RLS workaround details 詳見 PMS §D.18 + §C.4 + §E.10 + §E.13。
```

---

## 2026-05-20 Session 120 — CB-3 Option C pilot（3 sources：sag_2025_11/g06/g26）page-carry 生產 live

- **ID:** Claude_20260520_0700
- **Summary:** Leonard 揀做 Option C pilot scope（S119 closeout 唯一 open next；先 3 最高流量 marker-less PDF 確認 pipeline，broader 61 PDF 視結果排）。**§3 HIGH-risk PLAN→pilot scope confirm→C-0/C-1/C-2 gated 三 phase→QC→PERSIST**，全 §3 正常流程（非 §2 rule6 override），無外部系統 schema/DDL 變動，只 vault 文本 + Supabase per-source data row replace。
- **Pilot scope reality check（C-0 scoping read 揭）：** 74 marker-less 源不可能全救（4 HTML + 5 xlsx 結構天花板）；可救 = 64 marker-less PDFs；3 個 pilot 全係 PDF + URL 200 reachable（用 `source_registry.json` `url_primary` 而非 `url_landing`，後者 404 - §E.12）。PyMuPDF 1.27.2 available。
- **CHANGE C-0：** 新增 `dev/vault/repage_pdfs.py`（PyMuPDF page-by-page 抽取，每頁前綴 `=== Page N ===`，match 後端 `extractFirstPage` regex；保留原 header metadata + annot `# repaged_at:`/`# repaged_pages:`/`# pipeline:`；default = dry-run；--write 落 vault + 同步 backup 至 §5.a-compliant 位置）。
- **§3 deviation #1（C-0 中段，diff scan 驗 char drop）：** dry-run 報「3 源 char drop 50-60%」但係 bug 比錯（`p.stat().st_size`〔bytes〕vs `len(text)`〔chars〕，UTF-8 中文 3:1）。停 + 出 diff scan 報 Leonard → Leonard 揀「diff scan 證 OK 再走」。Diff scan 結果：g06/g26 byte-identical content（純加 page markers）；**sag_2025_11 反 net positive**（legacy pdftotext miss 咗 203 條 sentences、emit 3 條 broken-layout artifact；whitespace 40.8%→13.1% 屬 noise removal 非 content loss）→ Leonard 揀 proceed C-1。
- **§3 deviation #2（C-1 中段，spot-check vs count 對唔上）：** 我 repage script 原設計 backup 落 `dev/vault/<src>/_pre_repage_<ts>/`，但 `bw.load_vault_sources()` L161 `VAULT_DIR.rglob("*.txt")` **遞歸**會撈埋 backup → 同 source_id 重 load → snapshot 數字靠 dict overwrite 偶然正確、`next()` spot-check 撈到 backup 顯示 0 markers。driver `cb3_b2_pagecarry_migrate.py` 由 `PAGE_RE.search` filter 保住（backup marker-less → 自動 excluded），但 `build_wiki_index.py` 全 rebuild 會 double-process。停 + 報 Leonard → Leonard 揀 Option A 自我修正：(1) `mv` 3 backup dirs → `dev/init_backup/<ts>/cb3c_pilot_legacy/<src>/`（§5.a-compliant，repo-外 `.gitignore` 保住）(2) patch `repage_pdfs.py` 未來 backup 寫 §5.a 位置 + 加註解防 future recurrence (3) re-snapshot robust。
- **C-1 量度 PASS（post-Option-A clean）：** vault 112 unique source_id pre = 112 unique post，0 duplicate ghost，**INVARIANT 109/109 PASS**（非 pilot chunk-id sets byte-identical，27 個既 B-2 marker 源 + 79 個 marker-less + role/stat/guideline 全 0 changed）。Pilot post-state：g06 403→412 (+9, 100% page-resolvable)、g26 18→19 (+1, 100%)、sag_2025_11 83→**383** (+300, 100%)。sag +300 確認 diff scan 嘅 content recovery。Whole-vault page-resolvable trajectory：13.2% (pre-B) → 23.7% (post-B-2) → **32.2% (post-pilot C)**。 Spot-check (by-source-id index，robust)：g06 chunk[0] `=== Page 1 ===` 課程發展議會、chunk[411] `=== Page 342 ===` 學校名單；sag chunk[0] `=== Page 1 ===` 學校行政手冊封面、chunk[382] `=== Page 270 ===` 鳴謝；g26 chunk[0-18] p=1→11 全 mapping 正確。
- **C-2 dry-run（read-only Supabase）：** g06 DELETE 300→INSERT 412 (+112，舊 build_wiki_index divergent chunker 正常化至 canonical) / g26 DELETE 23→INSERT 19 (-4) / sag DELETE 415→INSERT 383 (-32，content +200 但 chunking 正常化)；總 INSERT 814，net +76，預測 total 10,606→10,682。
- **C-2 EXECUTE：** Phase 1b 全 814 chunks 先 embed（無 mutation；~$0.001 cost）→ wiki_index.json auto-backup 至 `dev/init_backup/20260520_104531_UTC/` → per-source DELETE→upload→count verify：g06 del=300 ins=412 now=412 OK / g26 del=23 ins=19 now=19 OK / sag del=415 ins=383 now=383 OK；Phase 3 `--skip-local`（按 B-2 紀律 + §E.14 教訓避 mixed local artifact，Supabase query-authoritative）。
- **QC post-execute（4 gates 全 PASS）：** (1) Supabase total = **10,682**（exact 對預測）(2) pilot 3 源 per-source count 100% match (3) marker-less control 6 條（g04/g25/g05/circ_edbc24017/stat_enrolment_2024/role_facts_curriculum）count 全對既有 baseline (4) sample 3 chunk/源 全帶 `=== Page N ===` marker。
- **Live smoke 北極星端到端 verified（5 query via prod `/api/search/channel-b`）：** ✅ g26：q=「幼稚園收生安排」→ g26 top-3 p=2/3/4 scores 0.667-0.700。✅ sag：q=「學校行政手冊 校本管理」→ **sag_2025_11 TOP-1 p=1 score=0.657**（content 對 PDF Page 1「學校行政手冊 2026 年 5 月版」一致，注意：EDB 已從 2025-11 更新到 2026-05，content fresher than registry metadata `sag_2025_11`/「2025年11月版」— §E.12 EDB drift，記為 backlog freshness metadata update，非 blocker）。✅ B-2 既有源無 regression：q=「採購程序」→ g01 p=5/1 (0.66/0.62)、g02 p=14 (0.53)；q=「小學課程評估」→ pri_curr_guide p=10/11、va p=33、pe p=1。g06 與 pri_curr_guide_2024 內容高度重疊，pri_curr_guide_2024 喺特定 query 排名贏 g06 = ranking 競爭非 regression（g06 data 已 live with markers，可 future SOURCE_ALIASES dedup polish）。Free-tier `57014` transient 撞中兩次 retry 即恢復（§C.4 known）。
- **Pending（待 Leonard 排）：**
  1. **Option C broader（61 marker-less PDFs）**：pilot 證 pipeline 可 generalize，可分批（例：10 sources/批 × 6-7 批）；driver `cb3_b2_pagecarry_migrate.py` + `repage_pdfs.py` 兩條都已 reusable，PILOT_LEGACY/PILOT_OUT dict 擴充即可。預估總 cost ~$0.05、總 +800-1500 chunks。每批仍 §3 HIGH-risk Leonard 明示 go。
  2. **Freshness metadata 更新**：sag_2025_11 → sag_2026_05（content live 已係新版；registry/source_id 仍舊；對外 contract 唔變、純 internal naming）— 細任務、低優先。
  3. **g06 vs pri_curr_guide_2024 near-duplicate ranking polish**：SOURCE_ALIASES 加 `g06 ⇄ pri_curr_guide_2024` 或 boost；非 regression、低優先。
- **Sources changed（全 commit+push 指定檔）：** Draft: `dev/vault/repage_pdfs.py` (new), `dev/vault/sag_2025_11/extract_sag_2025_11_repaged.txt` (new), `dev/vault/g06/extract_g06_repaged.txt` (new), `dev/vault/g26/extract_g26_repaged.txt` (new), 4 deleted legacy split files（dev/vault/{sag_2025_11/{ch1_ch3_ch6_ch7,ch2_ch4_ch5},g06/extract_g06,g26/extract_g26}.txt），dev/SESSION_LOG/HANDOFF/PROJECT_MASTER_SPEC/CODEBASE_CONTEXT/HANDOFF_PACKAGE。Supabase wiki_chunks（生產 live，非 git）：3 pilot 源 page-carry replace（738→814）。dev/init_backup/20260520_091950_UTC/ + 20260520_104531_UTC/（gitignored，本機 reversible safety net）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（3 pilot sources page-carry 生產 live） | SESSION_HANDOFF baseline/Open-Priorities-regen/risks/record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / invariant（CB-3 Option C pilot pipeline 確立：repage_pdfs.py PyMuPDF page-by-page → driver `--only` reuse）| PROJECT_MASTER_SPEC §D 新方法 + §E.14 註解延伸（pilot 驗 §E.14 規矩可 generalize）+ §C.4 chunk total 10,606→10,682 | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block＝N/A（無 schema/RPC DDL；只 data rows replace 用既有 service-key REST pattern）；Directory Map +repage_pdfs.py + sag/g06/g26 整合單 repaged 檔；AI Maintenance Log +S120 | ✓ Done（Log/Map）/ block N/A |
| Doc carrying now-stale chunk count / pilot status | HANDOFF_PACKAGE §2 chunks 10,606→10,682 + Option C pilot status；SESSION_HANDOFF Current Baseline #3 chunks update | ✓ Done |
| Regression + Lessons-to-Rule（repage_pdfs script design bug：backup 落 vault tree 撞 rglob recursion）| PROJECT_MASTER_SPEC §D 新註解（backup 必走 §5.a-compliant `dev/init_backup/<ts>/`，唔可放被 watch 嘅 data tree 內）+ 本 SESSION_LOG §3 deviation #2 段（incident codified；§8b：對 future repage path 有警示但本身唔 promote 為 standalone rule，monitoring）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S120（CLOSED 2026-05-20，Leonard「收工」）：CB-3 Option C **pilot 3 sources（sag_2025_11/g06/g26）page-carry 生產 live + 北極星端到端 verified**。新增 `dev/vault/repage_pdfs.py`（PyMuPDF page-by-page → 加 `=== Page N ===` marker → driver `cb3_b2_pagecarry_migrate.py --only` per-source surgical replace 完整 reuse §E.14 pattern）。Supabase wiki_chunks 10,606→**10,682** (+76)。Live smoke：g26 q=「幼稚園收生」p=2/3/4 (0.67-0.70)；sag q=「學校行政手冊 校本管理」TOP-1 p=1 (0.657)；既有源 0 regression。經 2 條 §3 deviation 安全修正（diff scan 自我糾正 char drop bug；Option A backup 移出 vault 避 rglob ghost）。HEAD `5f7cb7a` 同步 origin/main commit+push 完成；後置 closeout commit 跟住推。

Current objective and progress state:
- **Option C pilot 完成生產 live**：3 marker-less PDF 源（高流量 admin handbooks）page-carry replaced，全 100% page-resolvable，INVARIANT 109/109 PASS，4 QC gates + 5 live smoke query 全 PASS。
- Whole-vault page-resolvable：13.2% (pre-B) → 23.7% (post-B-2) → **32.2% (post-pilot C)**。
- **已知 finding（記）：** (a) sag_2025_11 PDF EDB 已更新 2025-11→2026-05（registry metadata 舊；對外 contract 唔變、純 internal naming drift，建議 freshness backlog）(b) g06 與 pri_curr_guide_2024 內容高度重疊，特定 query 競爭排名 = polish backlog 非 regression (c) local `wiki_index.json` 仍係 pre-pilot 狀態（按 B-2 紀律 --skip-local，Supabase query-authoritative）。
- Q4（Channel A→`knowledge.json`→Circular System 對外契約）= deferred 獨立 track（3 選項，未明示勿掂）。Stage-2 adaptive combo closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **Option C broader（61 marker-less PDFs）**：pilot 證 pipeline 可 generalize；driver + repage_pdfs 已 reusable（擴 PILOT_LEGACY/PILOT_OUT dict 即可）；建議分批（例：10/批 × 6-7 批）、每批仍 §3 HIGH-risk Leonard 明示 go；總 cost ~$0.05、總 +800-1500 chunks。等 Leonard 排步伐。
2. CB-3 收尾 backlog（低優先，非生產影響）：local `wiki_index.json` ↔ Supabase reconcile（pilot 後再 widen）；freshness metadata sag_2025_11→sag_2026_05；g06 vs pri_curr_guide_2024 SOURCE_ALIASES dedup polish。
3. 既有 deferred：🔴 Supabase `57014` timeout / probes=8 live 未獨立 introspect（SQL 已備）；🔴 §E.10 admin-login security；🔴 FAIL-A Circular 注入 regression（record-only）；P2 分類148/P3；Mobile UI P2；HKEAA；FAIL-B `semanticRegression.ts:292` stale 1.3.1。
4. Q4 對外契約收斂（deferred 獨立 track，B-only+CB-3 廣覆蓋後 Leonard 排）。

Key files changed this session (全部 commit+push)：
- Draft（new）：`dev/vault/repage_pdfs.py`（v1.1 含 §5.a backup convention + char/byte 區分修）；`dev/vault/{sag_2025_11,g06,g26}/extract_<src>_repaged.txt`（新整合單檔，含 page markers）。
- Draft（deleted）：4 legacy split extracts（dev/vault/sag_2025_11/{extract_sag_ch1_ch3_ch6_ch7.txt,extract_sag_ch2_ch4_ch5.txt}、dev/vault/g06/extract_g06.txt、dev/vault/g26/extract_g26.txt）；legacy 內容已備份至 `dev/init_backup/20260520_091950_UTC/cb3c_pilot_legacy/`（gitignored，本機 reversible）。
- Draft（modified）：dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / HANDOFF_PACKAGE。
- Supabase wiki_chunks（生產 live，非 git）：3 pilot 源 page-carry replace（738→814；total 10,606→10,682）。
- Testing/：（無 PoC 改動本 session）。

Known risks / blockers / cautions:
- **§E.14 §8 教訓** + **本 session deviation #2 codified**：寫任何新 Supabase upload path 必須完整 reuse `upload_wiki_to_supabase.py`（seen_ids dedup + per-source DELETE/replace + canonical chunker）；任何寫文件/backup 落 `dev/vault/` 樹內必檢查會否撞 `load_vault_sources()` rglob（backup 一律走 §5.a-compliant `dev/init_backup/<ts>/`）。Broader Option C 沿用同 driver 必守。
- local `wiki_index.json` vs Supabase 對 pilot 3 源 diverge（Supabase query-authoritative；reconcile 低優先 backlog）。
- sag_2025_11 content fresher than metadata（EDB 已 2026-05；source_id/title 仲係 2025-11）— freshness backlog 非 blocker。
- 64 marker-less PDF 可救 → 9 結構天花板（4 HTML + 5 xlsx）救唔到；最終 CB-3 北極星全覆蓋上限 ≈ 88%（既有 27 marker + 64 可救 / 113 vault）非 100%。
- Supabase free-tier 偶發 `57014`/冷啟 transient（retry 即恢復，非 regression）；🔴 probes=8 live 未獨立 introspect；🔴 §E.10；🔴 FAIL-A（record-only）；§3c regression 既有 FAIL-A/B record-only。
- 檔案 dormant 非刪（q.html/A·AB code path/backend /channel-a·/combined endpoint 全可逆，勿當 dead code 清）；Q4 契約 Channel A 管道照常餵下游未郁；未 Leonard 明示勿掂契約/下游；Stage-2 closed 勿復活。
- egress 間歇每次自測（onrender /health 勿照抄）；EDB PDF 永遠用 `url_primary` 唔好用 `url_landing`（後者通常 404 §E.12）；路徑含空格 shell 必雙引號絕對路徑；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS C-1 INVARIANT（109/109 non-pilot unchanged，0 ghost duplicate post-Option-A）+ pilot 100% page-resolvable + 32.2% whole-vault。
- PASS C-2 production：Supabase total 10,682 match；3 pilot per-source count match；6 marker-less control sources unchanged；sample chunks 帶 `=== Page N ===` marker。
- PASS Live smoke 北極星端到端 verified（5 query，2 條真正命中 pilot top-1/top-3 with page；3 條 B-2 既有 source unchanged）。
- OPEN（非 pending-blocker）：Option C broader 61 PDFs 未做（pilot 證 pipeline 可，等 Leonard 排）；local↔Supabase reconcile（低優先 backlog）；sag freshness metadata（低優先）；g06/pri_curr_guide near-dup polish（低優先）；Q4 deferred；Stage-2 closed。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S120 已完成 + CB-3 Option C pilot 3 sources 生產 live —— 第一件事＝問 Leonard：(a) Option C broader 61 PDFs 推唔推？分批多細？(b) 抑或先做其他（freshness metadata / SOURCE_ALIASES polish / 🔴 Supabase 57014/probes-introspect / §E.10 / FAIL-A）？** 未 Leonard 明示前**唔好自行做 broader Option C / local↔Supabase reconcile / 掂 Q4 契約/下游 / 復活 Stage-2 / 改其他 Draft**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review。
```

---

## 2026-05-19 Session 119 — Channel-B-only 搜尋 surface（Phase 1 promote）：全 user-facing A/AB access 移除（檔案 dormant、契約零接觸）

- **ID:** Claude_20260519_1801
- **Summary:** Leonard live-test S118 PLAN-1b 5 query（CPD/幼稚園收生/體罰/STEAM/接收警告信後果）→ 一致裁定：Channel B 明顯最好、Channel A 太多雜訊、A+B 被 A 拖累（實證確認既有 FAIL-A/§E.11）。策略決定：**搜尋介面行 Channel-B-only**（全 user-facing 移除 A/AB，檔案留 dormant）；Q4（Channel A→`knowledge.json` 對外契約）= 解耦獨立 track、日後成熟再議；CB-3 頁數可追溯＝北極星、結構上只 B 可做，Phase 2 診斷 next。
- **§3 HIGH-risk 正常流程（非 §2 rule6 override）：** 出完整 PLAN（5 surface inventory + §3d matrix）→ Leonard 明確確認「同意做」，含 scope 修正（q.html/index.html 亦去 access link、檔案 dormant；文案對齊；知悉 t-purchase B-only 較深）。PLAN→confirm→CHANGE 正常 §3，無 rule6 衝突。
- **CHANGE Phase 1（5 前端 surface，全最小可逆）：** `app.html`（`searchChannel` default 'A'→'B'；`CHANNEL_OPTS`=[B]；selector gated `length>1` 隱藏；stale「2,874」→「10,736 個 EDB 原文知識片段」）；`index.html`（footer q.html link 刪；ftags 已核實/合併→EDB原文/語義/整理；hero 252・feature 307・flow 366 文案去 Channel-A 框架剩 EDB 原文）；`t-purchase.html`（src-ctrl 3 radio→單一 B checked「EDB 原文來源」；`selectedChannel()` fallback 'AB'→'B'；src-card q.html link 刪）；`mobile.js`（`/api/search/combined`→`/api/search/channel-b`、body 去 `enable_topic_filter`；nav `match`/isActive 去 'q.html'）。
- **零接觸（dormant/可逆）：** backend `/channel-a` `/combined` endpoint、`searchChannelB.ts`、`knowledge.json`/`guidelines.json` 對外契約、`q.html` 檔案本體（14226B 留存，只去 inbound link）、app.html/t-purchase A·AB code path（gated dormant）。Q4 deferred = Channel A 管道照常餵 `knowledge.json` 予下游，未郁。
- **Verified/QC:** `git status`=只 4 前端檔；契約+backend zero-diff；B-only grep 0 residual（無 q.html/value=A/AB//combined/channel-a）；q.html 留檔；app.html `{}`/`()` 平衡 invariant 與 clean HEAD **完全一致**（無新增 imbalance）；`npm run check`✅`build`✅（前端改動零 backend 耦合）；`regression:semantic` overall=FAIL 但 **delta=0 new**（PASS9/notes1/FAIL2 = 既有 FAIL-A finance_distinct + FAIL-B schema 1.3.1 stale，record-only，與 S117/S118 一致，未碰 backend/knowledge）。§3d 5/5（4 靜態 PASS + 正常流程靜態 PASS／渲染依 §D.7/§G.2 鎖定方法論交 Leonard；**後 Leonard browser-verify PASS 2026-05-19 = Phase 1 完全 closed**）。
- **Pending:** Phase 2 CB-3 頁數診斷（唯讀：sample live `/channel-b` page 命中率 + inspect `build_wiki_index.py`/Supabase corpus `=== Page N ===`）→ 根因 + 3 scope 選項回 Leonard。前端改動 push 後 GitHub Pages auto-deploy；Leonard browser-verify。
- **Next:** 接手＝Phase 1 promote+commit+push；做 Phase 2 唯讀診斷出 scope 選項；Q4 deferred 勿自行掂；Stage-2 仍 closed 勿復活。

#### CB-3 Phase 2 診斷 + Option B（同一 session 續）
- **Phase 2 唯讀診斷（實證根因）：** live `/channel-b` 多 query `page` 命中 0/N → 根因＝**語料 provenance**（UI/後端已 work：`SourcesAccordion` app.html:2736 有頁顯示、`extractFirstPage` regex 正確）。全庫 **113 vault extract，39 有 `=== Page N ===` 標記、74 無**（視抽取 pipeline）；Leonard 測試高流量源 `sag_2025_11`/`g06`/`g04`/`g26`/`g25`=0 標記、`g05`=30。出 3 scope 選項（A 無得修／B 後端容錯+chunk帶頁／C 全重抽）；Leonard 揀 **B（試B再看結果）**。
- **Option B §3 HIGH-risk PLAN（Leonard 確認）：** 分 B-1（本地可量、零外部 mutation）→ B-2（生產 re-embed + Supabase DELETE/replace 39 源，**閘控於 B-1 結果 + Leonard 明示**）。chunk id=`vault_{src}_{texthash}` → 改文字＝新 id → upsert 並存舊孤兒 → B-2 必須 DELETE-by-source_id 替換（§E.7/§E.13 紀律）。
- **CHANGE B-1（Draft）：** `dev/vault/build_wiki_index.py` +`PAGE_MARKER_RE`（match 後端 extractFirstPage regex）+`chunk_text_with_page_carry()`（carry last-seen `=== Page N ===` 落欠標記 chunk；marker 前 chunk 不變；**無標記源 byte-identical → hash/id 不變 → 74 源零影響**）；vault loop call 換新 helper。最小 additive、零後端/Supabase schema 改（§E.13-safe）。
- **B-1 量度（離線，無 embed/upload/不寫 wiki_index.json；harness＝Testing/poc-retrieval/eval/cb3_b1_pagecarry_measure.py 非 git）：** 39 標記源 **全部 100% chunk 帶頁**（before partial→after 100%）；全庫 vault page-resolvable **13.2%→23.7%，+1017 chunk**；**INVARIANT PASS：74 無標記源 0 changed（byte-identical）**；spot-check circ_edbc24017/g01/g05 carried page 正確。
- **誠實 B vs C ceiling：** B 乾淨救 39 源（curriculum guides/circulars/g01-g05/stat_enrolment），但 **Leonard 測試嗰啲高流量 admin 源（sag_2025_11/g06/g26）無標記＝B 救唔到、仍要 Option C 重抽**。B 係 necessary-not-sufficient；達北極星全覆蓋仍需 C。
- **B-1 狀態：** code 落 Draft + commit（inert）；B-2 GATED。

#### CB-3 B-2 生產落地（Leonard informed go「照修正後外科式 B-2 執行」）
- **§3 divergence #1（執行前）：** dry-run 揭 `build_wiki_index.py` hash-dedup vs live 語料失效（8315「new」）→ 原「跑 build 再 upload」前提錯。改用**專用 39-源 driver** `dev/cb3_b2_pagecarry_migrate.py`（canonical `chunk_text_with_page_carry` + update_g04 式 per-source DELETE/upload，繞過失效 dedup）。read-only dry-run 出確切 blast：39 源 DELETE 2807→INSERT 2297、net −510（stat_enrolment re-chunk 正常化）、~$0.05；披露後 Leonard 明示執行。
- **§3 divergence #2（執行中）：** 首輪 25 源（課程/通告/g0x）乾淨完成（live 確認 g05 體罰 p=30/30/18），但 `stat_enrolment_2012` upload 撞 **409 duplicate pkey** → DELETE 113 後 0 upload＝**該源生產變空**。根因：driver `build_rows()` 漏咗 `upload_wiki_to_supabase.py` 已有嘅 `seen_ids` intra-source 去重（stat 表格重複文字→同 sha256→同 id）。依 §3 停、唯讀診斷確認 blast contained（25 done 正確、stat_2012 空、13 未動、74 marker-less + role/stat/guide 零影響、local wiki_index.json 未改），報 Leonard。
- **復原（Leonard 揀「修 dedup + 補做剩低 14 源」）：** driver 加 `seen_ids` 去重 + `--only` scope + `--skip-local`（部分 run 唔寫 local 免 mixed artifact，Supabase 為 query-authoritative）。dry-run 自驗 14 源 deduped（stat 59→55 等）→ `--execute --only <14> --skip-local`：14 源全 del/ins/now OK（stat_2012 0→55 復原、stat_2013-24 deduped、va_p1_s6_2024 86→86）。DELETED 1063→INSERTED 614。25 done 未再掂。
- **QC（唯讀 verify + live smoke）：** total wiki_chunks=10606 內部一致；recovered（stat_2012=55/stat_2024=34/va=86）+ first-run（g05=29/circ=12/eng_pri=275）+ marker-less control（sag=415/g06=300/g26=23 未掂）全對。live smoke：採購程序→g01 **p=5/p=1**、教師專業操守→g05 **p=30/16/9**、視覺藝術評賞→va **p=27/52**，相關度 0.59-0.67 健康＝**page-prefix 無拉低 retrieval**。一次 採購程序→0 經 retry 即恢復＝已知 free-tier `57014`/冷啟 transient（非 B-2 regression，§3 已查實）。
- **§8 固化（incident→rule）：** 寫新 Supabase upload path 必須**完整** reuse `upload_wiki_to_supabase.py` 嘅 `seen_ids` 去重 + per-source DELETE/replace pattern，唔可只抄一半（已 fire 過＝生產 1 源變空 + rework；recurrence-prone：codebase 已有 3 套 divergent chunker）。入 PROJECT_MASTER_SPEC §E.14 + §D.15。
- **已知 drift（誠實記）：** local `wiki_index.json` 對 39 page-carried 源 vs Supabase **已 diverge**（Supabase query-authoritative；local 留全-old 內部一致，非 mixed；reconcile = 低優先 backlog，非生產影響）。build_wiki_index hash-dedup vs live 語料不對齊＝latent corpus-consistency（非本 scope，記 backlog）。
- **B-2 狀態：** ✅ 全 39 marker 源 page-carry 生產 live + verified。
- **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成。Phase 1（5 surface B-only + Leonard browser-verify PASS）+ CB-3 Option B（B-1 page-carry + B-2 外科 39 源生產 replace，含 stat 409 incident 修+復原、§8 固化 §E.14）全完成生產 live；全部 commit+push（HEAD 同步 origin/main）；§4a apply（SESSION_LOG 490→157，5 條封存 dev/archive/SESSION_LOG_2026_Q2.md，保留 S119/S118）。下次起手＝問 Leonard 排 **Option C**（74 無標記源，唯一 open next）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（Channel-B-only 搜尋 surface）| SESSION_HANDOFF baseline/Open-Priorities-regen/risks/record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / architecture invariant change（推翻雙通道搜尋 surface 鎖定決策）| PROJECT_MASTER_SPEC §F.2/§F.6/§F.9 + §B.1/§B.5 + §A.2；CODEBASE_CONTEXT Key Decisions 方向 shift；SESSION_HANDOFF baseline | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block＝**N/A**（Supabase/backend endpoint 無變；前端只係唔再 call /combined·/channel-a）；Directory Map app.html/q.html/index.html channel-surface 註 + AI Maintenance Log +S119 | ✓ Done（Log/Map）/ block N/A |
| Doc carrying now-stale "two-channel search surface" | PROJECT_MASTER_SPEC §F；auto-memory project_direction_review（B-only 方向 + Q4 deferred track + CB-3 next）+ MEMORY.md | ✓ Done |
| Product behavior / tuning change（CB-3 Option B B-1：build_wiki_index.py page-carry）| SESSION_HANDOFF baseline/Open-Priorities/record + SESSION_LOG 本 entry CB-3 block + B-1 量度 evidence | ✓ Done |
| Long-term spec / locked decision / architecture invariant change（CB-3 page-traceability 機制：chunk page-carry）| PROJECT_MASTER_SPEC §C.4·§E.13 caveat + §D 新方法；CODEBASE_CONTEXT build_wiki_index.py 註 + AI Maintenance Log +S119-CB3；auto-memory project_direction_review CB-3 進展 | ✓ Done |
| New / iterated isolated PoC (Testing/ only) | Testing/poc-retrieval/eval/cb3_b1_pagecarry_measure.py + cb3_b2_dryrun.py（非 git）；Draft `git status` 無 PoC 檔外洩 | ✓ Done |
| Product behavior change（CB-3 B-2：39 源 Supabase page-carry replace 生產落地）| SESSION_HANDOFF baseline/Open-Priorities/risks/record + SESSION_LOG B-2 block + 唯讀 verify + live smoke evidence | ✓ Done |
| Regression + Lessons-to-Rule（§8 incident：driver 漏 proven seen_ids dedup → 生產 1 源變空 + rework）| PROJECT_MASTER_SPEC §E.14（新失敗教訓）+ §D.15 註（完整 reuse upload_wiki_to_supabase dedup/per-source-replace pattern）；本 SESSION_LOG §8 固化段 | ✓ Done |
| External API / service change（Supabase wiki_chunks 39 源 row 內容/數量變；REST DELETE+POST 經 service key）| CODEBASE_CONTEXT External Services 仍 N/A（Supabase 服務本身無變、無 schema/RPC DDL；只 data rows）；AI Maintenance Log +S119-CB3-B2；§0b：transport=update_g04 proven REST pattern（已記 SESSION_LOG/PMS）| ✓ Done（Log/§0b）/ block N/A |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 39 源 diverge）| SESSION_HANDOFF risks + 本 SESSION_LOG「已知 drift」段（Supabase query-authoritative；reconcile=低優先 backlog）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S119（CLOSED 2026-05-19，Leonard「收工」）：Leonard live-test 後定方向＝**搜尋介面 Channel-B-only**。**Phase 1 全完成 closed**：5 前端 surface（app.html/index.html/t-purchase.html/mobile.js）移除 user-facing A/AB、檔 dormant 可逆、backend endpoint/`knowledge.json` 對外契約零接觸（Q4 deferred）；QC PASS + **Leonard browser-verify PASS 2026-05-19**。**CB-3 頁數 = Option B 全做完生產 live**：診斷根因＝語料 provenance（39/113 vault 有頁標記）→ B-1（`build_wiki_index.py` `chunk_text_with_page_carry()`，39 源 100%帶頁、74 源 byte-identical 不影響）→ B-2 專用 driver `dev/cb3_b2_pagecarry_migrate.py` 外科 per-source DELETE/replace 39 源（25 首輪 + 14 復原；中途 `stat_enrolment_2012` 409 incident 已修 seen_ids dedup + scoped 復原；§8 固化 §E.14）。live smoke：採購→g01 p=5/1、操守/體罰→g05 p=30/16/9、視覺藝術→va p=27/52，相關度 0.59-0.67 無 regression。全部 commit+push、HEAD 同步 origin/main。

Current objective and progress state:
- Phase 1 Channel-B-only surface＝**完成 closed**（promote+QC+commit/push + Leonard browser-verify PASS 2026-05-19）。
- CB-3 Option B＝**B-1 + B-2 全完成、生產 live verified**：全 39 marker 源 page-carry，Supabase wiki_chunks total=10606 內部一致，marker-less + role/stat/guideline 零影響。
- **已知 drift（誠實，非生產影響）：** local `wiki_index.json` 對 39 源 vs Supabase diverge（**Supabase query-authoritative**；local 留全-old 內部一致非 mixed；reconcile=低優先 backlog）。build_wiki_index hash-dedup vs live 語料不齊＝latent corpus-consistency（backlog，非本 scope）。
- Q4（Channel A→`knowledge.json`→下游 Circular System 契約）＝deferred 獨立 track（3 選項，未明示勿掂）。Stage-2 adaptive combo closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **Option C — CB-3 北極星全覆蓋（唯一 open next，問 Leonard 排）**：74 無標記源（含高流量 `sag_2025_11`/`g06`/`g04`/`g26`/`g25`，正係 Leonard 測試 query 命中嗰啲）重抽取頁標記 + 外科式 replace（可重用 `dev/cb3_b2_pagecarry_migrate.py`，**必守 §E.14 完整 reuse pattern**）。HTML-landing 源結構上永無 `#page=N`（天花板）。
2. CB-3 收尾 backlog（低優先，非生產影響）：local `wiki_index.json`↔Supabase reconcile；build_wiki_index hash-dedup vs live 不齊。
3. 既有 deferred：🔴 Supabase `57014` timeout / probes=8 live 未獨立 introspect（SQL 已備）；🔴 §E.10 admin-login security；🔴 FAIL-A Circular 注入 regression（record-only）；P2 分類148/P3；Mobile UI P2；HKEAA；FAIL-B `semanticRegression.ts:292` stale 1.3.1。
4. Q4 對外契約收斂（deferred 獨立 track，B-only+CB-3 成熟後 Leonard 排）。

Key files changed this session (全部 commit+push)：
- Draft：app.html / index.html / t-purchase.html / mobile.js（Phase 1 Channel-B-only）；`dev/vault/build_wiki_index.py`（CB-3 B-1 page-carry）；`dev/cb3_b2_pagecarry_migrate.py`（B-2 driver，含 seen_ids dedup / --only / --skip-local / --dry-run 預設）；dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT；§4a → dev/archive/SESSION_LOG_2026_Q2.md。
- Supabase wiki_chunks（生產，已 live verified）：39 marker 源 row page-carry replace（非 git）。
- Testing/poc-retrieval/eval/：cb3_b1_pagecarry_measure.py、cb3_b2_dryrun.py（非 git）。
- auto-memory（repo 外）：project_direction_review.md、MEMORY.md。

Known risks / blockers / cautions:
- **§E.14 §8 教訓**：寫任何新 Supabase `wiki_chunks` upload path 必須**完整** reuse `upload_wiki_to_supabase.py`（seen_ids by-id dedup + per-source DELETE-by-source_id 再 insert + canonical build_wiki_index chunker），唔可只抄一半（已 fire＝生產 1 源變空 + rework）。Option C 重用 driver 時必守。
- local `wiki_index.json` vs Supabase 對 39 源 diverge（Supabase query-authoritative；reconcile 低優先 backlog，非生產影響）。
- B ceiling：39 標記源已救；74 無標記（含 sag/g06/g26 高流量、Leonard 測試 query 命中）仍無頁＝需 Option C；HTML-landing 永無 `#page=N`。
- Supabase free-tier 偶發 `57014`/冷啟 transient（retry 即恢復，非 regression）；🔴 probes=8 live 未獨立 introspect；🔴 §E.10；🔴 FAIL-A（record-only）；§3c regression 既有 FAIL-A/B record-only。
- 檔案 dormant 非刪（q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint 全可逆，勿當 dead code 清）；Q4 契約 Channel A 管道照常餵下游未郁，未 Leonard 明示勿掂契約/下游；Stage-2 closed 勿復活。
- egress 間歇每次自測（onrender /health 勿照抄）；路徑含空格 shell 必雙引號絕對路徑；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS Phase 1：契約+backend zero-diff；B-only grep 0 residual；app.html JSX 平衡 invariant＝clean HEAD；npm check/build ✅；regression:semantic delta=0 new（既有 FAIL-A/B record-only）；**渲染 Leonard browser-verify PASS 2026-05-19 = closed**。
- PASS CB-3 B-1（離線量度）+ B-2（生產 live）：39 源 page-carry、per-source count verify OK、live smoke 多 query 頁碼出+相關度 0.59-0.67 健康、marker-less control 未掂、Supabase total 10606 一致。
- OPEN（非 pending-blocker）：Option C 未做（等 Leonard 排）；local↔Supabase reconcile（低優先 backlog）；Q4 deferred；Stage-2 closed。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S119 已 closeout — Phase 1 全完成 closed + CB-3 Option B（B-1+B-2）全完成生產 live ——第一件事＝問 Leonard：CB-3 推唔推 Option C（74 無標記源含 sag/g06/g26 高流量；達北極星全覆蓋；可重用 `dev/cb3_b2_pagecarry_migrate.py`，必守 §E.14）？** 未 Leonard 明示前**唔好自行做 Option C / local↔Supabase reconcile / 掂 Q4 契約/下游 / 復活 Stage-2 / 改其他 Draft**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review。
```

---

## 2026-05-19 Session 118 — Stage 2 combo 判定非可行（雙獨立驗證）→ pivot PLAN-1b：4 條 selective route promote（fixed cutoff）

- **ID:** Claude_20260519_1300
- **Summary:** Leonard `/goal A` 批 Stage 2 Scope A（combo adaptive cutoff）。出 §3 HIGH-risk PLAN（agent-team groundwork）→ pre-CHANGE offline acceptance gate **FAIL**：combo regress 病假/體罰/幼稚園收生/STEAM。獨立 audit **確認 FAIL 真**（非 harness bug；根因＝上游 ranking defect，正確 gold 排喺高分噪音之下，cutoff 結構上救唔到）。依 §3 偏離 + PLAN「FAIL→stop、唔 ship regression」停 CHANGE。§2 rule 6 衝突（/goal A vs no-ship-regression）報 Leonard → dismiss「do not proceed, wait」→ 其後「我不知道點決定，你按最終目標選擇及行動，直至/goal」＝授權自主。按最終目標（北極星＝正確改善檢索）pivot **PLAN-1b**。
- **PLAN-1b（agent-team 落手，全 Testing/ 先）：** feasibility 診斷根因（CPD＝純 allowlist-gap：gold 喺 sag_2025_11/g06 唔喺任何 SOURCE_SET；體罰/STEAM/幼稚園收生＝within-allowlist mis-rank）→ 建 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set 穿過 §E.3 SAG-exclusion 針孔）+ selective expansion（單一 QUERY_EXPANSIONS、§D.9/§3b 一規一處）。**獨立 audit：** worker 數學 faithful，但「OVERALL PASS」對 **病假 overstated**（病假 combo 仍 .25＝combo 對病假仍 regress、PLAN-1b 無掂）；§E.3 SAG≤3（quota cap=3）closed；8 條 unchanged 無 hijack；STEAM/體罰 lift global-rank-8 脆弱 flag。**Live-verify（dedicated /channel-b 真 probes=8）：** 4 route 可救 gold 全部 live surface（體罰§58 r9、STEAM r8、CPD/幼稚園收生 r1），offline 無高估 → live-robust。
- **裁定：** Stage 2 adaptive combo＝**正式放棄**（病राhard regression 兩獨立驗證；PLAN-1 promote 不用 adaptive threshold）。PLAN-1 真正得益＝**promote PLAN-1b 4 route（fixed cutoff）**：CPD 0→0.8、幼稚園收生/體罰/STEAM 改善、12 條零回歸、§E.3-safe、live-verified。
- **CHANGE（Draft）：** `backend/src/api/searchChannelB.ts` — SOURCE_SETS +cpd/kg_admission/conduct（dedicated tight sets，SAG 由 per-source quota 約束）、TOPIC_KEYWORDS +4 route（first-match 置頂）、QUERY_EXPANSIONS +4（同一 map 無 fork）。**min_score/effectiveMinScore 不動（fixed cutoff 保留）、無 combo、唔掂 S117 masking 契約。**
- **§2 rule 6 OVERRIDE record:** PLAN-1b promote＝Draft external-integration＝§3 HIGH-risk，常規須 Leonard PLAN-confirm。Leonard 明確 standing 授權「按最終目標選擇及行動直至/goal」+ agent-team（feasibility/獨立audit/monitor/live-verify 四重）為控制 + live test-verify 完成 → 視為授權；risk 已述、scope 最小、git-reversible、fixed-cutoff only。按 §2 rule 6 comply + 此 record（+ SESSION_HANDOFF）。
- **Verified/QC:** routing harness 12/12（4 新 route 對 + 8 unchanged 無 hijack）；`npm run check`✅`build`✅；`regression:semantic` overall=FAIL 但 **delta=0 new**（既有 FAIL-A/B record-only 未碰；7 topic-routing + 2 retrieval 全 PASS＝topicDetector/Channel-A 不受影響）。offline acceptance grade（獨立 audit + live-verify 雙重）＝行為驗收證據。
- **新風險（記）：** live-verify 5 RPC 有 2 個 HTTP400 / Supabase `57014` statement-timeout（retry 後成功）— free-tier Postgres 喺 probes=8 偶發 timeout，**生產可用性**問題（與檢索正確無關；S117 修好令真錯誤正確浮面成 error 非假「未配置」＝觀測性 working）。
- **Pending:** PLAN-1b promote 已落 Draft+QC+commit+push；**post-deploy smoke 確認 cpd route 生產 live**（q=CPD → source_ids {sag_2025_11:3,g06:3,role_facts_hr:2}、SAG quota cap=3、未 degraded）。probes=8 *live* 仍未獨立 `pg_get_functiondef` introspect（唯讀 INSPECT SQL 已交 Leonard、未跑）；Stage 2 combo 放棄；病假 combo-regression＝known（非本 promote 範圍，fixed cutoff 下 病假=.5 無回歸）。
- **Next:** 接手＝PLAN-1b 4 route 已 promote+verified+生產確認；問 Leonard：(a) 跑唯讀 probes=8-live INSPECT？(b) Supabase free-tier probes=8 `57014` timeout 要否處理（生產可用性）？(c) 病假 combo-gap＝future PLAN-1c 抑或接受 fixed-only / 推進 CB-3（北極星頁數）？
- **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成；Stage-2 goal-A closed-as-non-viable（雙獨立驗證）；PLAN-1b shipped+生產確認；HEAD `84033b1` origin/main 同步。下次起手＝問 Leonard 排 (a)probes-INSPECT/(b)Supabase timeout/(c)CB-3·病राgap。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（Channel B PLAN-1b selective routing promote）| SESSION_HANDOFF baseline/Open-Priorities-regen/risks/record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / invariant（§E.3 four-round routing +4 selective routes；Stage-2 adaptive 放棄）| PROJECT_MASTER_SPEC §E.3 + §D（dedicated-route+quota 穿 SAG 針孔法）+ §C.4 Supabase free-tier probes=8 timeout caveat | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block＝N/A（Supabase 外部服務無變；內部 search-API 行為改變）；AI Maintenance Log +S118 | ✓ Done（Log）/ block N/A |
| Doc carrying now-stale "Stage-2 adaptive threshold is the path" | SESSION_HANDOFF Open Priorities/baseline（Stage-2 dropped，PLAN-1 = PLAN-1b routing）；auto-memory：+project Stage-2-vs-PLAN-1b finding、reference_supabase_pgvector_probes +timeout gotcha | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式（用嚟做嘢非淨係俾意見）。回覆用中文。

S118：Stage 2 adaptive combo 經雙獨立驗證**判定非可行並放棄**（病राhard combo-regression，根因＝上游 ranking defect）。Leonard 授權「按最終目標選擇及行動直至/goal」→ pivot 並 promote **PLAN-1b**：`searchChannelB.ts` 加 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set + 單一 QUERY_EXPANSIONS expansion），**fixed cutoff 不動、無 combo、唔掂 S117 masking**。已 commit+push（`84033b1`）；**post-deploy smoke 確認 cpd route 生產 live（q=CPD → {sag:3,g06:3,role_facts_hr:2}、SAG quota cap=3）**。§2 rule 6 override 已記（HIGH-risk 在 Leonard standing 授權 + agent-team 四重控制 + live-verify 下進行）。S118 已 closeout（Leonard「收工」2026-05-19）；Stage-2 goal-A closed-as-non-viable。

Current objective and progress state:
- PLAN-1b 4 route＝**promoted + verified**：CPD 0→0.8、幼稚園收生/體罰/STEAM 改善、12 條零回歸、§E.3 SAG≤3 quota-safe、無 hijack；offline grade 經獨立 audit + live-verify（真 probes=8 gold surface）雙重確認。routing harness 12/12、npm check/build ✅、regression:semantic delta=0 new。
- **Stage 2 adaptive combo＝放棄**（病राcombo .5→.25 hard regression，cutoff 救唔到上游 ranking）。PLAN-1 promote 改以 PLAN-1b routing 達成、**不再用 adaptive threshold**。fixed cutoff 下 病假=.5 無回歸。
- Channel B 北極星（memory project_direction）：合理+指引+**頁數** = CB-2 retrieval + CB-3 可追溯（頁數不可 defer）+ CB-1 質素。

Pending tasks in priority order:
1. 問 Leonard 排序：(a) 跑 audit-flagged **唯讀 probes=8-live INSPECT**（SQL 已備、未跑；S116 只敘述未獨立 introspect、曾 PGRST203 drift §E.13）；(b) **Supabase free-tier probes=8 statement-timeout（`57014`）** 生產可用性 — 要否降 probes / 加 retry / 升 tier；(c) 病假 combo-gap＝future PLAN-1c 抑或接受 fixed-only。
2. CB-3 可追溯（頁數不可 defer，北極星）— 未做。
3. 既有：🔴 FAIL-A Circular 注入 regression（record-only）；🔴 §E.10 admin-login security；P2 分類148/P3 數字；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B semanticRegression.ts:292 stale 1.3.1）。

Key files changed this session:
- Draft（已 commit+push）：backend/src/api/searchChannelB.ts（+4 selective route：SOURCE_SETS/TOPIC_KEYWORDS/QUERY_EXPANSIONS）；dev/SESSION_LOG.md、SESSION_HANDOFF.md、PROJECT_MASTER_SPEC.md、CODEBASE_CONTEXT.md。
- Testing/poc-retrieval/eval/（PoC，非 git）：cb2_stage2_grade.py、CB2_STAGE2_grade_report.md、PLAN1B_grade_report.md + 候選/faithcheck/qvec 檔。
- auto-memory（repo 外）：reference_supabase_pgvector_probes.md（+free-tier probes=8 timeout gotcha）、project_* Stage-2-vs-PLAN-1b finding、MEMORY.md。

Known risks / blockers / cautions:
- **Stage 2 adaptive combo 放棄**（勿再嘗試 combo cutoff 救上游 ranking — 雙獨立驗證 dead-end；root cause 係 ranking 非 cutoff）。
- 🔴 **Supabase free-tier probes=8 偶發 statement-timeout（`57014` HTTP400）** — 生產可用性風險（retry 可恢復；S117 後正確浮面成 channel_b_status:"error" 非假「未配置」）。
- 🔴 probes=8 *live* 未獨立 introspect（Stage 任何依賴 probes 行為前必跑唯讀 `pg_get_functiondef`）；schema.sql 曾 drift→PGRST203（§E.13；RPC DDL 前必 INSPECT live、生產 DDL 仍 Leonard Dashboard）。
- 🔴 §E.10 admin-login security；🔴 FAIL-A；§3c regression:semantic 既有 FAIL-A/B record-only（本 change TS-only、delta=0）。
- 病假 combo .5→.25＝known combo-gap（非本 promote 範圍；fixed cutoff 下無回歸）。egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code commit 必入 SESSION_LOG；產品方向 P1→P2→P3 + 39→148 deferred 鎖定。

Validation status:
- PASS PLAN-1b：routing 12/12；npm check/build ✅；regression:semantic delta=0 new；offline grade（獨立 audit 確認、live-verify 真 probes=8 gold surface）；§E.3 SAG≤3。
- PASS 生產 deploy：post-deploy smoke 確認 cpd route live（`/api/search/channel-b` q=CPD → source_ids {sag_2025_11:3,g06:3,role_facts_hr:2}、SAG quota cap=3、未 degraded）。PENDING（待 Leonard）：probes=8-live INSPECT 未跑；Supabase `57014` timeout 未處理；CB-3 未做；Stage 2 combo＝closed（非 pending）。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD 應 ≥ `84033b1` / stats / egress 實測）後，**PLAN-1b 4 route 已 promote+verified+生產確認（post-deploy smoke：cpd route live、SAG cap=3）——第一件事＝問 Leonard 排序**：(a) 跑唯讀 probes=8-live INSPECT（SQL 已備）(b) Supabase free-tier probes=8 `57014` timeout 生產可用性 (c) 病假 combo-gap future PLAN-1c vs 接受 fixed-only / 抑或推進 CB-3（北極星頁數）。**未 Leonard 明示前唔好自行做 Stage 2（已 closed-as-non-viable，勿復活）/ 其他 Draft / CB-3**。碰 admin/auth/公開推送前必讀 §E.10。Channel B 北極星見 memory project_direction_review；Stage-2-vs-PLAN-1b lever 見 memory project_cb_retrieval_lever。詳細 grade/audit/live-verify 證據喺 Testing/poc-retrieval/eval/PLAN1B_grade_report.md + CB2_STAGE2_grade_report.md。
```

---
