# Première mesure des piles dans POM2

Le processus de mesure est terminé avec le code 0. Les cinq scénarios
passent leurs 95 assertions. Le jeu et le HDV restent ceux de V6 ; seule
une copie de POM2 sous `/tmp/scoswamp-stack-pom2` est instrumentée.

| Scénario | Assertions | Pile 6502 maximale observée | Pile C aux appels MAIN |
|---|---:|---:|---:|
| [demarrage](demarrage.json) | 18 | 58 octets | 82 octets |
| [sac_combat](sac_combat.json) | 26 | 58 octets | 81 octets |
| [musique_aux](musique_aux.json) | 10 | 59 octets | 82 octets |
| [troc_alphonse](troc_alphonse.json) | 20 | 57 octets | 81 octets |
| [fin_transitions_175](fin_transitions_175.json) | 21 | 57 octets | 82 octets |

## Ce que mesure la sonde

La pile matérielle est observée avant chaque instruction et après chaque
décrément de son pointeur dans les opérations d’empilement. Elle inclut les
appels ROM/ProDOS et les IRQ exécutés pendant la période armée. La mesure
commence à l’entrée de `_main` ($80F3) et s’arrête à `_exit` ($400C).
Elle exclut donc le lanceur et les constructeurs précédant main.

Le maximum de 59 octets correspond à SP=$C4, soit les octets occupés
MAIN $01C5-$01FF. C’est le maximum sur ces cinq exécutions, pas une garantie
pour tous les chemins du jeu. Les scénarios utilisent leurs préparations
habituelles, dont des états injectés ; ce ne sont pas cinq parcours naturels.

Pour la pile C, la sonde lit le pointeur cc65 $80/$81 uniquement aux
instructions JSR de la zone MAIN $4000-$B347. Les lectures se font avant
l’appel. Le maximum relevé est 82 octets (SP=$BEAE), mais cette observation
ne couvre pas toutes les allocations entre appels ni les appels depuis LC.
**82 est une borne observée, pas le pic exact de la pile C.** La réserve de
384 octets est conservée ; aucune réduction n’est justifiée par ce seul chiffre.

Les écritures des deux octets du pointeur C sont séparées : les lire à
chaque instruction pourrait produire des valeurs transitoires incohérentes.
Cette première sonde évite de présenter un tel minimum brut comme un pic.

## Reproduction et preuves

`pom2-stack.patch` contient toute la modification du CPU. `provenance.json`
identifie les sources CPU avant/après, le binaire instrumenté, le jeu et le
HDV par SHA-256. Chaque `.log` contient les nouveaux minima et leur PC.
La journalisation s’exécute côté hôte et ne modifie pas la RAM invitée.

Sur une copie des sources POM2 dont M6502.cpp correspond au hash original,
appliquer le patch, puis construire :

```sh
cmake -S /tmp/scoswamp-stack-pom2 -B /tmp/scoswamp-stack-pom2/build -DPOM2_ENABLE_TESTS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/scoswamp-stack-pom2/build --target POM2 -j 6
python3 -u DOCS/PROFIL-PILES-V1/run_profile.py /tmp/nouveau-profil-piles
```

Le pilote vérifie le hash du jeu et les points d’armement avant de démarrer.
Il refuse de réécrire un dossier qui contient des traces. Le patch est lié
aux adresses de ce binaire ; il faut le régénérer pour un autre placement.

Restent à mesurer : le pic exact C, le démarrage avant main, et une couverture
plus large des parcours et des branches. L’émulateur installé est inchangé.
