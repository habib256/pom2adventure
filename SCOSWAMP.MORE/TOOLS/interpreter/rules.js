/* rules.js -- les regles de Defis Fantastiques, portees telles quelles.
 *
 * Portage ligne a ligne de SCOSWAMP/SRC/rules.c et dice.c. Les bornes, les
 * arrondis et jusqu'au generateur de des sont ceux de la machine : a semence
 * egale, ce lecteur jette EXACTEMENT les memes des que le binaire Apple II.
 * C'est ce qui permet de rejouer ici une partie constatee la-bas.
 *
 * Rien dans ce fichier ne connait le DOM ni le format des pages : c'est le
 * noyau de regles, et un autre jeu de l'atelier le remplacerait sans toucher
 * au reste.
 */

/* ── Les des : le congruentiel de dice.c, bit pour bit ─────────────────── */

let diceState = 1;

export function diceSeed(seed) {
  diceState = (seed >>> 0) || 1;   /* 0 est un point fixe : le fuir */
}

function next16() {
  /* state = state * 1664525 + 1013904223, en 32 bits non signes. Math.imul
   * fait la multiplication modulo 2^32 sans passer par les doubles. */
  diceState = (Math.imul(diceState, 1664525) + 1013904223) >>> 0;
  return (diceState >>> 16) & 0xffff;   /* les bits bas d'un LCG sont biaises */
}

export function rollD6()  { return (next16() % 6) + 1; }
export function roll2D6() { return rollD6() + rollD6(); }
export function diceStateGet() { return diceState; }
export function diceStateSet(v) { diceState = v >>> 0; }

/* ── Catalogues ───────────────────────────────────────────────────────────
 * Les objets viennent du disque (OBJ{LANG}.TXT, une ligne par bit, l'ordre
 * fait foi) ; les Pierres et les amulettes du descripteur du jeu. Aucune
 * table n'est ecrite ici : le lecteur lit les memes donnees que le jeu. */

export const cat = {
  objets: [],      /* [{cle, libelle, cache}] -- l'index EST le numero du bit */
  pierres: [],     /* [{fr, en, categorie}] */
  amulettes: [],   /* [{cle, fr, en}] */
  hidden0: 0,      /* premier drapeau narratif : rien au-dela ne se montre */
};

export function setCatalogs({ objets, pierres, amulettes }) {
  cat.objets = objets;
  cat.pierres = pierres;
  cat.amulettes = amulettes;
  const h = objets.findIndex((o) => o.cache);
  cat.hidden0 = h < 0 ? objets.length : h;
}

export const OBJ_COUNT    = () => cat.objets.length;
export const STONE_COUNT  = () => cat.pierres.length;
export const AMULET_COUNT = () => cat.amulettes.length;

/* Comparaison de same_name() : insensible a la casse, egalite complete. */
function sameName(a, b) { return String(a).toUpperCase() === String(b).toUpperCase(); }

export function objectFromName(name) {
  const i = cat.objets.findIndex((o) => sameName(name, o.cle));
  return i < 0 ? OBJ_COUNT() : i;
}
export function amuletFromName(name) {
  const i = cat.amulettes.findIndex((a) => sameName(name, a.cle));
  return i < 0 ? AMULET_COUNT() : i;
}
export function stoneFromName(name) {
  const i = cat.pierres.findIndex((s) => sameName(name, s.fr) || sameName(name, s.en));
  return i < 0 ? STONE_COUNT() : i;
}
export function stoneKind(s) { return cat.pierres[s] ? cat.pierres[s].categorie : 'N'; }
export function stoneName(s, english) {
  const p = cat.pierres[s];
  return p ? (english ? p.en : p.fr) : '';
}
export function objectName(o) { return cat.objets[o] ? cat.objets[o].libelle : ''; }
export function amuletName(a, english) {
  const m = cat.amulettes[a];
  return m ? (english ? m.en : m.fr) : '';
}

/* ── La Feuille d'Aventure ────────────────────────────────────────────── */

export function newCharacter() {
  return {
    hab: 0, hab0: 0, end: 0, end0: 0, cha: 0, cha0: 0,
    gold: 0, weaponBonus: 0,
    stones: new Array(12).fill(0),
    objects: 0,     /* un bit par objet */
    amulets: 0,     /* un bit par amulette */
  };
}

/* "Lancez un de. Ajoutez 6 [...] HABILETE. Lancez ensuite les deux des.
 * Ajoutez 12 [...] ENDURANCE. [...] Lancez a nouveau un de, ajoutez 6 [...]
 * CHANCE." L'ordre des jets compte : il fixe la suite du LCG. */
export function characterRoll(c) {
  c.hab0 = c.hab = rollD6() + 6;
  c.end0 = c.end = roll2D6() + 12;
  c.cha0 = c.cha = rollD6() + 6;
  c.gold = 20;
  c.weaponBonus = 0;
  c.stones = new Array(STONE_COUNT()).fill(0);
  c.objects = 1 << objectFromName('ANNEAU');   /* l'Anneau de Cuivre */
  c.amulets = 0;
}

export function hasObject(c, o) { return o >= 0 && o < OBJ_COUNT() && !!(c.objects & (1 << o)); }
export function giveObject(c, o) { if (o >= 0 && o < OBJ_COUNT()) c.objects |= (1 << o); }
export function takeObject(c, o) { if (o >= 0 && o < OBJ_COUNT()) c.objects &= ~(1 << o); }

export function migrateSavedFlags(hero, mem, rules) {
  const rows = [];
  for (const group of rules?.save_migrations || []) {
    if (!group.when_none.length || new Set(group.when_none).size !== group.when_none.length)
      throw new Error('la migration exige des drapeaux distincts');
    let mask = 0;
    for (const key of group.when_none) {
      const id = objectFromName(key);
      if (id === OBJ_COUNT()) throw new Error(`drapeau inconnu : ${key}`);
      mask |= 1 << id;
    }
    if (!group.first_visited.length) throw new Error('migration vide');
    for (const branch of group.first_visited) {
      if (!Number.isInteger(branch.page) || branch.page < 0 || branch.page > 65535 ||
          !group.when_none.includes(branch.give)) throw new Error('branche de migration invalide');
      rows.push({ mask, page: branch.page, id: objectFromName(branch.give) });
    }
  }
  for (const row of rows) {
    if (!(hero.objects & row.mask) && sceneVisited(mem, row.page)) giveObject(hero, row.id);
  }
}
export function hasAmulet(c, a) { return a >= 0 && a < AMULET_COUNT() && !!(c.amulets & (1 << a)); }
export function giveAmulet(c, a) { if (a >= 0 && a < AMULET_COUNT()) c.amulets |= (1 << a); }
export function amuletCount(c) {
  let bits = c.amulets, n = 0;
  while (bits) { n += bits & 1; bits >>= 1; }
  return n;
}
export function tradeAmulets(c, each) {
  const n = amuletCount(c);
  adjustGold(c, n * each);
  c.amulets = 0;
  return n;
}

/* Plancher a zero, plafond au total de depart : la seule porte qui connaisse
 * la regle -- "ce total ne doit en aucun cas exceder vos points de depart". */
function adjust(c, k, k0, d) {
  let v = c[k] + d;
  if (v < 0) v = 0;
  if (v > c[k0]) v = c[k0];
  c[k] = v;
}
export function adjustHab(c, d) { adjust(c, 'hab', 'hab0', d); }
export function adjustEnd(c, d) {
  if (c.end <= 0 && d > 0) return; // La mort ne peut pas etre annulee par un soin.
  adjust(c, 'end', 'end0', d);
}
export function adjustCha(c, d) { adjust(c, 'cha', 'cha0', d); }
/* L'or n'a pas de plafond -- le livre n'en pose aucun -- mais il a le meme
 * plancher : on ne paie pas ce qu'on n'a pas. */
export function adjustGold(c, d) { c.gold = Math.max(0, c.gold + d); }

// The policy selects eligible goods; catalogue order defines consumption
// order, objects before amulets. Validate everything before changing the bag.
export function tradeInventory(c, policy) {
  if (policy === undefined) return {count: 0, categories: 'N'};
  if (!policy || typeof policy !== 'object') throw new Error('invalid trade policy');
  const {objects, amulets, limit, categories} = policy;
  if (!Array.isArray(objects) || new Set(objects).size !== objects.length ||
      !objects.every(k => typeof k === 'string') || typeof amulets !== 'boolean' ||
      !Number.isInteger(limit) || limit < 0 || limit > 255 ||
      typeof categories !== 'string' || !/^[NBM]{1,2}$/.test(categories) ||
      new Set(categories).size !== categories.length) throw new Error('invalid trade policy');
  let mask = 0;
  for (const key of objects) {
    const id = objectFromName(key);
    if (id === OBJ_COUNT() || cat.objets[id].cle !== key) throw new Error(`unknown trade object: ${key}`);
    mask |= 1 << id;
  }
  let bits = c.objects & mask, count = 0;
  while (bits && count < limit) { bits &= bits - 1; count++; }
  c.objects = (c.objects & ~mask) | bits;
  while (amulets && c.amulets && count < limit) { c.amulets &= c.amulets - 1; count++; }
  return {count, categories};
}

/* Variation du TOTAL DE DEPART, valeur courante comprise. En perte elle est
 * definitive (page 87), en gain elle releve le plafond (page 155).
 * k suit carac_of : 0 ENDURANCE, 1 HABILETE, 2 CHANCE. */
export function shift0(c, k, delta) {
  const paire = [['end', 'end0'], ['hab', 'hab0'], ['cha', 'cha0']][k];
  if (!paire) return;
  let n0 = c[paire[1]] + delta;
  if (n0 < 1) n0 = 1;    /* une caracteristique nulle serait une mort */
  c[paire[1]] = n0;
  adjust(c, paire[0], paire[1], delta);
}

export function isDead(c) { return c.end === 0; }

/* ── Tentez votre Chance ──────────────────────────────────────────────────
 * "Si le chiffre obtenu est egal ou inferieur a vos points de CHANCE, vous
 * etes Chanceux." Le point se paie meme quand la CHANCE est deja a zero. */
export function luckTest(c) {
  const roll = roll2D6();
  const lucky = roll <= c.cha;
  if (c.cha > 0) c.cha--;
  return { lucky, roll };
}

/* ── Batailles ────────────────────────────────────────────────────────── */

export function newMonster() {
  return { hab: 0, end: 0, end0: 0, damage: 2, stopAt: 0, name: '' };
}
export function monsterSeal(m) { m.end0 = m.end; }
export function monsterIsBeaten(m) { return m.end <= m.stopAt; }

export const ROUND_DODGE = 0, ROUND_HERO_HITS = 1, ROUND_MONSTER_HITS = 2;

/* Un assaut : les des un par un, comme combat_round -- meme somme, donc meme
 * partie a semence egale, mais l'ecran peut montrer le jet. L'ORDRE des
 * quatre jets est celui du C : creature d'abord, heros ensuite. */
export function combatRound(c, m) {
  const a = rollD6(), b = rollD6(), d = rollD6(), e = rollD6();
  const r = {
    monsterD1: a, monsterD2: b, heroD1: d, heroD2: e,
    monsterForce: a + b + m.hab,
    heroForce: d + e + c.hab,
    outcome: 0,
  };
  if (c.hab && hasObject(c, objectFromName('.D'))) r.heroForce--;
  if (hasObject(c, objectFromName('EP'))) r.heroForce += c.weaponBonus;
  r.outcome = r.heroForce > r.monsterForce ? ROUND_HERO_HITS
            : r.heroForce < r.monsterForce ? ROUND_MONSTER_HITS
            : ROUND_DODGE;
  return r;
}

/* Etapes 4 a 6. Rend {lucky} si la Chance a ete tentee et etait bonne. */
export function combatApply(c, m, r, useLuck) {
  let lucky = false, dmg;
  if (r.outcome === ROUND_HERO_HITS) {
    dmg = 2;
    if (useLuck) { lucky = luckTest(c).lucky; dmg = lucky ? 4 : 1; }
    m.end = m.end > dmg ? m.end - dmg : 0;
  } else if (r.outcome === ROUND_MONSTER_HITS) {
    dmg = m.damage;
    if (useLuck) { lucky = luckTest(c).lucky; dmg += lucky ? -1 : 1; }
    adjustEnd(c, -dmg);
  }
  return lucky;
}

/* "la creature vous aura automatiquement inflige une blessure" : celle de la
 * creature, doublee comprise, et la Chance peut encore la changer. */
export function combatFlee(c, m, useLuck) {
  let lucky = false, dmg = m.damage;
  if (useLuck) { lucky = luckTest(c).lucky; dmg += lucky ? -1 : 1; }
  adjustEnd(c, -dmg);
  return lucky;
}

/* ── Memoire des clairieres ───────────────────────────────────────────────
 * "il est possible que vous reveniez plus tard dans cette clairiere [...] il
 * vous faudrait peut-etre reprendre le combat la ou vous l'aviez laisse."
 * Table clairsemee de 40 emplacements, comme rules.c : zone 0 = libre. */
export const MONSTER_SLOTS = 40;

export function newMemory() {
  return {
    seen: Array.from({ length: MONSTER_SLOTS }, () => ({ scene: 0, index: 0, end: 0 })),
    visited: new Uint8Array(53),   /* un bit par page, 424 au plus */
  };
}

function slotOf(mem, zone) { return mem.seen.findIndex((s) => s.scene === zone); }

export function monsterZoneKey(app) {
  return app.mapHere >= 0 ? app.mapHere + 1 : 0x100 + app.currentScene;
}
export function monsterRecover(mem, zone, amount, maximum) {
  const i = slotOf(mem, zone);
  if (i < 0 || !mem.seen[i].end || mem.seen[i].end >= maximum) return;
  mem.seen[i].end = Math.min(maximum, mem.seen[i].end + amount);
}

export function monsterEnter(mem, zone, foes, count) {
  const i = slotOf(mem, zone);
  if (i < 0) return 0;                    /* jamais combattu ici */
  let idx = mem.seen[i].index;
  if (idx >= count) {
    if (idx !== count || !mem.seen[i].end) return count;
    idx--;
  }
  foes[idx].end = mem.seen[i].end;
  if (monsterIsBeaten(foes[idx])) return idx + 1;
  return idx;
}

export function monsterRemember(mem, zone, index, m) {
  let i = slotOf(mem, zone);
  if (i < 0) i = slotOf(mem, 0);
  if (i >= 0) { mem.seen[i] = { scene: zone, index, end: m.end }; }
}

export function sceneVisited(mem, scene) {
  if (scene < 0 || scene >= mem.visited.length * 8) return false;
  return (mem.visited[scene >> 3] & (1 << (scene & 7))) !== 0;
}
export function sceneMarkVisited(mem, scene) {
  if (scene >= 0 && scene < mem.visited.length * 8) mem.visited[scene >> 3] |= (1 << (scene & 7));
}

/* ── La Magie ─────────────────────────────────────────────────────────── */

export function giveStone(c, s, n) {
  if (s >= 0 && s < STONE_COUNT()) c.stones[s] = Math.min(255, (c.stones[s] || 0) + n);
}
export function hasStone(c, s) { return s >= 0 && s < STONE_COUNT() ? c.stones[s] : 0; }

/* "Vous avez le droit d'utiliser les pierres d'ENDURANCE, d'HABILETE et de
 * CHANCE a tout moment, SAUF au cours d'un combat [...] sitot que le premier
 * coup a ete donne." Les trois premieres du catalogue sont celles-la. */
export function stoneUsable(s, inCombat) { return inCombat !== 2 && (!inCombat || s > 2); }

export const STONE_USE_OK = 0, STONE_USE_NONE = 1, STONE_USE_FORBIDDEN = 2;

/* "vous recupererez [...] la moitie de votre total de depart (si ce total est
 * impair, arrondissez au chiffre superieur)". */
const halfUp = (start) => ((start + 1) / 2) | 0;

export function stoneUse(c, s, inCombat) {
  if (s < 0 || s >= STONE_COUNT()) return STONE_USE_NONE;
  if (!c.stones[s]) return STONE_USE_NONE;
  if (!stoneUsable(s, inCombat)) return STONE_USE_FORBIDDEN;
  c.stones[s]--;
  if (s === 0) adjustHab(c, halfUp(c.hab0));
  else if (s === 1) adjustEnd(c, halfUp(c.end0));
  else if (s === 2) adjustCha(c, halfUp(c.cha0));
  else if (stoneName(s, false) === 'MALEDICTION') adjustEnd(c, -rollD6());
  /* Les autres n'ont aucun effet chiffre sur le heros : la pierre est
   * consommee, c'est la page qui decide de la suite. */
  return STONE_USE_OK;
}

/* PD / PO : "on vous prend n biens". Les Pierres partent en premier, puis les
 * objets VISIBLES sauf l'Anneau de Cuivre (bit 0), puis les amulettes. */
export function hasPayableItem(c) {
  return !!((c.objects & ((1 << cat.hidden0) - 2)) || c.amulets || c.stones.some(n => n > 0));
}

export function loseItems(c, n) {
  const STEALABLE = (1 << cat.hidden0) - 2;
  while (n) {
    const i = c.stones.findIndex((v) => v > 0);
    if (i >= 0) { c.stones[i]--; n--; continue; }
    let bits = c.objects & STEALABLE;
    if (bits) {
      bits &= bits - 1;                                   /* le plus bas s'en va */
      c.objects = (c.objects & ~STEALABLE) | bits;
      n--; continue;
    }
    if (c.amulets) { c.amulets &= c.amulets - 1; n--; continue; }
    break;
  }
}
