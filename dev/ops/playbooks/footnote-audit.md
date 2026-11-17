# Playbook：註腳審核（footnote-audit）

- **何時用**：`footnote-anchor` Issue 有新項目（每月的機械核對報原文有變，見下一節）；`PAGE_ANCHORED` 高於基準；新增一批註腳之後。
- **建議模型**：中階，**嚴格唯讀**。更正由主 session 在 Leonard 批准後做。
- **背景**：註腳是人手策展的短答案，檢索時優先採用，所以錯一條就會直接答錯。S249 首次審核 41 條，找到 2 條金額／機構錯誤、3 條指錯 PDF；S250 由中階模型按本程序審核全部 177 條（約 14 分鐘、36 萬 token），找到 28 條頁碼錯、9 條內容不符，28 條頁碼經主 session 獨立核實全部成立。

## 每月機械核對（S252 起，不用模型）

每月 2 日 `.github/workflows/footnote_anchor_check.yml` 自動跑 `dev/source/check_footnote_anchors.py`：下載每條註腳所引的原文，檢查 `dev/source/footnote_anchors.json` 記下的一句原文（錨句）是否仍在所記的頁。它只看**原文有沒有變**，不判斷註腳寫得對不對；全量的語意審核仍照下面「步驟」做。工具唯讀，沒有寫入模式。

本機重跑：`/usr/local/bin/python3 dev/source/check_footnote_anchors.py --check [--only <註腳 id>] --out <scratchpad>/report.json`（輸出一律寫到 repo 以外）。

| 結果 | 意思 | 怎樣處理 |
|---|---|---|
| `OK` | 錨句仍在所記的頁 | 不用處理 |
| `MOVED` | 錨句在同一份文件的另一頁（報告列出新頁） | 打開該 PDF 核實新頁確有該句 → 在 `dev/source/url_overrides.json` 改 `#page=`，跑 `dev/apply_url_overrides.py` 預演，交 Leonard 批准後 `--execute` → 把 `footnote_anchors.json` 該條的 `page` 改成同一頁（`--self-test` 會核對兩檔一致） |
| `GONE` | 整份文件都找不到錨句，原文多半已換版 | **不要自行改註腳。** 把舊錨句、註腳現時的寫法與新版原文的相應段落並列，交 Leonard 決定更新還是退役；定案並寫入後才改 `footnote_anchors.json` 的 `quote` |
| `FETCH_FAIL` | 下載失敗（列出 HTTP 狀態） | 單次不通知；同一條連續兩次才列入 Issue。先用瀏覽器開連結：連結失效按 `source-reingest.md` 網址搬遷部分處理 |

全部 `OK` 時 Issue 自動關閉。新增註腳時，同時在 `footnote_anchors.json` 加一條（網址不帶 `#page=`、PDF 實際頁序、一句逐字的原文），並把 `_meta.count` 加一；錨句要先以 `--only <id>` 實測為 `OK`。現時 14 條註腳未有錨句（清單在該檔 `_meta.not_covered`），月檢看不到它們。

## 步驟

1. **取出所有註腳**：`wiki_chunks?content_type=eq.footnote_curated&select=id,source_id,text,url`（唯讀，金鑰在 `backend/.env`，不得印出）。
2. **逐條核對出處**：下載 `url`（去掉 `#page=`）所指的文件到 scratchpad（每份只下載一次，相隔約 1 秒；全部約 80 份，需時十多分鐘）。
   - **PDF**：逐頁抽文字。`#page=N` 的 N 是 **PDF 的實際頁序**（第一頁為 1），不是頁面上印的頁碼。
   - **網頁**：抽主內容區文字比對。
   - **電子版香港法例（e-Legislation）**：頁面由 JavaScript 產生，直接抓取只得空殼；歸類為「找不到」並註明原因，不要猜。
   - 從註腳中取**數字、金額、日期、專有名詞、條件與方向（可以／必須／不可）**，以及一句關鍵句，在原文搜尋（去空白、NFKC 正規化後比對）。註腳多是以口語中文轉述英文或書面中文原文：**措辭和語言不同不算不符**，只有上述實質內容不同、或原文根本沒有這個說法，才算。
   - 一併核對註腳自己寫的出處標籤（例如「註 3」、文件日期、學年）是否與所引文件相符。
   - 內容橫跨兩頁時，頁碼取**首句或主要數字所在的一頁**，並在備註列出其餘頁。
3. **每條一個結論**：

| 結論 | 意思 |
|---|---|
| 相符 | 關鍵數字與句子都在 `#page=` 所指的那一頁 |
| 頁碼不對 | 內容在同一份 PDF 的另一頁 → 建議新頁碼 |
| 文件不對 | 內容不在這份 PDF，在另一份（列出是哪一份、哪一頁） |
| 內容不符 | 數字或說法與原文不同 → 並列註腳原句與 PDF 原句 |
| 來源已更新 | 所引網頁現時的數字／年度已不同（註腳當時可能正確）→ 並列兩者，交 Leonard 決定更新還是退役 |
| 找不到 | 說明搜尋過甚麼（包括抓不到的原因） |

4. **交回**：`audit.json`（每條：id、現有 url、結論、找到的頁碼、比對到的原句、備註）與一份按來源分組的表；另列「內容不符」的清單。分開「已核實」與「推斷」。

## 主 session 收到之後

- 抽查：每條擬寫入的頁碼，用比對到的原句再對 PDF 核實一次——原句要在建議的頁、而且不在現時所指的頁。
- 「內容不符」逐條自己讀原文再下結論；sub-agent 對中文語意的判斷屬推斷，不是機械核實。
- 頁碼／網址：加入 `dev/source/url_overrides.json`，跑 `dev/apply_url_overrides.py`（先 dry-run）。
- 內容更正：見 `source-reingest.md` 的「註腳」一節（清單 `dev/source/footnote_corrections.json`＋工具 `dev/apply_footnote_corrections.py`）。
- **沒有最強模型時**：「內容不符」不要自行改寫。只做兩件事——把註腳原句與原文原句並列交給 Leonard；Leonard 選定寫法後才登記。數字、金額、年度、頁碼這類可逐字對照的更正，可以直接備妥預演。
- 改了之後，`dev/source/qc_report.py` 的 `no_page_anchor` 基準要相應調低（基準只可向下調）。
