# Zone `combat` — les 32 pages de bataille

**Fichier proposé : `BATTLE.MB` (`BATTLE.MB.BIN`, 644 octets, 32,8 s de boucle)**

## Ce que la zone couvre

Les **32 pages qui portent au moins une ligne `M`** (42 lignes d'adversaire au
total, appariées aux 32 images `Bxxx` — `CARTOGRAPHIE.md:597-599`). Repérage :

```sh
grep -l '^M ' SCOSWAMP/TEXTFR/N*/N*.TXT
```

| Page | Adversaire(s) | Lieu |
| --- | --- | --- |
| 012, 211 | GÉANT | clr 7 (nord) |
| 026, 261 | MAÎTRE DES ARAIGNÉES, ARAIGNÉE GÉANTE | clr 17 (danger) |
| 028 | ARBRES-ÉPÉES | clr 18 (danger) |
| 064, 120, 215 | MAÎTRE DES LOUPS, les loups | clr 4 / 11 |
| 079, 235, 301 | CHEF DES BRIGANDS et les siens | clr 9 (nord) |
| 082 | BÊTE DU BASSIN | clr 25 (sud) |
| **124**, 222, 225, 402 | **STRATAGUS**, DÉMON | tour |
| 134 | HERBE À PINCES | clr 24 (danger) |
| 146 | LES GRENOUILLES | clr 8 (sud) |
| 171 | LA VASE | clr 28 (danger) |
| 176 | BÊTE IMMONDE | cul-de-sac (danger) |
| 200 | OURS | clr 12 |
| 221 | LICORNE | clr 29 (sud) |
| 267 | VOLEUR | clr 9 bis (sud) |
| 281 | TROIS ORQUES | clr 26 (danger) |
| 284 | STATUE DE GOBELIN | hors Marais |
| 312 | SCORPION GÉANT | clr 32 (danger) |
| 341 | POMPATARTE | hors Marais |
| 355 | DEUX COUPEURS DE BOURSES | Courbensaule |
| 378 | PATROUILLEUR | clr 19 (nord) |
| 379 | MAÎTRE DES JARDINS | clr 27 (nord) |
| 392 | AIGLE | clr 16 (nord) |

Le combat est une **surcouche** : il remplace le thème de zone le temps de la
page, puis la page suivante rend la main à la zone. Voir
`DOCS/MUSIQUE-CLAIRIERES.md` § 4 pour le mécanisme (`MU +NOM.MB`).

## La pièce

| | |
| --- | --- |
| Œuvre | **Bourrée en mi mineur, BWV 996** |
| Auteur | **Johann Sebastian Bach** (1685-1750), *Suite pour luth ou Lautenwerk* |
| Source | Mutopia Project, [piece-info.cgi?id=1743](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1743) |
| Fichiers | `https://www.mutopiaproject.org/ftp/BachJS/BWV996/bourree/bourree.{ly,mid}` |
| Édition | *Denkmäler alter Lautenkunst*, Wolfenbüttel, Julius Zwißlers Verlag, 1921 |
| Licence | **domaine public** |
| Effectif d'origine | luth (ou clavecin-luth) |
| Tempo retenu | **180** à la noire |
| Durée de boucle | 32,8 s |
| Taille | 644 octets |

## Pourquoi elle convient

C'est **la seule entorse chronologique du plan** — 1710 environ, contre
1470-1612 pour tout le reste — et elle est assumée : aucune pièce de la
Renaissance disponible librement ne fournit une **basse marchante en croches
continues**, qui est ce que demande un combat au tour par tour. La bourrée de
Bach en donne une, en mi mineur, avec une carrure de deux fois huit mesures que
l'oreille tient sans effort.

Elle a de plus une vertu propre au format : elle est **écrite à deux voix
réelles**, dessus et basse. `midi_to_mb.py` réduit à trois voix ; ici il n'a
rien à jeter, et la troisième voix reste libre pour les tenues. C'est la pièce
qui perdra le moins à la conversion.

**Tempo.** 180 la noire. Une bourrée se danse vite ; à 120 elle devient une
étude. À 180 la basse cogne à trois notes par seconde — le pouls d'un combat.

## Le conflit avec `sfx.s`, à ne pas oublier

`SCOSWAMP/SRC/sfx.s` synthétise les bruitages du combat par **boucles de délai
cycle-comptées** (`sfx.s:29-35`). Une IRQ musicale de 500 cycles au milieu d'un
balayage le désaccorde audiblement (`DOCS/MUSIQUE.md § 3.4`). Aujourd'hui le
problème est théorique — la musique ne joue nulle part ailleurs qu'à l'accueil.
Dès qu'une musique de combat existe, **il devient obligatoire** d'encadrer
chaque `_sfx_*` d'un `php / sei … plp` (8 octets, politique 1 de § 3.4).

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/combat/bourree.mid \
    SCOSWAMP.MORE/MUSIC/propositions/combat/BATTLE.MB.BIN \
    --bpm 180 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/combat/COMBAT.wav
```
