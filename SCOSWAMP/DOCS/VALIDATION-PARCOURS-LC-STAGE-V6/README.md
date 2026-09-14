# Parcours complets V6 — chargement Language Card en RAM basse

Campagne terminée avec le code 0 : trois victoires et cinq défaites archivées.
POM2 headless, Mockingboard slot 2. Le pilote modifie le jeu uniquement par
le clavier ; les personnages sont tirés par le jeu, sans injection de héros.

| Mission | Tentative gagnante | Fin | Durée | Touches |
|---|---:|---:|---:|---:|
| [gayolard](gayolard-06.json) | 6 | 175 | 60.6 s | 134 |
| [pompatarte](pompatarte-01.json) | 1 | 158 | 54.9 s | 121 |
| [stratagus](stratagus-01.json) | 1 | 358 | 49.8 s | 110 |

SHA-256 du volume testé, identique au HDV actuel : `81b14116bff5058631d29f606f52a3de48d0c88f14f537fd42ddd861f5405bb1`.

Ce volume comprend le préfixe LC de 3 072 octets transitoirement chargé en
RAM basse, la condition CB des biens payables, les corrections des sorts et
des Orques. Les tests structuraux de ces règles restent distincts : les trois
itinéraires ne passent pas par tous les embranchements.

Les JSON contiennent chaque touche, les états du héros, le tirage initial,
les paragraphes et la capture finale ; les fichiers `.log` gardent les traces
POM2. La présence des commandes après les fins ne prouve pas leur activation
dans ces parcours ; les tests ciblés de sortie/reprise documentent ce point.

## Tentatives conservées

| Rapport | Résultat | HAB/END/CHA initiales | État RNG initial |
|---|---|---|---|
| [gayolard-01](gayolard-01.json) | lost | 7/17/7 | `d5ec0000` |
| [gayolard-02](gayolard-02.json) | lost | 8/21/9 | `e52b0000` |
| [gayolard-03](gayolard-03.json) | lost | 8/16/12 | `018e0000` |
| [gayolard-04](gayolard-04.json) | lost | 7/20/11 | `12c50000` |
| [gayolard-05](gayolard-05.json) | lost | 7/16/9 | `ae290000` |
| [gayolard-06](gayolard-06.json) | success | 8/18/9 | `55b90000` |
| [pompatarte-01](pompatarte-01.json) | success | 10/19/11 | `49c70000` |
| [stratagus-01](stratagus-01.json) | success | 10/19/11 | `49c70000` |

Le pilote s’arrête au premier succès de chaque mission : ces résultats ne
sont pas une estimation statistique du taux de victoire. Les cinq pertes
de Gayolard sont des morts au combat contre les Arbres-Epées (028).

Mesure associée : [MEMOIRE-LC-STAGE.json](../MEMOIRE-LC-STAGE.json).
La campagne vérifie le déroulement réel avec musique et chargements ; elle
ne mesure pas le pic des piles C ou 6502.
