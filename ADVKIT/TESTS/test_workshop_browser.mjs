import {writeFile,readFile,copyFile,unlink,access,rmdir,mkdir,readdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const base=new URL('../../',import.meta.url);
let ws;
const files=['SCOSWAMP.MORE/GENERATED/N998.png','SCOSWAMP/DHGR/N950/N998.RLE.BIN','SCOSWAMP.MORE/HGR-PREVIEW/N998.png','SCOSWAMP.MORE/CHATMAUVE-PREVIEW/N998.png','SCOSWAMP.MORE/IMAGE-RECIPES/N998.json'];
for(const lang of ['FR','EN'])files.push(`SCOSWAMP/TEXT${lang}/N950/N998.TXT`);
for(const file of files){await assert.rejects(access(new URL(file,base)),{code:'ENOENT'});}
const reviewFile=new URL('SCOSWAMP.MORE/IMAGE-REVIEW.json',base);
const rejectDir=new URL('SCOSWAMP.MORE/GENERATED/.rejets/',base);
const previousBackups=(await readdir(rejectDir).catch(()=>[])).filter(n=>n.startsWith('N998.avant-'));
assert.deepEqual(previousBackups,[],'N998 backups must be reserved for this fixture');
const records=JSON.parse(await readFile(reviewFile,'utf8').catch(e=>{if(e.code!=='ENOENT')throw e;return '{}';}));
assert.equal(records.N998,undefined,'N998 review must be reserved for this fixture');
try {
await copyFile(new URL('SCOSWAMP.MORE/GENERATED/B120.png',base),new URL(files[0],base));
const original=await readFile(new URL(files[0],base));
for(const lang of ['FR','EN']){
  await mkdir(new URL(`SCOSWAMP/TEXT${lang}/N950/`,base),{recursive:true});
  await writeFile(new URL(`SCOSWAMP/TEXT${lang}/N950/N998.TXT`,base),`T 998 Review ${lang}\n\nA scene for review.\nC 001 Continue\n`);
}
const pages=await(await fetch('http://127.0.0.1:9228/json/list')).json();
ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();const errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(m.error):p.resolve(m.result);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params);if(m.method==='Page.javascriptDialogOpening')c('Page.handleJavaScriptDialog',{accept:true}).catch(()=>{});};
function c(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;const timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout: '+method));},20000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});}
async function ev(expression){const r=await c('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function until(expression){for(let i=0;i<200;i++){if(await ev(expression))return;await new Promise(r=>setTimeout(r,50));}throw Error('Timeout: '+expression);}
await c('Runtime.enable');await c('Page.enable');
// CDP headless navigation can hang on a beforeunload dialog. Suppress only
// that listener in the fixture; draft persistence is still exercised on reload.
await c('Page.addScriptToEvaluateOnNewDocument',{source:`const add=window.addEventListener;window.addEventListener=function(type,...args){if(type!=='beforeunload')return add.call(this,type,...args);};`});await c('Emulation.setDeviceMetricsOverride',{width:1280,height:800,deviceScaleFactor:1,mobile:false});
await c('Page.navigate',{url:'http://127.0.0.1:8765/ADVKIT/?image=N998'});
for(let i=0;i<120;i++){if(await ev('Boolean(document.querySelector("#status")?.textContent.startsWith("Aperçu prêt"))'))break;await new Promise(r=>setTimeout(r,500));}
assert.equal(await ev('document.querySelector("#dither").checked'),false);
assert.equal(await ev('document.querySelector("#asset-title").textContent'),'N998 / Scène');
async function click(selector){const rect=await ev(`(()=>{const r=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);await c('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...rect});await c('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...rect});}
assert.ok(await ev('document.querySelector("#apply").getBoundingClientRect().bottom <= innerHeight'),'save button visible');
await click('#crop-toggle');
await ev('document.querySelector("#zoom").value=2;document.querySelector("#zoom").dispatchEvent(new Event("input",{bubbles:true}))');
const crop=await ev('(()=>{const r=document.querySelector("#crop").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height}})()');
assert.ok(Math.abs(crop.w/crop.h-35/24)<.01,'crop ratio');
await c('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:crop.x,y:crop.y});
await c('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:crop.x+20,y:crop.y+10});
await c('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:crop.x+20,y:crop.y+10});
const t=Date.now();
await ev('document.querySelector("#brightness").value=1.23;document.querySelector("#brightness").dispatchEvent(new Event("input",{bubbles:true}))');
for(let i=0;i<400;i++){if(await ev('document.querySelector("#status").textContent.startsWith("Aperçu prêt")'))break;await new Promise(r=>setTimeout(r,50));}
console.log('slider → aperçu (ms)',Date.now()-t);
await click('#apply');
for(let i=0;i<400;i++){if(await ev('document.querySelector("#saved-state").textContent === "DHGR RLE enregistré"'))break;await new Promise(r=>setTimeout(r,50));}
assert.ok(await ev('document.querySelector("#status").textContent.includes("SCOSWAMP/DHGR/N950/N998.RLE.BIN enregistré")'));
const recipe=JSON.parse(await readFile(new URL(files[4],base),'utf8'));
assert.equal(recipe.brightness,1.23);assert.equal(recipe.dither,false);assert.ok(recipe.crop);
const final=await readFile(new URL(files[1],base));assert.equal(final.subarray(0,4).toString(),'DHRR');
assert.deepEqual(await readFile(new URL(files[0],base)),original);
console.log('saved',final.length,'bytes',createHash('sha256').update(final).digest('hex'));
await ev('document.querySelector("#asset-select").value="B026";document.querySelector("#asset-select").dispatchEvent(new Event("change",{bubbles:true}))');
await new Promise(r=>setTimeout(r,1000));
assert.equal(await ev('document.querySelector(".asset.selected").dataset.asset'),'B026');
await ev('document.querySelector("#asset-select").value="N998";document.querySelector("#asset-select").dispatchEvent(new Event("change",{bubbles:true}))');
await new Promise(r=>setTimeout(r,1000));
assert.equal(await ev('document.querySelector("#brightness").value'),'1.23');
await until('document.querySelector("#status").textContent.startsWith("Aperçu prêt") && !document.querySelector("#save-review").disabled');
assert.equal(await ev('new URL(document.querySelector("#scene-tree").href).searchParams.get("page")'),'998');
await ev('document.querySelector("#scene-language").value="EN";document.querySelector("#scene-language").dispatchEvent(new Event("change"))');
assert.match(await ev('document.querySelector("#scene-text").textContent'),/Review EN/);
assert.equal(await ev('new URL(document.querySelector("#scene-volume").href).searchParams.get("source")'),'volume');
await ev('document.querySelector("#layout").value="compare";document.querySelector("#layout").dispatchEvent(new Event("change"))');
assert.equal(await ev('document.querySelector("#before-image").toDataURL()===document.querySelector("#after-image").toDataURL()'),true);
await ev('document.querySelector(".review-card").open=true;document.querySelector("#review-selected").checked=true;document.querySelector("#review-notes").value="Mon choix de cadrage";document.querySelector("#review-decision").value="accepted";document.querySelector("#save-review").click()');
await until('document.querySelector("#status").textContent==="Votre avis est enregistré."');
assert.equal(JSON.parse(await readFile(reviewFile,'utf8')).N998.state,'accepted');
await ev('document.querySelector("#filter").value="selected";document.querySelector("#filter").dispatchEvent(new Event("change"))');
assert.equal(await ev('Boolean(document.querySelector(".asset[data-asset=N998]"))'),true);

// A new candidate is visible next to the saved file and cannot be validated yet.
await ev('document.querySelector("#brightness").value=.45;document.querySelector("#brightness").dispatchEvent(new Event("input",{bubbles:true}))');
await until('document.querySelector("#status").textContent.startsWith("Aperçu prêt")');
assert.equal(await ev('document.querySelector("#before-image").toDataURL()===document.querySelector("#after-image").toDataURL()'),false);
await ev('document.querySelector("#save-review").click()');
await until('document.querySelector("#status").textContent.startsWith("Enregistrez la proposition")');
assert.equal(JSON.parse(await readFile(reviewFile,'utf8')).N998.state,'accepted','draft must not overwrite the saved decision');
// Reload without a native leave-page dialog;
// the draft must be recovered from localStorage, not the prior JS instance.
await c('Page.navigate',{url:'about:blank'});
await c('Page.navigate',{url:'http://127.0.0.1:8765/ADVKIT/?image=N998'});
await until('document.querySelector("#status")?.textContent.startsWith("Aperçu prêt") && !document.querySelector("#save-review").disabled');
assert.equal(await ev('document.querySelector("#brightness").value'),'0.45');
assert.equal(await ev('document.querySelector("#review-notes").value'),'Mon choix de cadrage');

// Simulate a completed regeneration without invoking any paid generator.
await mkdir(rejectDir,{recursive:true});
await copyFile(new URL(files[0],base),new URL('N998.avant-20000101-000000.png',rejectDir));
await copyFile(new URL('SCOSWAMP.MORE/GENERATED/B026.png',base),new URL(files[0],base));
await c('Page.navigate',{url:'about:blank'});
await c('Page.navigate',{url:'http://127.0.0.1:8765/ADVKIT/?image=N998'});
await until('document.querySelector("#status")?.textContent.startsWith("Aperçu prêt") && !document.querySelector("#save-review").disabled');
assert.equal(await ev('document.querySelector("#review-state").textContent'),'Modifiée depuis votre avis');
assert.equal(await ev('document.querySelector("#brightness").value'),'1.23','draft from previous master must be discarded');
await ev('document.querySelector("#previous-master-box").open=true;document.querySelector("#restore-master").click()');
await until('!document.querySelector("#restore-master").disabled && document.querySelector("#brightness").value==="1"');
assert.deepEqual(await readFile(new URL(files[0],base)),original,'restore keeps the original master available');
assert.deepEqual(await readFile(new URL(files[1],base)),final,'master selection must not overwrite saved output');
assert.deepEqual(errors,[]);
const shot=await c('Page.captureScreenshot',{format:'png'});await writeFile('/tmp/scoswamp-studio-tested.png',Buffer.from(shot.data,'base64'));
console.log('PASS crop, saved/candidate comparison, scene links, decisions, persistent drafts, changed-master invalidation and restoration');
ws.close();
} finally {
  ws?.close();
  for(const file of files){await unlink(new URL(file,base)).catch(e=>{if(e.code!=='ENOENT')throw e;});}
  for(const dir of ['SCOSWAMP/DHGR/N950','SCOSWAMP/TEXTFR/N950','SCOSWAMP/TEXTEN/N950'])await rmdir(new URL(dir,base)).catch(e=>{if(!['ENOENT','ENOTEMPTY'].includes(e.code))throw e;});
  for(const name of (await readdir(rejectDir).catch(()=>[])).filter(n=>n.startsWith('N998.avant-')))await unlink(new URL(name,rejectDir));
  try{const records=JSON.parse(await readFile(reviewFile,'utf8'));delete records.N998;
    if(Object.keys(records).length)await writeFile(reviewFile,JSON.stringify(records,null,2)+'\n');else await unlink(reviewFile);
  }catch(e){if(e.code!=='ENOENT')throw e;}
}
