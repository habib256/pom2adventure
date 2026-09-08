<!-- Déplacé le 2026-08-29 depuis ~/Emu/AppleII/apple2src/apple2adventure
     vers ~/src/pom2adventure, à côté de l'émulateur. Historique git conservé. -->

> **Hommage, gratuit, non commercial.** SCOSWAMP est un portage Apple II du
> *Marais aux Scorpions*, huitième volume des *Défis Fantastiques* de Steve
> Jackson et Ian Livingstone, illustré par Duncan Smith, paru chez Gallimard
> en 1985. L'œuvre appartient à ses auteurs et à son éditeur ; ce dépôt en est
> un hommage écrit par un lecteur, distribué librement sous GPL v3, dont
> personne ne tire un centime. Si un ayant droit souhaite qu'il disparaisse, il
> disparaîtra.

> **pom2adventure — l'atelier logiciel Apple II.**
>
> Dépôt distinct de [POM2](../pom2), qui est l'émulateur : ici on écrit les
> programmes *pour* la machine, chaîne cc65 `apple2enh` + ProDOS 8.
>
> Construire SCOSWAMP :
> `cd SCOSWAMP/SRC && make hdv` — relie le jeu, le lanceur ProDOS, et
> reconstruit `dist/SCOSWAMP.HDV`, l'image de travail.
> `make release` en tire les deux fichiers que télécharge un joueur :
> `dist/scoswamp-<version>.hdv` (blocs ProDOS bruts) et
> `dist/scoswamp-<version>.2mg` (les mêmes blocs, précédés des 64 octets
> d'en-tête que réclament les émulateurs qui refusent de deviner la géométrie
> d'un `.hdv`). Le numéro est tenu par `VERSION` dans `SCOSWAMP/SRC/Makefile`.
>
> Les règles de jeu se testent sur la machine hôte, sans émulateur :
> `cmake -S SCOSWAMP.MORE/TOOLS -B SCOSWAMP.MORE/TOOLS/build && cd $_ && ctest`.
>
> Test dans l'émulateur voisin :
> `../pom2/build/POM2 --preset iie <image.hdv>` — ajouter `--ai-control=PORT`
> pour le piloter sans les mains (HTTP sur la boucle locale ; attention, son
> parseur JSON ne décode pas les échappements `\uXXXX`, une touche de contrôle
> se passe en octet brut dans le corps de la requête).
>
> Le disque ne porte plus BASIC.SYSTEM : le jeu occupe sa place en mémoire et
> démarre par `SCOSWAMP.SYSTEM`, un lanceur ProDOS. Voir `SRC/loader.c`.
>
> Backlog : [`TODO.md`](TODO.md). Ce qui n'est pas suivi par git et pourquoi :
> [`.gitignore`](.gitignore).

**Solutions SCOSWAMP (révélations)** : [les trois parcours gagnants](DOCS/PARCOURS-GAGNANTS.md),
avec les pierres nécessaires, les embranchements, les variantes de fin et
le niveau de validation dans POM2.

**Code et mémoire SCOSWAMP** : [audit précis du binaire et optimisations](DOCS/AUDIT-MEMOIRE-SCOSWAMP.md),
avec inventaire par fonction, allocations et expériences de compilation reproductibles.

---

# Apple II - Moteurs de Jeu Pilotés par Données

Deux jeux d'aventure pour Apple IIe Enhanced démontrant une architecture moderne : moteur compact (~13 Ko) + contenu illimité sur disque ProDOS.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 📖 Philosophie

**Architecture pilotée par données** : le moteur reste en mémoire (~13 Ko), seule la scène actuelle est chargée depuis le disque.

**Avantages** :
- Contenu illimité (limité uniquement par l'espace disque, jusqu'à 32 Mo ProDOS)
- Ajout de scènes sans recompilation
- Contenu moddable par les joueurs
- Ratio efficacité : 1000:1 (contenu vs. empreinte mémoire)

---

## 📊 État du projet

> Les chiffres ci-dessous sont **produits par `./tools/check-project.sh`**, pas saisis à la main.
> Relancer le script après toute modification de contenu pour les mettre à jour.
> Dernière vérification : 31 août 2026 — 0 erreur.

| Module | Rôle | Moteur | Scènes | Textes | Images | État |
|--------|------|--------|--------|--------|--------|------|
| **SCOSWAMP** | Le Marais aux Scorpions (livre-jeu) | 13 322 o | 407 | 814 ✅ | 407 / 407 + 32 combats ✅ | ✅ Complet |
| **SPACETRIP** | Space Explorer Trip (aventure sci-fi) | 12 835 o | 14 | 28 ✅ | 14 / 14 ✅ | ✅ Complet |
| **COMBAT** | Système de combat RPG | 14 490 o | — | — | 5 monstres | 🔬 Prototype autonome, **non intégré** |

**Progression par axe** (pas de pourcentage global : les axes ne sont pas comparables)

```
SCOSWAMP  texte FR/EN   [####################] 100%  (804/804 fichiers)
SCOSWAMP  moteur        [####################] 100%
SCOSWAMP  images DHGR   [####################] 100%  (407/407 scènes + 32 combats)
SPACETRIP tout          [####################] 100%
COMBAT    prototype     [####################] 100%  (fonctionne isolément)
COMBAT    intégration   [....................]   0%  (voir COMBAT/README.md)
Distribution            [....................]   0%  (voir DOCS/RELEASE.md)
```

**Intégrité** : 439 images DHGR compressées (DHRR), toutes vérifiées comme se décodant en 16 384 octets exactement (8 Ko auxiliaires + 8 Ko principaux). Aucun trou de numérotation, aucune scène FR sans équivalent EN, aucun fichier texte vide.

### Vérifier soi-même

```bash
./tools/check-project.sh          # rapport complet
./tools/check-project.sh --quiet  # erreurs seules (code de sortie 1 si problème)
```

Le script valide les tailles HGR, l'appariement FR/EN, la continuité des scènes, la taille des moteurs face au budget mémoire, et l'absence d'artefacts de build versionnés.

---

## 🎮 SCOSWAMP - Le Marais aux Scorpions

Adaptation du livre-jeu « Scorpion Swamp » (1985) par Steve JACKSON & Ian LIVINGSTONE.

### Ce qui est terminé

- **402 scènes** (N000 → N401), livre-jeu complet adapté
- **Bilingue FR/EN** : 804 fichiers texte, appariement complet vérifié
- **Mode texte 80 colonnes** : lecture confortable et immersive
- **Bascule instantanée** image ↔ texte (ESPACE / RETURN / ESC)
- **Navigation par choix** : branches narratives interactives
- **Memory swap** : transitions optimisées

- **Toutes les scènes sont illustrées** : 407 images de page + 32 tableaux de
  bataille, en couleur, dans la palette DHGR à seize indices.

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
`build_manifest.py --stale` les nomme.

### Compilation

```bash
cd SCOSWAMP/SRC
make
```

Ou manuellement :
```bash
cl65 -t apple2enh -O -Oirs -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 \
     -o ../SCOSWAMP.BIN scoswamp.c paths.c
```

### Exécution

1. Monter `SCOSWAMP/` comme disque ProDOS (Virtual ][)
2. `]BRUN SCOSWAMP`
3. Choisir la langue : `F` (Français) ou `E` (English)

**Contrôles** : `ESPACE/RETURN/ESC` = basculer image/texte | `A-Z` = choix | `Q` = quitter

---

## 🚀 SPACETRIP - Space Explorer Trip

Aventure galactique interactive démontrant l'architecture pilotée par données. **Complet** : 14 scènes, 14 images, bilingue.

| Métrique | Valeur |
|----------|--------|
| Moteur | 12 835 o |
| Scènes | 14 (FR + EN) |
| Images DHGR | deux banques de 8 Ko par image, compressées sur disque |
| Fichiers texte | 28 (14 FR + 14 EN) |
| Ratio efficacité | 11:1 |

### Compilation

```bash
cd SPACETRIP
cl65 -t apple2enh -O -Oirs -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 \
     -o SPACETRIP.BIN spacetrip.c paths.c
```

### Ajouter du contenu (sans recompilation)

1. Créer `TXTFR/N015` et `TXTEN/N015` (description + choix)
2. Créer `IMG/N015.HGR` (8192 octets exactement)
3. Lier depuis une scène : ajouter `C 015 Titre du choix`
4. Terminé, jouable immédiatement. Valider avec `./tools/check-project.sh`.

---

## ⚔️ COMBAT - Système de combat RPG

Prototype **fonctionnel mais autonome** : 847 lignes de C, son propre `main()`, compilé
séparément en `COMBAT.BIN`. Il ne s'exécute pas depuis SCOSWAMP ni SPACETRIP à ce jour.

C'est une **étape assumée du projet**, pas du code mort : l'intégration est planifiée.
Le détail des mécaniques, les obstacles techniques identifiés et la feuille de route
en 5 étapes se trouvent dans **[COMBAT/README.md](COMBAT/README.md)**.

Résumé des obstacles à lever :

| # | Obstacle | Nature | État |
|---|----------|--------|------|
| 1 | **Budget mémoire** | config étendue | ✅ **résolu** |
| 2 | `set_video_mode()` dupliqué, avec deux comportements **incompatibles** | refactorisation | ✅ identifié |
| 3 | Données monstres codées en dur, contraires à l'architecture pilotée par données | `MONSTERS.DAT` | à faire |
| 4 | Bestiaire sci-fi inadapté à l'univers médiéval-fantastique de SCOSWAMP | contenu | à faire |
| 5 | Pas de persistance HP/XP entre les scènes | moteur | à faire |

> **Obstacle 1 levé.** Avec la config cc65 standard, la fusion débordait de
> 6 219 o dans la zone ProDOS — sans que `ld65` ne signale rien. En récupérant
> les 10 496 octets de BASIC.SYSTEM via [`SRC/apple2enh-game.cfg`](SRC/apple2enh-game.cfg),
> le binaire fusionné (26 187 o d'empreinte) **tient, avec 4 277 octets de tas** —
> soit plus que ce dont SCOSWAMP dispose aujourd'hui seul (2 282 o).
> L'overlay n'est plus nécessaire. Reste à valider sur émulateur, voir
> [DOCS/MEMOIRE.md](DOCS/MEMOIRE.md).

---

## 🛠️ Développement

### Prérequis

- **cc65** : `brew install cc65` (macOS) ou https://cc65.github.io/
- **Virtual ][** ou autre émulateur Apple II
- **Apple IIe Enhanced** (65C02), 64 Ko RAM, carte 80 colonnes

### Carte mémoire

```
$0000-$1FFF : Système ProDOS (page zéro, pile 6502, buffers)
$2000-$3FFF : DHGR Page 1 (8 Ko dans chacune des deux banques)
$4000-$8DFF : Moteur : CODE + RODATA + DATA + BSS  (19 968 o utilisables)
$8E00-$95FF : Pile C (__STACKSIZE__ = 2 Ko)
$9600-$BFFF : ProDOS 8 — MLI, page globale ($BF00), buffers fichier (1 Ko/fichier)
$C000-$FFFF : I/O et ROM
```

Démarrage à `$4000` pour préserver HGR Page 1 (`$2000-$3FFF`).

**`$9600-$BEFF` n'est pas perdu.** cc65 y suppose BASIC.SYSTEM résident — ce
qu'implique `]BRUN` — et fixe par prudence `__HIMEM__ = $9600`. Un programme qui
renonce à revenir au BASIC récupère ces **10 496 octets**. C'est l'objet de
[`SRC/apple2enh-game.cfg`](SRC/apple2enh-game.cfg) :

| | Config cc65 standard | `SRC/apple2enh-game.cfg` |
|---|---|---|
| `__HIMEM__` | `$9600` | `$BF00` |
| Utilisable depuis `$4000` | 19 968 o | **30 464 o** |
| BASIC.SYSTEM | préservé | détruit |
| Sortie | `exit()` | `prodos_quit()` obligatoire |

Deux contraintes distinctes, à ne pas confondre :

| Contrainte | Ce qu'elle limite | Vérifiée par |
|------------|-------------------|--------------|
| Taille du `.BIN` | CODE + RODATA + DATA + ONCE | `check-project.sh` |
| Empreinte exécution | **+ BSS + tas + pile** | `check-memory.sh` (lit le `.map`) |

Le `.BIN` **ne contient pas la BSS**, allouée au lancement. Un binaire de taille
acceptable peut donc déborder à l'exécution :

```bash
cl65 ... -Wl -m,build.map -o SCOSWAMP.BIN ...
./tools/check-memory.sh build.map                    # config standard
./tools/check-memory.sh build.map --himem 0xBF00     # config étendue
```

> **Piège `ld65`.** Si la BSS démarre déjà au-delà du plafond, la taille de sa
> zone se calcule en négatif, déborde en non signé, et le contrôle d'overflow
> est neutralisé : **le link réussit sans le moindre avertissement**. Seule la
> lecture du `.map` révèle le problème.

> **Piège du tas.** `$0800-$1FFF` (6 Ko) est libre, mais y reloger la BSS ne
> marche pas : dans cc65 le tas est câblé sur `__BSS_RUN__ + __BSS_SIZE__` et
> **suit la BSS**. Relogée en bas, le tas traverse HGR page 1 puis le code, et
> `fopen()` — 1 Ko par fichier ouvert — écrase l'image affichée. Le linker
> accepte pourtant cette configuration sans broncher.

Analyse complète des zones récupérables, mesures et validation restante :
**[DOCS/MEMOIRE.md](DOCS/MEMOIRE.md)**.

Marge actuelle de SCOSWAMP : BSS finit à `$8516`, soit 2 282 octets sous le
plafond standard, 12 778 sous le plafond étendu.

### Format des fichiers

- **Images** : flux `DHRR` — **exactement 16 384 octets décodés**, 140×192, 16 couleurs
  Chaque plan DHGR fait 7680 octets affichés + 512 octets de « screen holes » non
  affichés. Un fichier plus court est chargé partiellement et laisse des résidus
  de la scène précédente à l'écran.
- **Textes** : `TEXTFR/N###/N###.TXT` et `TEXTEN/N###/N###.TXT`
- **Choix** : `C <scene_id> <titre>` (la ligne commence par `C` + espace)

### Chemins ProDOS

```c
build_paths(5, "FR", ...) → "IMG/N005.HGR", "TEXTFR/N000/N005.TXT"
```

---

## 📚 Documentation

| Document | Contenu |
|----------|---------|
| [SCOSWAMP/SRC/README.md](SCOSWAMP/SRC/README.md) | Compilation et structure du moteur |
| [SCOSWAMP/DOCS/README-TEXTES.md](SCOSWAMP/DOCS/README-TEXTES.md) | Format des fichiers texte |
| [DOCS/MEMOIRE.md](DOCS/MEMOIRE.md) | Carte mémoire, zones récupérables, pièges cc65 |
| [DOCS/PRODOS-MLI.md](DOCS/PRODOS-MLI.md) | Gestion des chemins ProDOS |
| [DOCS/RELEASE.md](DOCS/RELEASE.md) | Génération et publication des images disque |
| [COMBAT/README.md](COMBAT/README.md) | Système de combat et feuille de route d'intégration |
| [SPACETRIP/README.TXT](SPACETRIP/README.TXT) | Architecture et guide complet |
| [DOCS/cc65/](DOCS/cc65/) | Documentation cc65 complète (HTML) |

> Le statut chiffré du projet vit **uniquement ici**, alimenté par
> `tools/check-project.sh`. L'ancien `SCOSWAMP/DOCS/PROJECT-STATUS.md` a été
> fusionné dans ce README pour éviter deux sources de vérité divergentes.

---

## 📦 Images disque

Les fichiers `.2mg` **ne sont pas versionnés** : ce sont des artefacts de build
régénérables, et les committer ajoutait 5 à 32 Mo à l'historique Git à chaque
mise à jour, de façon définitive.

Ils sont publiés en **GitHub Release**. Voir [DOCS/RELEASE.md](DOCS/RELEASE.md)
pour la procédure de génération et de publication.

---

## 🔮 Évolutions futures

Au-delà de l'intégration de COMBAT :

- **Inventaire** : objets, clés, armes, armures (moddables via fichiers)
- **Sauvegarde** : système multi-emplacements
- **Fichiers de données** : `MONSTERS.DAT`, `ITEMS.DAT`, `IMG/MONSTERS/*.HGR`

Le moteur resterait ~15-18 Ko, le contenu illimité sur disque.

---

## 🐛 Dépannage

| Problème | Solution |
|----------|----------|
| Fichier non trouvé | Vérifier le format `N###` (3 chiffres) et les chemins |
| Choix absents | Les lignes doivent commencer par `C ` (C + espace) |
| Graphiques corrompus | Les fichiers HGR doivent faire 8192 octets — lancer `./tools/check-project.sh` |
| Plantage au démarrage | Compiler avec `-Wl -S,0x4000` |
| Texte manquant dans une langue | `./tools/check-project.sh` détecte les scènes non appariées FR/EN |

---

## 📦 Ressources

- **cc65** : https://cc65.github.io/
- **Virtual ][** (macOS) : https://www.virtualii.com/
- **AppleWin** (Windows) : https://github.com/AppleWin/AppleWin
- **bmp2dhr** : convertisseur HGR
- **ProDOS 8** : https://prodos8.com/

---

## 🚀 Démarrage rapide

```bash
# 1. Installer cc65
brew install cc65  # macOS

# 2. Vérifier l'intégrité du dépôt
./tools/check-project.sh

# 3. Compiler
cd SCOSWAMP/SRC && make
cd ../../SPACETRIP && cl65 -t apple2enh -O -Oirs \
    -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 -o SPACETRIP.BIN spacetrip.c paths.c

# 4. Exécuter (Virtual ][)
# - Menu → « Mount Folder as ProDOS Disk » → sélectionner SCOSWAMP/ ou SPACETRIP/
# - ]BRUN SCOSWAMP (ou SPACETRIP)
# - F = Français, E = English
# - ESPACE = basculer image/texte, A-Z = choix, Q = quitter
```

---

## 👨‍💻 Auteur & Licence

**Arnaud VERHILLE** (@habib256)
Licence : **GNU GPL v3.0** — libre d'utiliser, modifier, distribuer

**SCOSWAMP** : adaptation de « Scorpion Swamp » (1985) par Steve JACKSON & Ian LIVINGSTONE
- ✅ Traduction anglaise complète : octobre 2024 (402 scènes, 804 fichiers)
- ✅ Images : 31 août 2026 (407 scènes + 32 combats, toutes en couleur)

**Remerciements** : équipe cc65, communauté Apple II, équipe Virtual ][

---

**Bon voyage dans l'univers rétro-moderne d'Apple II ! 🍎✨**
