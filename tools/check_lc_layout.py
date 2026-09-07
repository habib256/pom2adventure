#!/usr/bin/env python3
"""Check the split-load contract between ld65, the game image and loader.c."""
import argparse
import re
from pathlib import Path


def check_layout(s, loader, length, staged=None):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    stage, lc, entry = (loader[k] for k in ('LC_STAGE', 'LC_BYTES', 'GAME_ADDR'))
    # Ce que le lanceur lit d'un coup en $1000. Pour le jeu c'est l'image LC
    # seule ; TOTAL y ajoute son kilo-octet de code LOWEXE, que crt0 laisse
    # en place ($1C00) au lieu de l'emporter dans la carte langage.
    prefix = staged if staged is not None else lc
    require(s['__LCIMAGE_FILEOFFS__'] == 0, 'LC must be the first bytes in the file')
    require(s['__LCIMAGE_START__'] == stage, 'LC staging address differs from loader')
    require(s['__LCIMAGE_SIZE__'] == lc, 'LC prefix size differs from loader')
    require(lc <= prefix, 'the staged prefix cannot be smaller than the LC image')
    require(s['__MAIN_FILEOFFS__'] == prefix, 'MAIN file offset differs from loader')
    require(s['__MAIN_START__'] == entry, 'MAIN entry address differs from loader')
    require(0x0C00 <= stage and stage + prefix <= 0x2000,
            'LC staging overlaps ProDOS buffers or the graphics page')
    if staged is not None:
        # Le code loge au-dessus de l'image LC dans le meme prefixe : il doit
        # commencer apres elle, et la BSS basse ne doit pas venir l'ecraser.
        require(s['__LOWEXE_RUN__'] >= stage + lc,
                'LOWEXE starts inside the LC staging area')
        require(s['__LOWEXE_RUN__'] + s['__LOWEXE_SIZE__'] <= stage + prefix,
                'LOWEXE runs past the staged prefix')
        require(s['__LOWBSS_RUN__'] + s['__LOWBSS_SIZE__'] <= s['__LOWEXE_RUN__'],
                'low BSS runs into LOWEXE')
    require(0xD400 <= s['__LC_START__'] <= s['__LC_LAST__'] <= 0xE000,
            'LC code crosses its bank-2 execution window')
    require(s['__LC_LAST__'] - s['__LC_START__'] <= lc,
            'LC code exceeds the fixed prefix')
    require(s['__LCIMAGE_LAST__'] - stage == s['__LC_LAST__'] - s['__LC_START__'],
            'LC staging and execution lengths differ')
    require(entry < s['__MAIN_LAST__'] <= 0xBF00,
            'MAIN image is empty or overlaps the ProDOS system page')
    require(length == prefix + s['__MAIN_LAST__'] - entry,
            'game file length does not match split-load layout')
    # Le plancher de la pile C. ld65 ne le controle pas : la zone BSS se
    # dimensionne par __HIMEM__ - __STACKSIZE__ - __ONCE_RUN__, et quand
    # cette difference passe en negatif il la lit en entier non signe, ne
    # signale rien et pose la BSS dans la pile. Tout ce qui survit a
    # l'initialisation -- CODE, RODATA, DATA, INIT, et la BSS ou qu'elle
    # soit -- doit finir sous ce plancher. Seul ONCE a le droit de le
    # depasser : il est mort avant le premier appel de main().
    floor = s['__HIMEM__'] - s['__STACKSIZE__']
    require(s['__ONCE_RUN__'] <= floor,
            'the cold end (${:04X}) runs into the C stack (${:04X})'.format(
                s['__ONCE_RUN__'], floor))
    require(s['__BSS_RUN__'] + s['__BSS_SIZE__'] <= floor,
            'BSS (${:04X}-${:04X}) runs into the C stack (${:04X})'.format(
                s['__BSS_RUN__'], s['__BSS_RUN__'] + s['__BSS_SIZE__'] - 1, floor))
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--src', type=Path, default=Path(__file__).resolve().parents[1]/'SCOSWAMP/SRC')
    # TOTAL partage le lanceur et la disposition du jeu : memes controles,
    # sur sa propre table de symboles et son propre fichier.
    ap.add_argument('--lbl', default='build.lbl', help='table de symboles ld65 (defaut : build.lbl)')
    ap.add_argument('--bin', default='../SCOSWAMP.BIN', help='image a charge separee (defaut : ../SCOSWAMP.BIN)')
    ap.add_argument('--stage', type=lambda v: int(v, 0), default=None,
                    help='octets mis en scene en $1000 (defaut : la seule image LC ; TOTAL y ajoute LOWEXE)')
    args = ap.parse_args()
    args.src = args.src.resolve()
    s = {name: int(value,16) for value,name in re.findall(
        r'^al ([0-9A-Fa-f]+) \.([\w]+)$', (args.src/args.lbl).read_text(), re.M)}
    loader = {name:int(value,0) for name,value in re.findall(
        r'^#define (LC_STAGE|LC_BYTES|GAME_ADDR)\s+(0x[0-9A-Fa-f]+|\d+)',
        (args.src/'loader.c').read_text(), re.M)}
    try:
        errors = check_layout(s,loader,(args.src/args.bin).stat().st_size,args.stage)
    except KeyError as exc:
        errors = [f'missing layout symbol or loader constant: {exc}']
    if errors:
        for error in errors:
            print('ERREUR LC : '+error)
        return 1
    print(f"LC : prefixe {args.stage or loader['LC_BYTES']} octets en ${loader['LC_STAGE']:04X}, "
          f"MAIN ${s['__MAIN_START__']:04X}-${s['__MAIN_LAST__']-1:04X}, "
          f"froid jusqu'a ${s['__ONCE_RUN__']:04X} sous une pile de "
          f"{s['__STACKSIZE__']} octets, disposition valide")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
