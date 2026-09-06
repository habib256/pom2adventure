/* data.js -- la couche qui lit le disque, et rien d'autre.
 *
 * Le lecteur ne connait aucun chemin en dur : tout vient du descripteur du
 * jeu (project.*.json), gabarits compris. C'est ce qui permet a SCOSWAMP et a
 * SPACETRIP d'etre deux DONNEES du meme atelier, et non deux programmes.
 *
 * Les catalogues suivent le meme principe que le portage Apple II : les
 * objets viennent de OBJ{LANG}.TXT, les messages d'interface de MSG{LANG}.TXT
 * indexes par l'enumeration de SRC/messages.h, les noms de clairieres du
 * fichier MAP. Rien n'est recopie ici.
 */

import { VolumeProDOS, cheminVolume } from './prodos.js';

/* La racine du depot, deduite de l'emplacement de ce module : le lecteur vit
 * dans SCOSWAMP.MORE/TOOLS/interpreter/, trois crans sous la racine.
 *
 * `globalThis.RACINE_DONNEES` la remplace : c'est la couture par laquelle un
 * banc d'essai sans navigateur (node, fetch branche sur le disque) monte les
 * memes modules. Le moteur ne connait pas d'autre chemin que celui-la. */
export const ROOT = globalThis.RACINE_DONNEES
  ? new URL(globalThis.RACINE_DONNEES)
  : new URL('../../../', import.meta.url);

export function url(p) { return new URL(p, ROOT).href; }

/* ── D'ou viennent les octets ─────────────────────────────────────────────
 *
 * Deux sources, et la difference compte. L'ARBORESCENCE du depot est ce qu'on
 * edite ; le VOLUME ProDOS (dist/SCOSWAMP.HDV) est ce que la machine demarre.
 * Entre les deux il y a un empaquetage, et tant qu'il n'a pas tourne les deux
 * different. L'atelier lit le volume par defaut -- « exactement les memes
 * donnees que l'implementation Apple II » veut dire les memes octets, pas les
 * memes fichiers a peu pres.
 *
 * Ce que le volume ne porte pas (les masters d'avant conversion, l'ordre des
 * messages qui vit dans SRC/messages.h) est lu dans l'arborescence, et le
 * lecteur le DIT plutot que de faire comme si de rien n'etait. */
let source = { type: 'arbre', volume: null, racine: '', horsVolume: new Set() };

export async function ouvrirVolume(proj) {
  if (!proj.volume) throw new Error('ce jeu ne declare pas de volume');
  const r = await fetch(url(proj.volume));
  if (!r.ok) throw new Error(`${proj.volume} : HTTP ${r.status}`);
  const v = new VolumeProDOS(new Uint8Array(await r.arrayBuffer()));
  source = { type: 'volume', volume: v, racine: proj.racineVolume || '', horsVolume: new Set() };
  return v;
}

export function utiliserArbre() {
  source = { type: 'arbre', volume: null, racine: '', horsVolume: new Set() };
}

export function etatSource() {
  return {
    type: source.type,
    nom: source.volume ? source.volume.nom : '',
    fichiers: source.volume ? source.volume.fichiers.size : 0,
    horsVolume: [...source.horsVolume],
  };
}

const LATIN1 = new TextDecoder('latin1');

/* `volume: false` force la lecture dans l'arborescence : c'est le cas des
 * masters d'avant conversion, qui n'ont RIEN a faire sur le volume -- les y
 * chercher et signaler leur absence serait un faux probleme. */
async function get(p, bin, o = {}) {
  let horsVolume = false;
  if (source.type === 'volume' && o.volume !== false) {
    const octets = source.volume.lire(cheminVolume(p, source.racine));
    if (octets) return bin ? octets : LATIN1.decode(octets);
    horsVolume = true;    /* absent du volume : on retombe sur l'arborescence */
  }
  const r = await fetch(url(p));
  /* On ne note que ce qui existe VRAIMENT ailleurs : un fichier absent des
   * deux cotes n'est pas « hors volume », il n'est nulle part -- et la boucle
   * du verificateur, qui sonde toutes les pages jusqu'a pageMax, en produit
   * par dizaines. */
  if (!r.ok) throw new Error(`${p} : HTTP ${r.status}`);
  if (horsVolume) source.horsVolume.add(p);
  return bin ? new Uint8Array(await r.arrayBuffer()) : r.text();
}
export const getText = (p, o) => get(p, false, o);
export const getBytes = (p, o) => get(p, true, o);

/* Le volume est-il a jour pour ce fichier-la ? Rend 'identique', 'different',
 * 'absent' ou null si l'on ne lit pas le volume. C'est la question que se pose
 * l'auteur qui vient d'editer une page : est-ce que la machine la verra ? */
export async function comparerAuDepot(p) {
  if (source.type !== 'volume') return null;
  const surVolume = source.volume.lire(cheminVolume(p, source.racine));
  if (!surVolume) return 'absent';
  try {
    const r = await fetch(url(p));
    if (!r.ok) return 'absent';
    const surDisque = new Uint8Array(await r.arrayBuffer());
    if (surDisque.length !== surVolume.length) return 'different';
    for (let i = 0; i < surDisque.length; i++) if (surDisque[i] !== surVolume[i]) return 'different';
    return 'identique';
  } catch { return 'absent'; }
}

export async function exists(p) {
  try { const r = await fetch(url(p), { method: 'HEAD' }); return r.ok; } catch { return false; }
}

/* ── Gabarits de chemin ───────────────────────────────────────────────── */

export const pad3 = (n) => String(n).padStart(3, '0');

/* Le sous-repertoire du volume ProDOS : (id / 50) * 50, la meme regle que
 * enter_asset_dir(). `bucket: 0` dans le descripteur = pas de decoupage. */
export function bucketOf(proj, id) {
  const b = proj.bucket | 0;
  return b ? 'N' + pad3(Math.floor(id / b) * b) : '';
}

export function fill(proj, gabarit, { lang, id, img } = {}) {
  return gabarit
    .replaceAll('{LANG}', lang || 'FR')
    .replaceAll('{BUCKET}', id === undefined ? '' : bucketOf(proj, id))
    .replaceAll('{PAGE}', id === undefined ? '' : 'N' + pad3(id))
    .replaceAll('{IMG}', img || '');
}

export const pagePath = (proj, lang, id) => fill(proj, proj.assets.texte, { lang, id });

/* ── Le descripteur ───────────────────────────────────────────────────── */

export async function loadProject(nom) {
  const r = await fetch(new URL(nom, import.meta.url).href);
  if (!r.ok) throw new Error(`descripteur ${nom} introuvable`);
  const proj = await r.json();
  if (proj.rulesSource) {
    const rules = await fetch(url(proj.rulesSource));
    if (!rules.ok) throw new Error(`regles ${proj.rulesSource} introuvables`);
    proj.rules = await rules.json();
    if (proj.rules.schema !== 1) throw new Error('schema de regles non pris en charge');
  }
  return proj;
}

/* ── Les catalogues d'une langue ──────────────────────────────────────── */

/* OBJ{LANG}.TXT : une ligne par bit, "JETON Libelle". L'ORDRE FAIT FOI, un
 * jeton prefixe d'un point est un drapeau narratif -- jamais montre. */
function parseObjets(txt) {
  return txt.split(/\r?\n/).filter((l) => l.trim() !== '').map((l) => {
    const i = l.indexOf(' ');
    const cle = i < 0 ? l : l.slice(0, i);
    return { cle, libelle: i < 0 ? '' : l.slice(i + 1), cache: cle.startsWith('.') };
  });
}

/* MSG{LANG}.TXT n'est qu'une liste de lignes : ce sont les noms de
 * SRC/messages.h qui leur donnent un sens. Lire le .h evite de recopier ici
 * une enumeration que build_messages.py tient deja. */
function parseEnum(header) {
  const bloc = header.slice(header.indexOf('enum {') + 6, header.indexOf('MSG_COUNT'));
  return bloc.split(',').map((s) => s.trim()).filter((s) => /^M_[A-Z0-9_]+$/.test(s));
}

/* Le formateur minimal de cfmt() : %u, %s, %c dans l'ordre, largeur comprise
 * (%2u, %-12s), %% litteral. Les catalogues du jeu s'en servent partout. */
export function fmt(s, ...args) {
  let i = 0;
  return String(s).replace(/%%|%(-?)(\d*)([usc])/g, (m, gauche, larg) => {
    if (m === '%%') return '%';
    const v = String(args[i++] ?? '');
    const n = parseInt(larg, 10) || 0;
    if (v.length >= n) return v;
    return gauche ? v + ' '.repeat(n - v.length) : ' '.repeat(n - v.length) + v;
  });
}

/* Un jeu peut n'avoir ni catalogue d'objets ni catalogue de messages -- ce
 * sont des fichiers de SCOSWAMP, pas une obligation du format. Le descripteur
 * fournit alors ses propres libelles, et ce qui manque manque en clair : un
 * message inconnu s'affiche sous son nom plutot que de disparaitre. */
export async function loadCatalogs(proj, lang) {
  const a = proj.assets;
  const objets = a.objets ? parseObjets(await getText(fill(proj, a.objets, { lang }))) : (proj.objets || []);
  let table = (proj.messages && proj.messages[lang]) || {};
  if (a.messages && a.messagesEnum) {
    const [msgTxt, header] = await Promise.all([
      getText(fill(proj, a.messages, { lang })),
      /* L'ORDRE des messages n'est pas une donnee du volume : il est compile
       * dans le binaire (l'enumeration de SRC/messages.h). On le lit donc
       * toujours dans l'arborescence -- c'est la meme verite, a la meme
       * source que le jeu. Les CHAINES, elles, viennent du volume. */
      getText(a.messagesEnum, { volume: false }),
    ]);
    const lignes = msgTxt.split(/\r?\n/);
    table = {};
    parseEnum(header).forEach((n, i) => { table[n] = lignes[i] ?? ''; });
  }
  return { objets, messages: table, msg: (n, ...args) => fmt(table[n] ?? n, ...args) };
}

export async function loadTexteEcran(proj, lang, cle, o) {
  if (!proj.assets[cle]) return '';
  try { return await getText(fill(proj, proj.assets[cle], { lang }), o); }
  catch { return ''; }
}

/* ── Le fichier MAP ───────────────────────────────────────────────────────
 * Format v3, tel que TOOLS/build_map.py l'ecrit et que scoswamp.c le lit.
 * Tout y est : la grille, les sorties, le rabattement page -> clairiere et
 * les deux blocs de langue (35 noms de 13 octets, puis les chaines de
 * l'ecran MAP dans l'ordre de l'enumeration MS_*). */
export const MS = {
  TITRE: 0, SUR35: 1, SORTIES: 2, VUE: 3, INCONNUE: 4, HORS: 5,
  LEGENDE: 6, LEG1: 7, LEG2: 8, LEG3: 9, LEG4: 10, LEG5: 11,
  TOUCHES: 12, ANNEAU: 13, LIEU: 14, DEJA: 15, DIRS: 16,
};

function parseBlocLangue(b, off, nclr, namew) {
  const dec = new TextDecoder('latin1');
  const noms = [];
  for (let i = 0; i < nclr; i++) {
    const s = off + i * namew;
    let e = s;
    while (e < s + namew && b[e]) e++;
    noms.push(dec.decode(b.subarray(s, e)));
  }
  const chaines = [];
  let p = off + nclr * namew;
  while (p < b.length && chaines.length < 32) {
    let e = p;
    while (e < b.length && b[e]) e++;
    if (e === p && chaines.length) break;
    chaines.push(dec.decode(b.subarray(p, e)));
    p = e + 1;
  }
  return { noms, chaines };
}

export async function loadMap(proj) {
  if (!proj.assets.carte) return null;
  let b;
  try { b = await getBytes(proj.assets.carte); } catch { return null; }
  if (b.length < 20 || b[0] !== 77 || b[1] !== 65 || b[2] !== 80) return null;
  const u16 = (i) => b[i] | (b[i + 1] << 8);
  const nclr = b[4], npages = b[5], namew = b[6];
  const head = 20, pool = head + 3 * nclr;
  const clr = [];
  for (let i = 0; i < nclr; i++) {
    const r = head + 3 * i;
    clr.push({ x: b[r] & 7, y: b[r] >> 3, cell: b[r], num: b[r + 1], out: b[r + 2] });
  }
  const pages = [];
  let p = 0;
  for (let i = 0; i < npages; i++) {
    p += b[pool + 2 * i];
    pages.push({ page: p, clr: b[pool + 2 * i + 1] });
  }
  const blocOff = pool + 2 * npages;
  const lenFR = u16(16);
  return {
    version: b[3], nclr, npages, namew,
    depart: b[7], pont: b[8], riviere: b[9],
    sortieSud: u16(10), sortieNord: u16(12), pageDepart: u16(14),
    clr, pages,
    langue: {
      FR: parseBlocLangue(b, blocOff, nclr, namew),
      EN: parseBlocLangue(b, blocOff + lenFR, nclr, namew),
    },
  };
}

/* La clairiere d'une page, ou -1 : le meme rabattement que map_of_page(). */
export function clairiereDePage(carte, page) {
  if (!carte) return -1;
  const e = carte.pages.find((x) => x.page === page);
  return e ? e.clr : -1;
}

/* Le voisin dans une direction : la premiere case occupee de la ligne ou de
 * la colonne. Aucune table de sentiers -- « un sentier peut suivre un trace
 * sinueux mais sa direction generale restera toujours la meme ». */
const DX = [0, 0, 1, -1], DY = [-1, 1, 0, 0];   /* N S E O */
export function voisin(carte, i, d) {
  let { x, y } = carte.clr[i];
  for (;;) {
    x += DX[d]; y += DY[d];
    if (x < 0 || x > 5 || y < 0 || y > 8) return -1;
    const j = carte.clr.findIndex((c) => c.x === x && c.y === y);
    if (j >= 0) return j;
  }
}
