#!/usr/bin/env python3
"""Calculate the minimum test success rate required for a portfolio to break even."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def finite_number(value: Any, name: str, *, allow_zero: bool = True) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if number < 0 or (number == 0 and not allow_zero):
        phrase = "positive" if not allow_zero else "non-negative"
        raise ValueError(f"{name} must be {phrase}")
    return number


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    test_count = finite_number(payload.get("test_count", 1), "test_count", allow_zero=False)
    cost_per_test = finite_number(payload.get("cost_per_test"), "cost_per_test")
    success_value = finite_number(payload.get("success_value"), "success_value", allow_zero=False)
    expected_success_rate = finite_number(payload.get("expected_success_rate", 0), "expected_success_rate")
    if expected_success_rate > 1:
        raise ValueError("expected_success_rate must be between 0 and 1")
    budget = payload.get("budget")
    budget_value = None if budget is None else finite_number(budget, "budget")

    minimum_success_rate = cost_per_test / success_value
    total_test_cost = test_count * cost_per_test
    expected_successes = test_count * expected_success_rate
    expected_profit = expected_successes * success_value - total_test_cost
    break_even_successes = total_test_cost / success_value
    budget_supported_tests = None if budget_value is None else math.floor(budget_value / cost_per_test) if cost_per_test else None

    return {
        "test_count": round(test_count, 2),
        "cost_per_test": round(cost_per_test, 2),
        "success_value": round(success_value, 2),
        "expected_success_rate": round(expected_success_rate, 4),
        "minimum_success_rate": round(minimum_success_rate, 6),
        "minimum_success_rate_pct": round(minimum_success_rate * 100, 2),
        "break_even_successes": round(break_even_successes, 2),
        "expected_successes": round(expected_successes, 2),
        "total_test_cost": round(total_test_cost, 2),
        "expected_profit": round(expected_profit, 2),
        "budget": round(budget_value, 2) if budget_value is not None else None,
        "budget_supported_tests": budget_supported_tests,
        "decision_hint": "CONTINUE" if expected_success_rate >= minimum_success_rate else "ITERATE_OR_STOP",
        "sensitivity": {
            "success_value_minus_30_pct": round(cost_per_test / (success_value * 0.7), 6),
            "success_value_base": round(minimum_success_rate, 6),
            "success_value_plus_30_pct": round(cost_per_test / (success_value * 1.3), 6),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        result = calculate(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
