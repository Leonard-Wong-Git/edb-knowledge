# 搜尋記錄與回答評分 —— 設計（S233 草稿，未實施）

## 一、目的

把每一次真實用戶的 Channel B 搜尋留底 180 日，作為改進檢索的數據庫：

1. 以真實查詢補充及抽樣 gold 題集，令量度代表真實用戶（現有 185 題為人手編寫）。
2. 找出內容缺口：拒答、低分、👎 的查詢即語料未覆蓋或檢索失手的題目。
3. 找出路由錯配（S227「津貼」一類）。
4. 補上 `dev/AUDIT.md` ⑤「單一請求事後無法重現」。

## 二、Leonard 定案（2026-09-28，S233）

| 項目 | 決定 |
|---|---|
| 保留期 | **180 日** |
| 回答全文 | **要存**，以便對照查詢、回答與來源 |
| 👍／👎 | **要做** |
| 查詢內容過濾（身份證、電話等） | **不做** —— 用戶不會輸入學生個人資料 |
| 前端收集說明 | **不加** —— 只記內容、不記身份，無私隱成份 |

## 三、記錄甚麼

每次非探針（無 `x-probe`）的 `POST /api/search/channel-b` 寫一行 `public.search_log`：

| 欄位 | 內容 | 來源 |
|---|---|---|
| `id` | 伺服器產生的 UUID，同時以 `log_id` 回傳前端，供評分用 | `crypto.randomUUID()` |
| `created_at` | 時間 | 資料庫預設 |
| `query` | 查詢原文（上限 500 字） | 請求 |
| `client` | `desktop`／`mobile`／空 | 前端新增的可選欄位 |
| `route` | 路由類別，無路由為空 | `detectQueryCategory(query)`（純函數，與搜尋內部同一判定；`enable_topic_filter:false` 時為空） |
| `declined` | 回答是否為拒答文字 | `synthesis === SYNTHESIS_DECLINE`（需 export 該常數） |
| `degraded` | Channel B 是否失效 | 回應 `degraded` |
| `synthesis` | 回答全文（上限 4,000 字） | 回應 |
| `results` | 結果窗，每格 `{id, source_id, title, page, score, content_type, text}` | 回應 `results` |
| `total`、`latency_ms` | 結果數、伺服器端耗時 | 回應／計時 |
| `feedback`、`feedback_at` | 👍 = 1、👎 = −1，可改一次心意 | 評分端點 |

**不記錄**：IP、cookie、user agent、任何可識別用戶的資料；帶 `x-probe` 的自家測試流量。

**片段全文要一併存**：重新入庫會刪去或改寫片段（例如 S223 SAG 換版刪 792 行），只存 ID 日後會對不上。以現時流量計（見第六節）容量無問題。

## 四、架構

沿用 S204 用量計數器的模式（`usage_daily` ＋ `bump_usage`）：

- 後端只持 anon key，寫入經兩個 `SECURITY DEFINER` 函數：`log_search(...)`、`record_search_feedback(id, rating)`，EXECUTE 授予 anon。
- 資料表開 RLS 而**不設任何 policy**：anon 不能直接讀寫。讀取只經 service_role（Dashboard 或本機腳本）。
- **記錄失敗絕不影響搜尋**：fire-and-forget，不 await、吞錯只 `console.warn`，與 `recordSearch()` 同一規則。
- **180 日清除**寫在 `log_search()` 內，每次寫入順手刪除過期行；不依賴 pg_cron（本項目未核實有無）。
- 評分只接受 24 小時內、已存在的 `id`。

DDL 草稿：`backend/supabase/s233_search_log.sql`。套用前已核實三個名稱在生產皆不存在（`search_log` → PGRST205；兩個 RPC → PGRST202），屬新建，無 overload 風險。

## 五、改動範圍

| 次序 | 改動 | 部署 | 需批准 |
|---|---|---|---|
| 1 | 套用 DDL | Leonard 在 Supabase SQL Editor 執行 | ✅ |
| 2 | 後端：`server.ts` channel-b 路由計時、產生 `log_id`、呼叫 `log_search`；新增 `POST /api/search/feedback`（同一限流）；`searchChannelB.ts` 只加一個 `export`（`SYNTHESIS_DECLINE`），**搜尋邏輯零改動** | PR → Render 重新部署 | ✅ |
| 3 | 前端：`app.html` 與 `mobile.js` 在回答下加「這個回答有幫助嗎？👍 👎」，送出後顯示「謝謝」；請求加 `client` 欄位 | PR；平台版本手動 bump（`PLATFORM_VERSION`＋README＋CHANGELOG，**不可用 `bump_version.py`**） | ✅ |
| 4 | 文件：`dev/CODEBASE_CONTEXT.md` External Services、`dev/PROJECT_INDEX.md`、`CHANGELOG.md`（`K1_API_SPEC.md` 不涵蓋 Channel B 端點，無需改） | 隨 PR | — |

次序理由：DDL 先行，後端上線後即開始寫入；即使次序顛倒，寫入失敗亦只會 warn，不影響搜尋。

回應新增的 `log_id` 屬加欄位，現有呼叫方（包括伺服器對伺服器的同步端點使用者）不受影響。

## 六、限制與要知的事

1. **流量很低**：`usage_daily` 實測 2026-08-18 起共 217 次搜尋（約每日 5 次），最近一星期約每日 1 次；其中包含 Leonard 自己的手動搜尋，與真實用戶無法區分（因為不記身份）。180 日預計只累積數百條。**價值在於「真實用戶問甚麼」的形狀，而非統計量**；分析時要逐條讀，不宜只看比率。
2. **第一階段不記「判官跳過與否」**（`trustedVaultLead` bypass）：這要把搜尋內部狀態帶出 `searchChannelB()`，屬改動搜尋主檔，另立一步。`declined` 已能分辨「答」與「拒答」。
3. anon key 只存在 Render 環境變數，前端不接觸 Supabase；函數內已為每個欄位設上限，防止被灌大。
4. 讀記錄的工具（例如 `dev/search_log_report.py`：拒答清單、👎 清單、路由分佈、可轉為 gold 的候選）屬第二步，資料累積後再寫。

## 七、驗收

1. DDL 後：`search_log` 行數 0、RLS 開、policy 0（SQL 檔尾三條檢查）。
2. 後端本機：`npm run check`、`npm run build`；本機搜尋一次 → 表內多一行、欄位齊全；帶 `x-probe` 搜尋 → 不增加；評分 → `feedback` 更新；Supabase 不可達時搜尋照常回應。
3. 生產上線後：一次真實搜尋 → 一行；👍 → 更新；`/health` commit 為新部署。
4. 前端：桌面與手機各按一次 👍／👎，並在預覽截圖核實。
