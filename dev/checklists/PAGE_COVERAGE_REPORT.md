# 全庫頁碼覆蓋分析報告（2026-06-11，S155 自主批次）

> 讀取 Supabase `wiki_chunks` 全量 **14,505 chunks／207 源**（read-only，零改動）。
> 頁碼標記定義：chunk text 含 `=== Page N ===`。整體覆蓋 **14,239/14,505 = 98.2%**。

| 分類 | 源數 |
|---|---|
| ✅ 全頁碼 | 179 |
| 🟡 部分頁碼（候選 repage） | 7 |
| 🔴 全無頁碼（候選 repage） | 2 |
| ◻️ 結構性無頁（HTML／數據／核實事實） | 19 |

> ⚠️ repage 屬 Supabase 資料改動（CB-3 pipeline：repage_pdfs.py + cb3_b2_pagecarry_migrate.py），本批次**只分析不執行**，候選清單留 Leonard 拍板。歷史脈絡：S119–S132 已 page-carry 94 源、達 ~88% 可行天花板；下表 🔴🟡 即天花板以外殘餘＋新入庫源檢視。

## 逐源明細（按 chunk 數降序）

| source_id | 文件 | chunks | 有頁碼 | % | 類型 | 分類 | 所屬 route |
|---|---|---|---|---|---|---|---|
| `eng_lit_guide_2023` | 英文文學課程及評估指引（中四至中六）（2023） | 633 | 633 | 100% | pdf | ✅ 全頁碼 |  |
| `g13` | 中學教育課程指引（2017）— 課程指引及文件 | 587 | 583 | 99% | html | ◻️ 結構性無頁（HTML/數據） | curriculum |
| `g07` | 基礎教育課程指引—聚焦·深化·持續（小一至小六）(2014) | 438 | 438 | 100% | pdf | ✅ 全頁碼 |  |
| `eng_sss_guide_2021` | 英國語文課程及評估指引（中四至中六）（2021） | 421 | 421 | 100% | pdf | ✅ 全頁碼 |  |
| `g33` | 英國語文教育課程指引（中一至中六）(2007) | 421 | 421 | 100% | pdf | ✅ 全頁碼 |  |
| `g06` | 《小學教育課程指引》完整版（2024） | 412 | 412 | 100% | pdf | ✅ 全頁碼 | cpd,sen,gifted |
| `g24` | 學校行政手冊（2025年11月版） | 383 | 383 | 100% | pdf | ✅ 全頁碼 |  |
| `sag_2025_11` | 學校行政手冊（2025年11月版） | 383 | 383 | 100% | pdf | ✅ 全頁碼 | cpd,conduct,sen,hr_admin,student_support,qa_inspection,gov_admin,safety |
| `gifted_ge_series` | 資優教育系列：全民資優教育＋校本學生才能庫＋學術英才教育單元 | 346 | 346 | 100% | pdf | ✅ 全頁碼 | gifted |
| `eng_jss_supp_2018` | 英國語文課程指引補充（中一至中三）（2018） | 292 | 292 | 100% | pdf | ✅ 全頁碼 |  |
| `eng_pri_guide_2025` | 英國語文課程指引（小一至小六）（2025） | 275 | 275 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `ls_jss_2010` | 生活與社會課程指引（中一至中三）（2010年） | 251 | 251 | 100% | pdf | ✅ 全頁碼 |  |
| `tech_kla_guide_2017` | 科技教育學習領域課程指引 (小一至中六) 二零一七年 | 237 | 236 | 100% | pdf | 🟡 部分頁碼（候選 repage） |  |
| `geog_sss_2007_2022` | 地理課程及評估指引 (中四至中六) 2007 (2022年7月更新) | 214 | 214 | 100% | pdf | ✅ 全頁碼 |  |
| `geog_jss` | 地理課程指引（中一至三） | 203 | 203 | 100% | pdf | ✅ 全頁碼 |  |
| `g38` | 音樂教育學習領域課程指引（小一至中三）(2003) | 194 | 194 | 100% | html | ✅ 全頁碼 | curriculum |
| `g35` | 個人、社會及人文教育學習領域課程指引（小一至中六）(2017) | 187 | 187 | 100% | pdf | ✅ 全頁碼 |  |
| `phys_sss_2007_2015` | 物理(中四至中六) 二零零七年 (二零一五年十一月更新) | 182 | 182 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `g36` | 科學教育學習領域課程指引（小一至中三）(2002) | 179 | 179 | 100% | pdf | ✅ 全頁碼 |  |
| `chem_sss_2007_2018` | 化學(中四至中六)二零零七年 (二零一八年六月更新) | 172 | 172 | 100% | pdf | ✅ 全頁碼 |  |
| `tour_hosp_sss_2007_2015` | 旅遊與款待課程及評估指引 (中四至中六) 2007 (2015年11月更新) | 172 | 172 | 100% | pdf | ✅ 全頁碼 |  |
| `religious_edu_jss_2024` | 宗教教育課程指引（中一至中三）（2024） | 167 | 167 | 100% | pdf | ✅ 全頁碼 |  |
| `chi_hist_sss_2007_2015` | 中國歷史課程及評估指引（中四至中六）2007 （2015年11月更新） | 166 | 166 | 100% | pdf | ✅ 全頁碼 |  |
| `ces_jss_2024` | 公民、經濟與社會課程指引（中一至中三）（2024） | 165 | 165 | 100% | pdf | ✅ 全頁碼 |  |
| `chi_edu_curr_docs` | 中國語文教育學習領域課程文件 | 157 | 157 | 100% | html | ✅ 全頁碼 | curriculum |
| `history_sss_2007_2015` | 歷史課程及評估指引 (中四至中六) 2007 (2015年11月更新) | 155 | 155 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `ma_sss_cag_2017` | 數學課程及評估指引（中四至中六）（2017年12月更新） | 152 | 152 | 100% | pdf | ✅ 全頁碼 |  |
| `apl_curr_docs` | 應用學習課程文件 | 147 | 147 | 100% | pdf | ✅ 全頁碼 |  |
| `ph_pri_guide_2025` | 小學人文科課程指引 (2025) | 146 | 146 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `va_sss_2015` | 《視覺藝術課程及評估指引（中四至中六）》（2015年11月更新） | 144 | 143 | 99% | pdf | 🟡 部分頁碼（候選 repage） |  |
| `pri_science_guide_2025` | 《科學（小一至小六）課程指引》（2025） | 143 | 143 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `ethics_relig_sss_2007_2019` | 倫理與宗教課程及評估指引 (中四至中六) 2007 (2019年11月更新) | 137 | 137 | 100% | pdf | ✅ 全頁碼 |  |
| `ma_kla_guide_2017` | 數學教育學習領域課程指引（小一至中六）（2017） | 136 | 136 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `ict_sss_2007_2015` | 資訊及通訊科技(中四至中六) 二零零七年 (二零一五年十一月更新) | 135 | 135 | 100% | pdf | ✅ 全頁碼 |  |
| `g10` | 《特殊學校課程指引》(2024) | 129 | 129 | 100% | pdf | ✅ 全頁碼 | sen |
| `music_sss_2015` | 《音樂課程及評估指引（中四至中六）》（2015年11月更新） | 129 | 129 | 100% | pdf | ✅ 全頁碼 |  |
| `bio_sss_2007_2015` | 生物(中四至中六) 二零零七年 (二零一五年十一月更新) | 128 | 128 | 100% | pdf | ✅ 全頁碼 |  |
| `history_jss_2019` | 歷史科課程指引（中一至中三）2019 | 125 | 124 | 99% | pdf | 🟡 部分頁碼（候選 repage） | curriculum |
| `pri_curr_guide_2024` | 《小學教育課程指引》(2024) | 124 | 124 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `arts_kla_guide_2017` | 藝術教育學習領域課程指引（小一至中六）(2017) | 116 | 116 | 100% | pdf | ✅ 全頁碼 |  |
| `g19` | 《全校參與模式融合教育運作指南》 | 116 | 116 | 100% | pdf | ✅ 全頁碼 | sen |
| `g37` | 藝術教育學習領域課程指引（小一至中三）(2002) | 116 | 116 | 100% | pdf | ✅ 全頁碼 |  |
| `tl_sss_2007_2015` | 科技與生活 (中四至中六) 二零零七年 (二零一五年十一月更新) | 114 | 114 | 100% | pdf | ✅ 全頁碼 |  |
| `econ_sss_2007_2015` | 經濟課程及評估指引 (中四至中六) 2007 (2015年11月更新) | 112 | 112 | 100% | pdf | ✅ 全頁碼 |  |
| `chi_hist_jss_2019` | 中國歷史科課程指引 (中一至中三) (2019) | 111 | 111 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `kgecg_2017` | 幼稚園教育課程指引（2017） | 108 | 108 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `g29` | 幼稚園教育課程指引（2017） | 107 | 107 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `dat_sss_2007_2015` | 設計與應用科技 (中四至中六) 二零零七年 (二零一五年十一月更新) | 103 | 103 | 100% | pdf | ✅ 全頁碼 |  |
| `sch_activities_guide` | 學校活動指引：戶外活動＋境外遊學團 | 102 | 102 | 100% | pdf | ✅ 全頁碼 | activity |
| `bafs_sss_2007_2020` | 企業、會計與財務概論 (中四至中六) (於2022/23學年的中四實施並在2 | 100 | 100 | 100% | pdf | ✅ 全頁碼 |  |
| `hmsc_sss_2007_2015` | 健康管理與社會關懷 (中四至中六)二零零七年 (二零一五年 十一月更新) | 99 | 99 | 100% | pdf | ✅ 全頁碼 |  |
| `imc_establishment_operation` | 法團校董會的成立與運作（校本管理手冊2014） | 97 | 97 | 100% | pdf | ✅ 全頁碼 | school_governance |
| `crisis_mgmt_handbook` | 學校危機處理（手冊） | 94 | 94 | 100% | pdf | ✅ 全頁碼 | student_support |
| `bafs_sss_2007_2015` | 企業、會計與財務概論 (中四至中六) 二零零七年 (二零一五年十一月更新) | 93 | 92 | 99% | pdf | 🟡 部分頁碼（候選 repage） |  |
| `values_edu_framework_2021_trial` | 《價值觀教育課程架構（試行版）》（2021） | 93 | 93 | 100% | pdf | ✅ 全頁碼 |  |
| `ethics_relig_sss_2024` | 倫理與宗教課程及評估指引 (中四至中六) 2024 | 90 | 90 | 100% | pdf | ✅ 全頁碼 |  |
| `gs_pri_guide_2017` | 常識科課程指引（小學）(2017) | 88 | 88 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `econ_sss_2025` | 經濟課程及評估指引 (中四至中六) (2025年更新) | 87 | 87 | 100% | pdf | ✅ 全頁碼 |  |
| `chi_jss_guide_2023` | 《中國語文課程指引（中一至中三）》（2023） | 85 | 85 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `chi_sss_guide_2021` | 《中國語文課程及評估指引（中四至中六）》（2021） | 85 | 84 | 99% | pdf | 🟡 部分頁碼（候選 repage） |  |
| `music_p1_s6_2024` | 《音樂科課程指引（小一至中六）》（2024） | 85 | 85 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `chi_pri_guide_2023` | 《中國語文課程指引（小一至小六）》（2023） | 83 | 83 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `ict_sss_2021` | 資訊及通訊科技 (中四至中六) 二零二一年 (於2022/23學年的中四實施 | 81 | 81 | 100% | pdf | ✅ 全頁碼 |  |
| `pe_sss_2023` | 體育-課程及評估指引(中四至中六) (2023) | 79 | 79 | 100% | pdf | ✅ 全頁碼 |  |
| `g14` | 校本資優培育課程指引 | 77 | 0 | 0% | html | ◻️ 結構性無頁（HTML/數據） | gifted |
| `icac_school_governance` | 防貪錦囊：學校管治與內部監控 (ICAC) | 75 | 75 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `sci_jss_framework_2025` | 科學教育學習領域課程指引補充文件–科學 (中一至中三)課程框架 二零二五年 | 75 | 74 | 99% | pdf | 🟡 部分頁碼（候選 repage） |  |
| `pe_kla_2017` | 體育學習領域課程指引(小一至中六) (2017) | 74 | 73 | 99% | pdf | 🟡 部分頁碼（候選 repage） | curriculum |
| `va_p1_s6_2024` | 《視覺藝術科課程指引（小一至中六）》（2024） | 71 | 71 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `music_sss_2024` | 《音樂課程及評估指引（中四至中六）》（2024年9月更新） | 69 | 69 | 100% | pdf | ✅ 全頁碼 |  |
| `g16` | 學生訓育工作指引 | 63 | 63 | 100% | index | ✅ 全頁碼 | student_support |
| `tdtf_report_2019` | 教師專業發展專責小組報告 (2019年3月) | 61 | 61 | 100% | pdf | ✅ 全頁碼 | cpd |
| `g22` | 科技教育 – 安全指引 | 58 | 58 | 100% | pdf | ✅ 全頁碼 | safety |
| `g23` | 體育 – 安全措施指引 | 57 | 57 | 100% | pdf | ✅ 全頁碼 |  |
| `imc_election_guides` | 法團校董會校董選舉指引（家長／教師／校友校董・委任五步曲） | 57 | 57 | 100% | pdf | ✅ 全頁碼 | school_governance |
| `stat_enrolment_2014` |  | 56 | 56 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2015` |  | 56 | 56 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2012` |  | 55 | 55 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2013` |  | 55 | 55 | 100% |  | ✅ 全頁碼 |  |
| `chi_lit_guide_2025` | 《中國文學課程及評估指引（中四至中六）》（2025年更新） | 54 | 54 | 100% | pdf | ✅ 全頁碼 |  |
| `sen_exam_arrangements_2025` | 《為有特殊教育需要學生提供校內考試特別安排》(2025) | 51 | 51 | 100% | pdf | ✅ 全頁碼 | sen |
| `g21` | 視覺藝術科安全指引 | 48 | 48 | 100% | pdf | ✅ 全頁碼 | safety |
| `imc_briefing_qa` | 法團校董會簡介會問答（2013） | 48 | 48 | 100% | pdf | ✅ 全頁碼 | school_governance |
| `gifted_tp_resource_kit` | 校本資優教育資源套（2024） | 41 | 41 | 100% | pdf | ✅ 全頁碼 | gifted |
| `nat_sec_edu` | 國家安全教育課程資源 | 39 | 39 | 100% | pdf | ✅ 全頁碼 |  |
| `kg_crisis_mgmt` | 幼稚園危機處理 — 危機善後介入及心理支援 | 38 | 38 | 100% | pdf | ✅ 全頁碼 | student_support |
| `coa_imc_1_19` | 資助則例（設有法團校董會資助學校適用版本） | 37 | 37 | 100% | pdf | ✅ 全頁碼 | school_governance,finance |
| `perf_indicators_2022` | 香港學校表現指標（中學、小學及特殊學校適用）(2022) | 36 | 36 | 100% | pdf | ✅ 全頁碼 | qa_inspection |
| `stat_enrolment_2020` |  | 35 | 35 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2016` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2017` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2018` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2019` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2021` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2022` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `stat_enrolment_2024` |  | 34 | 34 | 100% |  | ✅ 全頁碼 |  |
| `chi_hist_jss_bilingual_2019` | 中國歷史科課程大綱 (中一至中三) (2019) (中英雙語版) | 33 | 33 | 100% | pdf | ✅ 全頁碼 |  |
| `eng_nat_sec_2025` | 英文科國家安全教育課程框架（2025） | 33 | 33 | 100% | pdf | ✅ 全頁碼 |  |
| `stat_enrolment_2023` |  | 33 | 33 | 100% |  | ✅ 全頁碼 |  |
| `stims_guide_2025` | 學生資料管理系統（STIMS）指引（2025年9月版） | 33 | 33 | 100% | pdf | ✅ 全頁碼 | placement |
| `econ_sss_supp_2025` | 經濟課程及評估指引 (中四至中六)-補充文件 (2025年更新) | 32 | 32 | 100% | pdf | ✅ 全頁碼 |  |
| `g01` | 資助學校採購程序指引（2025年10月更新） | 32 | 32 | 100% | pdf | ✅ 全頁碼 | finance |
| `econ_sss_supp_2015` | 經濟課程及評估指引 (中四至中六)-補充文件 (2015年11月版) | 31 | 31 | 100% | pdf | ✅ 全頁碼 |  |
| `g05` | 教師專業操守指引 | 29 | 29 | 100% | html | ✅ 全頁碼 | conduct,hr_admin |
| `edbcm183_2023_values_edu` | 教育局通函第183/2023號 —— 豐富《價值觀教育課程架構（試行版）》內 | 27 | 27 | 100% | pdf | ✅ 全頁碼 |  |
| `imc_governance_supplements` | 法團校董會管治補充指引（成立運作第5章・角色責任・會議・法例提醒・良好管治・ | 27 | 27 | 100% | pdf | ✅ 全頁碼 | school_governance |
| `role_facts_curriculum` |  | 26 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | cpd,curriculum |
| `role_facts_finance` |  | 25 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | finance |
| `chi_hist_jss_ncs_2019` | 調適中國歷史科課程大綱 (中一至中三) (2019) (非華語學生適用) | 25 | 25 | 100% | pdf | ✅ 全頁碼 |  |
| `edbc18_2023_pri_science` | 教育局通告第18/2023號 — 開設小學科學科及一系列相關支援措施 | 25 | 25 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `g02` | 設有法團校董會的資助學校財務管理指引 | 25 | 25 | 100% | pdf | ✅ 全頁碼 | school_governance,finance |
| `k1_admission_2627` | 2026/27 學年小一（K1）入學安排（通函 EDBCM81/2025＋F | 25 | 25 | 100% | pdf | ✅ 全頁碼 | kg_admission |
| `edbc002_2026` | 教育局通告第2/2026號 | 24 | 24 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `lpe_framework_primary` | 小學生涯規劃教育推行策略大綱 | 23 | 23 | 100% | pdf | ✅ 全頁碼 | student_support |
| `sec_curr_guide_2017_booklet_6a` | 《中學教育課程指引》(2017) - 分冊6A︰德育及公民教育：加強價值觀教 | 21 | 21 | 100% | pdf | ✅ 全頁碼 |  |
| `edbc20_2023_ph_pri` | 教育局通告20/2023號 — 開設小學人文科 | 20 | 20 | 100% | html | ✅ 全頁碼 | curriculum |
| `edbc15_2025_child_abuse` | 教育局通告第15/2025號 處理懷疑虐待兒童及家庭暴力個案 | 19 | 19 | 100% | pdf | ✅ 全頁碼 | student_support |
| `g26` | 2026/27學年幼稚園收生安排指引 | 19 | 19 | 100% | pdf | ✅ 全頁碼 | kg_admission,curriculum |
| `gifted_osalp_compendium` | 資優教育基金校外進階學習課程匯編（OSALP） | 19 | 19 | 100% | pdf | ✅ 全頁碼 | gifted |
| `gifted_policy_docs` | 資優教育政策文件及指引 | 19 | 19 | 100% | html | ✅ 全頁碼 | gifted |
| `cgss_2024` | 特殊學校課程指引資源（2024） | 17 | 17 | 100% | pdf | ✅ 全頁碼 | sen |
| `geog_sss_update_brief` | 高中地理課程更新簡介 | 15 | 15 | 100% | pdf | ✅ 全頁碼 |  |
| `role_facts_student` |  | 14 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | conduct,sen,student_support |
| `edbcm58_2024_pri_science` | 教育局通函第58/2024號 — 《科學﹙小一至小六﹚課程框架》、「小學科學 | 14 | 14 | 100% | pdf | ✅ 全頁碼 |  |
| `g03` | 全方位學習津貼運用指引 | 14 | 14 | 100% | html | ✅ 全頁碼 | activity |
| `ma_sss_diversity_2021` | 高中數學科照顧學生多樣性及創造空間指引（2021） | 14 | 14 | 100% | pdf | ✅ 全頁碼 |  |
| `safety_mgmt_committee` | 成立學校安全管理委員會程序 | 14 | 14 | 100% | pdf | ✅ 全頁碼 | safety |
| `supply_teacher_guide` | 資助學校聘用代課教師的指引 | 14 | 14 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `role_facts_activity` |  | 13 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | activity |
| `role_facts_it` |  | 13 | 0 | 0% |  | ◻️ 核實事實（天生無頁） |  |
| `geog_sss_summary_2022` | 2022年7月更新的《地理科課程及評估指引(中四至中六)》撮要 | 13 | 13 | 100% | pdf | ✅ 全頁碼 |  |
| `mce_framework_2008` | 《德育及公民教育課程架構》(2008)（包括詳細內容及相關課程發展工具） | 13 | 13 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `pri_science_cert_course_list` | 「小學科學教師專業培訓證書（30小時）」指定課程清單 | 13 | 13 | 100% | pdf | ✅ 全頁碼 |  |
| `circ_edbc24017` | 教育局通告第17/2024號：學校課程持續更新：《小學教育課程指引》（202 | 12 | 12 | 100% | pdf | ✅ 全頁碼 | cpd,curriculum |
| `edbc_tropical_cyclone_day` | 教育局通告 熱帶氣旋及持續大雨下的安排（幼稚園及日校） | 12 | 12 | 100% | pdf | ✅ 全頁碼 | safety |
| `edbc14_2023_student_protect` | 教育局通告第14/2023號 加強保障學童的措施 | 12 | 12 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `edbc197_2024_ph_pri` | 教育局通函197/2024號 — 小學人文科：學校問卷調查及相關支援措施 | 12 | 12 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `g17` | 理念與指引（訓育及輔導） | 12 | 3 | 25% | html | ◻️ 結構性無頁（HTML/數據） | student_support |
| `geog_sss_supp_2022` | 《地理課程及評估指引（中四至中六）》(2022年7月更新版)「補充資料」 | 12 | 12 | 100% | pdf | ✅ 全頁碼 |  |
| `long_service_payment_guide` | 發放遣散費及長期服務金的指引 (2025年5月) | 12 | 12 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `edbc9_2024_ph_pri` | 教育局通告9/2024號 — 《小學人文科課程框架》（定稿）及支援措施 | 11 | 11 | 100% | html | ✅ 全頁碼 | curriculum |
| `role_facts_general` |  | 10 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | cpd,kg_admission,placement,conduct,sen,gifted,school_governance,finance,hr_admin,activity,student_support,qa_inspection,gov_admin,safety |
| `ct_programming_pri_2020` | 《計算思維－編程教育：小學課程補充文件》 (小學) 二零二零年 | 10 | 10 | 100% | pdf | ✅ 全頁碼 |  |
| `edbc12_2025_ph_pri` | 教育局通告第12/2025號 — 《小學人文科課程指引》及支援措施 | 10 | 0 | 0% | pdf | 🔴 全無頁碼（候選 repage） | curriculum |
| `edbc13_2025_pri_science` | 教育局通告第13/2025號 — 《科學（小一至小六）課程指引》、2025/ | 10 | 10 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `edbc18_2019_sspa` | 教育局通告第18/2019號 中學學位分配辦法 | 10 | 10 | 100% | pdf | ✅ 全頁碼 | placement |
| `g09` | 中國語文課程補充指引（非華語學生）(2025) | 10 | 10 | 100% | pdf | ✅ 全頁碼 |  |
| `sse_tools_2025` | 學校自我評估工具及數據小冊子 (2025) | 10 | 10 | 100% | pdf | ✅ 全頁碼 | qa_inspection |
| `surplus_teacher_arr_2026` | 資助中學及特殊學校過剩教師及實驗室技術員的安排 (2026) | 10 | 10 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `stat_pri` | 小學統計數字 | 9 | 0 | 0% | xlsx | ◻️ 結構性無頁（HTML/數據） |  |
| `stat_sec` | 中學統計數字 | 9 | 0 | 0% | xlsx | ◻️ 結構性無頁（HTML/數據） |  |
| `edbc_tropical_cyclone_night` | 教育局通告 熱帶氣旋及持續大雨下的安排（夜校） | 9 | 9 | 100% | pdf | ✅ 全頁碼 | safety |
| `edbcm57_2024_pri_science` | 教育局通函第57/2024號 — 支援開設小學科學科的一筆過津貼 | 9 | 9 | 100% | pdf | ✅ 全頁碼 |  |
| `g11` | 擬定校曆表指引 | 9 | 9 | 100% | html | ✅ 全頁碼 | hr_admin |
| `g18` | 學童乘搭校車的安全指引 | 9 | 9 | 100% | html | ✅ 全頁碼 | safety |
| `role_facts_hr` |  | 8 | 0 | 0% |  | ◻️ 核實事實（天生無頁） | cpd,conduct,hr_admin |
| `stat_kg` | 幼稚園統計數字 | 8 | 0 | 0% | xlsx | ◻️ 結構性無頁（HTML/數據） | curriculum |
| `blnst_test_candidate_notes` | 基本法及香港國安法測試（非學位程度）考生須知 | 8 | 8 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `edbc15_2022_accountability` | 教育局通告第15/2022號 優化學校發展與問責架構 | 8 | 8 | 100% | pdf | ✅ 全頁碼 | qa_inspection |
| `edbcm243_2024_pri_science` | 教育局通函第243/2024號 — 小學科學科教師專業培訓（2024/25學 | 8 | 8 | 100% | pdf | ✅ 全頁碼 |  |
| `fundraising_guide` | 學校籌款活動指引 | 8 | 8 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `hsp_drug_testing_2026` | 含測檢元素的健康校園計劃（2026/27學年） | 8 | 8 | 100% | pdf | ✅ 全頁碼 | student_support |
| `stat_special` | 特殊學校統計數字 | 7 | 0 | 0% | xlsx | ◻️ 結構性無頁（HTML/數據） |  |
| `emergency_repairs_guide` | 資助學校緊急修葺申請指導資料 | 7 | 7 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `g04` | 教職員批假指引 | 7 | 0 | 0% | html | ◻️ 結構性無頁（HTML/數據） | hr_admin |
| `edbc003_2026` | 教育局通告第3/2026號 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `edbc13_2022_blnst` | 教育局通告第13/2022號 新聘任教師《基本法及香港國安法》測試 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `edbcm83_2020_student_care` | 教育局通函第83/2020號 關顧學生 重回正軌 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | student_support |
| `edbcm98_2024_pri_science` | 教育局通函第98/2024號 — 小學科學科相關課程資源 | 6 | 6 | 100% | pdf | ✅ 全頁碼 |  |
| `job_sharing_guide` | 資助學校處理共享教職指引 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `major_repairs_proc_nonestate` | 大規模修葺工程的程序（非屋邨資助學校） | 6 | 6 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `private_sch_employment_notes` | 私立學校處理教職員聘用事宜的注意事項 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `sch_calendar_guide` | 學校曆／一般假期／上課日數計算指引 | 6 | 6 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `stat_integrated_edu` | 融合教育統計數字 | 5 | 0 | 0% | xlsx | ◻️ 結構性無頁（HTML/數據） |  |
| `blnst_test_notes_nondeg` | 基本法及香港國安法測試（非學位程度）申請人須知 | 5 | 5 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `dat_sss_supp_2020` | 設計與應用科技 (中四至中六) - 補充資料 (二零二零年十二月) | 5 | 5 | 100% | pdf | ✅ 全頁碼 |  |
| `edbcm_major_repairs_grant` | 教育局通函 大規模修葺工程津貼（2027-28） | 5 | 5 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `edbcm141_2025_blnst` | 教育局通函第141/2025號 教師《基本法及香港國安法》測試 | 5 | 5 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `embc5_2005_appointment` | 教育統籌局通告第5/2005號 學校教職員的聘任 | 5 | 5 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `kg_admin_guide` | 幼稚園行政指引：學費涵蓋項目＋售賣物品指引 | 5 | 5 | 100% | pdf | ✅ 全頁碼 | kg_admission |
| `major_repairs_proc_estate` | 大規模修葺工程的程序（屋邨資助學校） | 5 | 5 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `sdp_guide` | 如何編寫學校發展計劃（首份校董會/法團校董會服務合約適用） | 5 | 5 | 100% | pdf | ✅ 全頁碼 | school_governance,gov_admin |
| `edbc005_2026` | 教育局通告第5/2026號 | 4 | 4 | 100% | pdf | ✅ 全頁碼 | curriculum |
| `edbc015_2021_lpe` | 教育局通告第15/2021號 生涯規劃教育 | 4 | 4 | 100% | pdf | ✅ 全頁碼 | student_support |
| `edbc100_2002_healthy_sch` | 教育局通告第100/2002號 健康校園政策（禁毒） | 4 | 4 | 100% | pdf | ✅ 全頁碼 | student_support |
| `edbc14_2024_spms` | 教育局通告第14/2024號 校舍巡察及保養 (SPMS) | 4 | 4 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `fin_mgmt_notes_aided` | 資助學校財務管理注意事項 | 4 | 4 | 100% | pdf | ✅ 全頁碼 | finance |
| `sch_extension_guide` | 增設校舍指引（校舍設於為學校用途而設計建造的房產） | 4 | 4 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `bip_insurance_notes_2025` | 學校綜合保險計劃摘要說明 (2025/26 及 2026/27) | 3 | 3 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `g15` | 體育學習領域課程指引（小一至中三）(2002) | 3 | 3 | 100% | pdf | ✅ 全頁碼 |  |
| `lab_prep_room_aircon` | 實驗室預備室空調設備指引 | 3 | 3 | 100% | pdf | ✅ 全頁碼 | safety |
| `music_national_anthem_2024` | 《國歌的學與教：音樂科課程補充文件（小一至中六）》（2024年9月更新） | 3 | 3 | 100% | pdf | ✅ 全頁碼 |  |
| `s4_placement_2026` | 中四學位安排機制簡介（2026） | 3 | 3 | 100% | pdf | ✅ 全頁碼 | placement |
| `sch_name_change_guide` | 學校更改名稱的批核準則及程序 | 3 | 3 | 100% | pdf | ✅ 全頁碼 | gov_admin |
| `slope_rmi_ei_notes` | 斜坡的例行維修檢查及工程師維修檢查須知 | 3 | 3 | 100% | pdf | ✅ 全頁碼 | safety |
| `edbc18_2008_harmonious` | 教育局通告第18/2008號 締造和諧校園 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | student_support |
| `edbc22_2024_student_safety` | 教育局通告第22/2024號 學生安全及健康 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | safety |
| `fire_service_installation` | 消防裝置及設備指引 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | safety |
| `gas_odour_measures` | 校內出現氣體異味時應採取措施的指引 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | safety |
| `hsp_framework` | 健康校園政策架構 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | student_support |
| `occupational_safety_health` | 職業安全及健康指引 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | safety |
| `staff_medical_health` | 學校員工的體格檢驗及健康狀況 | 2 | 2 | 100% | pdf | ✅ 全頁碼 | hr_admin |
| `stat_integrated` |  | 2 | 0 | 0% |  | 🔴 全無頁碼（候選 repage） |  |
| `bank_choice_notes` | 學校選擇銀行注意事項 | 1 | 1 | 100% | pdf | ✅ 全頁碼 | finance |
| `g20` | 學校活動指引 | 1 | 0 | 0% | html | ◻️ 結構性無頁（HTML/數據） |  |
| `g25` | 幼稚園相關指引及須知 | 1 | 0 | 0% | html | ◻️ 結構性無頁（HTML/數據） | kg_admission,curriculum |
| `stat_edb_figures` | 教育統計數字 | 1 | 0 | 0% | html | ◻️ 結構性無頁（HTML/數據） |  |

