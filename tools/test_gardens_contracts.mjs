import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
R.setCatalogs({objets:[],pierres:proj.pierres,amulettes:proj.amulettes});
for(const lang of ['FR','EN'])for(const restoring of [false,true])for(const page of [283,396,117,292,264,379,251]){
 const app=new Engine(proj,{}).app;app.restoring=restoring;
 Object.assign(app.hero,{hab:12,hab0:12,end:24,end0:24,cha:10,cha0:10});
 const path=`../SCOSWAMP/TEXT${lang}/N${String(Math.floor(page/50)*50).padStart(3,'0')}/N${page}.TXT`;
 parseScene(app,await readFile(new URL(path,import.meta.url),'utf8'));
 if([283,396].includes(page)){assert.equal(app.chooseN,restoring?0:1);if(!restoring)assert.equal(app.chooseCats,'B');}
 if([117,292].includes(page)){assert.equal(app.hero.amulets,0);assert.equal(app.choices[0].scene,363);}
 if(page===264)assert.equal(app.hero.end,restoring?24:22);
 if(page===379){assert.equal(app.hero.hab,restoring?12:9);assert.equal(app.foes.length,1);assert.equal(app.foes[0].hab,7);assert.equal(app.foes[0].end,10);assert.equal(app.winScene,251);assert.equal(app.fleeTarget,363);}
 if(page===251){assert.equal(app.hero.cha,restoring?10:7);assert.equal(app.hero.amulets,restoring?0:1<<R.amuletFromName('FLEUR'));}
}
console.log('PASS Gardens FR/EN entry/restore: reward, temporary amulet, burn, combat skill loss and victory loot');
