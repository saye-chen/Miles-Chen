#!/usr/bin/env python3
"""Validate D10 blueprint traceability without treating file existence as completion."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "governance/capm-blueprint-implementation-manifest.json"
VALID = {"fixed", "partial", "missing", "controlled_external_gate"}

def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8")); errors = []
    reqs = data.get("requirements", []); ids = [r.get("id") for r in reqs]
    if len(ids) != len(set(ids)): errors.append("duplicate_requirement_id")
    if not all(str(section) in {str(r.get("section")) for r in reqs} for section in range(25)): errors.append("sections_0_to_24_not_fully_traced")
    source = data.get("blueprint", {})
    if not source.get("source_name") or not source.get("sha256") or len(source["sha256"]) != 64:
        errors.append("invalid_blueprint_provenance")
    for req in reqs:
        status = req.get("status")
        if status not in VALID: errors.append(f"{req.get('id')}:invalid_status")
        evidence = req.get("evidence", []); tests = req.get("tests", [])
        if status == "fixed" and (not evidence or not tests): errors.append(f"{req.get('id')}:fixed_without_evidence_and_test")
        for rel in evidence + tests:
            if not (ROOT / rel).exists(): errors.append(f"{req.get('id')}:missing_path:{rel}")
    if errors: raise SystemExit("CAPM blueprint validation failed:\n- " + "\n- ".join(errors))
    counts = {key: sum(r["status"] == key for r in reqs) for key in sorted(VALID)}
    print(f"CAPM blueprint traceability passed: {len(reqs)} requirements {counts}")

if __name__ == "__main__": main()
