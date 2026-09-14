# Cartographie du Marais aux Scorpions

**Référence complète et spécification exploitable pour la génération d'une carte.**

Relevé du 2026-09-03 sur `/Users/gistair/src/pom2adventure` : corpus français
`SCOSWAMP/TEXTFR/N*/N*.TXT` (412 pages), moteur `SCOSWAMP/SRC/scoswamp.c` +
`rules.c`, fichier de lien `SCOSWAMP/SRC/build.map`, et le fac-similé
`SCOSWAMP.MORE/Defis Fantastiques 08 - Le Marais aux Scorpions.pdf`.

Données structurées associées : **`SCOSWAMP.MORE/carte.json`** (13 313 octets,
35 clairières). Chaque chiffre de ce document a été recompté sur ce fichier ou
sur le corpus au moment de la rédaction.

Destinataires : le propriétaire du projet, et un générateur (script ou IA) qui
dessinera la carte du futur menu **MAP** (touche `M`).

---

## 1. Résumé

Le Marais tient en **35 clairières canoniques** posées sur une grille de
**6 × 9 = 54 cases** (35 occupées, 19 vides), reliées par **39 arêtes** dont 38
sont de vrais sentiers et une est le piège du Feu Follet. Ces 35 lieux sont
décrits par **116 pages** sur 412 : une clairière est toujours un *groupe* de
pages — première visite, revisites, variantes de récit, page-hub qui porte les
directions — jamais une page unique. **La carte doit donc être indexée par
clairière, non par page** : un index par page afficherait le même lieu jusqu'à
quatre fois (6 numéros du livre portent deux pages, 26 lignes `V` créent 26
paires aller/retour, d'autres pages de revisite existent en plus). La rivière Croupie
coule d'est en ouest sur la ligne `y = 3` et le **pont** (clairière 35) est le
seul passage entre les 12 clairières du nord et les 23 du sud. Le départ est la
page 195 = clairière 1, case (2,8). Le graphe complet compte 412 nœuds, 743 arcs,
0 cible manquante, 21 pages terminales, **1 seule page inaccessible** — la 000,
l'écran d'accueil, où le moteur entre sans qu'un choix y mène (§ 6.2). Le moteur possède
déjà tout l'état nécessaire : 52 octets de bitmap `visited`, sauvegardés.

---

## 2. Organisation des textes

### 2.1 Arborescence et nommage

```
SCOSWAMP/
├── TEXTFR/   412 .TXT (188 810 o)   N000/…N350/ : 50 fichiers ; N400/ : 12
├── TEXTEN/   412 .TXT (167 310 o)   même arbre, mêmes numéros
├── IMG/      439 .RLE.BIN : 407 illustrations Nxxx + 32 batailles Bxxx
├── MSGFR.TXT / MSGEN.TXT  55 lignes chacun (catalogue d'interface)
├── OBJFR.TXT / OBJEN.TXT  11 lignes (objets et drapeaux)
├── HELPFR.TXT / HELPEN.TXT / TITLE.TXT
└── SAVE/     emplacements PARTIE0-9
```

Le bucket est **`(id / 50) * 50`** sur trois chiffres : la page 137 vit dans
`N100/N137.TXT`. Le moteur refait ce calcul dans `enter_asset_dir()`
(`scoswamp.c:279-289`) et navigue **composant par composant** (`chdir("/SCOSWAMP")`,
`chdir("TEXTFR")`, `chdir("N100")`) parce que le runtime cc65/ProDOS refuse les
noms multi-composants dans `fopen` ; le découpage en buckets de 50 répond à la
limite du répertoire ProDOS (51 slots à la racine) et à sa recherche linéaire.
`N000` est l'écran d'accueil du portage, `N001`…`N401` les 401 paragraphes du
livre un pour un, `N402`…`N411` dix **pages relais** ajoutées par le projet.

### 2.2 Format d'une page

```
T 010 La clairiere des combats      ← ligne T : id + titre, vidéo inverse ligne 1
V 142                               ← directive V, obligatoirement AVANT tout le reste
                                    ← ligne vide (avalée par le moteur)
Vous franchissez des arbres noueux et entrez dans une nouvelle clairiere.
…                                   ← le corps, déjà replié à 78 colonnes
Que faites-vous ?
                                    ← ligne vide
C 059 Examiner la clairiere et chercher des indices
C 227 Quitter la clairiere au plus vite et partir
```

Ordre canonique imposé par `render()` de `reflow_txt.py` : `T`, lignes `V`, corps,
lignes `ED`, autres directives, lignes de choix. **L'ordre du fichier n'ordonne
pas l'exécution** : `load_scene` joue le dé et le combat quand il veut, la
position des lignes est pour l'œil. Le découpage est fait *en place*
(`parse_text_file`, `scoswamp.c:1086-1099`) : chaque fin de ligne devient un
`'\0'`, le moteur ne garde que des pointeurs dans `file_buffer`. L'alternance qui
reconnaît une directive — **l'ordre fait foi**, les préfixes de deux lettres
devant la lettre seule, sinon `M ` avalerait `MV` :

```
^(MD|MS|MV|MB|M|E0|ED|E|PC|PD|PO|PX|P|TR|CF|CP|CU|CI|CN|CA|CL|CE|CS|DV|GU|GX|GA|G|V)(?: |$)
```

### 2.3 Les 31 directives

Comptes mesurés le 2026-09-03 sur les 412 fichiers de `TEXTFR` ; « Occ. » =
lignes, « Pg » = fichiers distincts.

| Ligne | Syntaxe | Sens | Occ. | Pg |
| --- | --- | --- | --- | --- |
| `T` | `T <id> <titre>` | titre, ligne 1 en vidéo inverse ; sert de libellé de sauvegarde (32 o) | 412 | 412 |
| `C` | `C <id> <titre>` | choix ordinaire — **c'est là que vivent les directions** | 567 | 334 |
| `E` | `E <CARAC> <±delta>` | effet à l'entrée dans la page | 44 | 40 |
| `CU` | `CU <PIERRE> <id> <titre>` | choix qui **exige et consomme** une Pierre | 43 | 17 |
| `M` | `M <hab> <end> <nom>` | un adversaire, une ligne par créature ; `MAX_FOES = 3` | 42 | 32 |
| `MV` | `MV <id>` | après le dernier adversaire tombé, saut sans repasser par les choix | 31 | 31 |
| `CL` | `CL <ok> <ko> [<dok> <dko>]` | Chance qui **branche**, effet d'ENDURANCE optionnel par branche | 16 | 16 |
| `G` | `G <OBJET\|AMULETTE>` | donne un objet ou une amulette | 16 | 16 |
| `CF` | `CF <id> <titre>` | la Fuite, quand la page l'autorise | 15 | 15 |
| `V` | `V <id>` | « si vous y êtes déjà venu, rendez-vous au `<id>` » ; **court-circuite toute la page** | 14 | 14 |
| `ED` | `ED <CARAC> <±ndés>` | jet de dés **visible** ; signe = gain/perte, valeur absolue = nb de dés | 9 | 9 |
| `CI` | `CI <OBJET> <id> <titre>` | choix disponible **si** on possède l'objet | 6 | 5 |
| `GX` | `GX <OBJET>` | retire un objet | 5 | 5 |
| `CN` | `CN <OBJET> <id> <titre>` | choix disponible **si on ne le possède pas** | 4 | 4 |
| `CA` | `CA <lo> <hi> <id> <titre>` | choix ouvert si le nb d'amulettes ∈ `[lo,hi]` (encodé `(lo<<4)\|hi`) | 4 | 2 |
| `CE` | `CE <CARAC> <dok> <dko>` | Chance **qui ne branche pas** : décide d'un effet, la page continue | 4 | 4 |
| `P` | `P <PIERRE> [<n>]` | le sorcier vous donne n Pierres (défaut 1) | 4 | 2 |
| `PC` | `PC <n> <cats>` | il vous en laisse **choisir** n parmi `N`/`B`/`M` | 4 | 4 |
| `CS` | `CS <STAT> <ok> <ko>` | « Lancez deux dés » contre la caractéristique, **gratuit** | 3 | 3 |
| `GA` | `GA <n>` | remet les amulettes à Stratagus, récompense selon le compte | 3 | 3 |
| `DV` | `DV <max> <id>` | cascade : la 1re ligne dont la perte du dernier combat est ≤ `<max>` | 3 | 1 |
| `GU` | `GU <OBJET> <id> <titre>` | possède **et consomme** | 2 | 2 |
| `MD` | `MD <n>` | les coups du **dernier** `M` coûtent n ENDURANCE (défaut 2) | 2 | 2 |
| `MS` | `MS <n>` | le combat cesse à n ENDURANCE (défaut 0) ; idem | 2 | 2 |
| `E0` | `E0 <CARAC> <±delta>` | déplace le **total de départ** (perte définitive, plafond relevé) | 2 | 2 |
| `MB` | `MB <ok> <ko>` | duel au premier sang | 1 | 1 |
| `PD` / `PO` / `PX` | *(sans argument)* | retire deux objets / un objet / **tout le sac** | 1 / 1 / 1 | 1 |
| `TR` | *(sans argument)* | échange ≤ 3 objets ou amulettes contre autant de Pierres neutres | 1 | 1 |
| `CP` | `CP <PIERRE> <id> <titre>` | choix qui **remet** une Pierre | **0** | **0** |

**31 directives reconnues, 30 employées** (`CP` implémentée, jamais utilisée).
`<CARAC>` ∈ `{ENDURANCE, HABILETE, CHANCE, OR, BONUS}`, en français dans les deux
corpus (c'est de la mécanique) ; le moteur n'en lit que l'**initiale**
(`carac_of`, `scoswamp.c:582`), c'est `reflow_txt.py` qui refuse un mot mal
orthographié. Le garde de `V` est en tête de `classify_line`
(`if (app.revisit >= 0) return;`), d'où l'invariant « la ligne `V` précède tout le
reste » : une ligne `E` placée avant elle donnerait deux fois ce qu'on a déjà pris.

### 2.4 Les directives porteuses de cibles — ce qui alimente une carte

| Directive | Champ(s) cible | Type d'arc |
| --- | --- | --- |
| `C <id> <t>` / `CF <id> <t>` / `MV <id>` / `V <id>` | 1 | `C`, `CF`, `MV`, `V` |
| `CI`/`CN`/`GU <OBJ> <id> <t>` | 2 | `CI`, `CN`, `GU` |
| `CU`/`CP <PIERRE> <id> <t>` | 2 | `CU`, `CP` |
| `DV <max> <id>` | 2 | `DV` |
| `CA <lo> <hi> <id> <t>` | 3 | `CA` |
| `CL <ok> <ko> [dok dko]` | 1 et 2 | `CL[0]` Chanceux, `CL[1]` Malchanceux |
| `CS <STAT> <ok> <ko>` | 2 et 3 | `CS[0]`, `CS[1]` |
| `MB <ok> <ko>` | 1 et 2 | `MB[0]`, `MB[1]` |

⚠ **`CE <CARAC> <dok> <dko>` n'est pas un arc** : ses deux nombres sont des deltas
de caractéristique. C'est le seul piège du format — quatre occurrences
(`CE ENDURANCE 0 -1` en 058, `0 -2` en 073 et 190, `CE HABILETE 0 -1` en 249) qu'un
extracteur naïf transformerait en 8 faux arcs, dont quatre vers une « page 0 ».

**Le corpus n'a aucune notion de direction** : ni directive, ni champ. Les
directions n'existent que dans le **libellé français des lignes `C`** —
`C 170 Aller vers le nord`, `C 275 Aller vers l'est`, `C 218 Aller vers l'ouest`
(page 121, « Le croisement »). **58 pages** portent au moins un choix
directionnel, pour **111 choix**, tous cardinaux : aucune diagonale, aucun « à
gauche / à droite / tout droit » dans les 412 pages, donc une grille orthogonale
suffit. Le piège est le mot **« est »**, qui est aussi le verbe *être* :
`\best\b` ramasse cinq faux positifs (095, 267, 243, 225, 179) ; le filtre correct
teste des contextes explicites (`vers l'est`, `a l'est`, `l'est\b`, `sentier est`, …).

### 2.5 Les pages 402-411

Pages **relais** : elles portent un effet mécanique que le livre résout en prose
au milieu d'un paragraphe, et que le moteur ne sait exprimer qu'en entrant dans une page.

| Page | Rôle | Appelée depuis |
| --- | --- | --- |
| 402 | Colère de Stratagus blessé — jumelle de la 225 : `M 9 8 STRATAGUS`, `MV 140` | 373 (`CL` Chanceux) |
| 403 | Le bond parfait : `E CHANCE +2` | 257 (`CS` réussi) |
| 404 | De l'autre côté — **re-propose les trois directions** | 091 (`CS` réussi) |
| 405 | La chute dans la vase : `E HABILETE -1`, **mêmes trois directions** | 091 (`CS` échoué) |
| 406 | Les dards des Scorpions : `E ENDURANCE -3` | 377 (`CS` échoué) |
| 407 | L'objet donné aux Brigands : `PO` | 128 |
| 408 | Échange chez Alphonse : `TR` | 150 |
| 409 / 410 / 411 | Potions : `E HABILETE/ENDURANCE/CHANCE +99` | 164 |

Deux conséquences : **404 et 405 sont le même lieu vu deux fois** (réussite ou
chute), sorties identiques `O→398 / E→105 / S→208` — deux pages-hub de la
clairière 1 ; et 402 double la 225. Les pages 407-411 sont les **5 seules pages du
corpus sans illustration** (`IMG/` s'arrête à `N406`).

### 2.6 Contraintes d'affichage et de taille

L'écran est réparti en dur sur ses 24 lignes (`scoswamp.c:44-61`) : ligne 1, barre
de titre en vidéo inverse (titre + rappel des touches, `title_bar[81]`) ; lignes
2-20, le texte (`BODY_ROW0 = 1`, **`BODY_ROWS = 19`**) ; lignes 21-24, les choix
(`CHOICE_ROW0 = 20`, `CHOICE_ROWN = 23`). Les 4 lignes du bas sont **exactement**
celles que le mode mixte laisse voir sous l'image HGR : on choisit sans quitter
l'illustration. *(Le `README-TEXTES.md` parle encore d'un « maximum 18 lignes » :
c'est un format antérieur, `reflow_txt.py` replie à 19 lignes de 78 colonnes.)*

| Borne | Valeur | Vérifiée par |
| --- | --- | --- |
| corps replié | ≤ 19 lignes × 78 colonnes | `reflow_txt.py:740` |
| lignes de choix rendues | ≤ 4 (2 par ligne si les deux tiennent en 39 col.) | `choice_rows()`, `:786` |
| nombre de choix | ≤ 5 (`MAX_CHOICES`) | `:776` |
| adversaires | ≤ 3 (`MAX_FOES`) | `derive_combat` |
| titre de choix / de page | ≤ 76 (mesuré 63) / ≤ 60 (mesuré 39) caractères | `:782`, `:800` |
| **taille du fichier** | ≤ **1252 octets** (`FILE_BUFFER_SIZE − 1`) | `:790` |
| jeu de caractères | **ASCII pur, sans accents** — l'Apple II n'en affiche pas | `:797` |

`FILE_BUFFER_SIZE = 1253` est **calé sur la page la plus longue du corpus** :
`TEXTFR/N350/N361.TXT`, remesurée à 1 252 octets — la borne est atteinte à
l'octet. Le tampon vit en `LOWBSS` (`$1000-$1FFF`). Autres mesures : 458,3 octets
par page en moyenne, 0 caractère non ASCII, 0 fichier en CRLF.

### 2.7 La chaîne d'outils

| Outil | Rôle |
| --- | --- |
| `TOOLS/reflow_txt.py` (865 l.) | **la pièce maîtresse.** Reformate (replie à 78 col., remet les lignes dans l'ordre canonique, refuse de changer un mot : `if words(w) != words(body): problems.append(...)`), valide tous les invariants du § 2.6, recoupe la mécanique FR ↔ EN, et **dérive** la mécanique restée en prose (`--derive`) : `derive_combat`, `derive_revisit` (→ `V`), `derive_luck` (→ `CL`), `derive_dice` (→ `ED`), `derive_effects`, `derive_stone_use` (→ `CU`), `derive_win` (→ `MV`) **en dernier**, parce que `MV` se décide au compte des choix restants. État : 62 fichiers à reformater, **0 problème** |
| `TOOLS/fix_typos.py` (193 l.) | répare les dégâts de la désaccentuation par table (`maeitre → maitre`, `gant → geant`), établie en comparant le vocabulaire du corpus à celui du PDF |
| `TOOLS/build_messages.py` (151 l.) | **source unique** des messages d'interface : écrit `messages.h` **et** `MSGFR.TXT`/`MSGEN.TXT` (55 lignes) d'un même geste. « L'ORDRE FAIT FOI, il fixe les indices » ; `messages_load` refuse un fichier qui n'a pas exactement `MSG_COUNT` lignes |
| `TOOLS/build_objects.py` (48 l.) | source unique de `OBJFR.TXT`/`OBJEN.TXT` : 11 bits nommés, dont 1 drapeau caché (`.T`) ; l'ordre des lignes fixe le numéro de bit |
| `TOOLS/build_manifest.py` (453 l.) | `scene_manifest.jsonl` (407), `battle_manifest.jsonl` (32), `ref_manifest.jsonl` (74). C'est son `refs_for` qui, en cherchant les `aliases` de `decors.json` dans la prose, établissait le lien page → numéro de clairière |
| `SCOSWAMP.MORE/decors.json` | **la bible topologique** : 39 décors dont **29 `CLAIRIERE_NN`** (01 03 04 05 07 08 09 11 12 14 15 16 17 18 19 20 21 23 24 25 26 27 28 29 30 32 33 34 35 — pas de 13), chacun avec ses `aliases` et un `look` canonique qui **dit le nombre de chemins** (« three narrow paths leaving south, east and west » pour la 3) |

### 2.8 Le graphe des 412 pages

| Mesure | Valeur |
| --- | --- |
| nœuds / arcs | **412** / **743** (729 avant les correctifs du § 6.2) |
| **cibles inexistantes** | **0** — les 743 cibles pointent toutes sur un fichier existant |
| atteignable depuis 001 | **411** / 412 ; **1 seule page inaccessible**, la page de titre 000 |
| composantes faiblement connexes | **1** — le corpus tient d'un seul morceau |
| composantes fortement connexes | **84** ; la plus grande = **316 pages** (le cœur navigable du Marais), la 2ᵉ = 14 (l'épisode de la tour de Stratagus) ; 82 singletons |
| degré sortant max | **5** — pages 119, 152, 191, 256, 336, 374, 387 |
| pages terminales (aucune cible) | **21** |

**Les 21 pages terminales** : 003, 030, 098, 260, 297, 313, 332, 361, 372, 375, 401
(11 morts) ; 049, 052, 100, 141, 298, 327, 349 (7 fins vivantes non
victorieuses) ; **158, 175, 358 — les trois victoires**. Trois employeurs, donc
trois fins heureuses : il n'y a **pas une page finale unique**. La mort par
ENDURANCE nulle ne passe par aucune page (`die_and_restart()` → `game_over()`,
`scoswamp.c:1716`).

**Les pages les plus visitées sont, sans exception, des carrefours de la carte** —
meilleur signal automatique pour poser les nœuds : 019 (11 entrants), 161, 348,
363 (9), 234, 336 (8), 281, 398, 314, 124 (7), 088, 342, 390, 202, 047 (6).

**Les pages inaccessibles** étaient 19 au relevé initial : 000 (page de titre,
normal), 106, 108, 126, 129, 143, 168, 178, 181, 190, 210, 223, 243, 329, 338,
345, 364, 380, 382. Les douze lignes `V` manquantes et les trois liens rétablis
du § 6.2 les ont toutes ramenées dans le graphe : **il ne reste que la 000**, où
le moteur entre au lancement sans qu'aucun choix y mène.

---

## 3. Le modèle spatial du livre et du jeu

### 3.1 La règle du livre

Le Marais aux Scorpions est le seul *Défis Fantastiques* où le lecteur **doit**
dessiner sa carte. Le livre y consacre une section (PDF p. 14-15) qui est le
cahier des charges du menu MAP :

> Pour vous aider à établir votre carte, **toutes les clairières ont été
> numérotées**. […] **ces sentiers sont orientés au nord, au sud, à l'ouest ou à
> l'est. Parfois, un sentier peut suivre un tracé sinueux mais sa direction
> générale restera toujours la même.** […] si par exemple vous quittez une
> clairière en empruntant un sentier orienté au sud, vous entrerez automatiquement
> dans la clairière suivante par le nord et inversement.

Et p. 15, sur le plan-modèle en fac-similé — une grille de cercles numérotés
reliés par des `—` et des `|`, avec un `?` au bout de chaque sentier non encore
emprunté : « ce joueur a pris soin de noter **le numéro de chaque clairière** ainsi
que **le nom des créatures** qu'il y a rencontrées. Il a également **tracé les
sentiers** […] ce qui lui permettra […] de savoir par avance dans quelles
directions il pourra poursuivre son chemin. »

Quatre conséquences pour le format de données : le nœud porte **le numéro de
clairière**, pas celui du paragraphe ; il porte **le nom de la créature** et son
état (« tué ») ; un sentier **connu mais non emprunté** se note d'un rayon terminé
par `?` ; et **les sentiers peuvent être longs** — c'est cette phrase sur le tracé
sinueux qui rend la grille possible malgré les cycles impairs (§ 6.1 D).

### 3.2 L'Anneau de Cuivre et les boussoles

Le livre explique *pourquoi* la carte est un objet de fiction (PDF p. 17) :
« **Personne n'a jamais pu dresser une carte de cette région** […] Un brouillard
maléfique y obscurcit le ciel en permanence […] et **les boussoles elles-mêmes en
perdent le nord**. […] aussi longtemps que vous garderez cet anneau à votre doigt,
**vous saurez toujours où est le nord**. »

L'**Anneau de Cuivre** est donc l'artefact qui *autorise* la carte. C'est le
premier objet du catalogue (`OBJFR.TXT` ligne 1, donc `OBJ_ANNEAU = 0`,
`rules.h:52`), et le vendre (page 049, `GX ANNEAU`) termine l'aventure
sur-le-champ : sans boussole, plus de Marais. **Le menu MAP doit être conditionné
à la possession de l'ANNEAU** (§ 7.5) : c'est gratuit narrativement, et cela
transforme la vente de l'anneau en vrai dilemme.

### 3.3 Clairière = pages d'arrivée + page-hub

Le corpus impose une structure à **deux étages**, qu'il faut démonter :

```
  page d'ARRIVÉE : ce qu'on trouve       page-HUB : les sentiers qui
  (créature, objet, PNJ, piège)          partent de la clairière
  ───────────────────────────            ────────────────────
  N157 « La clairière des Arbres-Épées » N022 « Les pousses rapides »
    V 279                                  C 320  … vers le nord
    C 028 Combattre                        C 090  … vers le sud
    C 203 Magie                            C 011  … vers l'ouest
        │                                       ▲
        └── combat 028/203 ── … ────────────────┘
```

**58 pages** portent au moins une direction exploitable : ce sont les **hubs**.
Elles se regroupent en **35 clairières canoniques**, plusieurs hubs de même
signature de sorties étant des variantes de récit du même lieu. Le hub principal
est l'identifiant stable du nœud dans `carte.json`. Groupes de plus d'un hub :

| Clairière | Hubs | Pourquoi plusieurs |
| --- | --- | --- |
| 1 | **058**, 404, 405 | les trois issues du saut de la page 091 |
| 7 | **161**, 103, 244 | carrefour après le Géant / il vous laisse passer / son conseil |
| 11 | **232**, 247, 389 | la baie rangée / le buisson violet / l'Anthérique identifié |
| 15 | **218**, 249 | l'orée / saut dans l'obscurité (variante sans le Feu Follet) |
| 21 | **031**, 077 | bassin de cristal / bassin bienfaisant (avant et après avoir bu) |
| 25 | **082**, 308, 397 | combat au bassin / Bijou Violet arraché / fuite de la créature |
| 27 | **084**, 117, 238, 251, 283, 396 | six sorties narratives du Maître des Jardins |
| 34 | **044**, 254, 370 | sangsues / pont de l'arbre / pont de glace |
| 35 | **045**, 101 | contourner la rivière / franchir le pont |
| — Bête | **125**, 228, 243 | griffes de la Bête / graines-armes / charogne |
| — Courbensaule | **078**, 150, 408 | La Lance Tordue / marchand de potions / Alphonse |

### 3.4 Première visite, hub, revisite

Le Marais est le seul livre de la série où l'on revient sur ses pas, et le livre
justifie la mémoire des clairières : *sans elle, fuir puis revenir soignerait le
monstre*. `monster_enter()` rend l'ENDURANCE laissée au dernier passage, et 0 si
la créature est morte.

**26 pages** portent une ligne `V` — les 25 couples que le livre écrit noir sur
blanc (`grep « déjà venu, rendez-vous au » sur le fac-similé`), plus Courbensaule,
dont la formule diffère (« si vous êtes déjà venu à Courbensaule ») :

| 1re → revisite | Clr | 1re → revisite | Clr | 1re → revisite | Clr |
| --- | --- | --- | --- | --- | --- |
| 010 → 142 Clairière des combats | 5 | 105 → 330 Pierres et tronc | 12 | 290 → 323 Orques des Marais | 26 |
| 011 → 210 Cul-de-sac de la Bête | — | 118 → 303 Clairière des scorpions | 13 | 304 → 149 Le Perroquet | 14 |
| 014 → 338 Scorpion et nain | 32 | 144 → 345 Tente aux araignées | 17 | 305 → 238 Maître des Jardins | 27 |
| 031 → 364 Bassin de cristal | 21 | 157 → 279 Les Arbres-Épées | 18 | 320 → 265 La Licorne | 29 |
| 041 → 382 Sables mouvants | 30 | 170 → 363 Le Patrouilleur vert | 19 | 336 → 137 Le bassin de Vase | 28 |
| 053 → 329 Clairière des grenouilles | 8 | 204 → 250 Fleurs d'Angoisse | 23 | 350 → 331 Le nid de l'Aigle | 16 |
| 065 → 343 Clairière aux brigands | 9 | 209 → 168 Bête du bassin | 25 | 388 → 263 Herbe à Pinces | 24 |
| 066 → 192 Le pique-nique suspect | 9 *(bis)* | 275 → 342 Le Géant | 7 | 398 → 239 Maître des Loups | 4 |
| 092 → 108 Les deux loups | 11 | 280 → 355 Route de Courbensaule | — | | |

Mécanisme (`scoswamp.c`, branche `V` de `classify_line`) : dès que la ligne `V`
est lue et que le drapeau est levé, **rien d'autre de la page ne joue** — ni le
texte, ni les choix, ni surtout les lignes `E` et `P`.

**La détection se fait par clairière, pas par page.** La syntaxe est
`V <cible> [<page> …]` : les numéros qui suivent la cible sont les *autres* pages
de la même clairière (page-hub, variantes de récit, autres arrivées). Le détour
se déclenche si la page courante, la cible, **ou** l'une des pages citées a déjà
été vue. Sans cette liste, un joueur revenant par un autre sentier — le pont
dépose au sud sur 303 et non sur 118, par exemple — retombait sur une page jamais
vue et relisait la première visite : créature ressuscitée, objets redonnés.

**Conséquence pour le MAP** : la même table *paragraphe → clairière* (§ 7.2) sert
à allumer une clairière **quelle que soit la porte par laquelle on y entre** ; les
listes des lignes `V` en sont l'expression, page par page, dans le corpus.

### 3.5 La rivière Croupie et le pont

**La rivière Croupie coule d'est en ouest sur la ligne `y = 3`.** Trois clairières
seulement s'y trouvent, et toutes trois en parlent : (1,3) clr 33, page 295 « La
Rivière Croupie » ; (2,3) clr 20, page 183 « Sommet de la falaise », où l'on peut
**plonger** au nord (030) ou à l'est (321), les deux menant au crocodile ; (3,3)
clr 35, page 138 « Le pont sur la rivière Croupie… **La rivière Croupie la
traverse d'est en ouest** ».

**Le pont (clairière 35) est le SEUL passage entre le nord et le sud.** Vérifié en
supprimant l'arête 35 ⇄ 16 : la moitié **sud** compte 23 clairières, la **nord**
12 (7, 9, 11, 15, 16, 19, 27, 28, 30, 32, le croisement, Courbensaule). Les deux
moitiés ont des caractères différents, et la prose le dit : le **sud** (y = 4…8)
est le marais proprement dit — sol détrempé, sangsues, vase, scorpions,
arbres-épées, herbe à pinces — zone d'entrée où vivent 4 des 5 Maîtres (Loups,
Araignées, Grenouilles, Oiseaux) ; au **nord** (y = 0…2) « le sol devient plus sec
et la végétation des marais cède place à une forêt profonde » (page 092), c'est la
sortie vers Courbensaule, le Géant, le Patrouilleur, le Maître des Jardins ; et le
**nord-ouest** (x = 0, y = 4-5) est une poche tropicale — page 304, « le Marais
[…] ressemble de plus en plus à une **jungle tropicale** ».

### 3.6 Le village de départ, les sorties, Courbensaule

Le prologue est hors Marais et ne se cartographie pas :

```
001 Le chemin vers le Marais (taverne de Bourbenville)
 ├─ 048 défi aux villageois
 └─ 095 la rencontre avec Grognard
      ├─ 240 la proposition (les trois missions)
      └─ 122 mise en garde → 296 partir seul  →  173 / 009 « L'ENTRÉE DU MARAIS »
```

Page **009** : « Vous êtes à la **lisière sud** du Marais aux Scorpions. Grâce à
l'Anneau de Cuivre, vous saurez toujours où est le nord. Vous découvrez **un
sentier orienté plein nord**. » → `C 195`.

| Point | Page | Depuis, et dans quelle direction | Case |
| --- | --- | --- | --- |
| **Entrée** (prologue) | 009 → 195 | clairière 1, on entre par le sud | (2,8) |
| **Sortie sud** | 208 « Sortir du Marais » | depuis la clr 1, vers le sud | (2,8) → dehors |
| **Sortie nord** | 280 « Route de Courbensaule » | depuis la clr 9 (brigands), vers le nord | (0,2) → (0,0) |
| Fausses sorties (mort) | 030 / 321 | depuis la clr 20, en nageant N ou E | crocodile |

La page 208 est une porte à double sens (`C 195 Revenir sur vos pas…` /
`C 159 Retourner chez votre sorcier…`). **Courbensaule** (hub 078, case (0,0)) est
hors marais : la ville, l'auberge « La Lance Tordue », la boutique d'Alphonse le
marchand de potions, des coupeurs de bourses (355).

### 3.7 Les trois missions et leurs chemins critiques

Grognard (page 095, puis 240) propose trois quêtes. Les commanditaires français
sont **Gayolard** (bon), **Pompatarte** (neutre / marchand) et **Stratagus**
(mauvais) — les Gayolard / Poomchukker / Grimslade de l'original. Le retour se
fait par la page **159** (`C 006` Gayolard, `C 226` Stratagus, `C 056`
Pompatarte).

**Gayolard — la Baie d'Anthérique.** Le buisson est dans la **clairière 11** (les
deux loups gris), case (4,0). Chaîne : `092` → `344` ou `068/215` → `247`
« Buisson violet » → **`232 G BA`** → `389` (`G .T`) → `342`. Le Maître des Jardins
(page 396, clr 27) donne la route : « La plante que vous cherchez se trouve **à
l'est**, mais aucun chemin ne permet d'y parvenir directement. […] il vous faut
prendre la direction de **l'ouest**, puis revenir vers **l'est dans le sens des
aiguilles d'une montre**. » — ce qui se lit exactement sur la grille : de la 27
(3,0) on ne peut partir qu'à l'ouest (19), puis sud (croisement), puis est (Géant,
4,1), puis nord (les loups). Arrivée : `175` « SUCCÈS COMPLET ».

**Stratagus — les cinq Amulettes** (`rules.h:90` : loup, fleur, oiseau, araignée,
grenouille), donc cinq clairières obligatoires :

| Amulette | Maître | Clr | Case | Page du gain |
| --- | --- | --- | --- | --- |
| LOUP | Maître des Loups | **4** | (1,8) | `154 G LOUP` |
| FLEUR | Maître des Jardins | **27** | (3,0) | `251 G FLEUR` (ou 117) |
| ARAIGNEE | Maître des Araignées | **17** | (3,6) | `354 G ARAIGNEE` |
| GRENOUILLE | Maître des Grenouilles | **8** | (4,6) | `245 G GRENOUILLE` (vol discret) |
| OISEAU | Maîtresse des Oiseaux | **14** | (0,4) | via `131` / `071 G PL` |
| *(fausse)* | — | — | — | `184 G FAUX` |

**Pompatarte — LA CARTE.** La mission qui rend le menu MAP diégétique. Page 056 :
« M'avez-vous rapporté une carte permettant d'atteindre COURBENSAULE ? » ; page
**158**, seule page du corpus qui parle de la carte du joueur : « Vous […] tirez de
votre poche **un parchemin chiffonné : la carte que vous avez tracée au fil du
Marais. Chemins, clairières et périls y sont marqués avec soin.** » Le but
géographique est la page 280, sortie **nord** depuis la clairière 9.

Chemins critiques (BFS sur les 35 clairières) :

```
POMPATARTE (la carte jusqu'a Courbensaule) — 14 sentiers, le plus long du jeu :
  1 ─E→ 12 ─N→ 17 ─N→ 24 ─E→ 26 ─N→ 3 ─O→ 13 ─N→ 35 ─N→ 16 ─O→ 32
    ─N→ croisement ─O→ 15 ─S→ 28 ─O→ 9 ─N→ Courbensaule

GAYOLARD (la Baie d'Antherique, clr 11) — 11 sentiers :
  1 ─E→ 12 ─N→ 17 ─N→ 24 ─E→ 26 ─N→ 3 ─O→ 13 ─N→ 35 ─N→ 16 ─E→ 30 ─N→ 7 ─N→ 11

STRATAGUS (les 5 Amulettes) — l'union de cinq branches :
  Loup        : 1 ─O→ 4                                              (1)
  Araignees   : 1 ─E→ 12 ─N→ 17                                      (2)
  Grenouilles : 1 ─E→ 12 ─N→ 17 ─N→ 24 ─E→ 26 ─S→ 8                  (5)
  Oiseaux     : 1 ─O→ 4 ─N→ 34 ─N→ 18 ─N→ 29 ─O→ 23 ─N→ 14           (6)
  Jardins     : 1 ─E→…─N→ 35 ─N→ 16 ─O→ 32 ─N→ croisement ─N→ 19 ─E→ 27  (12)
```

Deux missions sur trois passent par le pont. Le raccourci le plus court vers le
pont est `1 ─E→ 12 ─N→ 17 ─N→ 24 ─E→ 26 ─N→ 3 ─O→ 13 ─N→ 35` (7 sentiers).
**Aucune clairière n'est inaccessible** : les 35 sont atteignables depuis la
clairière 1, et le graphe non orienté est connexe.

---

## 4. La liste complète des clairières

### 4.1 Les 35 clairières canoniques

**N°** = numéro du livre (`—` = anonyme) ; **(x,y)** = case, x vers l'est, y vers
le sud ; **Hub** = page qui offre les directions, identifiant stable du nœud ;
**1re** = page de première visite ; **Revisite(s)** = pages « déjà venu » et
variantes d'arrivée ; **Autres hubs** = pages-hub équivalentes ; **Sorties** =
`direction → page cible du choix`.

| N° | (x,y) | Hub | 1re | Revisite(s) | Autres hubs | Titre | Sorties | Contenu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | (0,0) | 078 | 280 | 355 | 150 408 | Route de Courbensaule | S→343 | **HORS MARAIS** : ville, La Lance Tordue, boutique d'Alphonse ; coupeurs de bourses |
| 19 | (2,0) | 234 | 170 | 363 | — | Le Patrouilleur vert | S→121 E→305 | PATROUILLEUR (10/10 en 378) ; demande quel sorcier vous servez ; donne l'itinéraire 166 |
| 27 | (3,0) | 084 | 305 | 238 363 | 117 251 283 396 | Le Maître des Jardins | O→363 | MAÎTRE DES JARDINS (7/10 en 379) — **Amulette de Fleur** ; indique l'Anthérique. **Cul-de-sac** |
| 11 | (4,0) | 232 | 092 | 108 | 247 389 | Les deux loups | S→342 | 2 LOUPS GRIS (7/5, 6/6 en 224) ; **buisson d'Anthérique** → `232 G BA`. **Cul-de-sac** |
| 15 | (1,1) | 218 | 218 | — | 249 | Feu follet à l'orée | S→336 E→121 O→072 | FEU FOLLET — piège : l'ouest téléporte à la clairière 1 |
| — | (2,1) | 121 | 121 | — | — | Le croisement | N→170 S→014 E→275 O→218 | rien : le seul carrefour à quatre branches du nord |
| 7 | (4,1) | 161 | 275 | 342 | 103 244 | Le Géant | N→092 S→041 O→121 | GÉANT (9/12 en 012, 6/12 en 211) — « IL EST INTERDIT DE PASSER ! » ; mouchoir → `286 GX CAPE` |
| 9 | (0,2) | 019 | 065 | 343 | — | Clairière aux brigands | N→280 E→137 | 5 BRIGANDS (chef 9/10) ; l'Anneau reste froid : non malfaisants. **Porte nord du Marais** |
| 28 | (1,2) | 153 | 336 | 137 | — | Le bassin de Vase | N→218 O→065 | VASE visqueuse (5/17 en 171) |
| 32 | (2,2) | 088 | 014 | 338 | — | Scorpion et nain | N→121 E→331 | SCORPION GÉANT (9/10 en 312) dévorant un NAIN ; **Fiole scellée** (`042 G FI`) |
| 16 | (3,2) | 202 | 350 | 331 025 112 | — | Le nid de l'Aigle | S→138 E→041 O→014 | AIGLE géant (7/6 en 392) ; grand nid → **Chaîne d'Or** (`073 G CH`) ; les Plumes l'apaisent |
| 30 | (4,2) | 270 | 041 | 382 | — | Sables mouvants | N→275 O→331 | SABLES MOUVANTS ; Pierre de Glace ou de Croissance pour passer (382) |
| 33 | (1,3) | 295 | 295 | — | — | La Rivière Croupie | S→094 E→183 | berge de la rivière Croupie |
| 20 | (2,3) | 183 | 183 | — | — | Sommet de la falaise | N→**030** S→066 E→**321** O→295 | falaise au-dessus de la rivière ; **plonger au N ou à l'E = mort** (crocodile) |
| 35 | (3,3) | 045 | 138 | — | 101 | Le pont sur la rivière Croupie | N→331 S→303 | vieux pont apparemment désert. **SEUL passage nord ⇄ sud** |
| 14 | (0,4) | 304 | 304 | 149 217 | — | Le Perroquet / Maîtresse des Oiseaux | *(aucune — retour non orienté)* | PERROQUET ; MAÎTRESSE DES OISEAUX ; **Plumes** (`071 G PL`) ; **Amulette d'Oiseau**. Cul-de-sac tropical |
| — | (1,4) | 094 | 094 | — | — | La brume fétide | N→295 S→320 | brume toxique : `E ENDURANCE -2` |
| 9 *(bis)* | (2,4) | 179 | 066 | 192 | — | Le pique-nique suspect | N→183 S→010 E→118 | VOLEUR (10/9 en 267) déguisé en pique-niqueur ; **Cape Rouge** (`386 G CAPE`) ; l'Anneau chauffe |
| 13 | (3,4) | 319 | 118 | 303 | — | La clairière des scorpions | N→138 E→047 O→066 | nuée de petits SCORPIONS ; `CL 070 182` (jamais de choix à prendre) |
| 3 | (4,4) | 047 | 047 | — | — | Trois chemins herbeux | S→290 E→031 O→118 | rien |
| 21 | (5,4) | 031 | 031 | 364 077 394 | — | Bassin de cristal | O→047 | bassin bienfaisant (récupération d'ENDURANCE). **Cul-de-sac** |
| 23 | (0,5) | 367 | 204 | 250 | — | Les Fleurs d'Angoisse | N→304 E→265 | FLEURS D'ANGOISSE : `E HABILETE -1` (et −1 de plus si l'on fuit, 269) |
| 29 | (1,5) | 348 | 320 | 265 | — | La Licorne | N→094 S→157 E→010 O→204 | LICORNE blessée (11/4 en 221) ; **Corne de Licorne** (`277 G CO`) ; bénédiction (381) |
| 5 | (2,5) | 227 | 010 | 142 | — | La clairière des combats | N→066 E→388 O→320 | traces d'un combat, cadavre → **Aimant d'Or** (`059 G AI`, maudit : `063 GX AI`) |
| 24 | (3,5) | 187 | 388 | 263 033 | — | Herbe à Pinces | S→144 E→290 O→010 | HERBE À PINCES (6/16 en 134) |
| 26 | (4,5) | 309 | 290 | 323 352 | — | Orques des Marais | N→047 S→053 O→388 | 3 ORQUES DES MARAIS (6/7, 7/7, 6/5 en 281) ; l'**Aimant d'Or** évite le combat (`CI AI 083`) |
| — | (0,6) | 125 | 011 | 210 299 | 228 243 | Cul-de-sac de la Bête | E→279 | BÊTE IMMONDE (9/10 en 176) ; graines-armes (228). « aucun autre sentier : un **cul-de-sac** » |
| 18 | (1,6) | 022 | 157 | 279 | — | La clairière des Arbres-Épées | N→320 S→090 O→011 | ARBRES-ÉPÉES (9/12 en 028) ; **leurs branches repoussent** entre deux visites |
| 17 | (3,6) | 165 | 144 | 345 354 | — | Tente aux araignées | N→388 S→105 | MAÎTRE DES ARAIGNÉES (9/6 en 026), ARAIGNÉE GÉANTE (8/9 en 261) — **Amulette d'Araignée** ; la clairière brûle ensuite (345) |
| 8 | (4,6) | 230 | 053 | 329 | — | Clairière des grenouilles | **N**→352 *(libellé « est », § 6.1 A)* | MAÎTRE DES GRENOUILLES sur un champignon lumineux ; 2 GRENOUILLES (5/6, 6/5 en 146) ; **Amulette de Grenouille** volée en 245. **Cul-de-sac** |
| 34 | (1,7) | 044 | 090 | — | 254 370 | La rivière profonde | N→157 S→398 | SANGSUES (044) ; franchie par un pont d'arbre (254) ou un pont de glace (370) |
| 4 | (1,8) | 314 | 398 | 239 | — | Clairière du Maître des Loups | N→090 E→195 | MAÎTRE DES LOUPS (11/10 en 064/120) + 2 LOUPS — **Amulette de Loup** (`154 G LOUP`) ; maison fermée en revisite |
| **1** | **(2,8)** | **058** | **195** | 024 208 | 404 405 | **Clairière n° 1 (rond-point)** | **S→208** *(sortie)* **E→105 O→398** | **DÉPART.** « Un large rond-point d'où partent trois sentiers », sol instable et détrempé |
| 12 | (3,8) | 390 | 105 | 330 | — | Pierres et tronc | N→144 E→209 O→195 | pierres plates (repos, 021), tronc creux (055/069), OURS (7/8 en 200) en revisite |
| 25 | (4,8) | 082 | 209 | 168 | 308 397 | Bête du bassin | O→330 | BÊTE DU BASSIN (8/10 en 082) — **Bijou Violet** au front (`308 G BJ`, `276 GX BJ`). **Cul-de-sac** |

### 4.2 Les 39 sentiers

Une ligne par arête distincte ; **dir** est la direction du départ vers l'arrivée,
**page** la page cible du choix directionnel. Répartition : **37 réciproques +
2 à sens unique**, dont l'un n'est pas un sentier mais une téléportation — il
reste donc **38 vrais sentiers** sur la grille.

| De | dir | Vers | page | Remarques |
| --- | --- | --- | --- | --- |
| clr 19 (234) | E | clr 27 (084) | 305 | — |
| clr 19 (234) | S | Le croisement (121) | 121 | — |
| clr 15 (218) | E | Le croisement (121) | 121 | — |
| clr 15 (218) | O | clr 1 (058) | 072 | **téléportation, hors grille, sens unique** (piège du Feu Follet) |
| clr 15 (218) | S | clr 28 (153) | 336 | — |
| clr 7 (161) | N | clr 11 (232) | 092 | — |
| clr 7 (161) | O | Le croisement (121) | 121 | **deux cases** |
| clr 7 (161) | S | clr 30 (270) | 041 | — |
| clr 9 (019) | N | Courbensaule (078) | 280 | **deux cases** ; sortie nord du Marais |
| clr 9 (019) | E | clr 28 (153) | 137 | — |
| clr 32 (088) | N | Le croisement (121) | 121 | — |
| clr 16 (202) | O | clr 32 (088) | 014 | — |
| clr 16 (202) | E | clr 30 (270) | 041 | — |
| clr 16 (202) | S | clr 35 (045) | 138 | **le franchissement de la rivière** |
| clr 13 (319) | N | clr 35 (045) | 138 | **le franchissement de la rivière** |
| clr 33 (295) | S | La brume fétide (094) | 094 | — |
| clr 20 (183) | O | clr 33 (295) | 295 | — |
| clr 9bis (179) | N | clr 20 (183) | 183 | — |
| clr 9bis (179) | E | clr 13 (319) | 118 | — |
| clr 3 (047) | O | clr 13 (319) | 118 | — |
| clr 3 (047) | E | clr 21 (031) | 031 | — |
| clr 3 (047) | S | clr 26 (309) | 290 | — |
| clr 23 (367) | N | clr 14 (304) | 304 | **sens unique** dans le graphe des directions (retour 217 → 250 non orienté) |
| clr 23 (367) | E | clr 29 (348) | 265 | — |
| clr 29 (348) | N | La brume fétide (094) | 094 | — |
| clr 5 (227) | N | clr 9bis (179) | 066 | — |
| clr 5 (227) | O | clr 29 (348) | 320 | — |
| clr 5 (227) | E | clr 24 (187) | 388 | — |
| clr 24 (187) | E | clr 26 (309) | 290 | — |
| clr 17 (165) | N | clr 24 (187) | 388 | — |
| clr 8 (230) | N | clr 26 (309) | 352 | libellé « est », prose « nord » : **la prose est retenue** (§ 6.1 A) |
| clr 18 (022) | N | clr 29 (348) | 320 | — |
| clr 18 (022) | O | Cul-de-sac de la Bête (125) | 011 | — |
| clr 18 (022) | S | clr 34 (044) | 090 | — |
| clr 4 (314) | N | clr 34 (044) | 090 | — |
| clr 1 (058) | O | clr 4 (314) | 398 | — |
| clr 1 (058) | E | clr 12 (390) | 105 | — |
| clr 12 (390) | N | clr 17 (165) | 144 | **deux cases** |
| clr 12 (390) | E | clr 25 (082) | 209 | — |

**Liens hors grille** — trois sorties directionnelles ne mènent à aucune clairière
et ne comptent pas dans les 39 : clr 1 `S → 208`, **sortie sud du Marais** (retour
par `C 195`) ; clr 20 `N → 030`, **mort** (plonger, crocodile) ; clr 20
`E → 321 → 030`, **mort** (nager vers le pont, même crocodile).

### 4.3 Créatures et objets, par clairière

| Clr | Créature(s) | Combat | Clr | Créature(s) | Combat |
| --- | --- | --- | --- | --- | --- |
| 4 | MAÎTRE DES LOUPS 11/10 ; 2 LOUPS 7/5, 6/6 | 064, 120, 215 | 24 | HERBE À PINCES 6/16 | 134 |
| 7 | GÉANT 9/12 puis 6/12 | 012, 211 | 25 | BÊTE DU BASSIN 8/10 | 082 |
| 8 | 2 GRENOUILLES 5/6, 6/5 | 146 | 26 | 3 ORQUES 6/7, 7/7, 6/5 | 281 |
| 9 | CHEF DES BRIGANDS 9/10 ; 8/8 ; 8/11 ; 8/10 | 079, 235, 301 | 27 | MAÎTRE DES JARDINS 7/10 | 379 |
| 9 *(bis)* | VOLEUR 10/9 | 267 | 28 | VASE 5/17 | 171 |
| 11 | 2 LOUPS GRIS 7/5, 6/6 | 224 | 29 | LICORNE 11/4 | 221 |
| 12 | OURS 7/8 | 200 | 32 | SCORPION GÉANT 9/10 | 312 |
| 17 | MAÎTRE DES ARAIGNÉES 9/6 ; ARAIGNÉE 8/9 | 026, 261 | — Bête | BÊTE IMMONDE 9/10 | 176 |
| 18 | ARBRES-ÉPÉES 9/12 | 028 | — Courb. | 2 COUPEURS DE BOURSES 7/5, 8/5 | 355 |
| 19 | PATROUILLEUR 10/10 | 378 | *hors Marais* | STRATAGUS 13/18, 9/10, 9/8 ; POMPATARTE 9/14 ; DÉMON 12/16 ; STATUE 7/6 | 124, 225, 402, 341, 222, 284 |

Les clairières 5 et 13 n'ont pas de ligne `M` : la 5 n'a qu'un butin maudit, la 13
une nuée de scorpions résolue par `CL`. L'appariement page à combat ↔ image de
bataille est **exact** : 32 pages avec une ligne `M`, 32 images `Bxxx`, aucun
orphelin d'un côté ni de l'autre.

Objets (`OBJFR.TXT`, 10 visibles + 1 drapeau caché) : **Anneau de Cuivre** de
départ, perdu en `049 GX ANNEAU` — **et l'aventure s'arrête** ; **Fiole scellée**
clr 32 (`042 G FI`, bue en `253 GX FI`) ; **Aimant d'Or** clr 5 (`059 G AI`, maudit
`063 GX AI`, évite le combat des Orques) ; **Chaîne d'Or** clr 16 (`073 G CH`, dans
le nid) ; **Plumes de Perroquet** clr 14 (`071 G PL`, apaisent l'Aigle de la
clr 16) ; **Cape Rouge** clr 9bis (`386 G CAPE`, `286 GX CAPE` : le mouchoir du
Géant) ; **Bijou Violet** clr 25 (`308 G BJ`, `276 GX BJ`) ; **Corne de Licorne**
clr 29 (`277 G CO`) ; **Baie d'Anthérique** clr 11 (`232 G BA` → `389 G .T`) ;
**Épée Magique** hors Marais (`241` / `340 G EP`) ; **Amulettes** LOUP / FLEUR /
ARAIGNEE / GRENOUILLE / OISEAU en clr 4 / 27 / 17 / 8 / 14 (154 / 251 / 354 / 245 / 131).

---

## 5. La grille

### 5.1 Conventions

* `x` croît vers l'**est**, `y` croît vers le **sud** — convention écran, le nord
  en haut. Grille **6 colonnes × 9 lignes = 54 cases**, **35 occupées**,
  **19 vides**.
* Une arête N/S/E/O impose un **ordre strict** sur un axe et une **égalité** sur
  l'autre, pas une distance de 1 :

  ```
  arête E :  x_b > x_a  et  y_b == y_a
  arête S :  y_b > y_a  et  x_b == x_a
  ```

  C'est ce que le livre autorise (« un tracé sinueux mais sa direction générale
  restera toujours la même ») et ce qui résout les cycles impairs (§ 6.1 D).
  **Trois sentiers font deux cases**, tous les autres une.
* La **rivière Croupie** occupe la ligne `y = 3` — cases (1,3), (2,3), (3,3) — et
  coupe la carte en deux. Le seul trait vertical qui la franchit part de (3,3), le
  pont.

### 5.2 La grille, en tableau

| y \ x | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| **0** | Courbensaule *(hors marais)* | | **19** Patrouilleur | **27** Maître des Jardins | **11** Les deux loups | |
| **1** | | **15** Feu follet | *(—)* Le croisement | | **7** Le Géant | |
| **2** | **9** Brigands | **28** Bassin de Vase | **32** Scorpion et nain | **16** Nid de l'Aigle | **30** Sables mouvants | |
| **3** | | **33** Rivière Croupie | **20** Sommet de la falaise | **35** LE PONT | | |
| **4** | **14** Perroquet | *(—)* Brume fétide | **9bis** Voleur | **13** Scorpions | **3** Trois chemins | **21** Bassin de cristal |
| **5** | **23** Fleurs d'Angoisse | **29** La Licorne | **5** Clairière des combats | **24** Herbe à Pinces | **26** Orques des Marais | |
| **6** | *(—)* Cul-de-sac de la Bête | **18** Arbres-Épées | | **17** Tente aux araignées | **8** Grenouilles | |
| **7** | | **34** Rivière profonde | | | | |
| **8** | | **4** Maître des Loups | **1 DÉPART** | **12** Pierres et tronc | **25** Bête du bassin | |

### 5.3 Le dessin ASCII — numéros de clairière

`( ?)` = clairière sans numéro dans le livre. Source : `carte_ascii.txt`.

```
( ?)        (19)--(27)  (11)
  |           |           |
      (15)--( ?)--    --( 7)
  |     |     |           |
( 9)--(28)  (32)--(16)--(30)
                    |
      (33)--(20)  (35)
        |     |     |
(14)  ( ?)  ( 9)--(13)--( 3)--(21)
  |     |     |           |
(23)--(29)--( 5)--(24)--(26)
        |           |     |
( ?)--(18)        (17)  ( 8)
        |           |
      (34)
        |           |
      ( 4)--( 1)--(12)--(25)
```

### 5.4 Le même dessin — pages-hub

C'est l'identifiant que le moteur manipule. Source : `carte_ascii_pages.txt`.

```
[ 78]         [234]--[ 84]  [232]
  |             |             |
       [218]--[121]--     --[161]
  |      |      |             |
[ 19]--[153]  [ 88]--[202]--[270]
                       |
       [295]--[183]  [ 45]
         |      |      |
[304]  [ 94]  [179]--[319]--[ 47]--[ 31]
  |      |      |             |
[367]--[348]--[227]--[187]--[309]
         |             |      |
[125]--[ 22]         [165]  [230]
         |             |
       [ 44]
         |             |
       [314]--[ 58]--[390]--[ 82]
```

### 5.5 Légende et lecture

| Signe | Sens | | Signe | Sens |
| --- | --- | --- | --- | --- |
| `(nn)` / `[nnn]` | clairière (numéro du livre / page-hub) | | `\|` | sentier nord-sud |
| `( ?)` | clairière que le livre ne numérote pas | | trait qui saute une case | sentier de **deux cases** |
| `--` | sentier est-ouest | | case vide | aucune clairière |

Lecture : la ligne `y = 3` (33 – 20 – 35) est la rivière Croupie ; seul le trait
vertical sous `(35)` la franchit. La colonne `x = 2` est l'axe central, la case
(2,8) le départ. Les trois traits qui « sautent » une case sont
9 ⇄ Courbensaule (colonne 0, entre y = 0 et y = 2), le croisement ⇄ 7 (ligne 1,
entre x = 2 et x = 4) et 17 ⇄ 12 (colonne 3, entre y = 6 et y = 8).

---

## 6. Incohérences et correctifs

### 6.1 Les incohérences relevées

**A. Un sentier dont le retour n'est pas l'opposé — la clairière 8.**
Page 309 `C 053 Au sud` → clr 8 ; page 230 `C 352 Reprendre la route vers l'est` ;
page 352 : « Le seul chemin qui permette de quitter la clairiere est celui par
lequel vous etes arrive. Vous l'empruntez donc a nouveau, EN DIRECTION DU NORD,
cette fois… » Le libellé dit *est*, la prose dit *nord*. **La prose est retenue** :
le sentier 26 ⇄ 8 est un axe N/S et la clairière 8 est un cul-de-sac au sud de la
26. C'est la seule correction de direction appliquée dans le modèle
(`FIX = {(230,'E'):'N'}`).

**B. Un lien à sens unique — le piège du Feu Follet.** Page 218 (clr 15)
`C 072 Suivre le Feu Follet vers l'ouest`, page 072 `C 024`, page 024 : « le sol
devient de plus en plus humide ; soudain vous tombez dans un trou rempli de vase.
Le Feu Follet disparaît : sa présence était une tromperie. Grâce à l'Anneau de
Cuivre vous savez quel chemin prendre pour retrouver la clairière. » Ce n'est
**pas un sentier** : l'Anneau raccroche le joueur à la clairière 1, à 8 cases de là
et de l'autre côté de la rivière. À représenter **hors grille** (pointillé, ou
rien) ; exclu du placement (`SKIP = {(218,'O')}`).

**C. Un cul-de-sac dont le retour n'est pas orienté — la clairière 14.** Page 367
(clr 23) `C 304 Aller au nord` ; page 217 : « Un seul sentier quitte la clairière :
celui par lequel vous êtes venu. Vous reprenez la direction du sud. » puis
`C 250 Rejoindre la clairière des Fleurs d'Angoisse`. La prose donne « sud » mais
**le libellé du choix ne le porte pas**, donc l'extraction automatique ne voit
qu'un arc aller. La clairière 14 est bien un cul-de-sac au nord de la 23.

**D. Deux cycles de longueur impaire.** Sur une grille, la parité de `x + y`
alterne à chaque pas : tout cycle est de longueur paire. Deux cycles du corpus
sont impairs :

```
cycle 1 (longueur 5) :
   croisement ─E→ clr 7 ─S→ clr 30 ─O→ clr 16 ─O→ clr 32 ─N→ croisement
   somme des vecteurs = (-1,0) != (0,0)

cycle 2 (longueur 9) :
   clr 5 ─E→ clr 24 ─S→ clr 17 ─S→ clr 12 ─O→ clr 1 ─O→ clr 4 ─N→ clr 34
        ─N→ clr 18 ─N→ clr 29 ─E→ clr 5
   somme des vecteurs = (0,-1) != (0,0)
```

Résolus en allongeant **trois** sentiers à deux cases, ce que le livre autorise
explicitement : 9 ⇄ Courbensaule (N/S), croisement ⇄ 7 (E/O), 17 ⇄ 12 (N/S).
Aucun cycle n'est resté dans les deux DAG de placement : **le Marais est bien
planaire-grille**, à trois sentiers étirés près. Les **68 contraintes d'ordre ont
été revérifiées une par une : 0 fautive**, et les trois collisions résiduelles
(nœuds sans contrainte relative : Courbensaule / clr 14, brume fétide / clr 15,
falaise / clr 19) ont été levées à la main sans violer un seul ordre. **Aucune
clairière ne partage sa case avec une autre.**

**E. Le numéro 9 est porté par deux clairières distinctes** — la « Clairière aux
brigands » (page 065, hub 019, case (0,2)) et « Le pique-nique suspect » du Voleur
(page 066, hub 179, case (2,4)). Elles sont de part et d'autre de la rivière et
n'ont aucun sentier commun : ce n'est pas réductible à une coquille, c'est la
numérotation du livre que l'adaptation n'a pas respectée. Cinq numéros sont libres
— 2, 6, 10, 22, 31 — dont un pourrait être donné au Voleur.

**F. Quatre coquilles de numéro dans la prose** (état d'avant leur retrait,
§ 6.3) :

| Page | Prose | Lecture correcte | Preuve |
| --- | --- | --- | --- |
| 388 | « la Clairiere n **0 24** » | **24** | « 0 » parasite ; `V 263` renvoie à la même clairière |
| 033 | « la Clairiere n **388** » | **24** | 033 est la variante de combat de la 388 (mêmes choix 134/167) |
| 042 | « la Clairiere n **042** » | **32** | c'est son propre numéro de page ; 042 sort en `C 088`, hub de la 32 |
| 025 | « la Clairiere n **025** » | **16** | 025 sort en `C 202`, hub du Nid de l'Aigle ; la 25 est la Bête du bassin (209) |

`decors.json` contourne les trois premières par `aliases`, mais **il reproduit la
quatrième** : `'Clairiere n 025'` y est aliasé vers `CLAIRIERE_25` alors que la
page appartient à la clairière **16**. À corriger dans la bible si l'on s'en
resert comme source.

**G. Numéros manquants et clairières anonymes.** La prose donnait 30 numéros
distincts (1, 3, 4, 5, 7, 8, 9, 11 à 21, 23 à 30, 32 à 35) pour 35 clairières :
**manquent 2, 6, 10, 22, 31**, et rien n'existe au-delà de 35 — l'adaptation ne
couvre pas tout le Marais du livre. Quatre lieux restent **anonymes** : le
croisement (121), la brume fétide (094), le cul-de-sac de la Bête (125),
Courbensaule (078, hors marais). `decors.json` a 29 planches `CLAIRIERE_NN` : il
n'y a **pas de n° 13**, parce que la page 118 écrivait « une petite clairiere : **la
no 13** », formulation que les `aliases` ne couvraient pas.

**H. L'itinéraire de la page 166 ne se vérifie pas sur la grille.** Le
Patrouilleur donne une route de sortie : « Prenez **la direction du sud**, puis
allez **vers l'est**, puis **au sud encore** lorsque vous atteindrez **le Nid
d'Aigle**, ensuite partez **vers l'ouest**, et enfin **au sud** une dernière
fois. » Depuis la clairière 19 (2,0), S-E-S-O-S ne rejoint pas la lisière sud et
le Nid d'Aigle n'est pas au bon rang : la page semble transcrite du livre alors
que le maillage de l'adaptation a été partiellement réinventé. **C'est le meilleur
test de non-régression disponible** si l'on décide un jour d'aligner le corpus sur
la carte du livre. La vraie route depuis la 19 est `S, S, E, S, S, E, S, O, S, S, O`
— 11 sentiers (le raccourci `S, O, O` existe mais passe par le piège du Feu
Follet, donc n'est pas un itinéraire).

**I. Trois pages sont revendiquées par deux clairières dans `carte.json`.** Relevé
en construisant la table de rabattement ; arbitrage, texte en main :

| Page | Titre | Rattachement | Preuve |
| --- | --- | --- | --- |
| 363 | Retour au Patrouilleur | **clr 19** (et non 27) | « Vous retournez dans la clairiere ou vous avez fait la rencontre du Patrouilleur » ; `C 234`, hub de la 19 |
| 394 | Le bassin paisible | **clr 21** (et non 3) | « vous observez attentivement le bassin » ; `C 077 Boire a votre tour` |
| 330 | Le tronc creux | **clr 12** (et non 25) | « Vous vous trouvez dans la clairiere au gros tronc creux » |

Le générateur du fichier `MAP` **doit** appliquer ces trois arbitrages, sinon la
table page → clairière est ambiguë.

**J. Divergence FR / EN — deux bugs de contenu.** Le graphe a été construit deux
fois et comparé : la page **347** perd son choix « Fuir la clairière » en anglais
(`C 379`, `C 363` en FR ; `C 379` seul en EN) et la page **382** est **tronquée en
pleine phrase** en anglais (« If you have one or ») et n'a **aucune sortie**.
`reflow_txt.py --derive` ne les voit pas : son recoupement FR/EN (`mechanics()`)
ne compare que la mécanique des directives, jamais les lignes `C`. **Une carte
générée depuis le seul corpus français serait fausse pour l'anglais.**

### 6.2 Correctifs appliqués dans les pages

**Appliqué le 2026-09-03**, FR et EN. Chaque rattachement a été relu sur le
fac-similé avant d'être écrit ; deux des propositions initiales étaient fausses
et le livre les a corrigées (lignes marquées ⚠).

| Page | Correctif | Justification |
| --- | --- | --- |
| `N230.TXT` | `C 352 Reprendre la route vers le nord` (au lieu de « vers l'est ») | la page 352 dit « EN DIRECTION DU NORD » ; un mot, et l'incohérence A disparaît |
| `N217.TXT` | `C 250 Reprendre la direction du sud vers les Fleurs d'Angoisse` | la prose dit déjà « Vous reprenez la direction du sud » ; la clairière 14 cesse d'être à sens unique (C) |
| `N041.TXT` | + `V 382 270` | clr 30 : livre § 41, « rendez-vous au 382 » |
| `N053.TXT` | + `V 329 230` | clr 8 : livre § 53, « rendez-vous au 329 » |
| `N144.TXT` | + `V 345 165 354` | clr 17 : livre § 144, « rendez-vous au 345 » |
| `N014.TXT` | + `V 338 088` | clr 32 : livre § 14, « rendez-vous au 338 » |
| `N011.TXT` | + `V 210 125 299 228 243` | cul-de-sac de la Bête : livre § 11 ; ouvre par 210 les pages 143 et 243 |
| ⚠ `N031.TXT` | + `V 364 077 394` | clr 21 : le livre § 31 renvoie au **364**, pas au 077. Le 077 est la page où l'on *boit* (+3 ENDURANCE) : en faire la revisite aurait donné une fontaine à ENDURANCE inépuisable |
| `N170.TXT` | + `V 363 234` | clr 19 : livre § 170, « rendez-vous au 363 » |
| `N209.TXT` | + `V 168 082 308 397` | clr 25 : livre § 209, « rendez-vous au 168 » |
| `N105.TXT` | + `V 330 390` | clr 12 : livre § 105, « rendez-vous au 330 » |
| `N065.TXT` | + `V 343 019` | clr 9 : livre § 65, « rendez-vous au 343 » |
| `N204.TXT` | + `V 250 367` | clr 23 : livre § 204, « rendez-vous au 250 » |
| ⚠ `N092.TXT` | + `V 108 232 247 389` | clr **11**, pas 7 : la page 108 dit « la clairière où vous aviez rencontré les **loups** » et son buisson sans baies, et le livre § 92 y renvoie. La 275 portait déjà `V 342` |

**Les 14 lignes `V` préexistantes ont été complétées** de la même façon avec les
autres pages de leur clairière (§ 3.4). Trois liens perdus à l'adaptation ont
par ailleurs été rétablis, chacun vérifié sur le fac-similé :

| Page | Correctif | Justification |
| --- | --- | --- |
| `N145.TXT` | + `CU GLACE 126 Pierre de Glace` | le livre § 145 offre **quatre** Pierres contre le Géant — Malédiction, Amitié, Feu, **Glace** ; la Glace manquait, et avec elle la page 126 |
| `N147.TXT` | `CL 213 106` (au lieu de `CL 213 267`) | livre § 147 : « Si vous êtes Malchanceux, rendez-vous au **106** ». Le portage sautait le piège du filet (−2 ENDURANCE) pour aller droit au combat |
| `N330.TXT` | + `C 129 Si vous y avez vu une creature lors d'une precedente visite` | la prose portait encore « rendez-vous au 129 » sans que le choix existe ; la 129 et, par elle, la 181 (« Le retour de l'Ours ») étaient injouables |

**Effet mesuré** : les lignes `V` passent de 14 à **26**, soit **25 clairières
sur 35** avec une revisite explicite, et les pages inaccessibles tombent de 18 à
**1** — la 000, l'écran d'accueil du portage, où le moteur entre au lancement
sans qu'aucun choix y mène. Le graphe passe de 729 à 743 arcs. Vérifié par BFS
depuis la page 001, sur les deux corpus, qui donnent le même graphe.

**Contrainte de forme** : la ligne `V` doit être placée **immédiatement après la
ligne `T`**, avant tout le reste. Le garde de `classify_line` court-circuite la
page entière dès qu'il la lit ; une ligne `E` ou `P` placée avant elle serait
rejouée à chaque visite. `reflow_txt.py` vérifie cet invariant, et depuis le même
jour que la liste soit entièrement numérique, sans doublon et sans citer sa
propre page.

Les quatre coquilles de numéro (§ 6.1 F) n'ont plus d'objet dans la prose (§ 6.3)
mais restent à corriger **dans les `aliases` de `decors.json`**, où
`'Clairiere n 025' → CLAIRIERE_25` est faux.

### 6.3 Note sur la numérotation — décision du propriétaire

> **Les numéros de clairière ne doivent PAS apparaître dans le texte du jeu.**

Décision appliquée : au 2026-09-03, un `grep` de
`clairiere (n|no|numero) ?[0-9]+` sur `SCOSWAMP/TEXTFR` **et** `SCOSWAMP/TEXTEN`
retourne **0 occurrence**. Les pages 025, 033, 042, 195 et 388 ne portent plus de
numéro.

La numérotation employée dans tout ce document est donc **une référence interne au
projet**, alignée sur les identifiants `CLAIRIERE_NN` de
`SCOSWAMP.MORE/decors.json` (29 valeurs, plus 4 clairières anonymes et le doublon
du 9). Elle sert à trois choses : nommer les nœuds dans `carte.json`, relier une
page à sa planche `SCOSWAMP.MORE/REF/CLAIRIERE_NN.png`, et permettre au menu MAP
de *choisir* d'afficher un numéro — ce qui reste une question d'interface, non de
contenu textuel. Si le menu MAP les affiche, il devra les lire dans le fichier
`MAP` et non dans la prose.

---

## 7. Spécification du menu MAP (touche `M`)

> **Construit le 2026-09-04** (branche `feat/scoswamp-map`). Ce qui suit est la
> spécification d'origine ; l'écart entre elle et ce qui a été fait est résumé
> au § 7.9 et détaillé dans `DOCS/rapport-map.md`.


### 7.1 Ce que le moteur garde déjà

**Tout l'état nécessaire existe.** `SCOSWAMP/SRC/rules.c:384-406` :

```c
#define SCENE_BITS SCENE_MEMORY_SIZE   /* rules.h:246 -> 52 ; 412 paragraphes arrondis a l'octet */
static unsigned char visited[SCENE_BITS];
int  scene_visited(unsigned int scene);
void scene_mark_visited(unsigned int scene);
void scene_memory_export(unsigned char* out);   /* 52 octets */
void scene_memory_import(const unsigned char* in);
```

52 octets = 416 bits ≥ 412 paragraphes. Ce bitmap est **déjà sauvegardé** dans les
emplacements `PARTIE0-9` (`HELPFR.TXT` : « État sauvé : scène, héros, objets,
amulettes, **visites** et monstres »). La mémoire des monstres existe aussi
(`MONSTER_SLOTS = 40`, `monster_memory_export`, 160 octets) : elle donne « la
créature et son état » que le livre demande sur chaque cercle. **Rien à ajouter
côté état** : la carte ne demande **pas de second bitmap de sentiers** — un
sentier est emprunté quand ses deux extrémités sont visitées, ce qui économise les
5 octets de bits de sentiers *et* le code pour les tenir à jour.

### 7.2 Le rabattement page → clairière

`scene_visited(page)` répond sur le *paragraphe*, la carte raisonne sur la
*clairière*. Mesure sur `carte.json` : 119 entrées, **116 pages distinctes** (les
trois doublons du § 6.1 I), réparties sur les 35 nœuds — 3,3 pages par clairière,
de 1 (clr 20, clr 33, brume fétide) à 8 (clr 27). Les 296 autres pages (combats,
dialogues, morts, prologue) ne se rattachent à aucun lieu.

```c
/* clairiere_visitee(i) : la i-eme clairiere a-t-elle ete vue,
 * par n'importe laquelle de ses pages ? */
unsigned char clairiere_visitee(unsigned char i)
{
    const unsigned char* p = &MAP_PAGES[MAP_OFF[i]];
    unsigned char n = MAP_OFF[i + 1] - MAP_OFF[i];
    while (n--) { if (scene_visited(page16(p))) return 1; p += 2; }
    return 0;
}
```

Le sens inverse — *quelle clairière suis-je en train de visiter ?* — est appelé à
chaque page, et une **table plate indexée par numéro de page** le rend gratuit :
412 octets, un par paragraphe, valant l'index de clairière (0…34) ou `0xFF`. Zéro
recherche, zéro code. La variante compacte (116 paires triées + dichotomie)
économise 64 octets et coûte une fonction : **la table plate gagne.**

```c
/* MAP_OF_PAGE[412] : index de clairiere, 0xFF si la page n'est pas un lieu. */
if (MAP_OF_PAGE[app.current_scene] != 0xFF)
    app.clairiere_courante = MAP_OF_PAGE[app.current_scene];
```

⚠ **La clairière courante doit être *collante*.** 296 pages sur 412 ne
correspondent à aucun lieu : si le joueur presse `M` au milieu du combat contre
l'Herbe à Pinces (page 134), la carte doit continuer à montrer la clairière 24.
D'où l'affectation conditionnelle ci-dessus, et **un octet de plus en BSS**.

### 7.3 Les trois états, tous déductibles du seul bitmap

| État | Test | Rendu (modèle du livre) |
| --- | --- | --- |
| clairière **vue** | `clairiere_visitee(i)` | cercle + numéro + nom de la créature |
| sentier **emprunté** | les deux extrémités vues | trait plein `--` / `\|` |
| sentier **connu, non emprunté** | une extrémité vue, l'autre non | rayon terminé par `?` |
| clairière **inconnue** | ni l'un ni l'autre | case vide |

Un raffinement optionnel — distinguer « je sais qu'un sentier part vers le nord »
de « j'y suis allé » — tiendrait dans **5 octets** (39 sentiers → 39 bits), mais
il faudrait du code pour les mettre à jour et le livre ne le demande pas.

### 7.4 Le rendu : texte 80 × 24

La grille tient en 6 cases de 4 caractères plus 5 liaisons de 2 = **34 colonnes**,
et 9 lignes de cellules plus 8 lignes de liaison = **17 lignes**. Avec les
étiquettes de coordonnées, **38 colonnes à gauche**, il reste **42 colonnes à
droite** pour la légende. Le mode texte 80 colonnes ne demande **aucune primitive
graphique** et — point décisif — **rien à sauvegarder** : `memory_swap.h` le dit,
« les bascules ne touchent QUE des soft-switches : l'écran texte reste en place en
`$400-$7FF` pendant tout le passage en graphique ». Presser `M` depuis le mode
image ne coûte donc pas une copie de la page HGR.

Maquette **exacte** (24 lignes, 80 colonnes vérifiées ; état simulé : le joueur a
suivi `clr 1 ─E→ 12 ─N→ 17 ─N→ 24` et se trouve dans la 24) :

```
CARTE DU MARAIS AUX SCORPIONS -- 4/35 CLAIRIERES
    0     1     2     3     4     5
0                                     CLAIRIERE N 24 -- Herbe a Pinces
                                      arrivee par l'OUEST (clr 5)
1
                                      HERBE A PINCES  HAB 6 / END 16  vivante
2
                                      SORTIES
3                                       O  clr 5   La clairiere des combats  vue
                                        E   ?      sentier connu, non emprunte
4                                       S   ?      sentier connu, non emprunte

5                 ?-<24>-?            LEGENDE
                     |                  (nn)  clairiere vue, numero du livre
6                   (17)                <nn>  vous etes ici (video inverse)
                     |                  ( ?)  vue, sans numero dans le livre
7                                       -- |  sentier emprunte
                     |                  -? ?  sentier connu, non emprunte
8           ?-( 1)--(12)-?
                                      4 clairieres sur 35 -- carte incomplete



IJKL / FLECHES = CURSEUR   RETURN = DETAIL   M = RETOUR AU RECIT
```

Notes de rendu : la **ligne 1** est la barre de titre, en vidéo inverse comme celle
du récit ; `<24>` marque la position courante (vidéo inverse à l'écran, `<…>` n'est
qu'une convention de maquette) ; le trait vertical sous `(12)` **saute la ligne 7**,
c'est le sentier de deux cases 17 ⇄ 12 ; le `?-` à gauche de `( 1)` est la
clairière 4, connue par sa direction mais pas encore visitée, le `-?` à droite de
`(12)` est la 25 ; la **sortie sud du Marais** (page 208) n'est pas un sentier et
mérite un signe propre (`v` sous la case) plutôt qu'un `?`. Un curseur de
consultation (flèches ou `IJKL`) déplace la sélection de case en case, `RETURN`
détaille la clairière sélectionnée. Les deux variantes plus coûteuses — HGR
280 × 192 (6 colonnes de 46 px, 9 lignes de 21 px, cercles de 14 px) et le mode
mixte (20 lignes HGR + 4 lignes de texte, l'infrastructure du combat) — sont à
réserver au jour où la RAM auxiliaire sera exploitée : elles redemandent les
primitives de tracé qui coûtaient l'essentiel des 5 019 octets de l'ancien mode
carte.

### 7.5 Le comportement de la touche `M`

`M` est libre : `HELPFR.TXT` / `HELPEN.TXT` listent `[A-E] [ESPACE/RETURN/ESC]
[I] [S] [L] [H] [Q]`, et la barre de titre affiche `M_TOUCHES` = « ESPACE=VUE
A-Z=CHOIX I=SAC Q=QUITTER » (ligne 29 de `MSGFR.TXT`, 39 caractères sur 80 : il y
a la place pour `M=CARTE`).

**Bascule, comme `I` et `H`.** `show_inventory()` est le modèle exact : elle sauve
`app.video_mode`, force le texte (`set_video_mode(0)`), boucle sur `cgetc()`, et
**`[I]` ressort** — « `[I]` est une bascule : elle ouvre le sac et le referme » —
en rendant au joueur le mode vidéo qu'il avait choisi. `show_map()` doit faire
pareil, avec `M` et `ESC` comme sorties.

**Le test de `M` doit précéder la branche `A-Z`** de `handle_user_input()`
(`scoswamp.c:1985-2022`). La chaîne est un `else if` : `' '/'\r'/27`, puis `I`, `H`,
`S`/`L`, `Q`, **puis** `(key >= 'A' && key <= 'Z')` ; insérer la branche `M` avant
ce dernier test suffit. `M` serait sinon lu comme l'index 12, donc jamais un choix
valide (`choice_num < app.num_choices`, `MAX_CHOICES = 5`), mais le code
deviendrait fragile au premier élargissement.

**Grisée sans l'Anneau de Cuivre** (§ 3.2) : si
`!character_has_object(&app.hero, OBJ_ANNEAU)`, `M` affiche un message du
catalogue — « Sans l'Anneau de Cuivre, les boussoles perdent le nord » — et rend la
main. Ce message passe par `build_messages.py`, **source unique** qui écrit
`messages.h` **et** les deux catalogues d'un même geste : `messages_load` refuse un
fichier qui n'a pas exactement `MSG_COUNT` lignes, donc tout se régénère ensemble.
Le rappel `M=CARTE` dans `M_TOUCHES` et les deux fichiers d'aide sont à retoucher
dans la même passe.

### 7.6 Le format du fichier `MAP`

Toute la doctrine du projet est là : « le texte du jeu est une donnée ». Les
tables ne vont pas dans le binaire mais dans un fichier `MAP` sur le disque,
généré par un `build_map.py` reconstruit **à partir de `SCOSWAMP.MORE/carte.json`**.

```
en-tete                              4 octets
   'M','A','P',1                     magie + version

table des clairieres         35 x 6 = 210 octets
   x           1 octet    0..5
   y           1 octet    0..8
   num         1 octet    numero de clairiere du livre, 0 = anonyme
   sorties     1 octet    bits 0..3 = N,S,E,O presentes ; bits 4..7 reserves
   nom_off     1 octet    offset dans le pool de noms
   pages_off   1 octet    offset dans la table des pages

table des sentiers           39 x 3 = 117 octets
   a, b        2 octets   index de clairiere
   dir|len     1 octet    bits 0..1 = direction a->b (0=N,1=S,2=E,3=O)
                          bits 2..3 = longueur en cases (1 ou 2)
                          bit  4    = sens unique
                          bit  5    = hors grille (teleportation)
                          bit  6    = infranchissable (mort)

table de rabattement page -> clairiere      412 octets
   un octet par paragraphe (0..411) : index de clairiere, 0xFF = aucune
   116 octets sur 412 sont renseignes ; O(1), aucune recherche

pool de noms de creatures                  ~311 octets
   chaines ASCII terminees par 0 : "GEANT", "LICORNE", "ARBRES-EPEES", ...
   les 26 noms du § 4.3, mesures : 311 octets

TOTAL                                     ~1 054 octets
```

Variante minimale sans les noms de créatures (mais le livre les demande) :
en-tête + clairières + sentiers + rabattement = **743 octets**. Variante extrême :
une table de 54 octets (index de clairière par case, 0 = vide) plus 39 × 3 octets
de sentiers = **171 octets**, mais sans rabattement le bitmap `visited` devient
inutilisable. À comparer aux **5 019 octets** de l'ancien mode carte : **la donnée
n'était pas le problème, c'étaient les primitives HGR.**

⚠ **Le fichier `MAP` doit être ajouté nommément à `PAYLOAD`,
`SCOSWAMP/SRC/Makefile:171`.** Le `find … 2>/dev/null` avale les fautes de frappe :
un nom faux se lit comme « aucune dépendance » et le disque garderait une carte
périmée sans le dire. C'est déjà arrivé à `MSGFR`/`MSGEN` (le disque gardait un
catalogue à `MSG_COUNT − 2` lignes, et toute l'interface partait vide) et à
`HELPFR`/`HELPEN`, absents de la liste. Le commentaire au-dessus de `PAYLOAD` le
rappelle : **« Les noms doivent être EXACTS. »**

### 7.7 Le coût mémoire et où loger le code

Carte mémoire **mesurée** sur `SCOSWAMP/SRC/build.map` (2026-09-03) :

| Zone | État | Marge |
| --- | --- | --- |
| `$0800-$0BFF` | tampon d'E/S ProDOS | — |
| `$0C00-$0FFF` | libre, réservé à un 2ᵉ fichier ouvert | 1 024 o |
| `$1000-$1FFF` | **`LOWBSS`** : catalogue, tampon de page, tampon HGR, barre de titre — `$1000-$1FAC`, 4 013 o | **83 o** |
| `$2000-$3FFF` | HGR page 1 | — |
| `$4000-$9D8A` | `STARTUP` + `LOWCODE` + `CODE` + `RODATA` | — |
| `$9D8B-$A311` | `DATA`, `INIT`, `BSS` | — |
| `$A312-$BD80` | **tas** (fenêtre principale) | **6 766 o** |
| `$BD80-$BF00` | pile C (`__STACKSIZE__ = $180`) | — |
| `$D400-$DF09` | **Language Card banque 2**, segment `LC`, 2 826 / 3 072 o | **246 o** |
| AUX 64 Ko | seul `$400-$7FF` sert (page texte 80 col.) | **~47 Ko** |

* **La Language Card est pleine** à 246 octets près : elle ne peut pas accueillir
  le mode carte. C'est là que vit le code froid, et il n'y a rien d'autre à y
  prendre sous ProDOS 8 — la banque 1 est le noyau, `$D000-$D3FF` de la banque 2
  son code de sortie. **`LOWBSS` n'a plus que 83 octets** : pas question d'y loger
  les 1 054 octets du fichier `MAP`.
* **La fenêtre principale offre 6 766 octets de tas.** En mode texte 80 × 24, code
  + données tiennent sous 2 Ko : ~1 054 octets chargés sur le tas au premier appui
  sur `M`, plus quelques centaines d'octets de code (grille, curseur, panneau).
  **C'est jouable dans la marge actuelle** — ce que le mode HGR n'était pas.
* **La RAM auxiliaire (~47 Ko) est le vrai gisement** pour la version HGR :
  données en lecture seule, donc cas d'usage exact de l'AUX. cc65 n'en sait rien
  et n'a pas besoin d'en savoir : un `AUXMOVE` (`$C311`) ou un basculement
  `RAMRD`/`RAMWRT` autour d'une copie suffit — sans marcher sur `$400-$7FF`.
* Piège avant de toucher `__HIMEM__` : `apple2enh.cfg` calcule la taille du BSS
  par `__HIMEM__ - __STACKSIZE__ - __ONCE_RUN__` ; quand le code déborde, la
  soustraction passe en négatif et **`ld65` ne signale rien**. Un lien qui réussit
  ne prouve pas que le programme tient : vérifier la fin du BSS dans le `.map`.

Coût d'état côté moteur : **1 octet** (`app.clairiere_courante`). Le bitmap
`visited` (52 o) et la mémoire des monstres (160 o) existent et sont déjà sauvés.

### 7.8 Ordre d'implémentation

1. **Corriger le corpus** — les deux mots de `N230` et `N217`, puis les 11 lignes
   `V` (§ 6.2). Sans elles la carte proposera des retours qui n'existent pas ;
   avec elles, 25 clairières sur 35 ont une revisite explicite et les pages
   inaccessibles tombent de 19 à 8. Vérifier par `reflow_txt.py` (invariant « `V`
   en tête ») et par un BFS depuis la page 001.
2. **Ajouter le contrôle FR/EN manquant** à `reflow_txt.py` : « même
   multi-ensemble de cibles dans les deux langues ». 20 lignes, et les bugs des
   pages 347 et 382 apparaissent (§ 6.1 J).
3. **Écrire `SCOSWAMP.MORE/TOOLS/build_map.py`** : il lit `carte.json`, applique
   les trois arbitrages de rabattement (§ 6.1 I) et écrit `SCOSWAMP/MAP`. Sa
   source est `carte.json`, pas la prose — c'est ce qui rend la génération
   reproductible et le retrait des numéros du texte (§ 6.3) sans conséquence.
4. **Déclarer `$(OUTDIR)/MAP` dans `PAYLOAD`** (Makefile:171), *nommément*.
5. **`show_map()` en mode texte**, sur le modèle de `show_inventory()` : bascule,
   sauvegarde de `app.video_mode`, boucle `cgetc()`, sortie sur `M`/`ESC` ; grille
   à gauche, panneau à droite, les trois états du § 7.3.
6. **Brancher `M`** dans `handle_user_input()`, **avant** la branche `A-Z` ;
   ajouter `M=CARTE` à `M_TOUCHES` et aux deux fichiers d'aide **via
   `build_messages.py`**.
7. **Griser `M`** sans `OBJ_ANNEAU`, avec son message.
8. **Le curseur de consultation** (flèches / `IJKL`, `RETURN` pour détailler) —
   c'est ce qui fait « une carte sur laquelle on se déplace ».
9. **Le fil Pompatarte** : un indicateur « votre carte est complète » dès que le
   bitmap contient un chemin continu de la clairière 1 à la page 280, et l'accès à
   la page 158 conditionné à ce test. Le menu MAP devient alors *l'objet de la
   quête* — et le corpus le dit déjà : « il vous faut un but plus digne que
   **tracer une simple carte** » (page 095).

### 7.9 Ce qui a été construit, et ce qui a bougé

| Point du § 7 | Réalisé | Écart |
| --- | --- | --- |
| fichier `MAP` généré depuis `carte.json` | `TOOLS/build_map.py` → `SCOSWAMP/MAP.BIN`, 1 844 octets | version 3 du format, deux blocs de langue au lieu d'un pool de créatures |
| table des clairières | 35 × **3** octets | `x` et `y` tiennent dans un octet ; le nom est à offset fixe, pas de champ ; les pages ne sont plus indexées par clairière |
| table des sentiers (39 × 3) | **supprimée** | le voisin est la première case occupée dans la direction annoncée ; les trois sentiers de deux cases sortent gratuitement, et les 117 octets avec |
| rabattement page → clairière | 115 paires (écart, clairière) = **230 octets** | la table plate de 412 octets ne tenait pas ; la boucle coûte trente octets de code et sert aussi au brouillard de guerre |
| pool de noms de créatures | **remplacé** par 35 noms de lieu ≤ 12 caractères, FR et EN | le livre demande le nom de la créature ; le nom du lieu tient sur la ligne de lieu de chaque page, ce que le livre ne prévoyait pas |
| les trois états du § 7.3 | tels quels | — |
| maquette 80 × 24 du § 7.4 | rendue à l'octet près | titre raccourci en « CARTE DU MARAIS » (14 octets de pool) ; pas de curseur de consultation |
| `M` grisée sans l'Anneau | **refus** avec message | choisi contre « carte désorientée » : un second rendu coûtait des centaines d'octets, et le refus donne son prix à la page 049 |
| coût mémoire : 1 octet d'état | 1 octet (`map_here`), **sauvegardé** — le format passe de `SCS3` à `SCS4` | 297 pages sur 412 ne sont d'aucun lieu : sans lui, reprendre en plein combat rouvrait la carte sans savoir où |
| « le tas offre 6 766 octets » | **faux au 2026-09-04** : il en restait 510 | c'est la musique et les objets qui les ont pris entre-temps. Le kilo-octet de `$0C00-$0FFF` — le second tampon ProDOS que le jeu ne réclame jamais — a fourni la place |
| curseur de consultation (§ 7.8 point 8) | **non fait** | il demandait ce qui manquait le plus : de la place |
| fil Pompatarte (§ 7.8 point 9) | **non fait** | — |

Deux corrections de modèle ont été appliquées par `build_map.py`, dans l'esprit
des `FIX` du § 8 : la direction d'un sentier est **dérivée de la grille** et non
du libellé (ce qui règle l'incohérence A sans table d'exception), et la
clairière 14 reçoit la sortie `S` que sa prose annonce et que son libellé de
choix ne porte pas (incohérence C). Le script **vérifie** ensuite, arête par
arête, que la recherche « première case occupée dans cette direction »
retrouve bien le voisin de `carte.json` : 39 sur 39.

---

## 8. Annexe — regénérer la carte

La carte a été dérivée du corpus par une chaîne de scripts (dans le scratchpad de
la session, non versionnés), listés ici dans l'**ordre d'exécution**. Le seul
livrable versionné est `SCOSWAMP.MORE/carte.json`.

| # | Script | Rôle | Sortie |
| --- | --- | --- | --- |
| 1 | `extract.py` | parse les 412 pages de `TEXTFR` en `{titre, prose, choix, directives}` selon la grammaire de `classify_line` ; détecte les directions dans les libellés `C` | `pages.json`, `pages.pkl` |
| 2 | `graph.py` | construit le graphe orienté complet : tous les champs cibles du § 2.4, **sans** `CE` | `graph.json`, `graphe_pages.json` |
| 3 | `hubs.py` | fermeture avant : depuis une page d'arrivée, remonte le graphe jusqu'au premier hub sans traverser un autre hub | — |
| 4 | `sig.py` | calcule la signature de sorties `{direction → {voisins}}` de chaque hub | `sig.json` |
| 5 | `canon.py` | union-find itéré jusqu'au point fixe : deux hubs de même signature sont la même clairière. **58 hubs → 39 groupes**, puis 4 corrections manuelles → **35** | `canon.json`, `adj.json` |
| 6 | `entries.py` | rattache les pages d'entrée et de revisite à leur clairière | `entries.json` |
| 7 | `grid.py` | le modèle canonique, établi à la main après vérification page par page : `clr`, `hubs`, `e1` (1re visite), `ev` (revisites), titre, contenu | `model.json` |
| 8 | `layer.py` | placement en couches : contracte les composantes reliées par N/S (même `x`), oriente les arêtes E/O, calcule les niveaux par plus long chemin dans le DAG ; idem pour `y`. Détecte les cycles impairs | — |
| 9 | `relax.py` | relaxation des positions sous les contraintes d'ordre | — |
| 10 | `final.py` | le placement retenu, trois collisions levées à la main ; **revérifie les 68 contraintes une par une** | `pos.json` |
| 11 | `ascii.py` | rend les deux dessins du § 5 | `carte_ascii.txt`, `carte_ascii_pages.txt` |
| 12 | `mkjson.py` | assemble le livrable : clairières, hubs, pages, coordonnées, sorties, voisins, notes | **`carte.json`** |
| 13 | `paths.py` | BFS sur les 35 clairières : chemins critiques des trois missions, test du pont | — |
| 14 | `mockup_map.py` | rend la maquette 80 × 24 du § 7.4 depuis `carte.json` ; **assertions sur 24 lignes et 80 colonnes** | — |

Deux constantes reviennent dans les scripts 8 à 11 et **doivent y rester** tant que
le corpus n'est pas corrigé (§ 6.2) :

```python
FIX  = {(230, 'E'): 'N'}   # page 352 dit "en direction du nord"
SKIP = {(218, 'O')}        # Feu Follet : teleportation, pas un sentier
```

Commandes de contrôle, à rejouer avant toute regénération :

```bash
cd /Users/gistair/src/pom2adventure
find SCOSWAMP/TEXTFR -name '*.TXT' | wc -l                     # 412
python3 SCOSWAMP.MORE/TOOLS/reflow_txt.py SCOSWAMP             # 0 probleme attendu
python3 SCOSWAMP.MORE/TOOLS/reflow_txt.py SCOSWAMP --derive | tail -60
grep -rl -E '^V ' SCOSWAMP/TEXTFR/N*/N*.TXT | wc -l            # 14 aujourd'hui, 25 apres les correctifs
grep -rniE "clairiere (n|no|numero) ?[0-9]+" SCOSWAMP/TEXTFR SCOSWAMP/TEXTEN | wc -l   # 0
python3 -c "import json; print(len(json.load(open('SCOSWAMP.MORE/carte.json'))['clairieres']))"  # 35
```

---

## Récapitulatif des chiffres

| | |
| --- | --- |
| pages | 412 (`N000`-`N411`) × 2 langues = **824 fichiers** ; 188 810 o FR / 167 310 o EN |
| page la plus longue | 1 252 o = `FILE_BUFFER_SIZE − 1`, à l'octet (`N361`) |
| directives | **31** reconnues, **30** employées ; 568 lignes `C` sur 335 pages ; **26** lignes `V` |
| graphe | 412 nœuds, **743 arcs**, **0 cible manquante**, 1 composante faible |
| pages terminales | **21** — 11 morts, 3 victoires (158, 175, 358), 7 fins vivantes |
| pages inaccessibles depuis 001 | **19** → **1** (la page de titre 000) après les correctifs du § 6.2 |
| pages à choix directionnels | **58**, pour **111** choix, tous cardinaux |
| **clairières canoniques** | **35** (30 numéros du livre, 4 anonymes, le 9 en double) |
| pages-hub | **58**, regroupées en 35 ; **116** pages rattachées à un lieu, soit 3,3 par clairière |
| **grille** | **6 × 9 = 54 cases**, 35 occupées, 19 vides |
| **sentiers** | **39 arêtes** = 37 réciproques + 2 sens unique ; 38 vrais sentiers + 1 téléportation ; 3 font deux cases |
| moitiés nord / sud | 12 / 23 clairières, un seul passage : le pont (clr 35) |
| chemins critiques | Pompatarte 14 sentiers, Gayolard 11, Stratagus (Jardins) 12 |
| état moteur nécessaire | `SCENE_MEMORY_SIZE = 52` o (déjà là, déjà sauvé) + **1 octet** |
| fichier `MAP` estimé | **~1 054 octets** (743 sans les noms de créatures) |
| marges mesurées (`build.map`) | tas **6 766 o**, `LOWBSS` **83 o**, `LC` **246 o**, AUX **~47 Ko** |
| ancien mode carte (retiré) | **5 019 octets** — les primitives HGR, pas la donnée |
