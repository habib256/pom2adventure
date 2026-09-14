# Le menu MAP — rapport de chantier

Branche `feat/scoswamp-map`, 2026-09-04. Base : `feat/scoswamp-memoire`
(fusionnée en cours de route, voir § 8).

> « Pour vous aider à établir votre carte, **toutes les clairières ont été
> numérotées**. […] ces sentiers sont orientés au nord, au sud, à l'ouest ou à
> l'est. » — *Le Marais aux Scorpions*, p. 14-15.

Le Marais est le seul *Défis Fantastiques* où le lecteur **doit** dessiner sa
carte, et l'une des trois missions — celle de Pompatarte — consiste à en
rapporter une. La touche `M` la tient à sa place, et ne montre que ce qu'elle a
vu.

---

## 1. L'écran, relevé dans l'émulateur

Relevé le 2026-09-04 sur `POM2 --preset iie dist/SCOSWAMP.HDV
--ai-control=6510`, lu par `GET /mem?addr=0x0400&len=1024` (colonnes impaires)
et `&bank=aux` (colonnes paires). Le joueur a suivi
`clr 1 ─O→ 4 ─N→ 34 ─N→ 18` et se bat contre les Arbres-Épées ; la carte a été
ouverte **en plein combat**, depuis le mode mixte.

```
 CARTE DU MARAIS -- 4 clairieres sur 35
   0     1     2     3     4     5
0                                     N 18  Arbres-Epees
                                      SORTIES
1                                       N  ?             inexploree
                                        S  R. profonde   vue
2                                       O  ?             inexploree

3

4
                                      LEGENDE
5        ?                              (nn) clairiere vue
         |                              <nn> vous etes ici
6     ?-<18>                            --   sentier emprunte
         |                              -?   sentier connu
7       (34)                            v    hors du Marais
         |
8       ( 4)--( 1)-?                  4 clairieres sur 35
               v



M ou ESC : retour au recit
```

La ligne 1 est en vidéo inverse comme celle du récit, et `<18>` l'est aussi.
Le `v` sous `( 1)` est la lisière sud du Marais — ce n'est pas un sentier, il a
son signe. Le `?-` à gauche de `( 1)` est la clairière 12, connue par sa
direction mais pas encore visitée.

Et la même routine, sur les 35 clairières allumées (rendue depuis `MAP.BIN`
par le même algorithme, pour montrer où l'écran va) :

```
CARTE DU MARAIS -- 35 clairieres sur 35
    0     1     2     3     4     5
0 ( ?)        (19)--(27)  (11)        N 35  Le Pont
   |           |           |          SORTIES
1  |    (15)--( ?)--------( 7)          N  Nid d'Aigle   vue
   |     |     |           |            S  Scorpions     vue
2 ( 9)--(28)  (32)--(16)--(30)
                     |
3       (33)--(20)  <35>
         |     |     |
4 (14)  ( ?)  ( 9)--(13)--( 3)--(21)
   |     |     |           |          LEGENDE
5 (23)--(29)--( 5)--(24)--(26)          (nn) clairiere vue
         |           |     |            <nn> vous etes ici
6 ( ?)--(18)        (17)  ( 8)          --   sentier emprunte
         |           |                  -?   sentier connu
7       (34)         |                  v    hors du Marais
         |           |
8       ( 4)--( 1)--(12)--(25)        35 clairieres sur 35
               v
```

C'est trait pour trait le dessin du § 5.3 de `CARTOGRAPHIE.md`, celui qu'on a
établi à la main : la rivière Croupie sur la ligne `y = 3`, le pont (35) seul
trait vertical qui la franchit, et les trois sentiers de deux cases —
9 ⇄ Courbensaule, croisement ⇄ 7, et 17 ⇄ 12.

La **ligne de lieu**, sous la barre de titre, relevée sur trois pages :

```
  Rond-point   sorties E O   deja visitee            (page 058, la clairière)
  Arbres-Epees   sorties N S O                       (page 022, première visite)
  (Arbres-Epees)                                     (page 028, le combat)
```

Les parenthèses disent « souvenir, pas position » : la page 028 n'est d'aucun
lieu, c'est la clairière **collante** qui parle.

---

## 2. Ce qui a été livré

### 2.1 Le fichier de données

`SCOSWAMP.MORE/TOOLS/build_map.py` lit `SCOSWAMP.MORE/carte.json` et écrit
`SCOSWAMP/MAP.BIN` (**1 844 octets**), que l'empaqueteur dépose sur le volume
sous le nom `MAP` — l'extension finale tombe, comme pour `MUSIC/<NOM>.MB.BIN`.
Il est **nommément** dans `PAYLOAD` (`Makefile:444`) et dépendance directe de
`$(HDV)` : le `find … 2>/dev/null` avale les fautes de frappe, et une carte
périmée sur le disque ne se voit pas — elle montre seulement les mauvaises
clairières.

| Bloc | Taille | Contenu |
| --- | ---: | --- |
| en-tête | 20 o | `'M','A','P',3`, 35 clairières, 115 pages, largeur d'un nom, clairière de départ, le pont, la ligne de la rivière, pages des deux sorties et du départ, longueur des deux blocs de langue |
| clairières | 3 × 35 = 105 o | `x \| (y<<3)`, numéro du livre (0 = anonyme), masque des sorties |
| rabattement page → clairière | 2 × 115 = 230 o | (écart depuis la page précédente, index de clairière), trié |
| bloc français | 743 o | 35 noms de 13 octets, puis 17 chaînes de l'écran |
| bloc anglais | 746 o | idem |

Le masque des sorties porte `N S E O` sur les bits 0-3, puis trois bits pour ce
qui n'est pas un sentier : bit 4 la lisière du Marais (page 208), bit 5 la
falaise où plonger tue, bit 6 la téléportation du Feu Follet.

**Il n'y a pas de table des sentiers.** Une clairière annonce ses directions ;
le voisin est la première case occupée de la ligne ou de la colonne. C'est ce
qui rend gratuits les trois sentiers de deux cases que la grille a dû étirer —
« un sentier peut suivre un tracé sinueux mais sa direction générale restera
toujours la même ». Le script **vérifie** arête par arête que cette recherche
retrouve bien le voisin de `carte.json` : 39 sur 39, et il refuse d'écrire
sinon. Économie : les 117 octets de la table du § 7.6, et le code qui l'aurait
lue.

Deux corrections de modèle y sont appliquées, dans l'esprit des `FIX` du § 8 de
`CARTOGRAPHIE.md` :

* **la direction est dérivée de la grille**, jamais du libellé — ce qui règle
  l'incohérence A (page 230 dit « vers l'est », la page 352 qui la suit dit
  « EN DIRECTION DU NORD ») sans table d'exception ;
* **la clairière 14 reçoit la sortie `S`** que sa prose annonce et que son
  libellé de choix ne porte pas (incohérence C).

Les trois arbitrages du § 6.1 I (363 → clr 19, 394 → clr 21, 330 → clr 12) sont
déjà dans `carte.json` ; le script vérifie qu'aucune page n'est revendiquée
deux fois.

Les **35 noms courts** (≤ 12 caractères, FR et EN) sont écrits à la main dans
le script : les titres de page (« Deux directions », « Trois chemins herbeux »)
nomment l'événement, pas le lieu, et le livre demande de porter le lieu sur la
carte.

### 2.2 L'écran, en texte 80 × 24

Le mode texte ne demande **aucune primitive de tracé** — c'est ce qui a coûté
5 019 octets à l'ancien mode carte, retiré faute de place — et **rien à
sauvegarder** : les bascules vidéo ne touchent que des soft-switches, la page
texte reste en `$400-$7FF` pendant tout le passage en graphique. Presser `M`
depuis l'illustration ne coûte donc pas une copie de la page HGR.

La grille tient en 34 colonnes (6 cases de 4 caractères, 5 liaisons de 2) et 17
lignes ; le panneau part de la colonne 38. Le brouillard de guerre sort du seul
bitmap `visited` (52 octets, déjà sauvegardé) : une clairière est vue dès
qu'**une** de ses pages l'est, quelle que soit la porte par laquelle on y est
entré — c'est le même rabattement que les listes des lignes `V` expriment page
par page dans le corpus. Aucun second bitmap, ni pour les clairières ni pour
les sentiers : un sentier est emprunté quand ses deux bouts sont vus.

### 2.3 L'Anneau de Cuivre : la touche est **refusée**

> « Personne n'a jamais pu dresser une carte de cette région […] et **les
> boussoles elles-mêmes en perdent le nord**. […] aussi longtemps que vous
> garderez cet anneau à votre doigt, vous saurez toujours où est le nord. »
> (PDF p. 17)

Sans `OBJ_ANNEAU`, `M` affiche « Sans l'Anneau de Cuivre, les boussoles perdent
le nord. » et rend la main. **Pourquoi le refus plutôt qu'une carte
désorientée :**

1. C'est ce que dit le livre. L'Anneau n'aide pas à lire la carte, il *autorise*
   la carte : une carte qu'on ne peut pas orienter n'est pas une carte.
2. Une carte sans orientation demandait un **second rendu** — grille sans axes,
   sentiers sans direction, panneau sans sorties — soit plusieurs centaines
   d'octets dans un binaire où il en restait 510.
3. Le refus donne son prix à la page 049, où l'on peut **vendre** l'anneau. Le
   dilemme devient réel : on perd la carte, donc la mission de Pompatarte.

Le héros part avec l'Anneau, donc la touche répond dès le premier pas ; c'est
seulement en le vendant qu'on la perd.

### 2.4 La clairière collante

**297 pages sur 412** — combats, dialogues, morts, prologue — ne sont d'aucun
lieu. `load_scene` met à jour `map_here` seulement quand la page en désigne une
(`map_of_page`), et le garde sinon : presser `M` au milieu du combat contre
l'Herbe à Pinces montre l'Herbe à Pinces.

Un octet en RAM, et un octet de plus dans les sauvegardes : le format passe de
`SCS3` à `SCS4`, la clairière courante s'écrivant après la mémoire des
monstres. Sans lui, une partie reprise en plein combat rouvrait la carte sans
savoir où l'on se tient. Les anciennes sauvegardes sont **refusées par la
signature**, pas lues de travers. `SCOSWAMP.MORE/TOOLS/forge_save.py` suit
(`clairiere=` en argument, 277 octets).

### 2.5 La ligne de lieu

`render_scene` laisse la ligne 2 vide chaque fois que le corps tient en 18
rangs sur les 19 — c'est le cas de tout le corpus sauf quelques pages. La ligne
de lieu s'y installe :

* `<nom>   sorties N S O   deja visitee` quand la page appartient à la
  clairière ;
* `(<nom>)` — plus discret — quand c'est la clairière collante qui parle ;
* **rien** quand la page prend ses 19 rangs. C'est le cas de la page 195, la
  première du Marais : vérifié dans l'émulateur, la ligne est bien omise et
  aucun rang de texte n'est perdu.

Les libellés viennent du fichier `MAP` (voir § 4), les lettres de direction
aussi : `NSEO` en français, `NSEW` en anglais.

### 2.6 La touche

`M` est testée **avant** la branche `A-Z` de `handle_user_input`, comme le
demandait le § 7.5 : elle y serait lue comme l'index 12, donc jamais un choix
valide, mais le code deviendrait fragile au premier élargissement. Elle est
aussi acceptée **en plein combat** — c'est le moment où l'on décide de fuir, et
où savoir vers quoi compte. Le tour de boucle suivant repeint la barre, le
bandeau et l'invite, comme après le sac à dos.

`M` referme, `ESC` aussi. Le mode vidéo du joueur lui est rendu.

`M_TOUCHES` devient `ESPACE=VUE  A-Z=CHOIX  I=SAC  M=CARTE  Q=QUITTER`, la barre
de titre `I:SAC M:CARTE H:AIDE`, et les deux fichiers d'aide gagnent une
section `CARTE` / `MAP` — à 18 lignes exactement, ce que `show_help` peut
afficher.

---

## 3. La mémoire : ce qu'il a fallu libérer

**Marge de départ : 510 octets de tas** (mesure au lien sur la base fusionnée).
**Marge d'arrivée : 314 octets** — 249 après la seconde fusion (§ 8). Entre les deux, le chantier a demandé environ
**2 900 octets** — 1 950 de code, 950 de données résidentes.

### 3.1 Le levier décisif : `$0C00-$0FFF`

`SRC/scoswamp.cfg` réservait ce kilo-octet « à un second fichier ouvert », et
`DOCS/MEMOIRE.md` notait « jamais le cas aujourd'hui ». Vérifié source par
source : **le jeu n'ouvre qu'un fichier à la fois**, chaque `fopen` étant suivi
de son `fclose` avant le suivant — texte, image, musique, aide, sauvegarde,
catalogue, et maintenant carte. La zone `MAPRAM` et le segment `MAPBSS` y
logent 1 023 des 1 024 octets :

| Contenu | Taille |
| --- | ---: |
| `map_data[884]` — en-tête, clairières, bloc de langue | 884 o |
| `visited[52]` de `rules.c` — le bitmap des pages vues | 52 o |
| en-tête de sauvegarde de `slot_title`, liste de `choose_stones`, statiques de `cfmt` | 87 o |

**Ce sont 1 023 octets qui ne coûtent rien à la fenêtre principale.** La
contrepartie est écrite dans le `.cfg` et dans `MEMOIRE.md` : plus jamais deux
fichiers ouverts en même temps, `iobuf-0800` distribuant ses tampons de 1 Ko à
partir de `$0800` vers le haut sans connaître `MAPRAM`.

### 3.2 Les gains, mesurés un par un

Chaque ligne est un lien complet, la précédente en place.

| # | Levier | Gain |
| ---: | --- | ---: |
| 1 | **`--codesize 100`** passé à cc65. Le compilateur en prend bien plus par défaut : 17 248 octets de `CODE` sur `scoswamp.c` sans l'option, 16 309 avec. En **dessous** de 100 le générateur cesse d'employer certaines séquences en ligne et le code **regrossit** (19 255 à 90) : le minimum est un plateau de 100 à 130. | **+ 1 310 o** |
| 2 | **Zone `MAPRAM`** (§ 3.1) — hors fenêtre, ne se mesure pas au tas | *+ 1 023 o* |
| 3 | `int` → `unsigned char` sur les indices, comparaisons et booléens de `scoswamp.c` ; `is_fr()` (un test d'initiale) à la place des deux `strcmp(app.language, "FR")` ; `load_hgr_image()`, **morte** depuis les images de bataille, supprimée | **+ 228 o** |
| 4 | Tampon du décodeur HGR de 1 Ko à **256 octets** (ProDOS lit par blocs de 512 et les met en cache dans son propre tampon : même nombre de blocs lus, seulement plus d'appels à `fread`), puis `app` (238 o), la barre de titre, les lignes de corps, les deux noms de musique et la table des pages partis en RAM basse | **+ 416 o** |
| 5 | **`classify_line`** : les 31 directives dans une table de 33 × 4 octets (deux lettres, troisième caractère exigé, drapeau « effet d'entrée ») et un `switch`, à la place de 29 cascades `c0 == 'X' && c1 == 'Y' && c2 == ' '` **et** du pavé de douze comparaisons du garde `restoring`. Mêmes règles, même ordre — les préfixes de deux lettres devant la lettre seule — lues au lieu d'être dépliées | **+ 336 o** |
| 6 | `map_voisin` et `map_str` dans la **Language Card** (elles ne touchent pas ProDOS) ; `show_help` emprunte la barre de titre et `display_language_selection` le tampon de page, au lieu de deux tampons de 81 octets à eux | **+ 531 o** |
| 7 | Toutes les pannes de disque par une seule fonction `oops(etape)` : cinq variantes écrites à la main, chacune avec ses chaînes, pour des pannes qu'un disque correct ne produit jamais | **+ 213 o** |
| 8 | `visited[]`, `slot_title`, `choose_stones` et les statiques de `cfmt` déménagés en `MAPBSS` | **+ 175 o** |
| 9 | *(dépense)* `wipe()` généralisée à tous les écrans, pour le bug du § 5 | *− 7 o* |
| — | **Non retenu** : `MUSIC_OVER` de 1 280 à 1 216 (voir § 8) | *(− 64 o)* |

Contrôle final :

```
Analyse mémoire : build.map
  Chargement    : $4000
  BSS           : $AD1F - $BC87
  Tas           : $BC87 - $BD80  (249 o)
  Plafond       : $BD80  (__HIMEM__ $BF00 moins 384 o de pile C)
  Empreinte     : 31879 o sur 32128 o disponibles
  LOWBSS        : $1000 - $1FE8  (4073 o, reste 23 o sous $2000)
  MAPBSS        : $0C00 - $0FFF  (1024 o, reste 0 o sous $1000)

OK : tient en mémoire, marge de 249 octets.
```

`tools/check-memory.sh` affiche désormais `MAPBSS` comme il affiche `LOWBSS`, et
refuse un débordement dans `LOWRAM`.

### 3.3 Les trois marges, et ce qui les garde

| Zone | Reste | Qui refuse le dépassement |
| --- | ---: | --- |
| tas (fenêtre principale) | 249 o | `check-memory.sh`, à chaque `make` |
| `LOWBSS` (`$1000-$1FFF`) | 36 o | `ld65`, puis `check-memory.sh` |
| `MAPBSS` (`$0C00-$0FFF`) | 1 o | `ld65` |
| `map_data[884]` | 13 o | `build_map.py`, qui dit quoi raccourcir |
| Language Card | 6 o | `ld65` |

C'est serré partout, et c'est voulu : chaque zone a son garde-fou, et aucun
n'est silencieux.

---

## 4. Où vit le texte de l'écran MAP

Les 17 chaînes de l'écran (titre, légende, `SORTIES`, `vue`, `inexploree`, le
refus de l'Anneau, les lettres `NSEO`) **ne passent pas** par
`build_messages.py`. Le catalogue `MSGFR`/`MSGEN` est chargé en RAM basse, où
il ne restait que 39 octets ; le bloc de langue du fichier `MAP`, lui, vit dans
le kilo-octet de `$0C00`. Elles voyagent donc avec les noms de clairière, dans
`build_map.py`, sous la même règle : **l'ordre fait foi**, et il suit
l'énumération `MS_*` de `scoswamp.c`.

Cette règle s'est vérifiée à la dure : la première version avait une chaîne de
moins que l'énumération, et l'écran affichait la légende à la place de son
titre et le refus de l'Anneau à la place de la ligne des touches. Le
commentaire de la table le dit maintenant, avec l'exemple.

Seul `M_TOUCHES` a bougé au catalogue (`+ M=CARTE`, 9 octets de RAM basse).

---

## 5. Deux bugs trouvés en chemin

**Le fond de l'écran ne s'effaçait qu'à moitié — et ce n'était pas la carte.**
Ouverte depuis le mode mixte, c'est-à-dire en plein combat, la carte laissait
l'ancienne page dans une colonne sur deux. `clrscr()` passe par `HOME` du
firmware, qui n'atteint la banque auxiliaire de l'écran 80 colonnes que si
l'entrée en graphique n'a pas dérangé ses commutateurs ;
`videomode(VIDEOMODE_80COL)` n'y change rien, cc65 ne réémettant sa séquence
que sur changement. `cclearxy` emprunte le même chemin que `cputc`, et celui-là
écrit bien dans les deux banques : la preuve était sous les yeux, la carte se
dessinait juste, seul le fond restait sale.

En cherchant, on s'est aperçu que **le défaut ne venait pas de la carte** : une
page repeinte après un combat gardait déjà la précédente dans une colonne sur
deux, depuis toujours. C'était invisible tant que rien n'occupait 80 colonnes.
`wipe()` a donc remplacé `clrscr()` dans **tous** les écrans du jeu — le récit,
le sac, les sauvegardes, l'aide, le choix des Pierres, la carte — pour le même
prix, un appel contre un appel, et elle rend la main avec le curseur en haut à
gauche exactement comme `clrscr`. Vérifié dans l'émulateur : la page qui suit
le combat des Sangsues, avec son jet de dé, est propre.

Dans la carte, `wipe()` est appelée à l'entrée **et à la sortie** : sinon les
queues de la grille resteraient derrière le texte de la page suivante.

**La ligne de lieu ne s'effaçait pas non plus.** Un nom court écrit par-dessus
un nom long laissait traîner la fin du précédent : « (Arbres-Epees) » suivi du
« deja visitee » de la Rivière profonde. Même recette que le bandeau de combat :
on écrit, puis on pousse des espaces jusqu'au bord, en un seul passage et sans
clignotement (`pad_to(79)`).

---

## 6. Vérifications

| Contrôle | Résultat |
| --- | --- |
| `python3 SCOSWAMP.MORE/TOOLS/reflow_txt.py SCOSWAMP` | `a reecrire : 0 fichiers` / **`problemes : 0`** |
| `cd SCOSWAMP/SRC && make` | **`OK : tient en mémoire, marge de 249 octets.`** |
| `make playtest` | **225 assertions passées, 1 en échec sur 24 scénarios** (voir § 8) |
| `make hdv` | `SCOSWAMP: 1330 files, 7610 blocks` ; `MAP` présent sur le volume (vérifié dans les entrées de répertoire de l'image) |
| `cmake --build … --target test_rules && …/test_rules` | **`regles : tout passe`** |
| `python3 build_map.py --root .` | `MAP.BIN : 1844 octets` ; `resident en $0C00 : 871 / 884` ; 39/39 sentiers retrouvés par la recherche de voisin |
| Essai `POM2 --preset iie … --ai-control=6510` | carte ouverte depuis une page **et** depuis un combat, ligne de lieu sur trois formes, retour au récit propre |

Les tests ajoutés à `test_rules.c` (`test_carte`) lisent `MAP.BIN` là où
`build_map.py` l'écrit et **rejouent à l'identique** les deux boucles du
moteur, `map_of_page` et `map_seen`. Le moteur lui-même ne peut pas être lié
sur la machine hôte — il parle à ProDOS et à l'écran — mais la table, elle, est
de l'arithmétique pure, et c'est elle qui décide quelle clairière la touche `M`
montre. Ce qu'ils défendent :

* la table est **triée et sans doublon** — c'est ce qui autorise la sortie
  anticipée de `map_of_page` ;
* la page 195 est bien la clairière n° 1, « Rond-point » ;
* **118 et 303 sont la même clairière** — le sentier de l'est dépose sur 118,
  le pont dépose au sud sur 303 : c'est exactement ce que les listes des lignes
  `V` disent page par page ;
* les trois arbitrages du § 6.1 I, et leurs contre-épreuves (363 n'est **pas**
  le Maître des Jardins, 330 n'est **pas** la Bête du bassin) ;
* le prologue, un combat, la sortie sud et l'écran d'accueil ne sont d'**aucun**
  lieu — c'est ce qui rend la clairière collante nécessaire ;
* arriver par le pont allume la clairière 13 et **elle seule** ;
* toutes pages vues, les **35** clairières s'allument.

---

## 7. Ce qui n'a pas été fait

* **Le curseur de consultation** (`IJKL` / flèches, `RETURN` pour détailler,
  § 7.8 point 8) : il demandait ce qui manquait le plus, de la place. La ligne
  du bas annonce donc `M ou ESC : retour au recit` et rien d'autre.
* **Le fil Pompatarte** (§ 7.8 point 9) : l'indicateur « votre carte est
  complète » et l'accès conditionné à la page 158.
* **Le nom de la créature sur chaque cercle**, que le livre demande. Le fichier
  `MAP` porte les noms de **lieu** à la place : ils servent à la fois au
  panneau et à la ligne de lieu de chaque page, ce que le livre ne prévoyait
  pas. La mémoire des monstres (160 octets, `MONSTER_SLOTS = 40`) est là et
  attend.
* **`M` n'est pas annoncée dans le bandeau de combat** (elle l'est dans la
  barre de titre et dans l'aide) : il aurait fallu une chaîne de plus, et il
  restait 13 octets dans `map_data`.

---

## 8. La seconde fusion : quatre chantiers arrivés d'un coup

`feat/scoswamp-memoire` a encore avancé pendant que la carte se construisait,
avec quatre fusions : **contenu** (`CI FAUX` en 025, le drapeau `.T`, les pages
124/126/140, sept fins muettes ou endeuillées, deux boucles `V` défaites),
**prologue** (pages 412-419, `000 → 419 → 001`, `SCENE_MEMORY_SIZE` à 53),
**combat rythmé** (`run_combat` réécrit : quatre dés dans `Round`, `sfx_beat`,
`put_verdict`, jauge en pavés inverses, enjeu de la Chance) et **playtest**
(`TOOLS/playtest.py`, cible `make playtest`, `-Wl -Ln,build.lbl`).

**Quatre conflits, tous petits.**

| Fichier | Conflit | Résolution |
| --- | --- | --- |
| `SRC/Makefile` | la ligne `.PHONY` : ma cible `map`, leur cible `playtest` | les deux |
| `TOOLS/forge_save.py` | `SCENE_MEM` 52 → 53 (prologue) contre mon octet `CLR` | les deux : `24 + 53 + 160 + 1`, **`SAVE_SIZE = 278`** |
| `SRC/messages.h` | leur suppression des doublons `M_CHANCEUX2` contre mon `M=CARTE` | régénéré par `build_messages.py` — 56 messages |
| `SCOSWAMP.BIN` | binaire | régénéré par `make` |

`scoswamp.c` et `rules.c` se sont fusionnés seuls, mais méritaient un audit :

* **`classify_line`** — vérifié directive par directive : leur branche n'y a pas
  touché, les 31 restent les mêmes, ma table de 33 entrées les couvre toutes.
* **`run_combat`** — leur réécriture est intacte, et ma branche `[M]` s'y est
  posée à côté de `[I]`.
* **`SAVE_SIZE`** — se calcule depuis `SCENE_MEMORY_SIZE` : il a suivi 52 → 53
  tout seul, `+ 1` pour la clairière, soit 278 octets, comme `forge_save.py`.
* **`wipe()`** — un `clrscr()` restait dans `game_over`, l'écran de mort, qu'on
  atteint depuis le mode mixte : c'est exactement le cas du § 5. Il est passé à
  `wipe()`.

**Le prix en mémoire.** La marge de leur base était de 284 octets, la mienne de
314 ; ensemble, 89. Il a fallu retrouver 160 octets, et le gisement était le
même qu'avant : le tampon du décodeur HGR est passé de 256 à **128 octets** —
ProDOS lit toujours le même nombre de blocs, trois `fread` sur quatre ne sont
plus qu'une recopie depuis son cache — ce qui a fait place en RAM basse à la
**mémoire des monstres** (`seen[40]`, 160 octets) de `rules.c`.
**Marge finale : 249 octets.**

**Le banc.** Deux garde-fous de `playtest.py` reposaient sur des voisinages que
le menu MAP a défaits : `sizeof(AppState)` se mesurait par `_restoring - _app`,
or `app` est parti en RAM basse (c'est `_file_buffer - _app` désormais), et la
taille de `seen` par `_visited - _seen`, or `visited` est parti en `$0C00`
(les tailles se lisent maintenant dans `rules.h`, à la source). Aucune
*attente de jeu* n'a été touchée. Un scénario **`carte`** a été ajouté — 16
assertions : la ligne de lieu sous ses deux formes, l'ouverture et la
fermeture par `[M]`, le compte des clairières, deux portes d'une même
clairière comptées une fois, et le refus sans l'Anneau.

Résultat : **225 assertions passées, 1 en échec sur 24 scénarios**. L'échec est
`images` — 13 pages sans planche : les 5 pages relais 407-411, que le § 2.5 de
`CARTOGRAPHIE.md` documente depuis toujours, et les 8 pages 412-419 du nouveau
prologue. Vérifié sur `feat/scoswamp-memoire` seule : `IMG/N400/` s'y arrête à
`N406`. C'est un vrai manque de contenu, pas une régression — l'assertion reste
debout.

---

## 8 bis. Ce que la première fusion a coûté

Le worktree avait été créé depuis `main` ; la base réelle du travail est
`feat/scoswamp-memoire`, détectée avant la première ligne de code — la branche
`feat/scoswamp-map` en part donc directement (`9f8c3ba`) et non de `main`.

En cours de chantier, `feat/scoswamp-memoire` a avancé de deux commits
(*The ten zone themes, a notch up, with drums* et *Thirty-five clearings, a
notch up, with drums*) : partitions reprises, 45 fichiers `.MB` régénérés.
`git merge feat/scoswamp-memoire` s'est fait **sans conflit** (264 fichiers,
aucun sur le moteur), mais il a coûté **un levier mémoire** :

> **`MUSIC_OVER` de 1 280 à 1 216 octets : annulé.** La plus grosse surcouche
> mesurait 1 216 octets à l'octet près avant la fusion ; les nouvelles
> partitions ont porté `VICTOIRE.MB` à **1 265** et `COMBAT.MB` à 1 228. Le
> levier est rendu à la musique : il ne restait que quinze octets de marge, et
> une surcouche refusée à la fabrication aurait coûté plus cher que 64 octets
> de moteur. `midi_to_mb.py` reste appelé avec `--max 1280`.

Les 64 octets ont été repris ailleurs (§ 3.2, lignes 7 et 8). Aucun autre
effet : `carte.json`, `CARTOGRAPHIE.md`, le corpus et le moteur n'avaient pas
bougé sur la branche de base.

---

## 9. Fichiers touchés

| Fichier | Ce qui change |
| --- | --- |
| `SCOSWAMP.MORE/TOOLS/build_map.py` | **nouveau** — écrit `SCOSWAMP/MAP.BIN` depuis `carte.json` |
| `SCOSWAMP/MAP.BIN` | **nouveau** — 1 844 octets, `MAP` sur le volume |
| `SCOSWAMP/SRC/scoswamp.c` | le bloc carte, `show_map`, `render_place`, la touche `M`, `SCS4`, `wipe()` à la place de `clrscr()`, la cure mémoire |
| `SCOSWAMP/SRC/scoswamp.cfg` | zone `MAPRAM` `$0C00-$0400`, segment `MAPBSS`, et la règle « un seul fichier ouvert » |
| `SCOSWAMP/SRC/rules.c` | `visited[]` en `MAPBSS`, `seen[]` en `LOWBSS` |
| `SCOSWAMP/SRC/hgr_loader.s` | tampon de lecture de 1 Ko à 256 octets |
| `SCOSWAMP/SRC/Makefile` | `--codesize 100`, cible `map`, `MAP.BIN` dans `PAYLOAD` et dans `$(HDV)` |
| `SCOSWAMP/SRC/music.h` | commentaire de `MUSIC_OVER` (valeur inchangée, voir § 8) |
| `SCOSWAMP.MORE/TOOLS/build_messages.py` | `M=CARTE` dans `M_TOUCHES` ; la note sur les chaînes de l'écran MAP |
| `SCOSWAMP.MORE/TOOLS/forge_save.py` | `SCS4`, 277 octets, `clairiere=` |
| `SCOSWAMP.MORE/TOOLS/test_rules.c` | `test_carte` : la table, le brouillard, les arbitrages |
| `SCOSWAMP.MORE/TOOLS/playtest.py` | scénario `carte`, et deux garde-fous d'adresses remis d'aplomb |
| `SCOSWAMP/HELPFR.TXT` / `HELPEN.TXT` | section `CARTE` / `MAP`, 18 lignes tenues |
| `tools/check-memory.sh` | affiche `MAPBSS` |
| `DOCS/MEMOIRE.md` | la zone `$0C00`, les mesures du jour |
| `SCOSWAMP/DOCS/CARTOGRAPHIE.md` | § 7.9 — ce qui a été construit, et ce qui a bougé |
