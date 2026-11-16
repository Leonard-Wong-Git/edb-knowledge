# Playbook：質素檢查惡化（qc-regression-triage）

- **何時用**：Issue `qc-regression` 開出（某項基準檢查的數目高於基準）。
- **建議模型**：定位交最平模型；定案由最強模型做。

## 步驟

1. **看是哪一項、多了多少**：`git show origin/main:qc_report.json` 內的 `regressions`（含 `id`、`count`、`baseline`、`top`）。
2. **找出新增的是哪些片段**：比較惡化前後兩份 `qc_report.json`（`git log --oneline -- qc_report.json`），或直接看該檢查的 offenders。
3. **對應最近的改動**：`git log --since=<上次正常日期> --oneline`，重點看入庫 PR（`feat(ingest)`）。
4. **按檢查項處理**：

| 檢查 | 最常見成因 | 處理 |
|---|---|---|
| `PAGE_ANCHORED` | 新註腳沒有頁碼；註腳腳本重跑蓋掉頁碼 | `dev/apply_url_overrides.py`（dry-run 看 `to_change`）；新註腳走 `footnote-audit` |
| `REGISTRY_UNROUTED` | 人手入庫的來源沒有加入路由清單 | `route-coverage` |
| `MOJIBAKE` | 新入庫的 PDF 字形抽取失敗 | 重新抽取（OCR）或退回該次入庫 |
| `NO_DUPLICATE_CHUNKS` | 同一文件以兩個 id 入庫 | 列為退役候選交 Leonard |
| `BODY_LENGTH_FLOOR`／`NO_TOC_NOISE`／`NO_MIDCLAUSE_START` | 新來源的切段問題 | 看具體片段；通常要改抽取而非改基準 |

5. **修好後**確認該項回到基準或以下。**基準只可向下調**：修好令數目下降時，把 `dev/source/qc_report.py` 的 `BASELINE` 調低；不要為了令檢查轉綠而調高基準。調高基準等於接受一個新缺口，要 Leonard 決定。

## 交給 Leonard 的格式

一句話說明多了甚麼、為何、建議怎樣處理、是否要寫生產資料。
