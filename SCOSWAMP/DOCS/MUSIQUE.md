# Musique Mockingboard pour SCOSWAMP — étude de faisabilité

**2026-09-03** · Dépôts : `/Users/gistair/src/pom2adventure` (le jeu),
`/Users/gistair/src/pom2` (l'émulateur). **Aucun fichier suivi modifié.**

Objectif : cinq thèmes (accueil, Marais, combat, victoire, mort) sur Mockingboard,
et étude d'une chaîne **Suno → Mockingboard**.

---

## En bref

**La musique Mockingboard est faisable, et pas chère.** Le lecteur coûte ~600
octets et **~1 % du CPU** sur les 6 767 octets de marge du jeu ; POM2 émule tout
ce qu'il faut ; la config de lien du jeu **déclare déjà** le mécanisme
d'interruption de cc65, et le runtime `apple2enh` fait l'`ALLOC_INTERRUPT` ProDOS
tout seul. Compter **6 à 7 jours** de technique, dont **2,5 lèvent tout le
risque**.

**La chaîne Suno, en revanche, ne tient pas.** Pas pour des raisons de goût :

- les CGU de Suno **interdisent** d'utiliser l'Output pour alimenter d'autres
  modèles d'apprentissage (or c'est ce que fait tout transcripteur) **et** de
  contourner leur filigrane (or c'est ce que fait toute réduction en registres) ;
- le tier gratuit est **non commercial**, donc frontalement **incompatible avec
  la GPL v3** du dépôt ; et l'*US Copyright Office* juge l'audio purement généré
  **non protégeable** — on ne peut pas licencier ce qu'on ne détient pas ;
- techniquement, **aucun outil audio → AY n'existe au monde**, et **personne n'a
  jamais fait « Suno → tracker »** ; demander « 3 voix carrées » à Suno n'a rien
  à quoi se raccrocher, aucun paramètre n'exposant la polyphonie ;
- et une transcription automatique coûte **2,5× plus de RAM** pour un résultat
  qui sonne accidentel.

**Ce qu'il faut faire à la place** : composer dans **Arkos Tracker 3** (MIT,
Apple Silicon natif, import MIDI) — qui embarque en prime **un lecteur AKY 6502
officiel pour Apple II + Mockingboard, sous licence MIT**. Suno peut servir
d'oreille, écoutée puis mise de côté. Et si l'on veut vraiment de l'IA dans la
chaîne, il faut lui demander **du MIDI, pas de l'audio** : `text2midi` et Magenta
sont les seuls générateurs dont le code, les poids *et* les sorties soient
redistribuables.

**Trois pièges à connaître avant d'écrire une ligne** : acquitter l'IRQ **en
écrivant** `$7F` dans `$C40D`, jamais en lisant (le Moniteur //e pose INTCXROM et
la lecture rend de la ROM) ; **balayer les slots `$C7`→`$C1`**, car POM2 met la
carte en slot 2 par défaut ; et **ne jamais mettre de code d'interruption dans le
segment `LC` de cc65**, que ProDOS rend inaccessible sous IRQ.

Détail, chiffres et sources ci-dessous. Plan par étapes en **§7.4**.

---

## 1. La Mockingboard, techniquement

### 1.1 Matériel et carte d'adresses

Carte Sweet Microsystems **sans ROM** : deux 6522 VIA, chacune pilotant un
AY-3-8910 (3 tons carrés + 1 bruit + 1 enveloppe par puce → **6 voix**).

| Fenêtre (slot *n*) | Slot 4 | Contenu |
|---|---|---|
| `$Cn00-$Cn0F` | **`$C400`** | VIA #1, miroirs partiels jusqu'à `$Cn7F` |
| `$Cn80-$Cn8F` | **`$C480`** | VIA #2, miroirs partiels jusqu'à `$CnFF` |
| `$Cn40-$Cn44` | `$C440` | SSI263A — variante « Sound II » seulement |

→ `pom2/src/Mockingboard.h:26-33`, `pom2/DEV.md:1257-1259`

Câblage VIA → AY (schéma Sweet = MAME `mockingboard.cpp` = AppleWin
`Mockingboard.cpp:193`) :

```
Port A (ORA, $C401) → bus de données AY D0..D7
Port B bit 0        → BC1
Port B bit 1        → BDIR
Port B bit 2        → /RESET (actif BAS : PB2=0 remet les 16 registres à 0)
```
→ `pom2/src/Ay3_8910.h:32-40`

`{BDIR,BC1}` : `00`→PB=`$04` INACTIVE · `01`→`$05` READ · `10`→`$06` WRITE ·
`11`→`$07` LATCH ADDR. La séquence canonique d'un driver est
**`PB = $07 → $04 → $06 → $04`**, PB2 restant haut (`pom2/DEV.md:1266-1268`).

> **Piège historique de POM2** : PB0=/RESET et PB2=BC1 inversés faisaient
> ressembler chaque strobe INACTIVE à un /RESET, vidant la banque AY — Nox
> Archaist, Ultima IV, Total Replay muets. Corrigé 2026-05-14
> (`src/Mockingboard.h:42-46`).

Initialisation obligatoire : `LDA #$FF / STA $C403` (DDRA) `/ STA $C402` (DDRB),
puis `LDA #$04 / STA $C400`. Un `$00` dans ORB tient /RESET bas — c'est la façon
propre de faire silence.

### 1.2 Les 16 registres

| Reg | Rôle |
|---|---|
| R0/R1, R2/R3, R4/R5 | périodes de ton A/B/C, 12 bits (poids fort = R1/R3/R5[3:0]) |
| R6 | période de bruit, 5 bits (0 = 1) |
| R7 | mixeur : bits 0-2 = *tone disable* A/B/C (actif bas), bits 3-5 = *noise disable* |
| R8/R9/R10 | amplitude A/B/C : bits 0-3 = volume 0-15, **bit 4 = suivre l'enveloppe** |
| R11/R12 | période d'enveloppe, 16 bits |
| R13 | forme d'enveloppe (16 formes) — **toute** écriture la redémarre |
| R14/R15 | ports d'E/S, non câblés sur Mockingboard |

→ `pom2/src/AyPsgSynth.h:223-311` (LFSR 17 bits `x^17+x^14+1`, machine
d'enveloppe MAME-verbatim, 16 formes épinglées)

**Hauteur** : compteur à `horloge/8`, bascule de sortie (÷2 de plus), donc
`f = horloge / (16 × TP)`. À 1 022 727 Hz (`pom2/src/CpuClock.h:26`) :
**`f = 63 920 / TP`**. Repères : C2→TP 977, C3→489, A4 (440 Hz)→145, C5→122,
C6→61, C7→31. Plage utile TP 20…3000 ≈ 21 Hz–3,2 kHz. Table de 5 octaves
= 60 mots = **120 octets**, transposition à l'octave par `lsr`.

> L'AY est cadencé par la **broche 22 du slot** (φ0) : sur les profils PAL de
> POM2 il tourne à 1 015 625 Hz, **12 cents** sous le NTSC, inaudible
> (`pom2/DEV.md:1319-1322`). Corollaire : **un //c+ à 4 MHz ne désaccorde pas la
> Mockingboard**, contrairement à `sfx.s` (§3.4).

### 1.3 L'IRQ de tempo : le T1 du 6522

Convention universelle : **VIA #1, Timer 1, mode continu**, à la cadence du tick
(50/60/25 Hz) → `pom2/src/Mockingboard.h:53-57`.

```asm
        lda #$C0 : sta $C40E    ; IER1 : bit7=set + bit6=T1 → autoriser
        lda #$40 : sta $C40B    ; ACR1 : T1 continu (free-run)
        lda #<P  : sta $C404    ; T1LL
        lda #>P  : sta $C405    ; T1CH → charge et démarre
```

Dans POM2 la période effective en continu est **`latch + 2`**
(`pom2/DEV.md:1275-1281`, aligné MAME `6522via.cpp:927-943`, `IFR_DELAY = 3`) :

| Tick | Cycles | Latch | Octets |
|---|---|---|---|
| 50 Hz | 20 454,5 | 20 452 | `$4F E4` |
| 60 Hz | 17 045,5 | 17 043 | `$42 93` |
| 25 Hz | 40 909 | 40 907 | `$9F CB` |

**Acquittement — le point qui casse tout.** Sur un //e il faut **écrire**
`$7F` dans l'IFR (`$C40D`), jamais lire T1CL :

> L'entrée IRQ du Moniteur //e en `$C3FA` exécute `STA $C007` (SETINTCXROM), qui
> route `$C100-$CFFF` en lecture vers la ROM interne. **Après ça, lire un
> registre Mockingboard renvoie de la ROM, pas l'état du VIA.** Les drivers qui
> acquittent par une lecture de `$C404` se cassent silencieusement ; ceux qui
> écrivent `$7F` dans `$C40D` marchent — les écritures ignorent INTCXROM
> (`Memory.cpp:1050-1066`).
> → `pom2/tests/mockingboard_iie_irq_smoke_test.cpp:16-31`

C'est le motif de Nox Archaist (offset `0x00B6F0` de son HDV). **Règle absolue
pour SCOSWAMP : `LDA #$7F / STA $C40D`.**

### 1.4 Détection, et pourquoi il faut balayer les slots

Routine canonique 4am / Total Replay / French Touch / Nox Archaist, reprise
telle quelle par POM2 comme test — source `deater/dos33fsprogs`,
`demos/demosplash2025/pt3_lib_mockingboard_detect.s` :

```asm
        lda (MB_ADDR_L),Y   ; T1CL en $Cn04
        sta MB_VALUE        ; 3 cycles
        lda (MB_ADDR_L),Y   ; relit
        sec : sbc MB_VALUE  ; attend -8 (8 cycles écoulés)
        cmp #$F8 : beq found
```
→ `pom2/tests/mockingboard_4am_detect_smoke_test.cpp:20-33`

Elle **lit** la fenêtre de slot : à faire une fois dans `main()`, hors IRQ.

**Le balayage est obligatoire, pas optionnel.** POM2 ne met *pas* la
Mockingboard en slot 4 par défaut :

```
"grappler",     // slot 1
"mockingboard", // slot 2  ← DIX & co scannent $C7→$C1 (boot_unidisk.a `bdet`)
"",             // slot 3
"mouseaw",      // slot 4  ← la souris (slot d'Apple, codé en dur par Extasie)
```
→ `pom2/src/SlotConfigurationCoordinator.cpp:49-61`

Un jeu qui code `$C400` en dur ne trouvera rien dans la config POM2 par défaut.
SCOSWAMP doit balayer **`$C7` vers `$C1`** et retenir le premier slot qui
répond. POM2 modélise aussi le fait qu'une Mockingboard est **muette en slot 3**
(`pom2/DEV.md:5063-5065`) — à sauter dans le balayage.

Deux variantes à garder en réserve si le test T1 se révèle capricieux :
écrire-puis-relire un registre AY par la commande READ (`PB = $05`, modélisée —
`src/Mockingboard.cpp:987-993` : la valeur est latchée sur le port A de la VIA) ;
ou **détecter les 6522 par le Timer 2**, ce que fait `MB Audit` de Tom
Charlesworth — mainteneur d'AppleWin — en le jugeant plus fiable que T1
(`github.com/tomcw/mb-audit`). Total Replay, pour mémoire, **ne fait que de la
détection** : `src/hw.mockingboard.a` (MIT), résultat en `MockingboardStuff = $FFF8`
(bit 5 = deux AY, bit 6 = SSI-263, bit 7 = SC-01) — il n'y a aucun lecteur dedans.

### 1.5 Ce que POM2 émule exactement

| Élément | État | Référence |
|---|---|---|
| 2× 6522, décodage `$Cn00`/`$Cn80` + miroirs partiels | ✅ | `src/Mockingboard.cpp:899-921` |
| Ports A/B + DDR · T1 one-shot **et continu** · T2 one-shot phase-2 | ✅ | `src/Via6522.h:331-353`, `DEV.md:1276-1284` |
| IFR/IER (T1=`$40`, T2=`$20`, bit7 = `ifr & ier & 0x7F`) · CA1 edge | ✅ | `src/Via6522.h:77`, `src/Mockingboard.cpp:1070` |
| SR, sorties CA2/CB1/CB2, T2 comptage PB6 | ❌ assumé | `docs/lle_vs_hle.md:107` |
| AY : 3 tons 12 bits, bruit + LFSR 17 bits, 16 enveloppes | ✅ MAME-verbatim | `src/AyPsgSynth.h:223-311` |
| Horloge AY = horloge CPU **vivante** · sync paresseuse des timers à chaque MMIO | ✅ | `src/Mockingboard.cpp:797, 837-897` |
| Stéréo AY1→G / AY2→D `/3` · limitation de bande · blocage DC 20 Hz · file horodatée | ✅ | `DEV.md:1290-1315` |
| Sound II + SSI263 · Phasor (4 AY, 12 voix) | ✅ | `DEV.md:1420-1450, 1518-1580` |

Tout ce dont une musique a besoin est modélisé, et sérieusement : les trois
propriétés du chemin audio ont été corrigées le 2026-08-01 avec mesures — le
point-sampling mettait 7 % de la puissance en repliement inharmonique, la
box-intégration 0,51 % (`DEV.md:1290-1296`). **POM2 est un banc d'essai crédible.**

### 1.6 Activer la carte

**Aucune option de ligne de commande** pour les cartes de slot (vérifié,
`src/CliDispatcher.cpp` ne connaît que `--fujinet-slot`). Deux voies :

1. UI : `Machine → Slot Configuration`, ou Ctrl+Shift+P → « Mockingboard ».
2. `~/.config/pom2/state.cfg` (`src/Settings.cpp:49-59`), clé
   `slot_<n>_card` (`src/SlotConfigurationCoordinator.cpp:112`) :
   `slot_4_card=mockingboard` (ou `mockingboard_c`, ou `phasor`).
   *État actuel de la config utilisateur : `slot_4_card=mouseaw`, et **aucune
   Mockingboard nulle part**.*

Puis `../pom2/build/POM2 --preset iie dist/SCOSWAMP.HDV`.

⚠️ **Pas de musique sur //c sous POM2** : les profils //c/​//c+ portent
`noPhysicalSlots=true` (`src/SystemProfile.cpp:182,234`) et le résolveur vide
tout slot demandé sauf `chatmauve` (`src/SlotConfigurationCoordinator.cpp:148-163`).
Voir §6.4.

---

## 2. Formats et lecteurs existants sur Apple II

### 2.1 Les six candidats sérieux

| Lecteur | Licence | Taille lecteur | CPU @50 Hz | Taille musique | ProDOS ? | IRQ |
|---|---|---|---|---|---|---|
| **PT3 — `pt3_lib` de deater** | **0BSD / GPL-2.0** (au choix) | **2 537 + 143 o** (mesuré par l'auteur) ; **~3 Ko de RAM** + le fichier + 26 o de page zéro | **14,6 %** sur son banc, **16,7-18,1 %** sur 18 morceaux réels | médiane **2 827 o**, moyenne 3 176, max 10 000 (80 fichiers) | ❌ écrit `$03FE/$03FF` en direct | ✅ T1 continu |
| **PT3 — `pt3plr`** (portage ProDOS + **cc65**) | non déclarée ⚠️ | idem | idem | idem | ✅ MLI OPEN/READ/CLOSE | ✅ mais **écrit `$FFFE`/`$03FE` en direct**, contourne ALLOC_INTERRUPT |
| **AKY — Arkos Tracker 3, lecteur 6502 officiel** | **MIT** (tout l'arbre) | **inconnue** (50 299 o de source ACME) | **inconnue**, mais French Touch classe **AKY < CHP < PT3** | inconnue | ❌ à faire | ✅ à câbler |
| **PT3 — `ppt3.a` de French Touch** | GPL-3.0 | **inconnue** (seules des adresses de fin publiées) | > AKY | 1 343 o pour son module embarqué | ❌ | ✅ |
| **FYM** — fenarinarsa | GPL-3.0 | ~555 lignes ACME | **sondé, pas en IRQ** (`JSR $D000` par trame) | « presque le ratio de MYM » sans LZ | ❌ (v2 a *abandonné* ProDOS) | ❌ sondage |
| **Flux de registres brut** (YM/PSG/maison) | — | ~100-300 o | **~3-4 %** (14 reg × 56 cyc) | **700 o/s** = 42 Ko/min | ✅ trivial | ✅ trivial |

Sources : `github.com/deater/dos33fsprogs` → `music/pt3_lib/` (table de tailles/CPU dans
`music/pt3_player/OPTIMIZATION.txt`), `github.com/StewBC/pt3plr` et son fork actif
`github.com/cybernesto/pt3plr`, `bitbucket.org/JulienNevo/arkostracker3` →
`hardware/apple2_oric/playerAky/sources/PlayerAKY_6502.a`,
`github.com/Fr3nchT0uch/DIX` → `OMT_020819/Sources/ppt3.a`,
`github.com/fenarinarsa/FYM`.

### 2.2 Le fait le plus important de cette section

**Arkos Tracker 3 embarque un lecteur AKY 6502 officiel pour Apple II +
Mockingboard, sous licence MIT, et l'éditeur importe le MIDI.**

En-tête du fichier, verbatim :

```
; 6502 ARKOS PLAYER for AKY format (ARKOS TRACKER 2)
;   AKY music player - V1.0. By Julien Névo a.k.a. Targhan/Arkos
;   6502 conversion: Arnaud Cocquière a.K.a GROUiK/FRENCH TOUCH
;   for APPLE IIx + MOCKINGBOARD | ORIC 1/ATMOS
; VERSION 0.10 - 07/2019     MIT / Copyright (c) 2019 Arnaud Cocquière
```

Slot 4 par défaut (`VIA_ORA=$C401`, `VIA_PCR=$C400`, avec le commentaire *« change
this if MB is in slot X → $CX01 »*), `F_SET_REG=$07 / F_INACTIVE=$04 /
F_WRITE_DATA=$06` — exactement la séquence de §1.1. **Un seul AY, 3 canaux**, par
souci de compatibilité Oric. Version courante **Arkos Tracker 3.7 (13/08/2026)**,
macOS Apple Silicon inclus, **MIT partout** : *« The players are MIT-licensed.
Basically, you can use and modify them at will, in any production, free or sold,
open or closed source. »*

Le format **AKY** (« Arkos Tracker YM ») n'est *pas* un vidage de registres : il
exploite la structure du morceau (séquences, sous-séquences, états delta) et —
point décisif ici — **il ne demande aucun tampon** : *« AKY does NOT rely on any
buffer! »*, contrairement à AYC / MYM / FAP. Spécifications dans
`doc/export/AKY.md` et `AKY Algorithm.md`. Import MIDI documenté :
https://www.julien-nevo.com/arkostracker/index.php/midi-import/ (Program Changes →
instruments AY, percussions, vélocités, BPM). **AT3 n'exporte pas PT3** ; sortie
AKY/AKG/AKM + VGM/YM/WAV/MOD/MIDI et des sources par CPU, profil **« 6502 MADS »**
(à reconvertir en ca65).

Réserves honnêtes : **taille et coût CPU du lecteur 6502 non publiés** (seul repère :
AKY = *« 12 scanlines on CPC »* contre AKG *« 25 à 35 »*, et French Touch place
AKY sous PT3) ; source **ACME** à porter en ca65 ; installation de vecteur à
remplacer par un `.interruptor`.

### 2.3 Ce qui ressort du reste de l'état de l'art

- **Le coût du PT3 est un décodeur, pas des écritures.** Les 14 registres vers les
  deux AY coûtent **56 cycles par registre** (`pt3_lib_irq_handler.s`), soit
  ~780 cycles = **3,8 %** à 50 Hz. Les **11 % restants** du 14,6 % sont le moteur de
  patterns / samples / ornements / effets. Un format d'événements sans moteur de
  tracker (§5.2) coûte donc l'ordre de 1-2 % : **conséquence arithmétique, pas
  optimisme.**
- **Le vidage brut est chiffré par l'auteur** : *« 700 bytes (50×14) a second, so
  42k per minute »*. Le même morceau, quatre fois : `.pt3` **3 871 o** · `.ym5`
  7 637 · **brut 137 015 (×35)** · `.pt3`+LZ4 1 793. Mesure indépendante sur deux
  vrais `.psg` : **507 et 1 221 o/s** — les 700 o/s théoriques sont encadrés des
  deux côtés. *(Le PT3 en LZ4 a été mesuré mais jamais implémenté : « that gets
  tricky … and you also need some RAM to decode into ».)*
- **Contrainte matérielle à ne pas rater** : la fiche de l'AY-3-891x plafonne la
  ligne WRITE à **10 µs**. deater la tenait 12 cycles → glitches audibles ; à
  8 cycles *« sounds a lot better »*
  (http://www.deater.net/weave/vmwprod/chiptune/mock_problem/). La séquence de §5.3
  tient WRITE **6 cycles** : conforme.
- **L'AY-3-8913** — la puce de la plupart des clones — a une enveloppe cassée dans
  le grave et un bruit qui exige une manipulation de /RESET ; **8910 et YM2149F sont
  sains** (fenarinarsa, https://www.fenarinarsa.com/?p=3183). POM2 modélise le 8910 :
  **l'émulateur sera plus indulgent que du vrai matériel de clone.**
- **Prior art cc65** : `github.com/jeremysrand/mocklib` (MIT) — Mockingboard + parole
  SSI263 **pour cc65**, mais orientée bruitages. `github.com/Michaelangel007/apple2_mockingboard`
  publie une **table note → période AY avec l'erreur quantifiée** (à reprendre pour
  les 120 o de §1.2). **Aucun exemple public de « cc65 + Mockingboard + IRQ musical »
  n'existe** — ce serait une première.
- **Le meilleur modèle de format est Ultima IV**, dont le driver Mockingboard est du
  code Origin officiel (Kenneth W. Arnold) **entièrement désassemblé** :
  `github.com/sean-gugler/u4remasteredA2`, `src/patchedgame/program/MBSM.s` — ~1,75 Ko
  résidents, **relogés dans les trous de la page texte `$0400-$07F7`**, moteur ADSR
  logiciel, sous-motifs appelables (`jsr_pattern=$80`, `rts_pattern=$81`),
  `clock_default=$429a` (17 050 cycles ≈ une trame). **Il valide l'approche « flux de
  commandes » contre l'approche tracker**, et c'est exactement `MB1` (§5.2).
  *(Dépôt sans licence déclarée.)*
- **Music Construction Set** (Will Harvey, 1983) a livré son lecteur d'interruption
  sur la disquette ; republié en MIT (`github.com/cybernesto/mcs-player`,
  `src/MCS-MB.S` : slot 4 en dur, 6 canaux, `TEMPO`/`DECAY`/`VOICE`, 64 fréquences).
  Il expose **exactement la parade de §6.1** : `PAUSE = SEI + couper les voix +
  réinitialiser la carte`, `CONTINUE = CLI`. **La solution recommandée ici est la
  solution d'époque.**
- Corrections au cahier des charges : **Electric Duet** est bien un moteur
  *haut-parleur* (Paul Lutus, 3 octets/événement, GPL) — mais un portage Mockingboard
  moderne existe (`github.com/cybernesto/electric-mock`, GPL-3.0). « **Musicraft** »
  n'a jamais existé sur Apple II (c'est un produit Amiga devenu Aegis Sonix). Les
  musiques Mockingboard d'**Ultima III/IV/V** étaient du **code Origin officiel**,
  pas un patch de fans. **Nox Archaist** a été composé dans *Bank Street Music
  Writer*, dont le format est décodé et la chaîne vers le MIDI publiée
  (`github.com/erangell/NoxMIDI`, 6 voix = les 6 canaux) — mais le moteur du jeu
  n'est pas public.

## 3. Le budget du jeu

### 3.1 État mesuré

`cd SCOSWAMP/SRC && make check`, exécuté pour ce rapport :

```
  Chargement : $4000      BSS : $9E8E-$A311     Tas : $A311-$BD80 (6767 o)
  Plafond    : $BD80 (__HIMEM__ $BF00 moins 384 o de pile C)
  Empreinte  : 25361 o sur 32128 o          LOWBSS : $1000-$1FAC (reste 83 o)
  OK : tient en mémoire, marge de 6767 octets.
```

| Ressource | Libre | Nature de la contrainte |
|---|---|---|
| **Fenêtre principale** `$4000-$BD80` | **6 767 o** | code + données + BSS + tas ProDOS |
| **LOWBSS** `$1000-$1FFF` | **83 o** | BSS seule (pas de code, pas de données init.) |
| **Language Card** `$D400-$DFFF` | **246 o** | code **lecture seule**, banque 2 |
| `$0C00-$0FFF` | 1 024 o | réservé au 2e tampon ProDOS |
| **RAM auxiliaire** | **~46 Ko** | non gérée par cc65, commutation manuelle |
| **Disque** | ~28 Mo sur 32 | `dist/SCOSWAMP.HDV` = 3,7 Mo |

Segments : `CODE` 22 429 o, `RODATA` 1 419, `DATA`+`INIT` 259, `BSS` 1 156,
`LOWBSS` 4 013, `LC` 2 826 (`build.map:299-313`). *Note : `SCOSWAMP/DOCS/MEMOIRE.md:160-176`
annonce 42 o libres en LC ; la carte actuelle en donne 246 — ligne périmée.*

Le **disque n'est pas une contrainte** (439 images RLE à ~6 Ko = 3,4 Mo ; un
thème de 20 Ko serait du bruit). **La contrainte est la RAM de la fenêtre
principale.**

### 3.2 Le vrai coût de la RAM auxiliaire

64 Ko auxiliaires, dont indisponibles : `$0000-$01FF` (ombre ZP/pile, ALTZP),
`$0400-$07FF` (écran texte 80 colonnes, utilisé en permanence —
`memory_swap.c:92-105`). `$2000-$3FFF` est récupérable car le jeu ne fait pas de
DHGR (`DHIRESOFF` en dernier, `memory_swap.c:44-50`). Reste **~46 Ko**.

**Mais y accéder depuis une IRQ est le point technique dur** : `RAMRD` (`$C003`)
route les lectures de `$0200-$BFFF` vers l'auxiliaire — or le lecteur vit en
`$4000-$9821`, dans cette plage. **Activer RAMRD fait perdre l'exécution.** La
boucle de recopie doit vivre hors de portée de RAMRD : `$0000-$01FF`,
`$C000-$CFFF`, ou `$D000-$FFFF`.

Candidat apparemment naturel : le **segment `LC`** (`$D400-$DFFF`, commuté par
`$C080-$C08F`, indépendant de RAMRD ; 246 o libres ; une boucle aux→principale en
ferait ~40).

> ❌ **Cette piste est morte, et c'est établi, pas supposé.** Le stub d'entrée
> d'interruption de ProDOS 8, `IRQENT` en **`$BFEB`**, fait `BIT RAMIN` **deux
> fois** avant de sauter dans `IRQRECEV` : **la banque 1 de la Language Card est
> commutée en lecture/écriture quand le gestionnaire tourne, et la MLI ProDOS
> occupe `$D000-$FFFF`.** Or cc65 fait tourner son segment `LC` en **banque 2**
> (`crt0.s` : `bit $C081` ×2 pour recopier, puis `bit $C080`). **Tout ce qui est
> dans le segment `LC` de cc65 est illisible depuis un gestionnaire
> d'interruption.** C'est précisément pour ça que cc65 place son propre `intptr`
> dans `LOWCODE` et pas dans `LC`. Règle : **jamais de code ni de données
> d'interruption dans `LC`.**

Reste `a2e.auxmem.emd` (454 o,
`/opt/homebrew/share/cc65/target/apple2enh/drv/emd/`) via `AUXMOVE` (`$C311`) —
mais AUXMOVE occupe `$3C-$3F`/`$42-$43` en page zéro, et ProDOS ne sauve que
`$FA-$FF` (§3.5) : il faudrait sauver/restaurer soi-même, et exiger un INTCXROM
correct. **L'option B devient donc franchement plus coûteuse qu'annoncée**, ce
qui renforce l'option A.

### 3.3 Les options de logement, chiffrées

Ordres de grandeur (justifiés §4.4/§5.2) : flux de registres brut 14 o × 50 Hz
= **700 o/s** (42 Ko/min) ; delta-codé **150-250 o/s** (9-15 Ko/min) ; format à
motifs type PT3 **2-8 Ko par pièce entière** ; liste d'événements maison
**~20 o/s** (1,2 Ko/min).

| Option | Fenêtre principale | Complexité | Verdict |
|---|---|---|---|
| **A. Tout en fenêtre principale** — lecteur + thème résidents, lecture disque au changement de thème | lecteur 600-900 o + plus gros thème | Faible | ✅ **si** le thème tient sous ~2 Ko → format compact obligatoire |
| **B. Thèmes en RAM auxiliaire**, recopiés par tranches de 256 o | lecteur + tampon 256 o + AUXMOVE | **Très haute** — le stub ne peut pas vivre en `LC` (§3.2), reste `AUXMOVE` et sa page zéro | ⚠️ 5 × 9 Ko = 45 Ko sur 46 : marge nulle |
| **C. Streaming disque continu** | lecteur + 2× 512 o | Très haute | ❌ voir ci-dessous |
| **D. Thème en LOWBSS** | 0 | Faible | ❌ 83 octets |

**Pourquoi C est mort** : SCOSWAMP est **entièrement bloquant**. Chaque écran
finit dans `cgetc()` (`wait_any` `scoswamp.c:411`, `wait_key_at` `:1258`,
`wait_space_at` `:1266`). Il n'existe **aucun** point où du code utilisateur
tourne en tâche de fond pour ravitailler un tampon ; tout doit se passer dans
l'IRQ, et une lecture ProDOS depuis une IRQ est interdite.

**→ Option A retenue.** Elle impose un format compact, ce qui est de toute façon
la bonne pression de conception. B reste théoriquement la porte de sortie pour
une v2 plus riche, mais §3.2 l'a nettement alourdie : c'est *un chantier*, pas
*une retouche*. Et §5.2 montre qu'avec un format compact **les cinq thèmes
tiennent résidents** — auquel cas B ne sert plus à rien.

Budget cible pour A :

| Poste | Estimation |
|---|---|
| Lecteur 6502 en IRQ (`music.s`) | 500-700 o `CODE` |
| Table de notes (5 octaves) | 120 o `RODATA` |
| Détection + init + API C | 150-250 o `CODE` |
| État du lecteur (curseurs, 6 voix) | ~60 o (`LOWBSS`, il y a 83 o) |
| Tampon du thème courant | **2 048 o** `BSS` |
| **Total** | **~3,1 Ko sur 6 767** → reste ~3,6 Ko |

### 3.4 Cohabiter avec `sfx.s`

`SCOSWAMP/SRC/sfx.s` (144 lignes) synthétise sur le haut-parleur par **boucles
de délai calibrées** : `$C030` inverse la membrane à chaque lecture, la hauteur
est l'inverse d'un délai compté à vide (`sfx.s:29-35`), donc **liée à l'horloge
CPU** (`sfx.s:7-9`). `sweep` balaye la période ; `steplen` (demi-ondes par
palier) décide si l'oreille entend un choc transitoire ou une note chantée —
c'est ce qui sépare le coup d'épée de la chute d'un corps (`sfx.s:39-45`,
`TODO.md:226-232`). Cinq entrées appelées depuis `run_combat`
(`scoswamp.c:1599,1623,1656,1660`). Un balayage coûte de l'ordre de
**0,3 à 1 s de CPU pleine** (`TODO.md:224-226`).

**Le conflit est réel.** Une IRQ musicale de 600 cycles tombant au milieu d'une
boucle de délai cycle-comptée l'allonge de 600 cycles : le bruitage se
**désaccorde et craque à 50 Hz**. C'est audible.

| Politique | Coût | Effet |
|---|---|---|
| **1. `php/sei … plp` autour de chaque `_sfx_*`** | 8 octets | La musique **saute** 0,3-1 s et le tempo dérive d'autant. Acceptable au tour par tour, où le bruitage *est* la ponctuation. |
| 2. Couper la musique pendant le combat | ~0 | Perd le thème de combat, justement demandé. |
| 3. Porter les bruitages sur l'AY (canal C + bruit, R13 en enveloppe descendante) | ~300 o | Le plus propre musicalement, supprime le conflit — mais muet sans carte, donc `sfx.s` reste en secours : deux implémentations. |

**Recommandation : 1 en v1, 3 en v2.** Le `TODO.md:233-234` disait déjà « le
Mockingboard demandera une autre couche, pas une retouche de celle-ci » : c'est
exactement ça, plus huit octets de `php/sei/plp`.

### 3.5 cc65 et les interruptions : la plomberie est déjà là

Le runtime `apple2enh` traite les `.INTERRUPTOR` **comme des gestionnaires
d'interruption ProDOS 8** : *« The runtime … uses routines marked as
`.INTERRUPTOR` for ProDOS 8 interrupt handlers. Such routines must be written as
simple machine language subroutines and will be called automatically »*
(<https://cc65.github.io/doc/apple2enh.html> §9.3) — et la limite DOS 3.3 confirme l'allocation à
l'init : *« Any attempt to use it yields the message 'Failed to alloc interrupt'
on program startup »* (même document, §8.1).

**Vérifié sur la bibliothèque installée** (cc65 2.19, `ar65 x apple2enh.lib
irq.o`) : `irq.o` vient de `apple2/irq.s`, exporte `initirq`/`doneirq`/`callirq`,
et contient un `JSR $BF00` suivi de `$40` (ALLOC_INTERRUPT), un autre suivi de
`$41` (DEALLOC_INTERRUPT) et un `JSR $FDED` (COUT) pour l'erreur. Le source amont
— `libsrc/apple2/irq.s`, **partagé par `apple2` et `apple2enh`**, il n'existe pas
de `libsrc/apple2enh/` — dit le reste :

```asm
initirq:                        ; constructeur priorité 10, segment ONCE
        lda  __dos_type : beq prterr                ; DOS 3.3 -> erreur + exit
        jsr  $BF00 : .byte $40 : .addr i_param      ; ALLOC_INTERRUPT
        bcs  prterr
        cli                     ; vieux ProDOS (1.1.1) saute aux SYS avec I=1
        rts
intptr: cld                     ; segment LOWCODE -- surtout PAS LC (§3.2)
        jsr  callirq
        bcc  :+
        clc : rts               ; traité     -> ProDOS veut carry CLEAR
:       sec : rts               ; pas à nous -> ProDOS veut carry SET
```

**Deux conventions de carry opposées, et cc65 fait la traduction.** Côté cc65
(`runtime/callirq.s`) : *« all interrupt routines will be called with carry clear
on entry »*, et **carry SET = traité**. Côté ProDOS 8 (TechRef §6.2) : **carry
CLEAR = traité**. `intptr` inverse — écrire directement pour ProDOS serait une
erreur.

Le crochet automatique est le `import = __CALLIRQ__` que **`scoswamp.cfg:60-65`
déclare déjà** (bloc `CONDES type = interruptor` identique au stock
`apple2enh.cfg`) : dès qu'un module déclare un interrupteur, le lien tire
`runtime/callirq.s`, qui déclare `.constructor irq_init, 10` /
`.destructor irq_done, 10`. Aucun interrupteur ⇒ aucun ALLOC_INTERRUPT. **Rien à
changer dans la config de lien** : un `.interruptor music_irq` dans `music.s`
suffit.

**Le contrat ProDOS que le gestionnaire doit respecter** (TechRef §6.2 +
Technical Note #12, https://prodos8.com/docs/technote/12/) :

| Règle | Conséquence pour `music.s` |
|---|---|
| Commencer par `CLD`, finir par `RTS` — **jamais `RTI`** | `intptr` s'en charge ; ne pas l'imiter à la main |
| **Jamais de `CLI`** dans le gestionnaire | on ne peut pas raccourcir la fenêtre masquée de §6.1 depuis l'intérieur |
| Rendre les banques **dans l'état trouvé**, LC laissée en écriture | interdit de bricoler `$C08x` ; et cf. §3.2 |
| ProDOS ne sauve que **`$FA-$FF`** (6 o de page zéro) + les registres | **ces 6 octets sont donc gratuits** pour le lecteur ; tout autre usage de la ZP doit être sauvé soi-même (cc65 occupe `$0080-$0099`) |
| **Aucun appel MLI** depuis un interrupteur | pas de `fopen`/`fread` : cf. §3.3, option C |
| Max **4** gestionnaires, polling croissant, le premier installé prioritaire | cc65 en occupe **un** — ne jamais appeler `$BF00`/`$40` soi-même |
| Pointeur de gestionnaire à **poids fort non nul** | pas de gestionnaire en page zéro (rejeté `$53`) |
| IRQ non réclamée : tolérée **255 fois**, puis `SYSTEM FAILURE ERR=$01` | ne pas rendre carry SET « au cas où » |

Vecteurs : `$BF80/81` … `$BF86/87` = **INTRUPT1-4**. *(Correction au cahier des
charges : `$BF32-$BF3F` est **DEVLST**, la liste des unités disque, et `$BF40`
ouvre la chaîne `"(C)APPLE'83"` — `$BF3F` n'est pas un vecteur d'interruption.)*

Deux décisions de conception :

1. *Comment savoir que l'IRQ vient de nous, si lire l'IFR est interdit (§1.3) ?*
   **Acquitter inconditionnellement** — écrire `$7F` dans `$C40D` est idempotent
   et inoffensif même si l'IRQ venait d'ailleurs — puis rendre carry SET
   seulement si l'on est bien la source armée.
2. `set_irq()` de `<6502.h>` **n'est pas le bon outil** :
   `libsrc/common/interrupt.s` sauve et restaure **20 octets de page zéro**
   (`zpspace = 26` moins `regbanksize = 6`) plus 4 empilements par interruption,
   pour se croiser en C. Le wiki cc65 le dit lui-même : *« the wrapper code
   written in Assembly is more than what has to be done in the interrupt handler
   itself »*. Le lecteur doit être **entièrement en assembleur**, en
   `.interruptor`.

---

## 4. La chaîne Suno → Mockingboard

### 4.1 Suno en 2026 : ce qui a changé, et ce qui bloque

**Pas d'API publique.** Aucune API self-serve, aucune console développeur, aucun
tarif ni quota publié : la génération passe par le web et l'application. Le
1er juillet 2026, Suno a ouvert un formulaire d'admission pour « un groupe
restreint de partenaires », sans calendrier ni critères
([MBW](https://www.musicbusinessworldwide.com/suno-explores-developer-api-seeking-apps-that-unlock-experiences-generative-music-makes-possible-for-the-first-time/)).
Les revendeurs tiers (sunoapi.org, ApiPass, aimlapi, Replicate, EvoLink…,
0,014 à 0,111 $ par morceau) **violent tous les CGU**, qui interdisent
explicitement *« data mining, robots, scraping »*. Aucun n'expose d'endpoint MIDI.
`gcui-art/suno-api` (LGPL-3.0, 3 194★) est figé depuis mars 2026 et réclame votre
propre cookie de session plus un compte 2Captcha.

**Correction au cahier des charges : Suno exporte désormais du MIDI.** Suno
Studio 2.0 (13 août 2026, **Premier uniquement**) ajoute l'import/édition MIDI sur
timeline et surtout **« Get MIDI » depuis un stem** — 10 crédits par stem,
~0,03 $ ([help.suno.com/13670529](https://help.suno.com/en/articles/13670529)).
La séparation en stems existe aussi (Auto Split 12 catégories ; Advanced Split
~100 instruments, Premier). Mais **cela ne change pas la nature du problème** :
Suno est un modèle audio latent sans représentation symbolique interne, donc
« Get MIDI » **est lui-même un transcripteur audio→MIDI greffé après coup**. La
qualité rapportée suit exactement ce qu'on attend : batterie propre, mélodie
correcte, basse moyenne (notes fantômes sous la grosse caisse), **accords et
nappes mauvais, à redessiner à la main**.

**Et c'est là que ça bloque pour SCOSWAMP.** Cinq obstacles, dont trois
rédhibitoires pour un dépôt GPL v3 :

| Obstacle | Détail | Gravité |
|---|---|---|
| **Gratuit = non commercial, et Suno reste propriétaire** | CGU : *« you will only use such Outputs for your lawful, personal and non-commercial purposes »* ; centre d'aide : *« Suno is the owner of the songs »* | **Incompatible GPL v3**, qui doit autoriser la redistribution commerciale en aval |
| **Clause anti-ML** (User Conduct §10) | interdiction d'utiliser l'Output pour *« power, enable or train other artificial intelligence and machine learning models »* | **Faire tourner Basic Pitch ou MuScriptor sur du Suno tombe dedans** |
| **Clause anti-altération** | interdiction de retirer ou contourner l'empreinte / filigrane / métadonnées ajoutés à l'Output | **Une transcription vers des registres AY détruit le filigrane par construction** |
| Plafonds de téléchargement, **effectifs aujourd'hui même (2026-09-03)** | Gratuit **7 téléchargements à vie** ; Pro 20/mois ; Premier 60/mois — **rétroactifs sur la bibliothèque existante**. Motif officiel : *« make it harder for bad actors to mass-export music »* ([Variety](https://variety.com/2026/music/news/suno-unveils-download-caps-for-free-paid-tiers-generator-1236831589/)) | Gênant ; les exports Studio en sont exemptés (Premier) |
| Absence de garantie de droit d'auteur | CGU : *« Suno makes no representation or warranty to you that any copyright will vest in any Output »* | On ne sait pas ce qu'on licencie |

Les tiers payants (Pro 8 $/mois, Premier 24 $/mois annualisés) **cèdent** bien les
droits — *« Suno hereby assigns to you all of its right, title and interest in and
to any Output »* — mais **sans rétroactivité** : un morceau fait en gratuit reste
non commercial même après abonnement, il faut le régénérer.

**Le contentieux, et il n'est pas théorique.** *UMG v. Suno* (D. Mass.,
1:24-cv-11611) : Warner a transigé en novembre 2025, **UMG et Sony plaident
toujours**, l'assiette étant passée à 61 026 enregistrements. Surtout, en
Allemagne, **GEMA a gagné** : Tribunal régional de Munich I, 42 O 763/25,
jugement du **31 juillet 2026**, qui interdit quatre actes dont **la reproduction
et la communication au public *par les Outputs eux-mêmes*** — avec **jusqu'à
250 000 € par violation future**
([JUVE](https://www.juve-patent.com/cases/munich-regional-court-stops-suno-using-gema-protected-music/)).
**C'est à ce jour la seule décision au monde qui juge les fichiers de sortie
contrefaisants.** Elle n'est pas définitive et vise Suno, pas ses utilisateurs.

**Et un obstacle qui ne dépend d'aucun éditeur** : le rapport Partie 2 du
*US Copyright Office* (29 janvier 2025) retient qu'une production entièrement
générée par IA en réponse à une invite **est dépourvue de paternité humaine et
n'est donc pas protégeable**, et que *« even if a prompt is extremely detailed or
complex, it does not confer copyright ownership »*. Autrement dit : **on ne peut
probablement pas licencier valablement de l'audio brut généré sous GPL v3, faute
de tenir quoi que ce soit à licencier.**

### 4.2 Transcription audio → MIDI sur macOS Apple Silicon, 2026

| Outil | Licence | Apple Silicon | État | Verdict |
|---|---|---|---|---|
| **MuScriptor** (Kyutai/Mirelo, ISMIR 2026) | code **MIT**, **poids CC-BY-NC-4.0** | **MPS natif fp16**, `--device auto` ; M4 Max : 4:46 de musique en 76 s avec `large` | PyPI 0.3.0, 08/2026, 1 339★ | **Le meilleur** : Onset F1 **60,4** contre 32,5 pour YourMT3+ ; multi-instrument, batterie, quantification au tempo. **Poids non commerciaux** |
| **Basic Pitch** (Spotify) | **Apache-2.0**, poids inclus | **CoreML est le backend macOS par défaut** — TensorFlow n'est pas requis (vérifié dans les métadonnées PyPI) | 0.4.0 (2024-08), **zéro commit en 2026**, plafond **Python 3.11** | Utile pour **les pitch bends**, que MuScriptor ne donne pas. Mais *« model not trained on multi-instrument mixtures »*, **pas de batterie**, pas d'attribution d'instrument |
| **Demucs** (séparation) | MIT | *« On Apple Silicon, the GPU is used automatically through Metal (MPS) »* | **`adefossez/demucs` 4.1.0 (07/2026)** — le dépôt Meta est **archivé** | Oui. `uvx demucs FILE` |
| **audio-separator** | MIT | PyTorch → MPS, ONNX → CoreML | 0.47.0 (08/2026) | **La meilleure option Mac** en 2026 |
| **MT3** (Google) | Apache-2.0 | — | **install cassée** (issue #172 ouverte) | **À ne pas utiliser** |
| **Omnizart** | MIT | ressuscité 05/2026 ; **l'app *chord* échoue sur arm64** (Vamp x86 seulement, PR #117 non fusionnée) | 0.6.3 | Marginal |
| **beat_this** (grille rythmique) | **MIT, code *et* poids** | torch ≥2.0 → MPS | 1.1.0, 04/2026 | **Préférer à `madmom`**, dont les *modèles* sont CC BY-NC-SA |

**La chaîne recommandée en 2026 sur un Mac Apple Silicon** :
`audio-separator` (ou `uvx demucs`) → `uvx muscriptor transcribe song.wav
--detect-tempo true` → retouche manuelle. Tout le monde s'accorde sur un point :
**la retouche manuelle n'est pas optionnelle.**

**Et le fait qui tranche §4.3 : aucun outil audio → AY n'existe. Pas un seul.**
Recherches exhaustives sur « audio to ay », « wav to ym », « audio to PSG »,
« chiptune resynthesis », « audio to SID » : uniquement des émulateurs, des
lecteurs et des trackers. Il existe **un** précédent architectural sérieux,
**`SampleToNES`** (MIT, PyPI 08/2026) : une resynthèse spectrale par recherche —
*« for every frame the system must pick, from a large but finite catalogue of NES
waveforms, the combination of instructions whose mixed output best matches that
slice of audio »* — avec des cadences de trame **incluant 50 Hz PAL**. Elle vise
le 2A03 du NES, pas l'AY, mais l'architecture se généralise. **Ce serait un
projet de recherche à soi seul.**

### 4.3 La vraie difficulté : réduire à 3 voix carrées

C'est ici que la chaîne casse, et le raisonnement ne dépend d'aucune recherche.

Le « Get MIDI » de Studio 2.0 (§4.1) ne résout rien ici : il rend un MIDI
polyphonique complet, pas un arrangement à trois voix. Un morceau Suno reste un
**mixage polyphonique** — batterie, basse, nappes, voix, réverbération. La
Mockingboard offre **trois oscillateurs carrés, un générateur
de bruit et une enveloppe** par puce, avec **un volume sur 4 bits** et **aucun
timbre réglable**. Le taux de compression informationnelle entre les deux est de
plusieurs ordres de grandeur. La transcription automatique ne « réduit » pas la
musique : elle en jette 95 % et rend un squelette. Ce squelette n'est pas
mauvais — c'est simplement **un arrangement, et personne ne l'a arrangé.**

Ce qu'il faut décider, morceau par morceau, et qu'aucun outil ne décide bien :

| Décision | Ce qui se passe si on la laisse à un outil |
|---|---|
| **Quelles 3 notes garder** à chaque instant sur les 10-30 du mixage | Les outils prennent les plus fortes ; on obtient la ligne de basse et deux harmoniques, jamais la mélodie perçue |
| **Quelle voix porte la mélodie**, laquelle la basse, laquelle l'accompagnement | Assignation instable : la mélodie saute de voix en voix, ce qui s'entend comme des craquements |
| **Percussion** : la caisse claire va sur le canal bruit + R13, la grosse caisse sur une chute de période de ton | Aucun transcripteur ne produit ça ; il rend des notes de batterie en MIDI canal 10 qu'il faut réinterpréter à la main |
| **Quantification au tick 50 Hz** (20 ms) | Un swing ou un triolet mal quantifié donne un rythme boiteux ; il faut choisir la grille, pas l'arrondir |
| **Arpèges** : sur 3 voix, un accord se joue en arpège rapide (la signature du chiptune) | Aucun outil ne convertit « accord de 4 notes » en « arpège à 50 Hz sur une voix » |
| **Enveloppes** (R13) pour donner une attaque | Perdu par construction : le MIDI n'a pas la notion |

**Conclusion de cette sous-section, indépendante du reste** : la partie
« créative » de la chaîne — celle qui décide de la musique — n'est pas
automatisable avec les outils de 2026. Un tracker la rend triviale ; une chaîne
audio→MIDI→AY la rend pénible et le résultat sonne accidentel.

### 4.4 Conversion vers le format du lecteur

Une fois qu'on tient un MIDI **déjà réduit à 3 pistes monophoniques + percussion**,
la conversion mécanique est un problème résolu — et la recherche a trouvé les
outils exacts, tous vérifiés :

| Outil | Licence | Fait quoi | État |
|---|---|---|---|
| **Arkos Tracker 3.7** | **MIT** | **importe le MIDI** (Program Change → instrument AY, percussions, vélocités → volumes, BPM) puis exporte AKY + le lecteur 6502. **Exige un MIDI format 1, une piste par instrument, quantifié** | 08/2026, **Apple Silicon natif** |
| **`spectrumizer`** | **MIT** | **le seul écrivain PT3 en Python** (`pip install spectrumizer`, dépend de `mido`). Réduction *skyline* à ≤3 voix monophoniques, vélocité → volume, percussions GM → bruit AY, arpèges d'accords, basse à enveloppe matérielle | PyPI 06/2026, **1★, non éprouvé** |
| **`midi2ay`** | libre | **MIDI → flux de registres AY brut**. Format `OUT` : groupes de 4 octets — *« time (2 bytes): 1/50th seconds elapsed since previous write; register (1 byte); value (1 byte) »*. Réduction : les 3 notes de plus fort poids (note × vélocité), **percussions ignorées** | ancien |
| **`miditones`** | MIT | MIDI → flux de commandes de notes compact, **`-t=n` jusqu'à 16 générateurs** (`-t=3` pour un AY, `-t=6` pour deux), stratégies d'allocation `-sn`, et il **rapporte combien de notes il a jetées** | 04/2025, 174★ |
| **`zxtune123 --convert mode=aydump`** | LGPL-3.0 | n'importe quel module AY → **14 octets par trame, purs, sans en-tête**. Aussi `mode=psg`, `mode=fym`, `mode=txt` (= texte Vortex) | **actif 08/2026** |
| **Furnace** (export FCS) | GPL-2.0+ | **refuse l'import MIDI par principe** (*« Furnace is not a MIDI tracker »*) mais exporte un **flux de commandes** *« useful if you're a developer and want to use a command stream dump… writing a hardware sound driver »* — le format le plus proche de `MB1` | actif |

Deux voies, donc :

| Voie | Comment | Coût | Qualité |
|---|---|---|---|
| **A. MIDI → Arkos Tracker 3 → AKY → lecteur 6502 MIT** | tout existe, tout est maintenu, tout est MIT | **0 ligne de conversion** | la meilleure : on édite dans un vrai tracker après l'import |
| **B. MIDI → `MB1`** | `mido` pour lire, quantification 50 Hz, encodage §5.2 — ou partir de `miditones -t=3`, dont le flux de commandes est presque `MB1` | ~200 lignes Python | dépend entièrement du MIDI d'entrée |

**A est meilleure sur tous les axes sauf un** : la taille du lecteur AKY 6502
n'est pas publiée (§2.1). C'est mesurable en une demi-journée — **étape 0 du
plan** (§7.4).

### 4.5 `suno_to_mb.py` — squelette

À prendre pour ce qu'il est : la **partie mécanique** de la chaîne. Il ne
remplace pas §4.3.

```python
#!/usr/bin/env python3
"""suno_to_mb.py -- audio Suno -> MUSIC/xxx.MB (format MB1, cf. §5.2).
    python3 suno_to_mb.py theme.mp3 -o MARAIS.MB --tick 50 --loop
Chaine : demucs (separation) -> basic-pitch (audio->MIDI par stem)
      -> reduction 3 voix + percussion -> quantification -> encodage MB1.
L'etape de reduction est celle qui demande une oreille (§4.3)."""
import argparse, struct, subprocess, sys, tempfile
from pathlib import Path

CPU_HZ, AY_DIV = 1_022_727, 16       # f = CPU_HZ / (16 * TP)  -- CpuClock.h:26
NOTE_LO = 36                          # C2 ; 60 entrees jusqu'a B6

def separate(src: Path, out: Path) -> dict:
    """htdemucs -> bass / drums / other / vocals. MPS sur Apple Silicon."""
    subprocess.run(["demucs", "-n", "htdemucs", "-o", str(out), str(src)],
                   check=True)
    return {p.stem: p for p in (out / "htdemucs" / src.stem).glob("*.wav")}

def to_midi(wav: Path, out: Path) -> Path:
    """Basic Pitch. On l'applique a des stems quasi monophoniques : le seul
    regime ou il est fiable."""
    from basic_pitch.inference import predict_and_save
    from basic_pitch import ICASSP_2022_MODEL_PATH
    predict_and_save([str(wav)], str(out), True, False, False, False,
                     model_or_model_path=ICASSP_2022_MODEL_PATH)
    return next(out.glob(f"{wav.stem}*.mid"))

def reduce_to_voices(midis: dict, tick_hz: int):
    """-> (voix[3], percu), voix[i] = [(tick, note, vol_0_15), ...]

    Politique par defaut, a retoucher a l'oreille :
      voix 0 <- vocals/other : la note la plus AIGUE  (melodie percue)
      voix 1 <- other        : la fondamentale de l'accord
      voix 2 <- bass         : la plus GRAVE
      percu  <- drums        : onsets -> bruit R6/R7 + enveloppe R13
    Toute autre politique est aussi legitime : c'est un choix musical."""
    raise NotImplementedError("arrangement -- voir §4.3")

def note_to_tp(note: int) -> int:
    f = 440.0 * 2 ** ((note - 69) / 12.0)
    return max(1, min(4095, round(CPU_HZ / (AY_DIV * f))))

NOTE, OFF, VOL, END = 0x80, 0x90, 0xA0, 0xE0

def encode(voices, perc, tick_hz, loop) -> bytes:
    out = bytearray(b"MB1\0" + bytes([tick_hz, 1 if loop else 0]))
    out += struct.pack("<H", 8)                       # loop_offset
    events = sorted((t, v, n, a) for v, evs in enumerate(voices)
                                 for (t, n, a) in evs)
    now = 0
    for t, v, n, a in events:
        while t - now > 127:                          # DELAY tient sur 7 bits
            out.append(127); now += 127
        if t > now:
            out.append(t - now); now = t
        out += bytes([NOTE | v, max(0, min(59, n - NOTE_LO))])
        if a != 15:
            out += bytes([VOL | v, a])
    out.append(END)
    return bytes(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--tick", type=int, default=50, choices=(50, 60))
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        stems = separate(Path(a.audio), tmp)
        midis = {k: to_midi(v, tmp) for k, v in stems.items()}
        voices, perc = reduce_to_voices(midis, a.tick)
    Path(a.out).write_bytes(encode(voices, perc, a.tick, a.loop))
    print(f"{a.out}: {Path(a.out).stat().st_size} octets")

if __name__ == "__main__":
    sys.exit(main())
```

**Taille de sortie pour 60 s** — comptée sur l'encodeur ci-dessus, densité
moyenne de 4 événements par seconde et par voix :

| Contenu | Octets |
|---|---|
| En-tête | 8 |
| 3 voix × 4 notes/s × 60 s × 2 o (NOTE) | 1 440 |
| Les mêmes coupures (OFF, 1 o) | 720 |
| DELAY (≈ 1 o par événement) | 720 |
| Changements de volume occasionnels | ~150 |
| **Total** | **≈ 3 040 o pour 60 s**, soit **~50 o/s** |

C'est **2,5 fois** l'estimation de §5.2 (20 o/s), parce que §5.2 suppose une
écriture *musicale* clairsemée et qu'une transcription automatique est **dense**
— elle émet une note à chaque changement détecté. Autre façon de le dire : **la
transcription automatique coûte 2,5× plus de RAM pour un résultat moins bon.**
Un thème de 90 s transcrit ferait ~4,5 Ko et ne tiendrait plus dans le budget de
§3.3 sans sacrifier autre chose.

### 4.6 Les cinq voies, comparées

La recherche a fait apparaître deux options que le cahier des charges
n'envisageait pas — et qui sont meilleures que celle qu'il proposait.

| | **1. Suno audio → transcription → AY** | **2. Suno comme esquisse, tracker pour la partition** | **3. IA *symbolique* → MIDI → AY** | **4. Tracker seul** | **5. Chiptune CC0 existant** |
|---|---|---|---|---|---|
| Générateur | Suno (audio) | Suno (écoute seule) | **text2midi** (code MIT + poids **Apache-2.0**) ou **Magenta RealTime 2** (Apache-2.0 / CC-BY-4.0, *« Google claims no rights in outputs »*) | aucun | OpenGameArt CC0 |
| Chaîne | demucs + MuScriptor + script + `MB1` | Arkos Tracker 3 | text2midi → `spectrumizer`/Arkos → PT3/AKY | Arkos Tracker 3 | conversion PT3 |
| Effort/thème | 1-2 h de script **puis plusieurs heures de retouche** | 30 min d'écoute + 2-4 h de tracker | 1-2 h + retouche | 2-5 h | ~30 min |
| Taille/thème | ~3-4,5 Ko (dense) | 1-3 Ko | 1-3 Ko | 1-3 Ko | 1-3 Ko |
| Qualité | **accidentelle** | maîtrisée | correcte mais **en deçà de Suno** (l'étude de text2midi le dit : 4,62/7 contre 5,79/7 pour du MIDI humain) | maîtrisée | variable |
| **Statut juridique** | ❌ **triplement bloqué** (§4.1) | ✅ composition humaine | ✅ **licences propres de bout en bout** | ✅ | ✅ **CC0, compatible GPL v3 sans discussion** |
| Chaîne maintenue | non | oui | oui | oui | — |
| Précédent | **aucun au monde** | flux normal du chiptune | LakhNES (2019, sans licence) | 30 ans | — |

Trois observations qui tranchent :

- **Demander « chiptune 8-bit, 3 voix carrées » à Suno ne sert à rien.** Vérifié :
  **aucun paramètre, balise ou champ de Suno n'expose le nombre de voix, la
  densité de notes, le rapport cyclique ou la forme d'enveloppe.** L'invite « 3
  voix » n'a rien à quoi se raccrocher. On obtient un mix stéréo dense et
  réverbéré qui *évoque* le chiptune — des leads carrés sur une vraie batterie —
  soit exactement la pire matière première pour une cible à 3 voix. La qualité
  audio elle-même est critiquée par les compositeurs (*« grainy and harsh, with a
  smeared/brittle top end »* même en WAV).
- **Personne n'a jamais fait « Suno → tracker ».** Recherche exhaustive sur
  GitHub et le web : aucun dépôt, aucun devlog, aucune entrée de jam. L'IA
  musicale est courante dans les game jams, mais **toujours livrée en fichiers
  audio bruts**. Il n'y a aucun art antérieur à copier.
- **Si l'on veut de l'IA, il faut lui demander du MIDI, pas de l'audio.**
  `text2midi` (MIT + Apache-2.0) et Magenta (Apache-2.0) sont **les deux seuls
  générateurs de tout ce rapport dont le code, les poids *et* les sorties soient
  indiscutablement redistribuables**. Ils produisent du MIDI épars par
  construction — c'est-à-dire exactement la forme dont une puce à 3 voix a
  besoin. Bonus : l'*Anticipatory Music Transformer* (Apache-2.0) fait du
  **remplissage** — on écrit à la main une mélodie adaptée à la puce, il complète
  basse et contre-chant **à l'intérieur du budget de voix**.

## 5. Conception côté jeu

### 5.1 Les cinq thèmes

| Thème | Déclencheur | Durée | Boucle | Caractère | Voix |
|---|---|---|---|---|---|
| **Accueil** | `main()` après `select_language()` / `load_scene(0)` | 40-60 s | ✅ | modal, solennel | 3 tons |
| **Marais** | `load_scene(n)`, pages narratives | 60-90 s | ✅ | lent, clairsemé : nappe grave + arpège lointain | 2 tons + bruit léger |
| **Combat** | entrée de `run_combat()` (`scoswamp.c:1512`) | 20-30 s | ✅ | rythmique, tempo double, percussion sur le bruit | 3 tons + bruit |
| **Victoire** | `run_combat()` → 1 (`scoswamp.c:1618`) | 4-6 s | ❌ | fanfare montante | 3 tons |
| **Mort** | `game_over()` `:1716`, `die_and_restart()` `:1769` | 6-8 s | ❌ | chute, cadence mineure | 2 tons |

Deux décisions :

- **Le thème du Marais ne se recharge pas à chaque page.** `load_scene` tourne à
  chaque clairière ; recharger 400 fois ferait entendre le silence à chaque
  transition. Le lecteur garde `current_theme` et ne fait rien si le thème
  demandé est déjà là. Seuls les *changements* touchent le disque.
- **Les one-shots doivent être résidents.** Une lecture disque juste après un
  combat, écran figé, s'entend. Une fanfare de 5 s fait ~200 octets : les garder
  en RODATA coûte 350 o et supprime le problème.

**Stéréo** : AY1 est entièrement à gauche, AY2 entièrement à droite
(`pom2/DEV.md:1310-1315`) — **le panning par canal est impossible**, French Touch
l'a documenté en concevant son PT3 6 canaux (§2.3). Une musique 3 voix sur AY1
seul est donc **collée à gauche**. Trois choix : dupliquer les écritures sur AY2
(image centrée, coût CPU ×2), ou le contournement French Touch (A → AY1 ch1,
B → AY1 ch2 *et* AY2 ch2, C → AY2 ch3, ce qui donne un semblant de largeur),
ou 6 voix en stéréo franche. **Recommandation : dupliquer sur AY2** — le coût
reste sous 2 % (§5.3) et une musique de jeu doit être centrée.

### 5.2 Format de données : `MB1`

Un **flux d'événements horodatés en ticks**, une seule piste entrelacée (un seul
curseur à tenir), le plus compact possible.

```
En-tête (8 o)
  +0  'M','B','1',0     magie + version
  +4  tick_rate         50 ou 60
  +5  flags             bit0 = boucle, bit1 = duplique sur AY2
  +6  loop_offset       mot 16 bits

Flux, premier octet = commande :
  $00..$7F  DELAY n     attendre n ticks
  $80|v     NOTE  v     + 1 o : note 0-59 → TP depuis la table, R7, R8+v
  $90|v     OFF   v     couper la voix v
  $A0|v     VOL   v     + 1 o : volume 0-15
  $B0       NOISE       + 2 o : R6, masque R7
  $C0       ENV         + 3 o : R11, R12, R13
  $D0|v     ENVON v     la voix v suit l'enveloppe (bit 4 de R8+v)
  $E0       END         boucle si flags.bit0, sinon silence
```

Coût typique : une mesure à 120 BPM = 2 s = 100 ticks ; 3 voix, ~8 notes :
8×2 (NOTE) + 8×1 (OFF) + ~16×1 (DELAY) = **40 o pour 2 s**, soit **~20 o/s**
→ **1,2 Ko/minute**.

| Thème | Durée | Taille |
|---|---|---|
| Accueil (3 voix) | 60 s | ~1 300 o |
| Marais (2 voix clairsemées) | 90 s | ~1 100 o |
| Combat (3 voix + bruit dense) | 30 s | ~1 000 o |
| Victoire / Mort | 5 s / 7 s | ~180 o / ~150 o |
| **Total disque** | | **~3,7 Ko** |
| **Plus gros thème résident** | | **1 300 o** |

Un tampon de **2 048 o** couvre tout. On pourrait même garder **les cinq thèmes
résidents** (3,7 Ko sur 6,7 de marge) et **supprimer tout accès disque** — à
trancher à la mesure, mais c'est séduisant : cela annule le risque §6.1.

Fichiers : `MUSIC/ACCUEIL.MB`, `MARAIS.MB`, `COMBAT.MB`, `VICTOIRE.MB`,
`MORT.MB`. ⚠️ **Il faut ajouter `MUSIC` à `PAYLOAD`** dans
`SCOSWAMP/SRC/Makefile:172-179`, sinon `make hdv` répondra « Nothing to be done »
après une modification de musique — le piège exact qui a déjà coûté une séance
de débogage (`Makefile:157-171`).

### 5.3 Le lecteur 6502

```
music.s   (assembleur, segment CODE)
  ├─ _music_detect     balaye $C7→$C1 (saute $C3), pose mb_slot (0 = absente)
  ├─ _music_init       DDRA/DDRB, /RESET, T1 continu, IER
  ├─ _music_play (A)   pose les curseurs, arme
  ├─ _music_stop       R7 = $3F + volumes 0, désarme IER
  ├─ _music_pause / _music_resume    (autour des E/S disque, §6.1)
  ├─ music_irq         .interruptor -- le tick
  │    ├─ delay-- ; si non nul → acquitte, carry clear, rts
  │    ├─ décodage des paquets jusqu'au prochain DELAY
  │    └─ ay_write : LATCH/WRITE par registre modifié
  └─ note_table        60 mots 12 bits (RODATA, 120 o)
```

**Coût CPU.** Une écriture de registre AY en assembleur droit :

```asm
        stx $C401     ; 4      ORA1 = numéro de registre
        lda #$07 : sta $C400   ; 2+4  LATCH
        lda #$04 : sta $C400   ; 2+4  INACTIVE
        lda val  : sta $C401   ; 4+4  ORA1 = valeur
        lda #$06 : sta $C400   ; 2+4  WRITE
        lda #$04 : sta $C400   ; 2+4  INACTIVE
```

≈ **40 cycles par registre** (43 avec le surcoût de boucle). Deux vérifications
externes : deater annote **56 cycles par registre** dans
`pt3_lib_irq_handler.s` — mais il écrit vers *les deux* AY ; le rapport est
cohérent. Et la ligne WRITE reste haute **6 cycles** ici, sous les 8 que deater
recommande après avoir constaté des glitches audibles à 12 (la fiche technique de
l'AY-3-891x plafonne WRITE à 10 µs, cf. §2.3).

| Scénario | Reg/tick | Cycles/tick | @50 Hz | % de 1 022 727 |
|---|---|---|---|---|
| Rafraîchissement complet des 14 registres | 14 | ~600 | 30 000 | **2,9 %** |
| `MB1`, tick « rien à faire » | 0 | ~40 | 2 000 | **0,2 %** |
| `MB1`, 2 notes (4 reg) | 4 | ~230 | 11 500 | **1,1 %** |
| `MB1`, moyenne réaliste + répartiteur ProDOS/`callirq` | ~1,5 | ~230 | 11 500 | **~1,1 %** |
| Idem **dupliqué sur AY2** (image centrée) | ~3 | ~340 | 17 000 | **~1,7 %** |

**Calibrage contre le seul chiffre publié.** Le PT3 de deater coûte **14,6 %**
(16,7-18,1 % sur du répertoire réel) pour **2 680 octets** de lecteur. Or ses
écritures de registres n'en représentent que ~3,8 % : les **~11 % restants sont
son moteur de patterns / samples / ornements / effets**. `MB1` n'a pas ce moteur
— d'où l'écart d'un facteur dix. **L'estimation de 1-2 % n'est donc pas
optimiste, elle est la conséquence arithmétique de ne pas embarquer de tracker.**

Le chiffre qui compte n'est pas la moyenne mais le **pire tick** : un accord
d'ouverture de 12 notes coûte ~500 cycles — invisible pour du texte, pas pour un
bruitage cycle-compté (§3.4).

**Taille estimée : 500-700 octets**, dont 120 de table de notes — à reprendre
telle quelle de `github.com/Michaelangel007/apple2_mockingboard`, qui publie une
table note → période AY avec l'erreur quantifiée. Le décodeur est un `switch` sur
les 4 bits hauts : table de sauts de 8 entrées (16 o) plus huit poignées de 15-40 o.

### 5.4 Détection et silence propre

```c
#define MUSIC_TITLE 0 ... MUSIC_DEATH 4
unsigned char music_detect(void);              /* slot 1-7, ou 0 */
void __fastcall__ music_play(unsigned char theme);
void music_stop(void); void music_pause(void); void music_resume(void);
```

Le silence propre est **garanti par construction** : `music_detect()` pose
`mb_slot = 0` et **toutes** les autres entrées commencent par
`lda mb_slot / beq rts`. Aucune écriture ne part vers `$C400` sans carte — ce qui
compte, car sans carte on écrit dans le bus flottant, et en slot 3 sur un //e
c'est le firmware 80 colonnes. Conséquence : le jeu reste identique sans carte,
`sfx.s` continue seul, **aucun `#ifdef` nulle part**.

### 5.5 Ordre d'implémentation

Détaillé, chiffré et ordonné par le risque en **§7.4**. Le principe : les quatre
premières étapes (mesure du lecteur AKY, détection, une note tenue, l'IRQ nue)
valent 2,5 jours et **lèvent tout le risque avant qu'on écrive une ligne de
lecteur**.

### 5.6 Vérifier dans POM2

**(a) Le panneau de diagnostic** (`Devices ▸ Sound ▸ Mockingboard`, ou
Ctrl+Shift+P — `DEV.md:5432-5433`) est écrit **exactement pour ce problème** —
*« Primary use case: figuring out why an IRQ-driven music driver is silent »*
(`src/MainWindow_AudioPanels.cpp:336-356`) — et donne la triche de dépannage :
registres AY **tous à 0** ⇒ le gestionnaire ne tourne pas (regarder IFR/IER +
`irqAsserted`) ; registres **qui bougent** ⇒ le driver tourne, chercher côté
`AudioDevice` ou mixeur R7 ; registres **chargés puis figés** ⇒ une seule IRQ est
arrivée, T1 n'est pas réarmé ou l'acquittement est cassé. Il affiche aussi
`VIA writes` / `AY writes` / `AY resets` et `AY cmd: LATCH/WRITE/INACT/READ`
(`:405-412`, via `src/Ay3_8910.h:69-73`), le compteur T1 et son latch,
ACR/PCR/IFR/IER et les 16 registres. **Un `LATCH` qui monte à ~50/s prouve que le
driver parle, avant même d'entendre quoi que ce soit.**

**(b) Trace hors ligne, reproductible.** POM2 embarque déjà les deux outils qu'il
faut, écrits pour les démos French Touch, tous deux `EXCLUDE_FROM_ALL`
(`tests/CMakeLists.txt:2910`) : `tests/dd2_ay_trace.cpp:16-45` boote une image
avec Mockingboard slot 4, **décode le bus AY** par `peekViaRegister` (sans effet
de bord) et sort histogrammes par registre, stats R13/R11, mixeur, amplitudes et
**la cadence de tick mesurée** ← *preuve directe que le T1 est bien programmé* ;
`tests/dd1_audio_ab.cpp:16-46` ajoute **un `.wav` 16 bits 44,1 kHz** et **un
`.csv` `cycle,chip,reg,val`** — on compare octet par octet ce que le lecteur a
*voulu* écrire et ce que la carte a *reçu*.

```bash
cd /Users/gistair/src/pom2 && cmake --build build --target dd1_audio_ab dd2_ay_trace
build/tests/dd2_ay_trace 30 ../pom2adventure/dist/SCOSWAMP.HDV
```

⚠️ Ils codent en dur un Disk II slot 6 et une image `.woz`/`.dsk` ; pour un HDV il
faut ~20 lignes d'adaptation (`ProDOSHardDiskCard` en slot 5).

**(c) L'API AI-control** (`--ai-control[=PORT]`, défaut **6503**, boucle locale,
`DEV.md:3416-3452`) **n'expose pas les registres AY** — `/mem` lit la RAM, pas
l'état des cartes. Elle sert à *conduire* (`/keyboard` pour atteindre un combat)
et à *observer les variables du lecteur* (`mb_slot`, curseur, compteur de ticks,
tous en RAM). **AI-control pour conduire, `dd1_audio_ab` pour écouter.**

Modèle existant pour l'étape 3 :
`tests/mockingboard_iie_irq_smoke_test.cpp:38-42` — gestionnaire minimal en
`$0300`, acquittement par `STA $7F → $C40D`, incrément en page zéro, `RTI`,
comptage des IRQ.

**Réserve à connaître** : French Touch rapporte que ses productions à IRQ
finement chronométrées *« seem not to work with MAME »* et ne marchent bien que
sous AppleWin ; deater rapporte l'inverse pour son lecteur (MAME sonne plus
clair). Autrement dit **le parc d'émulateurs est inégal sur ce terrain précis**,
et POM2 — MAME-verbatim sur l'AY, avec sa sync paresseuse maison sur les timers —
est un troisième point de mesure, pas une vérité. Une validation sur vrai
matériel resterait souhaitable, en gardant en tête l'AY-3-8913 des clones (§2.3).

## 6. Risques

### 6.1 IRQ sous ProDOS pendant les accès disque — **risque n° 1**

**Ce n'est pas seulement le pilote Disk II : c'est ProDOS lui-même, sur tout
périphérique.** Le source de ProDOS 8 2.0.3 encadre chaque descente vers un
pilote d'un `PHP / SEI … PLP`, et **il n'existe aucun `CLI` dans tout ProDOS 8** —
le drapeau I n'est restauré que par le `PLP` le plus externe : `POSNOPEN.S:373`
`FileIOZ PHP ;No interupts from here on out / SEI` couvre **toutes les E/S fichier**
(OPEN/READ/WRITE/CLOSE/FLUSH) ; `XDOSMLI.S:150` `DevMgr` couvre READ_BLOCK /
WRITE_BLOCK ; `ALLOC.S:272` la carte d'occupation ; `XRW2.S:77` le Disk II en plein
secteur.

J'avais d'abord cru que le fait que **SCOSWAMP ne soit jamais sur disquette**
sauvait la mise — `make release` ne produit que `.hdv` / `.2mg`
(`Makefile:193-207`), donc un périphérique bloc dont le pilote est une simple
boucle `LDA $C0x0 / STA (buf),y` (`pom2/src/ProDOSHardDiskCard.h:17-37`), sans
contrainte de temps. **C'est faux comme exemption** : `FileIOZ` masque les IRQ
quel que soit le périphérique. Ce qui reste vrai, c'est que **la fenêtre est bien
plus courte** — pas de latence rotationnelle (0-200 ms à 300 tr/min), pas de délai
de pas de 150 ms, pas de 64 tentatives. On perd quelques ticks, pas des dizaines.

Ce qui se passe pendant ce masquage, et c'est une bonne nouvelle : le **T1 en
mode continu continue de compter** avec I=1 et pose IFR6 (fiche Rockwell R6522) ;
**IFR6 est un verrou unique, pas un compteur**, donc N expirations masquées
s'effondrent en **une seule IRQ tardive**. La musique **cale et repart avec une
dérive de tempo — elle n'accélère pas** pour rattraper. Et pendant ce temps
**l'AY joue les registres laissés** : ce n'est pas un silence, c'est une **note
tenue**. C'est ça qui s'entend. Confirmation de terrain, comp.sys.apple2 (Kevin
Greene) : *« the only time the music would slow in ultima sometimes is during
disk access »*.

**Parade** : encadrer chaque E/S de `music_pause()` / `music_resume()`.
`music_pause` coupe le mixeur (R7 = `$3F`) et met les volumes à 0 — silence net et
instantané — puis désarme l'IER. Sites, tous identifiés : `hgr_rle_load` (via
`load_hgr_image_as`, `scoswamp.c:307`), `parse_text_file` (`:1024`),
`messages_load` (`:2106`), `save_game`/`load_game` (`:235,243`), `enter_asset_dir`
(`:279`). Le plus propre : envelopper au niveau C dans `load_scene` et
`load_hgr_image_as`, pas dans chaque `fopen`.

**Et c'est exactement la parade d'époque** : le lecteur livré sur la disquette de
*Music Construction Set* (1983) expose deux entrées et rien d'autre —
`PAUSE = SEI + couper les voix des deux AY + réinitialiser la carte`,
`CONTINUE = CLI` (`github.com/cybernesto/mcs-player`, `src/MCS-MB.S`). deater fait
de même (`sei` avant `read_file` dans `pt3_player.s`), et le `prorwts2` de qkumba
qu'utilise Total Replay en fait une option de compilation
(`no_interrupts = 0 ;set to 1 to disable interrupts across calls`).

**La sortie élégante** : si les cinq thèmes tiennent résidents (§5.2, 3,7 Ko), il
n'y a **plus aucune lecture disque de musique** — la parade se réduit à
`pause/resume` autour des lectures de scène. C'est aussi la solution de *Second
Reality* sur Apple II : tout précharger *« allowing the music to keep playing
while this is happening »*.

**Risque résiduel — résolu par la recherche, dans le mauvais sens** : la question
de l'état de la Language Card à l'entrée du gestionnaire (§3.2) a une réponse, et
elle est négative : `$BFEB` commute la **banque 1**, donc le segment `LC` de cc65
(banque 2) est inaccessible sous IRQ. Ce qui reste à mesurer expérimentalement
(étape 3 de §5.5) : si `LDA $C40D` fonctionne sous IRQ ProDOS — c'est-à-dire si
`$FFFE` pointant vers ProDOS plutôt que vers `$C3FA` évite le `STA $C007` de
§1.3. Sans importance si l'on suit la règle « acquitter par écriture seulement ».

### 6.2 Coût CPU pendant le décodage HGR

`hgr_loader.s` alterne `fread` de 1 Ko (IRQ coupées par ProDOS) et décodage RLE
direct en `$2000-$3FFF` (IRQ possibles). Le RLE n'a aucune contrainte de temps :
une IRQ de 500 cycles y est **invisible**, elle allonge le total de ~1 %.

**Piège spécifique** : `hgr_loader.s:151` fait `sta $C002` (RAMRDOFF), et
`memory_swap.s:35` de même. Si le lecteur touchait aux banques (option B de
§3.3), une IRQ tombant **entre** la commutation et la restauration lirait la
mauvaise banque. Avec l'option A, **le lecteur ne touche jamais
`$C002-$C005`** : le risque disparaît. Un argument de plus pour A.

### 6.3 RAM

~3,1 Ko sur 6 767 (§3.3), reste ~3,6 Ko. Trois rappels de `SCOSWAMP/DOCS/MEMOIRE.md` :

- **Le `.BIN` ne contient pas la BSS.** Un tampon de 2 Ko en `BSS` ne grossit pas
  le binaire mais pousse le tas de 2 Ko. Passer par `make check`
  (`SCOSWAMP.MORE/TOOLS/check-memory.sh`) après chaque ajout.
- **`ld65` peut manquer un débordement de BSS** : si `__ONCE_RUN__` dépasse déjà
  le plafond, la taille se calcule en négatif, déborde en non signé vers ~4 Go,
  et **le lien réussit sans avertissement** en écrasant ProDOS
  (`MEMOIRE.md:46-63`). Ne jamais conclure d'un lien réussi que le binaire tient.
- `LOWBSS` n'a que **83 octets** : l'état du lecteur (~60 o) y tiendrait juste,
  pas le tampon. `main()` doit l'effacer lui-même (`scoswamp.c:2065`) — donc
  tout nouvel objet y placé sera bien mis à zéro.

### 6.4 Le //c

Le jeu est jouable sur //c depuis POM2 `6d65741` (`TODO.md:526-528`), et le //c
**n'a pas de slot physique**.

| Posture | Conséquence |
|---|---|
| **Pas de musique sur //c** ✅ recommandé | `music_detect()` rend 0, jeu identique avec `sfx.s`. Coût : zéro. |
| Viser la **Mockingboard 4c** (ReactiveMicro, port d'extension //c) | Elle se présente en `$C400` ; le balayage la trouverait **sans une ligne de plus**. Mais **POM2 ne l'émule pas** (`SystemProfile.cpp:182,234`, `SlotConfigurationCoordinator.cpp:148-163`) → invérifiable sans vrai matériel. |
| Musique sur le haut-parleur du //c | Un autre moteur entier. Hors sujet. |

Le //c+ (4 MHz, `TODO.md:556-558`) : l'accélérateur ne change **rien** à la
Mockingboard (l'AY est cadencé par φ0 du slot). La musique Mockingboard est donc
*plus* portable que les bruitages actuels, dont toutes les hauteurs y montent.

### 6.5 Droits sur les musiques

SCOSWAMP est **GPL v3, hommage non commercial**, et son README dit : *« Si un
ayant droit souhaite qu'il disparaisse, il disparaîtra »* (`README.md:3-11`). La
GPL exige que **toute** l'œuvre distribuée soit redistribuable sous ses termes,
**y compris commercialement en aval**. Trois conséquences dures (détail §4.1) :

1. **Le tier gratuit de Suno est frontalement incompatible avec la GPL v3** :
   *« personal and non-commercial purposes »*, et Suno reste propriétaire.
   Aucun montage ne rattrape ça.
2. **Même en Pro/Premier, deux clauses interdisent précisément notre chaîne** :
   l'interdiction d'utiliser l'Output pour *« power, enable or train other …
   machine learning models »* (or Basic Pitch et MuScriptor en sont) et
   l'interdiction de contourner le filigrane (or une transcription vers des
   registres AY le détruit).
3. **Et même sans Suno, l'audio purement généré n'est probablement pas
   protégeable** (*US Copyright Office*, Partie 2, 29 janvier 2025) : on ne peut
   pas licencier ce qu'on ne détient pas.

À quoi s'ajoute le climat : Bandcamp (janvier 2026), Beatport, Traxsource, Tidal,
Deezer et Spotify ont tous restreint ou banni la musique entièrement générée par
IA, et l'ARIA l'a exclue des classements australiens (août 2026). **La scène
rétro et chiptune penchera du même côté** — ce qui compte pour un projet qui est
d'abord un hommage adressé à cette scène.

Trois façons d'être propre, par ordre de préférence :

1. **Composer les thèmes dans un tracker** (Arkos Tracker 3, MIT, Apple Silicon
   natif). Statut limpide, quelques kilo-octets, et c'est le flux de travail
   normal du chiptune depuis trente ans.
2. **Utiliser l'IA en amont, mais symbolique** : `text2midi` (MIT + poids
   Apache-2.0) ou Magenta (Apache-2.0), qui produisent du MIDI épars, puis
   **réécrire à la main** dans le tracker. La paternité humaine est restaurée sur
   l'artefact effectivement livré.
3. **Partir de chiptune CC0 existant** (OpenGameArt), converti en PT3/AKY.
   Compatible GPL v3 sans discussion possible.

Dans les trois cas, **ce qui est livré sur le disque est une partition, pas un
enregistrement** — et c'est précisément ce qui met le projet à l'abri.

## 7. Recommandation

### 7.1 Sur Suno : non — et il existe mieux pour le même besoin

**Ne pas construire la chaîne `Suno audio → transcription → AY`.** Quatre
raisons, dans l'ordre où elles mordent :

1. **Les CGU l'interdisent explicitement, deux fois.** Interdiction d'utiliser
   l'Output pour *« power, enable or train other artificial intelligence and
   machine learning models »* — c'est exactement ce que fait Basic Pitch ou
   MuScriptor. Et interdiction de contourner le filigrane — c'est exactement ce
   que fait une réduction en registres AY. Ce n'est pas une zone grise (§4.1).
2. **Le tier gratuit est incompatible avec la GPL v3** (*non-commercial*, et Suno
   reste propriétaire), sans rétroactivité si l'on s'abonne ensuite. Et
   l'*US Copyright Office* juge l'audio purement généré non protégeable : **on ne
   peut pas licencier ce qu'on ne détient pas** (§6.5).
3. **Ça ne produit pas de la musique, ça produit un squelette.** §4.3 : réduire
   un mix polyphonique à trois oscillateurs carrés est un travail d'arrangement,
   et **aucun outil de 2026 ne l'arrange** — il n'existe d'ailleurs *aucun* outil
   audio → AY, ni aucun précédent de « Suno → tracker » au monde. Demander
   « 3 voix carrées » à Suno ne sert à rien : **aucun paramètre n'expose la
   polyphonie** (§4.6).
4. **Ça coûte plus de RAM pour moins de qualité.** §4.5 : une transcription
   automatique est *dense* (~50 o/s contre ~20 o/s pour une écriture musicale),
   soit ~4,5 Ko pour le thème du Marais au lieu de ~1,1 Ko. Dans 6 767 octets,
   c'est disqualifiant.

**Ce qui reste légitime, et c'est mieux que la demande initiale** :

- **Suno comme oreille, pas comme source** : lui demander cinq ambiances, écouter,
  garder ce qui évoque le Marais, puis **réécrire la mélodie à la main** dans le
  tracker. Le livrable est une composition humaine ; Suno a servi de piano.
- **Ou, si l'on veut de l'IA dans la chaîne de production : lui demander du MIDI,
  pas de l'audio.** `text2midi` (code MIT, poids Apache-2.0) et Magenta
  (Apache-2.0) sont les **deux seuls générateurs de tout ce rapport dont le code,
  les poids et les sorties soient indiscutablement redistribuables**, et ils
  produisent du MIDI épars — la forme même dont une puce à 3 voix a besoin. Le
  MIDI entre ensuite directement dans Arkos Tracker 3. Qualité musicale en deçà
  de Suno, statut juridique sans ambiguïté, et **la chaîne fait la moitié du
  travail au lieu d'en créer**.

### 7.2 Sur le lecteur : mesurer AKY avant de décider

Deux voies restent ouvertes, et **une demi-journée de mesure les départage** :

| | **AKY (Arkos Tracker 3)** | **`MB1` maison** |
|---|---|---|
| Lecteur | officiel, **MIT**, Apple II + Mockingboard, écrit par GROUiK/French Touch | à écrire, 500-700 o |
| Taille lecteur | **inconnue** — c'est la mesure à faire | connue par construction |
| Chaîne de composition | **AT3 3.7 (08/2026), import MIDI, activement maintenu** | tracker + script maison |
| Format | AKY, **sans tampon**, structuré | flux d'événements, modèle Ultima IV |
| Travail | porter ACME → ca65, remplacer l'install de vecteur par `.interruptor` | tout écrire |
| Voix | 3 (un AY, compatibilité Oric) | 3, extensible |

**Prendre AKY si son lecteur assemblé tient sous ~2 Ko** : on hérite d'un
lecteur éprouvé, d'un éditeur maintenu et d'une licence MIT sans obligation
d'attribution gênante. **Sinon écrire `MB1`** : c'est 600 octets et deux jours,
et le modèle existe (le driver d'Ultima IV, entièrement désassemblé, §2.3).

### 7.3 Les décisions déjà tranchées

- **Logement : option A**, tout en fenêtre principale, **les cinq thèmes
  résidents** (~3,7 Ko en `MB1`). Cela supprime toute lecture disque de musique,
  donc l'essentiel du risque §6.1. La RAM auxiliaire (option B) est un chantier,
  pas une retouche — et le segment `LC` y est inutilisable (§3.2).
- **Acquitter par écriture** : `LDA #$7F / STA $C40D`, jamais par lecture (§1.3).
- **Balayer `$C7` → `$C1`** en sautant le slot 3 ; ne jamais coder `$C400` en dur
  (§1.4). POM2 met la carte en slot 2 par défaut.
- **`php/sei … plp` autour de chaque `_sfx_*`** (§3.4) ; `music_pause`/`resume`
  autour des lectures de scène (§6.1) — la parade de *Music Construction Set*,
  1983.
- **Dupliquer les écritures sur AY2** pour une image centrée (§5.1).
- **Pas de musique sur //c** : `music_detect()` rend 0, tout reste identique
  (§6.4).
- **Ajouter `MUSIC` à `PAYLOAD`** dans le Makefile (§5.2), sinon `make hdv`
  ignorera les modifications de musique.
- **La musique livrée est une partition composée, pas un enregistrement
  transcrit** — écrite dans Arkos Tracker 3 (MIT, Apple Silicon natif), avec
  Suno au mieux comme source d'inspiration écoutée puis mise de côté (§7.1).

### 7.4 Plan par étapes

| # | Étape | Livrable / critère de sortie | Jours |
|---|---|---|---|
| **0** | **Mesurer le lecteur AKY.** Récupérer `PlayerAKY_6502.a` sur Bitbucket, l'assembler, compter les octets, mesurer un tick | Un nombre. Décide §7.2 | **0,5** |
| **1** | `music_detect()` : balayage `$C7→$C1`, test T1 à −8. Affiché sur l'écran de langue | « Mockingboard : slot N » dans POM2 avec `slot_4_card=mockingboard` | **0,5** |
| **2** | Une note tenue (`music_test()`), sans IRQ | Le panneau POM2 montre R0/R1/R7/R8 posés, on entend un la | **0,5** |
| **3** | **`.interruptor` + T1 continu + un compteur**, sans musique | Le compteur monte à ~50/s, lu par `/mem` ; aucun `SYSTEM FAILURE` ; testé après une lecture de scène. **Étape la plus risquée** | **1** |
| **4** | Le lecteur (AKY porté, ou `MB1`) + un thème tapé à la main | `dd2_ay_trace` mesure la bonne cadence de tick ; le `.wav` de `dd1_audio_ab` est écoutable | **2** (AKY : 3) |
| **5** | `pause`/`resume` autour des E/S ; `sei` autour des `sfx` | Plus de note tenue pendant un chargement d'image ; les bruitages ne craquent plus | **0,5** |
| **6** | Branchements : `main`, `load_scene`, `run_combat`, `game_over`, `die_and_restart` ; `music_detect` en secours silencieux | Une partie complète avec musique, et une sans carte, identiques par ailleurs | **0,5** |
| **7** | `make check` + `MUSIC` dans `PAYLOAD` + mise à jour de `SCOSWAMP/DOCS/MEMOIRE.md` | Marge mesurée, image reconstruite | **0,5** |
| **8** | **Composition des cinq thèmes** dans le tracker | 5 fichiers, ≤ 3,7 Ko cumulés | **3 à 6** |
| | **Total technique (0-7)** | | **6 à 7 jours** |
| | **Total avec la musique** | | **9 à 13 jours** |

Les étapes 0 à 3 valent **2,5 jours** et lèvent tout le risque : si l'étape 3
échoue, on l'apprend avant d'avoir écrit une ligne de lecteur. **C'est le
découpage à respecter** — la plomberie ProDOS/cc65 sous IRQ n'a, à notre
connaissance, **aucun précédent public** (§2.3), et c'est là que le projet peut
se casser, pas dans la musique.
