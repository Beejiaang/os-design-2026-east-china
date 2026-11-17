"""Interleaved measured comparison; never ranks mismatched timer boundaries."""
import argparse
import json
import math
import random
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from collector.system import doctor
from runner.core import run_one
from runner.lifecycle import cleanup, install_handlers, restore_handlers
from workloads.dataset import generate, reference, check_output, sha256


def quota_matches(snapshot, quota):
    parts = (snapshot.get("cpu_max") or "").split()
    if quota is None:
        subtree = snapshot.get("parent_subtree_control")
        return (len(parts) == 2 and parts[0] == "max") or (not parts and isinstance(subtree, str) and "cpu" not in subtree.split())
    try:
        return len(parts) == 2 and parts[0] != "max" and abs(int(parts[0]) / int(parts[1]) * 100 - quota) < 0.1
    except (ValueError, ZeroDivisionError):
        return False


def parse_time(path):
    lines = Path(path).read_text().splitlines()
    parts = lines[-1].split(",")
    if len(parts) != 4:
        raise ValueError("Expected GNU time wall,user,system,exit")
    wall, user, system = map(float, parts[:3])
    if any(not math.isfinite(v) or v < 0 for v in (wall, user, system)):
        raise ValueError("Invalid time metrics")
    return {"wall_seconds": wall, "cpu_seconds": user + system, "exit_code": int(parts[3])}


def native_run(config, quota, directory, time_binary):
    directory.mkdir()
    unit = "osdesign-" + uuid.uuid4().hex + ".service"
    args = ["systemd-run", "--user", "--wait", "--collect", "--service-type=exec", "--unit=" + unit,
            "--property=CPUAccounting=yes", "--property=KillMode=control-group", "--property=TimeoutStopSec=2s",
            "--property=RuntimeMaxSec=" + str(config["timeout_seconds"] + 5) + "s",
            "--property=StandardOutput=file:" + str(directory / "stdout.log"),
            "--property=StandardError=file:" + str(directory / "stderr.log"),
            "--working-directory=" + str(ROOT), "--setenv=PYTHONPATH=" + str(ROOT / "src")]
    if quota is not None:
        args.append("--property=CPUQuota=" + str(quota) + "%")
    args += [sys.executable, str(ROOT / "experiments/comparison_probe.py"), str(directory / "snapshot.json"), "--",
             str(time_binary), "-f", "%e,%U,%S,%x", "-o", str(directory / "time.txt"), *config["command"]]
    (directory / "argv.json").write_text(json.dumps(args, indent=2))
    row = {"status": "error", "error": None, "wall_seconds": None, "cpu_seconds": None,
           "exit_code": None, "quota_verified": False, "unit": unit}
    group = None
    try:
        launched = subprocess.run(args, capture_output=True, text=True, timeout=config["timeout_seconds"] + 15)
        (directory / "launch.log").write_text(launched.stdout + launched.stderr)
        row["launcher_exit_code"] = launched.returncode
        snapshot = json.loads((directory / "snapshot.json").read_text())
        group = Path(snapshot["cgroup_path"])
        row.update(snapshot)
        row.update(parse_time(directory / "time.txt"))
        row["quota_verified"] = quota_matches(snapshot, quota)
        row["status"] = "success" if launched.returncode == 0 and row["exit_code"] == 0 and row["quota_verified"] else "failed"
    except KeyboardInterrupt:
        row.update(status="interrupted", error="Comparison cancelled")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        row["error"] = str(exc)
    finally:
        # Native collect normally already unloaded it. Verify only this owned UUID.
        if group is None and (directory / "snapshot.json").exists():
            group = Path(json.loads((directory / "snapshot.json").read_text())["cgroup_path"])
        row["cleanup_ok"], row["cleanup_detail"] = cleanup(unit, group)
        if not row["cleanup_ok"]:
            row["status"] = "cleanup_failed"
        (directory / "native-result.json").write_text(json.dumps(row, indent=2))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--time-binary", required=True, type=Path)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--rows", type=int, default=4000000)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 30 or not 1 <= args.rows <= 10000000:
        parser.error("Require repeats [1,30] and rows [1,10000000]")
    time_binary = args.time_binary.resolve(strict=True)
    preflight = doctor()
    if not preflight["supported"]:
        raise RuntimeError(str(preflight["errors"]))
    provenance = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    if provenance:
        raise ValueError("Clean source revision required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    metadata = generate(output / "input.csv", args.rows, 1000, 20261117)
    expected = reference(output / "input.csv")
    workload = ROOT / "workloads/group_aggregate.py"
    workload_hash = sha256(workload)
    config = {"command": [sys.executable, str(workload), str(output / "input.csv")], "cwd": str(ROOT),
        "workload_version": "sha256:" + workload_hash, "input_id": "lcg32-csv-v1:sha256:" + metadata["sha256"], "timeout_seconds": 60}
    versions = {"gnu_time": subprocess.check_output([str(time_binary), "--version"], text=True),
                "systemd": subprocess.check_output(["systemd-run", "--version"], text=True),
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "time_binary_sha256": sha256(time_binary)}
    for name, value in (("environment", preflight), ("input", metadata), ("reference", expected), ("config", config), ("versions", versions)):
        (output / (name + ".json")).write_text(json.dumps(value, indent=2))
    (output / "project").mkdir()
    (output / "native").mkdir()
    schedule = []
    for warmup, count in ((True, 1), (False, args.repeats)):
        block = [(tool, quota, warmup) for tool in ("project", "gnu-time-systemd") for quota in (None, 100, 50) for _ in range(count)]
        random.Random(20261117 + int(warmup)).shuffle(block)
        schedule.extend(block)
    records = []
    previous = install_handlers()
    try:
        for index, (tool, quota, warmup) in enumerate(schedule):
            started = time.monotonic()
            if tool == "project":
                row = run_one(config, quota, index, warmup, output / "project", preflight["environment"])
                directory = output / "project" / row["run_id"]
            else:
                directory = output / "native" / f"{index:03d}"
                row = native_run(config, quota, directory, time_binary)
            outer = time.monotonic() - started
            stdout = directory / "stdout.log"
            correct = stdout.is_file() and check_output(stdout, expected)
            record = {"kind": "tool-comparison-v1", "source": "measured", "tool": tool,
                      "quota_percent": quota, "warmup": warmup, "order_index": index,
                      "status": row["status"], "cleanup_ok": row["cleanup_ok"], "quota_verified": row.get("quota_verified", False),
                      "functional_ok": correct, "stdout_sha256": sha256(stdout) if stdout.is_file() else None,
                      "wall_seconds": row["wall_seconds"], "cpu_seconds": row["cpu_seconds"],
                      "parent_limits": row.get("visible_limits", [])[1:], "outer_seconds": outer, "artifacts": str(directory)}
            records.append(record)
            (output / "comparison.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
            print(f"{index + 1}/{len(schedule)} {tool} quota={quota} status={row['status']} correct={correct}", flush=True)
            if not row["cleanup_ok"] or row["status"] == "interrupted":
                break
    finally:
        restore_handlers(previous)
    unchanged = sha256(output / "input.csv") == metadata["sha256"] and sha256(workload) == workload_hash
    valid = [r for r in records if r["status"] == "success" and r["functional_ok"] and r["cleanup_ok"] and r["quota_verified"]]
    parents_equal = bool(records) and all(r["parent_limits"] and r["parent_limits"] == records[0]["parent_limits"] for r in records)
    groups = []
    for tool in ("project", "gnu-time-systemd"):
        for quota in (None, 100, 50):
            sample = [r for r in valid if not r["warmup"] and r["tool"] == tool and r["quota_percent"] == quota]
            groups.append({"tool": tool, "quota_percent": quota, "n": len(sample), **{
                field + "_median": statistics.median(r[field] for r in sample) if sample else None
                for field in ("wall_seconds", "cpu_seconds", "outer_seconds")}})
    complete = len(records) == len(schedule) == len(valid) and unchanged and parents_equal
    summary = {"complete": complete, "planned_count": len(schedule), "final_count": len(records),
               "valid_count": len(valid), "input_and_workload_unchanged": unchanged, "parent_limits_equal": parents_equal,
               "groups": groups, "note": "Different timer resolutions and instrumentation; descriptive agreement only, no speed ranking. Harness adds quota snapshots, correctness, repeats and cleanup checks to native tools."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
