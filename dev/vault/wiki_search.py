#!/usr/bin/env python3
"""
wiki_search.py — Channel B: LLM-Wiki Query Engine

Accepts a user query, retrieves relevant chunks from wiki_index.json
via semantic similarity, then synthesises a concise answer with source citations.

Channel B is NOT connected to the Circular System (paused pending testing).

Token efficiency:
  - Embeddings pre-computed (no re-embedding per query)
  - Only top-k chunks passed to LLM (default k=4, max ~2400 chars context)
  - Answer capped at 200 chars + source list

Usage:
  cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"

  # Interactive search
  python3 dev/vault/wiki_search.py "小學採購門檻是多少"

  # Show top retrieved chunks without LLM synthesis
  python3 dev/vault/wiki_search.py "教師CPD要求" --retrieve-only

  # Adjust number of retrieved chunks (default: 4)
  python3 dev/vault/wiki_search.py "融合教育學生人數" --top-k 6

  # Output as JSON (for programmatic use)
  python3 dev/vault/wiki_search.py "境外活動申報" --json

Environment:
  OPENAI_API_KEY — required (in backend/.env or env var)

Prerequisites:
  Run build_wiki_index.py first to create dev/knowledge/wiki_index.json
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = REPO_ROOT / "dev" / "knowledge" / "wiki_index.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_TOP_K = 4
MAX_CONTEXT_CHARS = 2400   # total chars sent to LLM (4 × 600)
ANSWER_MAX_CHARS = 200

SYNTHESIS_PROMPT = """你是香港學校管治顧問。根據以下 EDB 相關資料，用簡潔繁體中文回答用戶問題。

規則：
- 回答限 200 字以內
- 必須根據提供資料作答，不可猜測
- 如資料不足，請說「資料不足，建議參閱原文」
- 回答後列出資料來源（標題 + URL）
- 不要重複引用全文，只提取關鍵數字或規定
"""

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and not key.startswith("sk-..."):
                    return key
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    print("ERROR: OPENAI_API_KEY not found.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Cosine similarity (no numpy required)
# ---------------------------------------------------------------------------

def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

def norm(a: list[float]) -> float:
    return math.sqrt(sum(x * x for x in a))

def cosine_similarity(a: list[float], b: list[float]) -> float:
    n = norm(a) * norm(b)
    return dot(a, b) / n if n > 0 else 0.0


# ---------------------------------------------------------------------------
# Index loader
# ---------------------------------------------------------------------------

def load_index() -> dict:
    if not INDEX_PATH.exists():
        print(f"ERROR: wiki_index.json not found at {INDEX_PATH}", file=sys.stderr)
        print("Run: python3 dev/vault/build_wiki_index.py", file=sys.stderr)
        sys.exit(1)
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def embed_query(api_key: str, query: str) -> list[float]:
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai not installed.", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding


def retrieve(query_vec: list[float], chunks: list[dict],
             top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return top-k chunks by cosine similarity."""
    scored = []
    for chunk in chunks:
        emb = chunk.get("embedding")
        if not emb:
            continue
        sim = cosine_similarity(query_vec, emb)
        scored.append((sim, chunk))

    scored.sort(key=lambda x: -x[0])
    results = []
    seen_texts = set()
    for sim, chunk in scored:
        # Deduplicate near-identical chunks
        key = chunk["text"][:80]
        if key in seen_texts:
            continue
        seen_texts.add(key)
        results.append({**chunk, "_score": round(sim, 4)})
        if len(results) >= top_k:
            break
    return results


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

def synthesise(api_key: str, query: str, chunks: list[dict]) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai not installed.", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    # Build context (respect MAX_CONTEXT_CHARS)
    context_parts = []
    total = 0
    for i, chunk in enumerate(chunks, 1):
        text = chunk["text"]
        title = chunk.get("title", chunk.get("source_id", ""))
        part = f"[{i}] {title}\n{text}"
        if total + len(part) > MAX_CONTEXT_CHARS:
            break
        context_parts.append(part)
        total += len(part)

    context = "\n\n".join(context_parts)
    user_msg = f"問題：{query}\n\n參考資料：\n{context}"

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "user", "content": SYNTHESIS_PROMPT + "\n\n" + user_msg}
            ],
            max_tokens=500
        )
        content = response.choices[0].message.content
        if not content:
            # Log finish_reason to help diagnose silent empty responses
            reason = response.choices[0].finish_reason if response.choices else "no_choices"
            print(f"  ⚠️  LLM returned empty content (finish_reason={reason})", file=sys.stderr)
        return (content or "").strip()
    except Exception as e:
        print(f"  ⚠️  LLM synthesis failed: {e}", file=sys.stderr)
        return ""


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_result(query: str, chunks: list[dict],
                  answer: str = None, as_json: bool = False) -> str:
    sources = []
    seen_urls = set()
    for c in chunks:
        url = c.get("url", "")
        title = c.get("title", c.get("source_id", ""))
        if url and url not in seen_urls:
            sources.append({"title": title, "url": url,
                            "score": c.get("_score", 0)})
            seen_urls.add(url)

    if as_json:
        return json.dumps({
            "query": query,
            "answer": answer,
            "sources": sources,
            "chunks": [
                {
                    "text": c["text"],
                    "source_id": c.get("source_id"),
                    "content_type": c.get("content_type"),
                    "score": c.get("_score"),
                }
                for c in chunks
            ],
        }, ensure_ascii=False, indent=2)

    lines = []
    lines.append(f"\n{'='*55}")
    lines.append(f"  查詢：{query}")
    lines.append(f"{'='*55}")

    if answer:
        lines.append(f"\n📋 回答\n{answer}")

    lines.append(f"\n📚 參考來源（相關度排序）")
    for i, c in enumerate(chunks, 1):
        ct = c.get("content_type", "")
        score = c.get("_score", 0)
        title = c.get("title", c.get("source_id", ""))
        url = c.get("url", "")
        lines.append(f"\n  [{i}] {title}  (相關度 {score:.2f})")
        lines.append(f"       類型: {ct}")
        if url:
            lines.append(f"       URL: {url}")
        lines.append(f"       文字: {c['text'][:120]}{'...' if len(c['text'])>120 else ''}")

    lines.append(f"\n{'─'*55}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Channel B: LLM-wiki query")
    parser.add_argument("query", help="Search query in Chinese or English")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"Number of chunks to retrieve (default: {DEFAULT_TOP_K})")
    parser.add_argument("--retrieve-only", action="store_true",
                        help="Show retrieved chunks only, skip LLM synthesis")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    api_key = load_api_key()

    print("📖 Loading wiki index...", file=sys.stderr)
    index = load_index()
    chunks = index.get("chunks", [])
    total = len(chunks)
    with_emb = sum(1 for c in chunks if c.get("embedding"))
    print(f"   {with_emb}/{total} chunks have embeddings", file=sys.stderr)

    print(f"🔍 Embedding query...", file=sys.stderr)
    query_vec = embed_query(api_key, args.query)

    print(f"🎯 Retrieving top-{args.top_k} chunks...", file=sys.stderr)
    top_chunks = retrieve(query_vec, chunks, top_k=args.top_k)

    answer = None
    if not args.retrieve_only:
        print(f"🤖 Synthesising answer...", file=sys.stderr)
        answer = synthesise(api_key, args.query, top_chunks)

    print(format_result(args.query, top_chunks, answer, as_json=args.json))


if __name__ == "__main__":
    main()
