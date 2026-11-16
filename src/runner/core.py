import csv
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from collector.system import doctor, read
from runner.worker import atomic_json


def validate(config):
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    command = config.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(s, str) or not s or "\0" in s for s in command):
        raise ValueError("command must be a nonempty argv list")
    for key in ("workload_version", "input_id"):
        if not isinstance(config.get(key), str) or not config[key]:
            raise ValueError(key + " must identify the tested code/input")
    quotas = config.get("quotas", [None, 100, 50])
    if not isinstance(quotas, list) or not quotas or any(q is not None and
            (type(q) not in (int, float) or not math.isfinite(q) or not 1 <= q <= 10000) for q in quotas):
        raise ValueError("quotas must contain null or finite percentages in [1, 10000]")
    for key, default, lower, upper in (("repeats", 3, 1, 100), ("warmups", 0, 0, 20)):
        value = config.get(key, default)
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(key + " is out of range")
    timeout = config.get("timeout_seconds", 30)
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0.1 <= timeout <= 3600:
        raise ValueError("timeout_seconds must be in [0.1, 3600]")
    if type(config.get("order_seed", 0)) is not int:
        raise ValueError("order_seed must be an integer")


def ctl(*args, timeout=10):
    return subprocess.run(["systemctl", "--user", *args], capture_output=True, text=True, timeout=timeout)


def run_one(config, quota, index, warmup, root, env):
    run_id = uuid.uuid4().hex
    directory = root / run_id
    directory.mkdir()
    spec = dict(config, cwd=str(Path(config.get("cwd", ".")).resolve()),
                timeout_seconds=config.get("timeout_seconds", 30))
    atomic_json(directory / "spec.json", spec)
    unit = "osdesign-" + run_id + ".service"
    row = {"schema_version": "1.0", "run_id": run_id, "source": "measured",
           "timestamp_utc": datetime.now(timezone.utc).isoformat(), "order_index": index,
           "warmup": warmup, "environment": env, "command": spec["command"],
           "cwd": spec["cwd"], "workload_version": config["workload_version"],
           "input_id": config["input_id"], "quota_percent": quota,
           "timeout_seconds": spec["timeout_seconds"], "unit": unit,
           "status": "error", "error": None, "exit_code": None,
           "wall_seconds": None, "cpu_seconds": None, "cpu_stat_delta": None,
           "cleanup_ok": False, "artifacts": {"stdout": f"{run_id}/stdout.log", "stderr": f"{run_id}/stderr.log"}}
    row["runner_sha256"] = hashlib.sha256(b"".join(
        path.read_bytes() for path in sorted(Path(__file__).resolve().parents[1].glob("*/*.py")))).hexdigest()
    for name, command in (("git_commit", ["git", "rev-parse", "HEAD"]),
                          ("git_dirty", ["git", "status", "--porcelain"])):
        try:
            provenance = subprocess.run(command, cwd=spec["cwd"], capture_output=True, text=True, timeout=5)
            row[name] = provenance.stdout.strip() if provenance.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            row[name] = None
    args = ["systemd-run", "--user", "--quiet", "--unit=" + unit, "--service-type=exec",
            "--property=RemainAfterExit=yes", "--property=CPUAccounting=yes",
            "--property=KillMode=control-group", "--property=TimeoutStopSec=2s",
            "--property=RuntimeMaxSec=" + str(spec["timeout_seconds"] + 5) + "s",
            "--working-directory=" + spec["cwd"],
            "--setenv=PYTHONPATH=" + str(Path(__file__).resolve().parents[1])]
    if quota is not None:
        args.append("--property=CPUQuota=" + str(quota) + "%")
    args += [sys.executable, "-m", "runner.worker", str(directory)]
    group = None
    try:
        launched = subprocess.run(args, capture_output=True, text=True, timeout=10)
        (directory / "launch.log").write_text(launched.stdout + launched.stderr)
        if launched.returncode:
            raise RuntimeError("systemd-run failed: " + launched.stderr.strip())
        deadline = time.monotonic() + spec["timeout_seconds"] + 8
        while not (directory / "measurement.json").exists():
            if time.monotonic() >= deadline:
                raise TimeoutError("Worker did not produce measurements before supervisor deadline")
            state = ctl("show", unit, "--property=ActiveState", "--value").stdout.strip()
            if state in ("failed", "inactive", ""):
                raise RuntimeError("Service stopped without complete measurements: " + state)
            time.sleep(0.05)
        measurement = json.loads((directory / "measurement.json").read_text())
        row.update(measurement)
        group = Path(measurement["cgroup_path"])
        maximum = (measurement.get("cpu_max") or "").split()
        if quota is None:
            # Without cpu enabled for children, no local cpu.max exists. Parent
            # limits still apply and are preserved in visible_limits.
            subtree = measurement.get("parent_subtree_control")
            valid = (len(maximum) == 2 and maximum[0] == "max") or (
                not maximum and subtree is not None and "cpu" not in subtree.split())
        else:
            valid = (len(maximum) == 2 and maximum[0] != "max" and
                     abs(int(maximum[0]) / int(maximum[1]) * 100 - quota) < 0.1)
        row["quota_verified"] = valid
        if not valid:
            row.update(status="error", error="Actual cpu.max does not match requested quota")
        if row["status"] == "success" and (row.get("cpu_stat_delta") is None or
                any(row.get(key) is None for key in ("cpu_seconds", "wall_seconds"))):
            row.update(status="metrics_missing", error="Required performance metrics unavailable")
        with (directory / "stdout.log").open("rb") as stream:
            row["stdout_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired, TimeoutError) as exc:
        row.update(status="error", error=str(exc))
    finally:
        if group is None and (directory / "started.json").exists():
            group = Path(json.loads((directory / "started.json").read_text())["cgroup_path"])
        try:
            stopped = ctl("stop", unit)
            ctl("reset-failed", unit)
            state = ctl("show", unit, "--property=LoadState", "--value").stdout.strip()
            populated = read(group / "cgroup.events") if group else None
            row["cleanup_ok"] = state == "not-found" and (group is None or not group.exists() or
                                                        "populated 0" in (populated or ""))
            row["cleanup_detail"] = {"load_state": state, "cgroup_events": populated,
                                      "stop_stderr": stopped.stderr.strip()}
        except (OSError, subprocess.TimeoutExpired) as exc:
            row["cleanup_detail"] = str(exc)
        if not row["cleanup_ok"]:
            row["execution_status"] = row["status"]
            row.update(status="cleanup_failed", error="Unable to verify service and descendant cleanup")
        atomic_json(directory / "result.json", row)
    return row


def experiment(config, output):
    validate(config)
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    atomic_json(root / "config.json", config)
    preflight = doctor()
    atomic_json(root / "environment.json", preflight)
    if not preflight["supported"]:
        raise RuntimeError("; ".join(preflight["errors"]))
    schedule = []
    for warmup, count in ((True, config.get("warmups", 0)), (False, config.get("repeats", 3))):
        block = [(q, warmup) for q in config.get("quotas", [None, 100, 50]) for _ in range(count)]
        random.Random(config.get("order_seed", 0)).shuffle(block)
        schedule.extend(block)
    rows = []
    with (root / "runs.jsonl").open("w", encoding="utf-8") as stream:
        for index, (quota, warmup) in enumerate(schedule):
            row = run_one(config, quota, index, warmup, root, preflight["environment"])
            rows.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print(f'{index + 1}/{len(schedule)} quota={quota} status={row["status"]}', flush=True)
            if not row["cleanup_ok"]:
                break
    fields = ["run_id", "order_index", "warmup", "quota_percent", "status", "exit_code",
              "wall_seconds", "cpu_seconds", "cleanup_ok", "error"]
    with (root / "runs.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # CSV null is an empty cell; JSON retains explicit null.
            writer.writerow(row)
    return rows
