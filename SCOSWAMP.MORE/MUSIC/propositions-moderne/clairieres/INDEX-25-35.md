# Clairières 25 à 35 — une musique par clairière

Onze pièces originales, **une par clairière**, écrites avec `../compose.py` et
converties par `../../midi_to_mb.py`. Chacune est une **variation dans la
couleur de sa zone** — même famille de mode, même procédé identifiable que le
thème de zone — avec son propre thème et son propre caractère, tirés des pages
de la clairière.

**Les onze ont maintenant une batterie.** Le lecteur bat le canal de bruit de la
seconde puce ; les notes du canal MIDI 10 y deviennent des paquets NOISE sur la
**voix 5, à droite**. Il ne reste alors que **cinq** voix de hauteur : dans les
onze pièces c'est le **lit d'accords tenus** qui a cédé sa place, et le bourdon
qui a **migré** de la voix 5 (droite) à la voix 2 (gauche). Le procédé de zone —
un bourdon dans toutes les onze — est donc intact partout.

Tout tient dans le **tampon de zone : 2 304 octets**. La plus grosse est
`FROGS.MB.BIN` (2 246 o, 58 octets de marge) ; la plus légère est
`BEAST.MB.BIN` (1 467 o).

**Aucune des onze n'abandonne une seule note à la réduction** (`0 abandonnées` à
la conversion, polyphonie maximale = 5 exactement, plus la batterie).

## Le tableau

| # | Clairière (`hub`) | Fichier disque | Pièce | Mode | bpm | Durée | Coups | Octets |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 25 | Herbe à Pinces (187) | `PINCERS.MB` | **L'Herbe qui Serre** | mi phrygien | 176 | 43,9 s | 75 | 2 184 |
| 26 | Orques des Marais (309) | `ORCS.MB` | **Trois Arcs dans la Brume** | ré phrygien | **166** | 40,8 s | 105 | 1 918 |
| 27 | Cul-de-sac de la Bête (125) | `BEAST.MB` | **Le Rocher qui Respire** | sol phrygien | 143 | 45,6 s | 66 | 1 467 |
| 28 | Arbres-Épées (022) | `SWORDTREES.MB` | **Les Bras qui Repoussent** | fa phrygien | 166 | 40,4 s | 98 | 2 198 |
| 29 | Tente aux araignées (165) | `SPIDERS.MB` | **Le Fil d'Argent** | do♯ phrygien | 150 | 45,1 s | 113 | 1 900 |
| 30 | Clairière des grenouilles (230) | `FROGS.MB` | **Le Bal des Mares** | sol éolien | **176** | 38,5 s | 115 | **2 246** |
| 31 | La rivière profonde (044) | `DEEPWATER.MB` | **L'Eau Noire** | sol dorien | 136 | 49,7 s | 14 | 1 894 |
| 32 | Maître des Loups (314) | `WOLFMASTER.MB` | **Le Cor du Maître** | mi éolien | **150** | 45,9 s | 119 | 2 182 |
| **33** | **Le large rond-point, départ (058)** | `ROUNDABOUT.MB` | **Le Cœur du Marais** | ré éolien | 158 | 48,9 s | 101 | 2 219 |
| 34 | Pierres et tronc creux (390) | `LOG.MB` | **Pierres Plates** | do éolien | 150 | 45,1 s | 97 | 2 006 |
| 35 | Bête du bassin (082) | `POOL.MB` | **Ce qui Monte du Bassin** | fa éolien | **150** | 45,1 s | 88 | 2 024 |

**Total : 22 238 octets** pour les onze. Ce qui compte n'est pas la somme mais la
plus grosse : 2 246 o < 2 304 o. Les tempos en gras ont été **accélérés** —
jamais ralentis : la troupe d'orques avance, les grenouilles dansent, la meute
part et la Bête du bassin sort plus vite.

Les durées tiennent toutes entre **38,5 s et 49,7 s**. Le fondu de fin (`FADE`,
0,9 s avant la dernière note) est automatique : aucune ne finit sur un accord
tenu, toutes finissent sur une cadence qui prépare la reprise.

## Zone de référence, procédé gardé, procédé propre

| # | Zone | Ce qui vient de la zone | Ce qui n'est qu'à cette clairière |
| ---: | --- | --- | --- |
| 25 | `danger` | demi-ton phrygien fa–mi, bourdon fixe | l'arpège troué : trois croches, un silence — la pince qui claque, et la caisse claire tombe **dans** le trou |
| 26 | `danger` | demi-ton phrygien mi♭–ré, bourdon fixe | la marche : rythme pointé partout, grosse caisse au pas, fanfare énoncée sur quatre degrés |
| 27 | `danger` | demi-ton phrygien la♭–sol, bourdon refrappé à chaque mesure | **6/4** (la seule des 35), arpège boiteux 1+½+½+1+1½+1½, et le cœur qui bat sous la pierre |
| 28 | `danger` | demi-ton phrygien sol♭–fa, bourdon fixe | **canon** : la cellule fa–sol♭–fa repousse au contre-chant (mes. 6, 19, 21, 23) |
| 29 | `danger` | demi-ton phrygien ré–do♯, crescendo par la densité | l'arpège de **3** sons dans **4** temps qui **ne se recale jamais**, et l'incendie à la mesure 17 |
| 30 | `sud` | marche i-VI-III-VII sur bourdon immobile | la mélodie **saute** l'octave en croches, et c'est le seul bal : la batterie n'y quitte plus le morceau |
| 31 | `riviere` | croches ininterrompues, bourdon sur la **quinte** | le **remous** (0-2-1-2-0-1-2-1), et une batterie faite uniquement de **nappes de bruit** |
| 32 | `sud` | marche i-VI-III-VII sur bourdon immobile | le **cor** : quintes et quartes à vide, arpège sans aucune tierce, et le galop écrit au quart de temps |
| 33 | `sud` | marche i-VI-III-VII, **même tonique que la zone** | le thème du Marais : la montée ré-mi-fa, énoncée **sept fois** à sept degrés, et le pas du voyageur |
| 34 | `sud` | marche i-VI-III-VII sur bourdon immobile | arpège de **quintes à vide** (liste `CREUX`), le coup sur le tronc en notes répétées, et des toms pour seule batterie |
| 35 | `sud` | marche i-VI-III-VII | la **basse ascendante**, le Bijou Violet tenu une ronde sur le VI majeur, et un bourdon qui **monte** |

Les cinq clairières `danger` sont toutes phrygiennes, sur cinq toniques
distinctes (mi, ré, sol, fa, do♯) ; les cinq clairières `sud` sont toutes
éoliennes (sol, mi, ré, do, fa) ; la clairière `riviere` est dorienne, comme le
pont. Aucune ne reprend la tonique de son thème de zone, **sauf le rond-point**,
qui prend exactement celle de `sud` parce qu'il est le cœur du lieu.

## La batterie, pièce par pièce

Elle n'est nulle part une grille pleine : **un coup coûte 3 octets**, exactement
comme une note. Elle est là où elle porte, et elle se retire là où elle nuirait.

| # | Ce qu'elle joue | Où elle se tait |
| ---: | --- | --- |
| 25 | la caisse claire dans le trou de l'arpège — la pince | intro, mesures 19-20, dernière mesure |
| 26 | une marche : grosse caisse au pas, tambour lointain d'abord | mesures 1-2, et **toute la mesure 20** |
| 27 | le **cœur qui bat sourd** : deux grosses caisses collées, *loub-doub* | intro, et la mesure 14 où la Bête cesse de respirer |
| 28 | les lames : caisse claire sèche sur les temps faibles | intro ; trois coups nus dans la mesure amputée |
| 29 | **le feu** : charleston qui crépite, toms qui montent | tout, jusqu'à la mesure 17 — deux charlestons isolés mis à part |
| 30 | le bal : charleston sur les croches, ouvert en A' | l'intro seulement ; ensuite elle ne s'arrête plus |
| 31 | **l'eau** : neuf nappes de bruit de 0,6 à 1,2 s, aucun coup sec | partout ailleurs — 14 coups en 49 secondes |
| 32 | le **galop** au quart de temps, `ta-ta-TAM` | intro, et la mesure 20 à six temps |
| 33 | le **pas du voyageur**, régulier, jamais une danse | les six premières mesures ; deux pas seuls à la dernière |
| 34 | du bois sur du bois : des toms, **jamais de charleston** | intro, et la mesure 21 où l'on frappe et l'on écoute |
| 35 | ce qui sort de l'eau : une bulle, puis des toms, puis le tentacule | les quatre premières mesures |

## Les onze surprises

Une par pièce, et jamais deux fois la même :

| # | La surprise | Mesure |
| ---: | --- | ---: |
| 25 | la pédale se déplace d'un demi-ton, du mi au **fa** | 19-20 |
| 26 | le **grand silence** : tout se fige, la flèche passe | 20 |
| 27 | la Bête **cesse de respirer** : batterie muette, six temps | 14 |
| 28 | une **mesure de trois temps** : la lame coupe un temps à la pièce | 21 |
| 29 | **sol♯ majeur** : sensible et tierce majeure, l'incendie | 19 et 27 |
| 30 | **sol majeur** : le si bécarre, la bouche anormalement large | 13 et 25 |
| 31 | le bourdon **descend** de la quinte à la tonique : on touche le fond | 26-27 |
| 32 | une **mesure de six temps** : le Maître lève la main | 20 |
| 33 | **ré majeur** : un fa♯, un seul, la trouée de ciel | 31 |
| 34 | **on frappe et on écoute** : deux toms, puis rien | 21 |
| 35 | le bourdon **monte** : fa, la♭, si♭ — le sol se soulève | 25-28 |

## La stéréo

Avec une batterie, la voix 5 est le canal de bruit et il ne reste que **cinq**
voix de hauteur. Le plan est le même dans les onze, vérifié pièce par pièce
avec `../verifier.py` :

| voix | côté | rôle |
| ---: | :---: | --- |
| 0 | **gauche** | la mélodie, seule |
| 1 | gauche | le contre-chant |
| 2 | **gauche** | le **bourdon**, migré depuis la voix 5 |
| 3 | **droite** | l'arpège ou l'ostinato — et les **réponses au chant** |
| 4 | droite | la basse |
| 5 | **droite** | **la batterie** |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui
attribue, et à chaque articulation la basse et le contre-chant peuvent
s'échanger un instant leur puce. La stéréo mesurée va de **59/41 à 62/38** —
trois voix à gauche contre deux plus la frappe à droite, ce que le contrôle des
45 % accepte.

Vérification d'une pièce :

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres
python3 ../verifier.py 33-rondpoint/rondpoint.mid --bpm 158
```

Les onze concluent `OK — 6 voix employées, …, aucune note abandonnée`.

## Refabriquer les onze

```sh
cd /Users/gistair/src/pom2adventure/SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres
M=../../../midi_to_mb.py
(cd 25-pinces       && python3 pinces.py       && python3 $M pinces.mid       PINCERS.MB.BIN       --bpm 176 --max 2304 --wav PINCES.wav)
(cd 26-orques       && python3 orques.py       && python3 $M orques.mid       ORCS.MB.BIN       --bpm 166 --max 2304 --wav ORQUES.wav)
(cd 27-bete         && python3 bete.py         && python3 $M bete.mid         BEAST.MB.BIN         --bpm 143 --max 2304 --wav BETE.wav)
(cd 28-arbresepees  && python3 arbresepees.py  && python3 $M arbresepees.mid  SWORDTREES.MB.BIN  --bpm 166 --max 2304 --wav ARBRESEPEES.wav)
(cd 29-araignees    && python3 araignees.py    && python3 $M araignees.mid    SPIDERS.MB.BIN    --bpm 150 --max 2304 --wav ARAIGNEES.wav)
(cd 30-grenouilles  && python3 grenouilles.py  && python3 $M grenouilles.mid  FROGS.MB.BIN  --bpm 176 --max 2304 --wav GRENOUILLES.wav)
(cd 31-profonde     && python3 profonde.py     && python3 $M profonde.mid     DEEPWATER.MB.BIN     --bpm 136 --max 2304 --wav PROFONDE.wav)
(cd 32-maitreloups  && python3 maitreloups.py  && python3 $M maitreloups.mid  WOLFMASTER.MB.BIN  --bpm 150 --max 2304 --wav MAITRELOUPS.wav)
(cd 33-rondpoint    && python3 rondpoint.py    && python3 $M rondpoint.mid    ROUNDABOUT.MB.BIN    --bpm 158 --max 2304 --wav RONDPOINT.wav)
(cd 34-tronc        && python3 tronc.py        && python3 $M tronc.mid        LOG.MB.BIN        --bpm 150 --max 2304 --wav TRONC.wav)
(cd 35-bassin       && python3 bassin.py       && python3 $M bassin.mid       POOL.MB.BIN       --bpm 150 --max 2304 --wav BASSIN.wav)
```

Le bloc se recolle tel quel dans un shell. **Trois tempos ont changé** par
rapport à la version précédente — 26 (158 → 166), 30 (166 → 176), 32 et 35
(143 → 150) : les lignes ci-dessus sont les seules à jour.

`--vol` reste au défaut `13,11,11,12,11,11` partout. Le `.wav` de chaque dossier
**est** ce que la Mockingboard jouera — six ondes carrées, deux puces, la même
réduction, le même tempo, la même stéréo, la même batterie. Il n'est pas suivi
par git (`.gitignore:76`).

Rien n'est copié dans `SCOSWAMP/MUSIC/` : ce dossier reste un atelier tant que
le propriétaire n'a pas écouté et tranché.
