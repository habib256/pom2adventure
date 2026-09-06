# Clairière 10 — Scorpion et nain (`hub` 088, case 2,2)

**`DWARFSCORP.MB.BIN` — 2 076 octets, 36,5 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 014 | Scorpion et nain | les bruits de lutte derrière le tronc, le SCORPION GÉANT, le NAIN sans vie |
| 338 | Retour au Scorpion Géant | quelques ossements et une cuirasse |
| 088 | Quitter la clairière | la bifurcation, nord ou est |

## La pièce

| | |
| --- | --- |
| Titre | **Les Pinces et l'Os** |
| Source | composition originale, `scorpnain.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | deux choses à la fois : la bête qui se repaît, et l'homme qui ne bouge plus |
| Mode | **la mineur phrygien** (la **si♭** do ré mi fa sol) |
| Tempo | **184** à la noire (auparavant 176) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **36,5 s** |
| Taille | **2 076 octets** (marge 228 sur le tampon de zone) |
| Notes | 417 de hauteur + **89 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures, `la si♭ la mi do' / si♭ la` : la seconde
  phrygienne prise deux fois, qui est le claquement de la pince. Énoncé trois
  fois, et la pièce se ferme dessus ;
- **une réponse** aux mesures 12, 20 et 28 : le chant tient et les pinces — voix
  3, à droite — répondent. C'est la lutte entendue derrière le tronc : deux
  choses qui ne parlent jamais en même temps ;
- **la surprise** : au B, **la batterie s'arrête complètement**. Huit mesures
  sans un coup, l'arpège en noires, la basse en blanches, le chant en valeurs
  longues qui descendent. C'est le seul endroit des douze clairières où la
  musique cesse de mordre. Elle revient à la mesure 21 sur une cymbale, après
  **un temps et demi de silence général** où plus rien ne sonne du tout ;
- **le rythme harmonique varie** : grille à la demi-mesure ; le Scorpion change
  d'accord au milieu de la mesure, le Nain tient ;
- **le tempo monte de 176 à 184** : c'est le plus vif des douze.

## La batterie

**Le cliquetis.** Charleston fermé en croches serrées, caisse claire sèche,
grosse caisse au premier temps. Rien dans l'intro, **rien du tout dans les huit
mesures du Nain** : c'est la seule des douze où la batterie se tait pendant tout
un panneau, et c'est ce qui rend le retour du A' brutal.

## Ce qui la relie à `danger`, et ce qui l'en sépare

Même demi-ton phrygien, même bourdon immobile, même arpège sur la figure
`(0, 1, 2, 1)` que `DANGER.MB`. Ce qui appartient à cette clairière-là, c'est
que la page 014 raconte **deux** choses et que la pièce est donc en deux
matières : le A et le A' sont le Scorpion, arpège en croches détachées de 0,42
temps ; le B est le Nain, arpège en noires, basse en blanches.

**La voix des accords a cédé la place, pas le bourdon** — la règle du `danger`.
Cinq parties : chant, pinces, contre-chant, basse, bourdon. La basse passe à
droite sous l'arpège, le bourdon de mi garde le fond à gauche.

## Les six voix, mesurées

`python3 ../../verifier.py scorpnain.mid --bpm 184`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | E5..A6 | 78 |
| 1 | gauche | le contre-chant, et les notes basses des pinces | G3..A4 | 131 |
| 2 | **gauche** | **le bourdon de mi**, immobile | E2 | 7 |
| 3 | **droite** | **les pinces**, et les réponses | A3..D5 | 114 |
| 4 | droite | la basse, marchée puis tenue | C3..A♯3 | 87 |
| 5 | **droite** | **LA BATTERIE** — charleston fermé 56, grosse caisse 16, caisse claire 16, cymbale 1 | bruit | 89 |

Stéréo mesurée **60/40**, aucune note abandonnée, `verifier.py` conclut `OK`.

Cinquante-six des quatre-vingt-neuf coups sont des charlestons fermés, tous
dans le A et le A' : la pince claque quatre-vingt-neuf fois en trente-six
secondes, puis plus rien pendant huit mesures.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/10-scorpnain
python3 scorpnain.py
python3 ../../../midi_to_mb.py scorpnain.mid DWARFSCORP.MB.BIN \
    --bpm 184 --max 2304 --wav SCORPNAIN.wav
```
