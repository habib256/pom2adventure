/* engine.js -- le moteur : ce que la machine fait d'une page.
 *
 * Portage de load_scene(), run_combat(), run_luck_test(), run_stat_test(),
 * run_dice_roll(), choose_stones() et handle_user_input() (SCOSWAMP/SRC/
 * scoswamp.c). L'ORDRE des gestes est celui du C, parce que c'est lui qui
 * decide de ce que le joueur voit et de ce que les des donnent : le de d'une
 * ligne ED tombe avant le combat de la meme page quelle que soit la position
 * de la ligne dans le fichier, et un jet de Chance n'a pas lieu si un detour
 * (ligne V) a court-circuite la page.
 *
 * Le moteur ne touche jamais au DOM : il rend la main a `ui` pour peindre et
 * pour attendre une touche. C'est ce qui rend le meme moteur utilisable par
 * un banc d'essai sans ecran -- la suite naturelle de cet atelier.
 */

import * as R from './rules.js';
import * as D from './data.js';
import { parseScene, choiceAvailable, caracApply, CARAC_NOMS } from './scene.js';

export const ISSUE = { MORT: 0, VICTOIRE: 1, FUITE: 2, DEJA_GAGNE: 3 };

export class Engine {
  constructor(proj, ui) {
    this.proj = proj;
    this.ui = ui;
    this.app = {
      proj,
      lang: 'FR',
      english: false,
      currentScene: -1,
      pending: -1,
      restoring: false,
      heroReady: false,
      hero: R.newCharacter(),
      mem: R.newMemory(),
      /* La page en cours, remise a plat par loadScene. */
      title: null, body: [], choices: [], trace: [],
      foes: [], foeImg: [], foeCur: 0, lastLoss: 0, dvDone: false,
      revisit: -1, fleeTarget: -1, fleeAfter: 0, magicForbidden: false, winScene: -1,
      luckOk: -1, luckKo: -1, luckDok: 0, luckDko: 0,
      csCarac: 0, csOk: -1, csKo: -1,
      mbOk: -1, mbKo: -1,
      diceN: 0, diceCarac: 0,
      chooseN: 0, chooseCats: '',
      musicName: '', musicOver: false,
      /* Ce que l'ecran montre : les 4 lignes du bas, l'invite, la modale. */
      bottom: ['', '', '', ''], hint: '', modal: null, combat: null,
      imageKey: null, imageAlt: null,
      mapHere: -1, carte: null, lieuDejaVu: false, pageVolume: null,
      msg: (n, ...a) => n,
    };
  }

  /* ── Demarrage ──────────────────────────────────────────────────────── */

  async prepareLangue(lang) {
    const [cat, carte, aide] = await Promise.all([
      D.loadCatalogs(this.proj, lang),
      D.loadMap(this.proj),
      D.loadTexteEcran(this.proj, lang, 'aide'),
    ]);
    return {lang, cat, carte, aide};
  }

  applyLangue({lang, cat, carte, aide}) {
    const app = this.app;
    app.lang = lang;
    app.english = lang !== 'FR';
    R.setCatalogs({
      objets: cat.objets,
      pierres: this.proj.pierres,
      amulettes: this.proj.amulettes,
    });
    app.msg = cat.msg;
    app.messages = cat.messages;
    app.carte = carte;
    app.aide = aide;
  }

  async setLangue(lang) {
    this.applyLangue(await this.prepareLangue(lang));
  }

  async run() {
    const app = this.app;
    await this.loadScene(this.proj.moteur.pageDepart);
    for (;;) {
      if (app.pending >= 0) {
        const next = app.pending;
        app.pending = -1;
        await this.loadScene(next);
        app.restoring = false;
        continue;
      }
      /* Une page restee sans aucun choix est une fin -- mort par la prose,
       * victoire, ou combat gagne sans suite : on offre de recommencer. */
      app.hint = app.choices.length ? '' : app.msg('M_MORT_RECOMMENCER');
      this.ui.render();
      await this.handleKey(await this.ui.key());
    }
  }

  /* ── Charger une page ───────────────────────────────────────────────── */

  async loadScene(id) {
    const app = this.app;
    app.currentScene = id;
    if (app.carte) {
      const c = D.clairiereDePage(app.carte, id);
      if (c >= 0) app.mapHere = c;      /* la clairiere est COLLANTE */
    }
    app.title = null; app.body = []; app.choices = []; app.trace = [];
    app.foes = []; app.foeImg = []; app.foeCur = 0; app.dvDone = false;
    app.revisit = -1; app.fleeTarget = -1; app.fleeAfter = 0; app.magicForbidden = false; app.winScene = -1;
    app.luckOk = -1; app.luckKo = -1; app.luckDok = 0; app.luckDko = 0;
    app.csOk = -1; app.csKo = -1; app.mbOk = -1; app.mbKo = -1;
    app.diceN = 0; app.diceCarac = 0;
    app.chooseN = 0; app.chooseCats = '';
    app.musicName = ''; app.musicOver = false;
    app.bottom = ['', '', '', '']; app.hint = ''; app.combat = null;
    app.imageKey = null; app.imageAlt = null; app.source = '';
    /* lastLoss ne se remet PAS a zero : c'est la page SUIVANT le combat qui
     * la lit (lignes DV). */

    let texte;
    const chemin = D.pagePath(this.proj, app.lang, id);
    /* Quand on lit le volume, on dit si le depot a bouge depuis l'empaquetage :
     * c'est la question de l'auteur qui vient d'editer une page -- est-ce que
     * la machine la verra ? */
    D.comparerAuDepot(chemin).then((v) => { app.pageVolume = v; this.ui.render(); });
    try { texte = await D.getText(chemin); }
    catch (e) {
      app.body = [`*** Page ${id} introuvable : ${e.message}`];
      this.ui.render();
      return;
    }
    /* C'est la LECTURE du fichier qui applique les lignes E, P, G et V :
     * elles jouent une fois par visite, dans l'ordre du fichier. */
    app.source = texte;      /* l'onglet Source montre la page telle qu'elle est */
    parseScene(app, texte);

    if (app.heroReady && R.isDead(app.hero)) { await this.dieAndRestart(); return; }

    /* Deja venu : la page longue cede la place a sa version courte, sans rien
     * afficher entre les deux. Le passage n'est PAS marque. */
    if (app.revisit >= 0) { app.pending = app.revisit; return; }
    /* « deja visitee » se decide AVANT de marquer la page : sur la machine,
     * render_place() peint la ligne de lieu pendant la lecture du fichier,
     * donc avant scene_mark_visited(). Marquer d'abord aurait affiche le
     * mot des la premiere arrivee, sur toutes les pages. */
    app.lieuDejaVu = !!(app.carte && app.mapHere >= 0 &&
      app.carte.pages.some((p) => p.clr === app.mapHere && R.sceneVisited(app.mem, p.page)));
    R.sceneMarkVisited(app.mem, id);

    app.imageKey = 'N' + D.pad3(id);
    this.ui.render();

    /* Le de de la ligne ED tombe avant tout le reste : avant le jet de
     * Chance, avant le choix des Pierres, avant l'image, avant le combat. */
    if (app.diceN !== 0) {
      await this.runDiceRoll();
      if (R.isDead(app.hero)) { await this.dieAndRestart(); return; }
      app.bottom = ['', '', '', ''];
    }

    if (app.csOk >= 0) { app.pending = await this.runStatTest(); return; }
    if (app.luckOk >= 0) { app.pending = await this.runLuckTest(); return; }
    if (app.chooseN > 0) await this.chooseStones();

    if (app.foes.length) {
      app.foes.forEach(R.monsterSeal);
      app.foeCur = R.monsterEnter(app.mem, this.zoneKey(), app.foes, app.foes.length);
      if (app.foeCur < app.foes.length) this.setFoeImage();
    }
    if (!app.foes.length) { this.ui.render(); return; }

    const issue = app.foeCur < app.foes.length ? await this.runCombat() : ISSUE.DEJA_GAGNE;
    if (issue !== ISSUE.DEJA_GAGNE) R.takeObject(app.hero, R.objectFromName('.D'));
    if (issue === ISSUE.MORT) await this.dieAndRestart();
    else if (issue === ISSUE.FUITE) app.pending = app.fleeTarget;
    else if (app.winScene >= 0) app.pending = app.winScene;
    else { app.bottom = ['', '', '', '']; this.ui.render(); }
  }

  /* La memoire d'une rencontre appartient a la CLAIRIERE, pas au paragraphe :
   * fuir puis revenir par une autre page retrouve le meme adversaire blesse.
   * Les clairieres commencent a 1 -- 0 marque un emplacement libre. */
  zoneKey() {
    const app = this.app;
    return R.monsterZoneKey(app);
  }

  /* Le disque range une image de bataille par page (B<page>), mais une file
   * peut aligner trois especes : la ligne MI dit alors de quelle page
   * emprunter l'image. Sans elle, c'est celle de la page. */
  setFoeImage() {
    const app = this.app;
    const p = app.foeImg[app.foeCur] || app.currentScene;
    app.imageKey = 'B' + D.pad3(p);
    app.imageAlt = 'N' + D.pad3(app.currentScene);
  }

  /* ── Les gestes qui demandent une touche ────────────────────────────── */

  async pause(label) {
    const app = this.app;
    app.hint = label || app.msg('M_ESPACE_CONTINUER');
    this.ui.render();
    await this.ui.key();
    app.hint = '';
  }

  /* "Lancez un de et retranchez le chiffre obtenu" : le moteur joue le jet,
   * mais il le MONTRE -- un de qui tombe en coulisse ne se distingue pas
   * d'une perte seche. */
  async runDiceRoll() {
    const app = this.app;
    if (app.diceN === 3) { await this.runLuckTest(); return; }
    app.bottom = [app.msg('M_LANCEZ_LES_DES'), '', '', ''];
    await this.pause();
    let roll = R.rollD6();
    if (app.diceN > 1 || app.diceN < -1) roll += R.rollD6();
    caracApply(app.hero, app.diceCarac, app.diceN < 0 ? -roll : roll);
    app.bottom = [app.msg('M_VOUS_JETEZ', roll), '', '', ''];
    await this.pause();
  }

  /* La page ordonne un jet de Chance : il decide de la suite, il n'y a donc
   * pas de choix a offrir au joueur. */
  async runLuckTest() {
    const app = this.app;
    app.bottom = [app.msg('M_TENTEZ_VOTRE_CHANCE', app.hero.cha), '', '', ''];
    await this.pause();
    /* Le jet est releve avant d'etre applique, pour pouvoir le montrer : la
     * regle veut qu'un point de CHANCE parte a chaque tentative. */
    const roll = R.roll2D6();
    const lucky = roll <= app.hero.cha;
    app.bottom = [app.msg('M_JET_DE_CHANCE', roll, app.hero.cha), '', '', ''];
    if (app.hero.cha > 0) app.hero.cha--;
    app.bottom[1] = app.msg(lucky ? 'M_CHANCEUX' : 'M_MALCHANCEUX');
    caracApply(app.hero, app.diceN === 3 ? app.diceCarac : 0, lucky ? app.luckDok : app.luckDko);
    await this.pause();
    return lucky ? app.luckOk : app.luckKo;
  }

  /* Ligne CS : le meme geste qu'un jet de Chance, mais contre la
   * caracteristique nommee et sans depenser de point de CHANCE. */
  async runStatTest() {
    const app = this.app;
    app.bottom = [app.msg('M_LANCEZ_LES_DES'), '', '', ''];
    await this.pause();
    const roll = R.roll2D6();
    const contre = [app.hero.end, app.hero.hab, app.hero.cha][app.csCarac] ?? app.hero.cha;
    app.bottom = [app.msg('M_JET_CONTRE', roll, contre), '', '', ''];
    await this.pause();
    return roll <= contre ? app.csOk : app.csKo;
  }

  /* "Vous choisirez ces six Pierres dans la liste" -- un bon sorcier ne donne
   * pas de Pierre malefique, un mauvais pas de Pierre benefique, et l'on a le
   * droit de prendre plusieurs fois la meme. */
  async chooseStones() {
    const app = this.app;
    const allowed = [];
    this.proj.pierres.forEach((p, s) => {
      if (app.chooseCats.includes(p.categorie)) allowed.push(s);
    });
    if (!allowed.length) { app.chooseN = 0; return; }
    while (app.chooseN > 0) {
      app.modal = { type: 'pierres', allowed, reste: app.chooseN };
      this.ui.render();
      const key = await this.ui.key();
      if (key === '\x00') { app.chooseN = 0; break; }
      const i = key.charCodeAt(0) - 65;
      if (i >= 0 && i < allowed.length) {
        R.giveStone(app.hero, allowed[i], 1);
        app.chooseN--;
      }
    }
    app.modal = null;
  }

  /* ── Un combat ──────────────────────────────────────────────────────────
   * Rend MORT, VICTOIRE ou FUITE. La structure est celle de run_combat : une
   * touche par assaut, la blessure annoncee puis encaissee, et la Chance
   * choisie APRES avoir vu qui a touche -- c'est l'ordre du livre. */
  async runCombat() {
    /* Le bandeau de combat s'efface a la sortie, quelle qu'elle soit : la
     * mort, la fuite et la victoire rendent la main a un autre ecran, et un
     * bandeau qui survit a son combat ferait croire qu'il dure encore. */
    try { return await this.combatBoucle(); }
    finally { this.app.combat = null; }
  }

  async combatBoucle() {
    const app = this.app;
    let remaining = app.fleeAfter;
    let assaut = 0, pending = false, hits = false, r = null;
    let wgood = 0, wbad = 0;
    app.lastLoss = 0;

    const foe = () => app.foes[app.foeCur];
    /* Ce que l'ecran doit peindre d'un combat, en clair : le bandeau des deux
     * combattants, le jet du dernier assaut, le verdict, l'enjeu de la
     * Chance. C'est l'ecran qui les met en page -- aux colonnes exactes de
     * show_fighters() et de put_roll(). */
    app.combat = { assaut: 0, jet: null, verdict: '', message: '' };

    for (;;) {
      const c = app.combat;
      c.assaut = assaut;
      c.foe = foe();
      c.rang = app.foes.length > 1 ? `${app.foeCur + 1}/${app.foes.length}` : '';
      c.pending = pending;
      c.hits = hits;
      c.enjeu = pending && app.hero.cha ? { cha: app.hero.cha, bon: wgood, mauvais: wbad } : null;
      c.premier = assaut === 0;
      c.fuite = app.fleeTarget >= 0 && remaining === 0;
      this.ui.render();

      const key = await this.ui.key();
      /* Le banc d'essai peut poser le joueur ailleurs en plein combat : on
       * sort sans appliquer quoi que ce soit, la page demandee est deja en
       * attente. */
      if (key === '\x00') { app.combat = null; return ISSUE.DEJA_GAGNE; }
      if (key === 'I') {
        if (await this.showInventory(app.magicForbidden ? 2 : assaut !== 0)) return ISSUE.MORT;
        continue;
      }
      if (key === 'M') { await this.openMap(); continue; }
      if (key === 'F' && c.fuite) {
        c.message = app.msg('M_VOUS_FUYEZ_ELLE');
        c.jet = null;
        c.enjeu = { cha: app.hero.cha, bon: foe().damage - 1, mauvais: foe().damage + 1 };
        c.fuiteEnCours = true;
        this.ui.render();
        const k2 = await this.ui.key();
        const useLuck = k2 === 'C' && app.hero.cha > 0;
        const lucky = R.combatFlee(app.hero, foe(), useLuck);
        if (useLuck) c.verdict = app.msg(lucky ? 'M_CHANCEUX' : 'M_MALCHANCEUX');
        /* La creature blessee garde son ENDURANCE entamee. */
        R.monsterRemember(app.mem, this.zoneKey(), app.foeCur, foe());
        c.fuiteEnCours = false;
        await this.pause();
        return R.isDead(app.hero) ? ISSUE.MORT : ISSUE.FUITE;
      }
      const useLuck = pending && app.hero.cha > 0 && key === 'C';
      if (!useLuck && key !== ' ' && key !== '\r') continue;

      /* Encaisser la blessure en attente, puis enchainer : c'est ce qui fait
       * tenir un assaut en une seule frappe. */
      if (pending) {
        pending = false;
        if (remaining) remaining--;
        const endIn = app.hero.end;
        const lucky = R.combatApply(app.hero, foe(), r, useLuck);
        app.lastLoss += Math.max(0, endIn - app.hero.end);
        if (useLuck) {
          c.verdict = app.msg(lucky ? 'M_CHANCEUX' : 'M_MALCHANCEUX');
          c.pending = false;
          await this.pause();
        }
        if (R.monsterIsBeaten(foe())) {
          c.verdict = app.msg('M_S_EFFONDRE', foe().name);
          c.pending = false;
          app.foeCur++;
          R.monsterRemember(app.mem, this.zoneKey(), app.foeCur,
                            app.foes[Math.min(app.foeCur, app.foes.length - 1)]);
          await this.pause();
          if (app.foeCur >= app.foes.length) {
            /* "Evaluez vos blessures" : la page d'apres peut brancher sur ce
             * que le combat a coute (lignes DV). */
            return ISSUE.VICTOIRE;
          }
          assaut = 0;              /* les pierres de caracteristique redeviennent permises */
          c.verdict = '';
          this.setFoeImage();
          continue;
        }
        if (R.isDead(app.hero)) {
          R.monsterRemember(app.mem, this.zoneKey(), app.foeCur, foe());
          return ISSUE.MORT;
        }
        /* Duel au premier sang : la blessure vient d'etre encaissee, le
         * combat s'arrete la et la suite dit QUI a touche. */
        if (app.mbOk >= 0) {
          app.winScene = hits ? app.mbOk : app.mbKo;
          await this.pause();
          return ISSUE.VICTOIRE;
        }
      }

      /* L'assaut suivant : les des d'abord, le verdict apres. */
      assaut++;
      r = R.combatRound(app.hero, foe());
      hits = r.outcome === R.ROUND_HERO_HITS;
      c.assaut = assaut;
      c.jet = r;
      c.message = '';
      if (r.outcome === R.ROUND_DODGE) { if (remaining) remaining--; c.verdict = app.msg('M_VOUS_AVEZ_CHACUN'); continue; }
      /* "chaque blessure coute 2 points d'ENDURANCE" -- sauf aux creatures
       * dont la page dit autrement (ligne MD). On annonce la perte seche ; la
       * Chance peut encore la changer, et la jauge dira le vrai. */
      let hurt;
      if (hits) { hurt = 2; wgood = 4; wbad = 1; }
      else { hurt = foe().damage; wgood = hurt - 1; wbad = hurt + 1; }
      c.verdict = app.msg(hits ? 'M_VOUS_L_AVEZ' : 'M_ELLE_VOUS_A') + app.msg('M_DEGATS', hurt);
      pending = true;
    }
  }

  /* ── Les ecrans modaux ──────────────────────────────────────────────── */

  async showInventory(inCombat) {
    const app = this.app;
    try {
    while (!app.heroReady || !R.isDead(app.hero)) {
      const shown = [];
      app.hero.stones.forEach((n, s) => { if (n) shown.push(s); });
      app.modal = { type: 'sac', shown, inCombat, note: '' };
      this.ui.render();
      const key = await this.ui.key();
      if (key === '\x1b' || key === 'I' || key === '\x00') break;
      const i = key.charCodeAt(0) - 65;
      if (i < 0 || i >= shown.length) continue;
      const s = shown[i];
      const issue = R.stoneUse(app.hero, s, inCombat);
      app.modal.note = issue === R.STONE_USE_FORBIDDEN ? app.msg(inCombat === 2 ? 'M_PIERRE_ABSENTE' : 'M_LE_PREMIER_COUP')
                     : issue === R.STONE_USE_NONE ? app.msg('M_PIERRE_ABSENTE')
                     : app.msg('M_LA_PIERRE_DE', R.stoneName(s, app.english));
      this.ui.render();
      await this.ui.key();
    }
    return app.heroReady && R.isDead(app.hero);
    } finally { app.modal = null; }
  }

  /* [M] hors de l'Anneau de Cuivre : refus, avec la phrase du livre. « les
   * boussoles elles-memes en perdent le nord » -- l'Anneau est ce qui
   * AUTORISE la carte, et c'est ce qui donne son prix a la page 049. */
  async openMap() {
    const app = this.app;
    if (!app.carte) return false;
    const anneau = R.objectFromName(this.proj.objetsSpeciaux.anneauBoussole);
    if (!R.hasObject(app.hero, anneau)) {
      app.bottom = [app.carte.langue[app.lang].chaines[D.MS.ANNEAU], '', '', ''];
      await this.pause();
      app.bottom = ['', '', '', ''];
      return false;
    }
    app.modal = { type: 'carte' };
    this.ui.render();
    for (;;) {
      const key = await this.ui.key();
      if (key === '\x1b' || key === 'M' || key === '\x00') break;
    }
    app.modal = null;
    return true;
  }

  async showHelp() {
    this.app.modal = { type: 'aide' };
    this.ui.render();
    await this.ui.key();
    this.app.modal = null;
  }

  /* ── La creation du personnage, la mort, les sauvegardes ────────────── */

  async rollCharacter() {
    const app = this.app;
    R.characterRoll(app.hero);
    app.heroReady = true;
    app.modal = { type: 'feuille' };
    this.ui.render();
    await this.ui.key();
    app.modal = null;
  }

  async dieAndRestart() {
    const app = this.app;
    for (;;) {
      app.modal = { type: 'mort' };
      this.ui.render();
      const key = await this.ui.key();
      if (key === '\x00') { app.modal = null; return; }
      if (key === 'R') break;
      if (key === 'L' && await this.showSaves(false)) { app.modal = null; return; }
    }
    app.modal = null;
    app.mem = R.newMemory();
    app.mapHere = -1;
    app.heroReady = false;
    app.pending = this.proj.moteur.pageDepart;
  }

  /* Dix emplacements dans le stockage du navigateur. L'instantane porte tout
   * l'etat -- la Feuille, les deux memoires et la graine des des -- de sorte
   * qu'une partie reprise rejoue exactement la meme suite de jets. */
  slotKey(i) { return `${this.proj.id}.save.${i}`; }

  saveGame(i) {
    const app = this.app;
    localStorage.setItem(this.slotKey(i), JSON.stringify({
      titre: app.title || '', scene: app.currentScene, lang: app.lang,
      hero: app.hero, heroReady: app.heroReady,
      visited: Array.from(app.mem.visited), seen: app.mem.seen,
      mapHere: app.mapHere, lastLoss: app.lastLoss, dice: R.diceStateGet(),
      date: new Date().toISOString().slice(0, 16).replace('T', ' '),
    }));
  }

  readSave(i) {
    try {
      const s = JSON.parse(localStorage.getItem(this.slotKey(i)));
      const integer = (v, min = 0, max = Number.MAX_SAFE_INTEGER) =>
        Number.isSafeInteger(v) && v >= min && v <= max;
      const bytes = (v, n) => Array.isArray(v) && v.length === n &&
        v.every(x => integer(x, 0, 255));
      if (!s || !integer(s.scene, 0, this.proj.moteur.pageMax) ||
          !['FR', 'EN'].includes(s.lang) || typeof s.heroReady !== 'boolean' ||
          !s.hero || !bytes(s.hero.stones, this.app.hero.stones.length) ||
          !bytes(s.visited, this.app.mem.visited.length) ||
          !Array.isArray(s.seen) || s.seen.length !== R.MONSTER_SLOTS ||
          !s.seen.every(m => m && integer(m.scene, 0, 65535) &&
            integer(m.index, 0, 255) && integer(m.end, 0, 255)) ||
          !integer(s.mapHere, -1, 254) || !integer(s.dice, 0, 0xffffffff) ||
          (s.lastLoss !== undefined && !integer(s.lastLoss, 0, 255))) return null;
      for (const k of ['hab', 'hab0', 'end', 'end0', 'cha', 'cha0', 'gold']) {
        if (!integer(s.hero[k])) return null;
      }
      if (!integer(s.hero.weaponBonus, -128, 127) ||
          !integer(s.hero.objects, -0x80000000, 0xffffffff) ||
          !integer(s.hero.amulets, -0x80000000, 0xffffffff)) return null;
      return s;
    } catch { return null; }
  }

  async loadGame(i) {
    const s = this.readSave(i);
    if (!s) return false;
    // Prepare migrations on the detached snapshot: a bad rule must not
    // leave the active hero and memories partially replaced.
    const mem = {visited: Uint8Array.from(s.visited), seen: s.seen};
    let language;
    try {
      R.migrateSavedFlags(s.hero, mem, this.proj.rules);
      language = await this.prepareLangue(s.lang);
    }
    catch { return false; }
    const app = this.app;
    this.applyLangue(language);
    app.hero = s.hero;
    app.heroReady = s.heroReady;
    app.mem = mem;
    app.mapHere = s.mapHere;
    app.lastLoss = s.lastLoss || 0;
    R.diceStateSet(s.dice);
    app.restoring = true;      /* ne pas rejouer les effets d'entree */
    app.pending = s.scene;
    return true;
  }

  async showSaves(saving) {
    const app = this.app;
    for (;;) {
      const slots = [];
      for (let i = 0; i < 10; i++) {
        slots.push(this.readSave(i));
      }
      app.modal = { type: 'sauvegardes', saving, slots };
      this.ui.render();
      const key = await this.ui.key();
      if (key === '\x1b' || key === '\x00' || key === (saving ? 'S' : 'L')) { app.modal = null; return false; }
      const i = key.charCodeAt(0) - 48;
      if (i < 0 || i > 9) continue;
      if (saving) { this.saveGame(i); app.modal = null; return false; }
      if (await this.loadGame(i)) { app.modal = null; return true; }
    }
  }

  /* ── Les touches, hors combat ───────────────────────────────────────── */

  async handleKey(key) {
    const app = this.app;
    if (key === 'I') {
      if (await this.showInventory(false)) await this.dieAndRestart();
      return;
    }
    if (key === 'H') { await this.showHelp(); return; }
    if (key === 'M') { await this.openMap(); return; }
    if (key === 'S' || key === 'L') { await this.showSaves(key === 'S'); return; }
    if (key === 'R' && !app.choices.length) {
      app.mem = R.newMemory();
      app.mapHere = -1;
      app.heroReady = false;
      app.pending = this.proj.moteur.pageDepart;
      return;
    }
    if (key >= 'A' && key <= 'Z') await this.takeChoice(key.charCodeAt(0) - 65);
  }

  async takeChoice(n) {
    const app = this.app;
    const c = app.choices[n];
    if (!c) return;
    if (!choiceAvailable(app, c)) {
      /* On ne lance pas un sort qu'on n'a pas. */
      app.bottom = [app.msg('M_PIERRE_ABSENTE'), '', '', ''];
      await this.pause();
      app.bottom = ['', '', '', ''];
      return;
    }
    /* La Pierre exigee se desintegre en servant ; celle qu'offre le choix
     * change de main avant le saut. */
    if (c.require < R.STONE_COUNT()) R.stoneUse(app.hero, c.require, false);
    if (c.grant < R.STONE_COUNT()) R.giveStone(app.hero, c.grant, 1);
    if (c.objMode === 3) R.takeObject(app.hero, c.object);
    /* Le premier choix de l'introduction lance la creation : le joueur
     * comprend d'abord qui il va incarner, puis les des produisent sa
     * Feuille d'Aventure avant l'entree au Marais. */
    /* Un jeu sans Feuille d'Aventure -- SPACETRIP n'en a pas -- ne jette
     * aucun de : le descripteur le dit, le moteur n'a pas a le deviner. */
    if (!app.heroReady && this.proj.moteur.feuille !== false) await this.rollCharacter();
    app.pending = c.scene;
  }

  /* ── Le banc d'essai : se poser n'importe ou ────────────────────────── */

  gotoPage(id) { this.app.pending = id; this.ui.resume(); }
}
