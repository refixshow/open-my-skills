"""Manage de-identified coach-development focus areas and resumable drills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


VERDICTS = {"baseline", "progress", "mixed", "no_progress", "regression", "insufficient_evidence"}
FOCUS_STATUSES = {"candidate", "active", "monitoring", "closed"}
DRILL_STATUSES = {"planned", "in_progress", "completed", "cancelled"}
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def default_path(root: Path) -> Path:
    return root.resolve() / ".coaching-supervision" / "coach-development.json"


def empty_log() -> dict[str, Any]:
    return {
        "version": 1,
        "tracking_enabled": True,
        "privacy": {
            "stores_client_data": False,
            "rule": "Store only de-identified coach behaviors and timestamp anchors.",
        },
        "focus_areas": [],
    }


def load_log(path: Path, create: bool = False) -> dict[str, Any]:
    if not path.is_file():
        if create:
            return empty_log()
        raise ValueError(f"Development log does not exist: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Development log root must be an object")
    return value


def validate_log(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("version") != 1:
        errors.append("version must equal 1")
    if not isinstance(value.get("tracking_enabled"), bool):
        errors.append("tracking_enabled must be boolean")
    privacy = value.get("privacy")
    if not isinstance(privacy, dict) or privacy.get("stores_client_data") is not False:
        errors.append("privacy.stores_client_data must equal false")
    focuses = value.get("focus_areas")
    if not isinstance(focuses, list):
        return errors + ["focus_areas must be an array"]
    active_count = 0
    seen_focuses: set[str] = set()
    seen_drills: set[str] = set()
    for index, focus in enumerate(focuses, start=1):
        label = f"focus_areas[{index}]"
        if not isinstance(focus, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = focus.get("id")
        if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
            errors.append(f"{label}.id must use lowercase kebab-case")
        elif identifier in seen_focuses:
            errors.append(f"{label}.id is duplicated")
        else:
            seen_focuses.add(identifier)
        if focus.get("status") not in FOCUS_STATUSES:
            errors.append(f"{label}.status is invalid")
        elif focus["status"] == "active":
            active_count += 1
        if focus.get("priority") not in {1, 2, 3}:
            errors.append(f"{label}.priority must be 1, 2, or 3")
        for field in ("label", "behavior_to_reduce", "target_behavior", "created"):
            if not isinstance(focus.get(field), str) or not focus[field].strip():
                errors.append(f"{label}.{field} must be non-empty")
        observations = focus.get("observations", [])
        if not isinstance(observations, list):
            errors.append(f"{label}.observations must be an array")
        else:
            for obs_index, observation in enumerate(observations, start=1):
                obs_label = f"{label}.observations[{obs_index}]"
                if not isinstance(observation, dict):
                    errors.append(f"{obs_label} must be an object")
                    continue
                if observation.get("verdict") not in VERDICTS:
                    errors.append(f"{obs_label}.verdict is invalid")
                evidence = observation.get("evidence")
                if not isinstance(evidence, list) or not evidence or any(
                    not isinstance(item, str) or not item.strip() for item in evidence
                ):
                    errors.append(f"{obs_label}.evidence must contain de-identified strings")
                for field in ("date", "session", "note"):
                    if not isinstance(observation.get(field), str) or not observation[field].strip():
                        errors.append(f"{obs_label}.{field} must be non-empty")
        drills = focus.get("drills", [])
        if not isinstance(drills, list):
            errors.append(f"{label}.drills must be an array")
        else:
            for drill_index, drill in enumerate(drills, start=1):
                drill_label = f"{label}.drills[{drill_index}]"
                if not isinstance(drill, dict):
                    errors.append(f"{drill_label} must be an object")
                    continue
                drill_id = drill.get("id")
                if not isinstance(drill_id, str) or not IDENTIFIER.fullmatch(drill_id):
                    errors.append(f"{drill_label}.id must use lowercase kebab-case")
                elif drill_id in seen_drills:
                    errors.append(f"{drill_label}.id is duplicated")
                else:
                    seen_drills.add(drill_id)
                if drill.get("status") not in DRILL_STATUSES:
                    errors.append(f"{drill_label}.status is invalid")
                prompts = drill.get("prompts")
                if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or any(
                    not isinstance(item, str) or not item.strip() for item in prompts
                ):
                    errors.append(f"{drill_label}.prompts must contain 1-3 strings")
                for field in ("date", "source_session", "name", "trigger", "portable_rule", "note"):
                    if not isinstance(drill.get(field), str) or not drill[field].strip():
                        errors.append(f"{drill_label}.{field} must be non-empty")
                next_index = drill.get("next_prompt_index", 0)
                if not isinstance(next_index, int) or next_index < 0:
                    errors.append(f"{drill_label}.next_prompt_index must be a non-negative integer")
    if active_count > 3:
        errors.append("at most three focus areas may be active")
    return errors


def save_log(path: Path, value: dict[str, Any]) -> None:
    errors = validate_log(value)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_focus(value: dict[str, Any], focus_id: str) -> dict[str, Any]:
    for focus in value["focus_areas"]:
        if focus["id"] == focus_id:
            return focus
    raise ValueError(f"Unknown focus id: {focus_id}")


def resolve_path(args: argparse.Namespace) -> Path:
    return args.path.resolve() if args.path else default_path(args.root)


def command_init(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    if path.exists() and not args.force:
        raise ValueError(f"Development log already exists: {path}")
    save_log(path, empty_log())
    print(path)


def command_validate(args: argparse.Namespace) -> None:
    errors = validate_log(load_log(resolve_path(args)))
    if errors:
        raise ValueError("; ".join(errors))
    print("OK development-log")


def command_summary(args: argparse.Namespace) -> None:
    value = load_log(resolve_path(args))
    errors = validate_log(value)
    if errors:
        raise ValueError("; ".join(errors))
    if args.json:
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return
    print(f"TRACKING_ENABLED={str(value['tracking_enabled']).lower()}")
    for focus in sorted(value["focus_areas"], key=lambda item: (item["priority"], item["id"])):
        latest = focus["observations"][-1]["verdict"] if focus["observations"] else "none"
        queued = sum(drill["status"] in {"planned", "in_progress"} for drill in focus["drills"])
        print(f"FOCUS id={focus['id']} status={focus['status']} priority={focus['priority']} latest={latest} queued={queued}")


def command_add_focus(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path, create=True)
    if any(focus.get("id") == args.id for focus in value["focus_areas"]):
        raise ValueError(f"Focus already exists: {args.id}")
    if args.status == "active" and sum(focus.get("status") == "active" for focus in value["focus_areas"]) >= 3:
        raise ValueError("At most three focus areas may be active")
    value["focus_areas"].append(
        {
            "id": args.id,
            "label": args.label,
            "status": args.status,
            "priority": args.priority,
            "behavior_to_reduce": args.reduce,
            "target_behavior": args.target,
            "created": args.date,
            "observations": [],
            "drills": [],
        }
    )
    value["focus_areas"].sort(key=lambda item: (item["priority"], item["id"]))
    save_log(path, value)


def command_observe(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    focus = find_focus(value, args.focus)
    focus["observations"].append(
        {
            "date": args.date,
            "session": args.session,
            "verdict": args.verdict,
            "evidence": args.evidence,
            "note": args.note,
        }
    )
    save_log(path, value)


def command_drill(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    focus = find_focus(value, args.focus)
    if any(drill.get("id") == args.id for area in value["focus_areas"] for drill in area.get("drills", [])):
        raise ValueError(f"Drill already exists: {args.id}")
    focus["drills"].append(
        {
            "id": args.id,
            "date": args.date,
            "source_session": args.source_session,
            "name": args.name,
            "status": args.status,
            "trigger": args.trigger,
            "prompts": args.prompt,
            "portable_rule": args.portable_rule,
            "note": args.note,
        }
    )
    save_log(path, value)


def _prompt_payload(focus: dict[str, Any], drill: dict[str, Any]) -> dict[str, Any]:
    index = drill.get("next_prompt_index", 0)
    return {
        "status": "in_progress",
        "focus_id": focus["id"],
        "drill_id": drill["id"],
        "drill_name": drill["name"],
        "prompt_number": index + 1,
        "prompt_count": len(drill["prompts"]),
        "prompt": drill["prompts"][index],
    }


def command_next_exercise(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    for desired in ("in_progress", "planned"):
        for focus in sorted(value["focus_areas"], key=lambda item: (item["priority"], item["id"])):
            if focus["status"] not in {"active", "monitoring"}:
                continue
            for drill in focus["drills"]:
                if drill["status"] != desired:
                    continue
                drill.setdefault("next_prompt_index", 0)
                if drill["next_prompt_index"] >= len(drill["prompts"]):
                    drill["status"] = "completed"
                    continue
                drill["status"] = "in_progress"
                save_log(path, value)
                print(json.dumps(_prompt_payload(focus, drill), ensure_ascii=False))
                return
    save_log(path, value)
    print(json.dumps({"status": "no_exercise"}))


def command_advance_exercise(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    focus = find_focus(value, args.focus)
    for drill in focus["drills"]:
        if drill["id"] != args.drill_id:
            continue
        if drill["status"] != "in_progress":
            raise ValueError(f"Drill is not in progress: {args.drill_id}")
        drill["next_prompt_index"] = drill.get("next_prompt_index", 0) + 1
        if drill["next_prompt_index"] >= len(drill["prompts"]):
            drill["status"] = "completed"
            save_log(path, value)
            print(json.dumps({"status": "completed", "focus_id": focus["id"], "drill_id": drill["id"]}))
            return
        save_log(path, value)
        print(json.dumps(_prompt_payload(focus, drill), ensure_ascii=False))
        return
    raise ValueError(f"Unknown drill id for focus {args.focus}: {args.drill_id}")


def command_set_focus_status(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    focus = find_focus(value, args.focus)
    if args.status == "active" and sum(
        item["status"] == "active" and item["id"] != args.focus for item in value["focus_areas"]
    ) >= 3:
        raise ValueError("At most three focus areas may be active")
    focus["status"] = args.status
    save_log(path, value)


def command_set_drill_status(args: argparse.Namespace) -> None:
    path = resolve_path(args)
    value = load_log(path)
    focus = find_focus(value, args.focus)
    for drill in focus["drills"]:
        if drill["id"] == args.drill_id:
            drill["status"] = args.status
            if args.note:
                drill["note"] = args.note
            save_log(path, value)
            return
    raise ValueError(f"Unknown drill id for focus {args.focus}: {args.drill_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--path", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=command_init)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.set_defaults(func=command_validate)

    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--json", action="store_true")
    summary_parser.set_defaults(func=command_summary)

    focus_parser = subparsers.add_parser("add-focus")
    focus_parser.add_argument("--id", required=True)
    focus_parser.add_argument("--label", required=True)
    focus_parser.add_argument("--target", required=True)
    focus_parser.add_argument("--reduce", required=True)
    focus_parser.add_argument("--priority", type=int, choices=(1, 2, 3), required=True)
    focus_parser.add_argument("--status", choices=sorted(FOCUS_STATUSES), default="active")
    focus_parser.add_argument("--date", default=date.today().isoformat())
    focus_parser.set_defaults(func=command_add_focus)

    observe_parser = subparsers.add_parser("observe")
    observe_parser.add_argument("--focus", required=True)
    observe_parser.add_argument("--date", required=True)
    observe_parser.add_argument("--session", required=True)
    observe_parser.add_argument("--verdict", choices=sorted(VERDICTS), required=True)
    observe_parser.add_argument("--evidence", action="append", required=True)
    observe_parser.add_argument("--note", required=True)
    observe_parser.set_defaults(func=command_observe)

    drill_parser = subparsers.add_parser("drill", aliases=["add-drill"])
    drill_parser.add_argument("--focus", required=True)
    drill_parser.add_argument("--id", required=True)
    drill_parser.add_argument("--date", required=True)
    drill_parser.add_argument("--source-session", required=True)
    drill_parser.add_argument("--name", required=True)
    drill_parser.add_argument("--status", choices=sorted(DRILL_STATUSES), default="planned")
    drill_parser.add_argument("--trigger", required=True)
    drill_parser.add_argument("--prompt", action="append", required=True)
    drill_parser.add_argument("--portable-rule", required=True)
    drill_parser.add_argument("--note", required=True)
    drill_parser.set_defaults(func=command_drill)

    next_parser = subparsers.add_parser("next-exercise")
    next_parser.set_defaults(func=command_next_exercise)

    advance_parser = subparsers.add_parser("advance-exercise")
    advance_parser.add_argument("--focus", required=True)
    advance_parser.add_argument("--drill-id", required=True)
    advance_parser.set_defaults(func=command_advance_exercise)

    focus_status_parser = subparsers.add_parser("set-focus-status", aliases=["set-status"])
    focus_status_parser.add_argument("--focus", required=True)
    focus_status_parser.add_argument("--status", choices=sorted(FOCUS_STATUSES), required=True)
    focus_status_parser.set_defaults(func=command_set_focus_status)

    drill_status_parser = subparsers.add_parser("set-drill-status")
    drill_status_parser.add_argument("--focus", required=True)
    drill_status_parser.add_argument("--drill-id", required=True)
    drill_status_parser.add_argument("--status", choices=sorted(DRILL_STATUSES), required=True)
    drill_status_parser.add_argument("--note")
    drill_status_parser.set_defaults(func=command_set_drill_status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
