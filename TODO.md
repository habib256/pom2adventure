# dev — TODO

Backlog du développement **logiciel Apple II** (les jeux). L'émulateur qui
les fait tourner a le sien, dans `../pom2/TODO.md`. Même convention que lui :
`🟠 haute · 🟡 moyenne · 🟢 basse`, effort indicatif en *italique*, fichier en
`backticks`.

Mesures courantes : 2026-09-06. Cible : Apple //e enhanced, cc65 `apple2enh`, ProDOS 8.

L’[audit détaillé du binaire](DOCS/AUDIT-MEMOIRE-SCOSWAMP.md) fait référence
pour les chiffres actuels ; les entrées datées plus bas conservent leur
contexte historique.

## Corrigé le 2026-09-06 — sac en combat

`I:SAC` ouvre maintenant le sac après le premier assaut. HABILETÉ, ENDURANCE
et CHANCE restent interdites à ce moment ; consulter et refermer le sac
conserve le jet, la blessure en attente et le mode vidéo. Le retour en DHGR
plein restaure les deux banques du texte 80 colonnes. **86 assertions POM2
headless réussies**, dont comparaison au même combat sans ouverture du sac.
Voir [le défaut initial](DOCS/VALIDATION-PARCOURS.md#anomalie-du-sac-en-combat).

---

## Le gestionnaire de fichiers a demenage (2026-09-07)

Apple IIe Total Commander s'appelle desormais **A2 Retro Cmd** et vit dans son
propre depot, avec ses sources, ses bancs et son integration continue :

> **<https://github.com/habib256/a2retrocmd>**

Le jeu n'en est plus le conteneur, seulement l'hote : `SCOSWAMP/A2RETRO/`
porte une copie des quatre fichiers publies, tiree d'une Release par
`tools/update_a2retrocmd.py`, et la touche **[T]** de l'ecran-titre la lance.
Les etudes qui le concernaient -- la souris, notamment -- ont suivi la-bas.
Voir [DOCS/A2RETROCMD.md](SCOSWAMP/DOCS/A2RETROCMD.md).

## Priorité : débloquer la mémoire pour le système de combat

C'est la contrainte qui bloque le reste. Carte mémoire **mesurée** sur
`SCOSWAMP.BIN` tel qu'il est construit aujourd'hui (fichier `.map` du linker,
pas une estimation) :

| Zone | État mesuré le 2026-09-06 |
| --- | --- |
| `$0800–$0BFF` | Tampon ProDOS de 1 024 octets, un seul fichier à la fois |
| `$0C00–$0FFF` | MAPBSS 1 012 octets ; **12 libres** |
| `$1000–$1FFF` | LOWBSS 4 059 octets ; **37 libres** |
| MAIN et AUX `$2000–$3FFF` | DHGR : 8 Ko par banque |
| `$4000–$ADF7` | Code et données initialisées résidentes |
| `$ADF8–$BD62` | BSS principale : 3 947 octets, dont 3 584 de musique |
| `$BD63–$BD7F` | **29 octets avant la pile C** |
| `$BD80–$BEFF` | Pile C : 384 octets réservés ; pic à mesurer |
| LC banque 2 `$D400–$DFFF` | 3 045 octets utilisés ; **27 libres** |
| AUX hors écrans | Piste d'extension, disponibilité système à établir |

Les tableaux de pierres 8 bits ont rendu 48 octets de code et 24 de RAM.
Le contrôle de fin de BSS tient désormais compte de la borne inclusive de
ld65 et refuse un dépassement d'un seul octet. La prochaine priorité est la
mesure de pile avant de déplacer des locales statiques, puis l'étude du
buffer musical en AUX. Les essais de compilation sont chiffrés dans l'audit.

### Historique des pistes mémoire (les chiffres ci-dessous sont datés)

Par ordre de rendement décroissant :

- ✅ **1. `__HIMEM__ = $BF00`** — **fait le 2026-08-29**, pour faire entrer le
  moteur de combat. Le gain est **deja consomme** : apres le mode carte il
  reste **21 octets** avant la pile. La fenetre `$4000-$BF00` est pleine, et
  tout ce qui suit demandera le point 2 ou le point 4.
  Deux contreparties, dont une seule était prévue :
  - la prévue : plus de retour à BASIC, on sort par le QUIT ProDOS ;
  - **l'imprévue** : le binaire fait maintenant 22 Ko et s'étend jusqu'à
    `$97xx`, donc **BASIC.SYSTEM ne peut plus le lancer** — il place ses
    tampons de fichier juste sous `$9600` et refuse, avec un
    `NO BUFFERS AVAILABLE` suivi d'un `BREAK`. D'où `SCOSWAMP.SYSTEM`
    (`SRC/loader.c`), un fichier ProDOS SYS chargé en `$2000` par ProDOS
    lui-même, qui lit le jeu en `$4000` et lui saute dedans. BASIC.SYSTEM et
    STARTUP.BAS ne sont plus sur le disque : ProDOS exécute le premier fichier
    `.SYSTEM` du répertoire, et `B` vient avant `S`.

  **Piège du fichier de lien**, à connaître avant de retoucher `__HIMEM__` :
  `apple2enh.cfg` calcule la taille du BSS par
  `__HIMEM__ - __STACKSIZE__ - __ONCE_RUN__`. Quand le code déborde, cette
  soustraction passe en négatif et déborde en entier non signé : **ld65 ne
  signale rien et le binaire écrase la RAM d'à côté**. Un lien qui réussit ne
  prouve donc pas que le programme tient — vérifier l'adresse de fin du BSS
  dans le `.map`.

- 🟠 **2. Les ~46 Ko de RAM auxiliaire** — *2-3 j.* Le vrai gisement, et
  l'endroit naturel pour les données de combat (stats de monstres, tables de
  résolution, sprites) : ce sont des données en **lecture seule**, donc le
  cas d'usage exact de l'AUX. cc65 n'en sait rien et n'a pas besoin d'en savoir :
  un petit mover suffit, soit l'appel firmware `AUXMOVE` (`$C311`), soit un
  basculement `RAMRD`/`RAMWRT` autour d'une copie. Attention à ne pas marcher
  sur `$400-$7FF` (page texte 80 colonnes).

- ✅ **3. `$1000-$1FFF`** — **fait le 2026-09-03** : segment `LOWBSS` dans
  `SRC/scoswamp.cfg`, les gros tampons y vont par `#pragma bss-name`. Le tas
  reste derrière la BSS principale (c'est ce qui rend la chose sûre, voir
  DOCS/MEMOIRE.md). Le même jour : famille printf remplacée par `cfmt`
  (876 o), `-Cl` (547 o), `classify_line` et la barre de titre resserrées
  (~1 100 o). **Marge : 184 → 7 544 octets.**

- ✅ **4. La Language Card** — le segment `LC` (`$D400-$DFFF`, 3 Ko) est
  plein depuis le mode carte. Il n'y a rien d'autre à y prendre sous ProDOS 8 :
  la banque 1 est le noyau, `$D000-$D3FF` de la banque 2 son code de sortie.

**Pour les marges actuelles, utiliser le tableau mesuré ci-dessus.**

---

## Corrigé le 2026-08-29 — gardé ici pour le *pourquoi*

Quatre bugs, tous vérifiés dans l'émulateur (pas seulement au lien) :

- **Le tas faisait 270 octets.** BSS finissait à `$8CF1`, la pile commençait à
  `$8E00`. Un `fopen` ProDOS réclame un tampon de 1 Ko aligné page, soit
  ~1 280 octets contigus : **aucun `fopen` ne pouvait aboutir**. Le symptôme
  était `errno=2` avec `ProDOS=$00` — trompeur, parce qu'en cc65 `errno=2`
  vaut **`ENOMEM`, pas `ENOENT`** (`errno.h` : `ENOENT` = 1). Et `_oserror = 0`
  disait déjà que ProDOS n'avait jamais été appelé : l'échec venait de
  `iobuf_alloc` (= `posix_memalign`) dans `libsrc/apple2/open.s`, avant la
  moindre requête MLI. Correctif : lier `apple2enh-iobuf-0800.o`, qui prend les
  tampons entre `$0800` et `__MAIN_START__` au lieu du tas — et raccourcit le
  binaire de ~1 230 octets au passage.
  → `SCOSWAMP/SRC/Makefile`, `build.sh`

- **`PLX` écrasait le flag N.** `hgr_loader.s`, `get_byte` finissait par
  `plx / sec / rts` : `PLX` positionne N et Z **d'après X**, pas d'après
  l'octet lu, qui est dans A. Le `bmi repeat_token` de l'appelant testait donc
  le signe de X. Résultat : **tout token RLE répété était décodé comme un token
  littéral**, le décodage partait en vrille et s'arrêtait sur l'EOF. C'était le
  bug bloquant des images. Correctif : `pha / pla` avant le `sec` pour
  recharger N/Z depuis A (`PLA` ne touche pas C).
  → `SCOSWAMP/SRC/hgr_loader.s`

- **`PLA` écrasait le flag Z.** Même fichier, `repeat_loop` faisait
  `pha / jsr advance_dst / pla` : le `PLA` détruisait le Z que `advance_dst`
  venait de poser pour signaler la fin de la page HGR. Latent sur le corpus
  actuel — aucune image ne finit par une répétition d'octet non nul — mais il
  aurait mordu au premier ré-encodage. L'octet répété passe maintenant par une
  case RAM (`rep_byte`) au lieu de la pile.

- **80STORE coupé et jamais restauré.** Le loader faisait
  `sta $C000/$C002/$C004` avant de décoder et ne remettait rien. Après une
  image, `cprintf` n'écrivait plus qu'en banque principale : une colonne sur
  deux perdue. Le loader mémorise maintenant `RD80STORE` (`$C018`) et le
  rétablit sur les deux chemins de sortie.

- **La sauvegarde d'écran ne gardait que la moitié de l'écran.**
  `memory_swap.c` copiait 1 Ko de `$400-$7FF`, mais en 80 colonnes l'écran est
  **à cheval sur deux banques** : colonnes impaires en RAM principale, paires
  en auxiliaire. La moitié auxiliaire n'était jamais sauvée — et c'est
  exactement ce que donnait le flash « 40 colonnes buggé » au retour de HGR.
  Deux tampons maintenant, atteints en basculant `PAGE2` sous 80STORE. De plus
  `switch_to_text()` faisait `TXTSET` **avant** `restore_text_screen()`,
  exposant une frame à moitié écrite : l'ordre est inversé, on repeint avant de
  rendre visible.
  → `SCOSWAMP/SRC/memory_swap.c`

- **L'image disque était périmée, et le bug déjà corrigé rejouait.** Le
  correctif iobuf ci-dessus était bien lié dans `SCOSWAMP.BIN` (13 334 o,
  14h34), mais `dist/SCOSWAMP.HDV` datait de 14h08 et portait l'entrée
  `SCOSWAMP` d'avant (14 371 o) : le jeu réaffichait un `errno=2 ProDOS=$00`
  qui n'existait plus dans le source. Une session de diagnostic pour une image
  pas reconstruite — le risque exact que l'entrée « un `make hdv` » du backlog
  annonçait, donc elle est faite. `make hdv` relie le binaire puis reconstruit
  le volume ; le boot loader ProDOS (1 Ko, les deux premiers blocs) est
  désormais versionné en `SCOSWAMP.MORE/TOOLS/prodos_boot.tmpl` pour que la
  cible parte d'un arbre propre, `dist/` étant ignoré par git. Le volume est
  monté depuis `SCOSWAMP/` moins `DOCS` et `SRC` : un nouvel asset n'a rien à
  déclarer.
  → `SCOSWAMP/SRC/Makefile`, `SCOSWAMP.MORE/TOOLS/prodos_boot.tmpl`

- **Mise en page fixe des pages de scène.** Le moteur affichait le fichier tel
  quel, ligne à ligne, en laissant la ligne `T <id> <titre>` s'imprimer avec
  son préfixe et en collant les choix à la suite du texte — donc à une hauteur
  qui dépendait de la longueur de la scène. Le mode mixte, qui ne montre que
  les 4 dernières lignes, n'avait donc aucune chance d'y trouver les choix.
  L'écran a maintenant trois zones fixes : **ligne 1** barre en vidéo inverse
  (titre + rappel des touches), **lignes 2-20** le texte, **lignes 21-24** les
  choix — deux par ligne quand ils tiennent dans une demi-largeur, ce qui fait
  entrer les 5 choix des 6 plus grosses scènes dans 4 lignes. Les 804 pages
  ont été repliées à 78 colonnes pour tenir dans les 19 lignes de corps (pire
  cas mesuré : 18), sans qu'un seul mot change.
  → `SCOSWAMP/SRC/scoswamp.c`, `SCOSWAMP.MORE/TOOLS/reflow_txt.py`

- **Deux pièges attrapés en câblant le moteur de combat**, tous deux invisibles
  au lien et à la compilation :

  1. **cc65 rend les structures par valeur de travers.** `combat_round()`
     rendait un `Round` ; à l'écran, un assaut à Forces d'Attaque **égales**
     blessait au lieu de faire esquiver. Le banc d'essai sur machine hôte ne
     pouvait pas l'attraper — il compile avec un vrai compilateur C. Le
     résultat passe désormais par un pointeur. À retenir pour tout le code de
     ce dépôt : sur cc65, on remplit une structure, on ne la rend pas.
  2. **Le verrou clavier arme au sortir du boot.** `dice_seed_from_keypress()`
     attendait une touche en comptant, pour semer les dés. Mais ProDOS laisse
     souvent une touche dans `$C000` avec son strobe armé : la fonction rendait
     la main aussitôt, avec un compte de zéro — **la même semence, donc le même
     personnage et la même partie à chaque lancement**. Elle vide le verrou
     avant d'attendre.
  → `SCOSWAMP/SRC/rules.c`, `SCOSWAMP/SRC/dice.c`

- **L'ecran de bataille, et le piege 80STORE qu'il a revele.** Un combat bascule
  desormais tout seul en mode mixte : l'illustration des deux adversaires
  occupe les 20 lignes du haut, l'echange d'assauts les 4 du bas, avec un
  bandeau qui porte les caracteristiques des DEUX combattants — la barre de
  titre, qui portait la Feuille d'Aventure, disparait sous l'image.
  Au premier essai, ces 4 lignes affichaient **deux textes entrelaces**, une
  colonne sur deux chacun : `enter_graphics()` coupe 80STORE, or le mixte est
  le seul mode graphique ou l'on **ecrit** du texte, et le firmware 80 colonnes
  atteint la banque auxiliaire par 80STORE + PAGE2. `switch_to_mixed()` le
  remet. L'image ne bouge pas pour autant : sous 80STORE l'ecran hi-res reste
  force sur la page 1 en banque principale.
  → `SCOSWAMP/SRC/memory_swap.c`, `SCOSWAMP/SRC/scoswamp.c`

- **Les messages de l'interface sont partis sur le disque.** 39 paires FR/EN
  en dur, 2 409 octets de litteraux, dans un binaire qui n'avait plus 21 octets
  de libre. Elles vivent maintenant dans `/SCOSWAMP/MSGFR` et `MSGEN`, et le
  jeu ne charge qu'une langue : **627 octets liberes**, et l'interface se
  traduit sans recompiler.
  `TOOLS/build_messages.py` est la source unique : il ecrit d'un meme geste
  l'enumeration C et les deux fichiers. Les editer separement decalerait tout
  le catalogue et le jeu afficherait les messages les uns pour les autres —
  d'ou le controle du nombre de lignes au chargement, qui refuse un catalogue
  incomplet en bloc plutot que de le decaler.
  → `SCOSWAMP/SRC/messages.c`, `TOOLS/build_messages.py`

- **Les Pierres Magiques se prennent au choix, depuis le texte.** Le livre ne
  les donne pas, il les fait choisir : « choisissez 6 Pierres de Magie, mais
  vous ne devrez prendre que des Pierres Malefiques ou Neutres » (Stratagus),
  six parmi les Benefiques et Neutres chez Gayolard, une Benefique chez le
  Maitre des Jardins. La ligne `PC <n> <cats>` dit cela, et l'ecran de choix
  n'offre que les categories permises — un bon sorcier ne donne pas de Pierre
  malefique. On peut prendre plusieurs fois la meme, comme le livre l'autorise.
  Les 4 pages concernees sont converties ; `reflow_txt.py --derive` **signale**
  toute page qui semble remettre une Pierre sans ligne `PC` ni `P`, parce que
  la formulation varie trop pour deviner sans risque.

- **Le verrou clavier etait lu deux fois.** `dice_seed_from_keypress` lisait
  `$C000` directement pour mesurer le temps d'attente du premier appui. Mais le
  firmware 80 colonnes du //e tient sa propre file d'entree : lire le verrou
  materiel dans son dos lui laissait la touche, et le `cgetc` suivant la rendait
  une seconde fois. Au demarrage, le `F` du choix de langue etait relu par
  l'ecran d'apres, qui passait tout seul — et l'ecran de choix des Pierres en
  prenait une sans qu'on ait appuye. La fonction passe maintenant par
  `kbhit()` / `cgetc()`.
  → `SCOSWAMP/SRC/dice.c`

- **Des bruitages sur le haut-parleur interne.** Cinq ponctuations pendant le
  combat : la lame qui touche, le coup encaisse, la double esquive, la chute
  d'une creature, la mort du heros. Tout est en assembleur (`sfx.s`) — une
  boucle C sur cc65 met plusieurs dizaines de cycles par tour, ce qui
  plafonnerait les sons dans les graves et lierait leur hauteur a l'humeur de
  l'optimiseur.
  La duree se paie : chaque palier d'un balayage coute `period * 5 * 12`
  cycles, et une chute de 60 a 200 mettait **plus d'une seconde** — une
  eternite quand la page aligne trois BRIGANDS. La plage a ete resserree.
  Le parametre qui compte est le nombre de demi-ondes par palier d'un
  balayage : peu de demi-ondes donnent un transitoire, que l'oreille entend
  comme un choc, beaucoup font chanter le balayage. C'est ce qui separe le
  coup d'epee de la chute d'un corps. Une note pure, elle, sonne comme un bip
  de terminal — c'etait le premier jet.
  Ces routines ne connaissent que `$C030`, present sur toutes les machines.
  **Le Mockingboard viendra plus tard** : il demandera une autre couche, pas
  une retouche de celle-ci.
  → `SCOSWAMP/SRC/sfx.s`

- **Le de se lance tout seul, et la victoire enchaine.** Deux mecaniques que
  le livre confiait au joueur, rendues au moteur par deux directives concues
  et implantees par un chantier d'agents (arpentage corpus + moteur,
  conception, implantation) :

  - **`ED <CARAC> <+-ndes>`** -- le jet de des visible. `ED ENDURANCE -1` :
    « lancez un de et perdez autant de points d'ENDURANCE ». Meme cadre que le
    jet de Chance : invite, une frappe, le resultat affiche, la Feuille
    d'Aventure mise a jour. `ED OR +1` couvre le seul jet de gain du corpus
    (les Pieces d'Or du brigand, page 135). Le de d'une ligne ED tombe AVANT
    le combat de la meme page : la Malediction de la 261 peut tuer d'abord.
  - **`MV <id>`** -- l'enchainement de victoire, jumeau de `V` : le dernier
    adversaire tombe, la page cible se charge, plus d'ecran de choix ou le
    joueur declarait lui-meme « si vous avez vaincu ». 28 pages converties,
    leurs choix de victoire retires.

  L'arpentage a aussi trouve des BUGS du corpus : quatre pages appliquaient
  une perte inconditionnelle la ou la prose la reservait au Malchanceux (058,
  190 -> `CE` posees) ; six pages annoncaient un gain qu'aucune ligne E ne
  donnait (020, 021, 067, 076, 077, 289 -> posees) ; la 028 offrait un choix
  « en cas de mort » que le moteur tient lui-meme ; et la 044 (sangsues)
  jetait une forme unique -- le plus petit de deux des, double = la somme --
  ramenee a un de simple, texte reecrit dans les deux langues.

  **Les six dernieres pages, exprimees a leur tour** (chantier suivant, le
  rapport `--derive` est VIDE) :

  - **`CS <STAT> <ok> <ko>`** -- « Lancez deux des » contre la caracteristique
    nommee, gratuit (le jet de Chance, lui, coute son point). Meme cadre
    visible que ED : « Vous jetez : 8, contre 22. » Pages 091, 257, 377.
  - **`MB <ok> <ko>`** -- duel au premier sang : la premiere blessure arrete
    le combat et la suite dit QUI a touche (079). Reutilise la sortie de MV.
  - **`DV <max> <id>`** -- cascade sur l'ENDURANCE perdue au dernier combat
    gagne : la 156 ne demande plus au joueur d'evaluer ses blessures, le
    moteur fabrique l'unique choix « continuer » vers la bonne branche.
  - La 341 n'avait besoin de RIEN de neuf : `MS 6` + `MV 372` + `CF 327`.
  - La 373 non plus : la solution du livre lui-meme -- une **page jumelle**,
    la 402, ou Stratagus entre en scene deja blesse (`M 9 8` au lieu de
    `M 9 10`), et `CL 402 225`. Les effets qu'une branche de CS doit porter
    vivent pareillement dans des **pages relais** : 403 (le bond parfait,
    `E CHANCE +2`), 404/405 (la reception ou la chute du saut de la 091),
    406 (les dards, `E ENDURANCE -3`). Cinq pages nouvelles, du pur contenu.

  Paye par un regime : les quatre fabriques de choix fondues en
  `push_choice` (~480 octets), le rappel des touches au catalogue, et la
  pile C ramenee de 2 Ko a 1,5 Ko (chaine la plus profonde : load_scene ->
  run_* -> cprintf -> vsnprintf ; tampons fichiers statiques ; recursion de
  load_scene interdite par la boucle principale). `check-memory.sh` prend
  `--stack` -- son defaut ECRASAIT l'option, lecon : un defaut se pose avant
  la lecture des options, pas apres. Marge : **194 octets**.

  Et une trouvaille de l'arpenteur moteur : la variable PAYLOAD de `make hdv`
  nommait `MSGFR`/`MSGEN` au lieu de `MSGFR.TXT`/`MSGEN.TXT` -- le
  `2>/dev/null` avalait la faute, la dependance aux catalogues ne mordait
  pas. Corrigee, HELPFR/HELPEN ajoutes.

  Marge apres le lot : **107 octets**. Les chantiers suivants (objets/
  drapeaux, sauvegarde, `CS`) exigent d'abord la recuperation d'octets --
  l'overlay des ecrans de lancement est la piste chiffree (~1 Ko).
  → `SCOSWAMP/SRC/scoswamp.c`, `SCOSWAMP/SRC/rules.c`,
    `SCOSWAMP.MORE/TOOLS/reflow_txt.py`

- **Les sept dernieres pages que le derivateur n'osait pas trancher.** Elles
  restaient signalees depuis que le corpus est derive du texte ; elles sont
  toutes reglees, et le rapport de `reflow_txt.py --derive` est vide.

  Deux etaient de FAUX positifs : la 191 rappelle les Pierres « que Gayolard
  vous a confiees » et la 282 en LANCE une -- dans les deux cas la Pierre ne
  vient pas au heros. Le detecteur les distingue maintenant.

  Une etait une perte seche que le mot « supplementaire » faisait passer pour
  conditionnelle (269) : il dit que la perte s'ajoute a une autre, pas qu'elle
  depend de quoi que ce soit. Une autre l'etait aussi, derriere un « si vous
  etes toujours vivant » (357) qui est du recit -- le moteur arrete deja la
  partie a zero.

  Les quatre dernieres demandaient au moteur deux choses qu'il ne savait pas
  dire, et qui sont maintenant deux directives :

  - **`CE <CARAC> <dok> <dko>`** -- « Tentez votre Chance » qui ne branche pas.
    « Si vous etes Malchanceux, vous tombez et perdez 2 points d'ENDURANCE,
    mais vous parvenez tout de meme a grimper » (73, 249) : le jet decide d'un
    effet, les deux issues menent au meme endroit, et la page continue de se
    lire. La ligne `CL` ne pouvait pas l'exprimer -- elle branche, donc elle
    aurait saute le paragraphe suivant, celui de la Chaine d'Or.
  - **`E0 <CARAC> <delta>`** -- la perte qui entame le TOTAL DE DEPART.
    « vous perdez 2 points d'HABILETE et devez reduire aussi de 2 points votre
    total initial [...] Vous ne pourrez plus jamais retrouver tous vos points
    de depart » (87). Une ligne `E` ordinaire se serait rattrapee a la
    premiere potion. Plancher a 1 : une caracteristique nulle serait une mort
    que le livre ne prononce pas.

  Verifie dans POM2 en posant les deux lignes sur la page 1 le temps d'un
  essai : HABILETE 11/11 -> 9/9 (le plafond bouge), ENDURANCE 17/17 -> 16/17
  et CHANCE 9/9 -> 8/9 (le jet a coute son point et paye la branche heureuse).
  Cout memoire : 986 octets, il reste 1047.
  → `SCOSWAMP/SRC/rules.c` (`character_lower_hab0`), `SCOSWAMP/SRC/scoswamp.c`

- **`make hdv` ignorait les donnees.** L'image disque ne dependait que du
  binaire : une page de texte corrigee ou une image reconvertie repondait
  « Nothing to be done », et on testait un disque perime. C'est exactement le
  piege qui a coute une seance de debogage sur un bug deja corrige. Le
  corpus, les images et les catalogues de messages sont maintenant des
  prerequis de la regle.
  → `SCOSWAMP/SRC/Makefile`

- **525 coquilles corrigees dans le corpus francais, en deux passes.** Le corpus est
  volontairement sans accents -- l'Apple II n'en affiche pas -- mais la
  conversion qui les a retires s'est mal passee. Deux familles de degats :
  un circonflexe rendu par deux lettres (`maitre` -> `maeitre`, `aussitot` ->
  `aussiteot`, `ou` -> `oeu`, `git` -> `geit`) et une lettre avalee avec
  l'accent (`geant` -> `gant`, `creature` -> `crature`, `eau` -> `au`,
  `beaucoup` -> `baucoup`, `epees` -> `epes`).

  La liste vient d'une comparaison avec le vocabulaire du **livre**, ou les
  accents sont intacts : un mot du corpus absent du livre est un suspect, et
  le mot du livre le plus proche donne la correction. Chaque entree a ete
  verifiee en contexte, ce qui a evite deux pieges : `vent` est bien le vent
  et non `vient`, et `gant` designe toujours le Geant, jamais un gant.
  → `SCOSWAMP.MORE/TOOLS/fix_typos.py`

  Cote anglais, le dictionnaire systeme ne laisse que 50 suspects, tous des
  noms propres ou des mots qu'il ne connait pas (`backpack`, `trapdoor`). Rien
  a corriger -- `Croupie` est le nom de la riviere.

  **Seconde passe (262 corrections de plus).** La methode du vocabulaire etait
  arrivee au bout de ce qu'elle pouvait voir : le portage ecrit sa propre
  prose, 1080 de ses mots sont absents du livre, et un suspect ne prouve plus
  rien. On cherche donc les FORMES du degat, qui elles sont des signatures :

  - **128 apostrophes elidees perdues** -- `d ENDURANCE`, `l ouest`,
    `s ecroule`, `jusqu au nid`. Aucune de ces lettres n'est un mot francais
    isole et l'elision ne se fait que devant une voyelle : la regle ne peut
    pas se tromper sur `a` ni sur `y`, les deux vrais mots d'une lettre. Les
    `n` de « Clairiere n 5 » sont des `n°` et restent.
  - **29 guillemets** -- le scan a rendu `«` par `e` et `»` par `u` :
    « e Venez donc, venez u, dit-il ». Ils deviennent des guillemets droits,
    seuls affichables sur Apple II.
  - **les formes `aei`, `eo`, `eu`, `-au`** -- `traeitre`, `veotre`,
    `breulure`, `coeutent`, `ridaux`, `tablau`.

  Deux effets de bord immediats : la page 311 derivait sa perte d'HABILETE en
  anglais et pas en francais, parce que le francais disait `coeutent` ; et la
  395 la manquait des deux cotes en francais parce qu'elle la disait a la voix
  causative (« vous font perdre »), reecrite en « vous perdez ». Le recoupement
  FR/EN ne signale plus aucune divergence.

  Et un invariant de plus dans `reflow_txt.py` : **aucun octet hors ASCII**.
  Deux accents avaient survecu (`à` page 401, `è` dans « Tancrède » page 395) ;
  sur Apple II ils sortent en glyphe faux.

- **Les personnages changeaient de tete d'une image a l'autre.** Chaque image
  etait generee seule, a partir de sa seule page : rien ne reliait le Maitre
  des Loups d'une illustration a la suivante, ni la creature d'une scene a
  celle de son image de bataille, et le heros n'etait decrit que dans les
  prompts de bataille.

  On n'obtient pas la constance en demandant « le meme personnage ». Quatre
  pieces la donnent, dans cet ordre :

  1. **Les bibles** -- `characters.json` (11), `monsters.json` (20),
     `decors.json` (10), `objects.json` (4). Une fiche par sujet, ecrite une
     fois, injectee mot pour mot dans tout prompt dont la page cite un de ses
     alias. Chaque fiche porte son `look`, sa `source` (le livre quand il
     decrit, l'illustration sinon), et son `scale` -- toujours relatif au
     heros, parce qu'un modele ne sait pas de lui-meme qu'un Maitre des Loups
     depasse un homme d'une tete.
  2. **Les planches de reference** -- `build_manifest.py --refs` produit un
     prompt par fiche vers `SCOSWAMP.MORE/REF/<ID>.png` : le sujet seul, plein
     pied sur fond noir pour une figure, une vue large et vide pour un decor.
     C'est le canon. Il se genere **avant** tout le reste.
  3. **L'attachement** -- `generate_images.sh` joint les planches au prompt
     avec `codex exec -i`. Le texte decrit, la planche montre : c'est la
     difference entre « un maitre des loups » et *ce* maitre des loups. Quatre
     planches au plus par image (heros, puis figures nommees, puis decor) :
     au-dela le modele moyenne au lieu de copier.
  4. **L'empreinte** -- chaque ligne de manifeste porte le sha1 des fiches qui
     l'ont formee. `--record` la classe apres une generation, `--stale` nomme
     ensuite exactement les images qu'une fiche modifiee a rendues fausses.
     Sans ca on regenere 433 images ou on en oublie trois.

  Le style commun (palette, cadrage, trait) est factorise dans `COMMON_STYLE`,
  partage par les prompts de scene, de bataille et de reference : il ne peut
  plus deriver entre eux.

  La chaine complete :

  ```
  build_manifest.py --refs    ->  REF/<ID>.png          (45 planches, d'abord)
  build_manifest.py --all     ->  scene_manifest.jsonl  (402 pages)
  build_manifest.py --battle  ->  battle_manifest.jsonl (31 batailles)
  generate_images.sh <manifeste>  ->  GENERATED/*.png
  build_manifest.py --record  ->  GENERATED/bible.stamp.json
  TOOLS/convert_images.sh     ->  SCOSWAMP/IMG/<bucket>/*.RLE.BIN
  ```

  `generate_images.sh` saute une image deja presente : il est relancable, et
  une generation interrompue reprend ou elle s'etait arretee.

  **Ne pas reformuler une fiche sans lancer `--stale`** : c'est la constance du
  texte et de la planche qui fait celle de l'image.

  **Deux pieges appris sur les planches elles-memes**, tous deux invisibles a
  la lecture du prompt :

  - Le cadrage disait « no props beyond what the description names » -- une
    interdiction, sans l'exigence complementaire. Le modele lisait la liste
    des vetements et n'en dessinait aucun : la planche du Maitre des Loups le
    montrait torse nu et desarme alors que sa fiche lui donnait tunique,
    amulette et epee. La consigne exige maintenant que **chaque** vetement,
    arme et ornement nomme soit visible, et rien de plus.
  - Le decor « bassin » et la BETE DU BASSIN portaient le meme identifiant,
    donc la meme planche : chacune effacait celle de l'autre. Deux fiches de
    meme nom sont desormais une erreur de chargement.

  Et une regle de fond, apprise en verifiant les fiches contre les pages : le
  **corpus prime sur la fiche**. La fiche du Maitre des Loups le disait sans
  epee la ou la page 398 lui en donne une ; celle de Gayolard en faisait un
  vieillard barbu en robe bleue la ou la page 371 decrit un petit homme replet
  en tunique blanche, au tour de potier. `--describe` met chaque fiche en
  regard des phrases qui decrivent son sujet : a relire avant d'en modifier
  une.

  Reste a faire : la regeneration elle-meme (433 images), et un detail de
  palette -- les fiches disent « grey wolf pelts », or le gris n'existe pas en
  HGR, il ressort bleu ; les fiches gagneraient a ne nommer que les six
  couleurs disponibles.
  → `SCOSWAMP.MORE/{characters,monsters,decors,objects}.json`,
    `TOOLS/build_manifest.py`, `TOOLS/generate_images.sh`

- **Les Pierres se depensaient sans jamais toucher au sac.** 43 choix du corpus
  disent « Utiliser une Pierre de Feu » : ils partaient en `C` ordinaire, donc
  rien ne verifiait qu'on possedait la Pierre et rien ne la consommait. D'ou
  les deux symptomes signales — l'inventaire qui ne suit pas, et le droit de
  lancer un sort qu'on n'a pas. La ligne `CU <PIERRE> <id> <titre>` exige la
  Pierre et la consomme ; un choix dont la Pierre manque **s'affiche sans
  lettre** — on le voit, le livre l'ecrit, mais on ne peut pas le prendre.

- **Cinq rencontres ne se lancaient pas du tout**, dont le Maitre des Loups et
  ses deux betes (`N120`). Ces pages posent leurs adversaires en TABLEAU —
  `HABILETE ENDURANCE Premier Loup 7 5 Deuxieme Loup 6 6 Maitre des Loups
  11 10` — que le motif en phrase ne voyait pas. **Les pages ont ete
  corrigees**, pas l'outil : le corpus a maintenant une seule facon d'ecrire un
  bloc de stats, `<NOM> HABILETE: h ENDURANCE: e`, avec les noms en capitales.
  Une deuxieme grammaire dans l'analyseur aurait ete une dette permanente pour
  cinq pages. `N281` en profite pour perdre sa coquille : `ORQUEDES MARAIS`.

- **Le recoupement FR/EN etait aveugle a la moitie des directives** : il ne
  retenait que `M`, `MD`, `MS` et `CF` a l'entree, si bien que l'extension aux
  `CU` et `CL` ne servait a rien. Il enregistre tout desormais, et c'est ce qui
  a fait sortir trois pages ou l'anglais depensait une Pierre que le francais
  gardait — le corpus francais ecrivant `Pierre d Amitie`, avec une espace au
  lieu de l'apostrophe.

- **La barre parlait francais en partie anglaise.** Les caracteristiques
  s'affichent maintenant `SKL / STA / LCK`, les trois mots de Fighting Fantasy,
  et le rappel devient `I:BAG H:HELP`.

- **A la mort, on choisit** : recommencer une aventure, ou rendre la main a
  ProDOS. Avec ProDOS 2.4 c'est Bitsy Bye qui reprend, et l'on peut lancer
  autre chose sans redemarrer la machine.

- **Le choix des Pierres ne se repeint plus a chaque prise.** La liste des
  Pierres permises ne bouge pas ; seul le compteur change. Six Pierres, c'etait
  neuf lignes redessinees neuf fois.

- ✅ **Le mode carte est revenu, en texte** (2026-09-04, branche
  `feat/scoswamp-map`, `DOCS/rapport-map.md`). Touche `M`, bascule comme `[I]`
  et `[H]`, refusée sans l'Anneau de Cuivre. Grille 6 × 9 en texte 80
  colonnes : **aucune primitive de tracé**, c'était elles qui coûtaient les
  5 019 octets. Les données sont sur le disque (`MAP`, 1 844 octets, écrit par
  `TOOLS/build_map.py` depuis `carte.json`) et résident dans le kilo-octet de
  `$0C00-$0FFF` que le second tampon ProDOS n'a jamais réclamé — donc **zéro
  octet de la fenêtre principale**. Le brouillard de guerre sort du seul
  bitmap `visited`, déjà sauvegardé ; il n'y a **pas** de table des sentiers,
  le voisin étant la première case occupée dans la direction annoncée. Une
  ligne de lieu s'installe sous la barre de titre. Il manque le curseur de
  consultation et le fil Pompatarte.
  Coût payé par : `--codesize 100` (1 310 o), la cure `int` → `unsigned char`,
  `classify_line` en table de directives, `oops()`, et six déménagements de
  tampons. **Marge finale : 249 octets** apres la fusion du prologue et du combat rythme.

- **Le mode carte a ete retire.** Il avait ete construit (fichier `MAP` genere
  depuis les directions de la prose, cercles numerotes, sentiers, rayons pour
  les chemins connus mais pas empruntes) et il fonctionnait. Il coutait
  **5 019 octets** — les primitives de trace HGR, l'ecran, le bitmap des
  clairieres visitees et quatre messages — dans une fenetre programme qui n'en
  a que 32 Ko. Retire, il reste **4 981 octets libres**.
  Ce qu'il faudrait pour le reprendre : la place (RAM auxiliaire ou Language
  Card), et les numeros de clairiere du livre — la carte affichait le numero
  du PARAGRAPHE, alors que le livre demande de porter celui de la CLAIRIERE,
  et 29 des 90 seulement le donnent en clair dans la prose.
  `SCOSWAMP.MORE/TOOLS/build_map.py` derivait la carte de la prose ; il a ete
  supprime avec le reste.

- **Le sac à dos demandait deux appuis.** `wait_key_at()` affiche une invite
  *et* consomme une touche ; l'appeler avant un `cgetc()` explicite en mangeait
  une pour rien. L'affichage est maintenant séparé de l'attente (`print_at`).
  → `SCOSWAMP/SRC/scoswamp.c`

---


## La suite du moteur — feuille de route (2026-08-30)

Le //c est conquis (POM2 `6d65741` : le BIT $CFFF manquant du stub — voir le
TODO de pom2). SCOSWAMP boote et se joue sur //e ET //c. La marge est de
2 099 octets grace a la Language Card (1,3 Ko de code froid en $D400, ~1,7 Ko
encore libres dans le banc). Dans l'ordre de valeur :

1. **Objets et drapeaux** — le chantier n° 1 de jouabilite : plus de
   comptabilite au crayon, plus de triche possible. Le catalogue est DEJA sur
   le disque (`build_objects.py` -> OBJFR/OBJEN : 9 objets visibles, 5
   drapeaux caches, l'ordre fait foi). Reste : le moteur (`G`/`GX` posent et
   effacent un bit ; `CI`/`CN`/`GU` gardent un choix — possede / ne possede
   pas / consomme ; grisage comme les Pierres ; le sac liste les bits
   visibles) puis la pose corpus, releve deja fait : AMULOUP (gain N154,
   portes N344/N092), AMUFLEUR (N251), CAPE (gain N386, usage N286), CHAINE
   (N073), FIOLE (N042), BAIE + .ANTHERIQUE (N389, porte N166), AIMANT
   (maudit N357), patrons .GAYOLARD/.POMPATARTE/.STRATAGUS (portes
   N006/N056/N226, poses sur les pages d'engagement), N128 en `CN`.
   ~600-800 octets, finances.

2. **Sauvegarde + « Reprendre »** — l'etat complet tient sous 200 octets
   (heros, Pierres, objets, or, scene courante, clairieres visitees 51 o,
   memoire des monstres 120 o). Ecriture ProDOS a chaque `load_scene`,
   « Reprendre la partie » sur N000, et la mort offre reprendre / recommencer
   / quitter. ATTENTION : fopen("w")/fwrite cc65 tirent du code de
   bibliotheque encore jamais lie — mesurer avant de promettre.

3. **Pages hors-aventure** (N900+) — la carte du livre en HGR, les regles de
   combat, les credits : du pur contenu, le mecanisme [H] existe deja.

4. **Game feel** — le de qui roule (3-4 valeurs rapides avec clic avant de
   s'arreter, ~40 o), le flash de blessure (inverser le bandeau un instant),
   la directive `S <n>` (jingle d'entree de scene : danger, victoire,
   decouverte) — motifs speaker d'abord, patterns Mockingboard sur disque le
   jour venu.

5. **Images** — ~370 scenes a regenerer avec le heros au fourreau (les ~34
   du run interrompu sont flaggees par `--stale`, la fiche du heros ayant
   change), puis `--record`, `convert_images.sh`, `make hdv`.

6. **Verifications de parc** — //c+ (IWM, 4 MHz) et les profils PAL n'ont
   pas encore vu le jeu ; DV n'est verifie en jeu que sur la branche
   « aucune blessure » (241) — provoquer les branches 193/326.

## Backlog

### Portage / gameplay

- 🟠 **Convertir les 402 pages au nouveau format** — le moteur de combat et
  d'objets existe et tourne (voir plus bas), mais **le corpus ne s'en sert
  presque pas** : deux pages converties sur 402. C'est désormais le seul
  travail qui sépare le jeu du livre. Détail chiffré ci-dessous.
- 🟡 **SPACETRIP** — au point 0.1alpha, n'a pas reçu les correctifs mémoire de
  SCOSWAMP. Il utilise `fopen` de la même façon (`SPACETRIP/spacetrip.c:43,95`)
  et a donc **le même tas de 270 octets** : à vérifier en priorité, le bug est
  probablement identique et jamais diagnostiqué.
- 🟢 **`build_paths()` ignore `lang`** — `paths.c:32`, paramètre non utilisé
  (le choix de langue se fait par `chdir` dans `enter_asset_dir`). Soit le
  retirer de la signature, soit s'en servir.

### Outillage

- 🟡 **Câbler `reflow_txt.py` dans un `make check`** —
  `SCOSWAMP.MORE/TOOLS/reflow_txt.py` remet les pages au format du moteur et
  **vérifie les invariants de mise en page** : corps ≤ 19 lignes une fois
  replié à 78 colonnes, choix ≤ 4 lignes, titre ≤ 60 caractères, et pas un mot
  modifié. Il tourne à la main aujourd'hui ; sans lui dans le build, une page
  trop longue ne se verra qu'à l'écran, tronquée.

- 🟢 **Un test de non-régression du décodeur RLE** — les trois bugs 6502
  ci-dessus étaient tous invisibles au lien et n'ont été trouvés qu'en
  exécutant. `TOOLS/test_hgr_rle.c` existe : lui faire décoder tout le corpus
  `IMG/` et comparer à un rendu de référence donnerait le test qui **échoue**
  quand un flag est mal restauré.

### Le personnage et le combat : ce qui existe, ce qui reste

**Le moteur est là.** `SCOSWAMP/SRC/rules.c` porte les règles de *Défis
Fantastiques* telles que les pages liminaires du livre les énoncent, chaque
règle non évidente accompagnée de la phrase qui la fonde. Il ne connaît ni
l'écran ni ProDOS, ce qui permet de le passer au banc sur machine hôte :
`SCOSWAMP.MORE/TOOLS/test_rules.c`, cible ctest `rules`.

Ce qu'il couvre : création du personnage (1d6+6 / 2d6+12 / 1d6+6), le plafond
« jamais au-dessus du total de départ », Tentez votre Chance et son point de
CHANCE consommé, l'assaut (2d6 + HABILETÉ de chaque côté, égalité = esquive),
les blessures avec leurs quatre modificateurs de Chance, la Fuite et sa
blessure automatique, la mémoire des clairières (une créature laissée blessée
garde son ENDURANCE — le Marais est le seul livre où l'on revient sur ses pas),
les douze Pierres Magiques avec leurs trois catégories, leur consommation à
l'usage, la restitution de la moitié du total de départ pour les trois pierres
de caractéristique, le dé de la Malédiction, et l'interdiction de s'en servir
une fois le premier coup donné.

`SCOSWAMP/SRC/dice.c` fournit le hasard : un congruentiel dont on ne garde que
les bits de poids fort (un modulo 6 sur les bits bas d'un LCG donnerait des dés
biaisés), semé par le temps d'attente du premier appui de touche.

**Le format de page sait déjà dire :**

| Ligne | Effet |
| --- | --- |
| `M <hab> <end> <nom>` | la créature de la clairière |
| `MD <n>` | ses coups coûtent n ENDURANCE (défaut 2) |
| `MS <n>` | le combat cesse à n ENDURANCE (défaut 0) |
| `E <CARAC> <delta>` | effet appliqué en entrant |
| `P <PIERRE> <n>` | Pierres reçues en entrant |
| `CF <id> <titre>` | la Fuite, quand la page l'autorise |
| `CP <PIERRE> <id> <titre>` | choix qui remet une Pierre |

Et côté images : `IMG/<bucket>/B<id>.RLE` est l'illustration de bataille d'une
clairière, préférée à `N<id>.RLE` pendant le combat.

Le paragraphe 12 (le GÉANT) est converti dans les deux langues et sert de cas
d'école : il exerce `M`, `MD 4` (« vous perdez 4 points d'ENDURANCE au lieu de
2 »), `MS 6` (« si vous parvenez à réduire à 6 les points d'ENDURANCE du
Géant ») et `CF`. Le paragraphe 283 exerce `CP` : le Maître des Jardins donne
une Pierre bénéfique au choix.

**Ce qui reste.**

- ✅ **`CL` : Tentez votre Chance.** 15 scènes dérivées, dans les deux langues.
  Le livre ne *propose* pas ces deux issues, il ordonne le jet et annonce ce
  qui arrive dans chaque cas ; les laisser en choix libres revenait à demander
  au joueur de tirer les dés lui-même, et de tricher. Le moteur joue le jet une
  fois la page lue, montre le résultat (« Vous jetez les deux dés : 7, contre
  une CHANCE de 8 »), consomme le point de CHANCE et saute.
  La ligne porte un effet d'ENDURANCE optionnel **par branche**, parce que le
  livre en pose deux : « si vous êtes Chanceux, vous perdez 2 points
  d'ENDURANCE et vous vous rendez au 270 ». Ce coût appartient à la
  transition, pas à la page d'arrivée — le 270 est atteint depuis cinq pages,
  une seule fait perdre ces points.

- 🟠 **Les conditions qui restent : 39 choix**, et ce ne sont plus des jets de
  dés mais de la mémoire de partie :

| Ce que la condition demande | Choix |
|---|---|
| Un fait acquis (« Si vous avez déjà trouvé le buisson », « Si vous touchez le Chef ») | 33 |
| La possession d'un objet (« Si vous possédez l'Amulette en forme de Loup ») | 4 |
| Une clairière déjà visitée | 1 |
| Un seuil de caractéristique | 1 |

  Il faut donc un jeu de **drapeaux** — quelques dizaines de bits de partie,
  posés par une directive et lus par une autre — plus un `CI <objet> <id>` pour
  l'inventaire. Le bitmap des clairières visitées existait pour la carte ; il
  est parti avec elle et reviendra ici.

- ✅ **Les combats sont dérivés de la prose.** `reflow_txt.py --derive` lit le
  bloc de stats que les pages écrivent déjà en toutes lettres — `BETE DU
  BASSIN HABILETE: 8 ENDURANCE: 10` — et en fait une ligne `M`, puis retire le
  bloc du texte (le bandeau de combat l'affiche désormais). **24 combats
  dérivés sur 26**, plus les `MD` (« 3 au lieu de 2 »), les `MS`
  (« si vous réduisez à 6 ») et les `CF` (un choix qui parle de Fuite).

  **Pourquoi à la construction et pas dans le moteur** : l'Apple II n'a plus la
  place d'un analyseur de prose, la tolérance aux trois façons dont le corpus
  écrit un bloc de stats y serait fragile, et surtout le résultat serait
  invisible — alors qu'ici il atterrit dans le fichier, lisible dans un diff.
  L'auteur écrit toujours de la prose ; personne ne tape de directive.

  L'outil **recoupe FR et EN** : une divergence de stats entre les deux langues
  est une erreur de contenu, il la signale. Et il refuse de deviner : les 2
  pages à plusieurs adversaires (`N224` deux LOUPS, `N235` trois BRIGANDS)
  gardent leur prose et sortent dans le rapport, en attendant que le moteur
  sache mener un combat contre plusieurs créatures.

- 🟠 **La conversion du corpus**, chiffrée sur `TEXTFR/` :

| À convertir | Scènes |
|---|---|
| Un combat / un adversaire à affronter | 88 |
| ~~Un bloc de stats en clair → `M`~~ | ~~26~~ **26 faits** |
| Choix écrits comme une condition → `CL` / `CS` | 68 |
| Les Pierres Magiques (12 noms) → `P` / `CP` | 53 |
| Une variation chiffrée (« perdez 2 points d'ENDURANCE ») → `E` | 14 |
| Provisions / repas | 8 |
| Pièces d'Or | 7 |

  Le PDF du livre est la source : c'est lui qui donne les exceptions par page
  (dégâts doublés, seuils, fuites autorisées) que le corpus actuel a perdues en
  route ou noyées dans la prose.

- 🟠 **Les images de bataille.** Le moteur cherche `IMG/<bucket>/B<id>.RLE`
  quand la clairière porte un adversaire, et retombe sur l'illustration
  ordinaire `N<id>.RLE` quand elle manque. La chaîne complète :

  ```
  build_manifest.py --battle  ->  SCOSWAMP.MORE/battle_manifest.jsonl   (26 prompts)
  codex exec                  ->  SCOSWAMP.MORE/GENERATED/B<id>.png
  TOOLS/convert_images.sh     ->  SCOSWAMP/IMG/<bucket>/B<id>.RLE.BIN
  SRC/make hdv                ->  dist/SCOSWAMP.HDV
  ```

  Les 26 clairières sont celles dont la page porte un bloc de stats ; le
  manifeste les extrait tout seul, y compris depuis une ligne `M` déjà
  convertie.

  **Deux contraintes de cadrage**, apprises sur le premier essai et écrites
  dans le prompt :
  - le héros doit être **le même sur les 26 images** — capuche et cape vertes,
    cotte de mailles, bouclier rond, sac à dos, épée levée, vu de trois quarts
    dos ;
  - le **quart inférieur** doit rester du sol sombre et vide : la fenêtre de
    texte du mode mixte recouvre le sixième du bas, et au premier essai elle
    coupait les pieds du héros.

  `convert_images.sh` ne reconvertit qu'un PNG plus récent que son RLE : les
  400 illustrations de scène ne sont pas refaites à chaque passage.

- 🟠 **La fenetre programme reste etroite.** Le catalogue de messages a rendu
  627 octets, l'ecran de choix des Pierres en a repris une partie. Les deux
  pistes suivantes sont structurelles :
  1. **La RAM auxiliaire** (point 2 de la carte memoire), ~46 Ko.
  2. **La Language Card** (point 4), 16 Ko.

  Deux choses attendent cette place, toutes deux visibles a l'ecran :
  effacer le fond d'un cercle de la carte avant d'y ecrire son numero (le
  numero est pour l'instant remonte au-dessus du diametre pour eviter les
  sentiers horizontaux), et le combat contre plusieurs creatures.

- 🟡 **La sauvegarde.** Une partie de *Défis Fantastiques* se joue en plusieurs
  fois. `Character` fait une trentaine d'octets, la mémoire des clairières 120 :
  un fichier ProDOS de rien du tout.

- ✅ **Combat contre plusieurs créatures.** « Parfois, vous les affronterez
  comme si elles n'étaient qu'un seul monstre ; parfois, vous les combattrez
  une par une. » Les deux rencontres à plusieurs du Marais sont du second
  type — `N224` (deux LOUPS, « à tour de rôle »), `N235` (trois BRIGANDS, « un
  seul à la fois ») — et une page porte désormais autant de lignes `M` que
  d'adversaires. Le suivant se présente entier dès que le précédent tombe, et
  le héros garde l'ENDURANCE qui lui reste : aucun répit entre deux.
  La mémoire des clairières retient **lequel** de la file était en cours, pas
  seulement son ENDURANCE — sans quoi fuir devant le deuxième LOUP puis
  revenir ferait recommencer au premier. Pinné par `test_rules`.
  Le mode « comme un seul monstre » n'existe pas dans ce livre-ci ; il faudra
  une directive le jour où un autre le demandera.

  Au passage, le motif de dérivation absorbe l'ordinal : le corpus écrit
  « Premier LOUP » et « Deuxieme LOUP », et sans lui les deux portaient le
  même nom dans le bandeau — « Premier » restant orphelin dans la prose.

- 🟢 **Les Provisions et l'or** existent dans `Character` mais aucune page ne
  les touche encore.

- 🟢 **Que faire de `COMBAT/SRC/combat.c`.** Ces 847 lignes ne sont **pas**
  réutilisables : c'est le système de SPACETRIP (HP / ATK / DEF / niveaux / XP,
  monstres de science-fiction), pas celui de *Défis Fantastiques*. Son
  générateur aléatoire est en plus semé sur une constante (`srand(0x1234)`) :
  toutes les parties seraient identiques. À garder pour SPACETRIP, ou à
  supprimer.

- 🟢 **Coquille dans le corpus** : `Fetrissure` apparaît 2 fois pour
  `Fletrissure` 10 — à corriger avant d'en faire une clé d'inventaire.

### Documentation

- 🟢 Consigner dans `DOCS/` les deux pièges cc65/ProDOS payés ici : `errno`
  n'est **pas** numéroté comme en POSIX, et `_oserror == 0` est le signal que
  l'échec est côté runtime C, pas côté ProDOS. C'est ce qui a fait chercher un
  fichier manquant pendant longtemps alors que le problème était le tas.

## Note d'atelier — import d'images vers HGR

- Avec **ii-pix**, `dither off` + `gamma 0.75` donnent en général de
  meilleurs résultats d'importation (constaté sur les planches SCOSWAMP,
  2026-08-30). Les refs sont désormais générées en traits épais non
  pixellisés précisément pour que cette conversion tienne.
  **Câblé dans `scoswamp_hgr convert`** : gamma 0.75 par défaut
  (`--gamma X` pour ajuster, `1.0` = off) ; le convertisseur ne trame
  jamais. Depuis le 2026-08-30 il fait aussi : réduction consciente de la
  palette (vote majoritaire par paire, fini les halos de bord), choix de
  banque par **DP 2D itéré** (pénalités bascule 150 / paire à cheval 300 /
  cohérence verticale 50, balayages alternés jusqu'à convergence), cible
  d'affichage **OpenEmulator** (couleurs du démod FIR de POM2 en régime
  établi ; `--palette feline` pour l'ancien rendu RGB Chat Mauve),
  `--report` (subDE / dissent / score) et `--preview-oe` (aperçu 560px à
  travers le vrai démod FIR). `convert_images.sh` imprime les **10 pires
  conversions** d'un lot pour relecture humaine.
- 🟢 Améliorations restantes du convertisseur, si besoin un jour : votes
  pondérés par recouvrement exact de surface (gain marginal) ; optimisation
  au niveau signal à travers le démodulateur (plafond théorique — gros
  effort, gain quasi nul sur des aplats, n'aurait de sens que pour des
  photos). Le tramage reste exclu par choix de style.

## ✅ Fait le 2026-08-31 — le sac à dos qui bloquait la machine en HGR

Signalé comme « ça bloque parfois en HGR, plus rien n'est possible, on ne
repasse pas au mixte ni au texte ». Ce n'était ni la bascule vidéo ni les
soft-switches : **`show_inventory` était le seul écran modal à ne pas allumer
le texte avant d'écrire dedans.**

Ouvert depuis le mode image, le sac se dessinait derrière l'illustration ; sa
boucle avalait ESPACE, RETURN et toutes les lettres sans que l'écran change,
et seul ESC en sortait — un premier ESC pour fermer le sac, un second pour que
la bascule vidéo reprenne enfin. Vu du joueur : image figée, clavier mort.

Reproduit dans l'émulateur en trois touches (ESC pour passer en image, `I`,
puis n'importe quoi), et vérifié corrigé de la même façon. `show_inventory`
force désormais le texte à l'entrée, comme le faisaient déjà l'aide et le
choix des Pierres, et **rend au joueur son mode à la sortie** — le sac ouvert
en plein combat rend son illustration au combat.

À retenir : **un écran modal doit allumer l'affichage dans lequel il écrit.**
Trois des quatre le faisaient ; celui qui ne le faisait pas n'était pas
détectable en lecture de code, parce que le défaut n'est pas dans sa boucle,
il est dans ce qu'elle suppose de l'état de la machine.

Reste dans la même famille, non corrigé parce que non bloquant : les attentes
de combat (`wait_space_at`, `prompt_luck`) écrivent aussi leur invite dans le
texte sans l'allumer. En mode image plein écran, l'invite est invisible — mais
**n'importe quelle touche** les satisfait, donc on n'y reste pas coincé.

## ✅ Fait le 2026-08-31 — la régénération complète des images

Les 74 planches de référence validées la veille ont servi de canon à
**439 images** : 407 pages et 32 tableaux de bataille, toutes régénérées,
converties et embarquées. `check-project.sh` compte 407/407 scènes illustrées,
et les 439 flux HGRR se décodent en 8192 octets.

Ce que le chantier a appris, et qui est resté dans les outils :

- **Une consigne polie ne tient pas ; une consigne géométrique tient.** Le
  prompt de scène demandait déjà que le héros ne tourne pas le dos à son
  interlocuteur, en une phrase, au milieu du reste : les rendus le montraient
  malgré tout de dos, planté face au spectateur. Réécrite en placement
  imposé — les deux figures sur des côtés opposés, épaules, hanches, tête et
  regard du héros pointés vers l'autre, et l'énoncé explicite de la faute à
  ne pas commettre — la règle est respectée. C'est exactement ce qui avait
  déjà sauvé les images de bataille (`git log 869573d`). Une consigne de
  cadrage se rédige comme une contrainte, jamais comme un souhait.
- **La génération se parallélise, l'attente est du réseau.** Une image coûte
  ~2 min de mur presque entièrement passées à attendre le service :
  `generate_images.sh` prend un troisième argument, le nombre de générations
  de front. À 10, les 439 images ont pris ~3 h 30 au lieu des ~14 h d'une
  file simple, sans un seul échec.
- **L'agent d'image laisse des brouillons** (`B284-0.png`, `N025.raw.png`) à
  côté du rendu. Ils échappaient au motif du convertisseur, donc au disque,
  mais pas à la relecture humaine : le script les balaie maintenant après
  chaque image.
- **Ne jamais réécrire un script shell pendant qu'il tourne.** Bash relit le
  fichier au fil de l'exécution ; changer sa longueur sous ses pieds le fait
  reprendre à un mauvais décalage. Les corrections d'outillage trouvées en
  cours de lot ont attendu la fin du lot.
- **`check-project.sh` mentait depuis le passage au RLE** : il cherchait des
  `*.HGR.BIN` de 8192 octets et annonçait « 0 / 402 images » sur un disque
  qui les portait toutes, et il jugeait encore `SCOSWAMP.BIN` contre le
  plafond `$9600` abandonné le 2026-08-29. Il valide désormais chaque flux
  compressé avec `scoswamp_hgr validate` et donne à chaque moteur son propre
  plafond. Un contrôle qui ne suit pas le format qu'il contrôle est pire que
  pas de contrôle : il rassure à tort, puis il crie à tort.

Reste ouvert :

- 🟡 **`N113` reste la conversion la plus chargée** du lot (score 5,44 après
  un second tirage, contre 5,94 au premier ; le pire des 439). Ce n'est pas le
  convertisseur : la page empile flammes, toiles et araignées, et 280x192 n'en
  garde qu'une masse. Le héros et le sentier s'y lisent désormais, le côté
  droit non. Un tirage de plus, avec une composition explicitement dépouillée,
  la sauverait.
- ✅ **La « cotte de mailles » de la feuille d'aventure** contredisait l'image
  depuis que la fiche du héros lui a donné un justaucorps de cuir et les bras
  nus. Tranché en faveur de l'image, le 2026-08-31 : `MSGFR.TXT` et
  `MSGEN.TXT` lignes 3 et 40 disent « un justaucorps de cuir » / « a leather
  jerkin ». Les gardes du N372 gardent leurs cottes de mailles rouges — ce
  n'est pas l'équipement du héros. Le nombre de lignes est inchangé, ce qui
  compte : `messages_load` rejette un fichier qui n'en a pas exactement
  MSG_COUNT.
