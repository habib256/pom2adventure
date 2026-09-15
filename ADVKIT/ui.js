/* ui.js -- l'ecran de la machine a gauche, l'atelier a droite.
 *
 * La colonne de gauche N'EST PAS une mise en page web qui ressemble a
 * l'Apple II : c'est une grille de 80 x 24 cellules, chacune avec son
 * attribut de video inverse, peinte par les memes primitives que
 * scoswamp.c -- render_title_bar(), render_place(), render_choices(),
 * show_fighters(), put_gauge(), put_key(), put_roll(). Les barres, les
 * jauges et les touches sont donc les memes, au caractere et a la colonne
 * pres, y compris la ou le C s'arrete a la colonne 79 pour ne pas faire
 * defiler l'ecran.
 *
 * Les ecrans modaux -- le sac, la carte, l'aide, la Feuille, les
 * sauvegardes, le choix des Pierres -- sont eux aussi peints dans cette
 * grille, comme sur la machine, et non en fenetres flottantes.
 *
 * La colonne de droite est ce que la machine ne peut pas montrer : le master
 * avant conversion, le flux DHGR decode a cote, le journal des directives de
 * la page et sa source.
 */

import * as D from './data.js';
import * as R from './rules.js';
import { matchDirective, choiceAvailable } from './scene.js';
import { decodeToImageData, decodeRawHgr, paletteUsage } from './dhgr.js';
import { Ecran } from './ecran.js';

/* La mise en page de la machine, en dur sur les 24 lignes -- les memes
 * constantes que scoswamp.c. */
const BODY_ROW0 = 1, PLACE_ROW = 19, CHOICE_ROW0 = 20, CHOICE_ROWN = 23;
const CHOICE_COL2 = 40, CHOICE_WIDTH = 39;
const BORD = 79;   /* pad_to(79) : la derniere cellule ne s'ecrit jamais */

export class UI {
  constructor(root, proj) {
    this.proj = proj;
    this.root = root;
    this.el = {};
    this.ecran = new Ecran(proj.moteur.colonnes || 80, proj.moteur.lignes || 24);
    this.resolveKey = null;
    this.variante = proj.images[0].id;
    this.onglet = 'journal';
    this.build();
    window.addEventListener('keydown', (e) => this.onKeyDown(e));
  }

  attach(engine) { this.engine = engine; this.app = engine.app; }

  /* ── Les touches ────────────────────────────────────────────────────── */

  /* Le moteur appelle `await ui.key()` la ou le C appelle cgetc(). Une seule
   * attente a la fois : c'est exactement la boucle de la machine. */
  key() { return new Promise((res) => { this.resolveKey = res; }); }

  press(k) {
    const r = this.resolveKey;
    if (!r) return;
    this.resolveKey = null;
    r(k);
  }

  /* Le banc d'essai reprend la main : '\0' est la touche qui ne fait rien, et
   * que chaque boucle du moteur sait reconnaitre pour abandonner. */
  resume() { this.press('\x00'); }

  onKeyDown(e) {
    if (e.target && /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    let k = null;
    if (e.key === 'Escape') k = '\x1b';
    else if (e.key === 'Enter') k = '\r';
    else if (e.key === ' ') k = ' ';
    else if (e.key.length === 1) k = e.key.toUpperCase();
    if (k === null) return;
    e.preventDefault();
    this.press(k);
  }

  /* ── Construction du cadre ──────────────────────────────────────────── */

  build() {
    this.root.innerHTML = `
      <header class="barre">
        <a href="?mode=images&jeu=${this.proj.id.toLowerCase()}">Atelier images ↗</a>
        <strong>${echap(this.proj.titre)}</strong>
        <span class="sep"></span>
        <label>Langue <select id="langue"></select></label>
        <label>Page <input id="goto" type="number" min="0" max="${this.proj.moteur.pageMax}" step="1"></label>
        <button id="allerA">Aller a</button>
        <label>Graine <input id="graine" type="number" value="1"></label>
        <button id="semer">Semer</button>
        <span class="sep"></span>
        <span id="source" class="etat"></span>
        <span id="etat" class="etat"></span>
      </header>
      <main>
        <section class="gauche">
          <div id="ecran" class="ecran"></div>
        </section>
        <section class="droite">
          <div class="cartouche">
            <div class="entete">
              <select id="variante"></select>
              <span id="imageEtat" class="etat"></span>
            </div>
            <div class="imageBoite">
              <canvas id="toile" width="280" height="192"></canvas>
              <img id="photo" alt="">
              <div id="imageVide" class="vide"></div>
            </div>
          </div>
          <div id="feuille" class="cartouche"></div>
          <div class="cartouche">
            <div class="onglets">
              <button data-onglet="journal">Journal</button>
              <button data-onglet="source">Source</button>
              <button data-onglet="sac">Sac</button>
              <button data-onglet="directives">Directives</button>
            </div>
            <div id="panneau" class="panneau"></div>
          </div>
        </section>
      </main>`;

    const $ = (id) => this.root.querySelector('#' + id);
    this.el = {
      ecran: $('ecran'), toile: $('toile'), photo: $('photo'), imageVide: $('imageVide'),
      imageEtat: $('imageEtat'), variante: $('variante'), feuille: $('feuille'),
      panneau: $('panneau'), etat: $('etat'), source: $('source'),
      goto: $('goto'), graine: $('graine'), langue: $('langue'),
    };

    for (const v of this.proj.images) {
      const o = document.createElement('option');
      o.value = v.id; o.textContent = v.nom;
      this.el.variante.append(o);
    }
    for (const l of this.proj.langues) {
      const o = document.createElement('option');
      o.value = l.code; o.textContent = l.nom;
      this.el.langue.append(o);
    }
    this.el.variante.onchange = () => { this.variante = this.el.variante.value; this.showImage(); };
    this.el.langue.onchange = async () => {
      await this.engine.setLangue(this.el.langue.value);
      this.engine.app.pending = this.engine.app.currentScene;
      this.resume();
    };
    $('allerA').onclick = () => {
      const n = parseInt(this.el.goto.value, 10);
      if (Number.isFinite(n)) this.engine.gotoPage(n);
    };
    $('semer').onclick = () => {
      R.diceSeed(parseInt(this.el.graine.value, 10) || 1);
      this.majEtat('graine posee');
    };
    this.root.querySelectorAll('[data-onglet]').forEach((b) => {
      b.onclick = () => { this.onglet = b.dataset.onglet; this.renderPanneau(); };
    });
    /* Toute cellule qui porte une touche est cliquable : les lettres des
     * choix, les touches de l'invite, les emplacements de sauvegarde. */
    this.el.ecran.onclick = (e) => {
      const z = e.target.closest('[data-clic]');
      if (z) this.press(z.dataset.clic);
    };
  }

  majEtat(t) { this.el.etat.textContent = t; }

  /* D'ou viennent les octets de cette page-la. Sur le volume, on dit aussi si
   * le depot a bouge depuis l'empaquetage : une page editee mais non
   * empaquetee n'est pas celle que la machine lira. */
  renderSource() {
    const s = D.etatSource();
    const app = this.app;
    if (s.type !== 'volume') {
      this.el.source.textContent = 'arborescence du depot';
      this.el.source.className = 'etat';
      return;
    }
    const accord = { identique: 'volume = depot',
                     different: 'le depot a change depuis l\'empaquetage',
                     absent: 'page absente du volume' }[app.pageVolume] || '';
    this.el.source.textContent = `volume ${s.nom} (${s.fichiers} fichiers)`
      + (accord ? ` -- ${accord}` : '')
      + (s.horsVolume.length ? ` -- ${s.horsVolume.length} hors volume` : '');
    this.el.source.className = 'etat' + (app.pageVolume === 'different' ? ' alerte' : '');
    this.el.source.title = s.horsVolume.length
      ? 'lus dans l\'arborescence :\n' + s.horsVolume.join('\n') : '';
  }

  /* ── L'ecran ────────────────────────────────────────────────────────── */

  render() {
    const app = this.app;
    if (!app) return;
    this.el.langue.value = app.lang;
    const e = this.ecran;
    e.effacer();
    if (app.modal) this.dessineModale(e);
    else this.dessinePage(e);
    this.el.ecran.innerHTML = e.html();
    this.renderSource();
    this.renderFeuille();
    this.renderPanneau();
    this.showImage();
    this.el.goto.value = app.currentScene;
  }

  /* render_title_bar : le titre a gauche, le rappel des touches derriere, la
   * Feuille d'Aventure calee a droite, le tout en video inverse sur les 80
   * colonnes. */
  barreTitre(e) {
    const app = this.app;
    e.padTo(0, 0, e.cols, { inv: true });
    if (app.title) {
      const t = app.title.slice(0, 40);
      e.put(1, 0, t, { inv: true });
      if (app.heroReady) {
        e.put(t.length + 3, 0,
          app.lang === 'FR' ? 'I:SAC M:CARTE H:AIDE' : 'I:BAG M:MAP   H:HELP', { inv: true });
      }
    }
    const h = app.hero;
    const droite = app.heroReady
      ? (app.lang === 'FR'
          ? `HAB ${h.hab}/${h.hab0}  END ${h.end}/${h.end0}  CHA ${h.cha}/${h.cha0}`
          : `SKL ${h.hab}/${h.hab0}  STA ${h.end}/${h.end0}  LCK ${h.cha}/${h.cha0}`)
      : app.msg('M_TOUCHES');
    e.put(BORD - droite.length, 0, droite, { inv: true });
  }

  /* render_place : ou l'on est et par ou l'on peut partir, en video inverse
   * juste au-dessus des quatre lignes du mode mixte. Quand la page n'est
   * d'aucun lieu, la clairiere collante s'affiche entre parentheses : c'est
   * un souvenir, pas une position. */
  barreLieu(e) {
    const app = this.app;
    if (!app.carte || app.mapHere < 0) return;
    const bloc = app.carte.langue[app.lang] || app.carte.langue.FR;
    const nom = bloc.noms[app.mapHere];
    let x = e.put(0, PLACE_ROW, ' ', { inv: true });
    if (D.clairiereDePage(app.carte, app.currentScene) !== app.mapHere) {
      x = e.put(x, PLACE_ROW, `(${nom})`, { inv: true });
    } else {
      const dirs = bloc.chaines[D.MS.DIRS] || 'NSEO';
      const m = app.carte.clr[app.mapHere].out;
      x = e.put(x, PLACE_ROW, `${nom}   ${bloc.chaines[D.MS.LIEU]} `, { inv: true });
      for (let d = 0; d < 4; d++) if (m & (1 << d)) x = e.put(x, PLACE_ROW, dirs[d] + ' ', { inv: true });
      if (app.lieuDejaVu) x = e.put(x, PLACE_ROW, `  ${bloc.chaines[D.MS.DEJA]}`, { inv: true });
    }
    e.padTo(x, PLACE_ROW, BORD, { inv: true });
  }

  dessinePage(e) {
    const app = this.app;
    this.barreTitre(e);
    for (let i = 0; i < app.body.length; i++) e.put(0, BODY_ROW0 + i, app.body[i]);
    this.barreLieu(e);
    if (app.combat) this.dessineCombat(e);
    else if (app.bottom.some((l) => l)) this.dessineMessages(e);
    else this.dessineChoix(e);
  }

  /* Les quatre lignes du bas quand le moteur parle : un de, un jet de
   * Chance, un refus. print_at() ecrit le texte puis comble jusqu'au bord. */
  dessineMessages(e) {
    const app = this.app;
    for (let i = 0; i < 4; i++) {
      const t = app.bottom[i] || '';
      if (i === 3) break;
      e.padTo(e.put(0, CHOICE_ROW0 + i, t), CHOICE_ROW0 + i, BORD);
    }
    e.put(0, CHOICE_ROWN, app.hint || app.msg('M_ESPACE_CONTINUER'), { clic: ' ' });
  }

  /* render_choices : deux choix par ligne quand les deux tiennent dans une
   * demi-largeur, sinon un seul sur toute la ligne -- c'est ce qui fait
   * entrer cinq choix dans quatre lignes. Ils se calent en BAS, le vide
   * reste au-dessus, contre le texte. Un choix qui exige une Pierre absente
   * du sac se voit mais ne porte pas de lettre. */
  dessineChoix(e) {
    const app = this.app;
    const cs = app.choices;
    const paire = (i) => i + 1 < cs.length
      && cs[i].title.length <= CHOICE_WIDTH - 3
      && cs[i + 1].title.length <= CHOICE_WIDTH - 3;

    let lignes = 0;
    for (let i = 0; i < cs.length; i += paire(i) ? 2 : 1) lignes++;
    if (lignes > CHOICE_ROWN - CHOICE_ROW0 + 1) lignes = CHOICE_ROWN - CHOICE_ROW0 + 1;
    let row = CHOICE_ROWN + 1 - lignes;

    let i = 0;
    while (i < cs.length && row <= CHOICE_ROWN) {
      if (paire(i)) {
        this.unChoix(e, 0, row, i);
        this.unChoix(e, CHOICE_COL2, row, i + 1);
        i += 2;
      } else {
        this.unChoix(e, 0, row, i, 75);
        i += 1;
      }
      row++;
    }
    if (!cs.length && app.hint) e.put(0, CHOICE_ROWN, app.hint, { clic: 'R' });
  }

  unChoix(e, x, row, i, large) {
    const c = this.app.choices[i];
    const libre = choiceAvailable(this.app, c);
    const lettre = libre ? String.fromCharCode(65 + i) : '-';
    const clic = libre ? String.fromCharCode(65 + i) : null;
    x = e.put(x, row, `${lettre}) `, { clic });
    e.put(x, row, large ? c.title.slice(0, large) : c.title, { clic });
  }

  /* show_fighters + put_roll + put_verdict + l'invite : les quatre lignes du
   * bas pendant un combat, aux memes colonnes que sur la machine. */
  dessineCombat(e) {
    const app = this.app, c = app.combat, f = c.foe;
    const fr = app.lang === 'FR';
    if (f) {
      /* "VOUS" tient en quatre lettres, l'adversaire pas : la colonne de
       * droite commence a 33 plutot qu'a la moitie de l'ecran. */
      let x = e.combattant(0, CHOICE_ROW0, app.msg('M_VOUS'), 12,
                           app.hero.hab, app.hero.end, app.hero.end0, fr ? 'HAB' : 'SKL');
      x = e.padTo(x, CHOICE_ROW0, 33);
      x = e.combattant(x, CHOICE_ROW0, f.name, c.rang ? 16 : 19,
                       f.hab, f.end, f.end0, fr ? 'HAB' : 'SKL');
      if (c.rang) x = e.put(x, CHOICE_ROW0, ` ${c.rang}`);
      e.padTo(x, CHOICE_ROW0, BORD);
    }
    if (c.message) e.padTo(e.put(0, CHOICE_ROW0, c.message), CHOICE_ROW0, BORD);
    if (c.jet) {
      const r = c.jet;
      e.put(0, CHOICE_ROW0 + 1, app.msg('M_ASSAUT_N', c.assaut));
      e.put(11, CHOICE_ROW0 + 1,
        `${app.msg('M_JET_VOUS')} ${r.heroD1} + ${r.heroD2} + ${r.heroForce - r.heroD1 - r.heroD2} = ${r.heroForce}`);
      e.put(11, CHOICE_ROW0 + 2,
        `${app.msg('M_JET_LUI')} ${r.monsterD1} + ${r.monsterD2} + ${r.monsterForce - r.monsterD1 - r.monsterD2} = ${r.monsterForce}`);
    }
    /* Le verdict s'ecrit A COTE du jet de la creature, pas par-dessus : les
     * deux lignes de des restent lisibles pendant que le coup porte. */
    if (c.verdict) e.padTo(e.put(40, CHOICE_ROW0 + 2, c.verdict), CHOICE_ROW0 + 2, BORD);

    let x = 0;
    const espace = fr ? 'ESPACE' : 'SPACE';
    if (c.fuiteEnCours) {
      x = e.touche(x, CHOICE_ROWN, espace, app.msg('M_K_ENCAISSER'), ' ');
      x = e.touche(x, CHOICE_ROWN, 'C', app.msg('M_K_CHANCE'), 'C');
    } else {
      x = e.touche(x, CHOICE_ROWN, espace,
        app.msg(c.premier ? 'M_K_ENGAGER'
          : (!c.pending ? 'M_K_SUIVANT' : (c.hits ? 'M_K_FRAPPER' : 'M_K_ENCAISSER'))), ' ');
      if (c.premier) x = e.touche(x, CHOICE_ROWN, 'I', app.msg('M_K_SAC'), 'I');
      if (c.fuite) x = e.touche(x, CHOICE_ROWN, 'F', app.msg('M_K_FUIR'), 'F');
      /* L'enjeu, et pas seulement la touche : le joueur pariait a l'aveugle
       * un point de CHANCE contre une blessure dont il ignorait les issues. */
      if (c.enjeu) {
        x = e.tag(x, CHOICE_ROWN, 'C', 'C');
        x = e.put(x, CHOICE_ROWN, app.msg('M_K_ENJEU', c.enjeu.cha, c.enjeu.bon, c.enjeu.mauvais), { clic: 'C' });
      }
    }
    e.padTo(x, CHOICE_ROWN, BORD);
  }

  /* ── Les ecrans modaux, peints dans la meme grille ───────────────────── */

  dessineModale(e) {
    const app = this.app, m = app.modal;
    const f = {
      sac: () => this.ecranSac(e, m),
      pierres: () => this.ecranPierres(e, m),
      carte: () => this.ecranCarte(e),
      aide: () => this.ecranAide(e),
      feuille: () => this.ecranFeuille(e),
      mort: () => this.ecranMort(e),
      sauvegardes: () => this.ecranSauvegardes(e, m),
    }[m.type];
    if (f) f();
  }

  /* show_inventory : les Pierres a gauche, les objets et les amulettes a
   * partir de la colonne 40, l'invite ligne 22. */
  ecranSac(e, m) {
    const app = this.app;
    this.barreTitre(e);
    e.put(0, 2, app.msg('M_SAC_A_DOS', app.hero.gold));
    m.shown.forEach((s, i) => {
      const lettre = String.fromCharCode(65 + i);
      const n = String(app.hero.stones[s]).padStart(2);
      const nom = R.stoneName(s, app.english).padEnd(12);
      const interdit = R.stoneUsable(s, m.inCombat) ? '' : app.msg('M_INTERDITE_EN_PLEIN');
      e.put(0, 4 + i, `${lettre}) ${n}  ${nom}  ${'NBM'['NBM'.indexOf(R.stoneKind(s))]}${interdit}`,
            { clic: lettre });
    });
    let row = 4;
    for (let i = 0; i < R.cat.hidden0; i++)
      if (R.hasObject(app.hero, i)) e.put(40, row++, `- ${R.objectName(i)}`);
    for (let i = 0; i < R.AMULET_COUNT(); i++)
      if (R.hasAmulet(app.hero, i)) e.put(40, row++, `- ${R.amuletName(i, app.english)}`);
    if (!m.shown.length) e.put(0, 4, app.msg('M_AUCUNE_PIERRE_MAGIQUE'));
    e.put(0, 22, m.note || app.msg('M_UNE_PIERRE_SE'));
    if (m.note) e.put(0, 23, app.msg('M_ESPACE_CONTINUER'), { clic: ' ' });
    else e.put(0, 23, 'ESC / I', { inv: true, clic: 'I' });
  }

  /* choose_stones : la liste ne bouge pas d'un choix a l'autre, seul le
   * compteur change -- tout repeindre a chaque prise faisait clignoter
   * l'ecran neuf fois de suite pour six Pierres. */
  ecranPierres(e, m) {
    const app = this.app;
    this.barreTitre(e);
    m.allowed.forEach((s, i) => {
      const lettre = String.fromCharCode(65 + i);
      e.put(0, 4 + i, `${lettre}) ${R.stoneName(s, app.english).padEnd(12)} ${R.stoneKind(s)}`,
            { clic: lettre });
    });
    e.put(0, CHOICE_ROW0, app.msg('M_CHOISISSEZ_PIERRES', m.reste));
    e.put(0, CHOICE_ROW0 + 1, app.msg('M_PRENDRE_UNE_PIERRE'));
  }

  ecranAide(e) {
    const app = this.app;
    this.barreTitre(e);
    (app.aide || '').split(/\r?\n/).forEach((l, i) => { if (i < CHOICE_ROW0 - 2) e.put(0, 2 + i, l); });
    e.put(0, CHOICE_ROWN, app.msg('M_ESPACE_CONTINUER'), { clic: ' ' });
  }

  ecranFeuille(e) {
    const app = this.app, c = app.hero;
    this.barreTitre(e);
    e.put(0, 3, app.msg('M_FEUILLE_D_AVENTURE'));
    e.put(0, 5, app.msg('M_HABILETE_DE', c.hab));
    e.put(0, 6, app.msg('M_ENDURANCE_DES', c.end));
    e.put(0, 7, app.msg('M_CHANCE_DE', c.cha));
    e.put(0, 9, app.msg('M_UNE_EPEE_UNE', c.gold));
    e.put(0, 10, app.msg('M_AUCUN_DE_CES'));
    e.put(0, 13, app.msg('M_ESPACE_ENTRER_DANS'), { clic: ' ' });
  }

  ecranMort(e) {
    const app = this.app;
    e.put(0, 6, app.msg('M_VOTRE_ENDURANCE_EST'));
    e.put(0, 8, app.msg('M_MORT_RECOMMENCER'), { clic: 'R' });
  }

  ecranSauvegardes(e, m) {
    const app = this.app;
    this.barreTitre(e);
    e.put(0, 2, app.msg(m.saving ? 'M_SAUVEGARDES' : 'M_CHARGEMENTS'));
    m.slots.forEach((s, i) => {
      e.put(2, 4 + i, `${i}) ${s ? `${s.date} -- p.${String(s.scene).padStart(3, '0')} ${s.titre}` : app.msg('M_VIDE')}`,
            { clic: String(i) });
    });
    e.put(0, CHOICE_ROWN, app.msg('M_ESPACE_CONTINUER'), { clic: '\x1b' });
  }

  /* show_map : la grille 6 x 9, les sentiers d'abord, les cases par-dessus,
   * et rien qui n'ait ete vu. Un sentier n'est dessine que depuis une
   * clairiere VUE, et il finit par '?' quand l'autre bout est inconnu --
   * c'est le « rayon termine par ? » du plan-modele du livre. */
  ecranCarte(e) {
    const app = this.app, carte = app.carte;
    const bloc = carte.langue[app.lang] || carte.langue.FR;
    const COL = [2, 8, 14, 20, 26, 32], ROW = [2, 4, 6, 8, 10, 12, 14, 16, 18];
    const DC = [0, 0, 1, -1], DR = [-1, 1, 0, 0], SC = [1, 1, 4, -1];
    const vu = carte.clr.map((_, i) => this.clairiereVue(i));
    const nVus = vu.filter(Boolean).length;

    let x = e.put(0, 0, ' ', { inv: true });
    x = e.put(x, 0, `${bloc.chaines[D.MS.TITRE]} -- ${nVus} ${bloc.chaines[D.MS.SUR35]}`, { inv: true });
    e.padTo(x, 0, BORD, { inv: true });
    e.put(BORD, 0, ' ', { inv: true });

    for (let i = 0; i < 6; i++) e.put(COL[i] + 1, 1, String(i));
    for (let i = 0; i < 9; i++) e.put(0, ROW[i], String(i));

    carte.clr.forEach((cl, i) => {
      if (!vu[i]) return;
      const r = ROW[cl.y], c = COL[cl.x];
      if (cl.out & 0x10) e.put(c + 1, r + 1, 'v');
      for (let d = 0; d < 4; d++) {
        if (!(cl.out & (1 << d))) continue;
        const j = D.voisin(carte, i, d);
        if (j < 0) continue;
        let n = 2;
        if (vu[j]) n = d < 2 ? Math.abs(ROW[carte.clr[j].y] - r) - 1
                             : Math.abs(COL[carte.clr[j].x] - c) - 4;
        let cc = c + SC[d], rr = r + DR[d];
        const glyphe = DC[d] ? '-' : '|';
        for (let k = n; k > 0; k--) {
          e.put(cc, rr, k > 1 || vu[j] ? glyphe : '?');
          cc += DC[d]; rr += DR[d];
        }
      }
    });
    /* Le livre veut le NUMERO DE LA CLAIRIERE sur chaque cercle ; quatre
     * lieux n'en ont pas dans la prose, ils portent un point d'interrogation.
     * Celle ou l'on se tient passe en video inverse. */
    carte.clr.forEach((cl, i) => {
      if (!vu[i]) return;
      const ici = i === app.mapHere;
      const t = (ici ? '<' : '(') + (cl.num ? String(cl.num).padStart(2) : ' ?') + (ici ? '>' : ')');
      e.put(COL[cl.x], ROW[cl.y], t, { inv: ici });
    });

    const dirs = bloc.chaines[D.MS.DIRS] || 'NSEO';
    let row = 2;
    if (app.mapHere >= 0) {
      const cl = carte.clr[app.mapHere];
      e.put(38, row++, (cl.num ? `N ${cl.num}  ` : '') + bloc.noms[app.mapHere]);
      e.put(38, row++, bloc.chaines[D.MS.SORTIES]);
      for (let d = 0; d < 4; d++) {
        if (!(cl.out & (1 << d))) continue;
        const j = D.voisin(carte, app.mapHere, d);
        const connu = j >= 0 && vu[j];
        e.put(38, row++, `  ${dirs[d]}  ${(connu ? bloc.noms[j] : '?').padEnd(12)}  ${bloc.chaines[connu ? D.MS.VUE : D.MS.INCONNUE]}`);
      }
      if (cl.out & 0x10) e.put(38, row++, `  v  ${''.padEnd(12)}  ${bloc.chaines[D.MS.HORS]}`);
    }
    e.put(38, 11, bloc.chaines[D.MS.LEGENDE]);
    for (let i = 0; i < 5; i++) e.put(40, 12 + i, bloc.chaines[D.MS.LEG1 + i]);
    e.put(38, 18, `${nVus} ${bloc.chaines[D.MS.SUR35]}`);
    e.put(0, CHOICE_ROWN, bloc.chaines[D.MS.TOUCHES], { clic: 'M' });
  }

  /* Le brouillard de guerre, deduit du seul bitmap des pages visitees : une
   * clairiere est vue des qu'UNE de ses pages l'est. */
  clairiereVue(i) {
    const app = this.app;
    return app.carte.pages.some((p) => p.clr === i && R.sceneVisited(app.mem, p.page));
  }

  /* ── Les panneaux de droite ─────────────────────────────────────────── */

  renderFeuille() {
    const app = this.app;
    /* Un jeu sans Feuille d'Aventure (SPACETRIP) n'a rien a montrer ici : le
     * cartouche disparait au lieu d'annoncer des des qui ne tomberont jamais. */
    if (this.proj.moteur.feuille === false) { this.el.feuille.hidden = true; return; }
    if (!app.heroReady) {
      this.el.feuille.innerHTML = '<div class="titre">Feuille d\'Aventure</div><div class="vide">les des ne sont pas encore jetes</div>';
      return;
    }
    const h = app.hero;
    const l = (nom, v, v0) => `<div class="carac"><span>${nom}</span><b>${v}</b><i>/${v0}</i><span class="barre2"><span style="width:${v0 ? (100 * v) / v0 : 0}%"></span></span></div>`;
    this.el.feuille.innerHTML = `<div class="titre">Feuille d'Aventure</div>
      ${l('HABILETE', h.hab, h.hab0)}${l('ENDURANCE', h.end, h.end0)}${l('CHANCE', h.cha, h.cha0)}
      <div class="menus">${h.gold} Pieces d'Or${h.weaponBonus ? ` &middot; Epee Magique +${h.weaponBonus}` : ''}</div>`;
  }

  renderPanneau() {
    const app = this.app, p = this.el.panneau;
    this.root.querySelectorAll('[data-onglet]').forEach((b) =>
      b.classList.toggle('actif', b.dataset.onglet === this.onglet));

    if (this.onglet === 'journal') {
      p.innerHTML = app.trace.length
        ? app.trace.map((t) => `<div class="trace"><code>${echap(t.jeton)}</code><span class="ligne2">${echap(t.ligne)}</span><em>${echap(t.note || '')}</em></div>`).join('')
        : '<div class="vide">aucune directive sur cette page</div>';
    } else if (this.onglet === 'source') {
      p.innerHTML = `<pre class="source">${(app.source || '').split('\n').map((l) => {
        const d = matchDirective(this.proj, l);
        return d ? `<span class="dir" title="${echap(d.aide || '')}">${echap(l)}</span>` : echap(l);
      }).join('\n')}</pre>`;
    } else if (this.onglet === 'sac') {
      p.innerHTML = this.htmlSac();
    } else {
      p.innerHTML = `<table class="dirs"><tr><th>jeton<th>3e<th>entree<th>role</tr>${
        this.proj.directives.map((d) => `<tr><td><code>${d.jeton}</code><td>${d.troisieme === ' ' ? '␣' : d.troisieme}<td>${d.effetEntree ? 'oui' : ''}<td>${echap(d.aide || '')}</tr>`).join('')}</table>`;
    }
  }

  htmlSac() {
    const app = this.app;
    if (!app.heroReady) return '<div class="vide">pas de heros</div>';
    const h = app.hero;
    const pierres = h.stones.map((n, s) => (n ? `<li>${n} &times; ${R.stoneName(s, app.english)} <em>${R.stoneKind(s)}</em></li>` : '')).join('');
    const objets = R.cat.objets.map((o, i) => (i < R.cat.hidden0 && R.hasObject(h, i) ? `<li>${echap(o.libelle)}</li>` : '')).join('');
    const drapeaux = R.cat.objets.map((o, i) => (i >= R.cat.hidden0 && R.hasObject(h, i) ? `<li><code>${echap(o.cle)}</code></li>` : '')).join('');
    const amulettes = this.proj.amulettes.map((a, i) => (R.hasAmulet(h, i) ? `<li>${echap(app.english ? a.en : a.fr)}</li>` : '')).join('');
    return `<div class="colonnes">
      <div><h4>Pierres</h4><ul>${pierres || '<li class="vide">aucune</li>'}</ul></div>
      <div><h4>Objets</h4><ul>${objets || '<li class="vide">aucun</li>'}</ul>
           <h4>Amulettes</h4><ul>${amulettes || '<li class="vide">aucune</li>'}</ul>
           <h4>Drapeaux</h4><ul>${drapeaux || '<li class="vide">aucun</li>'}</ul></div></div>`;
  }

  /* ── L'image ────────────────────────────────────────────────────────── */

  async showImage() {
    const app = this.app;
    const cles = [app.imageKey, app.imageAlt].filter(Boolean);
    const v = this.proj.images.find((x) => x.id === this.variante) || this.proj.images[0];
    /* render() repasse ici a chaque frappe : sans ce garde, chaque touche
     * relisait le flux du disque et redecodait 16 Ko pour rien. */
    const signature = v.id + '/' + cles.join(',');
    if (signature === this.imageMontree) return;
    this.imageMontree = signature;
    this.el.photo.hidden = true;
    this.el.toile.hidden = true;
    if (!cles.length) {
      this.el.imageVide.textContent = "cette page n'a pas d'illustration";
      this.el.imageEtat.textContent = '';
      return;
    }
    for (const cle of cles) {
      const id = parseInt(cle.slice(1), 10);
      if (await this.peindre(v, D.fill(this.proj, v.chemin, { img: cle, id }), cle)) return;
    }
    this.el.imageVide.textContent = `${v.nom} : ${cles.join(' / ')} absent`;
    this.el.imageEtat.textContent = 'manquant';
  }

  async peindre(v, chemin, cle) {
    if (v.type === 'png') {
      const ok = await new Promise((res) => {
        const img = this.el.photo;
        img.onload = () => res(true);
        img.onerror = () => res(false);
        img.src = D.url(chemin);
      });
      if (!ok) return false;
      this.el.photo.hidden = false;
      this.el.imageVide.textContent = '';
      this.el.imageEtat.textContent = `${cle} -- ${this.el.photo.naturalWidth}x${this.el.photo.naturalHeight}`;
      return true;
    }
    let bytes;
    try { bytes = await D.getBytes(chemin, { volume: !v.horsVolume }); } catch { return false; }
    const ctx = this.el.toile.getContext('2d');
    const img = v.type === 'hgr-brut' ? decodeRawHgr(bytes, ctx) : decodeToImageData(bytes, v.palette, ctx);
    if (!img) { this.el.imageEtat.textContent = `${cle} : flux illisible`; return false; }
    ctx.putImageData(img, 0, 0);
    this.el.toile.hidden = false;
    this.el.imageVide.textContent = '';
    const u = v.type === 'hgr-brut' ? null : paletteUsage(bytes);
    this.el.imageEtat.textContent = `${cle} -- ${bytes.length} octets`
      + (u ? `, ${u.filter((n) => n).length} couleurs` : '');
    return true;
  }
}

function echap(s) {
  return String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
