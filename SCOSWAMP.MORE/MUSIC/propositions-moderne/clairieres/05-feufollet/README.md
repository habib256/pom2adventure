# Clairière 5 — Feu follet à l'orée (`hub` 218, case 1,1)

**`WILLOWISP.MB.BIN` — 2 083 octets, 40,5 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 218 | Feu follet à l'orée | la faible lueur qui flotte à l'ouest, recule, et révèle un sentier boueux |
| 249 | Saut dans l'obscurité | le test de CHANCE, le bras blessé, la clairière quand même |

## La pièce

| | |
| --- | --- |
| Titre | **La Lumière qui Recule** |
| Source | composition originale, `feufollet.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | un piège qui ne menace pas. Rien n'appuie, rien ne pèse ; la lueur avance de deux pas et se dérobe |
| Mode | **sol mineur éolien** (sol la si♭ do ré mi♭ fa) |
| Tempo | **154** à la noire (auparavant 150) |
| Forme | intro (4) — A (8) — B (8) — A' (6) |
| Durée | 26 mesures à 4/4 = **40,5 s** |
| Taille | **2 083 octets** (marge 221 sur le tampon de zone) |
| Notes | 405 de hauteur + **80 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures, `sol si♭ ré' do' si♭ / la sol ré` : il monte à
  la quinte et redescend sans jamais toucher la tonique en haut. Énoncé trois
  fois ;
- **une réponse** aux mesures 10, 18 et 26 : le chant tient, la lueur — voix 3,
  à droite — répond à sa place. On appelle à gauche, ça répond à droite, et
  c'est toujours plus loin ;
- **la surprise** : mesures 15-16, la cellule est jouée **à l'envers**, note pour
  note. La lueur revient sur ses pas, une seule fois du morceau. Puis mesure 18,
  **un temps et demi de silence général** — elle s'éteint — et tout repart
  ensemble. La mesure 19 pose en plus un **fa dièse** que le mode n'a pas ;
- **le rythme harmonique varie** : grille à la demi-mesure ; l'orée tient un
  accord par mesure, le sentier en prend deux ;
- **le tempo monte de 150 à 154**.

## La batterie

**Elle recule aussi.** Le charleston ouvert et la grosse caisse battent
**toutes les cinq croches**, sur exactement la même grille que la cellule, donc
jamais sur le temps ; ils ne retombent d'aplomb avec la caisse claire qu'une
mesure sur cinq. Rien dans l'orée. Et aux six dernières mesures la batterie
tombe d'aplomb en même temps que la lueur : `K.H.S.H.`, quatre temps carrés,
c'est le piège qui se referme. Le bourdon de ré a cédé la place.

## Ce qui la relie à `nord`, et ce qui l'en sépare

L'ostinato de la zone est fixe **et** carré : il tombe toujours au même endroit
de la mesure. Celui-ci est fixe en notes — ré - sol - si♭ - la - fa — et jamais
au même endroit, parce que sa cellule fait **cinq croches** dans une mesure à
quatre temps. À chaque tour la figure recule d'une croche ; elle ne retombe
d'aplomb qu'une mesure sur cinq. Aux six dernières mesures elle passe à quatre
croches et s'immobilise : la lueur attend au bord du sentier boueux, et c'est le
seul endroit du morceau où l'on sait où elle est.

## Les six voix, mesurées

`python3 ../../verifier.py feufollet.mid --bpm 154`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | D5..A♯6 | 77 |
| 1 | gauche | le contre-chant, et les notes hautes des accords | A3..A♯4 | 99 |
| 2 | **gauche** | la basse, posée et lâchée | F2..G3 | 67 |
| 3 | **droite** | **la lueur**, et les réponses | D4..D5 | 112 |
| 4 | droite | les accords tenus | F3..A♯4 | 50 |
| 5 | **droite** | **LA BATTERIE** — grosse caisse 25, charleston ouvert 22, caisse claire 16, charleston fermé 16, cymbale 1 | bruit | 80 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

C'est la seule des douze où la batterie ne bat pas la mesure : vingt-deux des
quatre-vingts coups tombent sur une grille de cinq croches, et l'on ne peut pas
taper du pied dessus. C'est le sujet.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/05-feufollet
python3 feufollet.py
python3 ../../../midi_to_mb.py feufollet.mid WILLOWISP.MB.BIN \
    --bpm 154 --max 2304 --wav FEUFOLLET.wav
```
