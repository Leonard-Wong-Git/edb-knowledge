#!/usr/bin/env node
/**
 * cache_drift.mjs — 量度 judge_acceptance 嘅凍結 chunk cache 同今日真檢索差幾遠（S211）。
 *
 * judge_acceptance.py 特登把 chunks 凍結，令每個 prompt variant 都судged 喺 byte-identical
 * 輸入上——嗰個設計係啱嘅。但佢有個副作用冇人量過：語料一路加，路由一路改，凍結嘅 top-5
 * 就會慢慢唔再係今日真正餵去 judge 嗰五段。到咁上下，harness 就係喺量一個已經唔存在嘅世界。
 *
 * 呢個腳本唔叫 LLM，只係對每個 cached case 重跑今日嘅檢索，比較 top-5 嘅重疊數。
 *
 * 用法：node dev/source/cache_drift.mjs
 * 需要 backend/.env 同已 build 嘅 backend/dist。唯讀。
 */
import fs from "node:fs";
const B="/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft";
const env={}; for(const l of fs.readFileSync(B+"/backend/.env","utf8").split("\n")){const i=l.indexOf("=");if(i>0&&!l.trim().startsWith("#"))env[l.slice(0,i).trim()]=l.slice(i+1).trim().replace(/^["']|["']$/g,"");}
process.env.OPENAI_API_KEY=env.OPENAI_API_KEY; process.env.OPENAI_MODEL="gpt-4o-mini";
process.env.SUPABASE_URL="https://youkcekbrbywuqjxgibe.supabase.co"; process.env.SUPABASE_ANON_KEY=env.SUPABASE_SERVICE_KEY;
const {searchChannelB}=await import(B+"/backend/dist/api/searchChannelB.js");
const {createEmbeddingClient}=await import(B+"/backend/dist/lib/embeddingClient.js");
const emb=createEmbeddingClient(); const noLlm=async()=>{throw new Error("x");};
const cache=JSON.parse(fs.readFileSync(B+"/dev/source/judge_runs/chunks_cache.json","utf8"));
const norm=t=>t.replace(/\s+/g,"").slice(0,60);
let same=0,drift=0; const rows=[];
for(const [id,v] of Object.entries(cache)){
  let r; try{ r=await searchChannelB({query:v.query},emb,noLlm);}catch(e){ continue; }
  const now=(r.results||[]).slice(0,5).map(c=>norm(c.text));
  const then=(v.chunks||[]).slice(0,5).map(c=>norm(typeof c==="string"?c:c.text||""));
  const overlap=now.filter(x=>then.includes(x)).length;
  if(overlap===5) same++; else drift++;
  rows.push([id, overlap]);
}
rows.sort((a,b)=>a[1]-b[1]);
console.log(`凍結 cache（2026-07-31）對今日真檢索：top-5 完全相同 ${same}/${same+drift}，有漂移 ${drift}\n`);
console.log("重疊數最少嘅 12 個：");
for(const [id,o] of rows.slice(0,12)) console.log(`  ${String(o)}/5 重疊  ${id}`);
