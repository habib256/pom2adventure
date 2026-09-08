# Fichiers texte - Le Marais aux Scorpions

## 📊 Vue d'ensemble

- **Total de scènes** : 420 scènes de jeu (N000 à N419)
- **Fichiers français** : 420 fichiers .TXT (TEXTFR/) ✓ 100% complet
- **Fichiers anglais** : 420 fichiers .TXT (TEXTEN/) ✓ 100% complet
- **Support bilingue** : Français et Anglais intégralement traduits
- **Organisation** : Par tranches de 50 (N000/, N050/, N100/, etc.)
- **Conformité** : 100% des fichiers ≤18 lignes ✓

## 📐 Contraintes d'affichage

### Apple IIe Enhanced - Mode 80 colonnes

L'écran dispose de **24 lignes** totales :

```
Ligne 1    : Titre (ex: "T 001  Le chemin vers le Marais")
Ligne 3    : Ligne vide
Lignes 4-21: Texte de la scène (≤18 lignes)
Ligne 22   : Ligne vide
Ligne 23   : "--- Choix ---"
Lignes 24  : Choix (ex: "A) Tirer votre épée")
```

### Règle de limite

**Maximum 18 lignes de texte** (hors lignes de choix commençant par "C ")

Cette limite garantit :
- Affichage correct sans défilement
- Place pour les choix (2-3 lignes)
- Place pour les commandes (1 ligne)

## 📝 Format des fichiers

### Structure d'un fichier .TXT

```
001 : Titre de la scène
----------------------

Texte de description de la scène.
Plusieurs paragraphes possibles.

C 048 Choix numéro 1 (texte du choix)
C 095 Choix numéro 2 (texte du choix)
```

### Balises

- **Titre** : Numéro de scène suivi du titre
- **Séparateur** : Ligne de tirets
- **Texte** : Paragraphes de description
- **Choix** : Lignes commençant par `C` suivi de l'ID de scène et du texte

## 🔧 Optimisation effectuée

### Fichiers optimisés (9 au total)

| Fichier | Avant | Après | Gain | Réduction |
|---------|-------|-------|------|-----------|
| N001.TXT | 27 lignes | 16 lignes | -11 | -41% |
| N009.TXT | 22 lignes | 16 lignes | -6 | -27% |
| N048.TXT | 25 lignes | 15 lignes | -10 | -40% |
| N058.TXT | 19 lignes | 13 lignes | -6 | -32% |
| N095.TXT | 25 lignes | 16 lignes | -9 | -36% |
| N155.TXT | 21 lignes | 16 lignes | -5 | -24% |
| N240.TXT | 24 lignes | 16 lignes | -8 | -33% |
| N335.TXT | 23 lignes | 17 lignes | -6 | -26% |
| N371.TXT | 22 lignes | 18 lignes | -4 | -18% |

**Total** : 65 lignes supprimées, 30% de réduction moyenne

### Méthode d'optimisation

1. **Conservation totale** :
   - Histoire principale
   - Choix de jeu
   - Tests (CHANCE, ENDURANCE)
   - Informations critiques

2. **Condensation** :
   - Descriptions atmosphériques
   - Dialogues trop verbeux
   - Répétitions
   - Détails secondaires

3. **Qualité** :
   - Cohérence narrative préservée
   - Aucune information de jeu perdue
   - Style maintenu

## 📁 Organisation des dossiers

### Structure complète bilingue

```
TEXTFR/ (Version française - 420 fichiers)
├── N000/  (scènes 0-49)    → 50 fichiers
│   ├── N000.TXT (titre du jeu)
│   ├── N001.TXT
│   └── ...
├── N050/  (scènes 50-99)   → 50 fichiers
├── N100/  (scènes 100-149) → 50 fichiers
├── N150/  (scènes 150-199) → 50 fichiers
├── N200/  (scènes 200-249) → 50 fichiers
├── N250/  (scènes 250-299) → 50 fichiers
├── N300/  (scènes 300-349) → 50 fichiers
├── N350/  (scènes 350-399) → 50 fichiers
└── N400/  (scènes 400-419) → 20 fichiers

TEXTEN/ (Version anglaise - 420 fichiers)
├── N000/  (scenes 0-49)    → 50 fichiers
│   ├── N000.TXT (game title)
│   ├── N001.TXT
│   └── ...
├── N050/  (scenes 50-99)   → 50 fichiers
├── N100/  (scenes 100-149) → 50 fichiers
├── N150/  (scenes 150-199) → 50 fichiers
├── N200/  (scenes 200-249) → 50 fichiers
├── N250/  (scenes 250-299) → 50 fichiers
├── N300/  (scenes 300-349) → 50 fichiers
├── N350/  (scenes 350-399) → 50 fichiers
└── N400/  (scenes 400-419) → 20 fichiers
```

### Correspondance des fichiers

Chaque fichier français a son équivalent anglais :
- `TEXTFR/N000/N001.TXT` ↔ `TEXTEN/N000/N001.TXT`
- Les numéros de scène sont identiques
- La structure et les choix (C xxx) sont préservés
- Seul le texte narratif est traduit

## 🌍 Traduction anglaise

### Statut : 100% complète ✓

- **Date de traduction** : Octobre 2024
- **Fichiers traduits** : 420 fichiers (100%)
- **Méthode** : Traduction manuelle préservant :
  - Les numéros de scène
  - La structure des choix (C xxx)
  - Le gameplay et les références
  - L'atmosphère narrative

### Particularités

- Adaptation au contexte anglophone (gamebook genre)
- Respect des contraintes d'affichage (≤18 lignes)
- Terminologie cohérente :
  - `HABILETE` → `SKILL`
  - `ENDURANCE` → `STAMINA`
  - `CHANCE` → `LUCK`

## 📚 Documentation

- `OPTIMISATION-RAPPORT.txt` : Rapport détaillé de l'optimisation
- `FICHIERS-OPTIMISES.txt` : Liste rapide des fichiers modifiés
- `README-TEXTES.md` : Ce fichier

## ✅ Vérification

### Vérifier les limites de lignes (18 max)

Pour la version **française** :
```bash
for file in TEXTFR/*/*.TXT; do
    lignes=$(grep -v "^C " "$file" | grep -v "^$" | wc -l)
    if [ $lignes -gt 18 ]; then
        echo "$(basename $file): $lignes lignes (TROP LONG)"
    fi
done
```

Pour la version **anglaise** :
```bash
for file in TEXTEN/*/*.TXT; do
    lignes=$(grep -v "^C " "$file" | grep -v "^$" | wc -l)
    if [ $lignes -gt 18 ]; then
        echo "$(basename $file): $lignes lignes (TOO LONG)"
    fi
done
```

**Résultat actuel** : 
- Français : 0 fichiers trop longs ✓
- Anglais : 0 fichiers trop longs ✓

### Vérifier la correspondance FR ↔ EN

Le plus simple est de lancer le script de vérification du projet, qui contrôle
l'appariement FR ↔ EN scène par scène, les trous de numérotation et les fichiers
vides :

```bash
./tools/check-project.sh
```

Pour un comptage manuel rapide :

```bash
echo "Fichiers FR: $(find TEXTFR -name "*.TXT" | wc -l)"
echo "Fichiers EN: $(find TEXTEN -name "*.TXT" | wc -l)"
```

**Résultat attendu** : 420 fichiers dans chaque langue

## 🎯 Recommandations

Lors de la création de nouveaux textes :

1. ✅ Respecter la limite de 18 lignes
2. ✅ Être concis et percutant
3. ✅ Éviter les répétitions
4. ✅ Privilégier l'action sur la description
5. ✅ Tester l'affichage sur écran 80 colonnes

## 👨‍💻 Auteur

VERHILLE Arnaud - @habib256

**Dates importantes** :
- Optimisation française : 5 octobre 2024
- Traduction anglaise complète : 24 octobre 2024
- Statut : Version bilingue 100% opérationnelle ✓

## Les directives de page

Depuis 2026-08-29 une page ne porte plus seulement du texte et des choix : ce
qui se joue mecaniquement y est ecrit en clair, une directive par ligne.

| Ligne | Effet |
| --- | --- |
| `T <id> <titre>` | le titre, affiche en video inverse ligne 1 |
| `V <cible> [<page> ...]` | « si vous y etes deja venu, rendez-vous au `<cible>` » ; les numeros qui suivent sont les autres pages de la meme clairiere |
| `M <hab> <end> <nom>` | la creature de la clairiere |
| `MD <n>` | ses coups coutent n ENDURANCE (defaut 2) |
| `MS <n>` | le combat cesse a n ENDURANCE (defaut 0) |
| `E <CARAC> <delta>` | effet applique en entrant |
| `P <PIERRE> <n>` | Pierres Magiques recues |
| `PC <n> <cats>` | n Pierres a choisir parmi les categories N, B, M |
| `PD` / `PO` / `PX` | retire deux objets, un objet, ou tout le sac |
| `TR` | echange jusqu'a trois objets/amulettes contre autant de Pierres neutres |
| `G` / `GX` / `GA` | donne/retire un objet, ou remet les amulettes a Stratagus |
| `CI` / `CN` / `GU` | choix conditionne par un objet, eventuellement consomme |
| `CF <id> <titre>` | la Fuite, quand la page l'autorise |
| `CP <PIERRE> <id> <titre>` | choix qui remet une Pierre |
| `CU <PIERRE> <id> <titre>` | choix qui exige et consomme une Pierre |
| `C <id> <titre>` | choix ordinaire |
| `V <id>` | "si vous y etes deja venu, rendez-vous au <id>" -- doit preceder tout le reste de la page |

## Les pages synthetiques (400 et au-dela)

Le livre s'arrete au paragraphe 400. Au-dela, ce sont des pages que le portage
ajoute pour ce que le livre confiait au joueur ou a une phrase en passant.
Elles suivent exactement les memes regles que les autres et ne contiennent
aucun fait qui ne vienne du livre.

- **400-411** : les issues que le livre pliait dans une phrase (victoires
  enchainees, potions, sauts reussis).
- **412-418** : le prologue de Bourbenville. Le village devient un lieu qu'on
  parcourt avant de choisir un employeur : la place (412, longue, avec `V 413`
  vers sa version courte), la salle de la taverne (414), la boutique du vieil
  homme (415), le bout du village d'ou l'on voit la maison de Gayolard, celle
  de Pompatarte et la tour de Stratagus (416), l'Anneau de Cuivre et ses deux
  pouvoirs (417), et ce que le village raconte des trois missions (418). Le
  seul point d'entree est un choix ajoute a la page 240 ; toutes les sorties
  ramenent a la place, et la place ramene au 240. Les sept portent
  `MU VILLAGE.MB`, le theme du village, comme les pages 001, 095 et 240.
- **419** : la presentation, entre la Feuille d'Aventure et la route. La page
  000 y envoie son unique choix, `roll_character` joue au passage, et la 419
  dit qui est ce personnage : l'aventurier, la vieille femme de la route du
  Roi, l'Anneau de Cuivre et ses deux pouvoirs, et les trois hommes de
  Bourbenville. Elle garde `MU WELCOME.MB` : le theme d'accueil couvre
  desormais la creation du personnage et ne s'arrete qu'au 001, ou VILLAGE.MB
  prend le relais.

Ces huit pages n'ont pas encore d'illustration (comme 407 a 411) : une page
sans image tombe sur le texte, et le moteur le fait sans broncher.

La ligne `V` a deux particularites. Elle doit **preceder tout le reste de la
page** : le moteur court-circuite la page entiere des qu'il la lit, et une
ligne `E` ou `P` placee avant elle serait rejouee a chaque retour. Et elle
enumere la **clairiere**, pas la page : le livre dit « si vous *y* etes deja
venu », or une clairiere occupe plusieurs pages -- l'arrivee, la page-hub qui
porte les sentiers, la page de revisite ou un voisin depose parfois
directement. Le detour se declenche si la page courante, la cible, ou l'une
des pages citees a deja ete vue. Sans cette liste, revenir par un autre
sentier rejouait la premiere visite : creature ressuscitee, objets redonnes.

La plupart se **derivent de la prose** : `SCOSWAMP.MORE/TOOLS/reflow_txt.py
--derive` lit le bloc de stats que la page ecrit deja en toutes lettres et en
fait une ligne `M`. Le meme outil verifie les invariants de mise en page --
corps ≤ 19 lignes une fois replie a 78 colonnes, choix ≤ 4 lignes (ce sont
celles que le mode mixte laisse voir sous l'illustration), et pas un mot
change. A lancer apres toute retouche du corpus.
