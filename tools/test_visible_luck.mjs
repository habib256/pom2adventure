import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
const objects=JSON.parse(await readFile(new URL('../SCOSWAMP/JSON/OBJECTS.json',import.meta.url))).objects;
R.setCatalogs({objets:objects.map(o=>({cle:o.id,cache:o.hidden})),pierres:proj.pierres,amulettes:proj.amulettes});
for(const lang of ['FR','EN'])for(const [page,field,loss] of [[24,'end',2],[58,'end',1],[73,'end',2],[190,'end',2],[249,'hab',1]])for(const chance of [0,12]){
 let keys=0;const engine=new Engine(proj,{render(){},async key(){keys++;return ' ';}}),app=engine.app;
 Object.assign(app.hero,{cha:chance,cha0:chance,end:24,end0:24,hab:12,hab0:12});
 const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N${String(Math.floor(page/50)*50).padStart(3,'0')}/N${String(page).padStart(3,'0')}.TXT`,import.meta.url),'utf8');
 R.diceSeed(1234);const rng=R.diceStateGet();parseScene(app,text);
 assert.equal(R.diceStateGet(),rng);assert.equal(app.hero.cha,chance);assert.equal(app.diceN,3);
 await engine.runDiceRoll();assert.equal(keys,2);assert.equal(app.hero.cha,Math.max(0,chance-1));assert.equal(app.hero[field],(field==='end'?24:12)-(chance?0:loss));
 const before=structuredClone(app.hero);app.restoring=true;app.diceN=0;parseScene(app,text);assert.equal(app.diceN,0);assert.deepEqual(app.hero,before);
}
for(const n of [3,4,127]){const engine=new Engine(proj,{render(){},async key(){return ' ';}});Object.assign(engine.app.hero,{end:1,end0:255,cha:9});parseScene(engine.app,`ED ENDURANCE ${n}`);assert.equal(engine.app.diceN,2);await engine.runDiceRoll();assert.equal(engine.app.hero.cha,9);}
console.log('PASS visible CE: five pages FR/EN, lucky/unlucky, two prompts, no early RNG/cost, restore; ED 3+ remains two dice');
