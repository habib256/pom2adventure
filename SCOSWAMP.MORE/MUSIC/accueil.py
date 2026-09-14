#!/usr/bin/env python3
"""« Le Marais aux Scorpions » -- theme d'accueil, proposition n°2.

Trois voix, comme les trois canaux d'une AY-3-8910 : une melodie, un
accompagnement arpege facon luth, une basse galopante. Mode de re dorien,
125 a la noire (24 ticks de 50 Hz par temps : les croches et doubles tombent
juste), 28 mesures a 4/4 = 54 s, concu pour boucler. Aucune dependance.

    python3 accueil.py

ecrit, a cote du script :
- accueil.mid : trois pistes, programme 80 (square lead), pour Arkos Tracker ;
- accueil.wav : rendu a ondes carrees, 22 050 Hz mono, pour l'oreille.
Le flux MB1 joue par la Mockingboard en sort par midi_to_mb.py (Makefile).

Structure : fanfare (4 mesures, unisson sur re), A (16 mesures, l'appel du
village, Dm-C-Am-F), B (8 mesures, l'oree du Marais, G-Dm-Am) qui retombe
sur re. Le format MB1 est decrit dans SCOSWAMP/DOCS/MUSIQUE.md § 5.2 ; le sous-ensemble
emis ici : DELAY, NOTE, OFF, VOL, END avec boucle.
"""
import math
import struct
import wave
from pathlib import Path

BPM = 125
TICK_HZ = 50                     # cadence du T1 de la Mockingboard
TPB = 24                         # ticks par temps a 125 bpm (50 * 60 / 125)
TICKS = 480                      # ticks MIDI par noire
RATE = 22050                     # Hz du rendu WAV
AY_CLOCK = 1_022_727             # phi0 du slot, NTSC
BASE_NOTE = 36                   # index 0 de la table = C2 (MIDI 36)
VOLS = (13, 8, 10)               # melodie, accompagnement, basse (0-15)

NOTE_OF = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    letter, rest = name[0], name[1:]
    acc = 0
    if rest and rest[0] in "#b":
        acc = 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE_OF[letter] + acc


def bar(spec):
    out = []
    for tok in spec.split():
        n, d = tok.split(":")
        out.append((None if n == "-" else midi(n), float(d)))
    return out


# ── La melodie ────────────────────────────────────────────────────────────
MELODY = [
    # Fanfare : l'appel, a l'unisson de la basse
    "D5:.5 D5:.5 A5:1 D6:2",         "C6:.5 A5:.5 F5:1 D5:2",
    "D5:.5 D5:.5 A5:1 D6:1 E6:1",    "F6:1 E6:.5 D6:.5 C6:1 A5:1",
    # A : le village
    "D5:.75 E5:.25 F5:1 A5:2",       "G5:.5 F5:.5 E5:.5 D5:.5 E5:2",
    "E5:.75 F5:.25 G5:1 C6:2",       "B5:.5 A5:.5 G5:.5 E5:.5 G5:2",
    "D5:.5 A5:.5 D6:1 C6:.5 A5:.5 C6:1", "D6:1.5 C6:.5 A5:1 F5:1",
    "E5:.75 A5:.25 C6:1 B5:.5 A5:.5 B5:1", "A5:2 E5:1 -:1",
    "F5:.75 G5:.25 A5:1 C6:2",       "D6:.5 C6:.5 A5:.5 F5:.5 A5:2",
    "E5:.5 G5:.5 C6:1 D6:.5 C6:.5 D6:1", "E6:1.5 D6:.5 C6:2",
    "D6:.5 A5:.5 F5:.5 A5:.5 D6:1 F6:1", "E6:.5 C6:.5 B5:.5 A5:.5 B5:1 C6:1",
    "D6:1 A5:.5 F5:.5 E5:1 F5:1",    "D5:3 -:1",
    # B : l'oree du Marais
    "G5:.75 A5:.25 B5:1 D6:2",       "E6:.5 D6:.5 B5:.5 G5:.5 B5:2",
    "F5:.75 G5:.25 A5:1 D6:2",       "E6:.5 D6:.5 A5:.5 F5:.5 A5:2",
    "E5:.5 A5:.5 C6:.5 E6:.5 A6:2",  "G6:.5 E6:.5 D6:.5 C6:.5 B5:1 A5:1",
    "D6:.5 C6:.5 A5:.5 F5:.5 E5:.5 F5:.5 E5:.5 C5:.5", "D5:3 -:1",
]

DM, C, AM, F, G = "D4 F4 A4", "C4 E4 G4", "A3 C4 E4", "F4 A4 C5", "G4 B4 D5"
CHORDS = ([DM] * 4
          + [DM, DM, C, C, DM, DM, AM, AM, F, F, C, C, DM, AM, DM, DM]
          + [G, G, DM, DM, AM, AM, DM, DM])
BASS_OF = {DM: ("D3", "A2"), C: ("C3", "G2"), AM: ("A2", "E3"),
           F: ("F3", "C3"), G: ("G2", "D3")}
assert len(MELODY) == len(CHORDS) == 28


def voices():
    """Trois listes de (note MIDI ou None, debut en temps, duree en temps)."""
    mel, acc, bass = [], [], []
    t = 0.0
    for i, (m, c) in enumerate(zip(MELODY, CHORDS)):
        t0 = t
        for n, d in bar(m):
            mel.append((n, t, d)); t += d
        r, third, fifth = (midi(x) for x in c.split())
        if i < 4:   # fanfare : octaves martelees
            pattern = [r, r + 12, r, r + 12, r, r + 12, r + 7, r + 12]
        else:       # luth
            pattern = [r, fifth, third, fifth, r, fifth, third, r + 12]
        for k, n in enumerate(pattern):
            acc.append((n, t0 + k * 0.5, 0.3))
        lo, hi = (midi(x) for x in BASS_OF[c])
        gallop = [lo, lo, hi, lo, lo, lo, hi, hi]
        if i == 27: gallop = [lo] * 8          # retombee finale
        for k, n in enumerate(gallop):
            bass.append((n, t0 + k * 0.5, 0.42))
    return mel, acc, bass


# ── MIDI ──────────────────────────────────────────────────────────────────
def vlq(n):
    out = [n & 0x7F]; n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F)); n >>= 7
    return bytes(reversed(out))


def track(events, extra=b""):
    events.sort(key=lambda e: e[0])
    data = bytearray(extra); last = 0
    for tick, msg in events:
        data += vlq(tick - last) + msg; last = tick
    data += vlq(0) + b"\xFF\x2F\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + bytes(data)


def write_midi(path, parts):
    tempo = b"\x00\xFF\x51\x03" + struct.pack(">I", 60_000_000 // BPM)[1:]
    chunks = [track([], tempo + b"\x00\xFF\x58\x04\x04\x02\x18\x08")]
    for ch, (notes, vol) in enumerate(parts):
        ev = [(0, bytes([0xC0 | ch, 80]))]
        for n, t, d in notes:
            if n is None: continue
            a, b = int(t * TICKS), int((t + d) * TICKS)
            ev.append((a, bytes([0x90 | ch, n, vol])))
            ev.append((b, bytes([0x80 | ch, n, 0])))
        chunks.append(track(ev))
    Path(path).write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), TICKS)
                           + b"".join(chunks))


# ── MB1 : le flux du lecteur 6502 ─────────────────────────────────────────
def write_mb1(path, parts):
    """DELAY n ($01-$7F) / NOTE $80|v,idx / OFF $90|v / VOL $A0|v,vol / END $E0."""
    events = {}                                   # tick -> [(ordre, bytes)]
    for v, (notes, _) in enumerate(parts):
        for n, t, d in notes:
            if n is None: continue
            a, b = round(t * TPB), round((t + d) * TPB)
            events.setdefault(a, []).append((1, bytes([0x80 | v, n - BASE_NOTE])))
            events.setdefault(b, []).append((0, bytes([0x90 | v])))
    stream = bytearray()
    for v, vol in enumerate(VOLS):
        stream += bytes([0xA0 | v, vol])
    last = 0
    for tick in sorted(events):
        gap = tick - last
        while gap > 0:
            n = min(gap, 127); stream.append(n); gap -= n
        last = tick
        offs = [e for o, e in events[tick] if o == 0]
        ons = [e for o, e in events[tick] if o == 1]
        # une voix qui rejoue au meme tick n'a pas besoin de son OFF
        replay = {e[0] & 0x0F for e in ons}
        for e in offs:
            if (e[0] & 0x0F) not in replay: stream += e
        for e in ons: stream += e
    stream.append(0xE0)
    header = b"MB1\0" + bytes([TICK_HZ, 1]) + struct.pack("<H", 8)
    Path(path).write_bytes(header + bytes(stream))
    return len(header) + len(stream), last


def write_note_table(path):
    lines = ["; Genere par SCOSWAMP.MORE/MUSIC/accueil.py -- ne pas editer.",
             "; Periode AY (12 bits) par note, index 0 = C2 (MIDI 36) ... 59 = B6.",
             f"; f = {AY_CLOCK} / (16 * TP), soit TP = {AY_CLOCK / 16:.0f} / f.",
             "note_table:"]
    for i in range(60):
        f = 440.0 * 2 ** ((i + BASE_NOTE - 69) / 12.0)
        tp = round(AY_CLOCK / 16 / f)
        name = "C C# D D# E F F# G G# A A# B".split()[i % 12] + str(i // 12 + 2)
        lines.append(f"        .word {tp:5d}    ; {i:2d} {name:<3} {f:8.2f} Hz")
    Path(path).write_text("\n".join(lines) + "\n")


# ── Rendu a ondes carrees ─────────────────────────────────────────────────
def render_wav(path, parts, beats):
    beat = 60.0 / BPM
    total = int((beats * beat + 0.5) * RATE)
    mix = [0.0] * total
    for notes, vol in parts:
        g = vol / 127.0 * 0.45
        for n, t, d in notes:
            if n is None: continue
            f = 440.0 * 2 ** ((n - 69) / 12.0)
            s0, s1 = int(t * beat * RATE), int((t + d) * beat * RATE)
            length, half = s1 - s0, RATE / f / 2.0
            for i in range(length):
                x = i / RATE
                env = min(1.0, x / 0.005) * (0.6 + 0.4 * math.exp(-x * 12.0))
                rem = (length - i) / RATE
                if rem < 0.025: env *= rem / 0.025
                sq = 1.0 if int(i / half) % 2 == 0 else -1.0
                mix[s0 + i] += sq * env * g
    frames = bytearray()
    for v in mix:
        frames += struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32000))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(bytes(frames))


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    src = here.parent.parent / "SCOSWAMP" / "SRC"
    mel, acc, bass = voices()
    parts = [(mel, 100), (acc, 60), (bass, 85)]
    beats = 4 * len(MELODY)
    write_midi(here / "accueil.mid", parts)
    render_wav(here / "accueil.wav", parts, beats)
    print(f"accueil.mid et accueil.wav ecrits ; le flux MB1 sort de midi_to_mb.py ; "
          f"{len(mel)} + {len(acc)} + {len(bass)} notes a {BPM} bpm")
