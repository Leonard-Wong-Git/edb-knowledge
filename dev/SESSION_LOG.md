# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-27 Session 129 — batch-7 content refresh: 3 PDF marker-bearing re-page-carry (S128 EDB content drift follow-up; driver 8th-validation)

- **ID:** Claude_20260527_0720（同 S127/S128 連續執行）
- **Trigger:** S128 follow-up trio (b) freshness persist 揭 14 sources EDB-content-updated；Leonard 揀 (a) future content refresh batch → Claude 分類為 A (3 PDF marker-bearing HIGH ROI) / B (4 stat xlsx MEDIUM) / C (5 HTML LOW)、推薦 Scope A → Leonard 「按建議做」→ dry-run 揭 music/va chars -35~39% → Leonard「Proceed Gate 1 全 3 sources (推薦)」。
- **§3 HIGH-risk PLAN**: (a) ≥3 files + (d) Supabase mutation + (c) irreversible；既 driver 7 輪 0 incident、信 Hybrid-pattern reuse 直入。

- **CHANGE step 0 — `dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT +2 entries each (music_p1_s6_2024 + va_p1_s6_2024)；arts_kla_guide_2017 既有 batch-4 entries reuse。**

- **Gate 1 `repage_pdfs.py --only arts_kla_guide_2017,music_p1_s6_2024,va_p1_s6_2024 --write` 3/3 PASS：**
  - arts_kla_guide_2017: 5.51MB EDB → 106 pages / 106 markers / 67,587 chars (legacy 0 file = batch-4 已 move)
  - music_p1_s6_2024: 4.39MB EDB → 65 pages / 65 markers / **50,001 chars (legacy 82,339 -39%)** = 對應 EDB live Content-Length -845KB 縮短
  - va_p1_s6_2024: 6.63MB EDB → 53 pages / 53 markers / **40,499 chars (legacy 62,225 -35%)** = chars 大幅縮短
  - markers==pages 全對 (106/65/53)；§5.a-compliant backup `dev/init_backup/20260527_141140_UTC/cb3c_pilot_legacy/music_p1_s6_2024 + va_p1_s6_2024`（arts 無 legacy 因為 batch-4 已 move）。

- **Gate 2 `cb3_b2_pagecarry_migrate.py --only ... --execute --skip-local` 3/3 OK：**
  - dry-run prediction：arts del 116 ins 116 net **0** / music del 108 ins 85 net **-23** / va del 86 ins 71 net **-15** / total **DELETE 310 / INSERT 272 / net -38**。無 anomaly（無 +>50% 大 recovery、無 outlier）；chunks 全 -ve direction 對應 EDB content contraction (chars -35~39%) 合理。
  - EXECUTE：Phase 1b embed all 272 chunks first → wiki_index.json auto-backup `dev/init_backup/20260527_141248_UTC/` → per-source DELETE→upload→count verify 3/3 `del=/ins=/now=` 全對齊 → Phase 3 SKIPPED `--skip-local` (§E.14 紀律)。

- **QC post-execute 4 gates PASS：**
  - **Supabase total via Range header = 9,882** exact match prediction (9,920 - 38) ✅
  - Per-source counts via REST: arts 116 / music 85 / va 71 — match driver report ✅
  - **INVARIANT 5 spot-check** 0 touched non-target sources: g01=32 / sag_2025_11=383 / chem_sss_2007_2018=172 / eng_lit_guide_2023=633 / music_sss_2024=69 全 unchanged ✅
  - backend `/health` cache_a warm 455 facts ✅

- **Live smoke 2/3 surface direct with NEW page numbers + 1 ranking competition non-regression：**
  - ✅ music_p1_s6_2024 q=「音樂科 課程指引 中小學」**TOP-1+2 p=11 / p=16 score 0.704 / 0.701** — new content (post-S129 EDB refresh + new chunker output) live verified
  - ✅ va_p1_s6_2024 q=「視覺藝術 課程指引」**TOP-1+2 p=17 / p=11 score 0.727 / 0.723** — new content live verified
  - ⚠️ arts_kla_guide_2017 q=「藝術教育 學習領域 課程指引」0 hits = ranking competition non-regression（116 chunks live indexed confirmed via Supabase count；chars unchanged 67,587 等量 chunking；S122 tech_kla/ls_jss/chi_hist + S123 music_sss_2024 + S125 econ_sss_supp_2025 同 ranking-competition pattern；非 regression、batch ranking polish backlog 對應）。

- **§E.14 §8 lesson 8th-validation across 55 sources S122-S129 0 incident**: pipeline production-ready confirmed 再印證；music/va chars -35~39% 大幅縮短亦零 incident（driver canonical chunker + seen_ids + per-source DELETE/replace + `--skip-local` 紀律守得住）。

- **§G.2 cross-ref 第四次 ops 應用 (record-only)**: S128 sanity check finding 估「freshness baseline 是 stale not EDB drift、music/va vault content 對齊 EDB live」係 verified；但 S129 dry-run 再揭 music/va chars 大幅縮短 = EDB **新版** PDF 內容 condensed (vault stale + EDB content drift 同時存在)；S128 root-cause estimate 對「size spike 唔涉切換」嘅 verdict 正確、但無覆蓋「EDB live 新版本內容 condensed」呢層 — 多 layer reality 唔可由單一 read-only verify 完全 cover。本記錄 only、不 trigger 新 PMS codification（§G.2 banner 已 cover handoff hypothesis vs verified ground truth）。

- **Sources changed:**
  - Draft committed and pushed `86f8c4f`: `dev/vault/repage_pdfs.py` (PILOT_LEGACY/OUT +2 each) + `dev/vault/arts_kla_guide_2017/extract_arts_kla_guide_2017_repaged.txt` (M) + `dev/vault/music_p1_s6_2024/extract_music_p1_s6_2024.txt` (D) + `dev/vault/music_p1_s6_2024/extract_music_p1_s6_2024_repaged.txt` (new) + `dev/vault/va_p1_s6_2024/extract_va_p1_s6_2024.txt` (D) + `dev/vault/va_p1_s6_2024/extract_va_p1_s6_2024_repaged.txt` (new) — 6 files / +5785 / -5282 lines
  - Draft modified pending commit+push: `dev/SESSION_HANDOFF.md` (Current Baseline + Open Priorities regen + Last Session Record S129 + S128 demote + ✅ S129 完成 annotation) + `dev/SESSION_LOG.md` (本 S129 entry prepend + DOC_SYNC + verbatim handoff) + `dev/CODEBASE_CONTEXT.md` (External Services Supabase row count 9920→9882)。
  - Draft NOT modified this session: `dev/source/source_registry.json` (本 session 唔 touch、S128 (b) 已 update freshness baseline)；PROJECT_MASTER_SPEC (§D.16 batch-1~6 codification 已 cover；S129 內容 refresh 用既有 pipeline、唔 trigger 新 codification)；AGENTS.md / backend / app.html / knowledge.json / guidelines.json。
  - Supabase live: **mutated** 3 sources (arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024) per-source DELETE+INSERT; total 9,920→9,882。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Vault content + Supabase mutation (batch-7 content refresh) | SESSION_LOG S129 entry + SESSION_HANDOFF Current Baseline + Open Priorities regen + Last Session Record + CODEBASE_CONTEXT External Services Supabase row count | ✓ Done |
| repage_pdfs.py PILOT_LEGACY/OUT extension | CODEBASE_CONTEXT Directory Map (既有條目 cover broader scope 擴展點、無新行需加) | N/A (既有條目已說「extend PILOT_LEGACY/PILOT_OUT dict」mechanism、無需逐 batch 加 entry log) |
| Driver 8th-validation across 55 sources | SESSION_LOG S129 § §E.14 lesson note + SESSION_HANDOFF Current Baseline | ✓ Done |
| External Services / Data row change | CODEBASE_CONTEXT Supabase wiki_chunks row count 9,920→9,882 | ✓ Done |
| Tech stack / build / dependency change | N/A (純 ops、無 stack 改) | N/A |
| Governance rule change | N/A (§D.16 既 codified pipeline reused; §G.2 cross-ref record-only) | N/A |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S129 (2026-05-27、Leonard 起手揀 §8b 3-rule → "建議" → S126 trio → "a" content refresh → "Proceed Gate 1 全 3 sources")：**batch-7 content refresh closed**。HEAD origin/main = `86f8c4f` (S129) + governance closeout commit pending。3 PDF marker-bearing 重 page-carry: arts_kla_guide_2017 (106p/116 chunks unchanged) + music_p1_s6_2024 (65p/108→85 chunks -23, EDB live -845KB) + va_p1_s6_2024 (53p/86→71 chunks -15)。Total DELETE 310 / INSERT 272 / net -38 / Supabase **9,920→9,882**。Gate 1 markers==pages 全對 + §5.a-compliant backup + 0 quality regression；Gate 2 per-source `del/ins/now` 全對齊 + INVARIANT 5 spot-check 0 touched。Live smoke 2/3 surface NEW page numbers (music TOP-1+2 p=11/16 0.704; va TOP-1+2 p=17/11 0.727)；arts ranking competition non-regression。**driver `cb3_b2_pagecarry_migrate.py` 8 輪 verified across 55 sources S122-S129 0 incident** = production-ready confirmed。

Current objective and progress state:
- **S129 完成 batch-7 content refresh**：3 PDF marker-bearing re-fetch + re-page-carry + Supabase mutation 0 incident + live smoke 2/3 direct surface。
- **CB-3 達 final ceiling ~88%**（97/113 marker-bearing post-S129 + 2 deprecated + 6 Vanilla preserved + 9 結構天花板）— 北極星目標達成 + content refreshed。
- **driver 8 輪 verified**（55 sources page-carry 0 incident）+ `cb3_deprecate_stale.py` 0 incident。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4 deferred 獨立 track；Stage-2 closed 勿復活。

Pending tasks in priority order:
1. **Optional content refresh remainder (low ROI)**: 4 stat xlsx (stat_kg/pri/sec/special) + 5 HTML (stat_edb_figures / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr) — xlsx 無頁結構天花板、HTML catalogue-level、唔急。
2. **Future batch-7 stale-preserved re-evaluate (optional)**: 6 stale Vanilla-preserved 815 chunks 仲 in index；ranking polish 後 case-by-case re-evaluate；唔急。
3. **🔴 既有 deferred + batch ranking polish backlog**: §E.10 admin-login (OPEN); 57014 transient; FAIL-A record-only; P2/P3; Mobile UI; HKEAA; doc-debt; ranking polish ~15-18 sources (arts_kla_guide_2017 + S122-S125c 累計)。
4. **Q4 對外契約收斂 (deferred)**: Channel A→knowledge.json→Circular System; 未明示勿掂。
5. **§8b rule 2 automation tooling (future)**: KLA-title embedding similarity sub-agent prompt。

Key files changed this session (commit+push origin/main 指定檔)：
- `dev/vault/repage_pdfs.py` — PILOT_LEGACY + PILOT_OUT +2 entries each (music_p1_s6_2024 + va_p1_s6_2024 batch-7 content refresh)
- `dev/vault/arts_kla_guide_2017/extract_arts_kla_guide_2017_repaged.txt` (M, re-fetched + re-paged)
- `dev/vault/music_p1_s6_2024/extract_music_p1_s6_2024.txt` (D legacy) + `extract_music_p1_s6_2024_repaged.txt` (new)
- `dev/vault/va_p1_s6_2024/extract_va_p1_s6_2024.txt` (D legacy) + `extract_va_p1_s6_2024_repaged.txt` (new)
- All 6 vault files committed as `86f8c4f` push origin/main
- `dev/SESSION_HANDOFF.md` (pending commit) — Current Baseline + Open Priorities + Last Session Record S129 + S128 demote
- `dev/SESSION_LOG.md` (pending commit) — S129 entry + DOC_SYNC + verbatim
- `dev/CODEBASE_CONTEXT.md` (pending commit) — Supabase row count 9,920→9,882
- NO modifications: AGENTS.md / PROJECT_MASTER_SPEC / backend / app.html / source_registry.json / knowledge.json / guidelines.json

Known risks / blockers / cautions:
- 本 session 無新增 risk。
- **driver 8 輪 verified 55 sources 0 incident** = pipeline production-ready 再印證；任何新 batch / refresh task 可直接沿用同 pattern。
- **arts_kla_guide_2017 ranking competition** unchanged post-S129 refresh：data live indexed 116 chunks but va_p1_s6 dominate query；ranking polish 屬 broader backlog (S122-S125c 同 pattern)。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S129 batch-7 3 sources Gate 1 + Gate 2 EXECUTE + QC 4 gates + live smoke 2/3 surface direct。
- COMMITTED：S129 vault commit `86f8c4f` push origin/main。
- PENDING：governance docs commit+push 指定 3 檔（SESSION_HANDOFF + SESSION_LOG + CODEBASE_CONTEXT）；Leonard 揀下一步 / 收工。
- OPEN（非 pending-blocker）：optional content refresh remainder / Future batch-7 / 既有 deferred / §8b rule 2 future automation tooling。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD = S129 governance closeout / knowledge.json._meta.stats / Supabase chunk count = 9,882 / egress）後，**S129 batch-7 content refresh 已 closed（3 PDF marker-bearing re-page-carry 0 incident + live smoke direct surface + driver 8 輪 verified）**。第一件事＝問 Leonard 揀：(a) **既有 backlog**（🔴 §E.10 admin-login / batch ranking polish ~15-18 sources / etc）；(b) **Optional content refresh remainder**（4 stat xlsx + 5 HTML、low ROI）；(c) **Future batch-7 stale-preserved re-evaluate**；(d) **§8b rule 2 future automation tooling**；(e) 收工？未 Leonard 明示前**唔好自行 resume / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。
```

## 2026-05-27 Session 128 — S126 follow-up trio closed: g28 URL drift fix + freshness persist write-run + g29/g24 size-spike sanity check

- **ID:** Claude_20260527_0720（同 session 127 連續執行、Leonard 一句「按建議做」trigger trio）
- **Trigger:** S127 governance update closed 後 Leonard 問「建議」→ Claude 推薦先做 S126 follow-up trio 入面 (c) g29/g24 sanity check 揭 high-signal data quality issue → Leonard「按建議做」 = 三 sub-step 連環跑（(c) read-only → (a) g28 url fix → (b) freshness persist write run）。
- **§3 LOW-risk per sub-task**（(c) read-only / (a) single field edit 可逆 / (b) script write-mode 受 S126 threshold gate 保護）。trio 整體 ≤3 files、無 governance rule change、無 Supabase mutation。

- **(c) Read-only sanity check g29/g24 size-spike：** Live HEAD probe via curl + EDB url_primary：
  - **g24** url_primary `sag_c.pdf` HTTP 200 Content-Length 8,380,019 Last-Modified Wed, 20 May 2026 03:07:34 GMT Content-Type application/pdf → 真 PDF body
  - **g29** url_primary `KGECG-TC-2017.pdf` HTTP 200 Content-Length 12,481,467 Last-Modified Wed, 04 Oct 2017 06:58:21 GMT Content-Type application/pdf → 真 2017 KGECG PDF 本身
  - **Verdict**: 非 EDB url_primary 由 landing→PDF 切換、係 **freshness baseline 一直 stale** — baseline 寫 1.3KB/1.5KB Content-Length 應該係前次 fetch 拎到 EDB landing redirect HTML（非 PDF body）造成；g29 baseline Last-Mod 2022-12 反向至 2017-10 = baseline 從前拎錯 landing 嘅 date、PDF 本身真係 2017 原版。**Vault txt content 對齊 EDB live PDF；S125b batch-5 g24 page-carry 既有內容 valid；無需 trigger 重 page-carry**。g24 vs sag_2025_11 = 同一 SAG 文件兩個 PDF variant（clean `sag_c.pdf` vs markup `SAG_C_markup.pdf`） = PMS §E.7 既有 SOURCE_ALIASES 軟 dedup 處理中、unchanged。

- **(a) g28 dead URL fix — §E.12 EDB URL drift pattern apply：**
  - 舊 url（`source_registry.json` g28 entry）：`https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/information-security-in-school.html` HTTP 404
  - Discovery 手法：fetch parent landing `/it-in-edu/index.html` (HTTP 200 78KB) + `grep -oiE 'href="[^"]*[iI]nformation[-]?[sS]ecurity[^"]*"'` 揭 新 url `/it-in-edu/information-security.html` 多次出現
  - 新 url verify：HTTP 200 + Content-Length 96017 + Last-Modified Tue, 28 Apr 2026 10:08:03 GMT + 366KB live body → 正確新位置
  - EDB 改版 pattern：(1) lowercase（`Information-Security` → `information-security`）(2) 拍平 subdirectory（移走中間嘅 `/Information-Security/` 一層、直接放 .html 於 `/it-in-edu/`）。屬 §E.12 codified pattern 第二次 ops 應用（§E.12 講 EDB 一次過打爛 26 條 URL 屬 Session 61，本 g28 係單條 maintenance）。
  - CHANGE：`dev/source/source_registry.json` g28 entry `url_landing` + `url_primary` 同步 update（source_type=index、兩 fields 同值）。git scope = 1 file 2 lines。commit `9122964` push origin/main。

- **(b) freshness persist run — first successful write run since S126 fix：**
  - Command：`python3 dev/source/check_freshness.py`（無 --dry-run、write mode）
  - Result：**Checked 147 / Changes 22 / Errors 0 / Threshold 7 / exit 0** ✅
  - S126 fix end-to-end verified：null-guard `meta = src.get(...) or {}` + threshold gate `max(5, total_checked // 20)` + summary 強化 全部 functional；script 無 crash on freshness_metadata=null entries（pre-S126 fix 喺 entry ~22 即 traceback abort）。
  - 22 sources baseline updated 重要 sample：g28 2173→22310（new url 200 page）+ g24 1525→8380019（PDF body）+ stat_kg/pri/sec/special（Apr 2026 EDB updates）+ arts_kla_guide_2017（Mar 2018→Apr 2026）+ music_p1_s6_2024 / va_p1_s6_2024（Apr 2026 EDB content refresh）+ moral_civic_curr / ph_pri_curr / edbc197_2024_ph_pri / arts_curr_docs / stat_edb_figures。
  - commit `9f5c514` push origin/main；diff +228/-216 lines（4113 行 source_registry.json data file 之中 22 sources × ~20 lines each）。
  - **重要 surfaced 但 deferred**：22 changes 入面 14 sources 反映 EDB live PDF / page 內容已 update（非 baseline metadata stale），若要對齊 vault txt + Supabase chunks 內容 → 屬另一個 batch task（re-fetch + re-extract + page-carry）；非北極星阻塞、唔急、Leonard 排（SESSION_HANDOFF Open Priorities 新 #5 backlog）。

- **§3d test scenario static / coverage：** 本 trio 無預設 §3d matrix（read-only sanity + single-field fix + script run + verify-by-summary）；coverage：(c) live HEAD probe verified 即時、(a) HEAD probe 新 url HTTP 200 verified + freshness persist 再 cross-verify g28 baseline update、(b) exit 0 + 22 changes + 0 errors。

- **§G.2 / §E.12 second-instance evidence：** S128 揭發 (i) §G.2 第三次 ops 應用嘅 corollary：handoff S126 written「root cause = `if errors > 0: sys.exit(1)`」係 partial truth、S128 進一步驗證真根因 = AttributeError + baseline-stale-not-EDB-drift、原 handoff 將「size spike」描述為 「懷疑 url_primary 切換、可能影響 vault PDF extraction」亦係 hypothesis（hypothesis vs verified ground truth）；S128 verified = baseline-stale 而非 切換 而非 vault content stale。(ii) §E.12 EDB URL drift pattern 第二次 ops 應用（Session 61 first event、S128 single-source g28 re-discovery + url repair；codified pattern 直接適用）。本 entry record only、評估後不 trigger 新 PMS §G.2 / §E.12 codification 修改 — 既有條款已 cover。

- **Sources changed:**
  - Draft committed and pushed: `dev/source/source_registry.json`（commit `9122964` g28 url + commit `9f5c514` 22 sources freshness_metadata；二者疊加 230 lines insertions / 218 deletions 對 4113-line data file）。
  - Draft modified pending commit+push: `dev/SESSION_HANDOFF.md`（Open Priorities regen + Last Session Record S128 + S127 demote → Previous + ✅ S128 完成 annotation）+ `dev/SESSION_LOG.md`（本 S128 entry prepend + DOC_SYNC matrix + Next Session Handoff Prompt verbatim）。
  - Draft NOT modified this session: PROJECT_MASTER_SPEC（§E.12/§G.2 已 codified、第二次 ops 應用屬 evidence accumulation 唔 trigger 新 codification）/ CODEBASE_CONTEXT（無 stack/External Services/Key Decisions structural change）/ AGENTS.md / backend / app.html / vault / wiki_index.json / Supabase（無 mutate wiki_chunks）/ knowledge.json / guidelines.json。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| EDB source URL drift fix (§E.12) | SESSION_LOG S128 (a) entry + SESSION_HANDOFF Last Session Record + Open Priorities (S126 follow-up trio remove) | ✓ Done |
| Operational tooling write-mode run (freshness persist) | SESSION_LOG S128 (b) entry + SESSION_HANDOFF Open Priorities #5 future content refresh backlog | ✓ Done |
| Data file change (source_registry.json) | SESSION_LOG S128 (a)+(b) entries 已 record | ✓ Done |
| Sanity-check read-only finding | SESSION_LOG S128 (c) entry + Risks block §E.12 second-instance + §G.2 corollary record-only | ✓ Done |
| Tech stack / External Services / Key Decisions structural change | N/A (本 session 純 data + ops、無 stack 改) | N/A |
| New script / tool documentation | N/A (本 session 用既有 `check_freshness.py`、無新 tool) | N/A |
| Governance rule change | N/A (§G.2 / §E.12 second-instance evidence 屬 record-only、唔 trigger 新 codification) | N/A |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S128 (2026-05-27、Leonard 起手揀 §8b 3-rule + governance update → 完成後問「建議」→ 揀「按建議做」trio)：**S126 follow-up trio (a)+(b)+(c) 三 sub-step 連環 closed**。HEAD origin/main = `9f5c514` (b) + governance closeout commit pending。(c) 結論 = 非 EDB drift、係 freshness baseline 一直拎到 landing redirect HTML 而非 PDF body；vault content 對齊 live PDF 無需重 page-carry。(a) g28 dead URL fix = §E.12 EDB URL drift second-instance ops 應用：舊 `it-in-edu/Information-Security/information-security-in-school.html` 404 → 新 `it-in-edu/information-security.html` 200（lowercase + 拍平 subdir）；url_landing + url_primary 兩 fields 同步 update；commit `9122964`。(b) freshness persist write-run = Checked 147 / Changes 22 / Errors 0 / Threshold 7 / exit 0；S126 fix end-to-end verified；22 sources baseline updated 包含 g28+g24+stat_kg/pri/sec/special+arts_kla+music_p1_s6_2024+va_p1_s6_2024 等；commit `9f5c514`；diff +228/-216。**14 sources 內容已 update on EDB live**（vault txt + Supabase chunks 仲未對齊、屬另一 batch task 非北極星阻塞）= SESSION_HANDOFF Open Priorities 新 #5 future content refresh backlog。

Current objective and progress state:
- **S128 完成 S126 follow-up trio**：(c) sanity check verified non-drift / (a) g28 url fix §E.12 second-instance / (b) freshness persist 147/22/0/exit-0 — 全部 3 sub-step closed + 0 incident。
- **CB-3 達 final ceiling ~88%**（S125c closeout 達成）— 北極星目標達成 unchanged。
- **S127 §8b 3-rule + governance doc full update closed**（unchanged）— PROJECT_MASTER_SPEC §D.16/§D.19/§G.2/§G.3 全 codified。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4 deferred 獨立 track；Stage-2 closed 勿復活。

Pending tasks in priority order:
1. **可能 future content refresh**：S128 揭 14 sources 內容已 update on EDB live（stat_kg/pri/sec/special / arts_curr_docs / ph_pri_curr / edbc197 / moral_civic_curr / arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024 / stat_edb_figures 等）；若要對齊 vault txt + Supabase chunks 內容 = 另一個 batch task（re-fetch + re-extract + page-carry）；非北極星阻塞、唔急、Leonard 排。
2. **Future batch-7 (optional)**：6 stale Vanilla-preserved sources case-by-case re-evaluate（va_sss_2015 180 / ethics_relig_sss_2007_2019 166 / music_sss_2015 161 / econ_sss_2007_2015 147 / econ_sss_supp_2015 39 / bafs_sss_2007_2015 122 = 815 chunks 仲 in index）；ranking polish 後仍構成顯著競爭可考慮再 Hybrid deprecate；唔急。
3. **🔴 既有 deferred + batch ranking polish backlog**：§E.10 admin-login client-side gate（OPEN）；57014 transient（retry 即恢復）；FAIL-A 注入 regression（record-only）；P2/P3（39→148 deferred）；Mobile UI P2；HKEAA；doc-debt；batch ranking polish ~15-17 sources（S122-S125c 累計）。
4. **Q4 對外契約收斂（deferred）**：Channel A→knowledge.json→Circular System；3 選項；未明示勿掂。
5. **§8b rule 2 automation tooling（future implementation）**：semantic-supersede detection 嘅 KLA-title embedding similarity check 暫 process-level apply。

Key files changed this session (commit+push origin/main 已指定檔)：
- `dev/source/source_registry.json` — commit `9122964` g28 url_landing + url_primary fix (2 lines) + commit `9f5c514` 22 sources freshness_metadata baseline updates (+228/-216 lines)
- `dev/SESSION_HANDOFF.md` — Open Priorities regen + Last Session Record S128 + S127 demote + ✅ S128 完成 annotation (pending commit+push)
- `dev/SESSION_LOG.md` — S128 entry prepend + DOC_SYNC matrix + Next Session Handoff Prompt verbatim (pending commit+push)
- NO modifications: PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / AGENTS.md / backend / app.html / vault / wiki_index.json / Supabase / knowledge.json / guidelines.json

Known risks / blockers / cautions:
- 本 session 無新增 risk。
- **§E.12 EDB URL drift second-instance ops 應用** record-only：weekly cron freshness check 會持續 surface 任何新 dead URL；下次 cron run（Monday 09 UTC）會 reflect 本次 fix。
- **14 sources EDB content updated** but vault + Supabase 仲未對齊（baseline metadata 已 sync 但內容未 re-extract）— 屬 future batch；retrieval 可能略 stale 但唔影響北極星 page-traceability。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S128 trio 三 sub-step：(c) live HEAD probe verified / (a) HEAD probe 新 url 200 + freshness baseline update confirms / (b) Checked 147 / Changes 22 / Errors 0 / Threshold 7 / exit 0。
- COMMITTED：S128 (a) `9122964` + S128 (b) `9f5c514` push origin/main。
- PENDING：governance docs commit+push 指定 2 檔（SESSION_HANDOFF + SESSION_LOG）；Leonard 揀下一步 / 收工。
- OPEN（非 pending-blocker）：14 sources future content refresh batch / Future batch-7 / 既有 deferred / §8b rule 2 future automation tooling。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD = S128 governance closeout / knowledge.json._meta.stats / Supabase chunk count = 9,920 / egress）後，**S128 S126 follow-up trio 已 closed（三 sub-step 全完成 + 0 incident + g28 url repaired + freshness baseline 正確 + sanity check 揭真根因）**。第一件事＝問 Leonard 揀：(a) **14 sources future content refresh batch**（vault txt re-extract + Supabase page-carry 對齊新 EDB 內容）；(b) **Future batch-7** 6 stale Vanilla-preserved case-by-case re-evaluate；(c) **既有 backlog**（🔴 §E.10 admin-login / batch ranking polish / etc）；(d) **§8b rule 2 future automation tooling**（KLA-title embedding similarity sub-agent prompt）？未 Leonard 明示前**唔好自行 resume / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。
```

## 2026-05-27 Session 127 — §8b 3-rule promotion + PROJECT_MASTER_SPEC governance doc full update（pure governance / 0 code-data-Supabase mutation）

- **ID:** Claude_20260527_0720
- **Trigger:** Leonard 起手揀 "§8b 3-rule + governance update" chip（4-option AskUserQuestion）；S125 closeout 兩條 §8b lesson promote-candidate + S126 §G.2 第三度 ops 應用 promote-candidate 累計到 governance update threshold；Leonard scope sub-confirm「Promote (推薦)」rule 3 全部 codify。
- **§1 startup verify PASS：** HEAD `0b5ecc4` (S126 closeout commit) origin/main working tree clean / knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` 對齊 baseline / Supabase 9,920 採信 S125c verified state（無 service_role key 獨立 introspect、§D.18 ritual 留必要時用）/ egress `/health` HTTP 200 (warm 4.2s after 30s cold-start retry, `cache_a.warm=true size=455`)。注：handoff Prompt 寫「S126 commit pending」係 stale；實際 commit chain `393afca` (S126 fix) + `0b5ecc4` (S126 closeout) 已 push。

- **§3 HIGH-risk PLAN：** 4-file scope（PROJECT_MASTER_SPEC.md + CODEBASE_CONTEXT.md + SESSION_HANDOFF.md + SESSION_LOG.md）+ 7 §3d scenario matrix（Normal #1-4 grep-verifiable rule presence assertions + Regression A-C scope discipline guards）；HIGH-risk per §3 (a) ≥3 檔 + (e) 改 governance rules；Leonard AskUserQuestion 4-option confirm「§8b 3-rule + governance update」+ scope sub-confirm 4-option「Promote (推薦)」rule 3。

- **3 條 §8b lessons codified（4/6 §8b criteria met for each）：**
  - **Rule 1 — Audit cross-check stale-superseded**（S125b first live applied / S125c Hybrid deprecation verified）：Pre-flight audit sub-agent 必 cross-check index 既有 stale-superseded 版本（唔淨止 batch 自己 chain）；cross-check 法 = `source_registry.json` `supersedes` field + audit-tool 對既有 index 順 `source_id` 掃 stale 同舊 family。S123 + S125b 累計揭發 8 stale sources（1,010 chunks）：va_sss_2015 180 / ethics_relig_sss_2007_2019 166 / music_sss_2015 161 / econ_sss_2007_2015 147 / econ_sss_supp_2015 39 / bafs_sss_2007_2015 122 / pe_sss_2007_2015 119 / sci_jss_supp_2017 76。S125 live miss case = econ_sss_supp_2025 撞 econ_sss_supp_2015 superseded-still-in-index。Codified at PROJECT_MASTER_SPEC §D.16 結尾。
  - **Rule 2 — Semantic-supersede detection**（S125b 揭、3 度 pattern recurrence、S127 promote）：即使 registry `supersedes=[]` 都當潛在 supersede chain。Cases：(a) g24 vs sag_2025_11 same-domain elder-vs-newer consolidated S125b / (b) tech_kla_guide_2017 vs pri_curr_guide_2024 同 KLA scope shift S122 / (c) music_sss_2024 vs music_p1_s6_2024 cross-level domain coverage S123 — 三度同 KLA + same naming pattern + title overlap 都唔在 registry `supersedes` field 顯示。Audit sub-agent 加 (a) KLA-title embedding similarity ≥0.85 check + (b) same-prefix/naming-pattern detector + (c) human verify before deprecate。Automated tooling 留 future implementation、本 rule 即時 process-level apply（每 batch audit sub-agent 必 raise candidate pair）。Codified at PROJECT_MASTER_SPEC §D.16 結尾。
  - **Rule 3 — Handoff root-cause estimate ≠ verified ground truth**（S121 / S122 / S126 三度 cross-session recurrence、S127 promote）：triage agent 必先 run + 觀察 actual failure trace（traceback / log / live state）、再 verify hypothesis 對唔對；唔對即更新 root-cause 再 CHANGE。Cases：(a) S121 `schema.sql` 自稱 vector(1536) 簽名 vs live 真實 text 簽名 → 套 schema.sql 落 live → PGRST203 live 事故 §E.13 / (b) S122 commit `fd22e0a` message + SESSION_LOG 講「pending 5min URL-encoding patch」但 `git diff` 顯示 patch 實已 apply / (c) S126 chronic Freshness fail handoff 估「root cause = `if errors > 0: sys.exit(1)`」實 dry-run 真根因係 `check_freshness.py:101 AttributeError` (line 141-142 唔曾跑到)。Codified at PROJECT_MASTER_SPEC §G.2 banner +4th drift instance + §G.3 NEW #7。

- **CHANGE 4-edit PROJECT_MASTER_SPEC.md（additive，無 retire 舊條款）:**
  - **§D.16 extend**（既有覆蓋 batch-1/2，append batch-3/4/5/6 verified + rule 1 + rule 2 codification）：batch-3 DELETE 942/INSERT 795/net -147 + batch-4 DELETE 537/INSERT 417/net -120 + batch-5 Vanilla DELETE 752/INSERT 736/net -16（g24 +28% 3rd cap-recovery, S122 eng_lit +111% / S123 eng_sss +40% / S125b g24 +28% 三度印證 cap chunker-bound 非 era-dependent）+ batch-6 Hybrid DELETE 206/INSERT 9/net -197（2 page-carry + 2 DROP-only deprecation pe_sss_2007_2015/sci_jss_supp_2017）= **三批一日 Supabase 10,253→9,920 + CB-3 final ceiling ~88%（94/113 marker-bearing + 2 deprecated + 6 Vanilla preserved + 9 結構天花板）達成**。
  - **NEW §D.19** documenting `dev/cb3_deprecate_stale.py`（159 lines / service_role REST DELETE per `source_id` / per-source post-DELETE verify count==0 / Phase backup audit log §5.a-compliant `dev/init_backup/<ts>/cb3_deprecation_log.json` 含 reversibility note：vault legacy & registry 不刪 → rebuild from preserved vault txt → `cb3_b2_pagecarry_migrate.py --only <sid> --execute` 可復原 / `--skip-local` default / `--execute` gate / Python 3.9 PEP 604 compat fix）+ Hybrid decision framework（superseder direct dominance live verify + chunks count 細 ~<150 + audit cross-check confirm + Leonard sign-off = DROP；其餘 = Vanilla preserve §A.2 #1 traceability）。S125c first-use 2 sources 195 chunks 0 incident。
  - **§G.2 banner +4th drift instance**（handoff root-cause estimate ≠ ground truth、S121/S122/S126 三度）+ 教訓 sentence 更新加入「failure root-cause 描述」並列 load-bearing 常數一齊講。Rule 3 codification body 明確列三 case + multi-agent collab prone notice。
  - **§G.3 NEW #7**（接手 issue 嘅 handoff 寫「root cause = X」當 hypothesis、triage agent never skip live-reproduce step、cross-link §G.2 banner 4th 條 + §8b rule 3）。

- **CHANGE CODEBASE_CONTEXT.md**: Directory Map +`dev/cb3_deprecate_stale.py` 行（DROP-only deprecation tool full description）+ existing `cb3_b2_pagecarry_migrate.py` 條目 append「6th-validation across S122-S125c 52 sources 0 incident」+ AI Maintenance Log +S127 entry。

- **CHANGE SESSION_HANDOFF.md**: Open Priorities regen（移除既 #1 §8b 2-rule promotion + #3 governance doc full update 因 S127 已完成 / 保留 S126 follow-up trio 升 #1 / Future batch-7 保 #2 / 既有 deferred + ranking polish 合 #3 / Q4 deferred 保 #4 / 新加 #5 §8b rule 2 future automation tooling）+ Last Session Record S127 + 既 S126 demote → Previous Session Record + `> ✅ S127 完成` annotation prepend before `> ✅ S126 完成`。

- **§3d 7-scenario static verify matrix:**

| # | Scenario | Action | Expected | Actual | Result |
|---|---|---|---|---|---|
| 1 | Normal — rule 1 codified | grep `audit cross-check stale-superseded` in PROJECT_MASTER_SPEC.md | 1+ match | 2+ matches (§D.16 + §8b rule 1 ref) | PASS |
| 2 | Normal — rule 2 codified | grep `semantic-supersede` in PROJECT_MASTER_SPEC.md | 1+ match | 2+ matches (§D.16 rule 2 + §G.2 cross-ref) | PASS |
| 3 | Normal — rule 3 codified | grep `root-cause estimate` 或 `handoff hypothesis` in §G.2 banner | 1+ match | both phrases present (§G.2 4th + §G.3 #7) | PASS |
| 4 | Normal — `cb3_deprecate_stale.py` documented | grep `cb3_deprecate_stale` in PROJECT_MASTER_SPEC.md + CODEBASE_CONTEXT.md | both files | found §D.19 + Directory Map row | PASS |
| 5 | Regression A — §D.16 batch-1/2 既有條款 unchanged | git diff `dev/PROJECT_MASTER_SPEC.md` 看 batch-1/2 內容 byte-stable | additive only | append at 既有條款末尾、batch-1/2 inline text 未郁 | PASS |
| 6 | Regression B — §D / §E / §G 其他條款 byte-stable | git diff scope = 4 edit points only | 0 unrelated touch | §D.1-15 + §E.* + F unchanged confirmed via diff scope | PASS |
| 7 | Regression C — AGENTS.md 唔郁 | `git status AGENTS.md` clean | 0 modification | unchanged confirmed | PASS |

  Overall: **PASS**（純文檔 grep-verifiable）。

- **Sources changed:**
  - Draft modified pending commit+push: `dev/PROJECT_MASTER_SPEC.md`（4 edit points additive、+~150 lines net）/ `dev/CODEBASE_CONTEXT.md`（Directory Map +`cb3_deprecate_stale.py` row + AI Maintenance Log +S127 entry）/ `dev/SESSION_HANDOFF.md`（Open Priorities regen + Last Session Record S127 + S126 demote）/ `dev/SESSION_LOG.md`（本 S127 entry prepend + DOC_SYNC matrix + verbatim handoff prompt）。
  - Draft NOT modified this session: `AGENTS.md` (governance SSOT untouched per §3b 一規一處 / §8b clause 自身唔郁、本 session 純 PROJECT_MASTER_SPEC 層 codify) / `backend/**` / `app.html` / vault / source_registry / knowledge.json / guidelines.json / dev/cb3_deprecate_stale.py（既有 S125c script 維持 byte-identical）。
  - Supabase live: **unchanged** (本 session 純 governance markdown、無 mutate wiki_chunks)。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| §8b rule promotion (3 lessons) | PROJECT_MASTER_SPEC §D.16 + §D.19 NEW + §G.2 banner + §G.3 #7 NEW codify | ✓ Done |
| NEW deprecation script documented | PROJECT_MASTER_SPEC §D.19 + CODEBASE_CONTEXT Directory Map row | ✓ Done |
| §D.16 batch-3/4/5/6 verified codification | PROJECT_MASTER_SPEC §D.16 extend + AI Maintenance Log S127 entry | ✓ Done |
| Governance text edit | SESSION_HANDOFF Open Priorities regen + Last Session Record S127 + S126 demote + SESSION_LOG S127 entry + DOC_SYNC + Next Session Handoff verbatim | ✓ Done |
| External service / data row change | N/A (Supabase / knowledge.json / source_registry 全 byte-unchanged this session) | N/A |
| Tech stack / build / dependency change | N/A (純 markdown、無 dep change) | N/A |
| AGENTS.md §8b clause edit | N/A (governance SSOT 維持；本 session 純 PROJECT_MASTER_SPEC 層 codify、無需 retroactive AGENTS.md edit；若 future 多次 ops 復發再考慮 promote up to §8b clause itself) | N/A (deliberate scope choice) |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S127 (2026-05-27、Leonard 起手揀「§8b 3-rule + governance update」)：**§8b 3 rules promoted + PROJECT_MASTER_SPEC governance doc full update closed**。HEAD = S127 commit pending（下次起手自行 verify origin/main）。3 rules codified at PROJECT_MASTER_SPEC：(1) §D.16 audit cross-check stale-superseded（S125b first applied + S125c Hybrid verified）(2) §D.16 semantic-supersede detection（registry `supersedes=[]` 都當潛在 chain；audit sub-agent 加 KLA-title embedding similarity ≥0.85 + same-naming-pattern detector + human verify；automated tooling future）(3) §G.2 banner 4th + §G.3 #7 handoff root-cause estimate ≠ verified ground truth（S121 schema.sql / S122 commit-msg-vs-diff / S126 handoff hypothesis-vs-script-crash 三度 cross-session recurrence；triage agent 必先 run + 觀察 actual failure trace + verify hypothesis）。Plus §D.16 batch-3/4/5/6 verified state codified + NEW §D.19 documenting `cb3_deprecate_stale.py`（service_role REST DELETE / per-source verify count==0 / Phase backup audit log / Hybrid decision framework / S125c first-use 2 sources 195 chunks 0 incident）。**4-file scope + 0 code/data/Supabase mutation**（PROJECT_MASTER_SPEC + CODEBASE_CONTEXT + SESSION_HANDOFF + SESSION_LOG；AGENTS.md 唔郁）。§3d 7-scenario static verify PASS。

Current objective and progress state:
- **S127 完成 §8b 3-rule + governance doc full update**：4 edit points additive、無 retire 舊條款、§3d 7/7 grep-verifiable static PASS。
- **CB-3 達 final ceiling ~88%**（S125c closeout 達成、94/113 marker-bearing + 2 deprecated + 6 Vanilla preserved + 9 結構天花板）— 北極星目標達成。
- **driver 6 輪 verified（S122~S125c、52 sources page-carry 0 incident）+ NEW `cb3_deprecate_stale.py` first-use 2 sources 195 chunks 0 incident**。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4 deferred 獨立 track；Stage-2 closed 勿復活。

Pending tasks in priority order:
1. **S126 follow-up trio**：(a) g28 dead URL EDB re-discovery (§E.12 pattern 修 url_primary) (b) check_freshness 跑一次唔加 --dry-run persist 20 EDB freshness_metadata updates（4113 行 data file 改、獨立 commit）(c) g29/g24 size-spike content sanity check（懷疑 url_primary landing→PDF、可能影響 vault PDF extraction）。
2. **Future batch-7 (optional)**：6 stale Vanilla-preserved sources case-by-case re-evaluate（va_sss_2015 180 / ethics_relig_sss_2007_2019 166 / music_sss_2015 161 / econ_sss_2007_2015 147 / econ_sss_supp_2015 39 / bafs_sss_2007_2015 122 = 815 chunks 仲 in index）；ranking polish 後仍構成顯著競爭可考慮再 Hybrid deprecate；唔急。
3. **🔴 既有 deferred + batch ranking polish backlog**：§E.10 admin-login client-side gate（OPEN）；57014 transient（retry 即恢復）；FAIL-A 注入 regression（record-only）；P2/P3（39→148 deferred）；Mobile UI P2；HKEAA；doc-debt；batch ranking polish ~15-17 sources（S122-S125c 累計）。
4. **Q4 對外契約收斂（deferred）**：Channel A→knowledge.json→Circular System；3 選項；未明示勿掂。
5. **§8b rule 2 automation tooling（future implementation）**：semantic-supersede detection 嘅 KLA-title embedding similarity check 暫 process-level apply；automated sub-agent prompt 留 future batch / governance session 寫。

Key files changed this session (commit+push origin/main 指定檔)：
- `dev/PROJECT_MASTER_SPEC.md` — §D.16 extend (batch-3/4/5/6 verified + rule 1 + rule 2) + NEW §D.19 cb3_deprecate_stale.py documentation + §G.2 banner +4th drift instance (rule 3) + §G.3 NEW #7
- `dev/CODEBASE_CONTEXT.md` — Directory Map +`cb3_deprecate_stale.py` row + cb3_b2_pagecarry_migrate.py 6th-validation note + AI Maintenance Log +S127 entry
- `dev/SESSION_HANDOFF.md` — Open Priorities regen + Last Session Record S127 + S126 demote → Previous Session Record + `> ✅ S127 完成` annotation prepend
- `dev/SESSION_LOG.md` — S127 entry prepend + DOC_SYNC matrix + Next Session Handoff Prompt verbatim
- NO modifications: AGENTS.md / backend / app.html / vault / source_registry / knowledge.json / guidelines.json / Supabase

Known risks / blockers / cautions:
- 本 session 純 governance markdown 改、0 code/data/Supabase mutation、無新增 risk。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S127 governance update + §3d 7/7 static grep-verifiable + 4 file scope 確認 additive + commit+push pending (指定 4 檔)。
- PENDING：commit+push origin/main 指定 4 檔（PROJECT_MASTER_SPEC + CODEBASE_CONTEXT + SESSION_HANDOFF + SESSION_LOG）；Leonard 揀下一步。
- OPEN（非 pending-blocker）：S126 follow-up trio / Future batch-7 / 既有 deferred / §8b rule 2 future automation tooling。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD = S127 commit / knowledge.json._meta.stats / Supabase chunk count = 9,920 / egress）後，**S127 §8b 3-rule + governance doc full update 已 closed（PROJECT_MASTER_SPEC §D.16/§D.19/§G.2/§G.3 全 codified + CODEBASE_CONTEXT/SESSION_HANDOFF/SESSION_LOG sync + 4 file scope additive + 0 code/data mutation + §3d 7/7 PASS）+ §8b governance backlog clear**。第一件事＝問 Leonard 揀：(a) **S126 follow-up trio**（g28 dead URL + freshness_metadata persist run + g29/g24 size-spike sanity check）；(b) **Future batch-7** 6 stale Vanilla-preserved case-by-case re-evaluate；(c) 抑或 **既有 backlog**（🔴 §E.10 admin-login / batch ranking polish / etc）；(d) 抑或 **§8b rule 2 future automation tooling**（KLA-title embedding similarity sub-agent prompt）？未 Leonard 明示前**唔好自行 resume / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。
```

## 2026-05-26 Session 126 — Freshness workflow chronic-fail triage closed（bug fix + threshold gate；§G.2 verify-don't-trust-docs 第三次 ops 應用）

- **ID:** Claude_20260526_1811
- **Trigger:** S125 closeout 留 Freshness workflow chronic fail（5 連 since 2026-04-30）作 priority #1 backlog；Leonard 起手 4-option AskUserQuestion chip 揀 "Freshness workflow triage"；後續 sub-choices 揀 threshold = `errors > max(5, 5%)` + cron 保 weekly + scope = bug fix + threshold + re-run dry-run（freshness_metadata 唔寫返 registry 本 session）+ g28 dead URL 留 follow-up。
- **§1 startup verify PASS：** HEAD `cf3ea3e` (S125 closeout) origin/main working tree clean / `knowledge.json._meta.stats` `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` 對齊 baseline / Supabase wiki_chunks live total 9,920 exact via Range-header REST / egress `/health` HTTP 200 in 22.4s typical cold start，`cache_a.warm=true size=455`。
- **§3 HIGH-risk PLAN：** scope 5 files / §3d 5-scenario test matrix（Normal / Boundary-low 1-5err / Boundary-high >5err / Regression A dry-run no-write / Regression B filter unchanged）；HIGH-risk per (a) ≥3 files + (b) workflow notification 部份未明；Leonard AskUserQuestion 兩個 sub-question 直接 gate 同 confirm。
- **READ → dry-run v1 揭真根因（§G.2 第三度應用）：** `python3 dev/source/check_freshness.py --dry-run` → entry ~22 撞 **`AttributeError: 'NoneType' object has no attribute 'get'`** at `check_freshness.py:101 old_mod = meta.get("last_modified")`。Root cause = `meta = src.get("freshness_metadata", {})` 對「key 存在但 value=null」嘅 source entry 失效 — dict `.get(key, default)` 嘅 default 只 trigger on **missing key**、非 null value。Pre-crash 處理 ~21 條：1 dead URL g28 + 20 EDB CHANGE detected。**Handoff 估計 `root cause = line 141-142 if errors > 0: sys.exit(1)` 係 partial truth — script 根本未跑到嗰 exit 就 traceback abort、threshold 太嚴只係次要 surface**。§G.2 verify-don't-trust-docs 第三次 ops 應用（S121 schema.sql 自稱 vector 簽名 vs live text 簽名 / S122 commit-msg「pending 5min patch」vs diff 已 apply / S126 handoff root-cause 估計 vs script 真 crash point = 3 度 recurrence-prone）。
- **CHANGE `dev/source/check_freshness.py` 三點 minimal：** (a) **null-guard**: `meta = src.get("freshness_metadata") or {}`（handle explicit null）+ inline 解釋 comment（保留：non-obvious dict-API edge case）(b) **threshold gate**: `threshold = max(5, total_checked // 20)`；新 fail 條件 `if errors > threshold: sys.exit(1)`；within-threshold 印 `⚠️ exit 0 (workflow remains green)` 訊息保 transparency (c) **summary 強化**：印 `Threshold` 行 + 失敗時 list `Failed sources (sid + url)` block + 超 threshold 時印 `🚨 errors > threshold — exiting 1`。Cron 同 workflow yaml 唔改（Leonard 確認 weekly 保留）。Syntax PASS via `python3 -c "import ast; ast.parse(...)"`；git scope = 1 file。
- **QC dry-run v2 + §3d 5-scenario matrix：**

| Scenario | Precondition | Action | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal | All URLs 200 | local dry-run | exit 0、errors=0 | exit 0、errors=1 (g28) ≤ threshold 7 | PASS（變體：boundary-low live-cover normal） |
| Boundary-low | 1-7 err | local dry-run | exit 0 + warn | 1 err → `⚠️ within threshold` + exit 0 | PASS |
| Boundary-high | >7 err | code review (live sim 太貴) | exit 1 + 🚨 msg | `if errors > threshold: sys.exit(1)` + 🚨 print 路徑 correctness 經 inspection | PASS (code-review) |
| Regression A | `--dry-run` flag | local run | source_registry.json byte-unchanged | `git diff --stat dev/source/source_registry.json` empty | PASS |
| Regression B | verified+public+url_primary filter | local run | total_checked 同 logic 一致 | 147（vs Regression Notes #2 stale 145，+2 = vault 自 2026-04-08 加 2 sources、filter logic same） | PASS |

  Overall: **PASS**。完整數字：Checked 147 / Changes 20 / Errors 1 / Threshold 7 / **exit 0**。

- **20 EDB CHANGE detected + 1 dead URL 紀錄非 persist（本 session scope-out per Leonard）：** Changes：sag_2025_11 / g04 / g29 / g31 / g33 / g37 / g38 / g24 / stat_edb_figures / stat_kg / stat_pri / stat_sec / stat_special / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr / arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024。**Anomalies surfaced**：(1) g29 Content-Length 1,299→12,481,467（1.3KB→12MB）+ Last-Modified 反向（2022-12→2017-10）懷疑 url_primary 由 landing→直 PDF 切換 / (2) g24 Content-Length 1,525→8,380,019（1.5KB→8MB）同 pattern / (3) edbc197_2024_ph_pri 新 Len 3,389 與 ph_pri_curr 新 Len 3,389 同數字（可能同 URL 或 redirect 收斂）。Dead URL: **g28** `https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/information-security-in-school.html`（HEAD + GET 均 fail；按 §E.12 EDB URL drift pattern 處理 follow-up）。
- **§G.2 第三次 ops 應用 — §8b promote-candidate：** Recurrence-prone（3 度跨 5 session：S121 / S122 / S126）+ multi-agent collaboration prone（接手 agent 必依賴 handoff 文字描述、唔讀 code）+ long-term drift（doc 文字 vs 真實 code/script crash behaviour）+ 唔可單個 patch 收尾（每次新 drift 都係新 root-cause）= §8b 4/6 criteria met。建議 PROJECT_MASTER_SPEC §G.2 codify：**「root-cause 估計係 handoff hypothesis 非 verified ground truth；triage agent 必先 run + 觀察 actual failure trace，再 verify hypothesis 對唔對」**作 rule clause。本 entry record-only、待下次 governance-update session promote。
- **Sources changed:**
  - Draft modified pending commit+push: `dev/source/check_freshness.py`（null-guard + threshold + summary 強化、+15 lines）+ 2 governance docs (SESSION_HANDOFF + SESSION_LOG)。
  - Draft NOT modified this session: `dev/source/source_registry.json` (byte-unchanged per Regression A) / `.github/workflows/freshness_check.yml` (cron 保留、無 yaml 改) / CODEBASE_CONTEXT (operational tooling change、非 stack/External Services/Key Decisions) / PROJECT_MASTER_SPEC (governance-update 留 batch 性能、§G.2 promote-candidate record-only)。
  - Supabase live: **unchanged** (本 session 純 ops tooling、無 mutate wiki_chunks)。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Operational tooling fix (freshness workflow script bug + threshold) | SESSION_HANDOFF Regression Notes #2 update（stale baseline → S126 verified state）+ Open Priorities regen（remove freshness #1、加 g28 + persist run follow-up）+ Last Session Record S126 + SESSION_LOG 本 entry | ✓ Done |
| §G.2 lesson 累積（3 度 recurrence）promote-candidate | PROJECT_MASTER_SPEC §G.2 codify rule clause | ⚠ Skipped (defer to governance-update session per Open Priorities #3；本 entry record-only) |
| New backlog (g28 dead URL + 20 freshness_metadata persist run + g29/g24 size-spike) | SESSION_HANDOFF Open Priorities #4 + Risks block | ✓ Done |
| External service / data row change | N/A (Supabase / knowledge.json / source_registry 全 byte-unchanged this session) | N/A |
| Tech stack / build / dependency change | N/A (script 自身 stdlib + requests、無 new deps) | N/A |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S126 (2026-05-26、Leonard 起手揀「Freshness workflow triage」)：**`dev/source/check_freshness.py` bug fix + threshold gate；chronic 5 連 fail since 2026-04-30 closed**。HEAD = S126 commit pending（下次起手自行 verify origin/main）。Root cause 揭發 = handoff 估計嘅 `if errors > 0: sys.exit(1)` 係 partial truth — script 喺 line 101 撞 `AttributeError: 'NoneType' object has no attribute 'get'`（`meta = src.get("freshness_metadata", {})` 對 explicit-null value 失效、`.get()` default `{}` 只 trigger on missing key），entry ~22 即 traceback abort、threshold 嗰行根本未跑到。§G.2 verify-don't-trust-docs **第三次 ops 應用**（S121 schema.sql / S122 commit-msg-vs-diff / S126 handoff root-cause estimate = 3 度 recurrence-prone）。CHANGE 3 點：(a) null-guard `meta = src.get(...) or {}` (b) threshold gate `errors > max(5, total_checked // 20)` (c) summary 加 failed-sids list + within-threshold exit-0 warn。Cron 保留 weekly Monday 09 UTC（Leonard 確認）。QC dry-run v2 PASS：**Checked 147 / Changes 20 / Errors 1 (g28) / Threshold 7 / exit 0**；§3d 5/5 PASS（Normal / Boundary-low live-verified / Boundary-high code-review / Regression A `git diff` empty / Regression B filter logic same）。20 EDB CHANGE 包 sag_2025_11/g04/g29/g31/g33/g37/g38/g24/stat_*/arts_*/ph_*/edbc197/moral_civic/music_p1_s6/va_p1_s6 + g28 dead URL（§E.12 follow-up）。**Anomalies pending sanity check**：g29 Len 1.3KB→12MB + g24 Len 1.5KB→8MB（懷疑 url_primary 由 landing→直 PDF 切換、可能影響 vault PDF extraction）；g29 Last-Mod 反向至 2017-10。**Freshness_metadata 20 updates 本 session 唔寫返 registry（Leonard scope decision、保持 --dry-run）**。

Current objective and progress state:
- **S126 完成 Freshness workflow chronic-fail triage**：script bug fix + threshold gate + 5/5 §3d PASS + 真根因 surfaced + §G.2 第三度應用 record（promote-candidate 4/6 §8b criteria met）。
- **CB-3 達 final ceiling ~88%**（S125 closeout 達成、94/113 marker-bearing）— 北極星目標達成。
- **2 §8b promote candidates pending governance codify (S125)**: (1) audit cross-check stale-superseded (live + Hybrid verified) (2) NEW semantic-supersede detection。**S126 新加 candidate**: §G.2 root-cause-estimate-is-not-verified-ground-truth rule。
- **NEW S126 follow-up trio**: (a) g28 dead URL EDB re-discovery (b) check_freshness 跑一次唔加 --dry-run persist 20 freshness_metadata updates (c) g29/g24 size-spike url_primary landing→PDF 切換 sanity check。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4 deferred 獨立 track；Stage-2 closed 勿復活。

Pending tasks in priority order:
1. **§8b 3-rule promotion + PROJECT_MASTER_SPEC governance doc full update**：S125 (1) audit cross-check stale-superseded + (2) NEW semantic-supersede + S126 (3) §G.2 root-cause-estimate-is-not-ground-truth；同時 codify §D.16 batch-4/5/6 verified + NEW `cb3_deprecate_stale.py` documented。建議一次過做 governance update session。
2. **S126 follow-up trio**：(a) g28 dead URL EDB re-discovery (§E.12 pattern 修 url_primary) (b) check_freshness 跑一次唔加 --dry-run persist 20 freshness_metadata updates (4113 行 data file 改、獨立 commit) (c) g29/g24 size-spike content sanity check (懷疑 url_primary landing→PDF、可能影響 vault PDF extraction)。
3. **Future batch-7 (optional)**：6 stale Vanilla-preserved sources case-by-case re-evaluate（va_sss_2015 180 / ethics_relig_sss_2007_2019 166 / music_sss_2015 161 / econ_sss_2007_2015 147 / econ_sss_supp_2015 39 / bafs_sss_2007_2015 122 = 815 chunks 仲 in index）；ranking polish 後仍構成顯著競爭可考慮再 Hybrid deprecate；唔急。
4. **batch ranking polish backlog（低優先）**：S122-S125c 累計 ~15-17 sources ranking competition（去 deprecated 2 後）。
5. **🔴 既有 deferred**：§E.10 admin-login client-side gate（OPEN）；57014 transient（retry 即恢復）；FAIL-A 注入 regression（record-only）；P2/P3（39→148 deferred）；Mobile UI P2；HKEAA；doc-debt。
6. **Q4 對外契約收斂（deferred）**：Channel A→knowledge.json→Circular System；3 選項；未明示勿掂。

Key files changed this session (commit+push origin/main 指定檔)：
- `dev/source/check_freshness.py` — null-guard `src.get(...) or {}` + threshold gate `max(5, total_checked // 20)` + summary 強化 (+15 lines)
- `dev/SESSION_HANDOFF.md` — Regression Notes #2 update / Open Priorities regen / `> ✅ S126 完成` annotation / Last Session Record S126 + S125 demote
- `dev/SESSION_LOG.md` — S126 entry prepend
- NO modifications: source_registry.json (byte-unchanged per Regression A) / freshness_check.yml (cron 保留) / CODEBASE_CONTEXT / PROJECT_MASTER_SPEC / Supabase

Known risks / blockers / cautions:
- **§G.2 verify-don't-trust-docs 第三次 ops 應用 (recurrence-prone)**：handoff root-cause estimate ≠ verified ground truth；triage agent 必先 run + 觀察 actual failure trace、再 verify hypothesis 對唔對；§8b promote-candidate 4/6 criteria met。
- **g29 / g24 size-spike 異常**：懷疑 EDB url_primary 由 landing 改至直 PDF（Len 1.3KB→12MB / 1.5KB→8MB）；vault PDF extraction 可能受影響、要 follow-up sanity check。
- **g28 真係 EDB URL drift**：§E.12 codified pattern 處理；列 follow-up。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S126 freshness fix + 5/5 §3d matrix + dry-run v2 Checked 147 / Changes 20 / Errors 1 / Threshold 7 / exit 0 + commit+push pending (指定 3 檔)。
- PENDING：commit+push origin/main 指定 3 檔（check_freshness.py + SESSION_HANDOFF + SESSION_LOG）；Leonard 揀下一步。
- OPEN（非 pending-blocker）：S125 §8b 2-rule + S126 §G.2 candidate codify / S126 follow-up trio / 既有 deferred。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD = S126 commit / knowledge.json._meta.stats / Supabase chunk count = 9,920 / egress）後，**S126 Freshness workflow chronic-fail triage 已 closed（script bug fix + threshold gate + 5/5 §3d PASS）+ 揭發 §G.2 第三次 ops 應用（promote-candidate）+ S126 follow-up trio 列入 backlog**。第一件事＝問 Leonard 揀：(a) **§8b 3-rule promotion + PROJECT_MASTER_SPEC governance doc full update**（S125 2 lessons + S126 §G.2 一次過做、batch-4/5/6 verified codify + NEW `cb3_deprecate_stale.py` documented + §G.2 rule clause）；(b) **S126 follow-up trio**（g28 dead URL + freshness_metadata persist run + g29/g24 size-spike sanity check）；(c) **Future batch-7** 6 stale Vanilla-preserved case-by-case re-evaluate；(d) 抑或 **既有 backlog**（🔴 §E.10 admin-login / batch ranking polish / etc）？未 Leonard 明示前**唔好自行 resume / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。
```

## 2026-05-26 Session 125 — CB-3 Option C broader batch-4 + batch-5 + batch-6 Hybrid（22 marker-less PDF + 2 deprecation）= 三批一日打完 + Freshness workflow triaged + §8b audit cross-check live-validated + NEW deprecation script `cb3_deprecate_stale.py` + driver 6th-validation

- **ID:** Claude_20260526_0737
- **Trigger:** Leonard 起手揀「Batch-4 執行（推薦）」（chip selection 之 §3 HIGH-risk 明示授權 entry point）；S124 closeout pre-flight 已完成（10/10 GO / 10/10 KEEP），repage_pdfs.py PILOT_LEGACY/PILOT_OUT batch-4 entries 未加。Session 中段 Leonard 貼 GitHub Actions「Weekly Freshness Check workflow run failed」notification — triage 揭發 chronic fail（5 連 since 2026-04-30，非 batch-4 觸發），Leonard 揀 batch-4 Gate 2 EXECUTE 優先、freshness 收尾再處理。
- **§1 startup verify PASS：** HEAD `399de95` working tree clean / knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` 對齊 baseline / Supabase wiki_chunks 10,253 exact / repage_pdfs.py batch-4 entries 0 hit（未加，與 S124 handoff prediction 一致）/ egress `/health` 200 in 22s typical 冷啟。
- **§3 HIGH-risk PLAN 提交 + Leonard「go」：** 6 點 assumptions + 8 scenario §3d test matrix；Leonard 一次 go 授權 Gate 1 + Gate 2 dry-run，Gate 2 EXECUTE 需第二次 go（irreversible）。CHANGE step 0 = `dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT 各 +10 batch-4 entries（純 dict extension，無 logic 改），import verify PILOT_LEGACY/PILOT_OUT size 33→43，10 legacy paths 全 exist。
- **Gate 1 dry-run + EXECUTE 10/10 PASS：** dry-run fetch + PyMuPDF page count = 65/28/19/84/41/13/9/14/106/4 = total 383（pre-flight 預測 390，arts_kla 106 vs 109 + music_anthem 4 vs 8 = EDB content 微更新非異常）。`--write` 10/10 written；markers==pages 全對；content sanity new/legacy 102.5% slight + marker overhead 0 quality regression；backup at `dev/init_backup/20260526_073931_UTC/cb3c_pilot_legacy/` 10 entries（§5.a-compliant gitignored、git check-ignore 確認）；marker spot-check ict_sss_2021/econ_sss_2025/music_national_anthem_2024 first=Page 1 last=Page N 全對齊；git status scope = 1 M repage_pdfs.py + 10 D legacy + 10 ?? repaged，0 其他 vault sources / 其他 Draft 檔 touched（INVARIANT 守）。
- **Mid-session interrupt: Freshness workflow triage（read-only）：** Leonard 貼 GitHub Actions failure notification → triage 揭發 `.github/workflows/freshness_check.yml` `cron "0 9 * * 1"` Weekly Freshness Check 從 2026-04-30 起 5 連 fail（run #6-#10，每週 schedule 觸發）。Root cause = `dev/source/check_freshness.py` line 141-142 `if errors > 0: sys.exit(1)` — 只要 151 sources HEAD probe 任何 1 條 fail 就 exit 1 → GitHub mark FAILED + email。高機率係 EDB 偶發 5xx / URL 改版（PMS §E.12 codified pattern：曾一次打爛 26 URL）+ HEAD 15s timeout。**SESSION_HANDOFF Regression Notes #2「check_freshness.py Errors: 0 / Checked: 145 ✅」係 stale baseline（已 4+ 星期 false-positive，§G.2 verify-don't-trust-docs 又中）。** Artifact freshness-report-10 (1.2KB) 401 需 token 下載；非 batch-4 觸發（Supabase 未 mutate / workflow 只 HEAD probe）。Leonard 揀 batch-4 Gate 2 EXECUTE 優先；freshness 列入下次 session 處理 backlog。
- **Gate 2 dry-run + EXECUTE 10/10 OK：** dry-run no anomaly — 10 sources 全 normalize -14~-32% range（canonical chunker pattern）、無 +>50% recovery cap-hit、無 outlier；Total INSERT 417 DELETE 537 net -120 預估 Supabase 10,253→10,133；embed cost ~$0.004。EXECUTE under Leonard 第二次 go：Phase 1b embed all 417 chunks first → wiki_index.json auto-backup `dev/init_backup/20260526_091916_UTC/` → per-source DELETE→upload→count verify 10/10 `del=/ins=/now=` 全對齊 → Phase 3 SKIPPED `--skip-local`（§E.14 紀律）。
- **QC post-execute（4 gates PASS）：** (1) Supabase total via Range header = **10,133** exact match prediction (10,253 - 537 + 417) (2) INVARIANT 5 spot-check g01=32 / sag_2025_11=383 / chem_sss_2007_2018=172 / eng_lit_guide_2023=633 / music_sss_2024=69 全 unchanged，0 touched (3) backend `/health` ok cache_a cold 可恢復 (4) Gate 1 markers==pages 全對 + raw REST inspect econ_sss_2025 chunk text 含 `=== Page 1 === / === Page 2 ===` markers verified live。
- **Live smoke 4/10 batch-4 sources surface with page numbers + 6/10 ranking competition non-regression：** ⭐ chi_hist_jss_ncs_2019 p=4/5 (0.572/0.569) / geog_sss_supp_2022 p=1 (0.559 TOP-1) / geog_sss_update_brief p=14 (0.546) / econ_sss_2025 p=6/9 (0.543/0.534 via econ_sss_supp_2025 query)。6 non-surface = ranking 競爭非 regression（ict_sss_2021 now=81 1× 57014 transient retry pri_curr_guide 撞 / chi_hist_jss_bilingual_2019 chi_pri/chi_jss_guide_2023 撞 / **econ_sss_supp_2025 撞 econ_sss_supp_2015** = S123 audit miss pattern superseded 版本仍 in index / geog_sss_summary_2022 太 generic ma_kla 撞 / arts_kla_guide_2017 va_p1_s6_2024 dominate / music_national_anthem_2024 music_p1_s6_2024 dominate + 4-page 國歌 brief 短）。Live smoke parser 自身 bug：API response field 係 `page` 非 `page_number`（first-pass 全 `page=-` false alarm，rerun fix）。Supabase `wiki_chunks` 無 `page` column（42703），實際 backend 從 `text` content extract page marker 後組裝 response — infrastructure intact verified。
- **Whole-vault page-resolvable progression：** 13.2% → 23.7% (S119) → 32.2% (S120) → 55.2% (S122) → 64.4% (S123) → 73.0% (S124) → **~76.0% (S125)** = ~7,706 / 10,133 chunks；**82 / 113 vault sources marker-bearing**（39 B + 3 C pilot + 10 batch-1 + 10 batch-2 + 10 batch-3 + 10 batch-4）。Remaining: **21 marker-less PDFs**（batch-5~6）+ 9 結構天花板 → CB-3 final ceiling ≈ 88%。
- **§E.14 §8 教訓 4th-validation：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused = 40 sources end-to-end PASS（S122 batch-1 / S123 batch-2 / S124 batch-3 / S125 batch-4）+ 0 incident。**S125 unique §8b monitoring lesson：S123 superseder audit pattern 需延伸 — pre-flight audit 之前只 check batch-4 自己 chain，未 cross-check 落 index 既有 stale superseded 版本（e.g. econ_sss_supp_2015 在 index 未 retire 同 econ_sss_supp_2025 同 query namespace 競爭、causes batch-4 ranking miss）**。Recurrence-prone (S123/S125 兩度 surface) — 可考慮 §8b promote-to-rule（threshold met：multi-occurrence、recurrence-prone for multi-agent collaboration、非單一 batch fixable），下次 batch-5 audit agent 必須 cross-check index 既有 stale 版本 superseded by batch 候選 sources。
- **Sources changed (batch-4 + governance)：** commit `e703910` origin/main：`dev/vault/repage_pdfs.py`（PILOT_LEGACY/PILOT_OUT +10 batch-4 entries）+ 4 governance docs（SESSION_LOG / SESSION_HANDOFF / CODEBASE_CONTEXT / HANDOFF_PACKAGE）+ 10 vault rename pairs（extract_<sid>.txt → extract_<sid>_repaged.txt）。Supabase live（非 git）：wiki_chunks 10,253→10,133（10 batch-4 sources DELETE 537 INSERT 417）。dev/init_backup/{20260526_073931_UTC,20260526_091916_UTC}/（gitignored）。

#### Follow-up — broader Option C batch-5（10 marker-less PDF）page-carry 生產 live + Vanilla strategy（S125b、同 session）

- **Trigger：** Leonard 揀「Batch-5 pre-flight + execute」+ S125 §8b 新教訓 first live application；Vanilla strategy（推薦首輪、0 deprecation）。Audit cross-check 揭發 **8 stale-superseded sources 仲 in index 共 1,010 chunks（~10% Supabase）**：va_sss_2015 (180) / ethics_relig_sss_2007_2019 (166) / music_sss_2015 (161) / econ_sss_2007_2015 (147) / econ_sss_supp_2015 (39) / bafs_sss_2007_2015 (122) / pe_sss_2007_2015 (119) / sci_jss_supp_2017 (76)；Leonard 揀 Vanilla 保 §A.2 #1 traceability，deprecation 推 batch-6 評估。
- **Batch-5 10 sources（Vanilla）：** g24 / g29 / sci_jss_framework_2025 / pe_sss_2023 / edbcm183_2023_values_edu / sec_curr_guide_2017_booklet_6a / edbcm58_2024_pri_science / pri_science_cert_course_list / edbcm57_2024_pri_science / edbcm243_2024_pri_science。Pages 270/108/82/75/25/22/13/7/7/7 = total **616**。
- **Feasibility + Monitor pre-flight：** 10/10 GO（URL HEAD 200 + PyMuPDF page count + size 219KB-8.2MB；g24 270p 最大）；Monitor predict net -188（誤、見 Gate 2 真值）。
- **§3 HIGH-risk Gate 1 PLAN→Leonard「go」→EXECUTE 10/10 PASS：** repage_pdfs.py PILOT_LEGACY/PILOT_OUT 各 +10 batch-5 entries（size 43→53、import verify、10 legacy paths exist）→ dry-run 10/10 ok markers==pages total 616、content sanity 101.4-103.8% → `--write` 10/10 written；§5.a backup `dev/init_backup/20260526_124023_UTC/cb3c_pilot_legacy/`；git scope 21 entries clean。
- **§3 HIGH-risk Gate 2 dry-run + EXECUTE 10/10 OK：** dry-run 揭 **g24 300→383 +28% = content RECOVERY**（撞 legacy 300 cap、同 S122 eng_lit +111% / S123 eng_sss +40% pattern、cap chunker-bound non-era-dependent）；其餘 9 sources -16~-26% canonical normalization。Total DELETE 752 / INSERT 736 / net **-16**（vs PLAN predict -188，差源於 g24 cap-recovery；Monitor 模型需更新：large-page docs originally 撞 300 cap recovers when re-chunked，非 era-dependent）。Leonard 第二次 go → EXECUTE：Phase 1b embed all 736 chunks first → `wiki_index.json` auto-backup `dev/init_backup/20260526_133107_UTC/` → per-source DELETE→upload→count verify 10/10 `del=/ins=/now=` 完全對齊 → Phase 3 SKIPPED `--skip-local`。
- **QC post-execute：** Supabase total via Range header = **10,117** exact match prediction (10,133 - 752 + 736)；INVARIANT 6 spot-check g01=32 / sag_2025_11=383 / ict_sss_2021=81 / econ_sss_2025=87 / music_sss_2024=69 / ethics_relig_sss_2024=90 全 unchanged。
- **Live smoke 5/10 batch-5 sources surface with page numbers**（3 direct + 2 cross-query bonus）：⭐ sci_jss_framework_2025 (p=1, p=29 #3/#5、0.508/0.502) / edbcm183_2023_values_edu (p=1 #4、0.590) / edbcm57_2024_pri_science (p=7 #5、0.499) + **bonus** g24 (p=98 #2 via edbcm57 query、0.517) / sec_curr_guide_2017_booklet_6a (p=18 #3 via values_edu query、0.592)。5 non-surface = ranking competition：g24 「學校行政手冊」query 57014 transient 又 retry 撞 sag_2025_11 dominate（**新發現：g24 vs sag_2025_11 semantic-duplicate**，registry supersede=[] 但實質 sag_2025_11 係 g24 newer consolidated；S125 §8b lesson extension：audit 仲要 catch semantic-level supersede）/ g29 「小學課程指引」→ pri_curr_guide_2024 dominate / pe_sss_2023 → pe_kla_2017 0.723 dominate（broader KLA-level non-supersede competition、vanilla 預期）/ edbcm58 / edbcm243 → edbcm98_2024_pri_science cluster competition（同 series intra-cluster、PLAN assumption #6 中）/ pri_science_cert_course_list → pri_science_guide_2025 dominate。
- **Whole-vault page-resolvable progression（post-S125b）：** 13.2% → 23.7% → 32.2% → 55.2% → 64.4% → 73.0% → 76.0% (post-batch-4) → **~80.0% (post-batch-5)** = ~8,094 / 10,117 chunks。Sources marker-bearing：**92 / 113**（39 B + 3 C pilot + 10 batch-1 + 10 batch-2 + 10 batch-3 + 10 batch-4 + 10 batch-5）。Remaining：**~10 marker-less PDFs**（batch-6：7 stale-superseded for deprecation track + ~3 truly orphan small g15/edbcm98/pe_sss_2007_2015 也算入 stale list 視 deprecation strategy）+ 9 結構天花板 → CB-3 final ceiling ≈ 88%。
- **§E.14 §8 教訓 5th-validation：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused = **50 sources end-to-end PASS（S122-S125b）+ 0 incident**；pipeline production-ready confirmed multi-batch reuse。
- **S125b new §8b lesson extension：semantic-supersede detection**：g24 vs sag_2025_11 = registry 無 supersede 鏈但實質係 same-domain elder vs newer consolidated；audit cross-check 之前只用 registry `supersedes` field、未 catch semantic-level supersede（同 KLA + same naming pattern + title overlap）。Recurrence-prone（S122 tech_kla vs pri_curr / S123 music_sss_2024 vs music_p1_s6 同樣 pattern）— 應 promote §8b rule extension：audit agent 必跑 title/KLA/scope embedding similarity ≥0.85 check（across already-indexed sources）before approving batch candidate。
- **Sources changed (batch-5)：** commit `d66f091` origin/main：`dev/vault/repage_pdfs.py` PILOT +10 batch-5 + 10 vault rename pairs + 4 governance docs。Supabase live：10,133→10,117（DELETE 752 INSERT 736 net -16）。dev/init_backup/{20260526_124023_UTC,20260526_133107_UTC}/。

#### Follow-up — broader Option C batch-6 Hybrid strategy（同 session 第三 cycle）

- **Trigger：** Leonard `/goal go` full-flow authorization；batch-6 Hybrid = 2 page-carry orphan small (g15 + edbcm98_2024_pri_science) + 2 DROP-only deprecation (pe_sss_2007_2015 + sci_jss_supp_2017，S125b 剛被 pe_sss_2023 + sci_jss_framework_2025 supersede 嘅 stale pair) per S125b §8b audit cross-check finding。
- **Recon：** page-carry pair feasibility 2/2 GO（g15 22KB 3 pages、edbcm98 354KB 6 pages）；DROP pair pre-state confirmed indexed pe_sss_2007_2015=119 + sci_jss_supp_2017=76 = 195 chunks。
- **CHANGE step 0：** repage_pdfs.py PILOT_LEGACY/PILOT_OUT +2 batch-6 entries（size 53→55）。
- **NEW script `dev/cb3_deprecate_stale.py`：** DROP-only deprecation tool（mirror cb3_b2 discipline：service_role REST DELETE + per-source verify count==0 + Phase backup audit log dev/init_backup/<ts>/cb3_deprecation_log.json + --skip-local default + --execute gate）。Python 3.9 compat fix（`from __future__ import annotations` + Optional/Tuple from typing；first-write 撞 PEP 604 syntax error、5min fix verify）。
- **Gate 1 page-carry --write 2/2 PASS：** g15 3 markers / edbcm98 6 markers；content sanity 112% / 106% slight marker overhead；§5.a backup `dev/init_backup/20260526_135854_UTC/`。
- **Gate 2 page-carry dry-run + EXECUTE 2/2 OK：** dry-run DELETE 11 INSERT 9 net -2；EXECUTE 順流：Phase 1b embed 9 chunks first → wiki_index.json auto-backup `dev/init_backup/20260526_140052_UTC/` → per-source `del/ins/now` 完全對齊（edbcm98_2024_pri_science del=7 ins=6 now=6 / g15 del=4 ins=3 now=3）→ Phase 3 SKIPPED `--skip-local`。
- **Deprecation dry-run + EXECUTE 2/2 OK：** dry-run total DELETE planned = 195 (pe_sss_2007_2015 119 + sci_jss_supp_2017 76)；EXECUTE：audit log `dev/init_backup/20260526_140059_UTC/cb3_deprecation_log.json` 寫低 pre-delete counts + reversibility note → Phase 3 per-source REST DELETE：pe_sss_2007_2015 del_status=204 pre=119 post=0 OK / sci_jss_supp_2017 del_status=204 pre=76 post=0 OK。
- **QC post-execute 3 PASS：** (1) Supabase total via Range header = **9,920** exact match prediction (10,117 + (-2 page-carry) + (-195 deprecation) = 9,920) (2) INVARIANT 8 spot-check g01=32 / sag_2025_11=383 / pe_sss_2023=79 (S125b intact) / sci_jss_framework_2025=75 (S125b intact) / econ_sss_2025=87 / **va_sss_2015=180 / music_sss_2015=161 (Vanilla preserved as expected)** / g24=383 全 unchanged (3) Audit log file written with full reversibility note。
- **Live smoke deprecation ranking improvement verified：** ✅ **sci_jss_framework_2025 「初中科學 學習架構」TOP-1+#2 0.540/0.514 p=29/p=27** — superseder direct dominate post-deprecation（pre-batch-6 sci_jss_supp_2017 競爭已 cleared）。✅ pe_sss_2007_2015 完全不再 surface 任何 pe-related query（deprecation cleanup verified）；pe_sss_2023 vs pe_kla_2017 ranking competition 屬 broader KLA scope、非 stale-superseded，acceptable per vanilla strategy。⚠️ pe_sss_2023 直接 query 撞 57014 transient（PMS §C.4 known，retry alt query OK）。⚠️ g15/edbcm98 page-carry verified live indexed（now=3/now=6）但 size 太細 + KLA-level dominate、query 唔 surface（acceptable for small orphan sources）。
- **Whole-vault page-resolvable progression（post-S125c）：** ~80.0%→**~81.5%** ≈ 8,083 / 9,920 chunks（page-carry +9 chunks across g15/edbcm98 + deprecation removes -195 stale = net page-resolvable ratio 提升、無新 stale 入 ranking competition）。Sources marker-bearing：92 + 2 (batch-6 page-carry) = **94 / 113**（39 B + 3 C pilot + 10×5 batches + 2 batch-6 small）。Stale deprecated：pe_sss_2007_2015 + sci_jss_supp_2017 = 2 sources。Remaining marker-less PDFs: **6 stale (Vanilla preserved)** = va_sss_2015 / ethics_relig_sss_2007_2019 / music_sss_2015 / econ_sss_2007_2015 / econ_sss_supp_2015 / bafs_sss_2007_2015；可考慮 future batch-7 case-by-case re-evaluate 是否需 deprecate（要不要 follow Hybrid pattern 視 ranking polish 後評估）。+ 9 結構天花板。CB-3 final ceiling **~88%**（達成）。
- **§E.14 §8 教訓 6th-validation：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused for batch-6 page-carry pair = **52 sources end-to-end PASS S122-S125c 0 incident**；NEW `cb3_deprecate_stale.py` 同 discipline mirror（per-source verify + audit log + --skip-local + --execute gate）= 2 sources DROP 0 incident first-use。
- **S125c codified lessons:** (1) Hybrid deprecation strategy verified production-viable；(2) NEW deprecation script blueprint reusable（後續 batch-7 evaluate 6 remaining stale 可沿用 0 修改）；(3) audit cross-check stale-superseded rule (§8b S125b) → deprecation → live ranking improvement verified end-to-end（北極星 traceability priority 守、stale ranking competition cleared without 過度 deprecation）；(4) Python 3.9 first-write script compat lesson（PEP 604 syntax 用 `from __future__ import annotations` + typing module、未來 first-write 必驗）。
- **Sources changed (batch-6)：** Draft modified pending commit+push：`dev/vault/repage_pdfs.py`（PILOT_LEGACY/PILOT_OUT +2 batch-6 entries、size 53→55）+ **NEW `dev/cb3_deprecate_stale.py`** 159 lines + 4 governance docs (SESSION_LOG batch-6 sub-block + SESSION_HANDOFF + CODEBASE_CONTEXT + HANDOFF_PACKAGE)。Draft new: `dev/vault/g15/extract_g15_repaged.txt` + `dev/vault/edbcm98_2024_pri_science/extract_edbcm98_2024_pri_science_repaged.txt`。Draft deleted: corresponding 2 legacy `extract_<sid>.txt`（backed up gitignored）。Supabase live (非 git)：wiki_chunks 10,117→9,920（batch-6 page-carry DELETE 11 INSERT 9 + deprecation DELETE 195 INSERT 0）。dev/init_backup/{20260526_135854_UTC,20260526_140052_UTC,20260526_140059_UTC}/（gitignored）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / data change（10 sources Supabase page-carry replace 生產 live）| SESSION_HANDOFF baseline #1/#3 + Open-Priorities-regen + Last Session Record + SESSION_LOG 本 entry | ✓ Done |
| External service / data row change（Supabase wiki_chunks 10,253→10,133）| CODEBASE_CONTEXT External Services line 132 + AI Maintenance Log +S125；HANDOFF_PACKAGE §2 chunks count | ✓ Done |
| Long-term spec / pipeline 4-batch reuse 印證 + audit cross-check lesson | PROJECT_MASTER_SPEC §D.16 batch-4 verified note + §8b superseded-in-index lesson | ⚠ Skipped (defer to batch-5 closeout per S124 handoff plan; this entry codifies it inline) |
| New ops backlog（Freshness workflow chronic fail since 2026-04-30）| SESSION_HANDOFF Open Priorities + Known Risks；後續 session 處理 | ✓ Done |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 82 源 diverge，原 72 → 82）| SESSION_HANDOFF Risks update（local↔Supabase reconcile scope 擴）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S125 (CLOSED 2026-05-26 三批一日打完)：**CB-3 Option C broader batch-4 + batch-5 + batch-6 Hybrid（22 marker-less PDF page-carry + 2 deprecation）生產 live + CB-3 final ceiling ~88% 達成 + Freshness workflow chronic-fail triaged + §8b audit cross-check first live application + Hybrid deprecation production-verified + g24/sag NEW semantic-supersede lesson + NEW `dev/cb3_deprecate_stale.py` 0 incident first-use + driver 6th-validation**。HEAD = S125 commit chain (batch-4 `e703910` + batch-5 `d66f091` + batch-6 commit pending；下次起手自行 verify origin/main)。Batch-4 10 sources = ict_sss_2021 / chi_hist_jss_ncs_2019 / chi_hist_jss_bilingual_2019 / econ_sss_2025 / econ_sss_supp_2025 / geog_sss_supp_2022 / geog_sss_summary_2022 / geog_sss_update_brief / arts_kla_guide_2017 / music_national_anthem_2024（pages 383；DELETE 537 INSERT 417 net -120；Supabase 10,253→10,133；smoke 4/10 direct surface + 6/10 ranking competition non-regression）。Batch-5 10 sources Vanilla strategy = g24 / g29 / sci_jss_framework_2025 / pe_sss_2023 / edbcm183_2023_values_edu / sec_curr_guide_2017_booklet_6a / edbcm58_2024_pri_science / pri_science_cert_course_list / edbcm57_2024_pri_science / edbcm243_2024_pri_science（pages 616；g24 300→383 +28% content RECOVERY 撞 legacy 300 cap、其餘 -16~-26% canonical；DELETE 752 INSERT 736 net **-16**；Supabase 10,133→**10,117**；smoke 5/10 surface = 3 direct (sci_jss_framework_2025 p=1/29 / edbcm183_2023_values_edu p=1 / edbcm57_2024_pri_science p=7) + 2 cross-query bonus (g24 p=98 / sec_curr_guide_2017_booklet_6a p=18)；§5.a backup `dev/init_backup/20260526_124023_UTC/`）。Mid-session **Freshness workflow triage**：5 連 chronic fail since 2026-04-30，root cause = check_freshness.py line 141-142 `if errors > 0: sys.exit(1)` + EDB intermittent + 15s timeout，非 batch 觸發，列下次 session priority。**§8b audit cross-check rule FIRST PRODUCTION APPLICATION (S125b)**：揭發 8 stale-superseded sources 仲 in index 共 1,010 chunks ~10% Supabase（va_sss_2015 180 / ethics_relig_sss_2007_2019 166 / music_sss_2015 161 / econ_sss_2007_2015 147 / econ_sss_supp_2015 39 / bafs_sss_2007_2015 122 / pe_sss_2007_2015 119 / sci_jss_supp_2017 76）；Leonard 揀 Vanilla 保 §A.2 #1 traceability、deprecation 推 batch-6 評估。**S125b NEW semantic-supersede lesson extension**：g24 vs sag_2025_11 registry `supersedes=[]` 但實質係 same-domain elder vs newer consolidated（同 KLA + same naming pattern + title overlap）；S122 tech_kla vs pri_curr / S123 music_sss_2024 vs music_p1_s6 同 pattern；audit cross-check 之前只用 registry supersede field、未 catch semantic-level supersede。Whole-vault page-resolvable 73.0%→76.0% (post-batch-4)→**~80.0% (post-batch-5)**；**92/113 sources marker-bearing**。driver `cb3_b2_pagecarry_migrate.py` **5th-validation** zero-code-change reuse = 50 sources end-to-end PASS S122-S125b 0 incident。

Current objective and progress state:
- **Batch-4 + Batch-5（共 20 sources）= 生產 live closed**（Supabase 10,117；driver 5th-validation；§8b audit cross-check rule first live application 揭 8 stale-superseded；§8b NEW semantic-supersede lesson surfaced；INVARIANT 6 spot-check 0 touched batch-5）。
- **Remaining CB-3**：**~10 marker-less PDFs**（batch-6 = 7 stale-superseded for DEPRECATION track + 3 truly orphan small g15/edbcm98/可能 sci_jss_supp_2017+pe_sss_2007_2015 屬 stale list）+ 9 結構天花板 → CB-3 final ceiling ≈ 88%。
- **2 §8b promote candidates pending Leonard decision**：(1) audit cross-check stale-superseded rule (live-validated S125b 揭 1,010 chunks) (2) NEW semantic-supersede detection (g24/sag pattern S125b 新發現)。
- **NEW backlog (S125)**：Freshness workflow chronic fail（5 連 since 2026-04-30、SESSION_HANDOFF Regression #2 stale）等下次 triage。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4（Channel A→knowledge.json→Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **broader Option C batch-6 = DEPRECATION-mixed track**（not pure page-carry）：7 stale-superseded DROP candidate（va_sss_2015 / ethics_relig_sss_2007_2019 / music_sss_2015 / econ_sss_2007_2015 / econ_sss_supp_2015 / bafs_sss_2007_2015 / pe_sss_2007_2015 / sci_jss_supp_2017）— 需 Leonard 拍板 strategy (Vanilla 全保留 / Hybrid 部分 DROP / Aggressive 全 DROP)；driver 限制：cb3_b2_pagecarry_migrate.py 只支援 page-carry、DROP-only 需新 script 或 Leonard Dashboard SQL DELETE。3 orphan small (g15 / edbcm98_2024_pri_science / 另選) 走 page-carry path。
2. **Freshness workflow triage（chronic ops cleanup）**：(a) 本地跑 `python3 dev/source/check_freshness.py --dry-run` 識別 N 條 fail URL；(b) 修 source_registry.json URL drift；(c) 改 script 失敗 threshold（建議 errors >5 才 exit 1 / 用 GitHub Issue 而非 fail email）。SESSION_HANDOFF Regression Notes #2 同步更新「stale baseline」。
3. **§8b rule promotion (S125b 2 lessons)**：(1) audit cross-check stale-superseded（first applied S125b、可 codify PROJECT_MASTER_SPEC §D.16 + §8 lessons）(2) NEW semantic-supersede detection（g24/sag、tech_kla/pri_curr、music_sss_2024/music_p1_s6 同 pattern；audit agent 加 KLA-title embedding similarity check）。
4. **batch ranking polish backlog（低優先）**：S122-S125b 累計 ~17 sources ranking competition（含 stale-superseded 真因 + semantic-supersede 真因），可 dedicated route / SOURCE_ALIASES / deprecation 改善。
5. **🔴 既有 deferred**：§E.10 admin-login client-side gate（OPEN）；57014 transient；FAIL-A 注入 regression（record-only）；P2/P3 deferred；Mobile UI P2；HKEAA；doc-debt。
6. **Q4 對外契約收斂（deferred）**：Channel A→knowledge.json→Circular System；3 選項待 CB-3 收尾 + Leonard 排。
7. **Governance doc full update**（PROJECT_MASTER_SPEC §D.16 batch-4/5 verified + §8b 2 new rules codify）：建議 batch-6 closeout 一次過做。

Key files changed this session（commit+push）：
- Draft commit `e703910` origin/main (batch-4 主體)：dev/vault/repage_pdfs.py PILOT +10 batch-4 + 10 vault rename pairs + 4 governance docs。
- Draft pending commit (batch-5 + closeout)：dev/vault/repage_pdfs.py PILOT +10 batch-5 + 10 vault rename pairs + 4 governance docs。
- Supabase live (非 git)：wiki_chunks 10,253→10,133→10,117（batch-4 DELETE 537 INSERT 417 + batch-5 DELETE 752 INSERT 736 = 共 DELETE 1,289 INSERT 1,153 net -136）。
- dev/init_backup/{20260526_073931_UTC,20260526_091916_UTC,20260526_124023_UTC,20260526_133107_UTC}/（gitignored）。

Known risks / blockers / cautions:
- **2 §8b promote candidates pending Leonard decision**：(1) audit cross-check stale-superseded rule (live-validated S125b、~10% Supabase 受影響) (2) NEW semantic-supersede detection (g24/sag pattern)；下次 batch-6 + governance doc update 時 codify。
- **§E.14 driver reuse 5th-validation**：50 sources 0 incident、pipeline production-ready；batch-6 deprecation 部分需新 script (page-carry driver 唔做 DROP-only)。
- **Monitor agent prediction 模型 update need**：cap-recovery (legacy 撞 300 cap) 唔可以淨睇 era predict、large-page docs 都有 risk；S122 eng_lit +111% / S123 eng_sss +40% / S125b g24 +28% 三度印證。
- **Freshness workflow chronic fail (S125)**：低 blast radius、ops noise；triage 列 priority #2。
- local `wiki_index.json` vs Supabase 92 源 diverge（S125 後 82→92；Supabase query-authoritative；reconcile 低優先 backlog）。
- 既有 risks：🔴 §E.10 admin-login（OPEN）；🔴 Supabase free-tier 57014 transient（retry 即恢復；S125b g24 「學校行政手冊」query 撞 1 次）；🔴 FAIL-A（record-only）；§3c record-only；q.html/A·AB dormant 可逆勿清；Q4 deferred；Stage-2 closed。
- egress 間歇每次自測；EDB PDF 永遠 `url_primary`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft commit 必入 SESSION_LOG。

Validation status:
- PASS S125 batch-4 (commit `e703910` push) + S125 batch-5 vault write 10/10、Gate 2 EXECUTE 10/10 OK Supabase 10,117 exact、smoke 5/10 surface + INVARIANT 6 spot-check 0 touched + driver 5th-validation。
- PENDING：commit + push S125 batch-5 + closeout（若 Leonard「收工」），governance doc full update（batch-6 closeout 過），Freshness triage、§8b 2-rule promotion。
- OPEN：batch-6 = deprecation-mixed 等 Leonard 拍板 deprecation strategy / 既有 deferred / 既有 backlog。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD / knowledge.json._meta.stats / Supabase chunk count = **9,920** / egress）後，**S125 三批 + 2 deprecation 完成生產 live + CB-3 final ceiling ~88% 達成（22 sources page-carry + 2 deprecated + 6 Vanilla-preserved stale + 9 結構天花板；Supabase 10,253→10,133→10,117→9,920 = net -333；94/113 sources marker-bearing；live smoke deprecation ranking improvement verified；NEW `cb3_deprecate_stale.py` 0 incident；driver 6th-validation 52 sources 0 incident；§8b audit cross-check + semantic-supersede 2 lessons surfaced 待 governance codify）**。第一件事＝問 Leonard：(a) **Freshness workflow triage**（chronic 5 連 fail since 04-30、ops noise、低 blast radius；本地跑 `python3 dev/source/check_freshness.py --dry-run` 識別 N 條 fail URL + 修 source_registry URL drift + 改 script exit threshold + 修 SESSION_HANDOFF Regression Notes #2 stale baseline）；(b) **§8b 2-rule codify + PROJECT_MASTER_SPEC governance doc full update**（§D.16 batch-4/5/6 verified + audit cross-check stale-superseded rule + NEW semantic-supersede detection rule + NEW `cb3_deprecate_stale.py` documented）；(c) **Future batch-7 (optional)** 6 stale Vanilla-preserved 案例分析 case-by-case re-evaluate（va_sss_2015 / ethics_relig_sss_2007_2019 / music_sss_2015 / econ_sss_2007_2015 / econ_sss_supp_2015 / bafs_sss_2007_2015 = 815 chunks 仲 in index）；非急；(d) 抑或 **既有 backlog**（🔴 §E.10 admin-login client-side gate / batch ranking polish ~15 sources / freshness metadata / Mobile UI P2 / etc）？未 Leonard 明示前**唔好自行 resume / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。
```

---
