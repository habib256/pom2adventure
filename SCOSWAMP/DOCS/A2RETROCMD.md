# A2 Retro Cmd sur le disque du jeu

Le gestionnaire de fichiers à deux panneaux est né dans ce dépôt sous le nom
d'*Apple IIe Total Commander*. Il s'appelle maintenant **A2 Retro Cmd** et vit
chez lui, avec ses sources, ses bancs, son intégration continue et ses
publications :

> **<https://github.com/habib256/a2retrocmd>**

Le jeu n'en est plus le conteneur — il en est **l'hôte et la démonstration
d'intégration** : il l'embarque tel qu'il est publié, et le propose par la
touche **[T]** de l'écran-titre.

## Ce qui reste ici

`SCOSWAMP/A2RETRO/` — quatre fichiers, tirés de l'image de disquette d'une
Release, et le `PROVENANCE.txt` qui dit d'où ils viennent :

| Fichier | |
|---|---|
| `A2RETRO.SYSTEM` | le lanceur ; `launch()` de `scoswamp.c` le lit en `$2000` et y saute |
| `A2RETRO.CODE` | le programme, que le lanceur charge à ses trois adresses |
| `A2RETRO.HELP` | sa page d'aide, lue depuis le disque |
| `FORMAT.SYS` | le formateur de disques, que sa touche F lance |

Rien n'est compilé ici : `make hdv` copie ce dossier sur le volume comme le
reste de `SCOSWAMP/`. Le préfixe ProDOS étant `/SCOSWAMP` quand le jeu passe
la main, le lanceur ouvre `A2RETRO/A2RETRO.CODE` en relatif et trouve son
compte ; A2 Retro Cmd s'ouvre alors sur le volume du jeu, et écrit ses
préférences dans `A2RETRO/A2RETRO.CFG` à côté.

## Rafraîchir la copie

```sh
python3 tools/update_a2retrocmd.py            # la dernière Release
python3 tools/update_a2retrocmd.py --tag v1.1 # une version précise
python3 tools/update_a2retrocmd.py --from /chemin/A2RETROCMD.po
make -C SCOSWAMP/SRC hdv
```

L'outil télécharge l'image `.po` publiée, y lit les quatre fichiers par le
catalogue ProDOS, les écrit dans `SCOSWAMP/A2RETRO/` et note dans
`PROVENANCE.txt` l'URL, l'empreinte SHA-256 de l'image et celle de chaque
fichier. C'est la seule dépendance du jeu envers l'autre projet : une image
publique et vérifiable, pas un chemin de compilation.

## Ce qui est parti

Les sources (`total.c`, `total_mli.s`, `total.cfg`, le formateur, `chain.s`),
la disquette dédiée, les bancs `DOCS/VALIDATION-TOTAL/` et le manuel
`DOCS/TOTAL.md` ont suivi le programme, avec l'historique Git de chacun de ces
fichiers. Le `Makefile` du jeu n'a plus ni cible `total` ni cible `floppy`, et
`loader.c` a perdu sa variante : il ne sert plus qu'au jeu et à DIAPO.
