"""Inspect bundled Session Check Engine libraries and private development state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LIBRARIES = {
    "high-performance": ("high-performance", "sessions", 11),
    "coaching-tools": ("coaching-tools", "topics", 26),
}


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, str(error)
    if not isinstance(value, dict):
        return None, "root value must be an object"
    return value, None


def inspect_context(root: Path, skill_root: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    skill = (skill_root or Path(__file__).resolve().parents[1]).resolve()
    references = skill / "references"

    libraries: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    for role, (folder, card_folder, minimum) in LIBRARIES.items():
        path = references / folder
        catalog = path / "catalog.md"
        manifest = path / "source-manifest.md"
        policy = path / "source-policy.md"
        cards = sorted((path / card_folder).glob("*.md"))
        item = {
            "path": str(path),
            "catalog_present": catalog.is_file(),
            "manifest_present": manifest.is_file(),
            "policy_present": policy.is_file(),
            "card_count": len(cards),
            "expected_card_count": minimum,
            "present": catalog.is_file() and manifest.is_file() and policy.is_file() and len(cards) >= minimum,
        }
        libraries[role] = item
        if not item["catalog_present"]:
            blockers.append(f"missing {role} catalog")
        if not item["manifest_present"]:
            blockers.append(f"missing {role} source manifest")
        if not item["policy_present"]:
            blockers.append(f"missing {role} source policy")
        if item["card_count"] < minimum:
            blockers.append(f"{role} has {item['card_count']} cards; expected at least {minimum}")

    log_path = root / ".coaching-supervision" / "coach-development.json"
    development: dict[str, Any] = {
        "path": str(log_path),
        "exists": log_path.is_file(),
        "tracking_enabled": False,
        "active_focus_count": 0,
        "queued_drill_count": 0,
        "error": None,
    }
    if log_path.is_file():
        value, error = _load_json(log_path)
        development["error"] = error
        if value is not None:
            focuses = value.get("focus_areas", [])
            if not isinstance(focuses, list):
                development["error"] = "focus_areas must be an array"
            else:
                development["tracking_enabled"] = value.get("tracking_enabled") is True
                development["active_focus_count"] = sum(
                    isinstance(item, dict) and item.get("status") == "active"
                    for item in focuses
                )
                development["queued_drill_count"] = sum(
                    1
                    for item in focuses
                    if isinstance(item, dict)
                    for drill in item.get("drills", [])
                    if isinstance(drill, dict)
                    and drill.get("status") in {"planned", "in_progress"}
                )

    return {
        "root": str(root),
        "skill_root": str(skill),
        "status": "blocked" if blockers else "ready",
        "blockers": blockers,
        "libraries": libraries,
        "development": development,
        "privacy_mode": "development" if development["tracking_enabled"] else "review",
    }


def print_human(report: dict[str, Any]) -> None:
    print(f"SESSION_CHECK_ENGINE_ROOT={report['root']}")
    print(f"SKILL_ROOT={report['skill_root']}")
    print(f"STATUS={report['status']}")
    print(f"PRIVACY_MODE={report['privacy_mode']}")
    for role, item in report["libraries"].items():
        print(
            f"LIBRARY role={role} present={str(item['present']).lower()} "
            f"cards={item['card_count']} path={item['path']}"
        )
    development = report["development"]
    print(f"DEVELOPMENT_LOG={development['path']}")
    print(f"TRACKING_ENABLED={str(development['tracking_enabled']).lower()}")
    print(f"ACTIVE_FOCUSES={development['active_focus_count']}")
    print(f"QUEUED_DRILLS={development['queued_drill_count']}")
    if development["error"]:
        print(f"DEVELOPMENT_ERROR={development['error']}")
    for blocker in report["blockers"]:
        print(f"BLOCKER={blocker}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = inspect_context(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
