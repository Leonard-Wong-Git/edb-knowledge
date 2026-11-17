# 自動運作總流程（EDB K1 知識平台）

> **本檔的角色**：平台「偵測 → 分流 → 執行 → 驗證 → 記錄」的總流程、各類工作交給哪一級模型，以及可執行的程序（playbook）索引。
> **不是**現況權威（現況看 `dev/SESSION_HANDOFF.md`），**不是**規則本身（安全與批准規則看 `AGENTS.md`、`dev/rules/safety.md`）。
> **更新時機**：新增或退役一個監察、一個 playbook，或某類工作的自動化級別改變時。
> **目標**（Leonard，S243／S249）：各環節自行運作，人手只在真正要判斷或有風險的地方介入。

## 1. 總流程

```
偵測            分流                    執行                     驗證              記錄
GitHub Actions  → 這是哪一類？       → 按級別處理           → 機械檢查       → 最小的正確位置
排程監察           A 自動可修            A 自動修、事後報告      自測／對數／        update_log／registry
（見 §3）          B 要 Leonard 批准     B AI 備妥方案＋證據      before-after 量度   交接檔／PR
                   C 只需知悉            → 等批准 → 執行         線上探測
                                         C 記錄，不打擾
```

每一步的原則：

1. **偵測一律是機器做**，而且只在有新項目時通知 Leonard（`.github/scripts/notify_new_items.js`）。
2. **任何要人做決定的清單都要有出口**：處理完的項目必須離開清單，清單清空要自動關閉。只入不出的清單會變成牆紙。
3. **AI 把決定準備到「只差一個是或否」**：附證據、附建議、附回退方法。不要把未分類的原始清單交給 Leonard。
4. **寫生產資料前**：先全欄位備份、先預演（dry-run）、先取得 Leonard 明示批准；寫完逐項對數。
5. **凡改檢索**（路由清單、門檻、排序）：先量、後改、再量，用同一批題目。
6. **修一個問題時，順手加一個會在它重現時報警的檢查**，否則同一個問題會靜靜回來。

## 2. 自動化級別

| 級別 | 意思 | 適用條件 |
|---|---|---|
| **A 全自動** | 機器偵測、機器處理、事後在 PR／Issue 留紀錄 | 可機械判定對錯、可回退、不涉內容取捨 |
| **B 半自動** | AI 備妥方案與證據，Leonard 答「是／否」 | 寫生產資料、刪除、內容取捨、檢索改動、合併 PR |
| **C 只通知** | 記錄並在適當時告知 | 平台層限制、等上游修正、已知且接受的缺口 |

現況（2026-11-16）：

| 工作 | 現時級別 | 可升級至 | 還欠甚麼 |
|---|---|---|---|
| 新通告入庫（Option A executor） | A（Leonard 在 Issue 剔選後全自動） | — | — |
| 來源有否更新（Freshness） | 偵測 A；PDF 逐頁文字相同者 A（S252 起自動確認）；其餘處理 B | — | 網頁與試算表仍要人手比對；頁數改變或文字不同屬 B |
| 來源有實質改動 → 重新入庫 | B | 低風險個案升 A | 重新入庫改走 Option A 的分支 → PR → auto-merge 路徑，並以對數與線上探測作閘 |
| 連結失效（served-URL） | 偵測 A；修復 B | 純網址搬遷升 A | 新網址內容與舊抽取逐頁相同才自動改 |
| 質素檢查惡化（qc-regression） | 偵測 A；處理 B | — | 成因多樣，維持 B |
| 來源未入路由清單（UNROUTED，S250） | 偵測 A；處理 B | 新入庫來源升 A | executor 已自動加入清單；人手入庫要記得加，檢查會報 |
| 註腳出處有否搬頁、換版、失效 | 偵測 A（S252：`footnote_anchor_check.yml` 每月機械核對 163 條錨句，不用模型）；處理 B | 純搬頁升 A | 搬頁的頁碼更正仍要寫生產資料，維持經批准才寫 |
| 註腳的寫法與原文是否一致 | 人手觸發（S250 首次全量審核：177 條中 28 條頁碼錯、9 條內容不符；S251 全部更正，更正清單 `dev/source/footnote_corrections.json`） | — | 語意比對要有人或模型讀原文；月檢只看原文有沒有變。14 條註腳未有錨句（13 條 S250「找不到」＋ 1 條沒有記下原句） |
| 答案是否答錯對象 | 修正已部署未開 | — | 等 Leonard 決定 `FEATURE_SUBJECT_CHECK` |

## 3. 偵測層（現有監察）

| 監察 | 頻率 | 發現問題時 | Playbook |
|---|---|---|---|
| `freshness_check.yml` | 每週一 | Issue `freshness-change` | `freshness-triage` |
| `served_url_check.yml` | 每週一 | Issue `served-url-broken` | `source-reingest`（網址搬遷部分） |
| `discover_check.yml` | 每週一 | Issue（新文件候選） | Option A 入庫 |
| `title_check.yml` | 每月 | Issue（封面標題不符） | `freshness-triage` |
| `footnote_anchor_check.yml` | 每月 2 日 | Issue `footnote-anchor`（原文搬頁、換版；下載連續兩次失敗） | `footnote-audit` |
| `qc_report.yml` | 每日 | Issue `qc-regression`（高於基準才開） | `qc-regression-triage` |
| `live_probe.yml` | 每 6 小時 | 線上服務異常 | `health-probe` |
| `monitor_watchdog.yml` | 每日 | 其他監察沒有按時跑 | `health-probe` |
| `pgvector_check.yml` | 每週一 | 上游版本可升級 | 只通知 |

## 4. 模型分工

原則：**貴的模型只做判斷，便宜的模型做體力勞動；體力勞動的結果由貴的模型抽查後才採用。**

| 工作類型 | 交給 | 例子 |
|---|---|---|
| 設計、跨系統找根因、檢索設計、內容取捨、寫生產資料前的最後覆核 | 最強模型（主 session） | 為何 Freshness 清不完；哪些來源應加入路由清單 |
| 跟 playbook 做的多步調查、逐頁比對、跑量度並比較、按既定模式改程式 | 中階模型（sub-agent） | 51 條頁碼逐條對 PDF；185 題 before／after |
| 跑指令報結果、數數、對檔案、格式檢查、起手探針 | 最平模型（sub-agent） | 起手探針；`check_*.py --self-test` 全部跑一次 |

分派 sub-agent 的硬規則：

1. **預設嚴格唯讀**：不得寫 Supabase、不得改 repo 內的檔案、不得 commit／push、不得改旗標。輸出只寫到 scratchpad。
2. **任務說明要自足**：路徑（含空格要加引號）、用哪個 python（抽取與入庫用 `/usr/local/bin/python3`）、金鑰在 `backend/.env`（不得印出）、要交回甚麼。
3. **要求分開「已核實」與「推斷」**，並交回輸出檔的絕對路徑。
4. **主 session 獨立抽查後才採用**；寫生產資料所依據的每一條，都要再核一次（S249：40 條頁碼由 sub-agent 找、主 session 再逐條核實）。
5. **生產寫入只由主 session 在 Leonard 批准後執行**，不交給 sub-agent。

## 4a. 沒有最強模型時（S251）

Leonard 於 2026-11-16 告知：最強模型（Fable 5.2）的用量已近用完，之後不能假設有它。上表「交給最強模型」的工作，改按以下規則處理。原則：**判斷力不足的地方，用機械證據補；補不到的，交給 Leonard，不要硬做。**

| 工作 | 沒有最強模型時怎樣做 |
|---|---|
| 起手探針、跑檢查、對數 | 照 playbook 做，任何模型皆可 |
| 可逐字對照的更正（數字、金額、年度、頁碼、連結） | 把原文原句與現有寫法並列，備妥預演，交 Leonard 批准後用工具寫入 |
| 涉及語意的更正（原文沒有這個說法、條件或對象不同） | **不要自行改寫**。並列兩句交 Leonard 選定寫法 |
| 檢索改動（路由清單、門檻、排序、模型） | 只有在同一批 185 題改前改後逐題相同或更好、並有量度檔為證時，才可提出；否則只記錄問題，不改 |
| 刪除或退役生產資料 | 只列清單與備份方案，範圍由 Leonard 定 |
| 跨系統找根因 | 只報觀察到的事實與重現步驟，不把推斷寫成結論，不據此改碼 |
| 寫生產資料前的最後覆核 | 由另一個獨立 session 或 sub-agent 用不同方法重做一次；兩者一致才交 Leonard 批准，不一致就把分歧原樣交出 |

另外四條：

1. **只用有 `--check`、`--self-test` 或預演（dry-run）的工具寫生產資料**；沒有這類工具的寫入，先停下來報告，不要臨時寫一次性腳本。
2. **playbook 沒有寫的情況：停**。把情況記入交接檔 `## Open Priorities`，等 Leonard 或下一次有較強模型時處理。
3. **一次只做一件事，一個 PR 只做一件事**；每步做完先讀回再做下一步。
4. **不確定時寧可不做**。平台現時運作正常；錯的更正比遲的更正代價大。

現有可照做的工具（皆有預演與讀回）：`dev/apply_footnote_corrections.py`（註腳內容）、`dev/apply_url_overrides.py`（連結與頁碼）、`dev/source/check_freshness.py --ack`（確認來源基線）、`dev/cb3_b2_pagecarry_migrate.py`（重新入庫）、Option A executor（新通告入庫，Leonard 在 Issue 剔選）。

## 4b. 建議的模型與推理強度（S251）

Fable 5.2 不再可用之後，以 Opus 5.5 為主力。推理強度（effort）越高，推理 token 越多，費用與時間同步上升；照程序做的工作開高了沒有額外得益。**這是按工作性質作的建議，未在本專案實測各級的表現**；首次用某一級做某類工作時，留意它有沒有守住工作卡的停止條件，守不住就調高一級並把結果記在本節。

| 工作 | 建議 | 原因 |
|---|---|---|
| 起手探針、跑檢查、對數、收工 | Opus 5.5 **low**；或改用 Haiku 5.5／Sonnet 5.5 | 純照程序做 |
| `dev/ops/WORK_QUEUE.md` A 部（照卡實作、寫測試） | Opus 5.5 **medium** | 卡內已有設計決定、驗收與停止條件 |
| 寫入生產前的覆核；註腳與原文的語意比對；B 部的退役範圍 | Opus 5.5 **high** | 錯了會直接答錯用戶 |
| `dev/ops/NEXT_UPGRADE.md` 的檢索設計；跨系統找根因 | Opus 5.5 **xhigh** | 只在真的做這類工作時才開 |

日常預設 **medium**。

**agent 要主動提 Leonard**（他要求的，S251）：

1. **開工時**：起手卡之後加一句，說明這一節打算做的工作、建議用哪個模型與哪一級 effort，以及現時 session 用的是否相符。不相符就請他切換（模型用 `/model`；effort 由他在應用程式內調整），等他回覆才開始。
2. **工作性質中途改變時**（例如由照卡實作變成要寫入生產前的覆核）：先停，提他調高；做完再提他調回。
3. **不知道自己現時的 effort 時**：照實說不知道，把建議的級別告訴他，由他核對。不要猜。
4. 提醒只說一次，他決定不換就照現有設定做，並在報告內註明「本節以 X 執行，建議為 Y」。

## 5. Playbook 索引

Playbook 是可逐步照做的程序，放在 `dev/ops/playbooks/`。步驟次序以 playbook 為準；背後的原理與歷史教訓看它指向的文件。

| Playbook | 何時用 | 建議模型 | 會否寫生產 |
|---|---|---|---|
| `health-probe.md` | 每節開工；懷疑線上有問題 | 最平 | 否 |
| `freshness-triage.md` | `freshness-change` Issue 有新項目 | 中階（比對）＋最強（定案） | 只寫監察基線 |
| `source-reingest.md` | 經批准重新入庫一個已存在的來源 | 最強執行；中階可做預演 | **是（要批准）** |
| `route-coverage.md` | QC 報 `REGISTRY_UNROUTED`；人手入庫新來源後 | 最強（分類）＋中階（量度） | 否（改後端，要合併批准） |
| `footnote-audit.md` | `footnote-anchor` Issue 有新項目（月檢由機器做）；`PAGE_ANCHORED` 高於基準；新增一批註腳之後 | 月檢結果的處理：任何模型；全量語意審核：中階 | 審核唯讀；更正要批准 |
| `qc-regression-triage.md` | `qc-regression` Issue 開出 | 最平（定位）＋最強（定案） | 視乎成因 |

> **提升搜尋準確度的計劃**：`dev/ops/NEXT_UPGRADE.md`（有較強模型或 Leonard 明示時才做）。
> **待辦事項與逐項做法**：`dev/ops/WORK_QUEUE.md`（S251 起，所有待辦的唯一清單；下面三件事已寫成其中的 A1–A3、A11）。

## 6. 下一步可以交給機器的三件事（按得益排序）

1. ✅ **（S252 已做，PDF 部分）Freshness 自動確認「文字相同」的個案**：排程內下載新版、逐頁對 vault 抽取檔，完全相同即自動 `--ack`。S249 的 19 項中 11 項屬此類，全部可以不經人手。
2. **每月註腳審核**：✅ S252 已改為機械核對（`dev/source/check_footnote_anchors.py`＋`footnote_anchor_check.yml`，不用模型）：每條註腳記一句原文錨句，每月核對是否仍在所記的頁，有變才通知 Leonard。
3. **路由清單改動自動量度**：PR 一旦改到 `SOURCE_SETS`，CI 自動跑題庫 before／after 並把比較結果貼在 PR，省去人手起本機伺服器。
