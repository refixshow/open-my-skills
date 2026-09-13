"""Validate the two bundled, source-grounded coaching knowledge libraries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LIBRARIES = {
    "high-performance": {
        "cards": "sessions",
        "minimum": 11,
        "card_pattern": re.compile(r"^\d{2}-[a-z0-9-]+\.md$"),
        "required": ("catalog.md", "definitions.md", "report-contract.md", "source-manifest.md", "source-policy.md"),
    },
    "coaching-tools": {
        "cards": "topics",
        "minimum": 26,
        "card_pattern": re.compile(r"^\d{2}-[a-z0-9-]+\.md$"),
        "required": ("catalog.md", "report-contract.md", "source-manifest.md", "source-policy.md"),
    },
}


def validate_library(skill: Path, role: str) -> list[str]:
    config = LIBRARIES[role]
    root = skill / "references" / role
    errors: list[str] = []
    for filename in config["required"]:
        path = root / filename
        if not path.is_file():
            errors.append(f"{role}: missing {filename}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"{role}: empty {filename}")
    cards_dir = root / str(config["cards"])
    cards = sorted(cards_dir.glob("*.md"))
    if len(cards) < int(config["minimum"]):
        errors.append(f"{role}: expected at least {config['minimum']} cards, found {len(cards)}")
    for card in cards:
        if not config["card_pattern"].fullmatch(card.name):
            errors.append(f"{role}: invalid card filename {card.name}")
        text = card.read_text(encoding="utf-8")
        if not text.startswith("# "):
            errors.append(f"{role}: {card.name} needs an H1 title")
        if "## Evidence map" not in text:
            errors.append(f"{role}: {card.name} lacks Evidence map")
        if not re.search(r"\b(?:HP|T\d{2})-[A-Z0-9-]+", text):
            errors.append(f"{role}: {card.name} lacks a source identifier")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", choices=sorted(LIBRARIES))
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    roles = [args.library] if args.library else sorted(LIBRARIES)
    errors: list[str] = []
    for role in roles:
        errors.extend(validate_library(skill, role))
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    summary = ", ".join(
        f"{role}={len(list((skill / 'references' / role / str(LIBRARIES[role]['cards'])).glob('*.md')))}"
        for role in roles
    )
    print(f"OK knowledge {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
