# 系統現況總覽（EDB K1 知識平台）

> 給任何 AI 模型或新接手的人：這是一頁式地圖，不是現況權威。**現況數字以 `dev/SESSION_HANDOFF.md` `## Current Baseline` 為準**；本檔數字為 2026-11-16（S249）實測快照。
> 視像版（白板）：https://claude.ai/artifact/Ta4bGtx3insA46xKeSrax2 （私人連結，要 Leonard 分享才開得到）。
> 更新時機：系統結構、主要風險或處理次序有變時才改；不必每節同步數字。

## 1. 系統怎樣運作

```
EDB 官方來源 ──► 入庫 ──► Supabase 知識庫 ──► 後端（Render） ──► 網站
316 個來源        抽取→切段→向量   17,084 片段         路由→檢索→判官→合成   policychecker.wongfu.net
PDF／網頁／試算表  新通告自動，其餘人手                    模型 gpt-6-luna        政策搜尋、EDB 指引 182 份

監察（GitHub Actions：7 個排程＋每日看門狗） ──有新項目才通知──► Leonard
查來源更新、連結、質素、線上服務                                 入庫、刪除、合併都要他批准
```

| 組件 | 位置 | 要點 |
|---|---|---|
| 來源登記 | `dev/source/source_registry.json` | 每個來源一行；監察與入庫都讀它 |
| 入庫 | `dev/source/execute_ingest.py`（自動）、`dev/ingest_one_source.py`（人手） | 自動路徑走分支 → PR → auto-merge |
| 知識庫 | Supabase `public.wiki_chunks`（pgvector） | 後端用 anon key，`statement_timeout` 3 秒 |
| 後端 | `backend/src/`（Node／TypeScript，Render 部署） | 推上 `main` 即自動部署 |
| 前端 | `app.html`、`index.html`、`mobile.js`（GitHub Pages） | 升版只手改 `PLATFORM_VERSION`＋README＋CHANGELOG |
| 監察 | `.github/workflows/*.yml`、`dev/source/check_*.py` | 通知經 `.github/scripts/notify_new_items.js` |
| 治理 | `AGENTS.md`、`dev/SESSION_HANDOFF.md`、`dev/rules/*.md` | `main` 受保護，一切改動走 PR |

## 2. 困境與缺點（已知、已量度）

1. **答錯對象**：窗內有別類人的同類規則時，合成器會把它套到所問的人身上；生產已知漏判 5 條。對象核對 v1 已部署，旗標 `FEATURE_SUBJECT_CHECK` 未開。設計見 `dev/source/SUBJECT_CHECK_DESIGN.md`。
2. **找對文件、找錯段落**：185 題基線，Source Recall@5 0.711，Chunk Recall@5 0.349。
3. **忽快忽慢**：Render／Supabase 剛喚醒時首次查詢會逾時（`57014`），冷熱落差 58–90 倍，屬平台層。
4. **人手待辦積壓**：來源更新 3 項（Issue #77；S249 由 35 項減至 3 項，餘下為三份統計試算表）、欠頁碼連結 51 條（`PAGE_ANCHORED`）、瀏覽清單與庫不一致 `PHANTOM` 36／`UNLISTED` 119。
5. **刪除生產資料沒有機械閘**：AI 能直接執行 Supabase 刪除，只靠「先備份、先取得 Leonard 明示批准」的紀律。

## 3. 盲點（現時沒有任何機制看著）

1. **答案內文的連結**：chunk 正文內約 3,000 條網址（上限，未去重組）不受任何監察；`check_served_urls.py` 只查 `wiki_chunks.url`。
2. **監察同生共死**：所有監察跑在同一套 GitHub Actions 排程；一齊停時無人出聲，公開 repo 60 日無活動會自動停用排程。
3. **功能開關看不到**：旗標只在 Render 後台，`/health` 不報。
4. **AI 規則檔沒有備份**：`AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 不在 git 內。
5. **來源登記不如實**：`authority` 一欄全寫 `edb`，實有 8 個非 EDB 域、約 208 片段。

## 4. 之後怎樣處理（建議次序）

| 次序 | 做甚麼 | 為何排這裡 | 要 Leonard 做甚麼 |
|---|---|---|---|
| 1 | 合併來源更新監察的修正（S249） | 網頁不再誤報，清單 35 → 3；處理完自動關閉 | 合併 PR |
| 2 | 決定是否開 `FEATURE_SUBJECT_CHECK` | 最嚴重的答案錯誤；開啟可攔 5 條中 3 條 | 在 Render 設旗標 |
| 3 | 清餘下 3 項來源更新 | 三份統計試算表（`stat_pri`／`stat_sec`／`stat_special`）的教師數字上游已修訂，庫內仍是舊數 | 批准重新入庫 |
| 4 | 補 51 條頁碼連結 | 要寫生產資料 | 批准清單 |
| 5 | 退役通告 9/2019（`EDBC_9_2019_E`） | 已被 4/2026 取代，仍佔「SEN 學生留級」第一格 | 再確認批准 |
| 6 | 試 cross-encoder 重排 | 提升段落命中唯一未試的方向，上限多救 42 題 | 批准量度開支 |

## 5. 給其他模型的工作邊界

- 未經 Leonard 明示：不改旗標、不執行 DDL、不寫入或刪除生產片段、不作外部模型批次、不合併 PR。
- 抽取與入庫一律用 `/usr/local/bin/python3`；路徑含空格，指令要加雙引號。
- 文件會過時：動手前以程式碼和線上實測核實，不要只信文件（包括本檔）。
- 開工讀 `AGENTS.md` → `dev/SESSION_HANDOFF.md`；詳情與證據在 `dev/SESSION_STATE_DETAIL.md`，做到該項才讀。
