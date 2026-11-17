"""Comparison instrumentation and new output-preserving workload controls."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.compare_tools import parse_time, quota_matches
from workloads.dataset import reference


class ComparisonTests(unittest.TestCase):
    def test_parse_time_preserves_exit_and_rejects_invalid_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "time.txt"
            path.write_text("Command exited with non-zero status 7\n1.25,0.75,0.10,7\n")
            value = parse_time(path)
            self.assertEqual(value["exit_code"], 7)
            self.assertAlmostEqual(value["cpu_seconds"], 0.85)
            self.assertEqual(value["wall_seconds"], 1.25)
            for text in ("", "nan,0,0,0", "1,-1,0,0", "1,2,3", "inf,0,0,0"):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    parse_time(path)

    def test_quota_snapshot_never_treats_missing_as_unlimited(self):
        self.assertFalse(quota_matches({}, None))
        self.assertTrue(quota_matches({"cpu_max": None, "parent_subtree_control": "memory pids"}, None))
        self.assertFalse(quota_matches({"cpu_max": None, "parent_subtree_control": "cpu memory"}, None))
        self.assertTrue(quota_matches({"cpu_max": "50000 100000"}, 50))
        self.assertFalse(quota_matches({"cpu_max": "max 100000"}, 50))
        self.assertFalse(quota_matches({"cpu_max": "50000 0"}, 50))

    def test_partial_work_never_changes_functional_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text("group,value\n2,4\n0,-7\n2,-5\n")
            expected = reference(path)
            for percent in (0, 5, 15, 25, 100):
                result = subprocess.run([sys.executable, str(ROOT / "workloads/group_aggregate.py"), str(path),
                                         "--extra-percent", str(percent)], check=True, text=True, capture_output=True)
                self.assertEqual(json.loads(result.stdout), expected)


if __name__ == "__main__":
    unittest.main()
