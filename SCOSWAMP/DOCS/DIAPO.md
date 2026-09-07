# DIAPO

Depuis Bitsy Bye, ouvrir le dossier **DIAPO**, sélectionner **DIAPO.SYSTEM** puis appuyer sur **Entrée**.
Le lanceur affiche immédiatement **PLEASE WAIT** pendant le chargement.
Une page de titre en anglais présente le diaporama en texte 80 colonnes.
Appuyer sur Entrée pour démarrer. Le programme enchaîne ensuite les images
du jeu, scènes et combats compris, puis recommence à la fin.

- **Espace** : bascule entre DHGR plein écran et DHGR mixed avec les informations.
- **Flèche droite / Entrée** : image suivante.
- **Flèche gauche** : image précédente. Les flèches bouclent aux extrémités du catalogue.
- **M** : menu musical en texte 80 colonnes, également accessible depuis la page de garde.
- **Q** : quitte le logiciel depuis la page de garde, les images ou le menu musical.
  Échap reste un raccourci compatible.

Le plein écran est le mode initial. Le choix plein écran/mixed reste actif
sur les images suivantes, sans apparition automatique du bandeau.
Chaque image reste affichée 300 trames (environ cinq secondes NTSC, six PAL),
hors chargement. L'attente suit le signal vidéo VBL.
Le bandeau mixed affiche le titre de la directive T du texte anglais Nxxx ;
une image de combat Bxxx prend le titre du même Nxxx. Le titre est compilé
avec le catalogue, donc une correction dans l’éditeur est prise en compte
à la prochaine fabrication du disque. Les enregistrements de 144 octets
(chemin 64, titre 80) permettent aussi un accès direct à l’image précédente,
sans reparcourir toute la liste.

Dans le menu musical, les 45 titres et **STOP** tiennent dans trois colonnes
de 16 lignes. Haut/bas parcourent les titres ; gauche/droite changent de
colonne. Déplacer le curseur ne réécrit que deux caractères, sans effacer
l’écran. Au-delà de 48 entrées, une nouvelle page est affichée automatiquement. Entrée lance le morceau en boucle et
revient à l'image ; choisir **STOP** coupe la musique. M ferme le menu
sans changer le morceau. Le défilement des diapos est suspendu pendant le
menu ; l'image et le mode d'affichage sont conservés au retour.
Sans Mockingboard, le menu l'indique et le diaporama reste disponible.
Le lecteur six voix du jeu est réutilisé, avec détection automatique du slot.

La version actuelle contient **453 images**. Le catalogue est automatiquement
recalculé par `make -C SCOSWAMP/SRC hdv`, à partir de tous les fichiers
`SCOSWAMP/DHGR/**/*.RLE.BIN`, dans l'ordre des chemins. Il n'y a pas de liste
de scènes codée dans le programme.

## Fichiers sur le disque

| Nom ProDOS | Fonction |
|---|---|
| `DIAPO/DIAPO.SYSTEM` | Programme SYS sélectionnable dans Bitsy Bye |
| `DIAPO/DIAPO.CODE` | Moteur du diaporama |
| `DIAPO/DIAPO.LIST` | Liste lisible des chemins d’images |
| `DIAPO/DIAPO.IMAGES` | Catalogue binaire : chemin et titre de chaque image |
| `DIAPO/DIAPO.DATA` | Métadonnées binaires de démarrage (nombre d’images et titres) |
| `DIAPO/MUSIC.LIST` | Catalogue des noms et titres musicaux |
| `MUSIC/*.MB` | Les 45 morceaux Mockingboard |

Le dossier DIAPO regroupe le programme et ses catalogues. Les images restent
partagées dans DHGR et les musiques dans MUSIC à la racine, sans duplication. Le catalogue musical est généré
à partir de MUSIC ; chaque ligne associe `FICHIER.MB|Titre` (séparateur CR).
La fabrication compile aussi `DIAPO.DATA` : en-tête DIA1 de huit octets,
puis 46 entrées de 48 octets (nom 16, titre 32), soit **2 216 octets**.
DIAPO le charge directement sans recompter les 453 images ni analyser le
texte du catalogue musical.
Les titres par défaut proviennent des noms des morceaux. Les données musicales
résident en AUX `$1000–$1DFF`, distinctes des images AUX `$2000–$3FFF`.

DIAPO est un programme séparé ; il ne charge ni ne modifie les sauvegardes
de SCOSWAMP. Le lanceur DIAPO.SYSTEM reste dans DIAPO ; SCOSWAMP.SYSTEM est
le programme de démarrage à la racine du volume.

Le chargement réutilise le lanceur et la disposition LC/MAIN du moteur.
Le code tourne à `$4000`, les images occupent `$2000–$3FFF` dans MAIN et AUX,
le tampon RLE occupe `$1000–$107F`. Les deux fichiers ouverts simultanément
(catalogue et image) utilisent les tampons ProDOS `$0800` et `$0C00` ; DIAPO
n'utilise pas MAPBSS. La sortie suit le QUIT ProDOS du démarrage cc65.

Les preuves POM2 headless sont dans
[VALIDATION-DIAPO-MUSIC](../../DOCS/VALIDATION-DIAPO-MUSIC/result.json).

The slideshow reads images from `/SCOSWAMP/DHGR` and the shared tracks from
`/SCOSWAMP/MUSIC`. Music filenames and selection titles are in English.
The filename migration is recorded in `SCOSWAMP.MORE/MUSIC/english_names.json`.
