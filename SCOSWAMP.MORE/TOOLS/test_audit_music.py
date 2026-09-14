import unittest
from audit_music import inspect_stream

HEADER = b'MB1\0\x32\x00\x08\x00'


class MusicAuditTest(unittest.TestCase):
    def test_stream_and_timing(self):
        result = inspect_stream(HEADER + bytes([0xa0, 15, 0x80, 59, 50, 0x90, 0xe0]))
        self.assertEqual(result['seconds'], 1)
        self.assertEqual(result['peak_commands_per_tick'], 2)
        self.assertEqual(result['commands']['note'], 1)

    def test_reject_unsafe_streams(self):
        for body in ([0], [0x86, 20, 0xe0], [0x80, 60, 0xe0],
                     [0xa0, 16, 0xe0], [0xb0, 32, 0xe0], [0x80],
                     [1], [0xe0, 1], [0xc0, 0xe0]):
            with self.subTest(body=body), self.assertRaises(ValueError):
                inspect_stream(HEADER + bytes(body))


if __name__ == '__main__':
    unittest.main()
