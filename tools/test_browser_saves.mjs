import assert from 'node:assert/strict';
import {Engine} from '../SCOSWAMP.MORE/TOOLS/interpreter/engine.js';
import * as R from '../SCOSWAMP.MORE/TOOLS/interpreter/rules.js';

const storage = new Map();
globalThis.localStorage = {
  getItem: k => storage.get(k) ?? null,
  setItem: (k, v) => storage.set(k, v),
};
const engine = new Engine({id: 'test', moteur: {pageMax: 424}, assets: {}, objets: [], pierres: [], amulettes: [], messages: {FR: {TEST: 'Francais'}, EN: {TEST: 'English'}}}, {
  render() {}, async key() { return '\x1b'; },
});
engine.app.currentScene = 61;
engine.app.heroReady = true;
engine.app.hero.end = engine.app.hero.end0 = 20;
R.diceStateSet(12345);
engine.saveGame(1);
const valid = storage.get(engine.slotKey(1));

async function rejected(raw) {
  storage.set(engine.slotKey(1), raw);
  const before = JSON.stringify(engine.app);
  const dice = R.diceStateGet();
  assert.equal(await engine.loadGame(1), false);
  assert.equal(JSON.stringify(engine.app), before, 'rejection preserves active state');
  assert.equal(R.diceStateGet(), dice, 'rejection preserves RNG');
}
for (const raw of ['{', 'null', '[]', '{}']) await rejected(raw);
for (const mutate of [
  s => { s.hero = null; },
  s => { s.hero.end = '20'; },
  s => { s.hero.stones.pop(); },
  s => { s.visited[0] = 256; },
  s => { s.seen[0] = null; },
  s => { s.scene = 9999; },
  s => { s.dice = -1; },
  s => { s.lastLoss = -1; },
]) {
  const s = JSON.parse(valid); mutate(s); await rejected(JSON.stringify(s));
}
// Broken slots cannot trap the player in the save menu.
await engine.showSaves(false);
assert.equal(engine.app.modal, null);

engine.proj.rules = {save_migrations: [
  {when_none: ['UNKNOWN'], first_visited: [{page: 2, give: 'UNKNOWN'}]},
]};
await rejected(valid);
delete engine.proj.rules;
storage.set(engine.slotKey(1), valid);
engine.app.hero.end = 3;
R.diceStateSet(42);
assert.equal(await engine.loadGame(1), true);
assert.equal(engine.app.hero.end, 20);
assert.equal(engine.app.pending, 61);
assert.equal(engine.app.restoring, true);
assert.equal(R.diceStateGet(), 12345);
console.log('browser saves: invalid snapshots and migrations preserve state; menu and valid resume pass');

const english = JSON.parse(valid);
english.lang = 'EN';
storage.set(engine.slotKey(1), JSON.stringify(english));
assert.equal(await engine.loadGame(1), true);
assert.equal(engine.app.lang, 'EN');
assert.equal(engine.app.english, true);
assert.equal(engine.app.msg('TEST'), 'English');
// A failed catalogue fetch leaves even the previous language intact.
engine.proj.assets.objets = 'missing-objects-{lang}.txt';
await rejected(valid);
delete engine.proj.assets.objets;
storage.set(engine.slotKey(1), valid);
assert.equal(await engine.loadGame(1), true);
assert.equal(engine.app.lang, 'FR');
assert.equal(engine.app.english, false);
assert.equal(engine.app.msg('TEST'), 'Francais');
console.log('save languages: FR/EN restoration and failed catalogue rollback pass');
