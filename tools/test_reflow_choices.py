"""Formatting must preserve the executable order and therefore choice keys."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reflow", ROOT / "SCOSWAMP.MORE/TOOLS/reflow_txt.py")
reflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reflow)


def format_text(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "N001.TXT"
        path.write_text(text)
        title, body, choices, directives = reflow.parse(path)
    order = [line.rstrip() for line in text.splitlines()
             if reflow.DIRECTIVE.match(line) or reflow.CHOICE.match(line)]
    return reflow.render(1, title, reflow.wrap(body), choices, directives, order)


class ReflowChoiceTests(unittest.TestCase):
    def test_mixed_conditions_and_effects(self):
        mechanics = ["E OR -1", "C 116 First", "CG 1 078 Paid", "E ENDURANCE +2",
                     "CU FEU 100 Fire", "C 236 Next", "CA 0 0 101 Amulets",
                     "CV 001 102 Visit", "CX 001 103 Other", "CT 0 0 104 Empty",
                     "CI ANNEAU 105 Ring", "CN ANNEAU 106 No ring", "GU ANNEAU 107 Give",
                     "CP FEU 108 Gift", "CF 109 Flee", "C 289 Last"]
        result = format_text("T 001 Test\n\n   Some prose.\n\n" + "\n".join(mechanics) + "\n")
        self.assertEqual([line for line in result.splitlines()
                          if reflow.DIRECTIVE.match(line) or reflow.CHOICE.match(line)], mechanics)
        self.assertEqual(format_text(result), result)

    def test_actual_inn_choices_keep_letters(self):
        for lang in ["FR", "EN"]:
            text = (ROOT / f"SCOSWAMP/TEXT{lang}/N350/N395.TXT").read_text()
            result = format_text(text)
            original = [line for line in text.splitlines() if reflow.CHOICE.match(line)]
            self.assertEqual([line for line in result.splitlines() if reflow.CHOICE.match(line)], original)
            self.assertTrue(original[2].startswith("CG 1 078 "))


if __name__ == "__main__":
    unittest.main()
