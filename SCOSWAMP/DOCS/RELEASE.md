# Génération et publication des images disque

Les fichiers `.2mg` ne sont **pas versionnés** dans Git. Ce document explique
pourquoi, comment les régénérer, et comment les publier.

---

## Pourquoi les `.2mg` ne sont plus dans Git

Une image disque est un **artefact de build** : elle se reconstruit intégralement
à partir des fichiers du dépôt. La versionner pose trois problèmes :

1. **L'historique enfle définitivement.** Git stocke chaque version d'un binaire
   en entier (pas de delta utile sur une image disque). Chaque `git commit` d'un
   `.2mg` de 5 Mo ajoutait 5 Mo à l'historique, **pour toujours** — même après
   suppression du fichier. Le dépôt atteignait 58 Mo pour ~600 lignes de C.
2. **Aucun diff lisible.** « Update binary file ScoSwamp-0.5alpha.2mg » ne dit
   rien sur ce qui a changé. L'information utile est dans les fichiers sources.
3. **Risque de divergence.** Une image commitée peut ne plus correspondre aux
   sources du même commit, sans que rien ne le signale.

Les images sont donc publiées en **GitHub Release**, qui est faite pour ça :
binaires volumineux, versionnés par tag, hors historique Git.

> **Note.** Retirer les `.2mg` du suivi (`git rm --cached`) empêche les *futurs*
> ajouts, mais ne purge pas l'historique existant : les ~40 Mo déjà commités
> restent dans `.git`. Les supprimer vraiment demanderait de réécrire l'historique
> (`git filter-repo`), ce qui invalide tous les clones existants. À faire seulement
> si la taille du dépôt devient un problème concret, et jamais sans prévenir.

---

## Dimensionner le volume

Le volume doit être ajusté au contenu. L'ancienne image `SpaceTrip-0.1alpha.2mg`
faisait **32 Mo pour 340 Ko de contenu** — soit 99 % de vide, téléchargé par
chaque joueur.

| Projet | Contenu réel | Volume conseillé |
|--------|--------------|------------------|
| SCOSWAMP | ~4 Mo (hors `SRC/` et `DOCS/`) | 8 Mo |
| SPACETRIP | ~340 Ko (hors sources `.c` / `.h`) | 800 Ko |

Prévoir une marge d'environ 2× pour les images HGR à venir sur SCOSWAMP.
Maximum absolu d'un volume ProDOS : 32 Mo.

**Ne pas inclure dans l'image** : `SRC/`, `DOCS/`, `*.c`, `*.h`, `*.o`.
Ce sont des fichiers de développement, inutiles au joueur et coûteux en espace.

---

## Prérequis

Aucun de ces outils n'est requis pour développer — seulement pour produire une release.

- **Cadius** (macOS/Linux) — recommandé, gère nativement ProDOS et les types de fichiers
  https://github.com/mach-kernel/cadius
- **AppleCommander** (multiplateforme, Java) — alternative
  https://applecommander.github.io/

---

## Procédure

### 0. Vérifier avant de construire

```bash
./check-project.sh
```

Ne jamais produire une release si le script signale une erreur : une image HGR
à la mauvaise taille donne un affichage corrompu chez le joueur.

### 1. Compiler les moteurs

```bash
cd SCOSWAMP/SRC && make && cd ../..
cd SPACETRIP && cl65 -t apple2enh -O -Oirs \
    -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 -o SPACETRIP.BIN spacetrip.c paths.c && cd ..
```

### 2. Créer le volume (Cadius)

```bash
# SCOSWAMP — volume de 8 Mo
cadius CREATEVOLUME ScoSwamp-0.5alpha.2mg SCOSWAMP 8MB

cadius ADDFILE   ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/PRODOS.SYS
cadius ADDFILE   ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/BASIC.SYSTEM.SYS
cadius ADDFILE   ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/SCOSWAMP.BIN
cadius ADDFILE   ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/STARTUP.BAS
cadius ADDFOLDER ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/IMG
cadius ADDFOLDER ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/TEXTFR
cadius ADDFOLDER ScoSwamp-0.5alpha.2mg /SCOSWAMP/ SCOSWAMP/TEXTEN
```

Même principe pour SPACETRIP, avec `TXTFR` / `TXTEN` et un volume de 800 Ko.

### 3. Tester l'image avant publication

Monter le `.2mg` dans Virtual ][ ou AppleWin et vérifier :

- [ ] Le disque démarre sur ProDOS
- [ ] `]BRUN SCOSWAMP` lance le jeu
- [ ] La sélection de langue fonctionne (`F` / `E`)
- [ ] La scène N000 affiche son texte **et** son image
- [ ] La bascule image ↔ texte fonctionne (ESPACE)
- [ ] Au moins un choix mène bien à la scène attendue
- [ ] Une scène **sans** image ne plante pas (ex. N004)

### 4. Publier

```bash
git tag -a v0.5-alpha -m "SCOSWAMP 0.5 alpha : 402 scènes, 79 images"
git push origin v0.5-alpha
```

Puis, sur GitHub : **Releases → Draft a new release**, sélectionner le tag, et
joindre les `.2mg` en pièces jointes.

Indiquer dans la description : le nombre de scènes et d'images, les langues
disponibles, la configuration requise (Apple IIe Enhanced, 64 Ko, carte 80 colonnes),
et les limitations connues (scènes sans illustration, images non colorisées).

---

## Convention de nommage

```
<Projet>-<version><phase>.2mg

ScoSwamp-0.5alpha.2mg
SpaceTrip-0.1alpha.2mg
```

Le tag Git correspondant suit la forme `v0.5-alpha`.
