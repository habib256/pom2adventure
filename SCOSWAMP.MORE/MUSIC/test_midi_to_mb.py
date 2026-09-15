"""L'apercu de midi_to_mb.py rejoue music.s : table de volume de l'AY, fondu
d'entree de 45 ticks, coupure nette au OFF, puce 1 a gauche et puce 2 a droite.

    python3 -m unittest test_midi_to_mb      (depuis SCOSWAMP.MORE/MUSIC)
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import midi_to_mb as mb                                         # noqa: E402

HEADER = b"MB1\0\x32\x00\x08\x00"
SPT = mb.RATE // mb.TICK_HZ


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


class RenderTest(unittest.TestCase):
    def test_fade_in_as_music_s(self):
        # VOL 15 et NOTE sur la voix 0 au tick 0, puis 60 ticks
        ticks = mb.play_stream(HEADER + bytes([0xA0, 15, 0x80, 33, 60, 0xE0]))
        amps = [t[1][0] for t in ticks]
        self.assertEqual(len(ticks), 60)
        self.assertEqual(amps[:4], [1, 1, 1, 2])        # atten 14 au premier tick, un pas par 3
        self.assertEqual(amps[42], 15)                  # atten 0 au tick 42
        self.assertEqual(amps[59], 15)

    def test_hard_cut_on_off(self):
        # apres le fondu d'entree : une note de 10 ticks, OFF, 10 ticks de silence
        body = bytes([0xA0, 15, 50, 0x80, 45, 10, 0x90, 10, 0xE0])
        left, right = mb.render(HEADER + body, highpass=False)
        tone = left[50 * SPT:60 * SPT]
        after = left[60 * SPT:70 * SPT]
        self.assertGreater(max(tone), 0.3)
        self.assertEqual(max(after), 0.0)               # aucune extinction
        self.assertEqual(max(right), 0.0)               # la puce 1 ne fuit pas a droite

    def test_logarithmic_volume(self):
        def level(vol, voice):
            body = bytes([0xA0 | voice, vol, 50, 0x80 | voice, 33, 50, 0xE0])
            sides = mb.render(HEADER + body, highpass=False)
            return rms(sides[voice // 3][60 * SPT:100 * SPT])
        ratio = level(15, 4) / level(8, 4)
        self.assertAlmostEqual(ratio, mb.AY_VOLUME[15] / mb.AY_VOLUME[8], delta=0.1)
        self.assertAlmostEqual(20 * math.log10(level(10, 0) / level(8, 0)), 7.1, delta=0.2)

    def test_noise_voice(self):
        body = bytes([0xA5, 12, 50, 0xB5, 10, 20, 0x95, 10, 0xE0])
        left, right = mb.render(HEADER + body, highpass=False)
        burst = right[50 * SPT:70 * SPT]
        self.assertGreater(max(burst), 0.0)
        self.assertLess(min(burst), max(burst))         # du bruit, pas un palier
        self.assertEqual(max(right[70 * SPT:80 * SPT]), 0.0)
        self.assertEqual(max(left), 0.0)


if __name__ == "__main__":
    unittest.main()
