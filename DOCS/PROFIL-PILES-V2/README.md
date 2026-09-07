# Piles : trace complète du pointeur C

Mesure du 6 septembre 2026 sur le même moteur et le même volume que la
validation des parcours V6. L'hôte utilisé est `pom2_playtest`, sans fenêtre
ni réglages persistants, avec HDV en slot 5 et Mockingboard en slot 2.
Le processeur instrumenté est construit dans `/tmp/scoswamp-stack-pom2`.
La réserve C de 384 octets et le jeu ne sont pas modifiés.

## Résultats headless

Processus terminé avec le code 0 ; 95 assertions passent. Les 178 101
changements du pointeur C sont continus et leur minimum est une allocation
terminée. Le détail calculé est dans `peaks.json`.

| Scénario | Assertions | Pile 6502 maximale | Pile C maximale |
|---|---:|---:|---:|
| demarrage | 18 | 58 | 82 |
| sac_combat | 26 | 58 | 81 |
| musique_aux | 10 | 57 | 82 |
| troc_alphonse | 20 | 57 | 81 |
| fin_transitions_175 | 21 | 57 | 82 |

Valeurs en octets. Le maximum C correspond à `$BEAE`, après le `DEC $80`
à `$9D1C`. Le maximum matériel correspond à SP=`$C5`. Les 302 octets entre
le pic C observé et la réserve de 384 constituent une marge sur ces essais,
pas une quantité à récupérer sans couverture supplémentaire.

L'analyse rejette également trois traces volontairement invalidées : rupture
de continuité, initialisation inattendue et minimum obtenu avec emprunt.

## Portée et preuve du pic C

La mesure matérielle commence à `$4003`, après l'initialisation de SP par
TXS, et s'arrête à l'entrée de `_exit` (`$400C`). Elle inclut désormais les
constructeurs du moteur, mais exclut toujours le lanceur SYSTEM et les
destructeurs. Tous les empilements et frontières d'instructions sont observés.

Le pointeur C MAIN `$80/$81` est suivi après chaque instruction, sans filtre
sur la banque du code exécuté. Le suivi commence à `$B289`, juste après son
initialisation à `$BF00`, et se termine également à `_exit`. Chaque changement
enregistre PC, PC suivant, valeur avant et valeur après. Les écritures sont
observées côté hôte, sans modifier la mémoire du jeu.

`analyze.py` vérifie la continuité de toutes les valeurs avant/après. Le minimum
brut borne toutes les allocations terminées, mais peut être transitoire.
Pour prouver qu'il est réellement atteint, l'analyse vérifie dans le binaire
que l'instruction qui produit ce minimum est `DEC $80`, suivie de `RTS`, avec
un octet bas initial non nul : aucune retenue ni écriture du second octet
ne reste à effectuer. Si cette preuve échoue, l'analyse échoue aussi.

Cela établit le pic exact **sur les exécutions enregistrées**, pas une limite
valable pour tous les chemins du jeu. Les scénarios utilisent des états
préparés ; ils ne constituent pas cinq parcours naturels. Les interruptions
peuvent modifier légèrement le maximum matériel d'une exécution à l'autre.

## Reproduction

Les SHA-256 du jeu, du volume, du CPU original/instrumenté et de l'exécutable
de mesure sont dans `provenance.json`. Les traces sont compressées sans perte
en `.log.gz`; les `.json` gardent les assertions et les premiers compteurs.

Appliquer `pom2-stack.patch` aux sources CPU correspondant au hash original,
puis construire le cœur et l'hôte headless :

```sh
cmake -S /tmp/scoswamp-stack-pom2 -B /tmp/scoswamp-stack-pom2/build -DPOM2_ENABLE_TESTS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/scoswamp-stack-pom2/build --target pom2_core -j 6
c++ -std=c++17 -O2 -DNDEBUG -I/tmp/scoswamp-stack-pom2/src -I/tmp/scoswamp-stack-pom2/include -I/tmp/scoswamp-stack-pom2/build/generated -I/tmp/scoswamp-stack-pom2/imgui '-DPOM2_ROOT="/tmp/scoswamp-stack-pom2"' SCOSWAMP.MORE/TOOLS/pom2_playtest.cpp /tmp/scoswamp-stack-pom2/build/libpom2_core.a -framework CoreAudio -framework AudioToolbox -framework AudioUnit -o /tmp/scoswamp-stack-pom2/build/pom2_playtest
python3 -u DOCS/PROFIL-PILES-V2/run_profile.py /tmp/nouveau-profil-piles
python3 DOCS/PROFIL-PILES-V2/analyze.py /tmp/nouveau-profil-piles
```

Le pilote vérifie les hashes du moteur, du volume et de l'exécutable avant
de lancer les scénarios. Le patch est lié aux adresses de ce binaire.
Une reconstruction avec un autre compilateur exige de revoir la provenance.

Le dossier `pilote-graphique` conserve le premier essai, effectué par erreur
avec l'exécutable graphique piloté par API. Ce n'était pas du headless.
Ces traces ne remplacent pas la campagne headless à la racine du dossier.
