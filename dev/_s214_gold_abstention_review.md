# S214 Gold／棄權成因覆核（2026-09-06）

## 結論

**Verdict：FAIL（驗收 harness blocker）。** 第二批 40 題 acceptance artifact 不可直接用作 release 判決。`backend/scripts/groundedSynthesisProbe.ts` 當時先取首五項，再移除 `footnote_curated`；生產路徑則先篩出 `vault_extract`，再取五項。兩者不一致，令 18／40 題的模型證據窗少於生產應有的一手文件，至少直接排除了 `hr_lsp` 的 `long_service_payment_guide` 及 `hr_lang_req` 的 `edbcm088_2026`。

現已把一手證據選窗抽成 `selectPrimaryEvidence()`，由生產及 probe 共用；生產行為不變。`regression:grounded` 48／48、typecheck、build 及 `git diff --check` 通過。舊 artifact 保留作歷史證據，但其答案率及棄權率須標示為 **harness-confounded**。

## Harness 影響範圍

18 題的 evidence window 會因正確次序而改變：

`staff_sp_school`、`hr_teacher_reg_fee`、`fin_crypto`、`hr_overtime`、`ss_ncs_fee_remission_missing`、`bus_fee_noans`、`act_eca_min_hours_na`、`cpd_induction_period_na`、`qa_kg_pi_na`、`staff_fullday_12`、`hr_lsp`、`fin_lwl`、`gov_imc_60pct`、`hr_lang_req`、`cur_kg_free_play_time`、`saf_disease_notification`、`staff_halfday_12`、`sen_special_school_curriculum`。

不可把舊 draft／judge 輸出套入新窗，因證據編號及內容已改變。probe 已新增 `--acceptance-affected`，精確選取這 18 題；上限為 36 次 HTTP 嘗試（每題最多 draft＋judge），每題會保存 evidence-window SHA-256 fingerprint。未提供批准參數時，工具會在建立模型 client 前停止。執行前仍須另取 Leonard 明確批准。

## NCS Gold 重審

### `ss_ncs_chinese_framework_missing`

- 舊標籤：`answerable=false`，理由只核對錯置的 `g09`。
- 現有證據：`chi_edu_curr_docs` 第 20、28、30 頁直接說明「中國語文課程第二語言學習架構」、循序漸進學習目標、四個範疇及預期學習表現。
- 判斷：舊「無答案」前提已失效。不能再計作 false answer。
- 建議：保留舊案例 ID 作 deprecated audit record；新增版本化案例，以完整問題取代關鍵詞，例如「中國語文課程第二語言學習架構如何描述非華語學生的學習進程及四個學習範疇？」；expected source 納入 `chi_edu_curr_docs`，並用去除 OCR 重複後仍可在原文核證的 passage signature。

### `ss_ncs_history_adapted`

- 舊查詢：「非華語學生 中國歷史 課程」。
- 舊規則：只接受 `chi_hist_jss_ncs_2019`，並禁止 `chi_hist_jss_2019`。
- 現有證據：一般《中國歷史科課程指引（中一至中三）》第 25 頁直接寫明教師可因應非華語學生的興趣及文化背景，調適政治演變、文化特色及香港發展課題。
- 判斷：查詢本身足以由一般指引回答「調適原則」；把該來源一律列為禁引，與查詢字面衝突。
- 選項 A：若測試一般調適政策，接受 `chi_hist_jss_2019` 為有效替代來源。
- 選項 B（建議）：若目標是專門調適課程大綱，重寫為「非華語學生適用的調適初中中國歷史課程大綱，對指定歷史課題提出哪些建議學習內容？」並保留 `chi_hist_jss_ncs_2019` 為指定來源；一般指引可回答調適原則，但不能代替具體大綱內容。

## Rubric 漂移

以下案例的 query 與隱藏 intent／signature 並不完全相同；Leonard 已批准按建議修訂：

| ID | 問題 | 建議 |
|---|---|---|
| `gov_imc_60pct` | query 只問上限，intent 另加「替代校董是否計算」；signature 是策展提問句，不是政策答案 | 拆成兩個明確問題，signature 改用一手條文 |
| `hr_lang_req` | query 只問英文教師，intent 同時要求普通話；signature 只是通告標題 | 只驗英文教師，並指定實質能力要求原文 |
| `saf_disease_notification` | query 只寫「傳染病 通報」，intent 隱含通報單位及電話 | 明寫「學校爆發傳染病時須向哪個單位通報，聯絡方法是甚麼？」 |
| `plc_central_alloc_confusable` | query 問統一派位編位方法，signature 只說自行分配學位成功者不再參加統一派位 | 改問該規則，或另選真正描述統一派位編位方法的 signature |

關鍵詞式查詢本身可以保留作真實用戶行為測試；但 acceptance rubric 不可加入查詢沒有表達的第二個必答事項。

## 棄權成因

以下按修正後守門邏輯重播舊模型輸出，只用作定位，不是新的模型驗收：

- **正確無答案棄權：18 題。** 17 題在 draft 階段輸出空 claims；`dig_edb_cloud_guideline_na` 由 judge 拒絕四項不合題 claims。
- **標籤漂移＋輸出衞生：1 題。** `ss_ncs_chinese_framework_missing` 實際可答，但舊答案含連續 OCR 重複，現由 deterministic guard 在 judge 前拒絕。
- **生產應有證據未進舊 harness window：至少 2 題已直接證實。** `hr_lsp`、`hr_lang_req`。其餘受影響題須以修正後窗重新跑，不能沿用舊棄權原因。
- **正確來源／目標片段未進五格：** `ss_ncs_history_adapted`、`kg_sccc_ratio_confusable`、`sen_special_school_curriculum`；其中最後一題的 judge 正確拒絕把一般小學 SEN 指引套用特殊學校。
- **目標原文已在窗但 draft 留空：** `ss_discipline_style_democratic`、`plc_central_alloc_confusable`、`cpd_mainland_promotion_tour`。這三題是 draft recall 問題，而非 judge 誤殺。
- **引用核對失敗：** `saf_disease_notification` 的 draft 產生 claim，但逐字 quote 未在提供片段內命中，故 judge 前 fail closed；同時其指定 CHP 原文亦被舊 harness 的策展摘要佔位排除。
- **輸出截斷守門：** `qa_esr_no_fixed_cycle` 的舊 claim 句尾停在「具正面成」，現由 deterministic guard 在 judge 前拒絕；它仍未回答「是否固定週期」。

## 下一個 Gate

Leonard 已批准 gold 建議並完成落地：兩條舊 NCS 移至 `dev/source/gold_deprecated_s214.json`，active set 加入兩條 versioned replacement；四條 rubric drift 已修訂，校董雙重事項拆成兩題。Active gold 184→185，ID 185/185 唯一；本次七條以保存 evidence 及本地 extract 建最小 cache 驗證 7/7 通過。原全庫 cache 路徑已失效，故未連接 Supabase 重建；完整 185 條 corpus revalidation 尚待新的唯讀 snapshot。

1. 以修正後 harness 重跑受影響 18 題；執行前提交服務、模型及最高 36 次 HTTP 供 Leonard 批准。
2. 兩條新 NCS replacement 須先建立與新 query 對應的 retrieval fixture，不能沿用舊 query 的結果窗。
3. 新 artifact 已會記錄 evidence-window fingerprint；probe 與生產亦已共用 `selectPrimaryEvidence()`。
4. 新模型結果完成後，再做獨立 agent QC，才可更新 release verdict。
