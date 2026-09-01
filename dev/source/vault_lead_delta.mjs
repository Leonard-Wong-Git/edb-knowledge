#!/usr/bin/env node
/**
 * vault_lead_delta.mjs — S211 的確定性量度：vault-lead bypass 規則改動到底掂到邊幾個 case。
 *
 * 點解要有呢個腳本：judge 同 synthesis 都係 LLM 呼叫，冇設 temperature，所以整條 pipeline
 * 跑同一套 case 兩次會有唔同結果。S211 頭兩次 full-pipeline run 分別喺 GN02 同 GN03 出現
 * false answer，兩個都唔係改動掂得到嘅 case——純粹係雜訊，差啲就令人落錯結論。
 *
 * 檢索分數係 deterministic 嘅。所以呢個腳本唔叫 LLM，只係算出每個 case 嘅 forcedLeads、
 * slot0（舊規則睇嘅位）同 mainLead（新規則睇嘅位），再報邊個 case 嘅 bypass 判斷真係變咗。
 *
 * 用法：node dev/source/vault_lead_delta.mjs
 * 需要 backend/.env（OPENAI_API_KEY + SUPABASE_SERVICE_KEY）同已 build 嘅 backend/dist。
 * 唯讀：只讀 Supabase 同 OpenAI embedding，唔寫任何嘢。
 */
import fs from "node:fs";
const B="/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft";
const env={}; for(const l of fs.readFileSync(B+"/backend/.env","utf8").split("\n")){const i=l.indexOf("=");if(i>0&&!l.trim().startsWith("#"))env[l.slice(0,i).trim()]=l.slice(i+1).trim().replace(/^["']|["']$/g,"");}
process.env.OPENAI_API_KEY=env.OPENAI_API_KEY; process.env.OPENAI_MODEL="gpt-4o-mini";
process.env.SUPABASE_URL="https://youkcekbrbywuqjxgibe.supabase.co"; process.env.SUPABASE_ANON_KEY=env.SUPABASE_SERVICE_KEY;
const {searchChannelB}=await import(B+"/backend/dist/api/searchChannelB.js");
const {createEmbeddingClient}=await import(B+"/backend/dist/lib/embeddingClient.js");
const emb=createEmbeddingClient();
const noLlm=async()=>{throw new Error("no-llm");};   // synthesize 唔行，只睇檢索
const cases=JSON.parse(fs.readFileSync(B+"/dev/source/judge_acceptance_cases.json","utf8")).cases;
const all=[...cases,{id:"S211_target",query:"只修讀中學師資資格是否可以在小學任常額職位",want:"能"}];
const VAULT=0.70;
console.log("case                          want forced  slot0(舊規則)            mainLead(新規則)          舊→新");
for(const c of all){
  let r; try{ r=await searchChannelB({query:c.query},emb,noLlm);}catch(e){ console.log(c.id,"ERR"); continue; }
  const res=r.results||[];
  if(!res.length){ console.log(`${c.id.padEnd(29)} ${c.want}    (無結果)`); continue; }
  // 重算 forcedLeads：前面連續嘅 non-score-sorted 前綴 = 被強制插入嘅
  const sortedFrom=(k)=>{ for(let i=k;i<res.length-1;i++) if(res[i].score < res[i+1].score-1e-9) return false; return true; };
  let forced=0; while(forced<res.length && !sortedFrom(forced)) forced++;
  const s0=res[0], ml=res[forced]??res[0];
  const old=s0.content_type==="vault_extract"&&s0.score>=VAULT;
  const neu=ml.content_type==="vault_extract"&&ml.score>=VAULT;
  const mark=old!==neu?"  ***改變***":"";
  console.log(`${c.id.padEnd(29)} ${c.want}    ${forced}      ${(s0.content_type+" "+s0.score.toFixed(3)).padEnd(24)} ${(ml.content_type+" "+ml.score.toFixed(3)).padEnd(24)} ${old?"bypass":"judge "}→${neu?"bypass":"judge "}${mark}`);
}
