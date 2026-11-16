# Playbook：處理來源更新（freshness-triage）

- **何時用**：Issue `freshness-change` 有新項目；或 `title_check` 報封面標題不符。
- **建議模型**：第 1–3 步中階（唯讀）；第 4 步的判斷由最強模型做；第 5 步重新入庫另見 `source-reingest.md`。
- **原理與歷史**：`dev/source/FRESHNESS_GUIDE.md`。

## 步驟

1. **取清單**：`cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && /usr/local/bin/python3 dev/source/check_freshness.py --dry-run --changes-out <scratchpad>/fresh.json`。只處理 `changed_sources`。
2. **下載新版到 scratchpad**（不得寫入 repo）：每個來源的 `url_primary`（網址有空格要轉 `%20`）。
3. **逐頁比對**：
   - PDF：用 PyMuPDF 逐頁抽文字，去掉所有空白後，與 `dev/vault/<id>/extract_*.txt` 內以 `=== Page N ===` 分隔的各頁比較。記錄：新舊頁數、不同的頁、每頁差異的實際文字。
   - 網頁：`check_freshness.py` 已只比對主內容區；報告內的 `links` 會列出增減的文件連結。
   - 試算表：解出所有儲存格，按原抽取檔的格式（每列以 tab 連接）重排後逐行比對。
4. **分類**（每項一個結論，附證據）：

| 比對結果 | 結論 | 動作 |
|---|---|---|
| 文字完全相同，或只差字形編碼／標點／頁首日期數字 | 純重新匯出 | `check_freshness.py --ack <id>`，不必問 Leonard |
| 文字相同但**頁數改變** | 頁碼連結會指錯頁 | 要重新入庫（B 級，要批准） |
| 有實質文字改動 | 內容更新 | 要重新入庫（B 級，要批准）；向 Leonard 說明改了甚麼 |
| 網頁只多了或少了文件連結 | 可能有新文件 | 交 Option A 入庫流程判斷是否收錄，然後 `--ack` |
| 下載失敗／404 | 連結失效 | 屬 served-URL 問題，另行處理 |

5. **交給 Leonard 的格式**：一個表，每列一個來源：比對結果（頁數、改了甚麼）、建議、是否要寫生產。已自行 `--ack` 的另列，註明依據。

## 硬規則

- **不要跑全量 write-sync**（`check_freshness.py --ledger …`、workflow 的 `dry_run=false`）：它會一次重設所有來源的基線，等於把整張待處理清單靜靜丟掉。只用 `--ack`。
- `--ack` 只在比對過之後才用。「看來沒有變」不是依據。
- 重新入庫完成後一定要 `--ack`，否則該來源每週都會再報。
