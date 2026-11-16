#!/usr/bin/env python3
"""apply_footnote_corrections.py — apply curated-footnote text corrections (S251).

Why: a curated footnote is preferred at retrieval time, so a wrong one answers wrong.
Corrections live in dev/source/footnote_corrections.json (chunk id -> corrected text,
keywords, basis). This tool re-embeds ONLY the listed rows and PATCHes
text / hash / embedding (and title when given). `url` is never touched here — page
anchors belong to dev/source/url_overrides.json + dev/apply_url_overrides.py.

Re-run with --execute after ANY footnote ingest script is run with --execute: those
upserts write the old per-script text back. Idempotent — rows already matching are skipped.

  /usr/local/bin/python3 dev/apply_footnote_corrections.py             # dry-run (default)
  /usr/local/bin/python3 dev/apply_footnote_corrections.py --check     # exit 1 if any row drifted
  /usr/local/bin/python3 dev/apply_footnote_corrections.py --execute   # backup, then PATCH
  /usr/local/bin/python3 dev/apply_footnote_corrections.py --self-test # offline, no network

--execute needs Leonard's explicit approval (production write). It first exports every
row it will change (select=*, with embedding) to dev/init_backup/<ts>/, then PATCHes one
id at a time and reads back that exactly one row carries the new text.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORRECTIONS = REPO_ROOT / "dev" / "source" / "footnote_corrections.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
DEFAULT_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
TABLE = "wiki_chunks"


def combine(text, kw):
    """Embed-input format shared by every footnote ingest script (text + keywords)."""
    return text + " " + " ".join(kw)


def load_corrections(path=CORRECTIONS):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cor = data["corrections"]
    problems = []
    for cid, c in cor.items():
        if not cid.startswith("footnote_"):
            problems.append(f"{cid}: id must start with footnote_")
        if not isinstance(c.get("text"), str) or len(c["text"].strip()) < 20:
            problems.append(f"{cid}: text missing or too short")
        if not isinstance(c.get("keywords"), list) or not c["keywords"]:
            problems.append(f"{cid}: keywords missing")
        if not c.get("basis"):
            problems.append(f"{cid}: basis (source quote) missing")
        if not c.get("approved"):
            problems.append(f"{cid}: approved (who/when) missing")
    if data.get("_meta", {}).get("count") != len(cor):
        problems.append(f"_meta.count={data.get('_meta', {}).get('count')} but {len(cor)} corrections")
    return cor, problems


def plan(cor, rows):
    """rows: id -> stored row (or None). Returns (todo, missing, wrong_type)."""
    todo, missing, wrong_type = [], [], []
    for cid, c in cor.items():
        row = rows.get(cid)
        if row is None:
            missing.append(cid)
            continue
        if row.get("content_type") != "footnote_curated":
            wrong_type.append(cid)
            continue
        fields = []
        if row.get("text") != c["text"]:
            fields.append("text")
        if c.get("title") and row.get("title") != c["title"]:
            fields.append("title")
        if fields:
            todo.append((cid, fields))
    return todo, missing, wrong_type


def self_test():
    cor, problems = load_corrections()
    assert not problems, problems
    rows = {cid: {"content_type": "footnote_curated", "text": c["text"],
                  "title": c.get("title")} for cid, c in cor.items()}
    assert plan(cor, rows) == ([], [], []), "matching store must yield nothing to do"
    first = next(iter(cor))
    rows[first] = dict(rows[first], text="old")
    todo, missing, wrong = plan(cor, rows)
    assert todo == [(first, ["text"])] and not missing and not wrong, todo
    rows[first] = None
    assert plan(cor, rows)[1] == [first], "missing row must be reported"
    rows[first] = {"content_type": "wiki", "text": "x"}
    assert plan(cor, rows)[2] == [first], "non-footnote row must be refused"
    assert combine("a", ["b", "c"]) == "a b c"
    print(f"self-test ALL PASS ({len(cor)} corrections)")
    return 0


def env():
    out = {}
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                out[k] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    execute = "--execute" in sys.argv
    check = "--check" in sys.argv
    import requests
    cor, problems = load_corrections()
    if problems:
        print("ERROR in footnote_corrections.json:\n  " + "\n  ".join(problems))
        return 1
    e = env()
    base = e.get("SUPABASE_URL", DEFAULT_URL)
    key = e.get("SUPABASE_SERVICE_KEY")
    if not key:
        print("ERROR: SUPABASE_SERVICE_KEY missing in backend/.env")
        return 1
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    rows = {}
    for cid in cor:
        r = requests.get(f"{base}/rest/v1/{TABLE}", headers=h,
                         params={"id": f"eq.{cid}", "select": "*"}, timeout=60)
        r.raise_for_status()
        got = r.json()
        rows[cid] = got[0] if len(got) == 1 else None
    todo, missing, wrong_type = plan(cor, rows)
    print(f"corrections={len(cor)} already_applied={len(cor) - len(todo) - len(missing) - len(wrong_type)} "
          f"to_change={len(todo)} missing_in_store={len(missing)} not_footnote={len(wrong_type)}")
    for cid in missing:
        print(f"  MISSING {cid}  (row no longer exists — remove it from footnote_corrections.json)")
    for cid in wrong_type:
        print(f"  REFUSED {cid}  (content_type is not footnote_curated)")
    for cid, fields in todo:
        print(f"  {cid}  [{', '.join(fields)}]")
        if "text" in fields:
            print(f"      - {rows[cid]['text']}\n      + {cor[cid]['text']}")
        if "title" in fields:
            print(f"      title - {rows[cid].get('title')}\n      title + {cor[cid]['title']}")
    if missing or wrong_type:
        return 1
    if check:
        return 1 if todo else 0
    if not execute:
        print("DRY-RUN — nothing written.")
        return 0
    if not todo:
        print("Nothing to do.")
        return 0

    sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
    import build_wiki_index as bw
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    bdir = REPO_ROOT / "dev" / "init_backup" / ts
    bdir.mkdir(parents=True, exist_ok=True)
    backup = [rows[cid] for cid, _ in todo]
    assert all(b.get("embedding") for b in backup), "backup row without embedding"
    (bdir / "footnote_corrections_backup.json").write_text(
        json.dumps(backup, ensure_ascii=False), encoding="utf-8")
    print(f"backup: dev/init_backup/{ts}/footnote_corrections_backup.json ({len(backup)} rows)")

    ids = [cid for cid, _ in todo]
    vecs = bw.embed_batch(bw.load_api_key(), [combine(cor[c]["text"], cor[c]["keywords"]) for c in ids])
    assert len(vecs) == len(ids)
    failed = 0
    for cid, v in zip(ids, vecs):
        c = cor[cid]
        body = {"text": c["text"], "hash": bw.text_hash(c["text"]), "embedding": v}
        if c.get("title"):
            body["title"] = c["title"]
        r = requests.patch(f"{base}/rest/v1/{TABLE}",
                           headers={**h, "Prefer": "return=representation"},
                           params={"id": f"eq.{cid}", "select": "id,text,title,url"},
                           json=body, timeout=60)
        got = r.json() if r.status_code in (200, 204) else []
        ok = (len(got) == 1 and got[0]["text"] == c["text"]
              and rows[cid]["url"] == got[0]["url"]
              and (not c.get("title") or got[0]["title"] == c["title"]))
        print(f"  {cid}: {'OK' if ok else 'FAIL ' + r.text[:200]}")
        failed += 0 if ok else 1
    print(f"written={len(ids) - failed} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
