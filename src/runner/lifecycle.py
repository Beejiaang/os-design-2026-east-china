"""Cancellation, owned-unit cleanup, and explicit recovery after supervisor loss."""
import csv
import hashlib
import json
import os
import re
import signal
import subprocess
from pathlib import Path

from collector.system import read
from runner.worker import atomic_json

SCHEMA_VERSION = "1.1"


class RunInterrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum


def install_handlers():
    previous = {}
    cancelled = False

    def cancel(signum, frame):
        nonlocal cancelled
        if not cancelled:
            cancelled = True
            raise RunInterrupted(signum)
        # Let the first cancellation finish bounded service cleanup.

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, cancel)
    return previous


def restore_handlers(previous):
    for signum, handler in previous.items():
        signal.signal(signum, handler)


def process_identity(pid):
    text = read(f"/proc/{pid}/stat")
    if text is None:
        return None
    parts = text[text.rfind(")") + 2:].split()
    return {"state": parts[0], "start_ticks": parts[19]}


def owner_identity():
    if not hasattr(os, "getuid"):
        raise RuntimeError("Run recovery requires Linux")
    def digest(path):
        value = read(path)
        return hashlib.sha256(value.encode()).hexdigest() if value else None
    return {"uid": os.getuid(), "machine": digest("/etc/machine-id"),
            "boot": digest("/proc/sys/kernel/random/boot_id"), "pid": os.getpid(),
            "process": process_identity(os.getpid())}


def ctl(*args):
    return subprocess.run(["systemctl", "--user", *args], capture_output=True, text=True, timeout=10)


def cleanup(unit, group=None):
    if not re.fullmatch(r"osdesign-[0-9a-f]{32}\.service", unit):
        return False, {"error": "Refusing non-owned unit name"}
    try:
        # Query systemd rather than trusting an arbitrary path from a result file.
        live = ctl("show", unit, "--property=ControlGroup", "--value").stdout.strip()
        if live.startswith("/"):
            group = Path("/sys/fs/cgroup") / live.lstrip("/")
        if group is not None:
            group = Path(group).resolve()
            if not group.is_relative_to("/sys/fs/cgroup") or group.name != unit:
                return False, {"error": "Invalid owned cgroup path"}
        stopped = ctl("stop", unit)
        ctl("reset-failed", unit)
        state = ctl("show", unit, "--property=LoadState", "--value").stdout.strip()
        events = read(group / "cgroup.events") if group else None
        empty = group is None or not group.exists() or "populated 0" in (events or "").splitlines()
        return state == "not-found" and empty, {"load_state": state, "cgroup_events": events,
                                               "stop_stderr": stopped.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, {"error": str(exc)}


def write_summaries(root, rows):
    tmp = root / "runs.jsonl.tmp"
    tmp.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    tmp.replace(root / "runs.jsonl")
    fields = ["run_id", "order_index", "warmup", "quota_percent", "status", "exit_code",
              "wall_seconds", "cpu_seconds", "cleanup_ok", "error"]
    tmp = root / "runs.csv.tmp"
    with tmp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(root / "runs.csv")
    config = json.loads((root / "config.json").read_text())
    planned = len(config.get("quotas", [None, 100, 50])) * (config.get("warmups", 0) + config.get("repeats", 3))
    pending = sum(not (p.parent / "result.json").exists() for p in root.glob("*/pending.json"))
    state = "complete" if len(rows) == planned and all(r["status"] == "success" for r in rows) else "failed"
    if pending:
        state = "recovery_required"
    elif any(r["status"] == "interrupted" for r in rows):
        state = "interrupted"
    atomic_json(root / "experiment-status.json", {"state": state, "planned_count": planned,
                "finalized_count": len(rows), "pending_count": pending})


def recover(output):
    root = Path(output).resolve(strict=True)
    if not (root / "config.json").is_file() or not (root / "environment.json").is_file():
        raise ValueError("Not an experiment output directory")
    current = owner_identity()
    reports = []
    for path in sorted(root.glob("*/pending.json")):
        directory = path.parent
        if not re.fullmatch(r"[0-9a-f]{32}", directory.name):
            continue
        final_path = directory / "result.json"
        previous = json.loads(final_path.read_text()) if final_path.exists() else None
        if previous is not None and previous.get("cleanup_ok") is True:
            continue
        pending = json.loads(path.read_text())
        if not isinstance(pending, dict) or not isinstance(pending.get("owner"), dict) or not isinstance(pending.get("record"), dict):
            raise ValueError("Malformed recovery checkpoint: " + str(path))
        owner = pending.get("owner", {})
        row = pending.get("record", {})
        expected_unit = "osdesign-" + directory.name + ".service"
        reason = None
        if pending.get("kind") != "osdesign-pending-v1" or row.get("unit") != expected_unit or row.get("run_id") != directory.name:
            reason = "Invalid ownership checkpoint"
        elif any(owner.get(key) is None or owner.get(key) != current[key] for key in ("uid", "machine", "boot")):
            reason = "Recovery requires the original user, machine, and boot"
        elif type(owner.get("pid")) is not int or not isinstance(owner.get("process"), dict):
            reason = "Supervisor identity missing"
        else:
            process = process_identity(owner["pid"])
            if process and process["state"] != "Z" and process["start_ticks"] == owner["process"].get("start_ticks"):
                reason = "Original supervisor is still alive"
        if reason:
            reports.append({"run_id": directory.name, "recovered": False, "reason": reason})
            continue
        # Hard termination cannot execute a finally block. Preserve checkpoint,
        # worker measurements and prior failures, but never label recovery success.
        if previous is not None:
            atomic_json(directory / "pre-recovery-result.json", previous)
        row.update(status="aborted", error="Supervisor lost; recovered run is excluded from performance comparison",
                   cleanup_ok=False, recovered=True)
        started = directory / "started.json"
        group = None
        if started.exists():
            try:
                group = Path(json.loads(started.read_text())["cgroup_path"])
            except (ValueError, KeyError, TypeError):
                pass
        row["cleanup_ok"], row["cleanup_detail"] = cleanup(expected_unit, group)
        if not row["cleanup_ok"]:
            row.update(execution_status="aborted", status="cleanup_failed")
        atomic_json(final_path, row)
        reports.append({"run_id": directory.name, "recovered": row["cleanup_ok"], "status": row["status"]})
    rows = [json.loads(p.read_text()) for p in root.glob("*/result.json")]
    rows.sort(key=lambda row: row["order_index"])
    if reports and all(item["recovered"] for item in reports):
        write_summaries(root, rows)
    return {"checks": reports, "complete": all(item["recovered"] for item in reports)}
