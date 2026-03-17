# K1 知識庫接口規格（對外獨立版）

**文件版本：** 1.0.0
**建立日期：** 2026-03-15
**維護方：** EDB Circular AI Analysis System
**用途：** 供 K1 知識庫項目開發者參考，定義雙方接口契約
**獨立性聲明：** 本文件完全獨立，K1 項目無需閱讀或接觸 EDB 項目的任何其他文件、代碼或配置。

---

## 1. 整合目標

K1 知識庫項目的輸出，將被 EDB Circular AI Analysis System 在分析通告時注入 LLM prompt，以提升以下精準度：

- 各角色的責任判斷（「這條通告校長需要親自處理嗎？」）
- 採購 / 財務合規建議（「行政主任需要做幾份報價？」）
- 截止日期緊急程度評估（「這個截止對教師而言是否關鍵？」）
- 角色相關行動清單生成（「科主任應該採取哪幾步？」）

---

## 2. 接口契約：輸出文件規格

### 2.1 輸出文件

K1 項目需要輸出**一個 JSON 文件**：

```
輸出文件名：  role_facts.json
文件說明：    角色 × 主題的知識事實庫
Token 預算：  注入 LLM 時每次分析取用 ≤ 600 字（中文字符）
```

### 2.2 JSON Schema

```json
{
  "<topic_id>": {
    "_label": "人類可讀的主題名稱",
    "_keywords_zh": ["觸發這個主題的中文關鍵詞列表"],
    "all_roles": [
      "適用所有角色的事實（字串，每條 ≤ 80 字）"
    ],
    "<role_id>": [
      "只適用此角色的事實（字串，每條 ≤ 80 字）"
    ]
  }
}
```

### 2.3 完整範例

```json
{
  "finance": {
    "_label": "財務 / 採購 / 津貼",
    "_keywords_zh": ["採購", "財務", "津貼", "撥款", "資助", "金額"],
    "all_roles": [
      "採購門檻（資助學校）：< HK$2,000 直購免報價；$2,000–$20,000 最少 3 份書面報價；$20,000–$50,000 最少 5 份；> $50,000 公開招標",
      "廉潔約章：所有 > HK$2,000 採購須要求供應商簽署廉潔約章（ICAC 要求）"
    ],
    "eo_admin": [
      "行政主任負責採購程序合規，須保存完整報價記錄（最少 7 年）"
    ],
    "principal": [
      "整筆撥款（LSG）校長須確保各項撥款按核准用途使用，不可挪用"
    ],
    "supplier": [
      "學校採購需競爭性報價，供應商不可向教職員提供任何回扣或利益"
    ]
  },
  "hr": {
    "_label": "人力資源 / 教師 / 職員",
    "_keywords_zh": ["教師", "CPD", "培訓", "聘任", "薪酬", "專業發展"],
    "all_roles": [
      "教師持續專業發展（CPD）：建議每學年最少 150 小時，其中包含結構性培訓活動"
    ],
    "teacher": [
      "CPD 記錄須由教師自行保存，學校要求時須呈交",
      "代課教師：正規教師連續缺席超過 5 天可申請代課教師津貼"
    ]
  }
}
```

---

## 3. 固定清單（雙方必須一致）

### 3.1 Topic ID 清單

| Topic ID | 中文說明 | 典型觸發關鍵詞 |
|----------|----------|----------------|
| `finance` | 財務 / 採購 / 津貼 / 撥款 | 採購、財務、津貼、撥款、資助、金額 |
| `hr` | 人力資源 / 教師 / 職員 | 教師、CPD、培訓、聘任、薪酬 |
| `curriculum` | 課程 / 學習 / 評估 | 課程、科目、評估、學習、教學、課時 |
| `activity` | 校外活動 / 比賽 / 考察 | 活動、考察、旅行、比賽、境外 |
| `student` | 學生事務 / 安全 / 健康 | 學生、意外、安全、健康、SEN、欺凌 |
| `it` | 資訊科技 / 設備 / 網絡 | 資訊科技、電腦、設備、IT、AI |
| `general` | 通用（無特定主題匹配時） | （不設關鍵詞，作後備） |

> ⚠️ **約束：** Topic ID 必須完全吻合上表英文字串。如需新增 topic，雙方須協商後更新本文件版本。

### 3.2 Role ID 清單

| Role ID | 中文說明 | 備注 |
|---------|----------|------|
| `all_roles` | 所有角色適用 | 特殊保留 key，必須使用 |
| `principal` | 校長 | |
| `vice_principal` | 副校長 | |
| `department_head` | 科主任 | |
| `teacher` | 教師 | |
| `eo_admin` | 行政主任 | |
| `supplier` | 供應商 | |

> ⚠️ **約束：** Role ID 必須完全吻合上表英文字串，包括下劃線格式。

---

## 4. 事實條目撰寫規範

### 4.1 格式要求

| 項目 | 要求 |
|------|------|
| 每條字數 | ≤ 80 中文字（含標點） |
| 每個 role key 條數 | ≤ 5 條（建議 2–3 條） |
| `all_roles` 條數 | ≤ 5 條 |
| 語言 | 繁體中文 |
| 數字格式 | 金額用 `HK$X,XXX`；時間用阿拉伯數字 + 中文單位 |

### 4.2 內容質量標準

✅ **好的事實條目：**
```
採購門檻：< HK$2,000 直購；$2,000–$20,000 最少 3 份書面報價；> $20,000 招標
```
- 具體數字、可操作、來源可核實

❌ **不好的條目：**
```
校長需要注意財務問題並確保學校遵守規定
```
- 過於模糊，無法提供具體指引

### 4.3 資料來源優先級

1. 教育局官方 PDF 文件（最高可信度）
2. 教育局官方網頁內容
3. 廉政公署採購指引
4. 香港法例及條例
5. 其他政府部門官方資料

> **必須標記來源：** `_sources` 字段（見第 5 節）可選但建議填寫，以便日後核實。

---

## 5. 完整 Schema 定義（含可選字段）

```json
{
  "_meta": {
    "version": "必填，語義版本號如 1.0.0",
    "created": "必填，YYYY-MM-DD",
    "updated": "選填，YYYY-MM-DD",
    "description": "選填，本文件說明"
  },
  "<topic_id>": {
    "_label": "必填，人類可讀主題名",
    "_keywords_zh": ["必填，至少 3 個觸發關鍵詞"],
    "_sources": [
      {
        "title": "文件標題",
        "url": "https://...",
        "retrieved": "YYYY-MM-DD"
      }
    ],
    "all_roles": ["必填，可為空陣列 []"],
    "<role_id>": ["選填，不需要時可省略此 key"]
  }
}
```

---

## 6. 驗收測試（K1 輸出時可自行驗證）

K1 項目交付前，建議用以下 Python 腳本自我驗證：

```python
import json

VALID_TOPICS = {"finance","hr","curriculum","activity","student","it","general"}
VALID_ROLES  = {"all_roles","principal","vice_principal","department_head",
                "teacher","eo_admin","supplier"}
MAX_FACT_LEN = 80
MAX_FACTS_PER_KEY = 5

def validate(path="role_facts.json"):
    with open(path, encoding="utf-8") as f:
        db = json.load(f)

    errors = []
    for topic_id, topic_data in db.items():
        if topic_id == "_meta":
            continue
        if topic_id not in VALID_TOPICS:
            errors.append(f"Unknown topic: {topic_id}")
        if "_keywords_zh" not in topic_data:
            errors.append(f"{topic_id}: missing _keywords_zh")
        for role_key, facts in topic_data.items():
            if role_key.startswith("_"):
                continue
            if role_key not in VALID_ROLES:
                errors.append(f"{topic_id}.{role_key}: unknown role")
            if not isinstance(facts, list):
                errors.append(f"{topic_id}.{role_key}: must be list")
                continue
            if len(facts) > MAX_FACTS_PER_KEY:
                errors.append(f"{topic_id}.{role_key}: too many facts ({len(facts)} > {MAX_FACTS_PER_KEY})")
            for i, fact in enumerate(facts):
                if len(fact) > MAX_FACT_LEN:
                    errors.append(f"{topic_id}.{role_key}[{i}]: too long ({len(fact)} chars, max {MAX_FACT_LEN})")

    if errors:
        print("❌ Validation FAILED:")
        for e in errors: print(f"  - {e}")
    else:
        print("✅ Validation PASSED")

validate()
```

---

## 7. 交付流程

```
K1 項目                              EDB 項目
─────────────────────────────────    ────────────────────────────
1. 按本文件規格生成 role_facts.json
2. 執行第 6 節驗收腳本 → ✅ PASSED
3. 交付 role_facts.json              4. 替換 dev/knowledge/role_facts.json
                                     5. 下一次 GitHub Actions workflow
                                        自動使用新知識（無需改代碼）
```

**EDB 項目接收方確認清單：**
- [ ] 驗收腳本通過
- [ ] `_meta.version` 版本號已記錄於 SESSION_LOG
- [ ] 舊版 role_facts.json 已備份（git tag 即可）

---

## 8. 版本升級規則

| 變更類型 | Schema 版本號 | 是否需要通知 EDB |
|----------|--------------|-----------------|
| 新增 / 修改事實條目內容 | Patch（1.0.x） | 不需要，直接交付 |
| 新增現有 topic 下的新 role key | Minor（1.x.0） | 建議通知 |
| 新增全新 topic ID | **Minor（1.x.0）** | **必須通知，先更新本文件** |
| 修改 topic ID 或 role ID 名稱 | **Major（x.0.0）** | **必須協商，雙方同步更新** |

> Major 版本變更必須雙方同意後才能實施，避免 EDB 項目 silent break。

---

## 9. 聯絡 / 協商機制

如需新增 topic、修改 role ID、或對本規格有疑問，請更新本文件版本並通知 EDB 項目方，雙方確認後方可實施。

本文件（`K1_KNOWLEDGE_INTERFACE_SPEC.md`）是雙方接口的**唯一真相來源（SSOT）**。

---

*文件結束*
