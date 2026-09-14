import unittest
from compile_game_rules import compile_rules


class GameRulesTests(unittest.TestCase):
    def test_other_game_keys_and_positions(self):
        rules = {"schema": 1, "save_migrations": [{"when_none": [".CREW", ".PILOT"],
                  "first_visited": [{"page": 8, "give": ".PILOT"}, {"page": 2, "give": ".CREW"}]}]}
        result = compile_rules(rules, ["TOOL", ".CREW", ".PILOT"])
        self.assertIn("{6u, 8u, 4u}, {6u, 2u, 2u}", result)

    def test_unknown_reference(self):
        with self.assertRaises(KeyError):
            compile_rules({"schema": 1, "save_migrations": [{"when_none": ["MISSING"],
                          "first_visited": [{"page": 2, "give": "MISSING"}]}]}, [])

    def test_group_must_set_its_own_guard(self):
        with self.assertRaises(ValueError):
            compile_rules({"schema": 1, "save_migrations": [{"when_none": [".A"],
                          "first_visited": [{"page": 2, "give": ".B"}]}]}, [".A", ".B"])

    def test_no_migrations_is_valid(self):
        self.assertIn("MIGRATION_COUNT 0", compile_rules({"schema": 1}, []))

    def test_trade_uses_other_game_positions(self):
        rules = {"schema": 1, "trade": {"objects": ["FUEL", "MAP"],
                 "amulets": False, "limit": 1, "categories": "NM"}}
        result = compile_rules(rules, ["MAP", "TOOL", "FUEL"])
        for expected in ['OBJECT_MASK 5u', 'AMULETS 0', 'LIMIT 1', 'CATEGORIES "NM"']:
            self.assertIn(expected, result)

    def test_trade_rejects_bad_configuration(self):
        base = {"objects": ["TOOL"], "amulets": True, "limit": 3, "categories": "N"}
        for change in [{"objects": ["MISSING"]}, {"objects": ["TOOL", "TOOL"]},
                       {"limit": -1}, {"limit": 256}, {"limit": True}, {"amulets": 1},
                       {"categories": "NN"}, {"categories": "NBM"}, {"categories": "X"}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                compile_rules({"schema": 1, "trade": {**base, **change}}, ["TOOL"])


if __name__ == '__main__':
    unittest.main()
