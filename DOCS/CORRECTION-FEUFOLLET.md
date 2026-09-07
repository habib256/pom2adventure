# Contrat du piège du Feu Follet — N024

Le texte FR/EN indique explicitement que les deux issues permettent de sortir
et de retrouver la clairière ; l'échec coûte deux points d'ENDURANCE.
Pourtant `CL 273 297 0 -2` envoyait le joueur vers une fuite de la tour de
Stratagus, voire une mort par tapis volant, sans rapport avec cette rencontre.

Le chemin d'entrée est `218 → 072 → 024`. Les pages 218 et 249 décrivent
les sorties sud (336) et est (121) de cette clairière. La correction repose
sur ces textes du projet : `CE ENDURANCE 0 -2`, puis ces deux sorties.
Elle évite de passer par 249, qui provoquerait un second test, cette fois
sur l'HABILETE. Le joueur conserve le choix de sa direction ; le moteur
résout le test et ses dégâts.

La page 024 utilise désormais WILLOWISP.MB et appartient au groupe 218
sur la carte. Son ancienne affectation au rond-point 058 contredisait
le chemin d'entrée et la sortie décrite dans le texte. Le voisin ouest
fictif 058 a été retiré ; le sentier du leurre 072 reste présent.

Contrôles reproductibles :

- `node tools/test_visible_luck.mjs` : cinq pages CE, FR/EN, Chance 0/12,
  jet différé, coût et restauration sans répétition.
- `python3 SCOSWAMP.MORE/TOOLS/audit_contracts.py --output DOCS/CONTRATS-FEUFOLLET.json` :
  842 textes, 73 contrats explicitement revus, zéro erreur.
- `node SCOSWAMP.MORE/TOOLS/interpreter/verifier.js project.scoswamp.json FR`
  et même commande EN : 421 pages par langue, sans lien cassé, page
  inaccessible ou différence entre disque et dépôt.
- `python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --port 6527 --only chance_effet_visible --only feufollet_parcours` :
  tests natifs des résultats, sac, sauvegarde, deux sorties et dégâts mortels.

Ces parcours natifs partent d'un état contrôlé à la rencontre ; ils ne sont
pas des parties complètes depuis la création du héros. Cette correction
modifie les données et la carte, sans ajout de code moteur. Le build conserve
2065 octets de marge de tas et 384 octets de réserve de pile C.

Résultat POM2 headless avec Mockingboard : **124 assertions réussies, zéro
échec** (111 pour les cinq pages CE, 13 pour le parcours du Feu Follet).
