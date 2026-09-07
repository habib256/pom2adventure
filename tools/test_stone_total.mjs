import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene,choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
for(const restoring of [false,true]) {
  const app=new Engine(proj,{}).app; app.restoring=restoring;
  parseScene(app,'CT 0 0 316 empty\nCT 1 15 141 exchange\nCT 2 3 100 interval\nCT 15 15 101 saturated\nCA 0 0 102 noamulet');
  for(const total of [0,1,2,3,4,14,15,16,255,3060]) {
    app.hero.stones.fill(0);
    let left=total;
    for(let i=0;i<app.hero.stones.length;i++) {app.hero.stones[i]=Math.min(255,left);left-=app.hero.stones[i];}
    assert.deepEqual(app.choices.map(c=>choiceAvailable(app,c)),[total===0,total>0,total>=2&&total<=3,total>=15,true]);
  }
}
for(const lang of ['FR','EN']) {
  const app=new Engine(proj,{}).app;
  parseScene(app,await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N000/N008.TXT`,import.meta.url),'utf8'));
  for(const count of [0,1,0]) {
    app.hero.stones.fill(0);app.hero.stones[0]=count;
    assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),count?[141,341]:[316,341]);
  }
}
console.log('PASS CT: bounds, saturation, live bag changes, restore, CA compatibility and FR/EN exchange');
