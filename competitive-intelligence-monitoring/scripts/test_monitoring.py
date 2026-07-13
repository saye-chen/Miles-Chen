#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class MonitoringScripts(unittest.TestCase):
    def test_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            rows = [{"product_id": "A", "snapshot_at": f"2026-01-{i:02d}", "price": 100, "rating": 4.5, "rank": 100} for i in range(1, 9)]
            rows.append({"product_id": "A", "snapshot_at": "2026-01-09", "price": 80, "rating": 4.0, "rank": 60})
            history, alerts, report = tmp / "history.json", tmp / "alerts.json", tmp / "report.md"
            history.write_text(json.dumps(rows), encoding="utf-8")
            subprocess.run(["python3", ROOT / "detect_changes.py", "--input", history, "--output", alerts], check=True)
            data = json.loads(alerts.read_text(encoding="utf-8"))
            self.assertEqual({x["field"] for x in data["alerts"]}, {"price", "rating", "rank"})
            subprocess.run(["python3", ROOT / "build_monitoring_report.py", "--alerts", alerts, "--output", report], check=True)
            self.assertIn("自动检测只证明", report.read_text(encoding="utf-8"))

    def test_competitive_metrics_and_proxy_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, output = tmp / "metrics.json", tmp / "result.json"
            source.write_text(json.dumps({
                "model_version": "test-v1", "normalization_basis": "reviewed set",
                "own": {"dimensions": {"product": .5, "price": .5, "content": .5, "reputation": .5, "channel": .5}},
                "competitors": [{"id": "C1", "overlaps": {"market": 1, "category": 1, "customer": 1},
                    "dimensions": {"product": .8, "price": .6, "content": .7, "reputation": .8, "channel": .6}, "share_proxy": 70},
                    {"id": "C2", "overlaps": {"market": .5, "category": .5, "customer": .5},
                    "dimensions": {"product": .4, "price": .5, "content": .4, "reputation": .5, "channel": .4}, "share_proxy": 30}]}, ensure_ascii=False), encoding="utf-8")
            subprocess.run(["python3", ROOT / "compute_competitive_metrics.py", "--input", source, "--output", output], check=True)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["competitors"][0]["cri"], 1.0)
            self.assertIn("不等同真实市场份额", data["proxy_hhi_warning"])

    def test_learning_loop_keeps_denominators(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, output = tmp / "learning.json", tmp / "result.json"
            source.write_text(json.dumps({"events": [{"review_result": "real"}, {"review_result": "noise"}],
                "hypotheses": [{"confidence": "high", "result": "validated"}],
                "actions": [{"result": "inconclusive"}]}), encoding="utf-8")
            subprocess.run(["python3", ROOT / "evaluate_learning_loop.py", "--input", source, "--output", output], check=True)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["event_validity"]["denominator"], 2)
            self.assertEqual(data["high_confidence_hit_rate"]["rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
