# Système de Combat Apple II

Un système de combat RPG complet pour Apple II, inspiré du document d'améliorations SPACETRIP.

---

## ⚠️ État actuel : prototype autonome

**Ce module fonctionne, mais n'est intégré à aucun des deux jeux.**

`combat.c` possède son propre `main()` et se compile en un exécutable séparé
(`COMBAT.BIN`, 14 490 octets). Ni SCOSWAMP ni SPACETRIP ne l'appellent : dans
`scoswamp.c`, seul un emplacement est réservé (mode vidéo `2`, « mode mixte »,
lignes 27 et 248), sans code d'appel.

C'est une **étape assumée** du projet. La feuille de route d'intégration est en
bas de ce document. Tant qu'elle n'est pas achevée, le module reste jouable
isolément via `]BRUN COMBAT`.

---

## Fonctionnalités

### Système de Joueur
- **Points de Vie (HP)** : 20 au départ, augmentent avec les niveaux
- **Attaque** : Force d'attaque, augmente avec les niveaux
- **Défense** : Protection contre les dégâts
- **Niveau** : Progression du joueur (1-5)
- **Expérience (XP)** : Points gagnés en combattant

### Système de Monstres
- **5 types de monstres** avec difficultés croissantes :
  1. **Spore Cosmique** (Facile) - HP:8, ATK:3, DEF:1, XP:10
  2. **Alien Vortex** (Moyen) - HP:18, ATK:6, DEF:3, XP:25
  3. **Robot Sentinel** (Moyen) - HP:22, ATK:7, DEF:5, XP:30
  4. **Baleine Celeste** (Difficile) - HP:30, ATK:10, DEF:6, XP:50
  5. **Guardian Magnetar** (BOSS) - HP:50, ATK:15, DEF:10, XP:100

### Mécaniques de Combat
- **Attaque** : Calcul des dégâts basé sur ATK - DEF/2 + random(0-3)
- **Défense** : Double la défense pour 1 tour
- **Fuite** : Chance de 50% + (niveau × 5)%
- **Montée de niveau** : HP max +5, ATK +2, DEF +1

### Interface
- **Mode HGR** : Affichage des images de monstres en haute résolution
- **Mode Texte** : Interface de combat avec barres de vie
- **Barre de statut** : HP, niveau, XP, stats en temps réel
- **Multilingue** : Français et Anglais

### Effets Sonores
- **Bip simple** : Actions de combat
- **Son de victoire** : Trio de bips pour les victoires
- **Son de défaite** : Bip grave pour les défaites

## Compilation

```bash
cd COMBAT/SRC
make
```

Le programme sera compilé dans `COMBAT.BIN` à l'adresse `$4000`.

## Utilisation

1. **Lancer le programme** : Le système de combat démarre automatiquement
2. **Choisir un monstre** : Sélectionner 1-5 pour combattre différents monstres
3. **Combat** :
   - `[A]` Attaquer
   - `[D]` Défendre (défense ×2 pour 1 tour)
   - `[F]` Fuir
   - `[Q]` Quitter
4. **Statistiques** : `[S]` pour voir les stats du joueur
5. **Langue** : `[L]` pour changer la langue

## Structure des Fichiers

```
COMBAT/
├── SRC/
│   ├── combat.c      # Code source principal
│   └── Makefile      # Configuration de compilation
├── IMG/
│   └── MONSTERS/     # Images HGR des monstres
│       ├── SPORE01.HGR
│       ├── ALIEN01.HGR
│       ├── ROBOT01.HGR
│       ├── SPACE01.HGR
│       └── BOSS01.HGR
└── README.md         # Ce fichier
```

## Images de Monstres

Les images HGR doivent être placées dans `IMG/MONSTERS/` :
- Format : HGR standard (8192 octets)
- Résolution : 280×192 pixels
- Nommage : Selon les noms définis dans le code

## Formules Techniques

### Dégâts de Combat
```
dégâts = max(1, ATK_attaquant - (DEF_défenseur / 2) + random(0,3))
```

### Chance de Fuite
```
chance = min(95, 50 + (niveau × 5))
```

### XP Requis pour Niveau
```
XP_requis(n) = 50 × n × (n-1) / 2
```

### Montée de Niveau
- **Niveau 1** : 0 XP (HP:20, ATK:5, DEF:3)
- **Niveau 2** : 50 XP (HP:25, ATK:6, DEF:4)
- **Niveau 3** : 120 XP (HP:30, ATK:8, DEF:5)
- **Niveau 4** : 220 XP (HP:35, ATK:10, DEF:6)
- **Niveau 5** : 350 XP (HP:40, ATK:12, DEF:8)

## Compatibilité

- **Apple IIe Enhanced** ou ultérieur
- **64 KB RAM** minimum
- **ProDOS** requis
- **Carte 80 colonnes** recommandée
- **cc65 compiler** pour la compilation

## Développement

Le code est structuré de manière modulaire :
- `init_player()` : Initialisation du joueur
- `init_monsters()` : Configuration des monstres
- `combat_loop()` : Boucle principale de combat
- `display_combat_screen()` : Interface de combat
- `calculate_damage()` : Calcul des dégâts
- `check_level_up()` : Vérification de montée de niveau

---

## 🗺️ Feuille de route d'intégration

Cinq obstacles séparent le prototype d'un système de combat jouable depuis
SCOSWAMP. Ils sont ordonnés : chacun dépend du précédent.

### Étape 1 — Budget mémoire : **mesuré, l'overlay est obligatoire**

Mesure effectuée avec cc65 2.19, `combat.c` privé de son `main()` et de son
`set_video_mode()` (voir étape 2), lié avec `scoswamp.c + paths.c + memory_swap.c`.

**La fusion statique ne tient pas.** Le lien réussit, mais le binaire produit
est inutilisable.

#### Ce que dit la taille du fichier (trompeur)

```
SCOSWAMP.BIN seul   13 388 o
COMBAT.BIN seul     14 490 o
somme brute         27 878 o
MERGED.BIN réel     21 343 o   ← 6 535 o économisés (runtime cc65 dédoublonné)
```

21 343 o passe sous les 22 016 o chargeables (`$9600 - $4000`). **On pourrait
croire que ça tient. C'est faux** : le `.BIN` ne contient pas le segment BSS.

#### Ce que dit le fichier `.map` (la vérité)

| Build | Fin de BSS | Plafond `$8E00` | Verdict |
|-------|-----------|-----------------|---------|
| SCOSWAMP seul | `$8516` | | ✅ 2 282 o de marge |
| SPACETRIP seul | `$79AC` | | ✅ |
| COMBAT seul | `$7A3B` | | ✅ |
| **Fusionné** | **`$A63C`** | | ❌ **dépasse de 6 204 o** |

L'empreinte totale passe de 17 686 o (SCOSWAMP seul) à **26 172 o**, pour
19 968 o disponibles (`$8E00 - $4000`). La BSS atterrit à `$92A6-$A63C`,
c'est-à-dire **au-dessus de `$9600`, en plein territoire ProDOS 8** : MLI, page
globale, buffers fichier. Le jeu se corromprait à la première ouverture de scène.

#### Pourquoi `ld65` ne dit rien

La zone BSS est définie ainsi dans `apple2enh.cfg` :

```
BSS: start = __ONCE_RUN__, size = __HIMEM__ - __STACKSIZE__ - __ONCE_RUN__;
```

Dans le build fusionné `__ONCE_RUN__` vaut `$92A6`, déjà au-delà du plafond
`$8E00`. La taille se calcule donc en **négatif** (−1190), déborde en non signé
vers ~4 Go, et le contrôle d'overflow est neutralisé. **Le link réussit sans le
moindre avertissement.**

Le contrôle fonctionne normalement quand la BSS démarre du bon côté : un test
avec un tableau de 30 Ko produit bien `Segment 'BSS' overflows memory area 'BSS'
by 10284 bytes`. Le piège ne se déclenche que dans ce cas précis — celui-ci.

**À retenir : ne jamais conclure d'un link réussi que le binaire tient.**
Toujours produire et lire le `.map`.

#### Solution : récupérer BASIC.SYSTEM — la fusion tient

Le plafond `$9600` n'est pas une limite matérielle. C'est la valeur prudente de
cc65, qui suppose BASIC.SYSTEM résident en `$9600-$BEFF` — ce qu'implique un
lancement par `]BRUN`. Un programme qui renonce à revenir au BASIC récupère ces
**10 496 octets**. La limite réelle est `$BF00`, page globale ProDOS.

C'est l'objet de [`SRC/apple2enh-game.cfg`](../SRC/apple2enh-game.cfg).

| | Config standard | Config étendue |
|---|---|---|
| `__HIMEM__` | `$9600` | `$BF00` |
| Plafond BSS + tas | `$8E00` | `$B700` |
| Utilisable depuis `$4000` | 19 968 o | **30 464 o** |

**Mesure de la fusion avec la config étendue** (`scoswamp.c + combat.c +
paths.c + memory_swap.c + prodos_quit.asm`) :

```
Chargement    : $4000
BSS           : $92B5 - $A64B
Tas           : $A64B - $B700  (4277 o)
Plafond       : $B700
Empreinte     : 26187 o sur 30464 o disponibles

OK : tient en mémoire, marge de 4277 octets.
```

**L'overlay n'est pas nécessaire.** Mieux : les 4 277 octets de tas restants
dépassent les 2 282 dont SCOSWAMP dispose aujourd'hui seul. Le jeu n'ouvrant
qu'un fichier à la fois (1 Ko de buffer ProDOS), la marge est confortable.

#### Contrepartie : sortir par MLI QUIT

La BSS et le tas s'étendent au-dessus de `$9600` et détruisent BASIC.SYSTEM en
cours de partie. `exit(0)` — utilisé aujourd'hui dans `scoswamp.c` ligne 381 —
rendrait la main à un programme qui n'existe plus.

Remplacer par [`prodos_quit()`](../SRC/prodos_quit.asm), qui invoque l'appel MLI
QUIT (`$BF00`, commande `$65`) :

```c
#include "prodos_quit.h"
...
    cprintf("Au revoir!\r\n");
    prodos_quit();          /* et non exit(0) */
```

#### Fausse piste écartée : la RAM basse

`$0800-$1FFF` (6 Ko) est libre puisque le chargement commence à `$4000`. Y
reloger la BSS paraît un gain facile — **c'est un piège**. Dans cc65 le tas
n'est pas un segment : `_heap.o` n'importe que `sp`, `__STACKSIZE__`,
`__BSS_SIZE__` et `__BSS_RUN__`, et pose `__heaporg = __BSS_RUN__ +
__BSS_SIZE__`. Le tas **suit la BSS**. Relogée en `$0800`, le tas part de
`$1B96` et traverse HGR page 1 puis tout le code : `fopen()` écraserait l'image
affichée. Testé, et accepté sans broncher par le linker.

`tools/check-memory.sh` refuse cette configuration.

#### Vérifier systématiquement

```bash
cl65 -t apple2enh -C ../../SRC/apple2enh-game.cfg -O -Oirs \
     -Wl -D,__EXEHDR__=0 -Wl -m,build.map -o SCOSWAMP.BIN \
     scoswamp.c combat.c paths.c memory_swap.c ../../SRC/prodos_quit.asm
./tools/check-memory.sh build.map --himem 0xBF00
```

`check-project.sh` contrôle la taille du `.BIN`, ce qui est nécessaire mais pas
suffisant : la BSS ne s'y trouve pas. Analyse complète dans
[DOCS/MEMOIRE.md](../DOCS/MEMOIRE.md), y compris la validation sur émulateur
restant à faire.

### Étape 2 — Éliminer les duplications

`combat.c` et `scoswamp.c` redéfinissent chacun de leur côté :

| Symbole | `scoswamp.c` | `combat.c` |
|---------|--------------|------------|
| `HGR_PAGE1` | ligne 12 | ligne 9 |
| `HGR_SIZE` | ligne 13 | ligne 10 |
| `MAX_LINE` | ligne 14 | ligne 11 |
| `MAX_PATH` | ligne 16 | ligne 14 |
| `set_video_mode()` | ligne 69 | ligne 127 |

Confirmé à la compilation — c'est la **première** erreur rencontrée :

```
ld65: Error: Duplicate external identifier: '_set_video_mode'
```

Seul `set_video_mode()` bloque le link : les autres sont des macros
préprocesseur, invisibles à l'édition de liens (mais à unifier quand même,
pour éviter qu'elles divergent).

**Les deux implémentations ne sont pas interchangeables** — c'est le point
important :

| | `scoswamp.c` (l. 69) | `combat.c` (l. 127) |
|---|---|---|
| Méthode | `switch_to_text/hgr/mixed()` via `memory_swap` | écriture directe des soft switches |
| Page texte 80 col. | **sauvegardée et restaurée** | perdue |
| Mode mixte (2) | géré | absent |
| État `app.video_mode` | mis à jour | non suivi |

Garder celle de COMBAT casserait le memory swap de SCOSWAMP — donc l'affichage
du texte après chaque retour de combat.

**Action** : supprimer la version de `combat.c` et utiliser celle de
`scoswamp.c`. À terme, extraire un module commun (`SRC/apple2_video.c` / `.h`)
avec les constantes HGR et `set_video_mode()`, partagé par les trois moteurs.

C'est la configuration dans laquelle la mesure de l'étape 1 a été faite.

### Étape 3 — Externaliser les données monstres

`init_monsters()` (lignes 180-227) code en dur les 5 monstres. C'est contraire à
la philosophie du projet : ajouter un monstre impose aujourd'hui une recompilation.

**Action** : créer `MONSTERS.DAT`, un fichier texte lu au chargement, sur le
modèle des fichiers de scènes :

```
M 01 Spore Cosmique|8|3|1|10|SPORE01.HGR
M 02 Alien Vortex|18|6|3|25|ALIEN01.HGR
    ^  ^            ^  ^ ^  ^  ^
    |  nom          HP | |  XP image
    id                ATK DEF
```

### Étape 4 — Créer un bestiaire médiéval-fantastique

Les 5 monstres actuels (Spore Cosmique, Alien Vortex, Robot Sentinel, Baleine
Céleste, Guardian Magnetar) viennent de l'univers SPACETRIP. **Aucun ne convient
au Marais aux Scorpions**, qui est médiéval-fantastique.

**Action** : définir un bestiaire tiré du livre-jeu (scorpions géants, hommes-lézards,
sangsues, gobelins des marais…), avec ses images HGR. Une fois l'étape 3 faite,
c'est du contenu pur, sans recompilation.

**Bonus** : SPACETRIP, qui est complet et dont les monstres actuels correspondent
déjà à l'univers, est la cible d'intégration la plus simple. **Intégrer COMBAT à
SPACETRIP d'abord** valide toute la chaîne technique (étapes 1 à 3) sans avoir à
produire de contenu neuf.

### Étape 5 — Persister l'état du joueur

`init_player()` réinitialise HP/XP/niveau à chaque combat. Dans un livre-jeu, la
progression doit survivre d'une scène à l'autre, et les blessures se cumuler.

**Action** : déplacer la structure `player` dans l'état global du moteur, et
l'initialiser une seule fois au démarrage de la partie. Prévoir la sauvegarde
sur disque (voir « Évolutions futures » du README principal).

### Point ouvert : doublons d'images monstres

`IMG/MONSTERS/` contient deux jeux de fichiers **au contenu différent** :

| Fichier | Référencé par `combat.c` |
|---------|--------------------------|
| `SPORE01.HGR`, `ALIEN01.HGR`, `ROBOT01.HGR`, `SPACE01.HGR`, `BOSS01.HGR` | ✅ oui (lignes 188-224) |
| `SPORE01.HGR.BIN`, `SPACE01.HGR.BIN`, `BOSS01.HGR.BIN` | ❌ non |

Les `.HGR.BIN` sont orphelins et ne sont pas de simples copies : leur contenu
diffère de celui des `.HGR` correspondants (`ALIEN01` et `ROBOT01` n'ont d'ailleurs
pas de variante `.BIN`). Il s'agit vraisemblablement de deux passes de conversion
différentes. **À trancher avant l'étape 3** : déterminer quelle version est la
bonne, supprimer l'autre, et uniformiser le nommage avec le reste du projet
(`.HGR.BIN` dans SCOSWAMP et SPACETRIP, `.HGR` ici).

---

## Auteur

**Arnaud VERHILLE** - @habib256
Port Apple II - 2025

Inspiré du document d'améliorations SPACETRIP et du code source spacetrip.c
