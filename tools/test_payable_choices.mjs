import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene,choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
const read=p=>readFile(new URL('../'+p,import.meta.url),'utf8');
const proj=JSON.parse(await read('SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json'));
const objects=JSON.parse(await read('SCOSWAMP/JSON/OBJECTS.json')).objects;
R.setCatalogs({objets:objects.map(o=>({cle:o.id,cache:o.hidden})),pierres:proj.pierres,amulettes:proj.amulettes});
for(let objects=0;objects<65536;objects++) for(const amulets of [0,1]) for(const count of [0,1]) {
  const hero={objects,amulets,stones:Array(12).fill(count)};
  const copy=structuredClone(hero);R.loseItems(copy,1);
  assert.equal(R.hasPayableItem(hero),JSON.stringify(hero)!==JSON.stringify(copy));
}
for(const lang of ['FR','EN']) for(const restoring of [false,true]) {
  const app=new Engine(proj,{}).app;app.restoring=restoring;
  parseScene(app,await read(`SCOSWAMP/TEXT${lang}/N100/N128.TXT`));
  app.hero.objects=1;
  assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),[180]);
  app.hero.stones[0]=1;
  assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),[407]);
  assert.equal(app.hero.stones[0],1);
  app.hero.stones[0]=0;
  assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene),[180]);
}
console.log('PASS CB : 262144 inventaires concordent avec PO ; FR/EN, reprise et sac dynamique');
