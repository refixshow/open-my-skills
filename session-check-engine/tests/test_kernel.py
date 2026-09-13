from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from kernel import gate, hp_digest, route_text, validate_forms, validate_hp, validate_tools  # noqa: E402


def hp_result() -> dict:
    finding = {
        "moment": "10:00",
        "observation": "Coach paraphrased and asked for confirmation.",
        "interpretation": "The move preserved client meaning.",
        "source_basis": "HP-S00 PDF p.2",
        "priority": "No action",
        "confidence": "high",
    }
    return {
        "topic": "S00 Strategy",
        "topic_source": "declared",
        "topic_confidence": "high",
        "transcript_reliability": "Complete with reliable speakers and timestamps.",
        "overall_verdict": "The session substantially served its intended function.",
        "strengths": ["Clear contract", "Faithful paraphrase"],
        "findings": [finding, {**finding, "moment": "20:00"}],
        "topic_discipline": "The session stayed on its primary axis.",
        "safety_flags": [],
    }


def tool_candidate(identifier: str, **gate_values: bool) -> dict:
    admission = {
        "explicit_signal": True,
        "serves_objective": True,
        "hp_ready": True,
        "brief_and_in_scope": True,
        "adds_value": True,
    }
    admission.update(gate_values)
    return {
        "id": identifier,
        "moment": "22:00",
        "client_signal": "The client named a vague outcome.",
        "tool_id": "T05",
        "rationale": "A brief definition could make the action observable.",
        "intervention": "What would you notice if this were working?",
        "simpler_alternative": "Reflect the client's phrase and wait.",
        "source_basis": "T05 PDF p.3",
        "confidence": "medium",
        "hp_dependency": "The current session purpose is already contracted.",
        "admission_test": admission,
    }


def forms_draft() -> dict:
    absent = "not discussed in the reviewed transcript"
    client = {
        "productivity": absent,
        "persuasion": absent,
        "psychology": absent,
        "physiology": absent,
        "presence": absent,
        "purpose": absent,
        "notes": "The client clarified one desired outcome at 12:00.",
        "follow_up": absent,
    }
    self_eval = {
        field: {"prompt": "Coach-owned first-person reflection prompt.", "response": None}
        for field in (
            "worked_best",
            "handled_well",
            "strongest_connection",
            "client_insight_signal",
            "more_value",
            "clearer_point",
            "enabling_question",
            "practice_behavior",
        )
    }
    outcome = {
        "prompt": "How did I experience my coaching in this dimension?",
        "response": None,
        "rating": "__/10",
    }
    return {
        "context_note": "Complete text transcript; vocal qualities unavailable.",
        "client_observation": client,
        "coach_self_evaluation": self_eval,
        "outcomes": {name: copy.deepcopy(outcome) for name in ("clarity", "energy", "courage", "productivity", "influence")},
    }


class RoutingTests(unittest.TestCase):
    def test_transcript_alone_routes_to_complete_check(self) -> None:
        self.assertEqual("check-session", route_text("", transcript_supplied=True))

    def test_explicit_narrow_routes_win(self) -> None:
        self.assertEqual("hp-review", route_text("Tylko High Performance: sprawdź zgodność sesji"))
        self.assertEqual("practice", route_text("Poćwiczmy teraz ten fokus"))


class PayloadValidationTests(unittest.TestCase):
    def test_valid_payloads_pass(self) -> None:
        self.assertEqual([], validate_hp(hp_result()))
        self.assertEqual([], validate_tools([tool_candidate("candidate-1")]))
        self.assertEqual([], validate_forms(forms_draft()))

    def test_numeric_self_rating_is_rejected(self) -> None:
        value = forms_draft()
        value["outcomes"]["clarity"]["rating"] = "8/10"
        self.assertTrue(any("must remain blank" in error for error in validate_forms(value)))

    def test_prefilled_private_coach_reflection_is_rejected(self) -> None:
        value = forms_draft()
        value["coach_self_evaluation"]["worked_best"]["response"] = "The transcript suggests I felt connected."
        value["outcomes"]["energy"]["response"] = "I had high energy."
        errors = validate_forms(value)
        self.assertEqual(2, sum("response must remain blank" in error for error in errors))

    def test_legacy_transcript_evidence_outcome_is_rejected(self) -> None:
        value = forms_draft()
        value["outcomes"]["clarity"] = {
            "evidence": "Transcript evidence.",
            "counterevidence": "Transcript counterevidence.",
            "reflection_question": "How did this go?",
            "rating": "__/10",
        }
        self.assertTrue(any("has invalid fields" in error for error in validate_forms(value)))


class PriorityGateTests(unittest.TestCase):
    def test_gate_freezes_hp_and_rejects_failed_candidate(self) -> None:
        hp = hp_result()
        tools = [tool_candidate("admit"), tool_candidate("reject", hp_ready=False)]
        result = gate(hp, tools)
        self.assertTrue(result["hp_result_frozen"])
        self.assertEqual(hp_digest(hp), result["hp_result_digest"])
        self.assertEqual(["admit"], [item["id"] for item in result["admitted"]])
        self.assertEqual(["hp_ready"], result["rejected"][0]["reasons"])

    def test_gate_admits_at_most_three(self) -> None:
        tools = [tool_candidate(f"candidate-{index}") for index in range(4)]
        result = gate(hp_result(), tools)
        self.assertEqual(3, len(result["admitted"]))
        self.assertEqual(["maximum-three-admitted"], result["rejected"][0]["reasons"])

    def test_hp_digest_changes_after_material_edit(self) -> None:
        first = hp_result()
        second = copy.deepcopy(first)
        second["overall_verdict"] = "Changed verdict"
        self.assertNotEqual(hp_digest(first), hp_digest(second))


if __name__ == "__main__":
    unittest.main()
