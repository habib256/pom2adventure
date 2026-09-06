# Zone `victoire` — les deux fins heureuses, et les sept sorties vivantes

**Fichier proposé : `VICTORY.MB` (`VICTORY.MB.BIN`, 315 octets, 39,2 s — *sans boucle*)**

## Ce que la zone couvre

Le jeu n'a **pas de page finale unique** : il a une fin par employeur
(`CARTOGRAPHIE.md:232-237`).

| Page | Titre | Zone |
| --- | --- | --- |
| **175** | Le miracle de l'Anthérique (Gayolard) — *« FIN DE L'AVENTURE - SUCCÈS COMPLET »* (`TEXTFR/N150/N175.TXT:20`) | **`victoire`** |
| **158** | Réussite : la carte est complète (Pompatarte) — *« la carte que vous avez tracée au fil du Marais »* (`TEXTFR/N150/N158.TXT:3-4`) | **`victoire`** |
| 358 | Mission accomplie (Stratagus) — *« votre peu reluisante mission »* (`TEXTFR/N350/N358.TXT:12`) | **`tour`**, délibérément |

Les **sept fins vivantes non victorieuses** — 049 (vente de l'Anneau), 052
(échec à la baie), 100, 141 (le repos du guerrier), 298 et 327 et 349 (les
fuites de la tour) — ne prennent **pas** `VICTORY.MB`. Elles gardent la musique
de leur zone, ou passent en silence par `MU -`. Une fanfare sur une fuite serait
un contresens ; c'est le genre de détail que le validateur doit surveiller.

## La pièce

| | |
| --- | --- |
| Œuvre | **Old 100th** (« All people that on earth do dwell », psaume 100 du Psautier de Genève) |
| Auteur | **Loys Bourgeois** (c. 1510-1560) ; version Mutopia datée **1612** |
| Source | Mutopia Project, [piece-info.cgi?id=90](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=90) |
| Fichiers | `https://www.mutopiaproject.org/ftp/BourgeoisL/Old100/Old100.{ly,mid}` |
| Licence | **domaine public** (Creative Commons No Rights Reserved) |
| Effectif d'origine | quatre voix (SATB) |
| Tempo retenu | **150** à la noire (20 ticks par noire : tombe juste) |
| Durée de boucle | 39,2 s |
| Taille | **315 octets — la plus petite pièce du lot** |

## Pourquoi elle convient

Une victoire, sur trois ondes carrées, ne se joue pas avec une fanfare : il n'y
a ni cuivres ni percussions, et une tentative de fanfare sonne comme une sonnerie
de téléphone. Ce qui marche, c'est **l'ampleur** — des rondes, quatre voix qui
avancent ensemble, aucune syncope. Le psaume 100 est exactement cela : la
mélodie la plus large du répertoire libre, huit notes par phrase, quatre
phrases, et une cadence finale sans ambiguïté.

C'est aussi le contrepoint exact des deux pavanes : même écriture homorythmique,
mais **en majeur** et sans balancement. Après une heure de mode mineur, l'effet
de sortie est immédiat.

Enfin, 315 octets : la pièce la moins chère du disque, pour l'écran qu'on voit
le moins souvent.

## Elle ne doit PAS boucler

Comme `DEATH.MB` : bit 0 des drapeaux à zéro dans l'en-tête MB1, et le lecteur
s'arrête tout seul (`music.s`, branche `@stop` de la poignée `@end`). Voir
`propositions/mort/README.md`.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/victoire/Old100.mid \
    SCOSWAMP.MORE/MUSIC/propositions/victoire/VICTORY.MB.BIN \
    --bpm 150 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/victoire/VICTOIRE.wav
```
