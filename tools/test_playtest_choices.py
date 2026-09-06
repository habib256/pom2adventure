import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "SCOSWAMP.MORE/TOOLS/playtest.py"
spec = importlib.util.spec_from_file_location("playtest", path)
playtest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(playtest)


class ChoiceScreenTests(unittest.TestCase):
    def test_packed_choices_with_one_separator(self):
        rows = [" " * 80 for _ in range(24)]
        rows[21] = "A) " + "x" * 36 + " " + "B) next".ljust(40)
        rows[22] = "-) unavailable".ljust(80)
        rows[23] = "D) final".ljust(80)
        game = playtest.Game(None, None)
        self.assertEqual(game.choices(rows), ["A", "B", "-", "D"])
        self.assertEqual(game.letters(rows), ["A", "B", "D"])

    def test_mentions_inside_title_are_not_choices(self):
        rows = [" " * 80 for _ in range(24)]
        rows[23] = "A) Read option  B) inside this title".ljust(80)
        self.assertEqual(playtest.Game(None, None).choices(rows), ["A"])


if __name__ == "__main__":
    unittest.main()
