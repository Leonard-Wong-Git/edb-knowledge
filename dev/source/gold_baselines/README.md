# 獨立題集的基線（gold_baselines）

這裏放**不屬於 185 題主題庫**的題集在生產上的量度結果。刻意不放在 `dev/source/eval_runs/`：質素檢查的 `EVAL_LATEST` 會自動採用該資料夾內最新的檔案，題數不同的結果放進去會被誤當成主題庫的最新基線。

**不要把這裏的數字與 185 題的基線合併或比較**：題目、題數與用途都不同。

| 檔案 | 題集 | 結果 |
|---|---|---|
| `2026-11-17_s252_subject_guides_prod.json` | `dev/_s252_gold_subject_guides.json`：科目指引路由（`subject_guides`）10 題，S252 A5 擬寫；其中 4 題標為 `held_out`（只作最終驗收，平時不看逐題結果） | 來源層 10／10；片段層 4／10 |

重跑方法（唯讀，帶 `x-probe`，每題相隔 8 秒；先查一次 `/health` 暖機）：

```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s213_run_gold.py --gold dev/_s252_gold_subject_guides.json --out dev/source/gold_baselines/<日期>_subject_guides_prod.json --pace 8
```

改題目前後都要跑 `dev/_s213_validate_gold.py`（需要語料快照，見 `dev/_s213_corpus.py` 檔頭的重建方法）；不通過的題目隔離，不要為通過而改標籤。
