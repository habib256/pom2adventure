# Zone `tour` — la tour de Stratagus

**Fichier proposé : `TOWER.MB` (`TOWER.MB.BIN`, 548 octets, 58,4 s de boucle)**

## Ce que la zone couvre

Aucune clairière : la tour est hors carte et hors Marais. C'est la **deuxième
plus grande composante fortement connexe du graphe, 14 pages**
(`CARTOGRAPHIE.md:228`).

| Pages | Rôle |
| --- | --- |
| 226 | la porte de la tour (une des trois destinations de la page 159) |
| 225, 402 | Stratagus, les deux combats préliminaires |
| **124** | **le duel final** — *« une baguette qui […] se transforme en une lame dentelée »*, *« Ce combat sera le dernier »* (`TEXTFR/N100/N124.TXT:3-4,6-7`) |
| 222 | le Démon |
| 297 | le tapis volant (mort) |
| 372 | les gardes arrivent (mort) |
| 375 | l'explosion de la tour (mort) |
| 401 | La Trappe (mort) |
| 298, 327, 349 | les trois fuites |
| 373 | page relais |
| **358** | Mission accomplie — la **victoire amère** de Stratagus |

Les pages de combat (124, 222, 225, 402) passent en zone `combat` le temps du
duel, puis reviennent ici ; les quatre morts passent en zone `mort`.

**La page 358 reste sur `TOWER.MB` et non sur `VICTORY.MB`** : *« votre peu
reluisante mission »* (`TEXTFR/N350/N358.TXT:12`). Cette victoire-là ne mérite
pas d'hymne, et c'est la musique qui doit le dire.

## La pièce

| | |
| --- | --- |
| Œuvre | **Pavan 2** (Pavana II, *Libro de música de vihuela de mano « El Maestro »*) |
| Auteur | **Luys Milán** (1536-1561) |
| Source | Mutopia Project, [piece-info.cgi?id=24](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=24) |
| Fichiers | `https://www.mutopiaproject.org/ftp/MilanL/milan-pavan2/milan-pavan2.{ly,mid}` |
| Licence | **domaine public** |
| Effectif d'origine | vihuela (transcrit guitare) |
| Tempo retenu | **150** à la noire (20 ticks par noire : tombe juste) |
| Durée de boucle | 58,4 s |
| Taille | 548 octets |

## Pourquoi elle convient

Deux pavanes dans le plan, et c'est voulu : `sud` en porte une française
(Arbeau) qui marche, `tour` en porte une **espagnole** (Milán) qui menace. Les
pavanes de Milán sont célèbres pour leur couleur — cadences phrygiennes,
accords plaqués sur des basses obstinées, un balancement majeur/mineur qui ne se
décide jamais. C'est la musique de cour la plus sombre que le domaine public
offre, et Stratagus est le seul commanditaire des trois à demander une chose
franchement mauvaise (voler cinq Amulettes à leurs Maîtres).

L'écriture de vihuela est déjà à trois ou quatre voix serrées : la réduction
n'ampute rien, et les accords plaqués sonnent **plus durs** en ondes carrées
qu'en cordes pincées, ce qui sert.

**Tempo.** 150 la noire — le haut de la fourchette « pavanes et pièces graves » —
pour éviter que la tour ne s'endorme. La boucle de 58 s couvre l'essentiel d'un
passage dans la tour sans se répéter.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/tour/milan-pavan2.mid \
    SCOSWAMP.MORE/MUSIC/propositions/tour/TOWER.MB.BIN \
    --bpm 150 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/tour/TOUR.wav
```
