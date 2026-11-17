# A8 決定表：「📚EDB指引」瀏覽清單與庫存的差異（2026-11-17）

> **性質**：一次性決定材料（工作清單 A8 的交付物）。Leonard 批准後執行，執行完把本檔標為「已處理」並保留作證據；不是常設規則。
> **來源**：`python3 dev/source/check_registry_drift.py --check` 於 2026-11-17 13:32 UTC 的清單；各來源的 registry 狀態與 Supabase 片段標題同日讀取（唯讀）。
> **對用戶的影響**：瀏覽清單（`app.html` 的 `GUIDELINES_REGISTRY`，現 182 項）是用戶在「📚EDB指引」分頁看到的文件目錄。它與搜尋是兩回事：在庫但不在清單 → 搜得到但瀏覽不到；在清單但不在庫 → 瀏覽得到（連去 EDB 網頁），但問問題時平台答不到。

## 一、PHANTOM：清單有、庫內沒有（36 項）

### 甲　索引頁、專題頁（19 項）—— 建議：保留在清單，並令檢查不再把它們計入

這些項目本來就是「去 EDB 網頁找文件」的入口，不是一份文件，入庫沒有意義。保留讓用戶瀏覽是對的；但檢查每次都把它們算作差異，令真正的缺口被埋沒。

`arts_curr_docs`、`cs_curr`、`curr_renewal_guides`、`gs_pri_curr`、`ma_curr_index`、`moral_civic_curr`、`pe_curr_docs`、`pecg_2024_landing`、`ph_pri_curr`、`pri_science`、`pshe_curr_docs`、`sci_curr_docs`、`sen_curr_area`、`steam_edu`、`tech_curr_docs`、`provident_fund`、`g08`（標題寫《中國語文教育學習領域課程指引》(2024)，但連結是課程文件及示例總頁）、`g32`（連結是 PSHE 課程文件總頁）、`pri_science_cert_application_form`（申請表格，DOCX）

**批准後做法**：在 `dev/source/check_registry_drift.py` 加一個「只供瀏覽」名單（附逐項理由），PHANTOM 不再計這 19 項；自測加一條「名單內的項目若其實有片段即報錯」。屬改監察規則，與本表一同批准。

### 乙　舊版文件，庫內已有新版（7 項）—— 建議：從清單移除

用戶可能把舊版當成現行版本。庫內已有新版，搜尋會答新版。

| 清單項目 | 新版（已在庫） |
|---|---|
| `g12` 數學教育學習領域課程指引（小一至中三）(2002) | `ma_kla_guide_2017` |
| `g27` 小學數學課程指引（2000） | `ma_kla_guide_2017` |
| `g39` 科技教育學習領域課程指引（小一至中三）(2002) | `tech_kla_guide_2017` |
| `g34` 普通話科課程指引（小一至中三）(2000) | `pth_guide_2017`（2017 版本身亦未入庫，見丙） |
| `g30` 小學人文科課程及評估指引（試行版）(2023) | `ph_pri_guide_2025`（registry 已標 superseded） |
| `pe_sss_2007_2015` 體育課程及評估指引 (2007, 2015 更新) | `pe_sss_2023` |
| `sci_jss_supp_2017` 科學（中一至中三）補充文件 (2017) | `sci_jss_framework_2025` |

**批准後做法**：從 `GUIDELINES_REGISTRY` 刪除這 7 項；README 與平台介紹內的指引數目隨之更新（按 `dev/DOC_SYNC_CHECKLIST.md`）。

### 丙　現行文件，未入庫（10 項）—— 建議：其中 9 項入庫，1 項維持只供瀏覽

| 清單項目 | 建議 |
|---|---|
| `chi_pri_lo_2023` 小學中國語文建議學習重點 (2023) | 入庫 |
| `chi_sec_lo_2021` 中學中國語文建議學習重點 (2021) | 入庫 |
| `ma_pri_content_2017`、`ma_jss_content_2017`、`ma_sss_content_2017` 數學科學習內容（小學／初中／高中） | 入庫（老師常問某課題屬哪一級） |
| `pth_guide_2017` 普通話科課程指引（小一至中三）(2017) | 入庫 |
| `gspf_general_info_2023`、`sspf_general_info_2023` 補助／津貼學校公積金的一般資料 (2023) | 入庫（人事問題常見） |
| `pf_edu_ord_2013_faq` 與《2013年教育(修訂)條例》相關的常見問題（公積金） | 入庫 |
| `staff_est_sp_sch_pri` 資助特殊學校小學部教學人員編制 | 維持只供瀏覽（registry 標 `held_back`，當時刻意未入庫；原因未在本次追查） |

**批准後做法**：入庫屬寫生產資料，逐份走 Option A（在入庫 Issue 剔選），一次一份。

## 二、UNLISTED：庫內有、清單沒有（119 項，2,626 片段）

判斷原則（工作卡 A8）：指引、手冊、長期有效的通告，用戶會想瀏覽 → 加入；一次性或年度通函、計劃申請、報告、非教育局文件 → 不列（仍然搜得到）。

### 丁　建議加入清單：指引與手冊（51 項）

`gifted_ge_series`、`kg_admin_guide_2026`、`kg_operation_manual_2026`、`sch_activities_guide`、`imc_establishment_operation`、`crisis_mgmt_handbook`、`values_edu_framework_2026`、`cgss_sss_2021`、`icac_school_governance`、`imc_election_guides`、`sen_exam_arrangements_2025`、`imc_briefing_qa`、`kg_crisis_mgmt`、`gifted_tp_resource_kit`、`perf_indicators_2022`、`stims_guide_2025`、`imc_governance_supplements`、`va_safety_sec`、`lpe_framework_primary`、`supply_teacher_guide`、`gifted_osalp_compendium`、`smc_constitution_sample`、`cgss_2024`、`safety_mgmt_committee`、`long_service_payment_guide`、`sse_tools_2025`、`sch_bus_drivers_2026`、`sch_bus_operators_2026`、`sch_bus_parents_2026`、`sch_bus_escorts_2026`、`sch_bus_students_2026`、`fundraising_guide`、`emergency_repairs_guide`、`job_sharing_guide`、`major_repairs_proc_nonestate`、`major_repairs_proc_estate`、`private_sch_employment_notes`、`kg_admin_guide`、`fin_mgmt_notes_aided`、`sch_extension_guide`、`bip_insurance_notes_2025`、`lab_prep_room_aircon`、`s4_placement_2026`、`sch_name_change_guide`、`slope_rmi_ei_notes`、`fire_service_installation`、`gas_odour_measures`、`hsp_framework`、`occupational_safety_health`、`staff_medical_health`、`bank_choice_notes`

（其中 `cgss_sss_2021` 公民與社會發展科課程及評估指引是高中核心科目，現時瀏覽不到，最值得先加。五份校巴安全指引可合併為一個瀏覽項目，由 Leonard 決定。）

### 戊　建議加入清單：長期有效的教育局通告（26 項）

`edbc15_2025_child_abuse`、`edbc_tropical_cyclone_day`、`edbc_tropical_cyclone_night`、`edbc14_2023_student_protect`、`edbc18_2019_sspa`、`edbc15_2022_accountability`、`edbc14_2024_spms`、`edbc13_2022_blnst`、`edbc22_2024_student_safety`、`edbc015_2021_lpe`、`edbc100_2002_healthy_sch`、`edbc18_2008_harmonious`、`embc5_2005_appointment`、`edbc002_2026`（地理科初中課程框架）、`edbc003_2026`（價值觀教育課程架構）、`edbc005_2026`（更新學習宗旨）、`edbc007_2026`、`edbc008_2026`、`edbc009_2026`、`edbc010_2026`、`edbc011_2026`、`edbc012_2026`、`edbc013_2026`、`edbc014_2026`、`edbc015_2026`、`edbc016_2026`

（2026 年系列 13 份，另加 13 份較早但仍有效的通告。）

### 己　建議不列（42 項，仍然搜得到）

- **一次性或年度通函、計劃申請**（38 項）：`edbcm060_2026`、`edbcm186_2026`、`edbcm156_2026`、`edbcm_221_2025_smart_teaching`、`edbcm089_2026`、`edbcm066_2026`、`edbcm080_2026`、`edbcm136_2026`、`edbcm073_2026`、`edbcm134_2026`、`edbcm070_2026`、`edbcm107_2026`、`edbcm076_2026`、`edbcm116_2026`、`edbcm144_2026`、`edbcm081_2026`、`edbcm094_2026`、`edbcm096_2026`、`edbcm198_2026`、`edbcm088_2026`、`edbcm095_2026`、`edbcm108_2026`、`edbcm124_2026`、`edbcm167_2026`、`edbcm170_2026_blnst`、`edbcm203_2026`、`edbcm138_2026`、`edbcm152_2026`、`edbcm197_2026`、`edbcm113_2026`、`edbcm135_2026`、`edbcm141_2026`、`edbcm142_2026`、`edbcm155_2026`、`edbcm_major_repairs_grant`、`k1_admission_2627`、`hsp_drug_testing_2026`、`surplus_teacher_arr_2026`
- **報告、舊時期文件**（2 項）：`tdtf_report_2019`（專責小組報告，非指引）、`edbcm83_2020_student_care`（疫情期間）
- **非教育局文件**（1 項）：`pcpd_cloud_computing`（私隱專員公署）
- **與已列項目重複**（1 項）：`debp_leaflet`（藍圖三摺頁；清單已有藍圖全文與行政摘要）

**批准後做法（丁、戊）**：在 `GUIDELINES_REGISTRY` 逐項加入（標題、類別、級別、年份、連結取自 registry），按類別分批，每批一個 PR；README 與平台介紹內的指引數目同步更新；跑 `check_registry_drift.py` 確認 UNLISTED 相應下降。

## 三、批准後的數字（估算）

| | 現在 | 全部照建議執行後 |
|---|---|---|
| 瀏覽清單項目 | 182 | 約 182 − 7 + 51 + 26 = 252 |
| PHANTOM | 36 | 10（丙的現行文件，入庫後逐步降至 1） |
| UNLISTED | 119 | 約 42（己，按設計不列） |

己類 42 項會一直算作 UNLISTED。若要令檢查只報真缺口，可仿甲的做法把己類也列入「按設計不列」名單（同樣附理由）。

## 四、要 Leonard 決定的

1. 甲：19 個索引頁保留，並在檢查中標為「只供瀏覽」——可以嗎？
2. 乙：7 份舊版從清單移除——可以嗎？
3. 丙：9 份現行文件逐份入庫——可以嗎？
4. 丁、戊：77 項加入清單（五份校巴指引合併或分開？）——可以嗎？
5. 己：42 項不列，並在檢查中標為「按設計不列」——可以嗎？
