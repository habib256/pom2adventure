import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
const read = p => readFile(new URL('../'+p, import.meta.url), 'utf8');
const config=JSON.parse(await read('SCOSWAMP/JSON/RULES.json'));
const catalogue=JSON.parse(await read('SCOSWAMP/JSON/OBJECTS.json')).objects;
R.setCatalogs({objets: catalogue.map(o=>({cle:o.id,cache:o.hidden})),pierres:[],amulettes:[]});
const bit=k=>1<<R.objectFromName(k), accepted=config.trade.objects.map(bit);
const pop=n=>n.toString(2).replaceAll('0','').length;
for(let mask=0;mask<16;mask++) for(let amulets=0;amulets<64;amulets++) {
  const objects=bit('ANNEAU')|bit('CAPE')|accepted.reduce((n,b,i)=>n|(mask&(1<<i)?b:0),0);
  const hero={objects,amulets};
  const result=R.tradeInventory(hero,config.trade);
  assert.equal(result.count,Math.min(3,pop(mask)+pop(amulets)));
  assert.equal(pop(objects)+pop(amulets)-pop(hero.objects)-pop(hero.amulets),result.count);
  assert.equal(hero.objects&(bit('ANNEAU')|bit('CAPE')),bit('ANNEAU')|bit('CAPE'));
  const consumed=accepted.filter((_,i)=>mask&(1<<i)).slice(0,3);
  assert.equal(hero.objects,objects^consumed.reduce((n,b)=>n|b,0));
}
const proj=JSON.parse(await read('SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json'));
proj.rules=config;
for(const lang of ['FR','EN']) for(const restoring of [false,true]) {
  const app=new Engine(proj,{}).app;
  app.hero.objects=bit('CH')|bit('ANNEAU');app.hero.amulets=1;app.restoring=restoring;
  parseScene(app,await read(`SCOSWAMP/TEXT${lang}/N400/N408.TXT`));
  assert.equal(app.chooseN,restoring?0:2);
  assert.equal(app.hero.objects,restoring?bit('CH')|bit('ANNEAU'):bit('ANNEAU'));
  assert.equal(app.hero.amulets,restoring?1:0);
}
R.setCatalogs({objets:['MAP','TOOL','FUEL'].map(cle=>({cle})),pierres:[],amulettes:[]});
const other={objects:7,amulets:3};
assert.deepEqual(R.tradeInventory(other,{objects:['FUEL','MAP'],amulets:false,limit:1,categories:'NM'}),{count:1,categories:'NM'});
assert.deepEqual(other,{objects:6,amulets:3});
for(const invalid of [{objects:['MISSING']},{objects:['map']},{limit:-1},{categories:'NN'},{amulets:1}]) {
  const hero={objects:7,amulets:3};
  assert.throws(()=>R.tradeInventory(hero,{objects:['MAP'],amulets:true,limit:3,categories:'N',...invalid}));
  assert.deepEqual(hero,{objects:7,amulets:3});
}
const unchanged={objects:7,amulets:3};
assert.deepEqual(R.tradeInventory(unchanged),{count:0,categories:'N'});
assert.throws(()=>R.tradeInventory(unchanged,null));
assert.deepEqual(unchanged,{objects:7,amulets:3});
console.log('PASS trade: 1024 inventories, accepted goods, cap, bilingual restore, other-game policy and invalid configuration');
