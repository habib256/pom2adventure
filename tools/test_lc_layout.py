import unittest
from tools.check_lc_layout import check_layout


class SplitLoadLayout(unittest.TestCase):
    def setUp(self):
        self.s = dict(__LCIMAGE_FILEOFFS__=0, __LCIMAGE_START__=0x1000,
                      __LCIMAGE_SIZE__=0xC00, __MAIN_FILEOFFS__=0xC00,
                      __MAIN_START__=0x4000, __MAIN_LAST__=0xB348,
                      __LC_START__=0xD400, __LC_LAST__=0xE000,
                      __LCIMAGE_LAST__=0x1C00,
                      # Le plancher de la pile C, que ld65 ne verifie pas.
                      __HIMEM__=0xBF00, __STACKSIZE__=0x180,
                      __ONCE_RUN__=0xB249, __BSS_RUN__=0xB249,
                      __BSS_SIZE__=0x25C)
        self.loader = dict(LC_STAGE=0x1000, LC_BYTES=0xC00, GAME_ADDR=0x4000)
        self.length = 32584

    def check(self):
        return check_layout(self.s, self.loader, self.length)

    def test_valid_and_padded_prefix(self):
        self.assertEqual(self.check(), [])
        self.s['__LC_LAST__'] -= 128
        self.s['__LCIMAGE_LAST__'] -= 128
        self.assertEqual(self.check(), [], 'shorter LC still has fixed file prefix')

    def test_loader_disagreement(self):
        for key in self.loader:
            with self.subTest(key=key):
                self.loader[key] += 1
                self.assertTrue(self.check())
                self.loader[key] -= 1

    def test_wrong_file_offsets_and_length(self):
        for key in ['__LCIMAGE_FILEOFFS__', '__MAIN_FILEOFFS__']:
            self.s[key] += 1
            self.assertTrue(self.check())
            self.s[key] -= 1
        for delta in [-1,1]:
            self.assertTrue(check_layout(self.s,self.loader,self.length+delta))

    def test_stage_overlaps_launcher_even_if_loader_agrees(self):
        self.loader['LC_STAGE'] = self.s['__LCIMAGE_START__'] = 0x1500
        self.s['__LCIMAGE_LAST__'] = 0x2100
        self.assertIn('LC staging overlaps ProDOS buffers or the graphics page', self.check())

    def test_system_and_bank_overflow(self):
        self.s['__MAIN_LAST__'] = 0xBF01
        self.assertTrue(self.check())
        self.s['__MAIN_LAST__'] = 0xB348
        self.s['__LC_LAST__'] = 0xE001
        self.s['__LCIMAGE_LAST__'] = 0x1C01
        self.assertTrue(self.check())


    def test_cold_end_must_stay_under_the_c_stack(self):
        """ld65 calcule la zone BSS par __HIMEM__ - __STACKSIZE__ -
        __ONCE_RUN__ et lit le resultat en entier non signe : quand il passe
        en negatif, il pose la BSS dans la pile sans rien signaler."""
        self.assertEqual(self.check(), [])
        self.s['__ONCE_RUN__'] = self.s['__BSS_RUN__'] = 0xBD81   # $BF00 - $180 + 1
        self.assertTrue(any('C stack' in e for e in self.check()))

    def test_bss_alone_may_not_reach_the_stack(self):
        self.s['__BSS_SIZE__'] = 0xC00                            # jusqu'en $BE49
        self.assertTrue(any('BSS' in e for e in self.check()))

if __name__ == '__main__':
    unittest.main()
