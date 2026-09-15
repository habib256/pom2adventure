# Le combat retrouve son rythme

Branche `feat/scoswamp-combat-rythme`, fusionnee sur `feat/scoswamp-memoire`.

Le combat etait exact et sans tension. Une ligne donnait le total de chacun et
un signe entre les deux, on appuyait, on lisait la perte. Le livre ne procede
pas ainsi : chacun jette **deux des** et ajoute son HABILETE, le plus fort
blesse l'autre, et tout Defis Fantastiques tient dans la demi-seconde qui
separe les des de la blessure. C'est cette demi-seconde qui manquait.

---

## 1. Ce que l'ecran montre maintenant

### Avant (base `feat/scoswamp-memoire`, page 120, 80 colonnes, lignes 20 a 23)

Capture par l'API `ai-control` de POM2 (`/mem` sur $0400 principal + auxiliaire),
sauvegarde forgee par `SCOSWAMP.MORE/TOOLS/forge_save.py --scene 120`.

```
VOUS HAB 12 [##########] 24/24   PREMIER LOUP HAB 7 [######----] 3/5
ASSAUT 3     votre force 19   >   la sienne 14   1/3
Vous l'avez blesse  -2 END
 ESPACE  porter le coup    C  tenter la Chance    F  fuir    ESC  image
```

```
VOUS HAB 12 [##########] 24/24   MAITRE DES LOUPS HAB 11 [##########] 10/10
ASSAUT 1     votre force 15   <   la sienne 19   3/3
Elle vous a blesse  -2 END
 ESPACE  encaisser le coup    C  tenter la Chance    F  fuir    ESC  image
```

Trois nombres tombes du ciel, un signe, une perte. Le joueur n'a pas jete de
des : on lui rend un verdict.

### Apres

Meme page, meme sauvegarde. `█` est une espace en video inverse -- le pave
plein de la machine ; les noms de touches et les noms de creatures sont eux
aussi en inverse, d'ou les `█` qui les encadrent dans le vidage texte.

```
VOUS HAB 12 [██████████] 24/24   PREMIER█LOUP HAB 7 [██████████] 5/5 1/3
ASSAUT 2   Vous : 5 + 5 + 12 = 22
           Lui  : 3 + 2 + 7 = 12        Vous l'avez blesse  -2 END
█ESPACE█ frapper   █F█ fuir   █C█ Tentez votre Chance (CHANCE 12) : 4 ou 1
```

```
VOUS HAB 12 [██████████] 24/24   PREMIER█LOUP HAB 7 [██--------]█1/5 1/3
ASSAUT 4   Vous : 2 + 2 + 12 = 16
           Lui  : 6 + 4 + 7 = 17        Elle vous a blesse  -2 END
█ESPACE█ encaisser   █F█ fuir   █C█ Tentez votre Chance (CHANCE 12) : 1 ou 3
```

```
VOUS HAB 12 [██████████] 24/24   PREMIER█LOUP HAB 7 [██████████] 5/5 1/3
ASSAUT 1   Vous : 4 + 1 + 12 = 17
           Lui  : 6 + 4 + 7 = 17        Vous avez chacun esquive.
█ESPACE█ assaut suivant   █F█ fuir   █ESC█ image
```

Apres un `[C]` reussi, et le point de CHANCE paye (12 -> 11) :

```
VOUS HAB 12 [██████████] 23/24   PREMIER█LOUP HAB 7 [██--------]█1/5 1/3
ASSAUT 4   Vous : 2 + 2 + 12 = 16
           Lui  : 6 + 4 + 7 = 17        Chanceux !
█ESPACE█ continuer
```

La chute :

```
VOUS HAB 12 [█████████-] 21/24   MAITRE█DES█LOUPS HAB 11 [----------]█0/10 3/3
ASSAUT 6   Vous : 4 + 6 + 12 = 22
MAITRE DES LOUPS s'effondre.
█ESPACE█ continuer
```

---

## 2. Les cinq points, un par un

### 1. Les des visibles

`Round` (rules.h) ne portait que les deux Forces d'Attaque. Il porte
maintenant les quatre des : `hero_d1, hero_d2, monster_d1, monster_d2`.
`combat_round` les tire un par un au lieu de passer par `roll_2d6` -- meme
somme, donc **meme partie a semence egale**, l'ordre de tirage etant inchange.

L'ecran ecrit les deux jets sur les deux lignes qui suivent le bandeau :

    ASSAUT 3   Vous : 4 + 3 + 12 = 19
               Lui  : 2 + 6 + 7 = 15

L'HABILETE affichee est **deduite** (`force - d1 - d2`) et non relue : c'est
ce qui fait entrer le bonus de l'Epee Magique dans le compte sans un champ de
plus. Trois verifications neuves dans `test_rules.c` : les des tiennent dans
1..6, et `d1 + d2 + HABILETE` retombe sur la force annoncee des deux cotes --
une ligne qui mentirait sous les yeux du joueur serait pire que pas de ligne.

### 2. Le temps

`sfx_beat` (sfx.s) : un cinquieme de seconde de silence, compte en cycles
comme les hauteurs des bruitages -- la machine n'a pas d'horloge, et il n'y a
pas de compteur exploitable du cote Mockingboard. 160 tours externes de 1 280
cycles, soit ~206 000 cycles, ~200 ms a 1,023 MHz. Onze octets.

Il tombe a deux endroits :

- entre l'annonce des des et l'annonce de la blessure ;
- apres la mise a jour de la jauge, avant que les des de l'assaut suivant ne
  reprennent la ligne.

Et deux fois de plus a la fin : la creature met un instant a tomber, et
l'ecran de mort n'arrive pas sur le coup.

La jauge d'ENDURANCE ne bouge qu'apres `combat_apply` et apres la Chance :
elle est le **constat** du coup, jamais son annonce.

Le verdict s'ecrit desormais **a la colonne 40 de la ligne du jet adverse**,
pas par-dessus : effacer les des pour annoncer la blessure reprendrait d'une
main ce que les deux lignes viennent de donner.

### 3. La Chance au bon moment

L'invite dit l'enjeu :

    C  Tentez votre Chance (CHANCE 12) : 4 ou 1

Le premier nombre est le sort du Chanceux, le second celui du Malchanceux,
conformement au livre (page de regles « Utilisation de la Chance dans les
Combats ») et a `combat_apply`, verifie dans le PDF :

- le heros frappe : Chanceux **4**, Malchanceux **1** (« oter deux points de
  plus » / « vous n'aurez ote qu'un seul point ») ;
- le heros encaisse : Chanceux **blessure - 1**, Malchanceux **blessure + 1**
  (« rajoutez alors un point » / « enlevez encore un point »), donc 1 ou 3 sur
  une blessure ordinaire, 3 ou 5 sur les blessures doublees des lignes `MD`.

Une CHANCE a zero ne propose plus `[C]` : 2d6 ne descend pas sous 2, le jet
serait perdu d'avance et couterait quand meme sa frappe. La touche ne repond
pas davantage, pour que rien ne soit accepte qui n'ait ete propose.

L'enjeu passe en dernier sur la ligne et **la touche image lui cede la
place** : les deux ne tiennent pas dans 80 colonnes (l'invite la plus large
fait 76 colonnes sur 79 utilisables). `ESC` continue de fonctionner, il n'est
simplement plus annonce le temps d'une frappe.

### 4. Le bandeau

- Le rang dans la file (`2/3`) est passe de la fin de la ligne d'assaut -- que
  les des viennent de reprendre -- au bandeau, a cote de la creature a qui il
  se rapporte. Le nom cede trois lettres quand la file compte (19 -> 16
  caracteres) : le pire cas du corpus est `PREMIERE GRENOUILLE`, et 33 + 46
  colonnes font exactement 79.
- La jauge est en paves pleins (espace en video inverse) au lieu de dieses.
  Le diese faisait une trame grise ou l'on ne comptait rien.
- Sous cinq points d'ENDURANCE, le compte `4/10` passe en video inverse.
  **Ecart assume avec la consigne** : la machine ne fait pas de rouge en 80
  colonnes, l'inverse est le seul cri dont elle dispose, et il porte des deux
  cotes du bandeau -- une creature a bout est une nouvelle, elle aussi. Le
  distinguer pour le seul heros aurait coute un parametre de plus a
  `put_fighter` sans rien apprendre.

### 5. La fin

`sfx_fall` puis `sfx_beat` avant que le suivant ne se presente ; `sfx_death`
puis `sfx_beat` avant l'ecran de mort. Les bruitages restent a leur place
d'origine, avant le texte, et gardent le `sei/plp` que la branche memoire leur
a donne.

---

## 3. Le budget, etape par etape

`make` mesure la marge en memoire principale ; `LOWBSS` (le catalogue de
messages, en RAM basse) est un second compte, independant.

| Etape | Marge principale | LOWBSS libre |
|---|---|---|
| Base `feat/scoswamp-memoire` | 510 o | 39 o |
| **Etat livre** | **270 o** | **29 o** |
| **Depense** | **240 o** (budget 250) | **10 o** |

Le detail, mesure `.proc` par `.proc` sur les listings `ca65` :

| Poste | Octets |
|---|---|
| `rules.c` (les quatre des exposes) | **-51** |
| `sfx.s` (`_sfx_beat`) | +11 |
| `scoswamp.c`, code | +242 |
| RODATA et divers | ~+38 |

`rules.c` **retrecit** de 51 octets tout en exposant quatre des de plus. Deux
mesures y ont pourvu :

- `Round.outcome` descend de l'enum (un `int` sur cc65, donc des comparaisons
  16 bits par appels) a un octet : -12 sur `combat_apply` a lui seul ;
- `combat_round` compose l'assaut dans une locale et n'ecrit `out` qu'une
  fois, par affectation de structure. Cc65 ne garde pas un pointeur de
  parametre : chaque `out->x` relit `sp`, reconstruit `ptr1` et refait le
  detour -- sept champs, quatre-vingts octets de rechargement de pointeur. Avec
  `-Cl` la locale est statique, donc en adressage absolu, et la copie finale
  est un `memcpy` de sept octets. `combat_round` : 257 -> 218 octets.

Cote `scoswamp.c` (+242) : `put_roll` 77, `put_tag` 33 (contre -16 sur
`put_key`), `put_verdict` 31, `show_fighters` +48 (le rang dans la file),
`put_gauge` +22 et `put_fighter` +17 (les paves pleins et l'ENDURANCE basse),
`run_combat` +30.

Catalogue : trois messages neufs (`M_JET_VOUS`, `M_JET_LUI`, `M_K_ENJEU`)
payes presque entierement par la disparition de `M_ASSAUT_FORCE_D` (48
caracteres en francais, remplace par `M_ASSAUT_N`, 9) et par le raccourcissement
de `M_K_ENCAISSER` et `M_K_FRAPPER` -- huit et sept caracteres que la ligne du
dessus dit deja, et qui manquaient exactement a l'enjeu pour tenir a cote de
`FUIR`. Bilan LOWBSS : 10 octets, dont 6 pour les trois entrees de `slot[]`.

---

## 4. Ce que la fusion a coute

Le worktree avait ete cree depuis `main` ; la vraie base etait
`feat/scoswamp-memoire`, une quarantaine de commits plus loin. La fusion a ete
faite en cours de route (commit `Merge feat/scoswamp-memoire into the combat
rhythm`) et le budget est mesure **sur la base fusionnee**.

Trois fichiers en conflit :

- `SCOSWAMP.BIN` et `SRC/messages.h` : des artefacts, regeneres.
- `SRC/scoswamp.c` : six conflits reels, tous dans le combat. Les deux apports
  sont conserves ; chaque `cprintf` introduit ici est devenu un `cfmt` (le
  formateur maison de la branche memoire, qui a remplace la famille printf) et
  chaque chaine nue un `cputs`.

Ce que la fusion a coute en octets : **environ 160**. Sur l'ancienne base, la
reecriture de `put_gauge` et `put_fighter` -- ecrire a l'ecran au lieu de
composer une chaine -- rendait 160 octets qui payaient la moitie du travail.
La branche memoire avait deja fait exactement cette reecriture. Le remboursement
etait donc deja encaisse, et le meme travail est passe de 152 a 240 octets sans
qu'une ligne change. Les 79 octets rendus par la reecriture de `combat_round`
ci-dessus ont ete trouves pour repasser sous le budget.

Rien de la branche memoire n'a ete perdu : la page reste en texte jusqu'au
premier « engager », `MI` donne son portrait a chaque adversaire, la musique
Mockingboard joue sous le combat, `sfx.s` garde son `sei/plp`.

---

## 5. Verifications

| Controle | Resultat |
|---|---|
| `cd SCOSWAMP/SRC && make` | `OK : tient en mémoire, marge de 270 octets` |
| `make hdv` | image reconstruite, 1329 fichiers |
| `test_rules` | `regles : tout passe` (3 verifications neuves) |
| `python3 SCOSWAMP.MORE/TOOLS/reflow_txt.py SCOSWAMP` | `problemes : 0` |
| Emulateur | `POM2 --preset iie dist/SCOSWAMP.HDV --ai-control=6511`, page 120, les trois adversaires, esquive, blessure des deux cotes, `[C]` Chanceux, chute |

L'essai en emulateur a porte sur une **copie de travail** de `SAVE/PARTIE9`
forgee par `forge_save.py --scene 120` ; le fichier suivi a ete rendu a son
etat d'origine et l'image disque reconstruite avant le commit.

---

## 6. Ce qui reste a faire

- **30 octets de marge**, contre 510 sur la base. Le prochain travail sur le
  combat devra en rendre avant d'en prendre. Deux gisements connus, du meme
  ordre que celui de `combat_round` : `_classify_line` (5,1 Ko a lui seul) et
  les fonctions qui ecrivent encore `p->champ` en boucle.
- **L'ENDURANCE basse est signalee des deux cotes** du bandeau, pas seulement
  chez le heros (voir 2.4). A trancher : si l'on veut vraiment reserver le cri
  au heros, il faut un parametre de plus a `put_fighter`, une vingtaine
  d'octets.
- **La touche image n'est plus annoncee** quand une blessure attend et que la
  CHANCE n'est pas a zero. Elle fonctionne toujours. Une invite sur deux
  lignes reglerait la question, mais les 4 lignes du bas sont pleines en mode
  mixte.
- **`M_CHANCEUX` / `M_CHANCEUX2`** (et leurs jumeaux malchanceux) sont deux
  paires de messages identiques. Les fondre rendrait 29 octets de LOWBSS.
  Laisse en place : hors sujet de cette branche.
- **Le battement n'est pas interruptible.** Un joueur presse ne peut pas le
  sauter. Deux cents millisecondes deux fois par assaut, c'est peu ; sur un
  combat de quinze assauts, cela fait six secondes. A reevaluer en playtest.
- **Le cas CHANCE a zero** n'a pas ete atteint en emulateur (il aurait fallu
  douze `[C]` de suite). La condition est celle qui gouverne l'affichage et
  celle qui gouverne la touche, et c'est la meme.
