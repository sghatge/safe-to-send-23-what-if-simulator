import json
import unittest

from whatif import simulate

with open("examples/profiles.json", encoding="utf-8") as fh:
    P = {p["name"]: p for p in json.load(fh)}


class WhatIfTest(unittest.TestCase):
    def test_capped_profile_training_adds_nothing(self):
        base, rows = simulate(P["Fast mover, loose guardrails"])
        self.assertEqual(base, 59)
        gains = {what: g for g, what in rows}
        self.assertEqual(gains["+1 on Practical AI skills"], 0)
        self.assertGreater(gains["Fix data handling (clear flag, +2 on privacy)"], 20)
        self.assertEqual(rows[0][1], "Fix data handling (clear flag, +2 on privacy)")

    def test_uncapped_profile_every_bump_helps_or_holds(self):
        _, rows = simulate(P["Blocked enthusiast"])
        self.assertTrue(all(g >= 0 for g, _ in rows))
        self.assertEqual(len(rows), 10)


if __name__ == "__main__":
    unittest.main()
