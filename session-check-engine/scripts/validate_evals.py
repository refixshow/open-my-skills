"""Validate declarative Coaching Engine behavior-evaluation suites."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CASE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_ROUTES = {"doctor", "check-session", "hp-review", "tool-review", "forms", "progress", "practice", "knowledge", "sources"}
VALID_RISKS = {"low", "medium", "high", "sensitive"}


def _strings(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, list) and len(value) >= minimum and all(isinstance(item, str) and item.strip() for item in value)


def validate_suite(value: Any, path: Path, skill: Path) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: suite must be an object"]
    errors: list[str] = []
    if value.get("schema_version") != "1.0":
        errors.append(f"{path}: schema_version must equal 1.0")
    if not isinstance(value.get("description"), str) or not value["description"].strip():
        errors.append(f"{path}: description must be non-empty")
    cases = value.get("cases")
    if not isinstance(cases, list) or len(cases) < 2:
        return errors + [f"{path}: cases must contain at least two cases"]
    seen: set[str] = set()
    for index, case in enumerate(cases, start=1):
        label = f"{path}: case {index}"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        required = {"id", "prompt", "expected_route", "risk", "assertions", "forbidden", "files"}
        missing = sorted(required - case.keys())
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
            continue
        identifier = case["id"]
        if not isinstance(identifier, str) or not CASE_ID.fullmatch(identifier):
            errors.append(f"{label} id must use lowercase kebab-case")
        elif identifier in seen:
            errors.append(f"{label} duplicate id")
        else:
            seen.add(identifier)
        if case["expected_route"] not in VALID_ROUTES:
            errors.append(f"{label} expected_route is invalid")
        if case["risk"] not in VALID_RISKS:
            errors.append(f"{label} risk is invalid")
        if not _strings(case["assertions"], 2):
            errors.append(f"{label} assertions must contain at least two strings")
        if not isinstance(case["forbidden"], list) or any(not isinstance(item, str) or not item.strip() for item in case["forbidden"]):
            errors.append(f"{label} forbidden must be a string array")
        if not _strings(case["files"]):
            errors.append(f"{label} files must contain at least one path")
        else:
            for filename in case["files"]:
                if not (skill / filename).is_file():
                    errors.append(f"{label} missing referenced file: {filename}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    paths = [args.path.resolve()] if args.path else sorted((skill / "assets" / "evals").glob("*.json"))
    errors: list[str] = []
    count = 0
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: {error}")
            continue
        errors.extend(validate_suite(value, path, skill))
        if isinstance(value, dict) and isinstance(value.get("cases"), list):
            count += len(value["cases"])
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"OK eval_suites={len(paths)} cases={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
