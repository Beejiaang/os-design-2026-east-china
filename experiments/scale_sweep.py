"""Fixed 0.5M/2M/8M scale sweep with independent output and resource evidence."""
import argparse
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from collector.system import doctor
from collector.host_load import HostLoadSampler
from experiments.compare_tools import native_run
from runner.lifecycle import install_handlers, restore_handlers
from workloads.dataset import check_output, generate, reference, sha256


def parse_peak_rss(path):
    text = Path(path).read_text().strip()
    if not text.isascii() or not text.isdecimal():
        raise ValueError("Expected one nonnegative integer GNU time %M in KiB")
    return int(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time-binary", type=Path, required=True)
    args = parser.parse_args()
    binary = args.time_binary.resolve(strict=True)
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise ValueError("Clean source revision required")
    preflight = doctor()
    if not preflight["supported"]:
        raise RuntimeError(str(preflight["errors"]))
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    metadata, expected = {}, {}
    workload = ROOT / "workloads/group_aggregate.py"
    workload_hash = sha256(workload)
    scales = (500000, 2000000, 8000000)
    plan = {"kind": "scale-sweep-v1", "scales": scales, "quotas": [None, 100, 50],
            "warmups": 1, "repeats": 5, "seed": 20261117, "memory_unit": "KiB",
            "memory_method": "GNU time %M, maximum resident set size of aggregation child",
            "timer_boundary": "GNU time around inner GNU time + aggregation; includes inner timer overhead",
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "workload_sha256": workload_hash, "time_binary_sha256": sha256(binary),
            "time_version": subprocess.check_output([str(binary), "--version"], text=True)}
    (root / "plan.json").write_text(json.dumps(plan, indent=2))
    (root / "environment.json").write_text(json.dumps(preflight, indent=2))
    for scale in scales:
        directory = root / str(scale)
        directory.mkdir()
        metadata[scale] = generate(directory / "input.csv", scale, 1000, plan["seed"])
        expected[scale] = reference(directory / "input.csv")
        (directory / "input.json").write_text(json.dumps(metadata[scale], indent=2))
        (directory / "reference.json").write_text(json.dumps(expected[scale], indent=2))
    schedule = []
    for warmup, count in ((True, 1), (False, 5)):
        block = [(scale, quota, warmup) for scale in scales for quota in (None, 100, 50) for _ in range(count)]
        random.Random(plan["seed"] + int(warmup)).shuffle(block)
        schedule.extend(block)
    (root / "schedule.json").write_text(json.dumps(schedule, indent=2))
    records = []
    previous = install_handlers()
    sampler = HostLoadSampler(root)
    try:
        with sampler:
            for index, (scale, quota, warmup) in enumerate(schedule):
                directory = root / str(scale) / f"trial-{index:03d}"
                config = {"command": [str(binary), "-f", "%M", "-o", str(directory / "peak-rss.txt"),
                                      sys.executable, str(workload), str(root / str(scale) / "input.csv")],
                          "timeout_seconds": 120}
                row = native_run(config, quota, directory, binary)
                output = directory / "stdout.log"
                error = None
                try:
                    peak = parse_peak_rss(directory / "peak-rss.txt")
                except (OSError, ValueError) as exc:
                    peak, error = None, str(exc)
                record = {"kind": "scale-sweep-v1", "source": "measured", "scale": scale,
                          "order_index": index, "warmup": warmup, "quota_percent": quota,
                          "functional_ok": output.is_file() and check_output(output, expected[scale]),
                          "stdout_sha256": sha256(output) if output.is_file() else None,
                          "peak_rss_kib": peak, "memory_error": error, "artifacts": str(directory), **row}
                records.append(record)
                (root / "runs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
                print(f"{index + 1}/54 rows={scale} quota={quota} status={row['status']}", flush=True)
                if not row["cleanup_ok"] or row["status"] == "interrupted":
                    break
    finally:
        preflight["host_load"] = sampler.metadata()
        (root / "environment.json").write_text(json.dumps(preflight, indent=2))
        restore_handlers(previous)
    valid = [r for r in records if r["status"] == "success" and r["cleanup_ok"] and
             r["quota_verified"] and r["functional_ok"] and r["peak_rss_kib"] is not None]
    unchanged = sha256(workload) == workload_hash and all(
        sha256(root / str(scale) / "input.csv") == metadata[scale]["sha256"] for scale in scales)
    parents_equal = bool(records) and all(r.get("visible_limits", [])[1:] == records[0].get("visible_limits", [])[1:] and
                                          r.get("visible_limits", [])[1:] for r in records)
    groups = []
    for scale in scales:
        for quota in (None, 100, 50):
            sample = [r for r in valid if r["scale"] == scale and r["quota_percent"] == quota and not r["warmup"]]
            groups.append({"scale": scale, "quota_percent": quota, "n": len(sample),
                           **{field + "_median": statistics.median(r[field] for r in sample) if sample else None
                              for field in ("wall_seconds", "cpu_seconds", "peak_rss_kib")},
                           "peak_rss_kib_max": max((r["peak_rss_kib"] for r in sample), default=None)})
    complete = len(records) == len(valid) == 54 and unchanged and parents_equal
    (root / "summary.json").write_text(json.dumps({"complete": complete, "valid_count": len(valid),
        "input_and_workload_unchanged": unchanged, "parent_limits_equal": parents_equal, "groups": groups}, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
