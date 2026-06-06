# Channel B 入庫缺口 — 真檔 link 對賬表 (2026-06-06)

> **背景:** Supabase 向量庫實有 **173** distinct 來源 / 10,594 chunks;registry 登記 **203**。
> 計埋 alias(`g24→sag_2025_11`)後,**51 個 registry 來源未入向量庫**。本檔係呢 51 個嘅完整對賬冊。
> **純讀取產物。入庫係另外 HIGH-risk 步驟(動向量庫 = Channel B 搜尋 + 下游同步嘅根),待逐批 GO 先做。**
> **決定欄填:** `✅入` / `❌skip` / `🔍要再揾` / 或寫低揀邊幾條 link。

## ⚠️ 睇之前要知三件事
1. **候選 link 要逐個 vet,唔好照單全收。** 有啲 landing 頁第一條 link 係跨 KLA 導覽噪音;一個 KLA 大頁可能列幾十個 PDF,要揀返正確嗰本主指引。
2. **registry 有 url 擺錯。** 例:`sci_kla_guide_2017`(科學 KLA)個 `url_primary` 居然指住 PSHE 個人社會頁——入之前連 registry 都要順手修。
3. **入庫 = §3 HIGH-risk。** 到時另出 PLAN 等你 GO,分批 extract→chunk→embed→upsert,逐批驗 count。

## 全 51 缺口分佈
| 類別 | 數 | 點做 |
|---|---|---|
| 🟢 爬到真檔 PDF link | 30 | 下面詳列候選,逐個 vet 揀正確主檔 |
| 🟡 landing 冇直接 PDF | 13 | 要深一層 / AJAX,見下 |
| ✅ 已有 PDF 直連(免爬) | 2 | `mce_framework_2008`、`phys_sss_2007_2015`(registry `url_primary` 已係 .pdf;phys 係 2015 舊版,要諗值唔值) |
| ❌ 建議跳過 | 6 | 見下表 |

### ✅ 已有直連、可即入(2)
- `mce_framework_2008` 德育公民教育架構2008 — `https://www.edb.gov.hk/attachment/tc/common/revised mce framework.pdf`
- `phys_sss_2007_2015` 高中物理指引2015 — registry url_primary 已係 PDF 直連 ⚠️ 2015 舊版

### ❌ 建議跳過(6)
| id | 原因 |
|---|---|
| `pe_sss_2007_2015` | 之前**刻意 deprecated**(舊高中體育) |
| `sci_jss_supp_2017` | 之前**刻意 deprecated**(初中科學補充) |
| `g30` | superseded,保留作歷史(現由 `ph_pri_curr` 接手) |
| `religious_edu_jss` | candidate,Google redirect URL 已死,要先揾直連 PDF |
| `stat_enrolment_report` | **其實已覆蓋**:13 份年度檔已在庫(`stat_enrolment_2012–2024`) |
| `pri_science_cert_application_form` | DOCX 申請表,非政策知識內容 |

### 🟡 13 個 landing「冇直接 PDF」點解(實測 3 個,其餘按同類推斷)
- **PDF 喺下一層 sub-page**(KLA 大頁 270KB+,內文檔喺所連子頁)→ 要 depth-2 深爬。**確認:** `g36`、`steam_edu`。同類大頁:`g09 g14 g17 g31 g33 g35 g37 g39 gs_pri_curr curr_renewal_guides`。
- **JS / AJAX 動態載入**(靜態 curl 攞唔到,要瀏覽器渲染)→ **確認:** `gifted_policy_docs`(得 4.8KB + `.load(`/`ajax`)。

---

## ✅ 已收 Leonard 決定 — 批次 1 (2026-06-06) — 共 15 個(全部係 🟡13 + ⚫2 嗰批)

**入庫 (11):**
| # | id | 來源 | 入庫指示 |
|---|---|---|---|
| 2 | `g09` | 非華語中文指引 | `CLEKLAG_2017_for_upload_final_R77.pdf` **只入 p.43–48** |
| 3 | `g14` | 資優培育指引 | index 頁**各 link 嘅 HTML 內容**輸入成資料(非單一 PDF) |
| 4 | `g17` | 訓輔理念與指引 | 同上(index 各 link 嘅 HTML → 資料) |
| 5 | `g31` | 英文課程指引(小學) | `Pri_ELCG_Primary_1-6_2025.pdf` (+ en landing) |
| 6 | `g33` | 英文課程指引(中學) | 同上(en eng-edu landing 揾中學 ELCG PDF) |
| 7 | `g35` | 個社人文課程指引 | `PSHE_KLACG_P1-S6_Chi_2017.pdf` |
| 8 | `g36` | 科學課程指引 | `SEKLACG_CHI_2017.pdf` |
| 9 | `g37` | 藝術教育課程指引 | `AE_KLACG__Chi___2017.pdf` |
| 10 | `g39` | 科技教育課程指引 | `TE_KLACG_Chi_5_Dec_2017_r2.pdf` + `CT_Supplement_Chi_2020.pdf` |
| 11 | `gifted_policy_docs` | 資優教育政策文件 | `…/gifted/resources_and_support/cd/index.html` |
| 12 | `gs_pri_curr` | 常識科課程文件 | `GSCG_2017_Chi.pdf` |

**取消 (4):** `curr_renewal_guides`(#1 課程更新總覽) · `pri_science_cert_application_form`(#13 申請表) · `stat_enrolment_report`(#14 已覆蓋) · `steam_edu`(#15)

> 待 Leonard 決定:🟢 30 個有候選 link 嗰批 + ✅ 2 個直連(`mce_framework_2008`/`phys_sss_2007_2015`)+ ❌ 4 個 deprecated/superseded(`pe_sss_2007_2015`/`sci_jss_supp_2017`/`g30`/`religious_edu_jss`)。

---

## ✅ 批次1 執行結果（2026-06-06 S146）
- **真新增入庫 7 源 +1,002 chunks**：g33(421) · g35(187) · g36(179) · g37(116) · g09(10, p43-48) · g14(77) · g17(12)。Supabase **10,594 → 11,596**（live 雙驗）。
- **刪走 4 源**：
  - `g31`/`g39`/`gs_pri_curr` = 內容已由 sibling 覆蓋（`eng_pri_guide_2025`/`tech_kla_guide_2017`/`gs_pri_guide_2017`），刪走我新入嘅、保留既有。
  - `gifted_policy_docs` = provenance 錯（agent 抓咗 SECG booklet + 不明 circular），已刪;**待 Leonard 畀正確資優政策 link 再單獨抽**（cd/index.html 只 link PECG=g06 + SECG，無新內容;資優已由 g06+g14 覆蓋）。
- `g17` 正確但淺（12 chunks，只 index 概覽），可日後深化（3 指引子區）。
- 工具：`dev/fetch_extract.py`（抽取）+ `dev/ingest_one_source.py`（per-source 安全入庫）。
- **餘下待你決定**：下面 🟢30 候選 link + ✅2 直連（mce_framework_2008/phys_sss_2007_2015）+ ❌6 deprecated/superseded。

---

**以下 = 🟢 30 個爬到 link + 🟡 13 個冇 link 嘅逐源詳列(決定欄留空俾你填):**

## [apl_curr_docs] 應用學習課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/cross-kla-studies/applied-learning/curriculum-documents/index.html
- 爬到候選 link (2 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/applied-learning/ref-and-resources/ApL%20C&amp;A%20Guide%20C%202017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/applied-learning/curriculum-documents/cos_sen_report_print_060920_c.pdf
- 你的決定: ____

## [arts_curr_docs] 藝術課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/arts-edu/curriculum-docs/index.html
- 爬到候選 link (7 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/AE_KLACG__Chi___2017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/mus_cg_c_2024.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/mus_c_and_a_c_2024.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/mus-c-and-a-guide-2015-c.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/mus_supplement_c_2024.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/va_cg_c_2024.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/VA_CA_Guide_c-100418.pdf
- 你的決定: ____

## [chi_edu_curr_docs] 中文教育課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/chi-edu/curriculum-documents.html
- 爬到候選 link (19 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/CLEKLAG_2017_for_upload_final_R77.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Primary_Chi_Lang_Curr_Guide_2023.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Pri_Chin_Lang_LO_2023.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_eng.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_appx.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_appx_eng.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_chi.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_eng.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_urdu.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_nepali.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_tagalog.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_hindi.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_thai.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Suppl_guide_summary_vietnamese.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Junior_Sec_Chi_Lang_Curr_Guide_2023.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/CHI_LANG_CAGuide_2021.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/SEC_LO_2021.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Chi_Lit_C&amp;A_Guide_2025.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/PTH_Curriculum_guide_for_upload_final.pdf
- 你的決定: ____

## [cs_curr] 電腦科課程  —  OK
- 現 url: https://cs.edb.edcity.hk/tc/index_cs.php
- 爬到候選 link (2 條):
    1. https://cs.edb.edcity.hk/file/C_and_A_guide/202106/CS_CAG_S4-6_Chi_2021.pdf
    2. https://cs.edb.edcity.hk/file/C_and_A_guide/202106/CS_CAG_S4-6_Eng_2021.pdf
- 你的決定: ____

## [g07] 基礎教育課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/guide-basic-edu-curriculum/index.html
- 爬到候選 link (2 條):
    1. http://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/guide-basic-edu-curriculum/becg_2014_Full.pdf
    2. http://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/guide-basic-edu-curriculum/BECG-P1-P6-_Summary.pdf
- 你的決定: ____

## [g08] 中文課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/chi-edu/curriculum-documents-exemplars.html
- 爬到候選 link (14 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_01.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_02.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_03.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_04.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_05.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_06.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_07.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_08.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_09.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_10.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_11.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents-exemplars/Exemplar_14.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_12.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Exemplar_13.pdf
- 你的決定: ____

## [g12] 數學課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/ma/curr/basic-education-2002.html
- 爬到候選 link (26 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-Preamble.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-Key.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-Content.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch1.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch2.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch3.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch4.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch5.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ch6.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex1.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex2.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex3.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex4.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex5.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex6.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex7.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex8.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex9.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex10.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex11.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex12.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Ex13.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-App1.pdf
    24. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-App2.pdf
    25. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Bibliography.pdf
    26. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/BECG-Membership.pdf
- 你的決定: ____

## [g13] 中學教育課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/major-level-of-edu/secondary/cg_documents.html
- 爬到候選 link (18 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_Introduction_ch.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_1_ch.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_2_ch.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_3_ch.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_4_ch.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_5_ch.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6_ch.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6A_ch.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6B_ch.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6C_ch.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6D_ch.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_7_ch.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_8_ch.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_9_ch.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_10_ch.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_11_ch.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/Supp_notes_SECG_Chi.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SSCG_2009_all_ch.pdf
- 你的決定: ____

## [g16] 訓育工作指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/index.html
- 爬到候選 link (8 條):
    1. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/preface.pdf
    2. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch1.pdf
    3. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch2.pdf
    4. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch3.pdf
    5. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch4.pdf
    6. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch5.pdf
    7. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/ch6.pdf
    8. https://www.edb.gov.hk/attachment/tc/teacher/student-guidance-discipline-services/principles-guidelines/guidelines-on-student-discipline/capp.pdf
- 你的決定: ____

## [g18] 校車安全指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/student-parents/safety/sch-bus-services/index.html
- 爬到候選 link (12 條):
    1. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/school bus services committee_c.pdf
    2. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/Appointment of School Bus Service Operators_TC (2025-26)(r).pdf
    3. https://www.edb.gov.hk/attachment/sc/student-parents/safety/sch-bus-services/school_bus_leaflet.pdf
    4. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/Letter to NFB operators_Provision of student service (2025-26)_updated_TC(r).pdf
    5. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/Letter to SPLB operators_Provision of student service (2025-26)_updated_TC_rev(r).pdf
    6. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/Letter to School Principals (2025-26)_TC(r).pdf
    7. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Schools_TC(r).pdf
    8. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Operators_TC(r).pdf
    9. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Drivers_TC(r).pdf
    10. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Escorts_TC(r).pdf
    11. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Parents_TC(r).pdf
    12. https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2025_Guidelines_Students_TC(r).pdf
- 你的決定: ____

## [g21] 視藝安全指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/arts-edu/resources/va-curri/safety/index.html
- 爬到候選 link (2 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/resources/va-curri/VAsafety_pri_c.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/resources/va-curri/VAsafety_sec_c.pdf
- 你的決定: ____

## [g22] 科技安全指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/technology-edu/resources/safety.html
- 爬到候選 link (1 條):
    1. https://www.edb.gov.hk/attachment/en/curriculum-development/kla/technology-edu/resources/technology-and-living/Safety_Booklet(Chi)_final_2010_r1.pdf
- 你的決定: ____

## [g23] 體育安全指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pe/references_resource/safety-guidelines/index.html
- 爬到候選 link (3 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/references_resource/safety-guidelines/Safe_c.pdf
    2. https://applications.edb.gov.hk/circular/upload/EDBC/EDBC23013C.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/references_resource/safety-guidelines/FAQ_SafetyGuide_2024_tc.pdf
- 你的決定: ____

## [g27] 小學數學課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/ma/curr/pri-math-2000.html
- 爬到候選 link (14 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/content_4943.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/committee_4943.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/preamble_4943.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 1_4943.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 2_4943.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 3_4943.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_1.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_2.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_3.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_4.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_5.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 4_6.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 5.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/chapter 6.pdf
- 你的決定: ____

## [g28] IT保安建議措施  —  OK
- 現 url: https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/information-security.html
- 爬到候選 link (41 條):
    1. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/CM/2022/EDBCM22084C.pdf
    2. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/20210707_Seminar/CyberSecurityintheSchool.pdf
    3. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/20210707_Seminar/HKT.pdf
    4. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/20210707_Seminar/FakeChannel.pdf
    5. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/CyberSecurityInSchoolsSmartTips.pdf
    6. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/20200819_Seminar/is-20200819-seminar-HKACE-tc.pdf
    7. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/ZoomDataSecurityIncidents/ZOOM-Desktop-suggestion.pdf
    8. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/ZoomDataSecurityIncidents/ZOOM-Mobile-suggestion.pdf
    9. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/information-Security/20200508-Seminar/is-20200508-BuildASecureCyberspace-Webinar-C.pdf
    10. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-HKT-20200113.pdf
    11. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-Elearning-20200113.pdf
    12. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-PCPD-20200113.pdf
    13. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-CISCO-20200113.pdf
    14. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-HKIRC-20200113.pdf
    15. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-HKCERT-20200113.pdf
    16. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20200113-Seminar/PPT-HP-20200113.pdf
    17. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20191209-Seminar/PPT-EDB-20191209.pdf
    18. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20191209-Seminar/PPT-HKCERT-20191209.pdf
    19. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20191209-Seminar/PPT-HKACE-20191209.pdf
    20. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20191209-Seminar/PPT-AiTLE-20191209019.pdf
    21. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20191209-Seminar/PPT-HKEdCity-20191209.pdf
    22. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190925-Seminar/HKCERT-PPT-E.pdf
    23. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190925-Seminar/HKACE-PPT-E.pdf
    24. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190925-Seminar/AiTLE-PPT-E.pdf
    25. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190925-Seminar/HKEdCity-PPT-E.pdf
    26. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190925-Seminar/EDB-PPT-E.pdf
    27. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/CM/EDBCM19071C-BuildaSecureCyberspace2019.pdf
    28. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/information-Security/20190503-Seminar/is-20190503-seminar-BuildaSecureCyberspace-tc.pdf
    29. https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/20190115-Seminar/is-20190115-seminar-aitle-tc.pdf
    30. https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Securtiy/20190115-Seminar/is-20190115-seminar-hkace-en.pdf
    … 另有 11 條 (見原頁)
- 你的決定: ____

## [g32] 人文學科指引(初中)  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/curriculum-documents.html
- 爬到候選 link (23 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/PSHE_KLACG_P1-S6_Chi_2017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHist_Curr_Guide_S1-3_Chi_final.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Adapted_Framework_r.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Chinese_History_Framework_Bilingual_r.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHistCAGuide_updated_c_20180108_clean.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CESCG_c_20240730 clean.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_C&amp;A_Guide_C_with_updates_in_2025.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_supplementary_doc_Chi_with_updates_in_2025.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_C&amp;A_Guide_updated_c_(2015.11.24).pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_supplementary_doc_Chi_20151130_clean.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/curriculum-documents/ERS/ERS_CA Guide_updated_c.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/ERS_CA Guide_updated_c_(2019.12.03)_clean mode for upload.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/RE_Curriculum_Guide_Chi_for_upload.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CSS13REC.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/supplementary_notes-final-chi.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geography C&amp;A Guide 2022-chi.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geography_Consultation_Brief_Feb_2017-chi.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geog_Revision_2016_Questionnaire_chi-b.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geog_Curr_Guide_S1-3_Chi_web_final_21062011.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_Curr_Guide_S1-3_Chi_final_10072019.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_C&amp;A_Guide_c_20180109.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/6.THS_C&amp;A_Chi_Guide_c(2015.11.24)PSHE section.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/l&amp;s_curriculum_guide_chi.pdf
- 你的決定: ____

## [g34] 普通話課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/chi-edu/curriculum-past-documents.html
- 爬到候選 link (29 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/CLE_KLACG_2002.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/pri_chi_lang_lo_web_version.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/PLg_Guide.pdf
    4. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/plglo.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Pri_Chi_syllabus(1990).pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Chi%20Lang%20CA%20Guide_2015.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Checklist%20of%20CAGuide%20updates_2015_Chi%20Lang.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Supp_notes_Chi_Lang_CAGuide_2020.pdf
    9. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Chi%20Lang%20C&amp;A%20Guide_c_clean_c&amp;s_19112014_final.doc
    10. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Checklist%20of%20updates_Chi%20Lang.doc
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Supp%20notes_CHI%20LANG_CLE.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/sec_chi_suggest_learn_2007_070628.pdf
    13. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/chi_lang_final.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/chi_lang_guideline_20070401_Dec09.doc
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/Sec_chi_lang_sg_2001.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/D03_chi_v3.pdf
    17. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/ChiSyl_1990.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Chi%20Lit%20CA%20Guide_2015.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Checklist%20of%20CAGuide%20updates_2015_Chi%20Lit.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/Supp%20notes_CHI%20CLIT_CLE.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/Chi_Lit_C_and_A_Guide_updated_c_20141119.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/Checklist of updates_Chi Lit.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/D03_chi_lit_v3.pdf
    24. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/nss_chi_lit_ca_guide070327.pdf
    25. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/chi_lit_guideline_20070401.pdf
    26. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-past-documents/sfcurr-guide.pdf
    27. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Chinese_Literature_Syllabus_1992.pdf
    28. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/curriculum-documents/Chinese_Literature_Syllabus_S45_1986.pdf
    29. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/pth-pamphlet1998.pdf
- 你的決定: ____

## [g38] 音樂課程指引  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/arts-edu/curriculum-docs/curriculum-docs_past/index.html
- 爬到候選 link (3 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/curriculum-docs_past/con_chi.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/curriculum-docs_past/music_complete_guide_chi.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/arts-edu/curriculum-docs/curriculum-docs_past/va_guide_p1_s3_c.pdf
- 你的決定: ____

## [ma_curr_index] 數學課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/ma/curr/index2.html
- 爬到候選 link (15 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/ME_KLACG_chi_2017_12_08.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/pmc2017_tc.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_KS1_tc.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_KS2_tc.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/jsmc2017_tc.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_KS3_tc.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/Guidelines on Catering for LD in SS Math (C).pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/ssmc2017_tc.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/CA_2017_tc.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/CA_timeline_tc.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_CP_tc_1.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_M1_tc.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/EN_M2_tc.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/curr/Math_CAGuide_c_2015.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/timeline_tc.pdf
- 你的決定: ____

## [moral_civic_curr] 德育公民教育文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/4-key-tasks/moral-civic/curriculum-documents.html
- 爬到候選 link (2 條):
    1. https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM23183C.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/secondary/curriculum-guides-documents/SECG_booklet_6A_ch.pdf
- 你的決定: ____

## [nat_sec_edu] 國家安全教育  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/national-security-education/index.html
- 爬到候選 link (14 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_framework.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_pshechist.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_psheces.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_pshegeog.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_pshehist.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_pshere.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_psheecon.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_psheers.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_psheths.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/nse/nse2025_subject_framework_psheph.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/national-security-education/National_Security_Education_Knowledge_Enrichment_Seminar_Series/National_security_and_our_daily_lives.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/national-security-education/National_Security_Education_Knowledge_Enrichment_Seminar_Series/The_Importance_of_the_Rule_of_Law.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/national-security-education/National_Security_Education_Knowledge_Enrichment_Seminar_Series/Elucidation_of_the_Political_Structure.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/national-security-education/National_Security_Education_Knowledge_Enrichment_Seminar_Series/Knowing_more_about_the_Law_Continental_Law_Common_Law_and_National_Security_Law.pdf
- 你的決定: ____

## [pe_curr_docs] 體育課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pe/curriculum-doc/index.html
- 爬到候選 link (4 條):
    1. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/curriculum-doc/PE%20C&amp;A%20Guide_c.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/curriculum-doc/PEKLACG_c.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/curriculum-doc/scope_of_learning_pri/E_LT_SS.pdf
    4. http://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pe/curriculum-doc/PE C&amp;A Guide_2015_c.pdf
- 你的決定: ____

## [pecg_2024_landing] 小學指引索引頁  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide.html
- 爬到候選 link (27 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/EDBCM22154C.pdf
    2. https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM23110C.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/Letter_to_Pri_Sch_20250626.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/Letter_to_Pri_sch_20241010.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/2223_Letter to Pri sch_PECG_5 Jan 2023.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/20230912 Letter to Pri sch_PECG.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_full.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch1.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch2.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch3.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch4.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch5.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch6.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch7.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch8.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG2024_ch9.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_ch10.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG 2024_abridged version.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/little_seedling_comics_series_long_holidays_1.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/little_seedling_comics_series_long_holidays_2.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECGA&amp;A_FAQ_TC.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/materials/A&amp;A_leaflet_20250602.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/Poster 1.pdf
    24. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/Poster 2.pdf
    25. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/Poster 3.pdf
    26. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/Poster 4.pdf
    27. https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/Poster 5.pdf
- 你的決定: ____

## [ph_pri_curr] 小學人文科  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/cross-kla-studies/ph-primary/index.html
- 爬到候選 link (9 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBC_122025_C.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBCM_197_2024_C.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBC_092024_C.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBC202023_C.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/Primary_Humanities_Curriculum_Guide.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBCM_197_2024_C_Annex_2.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/EDBCM_197_2024_C_Annex_3.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/PH%20poster.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/cross-kla-studies/ph-primary/PH_leaflet.pdf
- 你的決定: ____

## [pri_science] 小學科學科  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/science-edu/primary-science.html
- 爬到候選 link (14 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/EDBC23018C.pdf
    2. https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM24057C.pdf
    3. https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM24058C.pdf
    4. https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM24098C.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/EDBCM24243C.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/EDBC25013C.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/PSCG(2025).pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/Designated_Courses_List(30hrs).pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/application_form_Pri_Sci_Cert_c.docx
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/PS_Safety_Handbook_Chi_2024.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/List_of_Suggested_Teaching_Aids_and_Equipment_for_Primary_Science.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/Primary_Science_ePoster.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/Primary_Science_eLeaflet.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/EDB_Pri_Sci_Survey_Chi.pdf
- 你的決定: ____

## [pshe_curr_docs] 個人社會人文課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/curriculum-documents.html
- 爬到候選 link (23 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/PSHE_KLACG_P1-S6_Chi_2017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHist_Curr_Guide_S1-3_Chi_final.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Adapted_Framework_r.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Chinese_History_Framework_Bilingual_r.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHistCAGuide_updated_c_20180108_clean.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CESCG_c_20240730 clean.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_C&amp;A_Guide_C_with_updates_in_2025.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_supplementary_doc_Chi_with_updates_in_2025.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_C&amp;A_Guide_updated_c_(2015.11.24).pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_supplementary_doc_Chi_20151130_clean.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/curriculum-documents/ERS/ERS_CA Guide_updated_c.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/ERS_CA Guide_updated_c_(2019.12.03)_clean mode for upload.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/RE_Curriculum_Guide_Chi_for_upload.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CSS13REC.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/supplementary_notes-final-chi.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geography C&amp;A Guide 2022-chi.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geography_Consultation_Brief_Feb_2017-chi.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geog_Revision_2016_Questionnaire_chi-b.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geog_Curr_Guide_S1-3_Chi_web_final_21062011.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_Curr_Guide_S1-3_Chi_final_10072019.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_C&amp;A_Guide_c_20180109.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/6.THS_C&amp;A_Chi_Guide_c(2015.11.24)PSHE section.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/l&amp;s_curriculum_guide_chi.pdf
- 你的決定: ____

## [sci_curr_docs] 科學課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/science-edu/curriculum-documents.html
- 爬到候選 link (7 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/SEKLACG_CHI_2017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/pri-sci/PSCG(2025).pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/Science(S1-3)_supp_c_2017.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/JS_Science_Curriculum_Framework_2025_chinese.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/Bio_C_and_A_Guide_updated_c_20151126.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/Chem_C_and_A_Guide_updated_Chi_22082018.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/science-edu/Phy_C_and_A_Guide_updated_c_20151126.pdf
- 你的決定: ____

## [sci_kla_guide_2017] 科學KLA指引2017  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/curriculum-documents.html
- 爬到候選 link (23 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/PSHE_KLACG_P1-S6_Chi_2017.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHist_Curr_Guide_S1-3_Chi_final.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Adapted_Framework_r.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/references-and-resources/chinese-history/Chinese_History_Framework_Bilingual_r.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CHistCAGuide_updated_c_20180108_clean.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CESCG_c_20240730 clean.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_C&amp;A_Guide_C_with_updates_in_2025.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Econ_supplementary_doc_Chi_with_updates_in_2025.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_C&amp;A_Guide_updated_c_(2015.11.24).pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/2.Econ_supplementary_doc_Chi_20151130_clean.pdf
    11. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/curriculum-documents/ERS/ERS_CA Guide_updated_c.pdf
    12. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/ERS_CA Guide_updated_c_(2019.12.03)_clean mode for upload.pdf
    13. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/RE_Curriculum_Guide_Chi_for_upload.pdf
    14. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/CSS13REC.pdf
    15. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/supplementary_notes-final-chi.pdf
    16. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geography C&amp;A Guide 2022-chi.pdf
    17. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geography_Consultation_Brief_Feb_2017-chi.pdf
    18. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/SS_Geog_Revision_2016_Questionnaire_chi-b.pdf
    19. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Geog_Curr_Guide_S1-3_Chi_web_final_21062011.pdf
    20. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_Curr_Guide_S1-3_Chi_final_10072019.pdf
    21. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/Hist_C&amp;A_Guide_c_20180109.pdf
    22. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/6.THS_C&amp;A_Chi_Guide_c(2015.11.24)PSHE section.pdf
    23. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/pshe/l&amp;s_curriculum_guide_chi.pdf
- 你的決定: ____

## [sen_curr_area] SEN課程發展  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/curriculum-area/special-educational-needs/index.html
- 爬到候選 link (1 條):
    1. https://sense.edb.gov.hk/uploads/page/integrated-education/guidelines/sea_guide_c.pdf
- 你的決定: ____

## [tech_curr_docs] 科技課程文件  —  OK
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/technology-edu/curriculum-doc/index.html
- 爬到候選 link (10 條):
    1. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/TE_KLACG_Chi_5_Dec_2017_r2.pdf
    2. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/CT_Supplement_Chi%20_2020.pdf
    3. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/BAFS_CA_Guide_c_2015.pdf
    4. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/BAFS C&amp;A Guide_c_oct 2020_clean.pdf
    5. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/HMSC_CA_Guide_c_2015.pdf
    6. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/TL_CAGuide_c_2015.pdf
    7. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/DAT_CAGuide_c_2015.pdf
    8. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/DAT_C&amp;A_Supplementary_notes_CHI_Dec_2020.pdf
    9. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/ICT_CAGuide_c_2015.pdf
    10. https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/technology-edu/curriculum-doc/ICT_C&amp;A Guide_c_final.pdf
- 你的決定: ____

## [curr_renewal_guides] 課程更新指引總覽  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/renewal/guides.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g09] 非華語中文指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/chi-edu/ncs-curriculum-documents.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g14] 資優培育指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/curriculum-area/gifted/guidelines-on-school-based-gifted-development-programmes/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g17] 訓輔理念與指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/teacher/student-guidance-discipline-services/principles-guidelines/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g31] 英文課程指引(小學)  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/eng-edu/curriculum-documents.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g33] 英文課程指引(中學)  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/eng-edu/curriculum-documents.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g35] 個社人文課程指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g36] 科學課程指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/science-edu/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g37] 藝術教育課程指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/arts-edu/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [g39] 科技教育課程指引  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/technology-edu/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [gifted_policy_docs] 資優教育政策文件  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/curriculum-area/gifted/resources_and_support/policy/policy_doc_and_guidelines/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [gs_pri_curr] 常識科課程文件  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/cross-kla-studies/gs-primary/curriculum-documents.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [pri_science_cert_application_form] 小學科學證書申請表  —  DEAD/empty
- 現 url: None
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [stat_enrolment_report] 學生人數統計  —  DEAD/empty
- 現 url: 
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____

## [steam_edu] STEAM教育  —  no-doc-links
- 現 url: https://www.edb.gov.hk/tc/curriculum-development/kla/technology-edu/steam/index.html
- 爬到候選 link (0 條):
    （無 — 頁面可能係純導航 / JS 動態 / 已失效，要人手 re-discover）
- 你的決定: ____
