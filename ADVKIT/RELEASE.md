# Images disque : `dist/`

`dist/` reçoit les images des deux jeux. Rien n'y est suivi par Git : ce sont
des artefacts, reconstruits à l'identique depuis le dépôt.

| Fichier | Produit par | Rôle |
|---|---|---|
| `dist/SCOSWAMP.2mg` | `make -C SCOSWAMP/SRC hdv` | l'image que télécharge un joueur |
| `dist/SCOSWAMP.HDV` | la même commande | l'image de travail : POM2, `make playtest`, l'atelier |
| `dist/SPACETRIP.2mg` | `python3 SPACETRIP/build_disk.py` | l'image que télécharge un joueur |
| `dist/SPACETRIP.hdv` | la même commande | l'image de travail |

Le `.2mg` porte exactement les mêmes blocs ProDOS que l'image de travail,
précédés des 64 octets d'en-tête 2IMG écrits par `ADVKIT/TOOLS/wrap_2mg.py` :
plusieurs émulateurs refusent de deviner la géométrie d'un `.hdv` d'après sa
taille. Les volumes eux-mêmes sortent de `ADVKIT/TOOLS/build_prodos_volume`
(avec l'amorce `ADVKIT/TOOLS/prodos_boot.tmpl`), que `make hdv` construit par
cmake au premier passage.

Le volume ne porte que ce que le joueur lit : `make hdv` écarte `SRC/`,
`DOCS/`, `BASIC.SYSTEM` et `STARTUP.BAS` (`STAGE_EXCLUDE` dans le Makefile).

## Pourquoi pas dans Git

Git garde chaque version d'un binaire en entier, pour toujours : une image
de quelques Mo commitée à chaque mise à jour fait enfler l'historique de
façon définitive, sans aucun diff lisible, et peut diverger en silence des
sources du même commit. Les images sont donc publiées en **GitHub Release**,
faite pour les binaires versionnés par tag.

## Publier une version

1. Vérifier le dépôt : `./check-project.sh`.
2. Construire les deux jeux :
   ```bash
   make -C SCOSWAMP/SRC hdv
   python3 SPACETRIP/build_disk.py
   ```
3. Monter chaque `.2mg` dans un émulateur et vérifier : le disque démarre et
   lance le jeu, le choix de langue (`F` / `E`) fonctionne, la première page
   affiche son texte et son image, `ESPACE` bascule image et texte, un choix
   mène à la page attendue.
4. Poser le tag et publier :
   ```bash
   git tag -a v1.0 -m "SCOSWAMP et SPACETRIP 1.0"
   git push origin v1.0
   ```
   Sur GitHub, **Releases → Draft a new release**, choisir le tag et joindre
   `dist/SCOSWAMP.2mg` et `dist/SPACETRIP.2mg`. Le numéro de version vit dans
   le tag, pas dans le nom des fichiers.

Indiquer dans la description la configuration requise : Apple IIe Enhanced
(65C02), 64 Ko, carte 80 colonnes, ProDOS 8.
