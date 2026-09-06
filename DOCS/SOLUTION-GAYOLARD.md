# Gayolard : un parcours gagnant

[Retour aux trois missions et à leurs variantes](PARCOURS-GAGNANTS.md).

Parcours effectué depuis la création normale du personnage, uniquement au
clavier, sans téléportation, sauvegarde forgée ni modification des statistiques.
La partie validée commence avec HAB 11, END 22, CHA 10 et termine page **175**,
HAB 11, END 19, CHA 6 : baie remise, « SUCCES COMPLET », musique VICTOIRE.MB.
Les combats et tests de chance restent aléatoires : ce parcours ne garantit
pas la survie avec tous les tirages.

**Une victoire intégrale est désormais validée aussi en POM2 headless avec
Mockingboard** : HAB/END/CHA 11/21/11 au départ, 11/12/7 à la fin, baie
remise et musique de victoire active. Les parties perdues sont conservées.
[Rapport de validation des trois missions et traces](VALIDATION-PARCOURS.md).

## Préparation et aller

Choisir Gayolard et prendre **GLACE ×2, BÉNÉDICTION, ENDURANCE, HABILETÉ, FEU**.
Au choix des six pierres, cela correspond aux touches `EEIBAD`.

Pages du prologue : 419 → 1 → 95 → 240 → 205 → 335 → 371.

Puis suivre :

```
9 → 195 → 58 → 398 → 314 → 90 → 370 → 157 → 28
```

Employer GLACE pour franchir la rivière profonde (90 → 370).
Vaincre les arbres (28), puis :

```
362 → 22 → 320 → 119 → 381 → 348 → 204 → 269 → 367 → 304 → 131 → 164
```

BÉNÉDICTION soigne la licorne et fournit notamment AMITIÉ. Après les fleurs,
utiliser la pierre HABILETÉ dans l'inventaire à la page 164 pour restaurer les
points perdus. Accepter ensuite la potion d'Endurance et le transport par l'aigle :

```
410 → 248 → 202 → 14 → 88 → 121 → 275 → 145 → 328 → 244 → 161 → 92 → 68 → 215
```

AMITIÉ permet de passer le géant vivant. Vaincre le loup (215), puis choisir
de garder la baie : 247 → 232 → 389.

## Retour

```
342 → 300 → 161 → 121 → 14 [renvoi automatique 338] → 88 → 331 → 112
→ 202 → 138 → 101 → 118
```

Traverser le pont. Au test des scorpions : si chanceux, 70 → 110 (FEU) → 319 ;
sinon, subir les dégâts en 182 puis rejoindre 319.

Continuer 319 → 66 → 147. Au test du voleur : si malchanceux, fuir par
106 → 179 ; sinon, 213 → 267. Avant ce combat, utiliser ENDURANCE dans
l'inventaire si elle reste disponible. Après victoire : 386 → 179.

```
179 → 10 → 227 → 320 [renvoi 265] → 348 → 157 [renvoi 279]
→ 28 [victoire déjà mémorisée : 362] → 22 → 90 → 370
→ 398 [renvoi 239] → 314 → 195 → 58 → 208 → 159 → 6 → 175
```

La seconde pierre GLACE sert au retour. La remise de la baie en 175
déclenche bien la fin réussie.

## Rejouer avec POM2 sans fenêtre

Le petit hôte du banc utilise `libpom2_core.a` du dépôt POM2 voisin, ses ROMs
Apple IIe, un disque dur en slot 5 et une Mockingboard en slot 2. Il ne lit
ni ne modifie la configuration de l'application graphique. Compilation macOS :

```sh
sh SCOSWAMP.MORE/TOOLS/build_pom2_playtest.sh
python3 -u SCOSWAMP.MORE/TOOLS/win_gayolard.py --only victoire_reelle --port 6523
```

Définir `POM2_ROOT` à la compilation si le dépôt POM2 n'est pas voisin.
Le banc `playtest.py` utilise également cet hôte par défaut ; `--pom2 CHEMIN`
permet de choisir un autre exécutable. Recompiler l'hôte après modification
du cœur POM2. Le disque de référence est copié pour chaque scénario.

## Les pages de succès existent

Les textes français et anglais et les illustrations des trois fins sont
présents : **175** (Gayolard), **158** (Pompatarte), **358** (Stratagus).
Les tests `fin_175`, `fin_158`, `fin_358` vérifient leurs écrans à partir de
sauvegardes préparées ; le parcours ci-dessus vérifie réellement la quête
de Gayolard depuis le début.

Anomalie narrative encore ouverte : le choix menant à 158 depuis 56 ne
contrôle pas que la mission cartographique est accomplie. Il permet donc
un succès prématuré chez Pompatarte.

Sources : [contrat 371](../SCOSWAMP/TEXTFR/N350/N371.TXT),
[baie conservée 232](../SCOSWAMP/TEXTFR/N200/N232.TXT),
[remise de la baie 6](../SCOSWAMP/TEXTFR/N000/N006.TXT),
[succès 175](../SCOSWAMP/TEXTFR/N150/N175.TXT).
