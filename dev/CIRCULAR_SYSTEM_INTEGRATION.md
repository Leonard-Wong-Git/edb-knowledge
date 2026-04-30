# Circular System → K1 知識平台 整合規格

**版本**: 1.0  
**建立**: 2026-04-30  
**用途**: 告知 Circular System (`edb_scraper.py`) 如何正確寫入政策訊號，供 K1 知識平台讀取及處理。

---

## 概覽

當 EDB Circular 被識別為**知識相關政策文件**時，`edb_scraper.py` 須靜默將訊號寫入 K1 repo 的 `dev/knowledge/policy_signals.json`。K1 管理員或自動化腳本 (`process_signals.py`) 隨後讀取此訊號，決定是否下載 PDF 並提取 Channel A 候選事實。

```
edb_scraper.py
  └── _apply_post_analysis_review()
        └── _write_policy_signal()    ← 本文件描述此函數
              └── dev/knowledge/policy_signals.json   (K1 repo)
```

---

## 檔案位置

| 路徑 | 說明 |
|------|------|
| `dev/knowledge/policy_signals.json` | 訊號儲存檔（K1 repo） |
| `dev/knowledge/source_registry.json` | 已處理來源登記（用於查重） |

> **K1 repo 路徑**（假設 edb_scraper.py 與 K1 repo 並列）：  
> `../Claude-edb-knowledge/dev/knowledge/policy_signals.json`  
> 實際路徑視 Circular System 安裝位置而定，應設為可配置常數。

---

## 觸發條件

訊號須在**同時符合以下兩項**時才觸發（`trigger_mode: "strong"`）：

### 條件 1 — 標題關鍵字（任一）
```python
TITLE_KEYWORDS = [
    "架構",
    "課程框架",
    "學習宗旨",
    "指引（",       # 例如「指引（2026）」「指引（小學）」
    "指引(",        # 半形括號變體
]
```

### 條件 2 — AI 主題分析
```python
AI_TOPICS_REQUIRED = ["curriculum"]
```
`ai_topics` 列表（由 Circular System 現有 AI 分析步驟返回）須包含 `"curriculum"`。

### 觸發判斷
```python
def _should_write_signal(title: str, ai_topics: list[str]) -> tuple[bool, list, list]:
    """
    Returns: (should_trigger, title_keywords_matched, ai_topics_matched)
    """
    matched_title_kw = [kw for kw in TITLE_KEYWORDS if kw in title]
    matched_ai_topics = [t for t in AI_TOPICS_REQUIRED if t in ai_topics]
    
    should_trigger = bool(matched_title_kw) and bool(matched_ai_topics)
    return should_trigger, matched_title_kw, matched_ai_topics
```

---

## `_write_policy_signal()` 完整實現

```python
import json
import os
from datetime import date
from pathlib import Path


# ── 配置 ──────────────────────────────────────────────────────────────────────
# 相對於 edb_scraper.py 的 K1 policy_signals.json 路徑
# 請根據實際部署位置調整
K1_SIGNALS_PATH = Path(os.environ.get(
    "K1_SIGNALS_PATH",
    "../Claude-edb-knowledge/dev/knowledge/policy_signals.json"
))


def _make_signal_id(circular_id: str) -> str:
    """
    將 circular_id 轉為 signal_id。
    例如：
      "EDBC002/2026" → "sig_edbc002_2026"
      "EDBA005/2025" → "sig_edba005_2025"
    """
    # 移除斜線，轉小寫，加前綴
    cleaned = circular_id.replace("/", "_").lower()
    return f"sig_{cleaned}"


def _make_url(circular_id: str) -> str:
    """
    從 circular_id 推導 PDF URL。
    EDBC002/2026 → EDBC26002C.pdf
    格式：EDB{TYPE}{YY}{NNN}C.pdf
    """
    # 解析格式 "EDBC002/2026" → type="C", num="002", year="2026"
    import re
    m = re.match(r'EDB([A-Z]+)(\d+)/(\d{4})', circular_id)
    if not m:
        return ""
    ctype, num, year = m.group(1), m.group(2), m.group(3)
    yy = year[2:]  # "2026" → "26"
    filename = f"EDB{ctype}{yy}{num}C.pdf"
    return f"https://applications.edb.gov.hk/circular/upload/EDB{ctype}/{filename}"


def _write_policy_signal(
    circular_id: str,
    title: str,
    url: str,                       # 若已知則直接傳入；否則傳 "" 由函數推導
    ai_topics: list[str],
    title_keywords_matched: list[str],
    signal_date: str = None,        # ISO format YYYY-MM-DD；None → 今日
) -> bool:
    """
    在 K1 policy_signals.json 中寫入一條新訊號。

    Returns:
        True  — 訊號成功寫入
        False — 已有相同 signal_id（跳過，非錯誤）
    
    Raises:
        IOError — signals 檔案無法讀寫
    """
    signal_id = _make_signal_id(circular_id)
    resolved_url = url or _make_url(circular_id)
    resolved_date = signal_date or date.today().isoformat()

    # ── 讀取現有 signals ──
    signals_path = K1_SIGNALS_PATH
    if signals_path.exists():
        with open(signals_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # 初始化空結構（不應發生，但防禦性處理）
        data = {"_meta": {}, "signals": []}

    # ── 查重：同一 signal_id 只寫一次 ──
    existing_ids = {s["signal_id"] for s in data.get("signals", [])}
    if signal_id in existing_ids:
        print(f"[policy_signal] SKIP duplicate: {signal_id}")
        return False

    # ── 構建訊號物件 ──
    signal = {
        "signal_id": signal_id,
        "circular_id": circular_id,
        "title": title,
        "url": resolved_url,
        "signal_date": resolved_date,
        "trigger_reason": {
            "title_keywords_matched": title_keywords_matched,
            "ai_topics_matched": [t for t in ai_topics if t in ["curriculum"]],
        },
        "status": "pending_review",
    }

    # ── 寫入 ──
    data["signals"].append(signal)
    data["_meta"]["updated"] = date.today().isoformat()

    with open(signals_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[policy_signal] WRITTEN: {signal_id} ({circular_id}) status=pending_review")
    return True
```

---

## 呼叫點：整合至 `_apply_post_analysis_review()`

在現有 `_apply_post_analysis_review()` 函數**末段**加入以下邏輯：

```python
def _apply_post_analysis_review(self, circular_id, title, ai_topics, url="", ...):
    # ... 現有邏輯 ...

    # ── 末段：K1 政策訊號靜默寫入 ──
    should_trigger, matched_kw, matched_topics = _should_write_signal(title, ai_topics)
    if should_trigger:
        try:
            _write_policy_signal(
                circular_id=circular_id,
                title=title,
                url=url,
                ai_topics=ai_topics,
                title_keywords_matched=matched_kw,
            )
        except Exception as e:
            # 靜默失敗：不中斷主流程
            print(f"[policy_signal] ERROR (non-fatal): {e}")
```

> **重要**：`_write_policy_signal()` 失敗須靜默（catch-all），不可中斷 edb_scraper.py 主流程。

---

## 訊號物件完整 Schema

```json
{
  "signal_id": "sig_edbc002_2026",
  "circular_id": "EDBC002/2026",
  "title": "教育局通告第2/2026號 — 地理科（中一至中三）課程框架",
  "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26002C.pdf",
  "signal_date": "2026-04-17",
  "trigger_reason": {
    "title_keywords_matched": ["課程框架"],
    "ai_topics_matched": ["curriculum"]
  },
  "status": "pending_review"
}
```

### 欄位說明

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `signal_id` | string | ✅ | 唯一識別碼，格式 `sig_{circular_id_normalized}` |
| `circular_id` | string | ✅ | 原始通告編號，如 `"EDBC002/2026"` |
| `title` | string | ✅ | 通告完整標題（中文） |
| `url` | string | ✅ | PDF 直鏈，格式見下方 |
| `signal_date` | string | ✅ | 訊號產生日期，ISO 8601 (`YYYY-MM-DD`) |
| `trigger_reason` | object | ✅ | 觸發原因，含 `title_keywords_matched` 及 `ai_topics_matched` 陣列 |
| `status` | string | ✅ | 初始值必須為 `"pending_review"`（由 K1 端更新，scraper 不修改） |

### `status` 值域（K1 端維護，scraper 只寫 `pending_review`）

| 值 | 說明 |
|----|------|
| `pending_review` | **scraper 寫入時的唯一初始值** |
| `auto_processed` | K1 `process_signals.py` 已自動處理 |
| `reviewed` | 管理員人手確認完成 |
| `skipped_duplicate` | source_id 已存在 source_registry |
| `download_failed` | PDF 下載失敗 |
| `extract_failed` | pdftotext 提取失敗 |

---

## URL 格式規則

```
https://applications.edb.gov.hk/circular/upload/EDB{TYPE}/EDB{TYPE}{YY}{NNN}C.pdf
```

| 變數 | 說明 | 例子 |
|------|------|------|
| `{TYPE}` | 通告類別字母 | `C`（EDBC）、`A`（EDBA）等 |
| `{YY}` | 年份後兩位 | `26`（2026） |
| `{NNN}` | 序號（零填充至3位） | `002` |

**示例**：
- `EDBC002/2026` → `EDBC26002C.pdf` → `https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26002C.pdf`
- `EDBC005/2026` → `EDBC26005C.pdf` → `https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26005C.pdf`

---

## 查重邏輯

- 以 `signal_id` 為唯一鍵
- 若 `signal_id` 已存在 `signals` 陣列中，跳過寫入（返回 `False`，不拋出異常）
- **不以 `circular_id` 或 `url` 為鍵**，避免同一通告被不同時間重新觸發時造成混淆

---

## 非功能性要求

1. **靜默優先**：任何寫入失敗不得中斷 edb_scraper.py 主流程
2. **原子性**：讀取→修改→寫入為同步操作；不需文件鎖（假設單進程）
3. **編碼**：JSON 必須 `ensure_ascii=False`，保留繁體中文
4. **縮排**：JSON indent=2，與現有 policy_signals.json 一致
5. **日期格式**：所有日期欄位為 ISO 8601 字串 `YYYY-MM-DD`

---

## 測試驗證

完成整合後，執行以下驗證：

```bash
# 在 K1 repo 根目錄
cd ~/Downloads/Claude-edb-knowledge

# 確認寫入成功
python3 -c "
import json
with open('dev/knowledge/policy_signals.json') as f:
    d = json.load(f)
new_signals = [s for s in d['signals'] if s['status'] == 'pending_review']
print(f'pending_review 訊號數: {len(new_signals)}')
for s in new_signals:
    print(f'  {s[\"signal_id\"]} — {s[\"title\"][:40]}')
"
```

預期輸出：每條新寫入訊號列出 `signal_id` 及標題前 40 字。

---

## 相關檔案（K1 repo）

| 檔案 | 說明 |
|------|------|
| `dev/knowledge/policy_signals.json` | 訊號儲存（本文件描述的寫入目標） |
| `dev/knowledge/source_registry.json` | 已處理 PDF 來源登記 |
| `dev/knowledge/candidate_queue.json` | Channel A 候選隊列 |
| `dev/CODEBASE_CONTEXT.md` | K1 平台整體架構說明 |

---

*最後更新：2026-04-30 | K1知識平台 v1.6.0*
