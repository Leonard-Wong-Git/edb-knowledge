# PolicyChecker 里程碑回顧（2026-03-09 → 2026-08-19）

> **用途**：Leonard 分享用嘅回顧材料。由「校長面對成堆 EDB 文件」嘅原始痛點講到今日，列出**加咗咩、刪咗咩、關鍵決定點解咁落**。
> **出處**：`dev/archive/SESSION_LOG_2026_Q1~Q3.md`（207 個 session）、`dev/SESSION_HANDOFF.md`、`dev/PROJECT_MASTER_SPEC.md`、`dev/PROJECT_DECISIONS.md`、`git log`（578 commits）。
> **注意**：本文係 point-in-time 回顧文件，唔係 SSOT。live 數字一律以 `dev/SESSION_HANDOFF.md` 為準。

---

## 0. 一句話

> **由「幫我睇通告」開始，變成「答你嗰句嘢，我可以指返出邊份文件、邊一頁、邊一章」。**

五個月、207 個 session、578 個 commit、平台由 v0.9.0 行到 v3.3.0。中間最重要嘅一件事唔係加功能，而係**認清楚呢個系統嘅價值係「可追溯」而唔係「識答嘢」**——所以先會有「寧願答唔到，都唔可以答一句冇出處嘅嘢」呢條不變量。

---

## 1. 原始痛點（2026-03-09，Session 1）

**起點唔係知識庫，係一份需求文件。** 第一個 session 讀嘅係 `EDB-項目需求及規則總覽.docx`，要做嘅係「EDB 通告 AI 分析系統」——貼一份通告入去，AI 幫你摘要、揀出影響邊個角色、幾時死線。第一日交嘅嘢係一個 1,452 行嘅互動 HTML mockup（4 個分頁、詳情面板、月曆、角色選擇器）。

**同一日晚啲（KB01 session）就轉咗調。** 開始整 8 個角色知識庫底稿 + `fetch_knowledge.py`（爬 EDB / ICAC）。原因好直接：要 AI 分析通告，佢背後要有嘢對——**冇知識庫，分析出嚟嘅嘢冇根據**。

> 💡 **第一個岔口**：由「分析工具」變成「知識平台」。分析係表，知識庫係裏。

---

## 2. 六個階段

### 階段一 — 人手審核知識庫（2026-03-17 → 04-14）

| 日期 | 里程碑 |
|---|---|
| 03-17 | 首個 release **v0.9.0**「K1 EDB Knowledge Dashboard」 |
| 03-23 | 加通告分析 tab + embedding 主題偵測器 |
| 03-31 | 改名「學校管理知識中心」 |
| 04-03 | Admin 密碼保護 + 知識提煉／知識管理 tab（**人手 approve 先入庫**）→ v1.0.0 |
| 04-04 | `knowledge.json` / `guidelines.json` 公開端點（供下游通告系統 fetch） |
| 04-09~12 | `source_registry.json` 建立（來源／provenance 層）+ 新鮮度監察雛型 |

**呢個階段定咗兩條到今日都冇變嘅嘢：**
1. **人手閘門** — policy fact 一定要人 approve；只有統計數字可以 auto-approve。LLM 唔可以自主發佈。
2. **角色模型** — 由籠統嘅 `department_head` 拆成 `subject_head`（科主任）/ `panel_chair`（統籌主任）/ `eo_admin`（行政主任）。

**同期學到嘅嘢：**
- **白屏事故連續兩次**（單檔 React + Babel）→ 鎖定「`INITIAL_DATA` 直接內嵌做 JS object，**永遠唔准改返 async fetch**」。
- **04-12：EDB 全站改版，一次過打爛 26 條來源 URL** → 兩輪緊急復原。呢件事之後先有「URL 會 churn，要有監察」呢個概念。

---

### 階段二 — 兩通道架構 + 向量搜尋（04-15 → 05-02）★ 「拆散再切詞」就喺呢度

**04-15（S72）三件套一次過整起：**
- `ai_extract.py` — AI 批量抽事實
- `build_wiki_index.py` — **離線切 chunk + 嵌入**
- `wiki_search.py` — cosine 檢索 + LLM 合成

**切法（今日仍然係同一套）：**
- 每個 chunk **≤ 600 字元**（同下游通告系統嘅 600 字 budget 對齊）
- **overlap 60 字元**——特登重疊，保住跨 chunk 邊界嗰句嘢嘅上文下理
- 內容雜湊做 dedup（改咗文字＝新 id）
- 嵌入模型 `text-embedding-3-small`
- 第一版：**810 個 chunk，成本約 US$0.002**

**04-16（S74）架構鎖定 7 條決策**，最關鍵嗰兩條：
- **Channel A（人手審核）** 同 **Channel B（全 AI）** 分開兩條線，**互不污染**
- **Channel B 唔准 auto-write `role_facts.json`**——AI 抽出嚟嘅嘢唔可以自己爬入已核實庫

**05-01（S92）Channel B 正式上線**：Supabase pgvector、**2,822 chunks**。同場修咗個經典坑：anon role 要**同時**有 `GRANT USAGE ON SCHEMA` 同 `GRANT SELECT`，少一樣都係 0 結果。

**❌ 同期刪咗：** QAPanel 嘅 WordCloud 浮動動畫（視覺效果差，S74 決定刪，寫明「不復活」）。

---

### 階段三 — 資料質素治理（04-30 → 05-20）

呢個階段冇加過一個新功能，全部係「執返乾淨」。

| Session | 發現 | 處理 |
|---|---|---|
| S88 | 三層資料嚴重脫節：`dev/knowledge/` 有 1,001 條，repo root 同公開端點只有 109 條 | 以 dev 為真源覆寫三層 → 1,001 |
| S102 | 1,001 條入面 **484 條係 exact duplicate（48%）** | Strategy B 去重 → **792** |
| S102 | 學校行政手冊有兩份入庫（g24 300 chunks vs sag 415 chunks），**chunk 雜湊重疊 0%** | 唔係重複資料，係**同一份文件兩種切割方式**。唔可以 DELETE，改做後端 source alias 軟 dedup |
| S111 | 再深一層去重 | **792 → 455**（呢個 455 就係日後嘅凍結點） |
| S101 | 單一大文件洗版 | 加來源配額（每源最多 N 條入合成窗） |
| S116 | Channel B 召回率低 | `ivfflat.probes` 1 → 8（≈√lists）。同場撞出 **PGRST203 生產事故**：repo 入面嘅 `schema.sql` 簽名同 live 唔同，照套落去整出第二個 overload，Channel B 一度全 0 |
| S121 | 安全 | Supabase `wiki_chunks` RLS 加固 |

> 🔴 **最貴嗰堂（S116）**：`schema.sql` 係「意圖」，唔係「現況」。**改任何外部 DB 之前，一定要先 introspect live 真定義。**

---

### 階段四 — 北極星確立：頁數可追溯（05-19 → 05-28）★ 全個 project 嘅轉捩點

**05-19（S119）Leonard 親手 live-test 5 條 query**（CPD / 幼稚園收生 / 體罰 / STEAM / 收到警告信後果），一致裁定：

- Channel B（原文語義搜尋）**明顯最好**
- Channel A（已核實事實）**太多雜訊**
- A+B 合併**被 A 拖累**

**➡️ 決定：搜尋介面行 Channel-B-only。** A / A+B 嘅 user-facing 入口全部移除（code 留 dormant 可逆、後端 endpoint 唔刪）。

**同一個 session 定咗北極星：「頁數可追溯」。** 而呢件事結構上只有 Channel B 做得到——因為只有原文 chunk 先知自己出自邊一頁。

**跟住嘅診斷好殘酷：** live 測頁碼命中 **0/N**。但根因唔喺 UI、唔喺後端（顯示同 regex 都啱），係**語料本身冇頁碼**——全庫 113 份 extract，只有 **39 份帶 `=== Page N ===` 標記，74 份冇**。而 Leonard 平時測嗰啲高流量來源（學校行政手冊、g06、g26）全部係冇標記嗰批。

**兩步救：**
- **Option B（05-19）** — chunk 帶頁：切 chunk 時 carry 上一個見到嘅頁碼標記。39 個有標記嘅源 → 100% 帶頁；全庫可解析頁碼 **13.2% → 23.7%**。零風險：冇標記嘅 74 個源 byte-identical、id 唔變。
- **Option C（05-20 → 05-27）** — 用 PyMuPDF **逐頁重抽**（`repage_pdfs.py`），每頁前綴 `=== Page N ===`。先 3 個源 pilot → 32.2%，再分 7 批打晒 61 份無標記 PDF。

**意外收穫**：學校行政手冊重抽時，發現舊嘅 `pdftotext` 抽漏咗 **203 句**——重抽唔止加頁碼，仲救返內容（該源 83 → 383 chunks）。

**05-28（S132）品牌上線** — `policychecker.wongfu.net` 自訂域、OG 卡（1.7MB PNG → 151KB JPG 過 WhatsApp 600KB 閘）、favicon 4 個尺寸、`embed-sample.html` 俾學校 IT 嵌入。名由「K1 知識平台」改為對外「香港學校政策搜尋平台 / PolicyChecker」。

---

### 階段五 — 廣度補完、功能爆發、然後收斂（06-03 → 06-29）

**📈 加：**

| 日期 | 加咗咩 |
|---|---|
| 06-03 | 公開 `guidelines.json` **39 → 148 份**（由 registry 全集投影，新寫 generator `build_guidelines.py`，registry 做 SSOT） |
| 06-09 | **來源頁碼顯示 + 一撳跳頁**（desktop + mobile，`url#page=N`）；同時**拎走分數顯示**（用戶睇唔明 0.67 代表咩） |
| 06-10 | **NEW 文件分析**：上載學校文件 → 逐段同指引比對 → 出報告。順手驗證咗「香港 IP 出 OpenAI 會唔會被 block」＝用戶零影響（browser HK → Render 美國 → OpenAI） |
| 06-10 | Cloudflare **免 cookie** 統計（受眾含未成年，唔用 GA4） |
| 06-13~14 | 學校版政策範本大量生成（14 範疇 docx）+ 幼稚園 pilot |
| 06-14 | **文件標註**：原檔**就地** highlight + 內聯建議 |
| 06-14 | 平台 **v3.0.0** 改版 |
| 06-17 | DEBP 數字教育 6 份入庫；指引庫「資訊科技」正名「**數字教育**」；加跨範疇 `also_in`（一份文件可以出現喺多個範疇） |
| 06-22 | 手機 4 步 onboarding tour |
| 06-25 | WhatsApp 分享按鈕（綜合答案 → wa.me deep link） |
| 06-28 | **第 4 監察**：EDB 通告 watcher（接 Leonard 自己個 circular dashboard feed，每日 19:30 開 GitHub Issue） |
| 06-28 | 安全審計（12-agent workflow）→ 修 1 HIGH + 2 MED API abuse surface |
| 06-28~29 | **Option A 自動入庫管道**：私密 ops repo + GitHub Issue **剔掣批准** + 每日 cron executor（自動重抽 → embed → 入 Supabase → push → 寫更新日誌） |

**🗑️ 刪 / 停：**

| 日期 | 刪咗咩 | 點解 |
|---|---|---|
| 06-05（S143） | **Channel A 正式凍結 @455 條事實** | 下游轉用 Channel B；`knowledge.json` 停更但 schema 不變、繼續供料（對外契約零接觸） |
| 06-08（S151） | **成個 admin surface 完整移除** — 登入閘、知識提煉、知識管理、匯出、批准、CRUD 全刪 | Channel A 凍結 + 下游已轉 B → 人手策展功能淘汰。`app.html` **4,100 → 2,935 行（−1,176）**。公眾端變成完全唯讀 |
| 06-10（S154） | 通告分析入口暫停 | Leonard 指示（06-17 S171 再重開） |
| — | `k1-dashboard.html` / `landing.html` / `k1-wiki.html` | 早期實驗頁，刪咗不復活 |
| 05-18（S115） | MemPalace 記憶同步 | 唔再用 |

> 💡 **呢個階段最值得講嘅一件事**：06-14 文件標註原本用 **Word 批註（comments.xml）**做建議。Leonard 攞真實「數學」課程 docx 一試，即刻反饋：「有 highlight 但睇唔到建議」——因為 Word 批註要開批註窗格先見到，一般檢視同匯出時係**隱形**嘅。同一個 session 即刻改成「**可見內聯註解段**」（💡相關指引 / ⚠建議修訂，直接插喺 highlight 後面）。
> **真檔試用一次，勝過離線驗證十次。**

---

### 階段六 — 量度、收斂、返去執頁碼（07-05 → 08-19）

**07-05（S192）系統分析 + 路線圖**：誠實評估——做得好 4 項、技術債 7 項。當時桌面已經有 **8 個 tab**（平台介紹／政策搜尋／指引文件／通告分析／文件分析／文件標註／政策範本／文件修訂），寫明「IA 需要收斂」。出咗 R1–R8 排序改進項。

**07-26（S194）R1 落地**：檢索 eval harness + **第 5 監察「封面核對」**（防止 registry 標題同真文件封面唔同）。

**07-29 → 07-31（S197–S201）Channel A 退役量度**，三件揸得住嘅嘢：
- **機械判定「已清」有 44% 撐唔住人手覆核**——唔可以用機器判斷取代讀原文
- **judge / synthesis 用緊嘅 model 唔係 code 入面嘅 default**：`env.ts` fallback 係 `gpt-4.1-nano`，但 Render 實設 `OPENAI_MODEL=gpt-4o-mini`，而 `/health` 唔報 model。任何量度引用做「生產行為」之前，一定要去 dashboard 確認
- judge V3 ship + footnote judge-bypass 收窄

**08-17（S204）**：人手編制文件群入庫、頁碼歸屬修正、平台 **v3.3.0**、加使用計數器。**同時暫收「政策範本下載」**（manifest 未跟知識庫更新，用 feature flag 收起，面板 code 原封未動，重生 manifest 後一 flag 就返）。

**08-18（S206）頁碼指路修復** — 北極星回頭再執一次：
- 根因＝`expand_vault.py` **兩層甩頁碼**（抽 PDF 時冇寫標記、切 chunk 時冇 carry）
- 兩層都修，`carry_pages()` 抽出嚟由兩條管道共用
- 11 個源重入 → **全庫無頁碼 chunk 1,859 → 451（修好 1,408 條）**
- 真 UI 實拍：「資助小學教學人員編制 · 3 個片段 · 頁 1, 3 ↗」

**08-19（S207）指章唔係指頁** — 網頁來源冇頁碼，點指？
- 關鍵觀察：`wiki_chunks.url` **本身已經係 per-chunk 欄位**，只不過入庫時全部填同一個 landing 頁 → **前端、後端、schema 一律唔使改**
- 加 `section_urls` opt-in map：g14 76 條 → 指返 10 個子頁；g17 13 條 → 6 個目標（3 子頁 + 3 附件 PDF，仲保住 `#page=N`）
- 順手揪出 g20/g25 **一直係亂碼**（EDB 唔出 charset → requests 當 ISO-8859-1）。**反直覺位：**「至少 200 字」嗰個健康守門一直**放行**佢哋，正正因為亂碼令字元數虛脹

---

## 3. 數字弧線

| 指標 | 起點 | 中途 | 今日 |
|---|---|---|---|
| **知識片段（chunks）** | 810（本地） | 2,822 → 10,682 → 15,874 | **17,473** |
| **已核實事實** | 109 | 1,001 → 792 | **455（凍結）** |
| **可解析頁碼比例** | ~13% | 24% → 32% | **97.4%**（無頁碼只剩 451 條） |
| **公開指引文件** | 39 | 148 | **158**（app 內庫 177） |
| **登記來源** | — | 120（已提取）→ 151 → 244 | **268** |
| **平台版本** | v0.9.0 | v1.0 → v2.3 → v3.0 | **v3.3.0** |
| **公開 tab** | 6 | 8（07月高峰） | **4**（範本暫收） |
| **自動監察** | 0 | 4 | **5** + 每日自動入庫管道 |

---

## 4. 功能生死簿

**今日仲喺度（4 個公開 tab）**
`ℹ️ 平台介紹` · `🔍 政策搜尋` · `📝 文件標註` · `📚 指引文件`

**加咗又拎走 / 收埋**

| 功能 | 結局 |
|---|---|
| QAPanel WordCloud | 刪，寫明不復活 |
| Channel A / A+B 搜尋介面 | 移除（S119），code dormant 可逆 |
| Admin 登入 + 知識提煉 + 知識管理 | **完整移除**（S151），−1,176 行 |
| `k1-dashboard.html` / `landing.html` / `k1-wiki.html` | 刪，不復活 |
| MemPalace 記憶同步 | 移除（S115） |
| 通告分析 | 暫停（S154）→ 重開入口（S171）；panel 本體早已係 dead code 清走 |
| 文件分析 + 文件修訂 | **合併**成「文件標註」（S161） |
| Word 批註做建議 | 改成可見內聯註解（真檔試用反饋） |
| 政策範本下載 | 暫收（S204），flag 一開即返 |
| `q.html` / `t-purchase.html` | Dormant 留檔，只去 inbound link |
| 搜尋結果分數顯示 | 拎走（S153），用戶睇唔明 |

---

## 5. 十一條真金白銀學返嚟嘅紀律

1. 判斷 judge / synthesis 行為之前，**先去 Render dashboard 確認實際 model**。
2. 落 negative result 結論之前先問：「如果目標訊號存在，呢個工具顯唔顯示到？」搵已發生事件做對照組。
3. **報一個數之前，打開數字背後至少一個實例親眼睇。** 搜尋命中唔算證據。
4. 剷任何嘢之前，分清「有可引用替代品」同「唯一來源」。
5. 任何檢索改動一律 **eval before → after** 對；任何合成閘改動一律 **live before → after** 對。
6. judge 係 LLM、非決定性 → 任何 verdict 要**重複跑 ≥3 次**先落結論。
7. **入庫 ≠ 可達。** 來源集 / 關鍵字 / spotlight / route expansion 四層每層都要實測。
8. **交接寫低嘅方案框架本身可以係錯。** S206 實測證明交接寫嘅兩個修法**兩個都修唔到佢自己指嘅 case**。動手前 live 重現。
9. 「應該冇」唔係「冇」。用戶答「應該一行都冇」係期望語氣，追問一句先落結論。
10. **報 population 數字要即刻拆類**：邊部分修得到 / 修唔到 / 唔關事。淨拋總數，對方會用自己嘅 mental model 填補。
11. **守門要證明佢會紅。** S207 個 `--prove-assertions` 模式（用 no-op 實作跑一次，證明測試真係會失敗）第一次跑就捉到兩個 regex 陷阱。

---

## 6. 由頭到尾嘅一條線

```
痛點：校長面對成堆 EDB 文件，唔知邊句嘢出自邊度
  ↓
做分析工具 → 發現冇知識庫嘅分析冇根據
  ↓
起人手審核知識庫（Channel A）→ 質素靚但覆蓋窄、擴唔大
  ↓
起 AI 原文向量庫（Channel B）：拆散、切 600 字 chunk、重疊 60 字、嵌入
  ↓
Leonard 實測裁定：原文搜尋贏，已核實事實反而係雜訊 → 轉 Channel-B-only
  ↓
定北極星：唔止答到，仲要指到「邊份文件、第幾頁」
  ↓
發現頁碼根本冇入語料 → 兩步救（carry + 逐頁重抽）→ 13% → 97%
  ↓
凍結 Channel A、拆走 admin、收窄介面 → 公眾端變成一個乾淨嘅唯讀查詢面
  ↓
自動化：5 個監察 + 每日自動入庫（Issue 剔掣批准）
  ↓
網頁來源冇頁碼？→ 逐條 chunk 指返自己嗰一章（S207）
```

**核心價值定位（寫死喺 spec 嘅不變量）：**
> 寧可答「搵唔到」，都唔可以俾一個冇來源、回溯唔到 EDB 原文嘅答案。
