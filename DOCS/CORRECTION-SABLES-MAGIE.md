# Traversée magique des Sables Mouvants

Défaut reproduit : N382 proposait `C 270 Utiliser une Pierre de Magie`, même
avec un sac vide, sans dépenser de Pierre. Le texte FR/EN décrit pourtant
Glace (passage temporaire) et Croissance (sentier permanent).

Correction préparée :

- `CU GLACE 270` : exige et consomme une Pierre de Glace.
- `CU CROISSANCE 421` : exige et consomme une Pierre de Croissance.
- N421 FR/EN confirme la création du sentier ; `VR 270 421` en N382 permet
  ensuite de traverser directement, sans nouveau coût ni test de Chance.
- N421 appartient à la clairière 270 sur la carte. La table passe de 115 à
  116 paires, soit deux octets supplémentaires en RAM basse. Le générateur
  calcule la longueur de table au lieu d'exiger 355 octets en dur.
- Le bitmap moteur possède déjà 53 octets et accepte N421. Le banc de test
  n'en préparait que 52 : son générateur `scene_bits` a été aligné sur 53.

État de validation :

- Défaut initial reproduit dans POM2, choix magique disponible sans Pierre.
- Premier test après correction : conditions, consommation, sauvegarde de
  N421 et retour vers N270 passent ; l'injection de l'historique 421 échouait
  dans le banc à cause de sa limite de 52 octets, corrigée depuis.
- Règle de revisite JavaScript validée FR/EN, entrée et restauration.
- Audit mécanique : 844 textes, 120 contrats enregistrés, zéro erreur.
- Validation native initialement interrompue, puis reprise avec succès ci-dessous.
  Une modification simultanée des extensions et une recompilation ont
  désynchronisé build.lbl et le disque pendant le dernier essai. Ce résultat
  est invalide et ne doit pas être attribué au comportement du jeu.

Commande à reprendre sur un disque et des symboles issus du même build :
`python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --port 6526 --only sables_magie`.

La dernière marge mesurée lors du build de cette correction, avant les
modifications simultanées, était de 2051 octets ; LOWBSS occupait 4072 octets.
Les changements ultérieurs doivent être mesurés sur leur propre build.

## Validation finale

POM2 headless avec Mockingboard : 41 assertions réussies, zéro échec
(17 pour les Sables, 24 pour le retour de carte DHGR). Le passage permanent
est atteint depuis 041 via 382 sans Pierre, dégâts ni dépense de Chance.
La consommation, la sauvegarde de 421 et la reprise ont également passé.
Les vérificateurs FR/EN lisent 422 pages chacun sans anomalie.

Pour contourner la génération DIAPO en cours de migration, le catalogue
existant a été comparé exhaustivement aux 453 images DHRR .BIN présentes :
ordre, chemins et signatures exacts. `make -C SCOSWAMP/SRC -o diapo-catalog hdv`
a ensuite reconstruit le disque en conservant ce catalogue validé, avec tous
les contrôles mémoire habituels. Le disque et SRC ont été copiés ensemble
sous /tmp/scos-sables-coherent avant le test, pour éviter de mélanger de
nouveaux symboles avec un ancien disque.

La migration indépendante vers les images exécutables .SYS n'est pas validée
par ce test ; la commande de build standard demande encore un catalogue
compatible avec les extensions réellement présentes.
