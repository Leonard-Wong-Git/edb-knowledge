#!/usr/bin/env python3
"""test_synthesis_guard.py — task 2: two-step anti-confabulation guard A/B test.

Does NOT touch production code. Approach: a cheap binary relevance JUDGE decides whether
the retrieved chunks can directly answer the query.
  - judge=YES -> run the ORIGINAL synthesis prompt unchanged (no over-refusal risk)
  - judge=NO  -> return a fixed "找不到直接資料" message (no fabrication)

Why two-step (vs one anti-confab prompt): gpt-4.1-nano cannot reliably judge-AND-answer in
one shot — it over-refuses on-topic queries (verified). A standalone binary judge is far
more accurate for a small model.

Scenarios: A/C on-topic (judge should say YES) ; B/D off-topic (judge should say NO,
B = the original 凍結教席 60% confabulation case).
Env: OPENAI_API_KEY from backend/.env.
"""
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
MODEL = "gpt-4.1-nano"


def api_key():
    k = os.environ.get("OPENAI_API_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return k


# Original production synthesis prompt — UNCHANGED (used on judge=YES path).
SYNTH_PROMPT = """你是香港學校管治的政策顧問。以下是從教育局政策文件中檢索到的相關資料。
請根據這些資料，用繁體中文綜合分析並回答問題，緊扣資料重點，約250字（上限300字），不需列出來源編號。

問題：{QUERY}

政策資料：
{CHUNKS}"""

# Binary relevance judge — small, single-purpose; small models do this far better than
# judge-and-answer in one shot.
JUDGE_PROMPT = """以下是從教育局文件檢索到的資料。請判斷這些資料能否「明確、直接」回答用戶的問題。

從嚴判斷（寧緊莫鬆）：只有當資料實際、明確包含問題所問的「具體答案」（所問的數字／上限／比例／條件／規則本身）時，才答「能」。若資料只是同一大主題但其實在講另一件事、或資料未必直接答到所問事項、或你有任何不確定，一律答「否」。寧可答否，也不要勉強當作能——答錯一個數字會誤導用戶，比如實答找不到更差。

只回答一個字：能 或 否。

問題：{QUERY}

資料：
{CHUNKS}"""

DECLINE_MSG = "根據檢索到的教育局文件，暫時未能找到可直接回答此問題的明確資料。下方為主題相關的原始文件，或可參考；亦可嘗試以其他關鍵詞重新搜尋。"

SCENARIOS = {
    "A 對題 病假（YES→答）": {
        "expect": "能",
        "query": "教師有薪病假有幾多日？",
        "chunks": [
            "資助學校常額教師的有薪病假：首次服務的第一年可享有28天有薪病假，其後每滿一年可享有全年48天有薪病假，有薪病假可累積至168天。",
            "如教師中斷服務超過一年，會喪失已積存的有薪病假。",
        ],
    },
    "B 唔對題 凍結教席（NO→拒，原 60% bug）": {
        "expect": "否",
        "query": "現在已成立法團校董會學校可以凍結的教席上限是百分之幾？",
        "chunks": [
            "計算法團校董會「辦學團體校董」60%人數上限時，替代校董計唔計？《法團校董會的成立與運作》附錄1：計算辦學團體校董人數上限（不得超過校董人數上限嘅60%）時，替代校董不計算在內。",
            "校本管理組有關法團校董會的問與答（簡介會答問摘要）：一、成立法團校董會；二、校董會組成；三、校董註冊。",
            "辦學團體可將設立法團校董會的意向以書面通知常任秘書長，須於不遲於預計開課日期前6個月通知。",
            "雖然條例沒有限制校董人數上限，但如法團校董會的成員人數過多，則可能影響運作；校董人數約有十人。",
            "設有法團校董會的學校只須因應學生／家長的要求發出正式收據。",
        ],
    },
    "C 對題 採購（YES→答）": {
        "expect": "能",
        "query": "學校採購要幾多個書面報價？",
        "chunks": [
            "學校採購貨品或服務，款額超過$5,000但不超過$50,000，須取得不少於兩份書面報價；超過$50,000但不超過$1,400,000，須取得不少於五份書面報價。",
            "採購須符合公開、公平、具成本效益的原則。",
        ],
    },
    "D 唔對題 師生比例（NO→拒）": {
        "expect": "否",
        "query": "幼稚園每班師生比例上限係幾多？",
        "chunks": [
            "學校曆：2025/26學年的公眾假期及學校假期安排，包括農曆新年、復活節及暑假的日期。",
            "全年上學日數不少於190天。",
            "學校須在開課前公布校曆。",
        ],
    },
    "E 邊緣 部分相關（保守→否）": {
        "expect": "否",
        "query": "資助學校教師的退休年齡係幾多歲？",
        "chunks": [
            "學校教職員的聘任須遵守教統局通告規定，考慮學歷、經驗及專業操守。",
            "教師須持有認可教師資格並向教育局註冊；常額教師按連續性合約受聘。",
            "校長為學校的教育領導，負責人事管理及校務運作。",
        ],
    },
}


def chat(prompt, temperature=0.3, max_tokens=400):
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
              "temperature": temperature, "max_tokens": max_tokens},
        timeout=90,
    )
    if r.status_code != 200:
        return f"<API {r.status_code}: {r.text[:120]}>"
    return r.json()["choices"][0]["message"]["content"].strip()


def two_step(query, chunks):
    chunk_text = "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(chunks))
    verdict = chat(JUDGE_PROMPT.replace("{QUERY}", query).replace("{CHUNKS}", chunk_text),
                   temperature=0, max_tokens=4)
    can_answer = verdict.startswith("能")
    if can_answer:
        out = chat(SYNTH_PROMPT.replace("{QUERY}", query).replace("{CHUNKS}", chunk_text))
    else:
        out = DECLINE_MSG
    return verdict, can_answer, out


def main():
    passed = 0
    for name, sc in SCENARIOS.items():
        verdict, can_answer, out = two_step(sc["query"], sc["chunks"])
        ok = verdict.startswith(sc["expect"])
        passed += ok
        print("=" * 70)
        print(f"{name}  | judge={verdict!r} expect={sc['expect']!r} -> {'PASS' if ok else 'FAIL'}")
        print("-" * 70)
        print(out[:300])
        print()
    print(f"=== judge accuracy: {passed}/{len(SCENARIOS)} ===")


if __name__ == "__main__":
    main()
