#!/usr/bin/env python3
"""Met a jour la copie d'A2 Retro Cmd embarquee sur le disque du jeu.

    tools/update_a2retrocmd.py [--from IMAGE.po | --tag v1.0]

Le gestionnaire de fichiers n'est plus construit ici : il vit dans son propre
depot, https://github.com/habib256/a2retrocmd, avec ses sources, ses bancs et
son integration continue. Le jeu n'en est plus que l'hote -- il l'embarque
tel qu'il est publie, et le propose par la touche [T] de l'ecran-titre.

Cet outil prend l'image de disquette d'une publication A2 Retro Cmd, en tire
les quatre fichiers a embarquer et les ecrit dans SCOSWAMP/A2RETRO/ :

    A2RETRO.SYSTEM.SYS   le lanceur, lu en $2000 par le jeu
    A2RETRO.CODE.BIN     le programme
    A2RETRO.HELP.TXT     sa page d'aide
    FORMAT.SYS.SYS       le formateur de disques

Il ecrit aussi PROVENANCE.txt : d'ou vient cette copie, et son empreinte.
"""
import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'SCOSWAMP/A2RETRO'
LATEST = 'https://github.com/habib256/a2retrocmd/releases/latest/download/A2RETROCMD.po'
BLOCK = 512
# Nom sur le volume -> nom d'hote (l'empaqueteur du jeu relit l'extension).
WANTED = {'A2RETRO.SYSTEM': 'A2RETRO.SYSTEM.SYS', 'A2RETRO.CODE': 'A2RETRO.CODE.BIN',
          'A2RETRO.HELP': 'A2RETRO.HELP.TXT', 'FORMAT.SYS': 'FORMAT.SYS.SYS'}


def entries(img, key):
    """Les entrees vivantes d'un repertoire ProDOS, chainage suivi."""
    out, block, first = [], key, True
    while block:
        b = img[block * BLOCK:(block + 1) * BLOCK]
        for k in range(13):
            if not (first and k == 0):
                e = b[4 + k * 39:4 + (k + 1) * 39]
                if e[0] >> 4:
                    out.append(e)
        first = False
        block = int.from_bytes(b[2:4], 'little')
    return out


def content(img, e):
    """Graine (un bloc) ou pousse (bloc d'index puis blocs de donnees)."""
    storage = e[0] >> 4
    key = int.from_bytes(e[0x11:0x13], 'little')
    eof = int.from_bytes(e[0x15:0x18], 'little')
    if storage == 1:
        return img[key * BLOCK:key * BLOCK + eof]
    if storage != 2:
        raise SystemExit(f'type de stockage {storage} inattendu')
    index, out = img[key * BLOCK:(key + 1) * BLOCK], bytearray()
    for i in range((eof + BLOCK - 1) // BLOCK):
        b = index[i] | (index[256 + i] << 8)
        out += img[b * BLOCK:(b + 1) * BLOCK]
    return bytes(out[:eof])


def harvest(img, key, found):
    for e in entries(img, key):
        name = e[1:1 + (e[0] & 15)].decode('ascii')
        if e[0] >> 4 == 0xD:
            harvest(img, int.from_bytes(e[0x11:0x13], 'little'), found)
        elif name in WANTED:
            found[name] = content(img, e)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument('--from', dest='path', type=Path, help='une image .po deja telechargee')
    src.add_argument('--tag', help='une version publiee (defaut : la derniere)')
    args = ap.parse_args()

    if args.path:
        origin, img = str(args.path), args.path.read_bytes()
    else:
        origin = (LATEST if not args.tag else
                  f'https://github.com/habib256/a2retrocmd/releases/download/{args.tag}/A2RETROCMD.po')
        print(f'telechargement de {origin}', flush=True)
        with urllib.request.urlopen(origin, timeout=60) as r:
            img = r.read()
    if len(img) != 280 * BLOCK:
        raise SystemExit(f'{len(img)} octets : ce n\'est pas une disquette ProDOS de 280 blocs')

    found = {}
    harvest(img, 2, found)
    missing = set(WANTED) - set(found)
    if missing:
        raise SystemExit('introuvable dans l\'image : ' + ', '.join(sorted(missing)))

    DEST.mkdir(parents=True, exist_ok=True)
    lines = [f'A2 Retro Cmd, copie embarquee sur le disque du jeu.', '',
             f'Source : {origin}',
             f'Image  : sha256 {hashlib.sha256(img).hexdigest()}', '',
             'Les sources, les bancs et la construction vivent dans',
             'https://github.com/habib256/a2retrocmd -- pas ici. Pour rafraichir',
             'cette copie : python3 tools/update_a2retrocmd.py', '']
    for name, host in sorted(WANTED.items()):
        data = found[name]
        (DEST / host).write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()[:16]
        print(f'  {host:<22} {len(data):>6} octets  {digest}')
        lines.append(f'{host:<22} {len(data):>6} octets  sha256:{digest}...')
    (DEST / 'PROVENANCE.txt').write_text('\n'.join(lines) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
