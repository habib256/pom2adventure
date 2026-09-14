/* dhgr.js -- lire les images du volume telles que la machine les lit.
 *
 * Le lecteur ne se contente pas des apercus PNG que la conversion depose a
 * cote : il DECODE le flux RLE du disque et le peint lui-meme. C'est la seule
 * facon honnete de comparer le master a ce que l'Apple II montrera -- un
 * apercu peut dater d'une conversion precedente, le flux, lui, est celui que
 * le jeu chargera.
 *
 * Portage direct de ADVKIT/TOOLS/scoswamp_dhgr.cpp (decode, preview)
 * et de pom2/src/hgrpaint/HgrPaintModel.cpp (dhgrColorAt, hgrRowAddress).
 */

/* Les deux palettes de scoswamp_dhgr.cpp. Les memes 4 bits ont deux rendus
 * materiellement differents ; le convertisseur ecrit des INDEX, pas des
 * couleurs, et garder les deux est la seule facon honnete de relire un asset
 * destine au composite ET a la Peritel. */
export const PALETTES = {
  composite: [
    [0x00,0x00,0x00],[0xa7,0x0b,0x40],[0x40,0x1c,0xf7],[0xe6,0x28,0xff],
    [0x00,0x74,0x40],[0x80,0x80,0x80],[0x19,0x90,0xff],[0xbf,0x9c,0xff],
    [0x40,0x63,0x00],[0xe6,0x6f,0x00],[0x80,0x80,0x80],[0xff,0x8b,0xbf],
    [0x19,0xd7,0x00],[0xbf,0xe3,0x08],[0x58,0xf4,0xbf],[0xff,0xff,0xff],
  ],
  chatmauve: [
    [0x00,0x00,0x00],[0xac,0x12,0x4c],[0x00,0x07,0x83],[0xaa,0x1a,0xd1],
    [0x00,0x83,0x2f],[0x9f,0x97,0x7e],[0x00,0x8a,0xb5],[0x9f,0x9e,0xff],
    [0x7a,0x5f,0x00],[0xff,0x72,0x47],[0x78,0x68,0x7f],[0xff,0x7a,0xcf],
    [0x6f,0xe6,0x2c],[0xff,0xf6,0x7b],[0x6c,0xee,0xb2],[0xff,0xff,0xff],
  ],
};

const DHGR_BYTES = 16384;   /* deux banques de 8 Ko : aux puis principale */
const HGR_BYTES  = 8192;

/* L'entrelacement HIRES : 192 lignes en trois groupes de 64, chacun par
 * blocs de 8 (Woz a reutilise le compteur de ligne pour le rafraichissement
 * DRAM). Offset relatif a la page, comme dans le modele. */
function rowBase(y) {
  return ((y / 64) | 0) * 0x28 + (((y % 64) / 8) | 0) * 0x80 + (y % 8) * 0x400;
}

/* L'octet qui porte le point `d` de la ligne : les colonnes paires viennent
 * d'une banque, les impaires de l'autre -- c'est tout le double hi-res. */
function dotOffset(d, base) {
  const byteCol = (d / 7) | 0;
  return ((byteCol & 1) ? HGR_BYTES : 0) + base + (byteCol >> 1);
}

/* Les quatre bits d'un pixel couleur, remis dans l'ordre de l'affichage :
 * dhgrNibbleToColor, une rotation d'un bit. */
export function dhgrColorAt(pair, x, y) {
  const base = rowBase(y);
  let v = 0;
  for (let i = 0; i < 4; i++) {
    const d = 4 * x + i;
    if ((pair[dotOffset(d, base)] >> (d % 7)) & 1) v |= 1 << i;
  }
  return ((v << 1) | (v >> 3)) & 0x0f;
}

/* Le RLE du volume : un en-tete de huit octets, puis des jetons. Bit 7 pose =
 * une repetition ((t & 0x7f) + 3 fois l'octet suivant), sinon un litteral de
 * (t + 1) octets. Le flux DOIT tomber juste sur la taille attendue -- une
 * image tronquee vaut mieux refusee qu'a moitie peinte. */
function rleDecode(bytes, magic, outSize) {
  const hdr = [...magic].map((c) => c.charCodeAt(0)).concat([1, 0, 0, outSize >> 8]);
  if (bytes.length < 8) return null;
  for (let i = 0; i < 8; i++) if (bytes[i] !== hdr[i]) return null;
  const raw = new Uint8Array(outSize);
  let n = 0, i = 8;
  while (n < outSize && i < bytes.length) {
    const t = bytes[i++];
    if (t & 0x80) {
      const run = (t & 0x7f) + 3;
      if (i >= bytes.length || run > outSize - n) return null;
      raw.fill(bytes[i++], n, n + run);
      n += run;
    } else {
      const run = t + 1;
      if (run > bytes.length - i || run > outSize - n) return null;
      raw.set(bytes.subarray(i, i + run), n);
      i += run; n += run;
    }
  }
  return n === outSize ? raw : null;
}

/* Le rendu HGR simple, garde pour les flux d'avant la migration DHGR : le
 * depot en contient encore dans son historique, et un lecteur qui refuse une
 * image ancienne ne dit pas ce qui cloche. */
const HGR_BANKS = [
  [[0,0,0],[0xaa,0x1a,0xd1],[0x6f,0xe6,0x2c],[255,255,255]],
  [[0,0,0],[0,0x8a,0xb5],[0xff,0x72,0x47],[255,255,255]],
];

function paintHgr(page, img) {
  const bits = new Uint8Array(280), bank = new Uint8Array(40);
  for (let y = 0; y < 192; y++) {
    const base = rowBase(y);
    for (let col = 0; col < 40; col++) {
      const b = page[base + col];
      bank[col] = b >> 7;
      for (let k = 0; k < 7; k++) bits[col * 7 + k] = (b >> k) & 1;
    }
    for (let x = 0; x < 280; x += 2) {
      const c = HGR_BANKS[bank[(x / 7) | 0]][bits[x] | (bits[x + 1] << 1)];
      for (let q = 0; q < 2; q++) {
        const o = (y * 280 + x + q) * 4;
        img.data[o] = c[0]; img.data[o+1] = c[1]; img.data[o+2] = c[2]; img.data[o+3] = 255;
      }
    }
  }
}

function paintDhgr(pair, img, palette) {
  for (let y = 0; y < 192; y++) {
    for (let x = 0; x < 140; x++) {
      const c = palette[dhgrColorAt(pair, x, y)];
      for (let q = 0; q < 2; q++) {
        const o = (y * 280 + x * 2 + q) * 4;
        img.data[o] = c[0]; img.data[o+1] = c[1]; img.data[o+2] = c[2]; img.data[o+3] = 255;
      }
    }
  }
}

/* Rend un ImageData 280x192 depuis le flux brut du disque, ou null si le flux
 * n'est ni DHRR v1 ni HGRR v1. L'appelant l'etire : les pixels DHGR ne sont
 * pas carres, et c'est le CSS qui s'en charge (image-rendering: pixelated). */
export function decodeToImageData(bytes, paletteName, ctx) {
  const img = ctx.createImageData(280, 192);
  const pair = rleDecode(bytes, 'DHRR', DHGR_BYTES);
  if (pair) { paintDhgr(pair, img, PALETTES[paletteName] || PALETTES.chatmauve); return img; }
  const page = rleDecode(bytes, 'HGRR', HGR_BYTES);
  if (page) { paintHgr(page, img); return img; }
  return null;
}

/* Le compte des couleurs reellement employees : un chiffre qui dit d'un coup
 * d'oeil si la conversion a rendu une image plate. */
export function paletteUsage(bytes) {
  const pair = rleDecode(bytes, 'DHRR', DHGR_BYTES);
  if (!pair) return null;
  const n = new Array(16).fill(0);
  for (let y = 0; y < 192; y++) for (let x = 0; x < 140; x++) n[dhgrColorAt(pair, x, y)]++;
  return n;
}

/* Une page HGR BRUTE, sans en-tete ni compression : c'est ainsi que SPACETRIP
 * range ses images (N001.HGR.BIN, 8192 octets). Le meme atelier lit les deux
 * jeux parce que le TYPE de l'image est une donnee du descripteur. */
export function decodeRawHgr(bytes, ctx) {
  if (bytes.length < HGR_BYTES) return null;
  const img = ctx.createImageData(280, 192);
  paintHgr(bytes, img);
  return img;
}
