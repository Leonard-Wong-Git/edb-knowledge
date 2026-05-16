#!/usr/bin/env python3
"""Session 111 one-shot: regenerate app.html INITIAL_REVIEW_STATE to match the
post-dedup 455-fact INITIAL_DATA (== knowledge.json). All facts -> "approved".

Safety: backs up app.html to dev/init_backup/<UTC>/ before writing; asserts the
target line shape; preserves the single inlined `JSON.parse("...")` literal
(project E.1 lesson: Babel Standalone cannot async-fetch under file://).
Only line 1481 (1-based) is rewritten; nothing else is touched here.
"""
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
APP = REPO / "app.html"
KNOW = REPO / "knowledge.json"
LINE_NO = 1481  # 1-based; verified pre-run
PREFIX = "const INITIAL_REVIEW_STATE = JSON.parse("

data = json.loads(KNOW.read_text(encoding="utf-8"))
review = {}
for tk, tv in data.items():
    if tk == "_meta" or not isinstance(tv, dict):
        continue
    for rk, rv in tv.items():
        if rk.startswith("_") or not isinstance(rv, list):
            continue
        for i in range(len(rv)):
            review[f"{tk}.{rk}.{i}"] = "approved"

n = len(review)
expected = data["_meta"]["stats"]["facts"]
if n != expected:
    sys.exit(f"ABORT: built {n} keys but _meta.stats.facts={expected}")

inner = json.dumps(review, ensure_ascii=False, separators=(", ", ": "))
new_line = f"{PREFIX}{json.dumps(inner, ensure_ascii=False)});"

lines = APP.read_text(encoding="utf-8").split("\n")
idx = LINE_NO - 1
if not lines[idx].startswith(PREFIX):
    sys.exit(f"ABORT: line {LINE_NO} does not start with expected prefix")

# parse OLD payload for before/after evidence
old_payload = lines[idx][len(PREFIX):]
old_payload = old_payload[: old_payload.rfind(");")]
old_review = json.loads(json.loads(old_payload))

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
bdir = REPO / "dev" / "init_backup" / ts
bdir.mkdir(parents=True, exist_ok=True)
shutil.copy2(APP, bdir / "app.html")

lines[idx] = new_line
APP.write_text("\n".join(lines), encoding="utf-8")

# self-verify round-trip
chk = json.loads(json.loads(APP.read_text(encoding="utf-8").split("\n")[idx][len(PREFIX):].rsplit(");", 1)[0]))
print(f"backup           : {bdir / 'app.html'}")
print(f"OLD review keys  : {len(old_review)}")
print(f"NEW review keys  : {len(chk)}  (expected {expected})")
print(f"all 'approved'   : {set(chk.values()) == {'approved'}}")
print(f"line {LINE_NO} len    : {len(new_line)} (single line preserved)")
print(f"sample           : {list(chk.items())[:3]} ... {list(chk.items())[-2:]}")
print("OK" if len(chk) == expected else "MISMATCH")
