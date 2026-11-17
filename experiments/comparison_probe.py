"""Comparison instrumentation: snapshot the service, then exec GNU time unchanged.

This helper belongs to our harness, not GNU time or native systemd features.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collector.system import ancestors, cgroup_path, read


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not Path(command[0]).is_absolute():
        parser.error("An absolute executable argv is required")
    group = cgroup_path()
    if group is None:
        raise RuntimeError("No cgroup v2 service path")
    args.snapshot.write_text(json.dumps({"cgroup_path": str(group), "cpu_max": read(group / "cpu.max"),
        "visible_limits": ancestors(group), "parent_subtree_control": read(group.parent / "cgroup.subtree_control")}, indent=2))
    os.execv(command[0], command)
