# L'atelier -- les jeux du depot dans le navigateur

Un interprete HTML/JavaScript qui lit **exactement les octets que l'Apple II
demarre** -- le volume ProDOS `dist/SCOSWAMP.HDV`, ouvert et parcouru dans le
navigateur -- et joue le jeu avec, en montrant a cote les **images master**,
celles d'avant la conversion DHGR.

La premiere page choisit le jeu : **SCOSWAMP** ou **SPACETRIP**. Ce sont deux
donnees du meme atelier.

    sh SCOSWAMP.MORE/TOOLS/interpreter/serve.sh        # puis http://localhost:8765/...

Le script sert la RACINE DU DEPOT (le lecteur lit `SCOSWAMP/TEXTFR/...`,
`SCOSWAMP/DHGR/...` et `SCOSWAMP.MORE/GENERATED/...`) et ouvre la page. Les
modules ES exigent `http://` : ouvrir `index.html` en `file://` ne marchera
pas.

Sans navigateur, le meme moteur verifie un corpus entier :

    node SCOSWAMP.MORE/TOOLS/interpreter/verifier.js                       # le volume
    node SCOSWAMP.MORE/TOOLS/interpreter/verifier.js project.scoswamp.json FR --arbre
    node SCOSWAMP.MORE/TOOLS/interpreter/verifier.js project.spacetrip.json

## Les memes octets que la machine

Deux sources, et la difference compte :

- l'**arborescence du depot** (`SCOSWAMP/TEXTFR/N000/N001.TXT`) : ce que l'on
  edite ;
- le **volume ProDOS** (`dist/SCOSWAMP.HDV`) : ce que la machine demarre.

Entre les deux il y a un empaquetage, et tant qu'il n'a pas tourne les deux
different. L'atelier lit donc le VOLUME par defaut : `prodos.js` ouvre le
`.HDV`, parcourt son catalogue (blocs de 512 octets, treize entrees de 39 par
bloc, seedling / sapling / tree) et sort les fichiers sous les noms que la
machine demande a `fopen()` -- `TEXTFR/N000/N001` et non `N001.TXT`, `MAP` et
non `MAP.BIN`, `IMG/N000/N012.RLE`. C'est la regle de `build_prodos_volume` :
le contenu du dossier du jeu a la racine du volume, extension retiree.

A chaque page, la barre du haut dit d'ou viennent les octets et **si le depot
a bouge depuis l'empaquetage** : `volume SCOSWAMP (1346 fichiers) -- volume =
depot`, ou `le depot a change depuis l'empaquetage` en orange. C'est la
question de l'auteur qui vient d'editer une page : est-ce que la machine la
verra ? Le verificateur pose la meme question sur tout le corpus.

Deux choses ne sont pas sur le volume, et le lecteur le dit au lieu de faire
comme si : les **masters** d'avant conversion (ils sont l'ENTREE de la
conversion, pas sa sortie) et l'**ordre des messages**, qui vit dans
l'enumeration de `SRC/messages.h` -- compilee dans le binaire, donc la meme
verite a la meme source. Les chaines, elles, viennent du volume.

## A quoi ca sert

Comparer le master et le DHGR **dans le contexte de la page**. Une
illustration ne se juge pas seule : elle se juge sous son texte, a cote de ses
choix, dans la scene qui l'amene. Le selecteur en haut de la colonne de droite
passe de l'un a l'autre sans rien recharger :

| variante | ce qu'elle montre |
| --- | --- |
| Master (avant DHGR) | `SCOSWAMP.MORE/GENERATED/N012.png`, pleine resolution |
| DHGR decode (Chat Mauve / composite) | le flux `IMG/N000/N012.RLE.BIN` **decode ici meme** |
| Apercu PNG | les PNG que `convert_images.sh` depose a cote |

Le decodeur DHGR est un portage de `TOOLS/scoswamp_dhgr.cpp` et de
`pom2/src/hgrpaint` : verifie pixel pour pixel contre les apercus de
reference, sur les deux palettes. Ce qui s'affiche est donc ce que la machine
affichera, pas une approximation.

Le reste de la colonne de droite est le banc d'essai : la Feuille d'Aventure,
le **journal des directives** de la page (chaque ligne `E`, `P`, `M`, `CU`...
avec ce qu'elle a fait), la **source** du fichier avec ses directives
surlignees, le sac, et la table des directives du jeu.

Trois parametres d'adresse, pour tester sans rejouer le prologue :

    ?jeu=spacetrip      passe le choix du jeu
    ?langue=FR          passe l'ecran d'accueil
    ?page=283           s'y pose, personnage deja jete
    ?graine=1234        rejoue exactement la meme partie -- meme des
    ?source=arbre       lit l'arborescence au lieu du volume

La graine n'est pas un a-peu-pres : le generateur est celui de `dice.c`, bit
pour bit (congruentiel 32 bits, bits de poids fort). A semence egale, ce
lecteur jette les memes des que le binaire Apple II.

## Le principe : un jeu est une DONNEE

Le portage Apple II tient deja que « le texte du jeu est une donnee » : les
pages, l'aide, la carte et les catalogues vivent sur le disque. Ce lecteur
pousse le trait d'un cran -- **les chemins, la table des directives, les
catalogues et la mise en page sont eux aussi des donnees**, dans un
descripteur JSON :

    project.scoswamp.json     35 clairieres, 33 directives, 420 pages, DHGR RLE
    project.spacetrip.json    94 pages a plat, huit directives, HGR brut

L'accueil les propose tous les deux (la liste est dans `jeux.json`, un serveur
HTTP ne listant pas un repertoire). SPACETRIP ne partage avec SCOSWAMP ni la
mise en page des fichiers, ni le format d'image, ni les catalogues, ni la
Feuille d'Aventure, ni meme l'endroit d'ou vient le titre d'une page -- et pas
une ligne de code ne change.

Ce que le descripteur porte :

- `assets` : les gabarits de chemin (`{LANG}`, `{BUCKET}`, `{PAGE}`, `{IMG}`) ;
- `directives` : les jetons du jeu **dans l'ordre qui fait foi** -- c'est la
  table `kOps` de `scoswamp.c`, sortie du code. Une directive absente n'existe
  pas pour ce jeu : sa ligne retombe dans le texte de la page ;
- `moteur` : le budget de l'ecran (18 lignes de recit, 80 colonnes, 5 choix) ;
- `pierres`, `amulettes`, `objetsSpeciaux` : ce que les regles doivent nommer.

Ce que le CODE porte : le SENS des jetons (une trentaine de gestes que tout
livre-jeu partage), les regles de Defis Fantastiques, et l'ecran.

Les catalogues, eux, ne sont pas recopies : les objets viennent de
`SCOSWAMP/TEXTFR/OBJFR.TXT`, les messages d'interface de `SCOSWAMP/TEXTFR/MSGFR.TXT` indexes par
l'enumeration de `SRC/messages.h`, les noms de clairieres et l'ecran de carte
du fichier `MAP` -- le meme binaire v3 que lit `map_load()`.

## Les fichiers

    index.html   main.js        l'amorce : descripteur, langue, boucle
    data.js                     la couche disque : gabarits, catalogues, MAP.BIN
    dhgr.js                     RLE DHRR/HGRR, palettes, rendu 280x192
    rules.js                    portage de rules.c et dice.c -- aucun DOM
    scene.js                    portage de classify_line() -- table en donnee
    engine.js                   portage de load_scene(), run_combat(), les jets
    ecran.js                    la grille 80 x 24 et ses primitives
    prodos.js                   le volume .HDV : catalogue et lecture
    ui.js                       la mise en page de la machine, l'atelier
    verifier.js                 le meme moteur, sans navigateur
    jeux.json                   les jeux que l'accueil propose
    project.*.json              les jeux

`rules.js` et `engine.js` ne touchent jamais au DOM : c'est ce qui permet a
`verifier.js` de monter **exactement les memes fichiers** que le navigateur --
pas une copie, pas une seconde implementation. Ce que le verificateur dit
d'une page est ce que le lecteur en fera.

## L'ecran est le meme, pas seulement ressemblant

La colonne de gauche n'est pas une mise en page web qui evoque l'Apple II :
c'est une grille de 80 x 24 cellules, chacune avec son attribut de video
inverse, peinte par les primitives de `scoswamp.c` portees telles quelles --
`render_title_bar()`, `render_place()`, `render_choices()`, `show_fighters()`,
`put_gauge()`, `put_key()`, `put_roll()`.

Sur la machine, la video inverse n'est pas un caractere mais un MODE :
`revers(1)` puis des espaces, c'est le seul pave plein dont elle dispose. Les
deux barres, les jauges d'ENDURANCE (`[####------]`, arrondies vers le HAUT --
tant qu'il reste un point, il reste une case), les noms des combattants, les
touches de l'invite (` ESPACE  engager `) et le compte qui passe en inverse
sous cinq points d'ENDURANCE sont tous faits de cela, et le sont ici aussi.

Les bornes suivent : `pad_to(79)` s'arrete a la colonne 79, parce que la
derniere cellule de l'ecran ferait defiler la page. La barre de lieu fait donc
79 colonnes et la barre de titre 80, exactement comme la-bas.

Les ecrans du sac, de la carte, de l'aide, de la Feuille, des sauvegardes et du
choix des Pierres se peignent dans cette meme grille -- la machine n'a qu'un
ecran et le repeint en entier. Il n'y a aucune fenetre flottante. Ce qui repond
a une touche repond aussi au clic.

La largeur de la colonne est celle de l'ecran, 80 colonnes de chasse fixe et
pas une de plus (`width: calc(80ch + 22px)`) : tout ce qui reste de la fenetre
va a l'image, qui gagne a etre grande.

## Ce qui est fidele, ce qui ne l'est pas

Fidele : l'ordre des gestes d'une page (un de `ED` tombe avant le combat quel
que soit son rang dans le fichier ; un detour `V` annule tout le reste), les
bornes des caracteristiques, le plafond du total de depart, la memoire des
clairieres (fuir puis revenir retrouve la creature blessee), la memoire des
pages vues, l'ordre des quatre des d'un assaut, les enjeux de la Chance, la
table des directives, la mise en page et ses budgets.

Fidele aussi : les barres, les jauges et les touches, au caractere et a la
colonne pres -- voir ci-dessus.

Pas fidele, et volontairement : pas de musique (les `.MB` sont des fichiers
Mockingboard -- le journal dit quel morceau la page demande), pas de bruitage,
pas de bascule video (l'image est toujours a cote), et les sauvegardes vont
dans le stockage du navigateur plutot que sur le volume.

## La suite

Ce lecteur est le premier etage d'un atelier de creation de jeux d'aventure :
on ecrit et on verifie les donnees ici, un moteur natif les joue sur la
machine cible. SCOSWAMP et SPACETRIP en sont les deux premiers jeux --
donnees d'un cote, implementation Apple II de l'autre.

Ce qui manque encore pour que ce soit un atelier et plus un lecteur :
l'edition des pages (le panneau Source est en lecture seule), la creation d'un
jeu depuis le descripteur vide, et l'export d'un volume -- ce que
`build_manifest.py`, `build_map.py` et `build_prodos_volume.cpp` font
aujourd'hui en ligne de commande.
