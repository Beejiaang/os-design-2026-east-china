"""One command: prepare input, execute A, independently verify, render C."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from runner.core import experiment, validate
from runner.lifecycle import install_handlers, restore_handlers
from workloads.dataset import generate, reference, sha256, check_output
from analysis.core import analyze
from report.html import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=2000000)
    parser.add_argument("--groups", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    validate({"command": ["placeholder"], "workload_version": "preflight", "input_id": "preflight",
              "repeats": args.repeats, "warmups": args.warmups, "timeout_seconds": args.timeout})
    if not 1 <= args.rows <= 10000000 or not 1 <= args.groups <= args.rows or not 0 <= args.seed < 2**32:
        raise ValueError("Require rows in [1,10000000], groups in [1,rows], seed uint32")
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    dataset = root / "input.csv"
    metadata = generate(dataset, args.rows, args.groups, args.seed)
    expected = reference(dataset)
    (root / "input.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (root / "reference.json").write_text(json.dumps(expected, indent=2), encoding="utf-8")
    workload = ROOT / "workloads" / "group_aggregate.py"
    config = {"command": [sys.executable, str(workload), str(dataset)], "cwd": str(ROOT),
              "workload_version": "group-aggregate-sha256:" + sha256(workload),
              "input_id": "lcg32-csv-v1:sha256:" + metadata["sha256"],
              "quotas": [None, 100, 50], "repeats": args.repeats,
              "warmups": args.warmups, "order_seed": args.seed, "timeout_seconds": args.timeout}
    previous = install_handlers()
    try:
        rows = experiment(config, root / "experiment")
    finally:
        restore_handlers(previous)
    unchanged = sha256(dataset) == metadata["sha256"] and sha256(workload) == config["workload_version"].split(":")[-1]
    checks = {}
    for row in rows:
        output = root / "experiment" / row["run_id"] / "stdout.log"
        checks[row["run_id"]] = {"ok": unchanged and output.is_file() and check_output(output, expected),
                                 "stdout_sha256": sha256(output) if output.is_file() else None}
    validation = {"kind": "group-correctness-v1", "method": "sqlite-group-by-exact-output-v1",
                  "input_id": config["input_id"], "workload_version": config["workload_version"],
                  "input_unchanged": unchanged, "runs": checks}
    (root / "experiment" / "correctness.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    summary = analyze(root / "experiment")
    (root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    render(summary, root / "report.html")
    print(root / "report.html")
    if any(row.get("interrupt_signal") for row in rows):
        return 128 + next(row["interrupt_signal"] for row in rows if row.get("interrupt_signal"))
    return 0 if summary["complete"] and len(summary["eligible"]) == 3 * args.repeats else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
