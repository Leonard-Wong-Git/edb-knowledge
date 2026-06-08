# 學校管理知識中心（K1 知識平台）

> 香港教育局（EDB）政策知識庫 — 專為學校管理人員而設

[![Version](https://img.shields.io/badge/version-v2.3.0-teal)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-brightgreen)](https://leonard-wong-git.github.io/edb-knowledge/app.html)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7)](https://edb-knowledge.onrender.com/health)

---

## 🔗 連結

| | URL |
|---|---|
| **知識平台（主應用）** | https://leonard-wong-git.github.io/edb-knowledge/app.html |
| **入口頁** | https://leonard-wong-git.github.io/edb-knowledge/ |
| **Quick Q&A** | https://leonard-wong-git.github.io/edb-knowledge/q.html |
| **後端 API** | https://edb-knowledge.onrender.com |

---

## 功能簡介

| 功能 | 說明 |
|------|------|
| 🔍 **政策搜尋** | 語義搜尋 455 條已核實政策事實（Channel A），顯示相關事實、角色標籤及原始出處連結 |
| 📚 **指引文件庫** | 161 份官方 EDB 指引（in-app 瀏覽庫；公開 `guidelines.json` 端點為 152 份全集投影），按類別 → 子類別 → 年份三層分組導覽 |
| 📄 **通告分析** | 貼入 EDB 通告文字，AI 自動識別主題、政策影響及相關知識 |
| ✍️ **知識提煉**（Admin） | 候選事實審核工作流：Pending → Approved → 同步至知識庫 |
| ⚙️ **知識管理**（Admin） | 批量管理、匯出、版本控制 |

## 涵蓋主題

- 💰 **財務 / 採購 / 津貼** — 採購程序、報價門檻、整筆撥款、代課教師津貼
- 👥 **人力資源** — CPD、批假政策、專業操守、調任安排
- 📖 **課程** — PECG 2024、八個 KLA、五種基要學習經歷、STEAM
- 🏃 **校外活動** — 境外活動、戶外活動、全方位學習津貼
- 🧒 **學生事務** — 訓育、反欺凌、SEN 融合教育、出席記錄
- 💻 **資訊科技** — 資訊保安政策、BYOD、數據保安
- 🏫 **通用行政** — 法團校董會、公開資料守則、學校行政手冊

---

## 技術架構

```
Frontend (GitHub Pages)          Backend (Render)
─────────────────────────        ──────────────────────────────
app.html   ← React 18 SPA   ──→  /api/search/channel-a   (語義搜尋)
index.html ← 入口頁               /api/search/channel-b   (Phase 2)
q.html     ← Quick Q&A           /api/search/combined    (Phase 2)
                                  /analyze-circular       (通告分析)
                                  /health
```

### Frontend
- **Single-file React SPA** — `app.html`（React 18 + Babel + Tailwind CSS 2.2，全部 CDN）
- 靜態托管於 GitHub Pages，無需構建工具

### Backend
- **Node.js + TypeScript**，托管於 [Render](https://render.com) 免費 tier
- **Channel A 搜尋**：對 455 條已審核事實做語義搜尋（OpenAI `text-embedding-3-small`）
- **通告分析**：LLM 提取主題、影響角色、政策要點
- 冷啟動約 30 秒（Render 免費 tier idle 15 分鐘後自動關閉）

### 知識管道

**Channel A — 人工審核（主線）**
```
EDB PDF → extract_candidates.py → candidate_queue.json
→ Admin 審核（inline edit）→ role_facts.json → knowledge.json
```

**Channel B — 全 AI（副線，Phase 2）**
```
EDB PDF → ai_extract.py → wiki_index.json（向量索引）
→ /api/search/channel-b → 智能搜尋 UI
```

---

## 知識庫狀態

| 項目 | 數量 |
|------|------|
| Channel A 已審核事實 | **455 條** |
| 指引文件庫（in-app 瀏覽） | **161 份** |
| 來源文件 | **120 份** |
| Channel B 向量索引 | **13,667 chunks**（Supabase pgvector，線上） |

> 註：由 792 條去重整合至 455 條唯一事實（2026-05-16，commit 711f911；可逆日誌 `dev/DEDUP_LOG_2026-05-16.md`）。
> 註：`161` 為 in-app 指引瀏覽庫（總文件基礎，S140 landing-curate +9 + 公積金 +4）；公開 `guidelines.json` API 端點為其全集投影 **152** 份（S140，剔 9 非文件；由 `dev/build_guidelines.py` 生成）。

---

## 文件結構

```
edb-knowledge/
├── app.html                    # K1 知識平台主應用（React SPA）
├── index.html                  # 入口頁
├── q.html                      # Quick Q&A（本地 knowledge.json 搜尋）
├── t-purchase.html             # 採購範本流程
├── role_facts.json             # Channel A 知識庫（公開 API）
├── knowledge.json              # 知識庫副本（供 EDB 通告系統調用）
├── guidelines.json             # 指引文件庫（公開 API）
├── CHANGELOG.md                # 版本歷史
├── backend/                    # Node.js TypeScript 後端
│   ├── src/
│   │   ├── server.ts           # HTTP server + 路由
│   │   ├── api/                # 各端點處理器
│   │   └── lib/                # embeddingClient、knowledgeRepository 等
│   └── package.json
└── dev/
    ├── knowledge/
    │   ├── role_facts.json     # Channel A 事實庫（source of truth）
    │   ├── policy_signals.json # Circular System 政策訊號
    │   └── candidate_queue.json
    ├── vault/                  # PDF 提取腳本
    ├── CODEBASE_CONTEXT.md     # 平台整體架構說明
    ├── CIRCULAR_SYSTEM_INTEGRATION.md  # edb_scraper.py 整合規格
    └── SESSION_HANDOFF.md      # 開發工作日誌
```

---

## 本地開發

### 前端
直接在瀏覽器開啟 `app.html`，或用任何靜態伺服器。

### 後端
```bash
cd backend
cp .env.example .env          # 填入 OPENAI_API_KEY
npm install
npm run dev                   # 啟動於 http://localhost:8787
```

環境變數（`backend/.env`）：
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-nano
PORT=8787
CORS_ORIGIN=https://leonard-wong-git.github.io
KNOWLEDGE_PATH=../../../dev/knowledge/role_facts.json
```

---

## 版本歷史

詳見 [CHANGELOG.md](CHANGELOG.md)

---

## 數據來源

所有事實均來自香港教育局官方文件，包括教育局通告、課程指引、學校行政手冊等 120 份文件。每條事實均附原始文件連結，確保可追溯性。

---

*最後更新：2026-05-16 | K1知識平台 v2.3.0 | 維護：leonard-wong-git*
