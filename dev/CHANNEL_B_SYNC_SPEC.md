# Channel B Incremental-Sync Migration Spec（K1-side）

**版本**: 0.4（§11 全 RESOLVED；下游 consumer 覆文 S145 納入：embedding 路 1 鎖定、manifest +topic/content_type、profile 校正；契約 build-ready，待 endpoint build PLAN）
**建立**: 2026-06-05 · Session S144（Claude）｜**v0.4 更新**: 2026-06-05 · Session S145（Claude，納入下游 Circular System consumer 覆文）
**狀態**: 契約設計稿 — **K1-side 端點未 build**（本 spec 只定契約；endpoint 屬後續 dormant/reversible build task）
**用途**: 定義下游 **Circular System** 由「消費 frozen `knowledge.json`（Channel A @455）」**增量同步（incremental sync）消費 Channel B**（Supabase `wiki_chunks`，現 10,594 chunks）所需嘅 **K1 端契約**。

> ⚠️ **邊界（硬規則）**：本 spec **只描述 K1 端**契約。K1 **絕不 mount／改下游 Circular System repo（AGENTS §A.3）**；下游消費端由 Leonard 喺下游 repo 主導實作。Channel A / `knowledge.json` 維持 **Q4 Phase 1 凍結 @455** 一個字唔郁；亦**不改 Supabase schema、不改 `match_wiki_chunks`、不改 upload pipeline（`cb3_b2_pagecarry_migrate.py`）**。

> 📋 **v0.2 hardening**：v0.1 經獨立對抗審核揪出 2 blocker（非原子 ingest 致誤刪 live 源；版本變更被 304 隱形）+ 多個 major（bulk feed 係 search superset、single-key 無限流、manifest O(N) server scan、embedding/ null 語義未定）。本版逐項收緊；未決者落 §11 開放決策交 Leonard。

---

## 0. 背景與決策鏈

| 階段 | 狀態 | 內容 |
|------|------|------|
| Q4 Phase 1 | ✅ EXECUTED（S143） | 凍結 Channel A：`knowledge.json` 停更 @455、schema 不變、繼續供下游零改變、pipeline dormant 可逆 |
| Q4 Phase 2 — 模型決策 | ✅ LOCKED（S144，Leonard 拍板） | 下游由「食靜態 `knowledge.json`」轉「增量同步 Channel B」；模型 = **Incremental sync（manifest-diff delta feed）** |
| Q4 Phase 2 — 下游 consumer 覆文 | ✅ 收到（S145） | 下游確認 embedding 路 1（`text-embedding-3-small`、零重嵌）；揭真實 profile（ephemeral cron 3×/日 + file-based numpy，非常駐/非 pgvector）；提 3 反問（topic 子集 / 限流 / 向量格式）全納入本版 |
| Q4 Phase 2 — K1 端 build | ⏳ 待 GO 另開 | 實作 §3/§4 兩個唯讀端點 + sync key（additive、reversible；見 §9） |
| Q4 Phase 2 — 下游 build | ⏳ 跨 repo、Leonard 主導 | 下游 file-based 鏡像（.npy + .jsonl）+ numpy cosine + 跨 cron-run 持久化（§5 informational） |

**點解揀 Incremental sync** — **下游真實 profile（S145 覆文校正）= GitHub Actions ephemeral runner、cron 3×/日（HKT 07/13/17）+ 手動、非常駐進程、file-based numpy 鏡像（非 pgvector）**。模型揀法在此 profile 下**仍最優**，惟理由須校正：(1) 下游今對 Channel A 係「每 run 全量重嵌」；Channel B 10,594 chunks 若照舊每 cron run 全量重嵌 = 燒大量 OpenAI 嵌入 + 時間 → **路 1（`include_embedding=true`）令下游零重嵌**、直接食 K1 向量；(2) **ETag/304 + delta**：多數 cron run 只 304（無變）或拉零至小量 delta = 頻寬/compute 最省；(3) 前提 = 下游把 `.npy`/`.jsonl` 鏡像**跨 ephemeral run 持久化**（commit 入 repo / Actions cache，屬下游內部決定）。對比：**export 全量快照 ❌** = 每 cron run 重拉全庫 10–30MB（即使 freshness 已放鬆）；**pure query-time API ⚠️** 每 query 綁 onrender free-tier（冷啟 ~30s + 無 SLA）。**incremental sync ✅✅**。（原 v0.1–v0.3 寫「常駐 + 近乎即時」係 K1 側假設，S145 經下游覆文校正為上述。）

**Provenance 註**：`wiki_chunks` schema 由一次性 service-key 探針讀一行核實（2026-06-05）。**但本 spec 兩個端點設計用 anon key**（與 backend `wikiRepository.ts` 一致、RLS `wiki_chunks_anon_read` SELECT-only 已足）——**K1 query 側不需、亦不應 provision service key**。

---

## 1. 關鍵發現 — delta cursor = content-hash id（零 schema change）

實測 `wiki_chunks`：**無 `created_at`/`updated_at`/`inserted_at`**（三者 order-by 全 HTTP 400 = 不存在）。但：

- `id` = `vault_<source_id>_<hash>`；**`hash = sha256(chunk_text)[:16]`**（截斷 SHA-256 hex，64-bit，**內容衍生、source_id 不入 hash**；見 `cb3_b2_pagecarry_migrate.py`）。
- Upload pipeline 係**逐源 delete-then-insert**（非 in-place update）。

→ chunk 嘅 `id` set 完整編碼 Channel B 狀態：新內容→新 id；移除→id 消失；改內容→舊 id 跌＋新 id 出（自動，因 id=內容雜湊）。**delta = `id` set 嘅 set-diff（manifest-diff），毋須 timestamp / schema change / trigger。**

> ⚠️ **三個必須知嘅 caveat（審核揪出）：**
> 1. **Re-ingest 會 re-chunk 全源** → page 邊界一移，該源**大量 id 一次過翻新**（唔淨係改咗嗰段）。即一次 re-curate `sag_2025_11`（~415 chunks）可令該源**整批 id flip**。所以「delta 一定細／大部分 poll 304」**只在「上次 poll 後無 re-ingest」成立**；delta 上限 = 單源全 chunk 數，batch/刪除邏輯**必須容忍全源級 delta**（見 §4/§5）。
> 2. **同一文件可存在於不同 `source_id`**（例 `學校行政手冊` = `sag_2025_11` ＋ `g24`，0% hash overlap、語義重疊；K1 內部用 `SOURCE_ALIASES` quota 合併）。Bulk feed 會送**兩套** id；下游會收到**語義重複源**。manifest 提供 `source_aliases`（§3）俾下游自行 dedup。
> 3. **64-bit 截斷 hash 理論可碰撞**：10.6K chunks 下全域碰撞機率 ~1e-8 = 可忽略；記錄在案非 blocker。

---

## 2. 契約總覽

K1 新增**兩個唯讀端點**（沿用 backend `node:http` 風格）。**注意：兩端點係 net-new PostgREST 表讀 path**（anon key、`apikey`+`Authorization: Bearer` header，與 RPC 同憑證但**唔係**現有 `match_wiki_chunks` RPC——嗰個係 vector RPC、本契約係 by-id 表讀）。下游**永遠睇唔到 Supabase key**，只打 K1 端點。

```
下游 Circular System                         K1 Policy Checker backend (NET-NEW routes)
─────────────────────                        ──────────────────────────────────────────
  本地 Channel B index   ── ① GET manifest ──▶  anon REST select=id,source_id,hash,topic,content_type
  （file-based numpy）    ◀── 細 manifest ─────   （+ source_aliases、ingest guard）
        │  set-diff(本地 id-set vs manifest)  + delete-safety(§5)
        └──────────── ② POST chunks(ids) ──▶  anon REST wiki_chunks?id=in.(...) select=全欄[+embedding]
                      ◀── 完整 chunk[+向量] ──
  查詢時：query embed(text-embedding-3-small) → 本地相似度搜尋（唔打 K1）
```

---

## 3. 端點 ① — Manifest

```
GET /api/channel-b/manifest
Header: X-Sync-Key: <downstream-scoped read key>      （見 §6；缺/錯 = 401/403；env 未設 = 503 fail-closed）
Header: If-None-Match: "<上次 etag>"                    （可選；未變回 304 headers-only 空 body）
Query (可選): ?include_statistical=false  &  ?cursor=<id>&limit=5000
```

**200 回應**（`chunks[]` **必按 id 升序**；server 側可分頁）：
```json
{
  "contract_version": "1.0",
  "embedding_model": "text-embedding-3-small",
  "embedding_dim": 1536,
  "generated_at": "2026-06-05T08:00:00Z",
  "ingest_in_progress": false,
  "count": 10594,
  "manifest_hash": "<見下：對 (contract_version + embedding_model + 排序 id-set) 之穩定雜湊>",
  "source_aliases": { "g24": "sag_2025_11" },
  "chunks": [
    { "id": "vault_stat_enrolment_2012_ebc2728957012532", "source_id": "stat_enrolment_2012", "hash": "ebc2728957012532", "topic": "general", "content_type": "vault_extract" }
  ],
  "next_cursor": null
}
```

- `chunks[]` 含 `{id, source_id, hash, topic, content_type}`（無 text/向量）→ ~10,594 × ~110–130B ≈ ~1.3MB raw、gzip ~200–300KB。**`topic`（7 值 enum：finance/hr/curriculum/activity/student/it/general）+ `content_type`（vault_extract/approved_fact/stat_fact/guideline）= 下游 client-side 揀子集鏡像（如「校本通告相關」）所需、只 fetch 子集向量**（S145 反問 a）。兩者皆 `wiki_chunks` 現有已 populate 欄、同一 table scan 取得、零額外查詢成本。
- **`manifest_hash` 必須涵蓋 `contract_version` ＋ `embedding_model` ＋ 排序後 id-set**（修 blocker 2：若只 hash id-set，換 embedding model 但 id 不變 → ETag 不變 → 304 → 下游永遠睇唔到版本變 = silent break）。排序後計 → order-independent，避免行序差異造成假變更。
- **`ETag` = 對「實際送出嘅 payload」計（同一 snapshot），唔好獨立重算**，免 body/ETag desync。
- **`ingest_in_progress`**（consistency guard 欄位）：**S144 決策 = K1 v1 不實作 sentinel、永遠回 `false`**（upload pipeline 不改）；一致性**淨靠下游 delete-safety**（§5 / §11.4）。欄位保留入契約俾將來：若日後 K1 加 sentinel，下游邏輯（見 `true` 即跳本輪 delta、尤其跳 deletes）無需改。
- **`source_aliases`**：K1 內部 `SOURCE_ALIASES`（同文件不同 source_id），俾下游 dedup。
- **`include_statistical`**（預設 `false`，鏡 search 預設）：見 §6「superset」說明。
- **分頁**：`?cursor=<id>&limit=`（id lexical order 穩定，live `order=id` HTTP 200）；回 `next_cursor`。v1.0 N 細未必需要、契約留位。
- **Server 成本**：因無 timestamp 欄，server **必須 O(N) 全表掃 `id,source_id,hash`** 先計到 `manifest_hash`。ETag/304 慳嘅係**下游頻寬、唔慳 server scan**；故 server 側快取（TTL 30–60s）令成本 = 每 TTL window 一次 scan（與 poll 率無關）。N 增大時 scan 延遲 + `57014` 風險上升（見 §8）。

---

## 4. 端點 ② — Fetch chunks by id

```
POST /api/channel-b/chunks
Header: X-Sync-Key: <key>   Content-Type: application/json
Body: { "ids": ["vault_...", ...], "include_embedding": true }   （單次上限建議 150 ids；下游分批；見下）
```

**200 回應**：
```json
{
  "contract_version": "1.0",
  "embedding_model": "text-embedding-3-small",
  "chunks": [
    {
      "id": "vault_xxx_yyy", "hash": "yyy", "source_id": "g04",
      "title": "...", "url": "https://www.edb.gov.hk/...",
      "topic": "general", "content_type": "vault_extract", "fact_type": "policy",
      "role": null, "school_level": null, "reference_year": null,
      "text": "=== Page 1 ===...",
      "embedding": "[0.00757,-0.00092,...]"
    }
  ]
}
```

- **欄位 = backend `WikiChunk` 全集 ＋ `embedding`。** Null 欄位 convention：`role`/`school_level`/`reference_year` **一律出現、值為顯式 `null`**（**注意**：backend search 序列化會 omit falsy key；本契約**統一改為永遠帶 null**，下游唔使估）。
- **Enum 屬 advisory、非 DB-enforced**（schema 存 bare `text`、無 CHECK）：`content_type` 現見 `vault_extract|approved_fact|stat_fact|guideline`、`fact_type` 現見 `policy|approved_policy|statistical|guideline_reference`；下游**勿 hard-reject 未知值**（K1 日後可能加值）。
- **`text` 保留 `=== Page N ===` 頁標記**；**無**預解析 `page` 欄（下游自行 parse，如 search 層 `extractFirstPage`）。
- **`embedding` 格式**：pgvector 預設文字序列化 `"[f,f,...]"`（逗號分隔、可能高精度/科學記數）；**非-null 時保證 1536 維**。**`embedding` 可為 `null`**（schema 容許 NOT NULL 缺位）→ 下游遇 null 應**跳過該 chunk 之向量索引**（或退 text-only 路徑），勿當解析失敗。`include_embedding:false` → 慳頻寬，俾「自家重嵌」consumer（§7 路 2）。
- **缺 id 容忍 = pending-add，非 delete**：若請求 id 喺 fetch 時已不存在，回應只含尚存者；下游**略過缺者、保持當 add 候選**，**切勿因此 tombstone**（佢仲喺 manifest = 加緊、唔係刪）。
- **Batch / URL**：建議單批 **150 ids**（每 chunk = full text + ~15–20KB 文字化向量；500 批可達 10–30MB/回應，free-tier 冷啟易 timeout）。K1→PostgREST 用 `id=in.(...)` 時 **150 ids × ~42 char ≈ 6KB URL** 安全；K1 內部若需更大批必須再切 `in.()` 或改 POST filter，免 URL 長度爆。

---

## 5. Delta 同步演算法（下游端；K1 不實作，描述俾下游 build）

```
# Bootstrap（首次）
m = GET /manifest;  fetch_all(m.chunks.ids in batches of 150) → 建本地 index

# 穩態（每 N 分鐘 poll；帶 If-None-Match）
m = GET /manifest
if 304: return                                  # 無變
if m.ingest_in_progress: return                 # K1 寫入中，跳本輪（尤其跳 deletes）
remote = { c.id for c in m.chunks }; local = { 本地所有 id }
adds = remote - local; deletes = local - remote
# ── delete-safety（修 blocker 1，純下游、零 pipeline touch）──
for sid, del_ids in group_by_source(deletes):
    if del_ids ≈ 本地該 sid 全部 chunks:        # 整源消失 = 疑似 mid-ingest 窗口
        mark_suspect(sid); 唔即刪                #   re-poll 30–60s 後再確認
deletes = deletes - suspect;  確認連續兩 poll 都缺 先 tombstone
for batch in chunk(adds, 150): POST /chunks{ids:batch} → upsert（含/不含向量）
apply_deletes(deletes)
```

**性質**：
- **冪等**；**內容修改自動處理**（舊 id∈deletes ＋ 新 id∈adds）。
- **Delete-safety**：整源級 deletes 視為疑似 mid-ingest（pipeline 非原子 delete-then-insert 有秒級窗口）→ 連續兩 poll 確認先 tombstone。配合 manifest `ingest_in_progress` = 雙重防護，**避免「manifest 中途讀到 → 誤刪 live 源 → search flap」**（v0.1 錯誤地宣稱「self-healing 毋須 transaction」；實際 manifest 路徑需此 guard）。
- **新鮮度**：下游真實 cadence（S145）= cron 3×/日（HKT 07/13/17）+ 手動、非常駐 → **有效新鮮度 = max(poll 間隔, manifest cache TTL)**；本下游 profile 唔需要亦做唔到常駐 poll。常駐型 consumer 先可縮 poll 至 2–5 分鐘逼近即時（本下游不適用）。delete-safety「連續兩 poll 確認」對本下游 = **連續兩個 cron run（隔數小時至跨日）→ 一致性窗口更闊、更安全**。
- **Manifest vs fetch 一致性**：manifest 可能 cache（≤TTL stale）、fetch 讀 live；manifest 列嘅 id 喺 fetch 時若缺 = 當 pending-add 跳過（**勿 tombstone**），下個 poll 補。Cache TTL 應 ≤ 下游可容忍嘅 fetch 落差。

---

## 6. Auth、限流、快取、cadence、bulk-exposure

- **Downstream-scoped read key**：header `X-Sync-Key` 比對 env `CHANNEL_B_SYNC_KEY`（**唔落 dev/* 檔，存 onrender env / OS secret；錯誤路徑亦不可 log key / header 值**）。下游側存 GitHub Actions secret（同其 `OPENAI_API_KEY` 一樣，S145 確認）。
  - **比對必用 `crypto.timingSafeEqual`**（naive `===` 係 timing oracle）。
  - **回應碼**：缺 header = **401**；錯 key = **403**；`CHANNEL_B_SYNC_KEY` env **未設 = 503（fail-closed，端點停用、絕不 open）**。
  - **Rotation/revoke**：支援**多把有效 key**（逗號分隔 env）以便輪換；撤銷 = 改 env + redeploy。
- **限流（不可豁免）**：sync 端點**不套** public POST 10/min（嗰個會夾死正常 sync），但**必須有自己嘅限流**：**60 req/min ＋ 每日 chunk/bytes 預算上限 ≈ 3× 全庫拉取量**（防全庫 exfil——60/min 仍可 ~22 個 batch 拉走全庫；故需 daily budget，非淨 req/min）。**Bootstrap pacing（S145 反問 b）**：全量 10,594 ÷ 150 = **71 批**，60/min 下 ≈ 1.1 分鐘跑完、佔每日預算 ~1/3（同日餘 ~2× 全庫 budget 俾後續 delta）；下游 3×/日 cron 不會掂頂。
- **Bulk-exposure 修正（審核揪出 v0.1 假設錯）**：bulk feed **唔等於**「Channel B search 已公開嘅同一份」——佢係 **superset**：(a) search 預設**隱藏** `stat_fact` / `source_id startsWith "stat_"`，bulk 全送；(b) bulk 送**原始 1536-維向量**（search 從不回向量）。故此 (1) §3 `include_statistical` 預設 `false` 鏡 search；(2) 全 feature 須 sync key gate + daily budget；(3) Leonard 決定 stat_/guideline chunk 是否入 feed（§11）。
- **快取 / cadence**：manifest server 側快取 `manifest_hash`+body（TTL 30–60s）；ETag 命中 304。下游 poll 2–5 分鐘；K1 pull-only 不 push。
- **CORS**：sync 端點 server-to-server（下游係 service）→ **唔好 call 現有 `setCorsHeaders`**（佢對每個 response 包括 404/429 都會發 `Access-Control-Allow-Origin`；sync route 誤用會錯誤對瀏覽器開 CORS）。sync route 不發 CORS allow header；唯一 gate = sync key。

---

## 7. Embedding invariant（硬規則，兩條路都 cover）

- K1 Channel B 向量 = **OpenAI `text-embedding-3-small`（1536 維）**。下游 **query 端必須用同一 model 嵌 query**，否則相似度全錯。
- **序列化格式（S145 反問 c，實測確認）**：`embedding` 係 JSON **字串** `"[f,f,…]"`（pgvector 預設文字序列化、逗號分隔、可能科學記數）、**非** JSON number array → 下游須 parse 個 string；非-null 時保證 **1536 維**。
- **已 L2-normalized（S145 實測 6 條跨源樣本 ‖v‖₂ = 1.0 ± ~3e-4）**：OpenAI 3-small 原生單位長度、pipeline 原樣存。下游 cosine 可當已正規化；防禦式自行 normalize = 無害 no-op。
- **兩條路（決策點 #4）**：
  1. **對齊 3-small ✅ 下游 S145 揀此路**：食 K1 送嘅 `embedding`（chunk 零重嵌），query 用 `text-embedding-3-small`。最省最快。
  2. **下游用第二 model（未採）**：`include_embedding:false` 慳頻寬、用 `text` 自家全量重嵌，query 同一自家 model。
- **K1 改 embedding model（未來）**：`contract_version` major bump ＋ `embedding_model` 改值；因 §3 已將兩者**摺入 `manifest_hash`/ETag**，304 consumer **必偵測到**（修 blocker 2）→ 觸發全量重 sync。

---

## 8. 失效 / 邊界情況

| 情況 | 處理 |
|------|------|
| Pipeline 非原子 delete-then-insert（秒級窗口） | manifest `ingest_in_progress` guard ＋ 下游 delete-safety（整源 deletes 兩 poll 確認）= 雙防；**勿宣稱毋須一致性保護** |
| Re-ingest re-chunk 全源 → 大量 id flip | delta 可達單源全 chunk；batch 150 自動分批；delete-safety 處理整源翻新 |
| `57014` statement-timeout | **manifest 全表掃 ≠ RPC 單 query**，timeout profile 更差；manifest 需**自己嘅 retry budget ＋ PostgREST `Range` 分頁**，勿照搬 RPC 嘅 ≤3 linear-backoff |
| onrender 冷啟 ~30s | 下游 poll 設 timeout + retry；穩態 304 後常駐 warm；如需 K1 keep-warm（獨立 ops） |
| K1 短暫不可用 | 下游**續用本地 index（last-known-good）**，下個 poll 補 — 對齊 playbook `prod-fail-visible-no-mock-fallback` |
| 共用 free-tier DB 爭用 | manifest 全表掃同 live `/api/search/channel-b` **共用 free-tier DB statement budget**；scan 必須節流，**勿餓死 live search**（雖非 schema 改、但係 shared-resource 風險） |
| manifest 列 id 喺 fetch 時缺 | 當 pending-add 跳過，**勿 tombstone** |

---

## 9. K1-side build tasks（**本 pass 不做**；待 Leonard review 契約後另開，全 additive/reversible）

1. `GET /api/channel-b/manifest` — anon REST `select=id,source_id,hash,topic,content_type`；server 快取 + ETag（涵蓋 version+model+排序 id-set）；`ingest_in_progress` guard（v1 永回 false）；`source_aliases`；`include_statistical`；分頁 + 自有 `57014` retry/Range。
2. `POST /api/channel-b/chunks` — anon REST `wiki_chunks?id=in.(...)&select=<全欄[+embedding]>`；單批 ≤150；`include_embedding`；null 欄位顯式 null；缺 id 跳過。
3. **Auth/限流**：`X-Sync-Key`（`timingSafeEqual`、401/403/503-fail-closed、多 key rotation、never-log）＋ sync 端點自有 req/min **＋ daily chunk/bytes budget**；**唔 call `setCorsHeaders`**。
4. 各 route 純新增；rollback = revert route（Supabase / Channel A / upload pipeline / 既有端點零接觸）。

**Out of scope（明確唔做）**：build 上述端點、掂下游 repo、un-freeze Channel A、改 Supabase schema / `match_wiki_chunks` / upload pipeline、手寫 `knowledge.json` / `guidelines.json`。

---

## 10. HTTP 契約細節（俾下游工程師）

| 狀況 | 碼 | Body |
|------|----|------|
| 成功 | 200 | 見 §3/§4 |
| manifest 未變 | 304 | **headers-only、空 body**（下游勿試 parse JSON） |
| body 壞 / `ids` 非陣列 | 400 | `{error}` |
| `ids` 超上限 | 400 | `{error, max_ids:150}`（不靜默截斷） |
| 缺 sync key | 401 | `{error}` |
| 錯 sync key | 403 | `{error}` |
| 超限流 | 429 | `{error, retry_after_sec}` + `Retry-After`（鏡既有限流 shape） |
| `CHANNEL_B_SYNC_KEY` 未設 | 503 | `{error:"sync disabled"}`（fail-closed） |
| upstream Supabase 故障 | 502/503 | `{error}`（retry 後仍失敗先回） |

排序保證：`manifest.chunks[]` 按 `id` 升序；`manifest_hash` 對排序 id-set 計（order-independent）。`generated_at` = server UTC（下游勿假設與本地零時差）。

---

## 11. 決策（S144 Leonard 逐條拍板 — RESOLVED）

1. **Stat / guideline chunks 入 feed**：✅ **預設排除**（`include_statistical=false`，鏡 Channel B search 預設）。下游要全廣度可顯式帶 `include_statistical=true`。
2. **預設 ship 向量定 text-only**：✅ **RESOLVED（S145 下游覆文）** — 下游確認 query 端用 `text-embedding-3-small`（路 1）→ **K1 預設 `include_embedding=true` 連向量送、下游零重嵌直接入庫**。向量格式（pgvector `"[…]"` 字串）+ L2-norm（實測 ‖v‖₂≈1.0）見 §7。`include_embedding=false` escape 保留俾將來「第二 model」consumer（純 param 控）。
3. **限流 / exfil budget / key rotation**：✅ **照建議** — sync 端點 60 req/min + 每日 chunk/bytes 上限 ≈ 3× 全庫拉取量 + 多 key（逗號分隔 env）季度輪換。
4. **一致性保護**：✅ **淨靠下游 delete-safety**（整源 deletes 兩 poll 確認；零 pipeline touch）；**不加** K1 `ingest_in_progress` sentinel。manifest `ingest_in_progress` 欄保留但 K1 v1 永遠回 `false`（§3）。

---

## 12. 相關檔案 / 契約演進

| 檔案 | 說明 |
|------|------|
| `dev/CHANNEL_B_SYNC_SPEC.md` | 本檔（K1-side Channel B 增量同步契約） |
| `dev/CIRCULAR_SYSTEM_INTEGRATION.md` | 舊整合（**輸入向**：下游寫 `policy_signals.json` → Channel A）；本 spec 係**輸出向**，並存不衝突 |
| `backend/src/lib/wikiRepository.ts` | `WikiChunk` interface SSOT + Supabase anon-key 讀取 |
| `backend/src/server.ts` | `node:http` 路由 + 限流 + CORS（新端點對齊風格，惟限流/CORS 按 §6 調整） |
| `backend/src/api/searchChannelB.ts` | search 預設隱藏 `stat_fact`（§6 superset 來源） |
| `dev/cb3_b2_pagecarry_migrate.py` | upload pipeline：`sha256(text)[:16]` id + 非原子逐源 delete-then-insert（§1/§5/§8 根據） |
| PMS §C.4 / §F.2 | Supabase 真實規格 / Q4 鎖定決策鏈 |

**契約版本規則**：`contract_version` semver。Minor = 加欄（向後相容）；Major = 改 `embedding_model` / 改 id 語義 / 移欄（下游需全量重 sync）。改契約必走 AGENTS §3 HIGH-risk PLAN + 更新本檔 + 通知下游。

---

*v0.2 draft — 2026-06-05 S144（過一輪對抗審核 hardening）。v0.3 — S144 §11 四決策定案。**v0.4 — 2026-06-05 S145：納入下游 Circular System consumer 覆文 — §11.2 RESOLVED（路 1 / `include_embedding=true`）、manifest +`topic`/`content_type`（反問 a）、限流 + bootstrap pacing（反問 b）、向量格式 + L2-norm 實測（反問 c）、profile 校正（ephemeral cron 3×/日 / file-based numpy，非常駐/非 pgvector）。契約 build-ready，待 Leonard GO 另開 K1-side endpoint build task。***
