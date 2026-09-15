/* prodos.js -- lire le volume ProDOS, c'est-a-dire LES OCTETS QUE LA MACHINE
 * DEMARRE.
 *
 * L'atelier ne doit pas lire « a peu pres » les memes donnees que l'Apple II :
 * il doit lire les memes. L'arborescence du depot est ce qu'on EDITE ; le
 * volume `dist/SCOSWAMP.HDV` est ce que la machine LIT, et les deux peuvent
 * diverger d'une page pendant qu'on travaille. Ce module ouvre le volume tel
 * quel et en sort les fichiers, avec les memes noms que ceux que fopen()
 * demande la-bas -- "N001" et non "N001.TXT", "MAP" et non "MAP.BIN".
 *
 * Format : blocs de 512 octets en ordre ProDOS (c'est ce qu'est un .HDV), le
 * catalogue du volume au bloc 2, treize entrees de 39 octets par bloc de
 * catalogue derriere un chainage de quatre octets. Voir « Beneath Apple
 * ProDOS », ch. 4.
 */

const TAILLE_BLOC = 512;
const ENTREE = 0x27;          /* 39 octets par entree de catalogue */
const PAR_BLOC = 13;

/* Les types de rangement, dans l'octet de tete de chaque entree. */
const SEEDLING = 1, SAPLING = 2, TREE = 3, SOUS_REP = 0x0d, ENTETE_REP = 0x0e, ENTETE_VOL = 0x0f;

export class VolumeProDOS {
  constructor(octets) {
    this.o = octets;
    this.fichiers = new Map();   /* CHEMIN MAJUSCULE -> {bloc, type, taille, rangement} */
    this.nom = '';
    this.indexer();
  }

  bloc(n) { return this.o.subarray(n * TAILLE_BLOC, (n + 1) * TAILLE_BLOC); }
  u16(b, i) { return b[i] | (b[i + 1] << 8); }

  indexer() {
    const tete = this.bloc(2);
    if ((tete[4] >> 4) !== ENTETE_VOL) throw new Error('ce fichier n\'est pas un volume ProDOS');
    this.nom = this.nomDe(tete, 4);
    this.parcourir(2, '');
  }

  nomDe(b, off) {
    const n = b[off] & 0x0f;
    let s = '';
    for (let i = 1; i <= n; i++) s += String.fromCharCode(b[off + i]);
    return s;
  }

  /* Un catalogue : une chaine de blocs, chacun precede de ses deux liens. La
   * premiere entree du premier bloc est l'en-tete (du volume ou du
   * repertoire), elle ne decrit aucun fichier. */
  parcourir(premier, prefixe) {
    let n = premier, garde = 0;
    while (n && garde++ < 4096) {
      const b = this.bloc(n);
      for (let i = 0; i < PAR_BLOC; i++) {
        const off = 4 + i * ENTREE;
        const rangement = b[off] >> 4;
        if (rangement === 0 || rangement === ENTETE_VOL || rangement === ENTETE_REP) continue;
        const nom = this.nomDe(b, off);
        const chemin = prefixe ? `${prefixe}/${nom}` : nom;
        const cle = this.u16(b, off + 0x11);
        if (rangement === SOUS_REP) { this.parcourir(cle, chemin); continue; }
        this.fichiers.set(chemin.toUpperCase(), {
          chemin,
          rangement,
          bloc: cle,
          type: b[off + 0x10],
          taille: b[off + 0x15] | (b[off + 0x16] << 8) | (b[off + 0x17] << 16),
        });
      }
      n = this.u16(b, 2);
    }
  }

  /* Les trois rangements de ProDOS : le fichier tient dans un bloc, dans un
   * bloc d'index de 256 entrees, ou dans un index d'index. Les numeros de
   * bloc y sont eclates -- octets de poids faible dans la premiere moitie du
   * bloc, poids forts dans la seconde. Un numero nul est un trou : ProDOS
   * rend des zeros, et nous aussi. */
  blocsDe(f) {
    if (f.rangement === SEEDLING) return [f.bloc];
    const lireIndex = (n) => {
      const b = this.bloc(n);
      const l = [];
      for (let i = 0; i < 256; i++) l.push(b[i] | (b[256 + i] << 8));
      return l;
    };
    if (f.rangement === SAPLING) return lireIndex(f.bloc);
    const sortie = [];
    for (const idx of lireIndex(f.bloc)) {
      if (!idx) { for (let i = 0; i < 256; i++) sortie.push(0); continue; }
      sortie.push(...lireIndex(idx));
    }
    return sortie;
  }

  lire(chemin) {
    const f = this.fichiers.get(String(chemin).toUpperCase());
    if (!f) return null;
    const sortie = new Uint8Array(f.taille);
    let ecrit = 0;
    for (const n of this.blocsDe(f)) {
      if (ecrit >= f.taille) break;
      const reste = Math.min(TAILLE_BLOC, f.taille - ecrit);
      if (n) sortie.set(this.bloc(n).subarray(0, reste), ecrit);
      ecrit += reste;
    }
    return sortie;
  }

  liste() { return [...this.fichiers.values()].map((f) => f.chemin).sort(); }
}

/* Le nom que la machine demande a fopen(), deduit du chemin du depot :
 * l'empaqueteur pose le contenu du dossier du jeu a la racine du volume et
 * retire l'extension -- "SCOSWAMP/TEXTFR/N000/N001.TXT" devient
 * "TEXTFR/N000/N001", "SCOSWAMP/DHGR/N000/N012.RLE.BIN" devient
 * "IMG/N000/N012.RLE", "SCOSWAMP/MAP.BIN" devient "MAP".
 *
 * ProDOS n'admet que 15 caracteres et pas de point de plus : c'est la regle
 * de build_prodos_volume, et enter_asset_dir/build_paths la supposent. */
export function cheminVolume(cheminDepot, racine) {
  let p = String(cheminDepot);
  if (racine && p.startsWith(racine)) p = p.slice(racine.length);
  return p.replace(/\.(TXT|BIN)$/i, '');
}
