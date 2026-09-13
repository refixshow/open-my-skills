"""Validate Coaching Engine lane payloads, route explicit requests, and gate tool candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROUTE_PATTERNS = [
    ("doctor", (r"\bdoctor\b", r"gotow", r"co dalej", r"status engine")),
    ("practice", (r"poćwicz", r"pocwicz", r"ćwiczeni", r"cwiczeni", r"next exercise")),
    ("progress", (r"progres", r"regres", r"porównaj z poprzed", r"compare.*previous")),
    ("forms", (r"arkusz", r"samoocen", r"self-evaluation", r"observation sheet")),
    ("hp-review", (r"tylko high performance", r"topic drift", r"zgodn.*high performance")),
    ("tool-review", (r"tylko narzędzi", r"tylko narzedzi", r"jakiego narzędzia", r"missed tool")),
    ("sources", (r"źród", r"zrodl", r"source corpus", r"validate.*source")),
    ("knowledge", (r"co oznacza", r"definicj", r"wyjaśnij.*sesj", r"explain.*tool")),
    ("check-session", (r"transkrypc", r"sprawdź sesj", r"sprawdz sesj", r"pełny check", r"pelny check", r"superwiz")),
]

CONFIDENCE = {"low", "medium", "high"}
TOPIC_SOURCE = {"declared", "inferred", "not-applicable"}
PRIORITIES = {"P1 - High Performance", "No action"}
FORM_FIELDS = {
    "productivity",
    "persuasion",
    "psychology",
    "physiology",
    "presence",
    "purpose",
    "notes",
    "follow_up",
}
SELF_EVAL_FIELDS = {
    "worked_best",
    "handled_well",
    "strongest_connection",
    "client_insight_signal",
    "more_value",
    "clearer_point",
    "enabling_question",
    "practice_behavior",
}
OUTCOME_FIELDS = {"clarity", "energy", "courage", "productivity", "influence"}
ADMISSION_FIELDS = {
    "explicit_signal",
    "serves_objective",
    "hp_ready",
    "brief_and_in_scope",
    "adds_value",
}


def route_text(text: str, transcript_supplied: bool = False) -> str:
    normalized = " ".join(text.lower().split())
    first = normalized.split(maxsplit=1)[0] if normalized else ""
    commands = {item[0] for item in ROUTE_PATTERNS}
    if first in commands:
        return first
    if transcript_supplied and not normalized:
        return "check-session"
    matches = [
        route
        for route, patterns in ROUTE_PATTERNS
        if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns)
    ]
    if len(set(matches)) == 1:
        return matches[0]
    if transcript_supplied:
        return "check-session"
    return "doctor" if not matches else "ambiguous"


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _blank_coach_response(value: Any) -> bool:
    return value is None or value == ""


def _string_list(value: Any, minimum: int = 0, maximum: int | None = None) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= minimum
        and (maximum is None or len(value) <= maximum)
        and all(_non_empty_string(item) for item in value)
    )


def _unwrap(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, dict) and key in value else value


def validate_hp(value: Any) -> list[str]:
    value = _unwrap(value, "HP_RESULT")
    if not isinstance(value, dict):
        return ["HP_RESULT must be an object"]
    errors: list[str] = []
    for field in ("topic", "transcript_reliability", "overall_verdict", "topic_discipline"):
        if not _non_empty_string(value.get(field)):
            errors.append(f"HP_RESULT.{field} must be a non-empty string")
    if value.get("topic_source") not in TOPIC_SOURCE:
        errors.append("HP_RESULT.topic_source is invalid")
    if value.get("topic_confidence") not in CONFIDENCE:
        errors.append("HP_RESULT.topic_confidence is invalid")
    if not _string_list(value.get("strengths"), 2, 4):
        errors.append("HP_RESULT.strengths must contain 2-4 strings")
    findings = value.get("findings")
    if not isinstance(findings, list) or not 2 <= len(findings) <= 5:
        errors.append("HP_RESULT.findings must contain 2-5 findings")
    else:
        required = {"moment", "observation", "interpretation", "source_basis", "priority", "confidence"}
        for index, finding in enumerate(findings, start=1):
            if not isinstance(finding, dict):
                errors.append(f"HP_RESULT.findings[{index}] must be an object")
                continue
            for field in required - {"priority", "confidence"}:
                if not _non_empty_string(finding.get(field)):
                    errors.append(f"HP_RESULT.findings[{index}].{field} must be non-empty")
            if finding.get("priority") not in PRIORITIES:
                errors.append(f"HP_RESULT.findings[{index}].priority is invalid")
            if finding.get("confidence") not in CONFIDENCE:
                errors.append(f"HP_RESULT.findings[{index}].confidence is invalid")
    if not isinstance(value.get("safety_flags"), list):
        errors.append("HP_RESULT.safety_flags must be an array")
    return errors


def validate_tools(value: Any) -> list[str]:
    value = _unwrap(value, "TOOLS_CANDIDATES")
    if not isinstance(value, list):
        return ["TOOLS_CANDIDATES must be an array"]
    if len(value) > 5:
        return ["TOOLS_CANDIDATES may contain at most five candidates"]
    errors: list[str] = []
    seen: set[str] = set()
    required = {
        "id",
        "moment",
        "client_signal",
        "tool_id",
        "rationale",
        "intervention",
        "simpler_alternative",
        "source_basis",
        "confidence",
        "hp_dependency",
        "admission_test",
    }
    for index, candidate in enumerate(value, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"TOOLS_CANDIDATES[{index}] must be an object")
            continue
        missing = sorted(required - candidate.keys())
        if missing:
            errors.append(f"TOOLS_CANDIDATES[{index}] missing: {', '.join(missing)}")
            continue
        for field in required - {"confidence", "admission_test"}:
            if not _non_empty_string(candidate.get(field)):
                errors.append(f"TOOLS_CANDIDATES[{index}].{field} must be non-empty")
        identifier = candidate.get("id")
        if identifier in seen:
            errors.append(f"TOOLS_CANDIDATES[{index}].id is duplicated")
        elif isinstance(identifier, str):
            seen.add(identifier)
        if candidate.get("confidence") not in CONFIDENCE:
            errors.append(f"TOOLS_CANDIDATES[{index}].confidence is invalid")
        admission = candidate.get("admission_test")
        if not isinstance(admission, dict) or set(admission) != ADMISSION_FIELDS:
            errors.append(f"TOOLS_CANDIDATES[{index}].admission_test must contain the five gate fields")
        elif any(not isinstance(admission[field], bool) for field in ADMISSION_FIELDS):
            errors.append(f"TOOLS_CANDIDATES[{index}].admission_test values must be booleans")
    return errors


def validate_forms(value: Any) -> list[str]:
    value = _unwrap(value, "FORMS_DRAFT")
    if not isinstance(value, dict):
        return ["FORMS_DRAFT must be an object"]
    errors: list[str] = []
    if not _non_empty_string(value.get("context_note")):
        errors.append("FORMS_DRAFT.context_note must be non-empty")
    client = value.get("client_observation")
    if not isinstance(client, dict) or set(client) != FORM_FIELDS:
        errors.append("FORMS_DRAFT.client_observation must contain all eight fields")
    elif any(not _non_empty_string(client[field]) for field in FORM_FIELDS):
        errors.append("FORMS_DRAFT.client_observation fields must be non-empty")
    self_eval = value.get("coach_self_evaluation")
    if not isinstance(self_eval, dict) or set(self_eval) != SELF_EVAL_FIELDS:
        errors.append("FORMS_DRAFT.coach_self_evaluation must contain all eight prompts")
    else:
        for field in SELF_EVAL_FIELDS:
            item = self_eval[field]
            if not isinstance(item, dict) or set(item) != {"prompt", "response"}:
                errors.append(f"FORMS_DRAFT.coach_self_evaluation.{field} has invalid fields")
                continue
            if not _non_empty_string(item.get("prompt")):
                errors.append(f"FORMS_DRAFT.coach_self_evaluation.{field}.prompt must be non-empty")
            if not _blank_coach_response(item.get("response")):
                errors.append(f"FORMS_DRAFT.coach_self_evaluation.{field}.response must remain blank")
    outcomes = value.get("outcomes")
    if not isinstance(outcomes, dict) or set(outcomes) != OUTCOME_FIELDS:
        errors.append("FORMS_DRAFT.outcomes must contain five dimensions")
    else:
        for field in OUTCOME_FIELDS:
            item = outcomes[field]
            if not isinstance(item, dict) or set(item) != {"prompt", "response", "rating"}:
                errors.append(f"FORMS_DRAFT.outcomes.{field} has invalid fields")
                continue
            if not _non_empty_string(item.get("prompt")):
                errors.append(f"FORMS_DRAFT.outcomes.{field}.prompt must be non-empty")
            if not _blank_coach_response(item.get("response")):
                errors.append(f"FORMS_DRAFT.outcomes.{field}.response must remain blank")
            if item.get("rating") not in {None, "__/10"}:
                errors.append(f"FORMS_DRAFT.outcomes.{field}.rating must remain blank")
    return errors


VALIDATORS = {"hp": validate_hp, "tools": validate_tools, "forms": validate_forms}


def hp_digest(value: Any) -> str:
    payload = _unwrap(value, "HP_RESULT")
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def gate(hp: Any, tools: Any) -> dict[str, Any]:
    errors = validate_hp(hp) + validate_tools(tools)
    if errors:
        raise ValueError("; ".join(errors))
    candidates = _unwrap(tools, "TOOLS_CANDIDATES")
    admitted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for candidate in candidates:
        failed = [field for field in sorted(ADMISSION_FIELDS) if not candidate["admission_test"][field]]
        if failed:
            rejected.append({"id": candidate["id"], "reasons": failed})
        elif len(admitted) < 3:
            admitted.append(candidate)
        else:
            rejected.append({"id": candidate["id"], "reasons": ["maximum-three-admitted"]})
    return {
        "hp_result_digest": hp_digest(hp),
        "hp_result_frozen": True,
        "admitted": admitted,
        "rejected": rejected,
    }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("text")
    route_parser.add_argument("--transcript-supplied", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("kind", choices=sorted(VALIDATORS))
    validate_parser.add_argument("path", type=Path)

    gate_parser = subparsers.add_parser("gate")
    gate_parser.add_argument("--hp", type=Path, required=True)
    gate_parser.add_argument("--tools", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "route":
        print(route_text(args.text, args.transcript_supplied))
        return 0
    if args.command == "validate":
        try:
            value = _read_json(args.path)
        except (OSError, json.JSONDecodeError) as error:
            print(f"ERROR {error}")
            return 1
        errors = VALIDATORS[args.kind](value)
        if errors:
            for error in errors:
                print(f"ERROR {error}")
            return 1
        print(f"OK {args.kind}")
        return 0
    try:
        result = gate(_read_json(args.hp), _read_json(args.tools))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
