# Le Marais aux Scorpions - Compilation

Ce répertoire contient les sources C du programme "Le Marais aux Scorpions" pour Apple IIe Enhanced.

## Fichiers source

- `scoswamp.c` : Programme principal (affichage, navigation, boucle de jeu)
- `paths.c` : Gestion des chemins ProDOS (images HGR et fichiers texte)
- `paths.h` : En-têtes pour la gestion des chemins
- `memory_swap.c` : Système d'optimisation memory swap (sauvegarde/restauration écran texte)
- `memory_swap.h` : En-têtes pour le système memory swap

## Compilation

### Prérequis

- **cc65** : compilateur C pour 6502/65C02 (Apple II)
- Installation : https://cc65.github.io/

### Commandes Make

```bash
# Compiler le projet (crée SCOSWAMP.BIN dans le répertoire parent)
make

# Afficher la configuration
make info

# Recompiler complètement (nettoie puis compile)
make rebuild

# Nettoyer les fichiers intermédiaires (.o, .s)
make clean

# Nettoyer tout (inclut le binaire)
make distclean
```

### Compilation manuelle (sans Makefile)

```bash
# Avec cl65 (tout-en-un)
cl65 -t apple2enh -O -Oirs \
     -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 \
     -o ../SCOSWAMP.BIN scoswamp.c paths.c memory_swap.c

# Ou étape par étape
cc65 -t apple2enh -O -Oirs -o scoswamp.s scoswamp.c
cc65 -t apple2enh -O -Oirs -o paths.s paths.c
cc65 -t apple2enh -O -Oirs -o memory_swap.s memory_swap.c
ca65 -t apple2enh -o scoswamp.o scoswamp.s
ca65 -t apple2enh -o paths.o paths.s
ca65 -t apple2enh -o memory_swap.o memory_swap.s
ld65 -t apple2enh -D __EXEHDR__=0 -S 0x4000 \
     -o ../SCOSWAMP.BIN scoswamp.o paths.o memory_swap.o apple2enh.lib
```

**Flags importants :**
- `-t apple2enh` : Cible Apple IIe Enhanced (65C02)
- `-O -Oirs` : Optimisations (inline, registres, taille)
- `-Wl -S,0x4000` : Démarrage à $4000 (préserve HGR Page 1)
- `-Wl -D,__EXEHDR__=0` : Binaire brut sans en-tête AppleSingle

**Résultat :** `SCOSWAMP.BIN` (~14-16 KB, démarre à $4000)

## Structure ProDOS

Le programme s'attend à cette arborescence relative :

```
/SCOSWAMP/
  ├── SCOSWAMP.BIN        (binaire compilé)
  ├── BASIC.SYSTEM.SYS    (ProDOS BASIC.SYSTEM)
  ├── PRODOS.SYS          (noyau ProDOS)
  ├── STARTUP.BAS         (script de démarrage optionnel)
  ├── DHGR/
  │   ├── N000/           (scènes 0-49)
  │   │   ├── N000.RLE.BIN
  │   │   ├── N001.RLE.BIN
  │   │   └── ...
  │   ├── N050/           (scènes 50-99)
  │   └── ...
  ├── TEXTFR/             (textes français)
  │   ├── N000/
  │   │   ├── N001        (pas d'extension .TXT)
  │   │   └── ...
  │   └── ...
  └── TEXTEN/             (textes anglais)
      └── ...
```

**Important** : Les chemins sont conformes ProDOS (≤64 caractères, composants ≤15 caractères).

## Configuration

### Flags de compilation

- `-t apple2enh` : Cible Apple IIe Enhanced (80 colonnes, 65C02)
- `-O -Oirs` : Optimisations (inline, registres, taille)
- `-Wl -S,0x4000` : Adresse de démarrage à $4000
- `-Wl -D,__EXEHDR__=0` : Binaire brut ProDOS (pas d'en-tête)

### Mémoire

**Pourquoi démarrer à $4000 ?**

La page DHGR 1 occupe **$2000-$3FFF dans chacune des deux banques** (16 384 octets). Si le programme démarrait à l'adresse par défaut (~$0803), il écraserait la zone graphique principale. En démarrant à **$4000**, on préserve les deux plans DHGR.

```
$0000-$03FF : Zero page + Stack
$0400-$07FF : Zone texte (1024 octets, 40×24 caractères)
$0800-$1FFF : Zone libre système
$2000-$3FFF : DHGR Page 1 (8 Ko auxiliaires + 8 Ko principaux, flux DHRR)
$4000-$BFFF : Programme SCOSWAMP.BIN et données
$C000-$FFFF : ROM et I/O
```

- **Adresse de chargement** : $4000 (16384)
- **Page DHGR 1** : $2000-$3FFF dans les deux banques (16 384 octets, préservés)
- **Zone texte** : $0400-$07FF (1024 octets, sauvegardé par memory swap)
- **Memory swap backup** : ~2 KB (texte + choix)
- **Buffer I/O ProDOS** : 1 Ko par fichier ouvert (géré par libc)

## Optimisation Memory Swap

### Principe

Le système memory swap permet de basculer instantanément entre les modes HGR et texte sans recharger les données depuis le disque. Cela améliore considérablement l'expérience utilisateur.

### Fonctionnement

1. **Sauvegarde automatique** : Quand le mode HGR est activé, la zone texte ($400-$7FF) et les choix sont sauvegardés en mémoire
2. **Restauration instantanée** : Au retour en mode texte, le contenu est restauré directement depuis la sauvegarde
3. **Pas de rechargement** : Aucune lecture disque nécessaire lors des switches HGR ↔ Texte

### Performance

| Opération | Sans memory swap | Avec memory swap | Gain |
|-----------|------------------|------------------|------|
| Switch HGR → Texte | 200-500ms | 1-2ms | **100-250x** |
| Lecture disque | Oui | Non | **Éliminée** |
| Parsing fichier | Oui | Non | **Éliminé** |

### Modes vidéo supportés

- **Mode 0** : Texte 80 colonnes (navigation principale)
- **Mode 1** : HGR plein écran (affichage images)
- **Mode 2** : Mode mixte (réservé pour le futur système de combat)

### Commandes utilisateur

- **[ESPACE]** / **[RETURN]** / **[ESC]** : Cycle entre HGR et texte
- **[A-Z]** : Sélection des choix de scène
- **[Q]** : Quitter le programme
- **[F]** / **[E]** : Sélection langue (français/anglais, au démarrage)

### Fichiers du système

- `memory_swap.c` : Implémentation (sauvegarde/restauration, soft switches)
- `memory_swap.h` : Interface publique (fonctions `switch_to_*()`, `save_choices()`)

### Documentation

Voir `../DOCS/OPTIMISATION-MEMORY-SWAP.md` pour les détails techniques complets.

## Référence

Voir la documentation ProDOS MLI : `../DOCS/PRODOS-MLI.md`

## Auteur

VERHILLE Arnaud - @habib256
