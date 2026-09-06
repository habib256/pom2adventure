import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
for(const lang of ['FR','EN'])for(const restoring of [false,true]){
 for(const [page,proof,no,yes] of [[129,69,181,268],[210,125,143,243],[342,366,300,197],[343,214,301,199],[331,392,112,202],[330,55,268,129]])for(const seen of [false,true]){
  const app=new Engine(proj,{}).app;app.restoring=restoring;if(seen)R.sceneMarkVisited(app.mem,proof);
  const body=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N${String(Math.floor(page/50)*50).padStart(3,'0')}/N${page}.TXT`,import.meta.url),'utf8');
  parseScene(app,body);assert.equal(app.revisit,seen?yes:no);
 }
}
console.log('PASS automatic history routing: six routers x two histories x FR/EN x entry/restore');

for(const lang of ['FR','EN'])for(const restoring of [false,true]){
 const body=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N050/N092.TXT`,import.meta.url),'utf8');
 for(const [visited,target] of [[[], -1],[[92],-1],[[92,247],247],[[247,20],108],[[247,232],108],[[247,389],108],[[108],108]]){
  const app=new Engine(proj,{}).app;app.restoring=restoring;
  for(const page of visited)R.sceneMarkVisited(app.mem,page);
  parseScene(app,body);assert.equal(app.revisit,restoring ? -1 : target,`${lang} restore=${restoring} history=${visited}`);
 }
}
console.log('PASS berry history: left available, eaten/picked depleted, ordered VR, FR/EN entry/restore');

for(const lang of ['FR','EN'])for(const restoring of [false,true]){
 const body=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N000/N031.TXT`,import.meta.url),'utf8');
 for(const [visited,target] of [[[], -1],[[31],-1],[[31,394],394],[[394,77],364],[[364],364]]){
  const app=new Engine(proj,{}).app;app.restoring=restoring;
  for(const page of visited)R.sceneMarkVisited(app.mem,page);
  parseScene(app,body);assert.equal(app.revisit,restoring ? -1 : target);
 }
}
console.log('PASS pool history: observation differs from drinking, priority and restore in FR/EN');

for(const lang of ['FR','EN'])for(const restoring of [false,true]){
 const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N350/N382.TXT`,import.meta.url),'utf8');
 for(const grown of [false,true]){
  const app=new Engine(proj,{}).app;app.restoring=restoring;
  if(grown)R.sceneMarkVisited(app.mem,421);
  parseScene(app,text);assert.equal(app.revisit,grown && !restoring ? 270 : -1);
 }
}
console.log('PASS permanent Growth path: explicit page 421, FR/EN entry and restoration');
