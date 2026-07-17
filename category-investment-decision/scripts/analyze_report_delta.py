#!/usr/bin/env python3
"""Compute transitive decision impacts and the minimum report-module review set."""
from __future__ import annotations
import argparse, json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "references/decision-impact-graph.json"

def analyze(changed_fields: list[str]) -> dict:
    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8")); graph = data["fields"]
    seen = set(changed_fields); queue = deque(changed_fields)
    while queue:
        field = queue.popleft()
        for downstream in graph.get(field, []):
            if downstream not in seen:
                seen.add(downstream); queue.append(downstream)
    mapping = data["module_mapping"]
    modules = sorted({mapping[field] for field in seen if field in mapping})
    unmapped = sorted(field for field in changed_fields if field not in graph)
    return {"changed_fields": sorted(changed_fields), "impacted_fields": sorted(seen),
            "required_modules": modules, "unmapped_changed_fields": unmapped,
            "status": "BLOCKED" if unmapped else "PASS"}

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("fields", nargs="+"); parser.add_argument("--json", action="store_true")
    args = parser.parse_args(); result = analyze(args.fields)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "\n".join(result["required_modules"]))
    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__": raise SystemExit(main())
