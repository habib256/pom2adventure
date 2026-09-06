import assert from 'node:assert/strict';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';

// Independent game vocabulary and bit positions, with two unrelated groups.
R.setCatalogs({objets: ['TOOL', '.CREW', '.PILOT', '.SEEN'].map(cle => ({cle, cache: cle[0] === '.'})),
  pierres: [], amulettes: []});
const rules = {schema: 1, save_migrations: [
  {when_none: ['.CREW', '.PILOT'], first_visited: [{page: 8, give: '.PILOT'}, {page: 2, give: '.CREW'}]},
  {when_none: ['.SEEN'], first_visited: [{page: 2, give: '.SEEN'}]},
]};
const mem = R.newMemory();
mem.visited[0] = 1 << 2;
mem.visited[1] = 1;
const hero = {objects: 1};
R.migrateSavedFlags(hero, mem, rules);
assert.equal(hero.objects, 1 | 4 | 8, 'first visited branch wins, independent groups both apply');
R.migrateSavedFlags(hero, mem, rules);
assert.equal(hero.objects, 13, 'migration is idempotent');
const explicit = {objects: 3};
R.migrateSavedFlags(explicit, mem, rules);
assert.equal(explicit.objects, 11, 'existing choice takes priority over history');
assert.throws(() => R.migrateSavedFlags({objects: 1}, mem, {save_migrations: [
  {when_none: ['UNKNOWN'], first_visited: [{page: 2, give: 'UNKNOWN'}]},
]}), /inconnu/);
assert.throws(() => R.migrateSavedFlags({objects: 1}, mem, {save_migrations: [
  {when_none: ['.SEEN'], first_visited: [{page: 2, give: 'TOOL'}]},
]}), /invalide/);
console.log('game migrations: priority, independence, idempotence and reference checks passed');

// An encounter stopped with a living foe can resume with a lower threshold.
// A killed foe and an unrelated encounter must never be resurrected.
const encounters = R.newMemory();
const foe = stopAt => ({hab: 9, end: 12, end0: 12, damage: 4, stopAt});
R.monsterRemember(encounters, 7, 1, {end: 6});
assert.equal(R.monsterEnter(encounters, 7, [foe(6)], 1), 1);
const resumed = [foe(0)];
assert.equal(R.monsterEnter(encounters, 7, resumed, 1), 0);
assert.equal(resumed[0].end, 6);
assert.equal(R.monsterEnter(encounters, 8, [foe(0)], 1), 0);
const restored = JSON.parse(JSON.stringify(encounters));
const afterLoad = [foe(0)];
assert.equal(R.monsterEnter(restored, 7, afterLoad, 1), 0);
assert.equal(afterLoad[0].end, 6);
R.monsterRemember(encounters, 7, 1, {end: 0});
assert.equal(R.monsterEnter(encounters, 7, [foe(0)], 1), 1);
console.log('encounters: threshold, resume, persistence, location isolation and death checks passed');

const recovery = R.newMemory();
R.monsterRecover(recovery, 34, 1, 8);
assert.equal(recovery.seen[0].scene, 0, 'no new encounter');
R.monsterRemember(recovery, 34, 0, {end:3});
R.monsterRecover(recovery, 34, 1, 8);
assert.equal(recovery.seen[0].end,4);
R.monsterRecover(recovery, 34, 255, 8);
assert.equal(recovery.seen[0].end,8);
R.monsterRemember(recovery, 2, 0, {end:2});
R.monsterRecover(recovery, 2, 255, 10);
assert.equal(recovery.seen[1].end,10);
assert.equal(recovery.seen[0].end,8);
R.monsterRemember(recovery, 34, 1, {end:0});
R.monsterRecover(recovery, 34, 255, 8);
assert.equal(recovery.seen[0].end,0);
const {Engine}=await import('../SCOSWAMP.MORE/TOOLS/interpreter/engine.js');
const {parseScene}=await import('../SCOSWAMP.MORE/TOOLS/interpreter/scene.js');
const {readFile}=await import('node:fs/promises');
const proj=JSON.parse(await readFile(new URL('../SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json',import.meta.url),'utf8'));
const e=new Engine(proj,{});e.app.mapHere=33;e.app.currentScene=181;
R.monsterRemember(e.app.mem,34,0,{end:3});
for(const lang of ['FR','EN']){
  e.app.restoring=lang==='EN';
  parseScene(e.app,await readFile(new URL(`../SCOSWAMP/TEXT${lang}/N150/N181.TXT`,import.meta.url),'utf8'));
  assert.equal(e.app.mem.seen[0].end,4,'MR is an entry effect, not replayed on restore');
}
console.log('recovery: gain, cap, isolation, no resurrection and bilingual restore guard passed');
