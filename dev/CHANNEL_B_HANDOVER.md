# Channel B Sync — 下游接入交接包 (K1 → Circular System)

> 交俾下游 Circular System 工程師 / agent 嘅 self-contained 接入 brief。
> 完整契約見 `dev/CHANNEL_B_SYNC_SPEC.md` **v0.5**（本檔係佢嘅落地摘要）。
> 製作：2026-06-06 (S146)。K1 端點 **已 LIVE**（S145 build + live smoke PASS）。
>
> ⚠️ **K1 = pull-only / server 端。下游 consumer（HTTP client、edb_scraper 接線、Actions cache）係下游 repo 自己 build，K1 絕不掂對方 repo。**

---

## 0. 你需要嘅 3 樣嘢

| # | 料 | 在邊 |
|---|---|---|
| 1 | 本契約（HTTP codes / versioning / rate-limit / endpoints） | 本檔 + `CHANNEL_B_SYNC_SPEC.md` v0.5 |
| 2 | 7-topic enum + content_type enum | 見 §5 |
| 3 | **sync key**（`X-Sync-Key` header 用） | **由 Leonard 經安全途徑另發**（見 §2） |

---

## 1. Base URL + 兩個端點

```
Base: https://edb-knowledge.onrender.com
GET  /api/channel-b/manifest        ← 列全部 chunk 嘅 id/hash/topic（無 text/向量）
POST /api/channel-b/chunks          ← 按 id 批量攞 full chunk（含 text + 向量）
```
> onrender free-tier：冷啟 ~30s → poll 設 timeout + retry；穩態 304 後 warm。

---

## 2. 認證（sync key）

- Header：**`X-Sync-Key: <key>`**，比對 K1 env `CHANNEL_B_SYNC_KEY`（server 用 `timingSafeEqual`）。
- **呢個 key ≠ OpenAI API key、≠ Supabase key。** 係 K1 專為 sync 端點發嘅獨立 read key。
- **下游存做 GitHub Actions secret**（同你自己 `OPENAI_API_KEY` 一樣存法）。
- 回應碼：缺 header = **401**；錯 key = **403**；K1 端 env 未設 = **503**（fail-closed）。
- 支援多 key 輪換（K1 端逗號分隔 env）。

---

## 3. 端點 ① GET /api/channel-b/manifest

**Request**
```
GET /api/channel-b/manifest
X-Sync-Key: <key>
If-None-Match: "<上次 etag>"          # 可選；未變 → 304 headers-only 空 body（勿 parse JSON）
# Query 可選: ?include_statistical=false   ?cursor=<id>&limit=5000
```
**200 回應**（`chunks[]` 按 id 升序）
```json
{
  "contract_version": "1.0",
  "embedding_model": "text-embedding-3-small",
  "embedding_dim": 1536,
  "generated_at": "2026-06-06T...Z",
  "ingest_in_progress": false,
  "count": 11596,
  "manifest_hash": "<涵蓋 contract_version + embedding_model + 排序 id-set 嘅穩定 hash>",
  "source_aliases": { "g24": "sag_2025_11" },
  "chunks": [
    { "id": "vault_g36_1c250847ea2532aa", "source_id": "g36", "hash": "1c250847ea2532aa", "topic": "curriculum", "content_type": "vault_extract" }
  ],
  "next_cursor": null
}
```
- `manifest_hash` / `ETag` 涵蓋 version+model+id-set → K1 日後換 embedding model 或加/改源，hash 必變 → 你下次 poll 會偵測到 → 觸發 re-sync。
- `ingest_in_progress`：v1 永遠 `false`（一致性靠你嘅 delete-safety，見 §6）。
- `source_aliases`：同文件不同 source_id 嘅對照，俾你 dedup。

---

## 4. 端點 ② POST /api/channel-b/chunks

**Request**
```
POST /api/channel-b/chunks
X-Sync-Key: <key>
Content-Type: application/json
{ "ids": ["vault_g36_...", "..."], "include_embedding": true }   # 單批上限 150 ids
```
**200 回應**
```json
{
  "contract_version": "1.0",
  "embedding_model": "text-embedding-3-small",
  "chunks": [
    {
      "id": "vault_g36_xxx", "hash": "xxx", "source_id": "g36",
      "title": "...", "url": "https://www.edb.gov.hk/...",
      "topic": "curriculum", "content_type": "vault_extract", "fact_type": "policy",
      "role": null, "school_level": null, "reference_year": null,
      "text": "=== Page 1 ===...",
      "embedding": "[0.00757,-0.00092,...]"
    }
  ]
}
```
- `role`/`school_level`/`reference_year` **一律出現、值可為顯式 `null`**（唔使估）。
- `text` 保留 `=== Page N ===` 頁標記（無預解析 `page` 欄，你自行 parse）。
- 缺 id（fetch 時已不存在）→ 回應只含尚存者；**當 pending-add 略過，切勿 tombstone**。
- `include_embedding:false` → 慳頻寬，俾自家重嵌嘅 consumer。

---

## 5. Enum（advisory，非 DB-enforced — 勿 hard-reject 未知值）

- **topic（7）**：`finance` · `hr` · `curriculum` · `activity` · `student` · `it` · `general`
- **content_type（4）**：`vault_extract` · `approved_fact` · `stat_fact` · `guideline`
- **fact_type（4）**：`policy` · `approved_policy` · `statistical` · `guideline_reference`

---

## 6. Embedding invariant（硬規則）

- 向量 = OpenAI **`text-embedding-3-small`（1536 維）**。**你 query 端必須用同一 model 嵌 query**，否則相似度全錯。
- 格式 = **JSON 字串** `"[f,f,…]"`（pgvector 文字序列化、逗號分隔、可能科學記數）→ **你要 parse 個 string**，非 number array。
- **已 L2-normalized**（‖v‖₂≈1.0）→ cosine 可當已正規化。
- `embedding` 可為 `null` → 遇 null **跳過該 chunk 之向量索引**（或退 text-only），勿當解析失敗。

---

## 7. HTTP 契約碼

| 情況 | code | body |
|---|---|---|
| 成功 | 200 | 見 §3/§4 |
| manifest 未變 | 304 | headers-only、空 body（勿 parse） |
| body 壞 / `ids` 非陣列 | 400 | `{error}` |
| `ids` 超上限 | 400 | `{error, max_ids:150}`（不靜默截斷） |
| 缺 sync key | 401 | `{error}` |
| 錯 sync key | 403 | `{error}` |
| 超限流 | 429 | `{error, retry_after_sec}` + `Retry-After` header |
| key env 未設 | 503 | `{error:"sync disabled"}`（fail-closed） |
| upstream Supabase 故障 | 502/503 | `{error}`（retry 後仍失敗先回） |

---

## 8. 限流 + Bootstrap pacing

- **60 req/min + 每日 chunk/bytes 預算 ≈ 3× 全庫拉取量**（防 exfil）。
- **Bootstrap**：全量現約 **11,596 chunks ÷ 150/批 ≈ 77 批**，60/min 下 ≈ **1.3 分鐘**跑完、佔每日預算約 1/3。
- 你 3×/日 cron + 手動 → 唔會掂頂。
- ⚠️ **corpus 仲會增長**（K1 補入庫進行中）。Count 由 manifest live 回；以 manifest 為準，**勿 hardcode 11,596**。manifest_hash 一變 = 下次 poll 自動帶出 delta。

---

## 9. Delta 同步演算法（你 build；K1 不實作）

```
# Bootstrap
m = GET /manifest;  fetch_all(m.chunks ids, batch 150) → 建本地 index

# 穩態（每 poll；帶 If-None-Match）
m = GET /manifest
if 304: return
if m.ingest_in_progress: return                       # K1 寫入中，跳本輪（尤跳 deletes）
remote = {c.id};  local = {本地 id}
adds = remote - local;  deletes = local - remote
# delete-safety：整源消失 = 疑似 mid-ingest 窗口 → re-poll 確認、連續兩 poll 都缺先 tombstone
for batch in chunk(adds, 150): POST /chunks{ids:batch, include_embedding:true} → upsert
apply_confirmed_deletes()
```
- **冪等**；內容修改自動處理（舊 id∈deletes + 新 id∈adds，因 re-ingest re-chunk 會令整源 id 翻新）。
- delete-safety 對你（cron 隔數小時）= 一致性窗口更闊、更安全。

---

## 10. 一致性 / 邊界

- manifest 可能 server-side cache（TTL 30–60s，stale ≤TTL）；fetch 讀 live。manifest 列嘅 id 喺 fetch 時若缺 = pending-add 跳過，**勿 tombstone**，下 poll 補。
- `57014`（Supabase statement-timeout）：manifest 全表掃比 search RPC timeout profile 更差 → 你 poll 設自己 retry + timeout。
- onrender 冷啟 ~30s → timeout + retry。

---

*K1 端負責人：Leonard。契約 SSOT = `dev/CHANNEL_B_SYNC_SPEC.md` v0.5。本 brief 有疑問以 spec 為準；spec 與 live 端點行為衝突請即回報 K1。*
