import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene,choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
R.setCatalogs({objets:[],pierres:proj.pierres,amulettes:proj.amulettes});
for(const lang of ['FR','EN']) {
 const read=async(group,page)=>readFile(new URL(`../SCOSWAMP/TEXT${lang}/${group}/N${page}.TXT`,import.meta.url),'utf8');
 const choice=new Engine(proj,{}).app;
 parseScene(choice,await read('N050','074'));
 assert.equal(choiceAvailable(choice,choice.choices[0]),false);
 choice.hero.stones[R.stoneFromName('MALEDICTION')]=1;
 assert.equal(choiceAvailable(choice,choice.choices[0]),true);
 assert.equal(choice.choices[0].scene,261);
 for(const restoring of [false,true]) {
  const fire=new Engine(proj,{}).app;fire.restoring=restoring;
  fire.hero.end=24;fire.hero.end0=24;
  parseScene(fire,await read('N100','113'));
  assert.equal(fire.hero.end,restoring?24:21);assert.equal(fire.hero.amulets,0);
  assert.equal(fire.foes.length,0);assert.equal(fire.choices[0].scene,165);
  const trap=new Engine(proj,{}).app;trap.restoring=restoring;
  parseScene(trap,await read('N350','361'));
  assert.equal(trap.choices.length,0);assert.equal(trap.foes.length,0);

  const app=new Engine(proj,{}).app;app.restoring=restoring;
  parseScene(app,await read('N250','261'));
  assert.equal(app.diceN,restoring?0:-1);
  assert.equal(app.foes.length,1);
  assert.equal(app.foes[0].hab,8);assert.equal(app.foes[0].end,9);
  assert.equal(app.fleeTarget,-1);assert.equal(app.winScene,354);
  const loot=new Engine(proj,{}).app;loot.restoring=restoring;
  parseScene(loot,await read('N350','354'));
  assert.equal(loot.hero.amulets,restoring?0:1<<R.amuletFromName('ARAIGNEE'));
 }
}
console.log('PASS spider curse FR/EN: required stone, one die on entry only, monster, no escape, victory and one-time amulet');

console.log("PASS Fire and Friendship FR/EN: burns once, no loot or combat, escape from blaze, terminal trap");
