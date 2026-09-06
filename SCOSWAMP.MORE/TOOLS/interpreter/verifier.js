/* verifier.js -- le meme moteur, sans navigateur, pour verifier un corpus.
 *
 *   node SCOSWAMP.MORE/TOOLS/interpreter/verifier.js [descripteur] [langue] [--arbre]
 *
 * Il monte les modules du lecteur tels quels -- pas une copie, pas une
 * seconde implementation -- et branche `fetch` sur le disque. Ce qu'il dit
 * d'une page est donc exactement ce que le lecteur en fera, et ce que la
 * machine en fera.
 *
 * Il lit par defaut le VOLUME ProDOS -- ce que la machine demarre ; `--arbre`
 * lui fait lire l'arborescence du depot, ce que l'on edite.
 *
 * Il repond a cinq questions qu'aucun outil ne posait :
 *   - une ligne du fichier n'est-elle comprise par personne ?
 *   - une page cite-t-elle une cible qui n'existe pas ?
 *   - une page est-elle inatteignable depuis le depart ?
 *   - une page deborde-t-elle le budget de l'ecran (18 lignes, 80 colonnes,
 *     5 choix) ?
 *   - le volume et le depot disent-ils encore la meme chose ?
 */

import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const ICI = dirname(fileURLToPath(import.meta.url));
globalThis.RACINE_DONNEES = pathToFileURL(resolve(ICI, '../../..') + '/').href;
globalThis.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
globalThis.fetch = async (u) => {
  try {
    const b = await readFile(fileURLToPath(new URL(u)));
    return {
      ok: true, status: 200,
      text: async () => b.toString('latin1'),
      json: async () => JSON.parse(b.toString('utf8')),
      arrayBuffer: async () => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength),
    };
  } catch {
    return { ok: false, status: 404, text: async () => '', arrayBuffer: async () => new ArrayBuffer(0) };
  }
};

const D = await import('./data.js');
const { loadProject, getText, pagePath } = D;
const R = await import('./rules.js');
const { parseScene } = await import('./scene.js');
const { Engine } = await import('./engine.js');

const args = process.argv.slice(2);
const drapeaux = new Set(args.filter((a) => a.startsWith('--')));
const positionnels = args.filter((a) => !a.startsWith('--'));
const descripteur = positionnels[0] || 'project.scoswamp.json';
const langue = positionnels[1] || 'FR';
const proj = await loadProject(descripteur);

/* Par defaut on verifie CE QUE LA MACHINE LIRA : le volume ProDOS. `--arbre`
 * verifie ce que l'on est en train d'editer. Les deux comptent, et ce ne sont
 * pas les memes octets tant que l'empaquetage n'a pas tourne. */
let source = 'arborescence';
if (proj.volume && !drapeaux.has('--arbre')) {
  try {
    const vol = await D.ouvrirVolume(proj);
    source = `volume ProDOS ${vol.nom} (${vol.fichiers.size} fichiers)`;
  } catch (e) {
    console.error(`volume illisible (${e.message}) -- lecture de l'arborescence`);
  }
}
const moteur = new Engine(proj, { render() {}, key: async () => ' ', resume() {} });
await moteur.setLangue(langue);
const app = moteur.app;

const existe = new Set(), cibles = new Map(), conditionRefs = [];
const soucis = [];

for (let id = 0; id <= proj.moteur.pageMax; id++) {
  let texte;
  try { texte = await getText(pagePath(proj, langue, id)); } catch { continue; }
  existe.add(id);

  Object.assign(app, {
    currentScene: id, title: null, body: [], choices: [], trace: [], foes: [], foeImg: [],
    revisit: -1, chooseN: 0, diceN: 0, luckOk: -1, luckKo: -1, csOk: -1, csKo: -1,
    mbOk: -1, mbKo: -1, winScene: -1, fleeTarget: -1, dvDone: false, lastLoss: 0,
    restoring: false,
  });
  app.hero = R.newCharacter();
  R.characterRoll(app.hero);
  parseScene(app, texte);

  for (const t of app.trace)
    if (/inconnu|non implementee|ignoree/.test(t.note || '')) soucis.push(`${id} : ${t.note} -- ${t.ligne}`);
  /* La ligne V doit PRECEDER tout le reste (le T excepte) : un effet d'entree
   * ecrit avant elle a deja joue quand le detour se decide, et la revisite
   * redonne ce qu'on a deja pris. C'est l'invariant que reflow_txt.py tient
   * pour SCOSWAMP ; le tenir ici pour tous les jeux. */
  const lignes = texte.split(/\r?\n/);
  lignes.forEach((l, i) => {
    if (/^VR? /.test(l) && lignes.slice(0, i).some((x) => x.trim() && !/^(T |VR? |AC$)/.test(x)))
      soucis.push(`${id} : la ligne V (ligne ${i + 1}) doit preceder le texte et les effets`);
  });
  if (app.body.length > proj.moteur.lignesTexte) soucis.push(`${id} : ${app.body.length} lignes de texte (budget ${proj.moteur.lignesTexte})`);
  for (const l of app.body) if (l.length > proj.moteur.colonnes) soucis.push(`${id} : ligne de ${l.length} colonnes`);

  /* Les cibles : celles des choix, celles des jets, celles de la victoire et
   * de la Fuite -- et celle de la ligne V, qui ne se declenche qu'a la
   * seconde visite et qu'un parcours a memoire vide ne verrait jamais. */
  const l = app.choices.map((c) => c.scene);
  for (const v of [app.luckOk, app.luckKo, app.csOk, app.csKo, app.mbOk, app.mbKo, app.winScene, app.fleeTarget])
    if (v >= 0) l.push(v);
  for (const ligne of texte.split(/\r?\n/)) {
    /* La ligne V ne se declenche qu'a la seconde visite, et la cascade DV ne
     * retient qu'une ligne selon ce que le combat a coute : un parcours a
     * memoire vide et sans blessure ne verrait jamais les autres. */
    if (/^C[VX] /.test(ligne)) {
      const parts = ligne.trim().split(/\s+/);
      l.push(Number(parts[2]));
      for (const proof of parts[1].split(',')) conditionRefs.push([id,Number(proof.replace('!', ''))]);
    }
    if (/^VR /.test(ligne)) {
      const nums = ligne.slice(3).trim().split(/\s+/).map(Number);
      l.push(nums[0]);
      for (const n of nums.slice(1)) conditionRefs.push([id,n]);
    }
    if (/^V /.test(ligne)) for (const n of ligne.slice(2).trim().split(/\s+/)) l.push(parseInt(n, 10));
    if (/^DV /.test(ligne)) l.push(parseInt(ligne.slice(3).trim().split(/\s+/)[1], 10));
  }
  cibles.set(id, l.filter((n) => Number.isFinite(n)));
}

const mortes = [];
for (const [id, ref] of conditionRefs) if (!existe.has(ref)) mortes.push(`${id} -> ${ref} (condition de visite)`);
for (const [id, l] of cibles) for (const c of new Set(l)) if (!existe.has(c)) mortes.push(`${id} -> ${c}`);

const vus = new Set([proj.moteur.pageDepart]);
const file = [proj.moteur.pageDepart];
while (file.length) {
  const p = file.pop();
  for (const c of cibles.get(p) || []) if (!vus.has(c)) { vus.add(c); file.push(c); }
}
const orphelines = [...existe].filter((p) => !vus.has(p));

/* Le depot et le volume disent-ils la meme chose ? Une page editee mais non
 * empaquetee n'est pas celle que la machine lira -- c'est le genre d'ecart
 * qu'on ne voit qu'en jouant, une heure trop tard. */
const desaccords = [];
if (D.etatSource().type === 'volume') {
  for (const id of existe) {
    const etat = await D.comparerAuDepot(pagePath(proj, langue, id));
    if (etat && etat !== 'identique') desaccords.push(`page ${id} : ${etat}`);
  }
  for (const cle of ['messages', 'objets', 'carte', 'aide', 'titre']) {
    if (!proj.assets[cle]) continue;
    const p = D.fill(proj, proj.assets[cle], { lang: langue });
    const etat = await D.comparerAuDepot(p);
    if (etat && etat !== 'identique') desaccords.push(`${cle} (${p}) : ${etat}`);
  }
}

const dit = (t, l) => console.log(l.length ? `${t} (${l.length}) :\n  ${l.join('\n  ')}` : `${t} : aucune`);
console.log(`${proj.titre} -- ${langue} : ${existe.size} pages lues depuis ${source}`);
dit('lignes non comprises ou hors budget', soucis);
dit('cibles inexistantes', mortes);
dit(`pages inatteignables depuis ${proj.moteur.pageDepart}`, orphelines);
if (D.etatSource().type === 'volume') {
  dit('ecarts entre le volume et le depot', desaccords);
  const hors = D.etatSource().horsVolume;
  if (hors.length) console.log(`lus hors du volume (${hors.length}) :\n  ${hors.join('\n  ')}`);
}
process.exit(soucis.length || mortes.length ? 1 : 0);
