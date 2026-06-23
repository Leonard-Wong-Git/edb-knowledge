# EDB 申請表格細字入庫批次 — Forms Footnote Coverage

> 工作檔(跨 session)。由來:S177(2026-06-22)凍結教席事件揭發 EDB「申請表格/forms」類文件**整批未入庫** —— 好多 load-bearing 數字(費用上限/資助級別/比例/計算公式/批核條件)淨係寫喺津貼申請表細字,正文/指引唔講。TRG 凍結教席 10% 已入(見 `ingest_trg_footnote.py`),呢個係系統性補 `fin-management/subsidy-info` 區。
> Leonard 授權:「/workflows 全部做」(全部 28+ 條入庫),留意 token。

## 安全界線(同 S174 FOOTNOTE_INGEST_LOOP)
- **live Supabase 寫入 = gated**:attended + INSPECT before/after + Leonard 已授權「全入」。唔做 unattended production write。
- 機制 = `content_type=footnote_curated`、`id=footnote_fn_*`、route-independent overlay(`searchFootnotes` exact cosine,新 footnote 自動可檢索、零 backend code 改)。
- embed 格式(已核 cos=1.0000):`text + " " + " ".join(keywords)`。
- chunk 數變 → display-sync 8 點(app.html/index.html/3 JSON/K1_API_SPEC/README + CHANGELOG)。
- 入 footnote 後**必 restart Render**(in-memory `_footnoteCache`,`invalidateFootnoteCache`)。
- 凍結合約零接觸(`_meta` 2.3.0 / facts 455 / guidelines 158)。
- ingest script 範本:`dev/ingest_trg_footnote.py`(--self-test / --execute,INSPECT)。

## 進度狀態(2026-06-22 S177)
- ✅ Discovery done(general-purpose agent,fan-out fetch 14 PDF/.doc)→ 28 候選 + 額外 5 費率 footnote。
- ✅ Spot-check done(agent 可靠):採購門檻 #26 同 live 庫一致;EOEBG 餐飲 `$200/$450/$600` + 盈餘 `twelve (12) months` 原文逐字核到(pymupdf)。
- ⏳ **逐條 verbatim 核實 = PENDING**(workflow `forms-footnote-verify` 7 agent 撞 session limit 全 fail;script 已存,reset 後重跑:`Workflow({scriptPath:".../forms-footnote-verify-wf_229daf72-9bc.js"})`)。
- ⏳ Stage(砌繁中 footnote text+keywords)= PENDING。
- ⏳ cosine 自測 + INSERT + display-sync + restart + live verify = PENDING。

## Source PDF(base = `https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/subsidy-info`)
- CEG: `/ref-capacity-enhancement-grant/Calculation of CEG_en.pdf` + `Ground Rules and Procedures_en.pdf`
- EOEBG/OEBG/CFEG/AC/Tables: `/ref-e-oebg-cfeg/` → `User Guide_EOEBG_e.pdf`、`User Guide_OEBG_e.pdf`、`User Guide_CFEG_e.pdf`、`CFEG_2026_e.pdf`、`E_Table I_2026_e.pdf`、`E_Sec_Table II_2026_e.pdf`、`E_Pri_Table III_2026_e.pdf`、`AC Grant in Aided Schools_e.pdf`
- Tips: `/Tips on handling govt subventions for aided schools_e.pdf`
- TRG companion: `/trg/` Annex III(中英 .doc)

## 候選清單(待逐條 verbatim 核實;✅=已 spot-check 核)

### 第一類:穩定規則/比例/公式/條件(~20,優先,long-lived)
| # | 計劃 | substance + figure | source | conf | 核 |
|---|---|---|---|---|---|
| 2 | TRG | 凍結空缺(60 曆日↑)MPF 僱主供款 = 月薪 5% 或 $1,500 較少者 | Annex III 註腳 | 高 | ⏳ |
| 3 | TRG | 不可凍結職位:校長/NET/學生輔導/小學課程統籌/SENCO/SEN 支援 | Annex III 中文版第 7 點 | 高 | ⏳ |
| 5 | CEG | 雙課制小學總班數 ≥25 → 每節當獨立學校計 CEG | Calculation of CEG #1 | 高 | ⏳ |
| 6 | CEG | 中小兼收一律用小學費率,合資格班數=小學+中學 | Calculation of CEG #2 | 高 | ⏳ |
| 7 | CEG | plan 未經 IMC/SMC 核准 + 10 月底前上載 → claw back | Ground Rules #2 | 中 | ⏳ |
| 8 | CEG | 唔准用 CEG 出補課/補習班額外薪津 | Ground Rules / OEBG 3.8(d) | 高 | ⏳ |
| 9 | EOEBG | 盈餘保留上限 = 12 個月撥款額 | EOEBG guide #6/#20 | 高 | ✅ |
| 10 | EOEBG | 盈餘 top-up 封頂:政府資助項目 50%/私人捐贈籌款 25% | EOEBG guide #9(c) | 高 | ⏳ |
| 11 | EOEBG | 應酬餐飲上限:早餐/其他 $200、午 $450、晚 $600(連加一) | EOEBG guide #11 註 4 | 高 | ✅ |
| 12 | EOEBG | 盈餘可付 4 類特定無薪假嘅法定假/年假 | EOEBG guide #6 | 高 | ⏳ |
| 15 | CFEG | 盈餘累積上限 = 該年撥款 5 倍(≠EOEBG 12 月,易混) | CFEG guide I(d) | 高 | ⏳ |
| 16 | CFEG | 新校首 3 年用 Set-up Fund,EDB 批准結束戶口後先發 CFEG | CFEG guide I(c) | 高 | ⏳ |
| 18 | CFEG | 家具設備項目本身冇金額上限 | CFEG guide I(b) | 中 | ⏳ |
| 19 | OEBG | 盈餘上限 = 12 個月,claw back 可自選 grant(建議先 Special 後 General) | OEBG guide 2.7/2.8/4.8 | 高 | ⏳ |
| 20 | OEBG | Special Domain 各 grant 唔准互調/調出,但可由 General Domain top-up | OEBG guide 2.2 | 高 | ⏳ |
| 22 | AC | 特別室封頂:小學 5/中學 12(特殊 8-12 按類型) | AC Grant #7 + Table | 高 | ⏳ |
| 23 | AC | AC 率等值公式:SAC=1 課室率/標準禮堂=2.5 特別室率/小組室=0.5 課室率/無禮堂有蓋操場=2 特別室率 | AC Grant #11 註 | 高 | ⏳ |
| 24 | AC | SAC 補貼每校封頂 2 個 | AC Grant #8 | 高 | ⏳ |
| 26 | Tips | 採購門檻階梯:≤$5k 免競投/>$5k-$50k 2 口頭/>$50k-$200k 5 書面/>$200k 招標 5 供應商 | Tips #3 + EDBC 4/2013 | 高 | ✅(live 對照) |
| 27 | Tips | 出租校舍淨收入須撥 40% 入政府資助戶口 | Tips #3(b)(EDBC 5/2011) | 高 | ⏳ |
| 28 | Tips | 12 個月內重複採購:口頭累計 ≤$50k/書面累計 ≤$200k,不得拆單 | Tips #4(g) | 高 | ⏳ |

### 第二類:費率金額(2026/27,逐年變,入庫要標年度 + 維護)
| # | 計劃 | substance + figure | source | 核 |
|---|---|---|---|---|
| 4 | CEG | 班數階梯定額:小學 1-5 班 $193,164…24↑ $670,238;中學 1-12 班 $305,888…$548,327;特殊 $214,627…$744,723 | Calculation of CEG | ⏳ |
| 14 | EOEBG | A/B 值:小學 A$393,980 B$30,274;中學 A$550,193 B(S1-3)$48,702/(S4-6)$51,332;智障特殊 A$594,246 B$38,025 | E_Table I_2026 | ⏳ |
| 17 | CFEG | 單位率:小學全日 $8,418/雙課制每節 $5,893/中學 $17,423;特殊視障 $24,847… | CFEG_2026 Table V | ⏳ |
| 25 | AC | 金額(中學):課室/SAC $8,384/特別室 $21,263/小組 $4,192/標準禮堂 $53,158 | E_Sec_Table II_2026 | ⏳ |
| — | Boarding | 每寄宿生每月津貼扣減宿費 $440(2026/27) | Table II 註 | ⏳ |
| — | DLG | Other Programmes 使用率 ≥80% 額外 $800/SS 班,**2026/27 起取消** | Table II 註 | ⏳ |
| — | LWL+Sister | 每校總額上限但每校不少於 $300,000 | Table II/III | ⏳ |
| — | Composite IT | 仲用 MMLC 嘅合資格學校每校每年額外 $59,570 | Table I/II 註 | ⏳ |
| 13 | EOEBG | 新校撥款公式 EOEBG = A + B×N + School Specific Grants | EOEBG guide #13 | ⏳ |

## Next step(session reset 2:10am London 後)
1. 重跑核實 workflow(`scriptPath` 上面)或自己 download PDF + pymupdf 逐條核 verbatim。
2. verified → 砌繁中 footnote(text+keywords,範本見 `ingest_trg_footnote.py` FN dict)→ 一個 batch staging JSON。
3. cosine 自測(每條對 query 變體 ≥0.45 lead)。
4. **attended** INSPECT + INSERT(可逆 footnote_curated)→ display-sync 8 點 → restart Render → live verify。
5. 建議:第一類(穩定規則)優先入;第二類費率標「2026/27」+ 列入 freshness 監察(逐年更新)。
