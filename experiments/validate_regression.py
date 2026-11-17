"""Predeclared fixed-quota validation of the existing exploratory 15% rule."""
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from analysis.core import analyze, compare
from runner.core import experiment
from runner.lifecycle import install_handlers, restore_handlers
from report.html import render
from workloads.dataset import generate, reference, check_output, sha256


SCENARIOS = [("baseline", 0, "reference"), ("healthy-1", 0, "healthy_control"),
             ("mild-5", 5, "known_extra_work_below_nominal_threshold"),
             ("boundary-15", 15, "boundary_no_preassigned_verdict"),
             ("clear-25", 25, "known_extra_work_above_nominal_threshold"),
             ("healthy-2", 0, "healthy_control")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--rows", type=int, default=4000000)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    if not 1 <= args.rows <= 10000000 or not 5 <= args.repeats <= 30:
        parser.error("Require rows [1,10000000], repeats [5,30]")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("Clean source revision required")
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    plan = {"kind": "regression-validation-plan-v1", "minimum": 5, "threshold": 0.15,
            "rows": args.rows, "repeats": args.repeats, "warmups": 1, "quota_percent": 100,
            "scenario_order": SCENARIOS, "environment_interference": "Ambient, not deliberately changed",
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "interpretation": "Extra work percentage is not a promised wall-time percentage; boundary has no target verdict. No threshold adjustment."}
    (root / "plan.json").write_text(json.dumps(plan, indent=2))
    metadata = generate(root / "input.csv", args.rows, 1000, 20261117)
    expected = reference(root / "input.csv")
    (root / "input.json").write_text(json.dumps(metadata, indent=2))
    (root / "reference.json").write_text(json.dumps(expected, indent=2))
    workload = ROOT / "workloads/group_aggregate.py"
    workload_hash = sha256(workload)
    summaries = {}
    previous = install_handlers()
    try:
        for index, (name, percent, label) in enumerate(SCENARIOS):
            config = {"command": [sys.executable, str(workload), str(root / "input.csv"), "--extra-percent", str(percent)],
                      "cwd": str(ROOT), "workload_version": "sha256:" + workload_hash + ":extra=" + str(percent),
                      "input_id": "lcg32-csv-v1:sha256:" + metadata["sha256"], "quotas": [100],
                      "repeats": args.repeats, "warmups": 1, "order_seed": 20261117 + index, "timeout_seconds": 60}
            directory = root / name
            directory.mkdir()
            (directory / "ambient-load-before.txt").write_text(Path("/proc/loadavg").read_text())
            rows = experiment(config, directory / "experiment")
            unchanged = sha256(root / "input.csv") == metadata["sha256"] and sha256(workload) == workload_hash
            checks = {}
            for row in rows:
                output = directory / "experiment" / row["run_id"] / "stdout.log"
                checks[row["run_id"]] = {"ok": unchanged and output.is_file() and check_output(output, expected),
                                        "stdout_sha256": sha256(output) if output.is_file() else None}
            validation = {"kind": "group-correctness-v1", "method": "sqlite-group-by-exact-output-v1",
                          "input_id": config["input_id"], "workload_version": config["workload_version"],
                          "input_unchanged": unchanged, "runs": checks}
            (directory / "experiment/correctness.json").write_text(json.dumps(validation, indent=2))
            summary = analyze(directory / "experiment")
            (directory / "summary.json").write_text(json.dumps(summary, indent=2))
            render(summary, directory / "report.html")
            summaries[name] = summary
            if any(r["status"] == "interrupted" or r["cleanup_ok"] is not True for r in rows):
                raise RuntimeError("Validation stopped after cancellation/cleanup failure")
    finally:
        restore_handlers(previous)
    outcomes = []
    for name, percent, label in SCENARIOS[1:]:
        result = compare(summaries["baseline"], summaries[name])
        render(summaries[name], root / name / "history.html", result)
        outcomes.append({"scenario": name, "extra_percent": percent, "label": label, "comparison": result})
    # These are explicitly altered derived copies, not extra measured runs.
    negatives = {}
    for case in ("insufficient_samples", "overlap", "incomplete", "wrong_input", "wrong_environment"):
        candidate = copy.deepcopy(summaries["healthy-1"])
        if case == "insufficient_samples":
            candidate["eligible"] = candidate["eligible"][:4]
        elif case == "overlap":
            candidate = copy.deepcopy(summaries["baseline"])
        elif case == "incomplete":
            candidate["complete"] = False
        else:
            for row in candidate["eligible"]:
                row["input_id" if case == "wrong_input" else "environment"] = "changed" if case == "wrong_input" else {"fingerprint": "changed"}
        negatives[case] = compare(summaries["baseline"], candidate)
    data_ok = all(s["complete"] and len(s["eligible"]) == args.repeats and all(g["comparable"] for g in s["groups"]) for s in summaries.values())
    negative_ok = all(all(r["verdict"] == "unable_to_compare" for r in value["comparisons"]) for value in negatives.values())
    result = {"plan": plan, "data_checks_passed": data_ok, "negative_checks_passed": negative_ok,
              "measured_run_count": sum(s["finalized_count"] for s in summaries.values()),
              "outcomes": outcomes, "derived_negative_checks": negatives,
              "note": "Small controlled validation, not a false-positive/false-negative rate estimate. No raw record changed."}
    (root / "validation.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"data_ok": data_ok, "negative_ok": negative_ok,
                      "outcomes": [{"scenario": o["scenario"], **o["comparison"]["comparisons"][0]} for o in outcomes]}, indent=2))
    return 0 if data_ok and negative_ok else 1


if __name__ == "__main__":
    sys.exit(main())
