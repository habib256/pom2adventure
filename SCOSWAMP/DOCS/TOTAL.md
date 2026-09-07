# TOTAL

Un gestionnaire de fichiers ProDOS à deux panneaux, dans l'esprit de Total
Commander, pour l'Apple IIe 128 Ko ; son nom complet est **Apple IIe Total
Commander 1.0** (le numéro vit dans `TOTAL_VERSION` du Makefile, repris par
le lanceur, la ligne de statut et l'aide). C'est un logiciel libre sous
licence GNU GPL v3, d'Arnaud Verhille, comme le reste du dépôt ; le lanceur
et l'aide le rappellent. Trois façons de le lancer : la touche **T** de l'écran-titre de
SCOSWAMP (la ligne « Utilitaires », en bas, propose aussi **D** pour DIAPO) ;
depuis Bitsy Bye, le dossier **TOTAL** puis **TOTAL.SYSTEM** et **Entrée** ;
ou la disquette dédiée décrite plus bas.
Le lanceur affiche un écran d'attente pendant le chargement : le titre, la
mention « ProDOS 8 only », la date et l'heure si une horloge est présente
(bit 0 de MACHID, `$BF98`) ou « No clock » sinon, puis **PLEASE WAIT**. Suivent
les deux panneaux en texte 80 colonnes : à gauche `/SCOSWAMP`, à droite
`/SCOSWAMP/DHGR` la première fois ; ensuite les deux dossiers, le tri et le
panneau actif de la session précédente, lus dans `TOTAL/TOTAL.CFG`.

Chaque panneau liste un dossier : nom, type ProDOS, auxtype et taille en
octets, les dossiers d'abord (avec leur nombre de blocs), puis les fichiers,
triés par nom, taille ou type selon le mode choisi (l'étoile de l'en-tête le
dit). La ligne en inverse est la sélection ; le chemin du panneau actif est
lui aussi en inverse. La ligne de séparation porte l'espace libre du volume
du panneau actif. La ligne 22 détaille l'entrée sélectionnée (type, auxtype,
blocs, octets, date de modification) et le nombre de fichiers marqués, la
ligne 23 reçoit les messages et les questions, la dernière ligne est la
barre de touches, façon Norton Commander : chaque touche dans un bloc
inverse, son libellé en clair juste après. Les visionneuses ont la leur,
avec le chemin et la page à gauche.

## Touches

| Touche | Action |
|---|---|
| **Haut / Bas** | déplacer la sélection |
| **Gauche / Droite** (ou **< / >**, **- / +**) | page précédente / suivante (18 lignes) : c'est le déplacement rapide dans un long dossier, le clavier de l'Apple IIe n'ayant pas de PgUp |
| **[ / ]** | première / dernière entrée |
| **TAB** | changer de panneau |
| **=** | ouvrir le dossier du panneau actif dans l'autre panneau |
| **Espace** | marquer ou démarquer le fichier sélectionné (étoile après le nom) et descendre |
| **\*** | inverser les marques du panneau |
| **'** puis une touche | sauter à l'entrée suivante dont le nom commence par cette lettre ou ce chiffre, comme dans Bitsy Bye |
| **Entrée** | ouvrir : un dossier s'ouvre ; une image s'affiche plein écran, en HGR ou en DHGR selon son contenu (une touche pour revenir, la ligne de message dit le format reconnu) ; un TXT se lit page par page ; un SYS ou un BAS se lance après confirmation ; tout autre fichier s'affiche en hexadécimal |
| **Échap** | remonter au dossier parent, la sélection revient sur le dossier quitté ; depuis la racine d'un volume, la liste des volumes |
| **/** | la liste des volumes en ligne |
| **C** | copier les entrées marquées, sinon l'entrée sélectionnée, dans le dossier de l'autre panneau ; un dossier est copié entier, sous-dossiers compris, un sous-dossier déjà présent est complété ; même nom, même type et auxtype. Quand le fichier existe, TOTAL demande : **O** écraser, **S** passer, **A** tout écraser, **N** ne rien écraser. Une barre de progression montre le fichier en cours, son rang sur le total et les octets copiés ; le message final compte les fichiers copiés et passés |
| **V** | déplacer : copie, puis suppression de l'original, dossiers compris |
| **R** | renommer (nom ProDOS : une lettre, puis lettres, chiffres ou points, 15 au plus) |
| **D** | supprimer les entrées marquées, sinon l'entrée sélectionnée, après une confirmation ; un dossier est supprimé avec tout son contenu |
| **K** | créer un dossier dans le panneau actif |
| **S** | changer le tri : nom, taille décroissante, type ; les deux panneaux suivent |
| **M** | marquer les fichiers absents de l'autre panneau ou de taille différente : suivi de C, c'est une synchronisation |
| **A** | changer le type et l'auxtype d'un fichier, en hexadécimal |
| **L** | verrouiller ou déverrouiller ; un fichier verrouillé porte un L après son nom et refuse la suppression et le renommage |
| **?** | l'aide, un écran qui résume toutes les touches, sous le titre « Apple IIe Total Commander » |
| **T** | lire le fichier sélectionné comme du texte |
| **H** | afficher le fichier sélectionné en hexadécimal |
| **X** | lancer le fichier sélectionné après confirmation ; TOTAL ne reprend pas la main. Un SYS est lu en `$2000`, un BIN à son auxtype, entre `$0800` et `$BAFF` (le talon garde son tampon ProDOS en `$BB00`). Un BAS (Applesoft) passe par `BASIC.SYSTEM`, voir ci-dessous |
| **E** | éditer le fichier sélectionné comme du texte ; sur un dossier ou `..`, créer un fichier texte neuf dans le dossier courant |
| **I** | afficher le fichier sélectionné comme une image, quel que soit son nom : HGR ou DHGR, brut ou compressé RLE |
| **P** | mettre en pause ou reprendre la musique Mockingboard ; Entrée sur un fichier `.MB` la lance |
| **F** | ouvrir le formateur, `TOTAL/FORMAT.SYS`, qui revient à TOTAL en sortant |
| **Q** | quitter vers ProDOS après confirmation : Bitsy Bye reprend |

Dans une image, **Gauche** et **Droite** passent à l'image précédente ou
suivante du même dossier sans revenir aux panneaux : le dossier DHGR se
feuillette comme un album, et le curseur suit. Toute autre touche revient.
Dans les visionneuses de texte et d'hexadécimal : **Espace**, **Entrée** ou
**Bas** page suivante, **B** ou **Haut** page précédente, **Échap** retour aux
panneaux.
La visionneuse de texte affiche 22 lignes par page, coupe les lignes au-delà
de 80 caractères et mémorise les débuts de page rencontrés, jusqu'à 96 pages.
La visionneuse hexadécimale affiche 320 octets par page, adresse, seize
octets et leur rendu ASCII.

## Les images

À l'ouverture, TOTAL lit les huit premiers octets et la taille :

| Contenu | Format reconnu | Affichage |
|---|---|---|
| `DHRR` 1 0 0 $40 | DHGR compressé RLE (flux DHRR v1, celui du jeu), 16 384 octets décompressés | DHGR |
| `HGRR` 1 0 0 $20 | HGR compressé RLE (flux HGRR v1, celui de SPACETRIP), 8 192 octets | HGR |
| 8 192 ou 8 184 octets | page HGR brute | HGR |
| 16 384 octets | page DHGR brute, banque AUX puis MAIN (l'ordre des fichiers A2FC et du jeu) | DHGR |

Le décodeur RLE est écrit en C et sert aux deux flux ; une répétition qui
chevauche la frontière des deux banques est coupée au passage de `$4000`.

**Le chargement ne se voit jamais.** Écrire dans `$2000-$3FFF`, c'est écrire
dans la page affichée : tant que le décodeur travaille, l'écran reste au
texte — les panneaux, intacts en `$400-$7FF` — et l'image ne s'allume qu'une
fois complète. Sans cela, feuilleter un dossier montrait l'image précédente
se faire recouvrir par la table d'entrées relue, puis la nouvelle se peindre
bande par bande, plan AUX avant plan MAIN. `load_image` remet aussi le
routage mémoire sur la banque principale avant toute lecture : le firmware 80
colonnes laisse `80STORE` armé, et avec `HIRES` encore actif d'une image
précédente une page HGR brute serait partie en banque auxiliaire.

**Une image DHGR détruit le contenu de `/RAM`, alors TOTAL le refait à
neuf.** Le disque virtuel de ProDOS vit en RAM auxiliaire, et la moitié
auxiliaire d'une page DHGR (`$2000-$3FFF` en banque AUX) lui appartient : 18
blocs, mesurés au banc, et c'est justement là que commencent les données d'un
fichier écrit sur `/RAM`. C'est la contrainte de la machine, pas un défaut de
TOTAL — le double haute résolution et `/RAM` se partagent les mêmes octets —
mais elle laissait un volume à moitié faux, dont la prochaine écriture rendait
n'importe quoi.

En quittant une image DHGR, TOTAL demande donc à `/RAM` de se reformater : il
reconnaît son pilote à son adresse `$FF00` dans `DEVADR` (`$BF10`), comme le
formateur, et lui envoie la commande FORMAT, carte langage commutée en banque
1 comme ce pilote l'exige (`ram_format`, dans `total_mli.s` — une quarantaine
d'instructions ; le pilote reconstruit lui-même le répertoire de volume, il
n'y a aucune structure à écrire, et l'appel rend à TOTAL la banque 2 de la
carte langage, pas la ROM). Le volume revient vide et cohérent, 119
blocs libres sur 127, et la ligne de message le dit : `/RAM was rebuilt
empty.` On perd ce qu'il contenait — c'était déjà perdu — mais plus rien
n'est faux.

Une image **HGR simple** n'écrit qu'en banque principale : elle ne touche pas
à `/RAM` et ne déclenche rien. Le banc `ram_dhgr.py` vérifie les deux cas.
Le jeu et DIAPO, qui affichent du DHGR en permanence, détruisent `/RAM` de la
même façon et ne le refont pas : ils ne s'en servent pas.
Dans un dossier, Gauche et Droite passent à l'image précédente ou suivante
parmi les fichiers qui ressemblent à une image (type FOT, ou BIN de la
taille d'une page, ou nom en `.RLE`). Un banc à part,
`validate_images.py`, monte un volume avec les formats compressés et le DHGR
brut, et compare la page graphique octet à octet : 10 contrôles.

## Lancer un programme Applesoft

Un fichier BAS ne se lance pas seul : c'est `BASIC.SYSTEM` qui l'exécute.
**X** (ou **Entrée**) sur un BAS charge donc `BASIC.SYSTEM` depuis la racine
du volume et lui passe le nom du programme dans le tampon que tous ses
lanceurs utilisent — Bitsy Bye compris : les huit premiers octets d'un
programme SYSTEM sont un saut puis un nom précédé de sa longueur, en `$2006`,
et `BASIC.SYSTEM` en fait la commande `-NOM` à son démarrage. `chain_command`
(chain.s) dépose ce nom dans le talon de la page `$0300`, qui l'écrit en
`chain_addr+6` juste avant de sauter.

Le préfixe ProDOS part sur le dossier du programme : `-NOM` s'y résout, un BAS
rangé dans un sous-dossier se lance donc aussi. Sans `BASIC.SYSTEM` à la
racine du volume, le lancement s'arrête sur `Run failed` et TOTAL garde la
main. Comme pour un SYS, TOTAL ne reprend pas la main ensuite : on revient
par Applesoft.

## Formater un disque

`F` (ou `TOTAL/FORMAT.SYS` depuis Bitsy Bye) lance le formateur, un
programme à part qui revient à TOTAL en sortant. Il liste les lecteurs que
ProDOS connaît, avec slot, lecteur, type (Disk II 5,25 pouces, SmartPort,
/RAM, périphérique de bloc), volume actuel s'il en a un et taille en blocs.
Le disque d'où tourne le programme est marqué IN USE et refusé. Trois
étapes : choisir un lecteur par son numéro, nommer le volume (BLANK par
défaut), puis lire l'avertissement, qui nomme le lecteur, son volume actuel
et sa taille, et taper le mot ERASE en capitales suivi d'Entrée. Rien n'est
écrit avant ce mot ; Échap annule à chaque étape.

Une disquette Disk II est formatée physiquement, piste par piste avec la
progression à l'écran : c'est le ProDOS Hyper-FORMAT de Jerry Hewett (1985,
domaine public) et Gary Desrochers (1989) tel qu'ADTPro l'a repris,
découpé en trois appels pour afficher l'avancement (`format_diskii.s`). Le
GAP1 de tête est allongé de 512 octets de synchro pour qu'une piste écrite
recouvre un tour complet, quel que soit le lecteur ou l'émulateur. Un
SmartPort qui le permet reçoit l'ordre de formatage bas niveau, le /RAM
celui de son pilote, un disque dur rien. Puis, pour tous, les structures
ProDOS sont écrites par WRITE_BLOCK (`format.c`) : l'amorce d'Hyper-FORMAT
au bloc 0, le catalogue racine aux blocs 2 à 5 avec la date de l'horloge,
la table d'allocation à partir du bloc 6. L'amorce et l'en-tête sont relus
et comparés. Le banc `validate_format.py` formate une disquette vierge dans
le Disk II émulé et le /RAM, vérifie le refus du disque en usage et d'un
mot inexact, le retour à TOTAL, la création d'un dossier sur le volume neuf
et, l'émulateur arrêté, l'image `.dsk` elle-même : 17 contrôles.

## La musique Mockingboard

Entrée sur un fichier `.MB` (flux MB1, 2 304 octets au plus) le monte en
mémoire auxiliaire par le lecteur six voix du jeu et le joue une fois, en
interruption : la navigation, les visionneuses et l'éditeur continuent
pendant la musique, et les lectures disque ne l'arrêtent pas (vérifié dans
l'émulateur : le curseur du flux avance pendant la lecture des dossiers et
le chargement d'une image). Sur une disquette 5,25 pouces, le pilote Disk II
de ProDOS coupe les interruptions pendant chaque lecture de bloc : le lecteur
se fige le temps de la lecture, puis reprend ; TOTAL n'y peut rien. P la met
en pause et la reprend, un autre `.MB` la remplace, Q et X la coupent ; une
fois le morceau fini, P le dit. La carte est cherchée dans les slots 1 à 7 à la
première demande ; sans carte, TOTAL le dit.

## L'éditeur de texte

`E` ouvre le fichier dans un éditeur plein écran de 22 lignes : flèches,
Suppr pour effacer à gauche, Ctrl-D à droite, Ctrl-A et Ctrl-E début et fin
de ligne, Ctrl-P et Ctrl-N page précédente et suivante, Ctrl-T et Ctrl-B
début et fin du texte, Entrée coupe la ligne, Tab insère quatre espaces.
La barre du bas donne le chemin, la ligne, la colonne, la taille et une
étoile si le texte a changé. Échap ouvre le menu : S sauver, X sauver et
sortir, Q quitter sans sauver (avec confirmation si le texte a changé),
Échap continuer. Le fichier garde son type et son auxtype ; le texte tient
dans la page graphique, donc 8 Ko au plus, fins de ligne CR, bit 7 ôté au
chargement. Les lignes plus longues que l'écran ne sont pas repliées.

## Ce que TOTAL ne fait pas

- Il refuse de copier un dossier dans lui-même, et un arbre dont un chemin
  cumule plus de 213 entrées (la réserve des parcours récursifs, logée dans
  la table du panneau inactif pendant l'opération).
- Il ne lance pas les programmes BASIC (BAS) : BASIC.SYSTEM n'est pas sur le
  volume, le jeu occupe sa mémoire.
- Un dossier de plus de 139 entrées est lu par fenêtres, dans l'ordre du
  disque et sans tri : l'en-tête indique le rang de la première entrée
  suivi d'un signe plus, et le curseur passe d'une fenêtre à l'autre en
  franchissant les bords. Aucun dossier du volume n'atteint cette taille ;
  ce mode n'est pas couvert par le banc.
- Il ne modifie aucun fichier de lui-même : seules les commandes C, V, R, D
  et K écrivent sur le disque.

## Fichiers sur le disque

| Nom ProDOS | Fonction |
|---|---|
| `TOTAL/TOTAL.SYSTEM` | Programme SYS sélectionnable dans Bitsy Bye (`loader.c`, comme DIAPO) |
| `TOTAL/TOTAL.CODE` | Le gestionnaire lui-même (`SCOSWAMP/SRC/total.c`, plus `total_mli.s` pour GET_FILE_INFO et SET_FILE_INFO : espace libre, type, auxtype, verrou) |
| `TOTAL/TOTAL.CFG` | Écrit par TOTAL en quittant : les deux dossiers, le tri et le panneau actif, trois lignes de texte |
| `TOTAL/FORMAT.SYS` | Le formateur (`format.c`, `format_diskii.s`, `format_mli.s`). Pas de suffixe .SYSTEM : ProDOS amorce le premier fichier .SYSTEM du catalogue, et F passe avant S |
| `TOTAL/TOTAL.HELP` | Le texte de la page d'aide (`SCOSWAMP/TOTAL/TOTAL.HELP.TXT`), une ligne par élément : `x,y,TOUCHE,libellé`, `x,y,#TITRE` pour une section, `x,y,~texte` pour du texte en clair. Il passe par la page graphique, rien de l'aide ne reste en mémoire |

Les noms tiennent dans les quinze caractères de ProDOS.

## La disquette 5,25 pouces

`make -C SCOSWAMP/SRC floppy` produit `dist/APPLE.TOTAL.po` (ordre ProDOS)
et `dist/APPLE.TOTAL.dsk` (ordre DOS 3.3, celui d'ADTPro et de la plupart
des émulateurs), une disquette amorçable de 280 blocs, volume `/APPLE.TOTAL` :

| Fichier | Contenu |
|---|---|
| `PRODOS` | ProDOS 8 2.4.3, la dernière version stable (identique à celle du volume du jeu, vérifiée contre l'image officielle du dépôt ProDOS-8) |
| `TOTAL.SYSTEM` | le lanceur, seul programme `.SYSTEM` : la disquette démarre directement dans TOTAL. Compilé avec `NO_CHDIR`, il se fie au préfixe du volume amorcé |
| `TOTAL/TOTAL.CODE`, `TOTAL/TOTAL.HELP` | le même binaire et la même aide que sur le volume du jeu ; `TOTAL.CFG` sera écrit à côté |
| `TEST/` | de quoi essayer : `HGR.RAW` (page HGR brute de SPACETRIP), `HGR.RLE` (la même en HGRR), `DHGR.RLE` (une image du jeu en DHRR), `WELCOME.MB` (une musique) et `README`. Une DHGR brute de 16 Ko aurait pris 33 des blocs restants |

Il reste 60 blocs libres. Au démarrage, le panneau gauche montre la racine
de la disquette et le panneau droit la liste des volumes, faute de dossier
`DHGR`. `build_prodos_volume` taille ses volumes au contenu ;
`make_floppy.py` porte ensuite le compte de blocs à 280, libère les blocs
ajoutés dans la table d'allocation et écrit les deux ordres de secteurs. Le
banc a démarré cette image comme disque dur dans POM2 : TOTAL s'ouvre sur
`/APPLE.TOTAL`, Q rend la main à Bitsy Bye sur ce volume. Une version 2.5
alpha 8 de ProDOS existe ; elle n'est pas retenue, faute d'être publiée.

## Construction et mémoire

`make -C SCOSWAMP/SRC total` construit les deux fichiers ;
`make -C SCOSWAMP/SRC hdv` les embarque. TOTAL réutilise le lanceur, la
disposition LC/MAIN, le décodeur DHGR (`hgr_loader.s`) et les bascules vidéo
(`memory_swap.c`) du jeu, sans la musique ni les catalogues de DIAPO. Le code
tourne à `$4000`. Les deux tables de 140 entrées occupent la page graphique
MAIN `$2000-$3FFF`, libre tant qu'aucune image n'est affichée : une image
la recouvre, et les deux panneaux sont relus au retour, marques conservées.
La RAM basse `$1000-$1FFF` reçoit toute la BSS de `total.c` (panneaux,
chemins, copie, débuts de page du texte), mise à zéro par `main`, et depuis
`total.cfg` la BSS principale de cc65 avec elle. Son dernier kilo-octet,
`$1C00-$1FFF`, est **du code** : segment `LOWEXE`, le décodeur RLE et ce qui
l'entoure. Le lanceur met en scène en `$1000` un préfixe de 4 Ko au lieu de 3
(`STAGE_BYTES` dans `loader.c`) ; `crt0` n'en emporte que les trois premiers
vers la carte langage, le quatrième reste sur place. Personne d'autre n'y
touche : la zone `LOWRAM` est bornée à `$0C00` pour que le lieur refuse une
BSS qui monterait jusque-là, et `check_lc_layout.py` le vérifie aussi. C'était
la dernière réserve de place de la machine — la fenêtre principale bute sur la
pile C, la carte langage est pleine. **`TOTAL.SYSTEM` et `TOTAL.CODE` vont
désormais par paire** : un ancien lanceur ne lit que 3 Ko et laisserait le
décodeur d'images absent. La réserve
des parcours récursifs emprunte la table d'entrées du panneau inactif.
Les visionneuses, les saisies et le fichier de préférences vivent dans la
carte langage, `$D400-$DFFF` en banque 2 (une vingtaine d'octets libres : `check_lc_layout.py` veille), copiés par `crt0.s` comme pour le
jeu ; avant de lancer un programme, TOTAL remet la ROM en lecture.

**Le plafond de la fenêtre principale.** Ce qui survit à l'initialisation —
CODE, RODATA, DATA, INIT — doit finir sous le plancher de la pile C,
`__HIMEM__ - __STACKSIZE__` ; seul ONCE a le droit de le dépasser, il est mort
avant `main`. ld65 ne le vérifie pas : la zone BSS se dimensionne par
`__HIMEM__ - __STACKSIZE__ - __ONCE_RUN__` et, dès que cette différence passe
en négatif, il la lit en entier non signé, ne signale rien et pose la BSS au
milieu de la pile. Le lien réussit, le programme se corrompt à l'usage. Deux
mesures ferment ce piège : TOTAL est lié par `total.cfg`, où la BSS descend en
RAM basse (il ne lie ni `malloc` ni `free` — les tampons ProDOS viennent de
`$0800` — donc aucun tas ne la suit, ce qui n'est pas vrai du jeu), et
`check_lc_layout.py` contrôle le plancher à chaque lien. La pile C fait 256
octets : le banc a mesuré son creux maximal à **94 octets** sous `$BF00`, la
copie récursive d'un arbre comprise, `-Cl` mettant les locales en statique.
Les 512 octets d'avant, plus les 88 de la BSS, sont rendus au code — de quoi
loger le lanceur Applesoft, là où il ne restait qu'une vingtaine d'octets.
Les programmes lancés par
X et F le sont par un talon recopié en page `$0300` (`chain.s`), qui lit le
fichier entier à son adresse et y saute : aucune limite de taille, et
FORMAT.SYS revient à TOTAL par le même talon ; `chain_command` y ajoute le nom
que `BASIC.SYSTEM` attend en `$2006`, seize octets de plus dans le talon, et
une assertion d'assemblage garde l'ensemble sous `$03D0`, où commencent les
vecteurs. TOTAL n'utilise plus ni
`opendir` ni `malloc` : les dossiers sont lus comme des fichiers, bloc par
bloc, dans le tampon de copie, ce qui est aussi plus rapide. Pour loger
l'éditeur et le visionneur, il a aussi rendu `hgr_loader.s` (le décodeur C
le remplace, par tranches `memset`/`memcpy` jusqu'à la frontière des
banques), `qsort` (un tri par insertion) et `exec()` (un lanceur de
quelques lignes) ; les messages répétés sont partagés et l'aide vit sur le
disque. Les deux fichiers ouverts pendant une copie utilisent les tampons
ProDOS `$0800` et `$0C00` ; TOTAL n'utilise pas MAPBSS. Le programme est
compilé avec `-Cl` (variables locales statiques) comme le jeu ; les trois
parcours récursifs (compte, copie, suppression d'un arbre) repassent leurs
variables sur la pile par `#pragma static-locals`, sans quoi le niveau
interne écrase la longueur de chemin du niveau externe. La sortie suit le QUIT ProDOS du démarrage cc65.

Les preuves POM2 headless sont dans
[VALIDATION-TOTAL](../../DOCS/VALIDATION-TOTAL/result.json) :
lancement depuis Bitsy Bye, barre inverse, espace libre, aide, images
`N000.RLE` puis `N001.RLE` (flèches) vérifiées octet à octet dans les deux
banques, tri, lecture de `TITLE`, hexadécimal de `MAP`, création d'un
dossier, copie simple et copie de deux fichiers marqués, suppression des
fichiers marqués, question d'écrasement (passer puis écraser), marquage des
différences et inversion, saut par lettre, verrou refusant la suppression,
changement de type et d'auxtype, copie d'un dossier entier avec ses types et
tailles, refus de copier un dossier dans lui-même, copie puis suppression
d'un arbre à deux niveaux, renommage, liste des volumes avec slot et espace
libre, retour à Bitsy Bye, restauration des panneaux par `TOTAL.CFG`, puis
lancement de `DIAPO.SYSTEM` depuis TOTAL : 50 contrôles. Le banc travaille sur
une copie du disque ; `SCOSWAMP/DHGR` n'est jamais modifié. Trois autres
bancs le complètent : `validate_images.py` (visionneur HGR RLE et DHGR brut et RLE,
comparaison octet à octet ; le HGR brut, un simple `fread` de 8 Ko, n'en fait
plus partie), `validate_format.py` (formatage d'une disquette
vierge et du /RAM, image vérifiée à l'arrêt), `validate_floppy.py`
(`dist/APPLE.TOTAL.dsk` amorcée seule avec `pom2_playtest --disk ... --boot 6` :
racine, F puis ESC qui revient à TOTAL, aide, musique de TEST jouée une fois
pendant l'image), `validate_basic.py` (un programme Applesoft rangé dans un
sous-dossier, lancé par `BASIC.SYSTEM` et qui imprime), `ram_dhgr.py` (les
blocs de `/RAM` détruits par une image DHGR, marque par marque, puis le volume
refait à neuf, et une image HGR qui n'y touche pas) et `stack.py`
(le creux maximal de la pile C) ; et `explore.py`, la chasse aux bugs de la 1.0 sur un
volume artificiel : dossier de 150 fichiers lu par fenêtres puis copié vers un
/RAM trop petit, dossier vide, fichiers de 0 octet, lignes de 200 caractères
dans le visionneur et l'éditeur, chemin de 56 caractères, renommage vers un
nom existant.

Bugs corrigés par cette chasse (et une relecture indépendante du code) avant
la 1.0 : la carte des marques faisait un octet de trop court (quatre entrées
fantômes dans une fenêtre pleine), le panneau tronquait les chemins longs par
la fin, une fenêtre après la première comptait 140 entrées et en répétait une,
un dossier vidé en mode fenêtré restait bloqué, le formateur calculait la
carte des blocs sur 16 bits (nulle pour 65 535 blocs), prenait la taille dans
l'en-tête de l'ancien volume, acceptait un lecteur sans disque, et revenait à
Bitsy Bye depuis la disquette (TOTAL.SYSTEM y est à la racine) ; un BIN chargé
en `$0800` écrasait le tampon du talon ; un TOTAL.HELP ou un TOTAL.CFG abîmé
pouvait faire écrire n'importe où ; la copie détruisait la cible avant d'avoir
ouvert la source, et pouvait remplacer un dossier vide par un fichier. Le
plus grave, trouvé par la relecture finale et reproduit par `roundtrips.py` :
le talon de lancement ne rendait pas à ProDOS l'entrée d'interruption prise
au démarrage pour la Mockingboard (ProDOS n'en a que quatre, et le vecteur
pointait dans de la mémoire recouverte) ; au troisième aller-retour F/ESC,
TOTAL plantait dans le moniteur. `chain.s` appelle désormais `donelib`
(les destructeurs cc65) avant de sauter, et le lanceur D/T du jeu fait de
même. Une troisième relecture, centrée sur l'éditeur, les images et la
musique, a encore corrigé : l'éditeur n'avait pas de curseur visible
(`cursor(1)` de conio), un fichier créé par E décalait les marques restaurées
sur d'autres entrées (elles sont effacées dans ce cas), une sauvegarde sur un
volume plein vidait le fichier avant d'échouer (la place est vérifiée avant
le `fopen "wb"` qui tronque), Entrée au milieu d'une ligne laissait
l'ancienne fin à l'écran, les erreurs d'ouverture de l'éditeur disparaissaient
sous le redessin, le lanceur lisait TOTAL.CODE sans borne sous `$BF00`, le
destructeur de la musique passait après la libération de l'interruption
(priorité 11 dans `music.s`), le visionneur d'images gardait un index périmé
si le dossier changeait sous lui, et un .MB sans END faisait lire l'AUX
au-delà du flux. `explore2.py` couvre l'éditeur (raccourcir, sans CR final,
LF seuls, fichier verrouillé), les marques en fenêtre pleine et en seconde
fenêtre, le déplacement vers /RAM et la suppression d'un arbre de 150
fichiers.
