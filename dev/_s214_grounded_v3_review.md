# S214 Grounded Synthesis V3 覆核（2026-09-06）

## 批次

- Artifact：`dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_acceptance_v3_windowfix.json`
- 服務：OpenAI Responses API
- Draft：`gpt-4.1-nano`
- Judge：`gpt-4.1-mini`
- 批准上限：36 次 HTTP；實際 25 次（18 draft＋7 judge）；`maxRetries:0`
- 範圍：只用保存 evidence，不作新 retrieval，不讀寫 Supabase
- 完整性：18／18 題、18／18 個 evidence-window SHA-256 fingerprint

## 結果

| 組別 | 結果 | 判斷 |
|---|---:|---|
| 無答案題 | 9／9 棄權 | PASS；沒有 false answer |
| 可答題 | 6／9 作答 | 不足以放行；其中兩題只屬安全部分回答 |
| API／格式錯誤 | 0 | PASS |
| 不合適對象答案 | 0 | PASS |
| OCR 重複／截斷輸出 | 0 | PASS |

相對舊 v2 的同一組九條可答題，作答由 4／9 增至 6／9；新增的兩項是 `hr_lang_req` 及 `saf_disease_notification`。此比較只說明修正 harness 後的合成結果，不代表 retrieval recall 已改善。

## 逐題覆核

- `staff_fullday_12`：PASS。直接回答全日制資助小學 12 班的小學學位教師為 5 名，不包括副校長。
- `fin_lwl`：PASS。四項用途均有第 3 頁逐字支持；問題屬開放式例子查詢，不要求列盡所有用途。
- `cur_kg_free_play_time`：PASS。半日制／全日制 30／50 分鐘及適用對象完整。
- `staff_halfday_12`：PASS。12 班半日制完整編制及總數有直接支持。
- `hr_lang_req`：PASS-with-flag。回答適用教師，但沒有列出同一片段已提供的豁免類別；系統正確附上「部分問題未能確認」，沒有冒充完整答案。屬 draft completeness 缺口。
- `saf_disease_notification`：PASS-with-flag。回答社會福利署／教育局，但漏去同一片段較前位置的衞生署；系統有部分回答提示。屬 draft completeness 缺口。
- `hr_lsp`：FAIL。`long_service_payment_guide` 已進五格，但命中的第 4 頁片段主要是比例、平均工資選項及扣減說明，沒有完整基本公式；draft 安全棄權。根因是 target passage 未進 evidence window，不可歸咎 judge。
- `gov_imc_60pct`：NOT VALID FOR NEW RUBRIC。模型使用 active gold 的新 query，但保存 evidence 仍來自舊短 query，且沒有附錄第 21 頁目標片段。須以新 query 重新 retrieval 後才可判分。
- `sen_special_school_curriculum`：FAIL。目標 `g10` 未進 evidence window；draft 只提出入讀特殊學校的轉介句，judge 正確判定沒有回答課程調適並棄權。

## Verdict

**FAIL，維持 feature flag 關閉。** 本批證明修正後 harness 沒有引入 false answer，亦證明兩道輸出衞生閘未再出現舊 blocker；但它不是完整 release gate：三條可答題仍未完整回答或不可有效判分，兩條新 NCS replacement 尚未有新 retrieval fixture，亦未做重複穩定性及獨立 agent 覆核。

## 下一步

1. ~~為兩條新 NCS、`gov_imc_60pct`、`hr_lsp`、`sen_special_school_curriculum` 以 active query 建新 retrieval fixture。~~ 已完成，見下節。
2. 把 `hr_lang_req`、`saf_disease_notification` 加入 draft completeness 小型回歸；不得要求模型猜測，只檢查同一 evidence 已明列的第二事項能否保留。
3. 以新 fixture 跑 focused acceptance 及至少兩次重複穩定性，再交獨立 agent 覆核。

## 五題新鮮檢索覆核

- Artifact：`dev/source/eval_runs/2026-09-06_s214_fresh_retrieval_5.json`
- 範圍：5 次 Render `synthesize:false`；每題後端使用 `text-embedding-3-small` 並唯讀查詢 Supabase；無重試、無寫入。
- `ss_ncs_chinese_framework_progress_v2`：PASS，正確一手來源及段落 rank 2；但片段有明顯 OCR 重複，輸出衞生閘仍須保留。
- `gov_imc_60pct`：PASS，正確一手原文 rank 3。另發現 gold 的舊 signature 拼接錯亂且頁碼誤標 21；已按 fresh evidence 更正為第 4 頁及 chunk `vault_imc_establishment_operation_1c25d85dde883f87`。
- `hr_lsp`：PARTIAL。策展摘要 rank 0；一手來源第 4 頁片段 rank 6，移除策展摘要後可進合成窗，但只有按比例年資及扣減註釋。完整公式其實存在於 `vault_long_service_payment_guide_ab49f971fc3d2752`，卻未被檢索；該 chunk 橫跨第 3／4 頁，公式實際在第 4 頁，但現行 dominant-page 推導判為第 3 頁。這同時是 chunk ranking 與頁碼 attribution 缺陷。Active gold 目前仍指向策展摘要，與 grounded synthesis 的一手證據政策不一致；本輪未硬改，因 validator schema 尚無法同時表達「原文真實頁碼 4」與「產品目前錯顯頁碼 3」。
- `ss_ncs_history_adapted_outline_v2`：FAIL。原本目標來源完全不在首 8；根因之一是來源已入庫但漏出 `SOURCE_SETS.curriculum`。最小 allowlist 修正後，本機候選實測令該來源升至 rank 0／1／3，但真正回答蒙古崛起的第 17 頁片段仍未進首 8。即 Source Recall 修好、Chunk Recall 仍失敗；不得把這項候選寫成完整修復。
- `sen_special_school_curriculum`：FAIL。`g10` 已在 `sen` allowlist，目標段落仍不在首 8；屬排序／表達問題，不是 route 漏項。本輪不以單題直接加入 spotlight。

候選中史驗證 artifact：`dev/source/eval_runs/2026-09-06_s214_ncs_history_candidate.json`。第一次本機啟動因缺 `SUPABASE_URL`／`SUPABASE_ANON_KEY` 在外部調用前 fail closed；其後依專案既有唯讀 fallback，以本機 service key 配合已登記 URL 完成同一批准範圍內的單次查詢。沒有重試、沒有 synthesis、沒有寫入。

## Phase B 離線方案判決（2026-09-07）

以 `dev/checklists/_work/all_chunks.json` 對三個失敗案例做 NFKC 後的中文二／三字元 IDF 排名，只用路由內片段，不調用外部服務：

- 非華語中史：指定目標片段由首 8 缺席升至 rank 0。
- 長期服務金：兩個完整公式片段分別為 rank 0 及 rank 4。
- 特殊學校：足以回答的相鄰 `g10` 片段進 rank 1，但 gold 指定片段只到 rank 12；短 query 的同詞片段大量同分。

因此 lexical overlap 能證明「先限制路由語料」有召回價值，但單獨作主排名會受短 query、重複表頭及同詞片段影響，不能直接上線。建議候選採以下次序：

1. 新增**獨立命名**的 route-first RPC，在 SQL 內先按 `source_id` allowlist 過濾，再對該子集作向量排序；不得修改或 overload 現有 `match_wiki_chunks(text, double precision, integer)`，避免重演 PGRST203 事故。
2. 現有全庫 ANN 保留為 fallback；新路徑須由預設關閉的 feature flag 控制，失敗時不得令 Channel B degraded。
3. lexical 只可作有限 rescue／tie-break 訊號，最多補一格，不能繞過一手來源政策、judge 或 grounded synthesis 閘。
4. 長期服務金跨頁 chunk 的頁碼歸屬另列 Phase B2；檢索召回改善不等於引用頁碼已修好。

正式啟用前最低證據：三題 fresh retrieval 全部讓目標答案片段進首 5；active gold 185 題 before／after 無 blocking regression；route regression、typecheck、build、grounded regression 全通過；再做至少兩次重複穩定性測試。現時 verdict 仍為 **FAIL**，兩個 feature flags維持 `0`。

Claude Code CLI 以既有 Plan session 作唯讀獨立覆核，結論為 **PASS-with-flags，無 code blocker**。它確認獨立 RPC 命名、欄位對應、零額外 embedding、flag-off 行為及 fallback 正確；提出 seqscan 隨語料增長及 `57014` 無重試兩項風險。候選其後補回與現行 RPC 相同的三次限定重試，並在 schema 記錄 17,602 片段基準；seqscan 效能仍須在實際安裝後量度，不能憑 code review 判定通過。
