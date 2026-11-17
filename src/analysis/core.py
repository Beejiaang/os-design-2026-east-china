"""Read authoritative results, fail closed, keep exclusions and provenance."""
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

from runner.compatibility import check_compatibility
from runner.core import validate


def read_json(path):
    def reject(value):
        raise ValueError("Non-JSON constant: " + value)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject, object_pairs_hook=unique)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def analyze(directory):
    root = Path(directory).resolve()
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "run-1.1.schema.json"
    validator = Draft202012Validator(read_json(schema_path), format_checker=FormatChecker())
    issues, excluded, eligible, records = [], [], [], []
    artifacts = {}
    for path in sorted(root.glob("*/result.json")):
        try:
            row = read_json(path)
            errors = sorted(error.message for error in validator.iter_errors(row))
            if errors:
                raise ValueError("; ".join(errors))
            if row["run_id"] != path.parent.name:
                raise ValueError("run_id does not match result directory")
            records.append(row)
            artifacts[row["run_id"]] = {"result": str(path), "sha256": digest(path)}
        except (ValueError, OSError) as exc:
            issues.append(str(path) + ": " + str(exc))
    ids = [row["run_id"] for row in records]
    if len(ids) != len(set(ids)):
        issues.append("Duplicate run_id")
    config = {}
    planned = None
    try:
        candidate_config = read_json(root / "config.json")
        validate(candidate_config)
        config = candidate_config
        planned = len(config.get("quotas", [None, 100, 50])) * (config.get("repeats", 3) + config.get("warmups", 0))
        schedule = Counter((q, w) for q in config.get("quotas", [None, 100, 50])
                           for w, n in ((True, config.get("warmups", 0)), (False, config.get("repeats", 3)))
                           for _ in range(n))
        if Counter((row["quota_percent"], row["warmup"]) for row in records) != schedule:
            issues.append("Actual quota/warmup counts differ from config")
        for row in records:
            for key in ("command", "workload_version", "input_id"):
                if row[key] != config[key]:
                    issues.append(row["run_id"] + ": config mismatch: " + key)
        if sorted(row["order_index"] for row in records) != list(range(planned)):
            issues.append("Missing/duplicate order_index")
        state = read_json(root / "experiment-status.json")
        if not isinstance(state, dict):
            raise ValueError("Experiment status must be an object")
        if (state.get("state") != "complete" or type(state.get("planned_count")) is not int or
                type(state.get("finalized_count")) is not int or type(state.get("pending_count")) is not int or
                state["planned_count"] != planned or state["finalized_count"] != len(records) or state["pending_count"] != 0):
            issues.append("Experiment status is incomplete or counts disagree")
        if len(records) != planned:
            issues.append("Final result count differs from plan")
    except (OSError, ValueError) as exc:
        issues.append("Experiment metadata: " + str(exc))
    for path in root.glob("*/pending.json"):
        if not (path.parent / "result.json").is_file():
            issues.append("Unfinalized checkpoint: " + path.parent.name)
    correctness = {}
    try:
        candidate_correctness = read_json(root / "correctness.json")
        if not isinstance(candidate_correctness, dict):
            raise ValueError("Correctness must be an object")
        correctness = candidate_correctness
    except (OSError, ValueError) as exc:
        issues.append("Correctness evidence unavailable: " + str(exc))
    for row in records:
        reasons = []
        if row["source"] != "measured":
            reasons.append("synthetic")
        if row["status"] != "success":
            reasons.append(row["status"])
        if row["warmup"]:
            reasons.append("warmup")
        # The existing A gate also checks finite metrics, quota, ancestors,
        # clean revision and explicit booleans. Self-check supplies no verdict.
        reasons.extend(check_compatibility(row, row)["reasons"])
        evidence = correctness.get("runs", {})
        check = evidence.get(row["run_id"], {}) if isinstance(evidence, dict) else {}
        if (correctness.get("kind") != "group-correctness-v1" or
                correctness.get("method") != "sqlite-group-by-exact-output-v1" or
                correctness.get("input_unchanged") is not True or
                correctness.get("input_id") != row["input_id"] or
                correctness.get("workload_version") != row["workload_version"] or
                not isinstance(check, dict) or check.get("ok") is not True or
                check.get("stdout_sha256") != row.get("stdout_sha256")):
            reasons.append("Independent functional verification missing/failed")
        stdout = root / row["run_id"] / "stdout.log"
        if not stdout.is_file() or digest(stdout) != row.get("stdout_sha256"):
            reasons.append("stdout artifact missing or hash mismatch")
        if reasons:
            excluded.append({"run_id": row["run_id"], "status": row["status"], "reasons": sorted(set(reasons))})
        else:
            eligible.append(row)
    complete = not issues and all(row["status"] == "success" for row in records) and bool(records)
    groups = []
    for quota in sorted({row["quota_percent"] for row in eligible}, key=lambda q: -1 if q is None else q):
        sample = [row for row in eligible if row["quota_percent"] == quota]
        # Configuration contrast must still hold input/environment/version fixed.
        # Quota-specific leaf and quota field are intentionally normalized here.
        reference = eligible[0]
        mismatch = []
        if len(sample) != config.get("repeats", 3) * config.get("quotas", [None, 100, 50]).count(quota):
            mismatch.append("Not all scheduled non-warmup runs passed functional/data checks")
        for row in sample:
            normalized = dict(row, quota_percent=reference["quota_percent"])
            mismatch.extend(check_compatibility(reference, normalized)["reasons"])
            if row["workload_version"] != reference["workload_version"]:
                mismatch.append("workload_version differs in configuration contrast")
        wall = [r["wall_seconds"] for r in sample]
        cpu = [r["cpu_seconds"] for r in sample]
        groups.append({"quota_percent": quota, "n": len(sample), "run_ids": [r["run_id"] for r in sample],
                       "wall_median_seconds": statistics.median(wall), "wall_min_seconds": min(wall),
                       "wall_max_seconds": max(wall), "cpu_median_seconds": statistics.median(cpu),
                       "comparable": complete and not mismatch, "reasons": sorted(set(mismatch))})
    baseline = next((g["wall_median_seconds"] for g in groups if g["quota_percent"] is None and g["comparable"]), None)
    for group in groups:
        group["wall_ratio_to_unlimited"] = group["wall_median_seconds"] / baseline if baseline and group["comparable"] else None
    return {"analysis_version": "1.0", "directory": str(root), "complete": complete,
            "planned_count": planned, "finalized_count": len(records), "issues": issues,
            "groups": groups, "eligible": eligible, "excluded": excluded, "artifacts": artifacts,
            "note": "Descriptive configuration contrast only. No validated regression verdict or root cause. Unlimited means no local quota set."}


def compare(baseline, current, minimum=5, threshold=0.15):
    """Exploratory median rule, deliberately not a statistical significance claim."""
    if type(minimum) is not int or minimum < 2 or type(threshold) not in (float, int) or not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("Invalid comparison policy")
    reasons = []
    if not baseline["complete"] or not current["complete"]:
        reasons.append("Both experiments must be complete")
    old, new = baseline["eligible"], current["eligible"]
    old_ids, new_ids = [r["run_id"] for r in old], [r["run_id"] for r in new]
    if len(set(old_ids)) != len(old_ids) or len(set(new_ids)) != len(new_ids) or set(old_ids) & set(new_ids):
        reasons.append("Duplicate/overlapping run_ids cannot be independent historical samples")
    quotas = sorted({r["quota_percent"] for r in old + new}, key=lambda q: -1 if q is None else q)
    comparisons = []
    for quota in quotas:
        left = [r for r in old if r["quota_percent"] == quota]
        right = [r for r in new if r["quota_percent"] == quota]
        problems = list(reasons)
        for summary in (baseline, current):
            if not any(g["quota_percent"] == quota and g["comparable"] for g in summary["groups"]):
                problems.append("Quota group has incomplete or incompatible evidence")
        if len(left) < minimum or len(right) < minimum:
            problems.append("Insufficient independently verified samples")
        if left and right:
            for row in left + right:
                problems.extend(check_compatibility(left[0], row)["reasons"])
        else:
            problems.append("Missing quota on one side")
        ratio = None
        range_bounds = None
        threshold_sensitive = None
        verdict = "unable_to_compare"
        if not problems:
            denominator = statistics.median(r["wall_seconds"] for r in left)
            if denominator <= 0:
                problems.append("Baseline median must be positive")
            else:
                ratio = statistics.median(r["wall_seconds"] for r in right) / denominator
                verdict = "slowdown_needs_review" if ratio > 1 + threshold else "no_threshold_signal"
                if min(r["wall_seconds"] for r in left) > 0:
                    range_bounds = [min(r["wall_seconds"] for r in right) / max(r["wall_seconds"] for r in left),
                                    max(r["wall_seconds"] for r in right) / min(r["wall_seconds"] for r in left)]
                    threshold_sensitive = range_bounds[0] <= 1 + threshold < range_bounds[1]
        comparisons.append({"quota_percent": quota, "baseline_n": len(left), "current_n": len(right),
                            "baseline_run_ids": [r["run_id"] for r in left], "current_run_ids": [r["run_id"] for r in right],
                            "wall_ratio": ratio, "verdict": verdict, "reasons": sorted(set(problems)),
                            "observed_range_ratio_bounds": range_bounds, "threshold_sensitive": threshold_sensitive})
    return {"rule": "exploratory-median-v1", "minimum": minimum, "threshold": threshold,
            "comparisons": comparisons, "sensitivity_version": "observed-range-v1",
            "note": "Exploratory review signal only; no statistical significance, validated accuracy, no-regression or root-cause claim. Observed range sensitivity is not a confidence interval."}
