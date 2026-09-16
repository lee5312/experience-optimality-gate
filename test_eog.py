"""Structural regression tests, not an evaluation of agent decision quality."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate import load_record, validate_record

ROOT = Path(__file__).resolve().parent
EXAMPLE = json.loads((ROOT / "example.json").read_text(encoding="utf-8"))


def add_observations(record: dict, checks: list[str] | None = None) -> None:
    for check in checks or [c["id"] for c in record["checks"]]:
        record["evidence"].append({
            "id": "V" + check,
            "check": check,
            "subject_revision": record["scope"]["subject_revision"],
            "observed_at": "2026-09-16T01:00:00+00:00",
            "locator": "fixture://observations/" + check,
            "result": "passed",
            "observation": "Synthetic test observation, not live host evidence.",
        })


def novel_record() -> dict:
    r = deepcopy(EXAMPLE)
    candidate = r["candidates"][1]
    candidate.update(kind="adapt", novel_parts=["Fixture-specific argument mapping"], gap_ids=["N1"])
    r["gaps"] = [{
        "id": "N1", "targets": ["E1"], "compared_candidates": ["W0"],
        "source_ids": ["R2"], "residual": "Synthetic existing interface lacks the fixture mapping.",
        "why_not_adapt": "Configuration alone cannot map this field; adaptation is the selected option.",
        "minimum_novelty": "Only the argument mapping, not the underlying transformation.",
    }]
    r["implementation"] = [{
        "id": "I1", "description": "Fixture argument mapping", "candidate": "W1",
        "supports": ["G1"], "novel": True, "gap_ids": ["N1"],
    }]
    return r


class EogRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = deepcopy(EXAMPLE)

    def assertInvalid(self, fragment: str, record: dict | None = None) -> None:
        errors = validate_record(self.record if record is None else record)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_example_is_valid_and_unexecuted(self) -> None:
        self.assertEqual(validate_record(self.record), [])
        self.assertEqual(self.record["execution"]["outcome"], "not_started")
        self.assertEqual(self.record["evidence"], [])

    def test_validation_does_not_mutate_input(self) -> None:
        before = deepcopy(self.record)
        validate_record(self.record)
        self.assertEqual(self.record, before)

    def test_all_consumer_kinds_are_supported(self) -> None:
        for kind in ("human", "agent", "program", "service", "device", "other"):
            with self.subTest(kind=kind):
                self.record["experiences"][0]["actor"]["kind"] = kind
                self.assertEqual(validate_record(self.record), [])

    def test_unknown_fields_fail(self) -> None:
        self.record["gate_pass"] = True
        self.assertInvalid("Additional properties")

    def test_missing_experience_fails(self) -> None:
        self.record["experiences"] = []
        self.assertInvalid("experiences")

    def test_blank_experience_is_not_a_target(self) -> None:
        self.record["experiences"][0]["target"] = "   "
        self.assertInvalid("target")

    def test_duplicate_id_across_entity_types_fails(self) -> None:
        self.record["goals"][0]["id"] = "E1"
        self.assertInvalid("duplicate id")

    def test_unknown_goal_parent_fails(self) -> None:
        self.record["goals"][0]["supports"] = ["Gmissing"]
        self.assertInvalid("unknown/wrong-type")

    def test_constraint_is_not_an_experience_root(self) -> None:
        self.record["goals"][0]["supports"] = ["C1"]
        self.assertInvalid("unknown/wrong-type")

    def test_cycle_fails(self) -> None:
        self.record["goals"][0]["supports"] = ["G1"]
        self.assertInvalid("goal graph: cycle")

    def test_goal_requires_acceptance_check(self) -> None:
        self.record["checks"] = [c for c in self.record["checks"] if c["target"] != "G1"]
        self.assertInvalid("G1: acceptance check missing")

    def test_root_requires_acceptance_check(self) -> None:
        self.record["checks"] = [c for c in self.record["checks"] if c["target"] != "E1"]
        self.assertInvalid("E1: acceptance check missing")

    def test_constraint_requires_real_source_reference(self) -> None:
        self.record["constraints"][0]["source_ids"] = ["E1"]
        self.assertInvalid("unknown/wrong-type")

    def test_scoped_goals_do_not_bind_other_candidates(self) -> None:
        g = deepcopy(self.record["goals"][0])
        g.update(id="G2", applies_to=["W0"])
        self.record["goals"].append(g)
        self.record["checks"].append({"id": "A4", "target": "G2", "method": "Fixture check", "pass_condition": "Fixture condition"})
        self.assertEqual(validate_record(self.record), [])

    def test_scoped_path_cannot_hide_orphan(self) -> None:
        self.record["goals"][0]["applies_to"] = ["W0"]
        g = deepcopy(self.record["goals"][0])
        g.update(id="G2", supports=["G1"], applies_to=["W1"])
        self.record["goals"].append(g)
        self.record["checks"].append({"id": "A4", "target": "G2", "method": "Fixture check", "pass_condition": "Fixture condition"})
        self.assertInvalid("no active experience path for W1")

    def test_refinement_requires_real_edge(self) -> None:
        self.record["refinements"] = [{"parent": "G1", "alternatives": [["G1"]], "why": "Fixture"}]
        self.assertInvalid("refinement lacks supports edge")

    def test_or_of_and_refinement_is_supported(self) -> None:
        g = deepcopy(self.record["goals"][0])
        g.update(id="G2", applies_to=["W0"])
        self.record["goals"].append(g)
        self.record["checks"].append({"id": "A4", "target": "G2", "method": "Fixture check", "pass_condition": "Fixture condition"})
        self.record["refinements"] = [{"parent": "E1", "alternatives": [["G1"], ["G2"]], "why": "Alternative fixture derivations"}]
        self.assertEqual(validate_record(self.record), [])

    def test_unsatisfied_refinement_fails(self) -> None:
        self.record["goals"][0]["status"] = "provisional"
        self.record["candidates"][1]["assessments"][1]["fit"] = "unmet"
        self.record["refinements"] = [{"parent": "E1", "alternatives": [["G1"]], "why": "Only fixture derivation"}]
        self.assertInvalid("no satisfied refinement alternative")

    def test_missing_wheel_category_fails(self) -> None:
        self.record["wheel_search"]["coverage"].pop()
        self.assertInvalid("coverage")

    def test_duplicate_category_cannot_fill_missing_search(self) -> None:
        self.record["wheel_search"]["coverage"][-1] = deepcopy(self.record["wheel_search"]["coverage"][0])
        self.assertInvalid("each search category")

    def test_search_category_list_is_not_evidence(self) -> None:
        self.record["wheel_search"]["coverage"][0]["source_ids"] = []
        self.assertInvalid("checked without source evidence")

    def test_all_not_applicable_is_not_a_search(self) -> None:
        for c in self.record["wheel_search"]["coverage"]:
            c["status"] = "not_applicable"
        self.assertInvalid("no actual inspection")

    def test_unknown_wheel_source_fails(self) -> None:
        self.record["wheel_search"]["coverage"][0]["source_ids"] = ["Rmissing"]
        self.assertInvalid("unknown/wrong-type")

    def test_unavailable_search_cannot_justify_novelty(self) -> None:
        r = novel_record()
        r["wheel_search"]["coverage"][0]["status"] = "unavailable"
        self.assertInvalid("novelty search has unavailable evidence", r)

    def test_novelty_requires_gap(self) -> None:
        self.record["candidates"][1]["novel_parts"] = ["New glue"]
        self.assertInvalid("novelty without gap")

    def test_new_candidate_must_declare_novelty(self) -> None:
        self.record["candidates"][1]["kind"] = "new"
        self.assertInvalid("must declare novel parts")

    def test_adaptation_with_scoped_gap_is_valid(self) -> None:
        self.assertEqual(validate_record(novel_record()), [])

    def test_no_circular_self_comparison_as_gap(self) -> None:
        r = novel_record()
        r["gaps"][0]["compared_candidates"] = ["W1"]
        self.assertInvalid("not itself", r)

    def test_gap_must_compare_existing_or_noop(self) -> None:
        r = novel_record()
        r["candidates"][0].update(kind="new", novel_parts=["Other new plan"], gap_ids=["N1"])
        self.assertInvalid("comparison omits existing/no-change", r)

    def test_gap_needs_source_reference(self) -> None:
        r = novel_record()
        r["gaps"][0]["source_ids"] = []
        self.assertInvalid("source_ids", r)

    def test_implementation_cannot_hide_novelty(self) -> None:
        r = novel_record()
        r["candidates"][1]["novel_parts"] = []
        self.assertInvalid("novelty not declared by its candidate", r)

    def test_novel_element_requires_gap(self) -> None:
        r = novel_record()
        r["implementation"][0]["gap_ids"] = []
        self.assertInvalid("novel element without a gap", r)

    def test_implementation_must_trace_to_valid_target(self) -> None:
        r = novel_record()
        r["implementation"][0]["supports"] = ["R1"]
        self.assertInvalid("unknown/wrong-type", r)

    def test_dominance_needs_basis(self) -> None:
        self.record["candidates"][0]["disposition"] = "dominated"
        self.assertInvalid("unsupported dominance")

    def test_dominance_cycle_fails(self) -> None:
        self.record["candidates"][0]["dominated_by"] = ["W1"]
        self.record["candidates"][1]["dominated_by"] = ["W0"]
        self.assertInvalid("dominance graph: cycle")

    def test_design_requires_selected_viable_candidate(self) -> None:
        self.record["decision"]["selected"] = None
        self.assertInvalid("selected viable candidate required")

    def test_failed_experience_blocks_design(self) -> None:
        self.record["candidates"][1]["assessments"][0]["fit"] = "unmet"
        self.assertInvalid("E1 missing or unmet/unknown")

    def test_failed_constraint_blocks_design(self) -> None:
        self.record["candidates"][1]["assessments"][2]["fit"] = "unmet"
        self.assertInvalid("C1 missing or unmet/unknown")

    def test_preference_is_not_hard_requirement(self) -> None:
        e = deepcopy(self.record["experiences"][0])
        e.update(id="E2", priority="preference")
        self.record["experiences"].append(e)
        self.record["checks"].append({"id": "A4", "target": "E2", "method": "Fixture check", "pass_condition": "Preferred, not mandatory"})
        self.assertEqual(validate_record(self.record), [])

    def test_decisive_unknown_blocks_design(self) -> None:
        self.record["unknowns"] = [{"id": "U1", "question": "Is the nearest wheel sufficient?", "decisive": True, "state": "open", "source_ids": []}]
        self.assertInvalid("decisive unknown remains")

    def test_provisional_decision_can_hold_unknown(self) -> None:
        self.record["decision"].update(status="provisional", selected=None)
        self.record["unknowns"] = [{"id": "U1", "question": "Unknown fit", "decisive": True, "state": "open", "source_ids": []}]
        self.record["execution"].update(outcome="blocked", reason="Evidence unavailable")
        self.assertEqual(validate_record(self.record), [])

    def test_resolved_unknown_requires_evidence(self) -> None:
        self.record["unknowns"] = [{"id": "U1", "question": "Unknown fit", "decisive": True, "state": "resolved", "source_ids": []}]
        self.assertInvalid("resolved without evidence")

    def test_design_pass_is_not_completion(self) -> None:
        self.record["execution"]["outcome"] = "success"
        self.assertInvalid("current consumer/constraint/required-goal evidence")

    def test_component_only_success_cannot_close_experience(self) -> None:
        add_observations(self.record, ["A2", "A3"])
        self.record["execution"]["outcome"] = "success"
        self.assertInvalid("missing or failed: A1")

    def test_current_root_and_constraints_allow_completion_claim_structure(self) -> None:
        add_observations(self.record)
        self.record["execution"]["outcome"] = "success"
        self.assertEqual(validate_record(self.record), [])

    def test_old_revision_does_not_prove_completion(self) -> None:
        add_observations(self.record)
        self.record["scope"]["subject_revision"] = "fixture-v2"
        self.record["execution"]["outcome"] = "success"
        self.assertInvalid("current consumer/constraint/required-goal evidence")

    def test_latest_failure_wins_regardless_of_input_order(self) -> None:
        add_observations(self.record)
        newer = deepcopy(self.record["evidence"][0])
        newer.update(id="Vlater", observed_at="2026-09-16T02:00:00Z", result="failed")
        self.record["evidence"].insert(0, newer)
        self.record["execution"]["outcome"] = "success"
        self.assertInvalid("missing or failed: A1")

    def test_same_time_conflicting_observations_fail(self) -> None:
        add_observations(self.record)
        conflict = deepcopy(self.record["evidence"][0])
        conflict.update(id="Vconflict", result="failed")
        self.record["evidence"].append(conflict)
        self.assertInvalid("conflicting observations")

    def test_evidence_needs_timezone(self) -> None:
        add_observations(self.record)
        self.record["evidence"][0]["observed_at"] = "2026-09-16T02:00:00"
        self.assertInvalid("observed_at must include")

    def test_source_needs_timezone(self) -> None:
        self.record["sources"][0]["checked_at"] = "yesterday"
        self.assertInvalid("checked_at must include")

    def test_clean_noop_cannot_have_changed_state(self) -> None:
        add_observations(self.record)
        self.record["execution"].update(outcome="clean_noop", changed=True)
        self.assertInvalid("cannot claim no change")

    def test_approval_required_is_not_success(self) -> None:
        self.record["execution"].update(outcome="approval_required", reason="Missing external action authority")
        self.assertEqual(validate_record(self.record), [])

    def test_exhausted_requires_supplied_limit(self) -> None:
        self.record["execution"]["outcome"] = "exhausted"
        self.assertInvalid("actual supplied limit source")

    def test_exhausted_limit_must_reference_a_source(self) -> None:
        self.record["execution"].update(outcome="exhausted", limit_source="Rmissing")
        self.assertInvalid("execution.limit_source")


class EogInputTests(unittest.TestCase):
    def test_duplicate_json_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text('{"decision": false, "decision": true}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_record(path)

    def test_non_json_nan_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text('{"value": NaN}')
            with self.assertRaisesRegex(ValueError, "non-JSON"):
                load_record(path)

    def test_cli_is_read_only_and_never_certifies_truth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text(json.dumps(EXAMPLE))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "validate.py"), str(path)], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertTrue(output["structural_valid"])
            self.assertFalse(output["truth_verified"])
            self.assertNotIn("design_pass", output)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_missing_input_returns_nonzero_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(ROOT / "validate.py"), str(Path(tmp) / "absent.json")], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads(result.stdout)["structural_valid"])
            self.assertFalse(json.loads(result.stdout)["truth_verified"])
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
