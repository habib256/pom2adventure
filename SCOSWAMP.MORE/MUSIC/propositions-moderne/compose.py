#!/usr/bin/env python3
"""Atelier de composition pour la Mockingboard — style fantasy moderne.

Ce module ne joue rien et n'ecrit pas de flux MB1 : il ecrit un **MIDI** que
`../midi_to_mb.py` reduit ensuite a six voix carrees et rend en WAV stereo.
C'est une generalisation de `../accueil.py`, qui melait la composition, le MIDI,
le MB1 et le rendu dans un seul fichier pour trois voix.

    from compose import *
    p = Piece("D", "dorien", bpm=136, beats_per_bar=4)
    p.add("melodie", line("D5:1 F5:.5 G5:.5 A5:2"))
    ...
    p.add_drums("K..S..K.", "H.H.H.H.", length=LEN)     # facultatif
    p.write(Path(__file__).with_name("piece.mid"))

## Les voix et la stereo

Deux AY-3-8910 : voix 0-2 a **gauche**, voix 3-5 a **droite**. Le lecteur ne
choisit pas la voix — `midi_to_mb.reduce_voices()` le fait, et il le fait par
**hauteur** : a chaque frontiere, les notes qui commencent sont triees du grave
a l'aigu (la plus haute servie d'abord) et prennent les voix libres dans
l'ordre `0, 3, 1, 4, 2, 5`, c'est-a-dire en alternant les deux puces.

**Sans batterie — six parties de hauteur :**

    dessus -> 0 (G)   2e -> 3 (D)   3e -> 1 (G)   4e -> 4 (D)   5e -> 2 (G)   basse -> 5 (D)

**Avec batterie — la voix 5 est le bruit, il ne reste que CINQ parties :**

    dessus -> 0 (G)   2e -> 3 (D)   3e -> 1 (G)   4e -> 4 (D)   basse -> 2 (G)
    batterie -> 5 (D)

Une piece avec batterie qui garde six parties de hauteur **perd des notes** :
il faut en retirer une, en general le bourdon — la grosse caisse en tient lieu —
ou la voix d'accords tenus si le bourdon fait le caractere de la piece.
`Piece.write()` le verifie et le dit.

Composer pour cette machine, c'est donc **ecrire des registres distincts et les
garder distincts**. Si deux parties se croisent, elles echangent leurs cotes en
cours de route. `stats()` mesure ce qui se passe reellement ; `verifier.py` le
confirme apres conversion.

## La batterie

`midi_to_mb.py` transforme les notes du **canal MIDI 10** en paquets NOISE sur
la voix 5, a droite. Six instruments, notes General MIDI, ecrits ici par une
lettre :

    K grosse caisse (36)   S caisse claire (38)   H charleston ferme (42)
    O charleston ouvert (46)   T tom (45)   C cymbale (49)

Un coup coute **3 octets** (NOISE + OFF + le delai) : une double croche continue
de charleston sur 32 mesures, c'est 1 500 octets, plus que le tampon. On ecrit
donc des motifs, pas des grilles pleines.

La duree se compte en **ticks de 50 Hz**, pas en temps : un coup sec fait 1 a 3
ticks, une cymbale 6 ou 7. `Piece.add_drums()` fait la conversion depuis le
tempo de la piece.

## Le budget

Le moteur a deux tampons : **2 304 octets pour un theme de zone, 1 280 pour une
surcouche** (combat, mort, victoire). Une note coute environ 3 a 4 octets
(NOTE + OFF + les delais). Il faut donc rester sous ~600 notes pour une zone et
sous ~330 pour une surcouche : une seule voix en croches continues mange la
moitie du budget. D'ou l'ecriture du style : bourdons tenus, quintes ouvertes en
rondes, une seule voix rapide a la fois — et, pour les surcouches, une boucle
courte plutot qu'une texture amaigrie. Un coup de batterie coute 3 octets ;
compter les coups avec les notes.

## Ce qu'il faut eviter

- plus de six notes simultanees : la reduction abandonne l'interieur (`stats()`
  le signale) ;
- des hauteurs hors de C2..B6 (MIDI 36..95) : `fold()` les ramene a l'octave et
  la basse remonte au milieu de la texture ;
- deux notes de la meme voix qui se touchent : `Piece.write()` raccourcit tout
  d'un souffle (`GATE`) pour que l'onde carree articule.
"""
from pathlib import Path
import struct

TICKS = 480                       # ticks MIDI par noire
TICK_HZ = 50                      # l'horloge du lecteur Mockingboard
GATE = 0.06                       # souffle retire a chaque note, en temps
LO, HI = 36, 95                   # C2..B6, la table de `midi_to_mb.py`

NOTE_OF = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

MODES = {
    "ionien":     (0, 2, 4, 5, 7, 9, 11),
    "dorien":     (0, 2, 3, 5, 7, 9, 10),
    "phrygien":   (0, 1, 3, 5, 7, 8, 10),
    "lydien":     (0, 2, 4, 6, 7, 9, 11),
    "mixolydien": (0, 2, 4, 5, 7, 9, 10),
    "eolien":     (0, 2, 3, 5, 7, 8, 10),
    "mineur_h":   (0, 2, 3, 5, 7, 8, 11),   # mineur harmonique
}

QUALITIES = {
    "":     (0, 4, 7),         "m":    (0, 3, 7),
    "5":    (0, 7, 12),        "sus2": (0, 2, 7),      "sus4": (0, 5, 7),
    "dim":  (0, 3, 6),         "aug":  (0, 4, 8),
    "7":    (0, 4, 7, 10),     "m7":   (0, 3, 7, 10),  "maj7": (0, 4, 7, 11),
    "6":    (0, 4, 7, 9),      "m6":   (0, 3, 7, 9),
    "add9": (0, 4, 7, 14),     "madd9": (0, 3, 7, 14), "m9": (0, 3, 7, 10, 14),
    "7sus4": (0, 5, 7, 10),
}


# ── Hauteurs ──────────────────────────────────────────────────────────────
def midi(name):
    """\"D4\", \"F#3\", \"Bb5\" -> numero MIDI. C4 = 60."""
    letter, rest = name[0].upper(), name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE_OF[letter] + acc


def pc(name):
    """Classe de hauteur d'un nom sans octave : \"Bb\" -> 10."""
    acc = sum(1 if c == "#" else -1 for c in name[1:] if c in "#b")
    return (NOTE_OF[name[0].upper()] + acc) % 12


def degree(root, mode, d, octave=4):
    """Degre `d` (1 = tonique) du mode, dans l'octave donnee ; d peut deborder.

    degree("D", "dorien", 1, 5) == midi("D5") ; degree(..., 8, 5) est l'octave.
    """
    steps = MODES[mode]
    i, up = (d - 1) % 7, (d - 1) // 7
    return 12 * (octave + 1) + pc(root) + steps[i] + 12 * up


def chord(name, octave=3):
    """\"Dm\", \"Bb\", \"F#m\", \"A7sus4\", \"E5\" -> hauteurs MIDI, fondamentale
    dans l'octave donnee. Pas de chiffre d'octave dans le nom : \"E5\" est la
    quinte a vide sur mi, pas un accord de mi a l'octave 5."""
    i = 1
    while i < len(name) and name[i] in "#b":
        i += 1
    root, qual = name[:i], name[i:]
    if qual not in QUALITIES:
        raise ValueError(f"accord inconnu : {name!r} (qualite {qual!r})")
    r = 12 * (octave + 1) + pc(root)
    return [r + s for s in QUALITIES[qual]]


def fit(pitch, lo, hi):
    """Replie une hauteur par octaves dans la fenetre [lo, hi]."""
    while pitch < lo:
        pitch += 12
    while pitch > hi:
        pitch -= 12
    return pitch


def voicing(name, lo):
    """L'accord en position de fondamentale, la fondamentale posee dans [lo, lo+11].

    Rend `[fondamentale, tierce, quinte, ...]` en ordre croissant serre. C'est
    la cle de la stereo : chaque partie recoit **sa** fenetre de registre et n'en
    sort pas, donc l'ordre des six parties par hauteur ne change pas, donc
    `midi_to_mb.reduce_voices()` leur rend toujours la meme voix — le meme cote.
    """
    tones = chord(name, 3)
    root = fit(tones[0], lo, lo + 11)
    out = [root]
    for t in tones[1:]:
        n = root + (t - tones[0]) % 12
        while n <= out[-1]:
            n += 12
        out.append(n)
    return out


def pick(v, i):
    """`v[i]` avec debordement par octaves : -1 = le dernier son une octave plus bas."""
    return v[i % len(v)] + 12 * (i // len(v))


def guard(part, name="?"):
    """Verifie que tout tient dans C2..B6, sinon lever plutot que replier."""
    for n, t, d in part:
        if n is not None and not (LO <= n <= HI):
            raise ValueError(f"voix {name} : hauteur {n} hors de C2..B6 a t={t}")
    return part


# ── Ecriture en notation texte ────────────────────────────────────────────
def line(spec, t0=0.0, transpose=0):
    """\"D5:1 F5:.5 -:.5 A5:2\" -> [(hauteur, debut, duree)], silences ignores.

    Les durees sont en temps (1 = une noire). `-` est un silence : il avance le
    temps sans rien produire. C'est la notation de `../accueil.py`.
    """
    out, t = [], float(t0)
    for tok in spec.split():
        n, _, d = tok.partition(":")
        d = float(d)
        if n != "-":
            out.append((midi(n) + transpose, t, d))
        t += d
    return out


def lines(specs, t0=0.0, transpose=0, bar=4.0):
    """Une liste de mesures, chacune posee sur `bar` temps quoi qu'elle contienne."""
    out = []
    for i, s in enumerate(specs):
        out += line(s, t0 + i * bar, transpose)
    return out


def seq(items, t0=0.0):
    """[(hauteur|None, duree), ...] -> [(hauteur, debut, duree)]."""
    out, t = [], float(t0)
    for n, d in items:
        if n is not None:
            out.append((n, t, float(d)))
        t += float(d)
    return out


# ── La batterie (canal MIDI 10) ───────────────────────────────────────────
DRUM_NOTE = {"K": 36, "S": 38, "H": 42, "O": 46, "T": 45, "C": 49}
DRUM_TICKS = {"K": 3, "S": 2, "H": 1, "O": 4, "T": 2, "C": 7}
DRUM_NAME = {"K": "grosse caisse", "S": "caisse claire", "H": "charleston ferme",
             "O": "charleston ouvert", "T": "tom", "C": "cymbale"}


def drum_pattern(spec, tpb, t0=0.0, step=0.5, length=None):
    """Un motif de batterie en notation texte -> [(note MIDI, debut, duree)].

    `spec` : une lettre par pas de `step` temps, `.` ou `-` pour un silence.
    Les espaces et les `|` sont ignores, ce qui permet d'ecrire les temps :

        "K.H. S.H. K.H. S.H."       une mesure a 4/4 en croches
        "K..S..K." + step=0.5       le meme motif sans charleston

    `tpb` est le nombre de ticks de 50 Hz par temps (`Piece.tpb`) : la duree de
    chaque coup est fixee en **ticks** par `DRUM_TICKS`, pas en temps, pour que
    la frappe reste seche quel que soit le tempo. Le motif se repete jusqu'a
    `length` temps ; sans `length`, il est joue une fois.
    """
    cells = [c for c in spec if c not in " |"]
    if not cells:
        return []
    span = len(cells) * step
    if length is None:
        length = span
    out, base = [], 0.0
    while base < length - 1e-6:
        for k, c in enumerate(cells):
            t = base + k * step
            if c in ".-" or t >= length - 1e-6:
                continue
            if c not in DRUM_NOTE:
                raise ValueError(f"instrument inconnu : {c!r} "
                                 f"(attendus {''.join(sorted(DRUM_NOTE))})")
            out.append((DRUM_NOTE[c], t0 + t, DRUM_TICKS[c] / tpb))
        base += span
    return out


def drum_at(hits, tpb, t0=0.0):
    """La forme explicite : [(temps, instrument, ticks facultatifs), ...].

        drum_at([(0, "K"), (1.5, "S"), (3, "K", 5)], p.tpb)

    Utile pour une frappe isolee — une cymbale au debut d'une partie B, un roulement
    de tom avant la reprise — la ou un motif regulier serait faux.
    """
    out = []
    for h in hits:
        t, c = h[0], h[1]
        ticks = h[2] if len(h) > 2 else DRUM_TICKS[c]
        if c not in DRUM_NOTE:
            raise ValueError(f"instrument inconnu : {c!r}")
        out.append((DRUM_NOTE[c], t0 + float(t), ticks / tpb))
    return out


# ── Les figures du style ──────────────────────────────────────────────────
def ostinato(pitches, durs, t0, length, gap=0.0):
    """Un motif tourne en boucle du temps `t0` jusqu'a `t0 + length`.

    `pitches` est la cellule (hauteurs MIDI, `None` pour un trou), `durs` la
    duree de chaque note — un nombre unique s'applique a toutes. `gap` raccourcit
    chaque note sans decaler la grille (staccato).
    """
    if not isinstance(durs, (list, tuple)):
        durs = [durs] * len(pitches)
    out, t, i = [], float(t0), 0
    end = t0 + length
    while t < end - 1e-6:
        n, d = pitches[i % len(pitches)], durs[i % len(durs)]
        if n is not None:
            out.append((n, t, min(d - gap, end - t)))
        t += d
        i += 1
    return [(n, s, d) for n, s, d in out if d > 0.05]


def pedal(pitch, t0, length, retrig=None):
    """Un bourdon. Sans `retrig`, une seule note tenue — une note, trois octets.

    Avec `retrig`, la note est refrappee tous les `retrig` temps : le bourdon
    respire au lieu de se figer, au prix d'une note par frappe.
    """
    if retrig is None:
        return [(pitch, float(t0), float(length))]
    return ostinato([pitch], retrig, t0, length)


def spans(chords, t0, per_chord):
    """[(accord, debut, duree)] — `per_chord` est un nombre, ou une duree par accord.

    C'est ce qui permet de faire **varier le rythme harmonique** : deux mesures
    sur le meme accord, puis deux accords dans une mesure. Une harmonie qui
    change toujours au meme endroit s'entend comme une grille ; c'est le defaut
    le plus courant de la musique ecrite au clavier d'ordinateur.

        spans(["Dm", "C", "Am"], 0, [8, 2, 2])
    """
    if not isinstance(per_chord, (list, tuple)):
        per_chord = [per_chord] * len(chords)
    if len(per_chord) != len(chords):
        raise ValueError(f"{len(chords)} accords pour {len(per_chord)} durees")
    out, t = [], float(t0)
    for c, d in zip(chords, per_chord):
        out.append((c, t, float(d)))
        t += float(d)
    return out


def bed(chords, t0, per_chord, lo, which=1):
    """Le lit d'accords : **une** note tenue par accord — trois octets la mesure.

    `which` choisit le son (0 = fondamentale, 1 = tierce, 2 = quinte, -1 = la
    quinte une octave plus bas). Deux appels avec deux `lo` differents donnent
    les deux voix d'accords du plan a six voix, sans jamais se croiser.
    """
    return [(pick(voicing(c, lo), which), t, d)
            for c, t, d in spans(chords, t0, per_chord)]


def progression(chords, t0, per_chord, pattern, lo):
    """Marche harmonique : `pattern` est joue sur chaque accord de la suite.

    Chaque element de `pattern` est `(indice, duree)` ; l'indice designe un son
    de l'accord pose a partir de `lo` (0 = fondamentale), et deborde par octaves.
    `None` a la place de l'indice fait un silence. Le motif tourne en boucle
    jusqu'a remplir l'accord, quelle que soit sa duree, et la derniere note est
    rognee : un accord de six temps recoit une fois et demie un motif de quatre.
    """
    out = []
    for c, t0c, span in spans(chords, t0, per_chord):
        v = voicing(c, lo)
        t, i = t0c, 0
        while t < t0c + span - 1e-6:
            k, d = pattern[i % len(pattern)]
            d = min(d, t0c + span - t)
            if k is not None and d > 0.05:
                out.append((pick(v, k), t, d))
            t += d
            i += 1
    return out


def arpeggio(chords, t0, per_chord, step, shape, lo):
    """Arpege continu : `shape` parcourt l'accord pose a partir de `lo`."""
    out = []
    for c, t0c, span in spans(chords, t0, per_chord):
        v = voicing(c, lo)
        for k in range(int(round(span / step))):
            j = shape[k % len(shape)]
            if j is not None:
                out.append((pick(v, j), t0c + k * step, step))
    return out


def double(part, semitones=-12, keep=None):
    """Doublure : la meme partie transposee. `keep` filtre (ex. `lambda n,t,d: d>=1`)."""
    return [(n + semitones, t, d) for n, t, d in part
            if keep is None or keep(n, t, d)]


def hush(part, t0, t1):
    """Fait taire une partie entre `t0` et `t1` (en temps), en rognant ce qui deborde.

    Le seul silence qui ne deregle pas la stereo est celui que **toutes** les
    parties observent ensemble : elles liberent leurs voix au meme instant et les
    reprennent au meme instant, donc dans le meme ordre de hauteur. Passer par
    `Piece.hush()` plutot que par cette fonction garantit qu'on n'en oublie pas une.
    """
    out = []
    for n, t, d in part:
        if t0 - 1e-6 <= t < t1 - 1e-6:
            continue
        if t < t0 and t + d > t0:      # une note a cheval : on la rogne
            d = t0 - t
            if d <= 0.05:              # ... sauf si le reste n'est plus audible
                continue
        out.append((n, t, d))          # les coups de batterie durent 1 a 7 ticks :
    return out                         # jamais de plancher de duree sur eux


def shift(part, dt):
    return [(n, t + dt, d) for n, t, d in part]


def repeat(part, times, length):
    out = []
    for k in range(times):
        out += shift(part, k * length)
    return out


# ── La piece ──────────────────────────────────────────────────────────────
class Piece:
    """Les parties de hauteur, plus une batterie facultative, dans un MIDI.

    Six parties de hauteur si la piece n'a pas de batterie ; **cinq** si elle en
    a, la voix 5 etant alors le canal de bruit. `write()` refuse de mentir : il
    dit combien de parties passeront et combien seront ecrasees.
    """

    def __init__(self, root, mode, bpm, beats_per_bar=4, title=""):
        self.root, self.mode, self.bpm = root, mode, bpm
        self.bar = beats_per_bar
        self.title = title
        self.parts = []           # [(nom, [(hauteur, debut, duree)])]
        self.drums = []           # [(note de batterie, debut, duree)]

    @property
    def tpb(self):
        """Ticks de 50 Hz par temps — 20 a 150 bpm, 24 a 125, 16 a 187,5.

        Un tempo qui tombe entre deux ticks rend deux notes de meme valeur en
        longueurs differentes : on ecrit `BPM = 3000 / ticks`, avec un nombre
        de ticks qui rend entiere la plus petite subdivision de la piece."""
        return TICK_HZ * 60.0 / self.bpm

    @property
    def limit(self):
        """Parties de hauteur que la carte peut tenir : 5 avec batterie, 6 sans."""
        return 5 if self.drums else 6

    def deg(self, d, octave=4):
        return degree(self.root, self.mode, d, octave)

    def add(self, name, part):
        self.parts.append((name, guard(sorted(part, key=lambda e: e[1]), name)))
        return self

    def hush(self, t0, t1):
        """Le grand silence : toutes les parties et la batterie se taisent ensemble.

        C'est la seule rupture qui ne melange pas la stereo, et c'est la plus
        efficace de la boite a outils — deux temps de rien avant la reprise valent
        mieux qu'un crescendo.
        """
        self.parts = [(n, hush(part, t0, t1)) for n, part in self.parts]
        self.drums = hush(self.drums, t0, t1)
        return self

    def add_drums(self, *specs, step=0.5, t0=0.0, length=None):
        """Superpose des motifs de batterie, ou pose des coups explicites.

            p.add_drums("K..S..K.", "H.H.H.H.", length=LEN)
            p.add_drums([(0, "C", 7), (0, "K")], t0=BAR * 8)

        Chaque chaine est un motif (voir `drum_pattern`) repete jusqu'a `length`
        temps ; une liste de tuples est passee telle quelle a `drum_at`. Les
        appels s'accumulent : un motif de base sur toute la piece, puis les
        ponctuations mesure par mesure.
        """
        for spec in specs:
            if isinstance(spec, str):
                self.drums += drum_pattern(spec, self.tpb, t0, step, length)
            else:
                self.drums += drum_at(spec, self.tpb, t0)
        self.drums.sort(key=lambda e: e[1])
        return self

    @property
    def length(self):
        return max((t + d for _, p in self.parts for _, t, d in p), default=0.0)

    # -- diagnostic ------------------------------------------------------
    def holes(self):
        """Les temps forts ou une partie ne sonne pas — la faute qui melange la stereo.

        `reduce_voices()` remet tout d'aplomb chaque fois que les six parties
        attaquent ou tiennent ensemble : les notes tenues gardent leur voix, les
        notes neuves remplissent les voix libres de l'aigu au grave dans l'ordre
        `0, 3, 1, 4, 2, 5`. Si une partie se tait sur un temps fort, les cinq
        autres se decalent d'un cran et changent de cote. On ecrit donc des
        parties qui **sonnent sur chaque premier temps**, quitte a tenir.
        """
        bad = []
        for name, part in self.parts:
            miss = []
            b = 0.0
            while b < self.length - 1e-6:
                if not any(t <= b + 1e-6 < t + d for _, t, d in part):
                    miss.append(int(b // self.bar) + 1)
                b += self.bar
            if miss:
                bad.append((name, miss))
        return bad

    def stats(self):
        events = []
        for i, (_, p) in enumerate(self.parts):
            for n, t, d in p:
                events.append((t, 1, i, n)); events.append((t + d - 1e-9, -1, i, n))
        events.sort()
        limit = self.limit
        cur, peak, over, last = 0, 0, 0.0, None
        for t, k, _, _ in events:
            if last is not None and cur > limit:
                over += t - last
            cur += k; peak = max(peak, cur); last = t
        notes = sum(len(p) for _, p in self.parts)
        return {"notes": notes, "peak": peak, "over6_beats": round(over, 2),
                "drums": len(self.drums), "limit": self.limit,
                "parts": len(self.parts),
                "octets": 3 * (notes + len(self.drums)) + 40,
                "beats": round(self.length, 2),
                "seconds": round(self.length * 60.0 / self.bpm, 1),
                "ranges": [(n, min((x for x, _, _ in p), default=0),
                            max((x for x, _, _ in p), default=0))
                           for n, p in self.parts]}

    # -- MIDI ------------------------------------------------------------
    @staticmethod
    def _vlq(n):
        out = [n & 0x7F]; n >>= 7
        while n:
            out.append(0x80 | (n & 0x7F)); n >>= 7
        return bytes(reversed(out))

    @classmethod
    def _track(cls, events, extra=b""):
        events.sort(key=lambda e: (e[0], e[1]))
        data = bytearray(extra); last = 0
        for tick, _, msg in events:
            data += cls._vlq(tick - last) + msg; last = tick
        data += cls._vlq(0) + b"\xFF\x2F\x00"
        return b"MTrk" + struct.pack(">I", len(data)) + bytes(data)

    def write(self, path, gate=GATE):
        """Ecrit le MIDI : une piste par partie de hauteur, puis la batterie
        sur le **canal 10** (index 9), la seule que `midi_to_mb.py` transforme
        en bruit. Les coups de batterie ne sont pas raccourcis par `gate` : leur
        duree est deja calee en ticks de 50 Hz, et c'est elle qui fait la frappe."""
        tempo = b"\x00\xFF\x51\x03" + struct.pack(">I", int(60_000_000 / self.bpm))[1:]
        num = self.bar
        chunks = [self._track([], tempo + bytes([0, 0xFF, 0x58, 0x04, num, 2, 0x18, 8]))]
        chans = [c for c in range(16) if c != 9][:len(self.parts)]
        for ch, (_, part) in zip(chans, self.parts):
            ev = [(0, 0, bytes([0xC0 | ch, 80]))]
            for n, t, d in part:
                d = max(d - gate, min(d * 0.6, 0.12))
                a, b = int(round(t * TICKS)), int(round((t + d) * TICKS))
                if b <= a:
                    b = a + 1
                ev.append((a, 1, bytes([0x90 | ch, n, 100])))
                ev.append((b, 0, bytes([0x80 | ch, n, 0])))
            chunks.append(self._track(ev))
        if self.drums:
            ev = []
            for n, t, d in self.drums:
                a, b = int(round(t * TICKS)), int(round((t + d) * TICKS))
                if b <= a:
                    b = a + 1
                ev.append((a, 1, bytes([0x99, n, 100])))
                ev.append((b, 0, bytes([0x89, n, 0])))
            chunks.append(self._track(ev))
        Path(path).write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), TICKS)
                               + b"".join(chunks))
        s = self.stats()
        kit = "".join(sorted({c for c, n in DRUM_NOTE.items()
                              if any(x == n for x, _, _ in self.drums)}))
        print(f"{Path(path).name}: {s['notes']} notes"
              + (f" + {s['drums']} coups [{kit}]" if self.drums else "")
              + f", {s['beats']:g} temps = {s['seconds']}s a {self.bpm:g} bpm, "
              f"{s['parts']} parties, polyphonie max {s['peak']}/{s['limit']}"
              f", ~{s['octets']} octets")
        if s["parts"] > s["limit"]:
            print(f"   !! {s['parts']} parties de hauteur pour {s['limit']} voix : "
                  f"la batterie prend la voix 5, retirer une partie "
                  f"(le bourdon, en general) sinon des notes seront abandonnees")
        if s["peak"] > s["limit"]:
            print(f"   !! {s['over6_beats']} temps au-dessus de {s['limit']} voix")
        for name, miss in self.holes():
            print(f"   !! {name} se tait au temps fort des mesures "
                  f"{', '.join(map(str, miss[:12]))}"
                  + (" ..." if len(miss) > 12 else ""))
        return s


__all__ = [n for n in dir() if not n.startswith("_")]
