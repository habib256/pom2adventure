import {writeFile,readFile,copyFile,unlink,access,rmdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const base=new URL('../',import.meta.url);
const files=['SCOSWAMP.MORE/GENERATED/N998.png','SCOSWAMP/DHGR/N950/N998.RLE.BIN','SCOSWAMP.MORE/HGR-PREVIEW/N998.png','SCOSWAMP.MORE/CHATMAUVE-PREVIEW/N998.png','SCOSWAMP.MORE/IMAGE-RECIPES/N998.json'];
for(const file of files){await assert.rejects(access(new URL(file,base)),{code:'ENOENT'});}
await copyFile(new URL('SCOSWAMP.MORE/GENERATED/B120.png',base),new URL(files[0],base));
const original=await readFile(new URL(files[0],base));
try {
const pages=await(await fetch('http://127.0.0.1:9228/json/list')).json();
const ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();const errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params);};
function c(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function ev(expression){const r=await c('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
await c('Runtime.enable');await c('Page.enable');await c('Emulation.setDeviceMetricsOverride',{width:1280,height:800,deviceScaleFactor:1,mobile:false});
await c('Page.navigate',{url:'http://127.0.0.1:8765/SCOSWAMP.MORE/TOOLS/interpreter/?image=N998'});
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
assert.deepEqual(errors,[]);
const shot=await c('Page.captureScreenshot',{format:'png'});await writeFile('/tmp/scoswamp-studio-tested.png',Buffer.from(shot.data,'base64'));
console.log('PASS crop drag, ratio, default dither, slider, visible save, native file, preserved master, selection round trip');
ws.close();
} finally {for(const file of files){await unlink(new URL(file,base)).catch(e=>{if(e.code!=='ENOENT')throw e;});}await rmdir(new URL('SCOSWAMP/DHGR/N950',base)).catch(e=>{if(!['ENOENT','ENOTEMPTY'].includes(e.code))throw e;});}
