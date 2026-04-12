# vault/stat_enrolment_report — 學生人數統計報告書（年度系列）

**source_id:** `stat_enrolment_report`
**來源系列 URL 格式:** `https://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/Enrol_{YYYY}.pdf`
**涵蓋範圍:** 2012/13 至 2024/25 學年
**內容:** 幼稚園、小學、中學及特殊教育學校學生人數統計

## 已提取檔案

| 檔案 | 學年 | 提取頁數 | 狀態 |
|---|---|---|---|
| extract_enrolment_2012.txt | 2012/13 | 首20頁 | ✅ |
| extract_enrolment_2013.txt | 2013/14 | 首20頁 | ✅ |
| extract_enrolment_2014.txt | 2014/15 | 首20頁 | ✅ |
| extract_enrolment_2015.txt | 2015/16 | 首20頁 | ✅ |
| extract_enrolment_2016.txt | 2016/17 | 首20頁 | ✅ |
| extract_enrolment_2017.txt | 2017/18 | 首20頁 | ✅ |
| extract_enrolment_2018.txt | 2018/19 | 首20頁 | ✅ |
| extract_enrolment_2019.txt | 2019/20 | 首20頁 | ✅ |
| extract_enrolment_2020.txt | 2020/21 | 首20頁 | ✅ |
| extract_enrolment_2021.txt | 2021/22 | 首20頁 | ✅ |
| extract_enrolment_2022.txt | 2022/23 | 首20頁 | ✅ |
| extract_enrolment_2023.txt | 2023/24 | 首20頁 | ✅ |
| extract_enrolment_2024.txt | 2024/25 | 首20頁 | ✅ |

## 提取策略

每份報告書首20頁涵蓋：
- 簡介（Introduction）：整體趨勢說明
- 總表 I（All Schools）：全港學校及學生總覽
- 幼稚園總表起始部份

如需更深層數據（個別學校、分區統計），可日後按需提取剩餘頁面。

## Phase 2 自動更新

Phase 2 腳本應：
1. 下載 `Enrol_{current_year}.pdf`
2. 提取首20頁文字
3. 與最新年份 extract 比對 diff
4. 若為新學年則新增 `extract_enrolment_{YYYY}.txt`（自動審批，fact_type=statistical）
