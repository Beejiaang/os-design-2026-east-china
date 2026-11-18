import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def cpu_stat(path):
    text = read(Path(path) / "cpu.stat")
    if text is None:
        return None
    return {key: int(value) for key, value in (line.split() for line in text.splitlines())}


def stat_delta(before, after):
    if before is None or after is None:
        return None
    return {key: after[key] - value for key, value in before.items() if key in after}


def cgroup_path():
    for line in (read("/proc/self/cgroup") or "").splitlines():
        if line.startswith("0::"):
            return Path("/sys/fs/cgroup") / line[3:].lstrip("/")
    return None


def ancestors(path):
    result = []
    root = Path("/sys/fs/cgroup")
    while path is not None and path.is_relative_to(root):
        result.append({"path": str(path), "cpu_max": read(path / "cpu.max"),
                       "cpuset_effective": read(path / "cpuset.cpus.effective")})
        if path == root:
            break
        path = path.parent
    return result


def environment_fingerprint(fields):
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def environment():
    cpuinfo = read("/proc/cpuinfo") or ""
    model = next((line.split(":", 1)[1].strip() for line in cpuinfo.splitlines()
                  if line.startswith("model name")), None)
    fields = {"os_release": read("/etc/os-release"), "kernel": platform.release(),
              "architecture": platform.machine(), "cpu_model": model,
              "logical_cpus": os.cpu_count(), "python": platform.python_version(),
              "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
              "visible_limits": ancestors(cgroup_path())}
    # Machine identity is hashed; hostnames and raw machine IDs are not exported.
    machine = read("/etc/machine-id")
    fields["machine_id_sha256"] = hashlib.sha256(machine.encode()).hexdigest() if machine else None
    fields["fingerprint"] = environment_fingerprint(fields)
    return fields


def doctor():
    errors = []
    if platform.system() != "Linux":
        errors.append("Linux is required")
    controllers = (read("/sys/fs/cgroup/cgroup.controllers") or "").split()
    if "cpu" not in controllers:
        errors.append("cgroup v2 cpu controller is unavailable")
    try:
        check = subprocess.run(["systemctl", "--user", "show-environment"], capture_output=True, text=True, timeout=5)
        if check.returncode:
            errors.append("systemd user manager unavailable: " + check.stderr.strip())
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    return {"supported": not errors, "errors": errors, "environment": environment(),
            "note": "Preflight only; actual quota application is verified for every run."}
