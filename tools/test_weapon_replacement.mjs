import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
const objects=JSON.parse(await readFile(new URL('../SCOSWAMP/JSON/OBJECTS.json',import.meta.url))).objects;
R.setCatalogs({objets:objects.map(o=>({cle:o.id,cache:o.hidden})),pierres:proj.pierres,amulettes:proj.amulettes});
for(const lang of ['FR','EN'])for(const [page,bonus] of [[241,1],[140,2],[340,2]])for(const old of [0,1,2])for(const owned of [false,true]){
 const app=new Engine(proj,{}).app;app.hero.weaponBonus=old;
 if(owned)R.giveObject(app.hero,R.objectFromName('EP'));
 const text=await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N${String(Math.floor(page/50)*50).padStart(3,'0')}/N${page}.TXT`,import.meta.url),'utf8');
 parseScene(app,text);assert.equal(app.hero.weaponBonus,bonus);assert.ok(R.hasObject(app.hero,R.objectFromName('EP')));
 const before=structuredClone(app.hero);app.restoring=true;parseScene(app,text);assert.deepEqual(app.hero,before);
}
for(const token of ['ANNEAU','CH','LOUP','INEXISTANT']){
 const app=new Engine(proj,{}).app;app.hero.weaponBonus=2;
 parseScene(app,`G ${token}`);assert.equal(app.hero.weaponBonus,2);
}
console.log('PASS 36 weapon acquisitions FR/EN: stale bonus, existing weapon, restore; other grants unchanged');
