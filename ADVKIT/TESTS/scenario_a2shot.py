#!/usr/bin/env python3
"""Parcours des volumes livrés sur le SDK public POM2, par `a2shot`.

Amorce le vrai volume de chaque jeu, brut et 2MG, sur le //e amélioré. Pour
SCOSWAMP : choix de la langue, entrée dans le jeu, sauvegarde relue côté hôte,
reprise après un nouvel amorçage, puis média protégé et reproductibilité.
SPACETRIP : choix de la langue et entrée dans le jeu. Les empreintes du cœur, des
ROM, du volume et du programme en mémoire sont relevées et imprimées.

`a2shot` travaille sur une copie privée ; les disques de `dist/` ne sont jamais
écrits, ce que vérifient leurs empreintes. Un outil ou un volume absent est un
échec, pas un contrôle ignoré. Ce banc vérifie le fonctionnement, pas les images.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BLOCK = 512
TWOIMG_HEADER = 64

# Trames vidéo NTSC, marges comprises. Le premier appui sème les dés avec le
# temps d'attente : ces valeurs font partie du scénario reproductible. Chaque
# touche attend d'avoir été prise (`keywait`, qui échoue si le jeu ne la prend pas
# dans son budget), puis la page a le temps de se peindre.
BOOT = "wait:1200"


def press(key, settle=1200):
    return [f"press:{key}", "keywait:3000", f"wait:{settle}"]


TO_GAME = [*press("F"), *press("A"), *press(" ")]
SAVE_SLOT_3 = [*press("S"), *press("3")]
SCENE = "Qui vous etes"


class Failure(Exception):
    pass


def check(condition, message):
    if not condition:
        raise Failure(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def a2shot(tool, disk, steps):
    """Exécute un scénario ; rend sa sortie, sans le journal du cœur."""
    command = [str(tool), "--iie", "--mockingboard", "--disk", str(disk), *steps]
    done = subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=240)
    if done.returncode:
        raise Failure(f"a2shot, code {done.returncode} : {done.stderr.strip()[-400:]}")
    return "\n".join(line for line in done.stdout.splitlines() if not line.startswith("["))


def directory(image, block):
    """Les entrées actives d'un répertoire ProDOS : nom → (clé, taille)."""
    entries = {}
    while block:
        at = block * BLOCK
        for index in range(13):
            entry = image[at + 4 + index * 39:at + 4 + (index + 1) * 39]
            kind = entry[0] >> 4
            if kind and kind < 0xE:
                name = entry[1:1 + (entry[0] & 15)].decode("ascii")
                entries[name] = (entry[17] | entry[18] << 8,
                                 entry[21] | entry[22] << 8 | entry[23] << 16)
        block = image[at + 2] | image[at + 3] << 8
    return entries


def payload(path):
    data = Path(path).read_bytes()
    return data[TWOIMG_HEADER:] if data[:4] == b"2IMG" else data


def save_file(path):
    """Le fichier de l'emplacement 3, lu côté hôte, par le catalogue."""
    image = payload(path)
    folder = directory(image, 2)["SAVE"][0]
    key, size = directory(image, folder)["SAVE3"]
    return image[key * BLOCK:key * BLOCK + size]


def blocks_changed(before, after):
    before, after = payload(before), payload(after)
    check(len(before) == len(after), "la capacité du volume a changé")
    return sum(before[i:i + BLOCK] != after[i:i + BLOCK] for i in range(0, len(before), BLOCK))


def scoswamp(tool, shipped, work):
    label = shipped.name
    saved = work / f"saved-{label}"
    first = a2shot(tool, shipped, [
        "hddinfo", BOOT, "text80", *TO_GAME, "text80", *SAVE_SLOT_3, "hddinfo",
        f"hddsave:{saved}", "hddinfo",
    ])
    blocks = len(payload(shipped)) // BLOCK
    check(f"blocks={blocks} wp=0 unsaved=0" in first, f"{label} : capacité ou protection inattendue")
    check("SELECT YOUR LANGUAGE" in first, f"{label} : menu de langue absent")
    check(SCENE in first, f"{label} : première scène absente")
    check(f"blocks={blocks} wp=0 unsaved=2" in first, f"{label} : écritures en attente inattendues")
    check(first.rstrip().endswith("unsaved=0"), f"{label} : le flush laisse des blocs en attente")

    # La sauvegarde relue par le catalogue, sans rien d'autre sur le volume.
    before = save_file(shipped)
    after = save_file(saved)
    check(len(before) == 2 and after[:3] == b"SCS" and len(after) > len(before),
          f"{label} : sauvegarde absente du fichier hôte ({len(before)} → {len(after)} octets)")
    check(blocks_changed(shipped, saved) == 2, f"{label} : blocs modifiés hors du répertoire et de SAVE3")
    if shipped.read_bytes()[:4] == b"2IMG":
        check(saved.read_bytes()[:TWOIMG_HEADER] == shipped.read_bytes()[:TWOIMG_HEADER],
              f"{label} : en-tête 2MG modifié")

    # Un nouvel amorçage du volume sauvegardé propose et reprend la partie.
    resumed = a2shot(tool, saved, [
        BOOT, *press("F"), *press("L"), "text80", *press("3"), "text80", "hddinfo",
    ])
    check(f"3) {SCENE}" in resumed, f"{label} : emplacement 3 absent à la reprise")
    check(resumed.count(SCENE) >= 2, f"{label} : la partie n'a pas repris")
    check(resumed.rstrip().endswith("unsaved=0"), f"{label} : la reprise a écrit sur le volume")

    # Protégé : le jeu n'écrit rien, jusque dans le fichier.
    locked = work / f"locked-{label}"
    a2shot(tool, shipped, [BOOT, *TO_GAME, "hddprotect:1", *SAVE_SLOT_3, f"hddsave:{locked}"])
    check(locked.read_bytes() == shipped.read_bytes(), f"{label} : un volume protégé a changé")

    # Même scénario, mêmes octets et même écran, aux points de contrôle.
    again = work / f"again-{label}"
    second = a2shot(tool, shipped, [
        "hddinfo", BOOT, "text80", *TO_GAME, "text80", *SAVE_SLOT_3, "hddinfo",
        f"hddsave:{again}", "hddinfo",
    ])
    check(first == second.replace(str(again), str(saved)), f"{label} : sortie différente au second passage")
    check(saved.read_bytes() == again.read_bytes(), f"{label} : volume différent au second passage")
    print(f"ok : {label} — amorçage, jeu, sauvegarde ({len(after)} octets), reprise, protection, reproductibilité")


def spacetrip(tool, shipped):
    text = a2shot(tool, shipped, ["hddinfo", "wait:1800", "text80", *press("F", 1800), "text80", "hddinfo"])
    blocks = len(payload(shipped)) // BLOCK
    check(f"blocks={blocks} wp=0" in text, f"{shipped.name} : capacité inattendue")
    menu, _, game = text.partition("keywait")
    check("SPACE EXPLORER TRIP" in menu and "SELECT YOUR LANGUAGE" in menu,
          f"{shipped.name} : menu de langue absent")
    check("SELECT YOUR LANGUAGE" not in game and game.strip("|\n ") != "",
          f"{shipped.name} : le choix de langue n'a pas fait entrer dans le jeu")
    print(f"ok : {shipped.name} — amorçage, choix de langue, entrée dans le jeu")


def provenance(tool, shipped):
    """Ce qui a réellement tourné : cœur, ROM, volume, programme chargé."""
    report = a2shot(tool, shipped, [BOOT, "provenance", "ramhash:main:2000:8192"])
    for field in ("provenance core=", " commit=", "capabilities=", "provenance rom=",
                  "provenance disk=", "provenance copy=", "ramhash main 2000 8192 "):
        check(field in report, f"provenance incomplète : {field!r} absent")
    check("harddisk" in report, "le cœur ne déclare pas le disque dur")
    disk = next(line for line in report.splitlines() if line.startswith("provenance disk="))
    check(disk.endswith(sha256(shipped)), f"empreinte du volume fausse : {disk}")
    for line in report.splitlines():
        print("  " + line)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_tool = os.environ.get("A2SHOT", str(ROOT.parent / "pom2games/dev/tools/a2shot/a2shot"))
    parser.add_argument("--a2shot", type=Path, default=Path(default_tool))
    args = parser.parse_args()

    dist = ROOT / "dist"
    volumes = [dist / name for name in
               ("SCOSWAMP.HDV", "SCOSWAMP.2mg", "SPACETRIP.hdv", "SPACETRIP.2mg")]
    try:
        check(args.a2shot.is_file(), f"a2shot introuvable : {args.a2shot} (make -C ../pom2games/dev/tools/a2shot)")
        for volume in volumes:
            check(volume.is_file(), f"volume introuvable : {volume}")
        shipped = {volume: sha256(volume) for volume in volumes}
        with tempfile.TemporaryDirectory(prefix="scenario-a2shot-") as tmp:
            work = Path(tmp)
            provenance(args.a2shot, volumes[0])
            scoswamp(args.a2shot, volumes[0], work)
            scoswamp(args.a2shot, volumes[1], work)
            spacetrip(args.a2shot, volumes[2])
            spacetrip(args.a2shot, volumes[3])
        for volume, digest in shipped.items():
            check(sha256(volume) == digest, f"{volume.name} livré a été modifié")
    except (Failure, subprocess.TimeoutExpired, KeyError) as exc:
        print(f"ÉCHEC : {exc}", file=sys.stderr)
        return 1
    print("ok : disques de dist/ inchangés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
