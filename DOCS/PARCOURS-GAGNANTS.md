# SCOSWAMP — les parcours gagnants

Guide avec révélations, vérifié contre les textes français et les règles du
moteur le 6 septembre 2026. Il couvre les **trois missions**, leurs variantes
de dénouement et les sorties alternatives vivantes. Il donne un itinéraire
par mission, pas toutes les combinaisons de détours possibles dans le Marais.

| Mission | Objectif | Fin | Guide |
| --- | --- | --- | --- |
| Gayolard | Rapporter la baie d'Anthérique sans la manger | **175** | [Parcours complet](SOLUTION-GAYOLARD.md) |
| Pompatarte | Atteindre Courbensaule et rapporter l'itinéraire | **158** | [Parcours complet](SOLUTION-POMPATARTE.md) |
| Stratagus | Rapporter au moins trois amulettes et réclamer le paiement | **358** | [Parcours et variantes](SOLUTION-STRATAGUS.md) |

## Lire les itinéraires

Les nombres sont les pages du livre. Une flèche désigne le choix menant à la
page suivante ; « victoire → » signifie qu'il faut gagner un combat. Les
renvois automatiques lors d'une revisite sont indiqués entre crochets.
Lire le libellé des choix : une réponse sur le maître servi ou une rencontre
antérieure doit correspondre à l'histoire de votre partie, même quand le
moteur ne la contrôle pas.

Tous les parcours commencent par créer normalement le personnage, puis :

`419 → 1 → 95 → 240 → 205`.

À partir de 205, choisir **335 pour Gayolard**, **27 pour Pompatarte** ou
**255 pour Stratagus**. Garder l'Anneau de Cuivre : il donne accès à la carte
et avertit des dangers. Une clairière connue y est représentée par `(*)`.

Les pierres sont consommées à l'emploi. HABILETÉ et ENDURANCE restaurent la
statistique jusqu'au total initial ; elles ne rendent pas invincible. Soigner
avant un combat dangereux, pas après une blessure mortelle. Aucun itinéraire
ne garantit de gagner avec tous les tirages de personnage et de dés.

## Ce qui a été vérifié

| Vérification | Résultat |
| --- | --- |
| Gayolard, du personnage nouvellement créé à 175, clavier uniquement | Victoire dans POM2 graphique, HAB initiale 11 |
| Les trois itinéraires principaux, depuis l'accueil, en headless | **Victoires 175, 158 et 358** ; [rapport et traces](VALIDATION-PARCOURS.md) |
| Fins 175, 158 et 358 dans POM2 headless + Mockingboard | **23 assertions réussies**, depuis des sauvegardes préparées avant les fins |
| Tentatives intégrales perdues | Conservées dans le rapport ; les dés ne garantissent pas la victoire |
| Autres variantes terminales décrites ci-dessous | Vérifiées dans les textes et les instructions du moteur |

Les tests des trois fins vérifient leurs écrans, pas l'accomplissement de toute
la quête. La campagne intégrale complémentaire vérifie aussi les objectifs
et le retour. Les textes et illustrations existent pour chacune des trois fins.

Pour refaire ces contrôles sur une copie du disque, sans ouvrir de fenêtre :

```sh
sh SCOSWAMP.MORE/TOOLS/build_pom2_playtest.sh
python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --only fin_175 --only fin_158 --only fin_358 --port 6522
```

Le [guide Gayolard](SOLUTION-GAYOLARD.md#rejouer-avec-pom2-sans-fenêtre)
décrit aussi la reprise intégrale au clavier.

## Réussite, survie et faux succès

- **175** : la baie est requise et consommée (`GU BA 175`). C'est une quête
  effectivement contrôlée par l'inventaire.
- **158** : le choix `56 → 158` n'exige aucune visite de Courbensaule.
  Le raccourci décrit dans le guide Pompatarte reproduit ce défaut ; il ne
  constitue pas l'accomplissement de la mission.
- **358** : plusieurs branches y conduisent, y compris avec seulement une
  ou deux amulettes et après un paiement nul. L'écran final à lui seul ne
  prouve donc pas le respect du contrat des trois amulettes.
- **298** : tuer Stratagus puis sortir immédiatement de la tour. C'est une
  victoire contre le sorcier et une sortie vivante, mais pas la réussite de
  sa mission rémunérée. Voir les chemins dans le guide Stratagus.
- **349** : repartir vivant sans amulette après avoir échappé à sa colère.
  C'est une survie, pas une quête réussie.
- **49, 52, 100, 141, 327, 372** : abandon, échec ou fuite ; ne pas les
  compter comme des succès de mission.

Les possibilités anormales signalées ici sont documentées telles qu'elles
existent. Ce travail de documentation ne modifie pas les règles du jeu.
