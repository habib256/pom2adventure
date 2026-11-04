# Repères de travail

Ce dépôt contient deux jeux Apple II et leur atelier commun. Lire le
[README](README.md) pour l'arborescence, [TODO](TODO.md) pour les chantiers.

- `SCOSWAMP/` et `SPACETRIP/` portent les données livrées et les moteurs.
- Leurs dossiers `.MORE/` portent les sources artistiques et outils propres
  au jeu ; `ADVKIT/` porte l'atelier, les outils et tests communs.
- Les volumes de `dist/` sont reconstruits : une modification de l'arbre
  n'apparaît dans l'atelier en mode volume qu'après empaquetage.

## Vérifier une modification

Le [harnais](ADVKIT/TESTS/README.md) décrit les suites et leurs dépendances.
`python3 ADVKIT/TESTS/run.py` lance les tests autonomes Python, Node et C.
Choisir une suite ciblée pendant le travail ; `--list` donne les autres.
Les suites HTTP, Chrome et POM2 ont leurs propres prérequis explicites.
Ne pas présenter un test non exécuté ou un contrôle ignoré comme réussi.

Pour les moteurs Apple II, conserver les contrôles mémoire du Makefile et
reconstruire le volume avant un playtest. Les adresses du banc dépendent des
symboles du binaire courant ; voir [AUTOMATISATION](SCOSWAMP/DOCS/AUTOMATISATION.md).

Pour l'évolution du banc et les optimisations Apple II, consulter les outils
et contrats de `../pom2games/dev/` : `a2shot`, `a2test.py`, `lib/ABI.md` et
`bench/`. Préférer le SDK public POM2 aux en-têtes internes. Le SDK monte nos
volumes : la suite `a2shot` du harnais les joue et `playtest.py --host a2shot`
y rejoue le banc. L'hôte HTTP reste celui de l'émulateur POM2 complet ; les deux
doivent rester au vert (voir [le harnais](ADVKIT/TESTS/README.md)).
Mesurer les primitives dans notre moteur avant de reprendre une optimisation.

## Travail sur les images

Lire [ADVKIT/IMAGES.md](ADVKIT/IMAGES.md) avant une retouche du pipeline.
Distinguer les masters `GENERATED/`, les références suivies `REF/`, les
recettes `IMAGE-RECIPES/`, les flux livrés et les aperçus régénérables.
Les masters et aperçus sont ignorés par Git : vérifier leur présence avant
une comparaison et préserver les originaux lors d'une révision.
L'utilisateur est seul juge de la qualité visuelle. Son poste de revue est
l'interface web : sélection, cadrage, réglages, régénération et comparaison.
Le harnais vérifie le fonctionnement de ces outils et l'intégrité des fichiers.
Les métriques sont indicatives ; ne pas en déduire une validation artistique,
un rejet ou une liste d'images à refaire. Préparer les comparaisons et appliquer
les décisions de l'utilisateur, sans se substituer à son jugement.
