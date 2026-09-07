# S214 — Phase 1.1「量度修正與決策證據」覆核報告

- **日期：** 2026-09-04
- **Claude session：** `Claude_20260904_1204`（S214）
- **Codex角色：** 接手完成評測及獨立QC
- **Active root：** `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`
- **基準HEAD：** `05ea10e`（本輪零commit、零push、零deploy）
- **生產邊界：** 沒有修改搜尋、排序、合成、backend或Supabase資料；外部操作只有唯讀查詢

## 1. 執行摘要

Phase 1.1五項工作已完成：

| 項目 | 結果 |
|---|---|
| A. canonical評測器NFKC修正 | PASS；self-test全綠，39條canonical查詢無blocking failure |
| B. 棄權機制實測 | 已量度；19條原有無答案題13條標準棄權，19條正向對照2條誤拒答 |
| C. forbidden來源實際影響 | 已量度；4／4進入首五格，1／4實際被答案採用並造成對象混淆 |
| D. 排序反事實測試 | 已完成；全域score sort有害，不建議更改生產排序 |
| E. Gold Set補足 | PASS；184／184標籤通過validator，四個薄弱領域全部達標 |

**評測交付 verdict：PASS WITH FLAGS。** 工具、資料及證據可供下一階段使用，但棄權Gold label仍有一條語義爭議，runner亦暴露一次HTTP 400包裝的SQL timeout。

**產品 release-quality semantic search verdict：FAIL。** 相同162題cohort的Source Recall@8仍是0.706，Chunk Recall@5仍是0.273，與S213完全相同；未有產品準確度改善證據。

## 2. A — canonical評測器NFKC修正

`dev/source/eval_retrieval.py`的片段比對現於兩邊先做NFKC folding，再移除空白；source slug比對沒有改動。

### 驗證結果

- `python3 dev/source/eval_retrieval.py --self-test`：**ALL PASS**。
- 正向測試涵蓋相容碼位與統一碼位互配。
- 負向測試涵蓋不同漢字、12／24班錯行及視窗邊界，未見過度正規化。
- 39條canonical live run：PASS 27、FAIL 0、RECORD_ONLY 12、errors 0。
- 與S213凍結基線比較：38條`SAME`；`kg_admission`只有第八格來源組成改變，沒有`VERDICT_REGRESSED`、`SET_LOST`或blocking failure。

證據：

- `dev/source/eval_runs/2026-09-04_s214_nfkc_after.json`
- 舊基線：`dev/source/eval_runs/2026-09-03_s213_phase0_baseline.json`

### 判斷

修正只影響片段判分的碼位等價性，沒有證據顯示source層行為受影響。A可接受。

## 3. B — 棄權機制實測

公開API只外露`results`與`synthesis`，不外露`judgeCanAnswer`或`trustedVaultLead`狀態。因此本輪量度的是可觀察結果，不推測內部判斷路徑。

### 測試組合

- 原有Gold Set無答案題：19條，全數以`synthesize:true`執行。
- 正向對照：19條，優先選同領域且舊基線chunk PASS的題目。
- forbidden addon：3條；第四條已包含在正向對照。
- 新修復的BYOD無答案題：另作1條addendum。
- 合計42次唯讀合成請求，errors 0。

### 嚴格結果

| 指標 | 結果 |
|---|---:|
| 原有無答案題使用標準`SYNTHESIS_DECLINE` | 13／19（68.4%） |
| 原有無答案題仍生成答案 | 6／19（31.6%） |
| 正向對照正確地沒有棄權 | 17／19（89.5%） |
| 正向對照誤拒答 | 2／19（10.5%） |
| 全部受測可答題誤拒答（含forbidden addon） | 3／22（13.6%） |
| BYOD addendum標準棄權 | 1／1 |

正向對照兩條誤拒答：

- `hr_lang_req`：預期來源沒有進首五格，系統棄權。
- `qa_esr_no_fixed_cycle`：預期來源在第0及第2格，仍然棄權，顯示judge未能從相關片段辨認可答性。

第三條可答題誤拒答是`ss_ncs_history_adapted`，屬forbidden addon，不應混入19條正向對照分母。

### 六條未用標準句棄權的無答案題

1. `gov_board_pay`：答案承認資料不足，但加入「通常須透明申報」等未獲片段支持的推論；屬軟性棄權兼帶推測。
2. `cur_arts_guide_2002_missing`：把2024／2003及其他藝術材料說成2002版內容；屬錯版本合成，風險高。
3. `gifted_no_academy_iq`：承認沒有明確分數門檻，但推測智商可能是因素；屬軟性棄權兼帶推測。
4. `ss_ncs_chinese_framework_missing`：`chi_edu_curr_docs`其實含第二語言學習架構說明；現有no-answer Gold label可能過時或定義過窄，須人工重審。
5. `bus_fee_noans`：承認沒有每月收費標準，但把一般非標準項目收費條件外推至校車；屬軟性棄權兼帶不穩妥建議。
6. `qa_kg_pi_na`：把只適用於中小學及特殊學校的表現指標套用到幼稚園；屬對象混淆，風險高。

### 判斷

系統具備棄權能力，但門檻校準未達封版要求：既有31.6%無答案題沒有使用標準棄權，亦有10.5%正向對照誤拒答。更重要的是，錯版本及錯對象答案仍可在語氣肯定的情況下輸出。

證據：

- `dev/source/eval_runs/2026-09-04_s214_synthesis.json`
- `dev/source/eval_runs/2026-09-04_s214_synthesis_byod_addendum.json`

## 4. C — forbidden來源實際影響

四條核心查詢均至少有一個forbidden來源進入首五格，但只有一條可證明答案實際採用了不適用材料。

| 查詢 | forbidden位置 | 正確來源 | 答案採用情況 | 判斷 |
|---|---|---|---|---|
| `sen_special_school_curriculum` | 2、4 | 未進首八格 | 採用一般融合教育及其他相近材料 | **對象混淆** |
| `ss_ncs_history_adapted` | 0、1、2 | 未進首八格 | 輸出標準棄權 | 未採用forbidden，但屬誤拒答 |
| `bus_guide_audience_confusable` | 1、3、5 | `g18`在第4格 | 答案內容來自給學校的`g18` | forbidden曝光，未見實際誤用 |
| `kg_sccc_ratio_confusable` | 1 | 正確來源在第0格 | 正確回答SCCC 1:14 | forbidden曝光，未見實際誤用 |

因此應分四層描述：

1. 結果窗曝光：4／4。
2. 首五格合成窗曝光：4／4。
3. 答案語義採用：1／4。
4. 已證實對象混淆：1／4。

不能再把`forbidden_hits`直接寫成「答案引用」。

## 5. D — 排序反事實測試

以原162題的8格候選離線重排，結果如下：

| 策略 | Source@1 | Source@8 | Chunk@5 | chunk MRR | forbidden@1 |
|---|---:|---:|---:|---:|---:|
| 現行forced-footnote | 0.364 | 0.706 | 0.273 | 0.184 | 1 |
| 全域score sort | 0.420 | 0.706 | 0.245 | 0.169 | 2 |
| exact提頭，其餘原次序 | 0.385 | 0.706 | 0.273 | 0.196 | 1 |
| footnote推到第4格起 | 0.378 | 0.706 | 0.273 | 0.157 | 2 |

結論：

- **不要採用全域score sort。** 它雖提升Source@1，卻降低Chunk@5及chunk MRR，並把`g19`禁用來源推到榜首。
- 唯一無損方案是「score ≥ 0.999 exact提頭，其餘不動」，但全庫只影響3題，證據量不足以改生產排序。
- 五種窗內重排的Source@8均為0.706，證明主要瓶頸是召回窗成員，而非單純次序。

## 6. E — Gold Set補足及擴充基線

### 標籤建設

新增21條可答題：

- `kg_admission`：+6。
- `kg_operation`：+4。
- `digital_education`：+4。
- `info_security`：+7。

另修正原有`dig_byod_mandatory_na`：absence probe由過廣的「自攜裝置」收窄為「強制推行自攜裝置」，並把非權威`role_facts_it`列作forbidden。該題因此重新通過validator並納入總集。

最終Gold Set：**184／184通過，隔離0**。

| 領域 | 總題數 | 可答題 |
|---|---:|---:|
| `kg_admission` | 10 | 10 |
| `kg_operation` | 10 | 9 |
| `digital_education` | 10 | 10 |
| `info_security` | 11 | 9 |

全部領域均達到「總題數不少於10、可答題不少於8」。

### 184題擴充基線

| 指標 | 結果 |
|---|---:|
| Source Recall@1／@3／@5／@8 | 0.402／0.585／0.671／0.732 |
| Chunk Recall@1／@3／@5 | 0.171／0.287／0.311 |
| Source MRR／Chunk MRR | 0.511／0.229 |
| 可答題PASS／FAIL | 120／44 |
| forbidden exposure | 5條查詢 |

新增21條可答題中，19條找到預期來源，2條失敗：

- `kg_result_notification_date`
- `dig_ai_fact_check_privacy`

新增題的source命中率為19／21，但片段簽名只有12／21進入首五格；同來源不等於正確段落。

### 可比性控制

用擴充run只抽回原有162題，結果與S213舊基線逐項相同：

- Source Recall@1／@3／@5／@8：0.364／0.552／0.636／0.706。
- Chunk Recall@1／@3／@5：0.119／0.245／0.273。
- Source MRR／Chunk MRR：0.474／0.184。
- PASS 101、FAIL 42。

所以184題數字較高是題目組合改變，不是產品改善；判斷產品回歸或進步時必須使用matched cohort。

### Reliability事件

184題初跑有1次`Supabase RPC statement timeout`，被endpoint包裝成HTTP 400，現有runner因此不重試。單題第二次請求成功，仍為檢索FAIL。

- 初次技術錯誤率：1／184（0.54%）。
- 重試成功：1／1。
- 風險：暫時屬偶發，但HTTP狀態分類會令可恢復錯誤繞過現有retry政策。

證據：

- 原始run：`dev/source/eval_runs/2026-09-04_s214_gold_expanded.json`
- retry：`dev/source/eval_runs/2026-09-04_s214_retry_fin_sci_grant.json`
- resolved run：`dev/source/eval_runs/2026-09-04_s214_gold_expanded_resolved.json`
- metrics：`dev/source/eval_runs/2026-09-04_s214_gold_expanded_metrics.json`
- matched cohort：`dev/source/eval_runs/2026-09-04_s214_legacy162_metrics.json`

## 7. 交給Claude Code的改善次序

### P0 — 先提高答案安全性

1. 在合成前加入對象／文件版本／適用範圍檢查。若問題指定年份、學校類型或服務對象，而首五格只有其他版本或其他對象，應棄權，不可用相近內容拼答案。
2. forbidden不應只在評測後記錄。建立query intent與source audience的相容檢查；正確來源缺席而禁用來源主導時，直接棄權或重新檢索。
3. 對生成答案做claim-to-chunk支持檢查；「資料沒有說明」後追加的推測、一般做法或建議，若沒有片段支持，應刪除或改為標準棄權。

### P1 — 校準棄權judge

4. 把本輪6條漏拒答、2條正向對照誤拒答及3條forbidden可答題建立成固定回歸集。
5. 重點查`qa_esr_no_fixed_cycle`：正確來源已在第0格但仍棄權，可能是judge prompt、片段截取或否定句理解問題。
6. 人工重審`ss_ncs_chinese_framework_missing` Gold label；在定案前不要用它調棄權threshold。

### P1 — 改善召回，不動全域排序

7. 優先處理`cpd_teacher_qualification`、`digital_education`、`curriculum`、`gifted`及`qa_inspection`；其Source Recall@5只有0.333至0.500。
8. 為年份、文件名稱、數字及對象詞加入lexical／metadata rerank訊號，並以chunk-level recall作主閘。
9. 不採用全域score sort。若研究exact提頭，先擴充至少數十條真正exact positive／negative controls，再做離線反事實及held-out驗證。

### P2 — Reliability與評測工具

10. backend應把Supabase statement timeout映射為可重試5xx，或runner識別HTTP 400內的`57014`／`statement timeout`再有限重試。
11. metrics必須把未解決error row計入可答題分母或明確輸出「不可比較」；本輪已用resolved run避免分母由164縮成163。
12. 將184題Gold Set、20條無答案題及本輪synthesis回歸集納入下一個release gate；舊162題cohort須繼續保留作趨勢比較。

## 8. Release判斷

以「系統信度及效度」作封版blocker標準，現階段不建議把語義搜尋標示為release-ready：

- 原162題約29%可答題連正確來源也未進首八格。
- 正確段落進首五格的比例只有27.3%。
- 棄權層可運作，但仍有錯版本及錯對象答案。
- forbidden來源進入合成窗的問題真實存在，且已證實一宗實際誤用。

建議下一里程碑不是大規模重入庫，而是先完成P0安全閘及P1棄權校準，再用相同162題cohort、184題擴充集及synthesis回歸集重新量度。只有在chunk-level效度與錯對象率達到預先定義門檻後，才重新作封版裁決。
