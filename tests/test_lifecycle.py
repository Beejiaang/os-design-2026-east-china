import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from runner.core import experiment, validate
from runner.lifecycle import cleanup, owner_identity, recover


class FailureContractTests(unittest.TestCase):
    def test_unknown_config_and_invalid_cwd_are_rejected(self):
        cfg = {"command": ["true"], "workload_version": "test", "input_id": "fixed"}
        for bad in (dict(cfg, repeat=3), dict(cfg, cwd=None), dict(cfg, cwd="")):
            with self.subTest(config=bad), self.assertRaises(ValueError):
                validate(bad)

    def test_unsupported_environment_is_preserved_without_launch(self):
        cfg = {"command": ["true"], "workload_version": "test", "input_id": "fixed"}
        with tempfile.TemporaryDirectory() as parent, patch("runner.core.doctor", return_value={
                "supported": False, "errors": ["permission denied"], "environment": {}}), patch("runner.core.run_one") as launch:
            output = Path(parent) / "unsupported"
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                experiment(cfg, output)
            launch.assert_not_called()
            self.assertFalse(json.loads((output / "environment.json").read_text())["supported"])

    def test_unavailable_manager_cannot_claim_cleanup(self):
        with patch("runner.lifecycle.ctl", side_effect=OSError("manager unavailable")):
            ok, detail = cleanup("osdesign-" + "a" * 32 + ".service")
        self.assertFalse(ok)
        self.assertIn("manager unavailable", detail["error"])


@unittest.skipUnless(os.environ.get("OSDESIGN_INTEGRATION") == "1", "Set OSDESIGN_INTEGRATION=1 on Linux")
class LifecycleSystemTests(unittest.TestCase):
    def save_evidence(self, output, scenario):
        destination = os.environ.get("OSDESIGN_TEST_EVIDENCE")
        if destination:
            target = Path(destination) / scenario
            shutil.copytree(output, target)
            (target / "evidence-kind.json").write_text(json.dumps({"scenario": scenario,
                "purpose": "Fault-injection cleanup test; excluded from performance samples"}))

    def wait_until(self, predicate, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(0.05)
        self.fail("Condition did not become true before deadline")

    def assert_dead(self, pid):
        def dead():
            stat = Path(f"/proc/{pid}/stat")
            return not stat.exists() or stat.read_text().split()[2] == "Z"
        self.wait_until(dead)

    def start(self, parent, timeout=20, repeats=2):
        output = Path(parent) / "experiment"
        pidfile = Path(parent) / "child.pid"
        script = ("import subprocess,time; from pathlib import Path; "
                  "p=subprocess.Popen(['sleep','60'],start_new_session=True); "
                  f"Path({str(pidfile)!r}).write_text(str(p.pid)); time.sleep(60)")
        config = Path(parent) / "config.json"
        config.write_text(json.dumps({"command": [sys.executable, "-c", script],
                          "workload_version": "lifecycle-test-v1", "input_id": "fixed",
                          "quotas": [50], "repeats": repeats, "timeout_seconds": timeout}))
        process = subprocess.Popen([sys.executable, "-m", "runner", "run", str(config), "--output", str(output)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_process, process)
        self.wait_until(lambda: pidfile.exists() and pidfile.read_text())
        directory = next(output.glob("*/pending.json")).parent
        return process, output, directory, int(pidfile.read_text())

    @staticmethod
    def stop_process(process):
        if process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
        else:
            process.communicate()

    def test_sigint_and_sigterm_preserve_finalized_record(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum), tempfile.TemporaryDirectory() as parent:
                process, output, directory, child = self.start(parent)
                process.send_signal(signum)
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, 128 + signum, stderr)
                row = json.loads((directory / "result.json").read_text())
                self.assertEqual(row["status"], "interrupted")
                self.assertTrue(row["cleanup_ok"], row)
                self.assertEqual(len((output / "runs.jsonl").read_text().splitlines()), 1)
                self.assertEqual(json.loads((output / "experiment-status.json").read_text())["state"], "interrupted")
                self.assertNotIn("Traceback", stderr)
                self.assert_dead(child)
                self.save_evidence(output, "sigint" if signum == signal.SIGINT else "sigterm")

    def test_corrupt_started_snapshot_does_not_prevent_cleanup(self):
        with tempfile.TemporaryDirectory() as parent:
            process, output, directory, child = self.start(parent)
            (directory / "started.json").write_text("{broken")
            process.send_signal(signal.SIGINT)
            process.communicate(timeout=15)
            self.assertTrue(json.loads((directory / "result.json").read_text())["cleanup_ok"])
            self.assert_dead(child)
            self.save_evidence(output, "corrupt-started-snapshot")

    def test_worker_crash_is_error_with_descendant_cleanup(self):
        with tempfile.TemporaryDirectory() as parent:
            process, output, directory, child = self.start(parent, repeats=1)
            unit = "osdesign-" + directory.name + ".service"
            worker = subprocess.check_output(["systemctl", "--user", "show", unit, "--property=MainPID", "--value"], text=True)
            os.kill(int(worker.strip()), signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 1, stderr)
            row = json.loads((directory / "result.json").read_text())
            self.assertEqual(row["status"], "error")
            self.assertTrue(row["cleanup_ok"])
            self.assert_dead(child)
            self.save_evidence(output, "worker-crash")

    def test_hard_kill_watchdog_and_explicit_recovery(self):
        with tempfile.TemporaryDirectory() as parent:
            process, output, directory, child = self.start(parent, timeout=0.5)
            # Recovery may not interrupt a live supervisor or rewrite its summaries.
            before = (output / "runs.jsonl").read_bytes()
            report = recover(output)
            self.assertFalse(report["complete"])
            self.assertEqual((output / "runs.jsonl").read_bytes(), before)
            process.kill()
            process.communicate(timeout=5)
            self.assertFalse((directory / "result.json").exists())
            unit = "osdesign-" + directory.name + ".service"
            def unloaded():
                result = subprocess.run(["systemctl", "--user", "show", unit, "--property=LoadState", "--value"],
                                        text=True, capture_output=True, timeout=3)
                return result.stdout.strip() == "not-found"
            self.wait_until(unloaded, timeout=12)
            self.assert_dead(child)
            report = recover(output)
            self.assertTrue(report["complete"], report)
            row = json.loads((directory / "result.json").read_text())
            self.assertEqual(row["status"], "aborted")
            self.assertTrue(row["cleanup_ok"])
            self.assertEqual(len((output / "runs.jsonl").read_text().splitlines()), 1)
            self.assertEqual(recover(output)["checks"], [])
            self.save_evidence(output, "supervisor-hard-kill-recovery")

    def test_recovery_rejects_other_boot_without_stopping_units(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            (root / "config.json").write_text("{}")
            (root / "environment.json").write_text("{}")
            directory = root / ("b" * 32)
            directory.mkdir()
            owner = owner_identity()
            owner["boot"] = "different"
            (directory / "pending.json").write_text(json.dumps({"kind": "osdesign-pending-v1", "owner": owner,
                "record": {"run_id": directory.name, "unit": "osdesign-" + directory.name + ".service"}}))
            with patch("runner.lifecycle.cleanup") as stop:
                report = recover(root)
                self.assertFalse(report["complete"])
                stop.assert_not_called()
            self.assertFalse((directory / "result.json").exists())
