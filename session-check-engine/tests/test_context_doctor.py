from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from context import inspect_context  # noqa: E402
from doctor import diagnose  # noqa: E402


class ContextTests(unittest.TestCase):
    def test_bundled_libraries_make_an_empty_workspace_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = sorted(path.relative_to(root) for path in root.rglob("*"))
            report = diagnose(root)
            after = sorted(path.relative_to(root) for path in root.rglob("*"))
            self.assertEqual("ready", report["status"])
            self.assertEqual("review", report["privacy_mode"])
            self.assertEqual(11, report["libraries"]["high-performance"]["card_count"])
            self.assertEqual(26, report["libraries"]["coaching-tools"]["card_count"])
            self.assertEqual(before, after)
            self.assertEqual("check-session [transcript]", report["next_commands"][0]["command"])

    def test_missing_bundled_library_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake_skill = Path(directory) / "session-check-engine"
            (fake_skill / "references" / "high-performance").mkdir(parents=True)
            (fake_skill / "references" / "coaching-tools").mkdir(parents=True)
            report = inspect_context(Path(directory), skill_root=fake_skill)
            self.assertEqual("blocked", report["status"])
            self.assertTrue(report["blockers"])

    def test_development_state_remains_workspace_local(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / ".coaching-supervision" / "coach-development.json"
            state.parent.mkdir(parents=True)
            state.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "tracking_enabled": True,
                        "privacy": {"stores_client_data": False, "rule": "De-identified only."},
                        "focus_areas": [],
                    }
                ),
                encoding="utf-8",
            )
            report = inspect_context(root)
            self.assertEqual(str(state), report["development"]["path"])
            self.assertTrue(report["development"]["tracking_enabled"])


if __name__ == "__main__":
    unittest.main()
