import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from collector.system import doctor, stat_delta
from runner.compatibility import check_compatibility
from runner.core import experiment, validate


def config(command):
    return {"command": command, "workload_version": "test-v1", "input_id": "fixed",
            "quotas": [50], "repeats": 1, "timeout_seconds": 2}


class ContractTests(unittest.TestCase):
    def test_rejects_invalid_limits(self):
        for value in (0, -1, float("nan"), float("inf"), True, "50%"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(dict(config(["true"]), quotas=[value]))

    def test_rejects_shell_string_and_repeat_boolean(self):
        with self.assertRaises(ValueError):
            validate(config("echo unsafe"))
        with self.assertRaises(ValueError):
            validate(dict(config(["true"]), repeats=True))

    def test_missing_stat_is_not_zero(self):
        self.assertIsNone(stat_delta(None, {"usage_usec": 5}))
        self.assertEqual(stat_delta({"usage_usec": 3}, {"usage_usec": 7}), {"usage_usec": 4})

    def test_incompatible_data_never_passes(self):
        row = {"schema_version": "1.0", "source": "measured", "status": "success", "cleanup_ok": True,
               "quota_verified": True, "environment": {"fingerprint": "x"}, "stdout_sha256": "y",
               "input_id": "fixed", "quota_percent": 50, "timeout_seconds": 2,
               "workload_version": "v1", "runner_sha256": "runner-v1", "exit_code": 0,
               "git_commit": "c" * 40, "git_dirty": "",
               "cpu_stat_delta": {"usage_usec": 500000},
               "visible_limits": [{"path": "leaf", "cpu_max": "50000 100000", "cpuset_effective": None},
                                  {"path": "parent", "cpu_max": "max 100000", "cpuset_effective": None}],
               "wall_seconds": 1, "cpu_seconds": 0.5, "warmup": False}
        self.assertTrue(check_compatibility(row, copy.deepcopy(row))["compatible"])
        for key, value in (("status", "timeout"), ("source", "synthetic"), ("cleanup_ok", False),
                           ("input_id", "changed"), ("stdout_sha256", "different"), ("warmup", True),
                           ("quota_verified", False), ("wall_seconds", None), ("environment", {})):
            with self.subTest(key=key):
                self.assertFalse(check_compatibility(row, dict(row, **{key: value}))["compatible"])
        for key, value in (("cleanup_ok", "true"), ("quota_verified", 1), ("exit_code", False),
                           ("environment", None), ("visible_limits", None), ("warmup", None),
                           ("cpu_stat_delta", None), ("wall_seconds", float("nan")),
                           ("cpu_seconds", float("inf")), ("timeout_seconds", 0), ("quota_percent", True),
                           ("git_dirty", " M workload.py"), ("schema_version", "1.1")):
            with self.subTest(key=key, value=value):
                self.assertFalse(check_compatibility(row, dict(row, **{key: value}))["compatible"])
        for key in row:
            incomplete = dict(row)
            del incomplete[key]
            with self.subTest(missing=key):
                self.assertFalse(check_compatibility(row, incomplete)["compatible"])
        # Workload versions may change; the rest of the evidence must match.
        self.assertTrue(check_compatibility(row, dict(row, workload_version="v2"))["compatible"])

    def test_non_object_records_are_rejected(self):
        for value in (None, [], "", 5):
            self.assertFalse(check_compatibility(value, {})["compatible"])
            self.assertFalse(check_compatibility({}, value)["compatible"])


@unittest.skipUnless(os.environ.get("OSDESIGN_INTEGRATION") == "1", "Set OSDESIGN_INTEGRATION=1 on Linux")
class SystemTests(unittest.TestCase):
    def run_experiment(self, cfg):
        with tempfile.TemporaryDirectory() as parent:
            rows = experiment(cfg, Path(parent) / "experiment")
            for row in rows:
                self.assertTrue(row["cleanup_ok"], row)
                result = Path(parent) / "experiment" / row["run_id"] / "result.json"
                self.assertEqual(json.loads(result.read_text())["run_id"], row["run_id"])
            return rows

    def test_three_quotas_and_repeated_output(self):
        self.assertTrue(doctor()["supported"])
        cfg = config([sys.executable, "-c", "import hashlib; x=b'x';\nfor _ in range(700000): x=hashlib.sha256(x).digest()\nprint(x.hex())"])
        cfg.update(quotas=[None, 100, 50], repeats=2, timeout_seconds=15)
        rows = self.run_experiment(cfg)
        self.assertEqual(len(rows), 6)
        self.assertEqual({r["status"] for r in rows}, {"success"})
        self.assertTrue(all(r["quota_verified"] for r in rows))
        self.assertEqual(len({r["stdout_sha256"] for r in rows}), 1)
        self.assertTrue(all(r["cpu_seconds"] > 0 and r["cpu_stat_delta"]["usage_usec"] > 0 for r in rows))

    def test_failure(self):
        row, = self.run_experiment(config([sys.executable, "-c", "raise SystemExit(7)"]))
        self.assertEqual((row["status"], row["exit_code"]), ("failed", 7))

    def test_missing_executable(self):
        row, = self.run_experiment(config(["/nonexistent/osdesign-command"]))
        self.assertEqual(row["status"], "error")
        self.assertIsNone(row["exit_code"])

    def test_timeout_and_descendant_cleanup(self):
        with tempfile.TemporaryDirectory() as parent:
            pidfile = Path(parent) / "pid"
            # Child changes session to escape its parent's process group.
            script = ("import subprocess,time; from pathlib import Path; "
                      "p=subprocess.Popen(['sleep','60'],start_new_session=True); "
                      f"Path({str(pidfile)!r}).write_text(str(p.pid)); time.sleep(60)")
            cfg = config([sys.executable, "-c", script])
            cfg["timeout_seconds"] = 0.5
            row, = self.run_experiment(cfg)
            self.assertEqual(row["status"], "timeout")
            pid = int(pidfile.read_text())
            # Zombie may remain until adopted/reaped; it cannot execute.
            stat = Path(f"/proc/{pid}/stat")
            self.assertTrue(not stat.exists() or stat.read_text().split()[2] == "Z")


if __name__ == "__main__":
    unittest.main()
