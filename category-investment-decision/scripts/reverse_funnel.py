#!/usr/bin/env python3
"""Reverse a profit target into order, click, and impression requirements."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


RATE_KEYS = ("platform_commission", "creator_commission", "payment", "return_loss")
VARIABLE_KEYS = ("product", "logistics", "packaging", "other")
CREATOR_FIXED_KEYS = ("sample_cost_per_creator", "collaboration_fee_per_creator",
                      "creative_cost_per_creator", "base_ads_per_creator")


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


def sum_mapping(payload: dict[str, Any], name: str) -> tuple[float, dict[str, float]]:
    raw = payload.get(name, {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{name} must be an object")
    cleaned = {}
    total = 0.0
    for key, value in raw.items():
        amount = finite_number(value, f"{name}.{key}")
        cleaned[str(key)] = round(amount, 2)
        total += amount
    return total, cleaned


def get_rates(payload: dict[str, Any]) -> dict[str, float]:
    raw = payload.get("rates", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("rates must be an object")
    rates = {}
    for key in RATE_KEYS:
        rate = finite_number(raw.get(key, 0), f"rates.{key}")
        if rate > 1:
            raise ValueError(f"rates.{key} must be between 0 and 1")
        rates[key] = rate
    return rates


def get_funnel(payload: dict[str, Any]) -> tuple[float, float, float | None]:
    raw = payload.get("funnel", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("funnel must be an object")
    ctr = finite_number(raw.get("ctr"), "funnel.ctr", allow_zero=False)
    cvr = finite_number(raw.get("cvr"), "funnel.cvr", allow_zero=False)
    if ctr > 1 or cvr > 1:
        raise ValueError("funnel ctr and cvr must be between 0 and 1")
    impressions = raw.get("actual_impressions")
    actual_impressions = None if impressions is None else finite_number(impressions, "funnel.actual_impressions")
    return ctr, cvr, actual_impressions


def unit_economics(payload: dict[str, Any]) -> dict[str, Any]:
    price = finite_number(payload.get("price"), "price", allow_zero=False)
    fixed_total, fixed_items = sum_mapping(payload, "fixed_costs")
    variable_total, variable_items = sum_mapping(payload, "variable_costs")
    rates = get_rates(payload)
    rate_total = sum(rates.values())
    if rate_total >= 1:
        raise ValueError("combined rates must be below 1")
    contribution_margin = price * (1 - rate_total) - variable_total
    return {
        "price": price,
        "fixed_costs": fixed_total,
        "fixed_cost_items": fixed_items,
        "variable_costs_per_unit": variable_total,
        "variable_cost_items": variable_items,
        "rate_total": rate_total,
        "rates": rates,
        "contribution_margin_per_unit": contribution_margin,
    }


def reverse(payload: dict[str, Any]) -> dict[str, Any]:
    economics = unit_economics(payload)
    ctr, cvr, actual_impressions = get_funnel(payload)
    contribution = economics["contribution_margin_per_unit"]
    if contribution <= 0:
        return {
            **rounded_economics(economics),
            "ctr": ctr,
            "cvr": cvr,
            "break_even_units": None,
            "minimum_clicks": None,
            "minimum_impressions": None,
            "max_fixed_costs_at_given_impressions": 0 if actual_impressions is not None else None,
            "decision_hint": "STOP",
            "reason": "Contribution margin is not positive under current assumptions.",
        }
    break_even_units = math.ceil(economics["fixed_costs"] / contribution) if economics["fixed_costs"] else 0
    minimum_clicks = math.ceil(break_even_units / cvr) if break_even_units else 0
    minimum_impressions = math.ceil(minimum_clicks / ctr) if minimum_clicks else 0
    max_fixed = None
    if actual_impressions is not None:
        max_fixed = actual_impressions * ctr * cvr * contribution
    return {
        **rounded_economics(economics),
        "ctr": ctr,
        "cvr": cvr,
        "break_even_units": break_even_units,
        "minimum_clicks": minimum_clicks,
        "minimum_impressions": minimum_impressions,
        "max_fixed_costs_at_given_impressions": round(max_fixed, 2) if max_fixed is not None else None,
        "decision_hint": "CONTINUE" if actual_impressions is not None and actual_impressions >= minimum_impressions else "ITERATE",
    }


def creator_payload(payload: dict[str, Any]) -> dict[str, Any]:
    creator_count = int(finite_number(payload.get("creator_count", 1), "creator_count", allow_zero=False))
    if creator_count < 1:
        raise ValueError("creator_count must be at least 1")
    per_creator = 0.0
    per_creator_items = {}
    for key in CREATOR_FIXED_KEYS:
        value = finite_number(payload.get(key, 0), key)
        per_creator_items[key] = round(value, 2)
        per_creator += value
    fixed_total, fixed_items = sum_mapping(payload, "fixed_costs")
    merged = {**fixed_items, **per_creator_items}
    adjusted = dict(payload)
    adjusted["fixed_costs"] = {"base_fixed_costs": fixed_total, "creator_portfolio_fixed_costs": per_creator * creator_count}
    result = reverse(adjusted)
    per_creator_payload = dict(payload)
    per_creator_payload["fixed_costs"] = {"per_creator_fixed_costs": per_creator}
    per_creator_result = reverse(per_creator_payload)
    result.update({
        "mode": "creator",
        "creator_count": creator_count,
        "per_creator_fixed_costs": round(per_creator, 2),
        "creator_fixed_cost_items": merged,
        "portfolio_fixed_costs": round(fixed_total + per_creator * creator_count, 2),
        "break_even_units_per_creator": per_creator_result["break_even_units"],
        "minimum_impressions_per_creator": per_creator_result["minimum_impressions"],
        "minimum_impressions_total": result["minimum_impressions"],
        "creator_go_no_go": "GO" if per_creator_result["decision_hint"] == "CONTINUE" else "REVIEW",
    })
    return result


def rounded_economics(economics: dict[str, Any]) -> dict[str, Any]:
    return {
        "price": round(economics["price"], 2),
        "fixed_costs": round(economics["fixed_costs"], 2),
        "fixed_cost_items": economics["fixed_cost_items"],
        "variable_costs_per_unit": round(economics["variable_costs_per_unit"], 2),
        "variable_cost_items": economics["variable_cost_items"],
        "rates": {key: round(value, 4) for key, value in economics["rates"].items()},
        "rate_total": round(economics["rate_total"], 4),
        "contribution_margin_per_unit": round(economics["contribution_margin_per_unit"], 2),
        "contribution_margin_pct": round(economics["contribution_margin_per_unit"] / economics["price"] * 100, 1),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("standard", "creator"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        result = reverse(payload) if args.mode == "standard" else creator_payload(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
