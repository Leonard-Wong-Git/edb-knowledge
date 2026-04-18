#!/usr/bin/env python3
"""
extract_candidates.py — Phase 3 Evidence-First Candidate Extraction Pipeline

Reads vault extract text files, uses OpenAI to propose candidate facts,
and writes them to dev/knowledge/candidate_queue.json for Dashboard review.

Usage:
  # Extract from a single vault file
  python3 dev/vault/extract_candidates.py dev/vault/circ_edbc24017/extract_edbc24017_.txt

  # Extract from an entire vault directory (all .txt files)
  python3 dev/vault/extract_candidates.py dev/vault/circ_edbc24017/

  # Dry-run (print to stdout, don't write to queue file)
  python3 dev/vault/extract_candidates.py --dry-run dev/vault/circ_edbc24017/extract_edbc24017_.txt

  # Append to an existing queue (default overwrites)
  python3 dev/vault/extract_candidates.py --append dev/vault/circ_edbc24017/extract_edbc24017_.txt

  # Specify output path (default: dev/knowledge/candidate_queue.json)
  python3 dev/vault/extract_candidates.py -o my_queue.json dev/vault/circ_edbc24017/extract_edbc24017_.txt

Environment:
  OPENAI_API_KEY — required (checked in backend/.env then os.environ)

Architecture (from K1_PHASE3_DESIGN.md):
  vault extract → LLM proposes candidate fact (with source ref) → human approves → role_facts.json
"""

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # dev/vault/.. -> dev/.. -> repo root
DEFAULT_OUTPUT = REPO_ROOT / "dev" / "knowledge" / "candidate_queue.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

VALID_TOPICS = ["finance", "hr", "curriculum", "activity", "student", "it", "general"]
VALID_ROLES = [
    "all_roles", "principal", "vice_principal",
    "panel_chair", "subject_head", "teacher", "eo_admin", "supplier"
]

# Maximum characters of vault text to send per LLM call (to stay within token limits)
MAX_CHUNK_CHARS = 12_000

# ---------------------------------------------------------------------------
# Vault header parser
# ---------------------------------------------------------------------------

def parse_vault_header(text: str) -> dict:
    """
    Extracts metadata from vault extract header lines starting with '# key: value'.
    Returns dict with keys: source_id, title, url, fact_type, topic_tags, etc.
    """
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
    """Split text into chunks at page boundaries (=== Page N ===) respecting max_chars."""
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
# OpenAI interaction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """你是一位香港教育制度專家，專門從教育局 (EDB) 官方文件中提煉出可供學校管理人員即時運用的精確事實規條。

你的任務：
1. 仔細閱讀提供的 EDB 原始文件段落
2. 從中提煉出 **具體、可執行、有明確門檻或數字** 的事實 (facts)
3. 每條 fact 必須簡潔（最多 80 字中文），並且內容必須能在原文中「找到對應出處」

以下是你需要遵守的 JSON output 格式（嚴格使用 JSON array）：
[
  {
    "proposed_text": "精煉後的事實短句（≤80字，中文優先）",
    "source_quote": "從原文逐字複製的對應段落（用於人工驗證）",
    "page_number": "發現此段落的頁數（數字例如 5，透過查看 === Page X === 標記找出）",
    "suggested_topic": "finance|hr|curriculum|activity|student|it|general 其中之一",
    "suggested_roles": ["principal", "vice_principal", "panel_chair", "subject_head", "teacher", "eo_admin", "supplier", "all_roles"],
    "confidence": "high|medium|low"
  }
]

規則：
- 只提取「政策規定、具體門檻、數字指標、明確義務」，不要泛論或描述性內容
- 如果原文是統計資料，只提取最新年度的關鍵數字
- suggested_roles 選擇該 fact 最相關的 1-3 個角色
- 如果 fact 適用於所有角色，使用 ["all_roles"]
- confidence=high 代表原文有明確數字或規定；medium 代表原文有清楚描述但需解讀；low 代表需要進一步核實
- 如果這份文件沒有可提取的具體 facts，回傳空 array []
- 只輸出 JSON，不要有其他文字
"""

def _sanitize_llm_json(raw: str) -> str:
    """
    Fix common LLM JSON output quirks before parsing:
      1. page_number: 18-19  →  "18-19"  (arithmetic expression → string)
      2. "text" "more text"  →  "text more text"  (Python-style adjacent string literals)
    """
    # Fix 1: page_number values that are bare arithmetic like 18-19, 24-25
    raw = re.sub(
        r'("page_number"\s*:\s*)(\d+\s*[-–]\s*\d+)',
        lambda m: m.group(1) + '"' + m.group(2).replace(' ', '') + '"',
        raw
    )
    # Fix 2: adjacent JSON string literals  "..." "..."  →  "... ..."
    # Matches: closing quote, optional whitespace/newlines, opening quote
    # Uses a two-pass approach: replace the pattern where it appears inside a value position
    raw = re.sub(r'"\s*\n\s+"', ' ', raw)
    return raw


def call_openai(api_key: str, vault_text: str, meta: dict) -> list[dict]:
    """Call OpenAI API to extract candidate facts from vault text."""
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

以下為原文摘錄：
"""

    all_candidates = []
    chunks = chunk_text(vault_text)

    for i, chunk in enumerate(chunks):
        print(f"  ⏳ Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...", file=sys.stderr)

        user_content = source_context + chunk

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "user", "content": SYSTEM_PROMPT + "\n\n" + user_content}
                ],
                max_completion_tokens=25000
            )

            raw = response.choices[0].message.content or ""
            raw = raw.strip()
            if not raw:
                print(f"  ⚠️  Empty response! Output object: {response.model_dump_json(indent=2)}", file=sys.stderr)

            # Strip markdown code blocks if the model wrapped it
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?", "", raw)
                raw = re.sub(r"```$", "", raw).strip()

            # Sanitize common LLM JSON quirks before parsing
            raw = _sanitize_llm_json(raw)

            parsed = json.loads(raw)

            # Handle both {"facts": [...]} and [...] formats
            if isinstance(parsed, dict):
                candidates = parsed.get("facts", parsed.get("candidates", parsed.get("results", [])))
            elif isinstance(parsed, list):
                candidates = parsed
            else:
                candidates = []

            all_candidates.extend(candidates)
        except json.JSONDecodeError as e:
            print(f"  ⚠️  JSON parse error on chunk {i+1}: {e}", file=sys.stderr)
            print(f"  --- RAW RESPONSE BEGIN ---\n{raw}\n  --- RAW RESPONSE END ---", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️  API error on chunk {i+1}: {e}", file=sys.stderr)

    return all_candidates


# ---------------------------------------------------------------------------
# Post-processing & validation
# ---------------------------------------------------------------------------

def validate_and_enrich(candidates: list[dict], meta: dict) -> list[dict]:
    """Validate candidate facts and enrich with source metadata + IDs."""
    valid = []
    for c in candidates:
        # Required fields check
        if not c.get("proposed_text") or not c.get("source_quote"):
            continue

        # Enforce length
        if len(c["proposed_text"]) > 120:
            c["proposed_text"] = c["proposed_text"][:117] + "..."

        # Validate topic
        topic = c.get("suggested_topic", "general")
        if topic not in VALID_TOPICS:
            topic = meta.get("topic_tags", "general").split(",")[0].strip()
            if topic not in VALID_TOPICS:
                topic = "general"
        c["suggested_topic"] = topic

        # Validate roles
        roles = c.get("suggested_roles", ["all_roles"])
        if not isinstance(roles, list):
            roles = [roles]
        roles = [r for r in roles if r in VALID_ROLES]
        if not roles:
            roles = ["all_roles"]
        c["suggested_roles"] = roles

        # Enrich with source metadata
        c["id"] = f"cand_{uuid.uuid4().hex[:8]}"
        c["source_id"] = meta.get("source_id", "unknown")
        c["source_title"] = meta.get("title", "未知來源")
        c["source_url"] = meta.get("url", "")
        
        valid.append(c)

    return valid


# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------

def resolve_api_key() -> str:
    """Resolve OPENAI_API_KEY from environment or backend/.env file."""
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    if BACKEND_ENV.exists():
        with open(BACKEND_ENV) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key

    print("ERROR: OPENAI_API_KEY not found in environment or backend/.env", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def load_vault_file(path: Path) -> tuple[str, dict]:
    """Load a vault extract file, return (full_text, parsed_header_meta)."""
    text = path.read_text(encoding="utf-8")
    meta = parse_vault_header(text)
    return text, meta


def collect_vault_files(path: Path) -> list[Path]:
    """If path is a dir, collect all .txt files; if file, return [path]."""
    if path.is_file():
        return [path]
    elif path.is_dir():
        files = sorted(path.glob("*.txt"))
        if not files:
            print(f"WARNING: No .txt files found in {path}", file=sys.stderr)
        return files
    else:
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        sys.exit(1)


def write_queue(candidates: list[dict], output_path: Path, append: bool):
    """Write candidates to the queue JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if append and output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            existing = []

    merged = existing + candidates

    json_str = json.dumps(merged, ensure_ascii=False, indent=2)
    output_path.write_text(json_str + "\n", encoding="utf-8")
    
    # Also write a .js file to bypass file:// CORS restrictions in local browsers
    js_path = output_path.with_suffix('.js')
    js_path.write_text(f"window.EXTERNAL_CANDIDATES = {json_str};\n", encoding="utf-8")
    
    return len(merged)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract candidate facts from EDB vault extracts using LLM"
    )
    parser.add_argument("input", type=Path,
                        help="Vault extract file (.txt) or directory containing .txt files")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"Output JSON path (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print extracted candidates to stdout without writing to file")
    parser.add_argument("--append", action="store_true",
                        help="Append to existing queue (default: overwrite)")
    parser.add_argument("--skip-low", action="store_true",
                        help="Skip candidates with confidence=low")

    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("🔬 EDB Knowledge Extraction Pipeline — Phase 3", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    api_key = resolve_api_key()
    print(f"✅ API key resolved ({api_key[:8]}...)", file=sys.stderr)

    files = collect_vault_files(args.input)
    print(f"📂 Found {len(files)} vault extract(s) to process", file=sys.stderr)

    all_candidates = []

    for filepath in files:
        print(f"\n── Processing: {filepath.name} ──", file=sys.stderr)
        text, meta = load_vault_file(filepath)
        print(f"   source_id: {meta.get('source_id', '?')}", file=sys.stderr)
        print(f"   title: {meta.get('title', '?')}", file=sys.stderr)
        print(f"   fact_type: {meta.get('fact_type', '?')}", file=sys.stderr)
        print(f"   text length: {len(text)} chars", file=sys.stderr)

        raw_candidates = call_openai(api_key, text, meta)
        print(f"   ✨ LLM returned {len(raw_candidates)} raw candidates", file=sys.stderr)

        validated = validate_and_enrich(raw_candidates, meta)
        print(f"   ✅ {len(validated)} candidates passed validation", file=sys.stderr)

        if args.skip_low:
            before = len(validated)
            validated = [c for c in validated if c.get("confidence") != "low"]
            skipped = before - len(validated)
            if skipped:
                print(f"   ⏭️  Skipped {skipped} low-confidence candidates", file=sys.stderr)

        all_candidates.extend(validated)

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"📊 Total candidates extracted: {len(all_candidates)}", file=sys.stderr)

    if args.dry_run:
        print(json.dumps(all_candidates, ensure_ascii=False, indent=2))
        print(f"\n🏁 Dry run complete — nothing written to disk.", file=sys.stderr)
    else:
        total = write_queue(all_candidates, args.output, args.append)
        print(f"💾 Written to: {args.output}", file=sys.stderr)
        print(f"   Queue now contains {total} candidate(s)", file=sys.stderr)
        print(f"\n🏁 Done! Open K1 Dashboard → Admin → 知識提煉 to review.", file=sys.stderr)


if __name__ == "__main__":
    main()
