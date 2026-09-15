#!/usr/bin/env python3
"""Mesure la qualite d'une image DHGR : son master, sa conversion, ou les deux.

    image_quality.py measure --master M.png [--rle X.RLE.BIN] [--recipe R.json] [--json]
    image_quality.py worst [--count 10] [--sort dE|ssim|isolated|palette|gray] [NOMS...]
    image_quality.py check M.png [--rle X.RLE.BIN] [--min-palette 80] [--max-isolated 4.5]

Quatre mesures, reprises de l'audit du 2026-09-14 :

  palette   % des pixels du master a moins de 10 dE (CIELAB) d'une des 16
            couleurs DHGR. Echantillon au plus proche 378x260 du master entier.
            C'est ce qui predit l'erreur de conversion (correlation 0,99).
  isolated  % des pixels 140x192 de la conversion dont les quatre voisins ont
            une autre couleur : le mouchetis.
  ssim      SSIM de la luminance L* de la conversion contre le master ramene a
            140x192 par moyenne de zone en lumiere lineaire (cadrage de la
            recette et bandes 35:24 compris).
  gray      % des pixels de la conversion sur les deux gris de la palette.
  dE        ecart moyen conversion / master 140x192, en dE CIELAB.

Sans --rle, la conversion est faite par `scoswamp_dhgr convert` dans un dossier
temporaire : c'est celle qu'obtiendrait convert_images.sh sans recette.

`check` rend 0 si le master tient les seuils, 1 sinon, 2 sur erreur. Les seuils
par defaut se reglent par IMAGE_MIN_PALETTE et IMAGE_MAX_ISOLATED. La derniere
colonne imprimee, `ecart`, somme les depassements relatifs (0 dans les seuils) :
generate_images.sh s'en sert pour garder le moins mauvais de plusieurs essais.

Dependances : numpy et Pillow (presents dans /usr/bin/python3 sur macOS).
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit('image_quality.py : numpy et Pillow requis (essayer /usr/bin/python3)')

ROOT = Path(__file__).resolve().parents[2]
CONVERTER = Path(__file__).resolve().parent / 'build/scoswamp_dhgr'
MIN_PALETTE = float(os.environ.get('IMAGE_MIN_PALETTE', '80'))
MAX_ISOLATED = float(os.environ.get('IMAGE_MAX_ISOLATED', '4.5'))

# Palette composite de scoswamp_dhgr.cpp (kPaletteComposite), indices du flux.
PAL = np.array([(0x00,0x00,0x00),(0xa7,0x0b,0x40),(0x40,0x1c,0xf7),(0xe6,0x28,0xff),
    (0x00,0x74,0x40),(0x80,0x80,0x80),(0x19,0x90,0xff),(0xbf,0x9c,0xff),
    (0x40,0x63,0x00),(0xe6,0x6f,0x00),(0x80,0x80,0x80),(0xff,0x8b,0xbf),
    (0x19,0xd7,0x00),(0xbf,0xe3,0x08),(0x58,0xf4,0xbf),(0xff,0xff,0xff)], float)
GRAYS = (5, 10)


def s2l(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin2lab(lin):
    m = np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116*f[...,1]-16, 500*(f[...,0]-f[...,1]), 200*(f[...,1]-f[...,2])], -1)


PAL_LAB = lin2lab(s2l(PAL))


def decode_raw(raw):
    """16 384 octets aux+main -> indices 192x140, meme convention que dhgrColorAt."""
    if len(raw) != 16384:
        raise ValueError('page DHGR de 16384 octets attendue')
    page = np.frombuffer(bytes(raw), np.uint8)
    y = np.arange(192)
    base = (y // 64) * 0x28 + ((y % 64) // 8) * 0x80 + (y % 8) * 0x400
    col = np.arange(80)
    off = (base[:, None] + col[None, :] // 2) + np.where(col & 1, 8192, 0)[None, :]
    bits = (page[off][..., None] >> np.arange(7)) & 1           # 192x80x7
    bits = bits.reshape(192, 560).reshape(192, 140, 4)
    v = bits[..., 0] | (bits[..., 1] << 1) | (bits[..., 2] << 2) | (bits[..., 3] << 3)
    return (((v << 1) | (v >> 3)) & 15).astype(np.uint8)


def decode_rle(blob):
    """Flux DHRR v1 -> indices 192x140. Refuse un flux tronque ou trop long."""
    if blob[:8] != b'DHRR\x01\x00\x00\x40':
        raise ValueError('flux DHRR v1 attendu')
    raw = bytearray(); i = 8
    while i < len(blob) and len(raw) < 16384:
        t = blob[i]; i += 1
        if t & 0x80:
            if i >= len(blob): raise ValueError('flux DHRR tronque')
            raw += bytes([blob[i]]) * ((t & 0x7f) + 3); i += 1
        else:
            if i + t + 1 > len(blob): raise ValueError('flux DHRR tronque')
            raw += blob[i:i + t + 1]; i += t + 1
    if len(raw) != 16384 or i != len(blob):
        raise ValueError('flux DHRR de taille invalide')
    return decode_raw(raw)


def reference(master, recipe=None):
    """Master ramene a 140x192 en lumiere lineaire, par moyenne de zone."""
    im = master.convert('RGB')
    w, h = im.size
    if recipe is not None:
        im = im.crop(tuple(recipe.get('crop') or (0, 0, w, h)))
        cw, ch = im.size
        if not recipe.get('stretch'):
            pw = max(cw, (ch * 35 + 23) // 24); ph = max(ch, (cw * 24 + 34) // 35)
            canvas = Image.new('RGB', (pw, ph)); canvas.paste(im, ((pw - cw) // 2, (ph - ch) // 2))
            im = canvas
    lin = s2l(np.asarray(im, float))
    # Deux temps, comme l'audit : 560x768 (4x4 sous-cellules), puis moyenne par cellule.
    chans = [np.asarray(Image.fromarray(lin[..., c].astype(np.float32)).resize((560, 768), Image.BOX))
             for c in range(3)]
    return np.stack(chans, -1).reshape(192, 4, 140, 4, 3).mean((1, 3))


def palette_pct(master):
    small = np.asarray(master.convert('RGB').resize((378, 260), Image.NEAREST), float)
    d = np.linalg.norm(lin2lab(s2l(small))[..., None, :] - PAL_LAB[None, None], axis=-1).min(-1)
    return float((d < 10).mean() * 100)


def isolated_pct(idx):
    nb = np.stack([np.roll(idx, 1, 0), np.roll(idx, -1, 0), np.roll(idx, 1, 1), np.roll(idx, -1, 1)])
    iso = (nb != idx[None]).all(0)
    iso[0, :] = iso[-1, :] = iso[:, 0] = iso[:, -1] = False
    return float(iso.mean() * 100)


def boxblur(a, r):
    k = 2 * r + 1
    p = np.pad(a, [(r, r), (r, r)] + [(0, 0)] * (a.ndim - 2), mode='edge')
    c = p.cumsum(0).cumsum(1)
    c = np.pad(c, [(1, 0), (1, 0)] + [(0, 0)] * (a.ndim - 2))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def ssim(x, y, r=3):
    mx, my = boxblur(x, r), boxblur(y, r)
    vx = boxblur(x * x, r) - mx * mx; vy = boxblur(y * y, r) - my * my
    cxy = boxblur(x * y, r) - mx * my
    c1, c2 = 1.0 ** 2, 3.0 ** 2          # (0.01 L)^2, (0.03 L)^2 pour L* sur 0..100
    return float((((2*mx*my + c1) * (2*cxy + c2)) / ((mx*mx + my*my + c1) * (vx + vy + c2))).mean())


def conversion_metrics(idx, cell):
    ref = lin2lab(cell); conv = PAL_LAB[idx]
    hist = np.bincount(idx.ravel(), minlength=16) / idx.size
    return dict(isolated=isolated_pct(idx), ssim=ssim(ref[..., 0], conv[..., 0]),
                gray=float(hist[list(GRAYS)].sum() * 100),
                dE=float(np.linalg.norm(ref - conv, axis=-1).mean()))


def convert(master_path, converter=CONVERTER, resample='bilinear'):
    extra = [] if resample == 'bilinear' else ['--resample', resample]
    with tempfile.TemporaryDirectory(prefix='image-quality-') as tmp:
        out = Path(tmp) / 'image.bin'
        r = subprocess.run([str(converter), 'convert', *extra, str(master_path), str(out)],
                           capture_output=True, text=True)
        if r.returncode:
            raise ValueError(f'conversion impossible : {r.stderr.strip() or master_path}')
        return decode_rle(out.read_bytes())


def measure(master_path=None, rle=None, recipe=None, converter=CONVERTER, resample='bilinear'):
    """Mesures disponibles selon ce qui est fourni. Sans master : seulement le mouchetis et le gris."""
    out = {}
    master = Image.open(master_path) if master_path else None
    if master is not None:
        out['palette'] = palette_pct(master)
    if rle is not None:
        idx = decode_rle(Path(rle).read_bytes())
    elif master is not None:
        idx = convert(master_path, converter, resample)
    else:
        raise ValueError('un master ou un .RLE.BIN est requis')
    if master is not None:
        out.update(conversion_metrics(idx, reference(master, recipe)))
    else:
        hist = np.bincount(idx.ravel(), minlength=16) / idx.size
        out.update(isolated=isolated_pct(idx), gray=float(hist[list(GRAYS)].sum() * 100))
    return out


def excess(m, min_palette=MIN_PALETTE, max_isolated=MAX_ISOLATED):
    """Somme des depassements relatifs ; 0 quand les deux seuils sont tenus."""
    e = 0.0
    if 'palette' in m: e += max(0.0, (min_palette - m['palette']) / min_palette)
    if 'isolated' in m: e += max(0.0, (m['isolated'] - max_isolated) / max_isolated)
    return e


def line(name, m):
    cols = [('palette', 'palette %5.1f %%'), ('isolated', 'isoles %4.2f %%'), ('ssim', 'ssim %.3f'),
            ('gray', 'gris %4.1f %%'), ('dE', 'dE %5.2f')]
    return '%-5s ' % name + '  '.join(f % m[k] for k, f in cols if k in m)


def scoswamp_item(name, root=ROOT):
    bucket = 'N%03d' % (int(name[1:]) // 50 * 50)
    recipe = root / f'SCOSWAMP.MORE/IMAGE-RECIPES/{name}.json'
    return (root / f'SCOSWAMP.MORE/GENERATED/{name}.png', root / f'SCOSWAMP/DHGR/{bucket}/{name}.RLE.BIN',
            json.loads(recipe.read_text()) if recipe.exists() else None)


SORTS = dict(dE=('dE', True), ssim=('ssim', False), isolated=('isolated', True),
             palette=('palette', False), gray=('gray', True))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('measure', help='mesurer un master et/ou un .RLE.BIN')
    m.add_argument('--master'); m.add_argument('--rle'); m.add_argument('--recipe')
    m.add_argument('--resample', choices=('bilinear', 'area'), default='bilinear')
    m.add_argument('--json', action='store_true')
    wst = sub.add_parser('worst', help='les N pires conversions SCOSWAMP (toutes par defaut)')
    wst.add_argument('names', nargs='*')
    wst.add_argument('--count', type=int, default=10)
    wst.add_argument('--sort', choices=sorted(SORTS), default='dE')
    wst.add_argument('--root', type=Path, default=ROOT)
    wst.add_argument('--json', action='store_true')
    c = sub.add_parser('check', help='refuser un master hors seuils (code 1)')
    c.add_argument('master'); c.add_argument('--rle'); c.add_argument('--recipe')
    c.add_argument('--resample', choices=('bilinear', 'area'), default='bilinear')
    c.add_argument('--min-palette', type=float, default=MIN_PALETTE)
    c.add_argument('--max-isolated', type=float, default=MAX_ISOLATED)
    for p in (m, wst, c): p.add_argument('--converter', type=Path, default=CONVERTER)
    a = ap.parse_args(argv)
    try:
        if a.cmd == 'measure':
            recipe = json.loads(Path(a.recipe).read_text()) if a.recipe else None
            r = measure(a.master, a.rle, recipe, a.converter, a.resample)
            print(json.dumps(r, indent=1) if a.json else line(Path(a.master or a.rle).name[:4], r))
            return 0
        if a.cmd == 'worst':
            names = a.names or sorted(p.stem for p in (a.root / 'SCOSWAMP.MORE/GENERATED').glob('[NB][0-9][0-9][0-9].png'))
            rows = []
            for n in names:
                master, rle, recipe = scoswamp_item(n, a.root)
                if not master.exists() or not rle.exists():
                    print(f'{n}   absent : {master if not master.exists() else rle}', file=sys.stderr); continue
                rows.append(dict(name=n, **measure(master, rle, recipe, a.converter)))
            key, rev = SORTS[a.sort]
            rows.sort(key=lambda r: r[key], reverse=rev)
            rows = rows[:a.count] if a.count > 0 else rows
            if a.json: print(json.dumps(rows, indent=1))
            else:
                for r in rows: print(line(r['name'], r))
            return 0
        recipe = json.loads(Path(a.recipe).read_text()) if a.recipe else None
        r = measure(a.master, a.rle, recipe, a.converter, a.resample)
        e = excess(r, a.min_palette, a.max_isolated)
        print(('ok   ' if e == 0 else 'HORS ') + line(Path(a.master).stem, r) + '  ecart %.3f' % e)
        return 0 if e == 0 else 1
    except (OSError, ValueError) as err:
        print(f'image_quality.py : {err}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
