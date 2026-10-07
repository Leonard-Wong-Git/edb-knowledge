// Read-only projection of existing Kit records. No AI calls, generated summaries or source writes.
import {openSync,closeSync,readSync,fstatSync,statSync,realpathSync,existsSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
export const LIMITS={handoff:1024*1024,log:64*1024,recent:10,page:6,item:12000};
const names={
 'task-understanding-summary':'understanding','active-objective':'current','completed-this-session':'done',
 'next-priorities':'pending','risks-blockers':'risks','confirmed-decisions':'decisions'
};
const headings={
 'task understanding summary':'understanding','任務理解摘要':'understanding','active objective':'current','目前目標':'current',
 'completed this session':'done','本次完成':'done','本次已完成':'done','next priorities':'pending','下一步':'pending','下一步優先事項':'pending',
 'risks / blockers':'risks','風險與阻礙':'risks','風險 / 阻礙':'risks','confirmed decisions':'decisions','已確認決策':'decisions'
};
export const hash=v=>createHash('sha256').update(v).digest('hex');
const clean=s=>s.replace(/<!--.*?-->/g,'').replace(/^\s*(?:[-*+] |\d+[.)] )/,'').replace(/\*\*/g,'').trim();
const missing=s=>!s||/^(?:TBD|待填|尚未記錄|未提供)(?:\b|\s|$)/i.test(s)||/^<[^>]+>$/.test(s)||/^[^:：]{1,90}[:：]\s*(?:TBD|待填)(?:\b|\s|$)/i.test(s)||/^Record only work actually completed in the current session\./.test(s);
// Defensive display redaction. Source files remain untouched.
export const safe=s=>s.replace(/\b(?:sk-(?:ant-)?|gh[pousr]_|github_pat_|xox[baprs]-|AIza|AKIA)[A-Za-z0-9_-]{16,}/g,'<REDACTED>');
function item(text,file,line){text=safe(clean(text));return{id:hash(file+':'+line+':'+text).slice(0,16),text:text.slice(0,LIMITS.item),clipped:text.length>LIMITS.item,source:{file,line}};}

export function markdown(text,{prefix=false}={}){
 const lines=text.replace(/^\uFEFF/,'').split(/\r?\n/),sections=[];let fence=null,current=null,marker=null,title='',inComment=false,entryMarked=false,listContext=false;
 for(let i=0;i<lines.length;i++){
  let raw=lines[i];if(inComment){const end=raw.indexOf('-->');if(end<0)continue;raw=raw.slice(end+3);inComment=false;}
  const f=raw.match(/^\s{0,3}(`{3,}|~{3,})(.*)$/);
  if(f){if(!fence)fence=f[1];else if(f[1][0]===fence[0]&&f[1].length>=fence.length&&!f[2].trim())fence=null;continue;}if(fence)continue;
  if(/^(?: {4}|\t)/.test(raw)&&!listContext)continue;
  if(/^\s*<!-- ack:log-entry:start -->\s*$/.test(raw)){entryMarked=true;continue;}
  if(/^\s*<!-- ack:log-entry:end -->\s*$/.test(raw)){if(current)current.entryClosed=true;continue;}
  const m=raw.match(/^\s*<!-- ack:section:([a-z-]+) -->\s*$/);if(m){marker=m[1];continue;}
  while(raw.includes('<!--')){const start=raw.indexOf('<!--'),end=raw.indexOf('-->',start+4);if(end<0){raw=raw.slice(0,start);inComment=true;break;}raw=raw.slice(0,start)+raw.slice(end+3);}
  if(/^# [^#]/.test(raw)&&!title)title=raw.slice(2).trim();
  const h=raw.match(/^## (?!#)(.+?)\s*#*$/);
  if(h){if(current)current.end=i;current={title:h[1],key:names[marker]||headings[h[1].toLowerCase()]||null,line:i+1,rows:[],end:null,entryMarked,entryClosed:false};sections.push(current);marker=null;entryMarked=false;listContext=false;continue;}
  if(raw.trim()&&marker)marker=null;
  if(/^(?:[-*+] |\d+[.)] )/.test(raw))listContext=true;else if(raw.trim()&&!/^\s/.test(raw))listContext=false;
  if(current)current.rows.push({text:raw,line:i+1});
 }
 if((fence||inComment)&&!prefix)throw Error('incomplete');
 if(current&&!prefix)current.end=lines.length;
 return{title,sections};
}
function blocks(section,file){
 if(!section)return[];const out=[];let buffer=[],line=0;
 const following=new Array(section.rows.length);let nextRow=null;
 for(let i=section.rows.length-1;i>=0;i--){following[i]=nextRow;if(section.rows[i].text.trim())nextRow=section.rows[i];}
 const flush=()=>{const text=buffer.join(' ').trim();if(text&&!missing(clean(text)))out.push(item(text,file,line));buffer=[];};
 for(let i=0;i<section.rows.length;i++){
  const row=section.rows[i];
  if(!row.text.trim()){const next=following[i];if(buffer.length&&/^(?:[-*+] |\d+[.)] )/.test(buffer[0])&&next&&/^\s+\S/.test(next.text))continue;flush();continue;}
  if(/^#{3,}\s/.test(row.text)){flush();continue;}
  if(/^(?:[-*+] |\d+[.)] )/.test(row.text)){flush();line=row.line;buffer=[row.text];}
  else{if(!buffer.length)line=row.line;buffer.push(row.text);}
 }flush();return out;
}
const fieldNames=['Parent outcome / consumer','Current step','Task position','User intent','Task essence','User value','Resume point','Remaining acceptance','Completed within this task','Remaining acceptance / resume point','Recommended next step','專案目標','最終目標','目前階段','目前工作','任務位置','用戶意圖'];
const fieldPattern=new RegExp('(?:^|[.。]\\s+|\\s+(?=(?:Current step|目前階段)[:：]))('+fieldNames.map(s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')[:：]\\s*','gi');
function field(items,keys){for(const row of items){const matches=[...row.text.matchAll(fieldPattern)];for(let i=0;i<matches.length;i++){if(!keys.includes(matches[i][1].toLowerCase()))continue;const start=matches[i].index+matches[i][0].length,end=matches[i+1]?.index??row.text.length,value=row.text.slice(start,end).trim();if(!missing(value))return{...row,text:value};}}return null;}

export function parseHandoff(text,rootName='Project'){
 const parsed=markdown(text),groups={};
 for(const s of parsed.sections)if(s.key){if(groups[s.key])throw Error('duplicate');groups[s.key]=s;}
 if(!groups.current||!groups.pending||!groups.risks)throw Error('structure');
 const file='dev/SESSION_HANDOFF.md',all=Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,blocks(v,file)]));
 const understanding=all.understanding||[],active=all.current||[];
 const goal=field([...understanding,...active],['parent outcome / consumer','專案目標','最終目標'])||field(understanding,['user intent','用戶意圖']);
 const current=field(active,['current step','目前階段','目前工作'])||active.find(x=>!fieldNames.some(label=>x.text.toLowerCase().startsWith(label.toLowerCase()+':')||x.text.toLowerCase().startsWith(label.toLowerCase()+'：')))||null;
 const position=field(understanding,['task position','任務位置']);
 const title=parsed.title.replace(/\s+(?:Session\s+)?Handoff$/i,'').replace(/\s*交接(?:包|紀錄)?$/,'').trim();
 const name=!title||/^(?:Session|Handoff|Session Handoff)$/i.test(parsed.title)?rootName:title;
 const updated=text.match(/^Last Updated:\s*(.+)$/mi)?.[1]||text.match(/^最後更新[:：]\s*(.+)$/m)?.[1]||null;
 const collections={};for(const k of ['done','pending','risks','decisions'])collections[k]=all[k]||[];
 // Preserve source wording. Never infer that a child result completes the parent.
 return{name,goal,current,position,updated:missing(updated)?null:updated,collections,missingSections:['done','decisions'].filter(k=>!groups[k])};
}
// One event reader for both the bounded home prefix and paged history.
export function logEntry(s,file,startLine=1){
 if(!/^\d{4}-\d{2}-\d{2}\s*[—–-]/.test(s.title)||s.entryMarked&&!s.entryClosed)return null;
 const date=s.title.slice(0,10);if(Number.isNaN(Date.parse(date))||new Date(date+'T00:00:00Z').toISOString().slice(0,10)!==date)return null;
 const fields={};let active=null;const prose=[];
 for(const row of s.rows){
  const text=safe(clean(row.text)),nested=/^(?: {2,}|\t)/.test(row.text);
  const m=!nested&&text.match(/^([A-Za-z][A-Za-z0-9 _/-]{0,80})[:：]\s*(.*)$/);
  if(m){active=m[1].toLowerCase();fields[active]=missing(m[2])||/^[—-]$/.test(m[2])?'':m[2];}
  else if(nested&&active&&text)fields[active]+=(fields[active]?'\n':'')+text;
  else if(text){active=null;prose.push(text);}
 }
 for(const key of Object.keys(fields))if(!fields[key])delete fields[key];
 const body=safe(s.rows.map(x=>x.text).join('\n').trim()),explicit=fields['event id'];
 return{id:hash(explicit?'id:'+explicit:s.title+'\n'+body).slice(0,24),fingerprint:hash(s.title+'\n'+body),date,title:safe(s.title.slice(10).replace(/^\s*[—–-]\s*/,'')),titleZh:fields['title zh-hant']||null,summary:fields.summary||fields.done||prose[0]||'',summaryZh:fields['summary zh-hant']||null,work:fields.work||null,fields,body,source:{file,line:startLine+s.line-1}};
}
export function parseLog(text,limited=false){
 const {sections}=markdown(text,{prefix:limited}),entries=[];
 for(const s of sections){
  if(!/^\d{4}-\d{2}-\d{2}\s*[—–-]/.test(s.title))continue;
  if((limited&&s.end===null&&!s.entryClosed)||(s.entryMarked&&!s.entryClosed))continue; // Never display an unclosed or chopped entry as complete.
  const entry=logEntry(s,'dev/SESSION_LOG.md');if(!entry)continue;
  entries.push({...entry,title:safe(s.title),summary:entry.summary?item(entry.summary,entry.source.file,s.line):null,body:entry.body.slice(0,LIMITS.item)});
  if(entries.length===LIMITS.recent)break;
 }
 return{entries,limited:limited||sections.filter(s=>/^\d{4}-\d{2}-\d{2}\s*[—–-]/.test(s.title)).length>LIMITS.recent};
}
export function readBounded(root,file,limit,{prefix=false}={}){
 const target=path.join(root,file),real=realpathSync(target),relative=path.relative(root,real);
 if(relative.startsWith('..')||path.isAbsolute(relative))throw Error('boundary');
 const fd=openSync(real,'r');try{
  const before=fstatSync(fd);if(!before.isFile()||(!prefix&&before.size>limit))throw Error('capacity');
  const checked=realpathSync(target),relativeNow=path.relative(root,checked);
  if(checked!==real||relativeNow.startsWith('..')||path.isAbsolute(relativeNow)||statSync(checked).ino!==before.ino)throw Error('boundary');
  const count=Math.min(before.size,limit),buffer=Buffer.alloc(count);let offset=0;
  while(offset<count){const n=readSync(fd,buffer,offset,count-offset,offset);if(!n)throw Error('unstable');offset+=n;}
  const after=fstatSync(fd),now=statSync(target);
  if(before.size!==after.size||before.mtimeMs!==after.mtimeMs||now.ino!==before.ino||now.size!==before.size||now.mtimeMs!==before.mtimeMs)throw Error('unstable');
  const limited=before.size>limit;let content=new TextDecoder('utf-8',{fatal:true}).decode(limited?buffer.subarray(0,Math.max(0,buffer.lastIndexOf(10)+1)):buffer);
  return{text:content,hash:hash(content),bytesRead:offset,limited,mtime:new Date(before.mtimeMs).toISOString()};
 }finally{closeSync(fd);}
}
export function signature(root,file){try{const target=path.join(root,file),real=realpathSync(target),r=path.relative(root,real);if(r.startsWith('..')||path.isAbsolute(r))return'boundary';const s=statSync(target);return[s.ino,s.size,s.mtimeMs,s.ctimeMs].join(':');}catch(e){return e.code==='ENOENT'?'missing':'unreadable';}}
export function createSource(projectRoot){
 const root=realpathSync(path.resolve(projectRoot)),files=['dev/SESSION_HANDOFF.md','dev/SESSION_LOG.md'];
 const state={handoff:null,log:null,errors:{},metrics:{reads:0,bytes:0,handoffBytes:0,logBytes:0},rootName:path.basename(root)};
 const seen=new Map(),pending=new Map();let previous='',version=0;
 function refresh({immediate=false}={}){
  if(existsSync(path.join(root,'dev/governance_migrations/.upgrade.lock'))){state.errors.lock='upgrade';}
  else{
   delete state.errors.lock;
   for(const file of files){const key=file.includes('HANDOFF')?'handoff':'log',sig=signature(root,file);
    if(seen.get(file)===sig&&!['unreadable','unstable'].includes(state.errors[key]))continue;
    if(!immediate&&pending.get(file)!==sig){pending.set(file,sig);continue;}
    try{
     const read=readBounded(root,file,LIMITS[key],{prefix:key==='log'});state.metrics.reads++;state.metrics.bytes+=read.bytesRead;state.metrics[key+'Bytes']=read.bytesRead;
     const parsed=key==='handoff'?parseHandoff(read.text,state.rootName):parseLog(read.text,read.limited);
     state[key]={...parsed,meta:{file,updated:read.mtime,hash:read.hash,bytesRead:read.bytesRead,limited:read.limited}};if(key==='handoff')state.acceptedHandoff=read.text;delete state.errors[key];
    }catch(e){state.errors[key]=['capacity','boundary','structure','incomplete','duplicate','unstable'].includes(e.message)?e.message:sig==='missing'?'missing':'unreadable';}
    seen.set(file,sig);pending.delete(file);
   }
  }
  const value=JSON.stringify({handoff:state.handoff,log:state.log,errors:state.errors});if(value===previous)return false;previous=value;version++;return true;
 }
 function snapshot(){const h=state.handoff;return{schemaVersion:2,version,project:{name:h?.name||state.rootName,goal:h?.goal||null,current:h?.current||null,position:h?.position||null},recordDate:h?.updated||null,available:!!h,sections:Object.fromEntries(['done','pending','risks','decisions'].map(k=>[k,{items:(h?.collections[k]||[]).slice(0,k==='risks'?2:3),total:h?.collections[k]?.length||null}])),recent:{items:(state.log?.entries||[]).slice(0,3),total:state.log?.entries.length??null,limited:state.log?.limited||false},sources:[h?.meta,state.log?.meta].filter(Boolean),errors:{...state.errors},limits:LIMITS};}
 function page(kind,offset=0){if(!['done','pending','risks','decisions','recent'].includes(kind)||!Number.isSafeInteger(offset)||offset<0)throw Error('query');const items=kind==='recent'?state.log?.entries||[]:state.handoff?.collections[kind]||[];if(offset>items.length)throw Error('query');return{version,kind,offset,total:items.length,items:items.slice(offset,offset+LIMITS.page),next:offset+LIMITS.page<items.length?offset+LIMITS.page:null,previous:offset?Math.max(0,offset-LIMITS.page):null};}
 return{root,state,refresh,snapshot,page};
}
