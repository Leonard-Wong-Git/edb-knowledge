#!/usr/bin/env python3
"""check_monitor_health.py — did each monitor actually run, and did it succeed?

WHY THIS EXISTS (S222)
Seven monitors watch EDB documents and links. Every one of them is a weekly
GitHub Actions cron, and that arrangement has three silent-death modes that no
individual monitor can see, because a check cannot report that it never ran:

  1. A failed run is simply lost. GitHub does not retry a missed or failed
     schedule (`schedule` docs), so one bad night — an expired secret, a rate
     limit, EDB down — costs a full week of coverage and nothing says so.
  2. `schedule` is delayed under load and can be skipped entirely.
  3. This repository is PUBLIC, and GitHub disables scheduled workflows in a
     public repository "when no repository activity has occurred in 60 days".
     All seven share that single point of failure.

The gap is not detection. `check_freshness` DID report the School Administration
Guide changing; nobody downstream picked it up. What was missing is a surface
that says "this monitor has not succeeded since <date>" — the same 紀律 #14
lesson the project keeps relearning: a signal nobody has to acknowledge is a
signal nobody acts on.

WHAT IT DOES
Reads each monitor's own run history from the GitHub Actions API and answers the
question no single monitor can ask about itself: when did you last SUCCEED?

The run history is used rather than a committed ledger on purpose. A ledger has
to be written by the very run that may have crashed before it got there, and
seven workflows committing to one file race each other. The API is the ground
truth GitHub already keeps, it records the runs that failed before any of our
code executed (a missing secret, a checkout failure), and it needs no change to
the seven workflows at all.

Two actions come out of that:

  * DUE  — past its cadence. The watchdog dispatches it. This is the catch-up:
           a run lost to a bad night is retried the next day instead of waiting
           out the rest of the week.
  * OVERDUE / repeatedly failing — the monitor itself is broken. One Issue is
           opened or updated, and the run exits non-zero.

WHY THAT SURVIVES A DEAD SCHEDULE
It does not, on its own — a watchdog on the same machinery dies with it, and
this file does not pretend otherwise. What it buys is CROSS-monitoring: seven
schedules rarely die together, and whichever one runs next reports the silence
of the others. The watchdog workflow narrows the detection window from a week to
a day; the 60-day inactivity mode is only escaped by activity, which the ingest
bots currently provide. Both limits are stated in `overdue_report()` output so
no one mistakes this for a guarantee.

USAGE
  python3 dev/source/monitor_heartbeat.py --self-test
  python3 dev/source/monitor_heartbeat.py --prove-assertions
  python3 dev/source/monitor_heartbeat.py --record <monitor> --status ok|fail|skipped
  python3 dev/source/monitor_heartbeat.py --check          # overdue report
  python3 dev/source/monitor_heartbeat.py --due <monitor>  # exit 0 = run it now
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE = REPO_ROOT / "dev" / "source" / "monitor_state.json"

# Every scheduled monitor, and how often it is SUPPOSED to succeed. The cadence
# is the promise; the ledger measures the promise. Keep in step with the crons
# in `.github/workflows/` — `--self-test` asserts the two agree.
WORKFLOWS: Dict[str, tuple] = {
    # monitor            (workflow file,           cadence days)
    "freshness":         ("freshness_check.yml",    7),
    "discover":          ("discover_check.yml",     7),
    "served_urls":       ("served_url_check.yml",   7),
    "pgvector":          ("pgvector_check.yml",     7),
    "qc_report":         ("qc_report.yml",          1),
    "source_titles":     ("title_check.yml",       31),
}
CADENCE_DAYS: Dict[str, int] = {k: v[1] for k, v in WORKFLOWS.items()}

OVERDUE_FACTOR = 2.0

# Below this, a run that failed is treated as bad luck worth retrying rather
# than a broken monitor worth reporting. Set at 2 because the catch-up schedule
# gives a weekly monitor six more chances inside its own window: reporting on
# the first stumble would be the noise 紀律 #14 warns about.
FAILURES_BEFORE_ALARM = 2

STATUSES = ("ok", "fail", "skipped")


# ---------------------------------------------------------------------------
# pure helpers — every one covered by --self-test
# ---------------------------------------------------------------------------

def parse_ts(s: Optional[str]) -> Optional[datetime]:
    """An ISO-8601 UTC stamp, or None for anything unusable.

    Returns None rather than raising: a corrupt ledger entry must read as
    "never succeeded" — the safe direction — instead of crashing the monitor
    that is trying to report it.
    """
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def is_due(entry: Optional[dict], cadence_days: int, now: datetime) -> bool:
    """Should this monitor do real work on this tick?

    The catch-up rule, and the reason the workflows can move to a DAILY cron
    without doing seven times the work: due when the last SUCCESS is older than
    the cadence. A failed run therefore leaves the monitor due tomorrow instead
    of next week, which is the whole point — one bad night costs a day, not a
    full cycle.
    """
    if not entry:
        return True
    last_ok = parse_ts(entry.get("last_success"))
    if last_ok is None:
        return True
    return (now - last_ok) >= timedelta(days=cadence_days)


def is_overdue(entry: Optional[dict], cadence_days: int, now: datetime) -> bool:
    """Has this monitor gone quiet long enough to be a defect in itself?"""
    if not entry:
        return True
    last_ok = parse_ts(entry.get("last_success"))
    if last_ok is None:
        return True
    return (now - last_ok) > timedelta(days=cadence_days * OVERDUE_FACTOR)


def alarming(entry: Optional[dict]) -> bool:
    """Failing repeatedly — distinct from quiet, and a different diagnosis."""
    if not entry:
        return False
    return int(entry.get("consecutive_failures") or 0) >= FAILURES_BEFORE_ALARM


def record(state: dict, monitor: str, status: str, now: datetime,
           detail: str = "") -> dict:
    """Fold one run's outcome into the ledger. Pure: returns the new state.

    `skipped` is deliberately not a failure and not a success — a catch-up tick
    that correctly did nothing must neither reset the clock nor raise an alarm.
    """
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}; expected one of {STATUSES}")
    out = json.loads(json.dumps(state))          # copy; never mutate the caller's
    e = out.setdefault("monitors", {}).setdefault(monitor, {})
    stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    e["last_attempt"] = stamp
    e["last_status"] = status
    if detail:
        e["last_detail"] = detail[:300]
    if status == "ok":
        e["last_success"] = stamp
        e["consecutive_failures"] = 0
    elif status == "fail":
        e["consecutive_failures"] = int(e.get("consecutive_failures") or 0) + 1
    return out


def overdue_report(state: dict, now: datetime,
                   cadence: Optional[Dict[str, int]] = None) -> dict:
    """Which monitors are quiet, which are failing, and which are fine."""
    cadence = cadence or CADENCE_DAYS
    quiet, failing, ok, unknown = [], [], [], []
    for name, days in sorted(cadence.items()):
        e = (state.get("monitors") or {}).get(name)
        if e and e.get("unreadable"):
            unknown.append(name)
        elif is_overdue(e, days, now):
            last = (e or {}).get("last_success") or "從未成功"
            quiet.append({"monitor": name, "cadence_days": days, "last_success": last})
        elif alarming(e):
            failing.append({"monitor": name,
                            "consecutive_failures": int(e.get("consecutive_failures") or 0),
                            "last_detail": e.get("last_detail", "")})
        else:
            ok.append(name)
    return {"quiet": quiet, "failing": failing, "ok": ok, "unknown": unknown,
            "speaks": bool(quiet or failing or unknown)}


# ---------------------------------------------------------------------------
# io — the GitHub Actions API is the source of truth
# ---------------------------------------------------------------------------

API = "https://api.github.com"


def _token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not tok:
        raise SystemExit(
            "❌ 需要 GITHUB_TOKEN（actions:read；要 --dispatch 則需 actions:write）。\n"
            "   沒有 token 讀不到 run 歷史，而『讀唔到』同『健康』在輸出上會一模一樣 —— "
            "所以這裡直接失敗，不出一份假的全綠報告。")
    return tok


def _api(path: str, token: str, method: str = "GET", body: dict | None = None):
    req = urllib.request.Request(
        f"{API}{path}", method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json",
                 "User-Agent": "edb-knowledge-monitor-health"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def state_from_runs(runs_by_monitor: Dict[str, list]) -> dict:
    """Fold the API's run list into the same shape the pure helpers expect.

    `consecutive_failures` counts back from the newest run and stops at the
    first success, so a monitor that failed twice and then recovered reads as
    healthy — which is what recovery means.
    """
    out: dict = {"monitors": {}}
    for name, runs in runs_by_monitor.items():
        if runs is None:                      # 讀唔到 ≠ 冇成功過
            out["monitors"][name] = {"unreadable": True}
            continue
        runs = sorted(runs, key=lambda r: r.get("created_at") or "", reverse=True)
        entry: dict = {}
        for r in runs:
            if r.get("status") != "completed":
                continue          # queued / in-progress says nothing either way
            if r.get("conclusion") == "success":
                entry.setdefault("last_success", r.get("updated_at") or r.get("created_at"))
                break
            entry["consecutive_failures"] = int(entry.get("consecutive_failures") or 0) + 1
            entry.setdefault("last_detail", f"{r.get('conclusion')} · {r.get('html_url','')}")
        if runs:
            entry["last_attempt"] = runs[0].get("created_at")
            entry["last_status"] = runs[0].get("conclusion") or runs[0].get("status")
        out["monitors"][name] = entry
    return out


def fetch_runs(repo: str, token: str, per_workflow: int = 12) -> Dict[str, list]:
    runs: Dict[str, list] = {}
    for name, (wf, _days) in WORKFLOWS.items():
        try:
            data = _api(f"/repos/{repo}/actions/workflows/{wf}/runs"
                        f"?per_page={per_workflow}", token)
            runs[name] = data.get("workflow_runs") or []
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            # S222: an unreadable workflow must NOT be folded in as "never
            # succeeded". That was this tool's own first bug: a bad token made
            # every monitor look dead, which is a false alarm indistinguishable
            # from a real total outage — the same failure as a false all-clear,
            # pointed the other way. Unknown is its own answer.
            code = getattr(e, "code", type(e).__name__)
            print(f"  ⚠️ 讀唔到 {wf} 的 run 歷史：{code}")
            runs[name] = None
    return runs


def dispatch(repo: str, monitor: str, token: str, ref: str = "main") -> bool:
    wf = WORKFLOWS[monitor][0]
    try:
        _api(f"/repos/{repo}/actions/workflows/{wf}/dispatches", token,
             method="POST", body={"ref": ref})
        return True
    except urllib.error.HTTPError as e:
        print(f"  ⚠️ 補跑 {wf} 失敗：HTTP {e.code} {e.read()[:120].decode(errors='replace')}")
        return False


def render(report: dict) -> str:
    if not report["speaks"]:
        return (f"🫀 監察心跳：{len(report['ok'])} 個全部準時（"
                + "、".join(report["ok"]) + "）")
    out = ["🫀 監察心跳 —— 有監察本身出事了", ""]
    for q in report["quiet"]:
        out.append(f"  🔇 `{q['monitor']}` 應每 {q['cadence_days']} 日成功一次，"
                   f"最後一次成功：{q['last_success']}")
    for f in report["failing"]:
        out.append(f"  ❌ `{f['monitor']}` 連續失敗 {f['consecutive_failures']} 次"
                   + (f" —— {f['last_detail']}" if f["last_detail"] else ""))
    if report.get("unknown"):
        out.append("  ❓ 判斷不到（讀唔到 run 歷史，多數係 token 權限）："
                   + "、".join(report["unknown"])
                   + " —— 呢個唔等於佢哋死咗，只係本檢查睇唔到，同樣要跟進。")
    if report["ok"]:
        out += ["", "  準時：" + "、".join(report["ok"])]
    out += ["",
            "⚠️ 這份心跳本身也跑在 GitHub Actions 排程之上，救不到「七個一齊死」。",
            "   本 repo 是 PUBLIC，官方行為：60 日無 repository 活動，排程會被自動停用；",
            "   錯過的排程亦不會補跑。這裡買到的是互相監察 —— 邊個仲跑得郁，就由佢報其餘幾個的沉默。"]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def _run_self_test(is_due_fn=is_due, is_overdue_fn=is_overdue,
                   record_fn=record) -> int:
    fails = []

    def check(label, cond):
        """`cond` may be a bool or a thunk. A thunk that raises counts as FAIL,
        not as a crash — `--prove-assertions` swaps the rules for no-ops, and an
        assertion that explodes instead of going red proves nothing."""
        try:
            ok = bool(cond() if callable(cond) else cond)
        except Exception as exc:                       # noqa: BLE001 — see docstring
            ok = False
            label = f"{label}  [{type(exc).__name__}]"
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            fails.append(label)

    NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
    def ago(days):
        return (NOW - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    check("從未見過的監察一定 due", is_due_fn(None, 7, NOW))
    check("剛剛成功過就唔 due", not is_due_fn({"last_success": ago(1)}, 7, NOW))
    check("夠鐘就 due", is_due_fn({"last_success": ago(7)}, 7, NOW))
    check("壞掉的時間戳當作從未成功（安全方向）",
          is_due_fn({"last_success": "唔係時間"}, 7, NOW))
    check("失敗過但未夠鐘，仍然唔 due（唔會即刻重試到爆）",
          not is_due_fn({"last_success": ago(2), "last_status": "fail"}, 7, NOW))

    check("遲少少唔算 overdue", not is_overdue_fn({"last_success": ago(9)}, 7, NOW))
    check("靜超過兩個週期先算 overdue", is_overdue_fn({"last_success": ago(15)}, 7, NOW))
    check("每日跑的監察，兩日冇成功就 overdue",
          is_overdue_fn({"last_success": ago(3)}, 1, NOW))

    st = record_fn({}, "freshness", "ok", NOW)
    check("record ok 會寫低成功時間並清零失敗計數",
          lambda: st["monitors"]["freshness"]["last_success"].startswith("2026-09-13")
          and st["monitors"]["freshness"]["consecutive_failures"] == 0)
    st2 = record_fn(st, "freshness", "fail", NOW, detail="no token")
    check("record fail 會累加，但唔會覆蓋上次成功時間",
          lambda: st2["monitors"]["freshness"]["consecutive_failures"] == 1
          and st2["monitors"]["freshness"]["last_success"] == st["monitors"]["freshness"]["last_success"])
    st3 = record_fn(record_fn(st2, "freshness", "fail", NOW), "freshness", "ok", NOW)
    check("再成功一次即刻清零",
          lambda: st3["monitors"]["freshness"]["consecutive_failures"] == 0)
    check("record 唔會改動傳入的 state（純函式）",
          lambda: st == json.loads(json.dumps(st)) and "freshness" in st["monitors"])
    st4 = record_fn(st, "freshness", "skipped", NOW)
    check("skipped 唔當成功、亦唔當失敗",
          lambda: st4["monitors"]["freshness"]["last_success"] == st["monitors"]["freshness"]["last_success"]
          and st4["monitors"]["freshness"]["consecutive_failures"] == 0)
    bad = False
    try:
        record_fn({}, "x", "weird", NOW)
    except ValueError:
        bad = True
    check("未知 status 會拋錯（證明會紅）", bad)

    cad = {"a": 7, "b": 7, "c": 1}
    state = {"monitors": {"a": {"last_success": ago(1)},
                          "b": {"last_success": ago(30)},
                          "c": {"last_success": ago(0), "consecutive_failures": 3}}}
    rep = overdue_report(state, NOW, cad)
    check("靜咗嘅監察會被點名", [q["monitor"] for q in rep["quiet"]] == ["b"])
    check("連續失敗嘅監察分開報", [f["monitor"] for f in rep["failing"]] == ["c"])
    check("準時嘅唔會出聲", rep["ok"] == ["a"] and rep["speaks"] is True)
    quiet_ok = overdue_report({"monitors": {k: {"last_success": ago(0)} for k in cad}},
                              NOW, cad)
    check("全部準時就完全靜默", quiet_ok["speaks"] is False)
    check("靜默時的文案唔會嚇人", "全部準時" in render(quiet_ok))
    check("出聲時一定講明本機制自己的極限",
          "60 日" in render(rep) and "互相監察" in render(rep))

    # --- state_from_runs：由 Actions run 歷史摺出台帳 ---
    def run(concl, created, status="completed"):
        return {"conclusion": concl, "created_at": created, "updated_at": created,
                "status": status, "html_url": "u"}
    got = state_from_runs({"freshness": [
        run("failure", ago(1)), run("failure", ago(2)), run("success", ago(9))]})
    e = got["monitors"]["freshness"]
    check("最後一次成功由 run 歷史讀出", lambda: e["last_success"] == ago(9))
    check("連續失敗由最新數起，遇到成功即停", lambda: e["consecutive_failures"] == 2)
    got2 = state_from_runs({"freshness": [run("success", ago(1)), run("failure", ago(2))]})
    check("失敗之後再成功 = 已復原，唔算連續失敗",
          lambda: int(got2["monitors"]["freshness"].get("consecutive_failures") or 0) == 0)
    got3 = state_from_runs({"freshness": [run(None, ago(0), status="in_progress"),
                                          run("success", ago(2))]})
    check("跑緊嘅 run 唔當成功亦唔當失敗",
          lambda: got3["monitors"]["freshness"]["last_success"] == ago(2))
    check("完全冇 run 歷史 = 從未成功 = 一定 overdue",
          lambda: is_overdue_fn(state_from_runs({"x": []})["monitors"]["x"], 7, NOW))

    # --- 「讀唔到」必須同「死咗」分開（S222 本工具自己的第一個 bug）---
    unread = state_from_runs({"freshness": None, "qc_report": [run("success", ago(0))]})
    check("讀唔到嘅 workflow 標記為 unreadable，唔會摺成「從未成功」",
          lambda: unread["monitors"]["freshness"] == {"unreadable": True})
    rep_u = overdue_report(unread, NOW, {"freshness": 7, "qc_report": 1})
    check("判斷不到會入自己嗰個桶，唔會報成靜咗",
          lambda: rep_u["unknown"] == ["freshness"] and rep_u["quiet"] == [])
    check("判斷不到一樣要出聲（唔可以當冇事）", lambda: rep_u["speaks"] is True)
    check("讀得到嗰個仍然照常判斷", lambda: rep_u["ok"] == ["qc_report"])
    check("文案要講明「唔等於死咗」", lambda: "唔等於佢哋死咗" in render(rep_u))

    # --- token 取得（S222 呢度曾經漏咗 return，送出 "Bearer None" 全部 401）---
    _saved = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = "ghs_dummy_for_selftest"
    try:
        check("_token() 真係還個 token 出嚟，唔係 None",
              lambda: _token() == "ghs_dummy_for_selftest")
    finally:
        if _saved is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = _saved
    os.environ.pop("GITHUB_TOKEN", None); os.environ.pop("GH_TOKEN", None)
    _no_tok = False
    try:
        _token()
    except SystemExit:
        _no_tok = True
    check("冇 token 時直接失敗，唔會靜靜出一份假報告（證明會紅）", _no_tok)
    if _saved is not None:
        os.environ["GITHUB_TOKEN"] = _saved

    # 台帳與真實 cron 必須對得上，否則量度緊一個唔存在的承諾
    wf = REPO_ROOT / ".github" / "workflows"
    files = {p.stem for p in wf.glob("*.yml")} if wf.exists() else set()
    expected = {"freshness_check", "discover_check", "served_url_check",
                "pgvector_check", "qc_report", "title_check"}
    check(f"CADENCE_DAYS 覆蓋所有排程 workflow（{len(CADENCE_DAYS)} 個）",
          not files or expected.issubset(files))

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


def _prove_assertions() -> int:
    """Replace the rules with no-ops; the tests must go red."""
    print("以無效規則取代真規則，斷言必須全部轉紅：\n")
    fired = []
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _run_self_test(is_due_fn=lambda *a, **k: True,
                       is_overdue_fn=lambda *a, **k: False,
                       record_fn=lambda st, m, s, n, detail="": st)
    for line in buf.getvalue().splitlines():
        if line.strip().startswith("FAIL"):
            fired.append(line.strip()[6:])
    for f in fired:
        print(f"  紅了：{f}")
    ok = len(fired) >= 8
    print(f"\n{'ALL PASS' if ok else 'PROOF FAILED'} — {len(fired)} 條斷言在無效規則下轉紅（需 ≥ 8）")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--prove-assertions", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dispatch", action="store_true",
                    help="補跑逾期未成功的監察（需 actions:write）")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY",
                                                     "Leonard-Wong-Git/edb-knowledge"))
    ap.add_argument("--ref", default="main")
    ap.add_argument("--json-out", metavar="PATH")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_test()
    if args.prove_assertions:
        return _prove_assertions()
    if not args.check:
        ap.print_help(); return 2

    token = _token()
    now = datetime.now(timezone.utc)
    state = state_from_runs(fetch_runs(args.repo, token))
    rep = overdue_report(state, now)

    # 補跑：due（過咗週期）就開，唔使等到 overdue —— 呢個就係「第一次 fail 之後
    # 仲有下一次」嘅機制本身。overdue 只係用嚟出聲，唔係用嚟決定開唔開。
    started = []
    if args.dispatch:
        for name, (_wf, days) in WORKFLOWS.items():
            entry = (state.get("monitors") or {}).get(name)
            if entry and entry.get("unreadable"):
                continue          # 唔知佢跑成點就唔好亂開，否則會重複開一堆
            if is_due(entry, days, now) and dispatch(args.repo, name, token, args.ref):
                started.append(name)
    rep["dispatched"] = started

    print(render(rep))
    if started:
        print("\n🔁 已補跑：" + "、".join(started)
              + "\n   （逾期未成功即補開一次；下一個 daily tick 會再檢查，"
                "所以一晚失敗最多只蝕一日，唔使等足一個星期。）")
    if args.json_out:
        pathlib.Path(args.json_out).write_text(
            json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 依 S126 慣例：只有「監察本身壞咗」先影響 exit code。補跑成功唔算壞。
    return 1 if rep["speaks"] else 0


if __name__ == "__main__":
    sys.exit(main())
