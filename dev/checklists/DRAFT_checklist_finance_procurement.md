# 校本「採購及財務」政策文件 — 要求清單＋文件骨架（DRAFT v0.2）

> **狀態：DRAFT v0.2，待 Leonard 審。** 試點範疇＝採購及財務（S155）。本檔係預生成 derived artifact 草稿；未發佈、未接駁任何 product surface。發佈形態（已定）＝可下載 docx。
>
> **v0.2 變更（2026-06-11 Leonard 審訂）**：採購程序拆 8 個子節；開標／標書批核委員會 3 條由「治理權責」移入「採購委員會（IMC 架構）」子節（按學校憲章設立，標明治理脈絡）；條文維持義務句；引文維持 PDF 原樣。
>
> **生成方法**：5 個 EDB 文件源（Supabase Channel B，99 chunks，頁碼覆蓋 100%）→ 3 組蒸餾 → 獨立對抗覆核 agent 逐條重拉 chunk 驗引文＋頁碼 → 完整性批判 agent 重讀全庫搵漏 → 本機機械重驗（exact→去空格→NFKC 三級引文比對＋頁碼重計）。每條要求必帶原文引文＋頁碼，引唔到嘅一律唔出（寧缺勿估）。
>
> **引文說明**：引文照抄 PDF 文字層原樣，怪空格／異體字（Unicode 相容表意字）係抽取產物，唔係錯字。頁碼＝chunk 內最近嘅 `=== Page N ===` 標記；標 ⚠️ 者為近似頁碼（引文位於 chunk 首個標記之前）。

## 來源文件（5 源，URL 已驗 200／PDF，2026-06-11）

| source_id | 文件 | 連結 |
|---|---|---|
| `g01` | 《資助學校採購程序指引（2025年10月更新）》 | [PDF](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf) |
| `g02` | 《設有法團校董會的資助學校財務管理指引》 | [PDF](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf) |
| `coa_imc_1_19` | 《資助則例（設有法團校董會資助學校適用版本）》 | [PDF](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf) |
| `fin_mgmt_notes_aided` | 《資助學校財務管理注意事項》 | [PDF](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf) |
| `bank_choice_notes` | 《學校選擇銀行注意事項》 | [PDF](https://www.edb.gov.hk/attachment/tc/The%20Choice%20of%20Bank%20Counterparties_EDB%20web_tc.pdf) |

註：`role_facts_finance`（Channel A 核實事實，25 條）天生冇頁碼，唔用做本清單 grounding。《資助則例》只取財務相關章節（教職員聘任、收生、校舍等非財務章節不在範圍）。

## A. 文件骨架（章節地圖）

校本「採購及財務」政策文件建議章節。每章列出「呢章要講乜」＋對應要求條目。

| 章 | 章節 | 內容 | 條目數 |
|---|---|---|---|
| 1 | 治理權責 | 法團校董會作為公帑受託人嘅總體責任同批核權限 | 6 |
| 2 | 財務管理框架 | 校本財務管理機制嘅基本元素：長遠財務計劃、周年預算編制與監控 | 12 |
| 3 | 政府撥款與津貼使用 | 各類津貼嘅指定用途、轉撥規則同上限 | 10 |
| 4 | 採購程序 | 採購門檻、報價／招標程序、開標／評標／批核、委員會、單一報價例外 | 41 |
| 5 | 工程設備與採購 | 工程及設備津貼計算、大型修葺申請 | 3 |
| 6 | 廉潔與利益申報 | 防賄條例、利益衝突申報、職務分隔避嫌 | 10 |
| 7 | 薪金津貼帳目 | 薪酬按《匯編》支付、多付／少付薪金處理 | 4 |
| 8 | 銀行與現金管理 | 銀行帳戶管理、存款分散、現金支票處理 | 19 |
| 9 | 收費及代收費 | 堂費、售賣物品利潤上限、商業活動收益用途 | 2 |
| 10 | 風險與保險 | 政府承擔範圍、學校自購保險項目 | 2 |
| 11 | 核數監察與紀錄 | 帳目查核、紀錄保存年期、配合審計 | 13 |

## B. 要求清單

### 1. 治理權責
_法團校董會作為公帑受託人嘅總體責任同批核權限_

- **R-1.1** 校董會或法團校董會須確保學校在任何時候都採用公平、開放及透明的採購程序，並設有足夠的監察及制衡機制以防偏私、貪污及舞弊。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=2)
  - 引文：「校董會或法團校董會 應確保其學校在任何時候都採用 公平、開放及透明的採購程序」
- **R-1.2** 商業活動必須在法團校董會會議上討論及通過，並在會議記錄中妥善記錄。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 6 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=6)
  - 引文：「必須在法團校董會會議 上 討 論 及 通 過 ， 並 在 會 議 記 錄 中 妥 善 記 錄」
- **R-1.3** 法團校董會須審慎運用公帑（包括各類津貼及其他特定教育用途的政府撥款），並就公帑的運用作出交代。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 17 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=17)
  - 引文：「法團校董會 必須審慎 運用公帑」
- **R-1.4** 法團校董會以政府資助金受託人身分領取津貼，必須遵守資助條件；違反規定政府可撤回津貼。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=8)
  - 引文：「若未能遵守本《資助則例》所載的各項規定和條件，政府可撤回發放予該校的津貼」
- **R-1.5** 法團校董會須肩負全責處理人事、僱傭及投訴事宜，確保撥款運用合乎成本效益和經濟原則。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 13 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=13)
  - 引文：「確保撥款運用合乎成本效益和經濟原則」
- **R-1.6** 防止學校陷入嚴重財務混亂；不符資助條件時常任秘書長可發通知書要求改善，逾期未補救可減少、停止或撤回津貼。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 16 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=16)
  - 引文：「減少、停止或撤回任何發放予該校的津貼」

### 2. 財務管理框架
_校本財務管理機制嘅基本元素：長遠財務計劃、周年預算編制與監控_

- **R-2.1** 批核人員須先確定可獲得所需撥款，方可批准接納推薦的書面報價單／標書。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「批核書面報價/標書的人員須 先確定可獲得所需的撥款 後，方可批准接納推薦 的書面報價 單/標書」
- **R-2.2** 周年財政預算須規劃周詳、避免出現赤字預算，並須獲法團校董會批准。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 7 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=7)
  - 引文：「避免出現赤字預算。學校的周年財政預算應獲法團校董會的批准」
- **R-2.3** 開支與預算金額出現重大偏差時，須即時展開調查、加以解釋及適當糾正，並向法團校董會匯報。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 7 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=7)
  - 引文：「便 須 即 時 展 開 調 查 、 加 以 解 釋 及 適 當 糾 正 ，並向法團校董會匯報」
- **R-2.4** 經核准的財政預算如在學年中經過修訂，須由法團校董會批核或確認。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 7 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=7)
  - 引文：「有關預算 如經過修訂，須由法團校董會批核或確認」
- **R-2.5** 須正式設立會計、內部和外部監控制度，把一切收支適當入帳。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=8)
  - 引文：「正式設立會計、內部和外部監控制度，把一切收支適當入帳」
- **R-2.6** 委派財務管理職務時須遵守劃分及輪換職務原則，負責邀請供應商投標的人員不應同時負責批核該次投標。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=10)
  - 引文：「負責邀請供應商投標的人員，不應同時負責批核該次投標」
- **R-2.7** 學校須定期（例如按季度）向法團校董會匯報學校的財政狀況。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=11)
  - 引文：「學 校 須 定 期 (例 如 按 季 度 )向 法 團 校 董 會 匯 報 學校的財政狀況」
- **R-2.8** 須在向各持分者分發的周年校務報告中載錄財務摘要。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 12 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=12)
  - 引文：「向各持分者分發的周年校務報告中載錄財務摘要」
- **R-2.9** 校本財務管理機制須涵蓋長遠財務計劃、周年預算及預算管理、會計、資料披露及報告、內部監察及外部審計等基本元素。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=5)
  - 引文：「包括但不限於長遠財務計劃、周年預算及預算管理、會計、資料披露及報告、內部監察及外部審計規定」
- **R-2.10** （覆核補遺）在正常情況下學校不應借入款項；如擬借入款項，事前須取得法團校董會批准方可進行。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=7)
  - 引文：「資 助 學 校 如 擬 借 入 款 項 ， 事 前 須 取 得 法 團 校 董會的批准才可進行。」
- **R-2.11** （覆核補遺）投資活動所引致的虧損不可以政府津貼、宿費及資本儲備金支付（非指定用途捐款除外），擬進行的投資必須在法團校董會會議記錄中記載討論詳情和議決，虧損責任由法團校董會承擔。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=8)
  - 引文：「投 資 活 動所引致的虧損則不可以政府津貼、宿費及資本儲 備 金 支 付，非 指 定 用 途 的 捐 款 除 外」
- **R-2.12** （覆核補遺）商業活動所產生的利潤或淨收入，如未經教育局常任秘書長事先以書面准許，不得運用於任何不能使該校學生直接受益的用途上。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 13 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=13)
  - 引文：「任何因商業活動所產生的利潤或淨收入，如未經教育局常任秘書長事先以書面准許，學校不得運用於任何不能使該校學生直接受益的用途上。」

### 3. 政府撥款與津貼使用
_各類津貼嘅指定用途、轉撥規則同上限_

- **R-3.1** 員工紀念品／附帶福利（包括膳食供應或膳食津貼）、消閒娛樂開支、貸款及捐款等項目，不應以擴大的營辦開支整筆津貼支付。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 16 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=16)
  - 引文：「均不應以擴大的營辦開支整筆津貼支付」
- **R-3.2** 如學校活動的收益會存入學校本身經費之內，有關活動的開支不應以政府經費支付。
  - 出處：《資助學校財務管理注意事項》第 4 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=4)
  - 引文：「有關活動的開支不應以政府經費支付」
- **R-3.3** 接受常任秘書長按發放規定及程序調整津貼數額，確保公帑運用符合經濟效益和物有所值。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 17 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=17)
  - 引文：「以確保公帑的運用 符合經濟效益和物有所值」
- **R-3.4** 各類津貼（經常、非經常、工程及設備撥款）只可按其特定目的或指定用途使用。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 18 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=18)
  - 引文：「津貼以經常撥款、非經常撥款或工程 及設備撥款形式 發放，以作特定目的或指定用途」
- **R-3.5** 額外教育撥款只可用以支援推行該等撥款所核准的新教育措施及計劃，不得挪作他用。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 18 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=18)
  - 引文：「這些額外教育撥款，只可用 以 支 援 學 校 推 行 該等教育撥款所 核准的新教育措施及計劃」
- **R-3.6** 轉撥擴大的營辦開支整筆津貼餘款，必須訂定適當的程序、客觀的準則和清晰的批核者。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 22 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=22)
  - 引文：「學校必須為轉撥這項 津貼的 餘款，訂定適當的程序、客觀的準則和清晰的批核者」
- **R-3.7** 特定用途津貼（如整合代課教師津貼、租金及差餉津貼）只可用於特定用途，不可調撥作其他用途。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 22 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=22)
  - 引文：「這些津貼 只可用於 特定用途，不可調撥作其他用途」
- **R-3.8** （覆核補遺）不得以政府津貼、宿費及資本儲備金支付借入款項所招致的利息（非指定用途的捐款除外，且須事先取得捐款人同意）。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=7)
  - 引文：「不 得 以 政 府 津 貼、宿 費 及 資 本 儲 備 金 支 付借 入 款 項 所 招 致 的 利 息」
- **R-3.9** （覆核補遺）不得以政府津貼償還貸款。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 8 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=8)
  - 引文：「不得以政府津貼償還貸款。」
- **R-3.10** （覆核補遺）擴大的營辦津貼餘款補貼涵蓋範圍以外開支設有上限：不超過政府資助計劃經常開支的50%，以及私人捐贈或籌款計劃所得家具、設備和其他設施或教育服務經常開支的25%，並須就轉撥餘款制定適當程序、客觀準則及清晰批核者。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=5)
  - 引文：「擴 大 的 營 辦 津 貼 的 餘 款 ， 可 用 來 補 貼 不 超 過 ：—   政 府 資 助 計 劃 的 經 常 開 支 的 50%； 以 及—   透過私人捐贈或其他籌款計劃而得到的家具、設備和其他設施或教育服務的經常開支 的 25%。」

### 4. 採購程序
_採購門檻、報價／招標程序、開標／評標／批核、委員會、單一報價例外_

> 註：以下「採購委員會（IMC 架構）」子節所列委員會，屬法團校董會（IMC）架構下按學校憲章／規程設立及委任；其組成與權限同時受第 1 章治理規範約束。

#### 4.1 通用原則
_公開公平競爭、職務分工、資料同等與保密、合約條款_

- **R-4.1** 所有採購工作須符合公開、公正及公平競爭的原則，並遵守有關採購指引／程序的通告。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=10)
  - 引文：「所有採購工作亦須符合公開、公正及公平競爭的原則」
- **R-4.2** 報價／招標文件須加入維護國家安全條款，列明學校可取消涉危害國家安全供應商的資格及立即終止相關合約。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 3 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=3)
  - 引文：「在其報價／招標文 件中加入以下具體條款，列明基於國家安全而容許學校取消供應商的資格」
- **R-4.3** 採購過程須適當分工，邀請報價／投標、驗收物料及認收服務、確認付款等工序須由不同教職員處理。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「驗收物料及認收服務、確認付款等工序應由不同的教職員處理」
- **R-4.4** 須讓所有獲邀供應商得知充分和同等的報價／投標規定及規格資料，不得讓個別人士獲得額外資料或通知。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「學校不得讓個別人士獲得額外的報價 /投標資料或通知」
- **R-4.5** 報價及招標資料須保密處理並按知情需要限制取閱，相關往來信函由收到報價單／標書起至作出選擇決定為止一概列作限閱文件。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「有關報價及招標的資料須 保密處理，並按知情需要限制有關人士取得資料」
- **R-4.6** 邀請報價／投標時應盡可能同時邀請上次獲批核而服務令人滿意的供應商競投，其他供應商應以輪流方式邀請以示公平。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「應盡可能同時邀請上一次獲批核的供應商進行競投」
- **R-4.7** 物品須驗收無誤後方可付款。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 18 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=18)
  - 引文：「物品驗收無誤後，即可在          年      月     日付款」
- **R-4.8** 須妥善備存報價和招標的完整記錄，以供教育局審核。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 14 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=14)
  - 引文：「學校須妥善備存報價和招標的完整記錄，以供教育局審核」

#### 4.2 採購門檻與批核權限
_四級財政限額、12 個月累積上限、規避禁令_

- **R-4.9** 每次預算5,000元或以下的採購毋須公開競投，但須由校內適當職級人員證明採購屬必須及價格公平合理，並由校長／副校長批核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「5,000元或以下  毋須為採購物料或服務進行公開競投，但校內適當職級的人員須證明有關採購是必須」
- **R-4.10** 每次預算5,000元以上至50,000元的採購須邀請最少兩個口頭報價，由校長／副校長批核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「5,000元以上至 50,000元 邀請最少兩個口頭報價」
- **R-4.11** 每次預算50,000元以上至200,000元的採購須邀請最少五個書面報價，由校長批核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「50,000元以上至 200,00 0元 邀請最少五個書面報價  校長」
- **R-4.12** 每次預算200,000元以上的採購須邀請最少五名供應商投標，由標書批核委員會批核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「200,000元以上 邀請最少五名供應商投標」
- **R-4.13** 同一類項目須在12個月內累積價值不超過50,000元及200,000元，方可分別以口頭報價及書面報價方式重複採購。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「在12 個月內，採購項目的累積價值不超過50,000 元及200,000元的情況下」
- **R-4.14** 採購物料及僱用服務須按財政限額進行報價／招標：5,000元以上至50,000元邀請最少兩個口頭報價、50,000元以上至200,000元邀請最少五個書面報價、200,000元以上邀請最少五名供應商投標。
  - 出處：《資助學校財務管理注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=1)
  - 引文：「50,000 元以上至200,000 元邀請最少五個書面報價」
- **R-4.15** 不得分拆訂單、分期採購或縮短一般合約期，藉以規避財政限額、批核規定或報價／招標程序；同類物料服務須集中在同一附表競投。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「學校不得分拆訂單，藉以避免遵守批核報價單 /標書的規定或報價 /招標程序」
- **R-4.16** 不應把所需的同類項目分多次購買或藉縮短一般合約期，從而規避採購金額限制。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 14 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=14)
  - 引文：「資助學校不應把所需的同類項目分多次購買，或藉着縮短一般合約期，從而規避金額限制」

#### 4.3 口頭報價程序
_口頭報價嘅執行與記錄_

- **R-4.17** 無法邀請或收到所定最少數目口頭報價時，須在「按口頭報價購貨表格」說明，並由科主任或一名薪級點不低於總薪級表第25點的教職員批簽。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 6 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=6)
  - 引文：「由有關的科主任或一名薪級點不低於總薪級表第 25點的教職員批簽」
- **R-4.18** 作出口頭報價推薦前須就價錢質素與市場供應情況作比較，最終未選擇報價最低者必須記下原因。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 6 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=6)
  - 引文：「如最終未有選擇報價最低者，則必須記下原因」

#### 4.4 書面報價／招標 — 邀請與接收
_邀請期限、文件要求、密封遞交、投標箱保管、延期與逾期處理_

- **R-4.19** 邀請書面報價／招標與截止日期一般須相隔最少三周；緊急情況可經校長批准縮短至兩個完整工作周，原因須記錄在案。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 5 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=5)
  - 引文：「一般應該相隔最少三周，但在緊急情況下，可經由校長批准」
- **R-4.20** 邀請書面報價／招標文件須清楚說明預先設定的評審準則及評分制度（如適用），並清楚註明截止報價／截標日期及時間。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=7)
  - 引文：「亦須在邀請書面報價 /招標文件中清楚說明預先設定的評審準則及評分制度」
- **R-4.21** 不能邀請足夠數目（最少五名）供應商報價／投標時，須將情況記錄在案並事先取得校董會／法團校董會批准。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=7)
  - 引文：「如不能邀請足夠數目的供應商 ，校方須把有關情況記錄在案，並事先取得校董會 /法團校董會的批准」
- **R-4.22** 如未能邀請足夠數目的供應商而預計採購金額超過50,000元，須把有關情況記錄在案，並事先取得校董會／法團校董會批准。
  - 出處：《資助學校財務管理注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=1)
  - 引文：「須把有關情況記錄在案，並事先取得校董會／法團校董會的批准」
- **R-4.23** 須要求供應商將書面報價單／標書一式兩份密封遞交，信封註明編號及截止日期、以校長為收件人，並知會供應商勿在封面顯示身份。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=7)
  - 引文：「供應商須填 妥書面報價單/ 標書一式兩份，然後放入註明「 書面報價單/標書」的信封內封密」
- **R-4.24** 收到的書面報價單須上鎖保管，鎖匙由校內適當職級人員保管，而標書必須即時全數放進投標箱。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=8)
  - 引文：「學校須將收到的書面報價單上鎖，鎖匙由校內適當職級的入員保管」
- **R-4.25** 投標箱須雙重上鎖，鎖匙由校內不同人員保管，其中一條由督導級人員保管，校長另持一套後備鎖匙。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=8)
  - 引文：「投標箱須雙重上鎖，鎖匙須由校內的不同人員保管」
- **R-4.26** （覆核補遺）如在截止投標當日八號或以上熱帶氣旋警告信號懸掛，或黑色暴雨警告信號或政府公布的「極端情況」生效，投標箱須改於下一個工作日的同一時間開啟。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=8)
  - 引文：「如在截止投標當日 ，八號或以上熱帶氣 旋警告信號懸掛，或黑 色暴雨警告信號或政府公 布的「極端情況」 生效，投標箱應於 下一個工作日的同一時間開啟。」
- **R-4.27** （覆核補遺）除非只有一個供應商獲邀，否則不應考慮逾期遞交的書面報價單／標書；遲交的標書應原封不動註明逾期，由開啟人員簡簽後轉交批核人員決定是否仍然有效。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 10 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=10)
  - 引文：「除非只有一個供應商獲邀，否則不應考慮逾期書面 報價單/標書。」

#### 4.5 開標、評審與批核
_開標程序、評審準則、批核與發出訂單_

- **R-4.28** 指定截標日期及時間前不得開啟任何標書，開標及標書審核委員會須於截標當日指定時間開啟投標箱取出標書審核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 9 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=9)
  - 引文：「學校在指定截標的日期和時間前不得開 啟任何標書」
- **R-4.29** 開啟人員須在書面報價單／標書上簡簽及蓋上日期，逐一核對正副本內容是否完全相同，發現更改須以紅筆圈出修訂數額並簡簽。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=10)
  - 引文：「應在書面報價單/標書上簡簽及蓋上日期，並逐一檢查，看看書面報價單 /標書的正本和副本內容」
- **R-4.30** 批核時一般應選取合符規格而出價最低的書面報價單／標書，不選取出價較低者須記錄理據；使用評分制度則推薦最高整體評分者。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「如學校 不選取出價較低的 書面報價單 /標書，便應記錄不選取的理據」
- **R-4.31** 不接納符合規格而出價最低／較低的報價或標書時，應提供理據。
  - 出處：《資助學校財務管理注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=1)
  - 引文：「應提供不接納符合規格而出價最低／較低的理據」
- **R-4.32** 須在書面報價單／標書有效期屆滿前發出訂單。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「學校應在書面報價 單/標書的有效期屆滿前，發出訂單」

#### 4.6 採購委員會（IMC 架構）
_開標及標書審核委員會、標書批核委員會嘅組成與分隔_

- **R-4.33** 書面報價單須由校長委任兩名校內適當職級人員負責開啟、審核及轉交有關科目教師評估推薦，最後由校長批核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 9 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=9)
  - 引文：「校長須委任兩位校內適當職級的 人員負責開啟、審核」
- **R-4.34** 校長須於開標當日前至少三個工作天委出開標及標書審核委員會，成員包括兩名學校人員（一人薪級點不低於總薪級表第25點，另一人不低於文書助理或同等職級）。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 9 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=9)
  - 引文：「校長須在開標當日前 至少三個工作天 委出開標及標書審核委員會」
- **R-4.35** 標書批核委員會成員須包括校監／校董、校長、一名教師及一名家長教師會代表或家長校董，並由校董會／法團校董會委任。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「成員須包括校監 /校董、校長、一名教師及一名家長教師會代表或家長校董」
- **R-4.36** 開標及標書審核委員會和標書批核委員會的成員應由不同人士出任。
  - 出處：《資助學校財務管理注意事項》第 2 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「開標及標書審核委員會和標書批核委員會的成員應由」

#### 4.7 單一報價／招標
_例外情況嘅前提同批准層級_

- **R-4.37** 須盡可能以公開競投方式採購，僅在具備充份理據且競投方法不能有效獲取所需物料及服務時，方可採用單一報價／招標程序。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「在採用競投的報價 /招標方法不能有效獲取所需 物料及服務的情 況下，才能採用單一報價 /招標程序」
- **R-4.38** 採用單一報價／招標須事先批准並將決定和理據妥為記錄：每次50,000元或以下由科主任或薪級點不低於總薪級表第25點教職員批准，50,000元以上由校董會／法團校董會批准。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 12 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=12)
  - 引文：「須事先得到下列相關人員的 批准，並將有關的決定和理據妥為紀錄」

#### 4.8 特殊安排
_辦學團體代購、分判限制、商業活動營辦商甄選_

- **R-4.39** 辦學團體獲授權為學校採購時必須依循與資助學校相同的採購程序，授權安排須事先獲校董會批准並存檔，採購紀錄須保存供學校審計。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 12 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=12)
  - 引文：「辦學團體如獲校董會 /法團校董會授權為學校進行採購活動 ，必須依循與資助學校 相同的採購程序」
- **R-4.40** 不宜准許承辦商分判服務；如認為恰當，須在文件訂明未獲校董會／法團校董會書面同意不得分判、轉讓或處置合約，承辦商仍須承擔全部責任。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 14 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=14)
  - 引文：「事先未獲校董會 /法團校董會書面同意，承辦商不得分判、轉讓或出讓或處置合約」
- **R-4.41** （覆核補遺）商業活動的營辦商／供應商須定期（宜至少每三年一次）以具競爭性的報價／招標程序甄選。
  - 出處：《資助學校財務管理注意事項》第 4 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=4)
  - 引文：「應定期(宜至少每三年一次)進行具競爭性的報價／招標程序，以甄選營辦商／供應商。」

### 5. 工程設備與採購
_工程及設備津貼計算、大型修葺申請_

- **R-5.1** 非經常工程及設備津貼金額按核准投標價或實際成本兩者較低者計算；大型修葺工程須透過周年預算程序申請。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 22 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=22)
  - 引文：「此類津貼的金額是根據核准投標價或實際成本 (兩者取其較低者 )計算的」
- **R-5.2** 收取堂費的資助小學，除常任秘書長另作決定外，工程及設備資助款項上限為核准金額的50%。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 22 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=22)
  - 引文：「收 取 堂 費 的 資 助 小 學 可 獲 發 不 超 過核准金額 50%的工程及設備資助款項」
- **R-5.3** 採購物料及服務、財務管理及監控等工作，須遵守《資助則例》以外的其他適用條例及實務守則，以及教育局不時發出的通告、指示及指引。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 7 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=7)
  - 引文：「適用於學校管理及行政、財務管理及監控、採購物料及服務等工作」

### 6. 廉潔與利益申報
_防賄條例、利益衝突申報、職務分隔避嫌_

- **R-6.1** 不得容許員工向供應商及承辦商收取任何利益（包括佣金），亦不得容許供應商以任何形式利益（包括捐贈）影響學校選擇。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 3 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=3)
  - 引文：「學校不得容許屬下員工向供應商和承辦商收取利益(包括佣金)」
- **R-6.2** 須以書面形式知會所有供應商及承辦商，向學校員工提供與職責有關的利益均屬違法，並可在訂單或報價／招標條款內加入此聲明。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 3 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=3)
  - 引文：「應以書面形式知會所有供應商和承辦商，如向學校員工提供任何與他們職責有關的利益均屬違法」
- **R-6.3** 須要求負責採購及物料供應職務的人員簽署承諾書，得知本人或家人與供應商有密切連繫時，盡早向校董會／法團校董會書面申報。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 4 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=4)
  - 引文：「學校應要求負責採購及物料供應職務的人員簽署承諾書」
- **R-6.4** 已申報利益衝突的員工須避免處理相關報價／投標或遵從校董會指示，申報及所採取行動須妥為記錄，每年並發通告要求員工簽署確認知悉。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 4 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=4)
  - 引文：「已申報利益衝突的員工須 避免處理相關的報價/ 投標」
- **R-6.5** 開標及標書審核委員會與標書批核委員會的成員須由不同人士出任，且不應包括負責作出推薦的有關科目教師／行政人員。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「開標及標書審核委員會 和標書批核委員會的成員，應由不同的人士出任」
- **R-6.6** 校董必須至少每隔12個月以書面向法團校董會申報利益一次，即使並無利益申報亦須如實匯報。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 9 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=9)
  - 引文：「校 董 必 須 至 少每 隔 12 個 月 以 書 面 向 法 團 校 董 會 申 報 利 益 一次」
- **R-6.7** 除非有非常強烈理據並事先獲校董會／法團校董會批准，學校不應接受營辦商／供應商的捐贈或利益。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 13 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=13)
  - 引文：「學校不應        以記錄。接受營辦商／供應商的捐贈或利益」
- **R-6.8** 確保校董和教職員遵守《防止賄賂條例》第9條，聽取廉政公署防貪意見並採取適當補救行動。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 18 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=18)
  - 引文：「遵守《防止賄賂條例》 (第201章)，特別是第 9條有關在學校事務或業務的事宜上索取及接受利益的規定」
- **R-6.9** 設立有效和足夠的制衡機制以避免校董涉及利益衝突，校董須按《教育條例》及教育局指引申報及披露個人利益。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=11)
  - 引文：「必 須 設 立 有 效 和 足 夠 的 制 衡 機制以避免校董成員涉及利益衝突」
- **R-6.10** （覆核補遺）員工須簽署承諾書，承諾不會未經批准披露報價或投標資料。
  - 出處：《資助學校財務管理注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=1)
  - 引文：「員工應簽署承諾書，承諾不會未經批准便披露報價或投標資料。」

### 7. 薪金津貼帳目
_薪酬按《匯編》支付、多付／少付薪金處理_

- **R-7.1** 向薪金津貼下核准人員編制內所有教學及非教學人員，按《匯編》訂明的薪級表和津貼支付薪酬。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 19 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=19)
  - 引文：「法團校董會須根據《 匯編》所列明的薪級表和津貼」
- **R-7.2** 如有多付或少付薪金，法團校董會須安排修正並追討多付薪金；無法追討時學校須承擔損失，教育局會在下次發放資助金時調整款額。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 27 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=27)
  - 引文：「學 校 應 向 有 關 的 教職員追討多付的薪金，如無 法追討，則學校須承擔有關的損失」
- **R-7.3** 以扣薪方式追討任何預付或多付的薪金時，必須遵守《僱傭條例》。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 28 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=28)
  - 引文：「以 扣 薪 方 式追 討 任 何 預 付 或 多 付 的 薪 金 時 ， 必須遵守《僱傭條例》」
- **R-7.4** 以法律訴訟向教職員追討多付薪金，必須在《時效條例》訂明的6年期內提出。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 29 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=29)
  - 引文：「必須在《時效條例》所訂明的 6年期內提出」

### 8. 銀行與現金管理
_銀行帳戶管理、存款分散、現金支票處理_

- **R-8.1** 不應把經費（包括政府撥款）用作高風險的投資活動，例如上市及非上市公司投資和衍生工具。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 8 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=8)
  - 引文：「不 應 把 經 費 ( 包 括 政 府 撥 款 ) 用 作 高風險的投資活動」
- **R-8.2** 法團校董會須以其名義開立和持有最少兩個銀行帳戶，分別處理政府經費及非政府經費。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=10)
  - 引文：「開 立 和 持 有 最 少 兩 個 銀 行 帳 戶」
- **R-8.3** 所有銀行帳戶須為聯名戶口，支票須由兩名獲授權的註冊校董聯署簽發。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=10)
  - 引文：「支 票 亦 須 由 兩 名 獲 授 權 的 註 冊 校 董 聯署 簽 發」
- **R-8.4** 學校經費只可存入以法團校董會名義開設的銀行帳戶。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=10)
  - 引文：「只 可 將 經 費 存 入 以法 團 校 董 會 名 義 開 設 的 銀 行 帳 戶」
- **R-8.5** 如經網上銀行管理帳戶，批准付款及授權更改使用者使用權和交易上限，須跟從支票付款安排，由兩名獲授權的註冊校董聯合批准。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 11 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=11)
  - 引文：「即由兩名獲授權的註冊校董聯合批准」
- **R-8.6** 所有付款均須有付款憑單及發票正本支持。
  - 出處：《資助學校財務管理注意事項》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「所有付款均須有付款憑單及發票正本」
- **R-8.7** 已繳付的憑單及發票必須蓋上「已繳付」或「PAID」字樣，並由清繳款項的職員加上日期，以防重複付款。
  - 出處：《資助學校財務管理注意事項》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「必須蓋上「已繳付」或「PAID」字樣」
- **R-8.8** 製備付款憑單和授權付款的工作應分開由不同人士負責，以達致內部監控。
  - 出處：《資助學校財務管理注意事項》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「製備付款憑單和授權付款的工作應分開由不同人士負責」
- **R-8.9** 正式收據應依照指定式樣印製、連續編號並順序發出，填上日期及蓋上學校印鑑。
  - 出處：《資助學校財務管理注意事項》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「正式收據應依照指定的式樣印製，而且須連續編號」
- **R-8.10** 收到的款項應盡速存入銀行。
  - 出處：《資助學校財務管理注意事項》第 2 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=2)
  - 引文：「收到的款項應盡速存入銀行」
- **R-8.11** 所有作廢支票須註明「註銷」並保存在支票簿內，以防再次使用。
  - 出處：《資助學校財務管理注意事項》第 3 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=3)
  - 引文：「應在所有作廢支票上註明「註銷」，並保存在支票簿內」
- **R-8.12** 校長應覆核學校文員每月製備的現金簿及銀行對帳表，查核後簡簽並註明查核日期。
  - 出處：《資助學校財務管理注意事項》第 3 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=3)
  - 引文：「校長應覆核學校文員每月製備的現金簿及銀行對帳表」
- **R-8.13** 所有正式收據均不應預先簽署。
  - 出處：《資助學校財務管理注意事項》第 4 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=4)
  - 引文：「所有正式收據均不應預先簽署」
- **R-8.14** 所有支票均不應預先簽署。
  - 出處：《資助學校財務管理注意事項》第 4 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=4)
  - 引文：「所有支票均不應預先簽署」
- **R-8.15** 學校各項收入（不論來自政府或其他來源）均應以最低風險的方式儲存。
  - 出處：《學校選擇銀行注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/The%20Choice%20of%20Bank%20Counterparties_EDB%20web_tc.pdf#page=1)
  - 引文：「均應以最低風險的方式儲存」
- **R-8.16** 毋須即時動用的剩餘款項應存入根據《銀行業條例》獲發牌的銀行，作定期或儲蓄存款。
  - 出處：《學校選擇銀行注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/The%20Choice%20of%20Bank%20Counterparties_EDB%20web_tc.pdf#page=1)
  - 引文：「存入根據《銀行業條例》獲發牌的銀行，作定期或儲蓄存款」
- **R-8.17** 款項應分散存入數間持牌銀行，以確保存款風險由兩至三間銀行分擔，在每間銀行的存款不應超逾該款項總額的50%。
  - 出處：《學校選擇銀行注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/The%20Choice%20of%20Bank%20Counterparties_EDB%20web_tc.pdf#page=1)
  - 引文：「學校在每間銀行的存款應不超逾該款項總額的50%」
- **R-8.18** 學校管理的款項如超逾港幣500萬元，在任何一間銀行的存款應不超逾該款項總額的20%。
  - 出處：《學校選擇銀行注意事項》第 1 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/The%20Choice%20of%20Bank%20Counterparties_EDB%20web_tc.pdf#page=1)
  - 引文：「如學校所管理的款項超逾港幣500萬元，則在任何一間銀行的存款應不超逾該款項總額的20%」
- **R-8.19** （覆核補遺）接受捐款須經校董會／法團校董會批准，並必須記錄所收到每項捐款的細節。
  - 出處：《資助學校財務管理注意事項》第 3 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=3)
  - 引文：「接受捐款須經校董會／法團校董會批准。」

### 9. 收費及代收費
_堂費、售賣物品利潤上限、商業活動收益用途_

- **R-9.1** 徵收超逾教育局常任秘書長書面核准上限的罰款及作特定用途的費用，須作教育用途並得到大部分家長明確同意，方可由法團校董會批准徵收。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 6 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=6)
  - 引文：「並得到大部分家長的明確同意，法團校董會便可批准徵收這些費用」
- **R-9.2** 售賣習作簿、校服、文具、用具及其他物品（課本除外）所得利潤不得超過成本價15%的上限，售賣課本不可獲利。
  - 出處：《資助學校財務管理注意事項》第 4 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=4)
  - 引文：「不得超過成本價15%的利潤上限」

### 10. 風險與保險
_政府承擔範圍、學校自購保險項目_

- **R-10.1** 知悉政府承擔火警、天災或惡意行為引致校舍損毀及公帑損失的風險，並按《學校行政手冊》辦理評估、償付程序及保安措施。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 23 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=23)
  - 引文：「政府會承擔 資助學校因火警、天災、其他種類的 危 險 或 任 何 人 的 惡 意 行 為」
- **R-10.2** 識別政府已投保的保險項目（公眾責任、僱員補償、團體人身意外、法團校董會責任）；範圍以外項目須由法團校董會自費購買。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 25 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=25)
  - 引文：「法團校董會可就 上述保險項目 範 圍 以 外的項目另行自費購買保險」

### 11. 核數監察與紀錄
_帳目查核、紀錄保存年期、配合審計_

- **R-11.1** 訂購物料及服務後須保留「按口頭報價購貨表格」及收到的報價資料三個曆年，以供查核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 6 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=6)
  - 引文：「保留「按口頭 報價購貨表格」 及收到的報價資料 （如有的話）三個曆年」
- **R-11.2** 須在「書面報價／投標摘要及批核紀錄表」記錄所有收到的書面報價單／標書資料，並抽樣查詢未交回報價單／標書的理由。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 10 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=10)
  - 引文：「「書面報價/ 投標摘要及批核紀錄表」(請參閱附件 IV)上記錄收到的所有書面報 價單」
- **R-11.3** 發出訂單後須保留所有收到的書面報價單／標書正本及全部投標文件（包括摘要及批核紀錄表）三個曆年，以供查核。
  - 出處：《資助學校採購程序指引（2025年10月更新）》第 11 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf#page=11)
  - 引文：「包括「書面報價 /投標摘要及批核紀 錄表」三個曆年，以供查核」
- **R-11.4** 須妥善備存帳簿及財務記錄，例如報價／招標文件、付款憑單、發票等。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 9 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=9)
  - 引文：「須 妥 善 備 存 帳 簿 及 財 務 記 錄」
- **R-11.5** 每年須擬備年度收支帳目及資產負債表，供外聘核數師審核。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 9 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=9)
  - 引文：「年 度 收 支 帳 目 及 資 產 負 債 表 須 擬 備 妥 當」
- **R-11.6** 須按《教育條例》第40BB(3)及(4)條規定，委任一名執業會計師審核學校的周年帳目。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 11 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=11)
  - 引文：「委任一名執業會計師審核學校的周年帳目」
- **R-11.7** 外聘核數師或教育局發出的管理建議信須向法團校董會匯報，如有跟進行動亦應納入周年校務計劃及／或周年財政預算中。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 12 頁 ⚠️頁碼近似 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=12)
  - 引文：「如有跟進行動，亦應納入周年校務計劃及／或周年財政預算中」
- **R-11.8** 遇有現金損失、欺詐、偽造文件等異常事件，法團校董會須立即報警，並從速（例如七天之內）以書面向有關的高級學校發展主任匯報。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 12 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=12)
  - 引文：「立即報 警 及 從 速 (例 如 七 天 之 內 ) 以 書 面 方 式」
- **R-11.9** 須於學年／財政年度結束後六個月內，向教育局提交外聘核數師報告、經審核的周年帳目及核數師管理建議信（如有）。
  - 出處：《設有法團校董會的資助學校財務管理指引》第 12 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/sbm/corner-imc-sch/fm%20guide%20chinese.pdf#page=12)
  - 引文：「須於學年／財政年度結束後六個月內向教育局提交下列文件」
- **R-11.10** 備妥學校的記錄和帳目（包括從學校轉撥款項的其他機構及特別基金的記錄），供審計署署長在有需要時查閱。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 17 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=17)
  - 引文：「查閱根據本《資助則例》條款獲發放津貼的學校的記錄和帳目」
- **R-11.11** 配合常任秘書長監察津貼及公帑運用，並於視察時供查核學校內部所有文件及記錄。
  - 出處：《資助則例（設有法團校董會資助學校適用版本）》第 14 頁 — [開啟原文](https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf#page=14)
  - 引文：「監 察 資 助 學 校 運 用 津 貼 及 公 帑 的 情況，確保津貼運用得宜及有效」
- **R-11.12** （覆核補遺）須製備「固定資產登記冊」記錄學校現有固定資產項目並不時更新，且應每年至少一次實地檢查各資產。
  - 出處：《資助學校財務管理注意事項》第 3 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=3)
  - 引文：「應製備「固定資產登記冊」，以記錄學校轄下的現有固定資產項目，並不時更新登記冊內的資料。(2) 應每年至少一次實地檢查各資產。」
- **R-11.13** （覆核補遺）註銷「固定資產登記冊」上的物品及貴重物品或調整有關記錄，設有法團校董會的學校須得到法團校董會批准；報銷報表須列出資產名稱、價值、數量及報銷原因，由法團校董會批核及顯示在帳目註釋中。
  - 出處：《資助學校財務管理注意事項》第 3 頁 — [開啟原文](https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/checklist/Points%20to%20Note%20on%20Financial%20Management%20of%20Aided%20Schools_c.pdf#page=3)
  - 引文：「至於設有法團校董會的資助學校，則須得到法團校董會的批准。報銷報表上需列出該項資產名稱、價值、數量及報銷原因等，並且由法團校董會批核及顯示在帳目註釋中。」

## C. 覆蓋度與 QC 紀錄

- 條目總數：**122**（g01 採購 41 ＋ g02 財務管理組 45 ＋ 資助則例 23 ＋ 覆核補遺 13，機械重驗後保留 122）
- 機械重驗（v0.2 重跑）：exact／去空格通過 108、NFKC 相容字通過 14、頁碼修正 0、approx 旗修正 0、剔除 0
- 對抗覆核（獨立 agent）：g01 41/41 頁碼正確；g02 組 45/45 頁碼正確；引文唯一 flag 係 PDF 相容表意字（NFKC 等價，非內容錯誤）
- URL 檢查：5/5 HTTP 200 application/pdf（2026-06-11）
- 已知限制：本清單係指引義務嘅蒸餾，唔係法律意見；條目以發佈時嘅指引版本為準，源文件改版須重新派生（freshness 週跑已監察呢 5 源）

