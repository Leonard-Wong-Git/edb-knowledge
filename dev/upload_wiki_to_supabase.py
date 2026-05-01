#!/usr/bin/env python3
"""
upload_wiki_to_supabase.py
──────────────────────────
將 dev/knowledge/wiki_index.json 的 2,874 chunks（含 1536-dim embeddings）
批次上傳至 Supabase wiki_chunks table。

使用方式（從 repo 根目錄執行）：
    python3 dev/upload_wiki_to_supabase.py

需要環境變數（或直接在腳本頂部填寫）：
    SUPABASE_URL        = https://youkcekbrbywuqjxgibe.supabase.co
    SUPABASE_SERVICE_KEY = sb-service-role-key（從 Supabase → Settings → API 取得）

注意：上傳使用 service_role key（繞過 RLS），查詢使用 anon key。
"""

import json
import os
import sys
import time
from pathlib import Path

import requests

# ── 配置 ──────────────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://youkcekbrbywuqjxgibe.supabase.co"
)

# 從 Supabase Dashboard → Settings → API → service_role (secret) 取得
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

WIKI_INDEX_PATH = Path(__file__).parent / "knowledge" / "wiki_index.json"

BATCH_SIZE = 50        # 每批上傳 50 條（每條含 1536 floats，約 300KB/batch）
TABLE = "wiki_chunks"

# ── 驗證 ──────────────────────────────────────────────────────────────────────

if not SUPABASE_SERVICE_KEY:
    print("❌ 缺少 SUPABASE_SERVICE_KEY")
    print("   請從 Supabase Dashboard → Settings → API → service_role (secret) 複製")
    print("   然後執行：SUPABASE_SERVICE_KEY=sb-... python3 dev/upload_wiki_to_supabase.py")
    sys.exit(1)

if not WIKI_INDEX_PATH.exists():
    print(f"❌ 找不到 wiki_index.json：{WIKI_INDEX_PATH}")
    sys.exit(1)

# ── 載入資料 ──────────────────────────────────────────────────────────────────

print(f"📂 載入 {WIKI_INDEX_PATH} ...")
with open(WIKI_INDEX_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

chunks = data["chunks"]
total = len(chunks)
print(f"✅ 載入完成：{total} chunks")

# ── 清理欄位（確保符合 table schema） ─────────────────────────────────────────

VALID_FIELDS = {
    "id", "hash", "text", "source_id", "title", "url",
    "topic", "content_type", "fact_type", "role",
    "school_level", "reference_year", "embedding"
}

def clean_chunk(c: dict) -> dict:
    """保留 schema 欄位，過濾多餘 key，確保 nullable 欄位正確處理。"""
    cleaned = {k: v for k, v in c.items() if k in VALID_FIELDS}
    # 確保 nullable 欄位存在（即使值為 None）
    for nullable in ("role", "school_level", "reference_year"):
        if nullable not in cleaned:
            cleaned[nullable] = None
    # embedding 必須是 list
    if "embedding" not in cleaned or not cleaned["embedding"]:
        print(f"  ⚠️  chunk {cleaned.get('id')} 沒有 embedding，跳過")
        return None
    return cleaned

# ── 上傳函數 ──────────────────────────────────────────────────────────────────

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",  # 只插入，不返回資料（更快）
}

endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE}"

def upload_batch(batch: list[dict], batch_num: int, total_batches: int) -> bool:
    """上傳一批 chunks，返回是否成功。"""
    resp = requests.post(
        endpoint,
        headers=headers,
        json=batch,
        timeout=60,
    )
    if resp.status_code in (200, 201):
        return True
    else:
        print(f"\n  ❌ Batch {batch_num}/{total_batches} 失敗：{resp.status_code} {resp.text[:200]}")
        return False

# ── 主流程 ────────────────────────────────────────────────────────────────────

print(f"\n🚀 開始上傳（batch size={BATCH_SIZE}）...")

batches = []
current_batch = []
skipped = 0

# Deduplicate by id across ALL chunks before batching
seen_ids: set = set()
deduped_chunks = []
for chunk in chunks:
    cleaned = clean_chunk(chunk)
    if cleaned is None:
        skipped += 1
        continue
    if cleaned["id"] in seen_ids:
        skipped += 1
        continue
    seen_ids.add(cleaned["id"])
    deduped_chunks.append(cleaned)

for chunk in deduped_chunks:
    current_batch.append(chunk)
    if len(current_batch) >= BATCH_SIZE:
        batches.append(current_batch)
        current_batch = []

if current_batch:
    batches.append(current_batch)

total_batches = len(batches)
uploaded = 0
failed_batches = []

for i, batch in enumerate(batches, 1):
    success = upload_batch(batch, i, total_batches)
    if success:
        uploaded += len(batch)
        # Progress bar
        pct = int(uploaded / (total - skipped) * 40)
        bar = "█" * pct + "░" * (40 - pct)
        print(f"\r  [{bar}] {uploaded}/{total - skipped} chunks  (batch {i}/{total_batches})", end="", flush=True)
    else:
        failed_batches.append(i)
    # 輕微延遲避免 rate limit
    time.sleep(0.2)

print()  # newline after progress bar

# ── 結果 ──────────────────────────────────────────────────────────────────────

print(f"\n{'='*50}")
print(f"✅ 上傳完成：{uploaded} chunks")
if skipped:
    print(f"⚠️  跳過（無 embedding）：{skipped} chunks")
if failed_batches:
    print(f"❌ 失敗 batch：{failed_batches}")
    print("   請重新執行腳本（Prefer: merge-duplicates 會自動跳過已上傳的）")
else:
    print("🎉 全部成功，無失敗 batch")

print(f"\n驗證指令（在 Supabase SQL Editor 執行）：")
print(f"  select count(*) from public.wiki_chunks;")
print(f"  -- 預期：{uploaded}")
