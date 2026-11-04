> **Hommage, gratuit, non commercial.** SCOSWAMP est un portage Apple II du
> *Marais aux Scorpions*, huitième volume des *Défis Fantastiques* de Steve
> Jackson et Ian Livingstone, illustré par Duncan Smith, paru chez Gallimard
> en 1985. L'œuvre appartient à ses auteurs et à son éditeur ; ce dépôt en est
> un hommage écrit par un lecteur, distribué librement sous GPL v3, dont
> personne ne tire un centime. Si un ayant droit souhaite qu'il disparaisse, il
> disparaîtra.

# pom2adventure — l'atelier logiciel Apple II

Deux jeux d'aventure pour Apple IIe Enhanced, et la fabrique qui les construit.
Dépôt distinct de [POM2](../pom2), qui est l'émulateur : ici on écrit les
programmes *pour* la machine, chaîne cc65 `apple2enh` + ProDOS 8.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Trois projets

| Projet | Ce que c'est | Son atelier |
|---|---|---|
| **[SCOSWAMP](#-scoswamp--le-marais-aux-scorpions)** | *Le Marais aux Scorpions*, le livre-jeu complet, bilingue, illustré | `SCOSWAMP.MORE/` |
| **[ADVKIT](#-advkit--la-fabrique-commune)** | la fabrique commune aux deux jeux : lecteur et atelier web, outils natifs, tests | — |
| **[SPACETRIP](#-spacetrip--space-explorer-trip)** | *Space Explorer Trip*, aventure galactique | `SPACETRIP.MORE/` |

```
SCOSWAMP/          le jeu : données du volume ProDOS, SRC/ (moteur), DOCS/
SCOSWAMP.MORE/     bibles, masters, musique, outils Python, banc POM2
ADVKIT/            lecteur/atelier HTML-JS, TESTS/, TOOLS/ natifs, RELEASE.md
SPACETRIP/         le jeu : moteur, textes, images, build_disk.py
SPACETRIP.MORE/    bible, manifeste d'images, conversion
dist/              les images produites (non suivies)
check-project.sh   contrôle d'intégrité des deux jeux
AGENTS.md          repères pour contribuer et choisir les validations
```

Un outil qui sert aux deux jeux vit dans `ADVKIT/` ; un outil propre à un jeu
vit dans son `.MORE/TOOLS/`.

## 🚀 Démarrage rapide

Prérequis : **cc65** (`brew install cc65`), **cmake**, **python3**, **node**,
et les sources de [POM2](../pom2) à côté du dépôt pour les outils natifs.

```bash
./check-project.sh                    # intégrité des deux jeux
make -C SCOSWAMP/SRC hdv              # dist/SCOSWAMP.2mg  (+ dist/SCOSWAMP.HDV)
python3 SPACETRIP/build_disk.py       # dist/SPACETRIP.2mg (+ dist/SPACETRIP.hdv)
sh ADVKIT/serve.sh                    # l'atelier : http://localhost:8765/ADVKIT/
```

`dist/` reçoit deux sortes d'images : le **`.2mg`**, que télécharge un joueur,
et l'**image de travail** (`.HDV` / `.hdv`), les mêmes blocs sans en-tête, que
relisent l'émulateur, les bancs et l'atelier. Voir
[ADVKIT/RELEASE.md](ADVKIT/RELEASE.md).

Tester dans l'émulateur voisin :

```bash
../pom2/build/POM2 --preset iie dist/SCOSWAMP.2mg
```

Ajouter `--ai-control=PORT` pour le piloter sans les mains (HTTP sur la boucle
locale ; attention, son parseur JSON ne décode pas les échappements `\uXXXX`,
une touche de contrôle se passe en octet brut dans le corps de la requête).

### Les tests

```bash
python3 ADVKIT/TESTS/run.py           # Python, Node et C autonomes
python3 ADVKIT/TESTS/run.py --list    # suites, dont images, HTTP et Chrome
python3 ADVKIT/TESTS/run.py images    # NumPy/Pillow et sources POM2 requis
make -C SCOSWAMP/SRC playtest         # le jeu rejoué sous POM2, ~2 minutes
```

Le [harnais](ADVKIT/TESTS/README.md) détaille les prérequis, les rapports JSON
et l'ajout de tests. Les tests C autonomes ne demandent ni POM2 ni cc65.
La [revue des images](ADVKIT/IMAGES.md#préparer-une-revue-détaillée) distingue
les contrôles automatiques de la comparaison visuelle dans l'atelier.

---

## 📊 État du projet

> Les chiffres ci-dessous sont **produits par `./check-project.sh`**, pas saisis à la main.
> Relancer le script après toute modification de contenu pour les mettre à jour.
> Dernière vérification : 31 août 2026 — 0 erreur.

| Jeu | Rôle | Moteur | Scènes | Textes | Images | État |
|--------|------|--------|--------|--------|--------|------|
| **SCOSWAMP** | Le Marais aux Scorpions (livre-jeu) | 13 322 o | 407 | 814 ✅ | 407 / 407 + 32 combats ✅ | ✅ Complet |
| **SPACETRIP** | Space Explorer Trip (aventure sci-fi) | 12 835 o | 14 | 28 ✅ | 14 / 14 ✅ | ✅ Complet |

**Intégrité** : 439 images DHGR compressées (DHRR), toutes vérifiées comme se
décodant en 16 384 octets exactement (8 Ko auxiliaires + 8 Ko principaux).
Aucun trou de numérotation, aucune scène FR sans équivalent EN, aucun fichier
texte vide.

Le script valide les tailles d'images, l'appariement FR/EN, la continuité des
scènes, la taille des moteurs face au budget mémoire, et l'absence d'artefacts
de build versionnés.

---

## 🎮 SCOSWAMP — Le Marais aux Scorpions

Adaptation du livre-jeu « Scorpion Swamp » (1985) par Steve JACKSON & Ian LIVINGSTONE.

**Solutions (révélations)** : [les trois parcours gagnants](SCOSWAMP/DOCS/PARCOURS-GAGNANTS.md),
avec les pierres nécessaires, les embranchements, les variantes de fin et le
niveau de validation dans POM2.
**Code et mémoire** : [audit précis du binaire et optimisations](SCOSWAMP/DOCS/AUDIT-MEMOIRE-SCOSWAMP.md),
avec inventaire par fonction, allocations et expériences de compilation reproductibles.

### Ce qui est terminé

- **Le livre complet**, bilingue FR/EN, appariement vérifié
- **Mode texte 80 colonnes**, bascule instantanée image ↔ texte (ESPACE / RETURN / ESC)
- **Toutes les scènes sont illustrées** : 407 images de page + 32 tableaux de
  bataille, en couleur, dans la palette DHGR à seize indices
- **Combat, Chance, Pierres, sac à dos, carte, sauvegardes**, fidèles aux
  règles des *Défis Fantastiques*
- **Musique Mockingboard** et **DIAPO**, le diaporama lancé par `[D]` depuis
  l'écran-titre

### Construire

```bash
make -C SCOSWAMP/SRC hdv
```

relie le jeu et `SCOSWAMP.SYSTEM`, son lanceur ProDOS, puis reconstruit
`dist/SCOSWAMP.HDV` et `dist/SCOSWAMP.2mg`. Le disque ne porte plus
BASIC.SYSTEM : le jeu occupe sa place en mémoire et démarre par le lanceur
(`SCOSWAMP/SRC/loader.c`). Les règles de jeu se testent sur la machine hôte,
sans émulateur, par `ctest` (voir [Les tests](#les-tests)).

**Contrôles** : `ESPACE/RETURN/ESC` = basculer image/texte | `A-Z` = choix | `Q` = quitter

### Comment les images sont faites

Ce que la note de périmètre des versions précédentes chiffrait à 165–330 h de
travail artistique a été fait autrement : par une chaîne reproductible, dont
les **bibles** (`characters.json`, `monsters.json`, `decors.json`,
`objects.json`) sont la pièce maîtresse. Une description visuelle y est écrite
**une seule fois** par sujet, et 74 **planches de référence** (`SCOSWAMP.MORE/
REF/`) la fixent en image. Chaque prompt de scène reprend la fiche mot pour mot
et attache les planches des sujets qu'il cite : c'est ce qui fait que le géant
du combat 012 est le même géant à la page 126.

```bash
# 1. les manifestes, un prompt par page, dérivés du corpus et des bibles
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . \
        --output SCOSWAMP.MORE/scene_manifest.jsonl --all
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . \
        --output SCOSWAMP.MORE/battle_manifest.jsonl --battle

# 2. les rendus maîtres (~1400x960), 10 de front ; relançable, il reprend
#    où il s'est arrêté
bash SCOSWAMP.MORE/TOOLS/generate_images.sh SCOSWAMP.MORE/scene_manifest.jsonl 0 10

# 3. la conversion vers l'écran de la machine, et le rapport des dix pires
sh SCOSWAMP.MORE/TOOLS/convert_images.sh

# 4. l'empreinte des fiches, pour savoir plus tard ce qu'un changement périme
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . --output /dev/null --record
```

Modifier une fiche de bible périme toutes les images qui la citent :
`build_manifest.py --stale` les nomme. L'atelier ADVKIT permet ensuite de
juger et de retoucher chaque image dans le contexte de sa page.

---

## 🧰 ADVKIT — la fabrique commune

Tout ce qui fabrique les deux jeux sans appartenir à l'un d'eux.

| Dossier | Contenu |
|---|---|
| `ADVKIT/` | le **lecteur et l'atelier** HTML/JavaScript : il ouvre le volume ProDOS exactement comme la machine le démarre, joue le jeu, compare chaque image à son master et la reconvertit ; `verifier.js` passe le même moteur sur tout un corpus, sans navigateur |
| `ADVKIT/TESTS/` | les tests node du moteur de règles et le test de l'atelier |
| `ADVKIT/TOOLS/` | les **outils natifs** : `build_prodos_volume` et son amorce `prodos_boot.tmpl`, `wrap_2mg.py`, `pom2_playtest` (POM2 sans fenêtre, pour les bancs), les convertisseurs `scoswamp_hgr` / `scoswamp_dhgr` |

```bash
sh ADVKIT/serve.sh                                    # l'atelier dans le navigateur
node ADVKIT/verifier.js                               # tout le volume SCOSWAMP
node ADVKIT/verifier.js project.spacetrip.json        # le corpus de SPACETRIP
cmake -S ADVKIT/TOOLS -B ADVKIT/TOOLS/build && cmake --build ADVKIT/TOOLS/build
sh ADVKIT/TOOLS/build_pom2_playtest.sh                # l'hôte headless de POM2
```

Les deux jeux sont deux **données** du même atelier, décrites par
`ADVKIT/project.scoswamp.json` et `ADVKIT/project.spacetrip.json`. Voir
[ADVKIT/README.md](ADVKIT/README.md) et [ADVKIT/IMAGES.md](ADVKIT/IMAGES.md).

---

## 🚀 SPACETRIP — Space Explorer Trip

Aventure galactique interactive démontrant l'architecture pilotée par données.
**Complet** : 14 scènes, 14 images, bilingue.

| Métrique | Valeur |
|----------|--------|
| Moteur | 12 835 o |
| Scènes | 14 (FR + EN) |
| Images | HGR brutes, 8 192 octets chacune |
| Fichiers texte | 28 (14 FR + 14 EN) |

### Construire

```bash
python3 SPACETRIP/build_disk.py       # moteur (SPACETRIP/build.sh), puis dist/SPACETRIP.2mg
```

`sh SPACETRIP/build.sh test` ne fait tourner que le banc hôte de l'analyseur
de page. La bible de l'univers et le manifeste des images vivent dans
`SPACETRIP.MORE/` ; `sh SPACETRIP.MORE/TOOLS/convert_images.sh` convertit les
masters en pages HGR.

### Ajouter du contenu (sans recompilation)

1. Créer `TXTFR/N015` et `TXTEN/N015` (description + choix)
2. Créer `IMG/N015.HGR.BIN` (8192 octets exactement)
3. Lier depuis une scène : ajouter `C 015 Titre du choix`
4. Valider avec `./check-project.sh`, reconstruire le disque

---

## 🛠️ Développement

### Philosophie : piloté par les données

Le moteur reste en mémoire, seule la scène courante est chargée depuis le
disque. Le contenu n'est limité que par l'espace disque (jusqu'à 32 Mo ProDOS),
une scène s'ajoute sans recompiler, et les joueurs peuvent la modifier.

### Machine cible

**Apple IIe Enhanced** (65C02), 64 Ko RAM, carte 80 colonnes, ProDOS 8.

### Carte mémoire

Configuration cc65 standard, celle de SPACETRIP :

```
$0000-$1FFF : Système ProDOS (page zéro, pile 6502, buffers)
$2000-$3FFF : HGR Page 1
$4000-$8DFF : Moteur : CODE + RODATA + DATA + BSS  (19 968 o utilisables)
$8E00-$95FF : Pile C
$9600-$BFFF : BASIC.SYSTEM puis ProDOS 8 — MLI, page globale ($BF00), buffers fichier
$C000-$FFFF : I/O et ROM
```

Démarrage à `$4000` pour préserver HGR Page 1 (`$2000-$3FFF`).

**`$9600-$BEFF` n'est pas perdu.** cc65 y suppose BASIC.SYSTEM résident — ce
qu'implique `]BRUN` — et fixe par prudence `__HIMEM__ = $9600`. Un programme qui
renonce à revenir au BASIC récupère ces **10 496 octets** : c'est ce que fait
SCOSWAMP, lancé par son propre `SCOSWAMP.SYSTEM`, avec `__HIMEM__ = $BF00` et
une zone `LOWRAM` supplémentaire en `$1000-$1FFF` (`SCOSWAMP/SRC/scoswamp.cfg`).

Deux contraintes distinctes, à ne pas confondre :

| Contrainte | Ce qu'elle limite | Vérifiée par |
|------------|-------------------|--------------|
| Taille du `.BIN` | CODE + RODATA + DATA + ONCE | `check-project.sh` |
| Empreinte exécution | **+ BSS + tas + pile** | `SCOSWAMP.MORE/TOOLS/check-memory.sh` (lit le `.map`) |

Le `.BIN` **ne contient pas la BSS**, allouée au lancement. Un binaire de taille
acceptable peut donc déborder à l'exécution. `make` dans `SCOSWAMP/SRC` passe
le `.map` au contrôle à chaque lien, et affiche la marge restante.

> **Piège `ld65`.** Si la BSS démarre déjà au-delà du plafond, la taille de sa
> zone se calcule en négatif, déborde en non signé, et le contrôle d'overflow
> est neutralisé : **le link réussit sans le moindre avertissement**. Seule la
> lecture du `.map` révèle le problème.

> **Piège du tas.** Reloger toute la BSS en RAM basse ne marche pas : dans cc65
> le tas est câblé sur `__BSS_RUN__ + __BSS_SIZE__` et **suit la BSS**. Relogée
> en bas, le tas traverse HGR page 1 puis le code, et `fopen()` — 1 Ko par
> fichier ouvert — écrase l'image affichée. Le linker accepte pourtant cette
> configuration sans broncher. D'où un *second* segment pour les gros tampons.

Analyse complète des zones récupérables et des mesures :
**[SCOSWAMP/DOCS/MEMOIRE.md](SCOSWAMP/DOCS/MEMOIRE.md)**.

### Format des fichiers

- **Images SCOSWAMP** : flux `DHRR` — **exactement 16 384 octets décodés**,
  140×192, 16 couleurs. Chaque plan DHGR fait 7680 octets affichés + 512 octets
  de « screen holes » non affichés. Un fichier plus court est chargé
  partiellement et laisse des résidus de la scène précédente à l'écran.
- **Images SPACETRIP** : page HGR brute de 8192 octets.
- **Textes** : `TEXTFR/N###/N###.TXT` et `TEXTEN/N###/N###.TXT`
- **Choix** : `C <scene_id> <titre>` (la ligne commence par `C` + espace)

---

## 📚 Documentation

| Document | Contenu |
|----------|---------|
| [SCOSWAMP/SRC/README.md](SCOSWAMP/SRC/README.md) | Compilation et structure du moteur |
| [SCOSWAMP/DOCS/README-TEXTES.md](SCOSWAMP/DOCS/README-TEXTES.md) | Format des fichiers texte |
| [SCOSWAMP/DOCS/MEMOIRE.md](SCOSWAMP/DOCS/MEMOIRE.md) | Carte mémoire, zones récupérables, pièges cc65 |
| [SCOSWAMP/DOCS/PRODOS-MLI.md](SCOSWAMP/DOCS/PRODOS-MLI.md) | Gestion des chemins ProDOS |
| [ADVKIT/README.md](ADVKIT/README.md) | Le lecteur et l'atelier |
| [ADVKIT/IMAGES.md](ADVKIT/IMAGES.md) | Retoucher et reconvertir une image |
| [ADVKIT/RELEASE.md](ADVKIT/RELEASE.md) | Les images de `dist/` et leur publication |
| [SPACETRIP/README.TXT](SPACETRIP/README.TXT) | Architecture et guide complet |
| [TODO.md](TODO.md) | Backlog et journal des corrections |

Ce qui n'est pas suivi par git, et pourquoi : [`.gitignore`](.gitignore).

---

## 🐛 Dépannage

| Problème | Solution |
|----------|----------|
| Fichier non trouvé | Vérifier le format `N###` (3 chiffres) et les chemins |
| Choix absents | Les lignes doivent commencer par `C ` (C + espace) |
| Image corrompue | Lancer `./check-project.sh`, qui vérifie la taille décodée de chaque image |
| Texte manquant dans une langue | `./check-project.sh` détecte les scènes non appariées FR/EN |
| `make hdv` ne trouve pas `build_prodos_volume` | Il se construit par cmake depuis `ADVKIT/TOOLS` ; vérifier que les sources de POM2 sont en `../pom2` |

---

## 📦 Ressources

- **cc65** : https://cc65.github.io/ — documentation : https://cc65.github.io/doc/
- **POM2** : l'émulateur voisin, `../pom2`
- **Virtual ][** (macOS) : https://www.virtualii.com/
- **AppleWin** (Windows) : https://github.com/AppleWin/AppleWin
- **ProDOS 8** : https://prodos8.com/

---

## 👨‍💻 Auteur & Licence

**Arnaud VERHILLE** (@habib256)
Licence : **GNU GPL v3.0** — libre d'utiliser, modifier, distribuer

**SCOSWAMP** : adaptation de « Scorpion Swamp » (1985) par Steve JACKSON & Ian LIVINGSTONE
- ✅ Traduction anglaise complète : octobre 2024
- ✅ Images : 31 août 2026 (407 scènes + 32 combats, toutes en couleur)

**Remerciements** : équipe cc65, communauté Apple II, équipe Virtual ][
