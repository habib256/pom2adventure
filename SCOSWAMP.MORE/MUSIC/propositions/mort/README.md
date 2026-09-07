# Zone `mort` — l'écran de mort et les onze fins fatales

**Fichier proposé : `DEATH.MB` (`DEATH.MB.BIN`, 725 octets, 32,3 s — *sans boucle*)**

## Ce que la zone couvre

**Deux choses de nature différente.**

### 1. L'écran de mort, qui n'est pas une page

`game_over()` (`SCOSWAMP/SRC/scoswamp.c:1788-1815`) est un écran texte 40
colonnes dessiné par le moteur : *« Votre ENDURANCE est… »*, puis `R` / `L` /
`Q`. **Aucun fichier `.TXT`, donc aucune ligne `MU` possible.** Il faut poser la
musique en dur dans `die_and_restart()` (`scoswamp.c:1842`), juste avant
l'appel à `game_over()`.

### 2. Les onze pages de mort narrative

| Page | Titre |
| --- | --- |
| 003 | Le Marais aux Scorpions |
| 030 | Morsure fatale |
| 098 | Transformation |
| 260 | La fin sous les oiseaux |
| 297 | Le tapis volant de Stratagus |
| 313 | Noyade dans la rivière |
| 332 | Piège du Maître des Araignées |
| 361 | Piège du Maître des Araignées |
| 372 | Les gardes arrivent |
| 375 | L'explosion de la tour |
| 401 | La Trappe |

Celles-ci sont de vraies pages : elles portent `MU +DEATH.MB` comme n'importe
quelle surcouche.

## La pièce

| | |
| --- | --- |
| Œuvre | **Marche funèbre, KV 453a** |
| Auteur | **Wolfgang Amadeus Mozart** (1756-1791), Vienne, **1784** |
| Source | Mutopia Project, [piece-info.cgi?id=446](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=446) |
| Fichiers | `https://www.mutopiaproject.org/ftp/MozartWA/KV453a/k453a/k453a.mid`, `.../k453a-lys.zip` (déballé ici en `k453a.ly` + `README-mutopia.txt`) |
| Licence | **domaine public** (Creative Commons No Rights Reserved) |
| Effectif d'origine | piano |
| Tempo retenu | **120** à la noire (25 ticks par noire : tombe juste) |
| Durée de boucle | 32,3 s |
| Taille | 725 octets |

## Pourquoi elle convient

C'est une **vraie** marche funèbre, courte, écrite pour le clavier, et donc déjà
pensée en trois ou quatre voix serrées : la réduction ne l'ampute pas. Elle
tient en une page de partition, ce qui donne 32 s — la bonne longueur pour un
écran où le joueur ne reste que le temps de choisir `R`, `L` ou `Q`.

Le pas pointé de la marche est reconnaissable dès la deuxième mesure, même
réduit à trois ondes carrées : c'est le genre le plus robuste à la conversion,
parce que son identité est **rythmique** avant d'être harmonique.

## Elle ne doit PAS boucler

Mettre le **bit 0 des drapeaux à zéro** dans l'en-tête MB1 : le lecteur traite
déjà ce cas — `music.s`, poignée `@end`, branche `@stop` :

```asm
@end:   lda _music_buf+5             ; drapeau de boucle
        and #1
        beq @stop
        ...
@stop:  jsr _music_stop
        sec
        rts
```

La marche se joue une fois, s'arrête, et l'écran de mort finit en silence. Une
marche funèbre en boucle serait comique au bout du troisième tour.

> `midi_to_mb.py` pose le bit de boucle systématiquement. Il faut soit lui
> ajouter un `--no-loop`, soit corriger l'octet +5 après coup. C'est l'étape 8
> du plan de `DOCS/MUSIQUE-CLAIRIERES.md § 7`.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/mort/k453a.mid \
    SCOSWAMP.MORE/MUSIC/propositions/mort/DEATH.MB.BIN \
    --bpm 120 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/mort/MORT.wav
```
