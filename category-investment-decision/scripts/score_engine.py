#!/usr/bin/env python3
"""Deterministic seven-dimension category score with sensitivity and redline gates."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

WEIGHTS = {
    "market_demand": 20,
    "competitive_entry": 20,
    "profit_space": 20,
    "content_communication": 10,
    "supply_control": 10,
    "risk_control": 10,
    "opportunity_window": 10,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid score input: {exc}") from exc
    scores = payload.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
        raise SystemExit(f"scores must contain exactly: {sorted(WEIGHTS)}")
    clean = {}
    for key, value in scores.items():
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"score must be numeric: {key}") from exc
        if not math.isfinite(number) or not 0 <= number <= 10:
            raise SystemExit(f"score must be finite and between 0 and 10: {key}")
        clean[key] = number
    caps = payload.get("sensitivity_caps", {})
    applied_caps = {}
    if caps:
        if not isinstance(caps, dict):
            raise SystemExit("sensitivity_caps must be an object")
        for key, cap in caps.items():
            if key not in clean or not isinstance(cap, (int, float)) or not math.isfinite(cap) or not 0 <= cap <= 10:
                raise SystemExit(f"invalid sensitivity cap: {key}")
            if clean[key] > cap:
                clean[key] = float(cap); applied_caps[key] = float(cap)
    redlines = payload.get("hard_redlines", [])
    if not isinstance(redlines, list):
        raise SystemExit("hard_redlines must be a list")
    total = round(sum(clean[k] * WEIGHTS[k] / 10 for k in WEIGHTS), 2)
    result = {
        "decision_status": "Blocked" if redlines else "Scored",
        "weighted_score": total,
        "scores_after_caps": clean,
        "applied_caps": applied_caps,
        "hard_redlines": redlines,
        "weight_total": sum(WEIGHTS.values()),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
