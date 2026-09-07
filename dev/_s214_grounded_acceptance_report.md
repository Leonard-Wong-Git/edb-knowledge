# S214 Grounded Synthesis Acceptance Report

日期：2026-09-05；治理對齊更新：2026-09-06  
狀態：本機候選；兩個 feature flags 預設關閉；未 commit、未 deploy

## Verdict

**FAIL（候選不可啟用）**。現行線上版本不受影響。

## 測試範圍

- Artifact：`dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_acceptance_v1.json`
- SHA-256：`939cd187aefb28d6c3605199eab83386b6a8f2074bec011c81449ded147e9351`
- 固定重播已保存 top-5 證據，不重新檢索、不連接 Supabase。
- 40 題原始 cohort：19 條 `no_answer`、19 條 `positive_control`、2 條 `forbidden_addon`；按 artifact 的 `expected_answerable` 為 19 條 false、21 條 true。
- 模型：draft=`gpt-4.1-nano`；judge=`gpt-4.1-mini`。
- Leonard 批准上限 80 次；artifact 記錄 56 次成功模型輸出（draft 40、judge 16）。當時 SDK 重試未關閉，實際 HTTP request 嘗試次數無法由 artifact 核證。

### Post-fix 第二批

- Artifact：`dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_acceptance_v2.json`。
- SHA-256：`d0ba44a2e8783aec24afbdaeb76b4092c5726d85db82c25c70ca1e7b0eb28bf6`。
- 使用相同 40 題及已保存證據；不重新檢索、不連接 Supabase。
- Leonard 另批最多 80 次 HTTP 嘗試；probe 專用 client 設 `maxRetries:0`，每次嘗試前先把計數寫入 artifact。
- 實際 `attempted_api_calls=54`，與 artifact 內 40 次 draft 加 14 次 judge 記錄完全相等；沒有隱藏 SDK 重試。

## 原始結果

| 分組 | 作答 | 棄權 | 原始命中 |
|---|---:|---:|---:|
| `expected_answerable=false` 19 題 | 2 | 17 | 17/19 棄權 |
| `expected_answerable=true` 21 題 | 13 | 8 | 13/21 作答 |

## Post-fix 第二批結果

| 分組 | 作答 | 棄權 | 原始標籤命中 |
|---|---:|---:|---:|
| `expected_answerable=false` 19 題 | 1 | 18 | 18/19 棄權 |
| `expected_answerable=true` 21 題 | 11 | 10 | 11/21 作答 |

這個表只反映原始標籤，不等於人工準確度。唯一負控作答 `ss_ncs_chinese_framework_missing` 已確認是 gold label 漂移：現有 `chi_edu_curr_docs` 第 20、28、30 頁確有直接資料。扣除該漂移後，18 條仍屬無答案的題目全部棄權。

第二批修正了三個既知高風險案例：`qa_kg_pi_na` 及 `sen_special_school_curriculum` 均安全棄權；`staff_fullday_12` 正確回答「小學學位教師 5 名（不包括副校長）」。原先四個只靠 `footnote_curated` 作答的案例，現因方案 A 不再以策展摘要支持答案；三項棄權，`fin_lwl` 則由 `vault_extract` 原文回答。

然而，第二批仍不能通過發布閘：

1. **Blocker — 原始抽取污染直接進入答案。** `ss_ncs_chinese_framework_missing` 的一手片段有大量四重複詞，答案逐字複製「教育局教育局教育局教育局」等內容。來源可追溯，但文字並非可發布質素。
2. **Blocker — 截斷句通過核證。** `qa_esr_no_fixed_cycle` 以「具正面成」完結，沒有回答「是否固定週期」，卻獲 judge 接納。這證明逐字存在、語意 judge 及適用對象三閘仍不足以保證句子完整和真正回應問題。
3. **Flag — 正控棄權上升。** 方案 A 把策展摘要降為檢索提示後，正控作答由 13/21 降至 11/21；其中一部分是預期的安全棄權，但仍有 evidence-window、抽取或生成召回缺口，不能把安全提升包裝成整體準確度提升。
4. **Flag — 模糊短 query 的驗收定義不足。** `gifted_talent_pool`、`act_national_edu_confusable` 等題目的 query 太短，artifact 的 `intent` 又沒有送入模型；部分答案可視為相關摘要，但未必符合 gold owner 想驗的具體事項。這些題目須先收緊 query 或明確 rubric，才可用於 release 分母。

## 人工覆核

1. **Blocker — 幼稚園對象混淆。** `qa_kg_pi_na` 問幼稚園，答案引用標題明列「中學、小學及特殊學校適用」的 2022 表現指標。Judge 明知未直接回答幼稚園仍把 `answers_any_part` 判為 true。
2. **Blocker — 特殊學校對象混淆。** `sen_special_school_curriculum` 問特殊學校課程調適，答案引用一般《小學教育課程指引》內對有特殊教育需要學生的課業安排，並推論為特殊學校政策。
3. **Blocker — 關鍵子類別遺漏。** `staff_fullday_12` 問「學位教師」，答案只列「助理小學學位教師 14 名」及總數，漏列同一精確行的「小學學位教師 5 名」。雖附部分回答提示，核心數字仍容易誤導。
4. **正控拒答偏高。** 原始標籤為 8/21；其中 `ss_ncs_history_adapted` 的 gold 定義另有矛盾，未重審前不應靜默改列負控。其餘七項：`hr_lang_req` 為 evidence-window failure；`ss_discipline_style_democratic`、`plc_central_alloc_confusable` 為 draft 未抽取直接內容；`ss_guidance_discipline_blend`、`plc_das_typo`、`cpd_mainland_promotion_tour`、`qa_esr_no_fixed_cycle` 為 citation／生成失敗。`qa_esr_no_fixed_cycle` 同時把原文「自」改成「由」，不只 citation index 錯。
5. **來源核證層級未統一。** 4 個作答案例只引用 `footnote_curated`。現有逐字核對只證明文字存在於策展片段，不等於已逐字核對原始 EDB 文件。啟用前須決定這類片段是可信二級證據，還是只可作 retrieval hint。
6. **評測標籤漂移。** `ss_ncs_chinese_framework_missing` 原標籤認定語料沒有答案，但現有 `chi_edu_curr_docs` 第 20、30 頁已直接描述第二語言學習架構與學習進程。該答案有直接原文支持；此項應由 gold owner 重審，不應計作系統 false answer。
7. **另一項標籤矛盾。** `ss_ncs_history_adapted` 在 artifact 標為可回答，但指定 gold 來源不在證據窗；現有一般中史指引又提及因應非華語學生需要作調適。Gold owner 須重新界定「可接受的一般調適」與「特定非華語中史框架」，重審前不計入 release 分母。
8. **文案質素。** `hr_lsp`、`gov_imc_60pct` 等答案直接複製策展片段中的提問句及粵語口語，不符合正式政策答案語氣；來源標題亦出現雙重《》包裹。

## 本輪後已完成的離線修正

- Judge schema 新增獨立 `applicable` 布林值；只有 relevant、supported、applicable 三者全真才可顯示。
- Prompt 明確禁止把中小學／特殊學校文件套用幼稚園，亦禁止把一般小學 SEN 內容推論為特殊學校政策。
- Citation index 指錯時，只在同一逐字引文於另一片段**唯一命中**時自動重綁；無效 index 或多重命中仍 fail closed。
- 來源標題先移除外層書名號，避免雙重《》。
- API probe 必須提供 `--approved-max-calls=N`，不足預算會在建立模型 client 前退出；Claude 不得執行該 probe。
- Probe 專用 OpenAI client 設 `maxRetries:0`；每次 HTTP attempt 前遞增並寫入 `attempted_api_calls`，超出批准上限即中止。
- 模型 claim 禁止換行及 `【】` 保留來源標記，防止仿冒 server citation。
- Grounded evidence window 從完整結果獨立選首五條 `vault_extract`，不再因前置策展摘要而只剩三條原文。
- 第二批後新增保守輸出衞生閘：80 字以下仍容許清單式短語；80 字或以上的 prose claim 必須有明確收句標點；任何 2–16 字元片語連續重複至少三次即拒絕。這兩項均在 judge 前 fail closed。
- 離線回歸由 34 增至 **47/47 PASS**；typecheck、build、`git diff --check` 通過。
- 以第二批 40 題 artifact 全量離線重播：只改變兩個目標 blocker，`ss_ncs_chinese_framework_missing` 與 `qa_esr_no_fixed_cycle` 均改為安全棄權；其餘 38 題逐字不變。
- 路由回歸 46/46 PASS。既有 semantic regression 為 24 PASS、1 PASS-with-notes、1 FAIL；唯一 FAIL 是測試仍保留舊 `guidelines 2.5.0` 常數而權威值已為 2.6.1，與本次 helper 改動無關，未在此範圍順手修正。

## 尚未完成

- 方案 A 已完成一次外部模型 post-fix 重跑；該批揭示的兩個輸出 blocker 已有離線決定性防線，但尚未經新模型批次驗證。
- `ss_ncs_chinese_framework_missing` gold label 尚未由 owner 重審。
- `ss_ncs_history_adapted` 的可接受答案邊界尚未由 owner 定案。
- 三個 Codex 子代理第二輪覆核均因額度上限未能執行；不能聲稱已完成獨立 agent QC。
- 排序／檢索的全套 end-to-end release gate 尚未完成。

## `footnote_curated` 證據資格決策

- **A（建議，短期）：** grounded synthesis 只准原始 `vault_extract`／可驗證一手片段成為最終 claim 證據；`footnote_curated` 只作 retrieval hint。代價是部分答案會暫時棄權，但來源聲稱最穩妥。
- **B：** 保留策展 footnote 作二級證據，但 UI 必須標示「策展摘要」，不可包裝成原始文件逐字核證。召回較高，但信度低於 A。
- **C（建議，長期）：** 為每條策展 footnote 補存原始 EDB 逐字引文、頁碼及可機械重驗欄位；驗證通過後才升格為一手證據。成本最高，但兼顧召回與可追溯性。

建議採 **A → C**；不要在未標示的情況下沿用現狀。

**決策結果：Leonard 已於 2026-09-05 批准先做 A。** 候選現已只准 `vault_extract` 支持最終 claim；策展摘要仍可出現在搜尋結果，但不會送入 grounded synthesis 證據窗。C 留作後續語料提升，不屬本輪啟用前最低修正。

## 下一個 Gate

覆核棄權成因時另發現 acceptance harness 先 `.slice(0,5)` 才移除策展摘要，與生產的「先篩一手文件，再取五格」不一致；18／40 題證據窗受影響。此 blocker 已以共用 `selectPrimaryEvidence()` 修正，回歸 48／48，但舊 v1／v2 artifact 均須標示為 harness-confounded。完整證據、NCS 重審及 rubric 選項見 `dev/_s214_gold_abstention_review.md`。

1. Gold owner 重審已完成：active gold 184→185；兩條舊 NCS 完整移入 deprecated audit 檔，兩條 replacement 及四條 rubric 修訂已落地，本次七條最小 cache 驗證 7/7 通過。
2. 修正後 18 題已完成：25／36 次 HTTP，不可答題 9／9 棄權、可答題 6／9 作答；artifact 含 evidence-window fingerprint。
3. 兩條新 NCS 及另外三條缺口的新 retrieval fixture 已建立；發現中史 NCS 漏 route allowlist、特殊學校 `g10` 仍未入首 8、長期服務金只有部分公式、校董 60% gold 標籤錯誤。詳見 `dev/_s214_grounded_v3_review.md`。
4. 完成獨立 agent／Claude Code CLI 覆核。
5. 在新模型驗收與重複穩定性測試完成通過前，`FEATURE_GROUNDED_SYNTHESIS` 維持 `0`；不 commit、不 push、不 deploy。

## V3 修正證據窗重驗（2026-09-06）

Leonard 批准 OpenAI Responses API 最多 36 次 HTTP；實際使用 25 次（18 draft＋7 judge，`maxRetries:0`）。18 題及 18 個 evidence-window fingerprint 全部落盤。無答案題 9/9 安全棄權；可答題 6/9 作答，其中 4 題完整、2 題安全部分回答，沒有不合適對象、OCR 重複或截斷答案。`hr_lsp`、`sen_special_school_curriculum` 仍因目標片段未進窗而棄權；`gov_imc_60pct` 的 evidence 源自舊 query，不能按新 rubric 判分。Verdict 維持 FAIL。逐題證據見 `dev/_s214_grounded_v3_review.md`。
