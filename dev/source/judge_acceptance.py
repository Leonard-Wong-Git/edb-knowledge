#!/usr/bin/env python3
"""
judge_acceptance.py — acceptance harness for the anti-confabulation judge
(`RELEVANCE_JUDGE_PROMPT` in `backend/src/api/searchChannelB.ts`).

S196 measured that the shipped judge declines nearly everything (8/16, declining all
eight answerable cases) and wrote it up in `dev/source/JUDGE_PROMPT_FINDINGS.md`, but the
measurement script was never committed — so S199 had to rebuild it. This file is that
rebuild, kept so the next prompt candidate is scored against the same frozen set instead
of a freshly invented one.

WHAT IT MEASURES, AND WHY IT IS SPLIT IN TWO
--------------------------------------------
The judge sees (query, top-5 chunk text) and answers 能 / 否. Two failure directions are
NOT symmetric:

  * a false ANSWER on the decline half is the S177 class — the system invents a number
    (凍結教席 → "IMC 60%") and states it with conviction. One of these is worse than
    several declines.
  * a false DECLINE on the answer half costs a user a correct answer that is sitting
    verbatim in the retrieved text.

So accuracy alone is not a verdict. `--score` always reports `false_answers` separately,
and a candidate prompt that raises accuracy while adding a false answer is a regression.

WHY THE CHUNKS ARE CACHED
-------------------------
Chunks are fetched once from the live endpoint (`synthesize:false`) and stored, then
prompt variants are scored offline. That is what makes iteration free: no deploy, no
re-retrieval, and — more importantly — every variant is judged on byte-identical input,
so a difference between two runs is the prompt and nothing else.

THE ONE DISCIPLINE THIS FILE EXISTS TO ENFORCE
----------------------------------------------
The 16 cases in JUDGE_PROMPT_FINDINGS were assembled and then iterated against, which is
why V3's 11/16 is a tuned number that will not hold on unseen queries. The case set here
is frozen in `judge_acceptance_cases.json` BEFORE any verdict was seen, and every label
was set by reading the retrieved passage, not by keyword search. Rules for anyone
extending it:

  1. Do not add, remove or re-label a case because a prompt scored badly on it. The only
     legitimate re-label is "I opened the passage and my original label was wrong", and
     it must be recorded in the case's `label_note` with what was read.
  2. `want` = 能 requires that the specific thing asked is present in the CACHED chunks —
     not merely that the corpus contains it somewhere. The judge is only shown those.
  3. New answer-half cases come from a curated footnote's OWN question (footnotes are
     written `<question>？<answer>`, so the question was authored by whoever curated the
     fact, not by whoever is tuning the prompt). New decline-half cases must be checked
     by reading the top-5, because a keyword miss is not evidence of absence.

Read-only against production: POSTs the public search endpoint and calls the OpenAI
Responses API exactly as `llmClient.ts` does. Writes nothing but its own run files.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
CASES_PATH = HERE / "judge_acceptance_cases.json"
RUNS_DIR = HERE / "judge_runs"
CACHE_PATH = RUNS_DIR / "chunks_cache.json"

ENDPOINT = "https://edb-knowledge.onrender.com/api/search/channel-b"

# Mirror of production: `createLlmClient()` uses the Responses API with the model from
# `getOpenAIModel()`, whose default is gpt-4.1-nano, and sets no temperature. If Render
# ever sets OPENAI_MODEL, this constant must follow it or the measurement stops
# describing production.
JUDGE_MODEL = "gpt-4.1-nano"

# Verbatim copy of RELEVANCE_JUDGE_PROMPT (searchChannelB.ts). Kept as a literal rather
# than parsed out of the TypeScript so that a drift between the two is a visible diff in
# this file's history; `--check-parity` compares them.
SHIPPED_PROMPT = """以下是從教育局文件檢索到的資料。請判斷這些資料能否「明確、直接」回答用戶的問題。

從嚴判斷（寧緊莫鬆）：只有當資料實際、明確包含問題所問的「具體答案」（所問的數字／上限／比例／條件／規則本身）時，才答「能」。若資料只是同一大主題但其實在講另一件事、或資料未必直接答到所問事項、或你有任何不確定，一律答「否」。寧可答否，也不要勉強當作能——答錯一個數字會誤導用戶，比答找不到更差。

只回答一個字：能 或 否。

問題：{QUERY}

資料：
{CHUNKS}"""


# ---------------------------------------------------------------------------
# Small helpers (pure — covered by --self-test)
# ---------------------------------------------------------------------------

def extract_question(text: str) -> str:
    """Curated footnotes are written '<question>？<answer>'. Mirrors
    footnote_lead_probe.extract_question so both tools sample the same way."""
    t = (text or "").strip()
    for mark in ("？", "?"):
        i = t.find(mark)
        if 0 < i <= 60:
            return t[: i + 1]
    return t[:40]


def is_question_led(text: str) -> bool:
    """A footnote whose text opens with a citation (《...》) has no usable own-question;
    extract_question would return a fragment of the citation instead. Those are dropped
    from sampling rather than hand-repaired, so the sample stays mechanical."""
    t = (text or "").strip()
    if t.startswith("《"):
        return False
    q = extract_question(t)
    return q.endswith("？") or q.endswith("?")


def chunk_block(chunks: list[str]) -> str:
    """Production hands the judge the same [n]-numbered block it hands the synthesiser."""
    return "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(chunks))


def verdict_is_answer(raw: str) -> bool:
    """Production: `verdict.startsWith("能")` — anything else, including noise, declines."""
    return (raw or "").strip().startswith("能")


def score_cases(cases: list[dict], verdicts: dict[str, str], scope: str = "primary") -> dict:
    """Split accuracy by direction. A false answer (want=否, judged 能) is the S177 class
    and is reported on its own line, never folded into a single accuracy number.

    `scope="primary"` scores only cases whose label was read off a passage; `"all"` adds
    the secondary (bare-noun topical) cases, whose label is a project position. Mixing the
    two into one headline would let a debatable label carry a measured claim."""
    out = {
        "scope": scope, "n": 0, "correct": 0,
        "answer_half": {"n": 0, "correct": 0},
        "decline_half": {"n": 0, "correct": 0},
        "false_answers": [], "false_declines": [], "missing": [],
    }
    for c in cases:
        if scope == "primary" and c.get("scope", "primary") != "primary":
            continue
        cid = c["id"]
        if cid not in verdicts:
            out["missing"].append(cid)
            continue
        said_answer = verdict_is_answer(verdicts[cid])
        want_answer = c["want"] == "能"
        half = "answer_half" if want_answer else "decline_half"
        out["n"] += 1
        out[half]["n"] += 1
        if said_answer == want_answer:
            out["correct"] += 1
            out[half]["correct"] += 1
        elif said_answer:
            out["false_answers"].append(cid)
        else:
            out["false_declines"].append(cid)
    return out


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_env_value(name: str) -> str | None:
    v = os.environ.get(name)
    if v:
        return v.strip()
    env_path = REPO_ROOT / "backend" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{name}=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_cases() -> list[dict]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]


def fetch_chunks(query: str, retries: int = 2) -> list[str]:
    """Top-5 chunk text exactly as synthesizeAnswer would see it. `synthesize:false` keeps
    this read-only and cheap; a 429/timeout is retried, never silently recorded as empty
    (a false zero here would look like 'the corpus has nothing', the very error the whole
    exercise is about)."""
    body = json.dumps({"query": query, "synthesize": False}).encode("utf-8")
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                ENDPOINT, data=body,
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                payload = json.load(r)
            results = payload.get("results") or []
            return [r.get("text", "") for r in results[:5]]
        except Exception as exc:  # noqa: BLE001 — reported, not swallowed
            last = exc
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"retrieval failed for {query!r}: {last}")


def call_judge(prompt: str, api_key: str, retries: int = 2) -> str:
    """Same call shape as llmClient.ts: POST /v1/responses with {model, input}."""
    body = json.dumps({"model": JUDGE_MODEL, "input": prompt}).encode("utf-8")
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                "https://api.openai.com/v1/responses", data=body,
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                payload = json.load(r)
            for item in payload.get("output", []):
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        return part.get("text", "").strip()
            return ""
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"judge call failed: {last}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_fetch(pace: float) -> int:
    cases = load_cases()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    for c in cases:
        cid = c["id"]
        if c.get("chunk_mode") == "fixed":
            cache[cid] = {"query": c["query"], "chunks": c["chunks"], "source": "fixed"}
            continue
        if cid in cache and cache[cid].get("chunks"):
            continue
        chunks = fetch_chunks(c["query"])
        cache[cid] = {"query": c["query"], "chunks": chunks, "source": "live",
                      "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        print(f"  fetched {cid}: {len(chunks)} chunks")
        time.sleep(pace)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"cache: {len(cache)} cases -> {CACHE_PATH}")
    return 0


def cmd_score(prompt_path: str | None, out_path: str | None, pace: float, label: str) -> int:
    cases = load_cases()
    if not CACHE_PATH.exists():
        sys.exit("no chunk cache — run --fetch first")
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    prompt_tpl = (Path(prompt_path).read_text(encoding="utf-8") if prompt_path
                  else SHIPPED_PROMPT)
    api_key = read_env_value("OPENAI_API_KEY")
    if not api_key:
        sys.exit("no OPENAI_API_KEY (env or backend/.env)")

    verdicts, raws = {}, {}
    for c in cases:
        cid = c["id"]
        entry = cache.get(cid)
        if not entry or not entry.get("chunks"):
            print(f"  !! {cid}: no cached chunks, skipped")
            continue
        prompt = (prompt_tpl
                  .replace("{QUERY}", c["query"])
                  .replace("{CHUNKS}", chunk_block(entry["chunks"])))
        raw = call_judge(prompt, api_key)
        verdicts[cid] = raw
        raws[cid] = raw
        mark = "能" if verdict_is_answer(raw) else "否"
        ok = "ok " if mark == c["want"] else "MISS"
        print(f"  {ok} {cid:<28} want={c['want']} got={mark} ({raw[:12]!r})")
        time.sleep(pace)

    summary = score_cases(cases, verdicts, scope="primary")
    secondary = score_cases(cases, verdicts, scope="all")
    print("\n" + "=" * 68)
    print(f"prompt: {label}   model: {JUDGE_MODEL}")
    print(f"PRIMARY      {summary['correct']}/{summary['n']}")
    print(f"  answer half  {summary['answer_half']['correct']}/{summary['answer_half']['n']}"
          f"   (false declines: {len(summary['false_declines'])})")
    print(f"  decline half {summary['decline_half']['correct']}/{summary['decline_half']['n']}"
          f"   (FALSE ANSWERS: {len(summary['false_answers'])})")
    if summary["false_answers"]:
        print(f"  !! false answers: {', '.join(summary['false_answers'])}")
    if summary["false_declines"]:
        print(f"  false declines: {', '.join(summary['false_declines'])}")
    print(f"incl. secondary  {secondary['correct']}/{secondary['n']}"
          f"   (bare-noun cases scored apart — see cases file _meta.scoring)")
    print("=" * 68)

    if out_path:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps({
            "label": label, "model": JUDGE_MODEL,
            "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "summary": summary, "verdicts": raws,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"run written -> {out_path}")
    return 0


def cmd_check_parity() -> int:
    """The shipped prompt is duplicated here; prove the copy still matches the source."""
    ts = (REPO_ROOT / "backend" / "src" / "api" / "searchChannelB.ts").read_text(encoding="utf-8")
    start = ts.find("const RELEVANCE_JUDGE_PROMPT = `")
    if start < 0:
        print("FAIL: RELEVANCE_JUDGE_PROMPT not found in searchChannelB.ts")
        return 1
    body_start = ts.index("`", start) + 1
    body_end = ts.index("`;", body_start)
    shipped = ts[body_start:body_end]
    if shipped == SHIPPED_PROMPT:
        print("parity OK: SHIPPED_PROMPT is byte-identical to searchChannelB.ts")
        return 0
    print("FAIL: SHIPPED_PROMPT has drifted from searchChannelB.ts")
    print(f"  harness {len(SHIPPED_PROMPT)} chars / source {len(shipped)} chars")
    return 1


def self_test() -> int:
    failures = []

    def check(name: str, cond: bool) -> None:
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            failures.append(name)

    check("question split", extract_question("邊個負責？答案在此。") == "邊個負責？")
    check("citation-led footnote rejected", not is_question_led("《學校行政手冊》附錄9：病假…"))
    check("question-led footnote accepted", is_question_led("空調津貼點計算？採等值公式…"))
    check("no-question footnote rejected", not is_question_led("一段冇問號嘅長描述" * 5))
    check("chunk block numbering", chunk_block(["a", "b"]) == "[1] a\n\n[2] b")
    check("verdict 能 = answer", verdict_is_answer("能"))
    check("verdict 否 = decline", not verdict_is_answer("否"))
    check("verdict noise = decline", not verdict_is_answer("我認為資料不足"))
    check("verdict 能 with trailing text still answers", verdict_is_answer("能。"))

    cases = [
        {"id": "a1", "want": "能"}, {"id": "a2", "want": "能"},
        {"id": "d1", "want": "否"}, {"id": "d2", "want": "否"},
    ]
    s = score_cases(cases, {"a1": "能", "a2": "否", "d1": "否", "d2": "能"})
    check("scoring: overall", s["correct"] == 2 and s["n"] == 4)
    check("scoring: halves counted apart",
          s["answer_half"] == {"n": 2, "correct": 1} and s["decline_half"] == {"n": 2, "correct": 1})
    check("scoring: false answer isolated", s["false_answers"] == ["d2"])
    check("scoring: false decline isolated", s["false_declines"] == ["a2"])
    s2 = score_cases(cases, {"a1": "能"})
    check("scoring: missing verdicts not counted as correct",
          s2["n"] == 1 and sorted(s2["missing"]) == ["a2", "d1", "d2"])

    # Deliberate break: a prompt that answers everything must NOT look perfect. This
    # guard exists because "answers more" is the failure mode the whole exercise guards
    # against — if it ever reads as an improvement, the scorer is broken.
    s3 = score_cases(cases, {c["id"]: "能" for c in cases})
    check("guard: answer-everything scores 2/4 with 2 false answers",
          s3["correct"] == 2 and len(s3["false_answers"]) == 2)

    scoped = [{"id": "p1", "want": "能", "scope": "primary"},
              {"id": "s1", "want": "能", "scope": "secondary"}]
    v = {"p1": "能", "s1": "否"}
    check("scope: primary excludes secondary cases",
          score_cases(scoped, v, "primary")["n"] == 1)
    check("scope: all includes them", score_cases(scoped, v, "all")["n"] == 2)
    check("scope: a secondary miss cannot dent the primary number",
          score_cases(scoped, v, "primary")["correct"] == 1
          and score_cases(scoped, v, "all")["correct"] == 1)

    if CASES_PATH.exists():
        cs = load_cases()
        ids = [c["id"] for c in cs]
        check("case ids unique", len(ids) == len(set(ids)))
        check("every case has a verified label note",
              all(c.get("label_note") for c in cs))
        check("both halves populated",
              any(c["want"] == "能" for c in cs) and any(c["want"] == "否" for c in cs))
        check("fixed-chunk cases carry their chunks",
              all(c.get("chunks") for c in cs if c.get("chunk_mode") == "fixed"))

    print(f"\nself-test: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="offline assertions, no network")
    ap.add_argument("--check-parity", action="store_true",
                    help="verify SHIPPED_PROMPT still matches searchChannelB.ts")
    ap.add_argument("--fetch", action="store_true", help="cache top-5 chunks per case")
    ap.add_argument("--score", action="store_true", help="score a prompt over the cache")
    ap.add_argument("--prompt", help="path to a candidate prompt (default: shipped)")
    ap.add_argument("--label", default="shipped", help="label recorded in the run file")
    ap.add_argument("--out", help="write the run JSON here")
    ap.add_argument("--pace", type=float, default=1.0, help="seconds between calls")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.check_parity:
        return cmd_check_parity()
    if args.fetch:
        return cmd_fetch(args.pace)
    if args.score:
        return cmd_score(args.prompt, args.out, args.pace, args.label)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
