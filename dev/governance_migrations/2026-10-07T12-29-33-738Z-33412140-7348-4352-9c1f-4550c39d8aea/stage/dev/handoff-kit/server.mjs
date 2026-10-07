import http from 'node:http';
import {readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID,createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createSource} from './projection.mjs';
import {createDashboard} from './dashboard.mjs';
import {assetBytes,assetNames} from './assets.mjs';

const assets=path.dirname(fileURLToPath(import.meta.url));
// Fingerprint the shipped view so an old process is not reused after a source update.
const buildId=createHash('sha256');
for(const file of ['server.mjs','projection.mjs','dashboard.mjs','project-version.mjs','open.mjs','launch.mjs'])buildId.update(readFileSync(path.join(assets,file)));
for(const file of assetNames)buildId.update(assetBytes(file));
const build=buildId.digest('hex');
export const PROGRESS_IDLE_MS=8*60*60*1000;
export function progressIdentity(root,version='unknown'){
 const canonical=realpathSync.native(path.resolve(root));
 return {service:'agent-handoff-kit-progress',rootId:createHash('sha256').update(canonical).digest('hex'),version,build};
}
export function openProgressBrowser(url){
 const command=process.platform==='win32'?'rundll32.exe':process.platform==='darwin'?'open':'xdg-open';
 const args=process.platform==='win32'?['url.dll,FileProtocolHandler',url]:[url];
 try{const child=spawn(command,args,{windowsHide:true,stdio:'ignore',detached:process.platform!=='win32'});child.once('error',()=>console.error('Open the progress URL in your browser.'));child.unref();}catch{console.error('Open the progress URL in your browser.');}
}
export async function startProgress({root,port=0,openBrowser=true,version='unknown',idleMs=PROGRESS_IDLE_MS,onReady=null}={}){
 if(!Number.isInteger(port)||port<0||port>65535)throw Error('progress --port must be an integer from 0 to 65535');
 if(!Number.isSafeInteger(idleMs)||idleMs<1||idleMs>2147483647)throw Error('Invalid progress idle timeout');
 const source=createSource(root);source.refresh({immediate:true});
 const dashboard=createDashboard(root,source);dashboard.refresh();
 if(source.state.errors.handoff==='missing')throw Error('No dev/SESSION_HANDOFF.md found. Select an installed Kit project with --root.');
 const identity=progressIdentity(root,version),session=randomUUID(),clients=new Set(),sockets=new Set();let boundPort=0,stopping=false,watch=null,heartbeat=null,idleTimer=null;
 const envelope=()=>({templateVersion:'dashboard-1',kitVersion:version,session,...source.snapshot(),dashboard:dashboard.snapshot()});
 const json=(res,status,data)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(data));};
 const broadcast=()=>{const payload=`data: ${JSON.stringify(envelope())}\n\n`;for(const client of clients)client.write(payload);};
 const refresh=(immediate=false)=>{const changed=source.refresh({immediate});const dashboardChanged=dashboard.refresh();return changed||dashboardChanged;};
 const stopPolling=()=>{clearInterval(watch);clearInterval(heartbeat);watch=null;heartbeat=null;};
 const deferShutdown=()=>{clearTimeout(idleTimer);idleTimer=null;if(!stopping&&!clients.size)idleTimer=setTimeout(()=>void close(),idleMs);};
 const resumePolling=()=>{clearTimeout(idleTimer);idleTimer=null;if(!watch)watch=setInterval(()=>{if(refresh())broadcast();},500);if(!heartbeat)heartbeat=setInterval(()=>{for(const client of clients)client.write(': keepalive\n\n');},5000);};
 const server=http.createServer((req,res)=>{
  const host=`127.0.0.1:${boundPort}`;
  if(req.headers.host!==host||(req.headers.origin&&req.headers.origin!==`http://${host}`)||req.headers['sec-fetch-site']==='cross-site'){json(res,403,{error:'origin'});return;}
  if(req.method!=='GET'){json(res,405,{error:'read_only'});return;}
  try{
   const url=new URL(req.url,`http://${host}`);
   if(url.pathname==='/events'){
    if(refresh(true))broadcast();
    res.writeHead(200,{'Content-Type':'text/event-stream; charset=utf-8','Cache-Control':'no-store','Connection':'keep-alive','X-Content-Type-Options':'nosniff'});res.write(`data: ${JSON.stringify(envelope())}\n\n`);clients.add(res);resumePolling();
    res.on('close',()=>{clients.delete(res);if(!clients.size){stopPolling();deferShutdown();}});return;
   }
   if(url.pathname==='/api/identity'){if(url.searchParams.get('reopen')==='1')deferShutdown();json(res,200,identity);return;}
   if(['/api/state','/api/document','/api/history','/api/section'].includes(url.pathname)){if(refresh(true))broadcast();deferShutdown();}
   if(url.pathname==='/api/state'){json(res,200,envelope());return;}
   if(url.pathname==='/api/document'){json(res,200,dashboard.document(url.searchParams.get('id')));return;}
   if(url.pathname==='/api/history'){json(res,200,dashboard.history(Object.fromEntries(['from','to','search','work','cursor'].map(k=>[k,url.searchParams.get(k)||'']))));return;}
   if(url.pathname==='/api/section'){
    if(Number(url.searchParams.get('version'))!==source.snapshot().version){json(res,409,{error:'changed'});return;}
    const offset=url.searchParams.get('offset')||'0';if(!/^\d{1,7}$/.test(offset))throw Error('query');json(res,200,source.page(url.searchParams.get('kind'),Number(offset)));return;
   }
   const routes={'/':'index.html','/index.html':'index.html','/styles.css':'styles.css','/renderer.js':'renderer.js','/agent-handoff-kit-logo2-256.png':'agent-handoff-kit-logo2-256.png','/dashboard-hero.png':'dashboard-hero.png','/icons.svg':'icons.svg'};
   const file=Object.hasOwn(routes,url.pathname)?routes[url.pathname]:null;if(!file){json(res,404,{error:'not_found'});return;}
   deferShutdown();
   const type=file.endsWith('.png')?'image/png':file.endsWith('.svg')?'image/svg+xml':file.endsWith('.css')?'text/css':file.endsWith('.js')?'text/javascript':'text/html';
   res.writeHead(200,{'Content-Type':type+'; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"});res.end(assetBytes(file));
  }catch{json(res,400,{error:'unavailable'});}
 });
 const close=()=>new Promise(resolve=>{if(stopping){resolve();return;}stopping=true;stopPolling();clearTimeout(idleTimer);for(const c of clients)c.end();server.close(resolve);for(const socket of sockets)socket.destroy();process.removeListener('SIGINT',signal);process.removeListener('SIGTERM',signal);});
 server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});
 const signal=()=>{void close();};
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',()=>{server.removeListener('error',reject);resolve();});});
 boundPort=server.address().port;const url=`http://127.0.0.1:${boundPort}`;
 deferShutdown();
 process.once('SIGINT',signal);process.once('SIGTERM',signal);
 const result={url,close,source,server};if(onReady)onReady(result);
 if(openBrowser)openProgressBrowser(url);
 return result;
}
