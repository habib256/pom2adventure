import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene, choiceAvailable} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import {stoneFromName, setCatalogs} from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj = JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json', import.meta.url)));
const objects = JSON.parse(await readFile(new URL('../SCOSWAMP/JSON/OBJECTS.json', import.meta.url))).objects;
setCatalogs({objets: objects.map(o=>({cle:o.id, cache:o.hidden})), pierres:proj.pierres, amulettes:proj.amulettes});
const cases = [
  [399, [309,281], [[346,'TERREUR'],[169,'ILLUSION']]],
  [34, [209], [[237,'FLETRISSURE'],[291,'FEU'],[356,'TERREUR']]],
  [374, [11], [[299,'TERREUR'],[60,'ILLUSION'],[160,'AMITIE']]],
  [324, [88,42], [[383,'BENEDICTION']]],
  [258, [212], [[198,'TERREUR'],[127,'AMITIE']]],
  [256, [57], [[274,'MALEDICTION'],[365,'TERREUR'],[385,'FEU'],[351,'ILLUSION']]],
];
let checks = 0;
for (const lang of ['FR','EN']) for (const [page, free, spells] of cases) {
  const dir=String(Math.floor(page/50)*50).padStart(3,'0');
  const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N${dir}/N${String(page).padStart(3,'0')}.TXT`,import.meta.url),'utf8');
  for (const restoring of [false,true]) {
    const app=new Engine(proj,{}).app;app.restoring=restoring;
    parseScene(app,text);
    for (const [destination,stone] of spells) {
      assert.equal(app.choices.find(c=>c.scene===destination)?.require,stoneFromName(stone));
    }
    for(let mask=0;mask<(1<<spells.length);mask++) {
      app.hero.stones.fill(0);
      spells.forEach(([,stone],i)=>app.hero.stones[stoneFromName(stone)]=(mask>>i)&1);
      const before=[...app.hero.stones];
      const expected=[...free,...spells.filter((_,i)=>mask&(1<<i)).map(([dest])=>dest)].sort((a,b)=>a-b);
      assert.deepEqual(app.choices.filter(c=>choiceAvailable(app,c)).map(c=>c.scene).sort((a,b)=>a-b),expected);
      assert.deepEqual(app.hero.stones,before,'afficher les choix ne doit pas consommer');
      checks++;
    }
  }
}
for (const lang of ['FR','EN']) {
  const app=new Engine(proj,{}).app;
  parseScene(app, await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N300/N346.TXT`,import.meta.url),'utf8'));
  assert.deepEqual(app.foes.map(f=>[f.hab,f.end]),[[6,7],[7,7]]);
  assert.deepEqual(app.foeImg.slice(0,2),[281,281]);
  assert.equal(app.choices.length,0,'la variante engage directement les deux survivants');
}
console.log(`PASS sorts : ${checks} inventaires FR/EN, entree/reprise, conditions dynamiques et deux Orques`);
