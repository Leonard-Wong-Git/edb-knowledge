import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {progressIdentity,openProgressBrowser} from './server.mjs';
import {createSource} from './projection.mjs';
const cli=fileURLToPath(new URL('./launch.mjs',import.meta.url));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
export function probeProgress(port,{reopen=false}={}){
 return new Promise(resolve=>{
  let done=false,request,response,deadline;
  const end=value=>{if(done)return;done=true;clearTimeout(deadline);response?.destroy();request?.destroy();resolve(value);};
  // Inactivity timeouts alone can be kept alive by a foreign slow-trickle server.
  deadline=setTimeout(()=>end(null),350);
  request=http.get({hostname:'127.0.0.1',port,path:'/api/identity'+(reopen?'?reopen=1':'')},res=>{
   response=res;let text='';if(res.statusCode!==200){end(null);return;}
   res.on('data',chunk=>{text+=chunk;if(text.length>2048)end(null);});
   res.on('end',()=>{try{end(JSON.parse(text));}catch{end(null);}});
   res.on('error',()=>end(null));res.on('aborted',()=>end(null));
  });
  request.on('error',()=>end(null));
 });
}
export async function openProgress({root,version,port=0,openBrowser=true}){
 if(!Number.isInteger(port)||port<0||port>65535)throw Error('progress --port must be an integer from 0 to 65535');
 root=path.resolve(root);const identity=progressIdentity(root,version);
 const source=createSource(root);source.refresh({immediate:true});
 if(source.state.errors.lock)throw Error('Upgrade lock exists; recover the Kit upgrade before opening progress.');
 if(source.state.errors.handoff==='missing')throw Error('No dev/SESSION_HANDOFF.md found. Select an installed Kit project with --root.');
 // Spread deterministic choices across ranges: Windows can reserve adjacent port blocks.
 const ports=port?[port]:Array.from({length:12},(_,i)=>42000+((parseInt(identity.rootId.slice(0,8),16)+i*997)%18000));
 const same=other=>other&&Object.keys(identity).every(key=>other[key]===identity[key]);
 for(const candidate of ports){const existing=await probeProgress(candidate);if(same(existing)&&same(await probeProgress(candidate,{reopen:true}))){const url=`http://127.0.0.1:${candidate}`;if(openBrowser)openProgressBrowser(url);return{url,reused:true};}}
 for(const candidate of ports){let error=null,ended=false;const child=spawn(process.execPath,[cli,'--serve','--root',root,'--port',String(candidate),'--version',version,'--no-open'],{detached:true,windowsHide:true,stdio:'ignore'});
  child.once('error',e=>{error=e;ended=true;});child.once('exit',()=>{ended=true;});
  const deadline=Date.now()+6000;
  while(Date.now()<deadline&&!ended){if(same(await probeProgress(candidate))){child.unref();const url=`http://127.0.0.1:${candidate}`;if(openBrowser)openProgressBrowser(url);return{url,reused:false,pid:child.pid};}await sleep(80);}
  if(!ended)child.kill();if(error)throw Error('Could not start the local progress process.');
  // Another invocation may have won the same port while our child exited.
  if(same(await probeProgress(candidate))&&same(await probeProgress(candidate,{reopen:true}))){const url=`http://127.0.0.1:${candidate}`;if(openBrowser)openProgressBrowser(url);return{url,reused:true};}
 }
 throw Error('Could not open project progress. Check the project files and available loopback ports.');
}
