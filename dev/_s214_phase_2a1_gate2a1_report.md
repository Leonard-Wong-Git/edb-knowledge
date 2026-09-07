# S214 Gate 2A1 / 2A1b — 證據報告（已按 Codex QC 修訂）

> **修訂記錄**：Codex 第二次 QC 判 FAIL，指出兩點：(a) §5b 把 forbidden@1（1→2）寫成「因應窗內重排而變動、屬可合法變動」是錯的——Gate 1 §8 明文規定 forbidden@1／@top3 不得上升，此為第二個硬閘違反，非可變指標；(b) 逐題排查顯示全域 score-sort 令多條 gold 答案註腳被降級（`hr_lsp`／`hr_severance`／`fin_ac_grant`／`gov_imc_60pct`／`gov_imc_pta`／`gov_coa_imc`／`kg_subsidy_eligibility`）。兩點均已核實成立，**原 §5b／§6 判斷保留作記錄，但不再視為結論**——結論見新增 §7／§8。原「PROPOSED」正名為 **BROAD-SCORE-SORT（已否決）**，新增 **EXACT-ONLY** 變體重新評估。

- **Session:** `Claude_20260904_1204` — S214
- **範圍：** 測試與量度基建。**未激活新排序邏輯**，生產零改動。
- **邊界：** 零 Supabase 寫入、零重入庫、零 commit/push/deploy、未改門檻／judge prompt／路由／source sets／生產排序。

---

## 0. Codex 修正已接受

T4 不再斷言合資格單一註腳必然不在 index 0。改為：仍在 `top min(5, top_k)` 內，且所有分數較高的入選窗成員都排在它之前。若它本身就是全場最高分，index 0 正確。已實作並通過（見 §2 T4）。

---

## 1. 交付物與檔案清單

| 檔案 | 性質 | 內容 |
|---|---|---|
| `dev/_s214_rank_model.py` | 新增 | 純合併模型（`merge_current`／`merge_proposed`（BROAD-SCORE-SORT，已否決）／`merge_exact_only`）+ 51 條自我測試 + fidelity 檢查器 |
| `dev/source/footnote_lead_probe.py` | 修改 | 新增 `window_of()`，每列加 `window` 欄位（記錄 top-8 全部 id/source_id/content_type/score），舊欄位一字不改；自我測試加 5 條斷言 |
| `dev/_s214_gate2a1_replay.py` | 新增 | 離線三方重放（CURRENT／BROAD-SCORE-SORT／EXACT-ONLY），區分「可算」與「不可算」指標，含逐題劣化掃描與 establishment 查詢逐一驗證 |
| `dev/source/eval_runs/2026-09-04_s214_gate2a1_footnote_probe.json` | 新增 | 43 條唯讀 live 探針（26 正控 + 4 可答對照 + 13 負控），全新時間戳，未覆寫 `2026-07-28_s196_fnlead_final.json` |
| `dev/source/eval_runs/2026-09-04_s214_gate2a1b_replay.json` | 新增 | 三方離線重放輸出（184 題 + establishment 逐題明細 + 兩份九題探針）。**取代**同節較早產出、已刪除的 `2026-09-04_s214_gate2a1_replay.json`（僅含 CURRENT／BROAD-SCORE-SORT 兩方，資訊已完整併入本檔） |

**為何模型落在 Python dev harness，不是 TypeScript 抽取**：`backend/package.json` devDependencies 只有 `@types/node`／`tsx`／`typescript`，scripts 只有 `dev`／`build`／`check`（`tsc --noEmit`）／一支 `tsx` 回歸腳本，全倉庫零 `jest`／`vitest`／`node:test` 用例。落地 T1–T14 為 TS 測試等於幫生產 `package.json` 加測試框架 —— 這是依賴變更，超出「最小模型」範圍，亦非 Gate 2A1 授權。Python 模型改為**規格文件**：Gate 2B 若要落地 TypeScript，須對同一批斷言驗證,不是另起爐灶。

---

## 2. T1–T14（含修正後 T4）

```
python3 dev/_s214_rank_model.py --self-test
```

**42/42 PASS**（40 條 T1–T14 + 2 條 §3 heuristic 專項；本節之後 §7 再加 9 條 EXACT-ONLY 專項，最終 51/51）。T4 修正後三條斷言：
- 低分合資格註腳仍在 `top min(5,top_k)` 內
- 窗內所有分數較高成員排在它之前
- 全場最高分的合資格註腳**容許**在 index 0（新增，防止過度修正）

---

## 3. `footnote_lead_probe.py` 擴充

新增 `window_of()`：擷取 `results` 全部項目的 `id`／`source_id`／`content_type`／`score`，原順序不變（被動記錄器，非重排）。接入兩個既有迴圈（curated-footnote 正控迴圈 + 負控／對照迴圈），每列加一個 `window` 欄位，**舊欄位（`class`／`query`／`want_source`／`lead_source`／`lead_score`／`lead_overlap`／`kept`）全部原封不動**。

```
python3 dev/source/footnote_lead_probe.py --self-test
```
**PASS**（含 5 條新斷言：保序、四欄完整、分數四捨五入一致、空回應、缺分數容錯）。

---

## 4. 新鮮 43 條唯讀探針

**預計呼叫量（事後對照）**：26 條正控（`sample_every=8` × 206 條註腳語料）+ 4 條可答對照 + 13 條負控（10 plausible_gap + 3 s196）= **43 次唯讀 `synthesize:false` 搜尋呼叫**，帶 `x-probe: 1`（既有機制，不計入用量計數），節奏 7 秒/次，實際耗時約 5 分鐘，`errors: 0`。

```
python3 dev/source/footnote_lead_probe.py --run --pace 7 \
  --out dev/source/eval_runs/2026-09-04_s214_gate2a1_footnote_probe.json
```

**結果**：
- 正控（30 條，含 4 條可答對照）：**30/30 取得 lead**（100%）
- 負控（13 條）：**5/13 仍取得 lead**（38.5%）
- `positive lead_score`：min 0.5378 / median 0.7482 / max 0.9097
- `negative lead_score`（仍取得 lead 的 5 條）：min 0.5058 / max **0.6005**

**與 S196 舊基線（2026-07-28）比較**：

| | S196（舊，2026-07-28） | 本次（新鮮，2026-09-04） |
|---|---|---|
| 正控 | 26/26 | 30/30（含 4 條新增可答對照） |
| 負控仍取 lead | 7/15（46.7%） | 5/13（38.5%） |
| 正負分數重疊 | 正下限 0.6061 vs 負上限 0.7213 | 正下限 0.5378 vs 負上限 0.6005 |

**Gate 1 §2 的結論獨立覆核成立**：兩個時間點的資料都顯示**正負分佈重疊**（負控最高分 ≥ 正控某些較低分），即**純提高 `FOOTNOTE_LEAD_SCORE` 門檻在數學上仍不可行**。負控仍取 lead 的比例本次略低（38.5% vs 46.7%），但重疊區間依然存在，不構成「問題已消失」的證據——樣本語料與判斷方式跨兩個月，差異可能來自語料本身變動（新增 footnote／新增來源），非本次確認。

---

## 5. 離線重放：CURRENT vs PROPOSED

```
python3 dev/_s214_gate2a1_replay.py > dev/source/eval_runs/2026-09-04_s214_gate2a1_replay.json
```

### 5a. Fidelity（模型是否忠實重現生產已記錄輸出）—— 過程中發現並修正一個真缺陷

初跑：184 題 174/184（94.6%）。逐條排查 10 條 mismatch，找到根因並修正：

**根因**：`classify_recorded` 的 spotlight 判斷式原本是「lead 之後那格的 source_id 在 `SPOTLIGHT_SOURCE_IDS` 內即判定為 spotlight」。但 `staff_est_pri`／`edbcm116_2026` 等來源**本身也會憑真實分數贏得第一名**，此時判斷式誤判，令該候選在 `merge_current` 的 spotlight 可見度過濾中被錯誤排除，整條記錄少一格。

**修正**：改為「該格分數必須**低於**其後某一格的分數」才算 spotlight（真正的插隊才會製造這種分數倒序；巧合登上第一名者，其後不會有更高分）。

**修正後**：184 題 **180/184（97.8%）**，6 個計數缺漏全部修好；新增 2 條正向／負向自我測試鎖住此行為，防止回歸。

**三個獨立樣本的加總 fidelity**（有 `content_type` 可判讀者）：

| 樣本 | n | reproduced | 比例 |
|---|---:|---:|---:|
| 184 題（生產 eval run） | 184 | 180 | 97.8% |
| 9 題（live synthesize 探針） | 9 | 8 | 88.9% |
| 43 題（本節新鮮 footnote 探針，交叉驗證） | 43 | 41 | 95.3% |
| **合計** | **236** | **229** | **97.0%** |
| 4 題（atomic follow-ups） | 4 | — | **NOT_COMPUTABLE**（該檔缺 `content_type`，無法判別 footnote／vault/establishment） |

**殘餘 7 條 mismatch，全部已定性、無新類型**：
- **5 條為分數完全相等的並列**（如兩格皆 0.7284、皆 0.7518）：本模型的 tie-break 是 `id` 升序（T2 要求的確定性選擇），**不聲稱**重現生產的實際並列次序——生產的並列排序依據不明（可能是資料庫／RPC 回傳順序），本節未進一步追查。已寫入 `classify_recorded` docstring 明確標示為「不可還原」。
- **2 條為同一根因的獨立重現**：`fin_seg`／`edu_sen_lsg_outsource` 兩條互不相干的查詢都出現 `edbc015_2026` 排在明顯更高分結果之前，且該來源不在 spotlight 名單、亦非並列。**此為未解釋的生產行為**，非本模型或本次修正範圍可解，建議列入 Gate 2B 待查項——兩次獨立出現同一來源，值得追查而非視為雜訊。

### 5b. 可算 vs 不可算指標（按 Codex 要求，不推論）

**184 題（parallel-array schema，有完整 gold 標籤，含 26 條 `acceptable_alternatives`）—— 全部可算**：

| 指標 | CURRENT | PROPOSED |
|---|---:|---:|
| Source Recall@1 | 0.4024 | **0.4573** |
| Source Recall@3 | 0.5915 | 0.5793 |
| Source Recall@5 | 0.6707 | 0.6707 |
| Source Recall@8 | 0.7317 | 0.7317 |
| Source MRR | 0.5111 | 0.5380 |
| Chunk Recall@1 | 0.1707 | 0.1524 |
| Chunk Recall@3 | 0.2866 | 0.2622 |
| Chunk Recall@5 | 0.3110 | 0.3110 |
| Chunk MRR | 0.2291 | 0.2143 |
| forbidden@1 | 1 | 2 |
| forbidden@top3 | 4 | 3 |
| exact score=1 命中（3 條） | 全部被壓 | **全部移到更低 index**（3/3 改善，0 不變，0 變差） |

n_answerable_scored = 164（184 題中 20 條為無答案題，正確排除）。

**⚠️ 本節判斷已被 Codex QC 推翻，原文保留供對照，見 §7／§8 為準。** 原判斷把 forbidden@1（1→2）寫成「屬可合法變動」——**這是錯的**。Gate 1 §8 明文：forbidden@1／@top3 屬硬閘，不得上升。BROAD-SCORE-SORT 同時違反**兩個**硬閘，不是一個：

- **Chunk Recall@3**：0.2866 → 0.2622（**降幅 0.0244，硬閘違反**）
- **forbidden@1**：1 → 2（**上升，硬閘違反**）——`sen_special_school_curriculum` 一題把禁用來源 `g19` 由第 2 格推到**第 0 格**，即全域分數排序把一個對象錯誤的來源送上榜首。

逐題排查（見 §7 的系統性掃描）另外顯示，全域 score-sort 令 **13 條**（非僅 Codex 點名的 7 條）gold 答案來源的排名劣化，全部集中在**依賴註腳作答**的查詢——這證實了 Gate 1 D 項「不得只以 Recall@1 選方案」的警告不是理論擔憂，而是本次唯一被否決方案的真實代價。

**9 題探針（nested schema，live probe，無 gold 標籤）—— Source/Chunk Recall NOT_COMPUTABLE**（無 `expect_any`，此為 Codex 明確要求：不可推論）；**可算的結構性事實**：8/9 CURRENT 忠實重現；3 條 exact score=1 命中，PROPOSED 下全部移至更低 index（與 184 題結果方向一致）。

**Atomic 4 題 —— NOT_COMPUTABLE**（缺 `content_type`，連結構性重放都做不到，非僅指標缺失）。

---

## 6. BROAD-SCORE-SORT 的 GO / NO-GO：**NO-GO（維持，理由已修正）**

違反**兩個**硬閘（Chunk Recall@3 下降、forbidden@1 上升），且逐題掃描顯示 13 條查詢的 gold 答案排名劣化。不建議以任何形式採用全域分數排序，包括「先修正 forbidden 曝光再重評」——問題是設計本身（重排整個窗）而非參數調校可解決。

---

## 7. Gate 2A1b — EXACT-ONLY 變體（Codex 指定的最小生產改動）

### 7.1 設計：只改一步，不碰其餘

`dev/_s214_rank_model.py` 新增 `merge_exact_only()`——與 `merge_current()` 逐行相同，**唯一差異**在 establishment 插入點：現行生產把 establishment 插在 `forcedLeads`（即已有的註腳／spotlight lead 之後）；本變體改插在**結果列表最前端**，`forcedLeads` 同步加總。footnote pass 與 spotlight pass **逐字複製，未改一行**。

**`results[forcedLeads]` 不變式由構造保證，非另加機制**：無論 establishment 插在最前或插在原位，`forced` 都同步遞增相同數量，故 `results[forced]`（即主搜尋 lead）恆等於未經任何 overlay 觸碰的 `rest[0]`。**因此本變體不需要 Gate 1 §4 提出的 `mainSearchLead` 簽名改動**——按 Codex 指示，未引入。

去重、statistical 過濾、fail-open try/catch 語意全部原封不動。

### 7.2 測試

新增 9 條自我測試（worked-example 移位、established-behind 次序守恆、footnote 相對次序不變、top_k 多重集守恆、`results[forcedLeads]` 不變式顯式驗證、establishment 內部次序 pass-through 而非另行排序、多條 establishment 列同時前置、establishment 為空時與 CURRENT 完全相同）。

```
python3 dev/_s214_rank_model.py --self-test
```
**51/51 PASS**（40 條原有 T1–T14 + 2 條 spotlight heuristic 專項 + 9 條 EXACT-ONLY 專項）。

### 7.3 184 題離線重放：三方比較

```
python3 dev/_s214_gate2a1_replay.py > dev/source/eval_runs/2026-09-04_s214_gate2a1b_replay.json
```

fidelity 不變（180/184，97.8%——EXACT-ONLY 與 BROAD-SCORE-SORT 共用同一份已修正的 CURRENT 模型與 candidate 重建邏輯，不重新引入 fidelity 問題）。

| 指標 | CURRENT | BROAD-SCORE-SORT（已否決） | **EXACT-ONLY** |
|---|---:|---:|---:|
| Source Recall@1 | 0.4024 | 0.4573 | **0.4207** |
| Source Recall@3 | 0.5915 | 0.5793 | **0.5915**（不變） |
| Source Recall@5 | 0.6707 | 0.6707 | **0.6707**（不變） |
| Source Recall@8 | 0.7317 | 0.7317 | **0.7317**（不變） |
| Source MRR | 0.5111 | 0.5380 | **0.5223** |
| Chunk Recall@1 | 0.1707 | 0.1524（↓） | **0.1890（↑）** |
| **Chunk Recall@3** | 0.2866 | **0.2622（↓ 硬閘違反）** | **0.2866（不變，過閘）** |
| Chunk Recall@5 | 0.3110 | 0.3110 | **0.3110**（不變） |
| Chunk MRR | 0.2291 | 0.2143（↓） | **0.2403（↑）** |
| **forbidden@1** | 1 | **2（↑ 硬閘違反）** | **1（不變，過閘）** |
| forbidden@top3 | 4 | 3 | **4**（不變） |

**EXACT-ONLY 通過兩個硬閘；BROAD-SCORE-SORT 兩個都違反。**

### 7.4 為何指標幾乎全數不變——結構性原因，非巧合

184 題中只有 **3 條**觸發 establishment overlay（`staff_fullday_12`／`staff_halfday_12`／`staff_halfday_24`）。`merge_exact_only` 對沒有 establishment 候選的查詢，`est` 為空列表，`if est:` 分支不執行，**輸出與 CURRENT 逐字元相同**。故 181/184 條查詢的任何指標貢獻與 CURRENT 完全一致，差異只可能來自那 3 條——這解釋了 Source@3／@5／@8 與 Chunk@5／forbidden@top3 為何精確不變（那 3 條本來就不受影響或影響方向恰好抵消），也解釋了 Chunk Recall@1 為何**改善**（3 條 established chunk 由原本 index 1–2 移到 index 0，符合期望）。

### 7.5 逐題系統性掃描：BROAD-SCORE-SORT 13 條劣化，EXACT-ONLY 零劣化

對全部 164 條可答題逐一比較 `source_rank`（不只是 Codex 點名的 7 條）：

**BROAD-SCORE-SORT 令 13 條查詢的來源排名劣化**（含 Codex 點名全部 7 條 + 另外 6 條新發現）：

| 查詢 | current rank | broad_score_sort rank |
|---|---:|---:|
| `hr_lsp` | 0 | 3 |
| `hr_severance` | 0 | 4 |
| `hr_ncs_allowance` | 1 | 2 |
| `fin_ac_grant` | 0 | 3 |
| `gov_imc_60pct` | 0 | 1 |
| `gov_imc_pta` | 0 | 4 |
| `gov_imc_setup` | 0 | 1 |
| `gov_coa_imc` | 0 | 3 |
| `gov_imc_quorum` | 0 | 1 |
| `ss_ncs_summer_bridging_grant` | 0 | 2 |
| `kg_reg_fee_cap` | 0 | 1 |
| `kg_subsidy_eligibility` | 0 | 3 |
| `kg_equal_admission_opportunity` | 1 | 4 |

**EXACT-ONLY：以上 13 條全部維持 CURRENT 的排名，0 條劣化**（因為 EXACT-ONLY 完全不碰註腳／spotlight 的相對次序，只移動 establishment）。

### 7.6 三條 establishment 查詢逐一驗證

| 查詢 | CURRENT index | BROAD-SCORE-SORT index | EXACT-ONLY index |
|---|---:|---:|---:|
| `staff_fullday_12` | 2 | 0 | **0** |
| `staff_halfday_12` | 2 | 0 | **0** |
| `staff_halfday_24` | 1 | 0 | **0** |

三條與 BROAD-SCORE-SORT 效果相同（exact match 移到 index 0），但 EXACT-ONLY 達成同樣效果**不需要重排窗內其餘任何一格**。

---

## 8. 最終 GO / NO-GO

### BROAD-SCORE-SORT：**NO-GO**（不可逆轉——設計本身有害，非參數問題）

### EXACT-ONLY：**GO（進入 Gate 2B 實作驗證），附三個前置條件**

**判斷依據**：184 題真實資料顯示 EXACT-ONLY 通過 Gate 1 §8 定義的全部硬閘（Chunk Recall@3／@5 不降、forbidden@1／@top3 不升），在 164 條可答題的逐題系統掃描中零劣化，且達成與 BROAD-SCORE-SORT 相同的 establishment 修正效果（3/3 exact match 移至 index 0），但代價是零——因為它只觸碰 184 題中的 3 題，其餘 181 題輸出與 CURRENT 逐字元相同（§7.4 結構性保證，非統計巧合）。

**GO 之前必須完成（Gate 2B 範圍，本輪不做）**：
1. **Live 驗證**：39 條 canonical baseline `--compare`；184 題 gold set live 重跑；3 條 establishment 查詢 live 驗證 exact match 落在 index 0；19 條無答案題 + 19 正控 `synthesize:true`（確認棄權層未受影響——EXACT-ONLY 不改變 `trustedVaultLead` 的判定對象，但仍須實測，不可只憑推導）。
2. **註腳正向對照集**：S196 的 26 條（+本節新鮮驗證的 30 條）必須零跌出 top-5——理論上 EXACT-ONLY 不觸碰註腳次序，應為 0 跌出，但這是「必須量度」而非「已經量度」的項目。
3. **實作對照**：TypeScript 落地時逐條核對 `dev/_s214_rank_model.py::merge_exact_only` 的 12 條專項斷言，確保生產程式碼改動範圍與模型描述的「只改 establishment 插入點一行」精確一致，不可在實作時不慎擴大改動範圍。

**明確排除**：`mainSearchLead` 簽名改動（Gate 1 §4）**不需要**用於本變體，若 Gate 2B 決定日後改用其他變體才需重新評估。

**未解事項（不阻塞 EXACT-ONLY，但需追蹤）**：
1. `edbc015_2026` 兩次獨立排序異常（非並列、非 spotlight、非本變體改動範圍）——列入 Gate 2B 待查項。
2. 5 條 tie-break 並列差異——已記錄為模型已知限制，不影響本判斷（EXACT-ONLY 不改變任何並列的相對次序）。
3. `dig_ai_fact_check_privacy`／`kg_result_notification_date`——與本輪無關。
