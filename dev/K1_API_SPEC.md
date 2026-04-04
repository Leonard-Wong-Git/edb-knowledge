# K1 知識庫 — EDB Circular System 接口規格

> 本文件供 EDB 通告智能分析系統（EDB-AI-Circular-System）接入 K1 知識庫時參考。

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

---

## 3. knowledge.json 格式

```json
{
  "_meta": {
    "version": "1.2.2",
    "count": 102,
    "topics": ["finance","hr","curriculum","activity","student","it","general"]
  },
  "finance": [
    {
      "id": "f01",
      "fact": "採購金額 $1,000 以下：口頭報價，不需書面。",
      "roles": {
        "all_roles": false,
        "principal": true,
        "vice_principal": false,
        "department_head": true,
        "teacher": false,
        "eo_admin": true,
        "supplier": false
      },
      "sources": [
        {
          "title": "資助學校採購程序指引（2024）",
          "url": "https://..."
        }
      ],
      "review_state": "approved"
    }
  ]
}
```

### 篩選方法

1. **按 topic 篩選**：用通告的 `topics` 陣列，從對應的 JSON key 取出事實
2. **按角色篩選**：Circular System 使用 `department_head` — 取出 `roles.department_head === true` 或 `roles.all_roles === true` 的事實
3. **只用 approved**：過濾 `review_state === "approved"` 的事實

```javascript
// 範例：取出 finance 主題中 department_head 適用的事實
const facts = knowledge["finance"]
  .filter(f => f.review_state === "approved")
  .filter(f => f.roles.department_head || f.roles.all_roles);
```

---

## 4. guidelines.json 格式

```json
{
  "_meta": {
    "version": "1.2.2",
    "updated": "2026-04-04",
    "count": 39,
    "description": "EDB 指引文件連結庫"
  },
  "finance": [
    {
      "id": "g01",
      "title": "資助學校採購程序指引（2025年10月更新）",
      "titleShort": "採購程序指引",
      "url": "https://...",
      "year": "2025",
      "format": "PDF"
    }
  ]
}
```

### 篩選方法

按通告的 `topics` 陣列，從對應的 JSON key 取出文件連結清單：

```javascript
// 範例：取出通告相關 topics 的所有指引文件連結
const relatedDocs = circular.topics
  .flatMap(topic => guidelines[topic] ?? []);
```

---

## 5. Topic ID 對照表

| Topic ID | 中文 | 說明 |
|----------|------|------|
| `finance` | 財務 / 採購 | 採購、報價、津貼、撥款 |
| `hr` | 人力資源 | CPD、代課、請假、操守 |
| `curriculum` | 課程 | KLA、PECG、評估、STEAM |
| `activity` | 校外活動 | 境外、戶外、全方位學習 |
| `student` | 學生事務 | 訓育、SEN、出席、反欺凌 |
| `it` | 資訊科技 | 資訊保安、BYOD、數據 |
| `general` | 通用行政 | 法團校董、公開資料、行政手冊 |

---

## 6. 角色對照（K1 vs Circular System）

| K1 dashboard 顯示 | knowledge.json 鍵值 | Circular System 對應角色 |
|-------------------|---------------------|--------------------------|
| 校長 | `principal` | `principal` |
| 副校長 | `vice_principal` | `vice_principal` |
| 學位主任 + 科主任（合併） | `department_head` | `department_head` |
| 教師 | `teacher` | `teacher` |
| 行政主任 | `eo_admin` | `eo_admin` |
| 全校適用 | `all_roles` | （始終包含） |

> K1 dashboard UI 使用 `panel_chair`（學位主任）/ `subject_head`（科主任），但 **knowledge.json 已合併為 `department_head`**，與 Circular System 一致。

---

## 7. 建議整合流程

```
Circular System 收到通告
  ↓
偵測 topics（例如 ["finance", "curriculum"]）
  ↓
Fetch https://…/edb-knowledge/knowledge.json
  ↓
篩選：topics × role=department_head × approved
  ↓
Fetch https://…/edb-knowledge/guidelines.json
  ↓
篩選：topics 對應的指引文件連結
  ↓
將事實 + 文件連結 注入通告分析 prompt
```

---

*K1 知識庫版本：v1.2.2 | 最後更新：2026-04-04*
