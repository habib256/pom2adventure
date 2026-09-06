/* main.js -- l'amorce : choisir le jeu, la source des donnees, la langue.
 *
 * La premiere page n'est pas un ecran de titre decoratif : c'est le choix de
 * ce qu'on va lire. Un jeu est une donnee (son descripteur), et la source en
 * est une autre -- le volume ProDOS que la machine demarre, ou l'arborescence
 * du depot que l'on edite. Les deux se choisissent ici.
 *
 * Les parametres d'adresse court-circuitent l'accueil :
 *   ?jeu=spacetrip   ?langue=FR   ?page=283   ?graine=1234   ?source=arbre
 */

import * as D from './data.js';
import { Engine } from './engine.js';
import { UI } from './ui.js';
import { diceSeed } from './rules.js';

const params = new URLSearchParams(location.search);
const accueil = document.getElementById('accueil');

/* La graine des des : ?graine=1234 rejoue exactement la meme partie, jets de
 * combat compris -- le generateur est celui de dice.c, bit pour bit. Sans
 * elle, l'horloge, comme l'attente de la premiere touche sur l'Apple II. */
diceSeed(parseInt(params.get('graine'), 10) || (Date.now() & 0xffff) || 1);

const catalogue = await (await fetch(new URL('jeux.json', import.meta.url))).json();
const jeux = [];
for (const j of catalogue.jeux) {
  try { jeux.push({ ...j, proj: await D.loadProject(j.descripteur) }); }
  catch (e) { console.warn(`${j.descripteur} : ${e.message}`); }
}

if (params.get('mode') !== 'jeu') {
  accueil.remove();
  const root = document.getElementById('app');
  root.className = 'studio';
  const { Workshop } = await import('./workshop.js');
  new Workshop(root);
} else {
const demande = params.get('jeu');
const direct = demande && jeux.find((j) => j.descripteur.includes(demande.toLowerCase()));
if (direct) choisirJeu(direct.proj);
else ecranJeux();
}

/* ── Le choix du jeu ────────────────────────────────────────────────────── */

function ecranJeux() {
  accueil.innerHTML = `
    <h1>Atelier de jeux d'aventure</h1>
    <p class="sous">Les donnees d'un jeu, lues comme la machine les lit.</p>
    <div class="jeux"></div>`;
  const liste = accueil.querySelector('.jeux');
  for (const j of jeux) {
    const p = j.proj;
    const c = document.createElement('button');
    c.className = 'jeu';
    c.innerHTML = `
      <strong>${esc(p.titre)}</strong>
      <span class="cle">${esc(p.id)}</span>
      <ul>
        <li>${p.moteur.pageMax + 1} pages au plus, ${p.directives.length} directive(s)</li>
        <li>${p.images.map((i) => esc(i.nom)).join(', ')}</li>
        <li>${p.volume ? 'volume ProDOS : ' + esc(p.volume) : 'pas de volume empaquete'}</li>
      </ul>`;
    c.onclick = () => choisirJeu(p);
    liste.append(c);
  }
}

/* ── La source des donnees, puis la langue ─────────────────────────────── */

async function choisirJeu(proj) {
  document.title = `${proj.titre} -- atelier`;
  let source = params.get('source') || (proj.volume ? 'volume' : 'arbre');
  let etat = '';

  if (source === 'volume') {
    try {
      const v = await D.ouvrirVolume(proj);
      etat = `volume ${v.nom} ouvert : ${v.fichiers.size} fichiers`;
    } catch (e) {
      source = 'arbre';
      D.utiliserArbre();
      etat = `volume illisible (${e.message}) -- lecture de l'arborescence`;
    }
  } else {
    D.utiliserArbre();
  }

  const titre = await D.loadTexteEcran(proj, 'FR', 'titre', { volume: source === 'volume' });
  accueil.innerHTML = `
    ${titre ? `<pre>${esc(titre)}</pre>` : `<h1>${esc(proj.titre)}</h1>`}
    <div class="source"></div>
    <div class="langues"></div>
    <button class="retour">&larr; changer de jeu</button>`;

  const boiteSource = accueil.querySelector('.source');
  if (proj.volume) {
    boiteSource.innerHTML = `
      <label><input type="radio" name="src" value="volume"> Volume ProDOS -- ce que la machine demarre</label>
      <label><input type="radio" name="src" value="arbre"> Arborescence du depot -- ce que l'on edite</label>
      <p class="etat">${esc(etat)}</p>`;
    boiteSource.querySelector(`input[value="${source}"]`).checked = true;
    boiteSource.querySelectorAll('input').forEach((r) => {
      r.onchange = () => { params.set('source', r.value); choisirJeu(proj); };
    });
  }

  const langues = accueil.querySelector('.langues');
  for (const l of proj.langues) {
    const b = document.createElement('button');
    b.textContent = `[${l.code[0]}] ${l.nom}`;
    b.onclick = () => demarrer(proj, l.code);
    langues.append(b);
  }
  accueil.querySelector('.retour').onclick = () => { D.utiliserArbre(); ecranJeux(); };

  const choisie = proj.langues.find((l) => l.code === (params.get('langue') || '').toUpperCase());
  if (choisie) demarrer(proj, choisie.code);

  window.addEventListener('keydown', function amorce(e) {
    const l = proj.langues.find((x) => x.code[0] === e.key.toUpperCase());
    if (!l || !accueil.isConnected) return;
    window.removeEventListener('keydown', amorce);
    demarrer(proj, l.code);
  });
}

/* ── En jeu ─────────────────────────────────────────────────────────────── */

async function demarrer(proj, lang) {
  accueil.remove();
  const ui = new UI(document.getElementById('app'), proj);
  const engine = new Engine(proj, ui);
  ui.attach(engine);
  await engine.setLangue(lang);
  ui.el.langue.value = lang;
  /* Un raccourci du banc d'essai : ?page=283 se pose directement sur la page,
   * avec un heros deja jete -- on teste une scene sans rejouer le prologue.
   * Un jeu sans Feuille d'Aventure (SPACETRIP) n'en recoit pas. */
  const page = parseInt(params.get('page'), 10);
  if (Number.isFinite(page)) {
    if (proj.moteur.feuille !== false) {
      const { characterRoll } = await import('./rules.js');
      characterRoll(engine.app.hero);
      engine.app.heroReady = true;
    }
    engine.proj.moteur.pageDepart = page;
  }
  await engine.run();
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
