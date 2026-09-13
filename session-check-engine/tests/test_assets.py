from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]


class AssetContractTests(unittest.TestCase):
    def test_eval_suites_are_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "validate_evals.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("cases=14", result.stdout)

    def test_golden_paths_are_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "validate_golden_paths.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("golden_paths=3", result.stdout)

    def test_router_exposes_all_commands(self) -> None:
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for command in ("doctor", "check-session", "hp-review", "tool-review", "forms", "progress", "practice", "knowledge", "sources"):
            self.assertIn(f"`{command}", router)

    def test_skill_is_self_contained(self) -> None:
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        check = (SKILL / "references" / "check-session.md").read_text(encoding="utf-8")
        self.assertNotIn("../high-performance-session-review", router + check)
        self.assertNotIn("../coaching-session-review", router + check)
        self.assertEqual(11, len(list((SKILL / "references" / "high-performance" / "sessions").glob("*.md"))))
        self.assertEqual(26, len(list((SKILL / "references" / "coaching-tools" / "topics").glob("*.md"))))

    def test_low_confidence_topic_and_absent_form_marker_are_hard_rules(self) -> None:
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        check = (SKILL / "references" / "check-session.md").read_text(encoding="utf-8")
        forms = (SKILL / "references" / "forms.md").read_text(encoding="utf-8")
        self.assertIn("If confidence would be `low`, ask", router)
        self.assertIn("two or more pillars as ambiguous by default", check)
        self.assertIn("exact literal marker `not discussed in the reviewed transcript`", forms)


if __name__ == "__main__":
    unittest.main()
