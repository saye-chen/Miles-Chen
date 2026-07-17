#!/usr/bin/env python3
"""Validate report lineage, current state, rebase integrity, actions and depth monotonicity."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "references/report-lineage-schema.json").read_text(encoding="utf-8"))
CHANGE = set(SCHEMA["change_classes"]); STATUSES = set(SCHEMA["report_statuses"]); ACTIONS = set(SCHEMA["action_statuses"])
REPORT_FIELDS = set(SCHEMA["required_report_fields"]); STATE_FIELDS = set(SCHEMA["required_current_state_fields"])
ACTIVE = {"planned", "approved", "committed", "in_progress", "irreversible", "paused", "recovery_required"}
DEPTH_FIELDS = {"decisive_modules", "evidence_count", "counterevidence_count", "assumption_count", "calculation_count", "action_contract_count"}

def nonempty(value: object) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value) if isinstance(value, (list, dict)) else value is not None

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(bundle: dict, base_dir: Path | None = None) -> list[str]:
    errors: list[str] = []; base_dir = base_dir or Path.cwd()
    objects = bundle.get("objects", []); reports = bundle.get("reports", []); states = bundle.get("current_states", [])
    if not isinstance(objects, list) or not isinstance(reports, list) or not isinstance(states, list):
        return ["objects, reports and current_states must be lists"]
    object_by_id = {x.get("object_id"): x for x in objects if isinstance(x, dict) and x.get("object_id")}
    if len(object_by_id) != len(objects): errors.append("object ids must be present and unique")
    report_by_id = {x.get("report_id"): x for x in reports if isinstance(x, dict) and x.get("report_id")}
    if len(report_by_id) != len(reports): errors.append("report ids must be present and unique")
    state_by_object = {x.get("object_id"): x for x in states if isinstance(x, dict) and x.get("object_id")}
    if len(state_by_object) != len(states): errors.append("current state object ids must be present and unique")

    for obj_id, obj in object_by_id.items():
        if obj.get("parent_object_id") and obj["parent_object_id"] not in object_by_id: errors.append(f"object {obj_id} has unknown parent")
        for child in obj.get("child_object_ids", []):
            if child not in object_by_id: errors.append(f"object {obj_id} references unknown child {child}")

    parents: dict[str, list[str]] = {}
    for rid, report in report_by_id.items():
        missing = sorted(REPORT_FIELDS - set(report));
        if missing: errors.append(f"report {rid} missing fields: {missing}")
        if report.get("object_id") not in object_by_id: errors.append(f"report {rid} references unknown object")
        if report.get("status") not in STATUSES: errors.append(f"report {rid} has invalid status")
        if report.get("change_class") not in CHANGE: errors.append(f"report {rid} has invalid change_class")
        parent_ids = report.get("parent_report_ids", []); parents[rid] = parent_ids if isinstance(parent_ids, list) else []
        if not isinstance(parent_ids, list): errors.append(f"report {rid} parent_report_ids must be a list")
        for parent in parents[rid]:
            if parent not in report_by_id: errors.append(f"report {rid} has unknown parent {parent}")
            elif report_by_id[parent].get("object_id") != report.get("object_id") and report.get("change_class") != "New Decision Object":
                errors.append(f"report {rid} crosses objects without New Decision Object")
        if len(parents[rid]) > 1 and not nonempty(report.get("conflict_resolution")):
            errors.append(f"merge report {rid} requires conflict_resolution")
        impact = report.get("impact_set", {})
        if report.get("change_class") in {"Revision", "Recalculation", "Rebase", "New Decision Object", "Correction", "Consolidation"}:
            for field in ("recalculate", "review", "inherit", "unaffected"):
                if not isinstance(impact, dict) or not isinstance(impact.get(field), list): errors.append(f"report {rid} impact_set.{field} is required")
        transition = report.get("transition_matrix", [])
        if report.get("change_class") not in {"Addendum"} and not transition: errors.append(f"report {rid} requires transition_matrix")
        if report.get("change_class") == "New Decision Object" and report.get("inherited_conclusion_ids"):
            errors.append(f"new decision object report {rid} cannot inherit conclusions")
        for delta in report.get("evidence_deltas", []):
            state = delta.get("state")
            if state not in set(SCHEMA["evidence_states"]): errors.append(f"report {rid} evidence delta has invalid state")
            if delta.get("effective_now") and state != "confirmed": errors.append(f"report {rid} non-confirmed evidence delta cannot be effective")
        for fact in report.get("dynamic_facts", []):
            if not nonempty(fact.get("fact_id")) or not nonempty(fact.get("verified_at")): errors.append(f"report {rid} dynamic fact lacks identity or verification date")
            valid_until = fact.get("valid_until")
            if valid_until and valid_until < report.get("evidence_cutoff", "") and fact.get("supports_current"):
                errors.append(f"report {rid} expired dynamic fact supports current conclusion")

        calcs = report.get("calculations", []); calc_ids = set()
        for calc in calcs if isinstance(calcs, list) else []:
            cid = calc.get("id"); calc_ids.add(cid)
            for field in ("id", "calculator", "input_hash", "output_hash", "status"):
                if not nonempty(calc.get(field)): errors.append(f"report {rid} calculation missing {field}")
            if calc.get("status") != "complete": errors.append(f"report {rid} calculation {cid} is not complete")
            for kind in ("input", "output"):
                file_key = f"{kind}_file"; hash_key = f"{kind}_hash"
                if calc.get(file_key):
                    target = (base_dir / calc[file_key]).resolve()
                    if not target.exists(): errors.append(f"report {rid} calculation {cid} missing {kind} artifact")
                    elif digest(target) != str(calc.get(hash_key)).removeprefix("sha256:"): errors.append(f"report {rid} calculation {cid} {kind} hash mismatch")
        changed_inputs = report.get("changed_inputs", [])
        if report.get("change_class") in {"Recalculation", "Rebase", "Correction"} and changed_inputs:
            required = set(report.get("required_calculation_ids", []))
            if not required or not required <= calc_ids: errors.append(f"report {rid} changed inputs lack complete required calculations")
            for calc in calcs:
                if calc.get("id") in required:
                    for field in ("input_file", "output_file", "verification_command", "verification_status"):
                        if not nonempty(calc.get(field)): errors.append(f"report {rid} required calculation {calc.get('id')} missing {field}")
                    if calc.get("verification_status") != "verified": errors.append(f"report {rid} required calculation {calc.get('id')} is not independently verified")
                    command = calc.get("verification_command")
                    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                        errors.append(f"report {rid} required calculation {calc.get('id')} verification_command must be an argv list")
                    elif calc.get("output_file"):
                        output_path = (base_dir / calc["output_file"]).resolve()
                        try:
                            completed = subprocess.run(command, cwd=base_dir, check=False, capture_output=True, timeout=30)
                        except (OSError, subprocess.TimeoutExpired) as exc:
                            errors.append(f"report {rid} calculation {calc.get('id')} verification execution failed: {exc}")
                        else:
                            if completed.returncode != 0:
                                errors.append(f"report {rid} calculation {calc.get('id')} verification returned {completed.returncode}")
                            elif output_path.exists() and completed.stdout != output_path.read_bytes():
                                errors.append(f"report {rid} calculation {calc.get('id')} verification output mismatch")

        actions = report.get("actions", [])
        action_ids = set()
        for action in actions if isinstance(actions, list) else []:
            aid = action.get("action_id")
            if not aid or aid in action_ids: errors.append(f"report {rid} action ids must be present and unique")
            action_ids.add(aid)
            if action.get("status") not in ACTIONS: errors.append(f"report {rid} action {aid} has invalid status")
            for field in ("owner", "deadline", "success", "stop", "rollback"):
                if not nonempty(action.get(field)): errors.append(f"report {rid} action {aid} missing {field}")
            if action.get("status") in {"revoked", "recovery_required"} and action.get("previous_status") in {"committed", "in_progress", "irreversible"}:
                for field in ("recovery_plan", "recoverable_cost", "sunk_cost"):
                    if not nonempty(action.get(field)): errors.append(f"report {rid} action {aid} missing {field}")

        depth = report.get("depth_metrics", {})
        if not DEPTH_FIELDS <= set(depth): errors.append(f"report {rid} missing depth metrics")
        for parent_id in parents[rid]:
            parent = report_by_id.get(parent_id, {}); pd = parent.get("depth_metrics", {})
            if report.get("change_class") != "Addendum" and DEPTH_FIELDS <= set(pd) and DEPTH_FIELDS <= set(depth):
                for field in DEPTH_FIELDS:
                    if float(depth[field]) < float(pd[field]) and field not in report.get("depth_reduction_justifications", {}):
                        errors.append(f"report {rid} regresses depth field {field}")
        if len([x for x in report.get("information_deltas", []) if x.get("class") in {"Addendum", "Revision"}]) >= 3 and report.get("change_class") != "Consolidation":
            errors.append(f"report {rid} requires Consolidation after three incremental deltas")

    visiting: set[str] = set(); visited: set[str] = set()
    def visit(rid: str) -> None:
        if rid in visiting: errors.append(f"report lineage cycle at {rid}"); return
        if rid in visited: return
        visiting.add(rid)
        for parent in parents.get(rid, []):
            if parent in report_by_id: visit(parent)
        visiting.remove(rid); visited.add(rid)
    for rid in report_by_id: visit(rid)

    def is_ancestor(candidate: str, rid: str, seen: set[str] | None = None) -> bool:
        seen = set() if seen is None else seen
        if rid in seen: return False
        seen.add(rid)
        return any(parent == candidate or is_ancestor(candidate, parent, seen) for parent in parents.get(rid, []) if parent in report_by_id)
    for rid, report in report_by_id.items():
        if report.get("status") == "current":
            newer = [other_id for other_id, other in report_by_id.items() if other_id != rid and other.get("status") != "blocked" and is_ancestor(rid, other_id)]
            if newer: errors.append(f"historical report {rid} cannot be restored as current; create a new Rebase")

    for obj_id in object_by_id:
        current = [r for r in reports if r.get("object_id") == obj_id and r.get("status") == "current"]
        if len(current) != 1: errors.append(f"object {obj_id} must have exactly one current report")
        state = state_by_object.get(obj_id)
        if not state: errors.append(f"object {obj_id} requires current state"); continue
        missing = sorted(STATE_FIELDS - set(state));
        if missing: errors.append(f"current state {obj_id} missing fields: {missing}")
        if len(current) == 1 and state.get("current_report_id") != current[0].get("report_id"): errors.append(f"current state {obj_id} points to wrong report")
        report = report_by_id.get(state.get("current_report_id"), {})
        report_actions = {a.get("action_id"): a for a in report.get("actions", []) if isinstance(a, dict)}
        expected_active = {aid for aid, action in report_actions.items() if action.get("status") in ACTIVE}
        if set(state.get("active_action_ids", [])) != expected_active: errors.append(f"current state {obj_id} active actions do not match current report")

    for report in reports:
        if report.get("status") != "current":
            active_old = {a.get("action_id") for a in report.get("actions", []) if a.get("status") in ACTIVE}
            child_inherited = set()
            for child in reports:
                if report.get("report_id") in child.get("parent_report_ids", []): child_inherited |= set(child.get("inherited_active_action_ids", []))
            if active_old - child_inherited: errors.append(f"superseded report {report.get('report_id')} leaves active actions without transition")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); args = parser.parse_args()
    try: bundle = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: print(f"INVALID: {exc}"); return 2
    errors = validate(bundle, args.input.parent)
    if errors:
        print("\n".join(f"BLOCKED: {e}" for e in errors)); return 1
    print("PASS: report lineage, current state, actions, calculations and depth are consistent"); return 0

if __name__ == "__main__": raise SystemExit(main())
