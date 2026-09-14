# Chaîne des images DHGR SCSWAMP

Les descriptions canoniques viennent du livre et sont consolidées dans
`characters.json`, `monsters.json`, `decors.json` et `objects.json`. Ces bibles
sont la source de vérité pour l'apparence des personnages, monstres, décors et
objets récurrents.

## Fichiers suivis

- `SCOSWAMP.MORE/REF/*.png` : références visuelles canoniques.
- `SCOSWAMP.MORE/ref_manifest.jsonl` : prompts des références.
- `SCOSWAMP.MORE/scene_manifest.jsonl` : prompts des scènes numérotées.
- `SCOSWAMP.MORE/battle_manifest.jsonl` : prompts des combats.
- `SCOSWAMP/IMG/` : images DHGR compressées intégrées au jeu (banque auxiliaire
  de 8 Ko, puis banque principale de 8 Ko).

Les manifestes sont suivis afin que toute modification des règles visuelles
soit relue comme du code. `GENERATED`, `HGR-PREVIEW`,
`CHATMAUVE-PREVIEW`, les WAV et les répertoires de build sont des sorties
temporaires ignorées par Git.

## Régénération

```sh
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . --output SCOSWAMP.MORE/ref_manifest.jsonl --refs
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . --output SCOSWAMP.MORE/scene_manifest.jsonl --all
python3 SCOSWAMP.MORE/TOOLS/build_manifest.py --root . --output SCOSWAMP.MORE/battle_manifest.jsonl --battle
SCOSWAMP.MORE/TOOLS/generate_images.sh SCOSWAMP.MORE/scene_manifest.jsonl 0 3
SCOSWAMP.MORE/TOOLS/generate_images.sh SCOSWAMP.MORE/battle_manifest.jsonl 0 3
SCOSWAMP.MORE/TOOLS/convert_images.sh
```

La génération emploie exclusivement les quinze teintes distinctes de la
palette DHGR Apple II. La conversion cible 140×192 pixels couleur, sans
dégradés ni teintes hors palette, et produit deux aperçus : `HGR-PREVIEW`
montre la palette composite, `CHATMAUVE-PREVIEW` la palette Péritel Féline.
Les indices gris 5 et 10 sont identiques en composite mais olive et mauve sur
Le Chat Mauve : aucun contour important ne doit donc dépendre d'un gris précis.

Dans les scènes narratives, le héros doit être présent et mis en valeur. Dans
les combats seulement, il est à gauche, tourné vers la droite, face à son
adversaire placé à droite et regardant vers la gauche.

## Musique

Dans le Marais, une musique de lieu est lancée uniquement quand la page fait
entrer le joueur dans une nouvelle clairière. Hors clairières, les directives
MU lancent les morceaux scénarisés de l'accueil, du village, du prologue et des
fins. Ces morceaux sont joués une seule fois. `COMBAT.MB` est l'unique
exception : il boucle pendant l'action et s'arrête dès la victoire, la fuite ou
la mort.
