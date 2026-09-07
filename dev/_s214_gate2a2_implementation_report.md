# S214 Gate 2A2 / 2A2b — 生產程式碼實作證據

- **範圍：** 落地 EXACT-ONLY 變體，其後按 Codex 兩輪 live 行為 QC 的 FAIL 結果各修正一個真缺陷（§0–§4 為第一輪 dedup 方向；§7 為第二輪同表衝突列移除）。**仍未跑 184 live 套件**（按 Codex 指示，留待 Codex 先 QC 本地改動）。
- **邊界：** 零 Supabase 寫入、零重入庫、零 commit/push/deploy。

---

## 0. Codex Gate 2A2 local 行為 QC：FAIL，已修正

**Codex 用真實 local backend 跑 `staff_fullday_24`（「24班小學編制」）發現的缺陷**：

- 正確 exact chunk `vault_staff_est_pri_58f262551ffa` **已經**由 ANN 在 rank 2（cosine 0.5288）出現。
- `searchEstablishmentRows` 對同一 chunk 回傳 score=1 的版本，但 Gate 2A2 遺留的 `seenIds` 過濾（`.filter((r) => !seenIds.has(r.id))`）因為該 id **已在 `results` 內**而把它篩走，新的前置邏輯因此從未收到它。
- Rank 0 仍是另一條 `staff_est_pri` chunk（0.5758），合成答案講「大約40」，並聲稱文件無明確列出數字——但 exact 那行**明文寫住總數 40**。

**根因**：Gate 2A2 只修好「exact row 不在 ANN 結果內」的情況（`estLead` 篩走已見 id 是安全的，因為它本來就不在 results 內）；但當 exact row **本身也被 ANN 找到**（同一 chunk id 兩條路徑都會撈到，因為 chunk id 是內容雜湊），舊過濾會把 estLead 那個 score=1 版本丟棄，只留低分的 ANN 副本，令 establishment 插入區塊完全收不到任何東西可插。

**修正**（詳見 §1）：
1. **dedup 方向對調**——`establishment` 永不因為 id 已存在而被篩走；改為把 `results` 中重複的 id 篩走，確保 estLead 版本（score=1）永遠勝出，且輸出中該 id 只剩一份。
2. **`mainSearchLead` 明確擷取**——因為 establishment 現在可以**取代**原本的 main-search lead（不只是前置），`results[forcedLeads]` 索引推導不再可靠。改為在任何 overlay 執行前，從已排序的主搜尋結果明確擷取 lead，`undefined` 時 fail closed 落閘俾 judge。
3. `forcedLeads` 現在**只**用於 overlay 插入定位（spotlight／establishment），不再用於 judge bypass 判斷。

---

## 1. 改動檔案

**只有 1 個生產檔案**：`backend/src/api/searchChannelB.ts`。三處改動：

**(a) 主搜尋排序後，overlay 執行前，明確擷取 `mainSearchLead`：**
```diff
   applySupersedePenalty(results);
   results.sort((a, b) => b.score - a.score);
 
+  // 擷取於任何 overlay 之前，確保 judge bypass 讀到真正的主搜尋 lead。
+  const mainSearchLead = results.find(
+    (r) => include_statistical || (r.content_type !== "stat_fact" && !r.source_id.startsWith("stat_"))
+  );
+
   // S193 — one raw-query embedding shared by both route-independent overlay passes below.
```

**(b) establishment 插入區塊——dedup 方向對調（Gate 2A2b 修正核心）：**
```diff
-      const seenIds = new Set(results.map((r) => r.id));
       // S211 — 全日制 unless the question asks for 半日制. …
       const estLead = estRaw
         .map(toChannelBResult)
         .filter(retiredMirrorFilter)
-        .filter((r) => !seenIds.has(r.id))
         .filter((r) => wantsHalfDay ? r.text.includes("半日制") : !r.text.includes("半日制"));
       if (estLead.length > 0) {
-        results = [
-          ...results.slice(0, forcedLeads),
-          ...estLead,
-          ...results.slice(forcedLeads),
-        ];
+        const estIds = new Set(estLead.map((r) => r.id));
+        results = [...estLead, ...results.filter((r) => !estIds.has(r.id))];
         forcedLeads += estLead.length;
       }
```

**(c) `synthesizeAnswer` 簽名與呼叫點——`forcedLeads` 換成 `mainSearchLead`：**
```diff
 async function synthesizeAnswer(
   query, results, llmFn,
-  forcedLeads = 0,
+  mainSearchLead: ChannelBResult | undefined,
   judgeFn = llmFn
 ): Promise<string> {
   ...
-  const mainLead = results[forcedLeads] ?? window[0];
-  const trustedVaultLead =
-    mainLead.content_type === "vault_extract" && mainLead.score >= VAULT_LEAD_SCORE;
+  const trustedVaultLead =
+    !!mainSearchLead &&
+    mainSearchLead.content_type === "vault_extract" &&
+    mainSearchLead.score >= VAULT_LEAD_SCORE;
```
```diff
-    synthesis = await synthesizeAnswer(query, results, llmFn, forcedLeads, judgeFn ?? llmFn);
+    synthesis = await synthesizeAnswer(query, results, llmFn, mainSearchLead, judgeFn ?? llmFn);
```

**未觸碰**：門檻常數（`FOOTNOTE_LEAD_SCORE`／`SPOTLIGHT_LEAD_SCORE`／`VAULT_LEAD_SCORE`）、footnote pass、spotlight pass 邏輯本身、路由、prompt、source sets、語料、無關檔案。`forcedLeads` 變數保留，但現在**只**驅動 spotlight／establishment 的插入定位，不再流入 judge bypass 判斷（item 3 要求）。註解已按要求精簡——舊版一次性長篇解釋改為指向本報告與 inline 短註解。

## 2. 檢查結果

| 檢查 | 指令 | 結果 |
|---|---|---|
| Backend 型別檢查 | `cd backend && npm run check` | **PASS**（`tsc --noEmit`，零輸出） |
| Backend 建置 | `cd backend && npm run build` | **PASS**（`tsc`，零輸出） |
| Rank-model 自我測試 | `python3 dev/_s214_rank_model.py --self-test` | **63/63 PASS**（51 舊有 + 12 條新增，見 §3） |
| Footnote probe 自我測試 | `python3 dev/source/footnote_lead_probe.py --self-test` | **PASS** |
| Canonical eval 自我測試 | `python3 dev/source/eval_retrieval.py --self-test` | **PASS**（確認本輪改動未波及既有評測器） |

**本輪未重跑三方離線重放**——該工具是 Python 模型，不匯入 `backend/src/*.ts`，跑一次只會再度得到「逐位元組相同」的結果，對驗證本次修正沒有新增資訊（Gate 2A2 報告已解釋此工具的驗證邊界）。**本次修正的證據力來自兩處**：(a) tsc check/build 全過；(b) 下方 §3 新增的 12 條斷言直接針對 Codex 描述的缺陷場景（id 重複於 main／footnote／spotlight 各路徑）逐一構造，並確認修正後行為符合預期——這是比重放更貼近本次 bug 本質的驗證方式，因為**該 bug 的成因本身就是舊版 184 題離線資料結構性無法呈現的**（見 §4）。

## 3. 新增測試（`dev/_s214_rank_model.py`）

按 Codex 指定的 7 類場景，全部以合成 fixture 構造（見下方「為何不能靠 184 題重放」）：

| 場景 | 斷言 |
|---|---|
| exact row 不在 ANN | 直接前置，總數正確 |
| exact row 已在 main rank 0 | 舊版本被取代，非重複；輸出 score=1 |
| exact row 已在 main rank 2（**即 `staff_fullday_24` 的精確重現**） | 升到 rank 0；舊 rank-2 位置消失但不重複；被擠開的其餘 main 候選（`hi`／`mid`）不被拋棄 |
| exact row 經另一 overlay（footnote）重複 | dedup 跨路徑生效，仍只得一份 |
| 輸出恰好一份 score=1 | 針對以上三個碰撞場景一併驗證 |
| `trustedVaultLead` 讀取 pre-overlay 原始主搜尋 lead | 明確用 `main_search_lead()` 在 overlay 前擷取，並證明 establishment 提升不會令 bypass 誤判（0.5758 vault_extract 不夠 0.70，不 bypass） |
| 主搜尋為空／全被統計過濾 | `mainSearchLead` 為 `None`，fail closed |

`merge_exact_only()` 本身亦按修正後語意重寫（establishment 永不因 id 已存在而被篩走；改為篩走 `results` 中的重複），docstring 同步更新，明確**收回** Gate 2A1b「不需要 `mainSearchLead` 簽名改動」的舊結論。

## 4. 為何 184 題離線重放結構性無法捉到這個 bug

值得記錄：本次缺陷**不是**離線重放工具的疏忽，而是重放所用的 184 題資料本身在結構上無法呈現這個場景。該資料是用**舊（有 bug）** 生產程式碼擷取的——當 exact chunk 同時被 ANN 撈到時，舊版 `seenIds` 過濾已經在擷取當下就把 estLead 丟棄，只留低分 ANN 副本，記錄下來的窗口因此**從未包含**「同一 id 兩個分數版本」這種狀態可供重放器讀取。這正是為何 Gate 2A1b 的 184 題重放只找到 3 條 establishment 查詢，而 Codex 用全新即時查詢一測就抓到第 4 個場景——離線重放只能驗證「相對於已記錄資料的重新排序」，抓不到「重新擷取會不會被同一個過濾器攔住」這類問題，唯有 live 呼叫或針對性合成測試才能覆蓋。

## 5. 新增檔案

| 檔案 | 內容 |
|---|---|
| `dev/_s214_gate2a2_implementation_report.md` | 本報告（已按 Codex FAIL 覆核修訂） |
| `dev/source/eval_runs/2026-09-04_s214_gate2a2_replay_postimpl.json` | Gate 2A2（未修正版）的重放輸出，保留作記錄 |

## 6. 未做（按指示）

- **未跑 184／39 live 套件**——留待 Codex 重跑四條 staffing 查詢核實。
- **未 commit／push／deploy／寫 Supabase／重入庫。**
- **未改** 任何門檻、路由、prompt、source、語料、無關檔案。

---

## 7. 第二輪 Codex live 行為 QC：FAIL，同表衝突列未清

**現象（Codex 用 `synthesize:true` 對「24班小學編制」實測）**：dedup 方向修好之後，exact 24 班列確實升到 rank 0，但 ANN 仍然把同一份文件其他班數（12／14 班）的列一併撈入首五格。合成答案把兩行混埋：「副校長3名（或1名，視學校規模而定）」——exact 24 班列明文寫住副校長 3 名，「或1名」係另一班數列滲入嘅結果。與 S211 記錄的「同表多列，cosine 分唔開邊行」是同一類缺陷，只是這次發生在 establishment overlay 已經解決咗「揀啱行」之後、仍然俾其他行滲返入合成窗。

**根因**：`estLead` 前置修好之後，`results.filter((r) => !estIds.has(r.id))`（第一輪修正）只篩走**同一 id** 的重複，冇篩走**同一來源、唔同班數**的其他列。呢啲列對呢條問題嚟講唔係 context，係互相矛盾嘅證據——問題問緊 24 班，12／14 班嘅數字擺喺同一個合成窗只會被誤讀成同一答案嘅選項。

### 最小修正

`backend/src/api/searchChannelB.ts`（establishment 插入區塊，同一個 if 分支）：

```diff
       if (estLead.length > 0) {
-        const estIds = new Set(estLead.map((r) => r.id));
-        results = [...estLead, ...results.filter((r) => !estIds.has(r.id))];
+        const estSourceIds = new Set(ESTABLISHMENT_SOURCE_IDS);
+        results = [
+          ...estLead,
+          ...results.filter((r) => !estSourceIds.has(r.source_id)),
+        ];
         forcedLeads += estLead.length;
       }
```

由「篩走重複 id」改為「篩走整個 establishment 來源」——`ESTABLISHMENT_SOURCE_IDS` 現時只有 `staff_est_pri` 一個來源，故效果等同「exact 班數列進場，同一份編制表的其他任何一行一律讓路」。非 establishment 來源（如 `sag_2025_11`、`g05` 等）完全不受影響，繼續按分數留在原位。

### 對應修改 `dev/_s214_rank_model.py`

`merge_exact_only()` 的 establishment 分支由「篩走重複 id」改為「篩走整個 `est_source_ids`（由 `establishment` 候選自身的 `source_id` 推導，對應生產的單一來源常數）」，docstring 新增第 3 點說明本輪修正動機。

### 新增測試（6 條，全部針對 Codex 描述的確切場景構造）

| 斷言 | 驗證內容 |
|---|---|
| 只剩一個 `staff_est_pri` 來源的候選 | exact 24 班列進場後，同來源其餘列全部消失，不止 id 重複那一條 |
| 14／12 班列確實被移除（非只是去重） | 直接檢查兩個 id 不在輸出內 |
| 不相關來源（`sag_2025_11`）不受影響 | 留在輸出內 |
| top_k 補位只從非衝突候選中取 | 5 個候選移除 3 個衝突列後，輸出恰為 2（exact 列 + 不相關列） |
| `mainSearchLead` 在衝突情境下仍讀 pre-overlay 值 | 用 `main_search_lead()` 對排序前主搜尋列表取值，確認取到 `hi24`（0.5758）而非任何 establishment 或已移除的列 |
| 該 pre-overlay lead 正確不觸發 bypass | 0.5758 < `VAULT_LEAD_SCORE`(0.70) |

修 fixture 時發現一個自己的計算錯誤：初版把 `row_14` 定為 0.60 分，高於 `hi24` 的 0.5758，令「pre-overlay lead 應為 hi24」的斷言邏輯上不成立（真正最高分是 row_14）。已改分數為 0.5327／0.50／0.45，令 fixture 內部一致，才符合斷言意圖。

### 驗證結果

| 檢查 | 指令 | 結果 |
|---|---|---|
| Backend 型別檢查 | `cd backend && npm run check` | **PASS** |
| Backend 建置 | `cd backend && npm run build` | **PASS** |
| Rank-model 自我測試 | `python3 dev/_s214_rank_model.py --self-test` | **ALL PASS**（63 舊有 + 6 條新增 = 69） |
| Footnote probe 自我測試 | `python3 dev/source/footnote_lead_probe.py --self-test` | **PASS** |
| Canonical eval 自我測試 | `python3 dev/source/eval_retrieval.py --self-test` | **PASS** |

**本輪同樣未跑 live 查詢／184 套件／commit／push／deploy／Supabase 寫入／重入庫**，按 Codex 指示留待其重啟本機後端重測 synthesis。

### 修改檔案（本輪新增）

| 檔案 | 改動 |
|---|---|
| `backend/src/api/searchChannelB.ts` | establishment 插入區塊：dedup 由「id 層級」改為「來源層級」（見上 diff） |
| `dev/_s214_rank_model.py` | `merge_exact_only()` 同步改為來源層級移除；docstring 新增第 3 點；新增 6 條 Gate 2A2b 第二輪測試 |
| `dev/_s214_gate2a2_implementation_report.md` | 本節 |
