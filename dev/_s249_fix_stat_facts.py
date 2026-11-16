#!/usr/bin/env python3
"""_s249_fix_stat_facts.py — one-off (S249, Leonard approved). EDB revised every
teacher figure in pri_tc.xlsx / sec_tc.xlsx (2026-08-05, footnote
「所有與教師有關的數字已作出修訂」). Two stat_fact rows quoted the old 2024/25
head-counts. dev/vault/build_stat_facts.py is corrected; this swaps just those two
rows in Supabase (stat_fact ids are text hashes, so a corrected fact is a new id:
INSERT the new row, verify, then DELETE the old one). Backup was taken first
(dev/init_backup/20261116_084506_UTC/s249_stat_backup.json).

  /usr/local/bin/python3 dev/_s249_fix_stat_facts.py [--execute]
"""
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev"))
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw   # noqa: E402
import forms_ingest as fi       # noqa: E402  (service-key loader only)

SWAPS = [
    ("stat_pri",
     "2024/25學年小學教師人數為26,701人，持學士學位或以上佔99.2%（26,481人）。",
     "2024/25學年小學教師人數為26,661人，持學士學位或以上佔99.2%（26,441人）。"),
    ("stat_sec",
     "2024/25學年中學教師人數為30,015人，持學士學位或以上佔99.6%（29,906人）。",
     "2024/25學年中學教師人數為29,978人，持學士學位或以上佔99.6%（29,869人）。"),
]


def main() -> int:
    execute = "--execute" in sys.argv
    h = fi.headers_svc()
    url = f"{fi.SUPABASE_URL}/rest/v1/wiki_chunks"
    plan = []
    for sid, old_text, new_text in SWAPS:
        old_id = f"stat_{sid}_{bw.text_hash(old_text)}"
        new_id = f"stat_{sid}_{bw.text_hash(new_text)}"
        r = requests.get(url, headers=h, params={"id": f"eq.{old_id}", "select": "*"}, timeout=60)
        r.raise_for_status()
        rows = r.json()
        state = "old row present" if rows else "old row absent"
        n = requests.get(url, headers=h, params={"id": f"eq.{new_id}", "select": "id"}, timeout=60).json()
        print(f"{sid}: {state}; new row {'present' if n else 'absent'}\n  - {old_text}\n  + {new_text}")
        if rows and rows[0]["text"] != old_text:
            print("  ABORT: stored text differs from the expected old text")
            return 1
        plan.append((old_id, new_id, new_text, rows[0] if rows else None, bool(n)))
    if not execute:
        print("DRY-RUN — nothing written.")
        return 0
    todo = [p for p in plan if p[3] is not None]
    if not todo:
        print("Nothing to do.")
        return 0
    vecs = bw.embed_batch(bw.load_api_key(), [p[2] for p in todo])
    for (old_id, new_id, new_text, old_row, has_new), v in zip(todo, vecs):
        row = {k: val for k, val in old_row.items() if k not in ("created_at", "updated_at")}
        row.update(id=new_id, hash=bw.text_hash(new_text), text=new_text, embedding=v)
        if not has_new:
            r = requests.post(url, headers={**h, "Prefer": "return=minimal"}, json=[row], timeout=60)
            if r.status_code not in (200, 201):
                print(f"INSERT FAIL {new_id}: {r.status_code} {r.text[:200]}")
                return 1
        chk = requests.get(url, headers=h, params={"id": f"eq.{new_id}", "select": "id,text"}, timeout=60).json()
        if len(chk) != 1 or chk[0]["text"] != new_text:
            print(f"VERIFY FAIL {new_id} — old row left in place")
            return 1
        d = requests.delete(url, headers={**h, "Prefer": "return=representation"},
                            params={"id": f"eq.{old_id}", "select": "id"}, timeout=60)
        print(f"  {new_id} inserted; deleted {[x['id'] for x in d.json()]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
