# Récompenses d'épées magiques

Contrats lus dans les textes et enregistrés dans l'audit bilingue :

| Page | Objet | Bonus de combat annoncé | Autre effet |
|---|---|---|---|
| 241 | EP | +1 | Chance restaurée au maximum |
| 140 | EP | +2 | aucun |
| 340 | EP | +2 | aucun |

Le scénario POM2 `epees_recompenses` part d'un héros sans épée ni bonus et
avec une Chance diminuée. Il vérifie les trois acquisitions, le retour du
sac et la sauvegarde/reprise sur chacune des pages. Il ne s'agit pas de
combats complets contre Stratagus.

Le cas de réacquisition a ensuite été reproduit : après un paiement PO en
407 avec une épée +2, l'acquisition en 241 donnait +2 au lieu du +1 annoncé.
Le test transporte le bonus constaté après la perte vers une fixture de
l'acquisition ; ce n'est pas la preuve d'un itinéraire narratif complet entre
ces deux pages.

Correction native et JavaScript : `G EP` commence une nouvelle acquisition
et remet le bonus à zéro ; le `E BONUS` suivant définit la puissance de cette
arme. Les dons d'autres objets et d'amulettes n'y touchent pas. La restauration
ignore les effets G/E et préserve donc le bonus sauvegardé. Le bonus résiduel
sans objet reste sans effet au combat et devient inoffensif à la réacquisition,
y compris pour les anciennes sauvegardes.

Dans le parseur natif, l'indice objet/amulette utilise un octet, suffisant pour
les indices et leurs sentinelles. Cela compense une partie du coût de la
correction : marge finale 2059 octets, contre 2065 avant correction. Pile C
384 octets et format de sauvegarde inchangés. Ce n'est pas encore le gain
mémoire significatif visé par l'objectif global.

Commandes :

- `python3 SCOSWAMP.MORE/TOOLS/audit_contracts.py --output DOCS/CONTRATS-EPEES.json`
- `python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --port 6527 --only epees_recompenses`

Le registre compte 102 paragraphes revus, avec zéro divergence de mécanique
FR/EN sur 842 textes. La correction de réacquisition décrite ci-dessus modifie le parseur G.

Résultat natif : 18 assertions réussies, zéro échec, POM2 headless avec
Mockingboard.

Test JavaScript complémentaire : `node tools/test_weapon_replacement.mjs`,
36 acquisitions FR/EN, bonus antérieur 0/1/2, objet présent/absent, restauration
et dons non concernés.

Validation finale de la correction : 55 assertions POM2 réussies, zéro échec
(7 remplacement, 18 récompenses, 7 chaîne du nid, 23 contrats des Jardins),
avec Mockingboard. Vérificateurs FR/EN sans erreur.
