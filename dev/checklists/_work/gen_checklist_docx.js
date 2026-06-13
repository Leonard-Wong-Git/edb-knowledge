// Generic checklist docx generator: node gen_checklist_docx.js <domain_key>
// Reads _work/<key>/checklist.json; writes dev/checklists/<key>/校本<cn>政策文件要求清單_DRAFT.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  ExternalHyperlink, Footer, PageNumber,
} = require(path.join(__dirname, "node_modules/docx"));

const KEY = process.argv[2];
const TYPE = process.argv[3] || null; // primary|secondary|special|kindergarten | null = generic(all items)
const TYPE_LABEL = { primary: "小學", secondary: "中學", special: "特殊學校", kindergarten: "幼稚園" };
const okType = (st) => !TYPE || !st || !Array.isArray(st) || st.length === 0 || st.includes(TYPE);
const TYPE_SUFFIX = TYPE ? `（${TYPE_LABEL[TYPE]}適用版）` : "";
const WORK = __dirname;
const OUTBASE = path.join(WORK, "..");
const C = JSON.parse(fs.readFileSync(path.join(WORK, KEY, "checklist.json"), "utf8"));
// per-type filtered sections (drop items whose school_types excludes TYPE; drop emptied sections)
const SECTIONS = C.sections
  .map(s => ({ name: s.name, items: s.items.filter(it => okType(it.school_types)) }))
  .filter(s => s.items.length);
const USED_SIDS = new Set();
SECTIONS.forEach(s => s.items.forEach(it => USED_SIDS.add(it.source_id)));
const FONT = "Microsoft JhengHei";
const CONTENT_W = 9026;

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: 22, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [children], ...o });
const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };

const children = [];
children.push(p(t(`校本「${C.cn}」政策文件要求清單${TYPE_SUFFIX}`, { bold: true, size: 40 }), { spacing: { after: 80 } }));
children.push(p(t("（內部參考 · 草擬本 · 逐條附 EDB 原文出處）", { size: 24, color: "888888" }), { spacing: { after: 240 } }));
children.push(p(t("本清單由 EDB K1 知識平台自教育局官方文件蒸餾而成，供逐條對照校本政策文件。每條要求附原文出處（文件＋頁碼＋直跳連結）及原文引文；引文照錄 PDF 文字層原樣，怪空格／異體字屬抽取產物。本清單為指引義務整理，並非法律意見；如與教育局原文有出入，概以原文為準。", { size: 22, color: "555555" }), { spacing: { after: 240 } }));

// source table
children.push(p(t("來源文件", { bold: true, size: 28 }), { spacing: { after: 120 } }));
const srcRows = [new TableRow({
  children: ["編號", "文件", "連結"].map((h, ci) => new TableCell({
    borders, width: { size: [1700, 5826, 1500][ci], type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: { fill: "EFEFEF", type: ShadingType.CLEAR },
    children: [p(t(h, { bold: true, size: 22 }))],
  })),
})];
for (const [sid, [title, url]] of Object.entries(C.src)) {
  if (TYPE && !USED_SIDS.has(sid)) continue;
  srcRows.push(new TableRow({
    children: [
      new TableCell({ borders, width: { size: 1700, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [p(t(sid, { size: 18 }))] }),
      new TableCell({ borders, width: { size: 5826, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [p(t("《" + title + "》", { size: 20 }))] }),
      new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [p(new ExternalHyperlink({ children: [t("PDF", { style: "Hyperlink", size: 20 })], link: url || "about:blank" }))] }),
    ],
  }));
}
children.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [1700, 5826, 1500], rows: srcRows }));
children.push(p(t("", {})));

// section map
children.push(p(t("章節地圖", { bold: true, size: 28 }), { spacing: { before: 120, after: 120 } }));
const mapW = [700, 6326, 2000];
const mapRows = [new TableRow({
  children: ["章", "章節", "條目數"].map((h, ci) => new TableCell({
    borders, width: { size: mapW[ci], type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: { fill: "EFEFEF", type: ShadingType.CLEAR },
    children: [p(t(h, { bold: true, size: 22 }))],
  })),
})];
SECTIONS.forEach((s, i) => {
  mapRows.push(new TableRow({
    children: [String(i + 1), s.name, String(s.items.length)].map((v, ci) => new TableCell({
      borders, width: { size: mapW[ci], type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [p(t(v, { size: 22 }))],
    })),
  }));
});
children.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: mapW, rows: mapRows }));

// items
children.push(p(t("要求清單", { bold: true, size: 32 }), { pageBreakBefore: true, spacing: { after: 160 } }));
let total = 0;
SECTIONS.forEach((s, si) => {
  children.push(new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [t((si + 1) + ". " + s.name, { bold: true, size: 28 })],
    spacing: { before: 320, after: 80 },
  }));
  s.items.forEach((it, j) => {
    total++;
    const [title, url] = C.src[it.source_id];
    const code = "R-" + (si + 1) + "." + (j + 1);
    const add = it.addendum ? "（覆核補遺）" : "";
    children.push(p([t(code + "  ", { bold: true, size: 22 }), t(add + it.req, { size: 22 })],
      { spacing: { before: 160, after: 40 }, indent: { left: 360, hanging: 360 } }));
    if (it.no_page) {
      children.push(p([t("出處：", { size: 20, color: "555555" }),
        new ExternalHyperlink({ children: [t("《" + title + "》（無頁碼源）", { style: "Hyperlink", size: 20 })], link: url || "about:blank" })],
        { indent: { left: 360 }, spacing: { after: 20 } }));
    } else {
      const flag = it.approx ? " ⚠️頁碼近似" : "";
      children.push(p([t("出處：", { size: 20, color: "555555" }),
        new ExternalHyperlink({ children: [t("《" + title + "》第 " + it.page + " 頁", { style: "Hyperlink", size: 20 })], link: url + "#page=" + it.page }),
        t(flag, { size: 20, color: "555555" })],
        { indent: { left: 360 }, spacing: { after: 20 } }));
    }
    children.push(p(t("引文：「" + it.quote + "」", { size: 20, italics: true, color: "777777" }),
      { indent: { left: 360 }, spacing: { after: 60 } }));
  });
});

children.push(p(t("附錄：編製與核驗紀錄", { bold: true, size: 28 }), { pageBreakBefore: true, spacing: { after: 120 } }));
[
  `條目總數 ${total}。生成方法：原文片段蒸餾 → 獨立對抗覆核 → 完整性批判補遺 → 機械重驗（原樣→去空格→Unicode 相容字正規化三級引文比對＋頁碼按片段標記重計），未通過者一律剔除。`,
  "來源連結生成時驗證有效；標註「⚠️頁碼近似」者頁碼或與原文相差一頁；「（覆核補遺）」為完整性批判輪補回之項目。",
].forEach(line => children.push(p(t(line, { size: 20, color: "555555" }), { spacing: { after: 80 } })));

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "1F4E36" },
        paragraph: { spacing: { before: 320, after: 80 }, outlineLevel: 0 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [t(`校本「${C.cn}」要求清單（草擬本）　·　第 `, { size: 18, color: "999999" }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999", font: FONT }), t(" 頁", { size: 18, color: "999999" })],
    })] }) },
    children,
  }],
});

const outdir = path.join(OUTBASE, KEY);
fs.mkdirSync(outdir, { recursive: true });
const FNAME = TYPE ? `校本${C.cn}政策文件要求清單_${TYPE_LABEL[TYPE]}_DRAFT.docx` : `校本${C.cn}政策文件要求清單_DRAFT.docx`;
const OUT = path.join(outdir, FNAME);
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("written:", OUT, buf.length, "bytes, items:", total); });
