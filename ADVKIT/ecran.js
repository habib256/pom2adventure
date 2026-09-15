/* ecran.js -- l'ecran de la machine : 80 x 24 cellules, chacune avec son
 * attribut de video inverse.
 *
 * Une chaine HTML ne suffit pas. Sur l'Apple II la video inverse n'est pas un
 * caractere mais un MODE : `revers(1)` puis des espaces, c'est le seul pave
 * plein dont dispose la machine, et c'est de quoi sont faites les jauges de
 * combat, les noms des combattants, les touches de l'invite et les deux
 * barres. Pour que les barres du navigateur soient LES MEMES, il faut le meme
 * modele : une grille de cellules qui portent chacune leur attribut.
 *
 * Les primitives ci-dessous sont celles de scoswamp.c -- gotoxy/cputs,
 * pad_to, put_gauge, put_tag, put_key -- avec leurs bornes : on ne remplit
 * jamais jusqu'a 80 quand le C s'arrete a 79, parce que la derniere cellule
 * de l'ecran ferait defiler la page.
 */

export class Ecran {
  constructor(cols = 80, rows = 24) {
    this.cols = cols;
    this.rows = rows;
    this.c = [];      /* le caractere */
    this.inv = [];    /* la video inverse */
    this.clic = [];   /* la touche que cette cellule envoie, si on la clique */
    this.effacer();
  }

  /* wipe() : 24 lignes d'espaces. */
  effacer() {
    for (let y = 0; y < this.rows; y++) {
      this.c[y] = new Array(this.cols).fill(' ');
      this.inv[y] = new Array(this.cols).fill(false);
      this.clic[y] = new Array(this.cols).fill(null);
    }
  }

  /* gotoxy(x, y) + cputs(texte). Rend la colonne d'arrivee, comme wherex(). */
  put(x, y, texte, o = {}) {
    if (y < 0 || y >= this.rows) return x;
    const s = String(texte ?? '');
    for (let i = 0; i < s.length && x + i < this.cols; i++) {
      this.c[y][x + i] = s[i];
      this.inv[y][x + i] = !!o.inv;
      this.clic[y][x + i] = o.clic ?? null;
    }
    return Math.min(x + s.length, this.cols);
  }

  /* pad_to(col) : comble d'espaces jusqu'a la colonne demandee -- exclue,
   * comme dans le C. C'est la moitie de la recette contre le clignotement,
   * et ici c'est ce qui donne aux barres leur longueur exacte. */
  padTo(x, y, col, o = {}) {
    while (x < col && x < this.cols) {
      this.c[y][x] = ' ';
      this.inv[y][x] = !!o.inv;
      this.clic[y][x] = o.clic ?? null;
      x++;
    }
    return x;
  }

  /* put_gauge : "[####------]" ou les pleins sont des espaces en video
   * inverse. Arrondi vers le HAUT -- tant qu'il reste un point d'ENDURANCE,
   * il reste une case, sinon la creature paraitrait morte un assaut trop
   * tot. */
  jauge(x, y, v, v0) {
    let n = (!v0 || !v) ? 0 : Math.floor((v * 10 + v0 - 1) / v0);
    if (n > 10) n = 10;
    x = this.put(x, y, '[');
    x = this.padTo(x, y, x + n, { inv: true });
    x = this.put(x, y, '-'.repeat(10 - n));
    return this.put(x, y, ']');
  }

  /* put_tag : la touche seule, en video inverse comme la barre de titre.
   * Entre crochets l'oeil devait chercher ; en inverse il accroche. */
  tag(x, y, cle, clic) {
    return this.put(x, y, ` ${cle} `, { inv: true, clic });
  }

  /* put_key : une touche et son verbe. */
  touche(x, y, cle, libelle, clic) {
    x = this.tag(x, y, cle, clic);
    return this.put(x, y, ` ${libelle}   `, { clic });
  }

  /* put_fighter : un demi-bandeau de combattant -- nom en inverse,
   * HABILETE, jauge, points. Sous cinq points le compte passe en inverse :
   * la machine ne fait pas de rouge en 80 colonnes, et l'inverse est le seul
   * cri dont elle dispose. */
  combattant(x, y, nom, nmax, hab, end, end0, etiquetteHab) {
    x = this.put(x, y, String(nom).slice(0, nmax), { inv: true });
    x = this.put(x, y, ` ${etiquetteHab} ${hab} `);
    x = this.jauge(x, y, end, end0);
    return this.put(x, y, ` ${end}/${end0}`, { inv: end < 5 });
  }

  /* Le rendu : une ligne par div, les cellules voisines de meme attribut
   * regroupees en un seul span. */
  html() {
    const sortie = [];
    for (let y = 0; y < this.rows; y++) {
      let ligne = '', i = 0;
      while (i < this.cols) {
        const inv = this.inv[y][i], clic = this.clic[y][i];
        let j = i;
        let t = '';
        while (j < this.cols && this.inv[y][j] === inv && this.clic[y][j] === clic) {
          t += this.c[y][j]; j++;
        }
        const cls = (inv ? 'inv' : '') + (clic !== null ? ' cliquable' : '');
        ligne += cls.trim()
          ? `<span class="${cls.trim()}"${clic !== null ? ` data-clic="${echapAttr(clic)}"` : ''}>${echap(t)}</span>`
          : echap(t);
        i = j;
      }
      sortie.push(`<div class="ligne">${ligne}</div>`);
    }
    return sortie.join('');
  }
}

function echap(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
}
function echapAttr(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
