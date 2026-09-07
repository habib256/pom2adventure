# Propositions musicales — une musique par zone, pas une par page

Ce dossier est un **atelier**, pas le disque. Rien ici n'est copié dans
`SCOSWAMP/MUSIC/` tant que le propriétaire n'a pas écouté et tranché. La
conception qui les commande est dans **`DOCS/MUSIQUE-CLAIRIERES.md`**.

Chaque sous-dossier contient : la source Mutopia telle quelle (`.ly` et `.mid`),
la conversion `<NOM>.MB.BIN` par `../midi_to_mb.py`, le rendu `<NOM>.wav` (ignoré
par git, `.gitignore:76`) et un `README.md` qui dit ce qu'il couvre et pourquoi.

Le `.wav` **est** ce que la Mockingboard jouera : trois ondes carrées, la même
réduction, le même tempo. C'est le seul objet à écouter pour juger.

---

## 1. Les onze musiques

| Zone | Fichier disque | Pièce | Auteur, date | bpm | Durée | Octets |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `accueil` *(déjà sur le disque)* | `COMEAGAIN.MB` | Come Again | J. Dowland, 1597 | 120 | — | 478 |
| `village` | `VILLAGE.MB` | Il Est de Bonne Heure Né | Anonyme, c. 1470 | **150** | 48,0 s | 916 |
| `courbensaule` | `BENTBEAKS.MB` | Saltarello | V. Galilei, 1584 | **180** | 35,8 s | 553 |
| `sud` | `SOUTHSWAMP.MB` | Pavane « Belle qui tiens ma vie » | T. Arbeau, 1588 | **125** | 31,5 s | 574 |
| `nord` | `NORTHSWAMP.MB` | Tmeiskin | J. Japart, av. 1507 | **200** | 58,4 s | 1 058 |
| `riviere` | `RIVER.MB` | The Silver Swan | O. Gibbons, 1612 | **136** | 37,8 s | 719 |
| `danger` | `DANGER.MB` | Unquiet Thoughts | J. Dowland, 1597 | **140** | 55,6 s | 960 |
| `tour` | `TOWER.MB` | Pavan 2 | L. Milán, XVI<sup>e</sup> s. | **150** | 58,4 s | 548 |
| `combat` | `BATTLE.MB` | Bourrée en mi mineur BWV 996 | J. S. Bach, c. 1710 | **180** | 32,8 s | 644 |
| `mort` | `DEATH.MB` | Marche funèbre KV 453a | W. A. Mozart, 1784 | **120** | 32,3 s | 725 |
| `victoire` | `VICTORY.MB` | Old 100th | L. Bourgeois, c. 1550 | **150** | 39,2 s | 315 |

**Total sur le volume : 7 490 octets** (7 012 pour les dix nouvelles + 478 pour
`COMEAGAIN.MB`), sur ~28 Mo libres. La plus grosse pièce, `NORTHSWAMP.MB`
(1 058 o), fixe le plancher du tampon : **1 280 octets** suffisent, contre 2 560
déclarés aujourd'hui (`SCOSWAMP/SRC/music.h:11`).

**Licences.** Les onze pièces sont dans le **domaine public** (Creative Commons
No Rights Reserved chez Mutopia). Aucune n'est sous CC-BY-SA : c'est délibéré,
`DOCS/MUSIQUE.md § 6.5` rappelle que SCOSWAMP est distribué sous GPL v3 et que la
compatibilité en aval doit être vérifiée pièce par pièce.

---

## 2. Les 35 clairières → leur zone

Numérotation, `hub` et cases reprises de `SCOSWAMP.MORE/carte.json` et de
`SCOSWAMP/DOCS/CARTOGRAPHIE.md`. Le `hub` est l'identifiant stable du lieu ; la
colonne « pages » liste tout ce que la clairière contient (arrivée, revisites,
hubs secondaires).

| # | `id` | `hub` | Titre | (x,y) | **Zone** | Pages |
| ---: | ---: | ---: | --- | :---: | --- | --- |
| 1 | — | **078** | Route de Courbensaule | (0,0) | `courbensaule` | 280, 355, 78, 150, 408 |
| 2 | 19 | **234** | Le Patrouilleur vert | (2,0) | `nord` | 170, 363, 234 |
| 3 | 27 | **084** | Le Maître des Jardins | (3,0) | `nord` | 305, 238, 84, 117, 251, 283, 396 |
| 4 | 11 | **232** | Les deux loups | (4,0) | `nord` | 92, 232, 247, 389 |
| 5 | 15 | **218** | Feu follet à l'orée | (1,1) | `nord` | 218, 249 |
| 6 | — | **121** | Le croisement | (2,1) | `nord` | 121 |
| 7 | 7 | **161** | Le Géant | (4,1) | `nord` | 275, 342, 161, 103, 244 |
| 8 | 9 | **019** | Clairière aux brigands | (0,2) | `nord` | 65, 343, 19 |
| 9 | 28 | **153** | Le bassin de Vase | (1,2) | **`danger`** | 336, 137, 153 |
| 10 | 32 | **088** | Scorpion et nain | (2,2) | **`danger`** | 14, 338, 88 |
| 11 | 16 | **202** | Le nid de l'Aigle | (3,2) | `nord` | 350, 331, 25, 112, 202 |
| 12 | 30 | **270** | Sables mouvants | (4,2) | **`danger`** | 41, 382, 270 |
| 13 | 33 | **295** | La Rivière Croupie | (1,3) | `riviere` | 295 |
| 14 | 20 | **183** | Sommet de la falaise | (2,3) | `riviere` | 183 |
| 15 | 35 | **045** | **Le pont sur la rivière Croupie** | (3,3) | `riviere` | 138, 45, 101 |
| 16 | 14 | **304** | Le Perroquet / Maîtresse des Oiseaux | (0,4) | `sud` | 304, 149, 217 |
| 17 | — | **094** | La brume fétide | (1,4) | `sud` | 94 |
| 18 | 9 bis | **179** | Le pique-nique suspect | (2,4) | `sud` | 66, 192, 179 |
| 19 | 13 | **319** | La clairière des scorpions | (3,4) | **`danger`** | 118, 303, 319 |
| 20 | 3 | **047** | Trois chemins herbeux | (4,4) | `sud` | 47 |
| 21 | 21 | **031** | Bassin de cristal | (5,4) | `sud` | 31, 77, 394 |
| 22 | 23 | **367** | Les Fleurs d'Angoisse | (0,5) | **`danger`** | 204, 250, 367 |
| 23 | 29 | **348** | La Licorne | (1,5) | `sud` | 320, 265, 348 |
| 24 | 5 | **227** | La clairière des combats | (2,5) | `sud` | 10, 142, 227 |
| 25 | 24 | **187** | Herbe à Pinces | (3,5) | **`danger`** | 388, 263, 33, 187 |
| 26 | 26 | **309** | Orques des Marais | (4,5) | **`danger`** | 290, 323, 352, 309 |
| 27 | — | **125** | Cul-de-sac de la Bête | (0,6) | **`danger`** | 11, 210, 299, 125, 228, 243 |
| 28 | 18 | **022** | La clairière des Arbres-Épées | (1,6) | **`danger`** | 157, 279, 22 |
| 29 | 17 | **165** | Tente aux araignées | (3,6) | **`danger`** | 144, 345, 354, 165 |
| 30 | 8 | **230** | Clairière des grenouilles | (4,6) | `sud` | 53, 329, 230 |
| 31 | 34 | **044** | La rivière profonde | (1,7) | `riviere` | 90, 44, 254, 370 |
| 32 | 4 | **314** | Clairière du Maître des Loups | (1,8) | `sud` | 398, 239, 314 |
| 33 | **1** | **058** | **Le large rond-point (départ)** | (2,8) | `sud` | **195**, 24, 208, 58, 404, 405 |
| 34 | 12 | **390** | Pierres et tronc | (3,8) | `sud` | 105, 330, 390 |
| 35 | 25 | **082** | Bête du bassin | (4,8) | `sud` | 209, 82, 308, 397 |

**Répartition : `sud` 12 · `danger` 10 · `nord` 8 · `riviere` 4 ·
`courbensaule` 1.**

⚠ **Trois pages sont revendiquées par deux clairières** (`CARTOGRAPHIE.md:810-820`).
Les arbitrages sont déjà appliqués ci-dessus, et il faut les respecter en posant
les lignes `MU`, sinon deux clairières se disputeront la même musique :

| Page | Va à la clairière | Et non à |
| --- | --- | --- |
| 363 | `id` 19 — Le Patrouilleur vert (`nord`) | `id` 27 |
| 394 | `id` 21 — Bassin de cristal (`sud`) | `id` 3 |
| 330 | `id` 12 — Pierres et tronc (`sud`) | `id` 25 |

---

## 3. Les écrans et les pages hors clairière

296 des 412 pages n'appartiennent à aucune clairière (`CARTOGRAPHIE.md:929-930`).
La règle générale est que **la musique de la dernière clairière continue** ; les
exceptions ci-dessous sont les seules à porter une ligne `MU`.

| Ensemble | Pages | Zone |
| --- | --- | --- |
| Accueil | 000 | `accueil` |
| Prologue de Bourbenville | 001, 048, 095, 122, 240, 296, 173, 009 | `village` |
| Retour des missions | 159 | `village` |
| Sortie du Marais | 208 | `village` |
| **Tour de Stratagus** (14 pages) | 226, 225, 402, **124**, 222, 297, 298, 327, 349, 372, 373, 375, 401 | `tour` |
| **Combats** (32 pages, ligne `M`) | 012, 026, 028, 064, 079, 082, 120, **124**, 134, 146, 171, 176, 200, 211, 215, 221, 222, 224, 225, 235, 261, 267, 281, 284, 301, 312, 341, 355, 378, 379, 392, 402 | `combat` *(surcouche)* |
| **Morts** (11 pages) + écran `game_over` | 003, 030, 098, 260, 297, 313, 332, 361, 372, 375, 401 | `mort` *(surcouche, sans boucle)* |
| **Victoires** | 158, 175 | `victoire` *(sans boucle)* |
| Victoire amère de Stratagus | 358 | `tour` |
| Fins vivantes non victorieuses | 049, 052, 100, 141, 298, 327, 349 | zone courante, ou `MU -` |

Une page peut apparaître deux fois (124 est une page de tour **et** de combat,
297/372/375/401 sont des pages de tour **et** de mort) : c'est exactement ce que
règle la notion de **surcouche** du § 4 de `DOCS/MUSIQUE-CLAIRIERES.md` —
`MU +BATTLE.MB` remplace le thème pour une page, sans effacer la mémoire du
thème de zone, qui revient tout seul à la page suivante.

---

## 4. Si l'on veut descendre de onze à huit

Le propriétaire visait 6 à 10 musiques. Trois fusions possibles, par ordre de
coût artistique croissant :

1. **`village` disparaît dans `courbensaule`** — les deux sont des villes ;
   `BENTBEAKS.MB` (saltarello) sert de thème urbain unique. **−916 octets.**
2. **`riviere` disparaît dans `sud`** — la rivière n'est que quatre clairières,
   dont trois d'une seule page. **−719 octets.** C'est la fusion la plus
   regrettable : le pont est le seuil du jeu.
3. **`victoire` disparaît dans `village`** — la sortie du Marais et la victoire
   partagent la même respiration. **−315 octets.** La moins chère, et
   `VICTORY.MB` ne pèse que 315 octets, donc le gain est nul : à ne pas faire.

Recommandation : **garder les onze**. Le disque a 28 Mo libres, et le tampon ne
dépend que de la *plus grosse* pièce, pas de leur nombre.

---

## 5. Pièces écartées, gardées en réserve

| Pièce | Auteur | Mutopia | Pourquoi pas |
| --- | --- | --- | --- |
| Greensleeves | anonyme anglais, XVI<sup>e</sup> | déjà sur le disque, 630 o | Trop connue pour un lieu précis ; réserve idéale pour la Licorne (page 320) si l'on veut un jour une musique de clairière isolée. |
| Le Chant des Oyseaux | C. Janequin | id 796 | Superbe pour la clairière du Perroquet (304) et la Maîtresse des Oiseaux, mais une seule clairière ne justifie pas un fichier. |
| What power art thou (*Cold Song*) | H. Purcell | id 2243 | Le chromatisme descendant serait parfait pour `danger` ; écartée parce que la basse solo se réduit mal à trois voix égales. Deuxième choix ferme. |
| Es ist ein Ros' entsprungen | M. Praetorius, 1609 | id 1175 | Trop associée à Noël. |
| Belle qui tiens ma vie *(alt.)* | — | — | Déjà retenue pour `sud`. |
| `WELCOME.MB` | composition maison (`../accueil.py`) | — | 2 339 octets pour un thème d'accueil : elle coûte à elle seule deux fois le tampon proposé. À remplacer par `COMEAGAIN.MB`, déjà en place sur la page 000. |

---

## 6. Refabriquer tout le dossier

Les URLs Mutopia sont dans chaque `README.md`. Pour tout reconvertir depuis les
`.mid` déjà présents :

```sh
cd /Users/gistair/src/pom2adventure
M=SCOSWAMP.MORE/MUSIC ; P=$M/propositions ; C="python3 $M/midi_to_mb.py"
$C $P/village/bonne_heure.mid      $P/village/VILLAGE.MB.BIN       --bpm 150 --wav $P/village/VILLAGE.wav
$C $P/courbensaule/saltarello.mid  $P/courbensaule/BENTBEAKS.MB.BIN --bpm 180 --wav $P/courbensaule/COURBENS.wav
$C $P/sud/belle.mid                $P/sud/SOUTHSWAMP.MB.BIN          --bpm 125 --wav $P/sud/MARAISUD.wav
$C $P/nord/27-tmeiskin.mid         $P/nord/NORTHSWAMP.MB.BIN         --bpm 200 --wav $P/nord/MARAISNO.wav
$C $P/riviere/SilverSwan.mid       $P/riviere/RIVER.MB.BIN       --bpm 136 --wav $P/riviere/RIVIERE.wav
$C $P/danger/UnquietThoughts.mid   $P/danger/DANGER.MB.BIN         --bpm 140 --wav $P/danger/DANGER.wav
$C $P/tour/milan-pavan2.mid        $P/tour/TOWER.MB.BIN             --bpm 150 --wav $P/tour/TOUR.wav
$C $P/combat/bourree.mid           $P/combat/BATTLE.MB.BIN         --bpm 180 --wav $P/combat/COMBAT.wav
$C $P/mort/k453a.mid               $P/mort/DEATH.MB.BIN             --bpm 120 --wav $P/mort/MORT.wav
$C $P/victoire/Old100.mid          $P/victoire/VICTORY.MB.BIN     --bpm 150 --wav $P/victoire/VICTOIRE.wav
```

`--vol` reste au défaut `13,9,11` partout : mélodie en avant, voix médiane
retenue, basse au milieu. C'est le réglage des trois pièces déjà sur le disque
(`SCOSWAMP/SRC/Makefile:139-149`), et il n'y a aucune raison d'en changer avant
d'avoir écouté sur la carte.
