# Playbook：重新入庫一個已存在的來源（source-reingest）

- **何時用**：`freshness-triage` 判定要重新入庫，而且 **Leonard 已明示批准**。
- **建議模型**：最強模型執行；第 1–3 步的預演可交中階。
- **會寫生產資料**。任何一步結果與預期不符：停，報告，不要自行補救。

一律先 `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`，python 一律 `/usr/local/bin/python3`。

## PDF 來源

1. **登記**：在 `dev/vault/repage_pdfs.py` 仿 `REFRESH_S249` 加入來源 id。
2. **預演抽取**：`dev/vault/repage_pdfs.py --only <ids>`（預設 dry-run）。核對頁數與 marker 數相同。
3. **亂碼檢查**：新 PDF 文字中的私用區字元（U+E000–U+F8FF）與 `\ufffd` 數目，不應比舊抽取檔多。
4. **備份**：把這些 `source_id` 在 `wiki_chunks` 的所有列（`select=*`，含 embedding）匯出到 `dev/init_backup/<UTC時間>/`。記下列數、是否每列都有 embedding。
5. **寫 vault**：`dev/vault/repage_pdfs.py --only <ids> --write`。
6. **預演入庫**：`dev/cb3_b2_pagecarry_migrate.py --only <ids> --include-non-page --skip-local`。看每個來源的 DELETE → INSERT 數目是否合理。
7. **執行**：同一指令加 `--execute`。每個來源必須顯示 `OK`。
8. **同步公開數字**：
   ```
   /usr/local/bin/python3 - <<'PY'
   import sys; sys.path.insert(0,'dev/source'); import execute_ingest as e
   print(e.live_display_sync(e.current_chunk_total(), e.live_total_count()))
   PY
   ```
9. **更新日誌**：`update_log.json` 每份改動的文件一條（白話、說明改了甚麼），只保留最新 6 條。標題要含 registry 的 `title`。
10. **下游檢查**：`python3 dev/source/check_downstream_sync.py --sources <ids> --base origin/main`，直至 `MUST_UPDATE` 為 0。
11. **確認基線**：`dev/source/check_freshness.py --ack <ids>`。
12. **線上驗證**：帶 `x-probe: 1` 向 `https://edb-knowledge.onrender.com/api/search/channel-b` 查一條只有新版才答得到的問題。每分鐘最多 10 次，相隔至少 7 秒。
13. **commit**：指定檔案加入（不要 `-A`），走 PR。

## 試算表來源（stat_*）

抽取檔是儲存格以 tab 連接的文字。重新產生後與舊檔逐行比對，確認只有預期的列不同；新檔名用抽取年月（`extract_<x>_YYYYmMM.txt`），**舊檔要移走**（同一資料夾內所有 `.txt` 都會被載入）。之後由第 4 步起相同。`dev/vault/build_stat_facts.py` 內寫死的數字如受影響要一併改，並定點替換 Supabase 內對應的 `stat_fact` 列（id 是文字雜湊，改文字即新 id：先插入新列、核實、再刪舊列）。

## 註腳（footnote_curated）

**不要**用註腳入庫腳本的 `--execute` 更正單條註腳：它會重寫該腳本內所有註腳並蓋掉頁碼。做法：改腳本內的原文，然後定點更新該列的 `text`／`hash`／`embedding`（範例 `dev/_s249_fix_two_footnotes.py`）。任何註腳腳本以 `--execute` 跑過之後，必須再跑 `dev/apply_url_overrides.py --execute`。

## 回退

由第 4 步的備份重新匯入該來源的列（先刪現有列）；vault 舊檔在 `dev/init_backup/<時間>/cb3c_pilot_legacy/`。
