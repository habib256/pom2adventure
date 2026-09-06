# Clairière 34 — Pierres et tronc creux (`hub` 390)

**`LOG.MB.BIN` — 2 006 octets, 45,1 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 105 | « le sol y est ferme ; vous pouvez y pénétrer d'un pas assuré » — des pierres plates de grande taille, un tronc creux massif, deux chemins |
| 330 | le retour : « le sentier est calme, mais vous savez que le tronc a déjà abrité autre chose que des ossements » |
| 390 | les trois sentiers marécageux, tous peu sûrs |

Zone de référence : **`sud`** (`SOUTHSWAMP.MB`, *Sentiers Verts*).

## La pièce

| | |
| --- | --- |
| Titre | **Pierres Plates** |
| Source | composition originale, `tronc.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | la seule clairière sûre des onze, et elle le dit par le vide, pas par la joie |
| Mode | **do éolien** (do ré mi♭ fa sol la♭ si♭) |
| Tempo | **150** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (8) — on écoute (1) — A' (7) |
| Durée | 28 mesures à 4/4 = **45,1 s** |
| Taille | **2 006 octets** (tampon de zone : 2 304) |
| Notes | 422 hauteurs + **97 coups de batterie**, **0 abandonnée** |

Le procédé de `sud` est là : marche i-VI-III-VII (Cm-A♭-E♭-B♭) sur un bourdon de
do immobile. Celui de la clairière aussi : l'arpège ne joue que des **quintes à
vide**, la liste `CREUX` remplaçant chaque accord par sa quinte nue.

**Ce que la révision change.**

* **Le tronc est plus creux qu'avant.** Le lit d'accords tenus a cédé sa voix à
  la batterie ; c'est donc le **contre-chant** qui porte désormais la seule
  tierce du morceau, et lui seul qui dise le mode. Tout le reste sonne à vide.
* **Le crochet est le coup sur le bois** : deux noires sur la même hauteur, puis
  une chute de quarte — `do do | sol`. On frappe le tronc pour savoir s'il est
  habité. Énoncé quatre fois (mesures 5, 9 sur mi♭, 22 à l'octave, et par
  l'arpège en réponse).
* **La batterie est faite de toms et presque rien d'autre** : deux coups collés,
  bois sur bois, **jamais de charleston**. La grosse caisse n'entre qu'en B,
  quand on décide d'y regarder de plus près.
* **Une vraie partie B** (mesures 13-20) : le registre monte au la♭ 6 et
  l'harmonie s'installe sur fa mineur et si♭, les deux degrés que A n'a pas.
* **La réponse** : mesures 8, 12 et 16, le chant tient une ronde et les quintes à
  vide rendent le coup.
* **La surprise** : mesure 21, **on frappe et on écoute**. Deux coups de tom, et
  puis plus rien : la batterie disparaît une mesure entière, les cinq voix
  tiennent un do mineur immobile, et personne ne répond du fond du tronc.
* **L'arc** : deux notes d'arpège par mesure à l'intro, huit en A' ; la basse
  passe de la ronde à la croche.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie — le coup sur le bois | G5..A♭6 | 69 |
| 1 | gauche | contre-chant — **la seule tierce du morceau** | G3..C5 | 94 |
| 2 | **gauche** | bourdon de do, une seule note tenue | C2 | 1 |
| 3 | **droite** | l'arpège de quintes à vide, et les trois réponses | C4..A♭5 | 112 |
| 4 | droite | basse | D2..F3 | 146 |
| 5 | **droite** | **BATTERIE** — du bois : tom 68, grosse caisse 15, caisse claire 14 | bruit | 97 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/34-tronc
python3 tronc.py
python3 ../../../midi_to_mb.py tronc.mid LOG.MB.BIN \
    --bpm 150 --max 2304 --wav TRONC.wav
```
