"""Validate Coaching Engine golden-path contracts and referenced files."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    skill = Path(__file__).resolve().parents[1]
    paths = sorted((skill / "assets" / "golden-paths").glob("*.json"))
    errors: list[str] = []
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: {error}")
            continue
        required = {"schema_version", "id", "trigger", "steps", "invariants", "files"}
        if not isinstance(value, dict) or not required.issubset(value):
            errors.append(f"{path}: missing golden-path fields")
            continue
        if value["schema_version"] != "1.0":
            errors.append(f"{path}: schema_version must equal 1.0")
        for field in ("steps", "invariants", "files"):
            items = value[field]
            if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
                errors.append(f"{path}: {field} must contain strings")
        for filename in value.get("files", []):
            if isinstance(filename, str) and not (skill / filename).is_file():
                errors.append(f"{path}: missing referenced file {filename}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"OK golden_paths={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
