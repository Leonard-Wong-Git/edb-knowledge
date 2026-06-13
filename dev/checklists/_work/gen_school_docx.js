// Generic school-version policy docx: node gen_school_docx.js <domain_key>
// Reads _work/<key>/clauses.json (chapters with clauses) + _work/<key>/checklist.json (cn + src map).
// Spec (Leonard-approved, finance pilot): 本校-voice clauses, X.Y numbering (chapter.clause),
// per-clause superscript markers, chapter-end deduplicated reference list (merged marker numbers,
// clickable #page=N), yellow-highlighted adjustables, cover sheet with usage notes + blanks.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  ExternalHyperlink, Footer, PageNumber,
} = require(path.join(__dirname, "node_modules/docx"));

const KEY = process.argv[2];
const WORK = __dirname;
const OUTBASE = path.join(WORK, "..");
const CH = JSON.parse(fs.readFileSync(path.join(WORK, KEY, "clauses.json"), "utf8"));
const CL = JSON.parse(fs.readFileSync(path.join(WORK, KEY, "checklist.json"), "utf8"));
const SRC = CL.src; // sid -> [title, url]
const CN = CL.cn;

const FONT = "Microsoft JhengHei";
const CONTENT_W = 9026;
const HILITE = "FFF2B8";

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: 22, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [children], ...o });
const sup = (n) => new TextRun({ text: String(n), font: FONT, size: 16, superScript: true, color: "1F4E36" });

function clauseRuns(text, adjustables) {
  let segs = [{ s: text, hi: false }];
  for (const a of (adjustables || []).filter(x => x && text.includes(x))) {
    const next = [];
    for (const seg of segs) {
      if (seg.hi) { next.push(seg); continue; }
      const parts = seg.s.split(a);
      parts.forEach((part, i) => {
        if (part) next.push({ s: part, hi: false });
        if (i < parts.length - 1) next.push({ s: a, hi: true });
      });
    }
    segs = next;
  }
  return segs.map(seg => seg.hi
    ? new TextRun({ text: seg.s, font: FONT, size: 22, shading: { fill: HILITE, type: ShadingType.CLEAR } })
    : t(seg.s));
}

const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };
function renderTable(tbl) {
  const ncol = tbl.headers.length;
  const w = ncol === 3 ? [2400, 4426, 2200] : Array(ncol).fill(Math.floor(CONTENT_W / ncol));
  const mk = (txt, head) => new TableCell({
    borders, width: { size: 0, type: WidthType.AUTO }, // placeholder replaced below
  });
  const rows = [new TableRow({
    children: tbl.headers.map((h, ci) => new TableCell({
      borders, width: { size: w[ci], type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      shading: { fill: "EFEFEF", type: ShadingType.CLEAR },
      children: [p(t(h, { bold: true, size: 20 }))],
    })),
  })];
  for (const r of tbl.rows) {
    rows.push(new TableRow({
      children: r.map((c, ci) => new TableCell({
        borders, width: { size: w[Math.min(ci, w.length - 1)], type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [p(t(String(c), { size: 20 }))],
      })),
    }));
  }
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: w, rows });
}

const children = [];
children.push(p(t(`本校${CN}政策`, { bold: true, size: 44 }), { alignment: AlignmentType.CENTER, spacing: { after: 80 } }));
children.push(p(t("（校本政策文件範本　·　草擬本）", { size: 24, color: "888888" }), { alignment: AlignmentType.CENTER, spacing: { after: 280 } }));
children.push(p(t("使用說明", { bold: true, size: 24 }), { spacing: { after: 80 } }));
[
  `本文件為校本「${CN}」政策範本，依據教育局現行指引整理而成，供本校管理層採納及按校情調整。`,
  "標示黃色底色之文字，為須由學校按自身情況填寫或選定之項目（例如校名、是否設有法團校董會、可調整之職級、委員會成員等），採納前請逐一核實修訂。",
  "每章末附「本章出處」，列明各條文所依據之教育局文件及頁碼，可點擊直接開啟原文相應頁面。如本文件與教育局原文有任何出入，概以教育局原文為準。",
].forEach(line => children.push(p(t(line, { size: 22, color: "555555" }), { spacing: { after: 80 } })));
const blank = () => new TextRun({ text: "【　　　　】", font: FONT, size: 22, shading: { fill: HILITE, type: ShadingType.CLEAR } });
children.push(p([t("制定日期：", { size: 22 }), blank(), t("　　法團校董會／校董會通過日期：", { size: 22 }), blank()], { spacing: { before: 160, after: 40 } }));
children.push(p([t("生效日期：", { size: 22 }), blank(), t("　　覆檢周期：", { size: 22 }), blank()]));

let totalClauses = 0;
for (const ch of CH) {
  const secNo = ch.section_no;
  if (!ch.clauses) continue;
  children.push(new Paragraph({
    heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
    children: [t(secNo + ". " + ch.name, { bold: true, size: 28 })],
    spacing: { after: 100 },
  }));
  let marker = 0;
  const refMap = new Map();
  ch.clauses.forEach((cl, ci) => {
    totalClauses++;
    const num = secNo + "." + (ci + 1);
    const markers = [];
    for (const c of (cl.citations || [])) {
      marker++; markers.push(marker);
      const key = c.source_id + "|" + c.page;
      if (!refMap.has(key)) refMap.set(key, { nums: [], sid: c.source_id, page: c.page });
      refMap.get(key).nums.push(marker);
    }
    const runs = [t(num + "　", { bold: true }), ...clauseRuns(cl.text, cl.adjustables)];
    markers.forEach((m, k) => { if (k) runs.push(t(" ", {})); runs.push(sup(m)); });
    children.push(p(runs, { spacing: { before: 120, after: 60 }, indent: { left: 480, hanging: 480 } }));
    if (cl.table && cl.table.headers && cl.table.headers.length) {
      children.push(renderTable(cl.table));
      children.push(p(t("", {}), { spacing: { after: 40 } }));
    }
  });
  if (refMap.size) {
    children.push(p(t("本章出處", { bold: true, size: 22, color: "1F4E36" }), { spacing: { before: 220, after: 60 } }));
    const entries = [...refMap.values()].sort((a, b) => a.nums[0] - b.nums[0]);
    for (const e of entries) {
      const [title, url] = SRC[e.sid] || [e.sid, ""];
      const label = (e.page && e.page > 0) ? `《${title}》第 ${e.page} 頁` : `《${title}》`;
      const link = (e.page && e.page > 0 && url) ? url + "#page=" + e.page : (url || "about:blank");
      children.push(p([
        t(e.nums.join(", ") + "　", { size: 18, color: "555555" }),
        new ExternalHyperlink({ children: [new TextRun({ text: label, style: "Hyperlink", font: FONT, size: 18 })], link }),
      ], { indent: { left: 420, hanging: 420 }, spacing: { after: 20 } }));
    }
  }
}
console.error("chapters:", CH.length, "clauses:", totalClauses);

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "1F4E36" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 0 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [t(`本校${CN}政策（範本草擬本）　·　第 `, { size: 18, color: "999999" }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999", font: FONT }), t(" 頁", { size: 18, color: "999999" })],
    })] }) },
    children,
  }],
});

const outdir = path.join(OUTBASE, KEY);
fs.mkdirSync(outdir, { recursive: true });
const OUT = path.join(outdir, `本校${CN}政策_學校版_DRAFT.docx`);
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("written:", OUT, buf.length, "bytes"); });
