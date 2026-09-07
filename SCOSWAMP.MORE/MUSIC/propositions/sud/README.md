# Zone `sud` — le Marais proprement dit

**Fichier proposé : `SOUTHSWAMP.MB` (`SOUTHSWAMP.MB.BIN`, 574 octets, 31,5 s de boucle)**

C'est **le thème du jeu** : douze clairières, la clairière de départ comprise,
et la majorité des pages que le joueur verra.

## Clairières couvertes (12)

| `hub` | `id` | Titre | Case | Pages |
| --- | --- | --- | --- | --- |
| **304** | 14 | Le Perroquet / Maîtresse des Oiseaux | (0,4) | 304, 149, 217 |
| **094** | — | La brume fétide | (1,4) | 094 |
| **179** | 9 bis | Le pique-nique suspect | (2,4) | 66, 192, 179 |
| **047** | 3 | Trois chemins herbeux | (4,4) | 47 |
| **031** | 21 | Bassin de cristal | (5,4) | 31, 77, 394 |
| **348** | 29 | La Licorne | (1,5) | 320, 265, 348 |
| **227** | 5 | La clairière des combats | (2,5) | 10, 142, 227 |
| **230** | 8 | Clairière des grenouilles | (4,6) | 53, 329, 230 |
| **314** | 4 | Clairière du Maître des Loups | (1,8) | 398, 239, 314 |
| **058** | **1** | **Le large rond-point — départ** | (2,8) | **195**, 24, 208, 58, 404, 405 |
| **390** | 12 | Pierres et tronc | (3,8) | 105, 330, 390 |
| **082** | 25 | Bête du bassin | (4,8) | 209, 82, 308, 397 |

Ambiances qui commandent le choix :

- page 195, la clairière de départ : *« Le silence pèse autour de vous, seulement
  troublé par le bourdonnement »* (`TEXTFR/N150/N195.TXT:13`), *« Le danger est
  tangible »* (`:19`) ;
- clairière 21 : *« un bassin luit d'une eau pure comme du cristal »*
  (`TEXTFR/N000/N031.TXT:8`) — le seul refuge ;
- clairière 29 : *« vous reconnaissez aussitôt une LICORNE. Elle semble blessée »*
  (`TEXTFR/N300/N320.TXT:9-10`).

## La pièce

| | |
| --- | --- |
| Œuvre | **Pavane « Belle qui tiens ma vie »** |
| Auteur | **Thoinot Arbeau** (1519-1595), *Orchésographie*, **1588** |
| Source | Mutopia Project, [piece-info.cgi?id=1](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1) |
| Fichiers | `https://www.mutopiaproject.org/ftp/ArbeauT/Orch/belle/belle.{ly,mid}` |
| Licence | **domaine public** (Creative Commons No Rights Reserved) |
| Effectif d'origine | quatre voix (SATB) |
| Tempo retenu | **125** à la noire (24 ticks par noire : tombe juste) |
| Durée de boucle | 31,5 s |
| Taille | 574 octets |

## Pourquoi elle convient

La pavane est une **marche lente et régulière** — deux pas simples, un pas
double — et c'est exactement la démarche qu'impose un marais : on avance, on
n'accélère jamais, chaque mesure ressemble à la précédente. C'est le plus
célèbre thème de danse de la Renaissance française, en mode mineur, et sa
carrure de quatre mesures répétées supporte d'être entendue vingt fois sans
fatiguer : c'est la musique que le joueur entendra le plus longtemps.

Les quatre voix d'Arbeau sont homorythmiques — elles bougent ensemble — donc la
réduction à trois voix de `midi_to_mb.py` ne perd presque rien : dessus, ténor,
basse suffisent à l'harmonie.

**Tempo.** À 100 la pavane devient un cortège funèbre et se confond avec la zone
`mort`. À **125** elle garde sa gravité mais respire ; c'est le haut de la
fourchette « pièces graves » demandée (120-150), et 125 tombe juste sur le tick
de 50 Hz (24 ticks à la noire).

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/sud/belle.mid \
    SCOSWAMP.MORE/MUSIC/propositions/sud/SOUTHSWAMP.MB.BIN \
    --bpm 125 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/sud/MARAISUD.wav
```
