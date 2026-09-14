#!/usr/bin/env python3
"""Bornes ld65 inclusives : le premier octet de pile ne doit jamais passer."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('check-memory.sh')


class MemoryBoundary(unittest.TestCase):
    def check_end(self, end, code, message, extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'edge.map'
            path.write_text(f'BSS 00AE10 {end:06X} {end-0xAE10+1:06X} 00001\n')
            result = subprocess.run(['bash', str(SCRIPT), '--himem', '0xBF00',
                                     '--stack', '0x0180', *extra, str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stdout+result.stderr)
            self.assertIn(message, result.stdout)

    def test_one_byte_free(self):
        self.check_end(0xBD7E, 0, 'marge de 1 octets')

    def test_exact_fit(self):
        self.check_end(0xBD7F, 0, 'marge de 0 octets')

    def test_first_stack_byte_is_overflow(self):
        self.check_end(0xBD80, 1, 'dépassement de 1 octets')

    def test_exact_reserve_passes(self):
        self.check_end(0xBD7F - 2048, 0, 'marge de 2048 octets', ('--min-free', '2048'))

    def test_one_byte_of_reserve_missing_fails(self):
        self.check_end(0xBD7F - 2047, 1, 'budget minimal de 2048', ('--min-free', '2048'))

    def test_negative_reserve_rejected(self):
        result = subprocess.run(['bash', str(SCRIPT), '--min-free', '-1'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
