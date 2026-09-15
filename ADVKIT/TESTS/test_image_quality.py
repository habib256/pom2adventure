#!/usr/bin/python3
"""Mesure de qualite DHGR, --resample area et refus des masters de generate_images.sh.

Images synthetiques dans des dossiers temporaires ; le depot n'est jamais ecrit.
Il faut numpy et Pillow (/usr/bin/python3 sur macOS). Les tests natifs exigent
ADVKIT/TOOLS/build/scoswamp_dhgr.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('quality', ROOT / 'ADVKIT/TOOLS/image_quality.py')
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)
spec = importlib.util.spec_from_file_location('workshop', ROOT / 'ADVKIT/image_workshop.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
native = unittest.skipUnless(q.CONVERTER.exists(), 'scoswamp_dhgr non construit')
PAL8 = q.PAL.astype(np.uint8)


def encode_idx(idx):
    """Indices 192x140 -> flux DHRR v1 en litteraux (l'inverse de decode_raw)."""
    page = bytearray(16384)
    v = ((idx >> 1) | (idx << 3)) & 15
    for y in range(192):
        base = (y // 64) * 0x28 + ((y % 64) // 8) * 0x80 + (y % 8) * 0x400
        for dot in range(560):
            if (int(v[y, dot // 4]) >> (dot % 4)) & 1:
                col = dot // 7
                page[(8192 if col & 1 else 0) + base + col // 2] |= 1 << (dot % 7)
    out = bytearray(b'DHRR\x01\x00\x00\x40')
    for i in range(0, 16384, 128):
        out += bytes([127]) + page[i:i + 128]
    return bytes(out)


def save(path, rgb):
    Image.fromarray(np.asarray(rgb, np.uint8)).save(path)
    return path


def cells(idx):
    """Indices 192x140 -> master 280x192 dont chaque cellule DHGR fait 2x1 pixels."""
    return PAL8[np.repeat(idx, 2, axis=1)]


def checker(cols=140):
    idx = np.zeros((192, 140), np.uint8)
    yy, xx = np.mgrid[:192, :cols]
    idx[:, :cols] = np.where((yy + xx) % 2, 15, 0)
    return idx


def flat_blocks():
    idx = np.zeros((192, 140), np.uint8)
    idx[:96, 70:] = 6; idx[96:, :70] = 12; idx[96:, 70:] = 9
    return idx


class MetricsTest(unittest.TestCase):
    def test_rle_round_trip_and_rejects(self):
        idx = np.random.default_rng(1).integers(0, 16, (192, 140)).astype(np.uint8)
        blob = encode_idx(idx)
        self.assertTrue((q.decode_rle(blob) == idx).all())
        for bad in (blob[:-1], blob + b'\0', b'DHRX' + blob[4:], blob[:8] + b'\x85'):
            with self.subTest(size=len(bad)), self.assertRaises(ValueError):
                q.decode_rle(bad)

    def test_isolated_pixels(self):
        self.assertAlmostEqual(q.isolated_pct(checker()), 190 * 138 / (192 * 140) * 100)
        dot = np.zeros((192, 140), np.uint8); dot[50, 50] = 3
        self.assertAlmostEqual(q.isolated_pct(dot), 100 / (192 * 140))
        self.assertEqual(q.isolated_pct(flat_blocks()), 0)

    def test_ssim_gray_and_palette(self):
        idx = flat_blocks()
        cell = q.s2l(q.PAL[idx])
        m = q.conversion_metrics(idx, cell)
        self.assertAlmostEqual(m['ssim'], 1.0, places=6)
        self.assertAlmostEqual(m['dE'], 0.0, places=3)
        self.assertEqual(q.conversion_metrics(np.full((192, 140), 5, np.uint8), cell)['gray'], 100)
        self.assertEqual(q.palette_pct(Image.fromarray(cells(idx))), 100)
        brown = np.full((192, 280, 3), (120, 100, 90), np.uint8)
        self.assertEqual(q.palette_pct(Image.fromarray(brown)), 0)

    def test_excess(self):
        self.assertEqual(q.excess(dict(palette=80, isolated=4.5)), 0)
        self.assertAlmostEqual(q.excess(dict(palette=60, isolated=1)), 0.25)
        self.assertAlmostEqual(q.excess(dict(palette=90, isolated=9)), 1.0)
        self.assertAlmostEqual(q.excess(dict(palette=60, isolated=9), 80, 4.5), 1.25)


@native
class NativeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args, env=None):
        return subprocess.run([sys.executable, str(ROOT / 'ADVKIT/TOOLS/image_quality.py'), *map(str, args)],
                              capture_output=True, text=True, env=dict(os.environ, **(env or {})))

    def test_decoder_matches_converter_preview(self):
        idx = np.random.default_rng(2).integers(0, 16, (192, 140)).astype(np.uint8)
        master = save(self.dir / 'm.png', cells(idx))
        out = self.dir / 'm.bin'
        subprocess.run([q.CONVERTER, 'convert', master, out, self.dir / 'c.png'], check=True, capture_output=True)
        preview = np.asarray(Image.open(self.dir / 'c.png').convert('RGB'))
        self.assertTrue((cells(q.decode_rle(out.read_bytes())) == preview).all())

    def test_check_exit_codes(self):
        good = save(self.dir / 'good.png', cells(flat_blocks()))
        noisy = save(self.dir / 'noisy.png', cells(checker()))
        brown = save(self.dir / 'brown.png', np.full((192, 280, 3), (120, 100, 90)))
        r = self.run_tool('check', good)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertTrue(r.stdout.startswith('ok'))
        for path in (noisy, brown):
            r = self.run_tool('check', path)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertTrue(r.stdout.startswith('HORS')); self.assertGreater(float(r.stdout.split()[-1]), 0)
        r = self.run_tool('check', noisy, env=dict(IMAGE_MAX_ISOLATED='100'))
        self.assertEqual(r.returncode, 0, r.stdout)
        (self.dir / 'broken.png').write_bytes(b'not a png')
        self.assertEqual(self.run_tool('check', self.dir / 'broken.png').returncode, 2)

    def test_worst_ranks_a_batch(self):
        root = self.dir / 'root'
        (root / 'SCOSWAMP.MORE/GENERATED').mkdir(parents=True)
        for name, idx in (('N001', flat_blocks()), ('N002', checker()), ('N051', checker(40))):
            save(root / f'SCOSWAMP.MORE/GENERATED/{name}.png', cells(idx))
            bucket = root / 'SCOSWAMP/DHGR' / ('N%03d' % (int(name[1:]) // 50 * 50)); bucket.mkdir(parents=True, exist_ok=True)
            (bucket / (name + '.RLE.BIN')).write_bytes(encode_idx(idx))
        r = self.run_tool('worst', '--root', root, '--count', 2, '--sort', 'isolated', '--json')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([row['name'] for row in json.loads(r.stdout)], ['N002', 'N051'])

    def test_default_resample_is_bilinear_to_the_byte(self):
        master = save(self.dir / 'm.png', np.random.default_rng(3).integers(0, 256, (333, 517, 3)))
        blobs = []
        for extra in ([], ['--resample', 'bilinear'], ['--resample', 'area']):
            out = self.dir / ('o%d.bin' % len(blobs))
            subprocess.run([q.CONVERTER, 'convert', *extra, master, out], check=True, capture_output=True)
            blobs.append(out.read_bytes())
        self.assertEqual(blobs[0], blobs[1]); self.assertNotEqual(blobs[0], blobs[2])
        r = subprocess.run([q.CONVERTER, 'convert', '--resample', 'box', master, self.dir / 'x.bin'], capture_output=True)
        self.assertEqual(r.returncode, 2)

    def test_area_averages_what_bilinear_skips(self):
        # Rayures d'une periode de 3 pixels : 10 pixels source par cellule. Le
        # bilineaire lit 2 texels dont la phase change d'une colonne a l'autre ;
        # la moyenne de zone voit partout un tiers de blanc.
        rgb = np.zeros((960, 1400, 3), np.uint8); rgb[:, ::3] = 255
        master = save(self.dir / 'stripes.png', rgb)
        colours = {}
        for mode in ('bilinear', 'area'):
            out = self.dir / (mode + '.bin')
            subprocess.run([q.CONVERTER, 'convert', '--resample', mode, master, out], check=True, capture_output=True)
            colours[mode] = len(np.unique(q.decode_rle(out.read_bytes())[:, 1:-1]))
        self.assertEqual(colours['area'], 1)
        self.assertGreater(colours['bilinear'], 1)

    def test_area_keeps_recipe_framing(self):
        # La mire du test de l'atelier, cadree et en bandes : meme boite englobante
        # a deux points pres, pour les quatre modeles DHGR.
        rgb = np.zeros((300, 500, 3), np.uint8); rgb[80:220, 180:320] = 255
        master = save(self.dir / 'mire.png', rgb)
        def bbox(blob):
            page = bytearray(16384); i = 8; raw = bytearray()
            while i < len(blob):
                t = blob[i]; i += 1
                if t & 128: raw += bytes([blob[i]]) * ((t & 127) + 3); i += 1
                else: raw += blob[i:i + t + 1]; i += t + 1
            pts = [(x, y) for y in range(192) for x in range(560)
                   if raw[((y & 7) << 10) + ((y & 56) << 4) + (y // 64) * 40 + ((x // 7) & 1) * 8192 + x // 14] & (1 << (x % 7))]
            return min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts)
        for model in range(4):
            for crop in (None, [100, 40, 450, 280]):     # 350x240 : ratio 35:24
                recipe = dict(w.DEFAULTS, model=model, crop=crop)
                boxes = []
                for mode in ('bilinear', 'area'):
                    dest = self.dir / f'{mode}{model}{bool(crop)}'; dest.mkdir()
                    w.convert(master, 'dhgr', recipe, dest, mode)
                    boxes.append(bbox((dest / 'image.bin').read_bytes()))
                with self.subTest(model=model, crop=crop):
                    for a, b in zip(*boxes): self.assertLessEqual(abs(a - b), 4 if model == 1 else 2)


@native
class GenerateImagesTest(unittest.TestCase):
    """generate_images.sh avec une generation simulee (GEN_COMMAND) dans une copie."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name).resolve()
        (self.root / 'SCOSWAMP.MORE/TOOLS').mkdir(parents=True)
        (self.root / 'ADVKIT/TOOLS/build').mkdir(parents=True)
        shutil.copy(ROOT / 'SCOSWAMP.MORE/TOOLS/generate_images.sh', self.root / 'SCOSWAMP.MORE/TOOLS/')
        shutil.copy(ROOT / 'ADVKIT/TOOLS/image_quality.py', self.root / 'ADVKIT/TOOLS/')
        os.symlink(q.CONVERTER, self.root / 'ADVKIT/TOOLS/build/scoswamp_dhgr')
        self.gen = self.root / 'SCOSWAMP.MORE/GENERATED'; self.gen.mkdir()
        self.kinds = self.root / 'kinds'; self.kinds.mkdir()
        save(self.kinds / 'good.png', cells(flat_blocks()))
        save(self.kinds / 'bad.png', cells(checker(28)))      # ~20 % de pixels isoles
        save(self.kinds / 'worse.png', cells(checker()))      # ~98 %
        (self.root / 'fake.py').write_text(
            'import json, os, shutil, sys\n'
            'dest = os.environ["GEN_DEST"]; name = os.path.basename(dest)[:4]\n'
            'plan = json.load(open(os.environ["PLAN"]))[name]\n'
            'count = os.path.join(os.environ["PLAN"] + "." + name)\n'
            'n = int(open(count).read()) if os.path.exists(count) else 0\n'
            'open(count, "w").write(str(n + 1))\n'
            'kind = plan[min(n, len(plan) - 1)]\n'
            'if kind != "none": shutil.copy(os.path.join(os.environ["KINDS"], kind + ".png"), dest)\n')

    def tearDown(self):
        self.tmp.cleanup()

    def generate(self, plan, force=False):
        (self.root / 'plan.json').write_text(json.dumps(plan))
        for f in self.root.glob('plan.json.*'): f.unlink()
        manifest = self.root / 'manifest.jsonl'
        manifest.write_text(''.join(json.dumps(dict(source_png=f'SCOSWAMP.MORE/GENERATED/{n}.png', prompt='scene', refs=[])) + '\n'
                                    for n in plan))
        env = dict(os.environ, GEN_COMMAND=f'"{sys.executable}" "{self.root / "fake.py"}"', PLAN=str(self.root / 'plan.json'),
                   KINDS=str(self.kinds), IMAGE_QUALITY_PYTHON=sys.executable, FORCE='1' if force else '0',
                   TMPDIR=str(self.root))
        r = subprocess.run(['bash', str(self.root / 'SCOSWAMP.MORE/TOOLS/generate_images.sh'), str(manifest)],
                           capture_output=True, text=True, env=env, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def same(self, name, kind):
        return (self.gen / f'{name}.png').read_bytes() == (self.kinds / f'{kind}.png').read_bytes()

    def rejects(self, name):
        return sorted(p.name for p in (self.gen / '.rejets').glob(name + '*')) if (self.gen / '.rejets').exists() else []

    def test_refuse_retry_and_keep_the_least_bad(self):
        save(self.gen / 'N004.png', cells(checker()))
        before = (self.gen / 'N004.png').read_bytes(); stamp = (self.gen / 'N004.png').stat().st_mtime_ns
        plan = dict(N001=['bad', 'good'], N002=['worse', 'bad', 'worse'], N003=['good'], N004=['good'],
                    N005=['bad', 'none'], N006=['none'])
        out = self.generate(plan)
        self.assertTrue(self.same('N001', 'good')); self.assertEqual(len(self.rejects('N001')), 1)
        self.assertTrue(self.same('N002', 'bad')); self.assertEqual(len(self.rejects('N002')), 2)
        self.assertTrue(self.same('N003', 'good')); self.assertEqual(self.rejects('N003'), [])
        self.assertEqual((self.gen / 'N004.png').read_bytes(), before)
        self.assertEqual((self.gen / 'N004.png').stat().st_mtime_ns, stamp)
        self.assertTrue(self.same('N005', 'bad')); self.assertEqual(self.rejects('N005'), [])
        self.assertFalse((self.gen / 'N006.png').exists())
        self.assertIn('HORS SCOSWAMP.MORE/GENERATED/N002.png', out)
        self.assertIn('ECHEC SCOSWAMP.MORE/GENERATED/N006.png', out)
        self.assertIn('4 image(s) generee(s), 1 echec(s)', out)
        self.assertIn('2 master(s) hors seuils', out)
        self.assertEqual(sorted(p.name for p in (self.gen / '.failed').iterdir()),
                         ['N002.hors-seuils', 'N005.hors-seuils', 'N006.log'])

    def test_force_keeps_a_copy_of_the_previous_master(self):
        save(self.gen / 'N007.png', cells(checker(60)))
        before = (self.gen / 'N007.png').read_bytes()
        out = self.generate(dict(N007=['bad', 'good']), force=True)
        self.assertTrue(self.same('N007', 'good'), out)
        kept = [p for p in (self.gen / '.rejets').iterdir() if '.avant-' in p.name]
        self.assertEqual(len(kept), 1); self.assertEqual(kept[0].read_bytes(), before)
        self.assertEqual(len(self.rejects('N007')), 2)   # la copie + l'essai refuse


if __name__ == '__main__':
    unittest.main()
