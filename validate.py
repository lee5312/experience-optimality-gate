#!/usr/bin/env python3
"""Read-only structural EOG validation; never grants authority or certifies truth."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("record.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
SHAPE = Draft202012Validator(SCHEMA)
CATEGORIES = frozenset(SCHEMA["$defs"]["coverage"]["properties"]["category"]["enum"])
SECTIONS = ("experiences", "goals", "constraints", "checks", "sources",
            "candidates", "gaps", "implementation", "unknowns", "evidence")
MAX_RECORD_BYTES = 2 * 1024 * 1024  # Parsing limit, not an execution/research budget.


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_record(path: Path) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(MAX_RECORD_BYTES + 1)
    if len(raw) > MAX_RECORD_BYTES:
        raise ValueError("record exceeds the 2 MiB parsing limit")
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-JSON numeric constant: {value}")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                      parse_constant=reject_constant)


def validate_record(record: Any) -> list[str]:
    """Check shape, typed references, graph, scoped gap and claim consistency."""
    errors = [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
              for e in SHAPE.iter_errors(record)]
    if errors:
        return sorted(errors)
    counts = Counter(item["id"] for section in SECTIONS for item in record[section])
    errors.extend(f"duplicate id: {key}" for key, count in counts.items() if count > 1)
    if errors:
        return sorted(errors)
    index = {section: {item["id"]: item for item in record[section]} for section in SECTIONS}
    exp, goals, constraints = (index[s] for s in ("experiences", "goals", "constraints"))
    sources, candidates, gaps, checks = (index[s] for s in ("sources", "candidates", "gaps", "checks"))
    targets = exp.keys() | goals.keys() | constraints.keys()
    def refs(values: list[str], allowed: Any, label: str) -> None:
        errors.extend(f"{label}: unknown/wrong-type reference {value}" for value in values if value not in allowed)
    def source_refs(item: dict[str, Any], label: str) -> None:
        refs(item.get("source_ids", []), sources, label)
    def active(goal: dict[str, Any], candidate: str | None) -> bool:
        return not goal.get("applies_to") or candidate in goal["applies_to"]
    for goal in goals.values():
        refs(goal["supports"], exp.keys() | goals.keys(), goal["id"])
        refs(goal.get("applies_to", []), candidates, goal["id"])
    graph = {g["id"]: [p for p in g["supports"] if p in goals] for g in goals.values()}
    try:
        order = list(TopologicalSorter(graph).static_order())
    except CycleError:
        errors.append("goal graph: cycle")
        order = []
    for candidate_id in candidates:
        reachable: dict[str, bool] = {e: True for e in exp}
        for goal_id in order:
            goal = goals[goal_id]
            reachable[goal_id] = active(goal, candidate_id) and any(reachable.get(p, False) for p in goal["supports"])
            if active(goal, candidate_id) and not reachable[goal_id]:
                errors.append(f"{goal_id}: no active experience path for {candidate_id}")
    for source in sources.values():
        try:
            if datetime.fromisoformat(source["checked_at"]).tzinfo is None:
                raise ValueError("timezone missing")
        except ValueError:
            errors.append(f"{source['id']}: checked_at must include ISO date/time and timezone")
    for item in constraints.values():
        source_refs(item, item["id"])
    for check in checks.values():
        refs([check["target"]], targets, check["id"])
    checked_targets = {c["target"] for c in checks.values()}
    errors.extend(f"{target}: acceptance check missing" for target in targets - checked_targets)
    coverage = record["wheel_search"]["coverage"]
    if Counter(c["category"] for c in coverage) != Counter(CATEGORIES):
        errors.append("wheel_search: each search category must appear exactly once")
    for item in coverage:
        source_refs(item, "wheel_search." + item["category"])
        if item["status"] == "checked" and not item["source_ids"]:
            errors.append(f"wheel_search.{item['category']}: checked without source evidence")
    if not any(c["status"] == "checked" for c in coverage):
        errors.append("wheel_search: no actual inspection recorded")
    for candidate in candidates.values():
        cid = candidate["id"]
        source_refs(candidate, cid)
        refs(candidate["gap_ids"], gaps, cid)
        assessment_targets = [a["target"] for a in candidate["assessments"]]
        refs(assessment_targets, targets, cid)
        if len(assessment_targets) != len(set(assessment_targets)):
            errors.append(f"{cid}: duplicate target assessment")
        for assessment in candidate["assessments"]:
            source_refs(assessment, cid)
        if candidate["novel_parts"] and not candidate["gap_ids"]:
            errors.append(f"{cid}: novelty without gap justification")
        if candidate["kind"] == "new" and not candidate["novel_parts"]:
            errors.append(f"{cid}: new candidate must declare novel parts")
        if candidate["disposition"] == "dominated":
            if not candidate.get("dominated_by") or not candidate.get("dominance_basis"):
                errors.append(f"{cid}: unsupported dominance claim")
        refs(candidate.get("dominated_by", []), candidates, cid)
        if cid in candidate.get("dominated_by", []):
            errors.append(f"{cid}: cannot dominate itself")
    try:
        list(TopologicalSorter({cid: c.get("dominated_by", []) for cid, c in candidates.items()}).static_order())
    except CycleError:
        errors.append("dominance graph: cycle")
    for candidate in candidates.values():
        for gap_id in candidate["gap_ids"]:
            if gap_id in gaps and candidate["id"] in gaps[gap_id]["compared_candidates"]:
                errors.append(f"{candidate['id']}: gap must compare independent existing/no-change options, not itself")
    for gap in gaps.values():
        refs(gap["targets"], targets, gap["id"])
        refs(gap["compared_candidates"], candidates, gap["id"])
        source_refs(gap, gap["id"])
        known = [candidates[c] for c in gap["compared_candidates"] if c in candidates]
        if known and not any(c["kind"] != "new" for c in known):
            errors.append(f"{gap['id']}: comparison omits existing/no-change options")
    for element in index["implementation"].values():
        refs([element["candidate"]], candidates, element["id"])
        refs(element["supports"], targets, element["id"])
        refs(element["gap_ids"], gaps, element["id"])
        if element["novel"] and not element["gap_ids"]:
            errors.append(f"{element['id']}: novel element without a gap")
        candidate = candidates.get(element["candidate"])
        if candidate and any(t in goals and not active(goals[t], candidate["id"]) for t in element["supports"]):
            errors.append(f"{element['id']}: implementation supports a goal inactive for its candidate")
        if candidate and element["novel"] and (not candidate["novel_parts"] or not set(element["gap_ids"]) <= set(candidate["gap_ids"])):
            errors.append(f"{element['id']}: novelty not declared by its candidate")
    for unknown in index["unknowns"].values():
        source_refs(unknown, unknown["id"])
        if unknown["state"] == "resolved" and (not unknown["source_ids"] or not unknown.get("resolution")):
            errors.append(f"{unknown['id']}: resolved without evidence/rationale")
    refinement_parents: set[str] = set()
    for refinement in record["refinements"]:
        parent = refinement["parent"]
        refs([parent], exp.keys() | goals.keys(), "refinement")
        if parent in refinement_parents:
            errors.append(f"{parent}: duplicate refinement; combine alternatives")
        refinement_parents.add(parent)
        for conjunction in refinement["alternatives"]:
            refs(conjunction, goals, f"refinement {parent}")
            for child in conjunction:
                if child in goals and parent not in goals[child]["supports"]:
                    errors.append(f"{child}: refinement lacks supports edge to {parent}")
    decision = record["decision"]
    source_refs(decision, "decision")
    selected_id = decision["selected"]
    if selected_id is not None:
        refs([selected_id], candidates, "decision")
    selected = candidates.get(selected_id)
    needed = {e["id"] for e in exp.values() if e.get("priority", "required") == "required"} | constraints.keys() | {g["id"] for g in goals.values() if g["status"] == "required" and active(g, selected_id)}
    if decision["status"] == "design_pass":
        if selected is None or selected["disposition"] != "viable":
            errors.append("design_pass: selected viable candidate required")
        if any(u["decisive"] and u["state"] == "open" for u in record["unknowns"]):
            errors.append("design_pass: decisive unknown remains")
        if selected:
            fit = {a["target"]: a["fit"] for a in selected["assessments"]}
            errors.extend(f"design_pass: {t} missing or unmet/unknown" for t in needed if fit.get(t) not in ("expected", "met"))
            if selected["novel_parts"] and any(c["status"] == "unavailable" for c in coverage):
                errors.append("design_pass: novelty search has unavailable evidence")
            for refinement in record["refinements"]:
                if refinement["parent"] in needed and not any(all(c in goals and active(goals[c], selected_id) and fit.get(c) in ("expected", "met") for c in group) for group in refinement["alternatives"]):
                    errors.append(f"design_pass: no satisfied refinement alternative for {refinement['parent']}")
    latest: dict[str, tuple[datetime, str]] = {}
    for evidence in record["evidence"]:
        refs([evidence["check"]], checks, evidence["id"])
        try:
            when = datetime.fromisoformat(evidence["observed_at"])
            if when.tzinfo is None:
                raise ValueError("timezone missing")
        except ValueError:
            errors.append(f"{evidence['id']}: observed_at must include ISO date/time and timezone")
            continue
        if evidence["subject_revision"] != record["scope"]["subject_revision"]:
            continue
        prior = latest.get(evidence["check"])
        if prior and prior[0] == when and prior[1] != evidence["result"]:
            errors.append(f"{evidence['check']}: conflicting observations at the same time")
        if prior is None or when >= prior[0]:
            latest[evidence["check"]] = (when, evidence["result"])
    execution = record["execution"]
    if execution["outcome"] in ("success", "clean_noop"):
        if decision["status"] != "design_pass":
            errors.append("completion: design decision not ready")
        for check in checks.values():
            if check["target"] in needed and latest.get(check["id"], (None, None))[1] != "passed":
                errors.append(f"completion: current consumer/constraint/required-goal evidence missing or failed: {check['id']}")
        if execution["outcome"] == "clean_noop" and execution["changed"]:
            errors.append("clean_noop: cannot claim no change after a change")
    if execution.get("limit_source"):
        refs([execution["limit_source"]], sources, "execution.limit_source")
    if execution["outcome"] == "exhausted" and not execution.get("limit_source"):
        errors.append("exhausted: an actual supplied limit source is required")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = load_record(args.record)
        errors = validate_record(record)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(json.dumps({"structural_valid": False, "truth_verified": False, "errors": [str(exc)]}))
        return 2
    print(json.dumps({"structural_valid": not errors, "truth_verified": False,
                      "note": "Structure only; no authority, design PASS, or experience certification is issued.",
                      "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
