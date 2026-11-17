#!/usr/bin/env python3
"""check_footnote_anchors.py — is each curated footnote's source sentence still
on the page it cites?  (S252, WORK_QUEUE A2)

WHY THIS EXISTS
A curated footnote is a short hand-written answer that retrieval prefers, so a
footnote that no longer matches its source answers users wrongly. The S250 audit
(177 footnotes: 28 wrong pages, 9 wrong statements) was done by a model reading
every source. That cannot be assumed to be available again, and it cannot run
monthly for free. This tool replaces the monthly part with a mechanical check:

  * dev/source/footnote_anchors.json records, per footnote id, ONE verbatim
    sentence of the source document (the "anchor quote"), the document url and
    the PDF page it was found on (page = null for web pages).
  * every month the documents are downloaded again and the quote is searched.

It catches a source that was replaced by a new edition (the SFO page that went
from 2025/26 to 2026/27 in S251), moved to another page, or went offline. It
does NOT judge whether the footnote's own wording is right — that was settled
when the anchor was recorded, and a wording question still needs a reader.

RESULTS (one per footnote)
  OK          the quote is on the recorded page (web page: anywhere in the page)
  MOVED       the quote is in the same document on another page (new page listed)
  GONE        the quote is nowhere in the document (probably a new edition)
  FETCH_FAIL  the document could not be downloaded (status listed)

READ-ONLY. There is no write mode: it never touches Supabase, the registry or
the anchors file. What to do with a result is in
dev/ops/playbooks/footnote-audit.md.

USAGE
  python3 dev/source/check_footnote_anchors.py --self-test
  /usr/local/bin/python3 dev/source/check_footnote_anchors.py --check \
      [--only ID[,ID...]] [--out report.json] [--table report.md] \
      [--previous last_report.json]

--previous is the report of the previous run. A FETCH_FAIL is only raised as an
alert when the same footnote also failed to download in that previous report —
one bad night at the source site is not news.

Needs `requests` and `pymupdf` for --check (use /usr/local/bin/python3 locally);
--self-test is offline and standard-library only.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ANCHORS = REPO_ROOT / "dev" / "source" / "footnote_anchors.json"
URL_OVERRIDES = REPO_ROOT / "dev" / "source" / "url_overrides.json"

FETCH_GAP_SECONDS = 1.0
FETCH_TIMEOUT = 90
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
# Same main-content markers as check_freshness.html_fingerprint (EDB page shell).
MAIN_START = "inner_page_content_container"
MAIN_END = "footer_content"
MIN_QUOTE_CHARS = 8          # after normalisation; shorter matches by accident

STATUSES = ("OK", "MOVED", "GONE", "FETCH_FAIL")
_WS = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# pure helpers — all covered by --self-test
# ---------------------------------------------------------------------------

def norm(s: str) -> str:
    """NFKC, then drop ALL whitespace. Both sides of every comparison use this."""
    return _WS.sub("", unicodedata.normalize("NFKC", s or ""))


def split_page(url: str) -> tuple[str, int | None]:
    """('https://x/a.pdf#page=3') -> ('https://x/a.pdf', 3); no fragment -> None."""
    base, _, frag = (url or "").partition("#")
    m = re.fullmatch(r"page=(\d+)", frag.strip())
    return base, int(m.group(1)) if m else None


def html_visible_text(body: bytes) -> str:
    """Visible text of a web page; only the main-content region when the EDB
    marker is present, so menus and footers cannot satisfy a quote."""
    text = body.decode("utf-8", "ignore")
    a = text.find(MAIN_START)
    if a != -1:
        b = text.find(MAIN_END, a)
        text = text[a:b if b != -1 else len(text)]
    text = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", text)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html_lib.unescape(text)


def pages_containing(pages: list[str], quote: str) -> list[int]:
    """1-based PDF pages the quote is on. A quote that runs across a page break
    is attributed to the page it STARTS on."""
    q = norm(quote)
    if not q:
        return []
    normed = [norm(p) for p in pages]
    hits = [i + 1 for i, p in enumerate(normed) if q in p]
    if hits:
        return hits
    joined, starts, pos = "", [], 0
    for p in normed:
        starts.append(pos)
        joined += p
        pos += len(p)
    at = joined.find(q)
    if at == -1:
        return []
    page = max(i for i, s in enumerate(starts) if s <= at) + 1
    return [page]


def classify(anchor: dict, doc: dict) -> dict:
    """One anchor against one fetched document -> {status, found_pages, detail}.

    doc is {"error": "..."} | {"kind": "pdf", "pages": [...]} |
           {"kind": "html", "text": "..."}.
    """
    page = anchor.get("page")
    if doc.get("error"):
        return {"status": "FETCH_FAIL", "found_pages": [], "detail": doc["error"]}
    if doc.get("kind") == "html":
        if page is not None:
            # A .pdf url that now answers with a web page is a soft 404 or a
            # redirect to a landing page: the cited document is not there.
            return {"status": "GONE", "found_pages": [],
                    "detail": "所記的是 PDF 第 %d 頁，但連結現時回傳的是網頁而不是 PDF" % page}
        if norm(anchor["quote"]) in norm(doc.get("text", "")):
            return {"status": "OK", "found_pages": [], "detail": "錨句仍在網頁內"}
        return {"status": "GONE", "found_pages": [],
                "detail": "網頁內找不到錨句（原文可能已更新）"}
    found = pages_containing(doc.get("pages", []), anchor["quote"])
    if not found:
        return {"status": "GONE", "found_pages": [],
                "detail": "整份 PDF（%d 頁）都找不到錨句（原文可能已換版）"
                          % len(doc.get("pages", []))}
    if page is None or page in found:
        return {"status": "OK", "found_pages": found,
                "detail": "錨句在第 %s 頁" % "、".join(map(str, found))}
    return {"status": "MOVED", "found_pages": found,
            "detail": "錨句不在所記的第 %d 頁，現在第 %s 頁"
                      % (page, "、".join(map(str, found)))}


def validate_anchors(data: dict) -> list[str]:
    """Problems with the anchors file itself (empty list = usable)."""
    bad = []
    anchors = data.get("anchors") if isinstance(data, dict) else None
    if not isinstance(anchors, dict) or not anchors:
        return ["no 'anchors' mapping"]
    if data.get("_meta", {}).get("count") != len(anchors):
        bad.append("_meta.count (%s) != number of anchors (%d)"
                   % (data.get("_meta", {}).get("count"), len(anchors)))
    for fid, a in anchors.items():
        if not isinstance(a, dict):
            bad.append("%s: not an object" % fid)
            continue
        url = a.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            bad.append("%s: url missing or not http(s)" % fid)
        elif "#" in url:
            bad.append("%s: url must not carry a #fragment (page goes in 'page')" % fid)
        page = a.get("page")
        if page is not None and not (isinstance(page, int) and page >= 1):
            bad.append("%s: page must be null or a positive integer" % fid)
        if len(norm(a.get("quote") if isinstance(a.get("quote"), str) else "")) < MIN_QUOTE_CHARS:
            bad.append("%s: quote missing or shorter than %d characters"
                       % (fid, MIN_QUOTE_CHARS))
    return bad


def override_mismatches(anchors: dict, overrides: dict) -> list[str]:
    """Anchors whose url/page disagree with the served url in url_overrides.json.

    The store serves the override; the anchor must describe the same document
    and page, or this monitor is watching something users are not sent to.
    """
    out = []
    for fid, a in anchors.items():
        o = overrides.get(fid)
        if not o:
            continue
        base, page = split_page(o.get("url", ""))
        if base != a.get("url"):
            out.append("%s: anchor url differs from url_overrides.json" % fid)
        elif page is not None and a.get("page") is not None and page != a["page"]:
            out.append("%s: anchor page %s but url_overrides.json says #page=%s"
                       % (fid, a["page"], page))
    return out


def build_report(anchors: dict, docs: dict, previous: dict | None,
                 generated_at: str) -> dict:
    """anchors: id -> anchor; docs: url -> fetched doc. Pure."""
    prev_fail = set()
    if isinstance(previous, dict):
        prev_fail = {r.get("id") for r in previous.get("results", [])
                     if r.get("status") == "FETCH_FAIL"}
    results = []
    for fid in sorted(anchors):
        a = anchors[fid]
        r = classify(a, docs.get(a["url"], {"error": "not fetched"}))
        row = {"id": fid, "url": a["url"], "page": a.get("page"), **r}
        if r["status"] == "FETCH_FAIL":
            row["consecutive"] = fid in prev_fail
        results.append(row)
    summary = {s: sum(1 for r in results if r["status"] == s) for s in STATUSES}
    summary["total"] = len(results)
    alerts = [r for r in results
              if r["status"] in ("MOVED", "GONE")
              or (r["status"] == "FETCH_FAIL" and r.get("consecutive"))]
    return {"generated_at": generated_at, "summary": summary,
            "alerts": alerts, "results": results}


def render_table(report: dict) -> str:
    s = report["summary"]
    lines = ["# 註腳錨句核對 — %s" % report["generated_at"], "",
             "共 %d 條：OK %d · MOVED %d · GONE %d · FETCH_FAIL %d"
             % (s["total"], s["OK"], s["MOVED"], s["GONE"], s["FETCH_FAIL"]), ""]
    rest = [r for r in report["results"] if r["status"] != "OK"]
    if not rest:
        lines.append("全部錨句都在所記的位置。")
        return "\n".join(lines) + "\n"
    lines += ["| 註腳 id | 結果 | 所記頁 | 說明 | 文件 |", "|---|---|---|---|---|"]
    for r in rest:
        lines.append("| `%s` | %s | %s | %s | %s |"
                     % (r["id"], r["status"],
                        "—" if r["page"] is None else r["page"],
                        r["detail"], r["url"]))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# network (not covered by --self-test)
# ---------------------------------------------------------------------------

def fetch_doc(url: str) -> dict:
    """Download once, retry once. Returns a doc dict as classify() expects."""
    import requests
    last = "no response"
    for attempt in (1, 2):
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT},
                                timeout=FETCH_TIMEOUT, allow_redirects=True)
            if resp.status_code != 200:
                last = "HTTP %d" % resp.status_code
            else:
                body = resp.content
                if body[:1024].lstrip().startswith(b"%PDF"):
                    import fitz  # PyMuPDF
                    try:
                        with fitz.open(stream=body, filetype="pdf") as pdf:
                            return {"kind": "pdf",
                                    "pages": [p.get_text() for p in pdf]}
                    except Exception as e:  # corrupt / truncated download
                        last = "PDF 讀取失敗：%s" % type(e).__name__
                else:
                    return {"kind": "html", "text": html_visible_text(body)}
        except requests.RequestException as e:
            last = type(e).__name__
        if attempt == 1:
            time.sleep(3)
    return {"error": last}


def run_check(args) -> int:
    data = json.loads(ANCHORS.read_text(encoding="utf-8"))
    problems = validate_anchors(data)
    if problems:
        print("anchors file is not usable:", *problems, sep="\n  ", file=sys.stderr)
        return 2
    anchors = data["anchors"]
    if args.only:
        want = [x.strip() for x in args.only.split(",") if x.strip()]
        missing = [x for x in want if x not in anchors]
        if missing:
            print("not in anchors file: %s" % ", ".join(missing), file=sys.stderr)
            return 2
        anchors = {k: anchors[k] for k in want}

    previous = None
    if args.previous:
        try:
            previous = json.loads(Path(args.previous).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print("previous report unreadable (%s): treating every FETCH_FAIL as "
                  "a first failure" % e, file=sys.stderr)

    urls = sorted({a["url"] for a in anchors.values()})
    print("%d anchors · %d documents" % (len(anchors), len(urls)), flush=True)
    docs = {}
    for i, url in enumerate(urls):
        if i:
            time.sleep(FETCH_GAP_SECONDS)
        docs[url] = fetch_doc(url)
        d = docs[url]
        what = d.get("error") or ("pdf %d 頁" % len(d["pages"]) if d["kind"] == "pdf"
                                  else "html")
        print("  [%d/%d] %s — %s" % (i + 1, len(urls), what, url), flush=True)

    report = build_report(anchors, docs, previous,
                          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    if args.out:
        Path(args.out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    table = render_table(report)
    if args.table:
        Path(args.table).write_text(table, encoding="utf-8")
    print("\n" + table)
    # Results never change the exit code (same signal routing as the freshness,
    # served-URL and cover-title monitors): the workflow decides what to notify.
    return 0


# ---------------------------------------------------------------------------
# self-test (offline)
# ---------------------------------------------------------------------------

def self_test() -> int:
    fails = []

    def check(name: str, cond: bool):
        print("  %s  %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    check("norm folds full-width forms and drops every kind of whitespace",
          norm("ＡＢ Ｃ\n１２　３") == "ABC123")
    check("split_page reads #page=N", split_page("https://e/a.pdf#page=7")
          == ("https://e/a.pdf", 7))
    check("split_page without a fragment gives None",
          split_page("https://e/a.pdf") == ("https://e/a.pdf", None))

    pdf = {"kind": "pdf", "pages": ["封面 目錄", "津貼額為 每班 $1,000 元。", "附件 甲"]}
    a_ok = {"url": "u", "page": 2, "quote": "津貼額為每班$1,000元"}
    r = classify(a_ok, pdf)
    check("OK: quote on the recorded page (spacing differences ignored)",
          r["status"] == "OK" and r["found_pages"] == [2])
    r = classify(dict(a_ok, page=3), pdf)
    check("MOVED: quote on another page, new page listed",
          r["status"] == "MOVED" and r["found_pages"] == [2])
    r = classify(dict(a_ok, quote="津貼額為每班$2,000元"), pdf)
    check("GONE: quote nowhere in the document", r["status"] == "GONE")
    r = classify(a_ok, {"error": "HTTP 404"})
    check("FETCH_FAIL: download failed, status carried in the detail",
          r["status"] == "FETCH_FAIL" and r["detail"] == "HTTP 404")
    check("a quote repeated on several pages is OK when one of them is the recorded page",
          classify({"url": "u", "page": 3, "quote": "重複的一句說話"},
                   {"kind": "pdf", "pages": ["重複的一句說話", "x", "重複的一句說話"]}
                   )["status"] == "OK")
    span = {"kind": "pdf", "pages": ["甲", "前半句在第二頁末，", "後半句在第三頁首。"]}
    check("a quote across a page break belongs to the page it starts on",
          classify({"url": "u", "page": 2, "quote": "前半句在第二頁末，後半句在第三頁首"},
                   span)["status"] == "OK"
          and classify({"url": "u", "page": 3, "quote": "前半句在第二頁末，後半句在第三頁首"},
                       span)["status"] == "MOVED")

    web = {"kind": "html", "text": "2026/27 學年 入息上限為 $50,000"}
    check("web page: quote present is OK",
          classify({"url": "u", "page": None, "quote": "入息上限為$50,000"}, web)["status"] == "OK")
    check("web page: quote absent is GONE",
          classify({"url": "u", "page": None, "quote": "入息上限為$48,000"}, web)["status"] == "GONE")
    check("a PDF anchor answered by a web page is GONE, never OK",
          classify({"url": "u", "page": 2, "quote": "入息上限為$50,000"}, web)["status"] == "GONE")
    check("a web anchor (page null) answered by a PDF is OK when the quote is in it",
          classify({"url": "u", "page": None, "quote": "津貼額為每班$1,000元"}, pdf)["status"] == "OK")

    shell = ("<html><div id='menu'>選單 入息上限</div><div class='inner_page_content_container'>"
             "<script>var x='入息上限';</script><p>正文&nbsp;內容</p></div>"
             "<div id='footer_content'>頁腳 入息上限</div></html>").encode("utf-8")
    vis = norm(html_visible_text(shell))
    check("html text keeps only the main region, without scripts, menu or footer",
          "正文內容" in vis and "入息上限" not in vis)
    check("html without the EDB marker falls back to the whole page",
          "整頁文字" in norm(html_visible_text("<p>整頁 文字</p>".encode("utf-8"))))

    anchors = {"fn_a": a_ok, "fn_b": dict(a_ok, url="v")}
    docs = {"u": pdf, "v": {"error": "HTTP 503"}}
    rep = build_report(anchors, docs, None, "t")
    check("summary counts every status",
          rep["summary"] == {"OK": 1, "MOVED": 0, "GONE": 0, "FETCH_FAIL": 1, "total": 2})
    check("a first FETCH_FAIL is not an alert", rep["alerts"] == [])
    rep2 = build_report(anchors, docs, rep, "t2")
    check("a FETCH_FAIL that also failed in the previous report IS an alert",
          [x["id"] for x in rep2["alerts"]] == ["fn_b"])
    rep3 = build_report(anchors, {"u": {"kind": "pdf", "pages": ["x"]}, "v": pdf}, rep, "t3")
    check("GONE is an alert at once; a recovered download is not",
          [x["id"] for x in rep3["alerts"]] == ["fn_a"])
    check("the table lists only the rows that are not OK",
          "fn_b" in render_table(rep) and "fn_a" not in render_table(rep))

    good = {"_meta": {"count": 1},
            "anchors": {"f": {"url": "https://e/a.pdf", "page": 1, "quote": "一句足夠長的原文句子"}}}
    check("a well-formed anchors file validates", validate_anchors(good) == [])
    check("a url carrying #page= is rejected",
          validate_anchors({"_meta": {"count": 1}, "anchors": {
              "f": {"url": "https://e/a.pdf#page=1", "page": 1, "quote": "一句足夠長的原文句子"}}}) != [])
    check("a too-short quote is rejected",
          validate_anchors({"_meta": {"count": 1}, "anchors": {
              "f": {"url": "https://e/a.pdf", "page": 1, "quote": "短"}}}) != [])
    check("a wrong _meta.count is rejected",
          validate_anchors(dict(good, _meta={"count": 2})) != [])
    check("override mismatch: a different page is reported",
          override_mismatches(good["anchors"], {"f": {"url": "https://e/a.pdf#page=4"}}) != [])
    check("override mismatch: same url and page is clean",
          override_mismatches(good["anchors"], {"f": {"url": "https://e/a.pdf#page=1"}}) == [])

    # the real files
    try:
        data = json.loads(ANCHORS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = None
    check("dev/source/footnote_anchors.json exists and validates",
          data is not None and validate_anchors(data) == [])
    if data is not None:
        try:
            ov = json.loads(URL_OVERRIDES.read_text(encoding="utf-8")).get("overrides", {})
        except (OSError, ValueError):
            ov = None
        mism = override_mismatches(data.get("anchors", {}), ov or {})
        for m in mism:
            print("       " + m)
        check("every anchor agrees with dev/source/url_overrides.json on url and page",
              ov is not None and mism == [])

    print("\n%s" % ("ALL PASS" if not fails else "%d FAILED: %s" % (len(fails), fails)))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated footnote ids")
    ap.add_argument("--out", default="", help="write the JSON report here")
    ap.add_argument("--table", default="", help="write the markdown table here")
    ap.add_argument("--previous", default="", help="JSON report of the previous run")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.check:
        return run_check(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
