#!/usr/bin/env python3
"""Summarize reviewed attribution and action outcomes without inventing causality."""

import argparse
import json
from pathlib import Path


def ratio(numerator, denominator):
    return None if denominator == 0 else numerator / denominator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    events = data.get("events", [])
    hypotheses = data.get("hypotheses", [])
    actions = data.get("actions", [])
    reviewed = [row for row in events if row.get("review_result") in {"real", "noise"}]
    matured_high = [row for row in hypotheses if row.get("confidence") == "high" and row.get("result") in {"validated", "falsified", "inconclusive"}]
    completed_actions = [row for row in actions if row.get("result") in {"success", "failure", "inconclusive"}]
    result = {
        "event_validity": {"numerator": sum(row.get("review_result") == "real" for row in reviewed), "denominator": len(reviewed)},
        "false_alert_rate": {"numerator": sum(row.get("review_result") == "noise" for row in reviewed), "denominator": len(reviewed)},
        "high_confidence_hit_rate": {"numerator": sum(row.get("result") == "validated" for row in matured_high), "denominator": len(matured_high)},
        "action_validation_rate": {"numerator": sum(row.get("result") == "success" for row in completed_actions), "denominator": len(completed_actions)},
    }
    for metric in result.values():
        metric["rate"] = ratio(metric["numerator"], metric["denominator"])
    result["warning"] = "指标反映复核与验证记录，不单独证明经营动作的因果效果"
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
