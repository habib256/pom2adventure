# Clairières 13 à 24 — douze musiques, une par clairière

Douze **compositions originales** (GPL v3), écrites avec `../compose.py` et
converties par `../../midi_to_mb.py` — le même code que le disque. Chacune est
une **variation dans la couleur de sa zone** : même famille de mode, même
procédé identifiable, mais son propre thème et son propre caractère, tirés des
pages de la clairière.

Le `.wav` de chaque dossier est l'**aperçu fidèle** de ce que la Mockingboard
jouera : `midi_to_mb.py` rejoue le flux écrit comme `music.s` le joue (volumes
sur la table logarithmique de l'AY, fondu d'entrée de 0,9 s, coupure nette au
OFF, bruit de la voix 5, puce 1 à gauche et puce 2 à droite) puis synthétise les
deux AY comme POM2. C'est un modèle : rien n'a encore été écouté sur une carte.
Il n'est pas suivi par git.

**Cette version est la seconde.** Les douze pièces ont été révisées : elles ont
maintenant une **batterie** (sauf une, et c'est un choix), un **crochet** énoncé
au moins deux fois, une **réponse** entre les voix 0 et 3, un rythme harmonique
qui varie, une surprise par pièce, des cadences affirmées, un arc de densité et
une fin qui prépare la boucle. Le procédé de zone et le caractère de chaque
clairière sont inchangés : ce sont des acquis.

## Le tableau

| # | `hub` | Clairière | Dossier | Fichier | Pièce | Mode | bpm | Durée | Octets | Coups |
| ---: | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 13 | 295 | La Rivière Croupie | `13-croupie` | `STAGNANT.MB.BIN` | **La Berge aux Crocodiles** | sol dorien | 136,4 | 42,5 s | 1 595 | 45 |
| 14 | 183 | Sommet de la falaise | `14-falaise` | `CLIFF.MB.BIN` | **Le Ciel s'Ouvre** | si dorien | **150** | 38,7 s | 1 447 | **—** |
| 15 | 045 | Le pont sur la Croupie | `15-pont` | `BRIDGE.MB.BIN` | **Le Seul Passage** | si♭ dorien | **150** | 41,9 s | 1 945 | 85 |
| 16 | 304 | Le Perroquet / la Maîtresse des Oiseaux | `16-oiseaux` | `BIRDS.MB.BIN` | **La Maîtresse des Oiseaux** | mi dorien | 166,7 | 40,6 s | 2 003 | 73 |
| 17 | 094 | La brume fétide | `17-brume` | `MIST.MB.BIN` | **La Brume Fétide** | do éolien | 125 | 42,5 s | 1 399 | 36 |
| 18 | 179 | Le pique-nique suspect | `18-piquenique` | `PICNIC.MB.BIN` | **Le Repas du Voleur** | fa dorien | 166,7 | 43,5 s | 1 865 | **120** |
| 19 | 319 | La clairière des scorpions | `19-scorpions` | `SCORPIONS.MB.BIN` | **La Nuée** | ré phrygien | **187,5** | 31,0 s | 2 022 | 108 |
| 20 | 047 | Trois chemins herbeux | `20-herbeux` | `GRASSLAND.MB.BIN` | **Trois Chemins Herbeux** | ré dorien | **150** | 35,5 s | 1 493 | 48 |
| 21 | 031 | Bassin de cristal | `21-cristal` | `CRYSTAL.MB.BIN` | **Le Bassin de Cristal** | do dorien | **150** | 41,9 s | 2 053 | 65 |
| 22 | 367 | Les Fleurs d'Angoisse | `22-angoisse` | `DREAD.MB.BIN` | **Les Fleurs d'Angoisse** | mi phrygien | **150** | 38,7 s | 1 772 | 75 |
| 23 | 348 | La Licorne | `23-licorne` | `UNICORN.MB.BIN` | **La Licorne Blessée** | fa éolien | **136,4** | 42,5 s | 1 601 | 51 |
| 24 | 227 | La clairière des combats | `24-arene` | `ARENA.MB.BIN` | **Ce qui Reste du Combat** | mi éolien | **166,7** | 40,6 s | **2 128** | 99 |

Les tempos en gras ont été **augmentés** à la révision. Tous les tempos ont
ensuite été recalés sur un nombre entier de ticks de 50 Hz par temps (16, 18,
20, 22 ou 24) : deux notes de même valeur durent enfin le même nombre de ticks.
Onze pièces ont bougé, de −5,3 à +4,2 %. Les douze durées sont entre **31,0 et
43,5 s**, dans la fenêtre de 30 à 50 s.

**Total : 21 323 octets** sur le volume, dont **805 coups de batterie**
(2 415 octets, soit 11 % du flux). Ce qui coûte, c'est la plus grosse :
`ARENA.MB.BIN`, **2 128 octets**, soit **176 octets de marge** sur le tampon de
zone (2 304). Les onze autres ont entre 251 et 905 octets de marge. Aucune des
douze n'abandonne une seule note à la réduction : la polyphonie maximale est de
**5** exactement pour les onze pièces avec batterie, **6** pour `falaise`, et
`midi_to_mb.py` affiche « 0 abandonnées » sur les douze.

## La batterie, pièce par pièce

Elle prend la **voix 5, à droite** ; il ne reste alors que **cinq** parties de
hauteur. Dans les onze pièces qui en ont une, c'est la **voix d'accords tenus**
qui a cédé la place, jamais le bourdon : le bourdon — sur la quinte dans la zone
`riviere`, sur la tonique dans `sud` et `danger` — est le procédé identifiable
de la zone, et il migre simplement à la **voix 2, à gauche**. La grosse caisse
et la basse se retrouvent donc ensemble à droite, le chant, le contre-chant et le
bourdon à gauche.

| # | ce qu'elle joue | où elle se tait |
| ---: | --- | --- |
| 13 | un **cœur sourd** : caisse au 1, tom au 3 une mesure sur deux | mesures 17-18, sur le mi♭ |
| 14 | **rien du tout** — voir ci-dessous | partout |
| 15 | une **marche** : le pas sur les planches, `K.H.S.H.` | mesures 17-18, sur le piège |
| 16 | un **tambourin** léger, un charleston ouvert par deux mesures en B | presque tout B |
| 17 | un **cœur sourd**, le plus lent des douze — 36 coups en tout | mesures 15-16, sur le ré♭ |
| 18 | une **valse**, `K.H.H.` — puis l'**hémiole**, 1-3-5 sur six temps | nulle part : elle contredit la mesure au lieu de s'arrêter |
| 19 | un **galop**, caisse sur le temps et sur la croche d'après | mesure 17, le gel |
| 20 | une marche qui **change à chaque sentier** et disparaît au troisième | mesures 17-18 |
| 21 | un charleston seul, la **démarche chaloupée** du Lézard, le charleston ouvert de l'éclat | l'intro |
| 22 | le **crescendo par la densité** en cinq paliers, jusqu'au tremblement de toms | l'intro |
| 23 | **un sabot toutes les deux mesures**, puis la charge, puis plus rien | l'intro et la fin |
| 24 | une **marche martiale** calée sur le pointé du chant | mesures 18-19, « le silence pèse » |

**Pourquoi `falaise` n'en a pas.** Un seul coup de bruit coûte la voix 5 et
ramène la pièce à cinq parties de hauteur. Au sommet d'une falaise, c'est la
largeur qui compte, pas la frappe : les six voix sont gardées, et c'est la seule
des douze à conserver **à la fois** le bourdon et la voix d'accords tenus. C'est
aussi la seule dont la stéréo mesure exactement **50/50**.

## Ce que chaque pièce garde de sa zone, ce qu'elle y ajoute, et sa surprise

| # | Zone | Procédé de la zone, conservé | Ce qui appartient à la clairière | La surprise |
| ---: | --- | --- | --- | --- |
| 13 | `riviere` | dorien, arpège continu, **bourdon sur la quinte** (ré) | basse brève-longue, la mâchoire | **mi♭ majeur** mes. 17-18, et la batterie qui s'arrête |
| 14 | `riviere` | dorien, **bourdon sur la quinte** (fa♯) | arpège à **quatre sons**, six voix, pas de batterie | **la pédale descend au mi** mes. 15-18 |
| 15 | `riviere` | dorien, arpège continu, **bourdon sur la quinte** (fa) | **quatre noires marchées** : on traverse | **sol♭ majeur** mes. 17-18, le sol dorien éteint |
| 16 | `sud` | **bourdon de tonique** (mi), marche modale large | dorien, **arpège en sauts de quinte** | **do naturel** mes. 17-18 contre le do♯ du mode |
| 17 | `sud` | éolien, **bourdon de tonique** (do) | la **descente**, mesure après mesure | **ré♭ majeur** mes. 15-16, à un demi-ton du bourdon |
| 18 | `sud` | **bourdon de tonique** (fa), marche modale | le **3/4**, seule valse des 35 | l'**hémiole** mes. 25-26 : trois pas sur six temps |
| 19 | `danger` | **phrygien** (mi♭ contre ré), **bourdon de tonique** | les **doubles croches** du grouillement | **le silence** mes. 17 : tout s'arrête une mesure |
| 20 | `sud` | **bourdon de tonique** sur le même ré que la zone | dorien, **trois phrases**, une par sentier | **si♭ majeur** mes. 18, le si dorien fermé |
| 21 | `sud` | **bourdon de tonique** (do), marche modale | la **sixte majeure**, l'éclat en doubles croches | le mode **bascule en majeur** mes. 21-22 |
| 22 | `danger` | **phrygien** (fa contre mi), crescendo **par la densité** | tierces douces, **tremblement** fa-mi-fa | **la pédale monte au fa** mes. 17-18 |
| 23 | `sud` | la **marche i-VI-III-VII** transposée ; bourdon (fa) | A **sans une croche** ; B au **rythme pointé** | **fa majeur** mes. 19 : l'animal vu en entier |
| 24 | `sud` | la **marche i-VI-III-VII** (Em-C-G-D), bourdon (mi) | le **rythme pointé** à chaque mesure | **deux mesures muettes**, puis un **fa majeur** |

Les douze surprises sont de cinq espèces différentes — rupture modale (13, 15,
16, 17, 20, 21, 23, 24), déplacement de pédale (14, 22), silence (19, 24),
mesure impaire (18) — et aucune pièce n'a la même que sa voisine de zone.

## Les six voix

Le plan du dossier tient, avec un déplacement dû à la batterie :

| voix | côté | sans batterie (`falaise`) | avec batterie (les onze autres) |
| ---: | :---: | --- | --- |
| 0 | **gauche** | la mélodie, seule | la mélodie, seule |
| 1 | gauche | une voix médiane | le contre-chant, et l'arpège quand il passe sous lui |
| 2 | **gauche** | la basse | **le bourdon**, seul, immobile |
| 3 | **droite** | l'arpège | l'arpège **et les réponses au chant** |
| 4 | droite | les accords tenus | **la basse** |
| 5 | **droite** | le bourdon | **la batterie** |

`Piece.write()` ne signale de trou sur aucune des douze : chaque partie sonne sur
chaque temps fort, en attaquant ou en tenant. La stéréo mesurée est de 59/41 ou
60/40 sur les onze pièces avec batterie — la batterie n'occupe que 5 à 14 % du
temps sonnant — et de **50/50** sur `falaise`.

## Refabriquer les douze

```sh
cd /Users/gistair/src/pom2adventure/SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres
M=../../../midi_to_mb.py
(cd 13-croupie    && python3 croupie.py    && python3 $M croupie.mid    STAGNANT.MB.BIN    --bpm 136.364 --max 2304 --wav CROUPIE.wav)
(cd 14-falaise    && python3 falaise.py    && python3 $M falaise.mid    CLIFF.MB.BIN    --bpm 150 --max 2304 --wav FALAISE.wav)
(cd 15-pont       && python3 pont.py       && python3 $M pont.mid       BRIDGE.MB.BIN       --bpm 150 --max 2304 --wav PONT.wav)
(cd 16-oiseaux    && python3 oiseaux.py    && python3 $M oiseaux.mid    BIRDS.MB.BIN    --bpm 166.667 --max 2304 --wav OISEAUX.wav)
(cd 17-brume      && python3 brume.py      && python3 $M brume.mid      MIST.MB.BIN      --bpm 125 --max 2304 --wav BRUME.wav)
(cd 18-piquenique && python3 piquenique.py && python3 $M piquenique.mid PICNIC.MB.BIN --bpm 166.667 --max 2304 --wav PIQUENIQUE.wav)
(cd 19-scorpions  && python3 scorpions.py  && python3 $M scorpions.mid  SCORPIONS.MB.BIN  --bpm 187.5 --max 2304 --wav SCORPIONS.wav)
(cd 20-herbeux    && python3 herbeux.py    && python3 $M herbeux.mid    GRASSLAND.MB.BIN    --bpm 150 --max 2304 --wav HERBEUX.wav)
(cd 21-cristal    && python3 cristal.py    && python3 $M cristal.mid    CRYSTAL.MB.BIN    --bpm 150 --max 2304 --wav CRISTAL.wav)
(cd 22-angoisse   && python3 angoisse.py   && python3 $M angoisse.mid   DREAD.MB.BIN   --bpm 150 --max 2304 --wav ANGOISSE.wav)
(cd 23-licorne    && python3 licorne.py    && python3 $M licorne.mid    UNICORN.MB.BIN    --bpm 136.364 --max 2304 --wav LICORNE.wav)
(cd 24-arene      && python3 arene.py      && python3 $M arene.mid      ARENA.MB.BIN      --bpm 166.667 --max 2304 --wav ARENE.wav)
```

Le bloc entier se recolle tel quel dans un shell. **Les bpm ont changé sur huit
des douze pièces** : ce bloc est la référence, pas l'ancien. `--max 2304` est le
tampon de zone : la conversion **échoue** au lieu de livrer un flux qui
déborderait à l'exécution. `--vol` reste à `10,8,8,9,8,8`, le défaut de
`midi_to_mb.py` : sur la table logarithmique de l'AY, la mélodie (voix 0) sort à
+7 dB et le contre-chant (voix 3) à +4 dB de l'accompagnement, et non +2 dB
comme le faisait entendre l'ancien aperçu linéaire, sur les douze.

Vérifier une pièce, voix par voix — les douze doivent conclure par `OK` :

```sh
cd /Users/gistair/src/pom2adventure/SCOSWAMP.MORE/MUSIC/propositions-moderne
python3 verifier.py clairieres/13-croupie/croupie.mid       --bpm 136.364
python3 verifier.py clairieres/14-falaise/falaise.mid       --bpm 150
python3 verifier.py clairieres/15-pont/pont.mid             --bpm 150
python3 verifier.py clairieres/16-oiseaux/oiseaux.mid       --bpm 166.667
python3 verifier.py clairieres/17-brume/brume.mid           --bpm 125
python3 verifier.py clairieres/18-piquenique/piquenique.mid --bpm 166.667
python3 verifier.py clairieres/19-scorpions/scorpions.mid   --bpm 187.5
python3 verifier.py clairieres/20-herbeux/herbeux.mid       --bpm 150
python3 verifier.py clairieres/21-cristal/cristal.mid       --bpm 150
python3 verifier.py clairieres/22-angoisse/angoisse.mid     --bpm 150
python3 verifier.py clairieres/23-licorne/licorne.mid       --bpm 136.364
python3 verifier.py clairieres/24-arene/arene.mid           --bpm 166.667
```
