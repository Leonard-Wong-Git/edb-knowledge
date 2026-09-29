#!/usr/bin/env python3
"""live_probe.py — is the live service actually answering users? (S234)

WHY THIS EXISTS
Nothing watched the running service between the daily QC report runs, and the QC
report only repaints a page — it never tells anyone. So an outage was found the
day Leonard happened to open the status page. `backend_build_check` only runs on
push and pull request; the watchdog only knows whether the *monitors* ran.

WHAT IT PROBES — two things, on purpose
  1. `/health` answers `ok:true`.
  2. A real search returns at least one passage.
`/health` alone is not enough: it is served off the Channel A cache and touches
neither the embedding provider nor Supabase. On 2026-09-03 it reported healthy
while every search on the site returned 429 "no credits remaining" (see
qc_report.check_search_live). The search probe goes through the same path a user
takes — key, quota, embedding, Supabase RPC, route filter — in one call.

RETRY, NOT STATE
A Render free-tier instance sleeps and needs a while to wake, so one failed
attempt is not an outage. The run therefore tries, waits, and tries once more;
only two failures in a row count. Doing it inside one run keeps the workflow
stateless — no ledger to race, nothing to commit.

EXIT CODES (project convention S126: only a broken *instrument* fails a run)
  0  the probe ran to completion — whether the service was up OR down. A down
     service is a finding, reported through the JSON and the issue step.
  1  the probe itself crashed. The watchdog counts that as a broken monitor.

The request carries `x-probe: 1`, so the backend neither logs it (search_log) nor
counts it as user usage.

    python3 dev/source/live_probe.py --self-test
    python3 dev/source/live_probe.py --check --json-out live_probe.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Callable, Optional

HEALTH_URL = "https://edb-knowledge.onrender.com/health"
SEARCH_URL = "https://edb-knowledge.onrender.com/api/search/channel-b"
PROBE_QUERY = "教師病假"          # same query as qc_report.py, so the two agree
HEALTH_TIMEOUT = 75              # cold start of a sleeping instance
SEARCH_TIMEOUT = 100
RETRY_WAIT_SECONDS = 120
ATTEMPTS = 2

# (status, body) — status 0 means the request never got an HTTP answer.
Fetch = Callable[[str, Optional[dict], int], "tuple[int, object]"]


def _fetch(url: str, payload: Optional[dict], timeout: int):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"x-probe": "1"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except (ValueError, OSError):
            return e.code, None
    except (OSError, ValueError) as e:  # URLError, timeout, bad JSON
        return 0, {"error": str(e)[:200]}


def judge(health: dict, search: dict) -> bool:
    """The whole definition of "the service is up". Kept pure so the self-test
    can hold it to the 2026-09-03 case."""
    return bool(health.get("ok")) and bool(search.get("ok"))


def probe_once(fetch: Fetch) -> dict:
    hs, hbody = fetch(HEALTH_URL, None, HEALTH_TIMEOUT)
    hbody = hbody if isinstance(hbody, dict) else {}
    health = {"ok": hs == 200 and bool(hbody.get("ok")), "http": hs,
              "commit": hbody.get("commit"),
              "error": hbody.get("error") if hs != 200 else None}

    ss, sbody = fetch(SEARCH_URL, {"query": PROBE_QUERY, "top_k": 3,
                                   "synthesize": False}, SEARCH_TIMEOUT)
    sbody = sbody if isinstance(sbody, dict) else {}
    n = len(sbody.get("results") or [])
    search = {"ok": ss == 200 and not sbody.get("error") and n > 0,
              "http": ss, "results": n,
              "error": (str(sbody.get("error"))[:200] if sbody.get("error")
                        else (f"HTTP {ss}" if ss != 200 else None))}
    return {"health": health, "search": search, "up": judge(health, search)}


def run_probe(fetch: Fetch, sleep: Callable[[float], None] = time.sleep,
              wait: int = RETRY_WAIT_SECONDS, attempts: int = ATTEMPTS) -> dict:
    last: dict = {}
    for i in range(1, attempts + 1):
        last = probe_once(fetch)
        last["attempt"] = i
        if last["up"]:
            break
        if i < attempts:
            sleep(wait)
    return {"checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "up": last["up"], "attempts": last["attempt"],
            "health": last["health"], "search": last["search"]}


# ---------------------------------------------------------------------------
# self-test — offline, injected fetch
# ---------------------------------------------------------------------------

def _script(*answers):
    """A fetch that replays canned answers in order: (health, search) per attempt."""
    seq = [a for pair in answers for a in pair]
    it = iter(seq)

    def f(url, payload, timeout):
        return next(it)
    return f


OK_H = (200, {"ok": True, "commit": "abc1234"})
OK_S = (200, {"results": [{"id": 1}, {"id": 2}]})
DOWN_H = (0, {"error": "timed out"})
DOWN_S = (0, {"error": "timed out"})


def _run_self_test(judge_fn=judge) -> "list[str]":
    global judge
    real = judge
    judge = judge_fn
    fails: list[str] = []
    nosleep = lambda s: None

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    try:
        r = run_probe(_script((OK_H, OK_S)), nosleep)
        check("全部正常 → up，只試一次", r["up"] and r["attempts"] == 1)

        r = run_probe(_script((DOWN_H, DOWN_S), (OK_H, OK_S)), nosleep)
        check("第一次失敗、重試成功 → up（冷啟動不算當機）", r["up"] and r["attempts"] == 2)

        r = run_probe(_script((DOWN_H, DOWN_S), (DOWN_H, DOWN_S)), nosleep)
        check("連續兩次失敗 → down", (not r["up"]) and r["attempts"] == 2)

        # 2026-09-03：/health 報 ok，搜尋卻 429
        r = run_probe(_script((OK_H, (429, {"error": "You have no credits remaining"})),
                              (OK_H, (429, {"error": "You have no credits remaining"}))), nosleep)
        check("/health 正常但搜尋 429 → down（2026-09-03 的個案）", not r["up"])

        r = run_probe(_script((OK_H, (200, {"results": []})),
                              (OK_H, (200, {"results": []}))), nosleep)
        check("搜尋回 200 但零片段 → down", not r["up"])

        r = run_probe(_script(((200, {"ok": False}), OK_S),
                              ((200, {"ok": False}), OK_S)), nosleep)
        check("/health 回 ok:false → down", not r["up"])

        waits: list = []
        run_probe(_script((DOWN_H, DOWN_S), (DOWN_H, DOWN_S)), waits.append, wait=7)
        check("兩次之間真的有等待（不是連環急打）", waits == [7])

        both = (200, {"results": [{"id": 1}], "error": "boom"})
        r = run_probe(_script((OK_H, both), (OK_H, both)), nosleep)
        check("回應同時帶 results 與 error → 不當作正常", not r["search"]["ok"])
    finally:
        judge = real
    return fails


def self_test() -> int:
    print("live_probe self-test\n")
    fails = _run_self_test()

    # 證明測試會轉紅：把判斷換成「永遠正常」，「當機」那幾條必須失敗。
    print("\n以「永遠正常」取代真判斷，當機類斷言必須轉紅：")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        broken = _run_self_test(judge_fn=lambda h, s: True)
    fired = [l for l in buf.getvalue().splitlines() if l.strip().startswith("FAIL")]
    print(f"  轉紅 {len(fired)} 條")
    if len(fired) < 4:
        fails.append("prove-red: 換成永遠正常後轉紅少於 4 條，斷言抓不到當機")
        print("  FAIL  斷言抓不到當機")
    else:
        print("  PASS  斷言抓得到當機")

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json-out", default="live_probe.json")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.check:
        ap.print_help()
        return 2

    try:
        rep = run_probe(_fetch)
    except Exception as e:  # the instrument crashed — that is the only exit 1
        print(f"probe crashed: {e!r}", file=sys.stderr)
        return 1
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"up={rep['up']} attempts={rep['attempts']} "
          f"health={rep['health']['ok']}(http {rep['health']['http']}) "
          f"search={rep['search']['ok']}(http {rep['search']['http']}, "
          f"{rep['search']['results']} results)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
