from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "development_log.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class DevelopmentLogTests(unittest.TestCase):
    def test_one_prompt_is_persisted_and_resumed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(0, run(root, "init").returncode)
            added = run(
                root,
                "add-focus",
                "--id", "confirm-first",
                "--label", "Confirm first",
                "--target", "Confirm the client's meaning before interpreting.",
                "--reduce", "Premature interpretation.",
                "--priority", "1",
            )
            self.assertEqual(0, added.returncode, added.stderr)
            drill = run(
                root,
                "drill",
                "--focus", "confirm-first",
                "--id", "confirm-first-01",
                "--date", "2026-08-13",
                "--source-session", "S00 Strategy",
                "--name", "Paraphrase and confirm",
                "--trigger", "The coach sees a quick interpretation.",
                "--prompt", "Give a faithful paraphrase.",
                "--prompt", "Ask for confirmation.",
                "--portable-rule", "Confirm before interpreting.",
                "--note", "Simulation only.",
            )
            self.assertEqual(0, drill.returncode, drill.stderr)
            first = run(root, "next-exercise")
            self.assertEqual(0, first.returncode, first.stderr)
            first_payload = json.loads(first.stdout)
            self.assertEqual(1, first_payload["prompt_number"])
            resumed = json.loads(run(root, "next-exercise").stdout)
            self.assertEqual(first_payload, resumed)
            advanced = run(root, "advance-exercise", "--focus", "confirm-first", "--drill-id", "confirm-first-01")
            self.assertEqual(2, json.loads(advanced.stdout)["prompt_number"])
            completed = run(root, "advance-exercise", "--focus", "confirm-first", "--drill-id", "confirm-first-01")
            self.assertEqual("completed", json.loads(completed.stdout)["status"])

    def test_more_than_three_prompts_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run(root, "init")
            run(
                root,
                "add-focus",
                "--id", "focus",
                "--label", "Focus",
                "--target", "Target behavior.",
                "--reduce", "Old behavior.",
                "--priority", "1",
            )
            result = run(
                root,
                "drill",
                "--focus", "focus",
                "--id", "too-long",
                "--date", "2026-08-13",
                "--source-session", "S00 Strategy",
                "--name", "Too long",
                "--trigger", "Trigger.",
                "--prompt", "One",
                "--prompt", "Two",
                "--prompt", "Three",
                "--prompt", "Four",
                "--portable-rule", "Rule.",
                "--note", "Note.",
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("1-3 strings", result.stderr)


if __name__ == "__main__":
    unittest.main()
