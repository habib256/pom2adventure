#!/usr/bin/env python3
"""MIDI -> MB1, le flux que SCOSWAMP/SRC/music.s joue sur la Mockingboard.

    python3 midi_to_mb.py entree.mid sortie.mb [--bpm 100] [--wav apercu.wav]
                          [--voices 6] [--vol 13,11,11,12,11,11] [--tail 24]
                          [--notes-inc chemin]

Une Mockingboard A ou C a deux AY-3-8910, six voix carrees : la partition,
quelle que soit sa polyphonie, est REDUITE a six lignes au plus (--voices).
L'attribution est STABLE : une note qui continue garde sa voix, une note
neuve prend une voix libre, les voix libres etant servies en alternant les
deux puces (0, 3, 1, 4, 2, 5) pour que chaque cote de la stereo ait du grave
et de l'aigu ; s'il n'y a plus de voix libre, la note la plus interieure est
abandonnee. Une note qui se repete sur la meme hauteur est detachee par un
tick de silence, sinon l'onde carree ne la fait pas entendre. Les hauteurs
hors de la table (C2..B6) sont ramenees a l'octave. L'apercu WAV est stereo,
puce 1 a gauche, puce 2 a droite, comme POM2.

Le tempo du fichier MIDI est ignore : --bpm fixe la vitesse, en noires par
minute, sur le tick de 50 Hz de la carte. Les valeurs qui donnent un nombre
entier de ticks par noire tombent juste : 100 (30), 120 (25), 125 (24),
150 (20). --tail ajoute un silence avant la boucle.

Format MB1 (SCOSWAMP/DOCS/MUSIQUE.md § 5.2), sous-ensemble emis :
  en-tete  'M','B','1',0, 50, drapeaux (bit0 = boucle), offset de boucle (16 bits)
  $01-$7F  DELAY n ticks     $80|v, note  NOTE     $90|v  OFF
  $A0|v, vol  VOL            $E0  END        $F0  FADE (fondu sortant de 45 ticks)
  $B0|v, periode  NOISE      la voix v bat le canal de bruit de sa puce (ton coupe)

Percussions : les notes du canal MIDI 10 deviennent des NOISE sur la voix
--drum-voice (5 par defaut, a droite), avec la periode de bruit tiree de la
note (grosse caisse 35/36 -> 24, caisse claire 38/40 -> 10, charleston 42/44
-> 2, ouvert 46 -> 4, toms 41-50 -> 14, cymbales 49/51/57 -> 6) et la duree de
la note MIDI ; les hauteurs sont alors reduites sur les cinq autres voix.
"""
import argparse
import math
import struct
import wave
from pathlib import Path

TICK_HZ = 50
RATE = 22050
AY_CLOCK = 1_022_727
BASE_NOTE = 36                    # index 0 de la table = C2
TABLE_SIZE = 60


# ── Lecture MIDI ──────────────────────────────────────────────────────────
def read_midi(path):
    """Rend (division, [(debut, fin, hauteur)]) en ticks MIDI, toutes pistes."""
    data = Path(path).read_bytes()
    assert data[:4] == b"MThd", "pas un fichier MIDI"
    _, ntracks, division = struct.unpack(">HHH", data[8:14])
    assert not division & 0x8000, "division SMPTE non geree"
    pos = 14
    notes = []                       # (debut, fin, hauteur, batterie)

    def vlq(p):
        v = 0
        while True:
            b = data[p]; p += 1
            v = (v << 7) | (b & 0x7F)
            if not b & 0x80:
                return v, p

    for _ in range(ntracks):
        assert data[pos:pos+4] == b"MTrk"
        length = struct.unpack(">I", data[pos+4:pos+8])[0]
        p, end = pos + 8, pos + 8 + length
        pos = end
        time, status = 0, 0
        active = {}
        while p < end:
            delta, p = vlq(p); time += delta
            b = data[p]
            if b == 0xFF:
                l, p2 = vlq(p + 2); p = p2 + l; continue
            if b in (0xF0, 0xF7):
                l, p2 = vlq(p + 1); p = p2 + l; continue
            if b & 0x80:
                status = b; p += 1
            hi = status & 0xF0
            drum = (status & 0x0F) == 9
            if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                d1, d2 = data[p], data[p+1]; p += 2
                key = (d1, drum)
                if hi == 0x90 and d2 > 0:
                    if key in active:
                        notes.append((active.pop(key), time, d1, drum))
                    active[key] = time
                elif hi == 0x80 or (hi == 0x90 and d2 == 0):
                    if key in active:
                        notes.append((active.pop(key), time, d1, drum))
            else:
                p += 1
        for (pitch, drum), start in active.items():
            notes.append((start, time, pitch, drum))
    notes = [n for n in notes if n[1] > n[0]]
    notes.sort()
    return division, notes


# ── Reduction a trois voix ────────────────────────────────────────────────
def to_ticks(notes, division, bpm):
    tpb = TICK_HZ * 60.0 / bpm            # ticks de 50 Hz par noire
    out = []
    for s, e, n, *rest in notes:
        a, b = round(s / division * tpb), round(e / division * tpb)
        if b <= a: b = a + 1
        out.append((a, b, n, *rest))
    return out


DRUM_PERIOD = {35: 24, 36: 24, 38: 10, 40: 10, 37: 8, 39: 8, 42: 2, 44: 2, 46: 4,
               41: 14, 43: 14, 45: 14, 47: 12, 48: 12, 50: 12, 49: 6, 51: 6, 57: 6}


def drum_hits(notes):
    """(debut, fin, periode de bruit) pour chaque note du canal 10."""
    return [(s, e, DRUM_PERIOD.get(n, 8)) for s, e, n, drum in notes if drum]


def fold(pitch):
    """Ramene la hauteur dans la table C2..B6 par octaves."""
    i = pitch - BASE_NOTE
    while i < 0: i += 12
    while i >= TABLE_SIZE: i -= 12
    return i


FILL_ORDER = [0, 3, 1, 4, 2, 5]          # puce 1, puce 2, puce 1, ...


def reduce_voices(notes, nvoices):
    """Rend nvoices listes de (debut, fin, index de table), attribution stable.

    A chaque frontiere (debut ou fin d'une note) : les notes qui continuent
    gardent leur voix ; les notes qui commencent prennent les voix libres, la
    plus haute d'abord, dans l'ordre FILL_ORDER ; faute de voix, on garde les
    extremes (la plus haute et la plus basse) et on abandonne l'interieur.
    """
    order = [v for v in FILL_ORDER if v < nvoices] + [v for v in range(nvoices) if v not in FILL_ORDER]
    bounds = sorted({t for s, e, _ in notes for t in (s, e)})
    voices = [[] for _ in range(nvoices)]
    current = [None] * nvoices
    for t in bounds:
        sounding = [n for n in notes if n[0] <= t < n[1]]
        keep = [n for n in current if n is not None and n in sounding]
        new = [n for n in sounding if n not in keep]
        # trop de notes : garder les extremes, lacher l'interieur des nouvelles
        while len(keep) + len(new) > nvoices and new:
            allp = sorted(keep + new, key=lambda n: n[2])
            inner = [n for n in new if n is not allp[0] and n is not allp[-1]]
            if not inner: break
            mid = (allp[0][2] + allp[-1][2]) / 2.0
            new.remove(min(inner, key=lambda n: abs(n[2] - mid)))
        new.sort(key=lambda n: -n[2])
        chosen = [n if n in keep else None for n in current]
        free = [v for v in order if chosen[v] is None]
        for n in new:
            if not free: break
            chosen[free.pop(0)] = n
        for v in range(nvoices):
            if chosen[v] is not current[v]:
                if current[v] is not None:
                    voices[v][-1] = (voices[v][-1][0], t, voices[v][-1][2])
                if chosen[v] is not None:
                    voices[v].append((t, None, fold(chosen[v][2])))
                current[v] = chosen[v]
    return voices


# ── Ecriture MB1 ──────────────────────────────────────────────────────────
def write_mb1(path, voices, vols, tail, loop=True, fade=30, drums=(), drum_voice=5):
    """`fade` : le FADE part autant de ticks avant la derniere fin de note ;
    avec la queue, le fondu de 45 ticks (0,9 s) couvre la fin du morceau.
    `drums` : (debut, fin, periode) -> NOISE puis OFF sur drum_voice."""
    events = {}
    end_tick = 0
    for s, e, per in drums:
        end_tick = max(end_tick, e)
        events.setdefault(s, []).append((1, bytes([0xB0 | drum_voice, per])))
        events.setdefault(e, []).append((0, bytes([0x90 | drum_voice])))
    for v, seq in enumerate(voices):
        prev_end, prev_idx = -1, None
        for s, e, idx in seq:
            assert e is not None, "note ouverte"
            end_tick = max(end_tick, e)
            # meme hauteur enchainee : un tick de silence pour l'articuler
            if s == prev_end and idx == prev_idx:
                events.setdefault(s, []).append((0, bytes([0x90 | v])))
                s += 1
                if s >= e: continue
            events.setdefault(s, []).append((1, bytes([0x80 | v, idx])))
            events.setdefault(e, []).append((0, bytes([0x90 | v])))
            prev_end, prev_idx = e, idx
    if fade:
        events.setdefault(max(0, end_tick - fade), []).append((0, bytes([0xF0])))
    stream = bytearray()
    for v, vol in enumerate(vols):
        stream += bytes([0xA0 | v, vol])
    last = 0
    for tick in sorted(events):
        gap = tick - last
        while gap > 0:
            n = min(gap, 127); stream.append(n); gap -= n
        last = tick
        offs = [e for o, e in events[tick] if o == 0]
        ons = [e for o, e in events[tick] if o == 1]
        replay = {e[0] & 0x0F for e in ons}
        for e in offs:
            if (e[0] & 0x0F) not in replay: stream += e
        for e in ons: stream += e
    gap = tail
    while gap > 0:
        n = min(gap, 127); stream.append(n); gap -= n
    stream.append(0xE0)
    header = b"MB1\0" + bytes([TICK_HZ, 1 if loop else 0]) + struct.pack("<H", 8)
    Path(path).write_bytes(header + bytes(stream))
    return len(header) + len(stream), end_tick + tail


# ── Table de notes pour music.s ───────────────────────────────────────────
def write_note_table(path):
    lines = ["; Genere par SCOSWAMP.MORE/MUSIC/midi_to_mb.py -- ne pas editer.",
             "; Periode AY (12 bits) par note, index 0 = C2 (MIDI 36) ... 59 = B6.",
             f"; f = {AY_CLOCK} / (16 * TP), soit TP = {AY_CLOCK / 16:.0f} / f.",
             "note_table:"]
    names = "C C# D D# E F F# G G# A A# B".split()
    for i in range(TABLE_SIZE):
        f = 440.0 * 2 ** ((i + BASE_NOTE - 69) / 12.0)
        lines.append(f"        .word {round(AY_CLOCK / 16 / f):5d}    ; {i:2d} "
                     f"{names[i % 12] + str(i // 12 + 2):<3} {f:8.2f} Hz")
    Path(path).write_text("\n".join(lines) + "\n")


# ── Apercu a ondes carrees, depuis la reduction elle-meme ─────────────────
def render_wav(path, voices, vols, total_ticks, fade_start=None, drums=(), drum_voice=5):
    """Stereo : voix 0-2 a gauche, 3-5 a droite, avec un tiers de fuite. Le
    bruit de l'AY : un tirage aleatoire tenu 16 * periode cycles."""
    import random
    total = int((total_ticks / TICK_HZ + 0.3) * RATE)
    left, right = [0.0] * total, [0.0] * total
    rnd = random.Random(1)
    g = vols[drum_voice] / 15.0 * 0.22
    side = left if drum_voice < 3 else right
    other = right if drum_voice < 3 else left
    for s, e, per in drums:
        s0, s1 = int(s / TICK_HZ * RATE), int(e / TICK_HZ * RATE)
        hold = max(1, int(RATE * 16 * per / AY_CLOCK))
        v = 0.0
        for i in range(s1 - s0):
            if i % hold == 0: v = rnd.choice((-1.0, 1.0))
            rem = (s1 - s0 - i) / RATE
            env = 1.0 if rem > 0.02 else rem / 0.02
            tsec = (s0 + i) / RATE
            if fade_start is not None and tsec > fade_start:
                env *= max(0.0, 1.0 - (tsec - fade_start) / 0.9)
            x = v * env * g
            if s0 + i < total: side[s0 + i] += x; other[s0 + i] += x / 3.0
    for v, seq in enumerate(voices):
        g = vols[v] / 15.0 * 0.22
        side = left if v < 3 else right
        other = right if v < 3 else left
        for s, e, idx in seq:
            f = AY_CLOCK / 16.0 / round(AY_CLOCK / 16 / (440.0 * 2 ** ((idx + BASE_NOTE - 69) / 12.0)))
            s0, s1 = int(s / TICK_HZ * RATE), int(e / TICK_HZ * RATE)
            half = RATE / f / 2.0
            for i in range(s1 - s0):
                rem = (s1 - s0 - i) / RATE
                env = 1.0 if rem > 0.02 else rem / 0.02
                # le fondu de fin : de fade_start a fade_start + 45 ticks
                tsec = (s0 + i) / RATE
                if fade_start is not None and tsec > fade_start:
                    env *= max(0.0, 1.0 - (tsec - fade_start) / 0.9)
                x = (1.0 if int(i / half) % 2 == 0 else -1.0) * env * g
                side[s0 + i] += x
                other[s0 + i] += x / 3.0
    frames = bytearray()
    for l, r in zip(left, right):
        frames += struct.pack("<hh", int(max(-1.0, min(1.0, l)) * 32000),
                              int(max(-1.0, min(1.0, r)) * 32000))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(bytes(frames))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("midi"); ap.add_argument("out")
    ap.add_argument("--bpm", type=float, default=100.0)
    ap.add_argument("--voices", type=int, default=6, choices=range(1, 7))
    ap.add_argument("--drum-voice", type=int, default=5, help="voix des percussions du canal 10")
    ap.add_argument("--vol", default="10,8,8,9,8,8",
                    help="volumes 0-15 par voix, dans l'ordre 0..5")
    ap.add_argument("--tail", type=int, default=15)
    ap.add_argument("--fade", type=int, default=30, help="ticks avant la fin ou le fondu sortant part (0 = aucun)")
    ap.add_argument("--wav"); ap.add_argument("--notes-inc")
    ap.add_argument("--no-loop", action="store_true", help="joue une fois puis s'arrete (mort, victoire)")
    ap.add_argument("--max", type=int, default=1280, help="taille maximale du .MB (un demi-tampon)")
    a = ap.parse_args()
    vols = [int(x) for x in a.vol.split(",")][:a.voices]
    vols += [11] * (a.voices - len(vols))
    division, notes = read_midi(a.midi)
    ticked = to_ticks(notes, division, a.bpm)
    drums = drum_hits(ticked)
    pitched = [(s, e, n) for s, e, n, drum in ticked if not drum]
    nv = a.voices - (1 if drums else 0)
    voices = reduce_voices(pitched, nv)
    if drums:
        voices = voices[:a.drum_voice] + [[]] + voices[a.drum_voice:]   # la voix des percussions reste vide de tons
        voices = voices[:6]
    size, total = write_mb1(a.out, voices, vols, a.tail, loop=not a.no_loop, fade=a.fade,
                            drums=drums, drum_voice=a.drum_voice)
    if size > a.max:
        raise SystemExit(f"{a.out}: {size} octets, plus que le demi-tampon de {a.max} -- "
                         f"raccourcir la piece ou baisser --voices")
    if a.notes_inc: write_note_table(a.notes_inc)
    if a.wav:
        end = max([e for seq in voices for _, e, _ in seq] + [e for _, e, _ in drums], default=0)
        render_wav(a.wav, voices, vols, total, (max(0, end - a.fade)) / TICK_HZ if a.fade else None,
                   drums=drums, drum_voice=a.drum_voice)
    dropped = len(pitched) - sum(len(v) for v in voices)
    print(f"{Path(a.midi).name}: {len(notes)} notes -> "
          f"{[len(v) for v in voices]} par voix ({max(dropped, 0)} abandonnees), "
          f"{len(drums)} coups de batterie, {size} octets, "
          f"{total / TICK_HZ:.1f} s a {a.bpm:g} bpm -> {a.out}")


if __name__ == "__main__":
    main()
