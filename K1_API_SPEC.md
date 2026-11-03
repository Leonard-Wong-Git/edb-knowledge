# K1 知識庫 — 公開 JSON 端點規格 v3.0.0

> 上次更新：2026-11-03（S243）
> 原供 EDB 通告智能分析系統（EDB-AI-Circular-System）接入；2026-11-03 起只餘 `guidelines.json`。

---

## 1. 架構定位

| 平台 | 職責 |
|------|------|
| **K1 知識庫**（本 repo） | 管理 EDB 指引文件連結；平台搜尋以 EDB 原文（Channel B）作答，附出處 |
| **EDB 通告智能分析系統** | 分析 EDB 通告；如需要，可讀取 `guidelines.json` 取得相關指引文件連結 |

> **S243（2026-11-03）**：舊「事實庫」`knowledge.json`（455 條已核實事實，2026-06-05 起凍結）已退役並刪除。平台不再提供無出處的事實；所有答案以附網址及頁碼的 EDB 原文為依據。

---

## 2. 公開 API 端點

| 端點 | URL |
|------|-----|
| 指引文件連結庫 | `https://policychecker.wongfu.net/guidelines.json` |

- 靜態 JSON，由 GitHub Pages 提供；K1 更新並 push 後自動更新
- 建議每次使用時 fetch 最新版，不應本地快取超過 1 天

---

## 3. guidelines.json 格式（全集投影，現為 151 份）

> S140（2026-06-03）：公開端點由 39 精選子集擴為 app 內庫 registry 全集投影（當時 **152** 份）（剔 7 統計表 / 1 申請表 / 1 壞連結；含 landing-curate +9 KLA/課程指引全文 PDF + 公積金覆蓋 +4 HR 文件）。schema 不變；篩選方法（按 topic 取 `guidelines[topic]`）不變，只係每桶文件數增加（curriculum 桶 ~25→132、hr 桶 2→6）。建議 Circular System 注入時對大桶通告做數量上限或相關性排序。
>
> **現況（2026-09-14 實測）：`_meta.count` = 151，in-app `GUIDELINES_REGISTRY` = 170。**

```json
{
  "_meta": {
    "version": "2.5.0",
    "updated": "2026-06-03",
    "count": 151
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

## 4. Topic ID 對照表

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

## 5. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v3.0.0 | 2026-11-03 | **S243：`knowledge.json`（Channel A，455 條事實）退役並刪除**；下游通告系統已不使用（Leonard 確認）。本規格只餘 `guidelines.json`。 |
| v1.3.1 | 2026-04-11 | 對齊 `knowledge.json` / `guidelines.json` 當前公開版本與日期，確認 split-role 公開 schema 仍為 `subject_head` + `panel_chair` |
| v1.3.0 | 2026-04-08 | `department_head` 拆分為 `subject_head`（科主任）+ `panel_chair`（統籌主任）；更新 spec 以反映實際 schema |
| v1.2.2 | 2026-04-04 | 初始公開版本；`department_head` 為合併角色 |


---

*K1 知識庫 — 最後更新：2026-11-03*
