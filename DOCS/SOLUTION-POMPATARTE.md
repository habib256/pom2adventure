# Pompatarte — atteindre Courbensaule et revenir

[Retour aux trois missions](PARCOURS-GAGNANTS.md).

Objectif : visiter réellement **280, Courbensaule**, puis revenir à
**56 → 158**. **Itinéraire gagné intégralement dans POM2 headless avec
Mockingboard**, depuis la création normale du personnage : HAB/END/CHA
11/21/11 au départ, 11/10/7 en fin. Courbensaule 280 et l'auberge 78 ont
bien été visitées. Le duel des brigands a été gagné sur cette partie.
[Rapport et trace complète](VALIDATION-PARCOURS.md).

## Contrat et préparation

`419 → 1 → 95 → 240 → 205 → 27 → 173`.

À 27, se présenter comme un guerrier hors pair. Pompatarte offre **cinq
pierres neutres**. Prendre **GLACE ×2, HABILETÉ, ENDURANCE, FEU**, puis
`9 → 195 → 58`.

Les deux GLACE sont réservées à la rivière profonde, à l'aller et au retour.
HABILETÉ répare la perte causée par les Fleurs d'Angoisse. FEU est conservée
pour les scorpions au retour. Utiliser ENDURANCE lorsque les blessures
l'exigent ; une seule pierre ne suffit pas à garantir la survie.

## Aller jusqu'à Courbensaule

```
58 → 398 → 314 → 90 → 370 → 157 → 28
victoire → 362 → 22 → 320 → 368 → 348
→ 204 → 269 → 367 → 304 → 131 → 23 → 248 → 202
→ 14 → 88 → 121 → 218 → 336 → 85 → 153 → 65 → 163 → 79
```

- À 398, obéir au Maître des Loups et partir. À 90, utiliser la première
  GLACE. À 28, vaincre les Arbres-Épées (**HAB 9, END 12**).
- À 320, fuir la licorne. À 204 puis 269, la fuite coûte au total **2 HAB**.
  Utiliser ensuite HABILETÉ dans le sac, avant les prochains combats.
- À 131, annoncer honnêtement **Pompatarte**. La Maîtresse des Oiseaux
  propose le voyage avec l'aigle en 23 → 248.
- À 14, laisser le scorpion à son repas. À 218, ignorer le Feu Follet.
  À 336, fuir la Vase par 85 → 153, puis partir à l'ouest vers les brigands.
- À 65, les saluer et accepter le **duel au premier sang** (79), contre un
  adversaire **HAB 9, END 10**. Le duel cesse dès la première blessure.

Deux issues du duel :

| Résultat | Suite |
| --- | --- |
| Vous touchez le chef | `360 → 214 → 19` : les brigands deviennent amicaux |
| Il vous touche | `128 → 407 → 19` : payer avec un autre objet, garder l'Anneau |

À 407, le moteur prélève automatiquement le premier objet accessible (`PO`).
Ce n'est pas un menu de sélection : contrôler le sac après le paiement et
ne pas supposer qu'une pierre prévue pour le retour est toujours présente.
Avec le lot conseillé et HABILETÉ déjà consommée, le paiement prend
ENDURANCE si elle reste, sinon FEU. Il laisse donc la GLACE du retour tant
que vous n'avez pas dépensé les deux autres pierres avant le duel.

Puis **`19 → 280 → 78 → 343`** : atteindre Courbensaule, dormir à la
**Lance Tordue** (+2 END, plafonnés au total initial), repartir vers le sud.
Il n'est pas nécessaire de visiter toutes les 35 clairières : le contrat
demande une route vers Courbensaule.

## Retour au village

À 343, si vous avez gagné le duel et sympathisé avec les brigands, prendre
`199 → 19`. Après paiement en 407, le récit est cordial mais n'énonce pas
explicitement l'amitié : le moteur laisse choisir la réponse en 343 sans
la contrôler. Pour une reprise prudente qui ne suppose pas cette amitié,
prendre `301`, affronter les deux brigands (**8/10 et 8/11**) jusqu'à
`246 → 19`, ou utiliser leur option de fuite vers 19.

```
19 → 137 → 153 → 218 → 121 → 14 [renvoi 338] → 88
→ 331 → 112 → 202 → 138 → 101 → 118
```

À 331, indiquer que vous n'avez pas combattu l'aigle. À 138 → 101,
**traverser le pont**. Le test de chance des scorpions en 118 donne :

| Résultat | Suite |
| --- | --- |
| Chanceux | `70 → 110 → 319`, employer FEU |
| Malchanceux | `182 → 319`, résoudre et acquitter les dégâts |

Si FEU a été donnée au chef, prendre **70 → 377** et sauter : test de 2d6
contre l'END actuelle, réussite → 319, échec → 406 (−3 END) → 319. Avec
au moins 12 END, ce test réussit nécessairement ; avec moins, il reste risqué.

Ensuite `319 → 66 → 147` : accepter de s'asseoir près du voleur pour le
test de chance. Ne pas choisir 17, qui vole toutes les pierres et les
objets magiques.

| Résultat | Suite |
| --- | --- |
| Malchanceux | `106 → 179`, fuir et perdre 2 END |
| Chanceux | `213 → 267`, combattre le voleur **10/9**, puis `386 → 179` |

Soigner avant 267 si ENDURANCE reste disponible. Puis :

```
179 → 10 → 227 → 320 [renvoi 265] → 348 → 157 [renvoi 279]
→ 28 [victoire précédente mémorisée : 362] → 22 → 90 → 370
→ 398 [renvoi 239] → 314 → 195 → 58 → 208 → 159 → 56 → 158
```

Employer la seconde GLACE à 90. La réutilisation de la victoire des arbres
est le comportement actuel du moteur, bien que 279 raconte leur repousse.
À 159 choisir Pompatarte, puis répondre oui à 56 : **la mission est réussie**.

Si une pierre nécessaire a été perdue ou utilisée plus tôt, ce tracé doit
être adapté ; ne pas essayer de choisir une option magique barrée.

## Raccourci anormal vers le même écran

Après le contrat en 173 et le choix des pierres :

`9 → 195 → 58 → 208 → 159 → 56 → 158`.

Le moteur accepte « Oui, je suis allé jusqu'à Courbensaule » sans vérifier
les visites. Cela affiche le succès, mais **Courbensaule n'a pas été
atteinte**. Ce défaut est distinct de la route légitime ci-dessus.

Sources principales : [contrat 173](../SCOSWAMP/TEXTFR/N150/N173.TXT),
[Courbensaule 280](../SCOSWAMP/TEXTFR/N250/N280.TXT),
[retour 56](../SCOSWAMP/TEXTFR/N050/N056.TXT),
[succès 158](../SCOSWAMP/TEXTFR/N150/N158.TXT).
