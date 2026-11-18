"""B/C algorithm and fail-closed tests. Temporary fixtures are not measured data."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workloads.dataset import generate, reference, check_output, sha256
from workloads.group_aggregate import aggregate
from analysis.core import analyze, compare
from report.html import render


class WorkloadTests(unittest.TestCase):
    def test_fixed_input_and_independent_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            one = generate(root / "a.csv", 10001, 29, 42)
            two = generate(root / "b.csv", 10001, 29, 42)
            self.assertEqual(one, two)
            actual, expected = aggregate(root / "a.csv"), reference(root / "a.csv")
            self.assertEqual(actual, expected)
            self.assertEqual(actual["rows"], 10001)
            self.assertEqual(len(actual["groups"]), 29)
            self.assertEqual(sum(g[1] for g in actual["groups"]), 10001)

    def test_hand_computed_negative_values_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.csv"
            path.write_text("group,value\n2,4\n0,-7\n2,-5\n", encoding="utf-8")
            expected = {"rows": 3, "groups": [[0, 1, -7], [2, 2, -1]]}
            self.assertEqual(aggregate(path), expected)
            self.assertEqual(reference(path), expected)
            output = Path(tmp) / "stdout.log"
            output.write_bytes((json.dumps(expected, separators=(",", ":")) + "\n").encode())
            self.assertTrue(check_output(output, expected))
            output.write_bytes(b'{"rows":3,"groups":[[0,1,-7],[2,2,1]]}\n')
            self.assertFalse(check_output(output, expected))
            path.write_text("group,value\n2,no\n", encoding="utf-8")
            for method in (aggregate, reference):
                with self.assertRaises(ValueError):
                    method(path)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # This copied real row is only the shape of a test fixture, not evidence.
        self.row = json.loads((ROOT / "examples" / "measured-run-1.1.json").read_text(encoding="utf-8"))
        self.row.update(git_dirty="", warmup=False, quota_percent=50, input_id="fixture-input", workload_version="fixture-v1")
        self.make_experiment()

    def write(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def make_experiment(self):
        root = self.root
        row = self.row
        directory = root / row["run_id"]
        directory.mkdir(exist_ok=True)
        (directory / "stdout.log").write_bytes(b"fixture\n")
        row["stdout_sha256"] = sha256(directory / "stdout.log")
        row["order_index"] = 0
        self.write(directory / "result.json", row)
        self.write(root / "config.json", {"command": row["command"], "workload_version": row["workload_version"],
                   "input_id": row["input_id"], "quotas": [50], "repeats": 1, "warmups": 0})
        self.write(root / "experiment-status.json", {"state": "complete", "planned_count": 1, "finalized_count": 1, "pending_count": 0})
        self.write(root / "correctness.json", {"kind": "group-correctness-v1", "method": "sqlite-group-by-exact-output-v1",
                   "input_unchanged": True, "input_id": row["input_id"], "workload_version": row["workload_version"],
                   "runs": {row["run_id"]: {"ok": True, "stdout_sha256": row["stdout_sha256"]}}})

    def test_authoritative_result_and_traceability(self):
        # A stale JSONL cannot override result.json.
        (self.root / "runs.jsonl").write_text("invalid index", encoding="utf-8")
        result = analyze(self.root)
        self.assertTrue(result["complete"], result["issues"])
        self.assertEqual(len(result["eligible"]), 1)
        self.assertTrue(result["groups"][0]["comparable"])
        self.assertIn(self.row["run_id"], result["artifacts"])

    def test_states_and_corruption_cannot_become_eligible(self):
        for key, value in (("source", "synthetic"), ("status", "timeout"), ("status", "aborted"),
                           ("warmup", True), ("wall_seconds", None), ("status", "future-status"),
                           ("cleanup_ok", 1), ("git_dirty", " M file")):
            with self.subTest(key=key, value=value):
                row = dict(self.row, **{key: value})
                self.write(self.root / self.row["run_id"] / "result.json", row)
                self.assertFalse(analyze(self.root)["eligible"])
        self.make_experiment()
        (self.root / self.row["run_id"] / "stdout.log").write_bytes(b"tampered\n")
        self.assertFalse(analyze(self.root)["eligible"])

    def test_incomplete_and_missing_correctness(self):
        (self.root / "experiment-status.json").unlink()
        summary = analyze(self.root)
        self.assertFalse(summary["complete"])
        self.assertFalse(summary["groups"][0]["comparable"])
        (self.root / "correctness.json").unlink()
        self.assertFalse(analyze(self.root)["eligible"])

    def test_malformed_metadata_is_reported_without_crashing(self):
        for filename in ("config.json", "correctness.json", "experiment-status.json"):
            with self.subTest(filename=filename):
                self.make_experiment()
                self.write(self.root / filename, [])
                summary = analyze(self.root)
                self.assertFalse(summary["complete"])
                self.assertTrue(summary["issues"])
                self.assertTrue(all(not group["comparable"] for group in summary["groups"]))

    def test_history_sample_and_compatibility_gates(self):
        summary = analyze(self.root)
        self.assertEqual(compare(summary, summary)["comparisons"][0]["verdict"], "unable_to_compare")
        # Expanded fixtures exercise the policy only; never claimed as evidence.
        old = copy.deepcopy(summary)
        old["eligible"] = [dict(old["eligible"][0], run_id=f"{i:032x}") for i in range(5)]
        new = copy.deepcopy(old)
        for i, row in enumerate(new["eligible"]):
            row["run_id"] = f"{100 + i:032x}"
            row["wall_seconds"] = self.row["wall_seconds"] * 1.3
        result = compare(old, new)
        self.assertEqual(result["comparisons"][0]["verdict"], "slowdown_needs_review")
        new["eligible"][0]["input_id"] = "changed"
        self.assertEqual(compare(old, new)["comparisons"][0]["verdict"], "unable_to_compare")

    def test_planned_quota_survives_absence_of_verified_samples(self):
        (self.root / self.row["run_id"] / "stdout.log").unlink()
        summary = analyze(self.root)
        group, = summary["groups"]
        self.assertEqual((group["quota_percent"], group["n"], group["comparable"]), (50, 0, False))
        self.assertIsNone(group["wall_median_seconds"])
        history, = compare(summary, summary)["comparisons"]
        self.assertEqual((history["verdict"], history["wall_ratio"]), ("unable_to_compare", None))

    def test_optional_counters_keep_missing_distinct_from_zero(self):
        summary = analyze(self.root)
        summary["eligible"][0]["cpu_stat_delta"] = {"usage_usec": 10, "nr_periods": 0, "nr_throttled": False}
        render(summary, self.root / "report.html")
        self.assertIn("<td>0</td><td>未提供</td><td>未提供</td>", (self.root / "report.html").read_text(encoding="utf-8"))

    def test_html_escapes_untrusted_strings(self):
        summary = analyze(self.root)
        summary["issues"].append("<script>alert(1)</script>")
        render(summary, self.root / "report.html")
        text = (self.root / "report.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn(self.row["run_id"], text)

    def test_threshold_tie_and_observed_range_sensitivity(self):
        old = analyze(self.root)
        old["eligible"] = [dict(old["eligible"][0], run_id=f"{i:032x}", wall_seconds=1.0) for i in range(7)]
        old["groups"][0]["n"] = 7
        current = copy.deepcopy(old)
        values = [1.1, 1.12, 1.13, 1.15, 1.17, 1.18, 1.2]
        for i, row in enumerate(current["eligible"]):
            row.update(run_id=f"{100+i:032x}", wall_seconds=values[i])
        row = compare(old, current)["comparisons"][0]
        self.assertEqual(row["verdict"], "no_threshold_signal")
        self.assertEqual(row["observed_range_ratio_bounds"], [1.1, 1.2])
        self.assertIs(row["threshold_sensitive"], True)
        for row in current["eligible"]:
            row["wall_seconds"] = 1.3
        row = compare(old, current)["comparisons"][0]
        self.assertEqual(row["verdict"], "slowdown_needs_review")
        self.assertIs(row["threshold_sensitive"], False)


if __name__ == "__main__":
    unittest.main()
