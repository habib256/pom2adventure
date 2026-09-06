#!/usr/bin/env python3
"""build_map.py - fabrique SCOSWAMP/MAP.BIN, la carte du Marais sur le disque.

« Pour vous aider a etablir votre carte, toutes les clairieres ont ete
numerotees. » Le Marais aux Scorpions est le seul Defis Fantastiques ou le
lecteur DOIT dessiner sa carte, et la mission de Pompatarte consiste a en
rapporter une. Le menu MAP (touche M) la dessine a sa place -- mais seulement
ce qu'il a vu.

Le texte du jeu est une donnee : la carte aussi. Ce script lit
SCOSWAMP.MORE/carte.json (35 clairieres, la bible topologique etablie par
SCOSWAMP/DOCS/CARTOGRAPHIE.md) et ecrit un fichier binaire compact que
l'empaqueteur ProDOS depose sur le volume sous le nom MAP.

    python3 build_map.py --root <depot>

Format (version 3), tout en petit-boutien :

    offset  taille  contenu
    ------  ------  ---------------------------------------------------------
      0       4     'M','A','P',3
      4       1     nombre de clairieres (35)
      5       1     nombre de pages rattachees (115)
      6       1     largeur d'un nom, terminateur compris (13)
      7       1     clairiere de depart (index)
      8       1     clairiere du pont (index) -- seul passage nord/sud
      9       1     ligne de la riviere Croupie (y = 3)
     10       2     page de la sortie sud du Marais (208)
     12       2     page de la sortie nord, vers Courbensaule (280)
     14       2     page de depart (195)
     16       2     longueur du bloc francais
     18       2     longueur du bloc anglais
     20     3*35    table des clairieres, 3 octets chacune :
                      b0 : x | (y << 3)          x 0..5, y 0..8
                      b1 : numero du livre, 0 si la clairiere est anonyme
                      b2 : masque des sorties
                             bit 0 N   bit 1 S   bit 2 E   bit 3 O
                             bit 4 : une sortie quitte le Marais (lisiere sud)
                             bit 5 : une sortie tue (le crocodile de la 20)
                             bit 6 : une sortie teleporte (le Feu Follet)
    125     2*115   table de rabattement page -> clairiere, triee :
                      b0 : ecart avec la page precedente (la premiere part de 0)
                      b1 : index de clairiere
    355      ...    bloc francais : 35 noms de 13 octets, puis les chaines de
                    l'ecran MAP, terminees par zero
     ...     ...    bloc anglais, meme disposition

Le moteur ne garde en RAM qu'un bloc de langue a la fois : il lit l'en-tete et
la table des clairieres, la table des pages, puis le bloc francais, et relit
le bloc anglais PAR-DESSUS si la partie est en anglais. Trois freads
sequentiels, aucun deplacement de curseur.

Pourquoi une table plate d'ecarts et non les 412 octets de CARTOGRAPHIE.md
Sec. 7.2 : 115 pages sur 412 se rattachent a un lieu, et les 412 octets ne
tenaient pas dans la RAM basse qui reste. 115 paires en font 230, la boucle de
recherche coute trente octets de code, et elle sert deux fois -- une fois pour
la clairiere courante, une fois pour allumer le brouillard de guerre.
"""
import argparse
import json
import struct
from pathlib import Path

MAGIC = b"MAP\x03"
NAME_W = 13            # 12 caracteres utiles + le zero final
# La taille de map_data[] dans scoswamp.c : ce que le moteur peut garder en
# RAM. Le reste de la zone $0C00-$0FFF loge d'autres tampons, et ld65 refuse
# le lien si l'ensemble deborde -- mais le message serait obscur, alors ce
# script tranche ici, avec le bon conseil.
MAP_DATA = 884
DIRS = "NSEO"          # l'ordre fixe les bits 0..3
DIRS_EN = "NSEW"

# Les 35 noms courts, dans l'ordre de carte.json, clef = page-hub.
#
# Les titres de carte.json sont des titres de page ("Le Perroquet / Maitresse
# des Oiseaux") : trop longs pour une case de panneau et pour la ligne de lieu.
# Ceux-ci sont ecrits a la main, 12 caracteres au plus, et disent le LIEU, pas
# l'evenement -- c'est ce que le livre demande de porter sur la carte.
NOMS = {
    78:  ("Courbensaule", "Courbensaule"),
    234: ("Patrouilleur", "The Patroller"[:12]),
    84:  ("Les Jardins",  "The Gardens"),
    232: ("Les 2 loups",  "Two Wolves"),
    218: ("Feu follet",   "Wisp Edge"),
    121: ("Croisement",   "Crossroads"),
    161: ("Le Geant",     "The Giant"),
    19:  ("Brigands",     "Brigands"),
    153: ("Bassin Vase",  "Slime Pool"),
    88:  ("Scorpion",     "Scorpion"),
    202: ("Nid d'Aigle",  "Eagle's Nest"),
    270: ("Sables mouv.", "Quicksand"),
    295: ("La Croupie",   "Croupie Bank"),
    183: ("La falaise",   "The Cliff"),
    45:  ("Le Pont",      "The Bridge"),
    304: ("Le Perroquet", "The Parrot"),
    94:  ("Brume fetide", "Fetid Mist"),
    179: ("Pique-nique",  "The Picnic"),
    319: ("Scorpions",    "Scorpions"),
    47:  ("3 chemins",    "Grassy Paths"),
    31:  ("B. de cristal"[:12], "Crystal Pool"),
    367: ("Angoisse",     "Dread Flower"),
    348: ("La Licorne",   "The Unicorn"),
    227: ("Les combats",  "Battleground"),
    187: ("Herbe Pinces", "Pincer Grass"),
    309: ("Orques",       "Swamp Orcs"),
    125: ("La Bete",      "The Beast"),
    22:  ("Arbres-Epees", "Sword Trees"),
    165: ("Araignees",    "Spiders"),
    230: ("Grenouilles",  "Giant Frogs"),
    44:  ("R. profonde",  "Deep River"),
    314: ("M. des Loups", "Wolf Master"),
    58:  ("Rond-point",   "Roundabout"),
    390: ("Tronc creux",  "Hollow Trunk"),
    82:  ("Bete bassin",  "Pool Beast"),
}

# Les chaines de l'ecran MAP, dans l'ordre : il fixe les indices lus par
# map_str() dans scoswamp.c. Elles vivent ici et non dans build_messages.py
# parce que le catalogue MSGFR/MSGEN est charge en RAM basse, ou il ne restait
# que 39 octets : le bloc MAP, lui, vit dans les 1 Ko de $0C00 que le second
# tampon ProDOS n'a jamais reclames.
# L'ordre suit l'enumeration MS_* de scoswamp.c, exactement comme celui de
# build_messages.py suit MSG_*. Une ligne de decalage et l'ecran affiche les
# chaines les unes pour les autres -- c'est arrive, l'ecran MAP portait la
# legende a la place de son titre et le refus de l'Anneau a la place des
# touches.
UI = [
    # (francais, anglais)                            index / nom C
    ("CARTE DU MARAIS",            "MAP OF THE SWAMP"),               # 0  TITRE
    ("clairieres sur 35",          "clearings out of 35"),           # 1  SUR35
    ("SORTIES",                    "PATHS OUT"),                     # 2  SORTIES
    ("vue",                        "seen"),                          # 3  VUE
    ("inexploree",                 "unexplored"),                    # 4  INCONNUE
    ("hors du Marais",             "out of the Swamp"),              # 5  HORS
    ("LEGENDE",                    "KEY"),                           # 6  LEGENDE
    ("(*) clairiere vue",           "(*) clearing seen"),             # 7  LEG1
    ("<*> vous etes ici",           "<*> you are here"),              # 8  LEG2
    ("--   sentier emprunte",      "--   path walked"),              # 9  LEG3
    ("-?   sentier connu",         "-?   path known, not taken"),    # 10 LEG4
    ("v    hors du Marais",        "v    out of the Swamp"),         # 11 LEG5
    ("M ou ESC : retour au recit", "M or ESC: back to the tale"),    # 12 TOUCHES
    ("Sans l'Anneau de Cuivre, les boussoles perdent le nord.",      # 13 ANNEAU
     "Without the Copper Ring, compasses lose their north."),
    ("sorties",                    "paths"),                         # 14 LIEU
    ("deja visitee",               "already seen"),                  # 15 DEJA
    ("NSEO",                       "NSEW"),                          # 16 DIRS
]

# Sec. 6.1 A : la page 230 annonce « vers l'est », la page 352 qui la suit dit
# « EN DIRECTION DU NORD ». La prose est retenue -- et de toute facon la grille
# tranche : la clairiere 8 est droit au sud de la 26. Le script derive donc
# TOUTES les directions de la geometrie ; le libelle ne sert que la ou aucune
# clairiere n'est atteinte.
#
# Sec. 6.1 C : la clairiere 14 est un cul-de-sac dont le retour n'est pas
# oriente dans le libelle du choix, seulement dans la prose (« Vous reprenez
# la direction du sud »). Sans cette ligne son panneau n'annoncerait aucune
# sortie, et le sentier 23 <-> 14 serait un aller simple sur le dessin.
SORTIE_AJOUTEE = {304: "S"}


def sortie_hors_grille(hub, direction, page, sortie_sud):
    """Classe une sortie qui ne mene a aucune clairiere. Rend le bit a poser."""
    if hub == 218 and direction == "O":
        return 0x40          # le piege du Feu Follet : une teleportation
    if page == sortie_sud:
        return 0x10          # la lisiere sud, on quitte le Marais
    return 0x20              # la falaise : plonger, c'est le crocodile


def direction_geometrique(a, b):
    ax, ay = a
    bx, by = b
    if ax == bx and by < ay:
        return "N"
    if ax == bx and by > ay:
        return "S"
    if ay == by and bx > ax:
        return "E"
    if ay == by and bx < ax:
        return "O"
    raise SystemExit(f"sentier ni horizontal ni vertical : {a} -> {b}")


def build(carte):
    clrs = carte["clairieres"]
    if len(clrs) != 35:
        raise SystemExit(f"carte.json : {len(clrs)} clairieres, 35 attendues")
    hub_index = {c["hub"]: i for i, c in enumerate(clrs)}
    pos = [(c["x"], c["y"]) for c in clrs]
    occupe = {p: i for i, p in enumerate(pos)}
    if len(occupe) != 35:
        raise SystemExit("deux clairieres partagent une case")

    # ── Les sorties, direction derivee de la grille ────────────────────────
    masques = [0] * 35
    voisin = {}          # (i, direction) -> j
    for i, c in enumerate(clrs):
        sorties = dict(c["sorties"])
        if c["hub"] in SORTIE_AJOUTEE:
            sorties.setdefault(SORTIE_AJOUTEE[c["hub"]], 0)
        for d, page in sorties.items():
            v = c["voisins"].get(d)
            if c["hub"] == 218 and d == "O":
                masques[i] |= 0x40
                continue
            if v is None:
                masques[i] |= sortie_hors_grille(c["hub"], d, page,
                                                 carte["sortie_sud"])
                continue
            j = hub_index[v]
            dd = direction_geometrique(pos[i], pos[j])
            masques[i] |= 1 << DIRS.index(dd)
            voisin[(i, dd)] = j

    # Le moteur ne porte AUCUNE table de sentiers : il cherche, dans la
    # direction annoncee, la premiere case occupee de la ligne ou de la
    # colonne. C'est ce qui rend les trois sentiers de deux cases gratuits.
    # Verifie ici, une fois pour toutes, que cette recherche retrouve bien le
    # voisin de carte.json.
    for (i, d), j in voisin.items():
        x, y = pos[i]
        dx, dy = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "O": (-1, 0)}[d]
        k = None
        cx, cy = x + dx, y + dy
        while 0 <= cx < 6 and 0 <= cy < 9:
            if (cx, cy) in occupe:
                k = occupe[(cx, cy)]
                break
            cx += dx
            cy += dy
        if k != j:
            raise SystemExit(
                f"la premiere case occupee au {d} de {pos[i]} est {k}, "
                f"pas le voisin {j} de carte.json")

    # ── Le rabattement page -> clairiere ──────────────────────────────────
    page_clr = {}
    for i, c in enumerate(clrs):
        for p in c["pages"]:
            if p in page_clr:
                raise SystemExit(f"la page {p} est revendiquee deux fois")
            page_clr[p] = i
    pages = sorted(page_clr)
    ecarts = []
    prev = 0
    for p in pages:
        d = p - prev
        if d > 255:
            raise SystemExit(f"ecart de {d} pages : l'octet deborde")
        ecarts.append((d, page_clr[p]))
        prev = p

    # ── Les blocs de langue ───────────────────────────────────────────────
    blocs = []
    for langue in (0, 1):
        b = bytearray()
        for c in clrs:
            nom = NOMS[c["hub"]][langue]
            if len(nom) > NAME_W - 1:
                raise SystemExit(f"nom trop long ({len(nom)}) : {nom!r}")
            if not nom.isascii():
                raise SystemExit(f"nom non ASCII : {nom!r}")
            b += nom.encode("ascii").ljust(NAME_W, b"\0")
        for paire in UI:
            s = paire[langue]
            if not s.isascii():
                raise SystemExit(f"chaine non ASCII : {s!r}")
            b += s.encode("ascii") + b"\0"
        blocs.append(bytes(b))

    # ── L'assemblage ──────────────────────────────────────────────────────
    depart_clr = page_clr[carte["depart"]]
    pont_clr = next(i for i, c in enumerate(clrs) if c["id"] == 35)

    out = bytearray(MAGIC)
    out += bytes([35, len(pages), NAME_W, depart_clr, pont_clr, 3])
    out += struct.pack("<HHHHH", carte["sortie_sud"], carte["sortie_nord"],
                       carte["depart"], len(blocs[0]), len(blocs[1]))
    assert len(out) == 20, len(out)
    for i, c in enumerate(clrs):
        x, y = pos[i]
        out += bytes([x | (y << 3), c["id"] or 0, masques[i]])
    for d, i in ecarts:
        out += bytes([d, i])
    assert len(out) == 20 + 3 * len(clrs) + 2 * len(pages), len(out)
    out += blocs[0] + blocs[1]
    return bytes(out), len(blocs[0]), len(blocs[1]), pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    args = ap.parse_args()

    carte = json.loads((args.root / "SCOSWAMP.MORE" / "carte.json")
                       .read_text(encoding="utf-8"))
    blob, nfr, nen, pages = build(carte)
    dest = args.root / "SCOSWAMP" / "MAP.BIN"
    dest.write_bytes(blob)

    # Ce que le moteur garde vraiment : l'en-tete et les clairieres (125 o) et
    # UN bloc de langue, dans map_data[900] -- la zone MAPRAM de $0C00-$0FFF,
    # dont le reste loge d'autres tampons chasses de la fenetre principale. La
    # table des pages (230 o) vit en RAM basse, elle est lue a chaque page.
    resident = 125 + max(nfr, nen)
    print(f"MAP.BIN : {len(blob)} octets ({len(pages)} pages rattachees, "
          f"bloc FR {nfr}, bloc EN {nen})")
    print(f"  resident en $0C00 : {resident} / {MAP_DATA} octets "
          f"(reste {MAP_DATA - resident})")
    print(f"  resident en RAM basse : {2 * len(pages)} octets "
          f"(table des pages)")
    if resident > MAP_DATA:
        raise SystemExit(
            f"le bloc resident deborde map_data[{MAP_DATA}] de scoswamp.c ; "
            "raccourcir les noms ou les chaines, ou agrandir map_data et "
            "reduire d'autant les autres tampons de MAPBSS")


main()
