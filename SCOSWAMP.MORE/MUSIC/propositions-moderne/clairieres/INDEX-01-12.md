# Clairières 1 à 12 — une musique par clairière

Douze compositions originales, écrites avec `../compose.py`, converties par
`../../midi_to_mb.py`, sous **GPL v3** comme le reste du dépôt. Chacune est une
**variation dans la couleur de sa zone** — même famille de mode, même procédé
identifiable — mais avec son propre thème, son propre caractère tiré des pages
de la clairière, et sa propre forme.

Le `.wav` de chaque dossier **est** ce que la Mockingboard jouera : six voix,
deux puces, la même réduction, le même tempo, la même stéréo. C'est le seul
objet à écouter pour juger ; il n'est pas suivi par git.

> **Révision.** Les douze pièces ont été réécrites. Elles ont toutes gagné
> **une batterie**, **un crochet mélodique énoncé au moins deux fois**, **une
> réponse écrite entre la voix 0 et la voix 3**, **un rythme harmonique
> variable**, **une surprise** et **un silence général**. Toutes ont accéléré.
> Le mode, la tonique, le procédé de zone et le caractère de chaque clairière
> sont inchangés : ce sont des acquis.

---

## 1. Les douze pièces

| # | `hub` | Clairière | Zone | Fichier disque | Pièce | Mode | bpm | Durée | Octets |
| ---: | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | 078 | Route de Courbensaule | `village` | `BENTBEAKS.MB` | **La Route des Trois Auberges** | ré mixolydien | **176** | 38,2 s | **2 276** |
| 2 | 234 | Le Patrouilleur vert | `nord` | `PATROLLER.MB` | **La Question du Patrouilleur** | la éolien | 162 | 41,5 s | 2 185 |
| 3 | 084 | Le Maître des Jardins | `nord` | `GARDENS.MB` | **L'Amulette de Fleur** | ré dorien | 144 | 43,3 s | 2 042 |
| 4 | 232 | Les deux loups | `nord` | `WOLVES.MB` | **Deux Paires d'Yeux** | si éolien | 172 | 38,4 s | **2 253** |
| 5 | 218 | Feu follet à l'orée | `nord` | `WILLOWISP.MB` | **La Lumière qui Recule** | sol éolien | 154 | 40,5 s | 2 083 |
| 6 | 121 | Le croisement | `nord` | `CROSSROADS.MB` | **Quatre Chemins** | mi éolien | 150 | 44,8 s | 2 177 |
| 7 | 161 | Le Géant | `nord` | `GIANT.MB` | **Il Est Interdit de Passer** | do éolien | **138** | 41,7 s | **1 624** |
| 8 | 019 | Clairière aux brigands | `nord` | `BRIGANDS.MB` | **Cinq Voix derrière l'Arbre** | ré éolien → **majeur** | **180** | **37,3 s** | **2 258** |
| 9 | 153 | Le bassin de Vase | `danger` | `MUD.MB` | **Ce qui Sort du Bassin** | ré phrygien | 138 | **45,2 s** | 1 594 |
| 10 | 088 | Scorpion et nain | `danger` | `DWARFSCORP.MB` | **Les Pinces et l'Os** | la phrygien | **184** | **36,5 s** | 2 076 |
| 11 | 202 | Le nid de l'Aigle | `nord` | `EAGLE.MB` | **Le Grand Nid** | fa♯ éolien | 156 | 43,1 s | 1 682 |
| 12 | 270 | Sables mouvants | `danger` | `QUICKSAND.MB` | **Le Sol qui Cède** | fa phrygien | 144 | 43,3 s | 1 920 |

**Total : 24 170 octets** sur le volume, pour douze fichiers — **4 824 notes de
hauteur et 985 coups de batterie**. Ce qui coûte n'est pas le nombre de pièces
mais la plus grosse : **`BENTBEAKS.MB`, 2 276 octets**, à **28 octets** de la
limite du tampon de zone (2 304).

⚠ Trois pièces sont serrées et doivent être **reconverties avant d'être crues**
après toute retouche : `COURBENS` (marge 28), `BRIGANDS` (46), `LOUPS` (51).
Les neuf autres ont entre 119 et 710 octets de marge.

Douze modes, douze toniques, **aucun doublon** : chaque clairière a sa propre
paire mode/tonique, et aucune ne reprend celle de sa zone sauf `CROISEMENT`,
délibérément en mi éolien parce qu'il est le centre du Marais nord.

Toutes les pièces : **cinq parties de hauteur plus la batterie, polyphonie
maximale 5/5, zéro note abandonnée par la réduction**, tempo entre 138 et 184,
boucle entre 36,5 et 45,2 s. `verifier.py` conclut **`OK` sur les douze**.

## 2. Ce que la révision a apporté, pièce par pièce

Le brief était le même pour les douze : un crochet, une vraie partie B, une
réponse au chant, un rythme harmonique qui varie, **une surprise**, des cadences
affirmées, un arc de densité, une fin qui prépare la boucle, et une batterie
là où elle porte.

| # | Le crochet | La surprise | Le silence général |
| ---: | --- | --- | :---: |
| 1 | `ré fa♯ la ré' do' / la sol fa♯`, 4 fois | **fa majeur** : la troisième auberge ment | ½ temps, mes. 20 |
| 2 | la ronde chantée, 4 fois | **mi majeur** : la pique se lève | 1 temps, mes. 20 |
| 3 | la fleur au sommet, 3 fois | **si bémol** : dorien → éolien, la fleur se referme | 2 temps, mes. 18 |
| 4 | `si ré fa♯ ré si / do♯ si fa♯`, 3 fois | **une mesure à 2/4** — la seule des douze | 1½ temps, mes. 20 |
| 5 | `sol si♭ ré' do' si♭ / la sol ré`, 3 fois | la cellule jouée **à l'envers** | 1½ temps, mes. 18 |
| 6 | la tête de panneau, **4 fois, une par route** | **si majeur** : la route de l'ouest ment | 1½ temps, mes. 22 |
| 7 | `do mi♭ sol la♭ sol / sol mi♭ do`, 3 fois | **ré bémol majeur**, le napolitain | 1½ temps, mes. 18 |
| 8 | `la ré' do' la fa / sol fa mi ré`, 3 fois | la pièce **finit en ré majeur** | 1½ temps, mes. 20 |
| 9 | le demi-ton chanté, 3 fois | **le bourdon monte d'un demi-ton** pendant tout le B | 1½ temps, mes. 12 |
| 10 | la pince, 3 fois | **la batterie s'arrête** huit mesures | 1½ temps, mes. 20 |
| 11 | le rythme du vol chanté, 3 fois | **la cellule se retourne** : il plonge | 1½ temps, mes. 20 |
| 12 | la chute, 3 fois | **l'arpège remonte**, une mesure, puis retombe deux fois plus vite | 1½ temps, mes. 20 |

Le **silence général** est le même dispositif partout : les cinq parties de
hauteur se taisent ensemble et repartent ensemble, la batterie reste seule
dedans. C'est sans risque pour la stéréo — après un silence total, la réduction
réattribue les cinq voix dans le bon ordre — et c'est le seul moyen d'obtenir
un vrai vide sur une machine qui n'a pas de volume par note.

La **réponse** est partout la même idée : trois ou quatre fois par pièce, le
chant tient une ronde et la voix 3, à droite, répond par une figure écrite dans
la bande juste sous lui. Question à gauche, réponse à droite.

## 3. La batterie

Le lecteur bat maintenant le canal de bruit de la seconde puce. Les notes du
canal MIDI 10 deviennent des paquets NOISE sur la **voix 5, à droite** ; il ne
reste alors que **cinq** parties de hauteur, `0, 1, 2` à gauche et `3, 4` à
droite. Chaque coup coûte trois octets, comme une note.

Il a donc fallu retirer une partie à chacune des douze pièces :

- **les neuf pièces `village` et `nord`** ont retiré le **bourdon** — la grosse
  caisse en tient lieu, et c'est un gain : un affût ne bourdonne pas, il bat.
  Cinq parties : chant, ostinato, contre-chant, accords tenus, basse ;
- **les trois pièces `danger`** (9, 10, 12) ont retiré la **voix d'accords
  tenus**, pas le bourdon, exactement comme `INDEX.md § 3.2` le demande : le
  bourdon immobile fait le caractère de la zone. Cinq parties : chant, cellule,
  contre-chant, basse, bourdon — et comme le bourdon est la partie la plus
  grave, **il prend la voix 2 à gauche et pousse la basse à droite, voix 4**.
  C'est audible et c'est voulu : le fond à gauche, le mouvement à droite.

| # | Le kit | Coups | Occupation | Ce qu'elle fait |
| ---: | --- | ---: | ---: | --- |
| 1 | K S H O T C | 101 | 11 % | le tambourin de marche, entrée au A, cellule pleine au A' |
| 2 | K S H C | 94 | 8 % | marche de patrouille — mais le charleston bat **toutes les trois croches**, comme la ronde |
| 3 | K H T C | 59 | **4 %** | presque rien : deux charlestons, un tom, une cymbale |
| 4 | K S T C | 69 | 9 % | le cœur qui bat, puis le galop, puis la marche du recul |
| 5 | K S H O C | 80 | 11 % | elle recule aussi : **toutes les cinq croches**, jamais sur le temps |
| 6 | K S H T C | 88 | 8 % | **une batterie par direction**, quatre en tout |
| 7 | K S H T C | 77 | 9 % | le pas : grosse caisse au 1, tom au 3, et rien d'autre |
| 8 | K S H O C | **114** | **12 %** | le tambourin de foire, contretemps, intro muette |
| 9 | K T C | 83 | 10 % | le cœur qui bat sourd — **aucun charleston** |
| 10 | K S H C | 89 | 8 % | le cliquetis, et **rien du tout** pendant les huit mesures du Nain |
| 11 | K O C | **34** | **7 %** | trois grosses caisses, le reste en charleston ouvert et cymbale |
| 12 | K T C | 97 | 11 % | un tom qui accélère avec le terrain — **pas un charleston** |

Deux extrêmes voulus : `AIGLE` avec trente-quatre coups et pas une caisse
claire, `BRIGANDS` avec cent quatorze. Une clairière contemplative n'a pas
besoin d'être battue.

## 4. Les procédés, zone par zone

| Zone | Procédé de la zone | Ce que les clairières en font |
| --- | --- | --- |
| `village` | arpège de croches, basse balancée | **1** garde les deux, descend d'une quinte, et le tambourin répond au chant quatre fois |
| `nord` | un ostinato **fixe** sous des accords qui bougent | **2** le met à trois pas et le fait ralentir au B, **3** lui donne la sixte majeure et la lui retire quatre mesures, **4** en fait deux qui se relaient, **5** le met à cinq croches et le joue à l'envers une fois, **6** en met un par direction et le fait mentir à l'ouest, **7** le met en noires, **8** lui donne cinq notes, **11** lui donne un rythme de vol qu'il retourne pour plonger |
| `danger` | demi-ton phrygien, bourdon immobile, crescendo par la densité | **9** fait du demi-ton la cellule, la resserre trois fois, et déplace le bourdon d'un demi-ton, **10** arrête tout au milieu, **12** retourne l'arpège vers le bas et le fait remonter une seule mesure |

## 5. Refabriquer les douze

Depuis `SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres` :

```sh
M=../../../midi_to_mb.py
(cd 01-courbens   && python3 courbens.py   && python3 $M courbens.mid   BENTBEAKS.MB.BIN   --bpm 176 --max 2304 --wav COURBENS.wav)
(cd 02-patrouil   && python3 patrouil.py   && python3 $M patrouil.mid   PATROLLER.MB.BIN   --bpm 162 --max 2304 --wav PATROUIL.wav)
(cd 03-jardins    && python3 jardins.py    && python3 $M jardins.mid    GARDENS.MB.BIN    --bpm 144 --max 2304 --wav JARDINS.wav)
(cd 04-loups      && python3 loups.py      && python3 $M loups.mid      WOLVES.MB.BIN      --bpm 172 --max 2304 --wav LOUPS.wav)
(cd 05-feufollet  && python3 feufollet.py  && python3 $M feufollet.mid  WILLOWISP.MB.BIN  --bpm 154 --max 2304 --wav FEUFOLLET.wav)
(cd 06-croisement && python3 croisement.py && python3 $M croisement.mid CROSSROADS.MB.BIN --bpm 150 --max 2304 --wav CROISEMENT.wav)
(cd 07-geant      && python3 geant.py      && python3 $M geant.mid      GIANT.MB.BIN      --bpm 138 --max 2304 --wav GEANT.wav)
(cd 08-brigands   && python3 brigands.py   && python3 $M brigands.mid   BRIGANDS.MB.BIN   --bpm 180 --max 2304 --wav BRIGANDS.wav)
(cd 09-vase       && python3 vase.py       && python3 $M vase.mid       MUD.MB.BIN       --bpm 138 --max 2304 --wav VASE.wav)
(cd 10-scorpnain  && python3 scorpnain.py  && python3 $M scorpnain.mid  DWARFSCORP.MB.BIN  --bpm 184 --max 2304 --wav SCORPNAIN.wav)
(cd 11-aigle      && python3 aigle.py      && python3 $M aigle.mid      EAGLE.MB.BIN      --bpm 156 --max 2304 --wav AIGLE.wav)
(cd 12-sables     && python3 sables.py     && python3 $M sables.mid     QUICKSAND.MB.BIN     --bpm 144 --max 2304 --wav SABLES.wav)
```

**Les tempos ont changé** : ce bloc n'est plus interchangeable avec l'ancien.
Une pièce convertie au mauvais `--bpm` sonnera juste mais ne durera pas ce que
le tableau annonce, et le tampon peut déborder.

Le bloc entier se recolle tel quel dans un shell ; avec `set -e` il s'arrête à la
première erreur. `--max 2304` fait **échouer** la conversion au lieu de livrer un
flux qui déborderait le tampon de zone à l'exécution. `--vol` reste au défaut
`13,11,11,12,11,11` partout, comme pour les dix pièces de zone.

Pour contrôler ce que la carte fera réellement d'une pièce — voix par voix, côté
par côté, batterie comprise :

```sh
python3 ../verifier.py 11-aigle/aigle.mid --bpm 156
```

Les douze finissent par `OK`.

## 6. Ce que l'adoption demanderait

Aucun texte, aucun code, aucun `Makefile` n'a été touché : ce dossier est un
atelier. Adopter une de ces douze pièces demanderait, **pour chaque page de la
clairière**, de remplacer sa ligne `MU NORTHSWAMP.MB` / `MU DANGER.MB` /
`MU VILLAGE.MB` par le fichier de la clairière, et de copier le `.MB.BIN` sur le
volume. Les pages concernées sont listées en tête de chaque `README.md`.

Trente-cinq musiques de clairière remplaceraient les cinq thèmes de zone par
trente-cinq fichiers d'environ deux kilo-octets, soit de l'ordre de 70 Ko sur les
~28 Mo libres : le volume n'est pas la question. La question est le tampon, qui
reste de **2 304 octets par zone** et qu'aucune de ces douze pièces ne dépasse.
