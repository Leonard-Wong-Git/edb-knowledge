# K1 知識庫 — EDB Circular System 接口規格 v2.3.0

> 本文件供 EDB 通告智能分析系統（EDB-AI-Circular-System）接入 K1 知識庫時參考。
> 上次更新：2026-05-16
> 對齊 knowledge.json v2.3.0

---

## 1. 架構定位

| 平台 | 職責 |
|------|------|
| **K1 知識庫**（本 repo） | 管理、核實 EDB 政策事實及指引文件連結；提供靜態 JSON API |
| **EDB 通告智能分析系統** | 分析 EDB 通告；向 K1 取得相關事實及指引文件，豐富分析內容 |

K1 **不分析通告**。Circular System **不儲存事實**。兩者以 JSON API 解耦。

---

## 2. 公開 API 端點

| 端點 | URL |
|------|-----|
| 事實庫 | `https://leonard-wong-git.github.io/edb-knowledge/knowledge.json` |
| 指引文件連結庫 | `https://leonard-wong-git.github.io/edb-knowledge/guidelines.json` |

- 兩個端點均為靜態 JSON，由 GitHub Pages 提供
- 每次 K1 更新知識並 push，端點自動更新
- 建議：Circular System 每次分析時 fetch 最新版，不應本地快取超過 1 天

> ⚠️ **凍結公告（2026-06-05，K1 內部 Q4 Phase 1）**：`knowledge.json`（事實庫）已**凍結於現行 455 條 approved facts**、暫停加入新事實；**schema 完全不變、端點繼續正常供應**，下游現階段**無需任何改動**。日後若調整事實供料方式，K1 會另行通知並同步更新本規格。`guidelines.json`（指引文件連結庫）**不在凍結範圍、繼續更新**。

---

## 3. knowledge.json 實際格式（v2.3.0）

```json
{
  "_meta": {
    "version": "2.3.0",
    "created": "2026-04-04",
    "updated": "2026-05-16",
    "description": "...（455 條已核實事實；2026-05-16 dedup：792 → 455）...",
    "stats": { "facts": 455, "chunks": 15364, "sources": 120, "guidelines": 158, "topics": 7 }
  },
  "finance": {
    "_label": "財務 / 採購 / 津貼 / 撥款",
    "_keywords_zh": ["採購", "財務", ...],
    "all_roles":     ["全體適用的事實字串", ...],
    "principal":     ["校長適用的事實字串", ...],
    "vice_principal":["副校長適用的事實字串", ...],
    "subject_head":  ["科主任適用的事實字串", ...],
    "panel_chair":   ["[統籌主任類] 適用的事實字串", ...],
    "teacher":       ["教師適用的事實字串", ...],
    "eo_admin":      ["EO適用的事實字串", ...],
    "supplier":      ["供應商適用的事實字串", ...]
  },
  "hr": { ... },
  "curriculum": { ... },
  "activity": { ... },
  "student": { ... },
  "it": { ... },
  "general": { ... }
}
```

### ⚠️ 重要：格式說明

- 每個 role bucket 是**字串陣列**（plain string array），不是物件陣列
- 所有事實已預先過濾為 `approved` 狀態，**無需再過濾 `review_state`**
- 無 `id`、`roles{}`、`review_state` 等欄位（舊版 spec 描述有誤，以本文件為準）

---

## 4. 角色 bucket 定義

| Bucket | 中文 | 說明 |
|--------|------|------|
| `all_roles` | 全體適用 | 全校所有角色均須遵守的事實（如法律要求） |
| `principal` | 校長 | 校長職責 |
| `vice_principal` | 副校長 | 副校長職責 |
| `subject_head` | 科主任 | **科/部門層面**的主任職責（課程、評估、科組管理） |
| `panel_chair` | 統籌主任 | **全校統籌層面**的主任職責（課程統籌主任、活動主任、訓導主任、特教統籌主任、IT統籌主任等）；事實字串常帶有 `[具體角色]` 標注 |
| `teacher` | 教師 | 教師職責 |
| `eo_admin` | EO | 行政主任職責 |
| `supplier` | 供應商 | 供應商要求（僅 finance topic） |

### `subject_head` vs `panel_chair` 區別

```
subject_head（科主任）
  → 管理本科/科組的主任
  → 例：科主任規劃本科課程、帶領共同備課

panel_chair（統籌主任）
  → 負責全校某一範疇的統籌主任
  → 例：[課程統籌主任]、[活動主任]、[訓導及輔導主任]、
         [特殊教育統籌主任]、[資訊科技統籌主任]
  → 事實字串以 [具體角色] 標注，方便 LLM 理解適用範圍
```

---

## 5. 篩選方法

### 同時取用 `subject_head` + `panel_chair`（推薦）

```python
# 取出通告相關 topics 中所有主任層面的事實
facts = []
for topic in detected_topics:
    topic_data = knowledge.get(topic, {})
    facts += topic_data.get("all_roles", [])
    facts += topic_data.get("subject_head", [])
    facts += topic_data.get("panel_chair", [])
```

### 只取特定角色（按需選用）

```python
# 只取科主任相關（如通告明確針對科主任）
facts = knowledge[topic].get("subject_head", []) + knowledge[topic].get("all_roles", [])

# 只取統籌主任相關（如通告針對行政架構）
facts = knowledge[topic].get("panel_chair", []) + knowledge[topic].get("all_roles", [])
```

---

## 6. guidelines.json 格式（S140：39 → 152 全集投影）

> S140（2026-06-03）：公開端點由 39 精選子集擴為 app 內庫 registry 全集投影 **152** 份（剔 7 統計表 / 1 申請表 / 1 壞連結；含 landing-curate +9 KLA/課程指引全文 PDF + 公積金覆蓋 +4 HR 文件）。schema 不變；篩選方法（按 topic 取 `guidelines[topic]`）不變，只係每桶文件數增加（curriculum 桶 ~25→132、hr 桶 2→6）。建議 Circular System 注入時對大桶通告做數量上限或相關性排序。

```json
{
  "_meta": {
    "version": "2.5.0",
    "updated": "2026-06-03",
    "count": 152
  },
  "finance": [
    {
      "id": "g01",
      "title": "資助學校採購程序指引（2025年10月更新）",
      "titleShort": "採購程序指引",
      "url": "https://www.edb.gov.hk/...",
      "year": "2025",
      "format": "PDF"
    }
  ],
  ...
}
```

### 篩選方法

```python
# 取出通告相關 topics 的所有指引文件連結
docs = []
for topic in detected_topics:
    docs += guidelines.get(topic, [])
```

---

## 7. Topic ID 對照表

| Topic ID | 中文 | 涵蓋範疇 |
|----------|------|---------|
| `finance` | 財務 / 採購 | 採購門檻、報價、津貼、撥款、LSG |
| `hr` | 人力資源 | CPD、代課、SEN人手、駐校社工 |
| `curriculum` | 課程 | KLA、PECG、評估、STEAM、人文科 |
| `activity` | 校外活動 | 境外活動、全方位學習、風險評估 |
| `student` | 學生事務 | 訓育、SEN支援、出席、反欺凌 |
| `it` | 資訊科技 | 資訊保安、BYOD、IT設備、數據私隱 |
| `general` | 通用行政 | 法團校董會、公開資料守則、維修 |

---

## 8. 建議整合流程

```
Circular System 收到通告
       ↓
偵測 topics（例如 ["finance", "curriculum"]）
       ↓
Fetch knowledge.json
       ↓
按 topics 取 subject_head + panel_chair + all_roles 的事實
       ↓
Fetch guidelines.json
       ↓
按 topics 取指引文件連結清單
       ↓
將事實 + 文件連結注入通告分析 prompt
```

---

## 9. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.3.1 | 2026-04-11 | 對齊 `knowledge.json` / `guidelines.json` 當前公開版本與日期，確認 split-role 公開 schema 仍為 `subject_head` + `panel_chair` |
| v1.3.0 | 2026-04-08 | `department_head` 拆分為 `subject_head`（科主任）+ `panel_chair`（統籌主任）；更新 spec 以反映實際 schema |
| v1.2.2 | 2026-04-04 | 初始公開版本；`department_head` 為合併角色 |

---

*K1 知識庫 — 最後更新：2026-05-16*
