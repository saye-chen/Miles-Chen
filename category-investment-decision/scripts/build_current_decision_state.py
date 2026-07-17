#!/usr/bin/env python3
"""Validate a lineage bundle and emit the authoritative state for every decision object."""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lineage", HERE / "validate_report_lineage.py")
lineage = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(lineage)

def build(bundle: dict, base_dir: Path) -> dict:
    errors = lineage.validate(bundle, base_dir)
    if errors: return {"status": "BLOCKED", "errors": errors, "current_states": []}
    reports = {r["report_id"]: r for r in bundle["reports"]}
    states = []
    for state in bundle["current_states"]:
        report = reports[state["current_report_id"]]
        states.append({**state, "report_version": report["report_version"], "runtime_version": report["runtime_version"],
                       "evidence_cutoff": report["evidence_cutoff"], "information_state": report["information_state"],
                       "effective_conclusion": report.get("effective_conclusion"),
                       "action_states": {a["action_id"]: a["status"] for a in report["actions"]}})
    return {"status": "PASS", "current_states": states}

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); bundle = json.loads(args.input.read_text(encoding="utf-8")); result = build(bundle, args.input.parent)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output: args.output.write_text(payload, encoding="utf-8")
    else: print(payload, end="")
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())
