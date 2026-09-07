import assert from 'node:assert/strict';
import {Engine,ISSUE} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import {parseScene} from '../SCOSWAMP.MORE/TOOLS/interpreter/scene.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';
import {readFile} from 'node:fs/promises';
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url)));
function fixture(steps,minimum=2,hab=1,foeHab=100){
 const e=new Engine(proj,{render(){},async key(){assert.ok(steps.length,'unexpected prompt');const k=steps.shift();return typeof k==='function'?k(e.app):k;}});
 Object.assign(e.app.hero,{hab,hab0:hab,end:20,end0:20,cha:6,cha0:6});e.app.heroReady=true;
 e.app.foes=[{name:'FOE',hab:foeHab,end:20,end0:20,damage:2,stopAt:0}];
 parseScene(e.app,`MF ${minimum}\nCF 348 Exit`);R.diceSeed(1234);return e;
}
let rng;
const steps=[a=>{assert.equal(a.combat.fuite,false);rng=R.diceStateGet();return 'F';},
 a=>{assert.equal(a.hero.end,20);assert.equal(R.diceStateGet(),rng);return ' ';},
 a=>{assert.equal(a.combat.assaut,1);assert.equal(a.combat.fuite,false);return 'F';},
 a=>{assert.equal(a.hero.end,20);return ' ';},
 a=>{assert.equal(a.hero.end,18);assert.equal(a.combat.fuite,false);return 'I';},
 a=>{assert.equal(a.modal.type,'sac');return 'I';},
 a=>{assert.equal(a.combat.fuite,false);return ' ';},
 a=>{assert.equal(a.hero.end,16);assert.equal(a.combat.fuite,true);return 'F';},' ',' '];
const e=fixture(steps);assert.equal(await e.runCombat(),ISSUE.FUITE);assert.equal(steps.length,0);assert.equal(e.app.hero.end,14);
// Zero keeps the existing immediate escape contract.
const direct=fixture(['F',' ',' '],0);assert.equal(await direct.runCombat(),ISSUE.FUITE);assert.equal(direct.app.hero.end,18);
// Two draws are two resolved assaults too, without a pending wound.
let seed;
for(let n=1;n<10000;n++){R.diceSeed(n);const c={hab:9,weaponBonus:0,objects:0},m={hab:9};if(R.combatRound(c,m).outcome===R.ROUND_DODGE&&R.combatRound(c,m).outcome===R.ROUND_DODGE){seed=n;break;}}
assert.ok(seed);
const dodgeSteps=[' ',a=>{assert.equal(a.combat.fuite,false);assert.equal(a.combat.pending,false);return ' ';},
 a=>{assert.equal(a.combat.fuite,true);assert.equal(a.hero.end,20);return 'F';},' ',' '];
const draw=fixture(dodgeSteps,2,9,9);R.diceSeed(seed);assert.equal(await draw.runCombat(),ISSUE.FUITE);assert.equal(dodgeSteps.length,0);
for(const lang of ['FR','EN']){
 const app=new Engine(proj,{}).app;app.restoring=true;
 parseScene(app,await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N200/N221.TXT`,import.meta.url),'utf8'));
 assert.equal(app.fleeAfter,2,'MF is structural and restored when reading the scene');
}
console.log('PASS MF: early key ignored, two resolved wounds, menu preserves delay, zero delay, draws count, bilingual restore');
