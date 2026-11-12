"""Verify built-in lessons and the tutoring helpers."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from puzzlecoach.coach import check_attempt, explain_program, explain_rule
from puzzlecoach.engine import run, s
from puzzlecoach.format import parse_any
from puzzlecoach.puzzles import PUZZLES
from puzzlecoach.search import search_rules


class BuiltinPuzzles(unittest.TestCase):
    def test_authored_rules_match_outputs(self):
        for p in PUZZLES:
            with self.subTest(p["id"]):
                mm = p["use_marker"]
                for ex in p["examples"]:
                    got = run(p["rules"], ex["input"], mm)
                    self.assertEqual(got, ex["output"], p["id"])
                self.assertEqual(run(p["rules"], p["test"], mm), p["test_output"])

    def test_explanations_cover_vocabulary(self):
        for p in PUZZLES:
            text = explain_program(p["rules"], "en")
            self.assertTrue(len(text) > 20)
            self.assertNotIn("None", text)
            self.assertTrue(len(explain_program(p["rules"], "zh")) > 10)

    def test_check_attempt(self):
        p = PUZZLES[0]
        ok = check_attempt(p["test_output"], p["test_output"])
        self.assertTrue(ok["correct"])
        bad = [row[:] for row in p["test_output"]]
        bad[0][0] = 1 if bad[0][0] == 0 else 0
        result = check_attempt(p["test_output"], bad)
        self.assertFalse(result["correct"])
        self.assertGreater(result["wrong_count"], 0)
        self.assertIn("row", result["focus"])


class FormatAndSearch(unittest.TestCase):
    def test_parse_text_and_json(self):
        p = PUZZLES[1]
        rows = lambda g: "\n".join("".join(map(str, r)) for r in g)
        text = (
            "Example 1 input (10 rows x 10 cols):\n"
            + rows(p["examples"][0]["input"])
            + "\n\nExample 1 output (10 rows x 10 cols):\n"
            + rows(p["examples"][0]["output"])
            + "\n\nTest input (10 rows x 10 cols):\n"
            + rows(p["test"])
            + "\n"
        )
        parsed = parse_any(text)
        self.assertEqual(parsed["examples"][0]["input"], p["examples"][0]["input"])
        self.assertEqual(parsed["test"], p["test"])

        import json
        blob = json.dumps(
            {
                "train": [{"input": p["examples"][0]["input"], "output": p["examples"][0]["output"]}],
                "test": [{"input": p["test"], "output": p["test_output"]}],
            }
        )
        parsed2 = parse_any(blob)
        self.assertEqual(parsed2["test_output"], p["test_output"])

    def test_search_finds_one_rule_puzzles(self):
        # Keep this to the single-rule lessons so the test stays quick.
        for p in PUZZLES:
            if len(p["rules"]) != 1:
                continue
            with self.subTest(p["id"]):
                ex = [(e["input"], e["output"]) for e in p["examples"]]
                result = search_rules(ex, test=p["test"], marker_mode=False, beam=40, depth=2, timeout=20)
                self.assertTrue(result["solved"], result["log"])
                keys = {s["test_key"] for s in result["solutions"]}
                self.assertIn(s(p["test_output"]), keys)

    def test_search_finds_two_step_puzzle(self):
        p = next(x for x in PUZZLES if x["id"] == "fall-of-towers")
        ex = [(e["input"], e["output"]) for e in p["examples"]]
        result = search_rules(ex, test=p["test"], marker_mode=False, beam=50, depth=3, timeout=30)
        self.assertTrue(result["solved"], result["log"])
        keys = {s["test_key"] for s in result["solutions"]}
        self.assertIn(s(p["test_output"]), keys)


if __name__ == "__main__":
    unittest.main()
