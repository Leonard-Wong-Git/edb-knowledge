// Deterministic, read-only dashboard. Existing Markdown remains authoritative.
import {openSync,closeSync,readSync,fstatSync,statSync,realpathSync,existsSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {readBounded,signature,markdown,safe,logEntry} from './projection.mjs';
import {parseProjectIndexTemplateVersion} from './project-version.mjs';

export const DASH_LIMITS=Object.freeze({document:1024*1024,metadata:512*1024,items:128,documents:160,historyBytes:256*1024,historyFiles:4,historyPage:20,entryBytes:64*1024,cursors:32});
const digest=s=>createHash('sha256').update(s).digest('hex');
const states=new Set(['planned','active','waiting','review','done','paused','dropped']);
const clean=s=>safe(String(s||'').replace(/\*\*/g,'').replace(/^\s*[-*]\s+/,'').trim());
const placeholder=s=>!s||s==='TBD'||/^<.*>$/.test(s)||s==='—'||s==='-';
const lines=s=>s.replace(/^\uFEFF/,'').split(/\r?\n/);
const key=s=>clean(s).toLowerCase();
const known=[
 ['handoff','dev/SESSION_HANDOFF.md','handoff','current'],['log','dev/SESSION_LOG.md','log','history'],
 ['archive','dev/SESSION_LOG_archive/INDEX.md','archive','history'],['index','dev/PROJECT_INDEX.md','index','reference'],
 ['rules','AGENTS.md','rules','rules'],['packs','dev/RULE_PACKS.md','packs','rules'],
 ['decisions','dev/PROJECT_DECISIONS.md','decisions','reference'],['sync','dev/DOC_SYNC_REGISTRY.md','sync','reference']
];
function section(text,title){return markdown(text).sections.find(s=>key(s.title)===title.toLowerCase());}
function table(section){
 if(!section)return[];let headers=null,out=[];
 for(const r of section.rows){if(!r.text.trim().startsWith('|'))continue;const cells=r.text.trim().replace(/^\||\|$/g,'').split(/(?<!\\)\|/).map(x=>clean(x.replace(/\\\|/g,'|')));
  if(cells.every(x=>/^:?-+:?$/.test(x)))continue;
  if(!headers){headers=cells.map(key);continue;}
  out.push({...Object.fromEntries(headers.map((h,i)=>[h,cells[i]||''])),line:r.line});
 }return out;
}
function fields(s){const out={};for(const r of s?.rows||[]){const m=clean(r.text).match(/^([^:：]+)[:：]\s*(.*)$/);if(m&&!placeholder(m[2]))out[key(m[1])]=m[2];}return out;}
function relativeFile(value){
 const s=String(value||'').replace(/`/g,'').split('#')[0];
 if(!s||s.includes('\\')||s.includes('\0')||path.isAbsolute(s)||/^[a-z]+:/i.test(s)||s.split('/').some(x=>!x||x==='.'||x==='..'||x.startsWith('.'))||/(?:^|\/)(?:node_modules|governance_migrations)(?:\/|$)/i.test(s)||/(?:credential|secret|\.env|private.key)/i.test(s))return null;
 return s;
}
function checked(root,file){const rel=relativeFile(file);if(!rel)throw Error('boundary');const real=realpathSync(path.join(root,rel)),r=path.relative(root,real);if(r.startsWith('..')||path.isAbsolute(r))throw Error('boundary');if(!statSync(real).isFile())throw Error('not_file');return real;}

export function parseWork(text){
 const sections=markdown(text).sections.filter(s=>key(s.title)==='work items');if(sections.length>1)throw Error('work_format');
 const s=sections[0];if(!s)return {items:[],recorded:false};
 if(!s.rows.some(r=>/^\|\s*ID\s*\|\s*Title\s*\|\s*Status\s*\|\s*Parent\s*\|\s*Summary\s*\|\s*Source\s*\|/i.test(r.text.trim())))throw Error('work_format');
 const rows=table(s).filter(r=>!placeholder(r.id));if(rows.length>DASH_LIMITS.items)throw Error('work_capacity');
 const ids=new Set();const items=rows.map(r=>{
  if(!/^[a-z0-9][a-z0-9_-]{0,63}$/i.test(r.id)||ids.has(r.id)||!states.has(r.status)||placeholder(r.title))throw Error('work_format');ids.add(r.id);
  const source=placeholder(r.source)?null:relativeFile(r.source);if(!placeholder(r.source)&&!source)throw Error('work_source');
  return {id:r.id,title:r.title,titleZh:r['title zh-hant']||null,status:r.status,parent:placeholder(r.parent)?null:r.parent,summary:r.summary||'',summaryZh:r['summary zh-hant']||null,artifact:source,source:{file:'dev/SESSION_HANDOFF.md',line:r.line}};
 });
 for(const item of items){let at=item,seen=new Set();while(at.parent){if(seen.has(at.id))throw Error('work_cycle');seen.add(at.id);at=items.find(x=>x.id===at.parent);if(!at)throw Error('work_parent');}}
 return {items,recorded:true};
}
export function parseProfile(text){const f=fields(section(text,'Project'));return {name:f.name||null,nameZh:f['name zh-hant']||null,goal:f.goal||null,goalZh:f['goal zh-hant']||null};}

function logEntries(text,file,startLine=1){
 return markdown(text).sections.map(s=>logEntry(s,file,startLine)).filter(Boolean);
}

export function createDashboard(root,source){
 root=realpathSync(root);const cache=new Map(),cursors=new Map(),watched=new Map();let acceptedIndex=null,projectKitVersion=null,historyRevision=0,revision=0,work={items:[],recorded:false},profile={},docs=[],links=[],errors={},last='';
 function read(file,limit=DASH_LIMITS.metadata){const sig=signature(root,file),old=cache.get(file);if(old?.sig===sig)return old;try{const r=readBounded(root,file,limit);const v={...r,sig};cache.set(file,v);return v;}catch(e){const v={sig,error:e.message,previous:old?.error?old.previous:old};cache.set(file,v);return v;}}
 function refresh(){if(existsSync(path.join(root,'dev/governance_migrations/.upgrade.lock')))return false;
  errors={};const h=source?.state?{text:source.state.acceptedHandoff,error:source.state.errors.handoff||(!source.state.acceptedHandoff?'unavailable':null)}:read('dev/SESSION_HANDOFF.md',DASH_LIMITS.document);let i=read('dev/PROJECT_INDEX.md');
  projectKitVersion=i.error?null:parseProjectIndexTemplateVersion(i.text);
  if(!h.error){try{work=parseWork(h.text);}catch(e){errors.work=e.message;}}else errors.work=h.error;
  if(!i.error){try{const next=parseProfile(i.text);const block=section(i.text,'Project');if((profile.name||profile.goal)&&!block||block&&!block.rows.some(r=>/^(?:-\s*)?Name:\s*\S/.test(r.text)))throw Error('index_format');profile=next;acceptedIndex=i;}catch{errors.index='format';i=acceptedIndex||{error:'format'};}}else{if(i.sig!=='missing'||acceptedIndex)errors.index=i.error;if(acceptedIndex)i=acceptedIndex;}
  const all=known.map(([id,file,role,group])=>({id,file,role,group,title:null,registered:true}));
  if(!i.error){for(const r of table(section(i.text,'Directory Map'))){const file=relativeFile(r.path);if(file&&!all.some(x=>x.file===file)&&/\.(md|txt|html|pdf|csv|json)$/i.test(file))all.push({id:digest(file).slice(0,16),file,role:'document',group:'reference',title:r.role||file,registered:true,source:{file:'dev/PROJECT_INDEX.md',line:r.line}});}}
  for(const item of work.items)if(item.artifact&&!all.some(x=>x.file===item.artifact))all.push({id:digest(item.artifact).slice(0,16),file:item.artifact,role:'artifact',group:'results',title:item.title,titleZh:item.titleZh,registered:true,source:item.source});
  if(all.length>DASH_LIMITS.documents)errors.documents='capacity';
  docs=all.slice(0,DASH_LIMITS.documents).map(d=>{try{const st=statSync(checked(root,d.file));return {...d,available:true,updated:new Date(st.mtimeMs).toISOString(),bytes:st.size};}catch{return {...d,available:false};}});
  links=[['index','handoff','routes'],['rules','handoff','governs'],['packs','rules','routes'],['log','archive','archives']].filter(([a,b])=>docs.some(x=>x.id===a&&x.available)&&docs.some(x=>x.id===b&&x.available)).map(([from,to,type])=>({from,to,type,basis:'kit-contract'}));
  // Project-specific links must be explicit, never inferred from prose or filenames.
  if(!i.error)for(const r of table(section(i.text,'Document Relations'))){const a=docs.find(x=>x.file===relativeFile(r.from)),b=docs.find(x=>x.file===relativeFile(r.to));if(a&&b&&['references','routes','mirrors','checks'].includes(r.relation))links.push({from:a.id,to:b.id,type:r.relation,basis:'dev/PROJECT_INDEX.md',line:r.line});}
  for(const file of ['dev/SESSION_LOG.md','dev/SESSION_LOG_archive/INDEX.md',...watched.keys()]){const sig=signature(root,file);if(watched.has(file)&&watched.get(file)!==sig)historyRevision++;watched.set(file,sig);}
  const value=JSON.stringify({work,profile,projectKitVersion,docs,links,errors,historyRevision});if(value===last)return false;last=value;revision++;return true;
 }
 function snapshot(){return{revision,historyRevision,work,profile,projectKitVersion,documents:docs,links,errors,limits:DASH_LIMITS};}
 function document(id){if(existsSync(path.join(root,'dev/governance_migrations/.upgrade.lock')))throw Error('upgrade');const doc=docs.find(x=>x.id===id);if(!doc)throw Error('unknown_document');checked(root,doc.file);if(!/\.(md|txt|csv|json)$/i.test(doc.file))return{...doc,text:null,reason:'preview_unavailable'};const r=readBounded(root,doc.file,DASH_LIMITS.document);return{...doc,text:safe(r.text),updated:r.mtime,hash:r.hash};}
 function history({from='',to='',search='',work:workId='',cursor=''}={}){
  if(existsSync(path.join(root,'dev/governance_migrations/.upgrade.lock')))throw Error('upgrade');
  for(const d of [from,to])if(d&&(!/^\d{4}-\d{2}-\d{2}$/.test(d)||Number.isNaN(Date.parse(d))||new Date(d+'T00:00:00Z').toISOString().slice(0,10)!==d))throw Error('date');if(from&&to&&from>to)throw Error('date');if(search.length>100||workId.length>64)throw Error('query');
  const query={from,to,search,workId},q=digest(JSON.stringify(query));let job;
  if(cursor){job=cursors.get(cursor);if(!job||job.q!==q||Date.now()-job.created>15*60_000)throw Error('expired');cursors.delete(cursor);for(const [file,sig]of Object.entries(job.signatures))if(signature(root,file)!==sig)throw Error('history_changed');}
  else{
   const files=['dev/SESSION_LOG.md'],warnings=[];const idx=read('dev/SESSION_LOG_archive/INDEX.md');
   if(!idx.error){const block=section(idx.text,'Batch 清單')||section(idx.text,'Batches')||markdown(idx.text).sections.find(s=>s.rows.some(x=>/\|.*(?:File path|Path).*\|/i.test(x.text)));const rows=table(block);
    if(!block||!block.rows.some(r=>/\|.*Date range.*\|.*(?:File path|Path).*\|/i.test(r.text)))warnings.push('archive_index');
    for(const r of rows){const file=String(r['file path']||r.path||'').replace(/`/g,'');const rel=relativeFile('dev/SESSION_LOG_archive/'+file);if(!rel||!/^archive_[\w.-]+\.md$/.test(file)){warnings.push('archive_index');continue;}
     const dates=String(r['date range']||'').match(/\d{4}-\d{2}-\d{2}/g);if(!dates||dates.length!==2||dates[0]>dates[1]||dates.some(d=>Number.isNaN(Date.parse(d))||new Date(d+'T00:00:00Z').toISOString().slice(0,10)!==d)){warnings.push('archive_range');files.push(rel);continue;}
     if((!from||dates[1]>=from)&&(!to||dates[0]<=to))files.push(rel);
    }
   }else if(idx.sig!=='missing')warnings.push('archive_index');
   else if(existsSync(path.join(root,'dev/SESSION_LOG_archive')))warnings.push('archive_index');
   job={q,query,files:[...new Set(files)],index:0,offset:0,line:1,buffer:'',entry:'',entryLine:1,fence:null,seen:{},queue:[],warnings:[...new Set(warnings)],created:Date.now(),signatures:{'dev/SESSION_LOG_archive/INDEX.md':signature(root,'dev/SESSION_LOG_archive/INDEX.md')},bytes:0};
  }
  // Bound every request independently of total history. Resume byte offsets using an opaque cursor.
  let budget=DASH_LIMITS.historyBytes,fileBudget=DASH_LIMITS.historyFiles;
  const emit=(text,file,line)=>{try{if(text.includes('<!-- ack:log-entry:start -->')&&!text.includes('<!-- ack:log-entry:end -->'))job.warnings.push('incomplete_entry');for(const item of logEntries(text,file,line)){
   if(from&&item.date<from||to&&item.date>to||workId&&item.work!==workId||search&&!`${item.title}\n${item.body}`.toLocaleLowerCase().includes(search.toLocaleLowerCase()))continue;
   if(job.seen[item.id]){if(job.seen[item.id]!==item.fingerprint)job.warnings.push('event_conflict');continue;}job.seen[item.id]=item.fingerprint;job.queue.push(item);
  }}catch{job.warnings.push('incomplete_entry');}};
  while(job.queue.length<DASH_LIMITS.historyPage&&job.index<job.files.length&&budget>0&&fileBudget>0){
   const file=job.files[job.index];let fd;
   try{
    const real=checked(root,file),sig=signature(root,file);if(job.signatures[file]&&job.signatures[file]!==sig)throw Error('history_changed');job.signatures[file]=sig;
    if(watched.size>=130&&!watched.has(file)){const victim=[...watched.keys()].find(x=>x.includes('/archive_'));if(victim)watched.delete(victim);}watched.set(file,sig);
    fd=openSync(real,'r');const st=fstatSync(fd);if(st.size<job.offset)throw Error('history_changed');
    const len=Math.min(32768,budget,st.size-job.offset),buf=Buffer.alloc(len);const n=readSync(fd,buf,0,len,job.offset);job.offset+=n;budget-=n;job.bytes+=n;
    // Buffer bytes between chunks so a multi-byte UTF-8 character is never split.
    const pending=Buffer.concat([Buffer.from(job.buffer,'base64'),buf.subarray(0,n)]);const end=job.offset===st.size?pending.length:pending.lastIndexOf(10)+1;
    job.buffer=pending.subarray(end).toString('base64');if(pending.length>DASH_LIMITS.entryBytes&&end===0)throw Error('entry_capacity');
    const text=new TextDecoder('utf-8',{fatal:true}).decode(pending.subarray(0,end));
    for(const raw of text?text.split('\n').slice(0,text.endsWith('\n')?-1:undefined):[]){
     const line=raw.replace(/\r$/,'');let visible=line;
     if(!job.fence&&!/^\s*<!-- ack:log-entry:(?:start|end) -->\s*$/.test(line)){if(job.inComment){const end=visible.indexOf('-->');if(end<0)visible='';else{visible=visible.slice(end+3);job.inComment=false;}}while(visible.includes('<!--')){const start=visible.indexOf('<!--'),end=visible.indexOf('-->',start+4);if(end<0){visible=visible.slice(0,start);job.inComment=true;break;}visible=visible.slice(0,start)+visible.slice(end+3);}}
     const f=visible.match(/^\s*(`{3,}|~{3,})(.*)$/);if(f){if(!job.fence)job.fence=f[1];else if(job.fence[0]===f[1][0]&&f[1].length>=job.fence.length&&!f[2].trim())job.fence=null;}
     if(!job.fence&&!job.inComment&&/^\s*<!-- ack:log-entry:start -->\s*$/.test(line)){if(job.entry)emit(job.entry,file,job.entryLine);job.entry='';job.marked=true;job.line++;continue;}
     const heading=!job.fence&&/^## \d{4}-\d{2}-\d{2}\s*[—–-]/.test(visible);
     if(heading){if(job.entry)emit(job.entry,file,job.entryLine);job.entry=(job.marked?'<!-- ack:log-entry:start -->\n':'')+line+'\n';job.entryLine=job.line-(job.marked?1:0);job.marked=false;}
     else if(job.entry)job.entry+=line+'\n';
     if(Buffer.byteLength(job.entry)>DASH_LIMITS.entryBytes){job.entry='';job.warnings.push('entry_capacity');}job.line++;
    }
    if(signature(root,file)!==sig||fstatSync(fd).mtimeMs!==st.mtimeMs)throw Error('history_changed');
    if(job.offset===st.size){if(job.entry)emit(job.entry,file,job.entryLine);if(job.marked||job.fence||job.inComment)job.warnings.push('incomplete_entry');job.index++;job.offset=0;job.line=1;job.entry='';job.buffer='';job.fence=null;job.marked=false;job.inComment=false;fileBudget--;}
   }catch(e){if(e.message==='history_changed')throw e;job.warnings.push(e.message==='boundary'?'boundary':'history_unreadable');job.index++;job.offset=0;job.line=1;job.entry='';job.buffer='';job.fence=null;job.marked=false;fileBudget--;}
   finally{if(fd!==undefined)closeSync(fd);}
  }
  job.queue.sort((a,b)=>b.date.localeCompare(a.date));const items=job.queue.splice(0,DASH_LIMITS.historyPage);const complete=job.index>=job.files.length&&!job.queue.length;
  // Cap remembered deduplication identities; explicit coverage warning instead of silent unbounded growth.
  if(Object.keys(job.seen).length>10000){job.warnings.push('history_capacity');job.index=job.files.length;job.queue=[];}
  let next=null;if(!complete&&Object.keys(job.seen).length<=10000){next=digest(q+Date.now()+Math.random());job.created=Date.now();if(cursors.size>=DASH_LIMITS.cursors)cursors.delete(cursors.keys().next().value);cursors.set(next,job);}
  return{items,next,complete:complete&&!job.warnings.length,warnings:[...new Set(job.warnings)],bytesRead:DASH_LIMITS.historyBytes-budget,filesChecked:job.index,totalFiles:job.files.length,range:{from,to},revision};
 }
 return{refresh,snapshot,document,history};
}
