# S214 route-first：已保存三題測試的離線覆核

日期：2026-09-07。範圍：只讀本地 artifact、active gold 及候選程式碼；本輪沒有外部呼叫、資料庫寫入或部署。

## 證據與限制

來源：`dev/source/eval_runs/2026-09-07_s214_route_first_focused.json`。
其 trace 記錄新 RPC 三次 HTTP 200，以及特殊學校一次 HTTP 500／57014 後重試成功。這與交接「尚未安裝、未跑 focused」不一致。只能證明保存紀錄中的成功，不能確認現在 live 定義、安裝者、安裝授權或生產 flag 狀態。不得據此重做 DDL。

## 離線核對

以 active gold 的 passage signature 作 NFKC／空白正規化比對，位置採一基：

| 案例 | before | after | 判讀 |
|---|---|---|---|
| hr_lsp | 舊策展 signature 位於 1 | 同樣位於 1 | 該 gold 只驗策展摘要，不能證明完整公式；一手公式 chunk `vault_long_service_payment_guide_ab49f971fc3d2752` 兩邊均缺席 |
| sen_special_school_curriculum | 指定 signature 缺席 | 指定 signature 缺席 | `g10` 亦未進兩邊首八項；不能宣稱修好 |
| ss_ncs_history_adapted_outline_v2 | 指定 signature 缺席 | 指定 signature 缺席 | 來源存在但答案片段缺席；不能以 Source Recall 代替 Chunk Recall |

特殊學校的新 RPC 原始回傳中首個 g10 位於第 17；其 gold 指定 chunk 不在原始 40 項。中史 gold 指定 chunk亦不在新 RPC 原始回傳。故問題並非全部由最後八項的後處理造成，下一步須查 query expansion／向量排名；本輪未證明哪一項是根因。

## 效能

特殊學校 after 整題 16,666 ms；新 RPC 先以 8,620 ms 逾時，再以 7,156 ms 成功。三題單次結果不能推論 p95 或穩定性。程式 `searchChannelB.ts` 先完成舊 searchWiki 再呼叫新 RPC，故候選成功路徑亦承擔兩次搜尋；這是靜態可見的額外工作，不代表已量得其獨立延遲成本。

## 下一步

維持候選不啟用。先離線追蹤三題 query expansion、目標片段在既有回傳中的位置及 gold 的完整性缺口。完整 185 題 live 驗證暫不建議立即執行；新外部批次仍須另列模型、案例及 HTTP 上限取得批准。任何 DDL 前先確認 live 函式定義；本輪不重做安裝。

Artifact SHA-256：`9d6642af783e17f9bb183afe74b60760d4ec019037249ae553fb3882e8d824dd`。
