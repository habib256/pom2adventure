import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene,choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
function appWith(pages){const app=new Engine(proj,{}).app;for(const p of pages)R.sceneMarkVisited(app.mem,p);return app;}
for(let mask=0;mask<16;mask++){
 const pages=[1,2,3,4].filter((_,i)=>mask&(1<<i));
 for(const restoring of [false,true]){
  const app=appWith(pages);app.restoring=restoring;
  parseScene(app,'CV 1,!2,3,!4 100 yes\nCX 1,!2,3,!4 101 no\nCV 2 102 oldyes\nCX 2 103 oldno');
  const expected=mask===5;
  assert.deepEqual(app.choices.map(c=>choiceAvailable(app,c)),[expected,!expected,!!(mask&2),!(mask&2)]);
  assert.deepEqual(app.choices.map(c=>c.scene),[100,101,102,103]);
 }
}
for(const lang of ['FR','EN']){
 const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N350/N363.TXT`,import.meta.url),'utf8');
 for(const [pages,target] of [[[],133],[[115],133],[[166],133],[[185],133],[[333],133],[[378],306],[[378,219],234],[[219],234]]){
  const app=appWith(pages);parseScene(app,text);
  assert.equal(app.revisit,target);
 }
}
console.log('PASS CV/CX: complete 4-condition truth table, inversion, legacy syntax, restore and bilingual Patroller outcomes');

for (const lang of ['FR','EN']) {
 const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N100/N144.TXT`,import.meta.url),'utf8');
 for(let mask=0;mask<32;mask++) for(const restoring of [false,true]) {
  const pages=[144,165,345,113,354].filter((_,i)=>mask&(1<<i));
  const app=appWith(pages);app.currentScene=144;app.restoring=restoring;
  parseScene(app,text);
  assert.equal(app.revisit,!restoring&&(mask&24)?345:-1);
 }
}
for (const pages of [[],[144],[345],[354]]) {
 const app=appWith(pages);app.currentScene=144;parseScene(app,'V 345 354');
 assert.equal(app.revisit,pages.length?345:-1,'legacy V remains unchanged');
}
console.log('PASS VR: 32 histories, FR/EN and restore; legacy V behavior preserved');
