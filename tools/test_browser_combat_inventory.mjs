import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import {Engine,ISSUE} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
R.setCatalogs({objets:[],pierres:proj.pierres,amulettes:[]});
function fixture(steps){
 const engine=new Engine(proj,{render(){},async key(){assert.ok(steps.length,'unexpected extra key prompt');const step=steps.shift();return typeof step==='function'?step(engine.app):step;}});
 Object.assign(engine.app.hero,{hab:1,hab0:12,end:20,end0:24,cha:6,cha0:6});
 engine.app.foes=[{name:'TEST',hab:100,end:20,end0:20,damage:2,stopAt:0}];
 engine.app.heroReady=true;engine.app.currentScene=200;R.diceSeed(1234);
 return engine;
}
// Open after a rolled but unresolved assault. Forbidden healing is not spent,
// and neither opening nor closing the menu alters the pending roll or RNG.
let saved;
const steps=[' ',app=>{saved={jet:structuredClone(app.combat.jet),hero:structuredClone(app.hero),rng:R.diceStateGet()};return 'I';},
 app=>{assert.equal(app.modal.type,'sac');assert.equal(app.modal.inCombat,true);return 'A';},
 app=>{assert.equal(app.modal.note,'M_LE_PREMIER_COUP');assert.deepEqual(app.hero,saved.hero);return ' ';},
 '\x1b',app=>{assert.deepEqual(app.combat.jet,saved.jet);assert.equal(R.diceStateGet(),saved.rng);assert.deepEqual(app.hero,saved.hero);return ' ';},
 app=>{assert.equal(app.hero.end,18);assert.equal(app.lastLoss,2);return '\x00';}];
const combat=fixture(steps);combat.app.hero.stones[1]=1;
assert.equal(await combat.runCombat(),ISSUE.DEJA_GAGNE);assert.equal(steps.length,0);assert.equal(combat.app.modal,null);assert.equal(combat.app.combat,null);
// A fatal curse while an assault is pending returns death immediately, before
// any pending combat damage, next roll, or another stone selection.
const fatalSteps=[' ','I',app=>{assert.equal(app.modal.inCombat,true);return 'A';},app=>{assert.equal(app.hero.end,0);return ' ';}];
const fatal=fixture(fatalSteps);fatal.app.hero.end=1;fatal.app.hero.stones[11]=1;
assert.equal(await fatal.runCombat(),ISSUE.MORT);assert.equal(fatalSteps.length,0);assert.equal(fatal.app.lastLoss,0);assert.equal(fatal.app.modal,null);assert.equal(fatal.app.combat,null);
// Outside combat, death opens its own screen and the unused healing stone
// remains in the bag: it cannot resurrect the hero after the curse.
const outsideSteps=['B',' ',app=>{assert.equal(app.modal.type,'mort');return '\x00';}];
const outside=fixture(outsideSteps);outside.app.hero.end=1;outside.app.hero.stones[1]=1;outside.app.hero.stones[11]=1;
await outside.handleKey('I');assert.equal(outsideSteps.length,0);assert.equal(outside.app.hero.end,0);assert.equal(outside.app.hero.stones[1],1);
R.adjustEnd(outside.app.hero,24);assert.equal(outside.app.hero.end,0);
// Cleanup remains reliable even when a view fails during a menu transition.
const broken=fixture([]);broken.ui.key=async()=>{throw Error('view interrupted');};
await assert.rejects(broken.showInventory(false),/view interrupted/);assert.equal(broken.app.modal,null);
console.log('PASS combat inventory: pending roll/RNG, forbidden stone, resolved wounds, fatal curse inside/outside combat, no resurrection, modal cleanup');
// SPACETRIP has no character sheet: zero initial END is not a dead hero.
const spaceSteps=[app=>{assert.equal(app.modal.type,'sac');return 'I';}];
const space=fixture(spaceSteps);space.app.heroReady=false;space.app.hero.end=0;
assert.equal(await space.showInventory(false),false);assert.equal(spaceSteps.length,0);
console.log('PASS inventory without character sheet (SPACETRIP)');

// Encounter-level prohibition also applies before the first assault.
for (const inCombat of [2]) for (let stone=0;stone<12;stone++) {
 const hero=R.characterInit ? R.characterInit() : structuredClone(combat.app.hero);
 hero.stones.fill(1);const before=structuredClone(hero);
 assert.equal(R.stoneUse(hero,stone,inCombat),R.STONE_USE_FORBIDDEN);
 assert.deepEqual(hero,before);
}
const banned=fixture(['I','A',app=>{assert.equal(app.modal.note,'M_PIERRE_ABSENTE');return ' ';},'I','\x00']);
banned.app.magicForbidden=true;banned.app.hero.stones[3]=1;
assert.equal(await banned.runCombat(),ISSUE.DEJA_GAGNE);
assert.equal(banned.app.hero.stones[3],1);
console.log('PASS encounter magic prohibition before first assault, all 12 stones');

for (const lang of ['FR','EN']) for (const page of [215,355]) for (const restoring of [false,true]) {
 const app=new Engine(proj,{}).app;app.restoring=restoring;
 const group=page===215?'N200':'N350';
 parseScene(app,await readFile(new URL(`../SCOSWAMP/TEXT${lang}/${group}/N${page}.TXT`,import.meta.url),'utf8'));
 assert.equal(app.magicForbidden,true);
 assert.equal(app.fleeTarget,-1);
 assert.equal(app.foes.length,page===215?1:2);
 parseScene(app,'MM 0');assert.equal(app.magicForbidden,false);
}
console.log('PASS MM: both encounters, both languages, initial entry and restore, explicit reset');
