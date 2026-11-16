#!/usr/bin/env python3
"""_s249_fix_two_footnotes.py — one-off (S249, Leonard approved): two curated footnotes
disagreed with their source PDF. The text is corrected in the owning ingest scripts
(dev/forms_ingest.py, dev/ingest_s179_topics.py); this re-embeds ONLY those two rows
and PATCHes text / hash / embedding, leaving url (page anchor) and everything else alone.
Running the owning scripts with --execute instead would rewrite every footnote they hold
and wipe the page anchors (see dev/apply_url_overrides.py).

  /usr/local/bin/python3 dev/_s249_fix_two_footnotes.py            # dry-run
  /usr/local/bin/python3 dev/_s249_fix_two_footnotes.py --execute
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev"))
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw          # noqa: E402
import forms_ingest as fi              # noqa: E402
import ingest_s179_topics as s179      # noqa: E402

TARGETS = {}
for fid, _src, text, kw, _q in fi.F:
    if fid == "ceg_rates_2627":
        TARGETS[f"footnote_fn_{fid}"] = (text, kw)
for e in s179.F:
    if e["fid"] == "mh_referral_consent":
        TARGETS[f"footnote_fn_{e['fid']}"] = (e["text"], e["keywords"])
assert len(TARGETS) == 2, TARGETS.keys()


def main() -> int:
    execute = "--execute" in sys.argv
    h = fi.headers_svc()
    base = fi.SUPABASE_URL
    old = {}
    for cid in TARGETS:
        r = requests.get(f"{base}/rest/v1/wiki_chunks", headers=h,
                         params={"id": f"eq.{cid}", "select": "*"}, timeout=60)
        r.raise_for_status()
        assert len(r.json()) == 1, cid
        old[cid] = r.json()[0]
        print(f"{cid}\n  - {old[cid]['text']}\n  + {TARGETS[cid][0]}")
    if not execute:
        print("DRY-RUN — nothing written.")
        return 0
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    bdir = REPO_ROOT / "dev" / "init_backup" / ts
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / "s249_two_footnotes_backup.json").write_text(
        json.dumps(list(old.values()), ensure_ascii=False), encoding="utf-8")
    print(f"backup: dev/init_backup/{ts}/s249_two_footnotes_backup.json")
    ids = list(TARGETS)
    vecs = bw.embed_batch(bw.load_api_key(), [fi.combine(*TARGETS[c]) for c in ids])
    for cid, v in zip(ids, vecs):
        text = TARGETS[cid][0]
        r = requests.patch(f"{base}/rest/v1/wiki_chunks",
                           headers={**h, "Prefer": "return=representation"},
                           params={"id": f"eq.{cid}", "select": "id,text,url"},
                           json={"text": text, "hash": bw.text_hash(text), "embedding": v},
                           timeout=60)
        ok = r.status_code in (200, 204) and len(r.json()) == 1 and r.json()[0]["text"] == text
        print(f"  {cid}: {'OK' if ok else 'FAIL ' + r.text[:200]}  url={r.json()[0]['url'][-28:] if ok else ''}")
        if not ok:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
