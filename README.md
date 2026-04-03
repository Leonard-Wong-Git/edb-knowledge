# 學校管理知識中心

> 香港教育局（EDB）政策知識庫 — 專為學校管理人員而設

[![Version](https://img.shields.io/badge/version-v1.1.0-teal)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Platform](https://img.shields.io/badge/platform-GitHub%20Pages-brightgreen)](https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html)

**🔗 Live Demo:** [https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html](https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html)

---

## 功能簡介

| 功能 | 說明 |
|------|------|
| 📚 **知識庫** | EDB 政策事實，按角色（校長、副校長、主任、教師等）分類 |
| 📋 **指引文件庫** | 官方 EDB 指引文件，按類別導覽 |
| 🔍 **智能搜尋** | 跨主題關鍵字搜尋，顯示相關事實、角色標籤及原始出處連結 |
| ✅ **審核流程** | Draft → Approved 工作流，支援批量批核及 JSON 匯出 |
| 🔗 **出處追溯** | 每個事實均連結至具體 EDB 官方文件（PDF 或網頁） |

## 涵蓋主題

- 💰 **財務 / 採購 / 津貼** — 採購程序、報價門檻、整筆撥款
- 👥 **人力資源** — CPD、代課教師津貼、批假政策、專業操守
- 📖 **課程** — PECG 2024、八個 KLA、五種基要學習經歷、STEAM
- 🏃 **校外活動** — 境外活動、戶外活動、全方位學習津貼
- 🧒 **學生事務** — 訓育、反欺凌、SEN 融合教育、出席記錄
- 💻 **資訊科技** — 資訊保安政策、BYOD、數據保安
- 🏫 **通用行政** — 法團校董會、公開資料守則、學校行政手冊

## 技術架構

- **Single-file SPA** — 純前端，無需後端或構建工具
- **React 18** + **Babel** + **Tailwind CSS 2.2**（全部由 CDN 載入）
- 資料嵌入 HTML 的 `INITIAL_DATA` 常數，同步備份於 `dev/knowledge/role_facts.json`

## 文件結構

```
edb-knowledge/
├── k1-dashboard.html          # 主應用程式（單一 HTML 文件）
├── index.html                 # 入口重定向
├── README.md                  # 本文件
├── CHANGELOG.md               # 版本歷史
└── dev/
    └── knowledge/
        └── role_facts.json    # 知識庫數據備份（JSON 格式）
```

## 版本歷史

詳見 [CHANGELOG.md](CHANGELOG.md)

## 數據來源

所有事實均來自香港教育局官方文件：

- [教育局通告 EDBC20006C（CPD）](https://www.edb.gov.hk/attachment/tc/teacher/qualification-training-development/development/cpd-teachers/EDBC20006C.pdf)
- [《小學教育課程指引》2024 完整版](https://www.edb.gov.hk/attachment/tc/curriculum-development/major-level-of-edu/primary/curriculum-documents/Primary_Education_Curriculum_Guide/PECG%202024_full.pdf)
- [資助學校採購程序指引（2024）](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/procurement-procedures-in-aided-schools/Guidelines%20on%20Procurement%20Procedures%20in%20Aided%20Schools%20Trad%20Chi_2024.pdf)
- [整合代課教師津貼指引（2023）](https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/trg/TRG_guidelines_C.pdf)
- [學校資訊保安建議措施（2019）](https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/information-security-in-school.html)
- 及其他 25+ 份 EDB 官方文件

---

*最後更新：2026-04-03 | 維護：leonard-wong-git*
