"""Run a read-only Session Check Engine readiness diagnostic."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from context import inspect_context
from development_log import load_log, validate_log


def _deep_check(role: str) -> dict[str, Any]:
    validator = Path(__file__).resolve().parent / "validate_knowledge.py"
    command = [sys.executable, str(validator), "--library", role]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "ok": result.returncode == 0,
        "command": command,
        "output": (result.stdout + result.stderr).strip(),
    }


def diagnose(root: Path, deep: bool = False, skill_root: Path | None = None) -> dict[str, Any]:
    report = inspect_context(root, skill_root=skill_root)
    development = report["development"]
    development_errors: list[str] = []
    if development["exists"] and not development["error"]:
        try:
            development_errors = validate_log(load_log(Path(development["path"])))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            development_errors = [str(error)]

    deep_checks: dict[str, Any] = {}
    if deep and not report["blockers"]:
        for role in report["libraries"]:
            deep_checks[role] = _deep_check(role)

    if report["blockers"]:
        status = "blocked"
    elif development_errors or any(not item["ok"] for item in deep_checks.values()):
        status = "needs-attention"
    else:
        status = "ready"

    next_commands: list[dict[str, str]] = []
    if status == "blocked":
        next_commands.append(
            {"command": "sources validate", "reason": "Restore the missing bundled methodology files."}
        )
    else:
        if development["queued_drill_count"]:
            next_commands.append(
                {"command": "practice", "reason": "A de-identified drill is already queued or in progress."}
            )
        next_commands.append(
            {"command": "check-session [transcript]", "reason": "Run the complete gated review on the next real session."}
        )
        if not development["tracking_enabled"]:
            next_commands.append(
                {"command": "progress [transcript]", "reason": "Opt in only if longitudinal coach-development tracking is wanted."}
            )
        elif not development["queued_drill_count"]:
            next_commands.append(
                {"command": "practice [focus]", "reason": "Generate or resume focused practice after a frozen review."}
            )

    return {
        **report,
        "status": status,
        "development_errors": development_errors,
        "deep_checks": deep_checks,
        "next_commands": next_commands[:3],
    }


def print_human(report: dict[str, Any]) -> None:
    print(f"SESSION_CHECK_ENGINE_ROOT={report['root']}")
    print(f"STATUS={report['status']}")
    print(f"PRIVACY_MODE={report['privacy_mode']}")
    for role, item in report["libraries"].items():
        print(f"SOURCE_LIBRARY role={role} cards={item['card_count']} present={str(item['present']).lower()}")
    development = report["development"]
    print(f"TRACKING_ENABLED={str(development['tracking_enabled']).lower()}")
    print(f"ACTIVE_FOCUSES={development['active_focus_count']}")
    print(f"QUEUED_DRILLS={development['queued_drill_count']}")
    for error in report["development_errors"]:
        print(f"ERROR development: {error}")
    for role, item in report["deep_checks"].items():
        print(f"DEEP_CHECK role={role} ok={str(item['ok']).lower()}")
        if not item["ok"]:
            print(item["output"])
    for item in report["next_commands"]:
        print(f"NEXT {item['command']} :: {item['reason']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = diagnose(args.root, args.deep)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
