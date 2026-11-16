"""Internal service worker. Runs within the measured cgroup, never via a shell."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from collector.system import ancestors, cgroup_path, cpu_stat, read, stat_delta


def atomic_json(path, value):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def main():
    import resource
    directory = Path(sys.argv[1])
    spec = json.loads((directory / "spec.json").read_text())
    group = cgroup_path()
    before = cpu_stat(group) if group else None
    start = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    data = {"status": "error", "exit_code": None, "error": None,
            "cgroup_path": str(group), "cpu_max": read(group / "cpu.max") if group else None,
            "visible_limits": ancestors(group), "cpu_stat_before": before,
            "parent_subtree_control": read(group.parent / "cgroup.subtree_control") if group else None}
    atomic_json(directory / "started.json", data)
    try:
        with (directory / "stdout.log").open("wb") as out, (directory / "stderr.log").open("wb") as err:
            process = subprocess.Popen(spec["command"], cwd=spec["cwd"], stdout=out, stderr=err,
                                       start_new_session=True)
            try:
                code = process.wait(timeout=spec["timeout_seconds"])
                data.update(status="success" if code == 0 else "failed", exit_code=code)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                data.update(status="timeout", error="Workload exceeded timeout")
    except OSError as exc:
        data.update(error=str(exc))
    finally:
        after = cpu_stat(group) if group else None
        usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        data.update(wall_seconds=time.monotonic() - start,
                    cpu_seconds=(usage_after.ru_utime + usage_after.ru_stime
                                 - usage_before.ru_utime - usage_before.ru_stime),
                    cpu_stat_after=after, cpu_stat_delta=stat_delta(before, after))
        atomic_json(directory / "measurement.json", data)
    # Stay running until the supervisor stops this unit. RuntimeMaxSec does not
    # bound a RemainAfterExit service once it has entered active/exited state.
    # The post-measurement wait is outside all recorded performance intervals.
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
