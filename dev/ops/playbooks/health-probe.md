# Playbook：起手探針（health-probe）

- **何時用**：每節開工；懷疑線上有問題；任何生產寫入之後。
- **建議模型**：最平。全部唯讀。
- **交回**：下表每項的實測值，與交接檔 `## Current Baseline` 不符的逐項列出。不要解釋成因，除非被問。

## 步驟

先建一個 scratchpad 資料夾（不在 repo 內），下文以 `$SP` 代表它。指令逐條照跑：

```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
# 1 網站版本
curl -s https://policychecker.minny.app/app.html | grep -o "PLATFORM_VERSION *= *'[^']*'"
# 2 後端
curl -s -m 60 https://edb-knowledge.onrender.com/health
# 3 片段數
curl -s https://policychecker.minny.app/stats.json
# 4 Git（只看，不要 checkout）
git fetch -q origin && git status -sb && git log --oneline -1 origin/main && gh pr list
# 5 登記漂移（--ledger 一定要指向 $SP，否則會改寫 repo 內的 dev/source/registry_drift.md）
mkdir -p "$SP" && python3 dev/source/check_registry_drift.py --check --ledger "$SP/ledger.md"
# 6 頁碼覆寫（不加參數即 dry-run，不會寫入）
/usr/local/bin/python3 dev/apply_url_overrides.py
# 6b 註腳更正（--check 只讀；有漂移即 exit 1 並列出）
/usr/local/bin/python3 dev/apply_footnote_corrections.py --check
# 7 開著的 Issue（PR 已在第 4 項列出，兩者分開報）
gh issue list --state open
```

| # | 正常 | 期望值在哪裏 |
|---|---|---|
| 1 | 版本與交接檔相同 | `dev/SESSION_HANDOFF.md` `## Current Baseline` 1 |
| 2 | `ok:true`；`cache_b.footnote` 有數；`commit` 相同 | 同上 4 |
| 3 | 片段數、來源數相同 | 同上 2 |
| 4 | `origin/main` 與開著的 PR 相同。**不同不代表有問題**：交接檔記的是上次收工時的快照，其後合併過 PR 就會不同；如實列出差異即可 | 同上 4 |
| 5 | `ZOMBIE`／`SERIES_UNMONITORED`／`UNMANAGED`／`UNROUTED` 皆 0；`PHANTOM`、`UNLISTED` 與交接檔相同（這兩項是待辦清單，不是故障） | 同上 3 |
| 6 | `to_change=0` | — |
| 6b | `to_change=0`。不是 0 代表有註腳入庫腳本重跑過、舊文字被寫回：報告，待批准後跑 `--execute` | — |
| 7 | 逐個列出編號、標題、標籤；交接檔沒有列的 Issue 標為「新」 | `## Open Priorities` |

## 已知的假警報

- **剛喚醒時 `/health` 的 `circular.last_error` 含 `57014`**：免費層冷啟動，隔半分鐘再查一次；第二次正常即無事。
- **`/health` 的 `commit` 落後 `origin/main`**：只有改到 `backend/` 的 commit 才會重新部署。用 `git diff --name-only <部署commit>..origin/main -- backend` 判斷，不要比 hash。

## 停止條件

第 2 項連續兩次失敗，或第 5 項任何一個 ERROR 類別不是 0：停止其他工作，先報告。
