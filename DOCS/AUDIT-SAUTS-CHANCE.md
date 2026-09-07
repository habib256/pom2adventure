# Audit des branches de Chance et des sauts

Lecture comparée des paragraphes FR et de leurs directives communes FR/EN.
Les contrats suivants sont maintenant enregistrés dans `audit_contracts.py`.
Il s'agit d'une revue ciblée, pas d'une preuve de l'intégralité du récit.

| Test | Issue favorable | Issue défavorable |
|---|---|---|
| 029 | 185 : mensonge cru par le Patrouilleur | 378 : combat |
| 083 | 035 : aimant, blessure de 1 END | 357 : blessure de 5 END |
| 086 | 189 : pierres Amitié et Chance | 348 : départ sans récompense |
| 118 | 070 : possibilité de réagir aux scorpions | 182 : perte de 1d6 END |
| 147 | 213 : piège du voleur évité | 106 : perte de 2 END |
| 231 | 018 : fuite des brigands | 259 : combat annoncé |
| 296 | 272 : retour au village, perte supplémentaire de 2 CHANCE | 003 : mort dans le marais |
| 315 | 051 : fuite de la tour | 401 : capture mortelle |
| 359 | 162 : mensonge cru par le Maître | 016 : mensonge soupçonné |

La perte supplémentaire de Chance en 272 est explicitement annoncée par le
texte : elle s'ajoute au coût du test en 296. Ce n'est pas un double débit
accidentel du même test.

Trois sauts utilisent CS et non CL : ils comparent 2d6 à la caractéristique
courante sans coût de Chance.

| Page | Seuil | Réussite | Échec |
|---|---|---|---|
| 091 | ENDURANCE | 404, aucun dégât | 405, -1 HABILETÉ |
| 257 | HABILETÉ | 403, +2 CHANCE plafonnée au maximum | 311, -2 HABILETÉ |
| 377 | ENDURANCE | 319, aucun dégât | 406, -3 ENDURANCE, mort si épuisée |

Le scénario natif `sauts_contrats` force un seuil de 12 ou 1 : l'issue est
certaine quel que soit le jet, sans remplacer le mécanisme aléatoire. Il
vérifie les six destinations, les trois caractéristiques, les retours du sac,
les sauvegardes des survivants et l'issue mortelle. Il part de fixtures locales,
pas d'une partie complète. Les neuf tests CL du tableau sont ici revus dans
les sources ; ce scénario ne prétend pas les avoir tous exécutés.

Commandes :

- `python3 SCOSWAMP.MORE/TOOLS/audit_contracts.py --output DOCS/CONTRATS-SAUTS-CHANCE.json`
- `python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --port 6527 --only sauts_contrats`

Le registre contient 94 paragraphes revus et compare 842 textes FR/EN : zéro
erreur. Aucun changement du moteur ou du disque n'est nécessaire pour ce lot.

Le premier passage du test attendait trop tôt le message de mort : les effets
E mortels laissent lire le paragraphe avant acquittement. Le test respecte
désormais cette étape et vérifie que la touche du choix de sortie déclenche
la mort, sans atteindre 319. Aucun changement de comportement moteur.

Résultat final : **53 assertions réussies, zéro échec**, dans POM2 headless
avec Mockingboard.
