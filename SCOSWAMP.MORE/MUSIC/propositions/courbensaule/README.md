# Zone `courbensaule` — la ville du nord et son auberge

**Fichier proposé : `BENTBEAKS.MB` (`BENTBEAKS.MB.BIN`, 553 octets, 35,8 s de boucle)**

## Ce que la zone couvre

Une seule clairière, mais c'est la seule ville de la carte.

| Clairière | `hub` | Case | Pages |
| --- | --- | --- | --- |
| Route de Courbensaule (`id` absent) | **078** | (0,0) | 280, 355, **078**, 150, 408 |

- 280 « Route de Courbensaule » — la sortie nord du Marais (`carte.json:772`) ;
- 078 « La Lance Tordue » — *« une auberge agréable et spacieuse »*,
  *« vous vous sentez parfaitement reposé »* (`TEXTFR/N050/N078.TXT:3,7`) ;
- 150 « Le marchand de potions », 408 « Échange chez Alphonse » — la boutique
  d'Alphonse Machefer ;
- 355 « Retour à Courbensaule » — *« deux COUPEURS DE BOURSES en haillons. Ils
  vous attaquent »* (`TEXTFR/N350/N355.TXT:12-13`), qui bascule sur la zone
  `combat`.

## La pièce

| | |
| --- | --- |
| Œuvre | **Saltarello** (danse de luth) |
| Auteur | **Vincenzo Galilei** (1520-1591), *Fronimo*, **1584** |
| Source | Mutopia Project, [piece-info.cgi?id=110](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=110) |
| Fichiers | `https://www.mutopiaproject.org/ftp/GalileiV/saltarello/saltarello.{ly,mid}` |
| Licence | **domaine public** |
| Effectif d'origine | luth (transcrit guitare) |
| Tempo retenu | **180** à la noire |
| Durée de boucle | 35,8 s |
| Taille | 553 octets |

Le `.mid` et le `.ly` viennent de `SCOSWAMP.MORE/MUSIC/src/`, où ils sont déjà
en place (`SOURCES.md`) : la seule chose qui change ici est le tempo.

## Pourquoi elle convient

Le saltarello *est* la danse d'auberge : un pas sauté, une basse qui bat le
plancher, seize mesures qui reviennent. C'est la seule pièce du lot qui donne
envie de commander à boire, et Courbensaule est le seul endroit du jeu où l'on
dort et où l'on marchande.

**Le tempo est le vrai sujet.** Le disque actuel la rend à **120**, ce qui la
fait traîner : un saltarello à 120 n'est plus un saltarello, c'est une pavane
mal jouée. À **180** (16,67 ticks par noire, arrondi supportable) elle retrouve
son élan, et la boucle tombe à 35,8 s — la bonne longueur pour trois ou quatre
pages passées dans la même clairière.

Réduite à trois voix carrées, la ligne de luth devient une mélodie nue plus une
basse : c'est précisément ce que le format MB1 sait faire de mieux.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/courbensaule/saltarello.mid \
    SCOSWAMP.MORE/MUSIC/propositions/courbensaule/BENTBEAKS.MB.BIN \
    --bpm 180 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/courbensaule/COURBENS.wav
```
