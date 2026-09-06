# Zone `nord` — la forêt profonde, au-delà de la rivière

**Fichier proposé : `NORTHSWAMP.MB` (`NORTHSWAMP.MB.BIN`, 1 058 octets, 58,4 s de boucle)**

C'est la moitié nord de la carte (`y = 0…2`), là où *« le sol devient plus sec et
la végétation des marais cède place à une forêt profonde »*
(`TEXTFR/N050/N092.TXT:4-5`). On n'y entre que par le pont.

## Clairières couvertes (8)

| `hub` | `id` | Titre | Case | Pages |
| --- | --- | --- | --- | --- |
| **234** | 19 | Le Patrouilleur vert | (2,0) | 170, 363, 234 |
| **084** | 27 | Le Maître des Jardins | (3,0) | 305, 238, 84, 117, 251, 283, 396 |
| **232** | 11 | Les deux loups | (4,0) | 92, 232, 247, 389 |
| **218** | 15 | Feu follet à l'orée | (1,1) | 218, 249 |
| **121** | — | Le croisement | (2,1) | 121 |
| **161** | 7 | Le Géant | (4,1) | 275, 342, 161, 103, 244 |
| **019** | 9 | Clairière aux brigands | (0,2) | 65, 343, 019 |
| **202** | 16 | Le nid de l'Aigle | (3,2) | 350, 331, 25, 112, 202 |

Ambiances :

- clairière 27 : *« une agréable clairière […] trop belle pour être entièrement
  naturelle »*, *« cet homme est animé d'intentions amicales »*
  (`TEXTFR/N300/N305.TXT:6,9,16-17`) — le seul lieu franchement beau du nord ;
- clairière 16 : *« un nid gigantesque »*, *« un AIGLE énorme qui vole
  au-dessus »* (`TEXTFR/N350/N350.TXT:5-6,10`) ;
- clairière 19 : *« Le sentier étroit serpente entre de gros rochers dans un
  brouillard épais »* (`TEXTFR/N150/N170.TXT:4`) ;
- clairière 9 : *« cinq hommes […] ce sont probablement des BRIGANDS. L'Anneau
  de Cuivre reste froid »* (`TEXTFR/N050/N065.TXT:8-9`) — tendus, pas hostiles.

## La pièce

| | |
| --- | --- |
| Œuvre | **Tmeiskin** (« Tmeiskin was jonck ») |
| Auteur | **Johannes Japart** (fl. 1474-1507), école franco-flamande |
| Source | Mutopia Project, [piece-info.cgi?id=1734](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1734) |
| Fichiers | `https://www.mutopiaproject.org/ftp/JapartJ/27-tmeiskin/27-tmeiskin.mid`, `.../27-tmeiskin-lys.zip` (déballé ici en `.orig.ly` et `.mod.ly`) |
| Licence | **domaine public** (Creative Commons No Rights Reserved) |
| Effectif d'origine | flûtes à bec (consort) |
| Tempo retenu | **200** à la noire (15 ticks par noire : tombe juste) |
| Durée de boucle | 58,4 s |
| Taille | 1 058 octets — **la plus grosse pièce du lot**, elle fixe la taille du tampon |

## Pourquoi elle convient

C'est la seule pièce purement **instrumentale et polyphonique** du lot : trois
lignes de flûte qui s'imitent, se croisent, ne se posent jamais en même temps.
Sur trois ondes carrées, cette écriture-là devient un tissu — l'oreille suit
tantôt une voix tantôt l'autre — et c'est exactement l'effet d'une forêt
profonde où l'on entend des choses sans les voir.

Elle est aussi **la plus ancienne** du lot (avant 1507), donc la plus modale : ni
majeur ni mineur franc, une couleur suspendue qui n'annonce pas si le lieu est
sûr. Le nord alterne des clairières bienveillantes (le Maître des Jardins) et des
guet-apens (le Géant, les Brigands) : une musique qui ne tranche pas est la
bonne.

**Tempo.** À 160 elle tenait 73 s, ce qui est long et mou. À **200** — un tempo
de danse instrumentale, et 15 ticks exacts par noire — la polyphonie devient
vive et la boucle tombe à 58 s.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/nord/27-tmeiskin.mid \
    SCOSWAMP.MORE/MUSIC/propositions/nord/NORTHSWAMP.MB.BIN \
    --bpm 200 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/nord/MARAISNO.wav
```

> **Attention taille.** 1 058 octets est le maximum du lot. Si l'on réduit
> `MUSIC_BUF_SIZE` (aujourd'hui 2 560, `SCOSWAMP/SRC/music.h:11`), c'est cette
> pièce qui donne le plancher : **1 280 octets**, pas moins.
