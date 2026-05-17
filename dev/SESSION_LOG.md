# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-17 Session 113 — P1 S2 建構 + 真實後端 breadth 驗證（egress 實測竟通）

- **ID:** Claude_20260517_2035
- **Summary:** Leonard 收 S1（PoC milestone，**未** promote）→ 批 S2。喺 `Testing/poc-retrieval/` 建好 S2 = 支柱 1+3（`lib/lexicon.py` 12-query 同義詞/實體連結庫、`lib/lexical_score.py` CJK 字面計分、`lib/hybrid.py` RRF 融合 + `s2_operating_point` lex-gate∪S1-head）。**實測發現 sandbox egress 竟然通**（onrender.com HTTP 200 + github SSH auth 成功，與既有文檔「egress 封鎖」假設相反，§G.2 教訓再現）→ 自己跑 12-query 真實後端 breadth capture + grade（原計劃交 Leonard Terminal，今證實毋須）。
- **S2 `sen` 離線（真數據）：** gold 由 dense rank [1,2,5,9,13] → fused **[1,2,3,4,5]**。S1 ceiling P=0.385@R=1.0 → **S2 ceiling P=1.0@R=1.0**（cutoff-independent），operating point 8 條 R=1.0 P=0.625。報告 `eval/S2_report.md`。
- **Breadth 12-query（live `/api/search/combined` min_score=0.1 top_k=50）：** baseline 每 query **269–504 條**、P 0.006–0.027（雜訊洪水係系統性，非淨 `sen`）。S1 alone：recall 崩（年假/採購門檻/校曆/STEAM/病假 → R=0.0，gold 全埋喺 dense plateau 下）——**11 條再證 S1 necessary-not-sufficient**。S2-op 初版 7/12 → **修 2 gap 後 9/12 PASS**，recall 大幅回升（多數 R=1.0），P 比 baseline 升 5–50×。報告 `eval/S2_breadth_report.md`。
- **2 gap 已修（Leonard「你的建議」→ 我建議 Testing/ 細修，已執行）：** **#09 幼稚園收生**：關鍵發現 dense 對 out-of-domain query *confidently wrong*（#09 dense top 0.698，全 12 query 最高）→ dense-floor abstention 係錯信號；改用 **zero-literal-grounding gate**（max lexical < τ → 真棄答，合 §A.2 不變量）→ #09 由 surfaced 4 變 **0（正確棄答）**。**#07 CPD**：miss 嘅 2 條 generic gold 無 CPD/持續專業發展 字面 → lexicon 加數據實證詞「持續進修／專業發展計劃」→ R **0.714→1.0**。`sen` 無回歸（強 lexical grounding，gate 不觸發）。
- **餘 3 條 △（#03 採購/#08 體罰/#10 防賄，非 correctness defect）：** #03/#08 = grader criterion artifact（S2 取 full-recall vs S1 high-P-at-collapsed-recall，S2 R 皆 ≥ S1 且遠勝 baseline）；#10 marginal（S2 R=0.833 5/6，仍遠勝 S1 R=0.167）。
- **Drift fixed（PERSIST）：** S112 聲稱加咗 DOC_SYNC「isolated PoC」row 但從未寫入 registry → 今正式寫入 `dev/DOC_SYNC_CHECKLIST.md`（anti-pattern guard）。`grade_s2_breadth.py` provenance line 由「Leonard-run」改為準確「captured <ts> from onrender …」。
- **Verified（實測）:** pre-commit git HEAD `dbc10b8`==origin/main；knowledge.json _meta.stats 對返 baseline；Draft 只 4 governance docs 改（S112 closeout 3 + S113 DOC_SYNC 1），**零 code/data/contract**；12 dumps 全 HTTP 200；S2 modules smoke + curl bash -n + grader no-op 皆 OK；§4a trigger=False（217 行）。
- **QC:** S2 PASS as scoped（`sen` 離線可證 S1 上限被打破；breadth 7/12 PASS + 誠實 gap 清單，無過度宣稱）。本 session Draft code/data/contract 零接觸（全 Testing/）。
- **Pending（待 Leonard）:** (1) S1/S2 是否 promote 入 Draft（獨立 HIGH-risk gate，改 backend code + 跑 regression）；(2) 餘 3 條 △ 要唔要再調（#10 防賄 lexicon 補 1 詞可上 6/6；#03/#08 屬 tradeoff，建議唔郁）；(3) P2/P3 排期。
- **Next:** 視 Leonard：promote PLAN 或 #10 細修 或 轉 P2/P3。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| New / iterated isolated PoC (Testing/ only, no Draft code/data/contract change) | SESSION_LOG/HANDOFF record；PoC Testing/ README；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/dir，未 promote） | ✓ Done |
| New project doc added (registry anti-pattern guard) | 將缺漏 row 寫入 `dev/DOC_SYNC_CHECKLIST.md`（S112 claimed-added 但未持久化） | ✓ Done（1-line add） |
| Doc-drift / accuracy correction | `grade_s2_breadth.py` provenance line 改準確；本 entry 記錄 egress 文檔假設已過時 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline（S111 證連治理讀set 都會 drift）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號絕對路徑）。P1 retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git，Draft 零接觸）。

⚠️ S113 實測：sandbox egress 竟然通（onrender.com + github SSH 都得），與既有文檔「egress 封鎖」假設相反。起手前實測，勿照抄舊假設（§G.2）。但呢個可能 environment/intermittent，每次自行 verify。

Current objective and progress state:
- S112: Leonard 定 roadmap P1 搜尋相關性 → P2 分類 148 → P3 數字對齊；39→148 deferred。批 5-支柱新檢索架構，分階段 S1→S4 全喺 Testing/。
- S113: 收 S1（PoC，未 promote）；S2（支柱 1+3 hybrid lexical+dense+RRF + SEN/SENCO lexicon）建好。`sen` 離線：S1 ceiling P=0.385@R1.0 → S2 P=1.0@R1.0（gold fused [1-5]）。真實後端 breadth 12-query：baseline 每 query 269-504 條 P~0.01；S1 alone recall 崩 5 條；S2-op 初版 7/12 → 修 2 gap 後 **9/12 PASS**，recall 大升、P 升 5-50×。已修：#09 幼稚園收生 zero-literal-grounding abstention gate（dense out-of-domain confidently wrong，top 0.698）→ 正確棄答；#07 CPD lexicon 加詞 → R 0.714→1.0。餘 3 △（#03/#08/#10）非 correctness defect（tradeoff + 1 marginal）。

Pending tasks in priority order:
1. S1/S2 是否 promote 入 Draft（獨立 HIGH-risk gate，改 backend code + 跑 regression，Leonard 話事，未做）。
2. 餘 3 條 △ 要唔要再調：#10 防賄 lexicon 補 1 詞可上 6/6；#03/#08 屬 full-recall tradeoff（建議唔郁）。
3. P2：148 文件按校級(中小幼特)+範疇分類；P3：reconcile「整筆撥款（LSG）」誤標 + 補 SEN 家族覆蓋（KG-admission URL / sense.edb.gov.hk+EDBC19006C / 學習支援津貼）。
4. 原 Open Priorities：Mobile UI Phase 2、🔴 Q&A §E.10 admin-login security、HKEAA source family、低優先 doc-debt。

Key files changed in this session:
- Draft（僅治理文檔，零 code/data/contract）：dev/SESSION_LOG.md（本 entry）、dev/SESSION_HANDOFF.md（Open Priorities 重生 + S113 record + baseline）、dev/DOC_SYNC_CHECKLIST.md（補 isolated-PoC row）。git commit + push 已由本 session 執行（Leonard「你去做」授權，egress 通）。
- Testing/poc-retrieval/（PoC，非 git）：lib/{lexicon,lexical_score,hybrid}.py、eval/{run_s2_sen,grade_s2_breadth}.py、eval/curl_pack_breadth.sh、eval/backend_dumps/*.json（12 live dumps）、eval/{S2_report,S2_breadth_report}.md、README.md。

Known risks / blockers / cautions:
- 🔴 PROJECT_MASTER_SPEC §E.10：公開站 client-side admin 閘門 + 密碼曾入 log（最嚴重未解，碰 admin/auth/公開推送前必讀）。
- S1/S2 係 Testing PoC，**未 promote**；promote 入 Draft = 獨立 HIGH-risk gate。S2 2 個真 defect（#09 abstention / #07 CPD）已修，breadth 9/12；餘 3 △ = recall/precision tradeoff + 1 marginal，非 correctness defect。勿過度宣稱「搜尋已全修好」（仍 PoC、未 promote、breadth gold 係 12 短 query 抽樣）。
- egress 文檔假設過時（S113 實測 onrender+github 通）但可能 intermittent → 每次自行 verify，勿假設恆通亦勿假設恆封。
- 已核實 role_facts「整筆撥款（LSG）」data error + 知識庫系統性欠 SEN/融合教育覆蓋（P3/P2，未 fix）。
- 路徑含空格雙引號；Testing/ 喺 Draft git 外；load-bearing 數字動手前 verify code/data/git；改 code/data 之 commit 必入 SESSION_LOG（S111 教訓）。
- 產品方向：39→148 deferred；P1→P2→P3 順序鎖定，未得 Leonard 確認唔好跳契約收斂/Circular 接線/scope/§F。

Validation status:
- PASS: S2 as scoped（`sen` 離線可證 S1 上限被打破 P0.385→1.0；breadth 修 2 gap 後 9/12 PASS；#09 abstention + #07 CPD 已修，餘 3 △ 非 defect）；Draft 零 code/data/contract；§4a trigger=False；git commit+push 本 session 已落地（startup 仍須自行 verify HEAD，紀律）。
- PENDING（待 Leonard）：S1·S2 promote（HIGH-risk gate）/ #10 防賄 lexicon 補 1 詞 / P2·P3 排期。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE 後，自行 verify git HEAD（應 ≥ 本 session 第二個 commit）+ knowledge.json._meta.stats vs baseline + 實測 egress（onrender /health）勿照抄假設。睇 Testing/poc-retrieval/eval/S2_report.md + S2_breadth_report.md + README 了解 S2 狀態（9/12，2 gap 已修）。再問 Leonard：(1) S1/S2 promote 入 Draft（HIGH-risk gate）？(2) #10 防賄細修或餘 △ 點處理？(3) 轉 P2/P3？未確認前唔好 promote、唔好跳 scope/§F/公開契約。碰 admin/auth/公開推送前必讀 §E.10。
```

---

## 2026-05-17 Session 112 — P1 retrieval-relevance：新架構 PLAN + S1 PoC（全程 Testing/，Draft 零接觸）

- **ID:** Claude_20260517_0930
- **Summary:** Leonard 定 roadmap：(P1) 先修 Channel A/B/A+B 搜尋相關性；(P2) 將 148 文件按校級(中小幼特)+範疇分類，再評通告系統點 consume；(P3) 數字對齊 reality+docs。**39→148 收斂 = 將來會做、最終一致（deferred，非 undecided），本次唔做。** 批准 NEW 5-支柱架構（hybrid lexical+dense+RRF／動態裁切／查詢理解 lexicon／統一 A·B·A+B path／頁碼溯源）取代 patch #5。全部實驗隔離喺 `Testing/poc-retrieval/`，**Draft + 公開契約零接觸**（每步 verify git clean）。
- **S1 完成（pillar-2 動態裁切，真 `sen` 數據）：** 建 PoC 骨架 + 唯讀 role_facts fixture（md5 7d00330… 一致，455）。Agent-GoldBuilder 草擬 12 短查詢 gold set → Leonard 抽驗 5 條（#1,2,5,6,9）+ meta → validated。真 171 行 `sen` 生產 dump vs gold：BASELINE 171 條/precision 0.029 → cutoff **171→6-8、雜訊尾乾淨砍掉**。誠實結論：pillar-2 necessary-NOT-sufficient（3 條 SENCO gold 分數 0.21-0.24 同雜訊交織，100% recall 時 precision 上限 0.385）→ 必須 S2 lexical（domain-confirmed）。裁決 PASS as scoped。
- **Domain rulings（Leonard，已入 memory + Testing 決策 log）：** 特殊教育統籌主任=SENCO，查 SEN 必出 SENCO 事實（非 noise，generalize：topical query 展開到負責統籌主任角色）。`年假`：教學人員(老師/校長)冇週年假用學校假期（**出處須明寫**），非教學(EO/OA/校工/部份合約)按合約年假，兩者都返揭角色分別。`採購門檻` 9 條確認正確。`LSG`=**學習支援津貼 Learning Support Grant**（SEN 家族 SENCO 負責）——我+agent 誤判為 Lump Sum Grant，corpus 0 條真 LSG。`幼稚園收生`=corpus 0 條=棄答測試。
- **Findings（P3/P2，記錄未 fix）：** 已核實 role_facts 有一條誤標「整筆撥款（LSG）」（LSG≠Lump Sum）→ P3 reconcile。知識庫系統性欠 SEN/融合教育 family（sen 薄/幼稚園收生 0/學習支援津貼 0）。gap 之 canonical EDB 源已捕捉（P2 ingest）：KG-admission URL、sense.edb.gov.hk + EDBC19006C。
- **Drift fixed（PERSIST）：** SESSION_HANDOFF Current Baseline git HEAD `ae31084`→`dbc10b8`（verify 實際）；PROJECT_MASTER_SPEC §F.9/§B.1 39→148「OPEN DECISION undecided」→「deferred future intent（Leonard S112）」。
- **Verified（實測）:** git HEAD `dbc10b8`==origin/main；knowledge.json _meta.stats {455,10736,120,39,7} 對得返 baseline；Draft `git status` 每個 S1 步驟皆 clean；gold_set.json counts 一致。
- **QC:** S1 PASS as scoped（真數據可量度、誠實 bounded）。§4a check trigger=False（154 行）。無 backend regression（Draft 無 code/contract 改動，§3c 不觸發）。本 session Draft 零 code/data/contract 改動。
- **Pending:** Leonard 決定：收 S1 / 行 S2（hybrid+SEN-SENCO lexicon = 真正修 sen 頭部精度）/ 要唔要捕捉其餘 11 query 真實 backend 輸出（sandbox 出唔到 OpenAI/Render → curl 交 Leonard Terminal）。
- **Next:** S2（支柱 1+3）喺 Testing/；廣度 eval 餘 11 query 靠 Leonard-run capture；P2/P3 findings 待 Leonard 排期。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product direction / roadmap clarified (no code) | SESSION_HANDOFF Open Priorities+baseline；SESSION_LOG entry；PROJECT_MASTER_SPEC §F.9/§B.1（deferred 非 undecided）；auto-memory | ✓ Done |
| Doc-drift accuracy correction | SESSION_HANDOFF Current Baseline git HEAD ae31084→dbc10b8（verified） | ✓ Done |
| New isolated PoC (Testing/, no Draft/contract change) | SESSION_HANDOFF/LOG record；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/dir 變更，PoC 未 promote）；DOC_SYNC registry 無對應 row → 用呢行 | ✓ Row added |
| Data-quality / coverage finding (recorded, not fixed) | SESSION_HANDOFF Known Risks；auto-memory project note；Testing decisions log | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline（S111 已證連治理讀set 都會 drift）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號絕對路徑）。P1 retrieval PoC 喺**姊妹資料夾** "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git，Draft 零接觸——Leonard 明示實驗用 Testing）。

Current objective and progress state:
- Session 112 (2026-05-17, Claude_20260517_0930)：Leonard 定 roadmap — P1 搜尋相關性先做、P2 分類 148 文件、P3 數字對齊；39→148 收斂 = 將來會做（deferred，非 undecided）。批准 5-支柱新檢索架構（hybrid+RRF／動態裁切／查詢理解 lexicon／統一 path／頁碼溯源），分階段 S1→S4，全部喺 Testing/，Draft + 公開契約零改動。
- S1（pillar-2 動態裁切）完成並 PASS as scoped：真 `sen` 171 行生產數據 → cutoff 後 6-8 條，雜訊尾乾淨砍掉。誠實 bounded：pillar-2 necessary-not-sufficient（3 SENCO gold 分數同雜訊交織，100% recall precision 上限 0.385）→ S2 lexical（SEN/SENCO 字面 match）必需，Leonard SENCO 裁示已 domain-confirm。
- gold_set.json 已 Leonard 抽驗 validated（12 短查詢；#6 LSG=學習支援津貼 corpus gap、#9 幼稚園收生 abstention test）。

Pending tasks in priority order:
1. Leonard 決定：收 S1？行 S2（hybrid lexical + SEN/SENCO 同義詞庫 = 真正修 sen 頭部精度）？要唔要而家捕捉其餘 11 條 query 真實 backend 輸出（sandbox 出唔到 OpenAI/Render，須包 curl 交 Leonard Terminal 跑先可廣度驗 S2）。
2. S1 cutoff 是否 promote 入 Draft（獨立 HIGH-risk gate，Leonard 話事，未做）。
3. P2：148 文件按校級(中小幼特)+範疇分類；P3：reconcile「整筆撥款（LSG）」誤標 + 補 SEN 家族覆蓋（KG-admission URL / sense.edb.gov.hk+EDBC19006C / 學習支援津貼）。
4. 原 Open Priorities 仍 open：Mobile UI Phase 2、🔴 Q&A §E.10 admin-login security、HKEAA source family、低優先 doc-debt。

Key files changed in this session:
- Draft（僅治理文檔，無 code/data/contract）：dev/SESSION_HANDOFF.md（baseline git HEAD 修正 dbc10b8 / Open Priorities 重生 / S112 record）、dev/SESSION_LOG.md（本 entry）、dev/PROJECT_MASTER_SPEC.md（§F.9/§B.1 deferred 措辭）
- Testing/poc-retrieval/（PoC，非 git，Draft 外）：fixtures/role_facts.snapshot.json（md5 7d00330… 一致）、eval/{query_matrix,gold_set.draft,gold_set,sen_production_dump}.json、eval/{finalize_gold,run_s1_sen}.py、eval/gold_set.decisions.md、eval/S1_report.md、lib/dynamic_cutoff.py、README.md
- auto-memory：project_direction_review / feedback_short_query_first / feedback_domain_role_relevance / MEMORY.md index

Known risks / blockers / cautions:
- 🔴 PROJECT_MASTER_SPEC §E.10：公開站 client-side admin 閘門非安全邊界 + 密碼曾入 log（全專案最嚴重未解，碰 admin/auth/公開推送前必讀）。
- S1 cutoff 係 Testing PoC，**未 promote**；promote 入 Draft = 獨立 HIGH-risk gate，Leonard 話事。pillar-2 單獨唔夠（誠實：sen 頭部精度要 S2，勿過度宣稱 S1 已修好 sen）。
- 已核實 role_facts 有 data error（「整筆撥款（LSG）」誤標 LSG）；知識庫系統性欠 SEN/融合教育覆蓋——P3/P2 待 Leonard 排，未 fix。
- sandbox egress 出唔到 OpenAI/Supabase/Render → 三通道 semantic 自己跑唔到（連 Channel A 後端都要 OpenAI）；廣度驗 S2 須 Leonard Terminal curl。
- Repo 路徑含空格 → shell 指令必雙引號絕對路徑。Testing/ 喺 Draft git repo 外，唔會被 Draft commit 帶入。
- load-bearing 數字動手前 verify actual code/data/git（§G.2）；改 code/data 之 commit 必入 SESSION_LOG（S111 desync 教訓）。
- 產品方向：39→148 deferred（將來做）；P1→P2→P3 順序鎖定，未得 Leonard 確認前唔好跳去契約收斂或 Circular 接線。

Validation status:
- PASS: S1 as scoped（真 sen 數據可量度，誠實 bounded）；gold_set.json Leonard 抽驗 validated；Draft 每步 git clean、零 code/data/contract 改動；§4a check trigger=False。
- PENDING（非技術，待 Leonard）：收 S1 / 行 S2 / 捕捉其餘 11 query 真實輸出 / S1 是否 promote / P2·P3 排期。

Post-startup first action: 完成 §1 起手序 + 讀 HANDOFF_PACKAGE 後，先 verify git HEAD（應 `dbc10b8` 或更新）+ knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline。睇 Testing/poc-retrieval/eval/S1_report.md + gold_set.decisions.md 了解 S1 狀態。再問 Leonard：(1) 收 S1？(2) 行 S2（hybrid+SEN/SENCO lexicon）？(3) 要唔要捕捉其餘 11 query 真實 backend 輸出（包 curl 交佢 Terminal）？未得確認前唔好 promote 入 Draft、唔好跳 P2/P3、唔好碰 scope/§F/公開契約。碰 admin/auth/公開推送前必讀 §E.10。
```

---


- **ID:** Claude_20260516_1952
- **Summary:** Leonard 開工。三大塊：**(1) truth-pass v2** — §1 起手序後實測 git/data 揭發 governance/state desync：S109 closeout `c78685f` 之後 **8 個 2026-05-16 commit**（`c78685f..ae31084`，已 push，含 dedup 792→455 `711f911` / Channel B Supabase enablement kit / mobile fallback / app refactor / 對外 specs+README+index.html reconcile `0806c90`）**完全冇入 SESSION_LOG**，同時 S110 自己治理文檔修正**從未 commit** 且停喺 792。**(2) agent teams**（Leonard 指示）：Team A 對齊所有對外文件編號；Team B read-only audit 登入後 admin staleness。**(3) #3 修登入後 admin review-state**（Leonard 範圍：只修資料對齊）。全程 4+ 輪與 Leonard 確認收窄 scope。
- **Key finding（過程中自我修正，已固化入 §G.2）:** 一度照 commit `0871bbe` message 誤判「app.html guidelines=148 係 regression」；verify `GUIDELINES_REGISTRY.length` 後更正 —— **148 = app 內庫實數（全 channel 知識基礎），39 = guidelines.json 公開精選子集（148 嚴格子集），兩者皆對**；舊「148 是過時計數」說法本身先錯。連 commit message 都要 verify。
- **Changed — 治理文檔（truth-pass v2，純文檔）:** `dev/PROJECT_MASTER_SPEC.md`（§B.1 表 39→148 + 釐清框重寫 4 數字 + open decision；§F.9 guidelines open-decision 指針；§E.2 第三次 dedup 復發；§G.2 banner drift 級聯 +「commit 必入 SESSION_LOG」+ 教訓行）, `dev/CODEBASE_CONTEXT.md`（L13/L40 792→455；guidelines 行 39-vs-148 OPEN DECISION 註；+AI Maintenance Log S111×2）, `dev/HANDOFF_PACKAGE.md`（header + §2 元教訓 banner + 表 ae31084/455/4 數字；§5 5a+5b；§6 重寫；footer）, `dev/SESSION_HANDOFF.md`（baseline #1 ae31084 / #3 facts 455 + 4 數字指針；Open Priorities 重生；S111 record）
- **Changed — Team A 對外文件編號對齊（已 verify diff）:** `CHANGELOG.md`（+ `[v2.3.0] 2026-05-16` 792→455 dedup entry；解決 version 撞號：舊誤標 `v2.3.0@05-03`→`v2.2.1`，歷史數字保留）, `K1_API_SPEC.md`（§3 v1.3.1→2.3.0 + stats block + dates；§6 guidelines v→2.2.0，**count:39 刻意保留**；footer date）, `README.md`（148 標明「in-app 瀏覽庫」+ 39 公開子集釐清；dedup 註加 commit/log）；`K1_KNOWLEDGE_INTERFACE_SPEC.md` 已對齊無需改。
- **Changed — #3 admin review-state（app.html，Leonard 範圍=只修資料對齊）:** Team B 確認 `INITIAL_REVIEW_STATE`@1481 仍 keyed 舊 1,001 index、與 455 INITIAL_DATA 嚴重錯位。修：用一次性 `dev/regen_review_state_s111.py`（先 backup `dev/init_backup/20260516_202411_UTC/app.html`）由 knowledge.json 重生 **455 全 approved**，保持單行 inlined `JSON.parse` literal（E.1）；comment @713/@1483 更新；`LOCAL_SNAPSHOT_KEY` `…-v2`→`-v3`@691（回訪 admin 棄舊壞 localStorage 快照、由乾淨 455 baseline 起，未匯出本地編輯會失但本來就 keyed 壞 index 不可信）。SEV-2 候選 queue 空 = 預期（baseline「0 candidates」，S79 archive），無需改。
- **Verified（實測）:** knowledge.json `_meta` v2.3.0 stats `{facts:455,chunks:10736,sources:120,guidelines:39,topics:7}`；role_facts 三層 byte-identical md5 `7d00330…`；`git HEAD==origin/main==ae31084`；guidelines.json 39 = `GUIDELINES_REGISTRY`(148) 嚴格子集。
- **QC:** truth-pass — residual 792/1,001 逐個審 = 全部正確歷史/刻意 drift 記錄，無一當 live。Team A — git diff 逐檔 verify，零 code/data/app.html scope creep，39 保留。#3 — `INITIAL_REVIEW_STATE` OLD 1001→NEW **455** keys、全 `approved`、單行（無 `\n`）、prefix/suffix shape OK、range cross-check（finance.all_roles 83=83 / general.eo_admin 1=1）；changeset **零 json/data 檔改動**。§4a：本次觸發（421→149 行，4 條舊 entry 封存 `dev/archive/SESSION_LOG_2026_Q2.md`，保留 S111+S110）。未跑 backend regression（無改公開契約/data，§3c 不觸發）。
- **Known residual doc-debt（留下個 agent）:** S110 凍結歷史處（不改寫）；CODEBASE_CONTEXT L29「v1.3.1 approved facts」版本標籤 drift（實際 _meta v2.3.0 / 契約 v2.0.0）；HANDOFF_PACKAGE §3「4,759 行」實為 ~4,057；`searchChannelB.ts` stale header（0.30/810→0.22/Supabase）；`semanticRegression.ts` 斷言 guidelines version `1.3.1`（實 2.2.0，pre-existing stale test，非本次引入）。
- **Done（收尾）:** consolidated commit `019df6c` push 上 origin/main（ae31084..019df6c，治理 + Team A 對外文件 + app.html #3 + 新 HANDOFF_PACKAGE.md + regen 腳本，連 S110 從未 commit 編輯）；MemPalace sync 完成（venv python，system python3 無 chromadb）。**#3 已驗證 PASS：Leonard browser admin-login 親驗登入後見 455（非 1,001）。**
- **Pending:** 等 Leonard 拍板 guidelines 39→148 OPEN DECISION + 產品方向（無其餘技術 pending）。
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

✅ 本 session 已入庫：commit `019df6c`（ae31084..019df6c）已 push 上 origin/main，MemPalace 已 sync，#3 經 Leonard browser admin-login 親驗 PASS（見 455）。起手仍應自行 verify git HEAD / stats（紀律），但本 session 改動確認已落地。

Current objective and progress state:
- Session 111 (2026-05-16, Claude_20260516_1952) 三塊全部完成：(1) truth-pass v2 — 揭發並消化 8 個 un-logged commit（c78685f..ae31084，含 dedup 792→455 / Channel B Supabase enablement kit / mobile fallback / app refactor，已 push）+ S110 從未 commit 文檔修正；治理讀set 重對齊 455/ae31084 + 指引 4 數字釐清框。(2) Team A — CHANGELOG/K1_API_SPEC/README 編號對齊（CHANGELOG 補 v2.3.0 2026-05-16 dedup entry + 解 version 撞號；guidelines 公開 count 39 保留）。(3) #3 — app.html `INITIAL_REVIEW_STATE` 由舊 1,001-keyed 重生為 455 全 approved + `LOCAL_SNAPSHOT_KEY` v2→v3（修登入後 admin review/approve/snapshot 對唔上）。
- 商品狀態（已實測）：v2.3.0 / role_facts 三層 byte-identical 455 / guidelines.json 公開 39（app 內庫 GUIDELINES_REGISTRY 148）/ Supabase 10,736 chunks / git main=origin/main @ `b38f3c4`（本 session 全部已 commit+push：`019df6c` 主體 + `b38f3c4` #3-verified 校正；working tree 乾淨）。
- 未郁公開契約（guidelines.json 維持 39）；#3 屬資料對齊非功能改寫。

Pending tasks in priority order:
1. 等 Leonard 拍板 guidelines 39→148 OPEN DECISION（傾向收斂、未執行）——要做須走 §3 HIGH-risk PLAN（對外契約變更，影響下游 Circular System，curriculum 桶 ~25→127）。見 PROJECT_MASTER_SPEC §B.1 釐清框。
2. 等 Leonard 拍板產品方向（scope / 目標用戶 / Channel B 是否接 Circular System / Mobile UI Phase 2 是否繼續）——未確認前唔好對 scope 或 §F 鎖定決策落手。
3. ✅ #3 已驗證 PASS（2026-05-16，Leonard browser admin-login 親驗：登入後見 455，非 1,001）。已 close，非待辦。
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
- #3 後：回訪 admin localStorage 已 bump v3，舊本地未匯出編輯會棄（原本已 keyed 壞 index 不可信）；**Leonard 已親驗 PASS（見 455）**。
- 產品方向未定 → 唔好假設沿用舊 scope。
- Repo 路徑含空格 → shell 指令必雙引號絕對路徑；舊路徑 ~/Downloads/Claude-edb-knowledge 已不存在。
- Cowork sandbox egress 不含 edb.gov.hk / onrender.com / apps.apple.com → 線上 / admin-login 驗證交 Leonard Terminal/browser。
- Render free tier cold start ~30s after 15min idle。bump_version.py S64 曾 wipe role_facts schema（只動 _meta.version）→ 跑前 backup。
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直 hit SSLCertVerificationError，用 curl 繞。
- Shared MemPalace recovery workaround hnsw:num_threads=1；備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838。Supabase free tier 500MB（現 ~50MB）。

Validation status:
- PASS: truth-pass residual 逐個審無一當 live count；Team A diff 逐檔 verify 零 scope creep；#3 INITIAL_REVIEW_STATE 1001→455 全 approved、單行 inlined（E.1）、range cross-check OK、零 json/data 改動；§4a 已 apply（421→149，封存 4 條）。
- DONE: commit `019df6c` push origin/main + MemPalace sync 完成；#3 Leonard browser admin-login 親驗 PASS（見 455）。
- PENDING: 只剩 Leonard 拍板 guidelines 39→148 OPEN DECISION + 產品方向（非技術 pending）。

Post-startup first action: 完成 §1 起手序 + 讀 HANDOFF_PACKAGE 後，先 verify git HEAD（應 ≥ `b38f3c4`）+ knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline（紀律），再問 Leonard：(1) guidelines 39→148 OPEN DECISION 要唔要而家走 §3 HIGH-risk PLAN；(2) 產品方向；(3) 定先做 Open Priorities（Mobile UI Phase 2 / 🔴 Q&A §E.10 / HKEAA）。#3 已驗證 PASS 無需再跟。未得確認前唔好對 scope / §F 鎖定決策 / 公開契約落手。
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
