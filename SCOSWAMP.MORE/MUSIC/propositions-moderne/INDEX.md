# Propositions musicales — style **fantasy moderne**, six voix, stéréo

Ce dossier est un **atelier**, pas le disque. Rien n'est copié dans
`SCOSWAMP/MUSIC/` tant que le propriétaire n'a pas écouté et tranché. Il propose
une alternative complète au dossier voisin `../propositions/`, qui suit la même
carte des zones mais avec un répertoire Renaissance à trois voix.

**Dix pièces, toutes des compositions originales** écrites en Python sans
dépendance (`compose.py` + un script par zone), donc sous la **GPL v3** comme le
reste du dépôt. Aucune œuvre tierce, aucune licence à vérifier, aucune
attribution à porter. Les recherches de MIDI CC0/CC-BY n'ont pas été menées :
elles n'auraient rien apporté qu'une composition maison ne donne pas ici, et
elles auraient rouvert la question de compatibilité que `DOCS/MUSIQUE.md § 6.5`
demande de trancher pièce par pièce.

Le `.wav` de chaque dossier **est** ce que la Mockingboard jouera : six ondes
carrées, deux puces, la même réduction, le même tempo, la même stéréo. C'est le
seul objet à écouter pour juger. Il n'est pas suivi par git
(`.gitignore:76`).

---

## 1. Les dix musiques

| Zone | Fichier disque | Pièce | Mode | bpm | Durée | Octets | Tampon | Percussion |
| --- | --- | --- | --- | ---: | ---: | ---: | :---: | --- |
| `accueil` | `WELCOME.MB` | **L'Appel du Marais** | ré dorien | 136 | 49,7 s | 2 233 | zone | motif complet |
| `village` | `VILLAGE.MB` | **Les Feux de Bourbenville** | sol mixolydien | **166** | 40,8 s | 2 254 | zone | danse |
| `nord` | `NORTHSWAMP.MB` | **Le Bois des Guetteurs** | mi éolien | 150 | 45,1 s | 2 262 | zone | marche de guet |
| `riviere` | `RIVER.MB` | **Le Pont sur la Croupie** | la dorien | 125 | 54,0 s | 1 964 | zone | **aucune** |
| `sud` | `SOUTHSWAMP.MB` | **Sentiers Verts** | ré éolien | 150 | 45,1 s | 2 277 | zone | marche |
| `danger` | `DANGER.MB` | **Ce qui Attend Sous l'Eau** | do phrygien | 136 | 49,7 s | 1 951 | zone | **un cœur**, grosse caisse seule |
| `tour` | `TOWER.MB` | **La Tour de Stratagus** | sol mineur harm. | 125 | 46,4 s | 1 045 | zone | un pas, toutes les 2 mesures |
| `combat` | `BATTLE.MB` | **Le Fer et la Pince** | si éolien | **200** | 24,3 s | 1 228 | **surcouche** | c'est elle qui court |
| `mort` | `DEATH.MB` | **Le Marais Referme** | do éolien | 125 | 31,0 s | 673 | **surcouche** | **aucune** |
| `victoire` | `VICTORY.MB` | **Par la Trouée de Ciel** | ré mixolydien | 150 | 25,9 s | 1 265 | **surcouche** | fanfare |

**Total sur le volume : 17 152 octets**, sur ~28 Mo libres — le nombre de pièces
ne coûte rien.

⚠ **Ce qui coûte, c'est la plus grosse de chaque tampon.** Le moteur en a deux,
et chaque pièce doit tenir dans le sien. Un coup de percussion coûte 3 octets,
exactement comme une note : les deux se comptent ensemble.

| Tampon | Limite | Pièces | La plus grosse | Marge |
| --- | ---: | --- | ---: | ---: |
| **zone** | 2 304 o | `accueil`, `village`, `nord`, `riviere`, `sud`, `danger`, `tour` | `SOUTHSWAMP.MB`, 2 277 o | **27 o** |
| **surcouche** | 1 280 o | `COMBAT`, `MORT`, `VICTOIRE` | `VICTORY.MB`, 1 265 o | **15 o** |

Les commandes des `README.md` passent `--max 2304` pour les thèmes de zone et
`--max 1280` pour les trois surcouches : la conversion **échoue** au lieu de
livrer un flux qui déborderait à l'exécution.

Quatre pièces sont à moins de 80 octets de leur limite — `sud` 27, `victoire`
15, `nord` 42, `village` 50 : **toute retouche doit être reconvertie avant
d'être crue.** Les six autres ont entre 71 et 1 259 octets de marge, `tour` et
`mort` étant très au large.

`mort` et `victoire` se convertissent en plus avec **`--no-loop`** : elles se
jouent une fois et laissent le silence.

---

## 2. Les 35 clairières → leur zone → leur fichier

Numérotation, `hub` et cases repris de `SCOSWAMP.MORE/carte.json` (35 entrées,
vérifié) et de `SCOSWAMP/DOCS/CARTOGRAPHIE.md`. La répartition en zones est
**identique** à celle de `../propositions/INDEX.md` § 2, à une exception près,
signalée en gras : `courbensaule` est fondue dans `village` (voir § 4).

| # | `hub` | Titre | (x,y) | Zone | Fichier |
| ---: | ---: | --- | :---: | --- | --- |
| 1 | 078 | Route de Courbensaule | (0,0) | **`village`** | `VILLAGE.MB` |
| 2 | 234 | Le Patrouilleur vert | (2,0) | `nord` | `NORTHSWAMP.MB` |
| 3 | 084 | Le Maître des Jardins | (3,0) | `nord` | `NORTHSWAMP.MB` |
| 4 | 232 | Les deux loups | (4,0) | `nord` | `NORTHSWAMP.MB` |
| 5 | 218 | Feu follet à l'orée | (1,1) | `nord` | `NORTHSWAMP.MB` |
| 6 | 121 | Le croisement | (2,1) | `nord` | `NORTHSWAMP.MB` |
| 7 | 161 | Le Géant | (4,1) | `nord` | `NORTHSWAMP.MB` |
| 8 | 019 | Clairière aux brigands | (0,2) | `nord` | `NORTHSWAMP.MB` |
| 9 | 153 | Le bassin de Vase | (1,2) | `danger` | `DANGER.MB` |
| 10 | 088 | Scorpion et nain | (2,2) | `danger` | `DANGER.MB` |
| 11 | 202 | Le nid de l'Aigle | (3,2) | `nord` | `NORTHSWAMP.MB` |
| 12 | 270 | Sables mouvants | (4,2) | `danger` | `DANGER.MB` |
| 13 | 295 | La Rivière Croupie | (1,3) | `riviere` | `RIVER.MB` |
| 14 | 183 | Sommet de la falaise | (2,3) | `riviere` | `RIVER.MB` |
| 15 | 045 | **Le pont sur la rivière Croupie** | (3,3) | `riviere` | `RIVER.MB` |
| 16 | 304 | Le Perroquet / Maîtresse des Oiseaux | (0,4) | `sud` | `SOUTHSWAMP.MB` |
| 17 | 094 | La brume fétide | (1,4) | `sud` | `SOUTHSWAMP.MB` |
| 18 | 179 | Le pique-nique suspect | (2,4) | `sud` | `SOUTHSWAMP.MB` |
| 19 | 319 | La clairière des scorpions | (3,4) | `danger` | `DANGER.MB` |
| 20 | 047 | Trois chemins herbeux | (4,4) | `sud` | `SOUTHSWAMP.MB` |
| 21 | 031 | Bassin de cristal | (5,4) | `sud` | `SOUTHSWAMP.MB` |
| 22 | 367 | Les Fleurs d'Angoisse | (0,5) | `danger` | `DANGER.MB` |
| 23 | 348 | La Licorne | (1,5) | `sud` | `SOUTHSWAMP.MB` |
| 24 | 227 | La clairière des combats | (2,5) | `sud` | `SOUTHSWAMP.MB` |
| 25 | 187 | Herbe à Pinces | (3,5) | `danger` | `DANGER.MB` |
| 26 | 309 | Orques des Marais | (4,5) | `danger` | `DANGER.MB` |
| 27 | 125 | Cul-de-sac de la Bête | (0,6) | `danger` | `DANGER.MB` |
| 28 | 022 | La clairière des Arbres-Épées | (1,6) | `danger` | `DANGER.MB` |
| 29 | 165 | Tente aux araignées | (3,6) | `danger` | `DANGER.MB` |
| 30 | 230 | Clairière des grenouilles | (4,6) | `sud` | `SOUTHSWAMP.MB` |
| 31 | 044 | La rivière profonde | (1,7) | `riviere` | `RIVER.MB` |
| 32 | 314 | Clairière du Maître des Loups | (1,8) | `sud` | `SOUTHSWAMP.MB` |
| 33 | 058 | **Le large rond-point (départ)** | (2,8) | `sud` | `SOUTHSWAMP.MB` |
| 34 | 390 | Pierres et tronc | (3,8) | `sud` | `SOUTHSWAMP.MB` |
| 35 | 082 | Bête du bassin | (4,8) | `sud` | `SOUTHSWAMP.MB` |

**Répartition : `sud` 12 · `danger` 10 · `nord` 8 · `riviere` 4 · `village` 1.**

Les trois pages disputées (`CARTOGRAPHIE.md:810-820`) sont arbitrées comme dans
le dossier voisin : **363** → clairière 2, **394** → clairière 21, **330** →
clairière 34. Deux dossiers de propositions qui trancheraient différemment
rendraient les lignes `MU` incomparables.

Les pages hors clairière (296 sur 412) suivent la règle générale — la musique de
la dernière clairière continue — sauf les ensembles listés dans chaque
`README.md` : prologue et sortie (`village`), tour (`tour`), combats et morts
(surcouches), victoires.

---

## 3. Règles d'écriture : les voix, les côtés, la batterie

C'est la différence de fond avec `../propositions/`, et cela mérite d'être
expliqué parce que ce n'est **pas** un réglage. Cette section vaut pour les dix
thèmes de zone **et** pour les 35 pièces de clairière : elle est le contrat du
module `compose.py`.

### 3.1 Le lecteur choisit la voix, pas le compositeur

`midi_to_mb.py` ne laisse pas choisir. À chaque frontière, les notes qui
continuent gardent leur voix ; les notes qui commencent sont servies **de l'aiguë
à la grave**, dans les voix libres prises dans l'ordre `0, 3, 1, 4, 2, 5`,
c'est-à-dire en alternant les deux AY. Les voix 0-2 sortent à gauche, 3-5 à
droite.

### 3.2 Cinq voix, pas six, dès qu'il y a une batterie

Depuis que le lecteur sait faire du bruit, les notes du **canal MIDI 10**
deviennent des paquets NOISE sur la **voix 5, à droite**. Cette voix ne joue
alors plus aucune hauteur : il ne reste que **cinq** parties mélodiques.

| | sans batterie | avec batterie |
| --- | --- | --- |
| parties de hauteur | 6 | **5** |
| ordre par hauteur | 0(G) 3(D) 1(G) 4(D) 2(G) 5(D) | 0(G) 3(D) 1(G) 4(D) 2(G) |
| voix 5 | la partie la plus grave | **la batterie**, à droite |

Une pièce avec batterie qui garde six parties **perd des notes**. Il faut en
retirer une : d'ordinaire le bourdon — la grosse caisse en tient lieu, et c'est
même un gain — ou bien la voix d'accords tenus quand le bourdon fait le
caractère de la pièce (`danger`). `Piece.write()` compte les parties et le dit :

```
   !! 6 parties de hauteur pour 5 voix : la batterie prend la voix 5,
      retirer une partie (le bourdon, en général) sinon des notes seront abandonnées
```

### 3.3 Les deux règles qui tiennent la stéréo

1. **Chaque partie reste dans sa bande de registre.** Si deux parties se
   croisent, elles échangent leur puce. `voicing()` et `pick()` posent chaque
   figure d'accord dans une fenêtre fixe.
2. **Chaque partie sonne sur chaque temps fort**, en attaquant ou en tenant. Si
   une partie se tait au moment où les autres attaquent, toutes se décalent d'un
   cran et changent de côté. `Piece.holes()` le vérifie et le signale.

La batterie échappe aux deux : elle a sa voix réservée et peut se taire quand
elle veut. C'est ce qui en fait le bon outil pour ménager un **silence** au
milieu d'une pièce sans dérégler la stéréo.

### 3.4 Écrire la batterie

`Piece.add_drums()` prend des motifs en notation texte, une lettre par pas :

| lettre | instrument | note GM | durée par défaut |
| :---: | --- | ---: | ---: |
| `K` | grosse caisse | 36 | 3 ticks |
| `S` | caisse claire | 38 | 2 ticks |
| `H` | charleston fermé | 42 | 1 tick |
| `O` | charleston ouvert | 46 | 4 ticks |
| `T` | tom | 45 | 2 ticks |
| `C` | cymbale | 49 | 7 ticks |

```python
p.add_drums("K.H. S.H. K.H. S.H.", length=LEN)      # motif de base, en croches
p.add_drums("H.H.H.H.", length=LEN)                 # une deuxième couche
p.add_drums([(0, "C", 7), (0, "K")], t0=BAR * 8)    # la cymbale qui ouvre le B
```

`.` et `-` sont des silences ; les espaces et les `|` sont ignorés, ce qui
permet d'écrire les temps. Les durées se comptent en **ticks de 50 Hz**, pas en
temps : un coup sec fait 1 à 3 ticks quel que soit le tempo, une cymbale 7.
`drum_at()` pose des frappes isolées là où un motif régulier serait faux.

**Un coup coûte 3 octets** (NOISE + OFF + le délai), exactement comme une note.
Un charleston en doubles croches sur 32 mesures pèse 1 500 octets : plus que le
tampon. On écrit des motifs, pas des grilles pleines. `Piece.write()` affiche
une estimation (`~N octets`) fiable à quelques octets près.

### 3.5 Vérifier

```sh
python3 verifier.py nord/nord.mid --bpm 150
```

`verifier.py` rejoue la réduction réelle, sépare la batterie des hauteurs,
donne pour chaque voix le côté, le nombre de notes, le registre et l'occupation,
détaille les instruments frappés, et **contrôle** : notes abandonnées, voix
laissée vide, mélodie qui n'est pas la partie la plus aiguë, stéréo déséquilibrée
(moins de 45 % d'un côté). Il finit par `OK` ou par des lignes `!!`.

Le résultat, mesuré sur les dix pièces après révision :

| voix | côté | ce qui s'y trouve | exceptions |
| ---: | :---: | --- | --- |
| 0 | **gauche** | **la mélodie**, seule, dans les dix | — |
| 1 | gauche | une voix médiane | l'ostinato dans `nord`, l'arpège dans `danger` et `tour` |
| 2 | **gauche** | la basse | le bourdon dans `danger` et `tour` |
| 3 | **droite** | **le contre-chant — la voix qui répond à la mélodie** | l'arpège dans `mort` |
| 4 | droite | l'arpège, l'essentiel du mouvement | la basse dans `danger` et `tour`, les accords dans `nord` |
| 5 | **droite** | **la batterie** (sept pièces) | le bourdon dans `riviere` et `mort`, qui n'en ont pas |

Soit : **la mélodie et la basse à gauche, la réponse, le mouvement et la frappe
à droite.** C'est ce qui rend audible le jeu de question-réponse : la phrase part
d'un côté et revient de l'autre. L'équilibre mesuré est de 59/41 pour les pièces
avec batterie (le bruit compte pour peu de durée) et de 50/50 sans.

Les parties médianes échangent parfois les voix 1 et 4 selon leur hauteur du
moment — c'est audible comme une largeur, pas comme un défaut.

### 3.6 Le fondu de fin

Le lecteur émet un `FADE` (`$F0`) 30 ticks avant la dernière note : 0,9 s de
fondu sortant, automatique. Une pièce à boucle n'a donc pas besoin de finir sur
un accord tenu — elle doit finir sur une **cadence qui prépare la reprise**,
le fondu se chargeant de la couture.

---

## 4. Ce que ce style change par rapport au dossier Renaissance

| | `../propositions/` (Renaissance) | **ce dossier** (fantasy moderne) |
| --- | --- | --- |
| Sources | onze pièces XV<sup>e</sup>-XVIII<sup>e</sup>, Mutopia, domaine public | dix compositions originales, GPL v3 |
| Voix | 3, mono en pratique | **6**, ou **5 + batterie**, stéréo écrite |
| Taille max | 1 058 o (`NORTHSWAMP.MB`) | 2 277 o (`SOUTHSWAMP.MB`) |
| Tampons | tout tient en 1 280 o | **zone 2 304 o**, surcouche 1 280 o |
| Langage | contrepoint vocal, cadences fonctionnelles, sensible | modes (dorien, phrygien, mixolydien, éolien), bourdons, quintes à vide, ostinatos, **percussion** |
| Forme | celle de l'œuvre d'origine | intro - A - B - A', un crochet énoncé deux fois, une surprise par pièce, écrite pour boucler sans couture |
| Tempo | 120-200, celui du genre | 125-200, jamais en dessous de 125 |
| Ce qui identifie une zone | le timbre du répertoire | **un procédé** : l'ostinato fixe du `nord`, le demi-ton phrygien du `danger`, la seconde augmentée de la `tour`, le bourdon de quinte de la `riviere` |
| Zones | 11 | 10 (`courbensaule` fondu dans `village`) |

Trois différences méritent une décision, pas un goût :

- **Le tampon.** Six voix coûtent le double d'octets pour la même durée, et la
  percussion se paie au même tarif (3 octets le coup). C'est ce qui a fixé les
  deux tailles du moteur : **2 304 octets pour une zone, 1 280 pour une
  surcouche.** `COMBAT` et `VICTOIRE` sont écrites pour la seconde — le combat
  en 20 mesures, ce qui lui va : une mêlée boucle court.
- **La percussion, et où elle ne va pas.** Sept pièces en ont, trois n'en ont
  pas, et ce n'est pas une économie : `riviere` parce que l'eau ne frappe pas,
  `mort` parce que l'absence de frappe *est* le sujet, `tour` presque pas — un
  pas toutes les deux mesures. Une batterie coûte une voix de hauteur (§ 3.2) :
  la question n'est jamais « peut-on en mettre » mais « qu'est-ce qu'on retire
  pour l'avoir ». Six fois sur sept la réponse a été le bourdon ; pour `danger`
  et `tour`, où la pédale fait le morceau, c'est la voix d'accords tenus.
- **L'unité.** Le dossier Renaissance emprunte onze langages à onze
  compositeurs ; celui-ci en a un seul, décliné. Le premier a plus de variété
  et moins de cohérence ; le second l'inverse. La question est de savoir si le
  Marais doit sonner comme une anthologie ou comme un lieu.
- **L'époque.** *Le Marais aux Scorpions* est un livre de 1984 et l'Apple IIe
  une machine de 1983 ; le style moderne assume l'anachronisme du portage, le
  style Renaissance assume celui du récit. Aucun des deux n'a tort.

Les deux dossiers sont **interchangeables fichier par fichier** : les noms de
disque (`NORTHSWAMP.MB`, `DANGER.MB`, …) et la carte des zones sont les mêmes.
On peut prendre `DANGER.MB` ici et `TOWER.MB` là.

---

## 5. Refabriquer tout le dossier

```sh
cd /Users/gistair/src/pom2adventure/SCOSWAMP.MORE/MUSIC/propositions-moderne
M=../../midi_to_mb.py
(cd accueil  && python3 accueil.py   && python3 $M accueil.mid   WELCOME.MB.BIN  --bpm 136 --max 2304 --wav ACCUEIL.wav)
(cd village  && python3 village.py   && python3 $M village.mid   VILLAGE.MB.BIN  --bpm 166 --max 2304 --wav VILLAGE.wav)
(cd nord     && python3 nord.py      && python3 $M nord.mid      NORTHSWAMP.MB.BIN --bpm 150 --max 2304 --wav MARAISNO.wav)
(cd riviere  && python3 riviere.py   && python3 $M riviere.mid   RIVER.MB.BIN  --bpm 125 --max 2304 --wav RIVIERE.wav)
(cd sud      && python3 sud.py       && python3 $M sud.mid       SOUTHSWAMP.MB.BIN --bpm 150 --max 2304 --wav MARAISUD.wav)
(cd danger   && python3 danger.py    && python3 $M danger.mid    DANGER.MB.BIN   --bpm 136 --max 2304 --wav DANGER.wav)
(cd tour     && python3 tour.py      && python3 $M tour.mid      TOWER.MB.BIN     --bpm 125 --max 2304 --wav TOUR.wav)
(cd combat   && python3 combat.py    && python3 $M combat.mid    BATTLE.MB.BIN   --bpm 200 --max 1280 --wav COMBAT.wav)
(cd mort     && python3 mort.py      && python3 $M mort.mid      DEATH.MB.BIN     --bpm 125 --no-loop --max 1280 --wav MORT.wav)
(cd victoire && python3 victoire.py  && python3 $M victoire.mid  VICTORY.MB.BIN --bpm 150 --no-loop --max 1280 --wav VICTOIRE.wav)
```

Chaque ligne entre dans son sous-dossier, d'où le `../../midi_to_mb.py` : c'est
aussi la forme utilisée dans les `README.md`. Le bloc entier se recolle tel quel
dans un shell ; il s'arrête à la première erreur si l'on a fait `set -e`.

`--vol` reste au défaut `13,11,11,12,11,11` partout : mélodie et arpège un cran
devant, le reste au même niveau. Rien ne justifie d'en changer avant d'avoir
écouté sur la carte.

---

## 6. Les fichiers de l'atelier

| Fichier | Rôle |
| --- | --- |
| `compose.py` | le module : noms de notes, modes, accords, `voicing`, `ostinato`, `pedal`, `bed`, `progression`, `arpeggio`, `double`, la batterie (`drum_pattern`, `drum_at`, `Piece.add_drums`), et la classe `Piece` qui écrit le MIDI et diagnostique |
| `verifier.py` | rejoue la réduction de `midi_to_mb.py` et dit, voix par voix, ce qui sortira à gauche et à droite ; sépare la batterie et contrôle la répartition |
| `<zone>/<zone>.py` | la pièce, en notation texte lisible |
| `<zone>/<zone>.mid` | le MIDI à six pistes, entrée de `midi_to_mb.py` |
| `<zone>/<NOM>.MB.BIN` | le flux MB1 que le lecteur 6502 joue |
| `<zone>/<NOM>.wav` | le rendu, non suivi par git |

`compose.py` généralise `../accueil.py`, qui mêlait composition, MIDI, MB1 et
rendu dans un seul fichier pour trois voix. Il n'écrit **que** du MIDI : le MB1
et le WAV viennent de `midi_to_mb.py`, donc du même code que le disque.
