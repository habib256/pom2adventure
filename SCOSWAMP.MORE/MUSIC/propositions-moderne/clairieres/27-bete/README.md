# Clairière 27 — Cul-de-sac de la Bête (`hub` 125)

**`BEAST.MB.BIN` — 1 467 octets, 45,6 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 011 | « le rocher bouge : ce n'était pas de la pierre » — une BÊTE IMMONDE à six pattes griffues, sa respiration lourde fait vibrer le bois |
| 210 | le retour : le sol porte encore les traces du combat, un silence lourd |
| 299 | la Pierre de Terreur : la Bête se réfugie derrière les rochers en gémissant |
| 125 | les griffes coupées en souvenir — et aucun autre chemin pour sortir |
| 228 | les graines d'Arbres-Épées semées devant elle |
| 243 | la charogne et les insectes charognards |

Zone de référence : **`danger`** (`DANGER.MB`, *Ce qui Attend Sous l'Eau*).

## La pièce

| | |
| --- | --- |
| Titre | **Le Rocher qui Respire** |
| Source | composition originale, `bete.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | six pattes qui ne tombent pas ensemble, et un cœur qu'on entend battre sous la pierre |
| Mode | **sol phrygien** (sol **la♭** si♭ do ré mi♭ fa) |
| Tempo | **143** à la noire (inchangé) |
| Forme | intro (2) — A (6) — B (6) — A' (4) |
| Durée | 18 mesures à **6/4** = **45,6 s** |
| Taille | **1 467 octets** (tampon de zone : 2 304) — la plus légère des onze |
| Notes | 301 hauteurs + **66 coups de batterie**, **0 abandonnée** |

Elle reste la seule des trente-cinq à ne pas être à quatre temps, et l'arpège y
boite toujours en 1 + ½ + ½ + 1 + 1½ + 1½. Le procédé de `danger` est intact :
demi-ton phrygien la♭–sol, bourdon de sol **refrappé à chaque mesure** — c'est
la respiration, et elle est restée.

**Ce que la révision change.**

* **La batterie du danger, telle qu'on l'entend.** Deux coups de grosse caisse
  collés, *loub-doub* : le **cœur qui bat sourd** sous le rocher. Il bat une
  fois par mesure en A, deux fois en B, sans répit en A'. Aucun charleston, rien
  de brillant : la Bête n'est pas rythmée, elle respire.
* **Le crochet** : `ré · mi♭ · ré`, long-bref-long, le demi-ton phrygien étiré
  sur six temps. Il ouvre A (mesure 3), revient à l'octave en A' (mesure 15) et
  conclut la pièce.
* **Une vraie partie B** (mesures 9-14) : le chant passe au-dessus du sol 6 et
  l'harmonie quitte le sol pour do mineur, si♭ et fa mineur.
* **La réponse** : mesures 8 et 18, le chant tient une ronde pointée et l'arpège
  lui rend le crochet une octave plus bas.
* **Le rythme harmonique varie** : les mesures à un accord gardent la boiterie à
  six temps entière ; celles à deux accords la coupent en deux. La Bête change
  de pas.
* **La surprise** : mesure 14, **la Bête cesse de respirer**. Silence complet de
  la batterie sur un sol tenu, six temps entiers. Puis le cœur repart, plus vite.
* **La cadence** : la♭–sol posé à la basse mesure 18, et la boucle repart sur le
  même sol. C'est un cul-de-sac : l'harmonie ne module jamais.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | B♭4..A♭6 | 48 |
| 1 | gauche | contre-chant | D3..B♭4 | 57 |
| 2 | **gauche** | bourdon de sol, refrappé à chaque mesure | G2 | 18 |
| 3 | **droite** | l'arpège boiteux, et les deux réponses | A3..E♭5 | 93 |
| 4 | droite | basse | F2..E♭4 | 85 |
| 5 | **droite** | **BATTERIE** — grosse caisse 54, tom 11, cymbale 1 | bruit | 66 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/27-bete
python3 bete.py
python3 ../../../midi_to_mb.py bete.mid BEAST.MB.BIN \
    --bpm 143 --max 2304 --wav BETE.wav
```
