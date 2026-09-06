# Stratagus — amulettes, paiement et autres dénouements

[Retour aux trois missions](PARCOURS-GAGNANTS.md).

Le contrat demande **au moins trois amulettes**, à **500 pièces d'or chacune**.
Le parcours ci-dessous rapporte **LOUP, ARAIGNÉE et FAUX** : cette dernière
est la réplique offerte par la Maîtresse des Oiseaux. Elle est explicitement
conçue pour tromper Stratagus et compte dans les trois bijoux du moteur.
Il ne s'agit donc pas de trois amulettes authentiques.

**Itinéraire gagné intégralement dans POM2 headless avec Mockingboard**,
depuis la création normale du personnage : HAB/END/CHA 11/21/11 au départ,
11/4/8 à la fin, or passé de 20 à 1 520. Le recrutement a emprunté 193 ;
les trois amulettes ont été réellement acquises puis remises.
[Rapport et trace complète](VALIDATION-PARCOURS.md).
Les combats restent susceptibles de vous tuer.

## Obtenir le contrat

```
419 → 1 → 95 → 240 → 205 → 255 → 40 → 97 → 284
victoire contre la statue → 156
```

La statue a **HAB 7, END 6**. En 156, le renvoi dépend des blessures reçues
pendant le combat (`DV`, total des dégâts reçus, pas la différence d'END
après d'éventuels soins) :

| Dégâts | Suite |
| --- | --- |
| Aucun | `241 → 206` : épée magique, bonus de combat +1, CHANCE restaurée |
| De 1 à 5 | `193 → 206` : le contrat est accessible |
| Plus de 5 | `326` : Stratagus refuse ; ce parcours de recrutement échoue |

Attention : 193 raconte la restauration des trois statistiques, mais son
fichier ne contient aucune commande de soin. **Vérifier les valeurs affichées
et ne pas compter sur cette guérison narrative.**

Autre recrutement possible : `40 → 50 → 222`, vaincre le démon **12/16**,
puis `174 → 193 → 206`. Cette épreuve est beaucoup plus dangereuse, mais
elle ne passe pas par le seuil de dégâts de la statue.

À 206, choisir les six pierres autorisées (**Neutres ou Maléfiques**) :
**MALÉDICTION, FLÉTRISSURE ×2, GLACE, HABILETÉ, ENDURANCE**.

| Pierre | Usage réservé |
| --- | --- |
| MALÉDICTION | Affaiblir le Maître des Loups, en 191 → 93 |
| FLÉTRISSURE n°1 | Détruire l'Herbe à Pinces, en 167 → 322 |
| FLÉTRISSURE n°2 | Détruire les Fleurs d'Angoisse, en 80 → 196 |
| GLACE | Franchir la rivière profonde au retour, en 90 → 370 |
| HABILETÉ | Restaurer l'HAB perdue dans les Fleurs, avant les arbres |
| ENDURANCE | Soigner les blessures avant un combat dangereux |

Puis `206 → 9 → 195 → 58`.

## Première amulette : le Loup

```
58 → 398 → 191 → 93
victoire → 154 → 46 → 314 → 195 → 58
```

La MALÉDICTION coûte **1d6 END** puis impose le combat contre le Maître
affaibli (**9/8**). Elle évite la succession des deux loups et du Maître
**11/10** de la page 120. Survivre au contrecoup avant de combattre.

En 154, récupérer **LOUP**. À 314, repartir vers l'est ; ne pas prendre la
rivière au nord maintenant : l'unique GLACE est réservée au retour final.

## Deuxième amulette : l'Araignée

```
58 → 105 → 390 → 144 → 26
victoire → 354 → 165
```

Quitter immédiatement la clairière du tronc (105 → 390), puis aller au nord.
À 144, **attaquer sans attendre**. Le Maître des Araignées a **9/6** ; la
page 26 fait perdre **3 END par coup reçu** (`MD 3`). Gagner mène à 354 et donne
**ARAIGNÉE**. Partir aussitôt vers 165.

Éviter 332, la conversation aimable : c'est une mort automatique. Le sort
d'Amitié conduit lui aussi à un piège fatal (361).

## Troisième amulette : la réplique des Oiseaux

```
165 → 388 → 167 → 322 → 81 → 187
→ 10 → 227 → 320 → 368 → 348 → 204 → 80 → 196
→ 367 → 304 → 131 → 288 → 184
```

Employer la première FLÉTRISSURE contre l'Herbe à Pinces, puis aller à
l'ouest. Quitter l'arène (10 → 227), continuer à l'ouest et fuir la licorne
(320 → 368 → 348).

L'entrée en 204 retire **1 HAB**. Utiliser la seconde FLÉTRISSURE pour
détruire les Fleurs. Cela évite la perte supplémentaire de la fuite 269 et
permet de traverser leur clairière sans danger au retour. Utiliser HABILETÉ
dans le sac une fois cette perte subie, avant le prochain combat.

À 304, demander à voir la Maîtresse ; à 131, annoncer **Stratagus** ; à 288,
**lui parler de la mission**, sans l'attaquer. En 184, elle donne **FAUX**.
Le sac doit maintenant contenir trois amulettes différentes.

## Retour avec les trois amulettes

```
184 → 217 → 250 → 367 → 265 → 348 → 157 → 28
victoire → 362 → 22 → 90 → 370 → 398 [renvoi 239]
→ 314 → 195 → 58 → 208 → 159 → 226 → 194 → 207 → 358
```

À 250, choisir que les fleurs sont mortes : elles ont bien été détruites en
196. À 28, les Arbres-Épées **9/12** sont rencontrés pour la première fois
sur cet itinéraire ; il faut réellement les vaincre. Employer ENDURANCE
avant ce combat si la pierre est encore disponible et les blessures graves.

À 90, utiliser GLACE puis partir au sud. Au village, choisir Stratagus en
159. En 226, la branche « trois ou plus » mène à 194. **Exiger d'abord le
paiement** pour atteindre 207 : `GA 500` verse **1 500 pièces** pour ce
lot de trois et retire les trois amulettes. Partir vers **358**.

## Toutes les branches qui aboutissent à 358

Le nombre d'amulettes est réellement contrôlé en 226 (`CA`). À partir de
cette page, les chemins directs vers le même écran de succès sont :

| Butin au retour | Choix et pages | Paiement réel du moteur |
| --- | --- | --- |
| 3 à 6 | `226 → 194 → 207 → 358` | **500 × nombre d'amulettes** |
| 3 à 6 | `226 → 194 → 99 → 242 → 358` | **0** (`GA 0`), amulettes retirées |
| 1 ou 2 | `226 → 7 → 207 → 358` | **500 × nombre d'amulettes**, en réclamant le prix promis |
| 1 ou 2 | `226 → 7 → 266 → 242 → 358` | **250 × nombre d'amulettes**, en acceptant l'offre réduite |

Les trois dernières lignes atteignent bien 358, mais les branches à une ou
deux amulettes ne remplissent pas le minimum du contrat. Donner le butin
sans condition est une escroquerie, pas un paiement optimal. `GA` retire
les amulettes dans les quatre cas.

### Variante courte : une seule amulette

Après le recrutement, garder le même choix de pierres et effectuer seulement
la chasse au Loup décrite plus haut. Après 154 :

`46 → 314 → 195 → 58 → 208 → 159 → 226 → 7 → 207 → 358`.

Le moteur paie 500 pièces et affiche la fin. C'est une variante réellement
permise par les textes, **pas l'accomplissement du contrat des trois**.
On peut choisir 266 à la place de 207 pour le paiement réduit.

### Amulettes et faux dons

| Amulette | Acquisition effective | Piège à éviter |
| --- | --- | --- |
| LOUP | 154, victoire en 120, 64 ou 93 | TERREUR fait fuir le Maître : pas de bijou en 46 |
| ARAIGNÉE | 354, victoire en 26 ou 261 | La conversation et AMITIÉ sont mortelles |
| FAUX | `131 → 288 → 184` | C'est une réplique, mais elle compte et est payée |
| GRENOUILLE | `53 → 13 → 287 → 359`, chance → `162 → 245` avec ILLUSION | Si le mensonge échoue : `16 → 198 → 146`, pas le vol prévu |
| FLEUR | `305 → 334 → 379`, victoire → 251 | Perte de 3 HAB avant le combat, puis de 3 CHA ; les « dons » de 117 et 292 sont repris immédiatement |
| OISEAU authentique | Aucune commande `G OISEAU` dans le corpus actuel | Ne pas la compter comme une récompense disponible |

Cette table donne les acquisitions alternatives ; elles demandent d'autres
détours et une autre réserve de pierres. Elles ne sont pas des substitutions
gratuites dans l'itinéraire détaillé. Chaque type ne compte qu'une fois :
le moteur stocke les amulettes dans un masque de bits.

## Sortir vivant sans réussir le contrat

**Sans amulette** : `226 → 54`, test de chance. Si chanceux :
`109 → 349`, quitter la tour. Si malchanceux, 285 impose de combattre ou
d'utiliser la magie. **349 est une survie sans récompense**, pas 358.

**Tuer Stratagus et s'échapper** : depuis la bourse truquée en 242, prendre
`124`, vaincre Stratagus **13/18**, puis `340 → 298`. Autre possibilité :
`242 → 256 → 274 → 298`, la Malédiction le tue, mais son contrecoup coûte
1d6 END. Le texte demande une pierre ; les options de 256 sont de simples
`C`, sans contrôle de possession ni consommation de MALÉDICTION : anomalie
du moteur à distinguer d'un usage normal de la magie. Pour un parcours
conforme au récit, prévoir une pierre supplémentaire ou conserver celle-ci.

Dans les deux cas, **partir immédiatement**. Rester fouiller en 375 mène à
l'explosion de la tour. La fin 298 reconnaît le service rendu en éliminant
le sorcier, mais pas une mission rémunérée réussie.

Sources : [contrat 206](../SCOSWAMP/TEXTFR/N200/N206.TXT),
[réplique 184](../SCOSWAMP/TEXTFR/N150/N184.TXT),
[contrôle du butin 226](../SCOSWAMP/TEXTFR/N200/N226.TXT),
[paiement 207](../SCOSWAMP/TEXTFR/N200/N207.TXT),
[fin 358](../SCOSWAMP/TEXTFR/N350/N358.TXT),
[comptage et vente des amulettes](../SCOSWAMP/SRC/rules.c).
