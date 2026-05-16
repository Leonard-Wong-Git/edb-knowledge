#!/usr/bin/env python3
"""
ai_extract.py — Channel B: Full AI Analysis Pipeline

Channel B companion to extract_candidates.py (Channel A).
Same vault sources, different extraction strategy:
  - Channel A: explicit rules with thresholds/numbers → human review → role_facts.json
  - Channel B: broader analysis (guidance, implications, risks, procedures) → ai_candidate_queue.json

Channel B output is NOT for direct injection into role_facts.json.
It serves as:
  1. A reference corpus for comparison with Channel A human-curated facts
  2. A gap detector (facts AI finds that humans missed, or vice versa)
  3. A future input for AI-assisted human review

Usage:
  cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"

  # Extract from a single vault file
  python3 dev/vault/ai_extract.py dev/vault/circ_edbc24017/extract_edbc24017_.txt

  # Extract from all .txt files in a vault directory
  python3 dev/vault/ai_extract.py dev/vault/circ_edbc24017/

  # Append to existing ai_candidate_queue.json (default: overwrite)
  python3 dev/vault/ai_extract.py --append dev/vault/g01/extract_g01_20260412.txt

  # Dry-run (print to stdout only)
  python3 dev/vault/ai_extract.py --dry-run dev/vault/circ_edbc24017/extract_edbc24017_.txt

  # Custom output path
  python3 dev/vault/ai_extract.py -o my_ai_queue.json dev/vault/circ_edbc24017/

Environment:
  OPENAI_API_KEY — required (checked in backend/.env then os.environ)

Output schema: dev/knowledge/ai_candidate_queue.json
  Differs from candidate_queue.json:
  - channel: "B" on every entry
  - extraction_type: requirement | guidance | deadline | procedure | risk_flag
  - compliance_risk: high | medium | low | none
  - related_topics: cross-topic connections the AI identifies
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "dev" / "knowledge" / "ai_candidate_queue.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

VALID_TOPICS = ["finance", "hr", "curriculum", "activity", "student", "it", "general"]
VALID_ROLES = [
    "all_roles", "principal", "vice_principal",
    "panel_chair", "subject_head", "teacher", "eo_admin", "supplier"
]
VALID_EXTRACTION_TYPES = ["requirement", "guidance", "deadline", "procedure", "risk_flag"]
VALID_RISK_LEVELS = ["high", "medium", "low", "none"]

MAX_CHUNK_CHARS = 12_000

# ---------------------------------------------------------------------------
# Channel B System Prompt
# ---------------------------------------------------------------------------
# Key differences from Channel A:
#   - Channel A: only explicit rules with numbers/thresholds (≤80 chars)
#   - Channel B: broader — guidance, procedures, risks, cross-topic links
#     extraction_type classifies what kind of fact it is
#     compliance_risk flags urgency for school administrators

SYSTEM_PROMPT_B = """你是一位香港學校管治顧問，專門對教育局 (EDB) 官方文件進行深度政策分析，
為學校管理層提供全面的合規指引及風險提示。

你的任務：從提供的 EDB 文件段落中提取所有對學校管理有實際影響的資訊，包括：
  - 明確規定及數字門檻（requirement）
  - 操作指引及最佳實踐建議（guidance）
  - 時限及截止日期（deadline）
  - 程序步驟及工作流程（procedure）
  - 合規風險提示及違規後果（risk_flag）

輸出格式（嚴格使用 JSON array）：
[
  {
    "proposed_text": "完整的政策要點（≤120字，中文，可比 Channel A 更詳盡）",
    "source_quote": "從原文逐字複製的對應段落（用於核實）",
    "page_number": "頁數（數字，根據 === Page X === 標記）",
    "suggested_topic": "finance|hr|curriculum|activity|student|it|general",
    "suggested_roles": ["適用角色列表"],
    "extraction_type": "requirement|guidance|deadline|procedure|risk_flag",
    "compliance_risk": "high|medium|low|none",
    "related_topics": ["此 fact 可能同時涉及的其他 topic，如跨題目則填入，否則空 array []"],
    "confidence": "high|medium|low"
  }
]

規則：
- 覆蓋面要廣：不只提取有數字的條文，也包括程序步驟、時限、指引建議
- extraction_type 說明：
    requirement = 明確規定，必須遵從
    guidance    = 建議或最佳實踐，非強制但重要
    deadline    = 有時間限制的要求（學年初、每年X月等）
    procedure   = 需要多個步驟的工作流程
    risk_flag   = 不合規的後果或風險提示
- compliance_risk 說明：
    high   = 違規可能涉及法律責任、教育局介入或資助問題
    medium = 違規影響學校運作或評審
    low    = 行政性要求，影響有限
    none   = 純資訊性內容
- related_topics：如採購程序同時涉及 hr（誰批核）可填 ["hr"]
- 每個 fact 應能獨立閱讀，不依賴上下文
- confidence=high：原文明確；medium：需合理解讀；low：有歧義
- 只輸出 JSON，不要有其他文字
"""

# ---------------------------------------------------------------------------
# Vault header parser (shared with extract_candidates.py)
# ---------------------------------------------------------------------------

def parse_vault_header(text: str) -> dict:
    meta = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("# "):
            break
        match = re.match(r"^#\s+(\w+):\s*(.+)$", line)
        if match:
            meta[match.group(1).strip()] = match.group(2).strip()
    return meta


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    pages = re.split(r"(=== Page \d+ ===)", text)
    chunks = []
    current = ""
    for segment in pages:
        if len(current) + len(segment) > max_chars and current:
            chunks.append(current)
            current = segment
        else:
            current += segment
    if current.strip():
        chunks.append(current)
    return chunks if chunks else [text[:max_chars]]


# ---------------------------------------------------------------------------
# API key loader
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text().splitlines():
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and not key.startswith("sk-..."):
                    return key
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    print("ERROR: OPENAI_API_KEY not found in backend/.env or environment.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# OpenAI interaction — Channel B
# ---------------------------------------------------------------------------

def call_openai_b(api_key: str, vault_text: str, meta: dict) -> list[dict]:
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    source_context = f"""文件來源資訊:
- source_id: {meta.get('source_id', 'unknown')}
- 標題: {meta.get('title', 'unknown')}
- URL: {meta.get('url', 'N/A')}
- 類型: {meta.get('fact_type', 'policy')}
- 主題標籤: {meta.get('topic_tags', 'general')}

[Channel B 分析模式：請進行廣義政策分析，涵蓋規定、指引、程序、風險]

以下為原文摘錄：
"""

    all_candidates = []
    chunks = chunk_text(vault_text)
    ts = datetime.now(timezone.utc).isoformat()

    for i, chunk in enumerate(chunks):
        print(f"  ⏳ [Channel B] Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...",
              file=sys.stderr)

        try:
            from openai import OpenAI
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "user", "content": SYSTEM_PROMPT_B + "\n\n" + source_context + chunk}
                ],
                max_completion_tokens=25000
            )

            raw = (response.choices[0].message.content or "").strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?", "", raw)
                raw = re.sub(r"```$", "", raw).strip()

            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                candidates = parsed.get("facts", parsed.get("candidates", []))
            elif isinstance(parsed, list):
                candidates = parsed
            else:
                candidates = []

            all_candidates.extend(candidates)

        except json.JSONDecodeError as e:
            print(f"  ⚠️  JSON parse error on chunk {i+1}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️  API error on chunk {i+1}: {e}", file=sys.stderr)

    return all_candidates


# ---------------------------------------------------------------------------
# Post-processing & enrichment
# ---------------------------------------------------------------------------

def validate_and_enrich_b(candidates: list[dict], meta: dict) -> list[dict]:
    valid = []
    ts = datetime.now(timezone.utc).isoformat()

    for c in candidates:
        text = c.get("proposed_text", "").strip()
        quote = c.get("source_quote", "").strip()
        if not text or not quote:
            continue

        topic = c.get("suggested_topic", "general")
        if topic not in VALID_TOPICS:
            topic = "general"

        roles = [r for r in (c.get("suggested_roles") or ["all_roles"]) if r in VALID_ROLES]
        if not roles:
            roles = ["all_roles"]

        ext_type = c.get("extraction_type", "requirement")
        if ext_type not in VALID_EXTRACTION_TYPES:
            ext_type = "requirement"

        risk = c.get("compliance_risk", "low")
        if risk not in VALID_RISK_LEVELS:
            risk = "low"

        related = [t for t in (c.get("related_topics") or []) if t in VALID_TOPICS]

        valid.append({
            "id": f"ai_{uuid.uuid4().hex[:8]}",
            "channel": "B",
            "auto_generated": True,
            "proposed_text": text,
            "source_id": meta.get("source_id", "unknown"),
            "source_title": meta.get("title", "unknown"),
            "source_url": meta.get("url", ""),
            "source_quote": quote,
            "page_number": str(c.get("page_number", "")),
            "suggested_topic": topic,
            "suggested_roles": roles,
            "extraction_type": ext_type,
            "compliance_risk": risk,
            "related_topics": related,
            "confidence": c.get("confidence", "medium"),
            "generated_at": ts,
        })

    return valid


# ---------------------------------------------------------------------------
# Queue I/O
# ---------------------------------------------------------------------------

def load_existing_queue(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "candidates" in data:
                return data
        except Exception:
            pass
    return {
        "_meta": {
            "schema": "ai_candidate_queue_v1",
            "channel": "B",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": "gpt-4.1-nano",
            "note": "Channel B full-AI analysis. Not for direct role_facts.json injection. Use for comparison and gap analysis against Channel A human-curated queue.",
            "sources_processed": [],
            "total_candidates": 0,
        },
        "candidates": []
    }


def save_queue(queue: dict, path: Path):
    queue["_meta"]["total_candidates"] = len(queue["candidates"])
    queue["_meta"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Channel B: Full AI analysis pipeline")
    parser.add_argument("input", help="Vault .txt file or directory containing .txt files")
    parser.add_argument("--append", action="store_true",
                        help="Append to existing ai_candidate_queue.json (default: overwrite)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print candidates to stdout without writing to queue file")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUTPUT),
                        help=f"Output path (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    api_key = load_api_key()
    output_path = Path(args.output)

    # Collect input files
    input_path = Path(args.input)
    if input_path.is_dir():
        txt_files = sorted(input_path.glob("*.txt"))
    elif input_path.is_file():
        txt_files = [input_path]
    else:
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not txt_files:
        print(f"ERROR: no .txt files found in {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load or create queue
    queue = load_existing_queue(output_path) if args.append else {
        "_meta": {
            "schema": "ai_candidate_queue_v1",
            "channel": "B",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": "gpt-4.1-nano",
            "note": "Channel B full-AI analysis. Not for direct role_facts.json injection.",
            "sources_processed": [],
            "total_candidates": 0,
        },
        "candidates": []
    }

    total_new = 0

    for txt_file in txt_files:
        print(f"\n📄 [Channel B] Processing: {txt_file.name}", file=sys.stderr)
        vault_text = txt_file.read_text(encoding="utf-8")
        meta = parse_vault_header(vault_text)
        source_id = meta.get("source_id", txt_file.stem)

        raw_candidates = call_openai_b(api_key, vault_text, meta)
        enriched = validate_and_enrich_b(raw_candidates, meta)

        if args.dry_run:
            print(json.dumps(enriched, ensure_ascii=False, indent=2))
        else:
            queue["candidates"].extend(enriched)
            if source_id not in queue["_meta"]["sources_processed"]:
                queue["_meta"]["sources_processed"].append(source_id)

        total_new += len(enriched)
        print(f"  ✅ Extracted {len(enriched)} Channel B candidates from {source_id}",
              file=sys.stderr)

    if not args.dry_run:
        save_queue(queue, output_path)
        print(f"\n✅ [Channel B] Written {total_new} new candidates → {output_path}",
              file=sys.stderr)
        print(f"   Total in queue: {len(queue['candidates'])}", file=sys.stderr)
        print(f"   Sources processed: {queue['_meta']['sources_processed']}", file=sys.stderr)


if __name__ == "__main__":
    main()
