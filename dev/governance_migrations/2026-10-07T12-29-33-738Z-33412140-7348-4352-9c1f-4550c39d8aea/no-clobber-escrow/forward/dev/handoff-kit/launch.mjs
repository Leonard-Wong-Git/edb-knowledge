#!/usr/bin/env node
// The installed progress entry has no npm, network acquisition or write step.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

try {
 const args=process.argv.slice(2),options={port:0,openBrowser:true};let serve=false,version;
 const seen=new Set();
 for(let i=0;i<args.length;i++){
  const arg=args[i];if(seen.has(arg))throw Error('Duplicate progress option');seen.add(arg);
  if(arg==='--no-open')options.openBrowser=false;
  else if(arg==='--serve')serve=true;
  else if(['--root','--port','--version'].includes(arg)){
   const value=args[++i];if(!value||value.startsWith('--'))throw Error('Missing progress option value');
   if(arg==='--root')options.root=path.resolve(value);
   if(arg==='--port'){if(!/^\d{1,5}$/.test(value)||Number(value)>65535)throw Error('Invalid progress port');options.port=Number(value);}
   if(arg==='--version'){if(!/^\d+\.\d+\.\d+$/.test(value))throw Error('Invalid progress version');version=value;}
  }else throw Error('Unknown progress option');
 }
 if(!options.root)throw Error('Select the project with --root');
 const root=options.root;
 if(path.relative(fs.realpathSync(root),root)!=='')throw Error('Linked project root is not supported');
 for(const rel of ['dev','dev/governance_migrations','dev/governance_migrations/.upgrade.lock']){
  const target=path.join(root,rel);let st;try{st=fs.lstatSync(target);}catch(e){if(e.code==='ENOENT')continue;throw e;}
  if(st.isSymbolicLink())throw Error('Linked project state is not supported');
  if(rel.endsWith('.upgrade.lock'))throw Error('Upgrade lock exists; finish upgrade recovery before opening progress');
  if(!st.isDirectory())throw Error('Invalid project state directory');
 }
 const directory=path.dirname(fileURLToPath(import.meta.url));
 if(path.relative(fs.realpathSync(directory),directory)!=='')throw Error('Linked progress program is not supported');
 for(const name of ['assets','open','server','projection','dashboard','project-version','launch']){
  const st=fs.lstatSync(path.join(directory,name+'.mjs'));if(st.isSymbolicLink()||!st.isFile())throw Error('Progress program is incomplete or linked');
 }
 const assets=await import('./assets.mjs');
 if(assets.installed&&path.relative(root,path.resolve(directory,'../..'))!=='')throw Error('Progress entry belongs to a different project');
 options.version=version??assets.runtimeVersion;
 if(serve){const {startProgress}=await import('./server.mjs');await startProgress(options);}
 else{const {openProgress}=await import('./open.mjs');const result=await openProgress(options);console.log(JSON.stringify(result));}
}catch(e){console.error('Progress could not open: '+e.message);process.exitCode=1;}
