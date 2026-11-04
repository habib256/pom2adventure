# Harnais du dépôt

Le point d'entrée est `python3 ADVKIT/TESTS/run.py`. Le lanceur se replace à
la racine du dépôt ; les anciens scripts restent exécutables directement.
Les tests restent près de leur domaine, sans déplacement de leurs imports.

```sh
python3 ADVKIT/TESTS/run.py --list
python3 ADVKIT/TESTS/run.py                         # quick : Python + Node + C
python3 ADVKIT/TESTS/run.py node python             # sélection, sans doublons
python3 ADVKIT/TESTS/run.py all --dry-run           # commandes, sans écriture
python3 ADVKIT/TESTS/run.py quick --report dist/checks/quick.json
```

| Suite | Contenu | Prérequis |
| --- | --- | --- |
| `python` | outils SCOSWAMP, mémoire/LC, musique, lanceur | Python 3.9+ et Bash |
| `node` | règles, scènes, choix, sauvegardes ADVKIT | Node 20+ ; aucun serveur |
| `native` | règles C, décodeur RLE, analyseur SPACETRIP | CMake, compilateur C/C++ ; aucun POM2 ou cc65 |
| `images` | métriques, conversion HGR/DHGR, recettes, avis, sauvegarde atelier et volume ProDOS | Python avec NumPy/Pillow, CMake, C++, sources POM2 |
| `integrity` | données des deux jeux, binaires et images présents | Bash ; contrôles natifs selon outils construits |
| `http` | données FR/EN et contenu du volume | serveur atelier sur 8765, `dist/SCOSWAMP.HDV` à jour |
| `browser` | interaction avec l'atelier | serveur 8765, Chrome CDP sur 9228, Node avec `--experimental-websocket` |
| `a2shot` | volumes livrés : amorçage, jeu, sauvegarde, reprise, protection | `a2shot` construit dans `../pom2games` (ou `$A2SHOT`), volumes de `dist/` à jour |

`quick` regroupe `python node native`. `all` ajoute `images integrity`.
Les suites HTTP, navigateur et `a2shot` se lancent explicitement, après
préparation de leurs services ou outils. Les tests nommés `test_browser_saves.mjs`, par exemple, sont
des tests Node autonomes : leur nom ne signifie pas qu'ils ouvrent Chrome.

Un échec rend le code **1**, y compris une dépendance absente ou un délai
dépassé (`--timeout`, 300 secondes par commande). Les autres tests continuent ;
un prérequis en échec arrête sa suite. Le rapport JSON conserve les commandes,
durées et codes de sortie ; les détails des assertions restent dans le terminal.
Un bilan réussi porte sur les suites sélectionnées, pas sur une validation
visuelle ou un parcours Apple II. `check-project.sh` conserve ses avertissements
quand un contrôle optionnel n'est pas disponible.

## Images et dépendances

Choisir explicitement le Python qui possède NumPy et Pillow : le lanceur
réutilise son propre interpréteur pour tous les scripts Python.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r ADVKIT/TESTS/requirements-images.txt
.venv/bin/python ADVKIT/TESTS/run.py images --report dist/checks/images.json
```

Avec un Python déjà équipé, utiliser directement cet interpréteur. Les sources
POM2 sont cherchées dans `../pom2/src` sur une configuration neuve ; fournir
`--pom2-src /chemin/vers/pom2/src` pour un autre emplacement. Un cache CMake
existant conserve sa valeur. La suite images reconstruit les deux convertisseurs et `build_prodos_volume`
dans `ADVKIT/TOOLS/build` avant les tests, pour éviter leurs exclusions conditionnelles
sur un clone neuf. La suite C utilise un dossier séparé `ADVKIT/TOOLS/build-host`.

L'utilisateur mène la revue des illustrations dans l'atelier web et décide
de leur qualité : voir [le parcours images](../IMAGES.md#préparer-une-revue-détaillée).
Le harnais valide les outils de cette revue, sans porter de jugement visuel.
Les tests d'images utilisent des projets temporaires et une génération simulée.
Le harnais ne lance pas de génération de masters.

## Intégration et machine émulée

```sh
make -C SCOSWAMP/SRC hdv
python3 ADVKIT/image_workshop.py --port 8765   # garder ce serveur ouvert
# Dans un autre terminal :
python3 ADVKIT/TESTS/run.py http
# Avec Chrome CDP déjà disponible sur 9228 :
python3 ADVKIT/TESTS/run.py browser

make -C SCOSWAMP/SRC playtest PLAYTEST=--list
make -C SCOSWAMP/SRC playtest PLAYTEST="--only combat"
```

`http` actualise le rapport historique
`SCOSWAMP/DOCS/VALIDATION-DIAPO-MUSIC/layout.json`. `browser` utilise N998
temporairement et écrit une capture dans `/tmp/scoswamp-studio-tested.png`.
Le banc POM2 reste piloté par `make playtest`, qui reconstruit le volume et
ses symboles ensemble. Voir [AUTOMATISATION](../../SCOSWAMP/DOCS/AUTOMATISATION.md).

Le SDK public POM2 monte maintenant nos disques durs : `a2shot` y amorce le
volume complet, sans réduire le jeu. La suite `a2shot` joue le scénario de la
[lettre à POM2](../../SCOSWAMP/DOCS/LETTRE-POM2-SDK-HDD.md) sur une copie privée :

```sh
make -C ../pom2games/dev/tools/a2shot
python3 ADVKIT/TESTS/run.py a2shot
```

Le banc de traversée a deux hôtes, qui rejouent les mêmes scénarios :

- `--host http` (défaut) pilote l'émulateur par son serveur local. Il valide le
  jeu sur POM2 complet avec `--pom2 ../pom2/build/POM2`. `pom2_playtest` en est
  la variante sans fenêtre, reconstruite par `ADVKIT/TOOLS/build_pom2_playtest.sh`.
- `--host a2shot` passe par le SDK public, sans fenêtre ni serveur, en cycles et
  non en temps d'horloge. C'est le chemin des tests SDK de `pom2games`.

L'émulateur complet traite `--speed` comme un accélérateur : le 6522 de la
Mockingboard reste à 1 MHz et la détection du jeu échoue. Le banc y démarre donc
à 1x, n'accélère qu'une fois la carte trouvée et allonge ses silences : il dure
bien plus longtemps que `pom2_playtest`. Les captures du SDK restent des
preuves techniques : `renderFrame` n'est pas le rendu CRT de l'atelier ni celui
du joueur (`docs/SDK.md` de POM2, § Rendering).

Les convertisseurs se construisent sans sources POM2 à partir du paquet
`pom2_imageconv` : `cmake -S ADVKIT/TOOLS -B ADVKIT/TOOLS/build
-DPOM2_SDK_PREFIX=/chemin/du/sdk`. `build_prodos_volume` n'en fait pas partie :
il reste construit depuis `POM2_SRC`, et omis si ces sources sont absentes.

## Ajouter un contrôle

- Tests Python d'outils SCOSWAMP : `SCOSWAMP.MORE/TOOLS/test_*.py` ; musique :
  `SCOSWAMP.MORE/MUSIC/test_*.py`.
- Tests communs Python : ici, `test_*.py` ; réserver `test_image_*.py` aux
  contrôles avec les dépendances images.
- Tests Node autonomes : ici, `test_*.mjs`. Déclarer explicitement un nouveau
  test dépendant d'un service dans `run.py`, pour l'exclure de `node`.
- Tests C : les déclarer dans `ADVKIT/TOOLS/CMakeLists.txt` hors du bloc
  `ADVKIT_BUILD_TOOLS` ; CTest les reprend dans `native`.

La découverte est triée et chaque script s'exécute dans un processus distinct.
Conserver un code de sortie non nul en cas d'échec et des fixtures temporaires.
