// S174 — full held-out eval through the locally-built searchChannelB against live Supabase.
// Same code + data production will run after deploy. Measures projected post-fix accuracy.
const SB = "https://youkcekbrbywuqjxgibe.supabase.co";
process.env.SUPABASE_URL = SB;
process.env.SUPABASE_ANON_KEY = process.env.SUPABASE_SERVICE_KEY;
const OPENAI = process.env.OPENAI_API_KEY;
async function embedFn(text) {
  const r = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + OPENAI },
    body: JSON.stringify({ model: "text-embedding-3-small", input: text }),
  });
  return (await r.json()).data[0].embedding;
}
const { searchChannelB } = await import("../backend/dist/api/searchChannelB.js");

const HO = {
  fn_k1_regfee: ["幼稚園收咗家長半日留位錢可唔可以收成千蚊", ["970", "1,570", "1570"]],
  fn_k1_appfee: ["K1 派表收家長報名手續費收到幾多先唔犯規", ["40元", "40"]],
  fn_k1_eligibility: ["邊類學童先符合幼稚園資助 身份證明點睇", ["居留權", "入境權", "居留許可"]],
  fn_sag_receipt: ["邊啲情況可以遲啲先開正式收據畀家長", ["收費摘要表", "現金證明書", "放寬"]],
  fn_sag_increment: ["請咗長假冇糧 跳 point 同公積金年資點計", ["延遲一個月", "16 至", "增薪日期"]],
  fn_sag_parapet: ["想喺天台搞體育堂 圍欄要砌幾高先安全", ["6.0", "護牆"]],
  fn_kgadmin_utilrate: ["校舍用得幾盡會影響到我哋攞幾多租金津貼", ["空置課室", "使用率", "課室容額"]],
  fn_kgadmin_asset: ["啲枱櫈電腦盤點本簿 邊個要每年睇完簽名", ["加簽", "校監", "登記冊"]],
  fn_kgop_classroom: ["全日班瞓晏覺嗰間房最多可以放幾多個細路", ["20 人", "午睡", "20人"]],
  fn_kgop_ratio: ["一個老師睇十四個 BB 嗰個比例邊種中心先用得", ["特殊幼兒中心", "1:14", "SCCC"]],
  fn_imc_60pct: ["辦學團體派幾多個校董入校董會有冇封頂 替代嗰個算唔算", ["替代校董", "不計算"]],
  fn_imc_99b: ["法團校董會做生意賺到嘅錢可唔可以亂使", ["99B", "學生直接受益", "淨收入"]],
  fn_icac_appraisal: ["個職員成日遲到 評核打分到第幾次要扣級", ["三次"]],
  fn_icac_bidrig: ["幾間公司夾埋投標份反圍標聲明邊個要簽", ["各自簽署", "合營", "獲授權"]],
  fn_icac_coi: ["校董有親戚做緊我哋供應商可以點處理避嫌", ["放棄", "獨立人員"]],
  fn_activities_sen: ["特殊學校出去交流團 帶幾多個老師跟足夠", ["附錄X", "特殊學校"]],
  fn_activities_ambulance: ["去內地遊學要叫白車 啲錢邊個畀", ["車費", "治療費", "救護車"]],
  fn_activities_civilservant: ["官校老師帶團出 trip 整親點同上面報", ["公務員事務規例", "因公受傷"]],
  fn_g01_delegate: ["普通老師買嘢要唔要申報利益 邊個幫手批", ["授權校長", "利益衝突申報"]],
  fn_g01_approver: ["買幾千蚊嘅嘢冇副校長嗰陣搵邊個簽單", ["副校長", "批核人員"]],
  fn_supply_approval: ["請個代課老師做成年 使唔使開校董會通過", ["6個月", "大多數校董", "不少於 6"]],
  fn_supply_oneyear: ["代課老師走咗幾耐再請返要查返佢有冇案底", ["第一天", "刑事定罪", "離職"]],
  fn_surplus_def: ["點先叫做超額老師 多過編制咁簡單咩", ["時限職位", "超越", "編制"]],
  fn_phpri_time: ["小學人文科一星期至少要排幾多堂先夠鐘", ["7%", "百分之七"]],
  fn_g11_schooldays: ["全日同半日小學成年要返夠幾多日學", ["190", "209", "91"]],
  fn_tdtf_senco: ["做特殊教育統籌主任係咪等於升咗職", ["晉升職級", "2019/20"]],
  fn_childabuse_def: ["強制舉報講嘅細路係幾多歲以下先當數", ["18 歲", "附表2", "18歲"]],
  fn_prisci_exempt: ["教小學科學唔夠學歷 邊個可以拍板批", ["豁免", "保留", "證明"]],
  fn_g22_inspectfreq: ["張安全檢查表上面寫住 D W M T 係咩意思", ["每天", "每周", "每學期"]],
  fn_lsp_calc: ["員工做唔夠一年就走 遣散嗰筆錢點計法", ["365", "366", "剔除款項", "按比例"]],
  fn_coa_imc_apply: ["轉咗做法團校董會之後份資助則例幾時開始跟", ["緊隨", "成立", "則例"]],
  fn_imc_election_pta: ["家教會要符合邊條教育條例先入到校董會選舉", ["40AO", "認可家長教師會"]],
  fn_g21_astm: ["美術堂買嘅顏料盒寫住 ASTM 嗰串字代表咩", ["ASTM", "D-4236"]],
};
let answerable = 0, fnhit = 0;
const fails = [];
for (const [fid, [q, kws]] of Object.entries(HO)) {
  const res = await searchChannelB({ query: q, top_k: 8, synthesize: false }, embedFn);
  const blob = JSON.stringify(res.results || []);
  const fnPresent = (res.results || []).some((r) => r.id === "footnote_" + fid);
  const kwPresent = kws.some((k) => blob.includes(k));
  if (fnPresent) fnhit++;
  if (fnPresent || kwPresent) answerable++;
  else fails.push(fid);
}
const N = Object.keys(HO).length;
console.log(`=== 修復後 full held-out（${N}，本地建置=production code）===`);
console.log(`答案可得 = ${answerable}/${N} = ${(100 * answerable / N).toFixed(1)}%`);
console.log(`footnote 直接命中 = ${fnhit}/${N}`);
if (fails.length) console.log("未過:", fails.join(", "));
