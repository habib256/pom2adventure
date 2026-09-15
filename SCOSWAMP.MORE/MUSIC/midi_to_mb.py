#!/usr/bin/env python3
"""MIDI -> MB1, le flux que SCOSWAMP/SRC/music.s joue sur la Mockingboard.

    python3 midi_to_mb.py entree.mid sortie.mb [--bpm 100] [--wav apercu.wav]
                          [--voices 6] [--vol 10,8,8,9,8,8] [--tail 15]
                          [--notes-inc chemin]

Une Mockingboard A ou C a deux AY-3-8910, six voix carrees : la partition,
quelle que soit sa polyphonie, est REDUITE a six lignes au plus (--voices).
L'attribution est STABLE : une note qui continue garde sa voix, une note
neuve prend une voix libre, les voix libres etant servies en alternant les
deux puces (0, 3, 1, 4, 2, 5) pour que chaque cote de la stereo ait du grave
et de l'aigu ; s'il n'y a plus de voix libre, la note la plus interieure est
abandonnee. Une note qui se repete sur la meme hauteur est detachee par un
tick de silence, sinon l'onde carree ne la fait pas entendre. Les hauteurs
hors de la table (C2..B6) sont ramenees a l'octave.

L'apercu WAV (--wav) rejoue le flux ECRIT comme music.s le joue : volumes de
depart a 12, fondu d'entree de 45 ticks, attenuation retranchee de chaque
amplitude, OFF qui coupe net, bruit de la voix 5 sur R6 de sa puce, fondu
sortant au FADE. Il synthetise ensuite les deux AY : table de volume
logarithmique mesuree (celle de POM2), ondes carrees a la periode de la table
sur l'horloge de 1 MHz, LFSR de 17 bits pour le bruit, puce 1 a gauche et puce 2
a droite sans fuite, passe-haut de 20 Hz. Le flux .MB ne depend pas de l'apercu.
Attention : 10 contre 8 sur l'AY, c'est +7 dB, pas +2.

Le tempo du fichier MIDI est ignore : --bpm fixe la vitesse, en noires par
minute, sur le tick de 50 Hz de la carte. Les valeurs qui donnent un nombre
entier de ticks par noire tombent juste : 100 (30), 120 (25), 125 (24),
136.364 (22), 150 (20), 166.667 (18), 187.5 (16). Il faut encore que la plus
petite subdivision de la piece tombe sur un tick entier : 20 ou 24 pour des
doubles croches, un nombre pair pour des croches. --tail ajoute un silence
avant la boucle.

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


# ── Apercu : le flux ecrit, rejoue comme music.s le joue ──────────────────
# Niveaux de sortie mesures de l'AY-3-8910 (Westcott 2001, le jeu de donnees
# de MAME), ramenes a 0..1 : la table de POM2, src/AyPsgSynth.h, kVolumeTable.
# Le volume 4 bits est LOGARITHMIQUE : 10 contre 8, c'est +7 dB, pas +2.
AY_VOLUME = (0.0000, 0.0105, 0.0154, 0.0223, 0.0321, 0.0468, 0.0635, 0.1061,
             0.1319, 0.2164, 0.2974, 0.3909, 0.5128, 0.6371, 0.8186, 1.0000)
PLAY_VOL = 12                     # music.s, music_play : vols[] au lancement
FADE_STEP = 3                     # music.s : ticks entre deux pas de fondu
HIGHPASS_HZ = 20.0                # POM2 et MAME : passe-haut de sortie, par cote
WAV_GAIN = 2.0                    # une puce a trois voix a 15 = pleine echelle


def play_stream(stream):
    """Rejoue music.s sur un flux MB1 et rend l'etat des deux AY a chaque tick :
    [(periodes[6], amplitudes[6], R7 des deux puces, R6 des deux puces)].

    Tout vient du lecteur 6502, dans son ordre : music_play met vols[] a 12 et
    arme le fondu d'entree (atten 15, un pas tous les 3 ticks) ; chaque IRQ fait
    d'abord le pas de fondu, qui reecrit les six amplitudes, puis decode jusqu'au
    DELAY suivant. NOTE ecrit la periode, ouvre le ton, coupe le bruit, et pose
    vols[v] ; VOL pose aussi l'amplitude, tout de suite ; OFF l'annule d'un coup ;
    NOISE ecrit R6 de la puce, coupe le ton, ouvre le bruit. Toute amplitude
    ecrite est diminuee de atten. L'apercu joue le flux une fois : END l'arrete.
    Les registres partent de zero, comme apres le /RESET de music_detect.
    """
    table = [round(AY_CLOCK / 16 / (440.0 * 2 ** ((i + BASE_NOTE - 69) / 12.0)))
             for i in range(TABLE_SIZE)]
    period, reg_amp = [0] * 6, [0] * 6
    mix, noise = [0x38, 0x38], [0, 0]
    vols, amps = [PLAY_VOL] * 6, [0] * 6
    atten, fade, fstep = 15, 2, 1          # fade_in_setup
    cur, delay = 8, 1
    ticks = []

    def amp(v, a):
        amps[v] = a
        reg_amp[v] = max(0, a - atten)

    while cur < len(stream):
        if fade:                           # fade_tick
            fstep -= 1
            if fstep == 0:
                fstep = FADE_STEP
                if fade == 1 and atten < 15:
                    atten += 1
                elif fade == 2 and atten > 0:
                    atten -= 1
                else:
                    fade = 0
                if fade:                   # apply_amps
                    for v in range(6):
                        reg_amp[v] = max(0, amps[v] - atten)
        delay = (delay - 1) & 0xFF
        if delay == 0:
            while True:
                op = stream[cur]; cur += 1
                if op < 0x80:              # DELAY n
                    delay = op
                    break
                v, kind = op & 0x0F, op & 0xF0
                chip, bit = v // 3, v % 3
                if op == 0xE0:             # END
                    return ticks
                if op == 0xF0:             # FADE
                    fade, fstep = 1, 1
                elif kind == 0x80:         # NOTE : ton ouvert, bruit coupe
                    period[v] = table[stream[cur]]; cur += 1
                    mix[chip] = (mix[chip] & ~(1 << bit)) | (8 << bit)
                    amp(v, vols[v])
                elif kind == 0x90:         # OFF
                    amp(v, 0)
                elif kind == 0xA0:         # VOL
                    vols[v] = stream[cur]; cur += 1
                    amp(v, vols[v])
                elif kind == 0xB0:         # NOISE : ton coupe, bruit ouvert
                    noise[chip] = stream[cur]; cur += 1
                    mix[chip] = (mix[chip] | (1 << bit)) & ~(8 << bit)
                    amp(v, vols[v])
        ticks.append((tuple(period), tuple(reg_amp), tuple(mix), tuple(noise)))
    return ticks


def render(stream, rate=RATE, highpass=True):
    """Les deux cotes, en flottants : puce 1 (voix 0-2) a gauche, puce 2 (voix
    3-5) a droite, sans fuite de l'une dans l'autre -- la Mockingboard A/C.

    L'AY compte sur une horloge de base a 1 MHz / 8 : le ton bascule toutes
    les `periode` bases, le bruit (LFSR de 17 bits, x^17 + x^14 + 1) avance
    toutes les 2 * R6 bases. Chaque echantillon integre le niveau sur les bases
    qu'il couvre, comme POM2 ; chaque puce est divisee par 3 puis passe par le
    passe-haut de 20 Hz de POM2. Le LFSR n'avance que quand il sonne : sa phase
    reelle depend du temps ecoule depuis le /RESET, elle est inconnaissable.
    Un canal qui a le ton et le bruit ouverts a la fois (music.s n'en fait
    jamais) est approche par le produit des deux.
    """
    spt = rate // TICK_HZ
    bps = AY_CLOCK / 8.0 / rate            # bases de l'AY par echantillon
    steps = [i * bps for i in range(spt + 1)]
    sides = [[], []]
    phase = [0.0] * 6                      # position dans la double periode, en bases
    last_p = [1] * 6
    lfsr, nout, npos = [1, 1], [1, 1], [0.0, 0.0]
    silence = [0.0] * spt
    for period, reg_amp, mix, noise in play_stream(stream):
        for c in range(2):
            buf = silence
            nfrac = None
            for ch in range(3):
                v = 3 * c + ch
                p = period[v] or 1
                if p != last_p[v]:         # le compteur continue, borne par la periode neuve
                    x, q = phase[v], last_p[v]
                    phase[v] = min(x, p - 1e-9) if x < q else p + min(x - q, p - 1e-9)
                    last_p[v] = p
                x0, p2 = phase[v], 2.0 * p
                phase[v] = (x0 + spt * bps) % p2
                lv = reg_amp[v] & 0x0F
                if not lv:
                    continue
                tone_on = not (mix[c] >> ch) & 1
                noise_on = not (mix[c] >> (ch + 3)) & 1
                level = AY_VOLUME[lv] / (3.0 * bps)
                if noise_on and nfrac is None:
                    nfrac = noise_frac(lfsr, nout, npos, c, 2.0 * ((noise[c] & 0x1F) or 1), spt, bps)
                if tone_on:
                    # temps passe a l'etat haut depuis le debut du tick : bas sur
                    # [0, p), haut sur [p, 2p), comme la bascule de sortie de l'AY
                    h = [(y // p2) * p + max(0.0, y % p2 - p) for y in [x0 + s for s in steps]]
                    frac = [b - a for a, b in zip(h, h[1:])]
                    if noise_on:
                        frac = [f * n / bps for f, n in zip(frac, nfrac)]
                elif noise_on:
                    frac = nfrac
                else:
                    frac = [bps] * spt
                buf = [s + f * level for s, f in zip(buf, frac)]
            sides[c].extend(buf)
    for side in sides:                     # l'apercu laisse sonner 0,3 s de silence
        side.extend([0.0] * int(0.3 * rate))
    if highpass:
        sides = [dc_block(side, rate) for side in sides]
    return sides


def noise_frac(lfsr, nout, npos, c, hold, spt, bps):
    """Le temps haut du bruit de la puce c dans chaque echantillon du tick, en
    bases ; `hold` bases entre deux pas du LFSR. Met a jour l'etat de la puce."""
    reg, bit, pos = lfsr[c], nout[c], npos[c]
    out = []
    for _ in range(spt):
        left, acc = bps, 0.0
        while left > 0.0:
            avail = hold - pos
            if avail > left:
                acc += bit * left
                pos += left
                break
            acc += bit * avail
            left -= avail
            pos = 0.0
            reg = (reg >> 1) | (((reg ^ (reg >> 3)) & 1) << 16)
            bit = reg & 1
        out.append(acc)
    lfsr[c], nout[c], npos[c] = reg, bit, pos
    return out


def dc_block(side, rate):
    """Le passe-haut de sortie de POM2 (et de MAME) : Butterworth d'ordre 2 a
    20 Hz, un par cote. Il retire la composante continue des niveaux de l'AY."""
    q = 0.7071067
    k = math.tan(math.pi * HIGHPASS_HZ / rate)
    d = k * k * q + k + q
    b0, b1, a1, a2 = q / d, -2.0 * q / d, 2.0 * q * (k * k - 1.0) / d, (k * k * q - k + q) / d
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for x in side:
        y = b0 * (x + x2) + b1 * x1 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y
        out.append(y)
    return out


def render_wav(path, stream, rate=RATE):
    """Ecrit l'apercu stereo 16 bits du flux MB1 `stream` (octets, en-tete compris)."""
    from array import array
    import sys
    left, right = render(stream, rate)
    frames = array("h", bytes(4 * len(left)))
    scale = WAV_GAIN * 32767.0
    frames[0::2] = array("h", [int(max(-32767.0, min(32767.0, s * scale))) for s in left])
    frames[1::2] = array("h", [int(max(-32767.0, min(32767.0, s * scale))) for s in right])
    if sys.byteorder == "big":
        frames.byteswap()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(frames.tobytes())


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
        render_wav(a.wav, Path(a.out).read_bytes())
    dropped = len(pitched) - sum(len(v) for v in voices)
    print(f"{Path(a.midi).name}: {len(notes)} notes -> "
          f"{[len(v) for v in voices]} par voix ({max(dropped, 0)} abandonnees), "
          f"{len(drums)} coups de batterie, {size} octets, "
          f"{total / TICK_HZ:.1f} s a {a.bpm:g} bpm -> {a.out}")


if __name__ == "__main__":
    main()
