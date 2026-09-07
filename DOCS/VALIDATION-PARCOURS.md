# Validation intégrale dans POM2 — 6 septembre 2026

**Les trois itinéraires principaux ont été gagnés de bout en bout**, dans
POM2 headless, Apple IIe Enhanced, Mockingboard en slot 2, HDV en slot 5.
Chaque partie commence à l'accueil, crée son personnage normalement et
progresse uniquement au clavier. Aucune sauvegarde préparée, téléportation,
modification de statistiques ou injection de graine aléatoire.

## Résultats

Les trois parties gagnées ont tiré naturellement **HAB 11, END 21, CHA 11**.

| Mission | Fin | HAB / END / CHA finales | Or final | Durée | Trace complète |
| --- | --- | --- | --- | --- | --- |
| Gayolard | **175** | **11 / 12 / 7** | 20 | 57,9 s | [Touches et états](VALIDATION-PARCOURS/lot-3-gayolard-03.json) |
| Pompatarte | **158** | **11 / 10 / 7** | 20 | 57,1 s | [Touches et états](VALIDATION-PARCOURS/lot-2-pompatarte-01.json) |
| Stratagus | **358** | **11 / 4 / 8** | **1 520** | 49,1 s | [Touches et états](VALIDATION-PARCOURS/lot-4-stratagus-01.json) |

Le pilote vérifie à chaque fin la page, le texte de succès, l'absence de
choix narratifs et la Mockingboard détectée. Il contrôle aussi les objectifs :

- **Gayolard** : baie acquise au cours de la partie, présente avant la remise
  en 175 puis consommée ; musique `VICTOIRE.MB` active.
- **Pompatarte** : arrivée effective en **280**, nuit en **78**, retour
  complet au village puis 56 → 158 ; musique `VICTOIRE.MB` active. Le duel
  des brigands a été gagné, les scorpions passés avec FEU et le voleur battu.
- **Stratagus** : recrutement par la statue, passage en 193 ; acquisition
  réelle de **LOUP, ARAIGNÉE et FAUX** ; les trois présentes ensemble en 184 ;
  retour à 226, choix du paiement intégral et hausse d'or de **20 à 1 520**.
  Les trois amulettes sont retirées. `TOUR.MB` reste active à la fin.

Ces résultats valident les itinéraires principaux des guides, pas chaque
variante de dénouement ni tous les résultats possibles des dés. Stratagus
termine avec 4 END et une pierre ENDURANCE inutilisée : réussir ce tirage ne
rend pas le parcours sans risque. Le pilote ne sélectionne pas les héros
selon leurs statistiques et n'efface pas les parties perdues.

## Tentatives et corrections du pilote

Le [journal de campagne](VALIDATION-PARCOURS/campagne.json) référence toutes
les traces conservées :

- Deux parties Gayolard perdues normalement : **HAB 8, mort aux arbres (28)**,
  puis **HAB 7, mort contre le voleur (267)**. La troisième tentative du
  pilote corrigé a gagné.
- Une première exécution a été bloquée par le bac à sable avant le démarrage
  du jeu. La relance autorisée a permis l'accès au port local de POM2.
- Une tentative a exposé une erreur du pilote : il essayait de soigner après
  le premier assaut, alors que le moteur bloque le sac à ce moment. Le
  pilote soigne désormais uniquement avant le premier assaut.
- Une tentative Stratagus s'est arrêtée après les trois acquisitions sur
  une assertion mal nommée : le texte emploie `FAUX`, le lecteur Python
  `FAUSSE_OISEAU`. Le masque lu était bien **41 = LOUP + ARAIGNÉE + FAUX**.
  Après correction du nom, une **nouvelle partie depuis l'accueil** a gagné.

Les deux erreurs de pilote ne sont pas présentées comme des morts de jeu
ni comme des parcours complets validés. Aucun correctif du moteur de jeu
n'a été introduit pendant cette campagne.

## Anomalie du sac en combat

**Corrigée après cette campagne**, le 6 septembre : le sac reste consultable
après le premier assaut, les trois pierres de caractéristiques y sont
signalées interdites, et le combat reprend sans relancer les dés. Le correctif
et le retour vidéo passent 86 assertions dans POM2 headless. Les traces de
parcours ci-dessus décrivent le binaire antérieur, identifié par son SHA-256.

Le bandeau général continue d'afficher **`I:SAC` après le premier assaut**,
mais `run_combat()` n'accepte `I` que lorsque `assaut == 0`. C'est un bug
d'interface confirmé par l'écran de la première tentative Gayolard.

Ce verrou bloque également la simple consultation de l'inventaire, alors
que `stone_usable()` ne restreint en combat que HABILETÉ, ENDURANCE et CHANCE.
Le code prouve cette incohérence ; il ne suffit pas à établir la règle exacte
du livre. La correction conserve les restrictions de `stone_usable()` et
sépare désormais l'accès au sac de l'autorisation d'utiliser une pierre.

## Reproduire

```sh
sh SCOSWAMP.MORE/TOOLS/build_pom2_playtest.sh
python3 -u SCOSWAMP.MORE/TOOLS/validate_routes.py --attempts 16 --port 6523 --output /tmp/scoswamp-validation-nouvelle
```

Utiliser un nouveau dossier pour conserver les rapports précédents. Pour
une seule mission, ajouter `--only gayolard`, `--only pompatarte` ou
`--only stratagus`. Une erreur du pilote arrête la mission ; une mort ou
un refus de recrutement permet une nouvelle tentative, jusqu'à la limite.
Le code de sortie est zéro seulement si toutes les missions demandées ont
atteint leur succès.

Le [pilote](../SCOSWAMP.MORE/TOOLS/validate_routes.py) copie le disque à chaque
tentative et interdit les écritures en RAM ainsi que les requêtes de mutation
autres que le clavier. Les lectures de mémoire servent à observer les pages,
les choix, le sac et la musique. Les durées correspondent à 200 000 cycles
par trame, pas au temps d'une partie humaine.

SHA-256 du HDV utilisé pour **toutes les parties** :

`3ca0cc5052406059ac789028c284d543cfda22a152df42e668df9e710e64875e`

Le journal conserve aussi l'empreinte de l'hôte headless. Les rapports JSON
contiennent chaque touche, les pages avant/après, la feuille d'aventure et
l'écran final.
