import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene,choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
for(const restoring of [false,true]) {
  const app=new Engine(proj,{}).app;app.restoring=restoring;
  parseScene(app,'CG 0 1 free\nCG 1 2 coin\nCG 3 3 three\nCG 255 4 maximum');
  for(const gold of [0,1,2,3,254,255,256,65535,0]) {
    app.hero.gold=gold;
    assert.deepEqual(app.choices.map(c=>choiceAvailable(app,c)),[true,gold>=1,gold>=3,gold>=255]);
    assert.equal(app.hero.gold,gold,'checking affordability must not debit');
  }
}
for(const lang of ['FR','EN']) {
  for(const gold of [0,1,2]) {
    const app=new Engine(proj,{}).app;app.hero.gold=gold;
    const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N250/N280.TXT`,import.meta.url),'utf8');
    parseScene(app,text);
    assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),gold?[395,78,289,343]:[343]);
    app.hero.gold=0;
    assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),[343]);
  }
  const app=new Engine(proj,{}).app;
  app.hero.gold=1;app.hero.end=10;app.hero.end0=20;
  parseScene(app,await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N350/N395.TXT`,import.meta.url),'utf8'));
  assert.equal(app.hero.gold,0);
  assert.equal(app.hero.end,9);
  assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),[116,236]);
}
console.log('PASS CG: thresholds, live gold changes, no implicit payment, restore and FR/EN inn access');
